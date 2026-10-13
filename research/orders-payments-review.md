# Independent integrated review

Date: 2026-10-11. Reviewer: `/root/payments_review`, requested native GPT-6.1
Sol / medium. Integrator transcribed the final result. The reviewer owned no
implementation files, made no edits, ran no builds/tests and spawned no agents.

**ACCEPT for the frozen educational candidate. No actionable findings.**

Candidate identity independently verified before and after review:
`799e7e4efa40c83325f920d3b40eddc95f770d208c863ef66ea5e5c8840b9c55`.
All 43 files matched their recorded SHA-256 and byte size. Historical baseline
content matched its manifest except the intentionally changed root README
navigation and `.gitignore`. All 128 inspected relative file links resolved.

## Coverage and reasoning

- Preserved Portuguese source hash and the three exact corrections at original
  lines 294, 300 and 316. The English edition preserves qualifications, fairly
  compares modern Java and Rust, and maps all 29 original topics.
- Frozen SPEC, all 42 fixture/oracle rows, Java and Rust domain, application,
  adapters and tests, strict parsing, shared verification, compiler-negative
  harnesses, documentation and retained execution evidence.
- Legitimate Java Template Method with final algorithms and narrow stable-adapter
  hooks; independent composition implementation; actual Rust composition
  through exclusive borrows of concrete adapters.
- Intent persistence before remote effects, immutable request fingerprints,
  typed key namespaces, terminal replay, Unknown versus NotFound, refund
  linkage, failed local commits, outbox acknowledgement gaps and duplicate
  suppression.
- Meaningful intermediate assertions and a strict independent oracle. Recorded
  negative diagnostics match intended Java access restrictions and Rust E0382,
  E0502 and E0624.

The retained validation log supports 280 Java assertions, 20 Rust unit tests,
positive/negative doctests, 42 oracle rows and ten malformed fixtures per runner.
Documentation consistently limits those results to deterministic in-memory
simulation and makes no production or performance claim.

## Confidence limits

This was independent read-only source/evidence review. The reviewer did not
rerun builds/tests, execute payment operations, edit files, use Git or delegate.
External source pages and historical evidence excluded from the baseline
manifest were not independently re-fetched or cryptographically attributed.
Acceptance covers the identified local candidate and bounded contract.

## Integrator disposition

Accepted with no correction tasks. The final manifest is
[orders-payments-candidate.json](orders-payments-candidate.json); its content
records and identity match the initial frozen manifest exactly. Review and run
ledger are excluded from the content identity to avoid a circular hash.
The [validation record](orders-payments-validation.md) and executed-check log
are included in the candidate identity. No executable or documentary candidate
content changed after review.

## Provenance and drift note (2026-10-13)

Added after the fact; the earlier text is not rewritten. This report relies on the orders-payments manifests listed below. Those manifests list `{path, sha256, bytes}` for a working tree as it stood **before** it was committed; they are preserved unedited. Measured on 2026-10-13 against git with `python3 -I research/manifest-audit.py --rev 8bf017f --also 0c3e2bb --also v0.1.0` (full results: [manifest-provenance-8bf017f.json](manifest-provenance-8bf017f.json)):

| Manifest | Entries | Match no git blob | Identical at `0c3e2bb` | Identical at `8bf017f` (v0.4.3) | Identical at `0c3e2bb` but changed by later commits |
|---|---:|---:|---:|---:|---:|
| `orders-payments-candidate-initial.json` | 43 | 6 | 37 | 35 | 2 |
| `orders-payments-candidate.json` | 43 | 6 | 37 | 35 | 2 |

- **Pre-commit state.** "Match no git blob" counts entries whose recorded SHA-256 equals no blob reachable from any git ref: those bytes were never committed, and the repository does not retain their intermediate content. `0c3e2bb` is the commit that first contains these manifests.
- **What "matched" means here.** Where this report says the candidate files matched the manifest, that was a working-tree comparison made at review time. This note neither repeats nor disproves it; it only shows that the claim cannot be reproduced from git for the entries counted above.
- **Drift after acceptance.** "Frozen" and "unchanged" in this report hold for the acceptance date only. At `8bf017f`, 8 of 43 entries in `orders-payments-candidate.json` differ from the manifest (by area: 5 in `case-studies/`, 2 in `repository root files`, 1 in `docs/`). 2 of those were byte-identical at `0c3e2bb` and were changed by later commits; the rest were already different from git at the first commit. The manifest was not updated, because historical manifests are not edited.
