//! An aggregate owns its lines but refers to a customer by domain identity.
//!
//! `CustomerId` does not keep a customer alive or prove it exists. Resolving it
//! against a customer repository is a separate application responsibility.

use std::num::NonZeroU32;

#[derive(Debug, PartialEq, Eq)]
pub enum OrderError {
    EmptyCustomerId,
    EmptySku,
    ZeroQuantity,
    AmountOverflow,
}

#[derive(Debug, PartialEq, Eq, Hash)]
pub struct CustomerId(String);

impl CustomerId {
    pub fn new(value: impl Into<String>) -> Result<Self, OrderError> {
        let value = value.into();
        if value.trim().is_empty() {
            Err(OrderError::EmptyCustomerId)
        } else {
            Ok(Self(value))
        }
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

#[derive(Debug, PartialEq, Eq)]
pub struct Quantity(NonZeroU32);

impl Quantity {
    pub fn new(value: u32) -> Result<Self, OrderError> {
        NonZeroU32::new(value)
            .map(Self)
            .ok_or(OrderError::ZeroQuantity)
    }

    pub fn get(&self) -> u32 {
        self.0.get()
    }
}

#[derive(Debug, PartialEq, Eq)]
pub struct OrderLine {
    sku: String,
    quantity: Quantity,
    unit_price_cents: u64,
    total_cents: u64,
}

impl OrderLine {
    pub fn new(
        sku: impl Into<String>,
        quantity: Quantity,
        unit_price_cents: u64,
    ) -> Result<Self, OrderError> {
        let sku = sku.into();
        if sku.trim().is_empty() {
            return Err(OrderError::EmptySku);
        }
        let total_cents = unit_price_cents
            .checked_mul(u64::from(quantity.get()))
            .ok_or(OrderError::AmountOverflow)?;
        Ok(Self {
            sku,
            quantity,
            unit_price_cents,
            total_cents,
        })
    }

    pub fn sku(&self) -> &str {
        &self.sku
    }
    pub fn quantity(&self) -> &Quantity {
        &self.quantity
    }
    pub fn unit_price_cents(&self) -> u64 {
        self.unit_price_cents
    }
    pub fn total_cents(&self) -> u64 {
        self.total_cents
    }
}

#[derive(Debug)]
pub struct Order {
    customer: CustomerId,
    lines: Vec<OrderLine>,
    subtotal_cents: u64,
}

impl Order {
    pub fn new(customer: CustomerId) -> Self {
        Self {
            customer,
            lines: Vec::new(),
            subtotal_cents: 0,
        }
    }

    /// On overflow, returns the owned line so the caller can recover it.
    pub fn add_line(&mut self, line: OrderLine) -> Result<(), RejectedLine> {
        let Some(total) = self.subtotal_cents.checked_add(line.total_cents) else {
            return Err(RejectedLine {
                line,
                reason: OrderError::AmountOverflow,
            });
        };
        self.lines.push(line);
        self.subtotal_cents = total;
        Ok(())
    }

    pub fn customer(&self) -> &CustomerId {
        &self.customer
    }
    pub fn lines(&self) -> &[OrderLine] {
        &self.lines
    }
    pub fn subtotal_cents(&self) -> u64 {
        self.subtotal_cents
    }
}

#[derive(Debug)]
pub struct RejectedLine {
    pub line: OrderLine,
    pub reason: OrderError,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rejects_business_invalid_values() {
        assert_eq!(Quantity::new(0), Err(OrderError::ZeroQuantity));
        assert_eq!(CustomerId::new("  "), Err(OrderError::EmptyCustomerId));
        assert_eq!(
            OrderLine::new("", Quantity::new(1).unwrap(), 1),
            Err(OrderError::EmptySku)
        );
        assert_eq!(
            OrderLine::new("x", Quantity::new(2).unwrap(), u64::MAX),
            Err(OrderError::AmountOverflow)
        );
    }

    #[test]
    fn rejected_add_preserves_aggregate_and_line() {
        let mut order = Order::new(CustomerId::new("customer-7").unwrap());
        order
            .add_line(OrderLine::new("a", Quantity::new(1).unwrap(), u64::MAX).unwrap())
            .unwrap();
        let rejected = order
            .add_line(OrderLine::new("b", Quantity::new(1).unwrap(), 1).unwrap())
            .unwrap_err();
        assert_eq!(rejected.line.sku(), "b");
        assert_eq!(order.lines().len(), 1);
        assert_eq!(order.subtotal_cents(), u64::MAX);
    }
}
