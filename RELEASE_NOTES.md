# ROO v0.1.0

The first public release of **ROO — Relationship & Ownership Oriented design**
introduces a language-independent method and an executable orders/payments
laboratory. Design relationships by stating who retains data, who may mutate
it, how access expires, and how uncertainty and failure are resolved.

## Included

- Foundations, an OO concept atlas, all 23 GoF pattern translations,
  architecture guidance, and cross-language mappings.
- Three practical templates, completed adoption examples, and six exercises
  with starter code and solutions.
- Equivalent Java composition, Java Template Method, and Rust composition
  implementations with PostgreSQL persistence and HTTP APIs.
- Shared tests for idempotency, concurrency, process-death recovery,
  PostgreSQL restart/WAL recovery, outbox delivery, and lost HTTP responses.
- Docker Compose reproduction and a GitHub-hosted AMD64 workflow with source
  provenance, isolation checks, and exported qualification receipts.
- Versioning, a changelog, contribution and release guides, and workflow,
  release, and license badges.

## Reproduce the adoption track

With Docker, Compose, Bash, and common POSIX utilities installed:

```sh
git clone --branch v0.1.0 https://github.com/limaronaldo/roo.git
cd roo
bash case-studies/orders-payments/track/compose.sh
```

The full qualification checks that the shipped starter is incomplete, the
solution passes all six exercises in all three implementations, and exercise
6 can pass independently while exercise 2 remains incomplete. PostgreSQL is
owned by the evaluator inside the isolated container. See the
[Docker guide](https://github.com/limaronaldo/roo/blob/v0.1.0/case-studies/orders-payments/track/DOCKER.md)
and [contribution guide](https://github.com/limaronaldo/roo/blob/v0.1.0/CONTRIBUTING.md).

## License and scope

Original ROO software, documentation, templates, and examples are available
under **MIT OR Apache-2.0**, at your option. Preserved supplied research input
and other third-party material retain their own terms; see
[THIRD_PARTY_NOTICES.md](https://github.com/limaronaldo/roo/blob/v0.1.0/THIRD_PARTY_NOTICES.md).
New documentation is in English, and historical records are preserved.

Version 0.1.0 is an evolving educational method and laboratory. This release
provides source archives and qualification evidence; the Rust packages remain
`publish = false`. The tests cover the documented scenarios, without claiming
every interleaving, physical power-loss behavior, external payment providers,
or production readiness.

The published GitHub release identifies its exact tested commit and hosted
workflow run. Its attached qualification report, original workflow evidence
archive, and `SHA256SUMS` preserve those results beyond workflow-artifact
retention. The [changelog](https://github.com/limaronaldo/roo/blob/v0.1.0/CHANGELOG.md)
records the release contents.
