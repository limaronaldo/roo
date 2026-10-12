# ROO v0.4.0

**The operation permissions edition (preview).** ROO — Relationship &
Ownership Oriented design — remains a language-independent method. This
release applies its Authorization field to separate HTTP operations in Java
composition, Java Template Method, and Rust composition, backed by PostgreSQL.
The eight-field contract introduced in v0.2.0 is unchanged.

## What changed

- Each fixture request binds one immutable operation. Every protected
  transaction checks its exact `(scope, principal, operation)` policy row
  before business locks or effects and retains the policy lock through
  completion, including retries and response reads.
- Eight explicit permissions: `read`, `init`, `add`, `pay`, `refund`,
  `reconcile`, `relay`, and the test-only `provider_conflict`. A permission
  grants only its named operation.
- Reconciliation-only callers can recover existing payment/refund intents
  after revocation or API/PostgreSQL restart. Recovery preserves the original
  identity and fingerprint, without creating another intent or provider effect.
- Equivalent permission-isolation, revocation, restart, and invalid-request
  tests across all three variants. Java and Rust now use the same rejection
  precedence when several application-level inputs are invalid.
- Updated learning and reproduction guidance that distinguishes current
  qualification from historical receipts.

See the [durable HTTP authorization contract](case-studies/orders-payments/http/AUTHORIZATION.md)
for transaction ordering, HTTP outcomes, and tested limits.

## Upgrade from v0.3.0

Legacy HTTP mode remains the default when `ROO_HTTP_AUTH_MODE` is absent.
Fixture authorization has an incompatible policy and observation-route change:

1. Install the existing PostgreSQL schema, then the updated additive
   [HTTP policy schema](case-studies/orders-payments/http/schema.sql).
2. Explicitly seed the intended `(scope, principal, operation)` rows in
   `roo_authorization.operation_grants` through trusted SQL before cutover.
   Existing coarse grants remain stored but are inert for v0.4.0 fixture
   binaries. There is no automatic backfill, fallback, wildcard, or implied
   grant. Keep denied rows as tombstones; do not delete policy rows or change
   their keys.
3. Set `ROO_HTTP_AUTH_MODE=fixture` and `ROO_HTTP_TEST_MODE=1`.
4. Send exactly one `X-Roo-Principal` matching `[A-Za-z0-9_]{1,32}`.
5. Use `GET /v1/scopes/{scope}/authorization/{operation}` for advisory
   observation. Execution always checks current permission again.

The header asserts a synthetic principal; it is **not authentication**.
Missing principals return 401, malformed/repeated principals return 400, and
current policy denial returns 403. There are no HTTP policy-administration
routes, roles, tenant policy, or real identity provider.

A `pay` grant does not imply `read` or `reconcile`; a payment response uses the
request's bound `pay` permission. Grant `reconcile` explicitly when a caller
should recover retained intents, possibly for a different synthetic principal.
That permission cannot initiate a new payment or refund.

Revocation preserves effects committed by earlier phases. A 403, 503, timeout,
or lost response is not proof of rollback. Recover a payment or refund through
reconciliation with its original key and current permission. Line additions
still have no durable command identity and must not be blindly replayed.

## Read and reproduce

The [documentation site](https://limaronaldo.github.io/roo/) selects the highest
numeric release tag. Its selector retains **v0.4.0**, **v0.3.0**, **v0.2.0**,
**v0.1.0**, and **Development**. Earlier chapters, templates, case studies,
and release notes remain at their original edition URLs.

With Docker, Compose, Bash, and common POSIX utilities installed:

```sh
git clone --branch v0.4.0 https://github.com/limaronaldo/roo.git
cd roo
bash case-studies/orders-payments/track/compose.sh
```

Qualification runs the six adoption exercises, legacy HTTP scenarios, and the
operation-permission matrix across all three variants, with isolated PostgreSQL.
It includes idempotency, witnessed concurrency, revocation, process/database
restart recovery, outbox delivery, and response loss. Shipped starters remain
intentionally incomplete. See the [Docker guide](case-studies/orders-payments/track/DOCKER.md).

For an existing Rust 1.96+ and Java 21 toolchain:

```sh
cargo fmt --all -- --check
cargo test --locked --offline
cargo clippy --locked --offline --all-targets -- -D warnings
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
English. The v0.1.0, v0.2.0, and v0.3.0 tags and historical research records
are preserved.

This is a GitHub source release; Rust packages remain `publish = false`. No
registry package, executable binary, signature, or production readiness is
claimed. The fixture shares one PostgreSQL/WAL domain with its simulated
provider. Its bounded scenarios do not establish real authentication,
external-provider authorization, exhaustive interleavings, or physical
power-loss durability. Independent human evaluation remains open. See
[Claims and limits](docs/claims-and-limits.md) and the [changelog](CHANGELOG.md).
