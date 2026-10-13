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

## Provenance and drift note (2026-10-13)

Added after the fact; the earlier text is not rewritten. This report relies on the PostgreSQL manifests listed below. Those manifests list `{path, sha256, bytes}` for a working tree as it stood **before** it was committed; they are preserved unedited. Measured on 2026-10-13 against git with `python3 -I research/manifest-audit.py --rev 8bf017f --also 0c3e2bb --also v0.1.0` (full results: [manifest-provenance-8bf017f.json](manifest-provenance-8bf017f.json)):

| Manifest | Entries | Match no git blob | Identical at `0c3e2bb` | Identical at `8bf017f` (v0.4.3) | Identical at `0c3e2bb` but changed by later commits |
|---|---:|---:|---:|---:|---:|
| `postgres-candidate-initial.json` | 119 | 22 | 97 | 86 | 11 |
| `postgres-candidate.json` | 120 | 21 | 99 | 88 | 11 |

- **Pre-commit state.** "Match no git blob" counts entries whose recorded SHA-256 equals no blob reachable from any git ref: those bytes were never committed, and the repository does not retain their intermediate content. `0c3e2bb` is the commit that first contains these manifests.
- **What "matched" means here.** Where this report says the candidate files matched the manifest, that was a working-tree comparison made at review time. This note neither repeats nor disproves it; it only shows that the claim cannot be reproduced from git for the entries counted above.
- **Drift after acceptance.** "Frozen" and "unchanged" in this report hold for the acceptance date only. At `8bf017f`, 32 of 120 entries in `postgres-candidate.json` differ from the manifest (by area: 15 in `case-studies/`, 9 in `docs/`, 4 in `repository root files`, 3 in `templates/`, 1 in `src/`). 11 of those were byte-identical at `0c3e2bb` and were changed by later commits; the rest were already different from git at the first commit. The manifest was not updated, because historical manifests are not edited.
