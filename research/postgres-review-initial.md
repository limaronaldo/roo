# Initial PostgreSQL candidate review

Reviewer: independent native Sol 6.1 Medium, pg_review. Date: 2026-10-11.
Candidate: a3b25017dcfe58184956a16df7130af346a661e61291824f5d174d84bde77a38.

One actionable Low documentation finding; no functional correctness defect
found within the reviewed synthetic scope.

The source ledger at postgres-sources.md:52 prohibited app locks over provider
or consumer calls. The normative relay contract intentionally holds the app
order lock across a bounded independent local inbox transaction. Clarify that
provider calls release app locks and the simulator's consumer exception forbids
inverse inbox-to-app/provider locking. See PostgreSQL SPEC:86–106, Java
Store.java:120–141 and Rust database.rs:496–512 in this initial candidate.

Both manifests agreed before and after review; every one of 119 file SHA-256
hashes and sizes matched, and the canonical identity recomputed correctly.
Coverage included PostgreSQL source/schema/parsing, language checks, shared
harness, documentation and retained evidence. The historical 43-file baseline
differs only in root README.md and .gitignore. All 201 relative Markdown file
targets across manifested documents resolved.

Evidence reconciled per variant: 42 oracle rows, 10 malformed fixtures,
3 persistent guards, 7 concurrent schedules, 5 SIGKILL recoveries and 4 restart
scopes. Receipt has 51 lock observations, 12 preserved/recovered snapshots,
WAL redo and five SQL constraint probes. Source supports independently committed
effects, stable fingerprints, serialized mutations, atomic terminal/outbox,
deduplicated inbox and fresh-process recovery. Template inheritance legitimately
fixes orchestration; Rust borrowing is explicitly local. Documentation bounds
shared-server durability, trusted adapters, uncertain COMMIT, production
security and external-provider claims.

The reviewer modified no files and performed no builds, tests, database,
network, Git or recursive delegation. Runtime results were assessed from
retained evidence rather than independently rerun. This initial review is
preserved; the corrected candidate needs a focused final re-review.
