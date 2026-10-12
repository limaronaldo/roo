# Changelog

This file records changes to public ROO releases. Versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html); the repository
release version is declared in the root `Cargo.toml` and tagged as `vX.Y.Z`.
Version 0.x is an evolving educational method and laboratory, with the
compatibility policy in [RELEASING.md](RELEASING.md).

## [Unreleased]

### Changed

- Remove remaining retired contract labels from current chapters and case
  guides; distinguish invariant coordination, caller authorization, and local
  mutation access.
- Keep homepage teaching and links within the selected documentation edition,
  including an introduction matching the archived first edition.
- Shorten the worked homepage contract, separate its eight fields from framing
  lines, and remove the caveat caption and redundant release link.

### Added

- A CI vocabulary check for retired field labels and summaries, with narrow
  migration exceptions and regression tests.

## [0.2.0] — 2026-10-11

The eight-field Relationship Contract, with versioned documentation and
executable chapter examples. This remains a pre-1.0 preview of the method.

### Changed

- Consolidate the method into one eight-field contract and six-step procedure;
  separate invariant coordination from caller authorization throughout the
  current chapters, templates, and case documentation.
- Shorten the overview and worksheet, center the homepage on a worked payment
  relationship and three clocks, and identify pre-1.0 editions as previews.
- Describe AI-assisted authorship and same-family agent review accurately;
  collect evidence boundaries in Claims and limits.

### Added

- Compile and execute chapter Rust and Java examples directly from Markdown
  in documentation CI, with checks against unclassified or skipped fences.

- Automatic documentation editions from stable release tags, with tagged
  navigation, semantic ordering, preservation checks against published sources,
  serialized publication on main, and an idempotent release dispatcher.

- Versioned GitHub Pages documentation with a pinned v0.1.0 content edition,
  a Development edition following main, an accessible version selector,
  edition-local search, source manifests, and redirects from existing URLs.

- GitHub Pages documentation with chapter, template, and case-study navigation,
  full-text search, a v0.1.0 release introduction, and automated build/link
  validation before deployment.

### Migration from 0.1.0

- Replace the old **Mutation authority** field with **Coordinator** (the
  component and operations that preserve an invariant) and **Authorization**
  (the principal, permitted operations, policy, and revocation rule).
- Use the eight compact keys: **Custodian, Identity, Coordinator,
  Authorization, Access, Horizon, Execution, Failure**. Invariant, Evidence,
  and Open provide context; they are not additional contract fields.
- Follow the canonical six-step procedure in Chapter 2, then use the same
  decisions in Java or Rust. A reference, ID, mutable borrow, or capability
  does not by itself establish caller permission.
- Existing case-study identifiers, policy inputs, HTTP behavior, and database
  schema remain compatible. Caller authentication and authorization are still
  outside the executable teaching case; the separate field makes that gap
  explicit rather than adding a security implementation.
- The v0.1.0 tag, original seven-field chapters, navigation, and historical
  research records remain preserved. The documentation publisher selects
  v0.2.0 by default and retains v0.1.0 and Development in the version selector.

## [0.1.0] — 2026-10-11

First public release of **ROO — Relationship & Ownership Oriented design**.

### Added

- A language-independent method for describing ownership, mutation authority,
  identity, access duration, execution domains, and failure boundaries.
- Foundations, a classical OO concept atlas, all 23 GoF pattern translations,
  software architecture guidance, cross-language mappings, and a learning path.
- Three reusable templates and completed orders/payments adoption examples.
- Rust laboratory examples and positive/compile-fail tests.
- Equivalent Java composition, Java Template Method, and Rust composition
  studies, extended with PostgreSQL persistence and HTTP APIs.
- Six executable adoption exercises with starter code, completed solutions,
  shared policy cases, and malformed-input checks.
- Witnessed concurrency, process-death recovery, immediate PostgreSQL
  restart/WAL recovery, durable payment identities, outbox delivery, and HTTP
  response-loss recovery in the bounded educational scenarios.
- Docker Compose reproduction with a nonroot container, no external runtime
  network, no host mounts or published ports, and scoped cleanup.
- GitHub-hosted AMD64 qualification, commit/source provenance, restricted
  container inspection, and downloadable test evidence.
- Dual licensing for original ROO material under `MIT OR Apache-2.0`, explicit
  third-party exceptions, contribution and release guides, and README badges.

### Release scope

This is a GitHub source release. The Rust packages remain `publish = false`;
no package registry publication or executable binary distribution is included.
New documentation is in English. Historical research inputs and recorded
results retain their original bytes and meaning. Passing the test scenarios
does not establish every interleaving, physical power-loss behavior, external
provider behavior, or production readiness.

[Unreleased]: https://github.com/limaronaldo/roo/compare/v0.2.0...main
[0.2.0]: https://github.com/limaronaldo/roo/releases/tag/v0.2.0
[0.1.0]: https://github.com/limaronaldo/roo/releases/tag/v0.1.0
