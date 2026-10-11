# Orders and payments: PostgreSQL contract

Status: frozen shared implementation contract, 2026-10-11. This extends the
[original specification](../SPEC.md) with persistent storage, concurrent
processes, and restart recovery. Its 42 existing scenario rows, action grammar,
domain outcomes, and eleven output fields remain unchanged. The original
in-memory sources and evidence remain a separate baseline.

## Domain and authority

The original one-order, one-payment, one-full-refund state machine applies in
each named scope. A scope names an isolated synthetic scenario, not a tenant
authorization boundary. OrderId remains `O1`, currency remains USD. IDs are
nonempty ASCII alphanumeric tokens; scope additionally permits underscores.
Money uses checked signed-64-bit integer minor units. The application validates
an entire action or fixture row before opening a transaction; out-of-range
integer text yields Overflow, malformed integer text rejects the input.

Both Java and Rust own domain validation, typed identities, state transition
rules, immutable request/event values, and orchestration. SQL is a persistence
adapter, with scalar/state-shape checks, uniqueness, atomic commits and row
locking. There are no domain stored procedures. The Java template variant, if
provided, retains a final algorithm and narrow adapter hooks; composition and
Rust implement the same protocol.

[schema.sql](schema.sql) is installed once by the dedicated local harness. It
does not drop data or initialize an arbitrary database. No command silently
resets existing scopes. `roo_app.orders` is the serialization row;
`roo_app.lines` retains line facts; `roo_app.outbox` retains terminal facts and
acknowledgements. `roo_provider.records` and `roo_consumer.inbox` deliberately
have no foreign keys to app tables: each commits independently on its own
connection. Approved provider records count effects; no additional mutable
counter can drift from their retained fingerprints.

Database checks do not prove that an arbitrary SQL writer preserves legal
transition history, sum(lines) = total, immutable prior events, or the provider's
approved-parent/full-amount refund relationship. The adapters enforce those
cross-row rules under the locks below. This is a trusted local educational
database; it does not claim RLS, tenant isolation, or least-privilege deployment.

## Short local transactions and independent effects

All connections use READ COMMITTED. Every app mutation first selects its scope's
order `FOR UPDATE`, then reads/revalidates the current row. Add inserts a line
and changes the total in that same transaction, only in Draft. Allocate line_no
while holding the order lock. A rejected add installs nothing.

Prepare validates the locked state and the entire immutable request. Draft to
Pending and Paid to Refunding commit the intent before the provider runs.
Matching pending intents may retry; differing IDs return IntentConflict.
Existing terminal states return the original AlreadyApplied/AlreadyDeclined
outcomes. Release the transaction and order lock before any provider call or
lookup. No cached object may advertise an uncommitted transition.

The provider opens a different connection and transaction, takes
`pg_advisory_xact_lock(hashtextextended(scope, 0))`, then reads the complete
existing `(scope, kind, operation_id)` record. Identical fingerprints return the
stable result; changed order, currency, amount or parent payment returns
KeyConflict. The lock serializes all simulated provider writes in a scope;
hash collisions can reduce concurrency but cannot bypass exclusion. For a new
refund, read and verify the Approved parent payment's complete amount and
identity and absence of another refund before insertion. The unique partial
index is a second defense against two refund keys for one payment. Commit
Approved/Declined independently before returning. timeout_before creates no
record; timeout_after commits Approved but returns Unknown. Lookup is read-only,
and NotFound remains distinct from Unknown. Retention lasts until explicit
harness cleanup; no eviction or external-provider claim is made.

Finalize opens a new app transaction and locks/reloads the order. Revalidate
the same intent and full immutable request. If another worker already finalized
it, return the matching terminal no-op without inserting a second event or
regressing the state (a payment may since have entered Refunding/Refunded).
Otherwise change Pending to Paid/Declined, or Refunding to Refunded, and insert
the corresponding deterministic outbox event in the same transaction. Never
blindly overwrite a conflicting existing event. The primary key deduplicates
stable event IDs. Refund preparation and finalization use the same order lock
as payment/add, so competing refund identities cannot both be installed.

The original prepare/commit action injections explicitly roll back only the
relevant initial/final local transaction. They remain LocalPrepareFailed and
LocalCommitFailed, respectively, and never roll back a provider transaction.
No-op/Unknown/NotFound has no final commit to fail.

## Relay and snapshots

Relay uses bounded serialized durable semantics: hold the order row lock while
reading pending outbox rows in seq order and acknowledging them. It calls a
consumer on a separate connection, which inserts the complete copied event in
its inbox and commits before the app marks delivered. A duplicate EventId must
compare the full fingerprint rather than silently accept conflicting content.
After `INSERT ... ON CONFLICT DO NOTHING`, use a new statement to read the
winning row: READ COMMITTED does not guarantee the losing insert can see it in
the same statement snapshot. Unique inbox insertion is the simulated consumer
effect. It must not acquire app/provider locks, preventing inverse lock order.

The relay's app lock deliberately spans this small local consumer transaction;
this serialized simulator trades throughput for exact fixture ordering. It is
not a production remote-network lock policy. send_fail performs no delivery;
ack_fail commits the first inbox event and rolls back that event's local
acknowledgement. Earlier committed acknowledgements may remain. A retry
redelivers safely. Competing relays block on the same order lock. A killed relay
rolls back its app transaction while already committed consumer inserts survive.

Snapshot counts all retained provider effects, events, inbox entries, and
undelivered events for one scope. Obtain the entire snapshot in a single SELECT
with scalar aggregates, or a read-only REPEATABLE READ transaction, to avoid
torn observations. An action's returned outcome may describe its own linearized
decision while its subsequent snapshot includes another worker's later commit.

## Persistent command interface

Runners support these commands (Java composition/template entry points use the
same arguments; Rust uses its single binary):

```text
fixtures PATH
init SCOPE
step SCOPE ACTION
snapshot SCOPE
```

`fixtures` parses the complete file before executing, requires fresh scenario
scopes, creates each Draft, then executes unchanged actions and produces the
same 42-row oracle output. It requires `ROO_RUN_ID`, an ASCII alphanumeric or
underscore prefix: its database scopes are `<run>_<scenario>` while its output
preserves the original scenario labels. The harness supplies a fresh prefix
for every fixture invocation; an already existing fixture scope rejects the
run without resetting data. `init` idempotently creates a Draft if absent and
otherwise reads the existing scope, never resetting it. `step` executes exactly one original grammar action on an existing
scope. `snapshot` only reads an existing scope. Every successful invocation
emits the original eleven-field header once and its row(s); scenario is the
scope. `init` and `snapshot` use `-` for last_result, a diagnostic sentinel, not
a new action outcome. Failures print bounded diagnostics only to stderr and
exit nonzero; never print DSNs, SQL parameters containing credentials, or stack
traces with connection strings. Missing scope, bad config, malformed input or
unexpected database failure is a runner error, not a fabricated domain result.

Configuration is structured environment: `ROO_PG_HOST=127.0.0.1`,
`ROO_PG_PORT`, `ROO_PG_DATABASE=roo_test`, `ROO_PG_USER=roo_test`. Require all
four explicit values, a port in 1..65535, database/user equal to roo_test,
reject host values other than 127.0.0.1, and do not consume DATABASE_URL or
arbitrary DSNs. The harness controls the dedicated private cluster and schema.
Use pgJDBC 42.7.14 (artifact SHA-256
`73914527305a40cce504b0d3d90b23caf565136912d607ae8ae7c5895512332c`)
and synchronous Rust `postgres = "=0.19.14"` without optional features.
Integrity and transitive lockfile evidence are recorded with the validation evidence;
dependency availability is not proof of executed acceptance. Java compiles
with JDK 26 targeting release 21; Rust targets installed 1.96, edition 2024.

## Deterministic gates and bounded failures

Optional `ROO_GATE_POINT` and positive signed-bigint `ROO_GATE_LOCK` instrument
one named phase. `ROO_WORKER_ID` is an ASCII alphanumeric/underscore diagnostic
worker token (use a bounded token so application_name fits 63 bytes). The harness holds that advisory session lock on its own
connection before starting the worker. At the matching point the worker sets
application_name to `roo:<worker>:<point>`, then executes
`SELECT pg_advisory_lock(key)` on a dedicated gate connection, blocking until
the harness releases it, and unlocks after acquisition. The harness observes
pg_stat_activity/pg_locks and kills the worker or releases the gate; no sleeps
alone determine the race. Gates are diagnostic instrumentation, not domain
commands or persisted business state.

| Point | Durable state before blocking |
|---|---|
| inside_prepare | Order lock held in the uncommitted prepare/add transaction; useful for a competing writer witness |
| after_prepare | Intent transaction committed; provider call has not begun |
| after_effect | Provider transaction committed (or lookup/call completed); final app transaction has not begun |
| after_finalize | App terminal state and event committed; response not yet returned |
| after_delivery | Consumer inbox committed; outbox acknowledgement not committed; relay retains app row lock |

Apply a matching after_prepare gate only when an operation has a persisted
active intent, after_effect after provider observation including Unknown, and
after_finalize only after a real terminal commit. Gate settings are absent in
normal runs. Default application_name includes worker identity for lock witnesses.
Suggested connection limits are connect_timeout=5 seconds,
statement_timeout=10000ms and lock_timeout=5000ms, set for every connection.
Gates use a separately bounded 30000ms statement/lock wait so the harness has
time to observe and act. Gate timeout is a runner failure; it is not silently
treated as successful release.

Retry only a known-aborted short transaction on SQLSTATE 40001, 40P01 or 55P03,
at most three attempts, with a fresh transaction/connection and revalidation.
Do not blindly replay the complete multi-transaction command or external
effect. Connection loss around COMMIT is an unknown commit observation, not a
known rollback: exit nonzero, reopen fresh connections, inspect committed
intent/state, and reconcile or safely retry the same stable operation identity.
An add after an unknown commit must be inspected, never automatically repeated.
An uncertain provider commit is resolved by a same-key request or status lookup;
an uncertain inbox commit is resolved by deduplicated redelivery. Use consistent
app order -> outbox ordering, no provider -> app or inbox -> app lock nesting.

## Acceptance and proof limits

The test harness runs both languages against all original oracle rows and common
malformed input cases. Meaningful unit checks cover arithmetic/identity parsing,
unchanged rejected candidates and the same domain boundaries. Database checks
attempt invalid scalar/state rows and duplicate event/refund keys. Common
deterministically orchestrated process tests cover competing payment/refund
identities, same-key retries, add/pay row blocking, duplicate relays, lost local
finalization, and all four post-commit kill gates. A fresh process must reconcile
retained intent/provider state and deduplicate inbox delivery. A dedicated
PostgreSQL restart must preserve committed app/provider/inbox records, and all
clients reconnect; immediate shutdown additionally exercises startup WAL
recovery if the harness records it explicitly.

Only executed, recorded checks establish evidence. Process recovery, clean
database restart, server-crash recovery, physical power loss and production
readiness are distinct claims. The simulator shares one PostgreSQL instance
across independent schemas/connections; it is not an external payment network
or distributed transaction test. No hardware-cache, real-provider retention,
security, operational scale, or exhaustive-interleaving guarantee is implied.
