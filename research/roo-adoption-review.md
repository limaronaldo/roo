# Independent practical ROO adoption documentation review

Date: 2026-10-11. Disposition: **ACCEPT**.

Reviewer: native delegate `adoption_final_review`; requested profile
`gpt-6.1-sol`, effort `medium`. Independent provider identity, actual effort,
token usage, cache, cost, and provider-call telemetry were unavailable.
Root persisted the delegate's terminal report below.

## Terminal reviewer report

Reviewed the complete 873-line diff, all four new documents, both navigation
edits, all three original templates, critical Java/Rust sources and intermediate
assertions, fixture/oracle rows, PostgreSQL transaction boundaries, HTTP recovery
contract, and cited historical validation records.

The guide provides an actionable adoption sequence for an existing project.
All template sections, seven relationship fields, supporting prompts, six
realization alternatives, seven ADR evidence categories, and twelve review
questions are retained and meaningfully completed. Java Template Method and
composition receive accurate treatment; Rust's exclusive capability borrows are
correctly distinguished from business identity, authorization, and persistence
guarantees.

The primary trace agrees with source and oracle: 250 USD minor units; persisted
`p1` before the effect; failed terminal commit leaves Pending, one charge, and
zero events; reconciliation reaches Paid with the same identity, one charge,
and one `payment:p1` event. Expected results, source assertions, and dated
execution evidence remain distinct.

The one identified documentation defect is resolved: the guide now states the
shared consumer guarantee, “Apply each unique EventId once,” without incorrectly
attributing Java's additional conflicting-content check to Rust.

Independent integrity verification confirms:

- Final candidate: `8c83e69c9106b79489d0efdc7ef8dd52b52c5e8f39b0c28920411bb5f4b1a16c`.
- All 178 candidate file hashes match.
- Only the two permitted navigation files differ from the 171-file baseline;
  169 protected files remain identical.
- All 13 existing navigation code fences remain identical.
- All 277 local links and four anchors resolve, including the intentional
  source-directory link.
- Independently reconstructed final diff matches exactly; SHA-256:
  `ccd363d072e13fe0befd0bfc809421699e9ec8a179f3eb8ef53ef4ee10bfddc7`.
- Refreshed static validation reports PASS and references that diff hash.

No unresolved actionable findings. This acceptance covers documentation
accuracy, completeness, usability, and preservation only. Review remained
read-only: no writes, builds, tests, network, SQL, HTTP, or cluster operations;
no new runtime or production assurance is established.

## Provenance and drift note (2026-10-13)

Added after the fact; the earlier text is not rewritten. This report relies on the adoption manifests listed below. Those manifests list `{path, sha256, bytes}` for a working tree as it stood **before** it was committed; they are preserved unedited. Measured on 2026-10-13 against git with `python3 -I research/manifest-audit.py --rev 8bf017f --also 0c3e2bb --also v0.1.0` (full results: [manifest-provenance-8bf017f.json](manifest-provenance-8bf017f.json)):

| Manifest | Entries | Match no git blob | Identical at `0c3e2bb` | Identical at `8bf017f` (v0.4.3) | Identical at `0c3e2bb` but changed by later commits |
|---|---:|---:|---:|---:|---:|
| `roo-adoption-baseline.json` | 171 | 3 | 168 | 126 | 42 |
| `roo-adoption-candidate.json` | 178 | 4 | 174 | 129 | 45 |

- **Pre-commit state.** "Match no git blob" counts entries whose recorded SHA-256 equals no blob reachable from any git ref: those bytes were never committed, and the repository does not retain their intermediate content. `0c3e2bb` is the commit that first contains these manifests.
- **What "matched" means here.** Where this report says the candidate files matched the manifest, that was a working-tree comparison made at review time. This note neither repeats nor disproves it; it only shows that the claim cannot be reproduced from git for the entries counted above.
- **Drift after acceptance.** "Frozen" and "unchanged" in this report hold for the acceptance date only. At `8bf017f`, 49 of 178 entries in `roo-adoption-candidate.json` differ from the manifest (by area: 32 in `case-studies/`, 10 in `docs/`, 4 in `repository root files`, 2 in `templates/`, 1 in `src/`). 45 of those were byte-identical at `0c3e2bb` and were changed by later commits; the rest were already different from git at the first commit. The manifest was not updated, because historical manifests are not edited.
