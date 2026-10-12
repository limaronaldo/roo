# ROO — Relationship & Ownership Oriented design

[![ROO adoption track](https://github.com/limaronaldo/roo/actions/workflows/roo-track.yml/badge.svg?branch=main)](https://github.com/limaronaldo/roo/actions/workflows/roo-track.yml?query=branch%3Amain)
[![Documentation](https://github.com/limaronaldo/roo/actions/workflows/docs.yml/badge.svg?branch=main)](https://limaronaldo.github.io/roo/)
[![Release](https://img.shields.io/github/v/release/limaronaldo/roo)](https://github.com/limaronaldo/roo/releases)
[![License: MIT OR Apache-2.0](https://img.shields.io/badge/license-MIT%20OR%20Apache--2.0-blue.svg)](LICENSE)

**Design relationships before choosing their representation.**

ROO is a proposed, language-independent design method. For a relationship that
crosses a lifecycle, process, transaction, or trust boundary, record who retains
the data, who coordinates its invariant, who may request a change, how access
expires, and how partial failure recovers. Then choose types, APIs, storage,
and protocols that uphold those decisions.

Maintained by [Ronaldo Martins](https://github.com/limaronaldo).
The material was developed with AI assistance, including review by separate
agents from the same model family. [How ROO was made](docs/how-roo-was-made.md)
describes that process and the scope of verification.

[Read v0.4.0 — operation permissions (preview)](https://limaronaldo.github.io/roo/) ·
[v0.3.0 — persistent authorization (preview)](https://limaronaldo.github.io/roo/v0.3.0/) ·
[v0.2.0 — eight-field contract (preview)](https://limaronaldo.github.io/roo/v0.2.0/) ·
[v0.1.0 — first edition (preview)](https://limaronaldo.github.io/roo/v0.1.0/) ·
[Development](https://limaronaldo.github.io/roo/dev/)

## Try ROO without installing anything

Consider an order whose payment request times out. Does that mean the provider
declined, or could the charge have succeeded? Write a contract before retrying:

```text
Relationship: Order -> PaymentAttempt
Invariant: recovery must not create a second charge
Custodian: local store retains intent; provider independently retains its result
Identity: reuse the same attempt ID and immutable request fingerprint
Coordinator: application sequences prepare, provider call, and finalization
Authorization: opt-in HTTP fixture rechecks current policy in each transaction
Access: order stores an ID and status observation, not a mutable provider object
Horizon: intent survives recovery; a status observation can become stale
Execution: short local transactions; provider operation commits independently
Failure: persist Pending before calling; reconcile unknown outcome by attempt ID
Evidence: shared success/failure scenarios; database and HTTP recovery checks
Open: verify a real provider's key retention and reconciliation guarantees
```

The [canonical contract and six-step procedure](docs/02-relationship-design.md)
define this record. The [short worksheet](templates/relationship-contract.md)
fits in a PR or an ADR. Apply it to one relationship, then try a duplicate
request, stale observation, or lost response against the proposed design.

Custody, invariant responsibility, identity, and authorization have separate
fields. A Rust mutable borrow or Java reference describes access; neither
decides who is entitled to refund an order.

## Read and apply

| Need | Start here |
|---|---|
| Understand the method | [Foundations](docs/01-foundations.md) and [relationship design](docs/02-relationship-design.md) |
| Translate OO concepts and inheritance | [Concept atlas](docs/03-concept-atlas.md), [23 GoF patterns](docs/04-pattern-catalog.md), [Rust and object design](docs/08-rust-and-object-design.md) |
| Choose architecture boundaries | [Architecture](docs/05-architecture.md) and [cross-language mappings](docs/06-cross-language.md) |
| Adopt one vertical slice | [Practical adoption](docs/09-adoption-guide.md) and [three completed templates](case-studies/orders-payments/adoption/relationship-contract.md) |
| Learn through equivalent exercises | [Learning path](docs/07-learning-path.md) and [six-exercise track](case-studies/orders-payments/track/README.md) |
| Inspect the evidence and its scope | [Claims and limits](docs/claims-and-limits.md) |

The orders/payments case follows the same decisions through
[in-memory state](case-studies/orders-payments/README.md),
[PostgreSQL concurrency and restart recovery](case-studies/orders-payments/postgres/README.md),
and [HTTP retry and response loss](case-studies/orders-payments/http/README.md).
Java composition, Java Template Method, and Rust composition use shared
scenario inputs and expected results. Inheritance is a legitimate alternative
when its hooks preserve the same behavioral contract.

The [durable HTTP authorization extension](case-studies/orders-payments/http/AUTHORIZATION.md)
adds opt-in synthetic policy checks to PostgreSQL transactions in all three API
variants. v0.4.0 adds separate permissions for each HTTP operation,
including revocation and reconciliation-only recovery after restart. See the
guide's migration rule for existing coarse grants.

The [authorization example](case-studies/orders-payments/authorization/README.md)
separately tests revocation between observing permission and executing an order
approval, with the same policy and outcomes in Java and Rust.

## Run the examples

The dependency-free root Rust laboratory requires Rust 1.96 or newer:

```sh
cargo test --locked --offline
cargo run --locked --offline --example order_workflow
```

Chapter Rust examples are included in rustdoc tests; the Java examples are
compiled for Java 21 and run with equivalent assertions:

```sh
python3 scripts/check_doc_examples.py
```

Run the authorization example's shared scenarios and controlled thread tests:

```sh
python3 case-studies/orders-payments/authorization/verify.py
```

With Docker, Compose, Bash, and common POSIX utilities, run the full track
with an isolated PostgreSQL lifecycle:

```sh
bash case-studies/orders-payments/track/compose.sh
```

The [Docker guide](case-studies/orders-payments/track/DOCKER.md) explains
starter and solution modes. The [hosted reproduction guide](docs/10-github-reproduction.md)
explains AMD64 qualification and how to inspect a run's evidence.

## Project status

v0.4.0 is the **operation permissions edition (preview)**. Its opt-in HTTP
fixture rechecks durable `(scope, principal, operation)` policy in Java and
Rust, including revocation and reconciliation-only recovery after restart.
Existing coarse grants require explicit operation grants; see the
[v0.4.0 migration notes](CHANGELOG.md#migration-from-030).
The eight-field contract is unchanged from v0.2.0.
Coordinator and Authorization fields replace v0.1.0's combined Mutation
authority field; see the [migration notes](CHANGELOG.md#migration-from-010).
v0.1.0 remains the **first edition (preview)**, and Development follows main.
Tagged editions and historical research records retain their original
content. Publication of a numeric release tag creates a documentation edition,
preserves earlier editions, and updates the selector. A version number records
a source snapshot, rather than certifying maturity.

ROO builds on information hiding, behavioral subtyping, ownership types,
separation logic, capabilities, RAII, DDD, and typestate. Its proposal is a
practitioner workflow that connects those ideas through explicit relationships.
Evaluation with independent human reviewers and real projects remains open.
See [claims and limits](docs/claims-and-limits.md) for the evidence map.

ROO originally stood for Rust Object Oriented. The expansion changed because
the method applies beyond Rust; Rust remains a laboratory language.

Contribute a concrete relationship and its counterexample using
[CONTRIBUTING.md](CONTRIBUTING.md). See [CHANGELOG.md](CHANGELOG.md),
[release notes](RELEASE_NOTES.md), and [RELEASING.md](RELEASING.md) for project
history and release instructions. Original material is available under
[MIT](LICENSE-MIT) OR [Apache-2.0](LICENSE-APACHE); [third-party terms](THIRD_PARTY_NOTICES.md)
apply to preserved inputs and dependencies.
