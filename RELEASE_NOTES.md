# ROO v0.2.0

**The eight-field Relationship Contract edition (preview).** ROO —
Relationship & Ownership Oriented design — is a language-independent method:
describe important relationships before choosing their realization in Java,
Rust, or another language.

## What changed

- One canonical contract with eight decisions: **Custodian, Identity,
  Coordinator, Authorization, Access, Horizon, Execution, Failure**.
- A six-step procedure: describe the scenario, triage relationships, complete
  the contract, choose realizations, check a counterexample, and record
  evidence before deciding.
- Chapters, three reusable templates, and completed orders/payments contracts
  aligned with the same method. Java composition, Java Template Method, and
  Rust composition show how the same decisions translate across languages.
- A shorter overview and worksheet, a worked payment relationship, and a
  three-clock explanation of memory validity, business lifecycle, and freshness.
- Rust and Java chapter examples compiled and executed directly from Markdown
  in CI, alongside positive and expected compile-fail Rust documentation tests.
- Versioned GitHub Pages with edition-local navigation and search, a version
  selector, exact source manifests, and automatic publication from numeric
  release tags. Earlier tagged documents and navigation remain preserved.
- Explicit claims and limits, AI-assisted authorship, and the scope of review
  by separate agents from the same model family. Independent human evaluation
  and evidence from real projects remain open.

## Migrate a v0.1.0 contract

Split **Mutation authority** into two independent answers:

| New field | Required decision |
|---|---|
| Coordinator | Which component and operations preserve the invariant? |
| Authorization | Which principal may request each operation, under which policy and revocation rule? |

Keep custody and identity separate from these roles. A mutable Rust borrow,
Java reference, known ID, or held capability does not alone establish caller
permission. Translate the other fields to the canonical compact keys listed
above. Invariant, Evidence, and Open supply context rather than additional
contract fields. See [Chapter 2](docs/02-relationship-design.md) and the
[worksheet](templates/relationship-contract.md).

The orders/payments teaching case does **not** implement caller authentication
or authorization; its contract now records that gap explicitly. This release
does not add a security layer or change case-study identifiers, policy inputs,
HTTP behavior, or the PostgreSQL schema.

## Read and reproduce

The [documentation site](https://limaronaldo.github.io/roo/) selects the
highest numeric release tag. Choose **v0.2.0**, **v0.1.0**, or **Development**
with the version selector. The original seven-field first edition remains
available at [v0.1.0](https://limaronaldo.github.io/roo/v0.1.0/), with its
[original release notes](https://github.com/limaronaldo/roo/blob/v0.1.0/RELEASE_NOTES.md).

With Docker, Compose, Bash, and common POSIX utilities installed:

```sh
git clone --branch v0.2.0 https://github.com/limaronaldo/roo.git
cd roo
bash case-studies/orders-payments/track/compose.sh
```

The qualification runs equivalent Java composition, Java Template Method,
and Rust scenarios against evaluator-owned PostgreSQL in an isolated
container. It checks that all six solution exercises pass, the shipped
starter remains intentionally incomplete, and exercise 6 can pass independently.
The scenarios cover idempotency, witnessed concurrency, process-death and
PostgreSQL restart/WAL recovery, outbox delivery, and lost HTTP responses.
See the [Docker guide](case-studies/orders-payments/track/DOCKER.md).

For the dependency-free root laboratory and the chapter examples:

```sh
cargo test --locked --offline
python3 scripts/check_doc_examples.py
```

Use Rust 1.96 or newer and Java 21. The published GitHub Release identifies
the exact tested commit and hosted Linux AMD64 run; its checked qualification
summary, workflow evidence, and `SHA256SUMS` retain evidence beyond the hosted
artifact's retention period. Documentation publication is verified separately
through the release dispatcher, Pages deployment, and public source manifests.

## License and scope

Original ROO material remains **MIT OR Apache-2.0**, at your option.
[Third-party terms](THIRD_PARTY_NOTICES.md) apply to preserved inputs and
dependencies. All new documentation is in English. The v0.1.0 tag and
historical research records are unchanged.

This is a GitHub source release. Rust packages remain `publish = false`;
no registry package, executable binary, or signing claim is included. A numeric
release tag records a source snapshot and does not certify method maturity.
Passing bounded educational scenarios does not establish every interleaving,
physical power-loss behavior, external provider behavior, or production
readiness. See [Claims and limits](docs/claims-and-limits.md) and the
[changelog](CHANGELOG.md).
