//! Consuming transitions make a submitted order unavailable for editing.
//!
//! A failed transition returns the draft, preserving retryable ownership.
//!
//! ```
//! use roo::{order::*, strategy::NoDiscount, typestate::*};
//! let mut draft = Draft::new(CustomerId::new("c1").unwrap());
//! draft.add_line(OrderLine::new("book", Quantity::new(1).unwrap(), 500).unwrap()).unwrap();
//! let submitted = draft.submit(&NoDiscount).unwrap();
//! assert_eq!(submitted.total_cents(), 500);
//! ```
//!
//! Submitted has no draft mutation method:
//! ```compile_fail
//! use roo::{order::*, strategy::NoDiscount, typestate::*};
//! let mut draft = Draft::new(CustomerId::new("c1").unwrap());
//! draft.add_line(OrderLine::new("book", Quantity::new(1).unwrap(), 500).unwrap()).unwrap();
//! let mut submitted = draft.submit(&NoDiscount).unwrap();
//! submitted.add_line(OrderLine::new("pen", Quantity::new(1).unwrap(), 100).unwrap());
//! ```
//!
//! A transition also consumes the original draft:
//! ```compile_fail
//! use roo::{order::CustomerId, strategy::NoDiscount, typestate::Draft};
//! let draft = Draft::new(CustomerId::new("c1").unwrap());
//! let result = draft.submit(&NoDiscount);
//! println!("{}", draft.order().subtotal_cents());
//! drop(result);
//! ```

use crate::order::{CustomerId, Order, OrderLine, RejectedLine};
use crate::strategy::{Discount, quote};

#[derive(Debug)]
pub struct Draft {
    order: Order,
}
#[derive(Debug)]
pub struct Submitted {
    order: Order,
    total_cents: u64,
}
#[derive(Debug, PartialEq, Eq)]
pub enum SubmitReason {
    EmptyOrder,
    InvalidDiscount,
}
#[derive(Debug)]
pub struct SubmitFailure {
    pub draft: Draft,
    pub reason: SubmitReason,
}

impl Draft {
    pub fn new(customer: CustomerId) -> Self {
        Self {
            order: Order::new(customer),
        }
    }
    pub fn add_line(&mut self, line: OrderLine) -> Result<(), RejectedLine> {
        self.order.add_line(line)
    }
    pub fn order(&self) -> &Order {
        &self.order
    }
    pub fn submit<D: Discount + ?Sized>(self, policy: &D) -> Result<Submitted, SubmitFailure> {
        if self.order.lines().is_empty() {
            return Err(SubmitFailure {
                draft: self,
                reason: SubmitReason::EmptyOrder,
            });
        }
        match quote(self.order.subtotal_cents(), policy) {
            Ok(total_cents) => Ok(Submitted {
                order: self.order,
                total_cents,
            }),
            Err(_) => Err(SubmitFailure {
                draft: self,
                reason: SubmitReason::InvalidDiscount,
            }),
        }
    }
}
impl Submitted {
    pub fn order(&self) -> &Order {
        &self.order
    }
    pub fn total_cents(&self) -> u64 {
        self.total_cents
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{order::Quantity, strategy::NoDiscount};
    #[test]
    fn failed_transition_can_be_retried() {
        let failure = Draft::new(CustomerId::new("c1").unwrap())
            .submit(&NoDiscount)
            .unwrap_err();
        assert_eq!(failure.reason, SubmitReason::EmptyOrder);
        let mut draft = failure.draft;
        draft
            .add_line(OrderLine::new("book", Quantity::new(2).unwrap(), 500).unwrap())
            .unwrap();
        assert_eq!(draft.submit(&NoDiscount).unwrap().total_cents(), 1000);
    }

    #[test]
    fn invalid_strategy_preserves_nonempty_draft_for_retry() {
        struct Excessive;
        impl Discount for Excessive {
            fn discount_cents(&self, _: u64) -> u64 {
                u64::MAX
            }
        }
        let mut draft = Draft::new(CustomerId::new("c1").unwrap());
        draft
            .add_line(OrderLine::new("book", Quantity::new(1).unwrap(), 500).unwrap())
            .unwrap();
        let failure = draft.submit(&Excessive).unwrap_err();
        assert_eq!(failure.reason, SubmitReason::InvalidDiscount);
        assert_eq!(failure.draft.order().lines().len(), 1);
        assert_eq!(
            failure.draft.submit(&NoDiscount).unwrap().total_cents(),
            500
        );
    }
}
