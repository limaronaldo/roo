# HTTP case-study independent final review

**ACCEPT — bounded local HTTP case-study acceptance.**

Candidate: `7111a514cad56aafbd02107d4b7a00c92649f986b799a46c7a051a68fed75af7`, dated 2026-10-11.

This report preserves the terminal assessment returned by the independent
`http_final_review` delegate. Root saved it after the read-only review; the
reviewer did not write or modify the candidate.

I independently recomputed the manifest identity and checked every listed file’s size and SHA-256: **154/154 match**, including a second verification after inspection. Against PostgreSQL candidate `d1594cd230a03bcad6edbb2b590cbcb3bbcbc5f94604cdc4fbb0af59596bd7ac`, **118/120 files remain byte-identical**. Only root `README.md` and `.gitignore` differ, as expressly permitted.

This is a manifest-based acceptance under the task-and-review contract. It is not a Git comparison or a claim that the full `code-review-rm` engine was completed.

The implementation satisfies the accepted user/SPEC scope:

- Java composition and final Template Method have independently selectable HTTP entrypoints. `HttpService.java:45–49,88–101` directly reuse the existing adapters/coordinators. Rust’s path dependency and `main.rs:119–153` directly invoke the accepted `Database` interfaces. No per-request runner, duplicated payment orchestration, schema migration, or additional receipt table was introduced.
- Both transport boundaries enforce bounded string-valued JSON, strict UTF-8, duplicate-field rejection, bounded identifiers/numeric text, narrow synthetic controls, and matching operation-key aliases before database execution. Relevant implementations are `HttpProtocol.java:26–155` and Rust `lib.rs:80–315`.
- Database admission is limited to sixteen operations. Java has a bounded executor and semaphore (`HttpService.java:52–54`); Rust moves its acquired permit into blocking work (`main.rs:104–112`). Neither introduces a global application mutex or shared live database client.
- Fixed public error responses preserve infrastructure uncertainty without fabricating a domain result. Payment/refund recovery retains natural operation identities; line POST remains explicitly non-idempotent. The English SPEC, tutorial, and language guides consistently explain these boundaries.

I inspected the new implementation, protocol tests, dependency configuration/lockfile, lifecycle scripts, complete shared HTTP harness, regression redirection, English documentation, and HTTP research evidence. The unchanged PostgreSQL baseline was verified by hashes, with supporting configuration, transaction, missing-scope, and snapshot paths inspected where needed; this was not a fresh exhaustive audit of all unchanged baseline sources.

The retained root-executed evidence reconciles with the actual harness:

| Recorded check | Result |
|---|---|
| Three variants, each | 42 oracle rows, 41 rejection cases, 2 negotiation cases, 8 ordinary-mode cases, 4 startup rejections |
| Admission, each | 16 simultaneous PostgreSQL wait witnesses; seventeenth request receives `503 Busy`; capacity recovers |
| Graceful termination, each | Listener closes with admitted request active; request completes after gate release; no forced termination |
| Concurrency/recovery, each | 7 competing schedules, 8 SIGKILL recovery schedules, 4 database restart scopes |
| Combined database restart | 12 snapshots preserved; the same 3 HTTP PIDs return generic 503 during downtime and reconnect afterward |
| Compiler/protocol checks | Java 72 checks; Rust 5 tests plus formatting, Clippy, build, and documentation |
| Historical regression | Exit zero; new PostgreSQL regression receipt preserves historical evidence |

The integration receipt contains 63 race/crash/drain lock witnesses; admission records another 48 simultaneous waits. Its WAL log records interrupted startup and redo, with durability settings enabled. `http-environment.json` records both qualification exits as zero. `regression.py:9–20` redirects only the old verifier’s evidence destination, and the baseline hash check confirms historical receipts remain unchanged.

The initial security findings are resolved in the reviewed candidate: raw-route/missing-scope validation and charset whitespace now agree, the shared rejection/negotiation cases exercise those corrections, and `support.py:146–156` checks the actual response scope before oracle relabeling. The active-drain and admission schedules substantiate their specifically recorded claims.

**Findings:** no blocking defect, required-scope omission, or unresolved actionable finding identified. No optional improvement is promoted to an acceptance requirement.

**Evidence limits:** I performed read-only source, manifest, and receipt inspection; I did not independently execute builds, tests, HTTP, SQL, network access, cluster operations, or Git, and wrote no files. Acceptance relies on root-retained execution evidence reconciled against the frozen sources. It covers the documented local educational simulator, not authentication, real payment networks, native malformed-framing parity, slow-client protection, exhaustive interleavings, worst-case combined shutdown duration, hardware power loss, dependency advisory clearance, or production readiness. The pending final review artifact is expected and does not invalidate this candidate.
