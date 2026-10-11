# Changelog

This file records changes to public ROO releases. Versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html); the repository
release version is declared in the root `Cargo.toml` and tagged as `vX.Y.Z`.
Version 0.x is an evolving educational method and laboratory, with the
compatibility policy in [RELEASING.md](RELEASING.md).

## [Unreleased]

- Automatic documentation editions from stable release tags, with tagged
  navigation, semantic ordering, preservation checks against published sources,
  serialized publication on main, and an idempotent release dispatcher.

- Versioned GitHub Pages documentation with a pinned v0.1.0 content edition,
  a Development edition following main, an accessible version selector,
  edition-local search, source manifests, and redirects from existing URLs.

- GitHub Pages documentation with chapter, template, and case-study navigation,
  full-text search, a v0.1.0 release introduction, and automated build/link
  validation before deployment.

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

[Unreleased]: https://github.com/limaronaldo/roo/compare/v0.1.0...main
[0.1.0]: https://github.com/limaronaldo/roo/releases/tag/v0.1.0
