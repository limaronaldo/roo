# ROO Compose and CI independent review

Status: **ACCEPT**. No actionable findings.

Date: 2026-10-11. Reviewer: distinct native delegate `compose_final_review`.
Requested profile: Sol 6.1 Medium. Actual provider model, effort, and usage
telemetry were not exposed. The reviewer applied the code-review-rm procedure
through read-only source inspection and evidence reconciliation. Root executed
the runtime checks; the reviewer did not execute or mutate the application,
Docker, or PostgreSQL.

Accepted [final candidate](roo-compose-candidate.json):
`b8cbee1a27fa27416a8f6f1a6207a9da85a13d337b030d403c1ffde136d5b5d7`.
All 235 file hashes and sizes match; the independently recomputed candidate
identity matches. The complete 608-line authored diff matches SHA-256
`2147398e0fd6b27804e03aec1e24100e4b31e35391177aa29de31184e6a5a4c3`.
All 223 previously reviewed source files remain unchanged. The 10 source and
documentation paths reconcile with the preserved baseline.

The reviewer independently reconciled:

- Native ARM64 and locally emulated AMD64 full qualification receipts,
  preserving the Java/Rust matrix, immediate restart/WAL recovery, HTTP
  response-loss checks, and e6 independence.
- Intentional learner failure: test/container/wrapper status 1, with evidence
  collection, export, and cleanup succeeding.
- All 133 exported artifact hashes and sizes, embedded receipts, 117 baked
  source hashes, and 19 evaluator/learner hashes per receipt.
- Running full-container isolation observations and unchanged host PostgreSQL
  marker, configuration, and server-log hashes.
- Immutable workflow pins and relevant inputs against official action sources.
- English documentation, preservation scope, and local-versus-hosted proof
  distinctions in the validation record.

Acceptance covers this frozen local implementation and recorded qualification.
Hosted GitHub Actions execution, native AMD64 hardware, optional PostgreSQL JIT
extension closure, and production readiness remain unproven as documented.
The current run ledger, this verdict, and the candidate manifest itself are
excluded from the manifest to avoid self-reference. See
[validation and proof limits](roo-compose-validation.md) and
[the run and AI usage record](roo-compose-run.md).

## Provenance and drift note (2026-10-13)

Added after the fact; the earlier text is not rewritten. This report relies on the Compose manifests listed below. Those manifests list `{path, sha256, bytes}` for a working tree as it stood **before** it was committed; they are preserved unedited. Measured on 2026-10-13 against git with `python3 -I research/manifest-audit.py --rev 8bf017f --also 0c3e2bb --also v0.1.0` (full results: [manifest-provenance-8bf017f.json](manifest-provenance-8bf017f.json)):

| Manifest | Entries | Match no git blob | Identical at `0c3e2bb` | Identical at `8bf017f` (v0.4.3) | Identical at `0c3e2bb` but changed by later commits |
|---|---:|---:|---:|---:|---:|
| `roo-compose-baseline.json` | 215 | 2 | 213 | 162 | 51 |
| `roo-compose-source-candidate.json` | 223 | 3 | 220 | 164 | 56 |
| `roo-compose-candidate.json` | 235 | 3 | 232 | 176 | 56 |

- **Pre-commit state.** "Match no git blob" counts entries whose recorded SHA-256 equals no blob reachable from any git ref: those bytes were never committed, and the repository does not retain their intermediate content. `0c3e2bb` is the commit that first contains these manifests.
- **What "matched" means here.** Where this report says the candidate files matched the manifest, that was a working-tree comparison made at review time. This note neither repeats nor disproves it; it only shows that the claim cannot be reproduced from git for the entries counted above.
- **Drift after acceptance.** "Frozen" and "unchanged" in this report hold for the acceptance date only. At `8bf017f`, 59 of 235 entries in `roo-compose-candidate.json` differ from the manifest (by area: 41 in `case-studies/`, 10 in `docs/`, 4 in `repository root files`, 2 in `templates/`, 1 in `.github/`, 1 in `src/`). 56 of those were byte-identical at `0c3e2bb` and were changed by later commits; the rest were already different from git at the first commit. The manifest was not updated, because historical manifests are not edited.
