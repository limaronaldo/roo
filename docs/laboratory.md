# The executable laboratory

The `roo` package is a small standard-library-only teaching library. Its APIs make selected ownership and behavioral decisions observable. It is not a production order system, graph database, event broker, or distributed workflow engine.

ROO is language-independent. This lab realizes selected decisions from the
[canonical contract and procedure](02-relationship-design.md) in Rust.
See [claims and limits](claims-and-limits.md) for the evidence boundaries.

This package defines the Rust laboratory qualification for selected Rust mechanics and behaviors. That qualification is separate from adopting the ROO method in another language: carry over the same scenarios, invariants, and contracts, then establish evidence for that language's runtime, storage, and protocols.

## Relationship map

| Relationship | Owner and authority | Representation | Evidence |
|---|---|---|---|
| Order → lines | `Order` owns its lines and changes them through checked operations | Private `Vec<OrderLine>` | Overflow leaves both aggregate state and rejected line recoverable |
| Order → customer | Order retains an identifier, not the customer | Validated `CustomerId` value | Empty identifiers rejected; existence remains an external concern |
| Pricing → policy | Caller retains the policy; quoting borrows it | Generic `Discount` or `&dyn Discount` | Shared contract tests and rejection of an excessive discount |
| Draft → Submitted | Transition consumes the draft; failure returns it | Distinct types and `Result` | Successful retry; forbidden method and use-after-move rejection |
| View → order | View temporarily borrows its owner | `OrderView<'a>` | Lifetime rejection and valid borrowing controls |
| Graph → nodes | Graph owns slots; edges retain local identities | Store-scoped generational `NodeId` | Stale, reused and foreign-store handles rejected |
| Queue → observers / messages | Queue owns subscription registry and pending payloads | Queue-scoped IDs and owned deliveries | Unsubscribe suppresses pending notifications; foreign IDs rejected |
| Worker → command | Sender transfers draft; scoped worker borrows immutable policy | Owned channel message and scoped thread | Executed command workflow and asserted result |

## Source tour

- [Order aggregate](../src/order.rs): private state, validated quantity and identifiers, checked money arithmetic, failure recovery.
- [Strategy](../src/strategy.rs): concrete and runtime behavior substitution, with an enforced numerical postcondition. Implementing a trait alone does not establish behavioral correctness.
- [Typestate](../src/typestate.rs): consuming transition and retryable failure state. The submitted type exposes no editing method.
- [Borrowed views](../src/view.rs): data access bounded by the owner's lifetime. Two mutable borrows can occur sequentially; overlapping exclusive borrows remain forbidden.
- [Graph](../src/graph.rs): handles include store identity, slot and generation. Exhausted generations are retired rather than wrapping into old identities.
- [Event queue](../src/events.rs): deferred delivery avoids storing subscriber borrows or invoking callbacks while the queue is mutably borrowed.

## Executable scenarios

```sh
cargo run --offline --example order_workflow
cargo run --offline --example graph_events
cargo run --offline --example command_transfer
```

[Order workflow](../examples/order_workflow.rs) first rejects an empty draft, recovers it, adds two units priced at 2,500 cents each, and submits with a 10% discount. Its asserted total is 4,500 cents.

[Graph and events](../examples/graph_events.rs) removes a parent, detects the now-stale parent link, creates a distinct replacement identity, and delivers an owned notification. Unsubscription rejects a later enqueue.

[Command transfer](../examples/command_transfer.rs) moves a draft through a channel to a scoped worker. The worker borrows a 20% discount policy and returns a submitted order totaling 800 cents. The example's `expect` calls deliberately keep application-level recovery out of this small scenario.

## Validation commands

```sh
cargo fmt --all -- --check
cargo test --offline
cargo clippy --offline --all-targets -- -D warnings
cargo doc --offline --no-deps
```

`cargo test` includes module tests and Rustdoc examples, including expected compilation failures. `cargo test --all-targets` alone does not execute doctests; run `cargo test --doc` separately when using that variant.

Compiler examples in source demonstrate these distinct obligations:

| Invalid operation | Required rejection |
|---|---|
| Calling `add_line` on `Submitted` | Method unavailable on that type |
| Reading a draft after submission consumes it | Use of moved value |
| Using an order view after its owner is dropped | Borrowed value does not live long enough |
| Keeping two exclusive borrows in simultaneous use | Multiple mutable borrows |

A passing `compile_fail` test proves that compilation failed. Checking the diagnostic and keeping a positive control are necessary to establish that it failed for the lesson's intended reason. The initial validation records those diagnostics in [validation evidence](../research/validation.md).

## Limits that matter

- The order model uses unsigned integer cents and one implied currency. It does not model taxes, currencies, rounding policies beyond integer percentage truncation, inventory, customer authorization, or database transactions.
- `Order` is the mutable aggregate used inside the typestate workflow. The lifecycle guarantee applies to the `Draft`/`Submitted` API; independent aggregates remain editable according to their own API.
- A `CustomerId` is syntactically nonempty. It is not proof that a customer exists or that a caller may access it.
- A graph deletion intentionally leaves stale logical edges and parent links. Every lookup must validate the handle; there is no cascading-delete or referential-integrity policy. IDs are local to a process and are not persistence keys.
- The event queue is single-owner, in-memory and unbounded. Unsubscribe suppresses pending deliveries that have not been drained; it cannot revoke a delivery already transferred to a consumer. There is no acknowledgement, retry, persistence, broadcast, fairness or exactly-once guarantee.
- Channel transfer proves that the concrete types satisfy the Rust thread-boundary requirements and demonstrates one successful run. The unbounded channel has no backpressure, durable delivery or recovery protocol. Scoped threads join before their scope ends; that does not prevent logical deadlocks in arbitrary applications.
- Private fields, safe Rust, tests and linting establish useful local properties. They do not establish all architectural qualities or all possible behaviors.

The architecture chapters discuss production concerns beyond this laboratory. Their design sketches should not be mistaken for implemented capabilities in the package.
