use std::fmt;

macro_rules! identity {
    ($name:ident) => {
        #[derive(Clone, Debug, PartialEq, Eq, Hash)]
        pub struct $name(String);
        impl $name {
            pub fn new(value: &str) -> Result<Self, String> {
                if value.is_empty() || !value.bytes().all(|b| b.is_ascii_alphanumeric()) {
                    return Err(format!(
                        "invalid {}: ASCII alphanumeric identity required",
                        stringify!($name)
                    ));
                }
                Ok(Self(value.to_owned()))
            }
            pub fn as_str(&self) -> &str {
                &self.0
            }
        }
    };
}
identity!(OrderId);
identity!(PaymentId);
identity!(RefundId);

#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct EventId(String);
impl EventId {
    pub fn as_str(&self) -> &str {
        &self.0
    }
    fn payment(id: &PaymentId) -> Self {
        Self(format!("payment:{}", id.as_str()))
    }
    fn refund(id: &RefundId) -> Self {
        Self(format!("refund:{}", id.as_str()))
    }
}

/// Positive minor units, checked before a value enters a request or line.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Money(i64);
impl Money {
    pub fn new(minor: i64) -> Result<Self, Outcome> {
        if minor <= 0 {
            Err(Outcome::InvalidLine)
        } else {
            Ok(Self(minor))
        }
    }
    pub fn minor(self) -> i64 {
        self.0
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum State {
    Draft,
    Pending,
    Paid,
    Declined,
    Refunding,
    Refunded,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Outcome {
    Added,
    InvalidLine,
    Overflow,
    InvalidOrder,
    InvalidState,
    IntentConflict,
    Approved,
    Declined,
    Unknown,
    NotFound,
    AlreadyApplied,
    AlreadyDeclined,
    LocalPrepareFailed,
    LocalCommitFailed,
    KeyConflict,
    RelayOk,
    RelaySendFailed,
    RelayAckFailed,
}
impl fmt::Display for Outcome {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{self:?}")
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
struct Line {
    unit: Money,
    quantity: i64,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct PaymentRequest {
    pub(crate) id: PaymentId,
    pub(crate) order: OrderId,
    pub(crate) currency: String,
    pub(crate) amount: Money,
}
#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct RefundRequest {
    pub(crate) id: RefundId,
    pub(crate) payment: PaymentId,
    pub(crate) order: OrderId,
    pub(crate) currency: String,
    pub(crate) amount: Money,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum EventKind {
    PaymentApproved,
    PaymentDeclined,
    RefundApproved,
}

/// An owned historical fact. Only domain transitions construct events.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Event {
    id: EventId,
    kind: EventKind,
    order: OrderId,
    payment: PaymentId,
    refund: Option<RefundId>,
    amount: Money,
}
impl Event {
    pub fn id(&self) -> &EventId {
        &self.id
    }
    pub fn kind(&self) -> EventKind {
        self.kind
    }
    pub fn order_id(&self) -> &OrderId {
        &self.order
    }
    pub fn payment_id(&self) -> &PaymentId {
        &self.payment
    }
    pub fn refund_id(&self) -> Option<&RefundId> {
        self.refund.as_ref()
    }
    pub fn amount(&self) -> Money {
        self.amount
    }
    pub fn currency(&self) -> &str {
        "USD"
    }
}

/// The committed store owns an Order; readers receive shared immutable views.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Order {
    id: OrderId,
    lines: Vec<Line>,
    total: i64,
    state: State,
    payment: Option<PaymentRequest>,
    refund: Option<RefundRequest>,
}
impl Order {
    pub fn new(id: OrderId) -> Self {
        Self {
            id,
            lines: Vec::new(),
            total: 0,
            state: State::Draft,
            payment: None,
            refund: None,
        }
    }
    pub fn id(&self) -> &OrderId {
        &self.id
    }
    pub fn state(&self) -> State {
        self.state
    }
    pub fn total(&self) -> i64 {
        self.total
    }
    pub fn line_count(&self) -> usize {
        self.lines.len()
    }
    pub fn payment_id(&self) -> Option<&PaymentId> {
        self.payment.as_ref().map(|r| &r.id)
    }
    pub fn refund_id(&self) -> Option<&RefundId> {
        self.refund.as_ref().map(|r| &r.id)
    }
    pub(crate) fn payment(&self) -> Option<&PaymentRequest> {
        self.payment.as_ref()
    }
    pub(crate) fn refund(&self) -> Option<&RefundRequest> {
        self.refund.as_ref()
    }

    pub(crate) fn add(&mut self, unit: i64, quantity: i64) -> Outcome {
        if self.state != State::Draft {
            return Outcome::InvalidState;
        }
        let Ok(unit) = Money::new(unit) else {
            return Outcome::InvalidLine;
        };
        if quantity <= 0 {
            return Outcome::InvalidLine;
        }
        let Some(line_total) = unit.minor().checked_mul(quantity) else {
            return Outcome::Overflow;
        };
        let Some(total) = self.total.checked_add(line_total) else {
            return Outcome::Overflow;
        };
        self.lines.push(Line { unit, quantity });
        self.total = total;
        Outcome::Added
    }
    pub(crate) fn prepare_payment(&mut self, id: PaymentId) -> Outcome {
        if self.state != State::Draft {
            return Outcome::InvalidState;
        }
        let Ok(amount) = Money::new(self.total) else {
            return Outcome::InvalidOrder;
        };
        self.payment = Some(PaymentRequest {
            id,
            order: self.id.clone(),
            currency: "USD".to_owned(),
            amount,
        });
        self.state = State::Pending;
        Outcome::Added
    }
    pub(crate) fn prepare_refund(&mut self, id: RefundId) -> Outcome {
        if self.state != State::Paid {
            return Outcome::InvalidState;
        }
        let payment = self.payment.as_ref().expect("Paid retains payment");
        self.refund = Some(RefundRequest {
            id,
            payment: payment.id.clone(),
            order: self.id.clone(),
            currency: payment.currency.clone(),
            amount: payment.amount,
        });
        self.state = State::Refunding;
        Outcome::Added
    }
    pub(crate) fn finish_payment(&mut self, approved: bool) -> Event {
        assert_eq!(
            self.state,
            State::Pending,
            "private transition precondition"
        );
        let request = self.payment.as_ref().expect("Pending retains payment");
        self.state = if approved {
            State::Paid
        } else {
            State::Declined
        };
        Event {
            id: EventId::payment(&request.id),
            kind: if approved {
                EventKind::PaymentApproved
            } else {
                EventKind::PaymentDeclined
            },
            order: request.order.clone(),
            payment: request.id.clone(),
            refund: None,
            amount: request.amount,
        }
    }
    pub(crate) fn finish_refund(&mut self) -> Event {
        assert_eq!(
            self.state,
            State::Refunding,
            "private transition precondition"
        );
        let request = self.refund.as_ref().expect("Refunding retains refund");
        self.state = State::Refunded;
        Event {
            id: EventId::refund(&request.id),
            kind: EventKind::RefundApproved,
            order: request.order.clone(),
            payment: request.payment.clone(),
            refund: Some(request.id.clone()),
            amount: request.amount,
        }
    }
}
