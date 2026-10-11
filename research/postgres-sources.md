# PostgreSQL Java/Rust case: primary-source ledger

Checked 2026-10-11 for the isolated case in `research/postgres-run.md` and the
frozen PostgreSQL contract. The contract remains normative; this note records
database/driver facts, application consequences, and evidence limits. This
source review did not create or query a database.

## Versions and evidence boundary

- PostgreSQL 18's official documentation currently lists 18, 17, and 16 as
  supported majors ([PostgreSQL 18 `INSERT`](https://www.postgresql.org/docs/18/sql-insert.html)).
- Read-only Homebrew inventory showed 16.15, 17.11, and 18.6 installed;
  `pg_config` resolves to 18.6 `libpq`, which does not identify the server
  instance selected by the harness.
- Record the chosen `postgres --version`, SQL `SHOW server_version_num`, and
  effective durability settings. Linked database pages target PostgreSQL 18;
  check the selected major's manual before generalizing version details.
- “Documented” means stated by a linked primary source; “consequence” is an
  app requirement derived from it; “inference” is marked explicitly.

## Concurrency, snapshots, and idempotency

1. **Read Committed snapshots are per statement.** The default sees rows committed before each statement began; later statements in one transaction may see intervening commits. [Transaction isolation](https://www.postgresql.org/docs/18/transaction-iso.html).

   Consequence: after waiting for another writer, re-read and validate the current row; do not base a transition on an earlier snapshot.

2. **Row locks wait and re-evaluate.** `UPDATE`, `DELETE`, and locking `SELECT` wait on a concurrently changed target; at Read Committed the `WHERE` clause is re-evaluated on the updated row, and `SELECT FOR UPDATE` returns/locks it if it still matches. [Isolation](https://www.postgresql.org/docs/18/transaction-iso.html), [`SELECT`](https://www.postgresql.org/docs/18/sql-select.html).

   Consequence: add, pay, refund, and order transitions must serialize on the same order row (or an equivalent conditional write). The lock ends with the transaction; never hold it across a provider call.

3. **Unique constraints arbitrate concurrent identities.** `ON CONFLICT` uses a unique arbiter; `DO NOTHING` skips a conflict, while `DO UPDATE` atomically inserts or updates under concurrency. [INSERT / ON CONFLICT](https://www.postgresql.org/docs/18/sql-insert.html).

   Consequence: enforce uniqueness in PostgreSQL for provider identity, one order intent, refund-per-payment, outbox EventId, and inbox EventId. Application check-then-insert alone is race-prone.

4. **A losing `DO NOTHING` may conflict with a row invisible to its snapshot.** At Read Committed, a concurrent row can cause the insert to skip even though that row is not visible to the insert's statement snapshot. [Transaction isolation](https://www.postgresql.org/docs/18/transaction-iso.html).

   Consequence: read the winner in a new statement. Compare the full immutable request (operation, key, order, currency, amount, refund parent) before replaying; `DO NOTHING RETURNING` does not return the existing row. A unique key does not define payload equality.

5. **Deadlocks abort one transaction.** PostgreSQL recommends consistent lock acquisition order; it can abort any deadlock participant. `40001` means `serialization_failure`, `40P01` `deadlock_detected`; retrying deadlocks may be advisable. [Explicit locking](https://www.postgresql.org/docs/18/explicit-locking.html), [retry guidance](https://www.postgresql.org/docs/18/mvcc-serialization-failure-handling.html), [SQLSTATEs](https://www.postgresql.org/docs/18/errcodes-appendix.html).

   Consequence: retry a bounded whole local transaction using fresh reads and stable IDs, not only its last statement. Do not repeat provider effects. Treat `23505` separately; the selected contract also limits `55P03` retries to known-aborted short transactions.

6. **`SKIP LOCKED` is queue policy, not a consistency guarantee.** It skips locked rows and creates an inconsistent view; PostgreSQL documents it for queue-like consumers, while `NOWAIT` errors immediately. [`SELECT` locking clauses](https://www.postgresql.org/docs/18/sql-select.html).

   Consequence: it cannot prove a queue empty, preserve global order, or prevent duplicate delivery after crashes. Retain stable event IDs and idempotent consumer inserts. The frozen contract serializes relay work to keep fixture order deterministic.

## Advisory locks and concurrency witnesses

- Advisory locks name application-defined resources; PostgreSQL does not enforce that every writer takes the same lock. `pg_advisory_xact_lock` is exclusive and automatically releases at transaction end. [Advisory lock functions](https://www.postgresql.org/docs/18/functions-admin.html), [locking semantics](https://www.postgresql.org/docs/18/explicit-locking.html).
- Session-level advisory locks survive transaction rollback and last until explicit release or session end; use a separate gate session only when a harness lock intentionally spans transactions. [Advisory lock functions](https://www.postgresql.org/docs/18/functions-admin.html).
- Consequence: the provider scope lock is a convention all provider writers must follow, with unique indexes as a second defense. Hash collisions may serialize distinct scopes but cannot grant two holders of the same lock key simultaneously.
- Release app order-row locks before provider calls; provider transactions never acquire app locks. The simulator relay deliberately retains its order lock across a bounded local independent inbox transaction, whose consumer never acquires app/provider locks. This explicit exception preserves the lock order; it is not a policy for production network delivery.
- `pg_stat_activity` reports one row per server process, including `application_name`, state, and wait event; `pg_locks` exposes outstanding locks. These are suitable witnesses for harness barriers. [Activity view](https://www.postgresql.org/docs/18/monitoring-stats.html), [lock view](https://www.postgresql.org/docs/18/monitoring-locks.html).
- Observation is a snapshot and may show transient discrepancies; use a positive lock/wait witness plus controlled release/termination, not a sleep or a single absent row, to establish an interleaving.

## Transaction boundaries and uncertain outcomes

7. **A transaction protects only PostgreSQL writes in that transaction.** `COMMIT` makes them visible and documents them as durable if a crash occurs. [`COMMIT`](https://www.postgresql.org/docs/18/sql-commit.html).

   Consequence: finalize local order state and its outbox fact together. Commit the provider simulator record/effect independently before returning the terminal result; PostgreSQL does not make an external effect atomic with local state.

8. **A lost COMMIT reply is an uncertain observation.** The frontend/backend protocol returns command responses and `ReadyForQuery` after processing. [Message flow](https://www.postgresql.org/docs/18/protocol-flow.html) and [message formats](https://www.postgresql.org/docs/18/protocol-message-formats.html).

   Inference: loss of connection while awaiting the response cannot show whether the backend committed before the reply was lost. Do not report definite rollback or repeat an external effect; reconnect and inspect stable identities, then reconcile or retry that same identity.

9. **Prepare/provider/finalize is the app protocol.** Commit `Pending` and immutable intent before provider call; commit terminal order state and one outbox fact afterward. Refund similarly persists `Refunding` first. Release the order lock before provider work.

   Evidence limit: a separately committed provider table demonstrates independent database transactions and chosen failure windows; it does not model networks, provider key expiry/consistency, or settlement. NotFound is authoritative only inside the complete simulator.

## Process restart, server restart, durability

10. **Immediate shutdown takes PostgreSQL's crash-recovery path.** It skips normal shutdown work and startup replays WAL; it is documented for emergencies. [Server shutdown](https://www.postgresql.org/docs/18/server-shutdown.html).

    Test distinction: restart only the application process to test loss of app memory; immediate PostgreSQL shutdown/restart exercises startup recovery. A graceful stop is not a crash test. Record stop mode, startup completion, and app/provider/inbox rows afterward.

11. **Durability settings bound commit acknowledgement.** `synchronous_commit=on` (default) waits at least for local WAL flush; with synchronous standbys configured, the setting also controls remote wait behavior. `off` can lose recent acknowledgements after server crash without database corruption. `fsync=off` risks corruption; `full_page_writes` logs full pages after checkpoints to repair partial writes. [WAL configuration](https://www.postgresql.org/docs/18/runtime-config-wal.html), [non-durable settings](https://www.postgresql.org/docs/18/non-durability.html).

    For committed-row survival, record/expect `fsync=on`, `synchronous_commit=on`, and `full_page_writes=on`; verify effective values in the isolated cluster.
    Also record `synchronous_standby_names` so a replica wait policy is not mistaken for local-only acknowledgement.

12. **Flush correctness depends on the storage stack.** PostgreSQL discusses volatile OS/controller/drive caches and assigns administrators responsibility for making storage honor flushes. [WAL reliability](https://www.postgresql.org/docs/18/wal-reliability.html).

    Evidence limit: immediate restart demonstrates recovery on this host/configuration. It is not a power-cut test or proof of physical flushes/hardware durability. A simulator table in the same cluster recovers through the same WAL and is not evidence about a real provider's storage.

13. **App process death, backend termination, and server crash differ.** A fresh JVM/Rust process with PostgreSQL still up tests app-memory loss. `pg_terminate_backend` or killing one child backend is not immediate server stop; stopping the whole server tests WAL recovery. None tests power loss.

## Java JDBC 21 and pgJDBC

14. **Java SE 21 connections default to auto-commit.** Each statement then commits individually; with auto-commit off, explicit `commit()`/`rollback()` ends a grouped transaction. Changing auto-commit during a transaction commits it. [Java SE 21 `Connection`](https://docs.oracle.com/en/java/javase/21/docs/api/java.sql/java/sql/Connection.html).

    Consequence: disable auto-commit explicitly for each multi-statement unit. These API rules apply when compiling with `--release 21` on the installed JDK.

15. **Pin the released driver artifact.** pgJDBC lists 42.7.14 as current in its Java 8+ line; Java 21 meets the minimum. The 2026-10-07 release fixes CVE-2026-107314 and CVE-2026-107315, including prior declared-length binary padding behavior. [Downloads](https://jdbc.postgresql.org/download/), [docs](https://jdbc.postgresql.org/documentation/), [release notes](https://jdbc.postgresql.org/changelogs/2026-10-07-42.7.14-release/).

16. **JDBC artifact integrity.** SHA-256 computed from JAR streams at the official pgJDBC site and Maven Central matched:

    `postgresql-42.7.14.jar` — `73914527305a40cce504b0d3d90b23caf565136912d607ae8ae7c5895512332c`

    [Official JAR](https://jdbc.postgresql.org/download/postgresql-42.7.14.jar), [Maven Central JAR](https://repo.maven.apache.org/maven2/org/postgresql/postgresql/42.7.14/postgresql-42.7.14.jar). Recompute the hash of the artifact actually used; version alone is not integrity evidence.

17. **Use SQLSTATE for known server failures.** `SQLException.getSQLState()` exposes the code; pgJDBC `PSQLException` extends it. This supports code-based abort handling but cannot resolve a lost COMMIT reply. [Java SE 21 `SQLException`](https://docs.oracle.com/en/java/javase/21/docs/api/java.sql/java/sql/SQLException.html), [pgJDBC `PSQLException`](https://jdbc.postgresql.org/documentation/publicapi/org/postgresql/util/PSQLException.html).

## Synchronous Rust `postgres` crate

18. **Use the project's synchronous client.** The official manifest describes `postgres` as a native synchronous client; pin `postgres = "=0.19.14"` and retain its `Cargo.lock`. [Manifest](https://github.com/sfackler/rust-postgres/blob/master/postgres/Cargo.toml), [versioned docs](https://docs.rs/postgres/0.19.14/postgres/).

    0.19.14 is not yanked, requires Rust 1.85, and its registry checksum is `33ad20e0aa0b24f5a394eab4f78c781d248982b22b25cecc7e3aa46a681605bd`; SHA-256 of the official crate archive matched the index. [Archive](https://static.crates.io/crates/postgres/postgres-0.19.14.crate), [index](https://index.crates.io/po/st/postgres).

19. **Transactions use a scoped mutable borrow.** `Client::transaction(&mut self)` returns `Result<Transaction<'_>, Error>`; unfinished transactions roll back on drop, and `commit(self)` explicitly commits. [Versioned `Client`](https://docs.rs/postgres/0.19.14/postgres/struct.Client.html), [`Transaction`](https://docs.rs/postgres/0.19.14/postgres/struct.Transaction.html).

    Rust ownership controls use through this client; it does not replace SQL constraints, locks, WAL durability, or provider idempotency. `Error::code()` returns optional SQLSTATE; transport failures may lack a server code. [Rust `Error`](https://docs.rs/postgres/0.19.14/postgres/error/struct.Error.html), [SQLSTATEs](https://www.postgresql.org/docs/18/errcodes-appendix.html).

## Evidence interpretation

- Use barriers, separate connections, and bounded waits for retries, competing identities, add/pay races, and duplicate relay workers; sleeps alone do not prove an interleaving.
- Record lock ownership, SQLSTATEs, and fresh-session observations. Verify order, intent, provider record, outbox, and inbox separately after each interruption.
- A multi-query Read Committed snapshot can combine different committed moments; collect a fixture snapshot in one SQL statement or a read-only Repeatable Read transaction. [Transaction isolation](https://www.postgresql.org/docs/18/transaction-iso.html).
- Test before-commit rollback and after-commit acknowledgement loss only when the harness can stop at those points deterministically; otherwise describe the narrower failure window.
- After server recovery, reconnect with a fresh client before checking durable rows; a stale pre-crash client cannot establish successful reconnection or reloaded state.
- These sources establish database and client API behavior, not production readiness, real-provider behavior, power-loss durability, exhaustive interleaving coverage, PCI controls, or performance.
