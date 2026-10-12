# Rust reviewer brief

Evaluate whether the declared relationship decisions translate honestly into
Rust. Use the [kit protocol and criteria](README.md) and one
[results record](../../templates/validation-results.md). This is a human
technical review; running a compiler alone does not complete it.

## Scope and reading route

Start with the frozen [canonical contract](../02-relationship-design.md),
[Rust mapping](../rust-relationship-mapping.md), and
[evidence limits](../claims-and-limits.md). Inspect these small source areas
before considering longer chapters:

- [Order transitions](../../src/order.rs) and [typestate](../../src/typestate.rs):
  visibility, validation, and the outcome of rejected consuming operations.
- [Graph identities](../../src/graph.rs): lookup, removal, reuse, and missing targets.
- [Authorization coordinator](../../src/authorization.rs) and its
  [shared design](../../case-studies/orders-payments/authorization/DESIGN.md):
  observations, execution checks, revocation, and retained effects.

Record exactly which files and behaviors you inspected. PostgreSQL/HTTP code
is an optional extension with its own [specification](../../case-studies/orders-payments/http/AUTHORIZATION.md);
the small local review does not cover it automatically.

## Review in four passes

1. **Read the contract first.** Explain one relationship without Rust terms.
   Then map its eight decisions to public operations and enforcement boundaries.
   Identify a decision that the language leaves to runtime policy or storage.
2. **Inspect access and identity.** Can a caller bypass validation through a
   field, constructor, clone, shared handle, or returned view? Does an owned
   value preserve domain identity after a move? Can a removed/reused handle
   resolve to a different entity? Examine observable behavior, not the number
   of smart pointers or lifetime parameters.
3. **Try a counterexample.** Trace a rejected transition and the outcome of
   observing permission, revoking it, and then executing. Check ordering and
   retained state. Review suspension/cancellation claims where relevant;
   a local lock or borrow supplies only its stated coordination scope.
4. **Check the teaching claims.** Does each compiler, runtime, storage, or
   protocol claim match its evidence? Do Java comparisons preserve the same
   behavior? Flag needless complexity and alternatives that preserve the
   contract with a smaller API.

For each concern, provide the requirement, source location, triggering
sequence, expected outcome, and observed outcome or unresolved question.
Distinguish a demonstrated defect from a hypothetical failure.

## Optional reproduction

From the selected clean checkout, with Rust 1.96+:

```sh
cargo test --locked --offline
cargo run --locked --offline --example authorization_cases
```

For paired Java/Rust revocation traces and controlled thread scenarios, with
Python 3.10+, JDK 21+, and Rust 1.96+:

```sh
python3 case-studies/orders-payments/authorization/verify.py
```

Record commands, tool versions, commit, exit status, and evidence references.
If not executed, mark **not run**. A walkthrough predicts behavior; an executed
test observes its selected scenarios. Neither proves all interleavings or
production authorization. For a full persistence review, separately scope the
[isolated adoption track](../../case-studies/orders-payments/track/DOCKER.md).

## Required output

Submit a results record with one contract-to-API explanation, one success and
one failure trace, any reproducible findings, and a judgment on whether the
method clarified Rust design choices. State what it added beyond familiar
Rust ownership/API review and where it added only paperwork. Preserve initial
findings before reading the DDD review or exercise facilitator notes.
