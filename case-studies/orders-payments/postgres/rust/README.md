# Rust PostgreSQL orders and payments

ROO — Relationship & Ownership Oriented design is a language-independent
method; this Rust implementation makes local access decisions visible while
the database coordinates durable state across processes.

Begin with a provider record committed before a failed finalization: the
persisted intent and same typed operation identity must support recovery in a
fresh process. The [frozen PostgreSQL contract](../SPEC.md) and
[original case](../../README.md) set the behavior. Chapter 2's
[Relationship Contract](../../../../docs/02-relationship-design.md#21-the-seven-field-relationship-contract)
and [worksheet](../../../../templates/relationship-contract.md) help decide who
retains resources, who owns domain decisions, which identities survive restart,
and where mutation, access, execution, and failure boundaries lie. Rust bounds
Client/Transaction access locally; PostgreSQL transactions and locks coordinate
processes. IDs are not credentials, and this case models no caller
authentication or authorization.

This standalone Rust 2024 crate implements the frozen [PostgreSQL contract](../SPEC.md).
It uses synchronous `postgres = "=0.19.14"` without optional features and targets
Rust 1.96. The `roo-postgres` binary accepts `fixtures PATH`, `init SCOPE`,
`step SCOPE ACTION`, and `snapshot SCOPE`. Successful output is the shared
11-column TSV; errors are bounded stderr diagnostics and nonzero exit codes.

The integrator creates the dedicated synthetic cluster and installs
`../schema.sql` before using these commands. The runner requires all four
structured environment values and rejects any host other than 127.0.0.1 or
user/database other than roo_test. It does not read DATABASE_URL.

```sh
export ROO_PG_HOST=127.0.0.1
export ROO_PG_PORT=55432   # use the actual dedicated harness port
export ROO_PG_DATABASE=roo_test
export ROO_PG_USER=roo_test
cargo build --locked
./target/debug/roo-postgres init demo
./target/debug/roo-postgres step demo add:125:2
./target/debug/roo-postgres step demo pay:p1:timeout_after:none
./target/debug/roo-postgres step demo reconcile:ok:none
./target/debug/roo-postgres step demo relay:ack_fail
./target/debug/roo-postgres step demo relay:ok
./target/debug/roo-postgres snapshot demo
```

Run the shared fixtures with a fresh run prefix on each invocation; an existing
scope is rejected without a reset. All fixture scopes are reserved in one
transaction before the first action; a collision rolls back the whole reservation:

```sh
ROO_RUN_ID=rust_first ./target/debug/roo-postgres fixtures ../../scenarios.tsv
cargo test --locked
cargo test --locked --doc
```

`Database` owns configuration, while each short operation creates its own
Client and a Transaction borrowing that Client. The application prepares a
persisted intent under the order row lock, releases it before provider access,
and finalizes with a new locked/revalidated transaction. Provider transactions
use a separate connection and a scope advisory lock. Terminal state and an
immutable outbox fact commit together. Inbox insertion commits on an independent
connection before acknowledgement. Relay retains the order lock during that
small consumer transaction and acknowledges one event per app transaction.

Domain identities are distinct types, request/event fields are inaccessible to
public callers, and domain arithmetic uses checked i64 multiplication and sums.
Rehydration replays validated line facts and transitions before coordination.
SQL supplies scalar constraints, locks, uniqueness and atomic persistence;
application code enforces legal transitions and complete fingerprints.

`prepare` and `commit` failure injections write the candidate changes and then
explicitly roll back the relevant app transaction. They never roll back provider
or inbox effects. Known-aborted transaction bodies with SQLSTATE 40001, 40P01 or
55P03 receive at most three attempts using fresh connections. COMMIT failures
escape without an automatic replay: inspect retained state in a new process,
then reconcile or retry a stable payment/refund identity. Do not automatically
repeat an add whose commit observation was lost.

Optional gate environment variables are `ROO_GATE_POINT`, positive
`ROO_GATE_LOCK`, and `ROO_WORKER_ID` (at most 32 ASCII alphanumeric/underscore
characters). Supported points are inside_prepare, after_prepare, after_effect,
after_finalize and after_delivery. A dedicated gate connection sets its
application_name to `roo:<worker>:<point>` and waits on a harness-owned session
advisory lock with 30-second timeouts. Normal connections use five-second connect
and lock limits and a ten-second statement limit.

Pure unit tests exercise unchanged rejected candidates, arithmetic/parser
boundaries, typed identities, copied terminal facts, and complete request
fingerprints. Positive doctests and intended compile-fail examples demonstrate
move-after-use, a Client's exclusive Transaction borrow, the transaction's
borrowed lifetime, and private terminal transitions. These compiler restrictions
do not establish distributed invariants. The integrator owns fixture/oracle,
malformed input, database, concurrency, process-kill and PostgreSQL restart
acceptance. This README describes commands and implementation; executed results
must be recorded separately. No production readiness, physical power-loss or
real payment-network guarantee is implied.
