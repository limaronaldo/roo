# PostgreSQL candidate review

**ACCEPT. No remaining findings.** Independent native Sol 6.1 Medium reviewer:
pg_review. Date: 2026-10-11.

Accepted local candidate:
d1594cd230a03bcad6edbb2b590cbcb3bbcbc5f94604cdc4fbb0af59596bd7ac.
See [the final manifest](postgres-candidate.json), [initial manifest](postgres-candidate-initial.json),
[preserved initial review](postgres-review-initial.md), and [executed validation](postgres-validation.md).
This review receipt and the live run ledger are excluded from candidate identity.

## Independent verification

Before and after focused review, all 120 file SHA-256 hashes and byte sizes
matched. Canonical manifest identity recomputed correctly. Initial-to-final
scope is exactly two changed documents and one added historical review, with
no removals. Reversing the declared text substitutions reproduced the initial
documents' hashes and sizes; no additional changes were hidden in those files.
All 202 relative Markdown file targets across manifested documents resolve.

The source ledger now correctly distinguishes release of app locks before
provider calls from the simulator's bounded local inbox exception, and forbids
inverse locking. The initial Low finding is resolved. The PostgreSQL README
links this separate acceptance receipt. The preserved initial review accurately
records prior findings, coverage, evidence and limits.

Implementation, schema, shared harness and runtime receipts are unchanged from
the initial review, so its substantive coverage remains applicable. That review
covered transactions, stable request fingerprints, row locks, typed ownership,
legitimate final Template Method inheritance, atomic terminal/outbox writes,
independent provider/inbox commits, deduplicated delivery, fresh-process recovery,
actual PostgreSQL immediate restart, oracle parity, meaningful compiler-negative
diagnostics, source documentation and historical baseline preservation.

Recorded results reconcile across all three variants: 42 oracle rows, ten
malformed fixtures, three persistent guards, seven witnessed concurrent
schedules, five SIGKILL recoveries and four server-restart scopes each. The
receipt retains 51 lock observations, twelve preserved/recovered snapshots,
WAL redo and five SQL constraint probes. Language/regression counts and their
proof boundaries agree with the retained logs.

## Limits

The reviewer made no edits and ran no builds, tests, database, network, Git or
delegation operations. Runtime results were independently assessed from retained
evidence rather than rerun. Acceptance covers this identified local synthetic
educational candidate. It establishes no production, external-provider,
physical power-loss or exhaustive concurrency guarantee.
