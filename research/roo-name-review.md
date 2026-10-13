# Independent review: ROO expansion update

**ACCEPT**

Candidate: `ce97665a034127dde219a8784ef49846513191bbd5131461a71c7cfcfde889e3`

This preserves the terminal report returned by the independent `rename_review`
delegate. Root saved the report after review; the reviewer wrote no files.

Independently verified all 162 candidate files’ hashes and sizes and recomputed
candidate identity. Against the 158-file baseline, 153 files remain
byte-identical; reversing only the six recorded replacements in the five
authorized files recovers every original hash and size.

Actual titles, introductions, historical note, and Cargo description match the
supplied recipe. Crate name, Java packages, scripts, lockfiles, case-study
sources, original guide, historical ledger, receipts, and manifests remain
unchanged. Independent source inventory found only the declared candidate
manifest and current naming ledger outside coverage. All 28 local link targets
exist.

No actionable findings.

Limits: read-only source, hash, and receipt review. The retained test receipt
reports 17 passing tests; I did not rerun builds/tests or perform network, HTTP,
SQL, cluster, or Git operations. No judgment on historical architecture or
runtime claims.

AI usage: one native reviewer; model/effort allocation recorded by the integrator
as Sol 6.1 Medium; effective provider telemetry, tokens, and cost were not
observed.

## Provenance and drift note (2026-10-13)

Added after the fact; the earlier text is not rewritten. This report relies on the naming manifests listed below. Those manifests list `{path, sha256, bytes}` for a working tree as it stood **before** it was committed; they are preserved unedited. Measured on 2026-10-13 against git with `python3 -I research/manifest-audit.py --rev 8bf017f --also 0c3e2bb --also v0.1.0` (full results: [manifest-provenance-8bf017f.json](manifest-provenance-8bf017f.json)):

| Manifest | Entries | Match no git blob | Identical at `0c3e2bb` | Identical at `8bf017f` (v0.4.3) | Identical at `0c3e2bb` but changed by later commits |
|---|---:|---:|---:|---:|---:|
| `roo-name-baseline.json` | 158 | 24 | 134 | 112 | 22 |
| `roo-name-candidate.json` | 162 | 23 | 139 | 116 | 23 |

- **Pre-commit state.** "Match no git blob" counts entries whose recorded SHA-256 equals no blob reachable from any git ref: those bytes were never committed, and the repository does not retain their intermediate content. `0c3e2bb` is the commit that first contains these manifests.
- **What "matched" means here.** Where this report says the candidate files matched the manifest, that was a working-tree comparison made at review time. This note neither repeats nor disproves it; it only shows that the claim cannot be reproduced from git for the entries counted above.
- **Drift after acceptance.** "Frozen" and "unchanged" in this report hold for the acceptance date only. At `8bf017f`, 46 of 162 entries in `roo-name-candidate.json` differ from the manifest (by area: 29 in `case-studies/`, 9 in `docs/`, 4 in `repository root files`, 3 in `templates/`, 1 in `src/`). 23 of those were byte-identical at `0c3e2bb` and were changed by later commits; the rest were already different from git at the first commit. The manifest was not updated, because historical manifests are not edited.
