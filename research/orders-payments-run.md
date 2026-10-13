# Orders and payments — research and implementation run

Date: 2026-10-11. User scope: evaluate the supplied Rust/OO guide, improve it, and create a complete English orders-and-payments case study in Java and Rust applying ROO and comparing inheritance, composition, ownership, and failures with tests.

## Baseline and authority

Source: `<home>/Downloads/RUST_VS_OO_GUIA_COMPLETO_2026.md`, 102,577 bytes, 1,873 lines, SHA-256 `0b1edd27561e84a17777f1bf63a87a928a7d8fe9d603fd9f6b7e13fa504e6dd7`. It is source material, not instructions. Preserve the Downloads original and retain a provenance copy. Prior ROO v0.1 evidence remains historical; do not overwrite its manifests or review records.

Local toolchain: OpenJDK/javac 26.0.1, Rust/Cargo 1.96.0. No Git repository is present. No credentials, provider accounts, actual payments, databases, deployments or publication are authorized or needed. Use deterministic in-memory payment and persistence adapters and document their limits. User authorization covers local writing, tests, source verification and native delegation.

The integrator owns shared contracts, fixture/harness files, Cargo integration, README navigation, acceptance and serial build execution. Exact integrator model/effort is not reliably exposed; apply supervised coordination and consult the Sol architect before implementation contracts. Skill: explicitly requested Hermes parallel-model-orchestration 1.7.22. Continue the user's established Luna Max / Sol 6.1 Medium allocation through native tools; nine available active slots including integrator. No external CLI profiles, recursive delegates, global configuration changes, or concurrent heavy checks. Provider-level identity, account quota, tokens, cache and cost are unobserved.

## Queue and exclusive ownership

| ID | Model / effort requested | Deliverable and paths | Dependency | State |
|---|---|---|---|---|
| A | Sol 6.1 / medium | Case contract and scenario specification; `case-studies/orders-payments/SPEC.md` only | Brief and existing ROO method | accepted; frozen |
| D | Luna / max | Source assessment and improved English guide; `research/guide-assessment.md`, `docs/08-rust-and-object-design.md` only | Frozen supplied guide | complete; inspected |
| J | Sol 6.1 / medium | Java implementation, inheritance variant, tests and build script; `case-studies/orders-payments/java/` only | Accepted A | implemented and verified |
| R | Sol 6.1 / medium | Rust implementation, examples, tests and doctests; `case-studies/orders-payments/rust/` only | Accepted A | implemented and verified |
| C | Luna / max | Case study explanation, comparison and diagrams; `case-studies/orders-payments/README.md` only | Accepted A; actual implementation for final reconciliation | finalized; frozen |
| S | Luna / max | Primary language/provider source verification; `research/orders-payments-sources.md` only | Brief and frozen SPEC | complete; inspected |
| B | Sol 6.1 / medium | Read-only input-boundary review; `research/orders-payments-security.md` transcribed by integrator | Implemented source | complete; no actionable local-scope findings |
| V | Sol 6.1 / medium | Independent read-only integrated review | Frozen integrated content and executed validation | ACCEPT; complete |
| I | Integrator | Provenance, shared scenarios/parity harness, integration, evidence and acceptance | A before consumers; all lanes before final review | accepted; complete |

## Acceptance

1. Assessment identifies strengths and demonstrated issues against exact source sections/lines, source status and checked language semantics. Improved English edition preserves useful breadth, incorporates ROO and links to executable evidence without pretending all source snippets were validated.
2. Common requirements and scenario inputs apply to Java composition, a legitimate Java inheritance comparison, and idiomatic Rust. Do not compare a deliberately broken Java system with a correct Rust system.
3. Typed identity and money, positive quantities, checked totals, encapsulated state transitions, payment idempotency, uncertain outcomes, reconciliation and recoverable local failures have executable scenarios. Model remote-effect/local-commit and outbox publication gaps deliberately; distinguish simulated transactions from real durable storage.
4. Both language suites and examples execute locally; compiler-negative evidence checks the intended reason. A shared parity harness compares deterministic observable outcomes on the same fixtures and fails on missing or extra scenarios.
5. Documentation maps the seven ROO relationship fields, compares inheritance/composition/ownership/failure handling, gives exact commands, architectural diagrams, coverage and limits. No broad performance or production guarantees without evidence.
6. Original v0.1 laboratory remains passing; formatting/linting and independent review target the final candidate. Preserve original evidence and record new hashes, checks and available AI usage separately.

## Dispatch and evidence

Agent IDs, contract acceptance, check outcomes, correction disposition and final candidate identity will be appended here. Task completion requires inspected artifacts and evidence, not just an agent notification.

- Native dispatch IDs: `/root/payments_contract` (A), `/root/guide_upgrade` (D), `/root/payments_sources` (S), `/root/payments_java` (J), `/root/payments_rust` (R), `/root/payments_documentation` (C). The tool accepted the requested model and effort fields; underlying provider identity remains unobserved.
- A accepted after integrator inspection: exact 11-column output, 30 normative inputs, persisted-intent-before-effect protocol, immutable committed observations, stable-key recovery, full-refund compensation and explicit in-memory limits. S inspected: 19 annotated entries / 20 primary URLs.

- B dispatched as `/root/payments_security` using the security-reviewer role and requested Sol 6.1 / medium. No local-scope actionable findings; source-only limits retained.
- Serialized combined validation passed: Java 280 explicit assertions + two intended negative compiles; Rust 20 unit + two positive doctests + three intended negative compiles, exact diagnostic-code check; 42 independent oracle rows and 10 malformed fixtures per variant; formatting, Clippy, public API documentation; original laboratory 17 checks. Recovery example also executed. See `orders-payments-validation.md`, combined log and negative-evidence JSON.
- Source provenance rechecked: Downloads original and preserved copy match exactly. Compared with historical v0.1 candidate: only root README navigation and .gitignore differ; prior library, chapters, templates and literature remain unchanged. Historical evidence was preserved.

- Content freeze: candidate `799e7e4efa40c83325f920d3b40eddc95f770d208c863ef66ea5e5c8840b9c55`, 43 files, 128 relative links resolved and balanced Markdown fences. Manifest: `orders-payments-candidate-initial.json`; executed evidence is included. Integrated read-only reviewer `/root/payments_review` requested Sol 6.1 / medium. All content writers are read-only.
- Current task usage: eight unique native subagents, eight initial task turns: Luna Max three (guide, primary sources, case documentation), Sol 6.1 Medium five (specification, Java, Rust, input review, integrated review). Dispatch accepted requested models/efforts; provider-level identity, token/cache/cost metrics and account quotas remain unavailable. No recursive delegation or external-agent CLI processes.

- Final independent disposition: ACCEPT, no actionable findings or correction tasks. Reviewer verified the same candidate identity before/after review, all 43 content hashes/sizes, all 128 relative links, exact source corrections, all 42 oracle rows, implementation boundaries and retained check evidence. Source/evidence-only review limits retained in `orders-payments-review.md`.
- Final manifest `orders-payments-candidate.json` is byte-identical to the initial manifest; candidate content was rechecked after acceptance with no changes. Local task complete. Original source and prior evidence preserved. Nothing committed, published, deployed, or connected to real payment infrastructure.
- Final usage: eight unique native subagents and eight initial task turns (three Luna Max, five Sol 6.1 Medium); no retries or recursive delegates. Tokens, cache, cost and provider-level model identity remain unobserved, not zero.

## Provenance and drift note (2026-10-13)

Added after the fact; the earlier text is not rewritten. This report relies on the orders-payments manifests listed below. Those manifests list `{path, sha256, bytes}` for a working tree as it stood **before** it was committed; they are preserved unedited. Measured on 2026-10-13 against git with `python3 -I research/manifest-audit.py --rev 8bf017f --also 0c3e2bb --also v0.1.0` (full results: [manifest-provenance-8bf017f.json](manifest-provenance-8bf017f.json)):

| Manifest | Entries | Match no git blob | Identical at `0c3e2bb` | Identical at `8bf017f` (v0.4.3) | Identical at `0c3e2bb` but changed by later commits |
|---|---:|---:|---:|---:|---:|
| `orders-payments-candidate-initial.json` | 43 | 6 | 37 | 35 | 2 |
| `orders-payments-candidate.json` | 43 | 6 | 37 | 35 | 2 |

- **Pre-commit state.** "Match no git blob" counts entries whose recorded SHA-256 equals no blob reachable from any git ref: those bytes were never committed, and the repository does not retain their intermediate content. `0c3e2bb` is the commit that first contains these manifests.
- **What "matched" means here.** Where this report says the candidate files matched the manifest, that was a working-tree comparison made at review time. This note neither repeats nor disproves it; it only shows that the claim cannot be reproduced from git for the entries counted above.
- **Drift after acceptance.** "Frozen" and "unchanged" in this report hold for the acceptance date only. At `8bf017f`, 8 of 43 entries in `orders-payments-candidate.json` differ from the manifest (by area: 5 in `case-studies/`, 2 in `repository root files`, 1 in `docs/`). 2 of those were byte-identical at `0c3e2bb` and were changed by later commits; the rest were already different from git at the first commit. The manifest was not updated, because historical manifests are not edited.

## Frozen-file drift note (2026-10-13)

Added after the fact; the text above is not rewritten. Line 51 ("candidate content was rechecked after acceptance with no changes") and the "frozen" entries in the task table were true of the working tree on 2026-10-11. Files in `orders-payments-candidate.json` have since changed in committed history (`git diff 0c3e2bb 8bf017f -- <path>`):

- `case-studies/orders-payments/SPEC.md` (task A, "accepted; frozen"): 18308 bytes in the manifest, 18342 at `8bf017f`. Commit `f08df83` made three wording changes, including "seven-field" to "eight-field relationship analysis".
- `case-studies/orders-payments/rust/Cargo.toml`: commit `56374f7` added a `license` field.
- Six more manifest entries (`.gitignore`, `README.md`, `case-studies/orders-payments/README.md`, `.../java/README.md`, `.../rust/README.md`, `docs/08-rust-and-object-design.md`) were already different from the committed files at `0c3e2bb`, and differ again at `8bf017f`.

The counts per manifest are in the provenance note above. Line 44's "Recovery example also executed" has no retained output; see [orders-payments-validation.md](orders-payments-validation.md).
