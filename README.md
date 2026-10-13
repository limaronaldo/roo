# ROO — Relationship & Ownership Oriented design

[![ROO adoption track](https://github.com/limaronaldo/roo/actions/workflows/roo-track.yml/badge.svg?branch=main)](https://github.com/limaronaldo/roo/actions/workflows/roo-track.yml?query=branch%3Amain)
[![Documentation](https://github.com/limaronaldo/roo/actions/workflows/docs.yml/badge.svg?branch=main)](https://limaronaldo.github.io/roo/)
[![Release](https://img.shields.io/github/v/release/limaronaldo/roo)](https://github.com/limaronaldo/roo/releases)
[![License: MIT OR Apache-2.0](https://img.shields.io/badge/license-MIT%20OR%20Apache--2.0-blue.svg)](LICENSE)

**Design relationships, ownership, and failure boundaries before choosing technologies.**

ROO is a proposed design method independent of programming language, runtime,
database, and protocol. For an important relationship, decide who retains the
data, who coordinates its invariant, who may request a change, how access
expires, and how partial failure recovers. Then select mechanisms and collect
evidence that they uphold those decisions.

Maintained by [Ronaldo Martins](https://github.com/limaronaldo).
Developed with AI assistance, including separate-agent review from the same
model family. [How ROO was made](docs/how-roo-was-made.md) describes authorship
and verification; independent human evaluation remains open.

[Released documentation](https://limaronaldo.github.io/roo/) ·
[Development](https://limaronaldo.github.io/roo/dev/) ·
[Release v0.4.3](https://github.com/limaronaldo/roo/releases/tag/v0.4.3)

## Try it on one relationship

A payment request times out. The charge may have succeeded. Before retrying,
write the relationship's decisions:

```text
Relationship: Order -> PaymentAttempt
Invariant: recovery preserves the original attempt and creates no second charge

Custodian: local store retains intent; provider independently retains its result
Identity: one scoped attempt ID binds the order, currency, amount, and operation
Coordinator: application sequences prepare/call/finalize; domain checks transitions
Authorization: baseline leaves caller policy open; define who may pay and recover
Access: detached observations and immutable commands expose no mutable provider
Horizon: intent survives recovery; an observation may become stale immediately
Execution: local commit boundaries and provider effects need separate coordination
Failure: retain Pending on uncertainty; reconcile the original attempt

Evidence: record observed checks for the chosen implementation and environment
Open: provider retention, policy, and unverified failure assumptions
```

The [canonical contract and six-step procedure](docs/02-relationship-design.md)
define the eight fields. Copy the [worksheet](templates/relationship-contract.md)
into a PR or ADR, then try a duplicate request, stale observation, or lost reply.

## Method, cases, and implementations

| Need | Start here |
|---|---|
| Learn the method | [Foundations](docs/01-foundations.md), [relationship design](docs/02-relationship-design.md), [architecture](docs/05-architecture.md) |
| Review a choice | [Technology selection](docs/technology-selection.md) and the [architecture decision template](templates/architecture-decision.md) |
| See decisions without a toolchain | [Payment recovery](case-studies/orders-payments/DESIGN.md) and [permission/revocation](case-studies/orders-payments/authorization/DESIGN.md) |
| Apply one operation | [Adoption guide](docs/09-adoption-guide.md) and [completed templates](case-studies/orders-payments/adoption/relationship-contract.md) |
| Inspect realizations | [Implementation index](docs/implementations.md), including language mappings and executable laboratories |
| Assess claims | [Claims and limits](docs/claims-and-limits.md) |
| Evaluate the proposal | [Validation kit](docs/validation/README.md): Rust and DDD review briefs, a technology-neutral exercise, and results template |
| Arrange human review | [First-round plan](docs/validation/first-round.md), unsent invitations, and a consolidation form for the v0.4.2 kit |

Java composition, Java Template Method, and Rust composition are current
reference implementations. PostgreSQL and HTTP laboratories add persistence,
concurrency, authorization, restart, and response-loss scenarios. Their
specifications keep exact APIs and mechanisms; they are examples of applying
the method, with bounded evidence.

Other languages, storage models, runtimes, and transports can be evaluated
against the same contract. No support or qualification for an alternative is
implied by listing it. If a technology needs a weaker promise, record the
changed contract explicitly.

## Reproduce the reference laboratories

The [implementation index](docs/implementations.md) explains each laboratory's
scope and toolchain. With Docker, Compose, Bash, and common POSIX utilities:

```sh
bash case-studies/orders-payments/track/compose.sh
```

For the root Rust examples with Rust 1.96+:

```sh
cargo test --locked --offline
cargo run --locked --offline --example order_workflow
```

Chapter examples and local authorization have [separate checks](CONTRIBUTING.md#validate-the-affected-behavior).
The [hosted guide](docs/10-github-reproduction.md) explains commit-bound AMD64
evidence. A successful lab run is evidence for those scenarios and candidate.

## Development improvements

The unreleased review corrections strengthen the reference laboratories and
the evidence used to assess them:

- Declined refunds leave the order unchanged; redelivering an event with a
  conflicting fact is detected and keeps the original fact.
- HTTP handling distinguishes size and framing errors, rejects URL fragments,
  and bounds slow body readers.
- Track boundary probes exercise the real runner and server. Docker status
  comes from the host, with CPU, memory, and process limits checked.
- CI definitions run the base, PostgreSQL, HTTP, and regression verifiers with
  distinct receipts. A tracked-file privacy guard checks for local paths and
  assistant session details.

The [development improvements guide](docs/development-improvements.md) maps
each correction to its source and checks. The dated port report records 27
passing local checks; that evidence does not establish hosted qualification
or behavior on an actual JDK 21 runtime. Consult the [CI runs](https://github.com/limaronaldo/roo/actions)
for subsequent integration results. These changes are not a new published
release or an evaluation of the method's efficacy.

## Status and provenance

v0.4.3 prepares the first human validation round for the v0.4.2 kit, with
unsent Rust and DDD invitations, a sequenced exercise, and a consolidation form.
The round has not started; publication does not complete human evaluation.
This pre-1.0 preview retains v0.4.1's separation
of method and implementations, and v0.4.0's eight-field method, operation
permissions, and executable APIs. v0.1.0's combined Mutation
authority field was split into Coordinator and Authorization in v0.2.0;
see the [migration notes](CHANGELOG.md#migration-from-010).
Published editions and historical research retain their sources and meaning.

ROO draws on information hiding, behavioral subtyping, ownership types,
separation logic, capabilities, RAII, DDD, and typestate. Its practitioner
workflow remains a proposal to evaluate with human reviewers and real projects.
ROO originally stood for Rust Object Oriented; the expansion changed to
reflect the method's broader scope.

Contribute through [CONTRIBUTING.md](CONTRIBUTING.md). See the
[changelog](CHANGELOG.md), [released notes](RELEASE_NOTES.md), and
[release policy](RELEASING.md). Original material uses [MIT](LICENSE-MIT) OR
[Apache-2.0](LICENSE-APACHE), with [third-party exceptions](THIRD_PARTY_NOTICES.md).
