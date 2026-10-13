//! Small, executable laboratories for ownership-aware object design.
//!
//! Domain identity, memory ownership, and permission to mutate are distinct.
//! Each module keeps that distinction explicit without a shared framework.
//!
//! Relationship contracts in this laboratory, using the compact keys of the
//! eight-field Relationship Contract in `docs/02-relationship-design.md`:
//!
//! | Relationship | Custodian | Identity | Coordinator | Authorization | Access | Horizon | Execution | Failure |
//! |---|---|---|---|---|---|---|---|---|
//! | Order to lines | Order retains line values | Customer ID is external domain identity; lines have none | Order aggregate methods | Not implemented; callers are not distinguished | Only aggregate methods mutate | Lines live with the order | Synchronous | Checked amounts; rejected line returned for recovery |
//! | Quote to policy | Caller retains policy | None; behavior is selected by a borrowed trait | Quote validation | Not implemented; callers are not distinguished | Immutable policy borrow | One call | Synchronous | Out-of-contract discount rejected |
//! | Draft to submitted | Transition transfers order ownership | Customer ID only; no order identity | State transition | Not implemented; callers are not distinguished | Only Draft edits | Old value consumed | Synchronous | Failure returns the draft for retry |
//! | Graph to nodes | Graph retains nodes | Store-scoped generational handles | Graph methods | Not implemented; callers are not distinguished | Exclusive graph methods mutate | Removal invalidates handles | Synchronous | Stale and foreign IDs rejected |
//! | Queue to observers | Queue retains deliveries | Queue-scoped observer IDs | Queue owner | Not implemented; callers are not distinguished | Owner subscribes and drains | Unsubscribe ends delivery validity | Deferred, single owner | Rejected message returned |
//! | View to order | Caller retains order | Borrowed order's customer ID | Order API | Not implemented; callers are not distinguished | Shared borrow | Owner must outlive view | Synchronous reads | Invalid borrows rejected by compiler |
//! | Principal to order approval | Coordinator retains orders and policy | Principal and order IDs are trusted fixture input | Policy and transition under one lock | Permission rechecked at execution | Detached observation is no credential; approval is controlled | Observation grants nothing later | One local lock for policy and transition | Revocation before execution denies without effect |
//!
//! The `command_transfer` example adds an execution boundary: an owned command
//! crosses a standard channel, while a scoped worker shares only an immutable
//! policy borrow. Channel disconnection and thread panic are explicit failure
//! points; the example treats them as programmer failures with `expect`.
#![forbid(unsafe_code)]

pub mod authorization;
pub mod events;
pub mod graph;
pub mod order;
pub mod strategy;
pub mod typestate;
pub mod view;

// Keep the published chapter examples executable without adding runtime code.
#[cfg(doctest)]
#[doc = include_str!("../docs/06-cross-language.md")]
pub struct CrossLanguageDocumentation;

#[cfg(doctest)]
#[doc = include_str!("../docs/08-rust-and-object-design.md")]
pub struct ObjectDesignDocumentation;
