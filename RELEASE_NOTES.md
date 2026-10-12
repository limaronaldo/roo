# ROO v0.3.0

**The persistent authorization edition (preview).** ROO — Relationship &
Ownership Oriented design — remains a language-independent method. This
release applies its Authorization field to durable HTTP operations in Java
composition, Java Template Method, and Rust composition. The eight-field
contract introduced in v0.2.0 is unchanged.

## What changed

- Opt-in HTTP fixture authorization backed by persistent PostgreSQL grants.
  Each protected transaction checks the current `(scope, principal)` policy
  before order or provider locks and retains its policy lock through completion.
- Equivalent tests for revocation between observation and execution, competing
  execution and revocation, denied reads and writes, and relay delivery while a
  revoker waits. A detached observation never grants later access.
- Recovery after API process death and immediate PostgreSQL restart, including
  denial after restart, later regrant, and reconciliation of the original
  payment/refund identity without another provider effect.
- The separate process-local Java/Rust authorization example, with shared
  outcomes and controlled thread schedules.
- Current vocabulary checks, edition-local homepage teaching, and a shorter
  worked homepage contract. Historical sources and records retain their wording.

See the [durable HTTP authorization contract](case-studies/orders-payments/http/AUTHORIZATION.md)
for the eight decisions, transaction ordering, HTTP outcomes, and tested limits.

## Upgrade from v0.2.0

Legacy HTTP mode remains the default when `ROO_HTTP_AUTH_MODE` is absent.
For the authorization fixture:

1. Install the existing PostgreSQL schema, then the additive
   [HTTP policy schema](case-studies/orders-payments/http/schema.sql).
2. Set `ROO_HTTP_AUTH_MODE=fixture` and `ROO_HTTP_TEST_MODE=1`.
3. Grant or revoke a synthetic `(scope, principal)` through trusted SQL. Keep
   denied rows as tombstones; do not delete policy rows or change their keys.
4. Send exactly one `X-Roo-Principal` matching `[A-Za-z0-9_]{1,32}`.

The header asserts a synthetic principal; it is **not authentication**. Missing
principals return 401, malformed/repeated principals return 400, and current
policy denial returns 403. There are no HTTP policy-administration routes,
roles, tenant policy, or real identity provider.

Revocation preserves effects already committed by earlier phases. A 403, 503,
timeout, or lost response is not proof of rollback. Reconcile a payment or
refund using current permission and its original key. Line additions still
have no durable command identity and must not be blindly replayed.

## Read and reproduce

The [documentation site](https://limaronaldo.github.io/roo/) selects the highest
numeric release tag. Its selector retains **v0.3.0**, **v0.2.0**, **v0.1.0**, and
**Development**. The earlier tagged chapters, templates, case studies, and
release notes remain available at their original edition URLs.

With Docker, Compose, Bash, and common POSIX utilities installed:

```sh
git clone --branch v0.3.0 https://github.com/limaronaldo/roo.git
cd roo
bash case-studies/orders-payments/track/compose.sh
```

Qualification runs the six adoption exercises, legacy HTTP scenarios, and the
persistent authorization matrix across all three variants, with isolated
PostgreSQL. It includes idempotency, witnessed concurrency, process/database
restart recovery, outbox delivery, and response loss. Shipped starters remain
intentionally incomplete. See the [Docker guide](case-studies/orders-payments/track/DOCKER.md).

For an existing Rust 1.96+ and Java 21 toolchain:

```sh
cargo test --locked --offline
python3 scripts/check_doc_examples.py
python3 case-studies/orders-payments/authorization/verify.py
bash case-studies/orders-payments/http/verify.sh
```

The GitHub Release identifies the exact qualified commit and hosted Linux
AMD64 run. Checked qualification/publication summaries, allowlisted workflow
evidence, and `SHA256SUMS` retain evidence beyond hosted artifact retention.
Pages publication is verified separately through the tag dispatcher, deployment,
version selector, and public source manifests.

## License and scope

Original material remains **MIT OR Apache-2.0**, at your option, with
[third-party exceptions](THIRD_PARTY_NOTICES.md). New documentation is in
English. The v0.1.0 and v0.2.0 tags and historical research records are preserved.

This is a GitHub source release; Rust packages remain `publish = false`. No
registry package, executable binary, signature, or production readiness is
claimed. The fixture shares one PostgreSQL/WAL domain with its simulated
provider. Its bounded scenarios do not establish real authentication,
external-provider authorization, exhaustive interleavings, or physical
power-loss durability. Independent human evaluation remains open. See
[Claims and limits](docs/claims-and-limits.md) and the [changelog](CHANGELOG.md).
