# Executable ROO track independent review

Date: 2026-10-11. Route: native collaboration, requested gpt-6.1-sol / medium.
Actual provider model, effort, usage, and call counts are unavailable. The
reviewer is separate from implementation and root runtime qualification.

## Initial result: CHANGES_REQUIRED

Candidate: `c85dfb218cca17533163b96304b0d4554ced1c8065c33958daf2548eeb113419`,
210 files and complete 2,633-line diff. The reviewer verified candidate hashes,
source/diff coverage, protected baseline files, local links, original fenced
examples, and runtime receipts. One actionable P2 finding: e6's supplementary
HTTP 202 case invoked the e2 learner recovery policy. An e6-only completion
could therefore fail despite satisfying every e6 obligation. No other
actionable finding was reported.

## Correction and requalification

The distinct architect approved an explicit harness/caller reconciliation
action for that supplementary demonstration, with provenance separate from
learner transcripts. Root removed the e2 call and unrelated learner negative
control, clarified English instructions, and added `check_independence.py`.
The regression compiles temporary Java/Rust starters with only e6 completed,
requires compiled e2 to return `stop`, executes real HTTP e6 in all three
variants, and rejects any non-e6 learner observation. Source starters remain
unchanged. The architect inspected the repair and reported no functional issue.

Root reran the complete qualification successfully, including 18 expected
starter behavioral RED groups, 18 solution PASS groups, and three independent
e6-only passes. Fresh saved receipts match all 19 executable source hashes.
The marked PostgreSQL cluster and all owned HTTP processes were stopped.

## Final review: ACCEPT

Target: `8e7e0c734394ed74d39ae1aa84fe96870542cdfee2507b748cb73def0191e99a`,
212 files, complete 2,768-line authored diff SHA-256
`c090aa000f7f4a94d569314fbf9780b7c499c15706afcd60361ab23098ea569e`.
The final reviewer must verify the repair, regression, evidence provenance,
updated documentation, exact target, and absence of new regressions.

The independent reviewer accepted this exact repaired candidate with no new
actionable finding. Prior full review plus affected-scope re-review reconciles
all 28 authored diff paths: four baseline modifications, 23 new track files,
and the qualification explanation. All 212 manifest entries and the candidate
identity recomputed exactly; the complete diff reconstructed byte-for-byte.
All 177 protected files, 14 original fenced examples, and 169 local links
passed the reviewer's independent integrity checks.

The reviewer confirmed that supplementary 202 reconciliation preserves actual
Pending-to-Paid, one-charge, one-event assertions while using explicit caller
provenance. The e6-only temporary learner test proves e2 remains incomplete
and checks real recovery for Java composition, Java inheritance, and Rust.
All three current receipts match 19 source hashes with no recorded errors.
The main and independence runtime evidence, boundary witnesses, and process
cleanup reconcile with the qualification record.

Review was read-only: runtime conclusions come from retained root evidence,
not a separate reviewer execution. Acceptance is limited to this learning
contract and its documented proof limits. Root rechecked exact manifest bytes
and protected baseline files after recording final acceptance.

## Provenance and drift note (2026-10-13)

Added after the fact; the earlier text is not rewritten. This report relies on the track manifests listed below. Those manifests list `{path, sha256, bytes}` for a working tree as it stood **before** it was committed; they are preserved unedited. Measured on 2026-10-13 against git with `python3 -I research/manifest-audit.py --rev 8bf017f --also 0c3e2bb --also v0.1.0` (full results: [manifest-provenance-8bf017f.json](manifest-provenance-8bf017f.json)):

| Manifest | Entries | Match no git blob | Identical at `0c3e2bb` | Identical at `8bf017f` (v0.4.3) | Identical at `0c3e2bb` but changed by later commits |
|---|---:|---:|---:|---:|---:|
| `roo-track-baseline.json` | 181 | 4 | 177 | 132 | 45 |
| `roo-track-candidate.json` | 212 | 2 | 210 | 159 | 51 |

- **Pre-commit state.** "Match no git blob" counts entries whose recorded SHA-256 equals no blob reachable from any git ref: those bytes were never committed, and the repository does not retain their intermediate content. `0c3e2bb` is the commit that first contains these manifests.
- **What "matched" means here.** Where this report says the candidate files matched the manifest, that was a working-tree comparison made at review time. This note neither repeats nor disproves it; it only shows that the claim cannot be reproduced from git for the entries counted above.
- **Drift after acceptance.** "Frozen" and "unchanged" in this report hold for the acceptance date only. At `8bf017f`, 53 of 212 entries in `roo-track-candidate.json` differ from the manifest (by area: 36 in `case-studies/`, 10 in `docs/`, 4 in `repository root files`, 2 in `templates/`, 1 in `src/`). 51 of those were byte-identical at `0c3e2bb` and were changed by later commits; the rest were already different from git at the first commit. The manifest was not updated, because historical manifests are not edited.
