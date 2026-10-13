use crate::{Consumer, Outcome, PaymentId, Provider, RefundId, State, Store};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Mode {
    Approve,
    Decline,
    TimeoutBefore,
    TimeoutAfter,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Failure {
    None,
    Prepare,
    Commit,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Lookup {
    Ok,
    Unavailable,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum RelayMode {
    Ok,
    SendFail,
    AckFail,
}

/// Short exclusive capability borrows coordinate three independently owned resources.
/// No reference to an Order is cached across candidate commits or remote calls.
pub struct Application<'a> {
    store: &'a mut Store,
    provider: &'a mut Provider,
    consumer: &'a mut Consumer,
}
impl<'a> Application<'a> {
    pub fn new(
        store: &'a mut Store,
        provider: &'a mut Provider,
        consumer: &'a mut Consumer,
    ) -> Self {
        Self {
            store,
            provider,
            consumer,
        }
    }
    pub fn add(&mut self, unit: i64, quantity: i64) -> Outcome {
        let mut candidate = self.store.candidate();
        let outcome = candidate.order.add(unit, quantity);
        if outcome == Outcome::Added {
            self.store.commit(candidate, false);
        }
        outcome
    }
    pub fn pay(&mut self, id: PaymentId, mode: Mode, failure: Failure) -> Outcome {
        let order = self.store.order();
        if order.state() != State::Draft {
            if order.payment_id() != Some(&id) {
                return Outcome::IntentConflict;
            }
            match order.state() {
                State::Paid | State::Refunding | State::Refunded => return Outcome::AlreadyApplied,
                State::Declined => return Outcome::AlreadyDeclined,
                State::Pending => {}
                State::Draft => unreachable!(),
            }
        } else {
            let mut candidate = self.store.candidate();
            let result = candidate.order.prepare_payment(id);
            if result != Outcome::Added {
                return result;
            }
            if !self.store.commit(candidate, failure == Failure::Prepare) {
                return Outcome::LocalPrepareFailed;
            }
        }
        let request = self
            .store
            .order()
            .payment()
            .expect("persisted payment intent")
            .clone();
        let observation = self.provider.pay(&request, mode);
        self.finish(observation, failure)
    }
    pub fn refund(&mut self, id: RefundId, mode: Mode, failure: Failure) -> Outcome {
        // The bounded protocol does not support a declined refund.
        if mode == Mode::Decline {
            return Outcome::InvalidState;
        }
        match self.store.order().state() {
            State::Paid => {
                let mut candidate = self.store.candidate();
                let result = candidate.order.prepare_refund(id);
                if result != Outcome::Added {
                    return result;
                }
                if !self.store.commit(candidate, failure == Failure::Prepare) {
                    return Outcome::LocalPrepareFailed;
                }
            }
            State::Refunding | State::Refunded => {
                if self.store.order().refund_id() != Some(&id) {
                    return Outcome::IntentConflict;
                }
                if self.store.order().state() == State::Refunded {
                    return Outcome::AlreadyApplied;
                }
            }
            _ => return Outcome::InvalidState,
        }
        let request = self
            .store
            .order()
            .refund()
            .expect("persisted refund intent")
            .clone();
        let observation = self.provider.refund(&request, mode);
        self.finish(observation, failure)
    }
    pub fn reconcile(&mut self, lookup: Lookup, failure: Failure) -> Outcome {
        let observation = match self.store.order().state() {
            State::Pending => self.provider.lookup_payment(
                self.store.order().payment_id().expect("Pending payment"),
                lookup,
            ),
            State::Refunding => self.provider.lookup_refund(
                self.store.order().refund_id().expect("Refunding refund"),
                lookup,
            ),
            _ => return Outcome::InvalidState,
        };
        self.finish(observation, failure)
    }
    fn finish(&mut self, observation: Outcome, failure: Failure) -> Outcome {
        if !matches!(observation, Outcome::Approved | Outcome::Declined) {
            return observation;
        }
        let mut candidate = self.store.candidate();
        let event = match candidate.order.state() {
            State::Pending => candidate
                .order
                .finish_payment(observation == Outcome::Approved),
            State::Refunding => candidate.order.finish_refund(),
            _ => unreachable!("only active persisted intents can be finalized"),
        };
        candidate.append(event);
        if self.store.commit(candidate, failure == Failure::Commit) {
            observation
        } else {
            Outcome::LocalCommitFailed
        }
    }
    pub fn relay(&mut self, mode: RelayMode) -> Outcome {
        self.store.relay(self.consumer, mode)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{EventKind, Order, OrderId};
    struct Lab {
        store: Store,
        provider: Provider,
        consumer: Consumer,
    }
    impl Lab {
        fn new() -> Self {
            Self {
                store: Store::new(Order::new(OrderId::new("O1").unwrap())),
                provider: Provider::default(),
                consumer: Consumer::default(),
            }
        }
        fn app(&mut self) -> Application<'_> {
            Application::new(&mut self.store, &mut self.provider, &mut self.consumer)
        }
        fn populated() -> Self {
            let mut lab = Self::new();
            assert_eq!(lab.app().add(100, 2), Outcome::Added);
            assert_eq!(lab.app().add(50, 1), Outcome::Added);
            lab
        }
        fn pay(&mut self, mode: Mode, failure: Failure) -> Outcome {
            self.app().pay(PaymentId::new("p1").unwrap(), mode, failure)
        }
        fn refund(&mut self, mode: Mode, failure: Failure) -> Outcome {
            self.app()
                .refund(RefundId::new("r1").unwrap(), mode, failure)
        }
    }
    #[test]
    fn invalid_additions_preserve_every_line_and_total() {
        let mut lab = Lab::populated();
        let before = lab.store.candidate();
        for (unit, qty, expected) in [
            (0, 1, Outcome::InvalidLine),
            (-1, 1, Outcome::InvalidLine),
            (1, 0, Outcome::InvalidLine),
            (1, -1, Outcome::InvalidLine),
            (i64::MAX, 2, Outcome::Overflow),
            (i64::MAX, 1, Outcome::Overflow),
        ] {
            assert_eq!(lab.app().add(unit, qty), expected);
            assert_eq!(lab.store.candidate(), before);
        }
        assert_eq!(lab.store.order().line_count(), 2);
    }
    #[test]
    fn maximum_total_is_accepted_but_following_sum_is_rejected() {
        let mut lab = Lab::new();
        assert_eq!(lab.app().add(i64::MAX, 1), Outcome::Added);
        let before = lab.store.candidate();
        assert_eq!(lab.app().add(1, 1), Outcome::Overflow);
        assert_eq!(lab.store.candidate(), before);
    }
    #[test]
    fn empty_and_cross_state_operations_have_no_effect() {
        let mut lab = Lab::new();
        let before = lab.store.candidate();
        assert_eq!(lab.pay(Mode::Approve, Failure::None), Outcome::InvalidOrder);
        assert_eq!(
            lab.refund(Mode::Approve, Failure::None),
            Outcome::InvalidState
        );
        assert_eq!(
            lab.app().reconcile(Lookup::Ok, Failure::None),
            Outcome::InvalidState
        );
        assert_eq!(lab.store.candidate(), before);
        assert_eq!(lab.provider.charge_count(), 0);
        assert_eq!(lab.provider.refund_count(), 0);
    }
    #[test]
    fn prepare_failure_precedes_remote_and_keeps_draft() {
        let mut lab = Lab::populated();
        let before = lab.store.candidate();
        assert_eq!(
            lab.pay(Mode::Approve, Failure::Prepare),
            Outcome::LocalPrepareFailed
        );
        assert_eq!(lab.store.candidate(), before);
        assert_eq!(lab.provider.charge_count(), 0);
        assert!(lab.store.order().payment_id().is_none());
    }
    #[test]
    fn terminal_commit_failure_keeps_pending_without_candidate_event() {
        let mut lab = Lab::populated();
        assert_eq!(
            lab.pay(Mode::Approve, Failure::Commit),
            Outcome::LocalCommitFailed
        );
        assert_eq!(lab.store.order().state(), State::Pending);
        assert_eq!(lab.store.order().payment_id().unwrap().as_str(), "p1");
        assert_eq!(lab.store.event_count(), 0);
        assert_eq!(lab.provider.charge_count(), 1);
        let before = lab.store.candidate();
        assert_eq!(
            lab.app().reconcile(Lookup::Ok, Failure::Commit),
            Outcome::LocalCommitFailed
        );
        assert_eq!(lab.store.candidate(), before);
        assert_eq!(
            lab.app().reconcile(Lookup::Ok, Failure::None),
            Outcome::Approved
        );
        assert_eq!(lab.store.order().state(), State::Paid);
        assert_eq!(lab.store.event_count(), 1);
        assert_eq!(lab.provider.charge_count(), 1);
    }
    #[test]
    fn missing_and_unavailable_lookup_remain_distinct_then_same_key_retry_recovers() {
        let mut lab = Lab::populated();
        assert_eq!(
            lab.pay(Mode::TimeoutBefore, Failure::Commit),
            Outcome::Unknown
        );
        let pending = lab.store.candidate();
        assert_eq!(
            lab.app().reconcile(Lookup::Unavailable, Failure::Commit),
            Outcome::Unknown
        );
        assert_eq!(lab.store.candidate(), pending);
        assert_eq!(
            lab.app().reconcile(Lookup::Ok, Failure::Commit),
            Outcome::NotFound
        );
        assert_eq!(lab.store.candidate(), pending);
        assert_eq!(lab.provider.charge_count(), 0);
        assert_eq!(lab.pay(Mode::Approve, Failure::Prepare), Outcome::Approved);
        assert_eq!(lab.provider.charge_count(), 1);
    }
    #[test]
    fn intent_is_frozen_and_retry_event_identity_is_stable() {
        let mut lab = Lab::populated();
        assert_eq!(lab.pay(Mode::TimeoutAfter, Failure::None), Outcome::Unknown);
        let pending = lab.store.candidate();
        assert_eq!(
            lab.app()
                .pay(PaymentId::new("p2").unwrap(), Mode::Approve, Failure::None),
            Outcome::IntentConflict
        );
        assert_eq!(lab.app().add(10, 1), Outcome::InvalidState);
        assert_eq!(lab.store.candidate(), pending);
        assert_eq!(lab.pay(Mode::Decline, Failure::None), Outcome::Approved);
        let fact = lab.store.events().next().unwrap().clone();
        assert_eq!(fact.id().as_str(), "payment:p1");
        assert_eq!(fact.kind(), EventKind::PaymentApproved);
        assert_eq!(fact.order_id().as_str(), "O1");
        assert_eq!(fact.payment_id().as_str(), "p1");
        assert_eq!(fact.amount().minor(), 250);
        assert_eq!(fact.currency(), "USD");
        assert!(fact.refund_id().is_none());
        assert_eq!(
            lab.pay(Mode::Approve, Failure::Commit),
            Outcome::AlreadyApplied
        );
        assert_eq!(lab.store.events().next().unwrap(), &fact);
        assert_eq!(lab.store.event_count(), 1);
        assert_eq!(lab.provider.charge_count(), 1);
    }
    #[test]
    fn decline_is_terminal_and_remembers_one_fact() {
        let mut lab = Lab::populated();
        assert_eq!(lab.pay(Mode::Decline, Failure::None), Outcome::Declined);
        assert_eq!(
            lab.pay(Mode::Approve, Failure::None),
            Outcome::AlreadyDeclined
        );
        assert_eq!(
            lab.refund(Mode::Approve, Failure::None),
            Outcome::InvalidState
        );
        assert_eq!(lab.store.order().state(), State::Declined);
        assert_eq!(
            lab.store.events().next().unwrap().kind(),
            EventKind::PaymentDeclined
        );
        assert_eq!(lab.store.event_count(), 1);
        assert_eq!(lab.provider.charge_count(), 0);
    }
    #[test]
    fn refund_prepare_failure_leaves_paid_without_refund_identity() {
        let mut lab = Lab::populated();
        assert_eq!(lab.pay(Mode::Approve, Failure::None), Outcome::Approved);
        let paid = lab.store.candidate();
        assert_eq!(
            lab.refund(Mode::Approve, Failure::Prepare),
            Outcome::LocalPrepareFailed
        );
        assert_eq!(lab.store.candidate(), paid);
        assert!(lab.store.order().refund_id().is_none());
        assert_eq!(lab.provider.refund_count(), 0);
    }
    #[test]
    fn refund_timeout_before_not_found_and_identity_conflict_then_retry() {
        let mut lab = Lab::populated();
        assert_eq!(lab.pay(Mode::Approve, Failure::None), Outcome::Approved);
        assert_eq!(
            lab.refund(Mode::TimeoutBefore, Failure::None),
            Outcome::Unknown
        );
        assert_eq!(lab.store.order().state(), State::Refunding);
        assert_eq!(lab.provider.refund_count(), 0);
        let before = lab.store.candidate();
        assert_eq!(
            lab.app().reconcile(Lookup::Ok, Failure::None),
            Outcome::NotFound
        );
        assert_eq!(
            lab.app()
                .refund(RefundId::new("r2").unwrap(), Mode::Approve, Failure::None),
            Outcome::IntentConflict
        );
        assert_eq!(lab.store.candidate(), before);
        assert_eq!(lab.refund(Mode::Approve, Failure::None), Outcome::Approved);
        assert_eq!(lab.store.order().state(), State::Refunded);
        assert_eq!(lab.provider.refund_count(), 1);
        assert_eq!(lab.store.event_count(), 2);
    }
    #[test]
    fn refund_commit_failure_keeps_refunding_and_remote_effect_then_recovers() {
        let mut lab = Lab::populated();
        assert_eq!(lab.pay(Mode::Approve, Failure::None), Outcome::Approved);
        assert_eq!(
            lab.refund(Mode::Approve, Failure::Commit),
            Outcome::LocalCommitFailed
        );
        assert_eq!(lab.store.order().state(), State::Refunding);
        assert_eq!(lab.store.event_count(), 1);
        assert_eq!(lab.provider.refund_count(), 1);
        let before = lab.store.candidate();
        assert_eq!(
            lab.app().reconcile(Lookup::Unavailable, Failure::None),
            Outcome::Unknown
        );
        assert_eq!(lab.store.candidate(), before);
        assert_eq!(
            lab.pay(Mode::Approve, Failure::None),
            Outcome::AlreadyApplied
        );
        assert_eq!(
            lab.app().reconcile(Lookup::Ok, Failure::None),
            Outcome::Approved
        );
        let fact = lab.store.events().nth(1).unwrap().clone();
        assert_eq!(fact.id().as_str(), "refund:r1");
        assert_eq!(fact.refund_id().unwrap().as_str(), "r1");
        assert_eq!(fact.payment_id().as_str(), "p1");
        assert_eq!(fact.kind(), EventKind::RefundApproved);
        assert_eq!(fact.amount().minor(), 250);
        assert_eq!(
            lab.refund(Mode::Approve, Failure::Commit),
            Outcome::AlreadyApplied
        );
        assert_eq!(lab.store.events().nth(1).unwrap(), &fact);
        assert_eq!(lab.store.event_count(), 2);
        assert_eq!(lab.provider.refund_count(), 1);
    }
    #[test]
    fn timeout_after_refund_lookup_recovers_recorded_effect() {
        let mut lab = Lab::populated();
        assert_eq!(lab.pay(Mode::Approve, Failure::None), Outcome::Approved);
        assert_eq!(
            lab.refund(Mode::TimeoutAfter, Failure::None),
            Outcome::Unknown
        );
        assert_eq!(lab.provider.refund_count(), 1);
        assert_eq!(lab.store.event_count(), 1);
        assert_eq!(
            lab.app().reconcile(Lookup::Ok, Failure::None),
            Outcome::Approved
        );
        assert_eq!(lab.provider.refund_count(), 1);
        assert_eq!(lab.store.event_count(), 2);
    }
    #[test]
    fn delivery_failure_ack_failure_and_deduplication_preserve_fact_order() {
        let mut lab = Lab::populated();
        assert_eq!(lab.pay(Mode::Approve, Failure::None), Outcome::Approved);
        assert_eq!(lab.refund(Mode::Approve, Failure::None), Outcome::Approved);
        assert_eq!(
            lab.app().relay(RelayMode::SendFail),
            Outcome::RelaySendFailed
        );
        assert_eq!(lab.consumer.count(), 0);
        assert_eq!(lab.store.pending_outbox(), 2);
        assert_eq!(lab.app().relay(RelayMode::AckFail), Outcome::RelayAckFailed);
        assert_eq!(lab.consumer.count(), 1);
        assert_eq!(lab.store.pending_outbox(), 2);
        assert_eq!(lab.app().relay(RelayMode::AckFail), Outcome::RelayAckFailed);
        assert_eq!(lab.consumer.count(), 1);
        assert_eq!(lab.app().relay(RelayMode::Ok), Outcome::RelayOk);
        assert_eq!(lab.consumer.count(), 2);
        assert_eq!(lab.store.pending_outbox(), 0);
        assert_eq!(lab.consumer.facts()[0].id().as_str(), "payment:p1");
        assert_eq!(lab.consumer.facts()[1].id().as_str(), "refund:r1");
        let copied = lab.consumer.facts()[0].clone();
        assert_eq!(lab.consumer.deliver(&copied), Outcome::RelayOk);
        assert_eq!(lab.consumer.count(), 2);
        assert_eq!(lab.app().relay(RelayMode::AckFail), Outcome::RelayOk);
        assert_eq!(lab.app().relay(RelayMode::SendFail), Outcome::RelayOk);
        assert_eq!(lab.provider.charge_count(), 1);
        assert_eq!(lab.provider.refund_count(), 1);
    }
}
