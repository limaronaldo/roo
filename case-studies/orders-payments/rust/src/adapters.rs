use crate::application::{Lookup, Mode, RelayMode};
use crate::domain::{
    Event, EventId, Order, Outcome, PaymentId, PaymentRequest, RefundId, RefundRequest,
};
use std::collections::{HashMap, HashSet};

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct OutboxRecord {
    pub(crate) event: Event,
    acknowledged: bool,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct Candidate {
    pub(crate) order: Order,
    pub(crate) outbox: Vec<OutboxRecord>,
}
impl Candidate {
    pub(crate) fn append(&mut self, event: Event) {
        self.outbox.push(OutboxRecord {
            event,
            acknowledged: false,
        });
    }
}

/// Owns the only committed local snapshot and its outbox.
/// Candidate replacement simulates an atomic transaction, not disk durability.
#[derive(Debug)]
pub struct Store {
    committed: Candidate,
}
impl Store {
    pub fn new(order: Order) -> Self {
        Self {
            committed: Candidate {
                order,
                outbox: Vec::new(),
            },
        }
    }
    pub fn order(&self) -> &Order {
        &self.committed.order
    }
    pub fn event_count(&self) -> usize {
        self.committed.outbox.len()
    }
    pub fn pending_outbox(&self) -> usize {
        self.committed
            .outbox
            .iter()
            .filter(|r| !r.acknowledged)
            .count()
    }
    pub fn events(&self) -> impl Iterator<Item = &Event> {
        self.committed.outbox.iter().map(|r| &r.event)
    }
    pub(crate) fn candidate(&self) -> Candidate {
        self.committed.clone()
    }
    pub(crate) fn commit(&mut self, candidate: Candidate, fail: bool) -> bool {
        if fail {
            return false;
        }
        self.committed = candidate;
        true
    }
    pub(crate) fn relay(&mut self, consumer: &mut Consumer, mode: RelayMode) -> Outcome {
        for record in &mut self.committed.outbox {
            if record.acknowledged {
                continue;
            }
            if mode == RelayMode::SendFail {
                return Outcome::RelaySendFailed;
            }
            consumer.deliver(&record.event);
            if mode == RelayMode::AckFail {
                return Outcome::RelayAckFailed;
            }
            record.acknowledged = true;
        }
        Outcome::RelayOk
    }
}

/// Independent remote custody. Complete typed key records last for this scenario.
#[derive(Debug, Default)]
pub struct Provider {
    payments: HashMap<PaymentId, (PaymentRequest, Outcome)>,
    refunds: HashMap<RefundId, RefundRequest>,
    charges: usize,
    refunded: usize,
}
impl Provider {
    pub fn charge_count(&self) -> usize {
        self.charges
    }
    pub fn refund_count(&self) -> usize {
        self.refunded
    }
    pub(crate) fn pay(&mut self, request: &PaymentRequest, mode: Mode) -> Outcome {
        if let Some((recorded, result)) = self.payments.get(&request.id) {
            return if recorded == request {
                *result
            } else {
                Outcome::KeyConflict
            };
        }
        if mode == Mode::TimeoutBefore {
            return Outcome::Unknown;
        }
        let terminal = if mode == Mode::Decline {
            Outcome::Declined
        } else {
            Outcome::Approved
        };
        if terminal == Outcome::Approved {
            self.charges += 1;
        }
        self.payments
            .insert(request.id.clone(), (request.clone(), terminal));
        if mode == Mode::TimeoutAfter {
            Outcome::Unknown
        } else {
            terminal
        }
    }
    pub(crate) fn refund(&mut self, request: &RefundRequest, mode: Mode) -> Outcome {
        if let Some(recorded) = self.refunds.get(&request.id) {
            return if recorded == request {
                Outcome::Approved
            } else {
                Outcome::KeyConflict
            };
        }
        let Some((payment, Outcome::Approved)) = self.payments.get(&request.payment) else {
            return Outcome::KeyConflict;
        };
        if payment.order != request.order
            || payment.currency != request.currency
            || payment.amount != request.amount
            || self.refunds.values().any(|r| r.payment == request.payment)
        {
            return Outcome::KeyConflict;
        }
        if mode == Mode::TimeoutBefore {
            return Outcome::Unknown;
        }
        // Refund modes deliberately exclude Decline at the application boundary.
        self.refunds.insert(request.id.clone(), request.clone());
        self.refunded += 1;
        if mode == Mode::TimeoutAfter {
            Outcome::Unknown
        } else {
            Outcome::Approved
        }
    }
    pub(crate) fn lookup_payment(&self, id: &PaymentId, lookup: Lookup) -> Outcome {
        if lookup == Lookup::Unavailable {
            return Outcome::Unknown;
        }
        self.payments
            .get(id)
            .map_or(Outcome::NotFound, |(_, outcome)| *outcome)
    }
    pub(crate) fn lookup_refund(&self, id: &RefundId, lookup: Lookup) -> Outcome {
        if lookup == Lookup::Unavailable {
            return Outcome::Unknown;
        }
        if self.refunds.contains_key(id) {
            Outcome::Approved
        } else {
            Outcome::NotFound
        }
    }
    // Adapter probe belongs to fixtures, never to the public checkout API.
    pub(crate) fn conflict(&mut self, id: &PaymentId, amount: i64) -> Result<Outcome, String> {
        let Some((recorded, _)) = self.payments.get(id) else {
            return Err("conflict requires a recorded payment key".to_owned());
        };
        let amount =
            crate::Money::new(amount).map_err(|_| "conflict requires a positive amount")?;
        if amount == recorded.amount {
            return Err("conflict amount must differ".to_owned());
        }
        let mut changed = recorded.clone();
        changed.amount = amount;
        Ok(self.pay(&changed, Mode::Approve))
    }
}

/// Remembers immutable fact identities; duplicate delivery applies no new fact.
#[derive(Debug, Default)]
pub struct Consumer {
    seen: HashSet<EventId>,
    applied: Vec<Event>,
}
impl Consumer {
    pub fn count(&self) -> usize {
        self.applied.len()
    }
    pub fn facts(&self) -> &[Event] {
        &self.applied
    }
    pub fn deliver(&mut self, event: &Event) {
        if self.seen.insert(event.id().clone()) {
            self.applied.push(event.clone());
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{Money, OrderId};
    fn payment() -> PaymentRequest {
        PaymentRequest {
            id: PaymentId::new("p1").unwrap(),
            order: OrderId::new("O1").unwrap(),
            currency: "USD".to_owned(),
            amount: Money::new(250).unwrap(),
        }
    }
    fn refund() -> RefundRequest {
        RefundRequest {
            id: RefundId::new("r1").unwrap(),
            payment: PaymentId::new("p1").unwrap(),
            order: OrderId::new("O1").unwrap(),
            currency: "USD".to_owned(),
            amount: Money::new(250).unwrap(),
        }
    }
    #[test]
    fn payment_fingerprint_compares_every_request_field_and_stable_result_wins() {
        let mut provider = Provider::default();
        let original = payment();
        assert_eq!(
            provider.pay(&original, Mode::TimeoutAfter),
            Outcome::Unknown
        );
        assert_eq!(provider.charge_count(), 1);
        assert_eq!(
            provider.lookup_payment(&original.id, Lookup::Ok),
            Outcome::Approved
        );
        for changed in [
            PaymentRequest {
                order: OrderId::new("O2").unwrap(),
                ..original.clone()
            },
            PaymentRequest {
                currency: "EUR".to_owned(),
                ..original.clone()
            },
            PaymentRequest {
                amount: Money::new(251).unwrap(),
                ..original.clone()
            },
        ] {
            assert_eq!(provider.pay(&changed, Mode::Approve), Outcome::KeyConflict);
        }
        assert_eq!(provider.pay(&original, Mode::Decline), Outcome::Approved);
        assert_eq!(provider.charge_count(), 1);
        assert_eq!(provider.payments.len(), 1);
        let mut decline = original;
        decline.id = PaymentId::new("p2").unwrap();
        assert_eq!(provider.pay(&decline, Mode::Decline), Outcome::Declined);
        assert_eq!(provider.pay(&decline, Mode::Approve), Outcome::Declined);
        assert_eq!(provider.charge_count(), 1);
    }
    #[test]
    fn refund_requires_confirmed_charge_and_full_matching_fingerprint() {
        let mut provider = Provider::default();
        let original = refund();
        assert_eq!(
            provider.refund(&original, Mode::Approve),
            Outcome::KeyConflict
        );
        assert_eq!(provider.pay(&payment(), Mode::Approve), Outcome::Approved);
        for changed in [
            RefundRequest {
                payment: PaymentId::new("p2").unwrap(),
                ..original.clone()
            },
            RefundRequest {
                order: OrderId::new("O2").unwrap(),
                ..original.clone()
            },
            RefundRequest {
                currency: "EUR".to_owned(),
                ..original.clone()
            },
            RefundRequest {
                amount: Money::new(249).unwrap(),
                ..original.clone()
            },
            RefundRequest {
                amount: Money::new(251).unwrap(),
                ..original.clone()
            },
        ] {
            assert_eq!(
                provider.refund(&changed, Mode::Approve),
                Outcome::KeyConflict
            );
        }
        assert_eq!(provider.refund_count(), 0);
        assert_eq!(
            provider.refund(&original, Mode::TimeoutAfter),
            Outcome::Unknown
        );
        assert_eq!(provider.refund_count(), 1);
        for changed in [
            RefundRequest {
                payment: PaymentId::new("p2").unwrap(),
                ..original.clone()
            },
            RefundRequest {
                order: OrderId::new("O2").unwrap(),
                ..original.clone()
            },
            RefundRequest {
                currency: "EUR".to_owned(),
                ..original.clone()
            },
            RefundRequest {
                amount: Money::new(249).unwrap(),
                ..original.clone()
            },
        ] {
            assert_eq!(
                provider.refund(&changed, Mode::Approve),
                Outcome::KeyConflict
            );
        }
        assert_eq!(
            provider.refund(&original, Mode::TimeoutBefore),
            Outcome::Approved
        );
        let second_id = RefundRequest {
            id: RefundId::new("r2").unwrap(),
            ..original
        };
        assert_eq!(
            provider.refund(&second_id, Mode::Approve),
            Outcome::KeyConflict
        );
        assert_eq!(provider.refund_count(), 1);
    }
    #[test]
    fn payment_and_refund_keys_have_separate_typed_namespaces() {
        let mut provider = Provider::default();
        let original = payment();
        assert_eq!(provider.pay(&original, Mode::Approve), Outcome::Approved);
        let refund = RefundRequest {
            id: RefundId::new("p1").unwrap(),
            ..refund()
        };
        assert_eq!(provider.refund(&refund, Mode::Approve), Outcome::Approved);
        assert_eq!(provider.charge_count(), 1);
        assert_eq!(provider.refund_count(), 1);
    }
    #[test]
    fn failed_store_commit_installs_neither_candidate_order_nor_event() {
        let mut store = Store::new(Order::new(OrderId::new("O1").unwrap()));
        let mut draft = store.candidate();
        assert_eq!(draft.order.add(10, 1), Outcome::Added);
        assert_eq!(
            draft.order.prepare_payment(PaymentId::new("p1").unwrap()),
            Outcome::Added
        );
        assert!(store.commit(draft, false));
        let before = store.candidate();
        let mut candidate = store.candidate();
        let event = candidate.order.finish_payment(true);
        candidate.append(event);
        assert!(!store.commit(candidate, true));
        assert_eq!(store.candidate(), before);
        assert_eq!(store.event_count(), 0);
    }
}
