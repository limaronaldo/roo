# ROO v0.4.1

**The method and implementations edition (preview).** ROO — Relationship &
Ownership Oriented design — starts with relationship decisions independent of
language, runtime, database, and protocol. This release makes that distinction
clearer throughout the documentation and site.

## What changed

- Separate navigation for **Method**, **Templates**, **Design cases**,
  **Implementations**, and **Evidence**. Start with the contract and neutral
  payment/revocation cases, then explore executable laboratories.
- Move Rust mechanism detail into a dedicated
  [relationship mapping guide](docs/rust-relationship-mapping.md), with an
  [implementation index](docs/implementations.md) for Java, Rust, PostgreSQL,
  and HTTP examples.
- Add [technology-selection questions](docs/technology-selection.md) for
  evaluating other storage models, runtimes, and coordination mechanisms
  against the same relationship obligations. Listing a technology does not
  establish implementation support or qualification.
- Preserve v0.1.0–v0.4.0 introductions, navigation, and tagged documents.
  Starting with this release, each new edition's homepage is read from its own
  tag and recorded as release content in its public source manifest.

## Why a patch release

The eight contract fields and canonical six-step procedure are unchanged.
Java/Rust behavior, operation-specific permissions, PostgreSQL schemas,
idempotency, and restart recovery retain the v0.4.0 contracts. There is no
migration from v0.4.0. The changes organize and clarify compatible documentation,
so they use a patch version under the [release policy](RELEASING.md).

## Read and reproduce

Read the [documentation site](https://limaronaldo.github.io/roo/),
starting with the [method](docs/02-relationship-design.md),
[payment recovery case](case-studies/orders-payments/DESIGN.md), and
[permission/revocation case](case-studies/orders-payments/authorization/DESIGN.md).
The selector retains v0.1.0, v0.2.0, v0.3.0, v0.4.0, and Development. The site
default becomes v0.4.1 as the highest numeric release tag.

With Docker, Compose, Bash, and common POSIX utilities:

```sh
git clone --branch v0.4.1 https://github.com/limaronaldo/roo.git
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
