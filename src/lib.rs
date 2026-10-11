//! Small, executable laboratories for ownership-aware object design.
//!
//! Domain identity, memory ownership, and permission to mutate are distinct.
//! Each module keeps that distinction explicit without a shared framework.
//!
//! Relationship contracts in this laboratory:
//!
//! | Relationship | Owner and identity | Mutation and validity | Execution and failure |
//! |---|---|---|---|
//! | Order to lines | Order owns values; customer ID is external domain identity | Only aggregate methods mutate; lines live with order | Synchronous; checked amounts and recoverable rejected line |
//! | Quote to policy | Caller owns policy; behavior selected by a borrowed trait | Immutable borrow valid for call | Synchronous; out-of-contract discount rejected |
//! | Draft to submitted | Transition transfers order ownership | Only Draft edits; old value consumed | Synchronous; failure returns draft for retry |
//! | Graph to nodes | Graph owns nodes; store-scoped generational handles identify them | Exclusive graph methods mutate; removal invalidates handles | Synchronous; stale and foreign IDs rejected |
//! | Queue to observers | Queue owns deliveries; queue-scoped IDs refer to subscribers | Queue owner subscribes and drains; unsubscribe ends delivery validity | Deferred, single-owner; rejected message returned |
//! | View to order | Caller owns order; view contains borrowed access | Shared borrow; owner must outlive view | Synchronous reads; invalid borrows rejected by compiler |
//!
//! The `command_transfer` example adds an execution boundary: an owned command
//! crosses a standard channel, while a scoped worker shares only an immutable
//! policy borrow. Channel disconnection and thread panic are explicit failure
//! points; the example treats them as programmer failures with `expect`.
#![forbid(unsafe_code)]

pub mod events;
pub mod graph;
pub mod order;
pub mod strategy;
pub mod typestate;
pub mod view;
