# PostgreSQL security and transaction review

Date: 2026-10-11. Independent static review of the synthetic PostgreSQL case study. No builds, tests, database connections, network calls, dependency audit, or process termination were performed in this review lane. Runtime evidence belongs to the integration lane.

## Disposition after source re-review

All four findings below were corrected during integration and the corrections were independently re-read in this lane. No unresolved High/Critical issue was identified within the reviewed synthetic scope. This is source-review acceptance, not independent runtime acceptance.

| Finding | Source correction inspected | Disposition |
|---|---|---|
| S1 | `cluster.py:21-30` strips ambient `PG*` variables and sets controlled password/service files and connection timeout. `cluster.py:103-117`, `:154-156` guard the connected server's data directory before utility SQL/schema; `verify.py:121-124` and its constraint subprocess use the same environment/guard. | Addressed in source. `createdb` uses a separate connection after the guarded read; safety assumes no hostile local endpoint replacement between those operations. |
| S2 | `verify.py:148-157` uses a `finally` fallback to kill and reap a controller that survives graceful close. | Addressed in source. Fault-path timeout behavior was not executed by this lane. |
| C1 | `verify.py:166-172` accepts the exact normal Java name or its colon-delimited phase suffix. | Addressed in source. |
| C2 | `rust/src/database.rs:166-185` reserves all fixture scopes in one transaction, with a common insertion order and rollback on conflict; `rust/src/main.rs:27-30` reserves before actions. | Addressed in source. |

The following original findings preserve the explanation and initial source locations. Line references in these historical descriptions and the transaction notes refer to the source first inspected; added remediation code shifts later lines.

## Original findings and rationale

### S1 — High: inherited libpq destination can escape the dedicated cluster

`case-studies/orders-payments/postgres/cluster.py:21-24` launches managed utilities without an explicit environment. Its SQL helper (`:95-101`), database creation (`:116-119`), and schema application (`:138-140`) pass `-h 127.0.0.1`, but inherit libpq settings such as `PGHOSTADDR`. A non-loopback `PGHOSTADDR` supplies the actual network destination even with an explicit host name. Ambient service/password settings can also change connection behavior. `verify.py:121-122` and `:384` similarly inherit the environment for direct psql invocations. The Java and Rust adapters construct their own explicit connection configurations and are outside this libpq-specific finding.

Consequence: a developer shell configured for another PostgreSQL server can cause schema installation or probe writes outside the owned synthetic cluster, violating the stated scope. A matching accessible database/role/port is a precondition; no external connection was attempted here.

Remediation: provide a shared sanitized environment to every PostgreSQL utility subprocess, removing ambient `PG*` connection/control settings and retaining only deliberately selected values. Set explicit bounded libpq timeouts and prohibit password prompting. Bind the SQL endpoint to the owned data directory with a read-only server identity check before schema installation, verification probes, or database creation. A marker file and `pg_ctl status` alone identify a filesystem/process target, not the psql endpoint (`cluster.py:45-54`, `:104-108`). Validate configured port and paths before use. Do not treat these checks as protection from a hostile same-user process capable of rewriting the checkout.

### S2 — Medium: barrier cleanup can leave its controller alive

`case-studies/orders-payments/postgres/verify.py:147-151` writes an unlock command and calls `communicate(timeout=10)` without a kill-and-reap fallback. `Popen.communicate` timeout does not terminate the child. Broken pipe or timeout during close can therefore leave the psql controller process/session alive and retain a diagnostic advisory lock. Worker processes have explicit `finally` cleanup (`:213-216`, `:257-259`); the controller needs equivalent treatment.

Remediation: make close idempotent, attempt graceful release, then kill and reap the controller in a bounded `finally` fallback; close streams and preserve the original test failure. This is local harness reliability, not an exposed application denial-of-service finding.

### C1 — Medium: Java contender lock witnesses use a different name shape

`case-studies/orders-payments/postgres/java/src/roo/postgres/Database.java:34` sets the normal application name to `roo:<worker>`. `verify.py:159-164` looks for `roo:<worker>:%` when witnessing an ordinary competing row-lock waiter. The Java contender cannot match that pattern, while Rust sets `roo:<worker>:rust` (`rust/src/database.rs:96`). This blocks valid Java concurrency acceptance without identifying a transaction defect.

Remediation: align the normal Java application name with the witness format or match the exact name plus its explicit phase variants. Retain the lock-state witness; do not replace it with elapsed sleeps.

### C2 — Low: fixture scope reservation differs between languages

Rust preflights scopes in independent SELECT statements (`rust/src/database.rs:166-175`) and then creates and executes scenarios individually (`rust/src/main.rs:27-35`). Two callers using the same fixture prefix can both pass preflight; one can commit earlier scenarios before rejecting a later scope created by its competitor. Java reserves all scopes in one transaction (`java/src/roo/postgres/Store.java:31-37`, `Runner.java:50-52`). The integrator generates fresh unique prefixes, so normal harness execution avoids this race.

Remediation: reserve the entire Rust scope set atomically with plain INSERT statements in a single short transaction before executing actions, matching Java. Existing scopes must remain unchanged; no reset or delete is appropriate. This is parity and partial-run behavior, not a tenant authorization issue.

## Transaction properties supported by source

- Business SQL values are bound parameters in Java prepared statements and Rust `$n` queries. Java's dynamic event-table identifier is checked against two closed constants (`Store.java:98-105`). Python probe SQL interpolates internally generated scopes/worker tokens and static test data, rather than runner action input (`verify.py:27-30`, `:83-90`, `:157-164`, `:373-384`).
- App writes serialize on the order row (`Store.java:14-16`, `rust/src/database.rs:197-198`). Intent commits precede provider calls; final state and outbox insertion share a subsequent transaction (`Store.java:62-96`, `rust/src/database.rs:343-465`). Provider transactions and inbox transactions use separate connections, with no app-table foreign keys (`schema.sql:50-70`). Shared PostgreSQL infrastructure is still a common failure domain.
- Provider requests compare retained order, currency, amount, parent payment and operation identity (`Provider.java:14-47`, `rust/src/database.rs:264-300`, `:467-484`). A scope advisory transaction lock serializes provider writes; approved-parent checks and the unique refund index guard one full refund (`schema.sql:65-67`). A terminal provider record is the simulated effect; this proves no real gateway behavior.
- Inbox/outbox duplicate insertion is followed by a separate SELECT and a complete fingerprint comparison (`Store.java:98-110`, `rust/src/database.rs:504-510`, `:547-553`). This correctly avoids depending on a losing READ COMMITTED INSERT statement's snapshot to expose its winner.
- Java retries SQLSTATE 40001/40P01/55P03 at most three attempts on fresh connections (`Database.java:44-60`). It does not retry generic connection-loss errors. Rust retries only matching transaction-body errors and lets every COMMIT error escape (`rust/src/database.rs:122-150`). Neither adapter blindly repeats an entire multi-transaction command after uncertain COMMIT. Java's allowlist also covers explicit known-abort COMMIT errors; Rust is more conservative there. Stable-key provider retry, reconcile, and deduplicated relay are valid recovery paths; an uncertain add must be inspected before repetition (`SPEC.md:181-190`).
- Snapshots use one SELECT with scalar subqueries in both languages (`Store.java:146-164`, `rust/src/database.rs:177-193`). The snapshot may include another worker's later commit, as documented; it need not describe the action's own exact decision instant.
- Runner diagnostics suppress driver connection strings and parameter values (`Runner.java:65-71`, `rust/src/database.rs:19-29`, `rust/src/main.rs:67-75`). JDBC fetch uses a fixed HTTPS URL, a bounded read and pinned SHA-256 before writing its artifact (`fetch_jdbc.py:8-25`). No credential literals were observed in the reviewed files; this is not a repository-wide secret scan or current vulnerability-database audit.

## Deliberate proof boundaries

Loopback trust authentication, a PostgreSQL superuser test role, shared schemas, and lack of RLS are deliberate educational constraints (`cluster.py:69-81`, `SPEC.md:35-39`). They are not evidence of least-privilege deployment or isolation against other local users. Domain history and cross-row invariants depend on trusted adapters; direct SQL writers can bypass those rules. Java's order reconstruction trusts the persisted total, while Rust additionally verifies the retained line sum (`Store.java:14-21`, `rust/src/database.rs:206-215`); the shared specification explicitly excludes arbitrary SQL-writer integrity guarantees.

The serialized relay intentionally holds its app row lock across a small local independent inbox transaction (`Store.java:120-141`, `rust/src/database.rs:486-510`). That ordering is coherent for the simulator because inbox processing does not acquire app/provider locks. It does not justify holding a database lock over production network delivery.

Static inspection cannot certify runtime concurrency, crash recovery, timeout cleanup, dependency safety, or the cluster's current identity. SIGKILL after a known committed phase, immediate PostgreSQL restart with WAL evidence, physical power loss, transport loss during COMMIT, and an external payment provider are separate proof claims. In particular, the harness's post-commit kill gates do not inject the ambiguous transport-loss-at-COMMIT case.
