# PostgreSQL orders/payments validation

Date: 2026-10-11. Scope: the local PostgreSQL extension, with Java composition,
Java Template Method inheritance and Rust composition. The integrator executed
all builds/database operations serially against a newly created, marked,
synthetic loopback cluster.

## Executed result

**PASS.** The post-hardening qualification exited zero. See the
[complete check log](postgres-checks.log), [integration receipt](postgres-integration-evidence.json),
[environment and exact compiler diagnostics](postgres-environment.json), and
[original-case regression log](postgres-regression.log). Independent final
candidate acceptance is recorded separately in [the review](postgres-review.md).

```sh
bash case-studies/orders-payments/postgres/verify.sh
bash case-studies/orders-payments/verify.sh
```

The first command builds/tests Java and Rust, verifies the JDBC hash, fetches
locked Rust dependencies, installs the schema if absent, runs integration, and
stops the owned cluster even on qualification failure. Data is retained. The
second verifies the unchanged in-memory case and original ROO laboratory. RTK
is an integrator convenience, not a runtime prerequisite for the new scripts.

## Shared behavioral parity

Each column uses the same harness and independent expected observations.

| Check | Java composition | Java inheritance | Rust composition |
|---|---:|---:|---:|
| Original oracle scenarios; exact eleven-field rows | 42 | 42 | 42 |
| Malformed fixture rejection before SQL mutation | 10 | 10 | 10 |
| Persistent boundary guards | 3 | 3 | 3 |
| Concurrent schedules with database lock witnesses | 7 | 7 | 7 |
| SIGKILL and fresh-process recovery cases | 5 | 5 | 5 |
| Durable scopes preserved/recovered across server restart | 4 | 4 | 4 |

Persistent guards verify atomic all-scope fixture reservation on collision,
idempotent init without reset, and non-loopback configuration rejection before
mutation. Malformed fixtures are also checked for absence of new app scopes.

Concurrent schedules cover different payment IDs, same-payment key retries,
different refund IDs, add before pay, pay before add, duplicate relay workers,
and same-refund key retries. Gates are witnessed in pg_stat_activity as advisory
lock waits; contenders are witnessed as database lock waits. The successful
receipt contains 51 observations. Sleeps only bound polling: elapsed time alone
never establishes the schedule.

Process-crash cases kill the application with SIGKILL after intent commit,
payment-provider commit, terminal-state/outbox commit, independent inbox commit
before acknowledgement, and refund-provider commit. A fresh subprocess reads
retained state and reconciles the same intent, safely retries its stable
identity, or redelivers to the deduplicating inbox. Counts and stable IDs are
asserted at the gap and after recovery.

## Actual PostgreSQL crash restart

The harness prepares four durable scopes per variant: pending payment with a
committed provider result, refunding with a committed refund result, outbox
acknowledgement gap with committed inbox, and completed paid order with outbox.
It captures twelve full normalized snapshots, stops only the dedicated server
with pg_ctl -m immediate, restarts it, then compares snapshots from new app
processes before recovery.

The receipt records different pg_postmaster_start_time values, PostgreSQL
server_version_num=180006, and fsync, synchronous_commit and full_page_writes
all on. Its server-log excerpt shows interrupted database, automatic recovery,
WAL redo starts, WAL redo done, and readiness for connections. All twelve
snapshots matched, and all twelve recovery paths passed. This exercises actual
server crash recovery as well as application process recovery.

Five direct SQL probes also passed: invalid quantity, overflowing line product
and invalid state/intent shape reject with SQLSTATE 23514; duplicate stable
event identity and a second full refund under another ID reject with 23505.
Every probe uses an isolated scope and a transaction that rolls back.

## Language and compiler checks

- Java: release 21, all lint warnings denied, on OpenJDK 26.0.1. Fifty-two
  explicit pure assertions passed, plus compiler-negative checks for private
  aggregate mutation and overriding the final Template Method.
- Rust 1.96.0, edition 2024: six unit tests, two positive doctests and four
  compile-fail doctests passed. A rustc JSON verifier also required exactly
  E0382, E0499, E0597 and E0624 for the respective negative examples.
- Rust formatting, Clippy with warnings denied, binary build and documentation
  generation passed. The standalone crate pins postgres =0.19.14 and retains
  the dependency graph in Cargo.lock.
- pgJDBC 42.7.14 from the official distribution matched SHA-256
  73914527305a40cce504b0d3d90b23caf565136912d607ae8ae7c5895512332c.

After full qualification, only public command documentation and the Java build
wrapper changed: RTK calls were removed and the same fixed source directory is
compiled. Its targeted rebuild again passed all 52 assertions and both compiler
negatives; see [portability recheck](postgres-build-portability.log). No business
or database source changed after full integration.

## Review, corrections and baseline

The [independent security/transaction review](postgres-security.md) identified
four issues: ambient libpq environment could redirect utilities, barrier close
needed guaranteed kill/reap cleanup, Java application-name shape differed from
the lock-witness filter, and Rust needed atomic fixture reservation matching
Java. All were corrected and independently re-read before final qualification.

The additional [boundary receipt](postgres-boundary-evidence.json) records a
successful utility connection despite intentionally invalid ambient
PGHOSTADDR, PGSERVICE and PGOPTIONS, rejection of a mismatched server data
directory, and final stopped-cluster status. Managed utilities strip ambient
PG settings; no connection to the supplied non-loopback address was made.

The architect froze schema/protocol before consumers. Luna Max agents handled
primary research and English documentation; Sol 6.1 Medium handled contract,
implementations and independent review. Only root ran builds/database commands.
See [ownership and dispatch](postgres-run.md). Token/cost/quota telemetry is
unavailable; no efficiency claim is made.

The previous 43-file candidate remains historical at
799e7e4efa40c83325f920d3b40eddc95f770d208c863ef66ea5e5c8840b9c55.
Its current hashes differ only for intentionally updated root README.md and
.gitignore. Original guide, case and evidence remain preserved. Regression again
passed 280 Java assertions, 20 Rust unit tests, positive/negative examples,
42 oracle rows and ten malformed inputs per variant. The original laboratory
again passed its 17 tests/examples.

## Limits and final local state

App, provider simulator and consumer use separate commits/connections but share
one PostgreSQL server, filesystem and WAL durability domain. Loopback trust
authentication and a dedicated superuser test role do not establish production
security. SQL protects scalar/shape/uniqueness rules; trusted adapters enforce
domain history and cross-row invariants. Relay holds an app row lock over a
bounded local inbox transaction; this is not a production network relay policy.

Tests do not establish physical power-loss survival, external-provider
idempotency, exhaustive interleaving correctness, throughput, tenant isolation
or dependency-vulnerability status. Known-phase SIGKILL differs from transport
loss during COMMIT. Uncertain COMMIT and every retry SQLSTATE are documented
policies supported by source review, not separately injected runtime proofs.

No existing PostgreSQL service, real payment, credential store, Git publication
or deployment was used. The owned cluster is stopped and synthetic data retained
under the ignored .runtime directory.

## Note added 2026-10-13: boundary receipt scope

Added after the fact; the paragraph at line 107 is not rewritten. The retained [boundary receipt](postgres-boundary-evidence.json) contains three booleans, all `true`: `ambient_libpq_settings_ignored`, `mismatched_data_directory_rejected`, `owned_cluster_stopped`. It does not retain the values given to `PGHOSTADDR`, `PGSERVICE` or `PGOPTIONS`, the script that injected them (`git grep PGHOSTADDR` matches only this report and [postgres-security.md](postgres-security.md), which describes the finding), or any network observation. Consequently the sentence "no connection to the supplied non-loopback address was made" is **not recorded**: no packet capture, listener log or address survives. At most it follows from `ambient_libpq_settings_ignored: true`. Treat it as an unverified inference.
