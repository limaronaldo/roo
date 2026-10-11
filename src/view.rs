//! A view borrows an aggregate; it cannot extend the aggregate's lifetime.
//!
//! Positive control:
//! ```
//! use roo::{order::{CustomerId, Order}, view::OrderView};
//! let order = Order::new(CustomerId::new("c1").unwrap());
//! let view = OrderView::new(&order);
//! assert_eq!(view.customer_id(), "c1");
//! ```
//!
//! A view cannot escape its owner:
//! ```compile_fail
//! use roo::{order::{CustomerId, Order}, view::OrderView};
//! let view;
//! {
//!     let order = Order::new(CustomerId::new("c1").unwrap());
//!     view = OrderView::new(&order);
//! }
//! println!("{}", view.customer_id());
//! ```
//!
//! Two overlapping exclusive borrows are rejected (both remain in use):
//! ```compile_fail
//! use roo::order::{CustomerId, Order, OrderLine, Quantity};
//! let mut order = Order::new(CustomerId::new("c1").unwrap());
//! let first = &mut order;
//! let second = &mut order;
//! first.add_line(OrderLine::new("a", Quantity::new(1).unwrap(), 1).unwrap()).unwrap();
//! println!("{}", second.subtotal_cents());
//! ```
//!
//! Sequential exclusive borrows work because the first is no longer in use:
//! ```
//! use roo::order::{CustomerId, Order, OrderLine, Quantity};
//! let mut order = Order::new(CustomerId::new("c1").unwrap());
//! let first = &mut order;
//! first.add_line(OrderLine::new("a", Quantity::new(1).unwrap(), 1).unwrap()).unwrap();
//! let second = &mut order;
//! assert_eq!(second.subtotal_cents(), 1);
//! ```

use crate::order::Order;

pub struct OrderView<'a> {
    order: &'a Order,
}
impl<'a> OrderView<'a> {
    pub fn new(order: &'a Order) -> Self {
        Self { order }
    }
    pub fn customer_id(&self) -> &'a str {
        self.order.customer().as_str()
    }
    pub fn line_count(&self) -> usize {
        self.order.lines().len()
    }
    pub fn subtotal_cents(&self) -> u64 {
        self.order.subtotal_cents()
    }
}
