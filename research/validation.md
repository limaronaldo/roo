# Validation evidence — ROO v0.1

Date: 2026-10-11. Local execution in the ROO project directory on the user's macOS host. Rust and Cargo both report 1.96.0. This record concerns educational source and documentation; it does not establish production behavior.

## Executed Rust checks

Commands were invoked through `rtk proxy` to preserve their exact outputs. Cargo operations ran serially and used offline mode.

| Check | Observed result |
|---|---|
| `cargo fmt --all` | Exit 0; source formatted before testing |
| `cargo test --offline` | Exit 0; 10 unit tests, 3 successful doctests, 4 expected compilation failures |
| `cargo clippy --offline --all-targets -- -D warnings` | Exit 0; no warnings |
| `cargo run --offline --example order_workflow` | Exit 0; `customer-7: 1 line(s), total 4500 cents` |
| `cargo run --offline --example graph_events` | Exit 0; `removed project` |
| `cargo run --offline --example command_transfer` | Exit 0; `Transferred command produced total 800 cents` |
| `cargo doc --offline --no-deps` | Exit 0; local API documentation generated |
| `cargo fmt --all -- --check` | Exit 0 |

## Expected failures checked for the intended reason

The four `compile_fail` bodies were independently extracted from source, wrapped in `fn main`, and compiled using `rustc --edition=2024` against the checked local library. Each invocation returned exit 1 and exactly the expected coded error, rather than merely an unrelated import or syntax failure.

| Source / case | Actual diagnostic | Obligation |
|---|---|---|
| `src/typestate.rs`, first failure | `E0599` | `Submitted` has no `add_line` operation |
| `src/typestate.rs`, second failure | `E0382` | A submitted draft has been moved |
| `src/view.rs`, first failure | `E0597` | A view cannot outlive its borrowed order |
| `src/view.rs`, second failure | `E0499` | Exclusive borrows overlap while both remain used |

Positive doctest controls cover successful submission, a valid borrowed view, and sequential mutable borrows. Module tests cover invalid inputs, checked arithmetic and state preservation, behaviorally invalid strategy implementations, retryable consuming transitions, stale/foreign handles, and unsubscribe behavior.

## Documentation and review

The canonical names of all 23 GoF patterns were mechanically found in the catalog (5 creational, 7 structural, 11 behavioral). Name presence is a coverage aid, not proof of semantic quality.

The initial local Markdown link check covered 34 relative file targets across 16 Markdown files; every target existed. A separate GFM-style check resolved all 18 local heading links. External availability was outside these mechanical checks.

After saving review and evidence, the final check verified all 27 content hashes and sizes and found all 36 relative file targets across 17 Markdown files. It also verified the canonical manifest identifier.

The final integrated content is identified by [candidate.json](candidate.json), SHA-256 `2e7f4aafab61b8f664a6cd84b3e1183ed9cef4cfd228cdc13c67a21c2f71df2d` (27 content files). The [independent review](review.md) accepted the original draft and the final citation-only correction after checking every manifest entry. The initial manifest is preserved as `candidate-initial.json`. Executable source is identical to the source tested above; the correction did not require repeating unrelated Rust tests.

Primary-source retrieval limitations are documented in the chapters and literature ledger; a linked citation is not a claim that every full text was accessible.

## Scope of assurance

The checked executable code is in `src/` and the three programs in `examples/`. Design sketches in chapters are not a separately compiled Java or multi-language suite. No paid-service probes, database operations, production calls, remote publication, commits or deployments are part of this result.

Passing checks do not prove behavioral correctness for all inputs, authorization, deadlock freedom, bounded memory use, persistence semantics, durable event delivery, or distributed consistency. The laboratory guide states the relevant example limitations.
