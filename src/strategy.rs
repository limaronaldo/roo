//! Strategy uses behavior substitution, not shared representation.
//!
//! Static dispatch (`quote`) and dynamic dispatch (`quote_dyn`) enforce the
//! same observable contract. A trait alone cannot prove that contract.

/// A discount must not exceed the subtotal. `quote` checks this at runtime.
pub trait Discount {
    fn discount_cents(&self, subtotal_cents: u64) -> u64;
}

pub struct NoDiscount;
impl Discount for NoDiscount {
    fn discount_cents(&self, _: u64) -> u64 {
        0
    }
}

pub struct Percentage {
    percent: u8,
}
impl Percentage {
    pub fn new(percent: u8) -> Option<Self> {
        (percent <= 100).then_some(Self { percent })
    }
}
impl Discount for Percentage {
    fn discount_cents(&self, subtotal: u64) -> u64 {
        // Widen before multiplication: even the largest subtotal is safe.
        (u128::from(subtotal) * u128::from(self.percent) / 100) as u64
    }
}

#[derive(Debug, PartialEq, Eq)]
pub struct InvalidDiscount;

pub fn quote<D: Discount + ?Sized>(subtotal: u64, policy: &D) -> Result<u64, InvalidDiscount> {
    subtotal
        .checked_sub(policy.discount_cents(subtotal))
        .ok_or(InvalidDiscount)
}

pub fn quote_dyn(subtotal: u64, policy: &dyn Discount) -> Result<u64, InvalidDiscount> {
    quote(subtotal, policy)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn contract<D: Discount>(policy: &D) {
        for subtotal in [0, 1, 99, 100, 10_001, u64::MAX] {
            let total = quote_dyn(subtotal, policy).unwrap();
            assert!(total <= subtotal);
            assert_eq!(quote(subtotal, policy), Ok(total));
        }
    }

    #[test]
    fn built_in_strategies_obey_same_contract() {
        contract(&NoDiscount);
        for percent in [0, 10, 50, 100] {
            contract(&Percentage::new(percent).unwrap());
        }
        assert!(Percentage::new(101).is_none());
        assert_eq!(quote(999, &Percentage::new(10).unwrap()), Ok(900));
    }

    #[test]
    fn trait_implementation_does_not_imply_valid_behavior() {
        struct Bad;
        impl Discount for Bad {
            fn discount_cents(&self, _: u64) -> u64 {
                100
            }
        }
        assert_eq!(quote(99, &Bad), Err(InvalidDiscount));
    }
}
