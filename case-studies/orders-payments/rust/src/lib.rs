//! A single-threaded payments laboratory with explicit local/remote boundaries.
//!
//! Values can be moved into a resource custodian. The old binding then cannot
//! be used (`E0382`); this says nothing about remote effect uniqueness.
//! ```compile_fail,E0382
//! use orders_payments_case::{Order, OrderId, Store};
//! let order = Order::new(OrderId::new("O1").unwrap());
//! let _store = Store::new(order);
//! println!("{:?}", order.state());
//! ```
//!
//! An immutable view cannot remain in use across an exclusive application borrow
//! (`E0502`). The resources must coordinate access inside this process.
//! ```compile_fail,E0502
//! use orders_payments_case::{Application, Consumer, Order, OrderId, Provider, Store};
//! let mut store = Store::new(Order::new(OrderId::new("O1").unwrap()));
//! let mut provider = Provider::default();
//! let mut consumer = Consumer::default();
//! let view = store.order();
//! let mut app = Application::new(&mut store, &mut provider, &mut consumer);
//! app.add(100, 1);
//! println!("{:?}", view.state());
//! ```
//!
//! Domain transitions are private to the crate (`E0624`), so callers cannot
//! skip intent preparation and directly advertise a paid order.
//! ```compile_fail,E0624
//! use orders_payments_case::{Order, OrderId};
//! let mut order = Order::new(OrderId::new("O1").unwrap());
//! order.finish_payment(true);
//! ```
//!
//! Positive examples exercise the public composed API:
//! ```
//! use orders_payments_case::*;
//! let mut store = Store::new(Order::new(OrderId::new("O1").unwrap()));
//! let mut provider = Provider::default();
//! let mut consumer = Consumer::default();
//! {
//!     let mut app = Application::new(&mut store, &mut provider, &mut consumer);
//!     assert_eq!(app.add(125, 2), Outcome::Added);
//!     assert_eq!(app.pay(PaymentId::new("p1").unwrap(), Mode::TimeoutAfter,
//!                        Failure::None), Outcome::Unknown);
//!     assert_eq!(app.reconcile(Lookup::Ok, Failure::None), Outcome::Approved);
//!     assert_eq!(app.relay(RelayMode::AckFail), Outcome::RelayAckFailed);
//!     assert_eq!(app.relay(RelayMode::Ok), Outcome::RelayOk);
//! }
//! assert_eq!(store.order().state(), State::Paid);
//! assert_eq!(provider.charge_count(), 1);
//! assert_eq!(consumer.count(), 1);
//! ```
#![forbid(unsafe_code)]

mod adapters;
mod application;
mod domain;
pub mod fixture;

pub use adapters::{Consumer, Provider, Store};
pub use application::{Application, Failure, Lookup, Mode, RelayMode};
pub use domain::{
    Event, EventId, EventKind, Money, Order, OrderId, Outcome, PaymentId, RefundId, State,
};
