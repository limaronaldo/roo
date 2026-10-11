//! Persistent orders with separately committed provider and consumer resources.
//!
//! Moving an owned domain snapshot consumes the old binding (`E0382`).
//! ```compile_fail,E0382
//! use roo_postgres_case::{Order, OrderId};
//! let order = Order::new(OrderId::new("O1").unwrap());
//! let owned = order;
//! println!("{:?}", order.state());
//! ```
//!
//! A live transaction exclusively borrows its Client (`E0499`).
//! ```compile_fail,E0499
//! use postgres::Client;
//! fn conflicting(client: &mut Client) {
//!     let mut tx = client.transaction().unwrap();
//!     client.simple_query("SELECT 1").unwrap();
//!     tx.simple_query("SELECT 2").unwrap();
//! }
//! ```
//!
//! A transaction cannot outlive the Client it borrows (`E0597`).
//! ```compile_fail,E0597
//! use postgres::{Client, NoTls};
//! let tx;
//! {
//!     let mut client = Client::connect("host=127.0.0.1", NoTls).unwrap();
//!     tx = client.transaction().unwrap();
//! }
//! tx.commit().unwrap();
//! ```
//!
//! Public code cannot invoke terminal transitions (`E0624`).
//! ```compile_fail,E0624
//! use roo_postgres_case::{Order, OrderId};
//! let mut order = Order::new(OrderId::new("O1").unwrap());
//! order.finish_payment(true);
//! ```
//!
//! The positive transaction example compiles without connecting during doctests.
//! ```
//! use postgres::Client;
//! fn sequential(client: &mut Client) -> Result<(), postgres::Error> {
//!     { let mut tx = client.transaction()?; tx.simple_query("SELECT 1")?; tx.rollback()?; }
//!     client.simple_query("SELECT 2")?;
//!     Ok(())
//! }
//! ```
//! ```
//! use roo_postgres_case::{Order, OrderId, PaymentId, Money, State};
//! let order = Order::new(OrderId::new("O1").unwrap());
//! assert_eq!(order.state(), State::Draft);
//! assert_eq!(order.total(), 0);
//! assert!(PaymentId::new("bad-id").is_err());
//! assert_eq!(Money::new(5).unwrap().minor(), 5);
//! ```
#![forbid(unsafe_code)]
pub mod database;
pub mod domain;
pub mod fixture;
pub use domain::*;
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
