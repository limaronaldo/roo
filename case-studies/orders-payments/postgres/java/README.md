# Java PostgreSQL orders and payments

ROO — Relationship & Ownership Oriented design is a language-independent
method for deciding each relationship before selecting Java, JDBC, or database
mechanisms.

Start with provider success followed by failed local finalization: the committed
intent and its PaymentId must remain available for recovery, while terminal
order state and its event commit together. The [frozen PostgreSQL contract](../SPEC.md)
and [original case](../../README.md) define those invariants. Chapter 2's
[Relationship Contract](../../../../docs/02-relationship-design.md#21-the-seven-field-relationship-contract)
and [worksheet](../../../../templates/relationship-contract.md) help separate
resource custody, domain responsibility, durable operation identity, mutation
authority, access duration, execution, and failure before choosing Java, JDBC,
and SQL mechanisms. IDs identify records, not authorized callers; this local
case models no caller authentication or authorization.

Two runners implement the frozen [persistent contract](../SPEC.md). Domain
identities and immutable request/event facts live in `Domain.java`; pure
transition decisions and checked minor-unit arithmetic stay in Java. The JDBC
store and provider persist those decisions. SQL performs scalar constraints,
row/advisory locking, uniqueness, and atomic writes, with no stored procedures.

`CompositionRunner` injects concrete adapters into a coordinator.
`TemplateRunner` supplies the same adapters through narrow protected hooks;
`TemplateApplication.execute` is final and owns the complete phase ordering.
Both coordinators use the same typed domain and persistence implementation.
The hooks are trusted capabilities, not a defense against malicious subclasses.

## Build and use

The integrator installs the dedicated local cluster/schema and fetches the
pinned pgJDBC 42.7.14 jar at `../.deps/postgresql-42.7.14.jar`. Its SHA-256 is
`73914527305a40cce504b0d3d90b23caf565136912d607ae8ae7c5895512332c`.
Use JDK 21 or newer; validation used JDK 26. Compilation targets Java 21 and treats all compiler warnings as errors.
No Maven, database download, schema initialization, or reset is performed here.
From this directory:

```sh
bash build.sh
export ROO_PG_HOST=127.0.0.1
export ROO_PG_PORT=55432 # use the dedicated harness port
export ROO_PG_DATABASE=roo_test
export ROO_PG_USER=roo_test
java -cp 'build/classes:../.deps/postgresql-42.7.14.jar' roo.postgres.CompositionRunner init example
java -cp 'build/classes:../.deps/postgresql-42.7.14.jar' roo.postgres.CompositionRunner step example add:100:2
java -cp 'build/classes:../.deps/postgresql-42.7.14.jar' roo.postgres.CompositionRunner step example pay:p1:approve:none
java -cp 'build/classes:../.deps/postgresql-42.7.14.jar' roo.postgres.CompositionRunner snapshot example
export ROO_RUN_ID=fresh_unique_run
java -cp 'build/classes:../.deps/postgresql-42.7.14.jar' roo.postgres.CompositionRunner fixtures ../../scenarios.tsv
```

Replace the entrypoint with `roo.postgres.TemplateRunner` for inheritance.
Each fixture invocation needs a fresh run prefix; existing scopes reject the
whole initialization transaction. `init` is idempotent and never resets data.
All successful output is eleven-field TSV; failures emit only bounded stderr.
Only explicit loopback host, bounded port, `roo_test` database and user are
accepted. Arbitrary URLs and `DATABASE_URL` are not consumed.

The build runs pure tests without Java's optional `-ea` assertions, then checks
compiler rejection of private aggregate mutation and final-algorithm override.
These checks do not establish database durability or concurrency. Executed
integration evidence belongs to the common harness and its recorded results.

## Transactions and recovery

Prepare/add/finalize transactions lock and reload the order at READ COMMITTED.
Intent commit precedes an independently connected provider transaction; no app
lock survives over the provider phase. Provider idempotency compares the entire
retained fingerprint under a scope advisory lock, and verifies the approved
full-amount parent and one-refund rule. Finalization reloads/revalidates under
the order lock and atomically inserts a deterministic immutable outbox fact.
Concurrent finalizers return terminal no-ops and cannot regress refund state.

Relay locks the order while a separate inbox transaction commits the full copied
fact, then acknowledges one event. Duplicate inbox insertions compare the winner
in a new statement snapshot. Acknowledgement failure explicitly rolls back the
acknowledgement writes; already committed inbox entries survive. Snapshot uses
one SELECT for state and all count aggregates.

Prepare/final-commit injections roll back after performing their local writes.
Only known-aborted short transactions with SQLSTATE 40001, 40P01, or 55P03 retry,
at most three attempts on fresh connections. No whole command or unknown COMMIT
is blindly repeated. On connection loss, inspect a new snapshot and reconcile
retained intent/provider state, or retry the same stable operation identity.
Inspect an uncertain add before deciding whether to add again.

Optional `ROO_GATE_POINT`, positive `ROO_GATE_LOCK`, and bounded `ROO_WORKER_ID`
follow the shared gate protocol. A separate connection waits at most 30 seconds,
with `application_name=roo:<worker>:<point>`. Supported points are
`inside_prepare`, `after_prepare`, `after_effect`, `after_finalize`, and
`after_delivery`; only the appropriate active/committed phase triggers a gate.
The normal connection bounds are 5 seconds to connect, 10 seconds per statement,
and 5 seconds for locks. Killed processes/restarts require fresh processes and
connections; no cached mutable state is presented as committed.

This is a trusted local simulator on one PostgreSQL instance, not an external
payment service, production authorization boundary, or exhaustive concurrency
proof. Process recovery, database restart, server-crash WAL recovery, physical
power loss, and production readiness remain separate evidence claims.
