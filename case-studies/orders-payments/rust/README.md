# Rust composition: orders and payments

ROO — Relationship & Ownership Oriented design is a language-independent
method, and Rust ownership is one way to realize its relationship contracts.

Begin with timeout-after-effect: the order remains Pending and the same
PaymentId supports reconciliation when the caller cannot know the provider
outcome. The [shared case](../README.md) and [contract](../SPEC.md) fix that
invariant; chapter 2's [Relationship Contract](../../../docs/02-relationship-design.md#21-the-seven-field-relationship-contract)
and [worksheet](../../../templates/relationship-contract.md) guide custody,
domain responsibility, stable identity, mutation authority, access lifetime,
execution, and failure decisions. This in-memory PaymentId lasts one scenario,
not a restart, and grants no authorization. Rust ownership and borrows enforce
local movement and aliasing rules, not provider idempotency. No caller
authorization policy is modeled.

This standalone, standard-library-only crate implements the frozen [shared
contract](../SPEC.md) using local ownership, typed identities, private domain
transitions, detached candidates, and short exclusive capability borrows.
It requires Rust 1.96, edition 2024, forbids unsafe code, and is not publishable.
Its nested workspace intentionally leaves the root laboratory package unchanged.

## Run from the repository root

```sh
cargo run --offline --manifest-path case-studies/orders-payments/rust/Cargo.toml -- case-studies/orders-payments/scenarios.tsv
cargo test --offline --manifest-path case-studies/orders-payments/rust/Cargo.toml
cargo run --offline --manifest-path case-studies/orders-payments/rust/Cargo.toml --example recovery
cargo fmt --manifest-path case-studies/orders-payments/rust/Cargo.toml -- --check
cargo clippy --offline --manifest-path case-studies/orders-payments/rust/Cargo.toml --all-targets -- -D warnings
```

The fixture binary is `roo-payments`. It accepts exactly one fixture path and
prints the contract's eleven-column TSV on stdout. Malformed input returns a
nonzero exit status with a diagnostic on stderr. Valid domain rejections appear
as closed result values in the output. The complete input is parsed structurally
before execution; no partial TSV is emitted for a rejected fixture.

These commands are instructions, not a claim that they were executed. The
integrator's validation record establishes which checks actually ran.

## Follow the code

- `domain.rs`: validated identity and money types, order-owned lines, immutable
  intent snapshots, closed state/results, and crate-private transitions.
- `adapters.rs`: independent simulated provider records/effects, atomic candidate
  replacement, retained outbox acknowledgement flags, and consumer deduplication.
- `application.rs`: composed coordinator borrowing store, provider, and consumer.
  It persists an intent before asking the provider and reloads committed state
  after any failed candidate commit. It retains no mutable cached order.
- `fixture.rs`: strict TSV grammar and signed integer boundary parsing, scenario
  execution, normalized output, and the isolated provider-conflict probe.
- `examples/recovery.rs`: runnable timeout, reconciliation, full refund, lost
  acknowledgement, and redelivery workflow with explicit observations.

A payment timeout can leave a successful remote charge beside a local Pending
order. A final local commit failure deliberately has the same retained boundary.
Reconciliation observes the existing key; same-key retry uses the persisted
request. Unknown and authoritative simulator NotFound remain different values.
A refund has its own typed identity and references a confirmed payment. Provider
records compare every request field, retain terminal results for this scenario,
and supply the idempotency guarantee themselves.

## Relationship contracts

| Relationship | Owner / custodian | Identity | Mutation authority | Access regime | Validity horizon | Execution domain | Failure boundary |
|---|---|---|---|---|---|---|---|
| Order to lines | Order owns its vector | Embedded values, no external line IDs | Private validated add operation through application | Owned values; observers receive counts/totals | Lines retained for order; frozen at Pending | One synchronous coordinator | Checked candidate arithmetic before installing any line |
| Application to Store | Caller owns Store | One O1 committed snapshot | Exclusive application capability; store replaces candidate | Short `&mut Store`; shared observation outside call | Application borrow ends before caller observes store | Single thread, no suspension | Failed replacement installs neither order nor events |
| Order to payment/refund intent | Order owns immutable request snapshots | Separate PaymentId/RefundId correlated with OrderId | Private preparation and finalization | Owned copies for provider calls | Retained through terminal order state | Two separate local transactions around remote call | Preparation failure precedes remote effect; final failure keeps persisted intent |
| Application to Provider | Caller owns independent simulator | Typed operation key plus complete request fingerprint | Application sends only persisted request; fixture probe separate | Short exclusive borrow; lookup read-only | Complete key records retained for fresh scenario | Same thread, independent effect boundary | Unknown observation never fabricates a terminal record; stable retry/reconcile |
| Store to event | Store owns committed facts and ack flags | EventId derived from typed intent | Domain constructs fact; store commits it with terminal state | Owned facts, shared read views | Retained for scenario, independent of transient candidate | Local candidate commit and later relay | Failed commit installs no event; send/ack failure retains pending record |
| Relay to Consumer | Caller owns consumer and dedup set | EventId | Deliver capability; fact payload immutable | Borrowed event copied into consumer on first delivery | Seen IDs retained for entire scenario | Single synchronous relay | Lost ack causes redelivery; duplicate fact has no second application |

`Order`, `Store`, and their resource bindings are not Copy. Compiler-negative
doctests in `lib.rs` demonstrate use after transfer (`E0382`), overlapping shared
and exclusive access (`E0502`), and inaccessible domain transitions (`E0624`).
Positive doctests demonstrate permitted composition and the runner boundary.
A compiler rejection is evidence about that access pattern, not evidence about
payment uniqueness, transaction durability, or all distributed interleavings.
The integrator checks the actual diagnostic codes independently of rustdoc's
compile-fail acceptance.

## Runtime evidence and limits

Unit tests assert intermediate states so recovery cannot conceal failures:
unchanged additions; multiplication/sum overflow; out-of-range numeric text;
malformed late actions; initial preparation failure; terminal/reconciliation
commit failure; Unknown versus NotFound; payment fingerprint mismatch across
order/currency/amount; refund mismatch across payment/order/currency/amount;
independent typed namespaces; frozen lines; invalid states; refund timeout before
retry and identity conflict; stable fact identity; consumer deduplication and
outbox ordering after send/ack failures.

The complete shared fixture comparison is separate acceptance evidence owned by
the integrator. No test here proves every interleaving. This is a deterministic
single-threaded in-memory model with no real charges, database, disk durability,
network, concurrency, authentication, fraud, PCI compliance, process crash, or
provider retention-window validation. Ownership enforces local access rules;
provider idempotency and candidate atomicity are explicit simulator contracts.
