# Orders and payments: local validation

Executed by the integrator on 2026-10-11 in the ROO workspace. Toolchain:
Rust/Cargo 1.96.0, edition 2024; OpenJDK/javac 26.0.1 compiling with
`--release 21`; Python 3 and Bash. All checks were serialized. No external
dependencies, payment provider, credentials, network payment call, database,
broker or deployment were used by the implementations.

The complete combined-check output is retained in
[orders-payments-checks.log](orders-payments-checks.log). The checked Rust error
codes and actual Java compiler diagnostics are retained in
[orders-payments-negative-evidence.json](orders-payments-negative-evidence.json).

## Executed checks

| Check | Result and scope |
|---|---|
| `bash case-studies/orders-payments/verify.sh` | Exit 0; combined Java, Rust, shared oracle and original laboratory checks below |
| Java `javac --release 21 -Xlint:all -Werror` | Compiled every Java case source without warnings |
| Java `roo.payments.UnitTests` | 280 explicit assertion checks passed, including both coordinator variants and shared adapter contracts; these are assertions, not 280 separate test methods |
| Java compiler negatives | Two samples rejected for the intended private-access and final-method-override diagnostics; diagnostics retained in `java/build/negative/` |
| Case `cargo fmt --all -- --check` | Passed after integrator formatting |
| Case `cargo test --offline` | 20 unit tests, two positive doctests and three compile-fail doctests passed; binary test target contains no separate tests |
| Case `cargo clippy --offline --all-targets -- -D warnings` | Passed |
| Case `cargo build --offline --bin roo-payments` | Passed |
| Case `RUSTDOCFLAGS="-D warnings" cargo doc --offline --no-deps` | Passed; generated public API documentation with warnings treated as errors |
| `verify_rust_negative.py` | Independently compiled each negative sample; the complete set of error codes for each was exactly its declared E0382, E0502 or E0624. This rules out an unrelated import/syntax failure being counted as success |
| `verify.py`: Java composition | All 42 rows matched the independent expected TSV, in order, with exact header and fields; all 10 malformed fixtures rejected with a diagnostic and nonzero exit |
| `verify.py`: Java inheritance | Same 42 oracle rows and 10 malformed fixtures passed |
| `verify.py`: Rust composition | Same 42 oracle rows and 10 malformed fixtures passed |
| Original ROO laboratory | 10 unit tests, three positive doctests and four compile-fail doctests remain passing; no original library source changed |
| Rust `recovery` example | Exit 0; observed Unknown/Pending with one remote charge, then Approved recovery, Approved refund, failed relay acknowledgement, successful retry and two unique consumed facts |

The 42 fixture rows comprise all 30 normative SPEC scenarios and 12 additional
boundary/replay/refund cases. `expected.tsv` was transcribed from the accepted
contract independently of either implementation. Agreement between languages
alone is not the acceptance oracle. The harness also checks exact input/output
scenario coverage, output order, field count and duplicate output identities.

The malformed fixture set covers wrong header, duplicate scenario ID, unknown
action, wrong arity, malformed numeric text, unsupported mode, trailing empty
action, extra column, invalid identity and a malformed later action.

Unit checks inspect intermediate snapshots so later successful recovery cannot
hide an earlier incorrect state or duplicate effect. They include arithmetic
bounds, immutable observations, intent preparation failure, terminal commit
failure, Unknown versus NotFound, stable event identity, all request fingerprint
fields, typed key namespaces, full-refund linkage and duplicate delivery.

## Supplied guide checks

The Downloads original and the preserved source copy have SHA-256
`0b1edd27561e84a17777f1bf63a87a928a7d8fe9d603fd9f6b7e13fa504e6dd7`.
The original records unavailable compilers in its own earlier authoring session;
that historical statement does not describe this host.

- [Rust fence record](guide-snippet-checks.json): 15 selected self-contained
  original Rust fences compiled to metadata under Rust 1.96, edition 2024,
  adding only a minimal `main` wrapper and a dead-code allowance. No execution,
  linkage, FFI safety or all-fence coverage is implied.
- [Java fence record](guide-java-snippet-check.json): the complete sealed
  interface / record fence beginning at original line 209 compiled with
  `--release 21 -Xlint:all -Werror`. This is one classfile compilation, with no
  execution; the partial Java DI sketch was not compiled.
- [Assessment](guide-assessment.md) records three narrow factual corrections
  and preserves the source's useful qualifications. The [source ledger](orders-payments-sources.md)
  distinguishes language specifications, provider-specific documentation and
  the simulator's own assumptions.

## Proof boundaries

All payment effects, failures, commits, delivery attempts and recovery are
deterministic in-memory simulations in one thread. The checks establish observed
behavior for these fixtures and unit cases, plus selected compiler restrictions.
They do not prove durable transactions, process-crash recovery, concurrent
writers, real-provider retention/consistency, authorization, security of a real
integration, performance, exhaustive state-space coverage or production readiness.

The case deliberately permits one payment intent and one full refund per order;
decline is terminal and refund outcomes exclude decline. Provider key records
last for the whole fresh scenario. These are explicit teaching constraints.
Rust memory ownership and Java access restrictions do not establish remote
effect uniqueness, transactionality, or compensation success.

The new candidate manifest and independent review are separate artifacts in
this run; historical `candidate.json`, `validation.md` and `review.md` continue
to describe ROO v0.1 and are not rewritten by this case study.
