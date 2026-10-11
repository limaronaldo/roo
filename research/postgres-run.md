# PostgreSQL case evolution: execution record

Date: 2026-10-11. User scope: evolve the orders/payments ROO study to local PostgreSQL, concurrency and recovery after restart, preserving Java/Rust test parity and English documentation.

## Authority and baseline

Local database creation, SQL execution against isolated synthetic fixtures, application subprocesses, controlled worker interruption and dedicated test-server restart are within this explicit request. Do not access existing databases, production services, credentials or real payments. Preserve historical candidate manifests, source guide and prior checks. No Git repository is present; no commit/publication/deployment requested.

Use a new implementation under `case-studies/orders-payments/postgres/`, retaining the existing in-memory case as a reference and regression suite. Integrator exact model/effort is not exposed, so supervision remains active: consult the Sol architect before freezing new interfaces. Skill: user-invoked Hermes parallel-model-orchestration 1.7.22; native delegation with established Luna Max / Sol 6.1 Medium allocation, nine active slots maximum including integrator. No recursive delegates or external-agent CLIs. Serialize builds and database qualification under integrator ownership. Model/provider tokens, cache, cost and quota telemetry unavailable.

## Queue and ownership

| ID | Requested model/effort | Exclusive ownership | Dependency | State |
|---|---|---|---|---|
| A | Sol 6.1 / medium, database-reviewer | PostgreSQL contract and schema; postgres/SPEC.md and postgres/schema.sql | Current user scope and in-memory SPEC | accepted; pg_contract |
| S | Luna / max | Primary evidence; research/postgres-sources.md | User scope | complete; pg_sources |
| J | Sol 6.1 / medium | postgres/java/ | Accepted A | implemented; pg_java |
| R | Sol 6.1 / medium | postgres/rust/ | Accepted A | implemented; pg_rust |
| D | Luna / max | postgres/README.md | Accepted A and actual implementation reconciliation | finalized receipts; pg_documentation |
| S2 | Sol 6.1 / medium, security-reviewer | research/postgres-security.md; other paths read-only | Source and harness | complete; pg_security; four findings corrected |
| V | Sol 6.1 / medium | Independent read-only review; integrator transcribes result | Frozen implementation and executed evidence | ACCEPT; pg_review |
| I | Integrator | Private cluster lifecycle, shared oracle/concurrency/restart harness, build integration, navigation and evidence | A before consumers | complete |

## Acceptance intent

- Real PostgreSQL transactions, constraints and row-level concurrency control, with separately committed durable provider simulation and consumer inbox/outbox state.
- Both Java and Rust retain matching business semantics on all original 42 expected scenarios; preserve Java inheritance/composition comparison where feasible and explicit.
- Shared adversarial tests exercise competing payment identities, same-key concurrent retries, add/pay serialization, duplicate relay workers, unknown/reconciliation, interrupted process gaps, and recovery from a fresh process. Include actual dedicated PostgreSQL restart with committed-data survival, distinguished from process restart and physical hardware durability.
- Every check uses isolated synthetic scope, deterministic orchestration/barriers rather than arbitrary timing, bounded waits and exact expected observations. Negative malformed input and database constraints remain meaningful.
- Reproducible local setup/verification, dependency versions/integrity, English architecture/ROO/failure documentation, preserved prior evidence and independent final review. External provider behavior, hardware failure and production readiness remain outside evidence.

## Dispatch and evidence

Architecture/scenario interfaces must be accepted before language implementations. Integrator owns database/test operations; delegates write only assigned paths and propose commands.

The architect's READ COMMITTED/order-row-lock protocol and independent provider/inbox transactions were accepted before consumers were dispatched. Dependencies were verified against primary sources: pgJDBC 42.7.14 (SHA-256 pinned in fetch_jdbc.py) and synchronous Rust postgres 0.19.14 (exact version plus Cargo.lock). Root fetched dependencies and ran all compiler/database checks serially.

The first integration qualification passed 42 oracle rows, 10 malformed fixtures, 7 concurrent schedules and 5 SIGKILL recoveries per variant; 12 snapshots survived one immediate PostgreSQL shutdown/restart, and 5 database constraints rejected invalid writes. An initial harness-only failure was corrected: Java's normal application name has no suffix, so lock witnesses now accept exact name or a suffixed name. No domain workaround was required.

Independent source review then prompted libpq environment sanitization, same-connection data-directory guards, guaranteed barrier-process reaping and atomic all-scope fixture reservation in Rust. Three shared persistent boundary checks were added for atomic reservation, idempotent init and non-loopback configuration rejection. These corrections require a final full serialized qualification before acceptance. Historical manifests/logs remain unchanged.

Final qualification exited zero: 42 oracle rows, 10 malformed inputs, 3 persistent guards, 7 concurrent schedules, 5 SIGKILL recoveries and 4 restart scopes per variant, plus 5 SQL constraint probes. Fifty-one database lock witnesses and WAL redo are retained in the JSON receipt. Java passed 52 pure checks and two compiler negatives; Rust passed six units, two positive doctests, four exact compiler-negative codes, formatting, Clippy, build and docs. The unchanged original regression suite also passed. After removing RTK calls from the public Java build wrapper, its focused rebuild passed again. Additional libpq environment/endpoint guard checks passed. The owned cluster is stopped with synthetic data retained. Final candidate review is the remaining acceptance gate, not further runtime work.

Frozen initial candidate: a3b25017dcfe58184956a16df7130af346a661e61291824f5d174d84bde77a38, 119 files. Its manifest covers current source, documentation, retained baseline and executed receipts, excluding build/cache/private runtime, JDBC binary, its own manifests, this live ledger and final review status. An independent native Sol 6.1 Medium reviewer was dispatched against that exact identity. Initial/final manifests are preserved separately; any requested correction requires a new hash and focused revalidation.

Initial review confirmed every hash, 201 relative Markdown targets, baseline preservation and all recorded execution counts. It requested one Low source-ledger wording correction: the simulator's bounded local consumer transaction deliberately runs while the app order lock is held, unlike provider calls. Root corrected that sentence, replaced the README's pending-review wording with a link to the separate review receipt, and preserved the initial review. These are documentation-only changes; no runtime recheck is warranted. A new manifest and focused independent re-review will bind the final acceptance.

Final focused independent result: ACCEPT, no remaining findings. Candidate d1594cd230a03bcad6edbb2b590cbcb3bbcbc5f94604cdc4fbb0af59596bd7ac has 120 files; every hash/size matched before and after review. Exact scope is two text corrections and one added initial-review receipt, with implementation/runtime evidence unchanged. All 202 manifested relative Markdown targets resolve. Final review is retained in postgres-review.md. Owned PostgreSQL status is stopped, synthetic data retained; no existing service or external action was used. All authorized work is complete.
