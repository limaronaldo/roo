# ROO v0.4.2

**The validation kit edition (preview).** ROO — Relationship & Ownership
Oriented design — now includes a practical protocol for human evaluation.
The method remains independent of language, runtime, database, and protocol.
Publishing the kit does not establish completed human review or field validation.

## What changed

- Add a [validation protocol](docs/validation/README.md) with separate
  [Rust](docs/validation/rust-review.md) and
  [DDD/architecture](docs/validation/ddd-review.md) reviewer briefs.
- Add a technology-neutral [document-publication exercise](docs/validation/exercise.md),
  a separate [facilitator guide](docs/validation/facilitator-guide.md), and a
  reusable [results template](templates/validation-results.md). The exercise
  covers stale content, revocation, competing admissions, conflicting keys,
  uncertain external effects, deletion, and restart.
- Predeclare success criteria and record scope, assistance, first attempts,
  predictions, observed checks, disagreements, and unknowns. Both proposed
  technology mappings must preserve every required promise to meet Transfer;
  a changed promise is unmet, and unresolved feasibility is unknown.
- Link the kit from the homepage, navigation, contributor guidance, and
  [Claims and limits](docs/claims-and-limits.md). Keep working notes private
  by default and publish only authorized synthetic summaries.

## Why a patch release

The eight contract fields, canonical six-step procedure, Java/Rust behavior,
operation-specific HTTP permissions, PostgreSQL schemas, idempotency, and
restart recovery are unchanged. No migration from v0.4.1 is required. This
compatible documentation addition uses a patch version under the
[release policy](RELEASING.md).

## Use the kit

Read the [documentation site](https://limaronaldo.github.io/roo/) and start
with the [validation protocol](docs/validation/README.md). The paper exercise
requires no code or toolchain. Assign human reviewers, preserve their initial
findings before discussion, and report negative or inconclusive results as
well as positive ones.

The initial method/code baseline remains v0.4.1, commit
`f6670a109d7dbfef8f72078b4cd361079ac6a10a`. Record the exact v0.4.2 kit commit
separately. A later trial may select other exact revisions, but participants
in the same trial must share the same requirements and frozen sources.

The version selector retains v0.1.0, v0.2.0, v0.3.0, v0.4.0, v0.4.1, and
Development. The automatic publisher selects v0.4.2 as the highest numeric
release tag and preserves previous editions and historical records.

## Reproduce the reference laboratories

With Docker, Compose, Bash, and common POSIX utilities:

```sh
git clone --branch v0.4.2 https://github.com/limaronaldo/roo.git
cd roo
bash case-studies/orders-payments/track/compose.sh
```

The shared qualification compares Java composition, Java Template Method, and
Rust composition with isolated PostgreSQL. It exercises idempotency,
concurrency, operation permissions, revocation, restart recovery, outbox
delivery, and lost responses. Shipped starters remain intentionally incomplete.
See the [Docker guide](case-studies/orders-payments/track/DOCKER.md) and
[contribution checks](CONTRIBUTING.md#validate-the-affected-behavior).

The GitHub Release records the exact qualified source and hosted Linux AMD64
run. Attached qualification/publication summaries, allowlisted workflow
evidence, and `SHA256SUMS` preserve checked evidence beyond hosted artifact
retention. Pages publication is verified separately through the automatic
tag dispatcher, deployment, selector, and public source manifests.

## License and scope

Original material remains **MIT OR Apache-2.0**, with
[third-party exceptions](THIRD_PARTY_NOTICES.md). Documentation is in English.
Earlier tags and historical research records retain their original content.

This is a GitHub source release; Rust packages remain `publish = false`.
Qualification covers the supplied reference laboratories and bounded scenarios.
It does not qualify alternative backends or establish production readiness,
real authentication, exhaustive interleavings, or physical power-loss durability.
Independent human evaluation remains open. See
[Claims and limits](docs/claims-and-limits.md) and the [changelog](CHANGELOG.md).
