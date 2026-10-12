# Durable authorization over HTTP

A caller can observe an allowed operation, lose permission, and then send the
request. Java composition, Java Template Method, and Rust composition now make
the execution decision against current PostgreSQL policy. A detached observation
does not grant permission or reserve an execution slot.

This is an opt-in **synthetic fixture**, using `ROO_HTTP_AUTH_MODE=fixture` and
`ROO_HTTP_TEST_MODE=1`. `X-Roo-Principal: alice` asserts a synthetic principal;
it does not authenticate a person. The legacy mode remains available when the
authorization setting is absent. Neither mode is a production identity boundary.

## Relationship Contract

**Relationship:** Principal → persistent order operations.
**Invariant:** a currently permitted principal may enter a protected transaction;
a denied transaction produces no new business effect.

| Field | Decision |
|---|---|
| Custodian | PostgreSQL retains orders, policy, provider records, outbox, and inbox. Each request owns its immutable principal/scope context and short-lived adapters. |
| Identity | Exact synthetic principal and scope strings identify one policy row. Existing payment/refund identities and fingerprints remain unchanged. |
| Coordinator | The existing application coordinates preparation, independent provider work, and finalization. Every protected transaction checks policy before order or provider locks. |
| Authorization | Deny by default. One `(scope, principal)` grant covers the case's operations. Execution reads the current row `FOR SHARE`; revocation updates that row and waits for earlier protected transactions. |
| Access | HTTP returns detached JSON. Request values and observations expose no connection, mutable order, or reusable permit. |
| Horizon | Grants and denied tombstones survive server and database restarts. An observation can become stale immediately. Revocation does not undo committed work. |
| Execution | Policy and each local effect share a PostgreSQL transaction. Preparation, provider, and finalization remain separate transactions; no order lock spans provider work. |
| Failure | Denial returns 403. Completed effects remain durable even if a later phase or response read is denied. Recovery requires a currently permitted caller and the original operation identity. |

**Evidence:** the [shared HTTP authorization verifier](verify_authorization.py)
checks the same observable schedules in all three variants. Its oracle is
project-authored. Existing [HTTP scenarios](verify.py) retain their independent
payment oracle and legacy-mode concurrency/recovery checks.
**Open:** real authentication, operation-specific permissions, tenant policy,
external-provider authorization, and independent human review.

## Policy and transaction ordering

Install [schema.sql](schema.sql) after the existing PostgreSQL schema. The trusted
fixture owner administers policy through SQL; no HTTP administration endpoint is
introduced. Grant and revoke retain the same primary key:

```sql
INSERT INTO roo_authorization.grants(scope, principal, allowed)
VALUES ('demo', 'alice', true)
ON CONFLICT (scope, principal) DO UPDATE SET allowed = EXCLUDED.allowed;
-- Revoke with the same statement and allowed=false; retain the row.
```

The transaction reads the exact policy row with `FOR SHARE` before accessing
protected order/provider state. It keeps that lock through commit or rollback.
Updating the row to revoke permission conflicts with that lock. Missing and
false rows deny access before order lookup, including on initialization, reads,
terminal duplicates, reconciliation, relay, and the synthetic provider probe.

The relay's outer transaction retains policy and order locks through its small
independently committed inbox write. A private inbox helper inherits that active
outer protection instead of taking a second policy lock behind a waiting
revoker. It does not expose a general bypass or release the outer policy lock.

Java uses a request-local immutable database context, JDBC transactions, and
private adapter methods. Rust uses a cloned database configuration with an
immutable context, borrowed transaction handles, and a closed `Forbidden`
error. Both enforce the same database ordering; memory ownership alone would
not establish the caller's current permission.

## Revocation across payment phases

| When revocation commits | Retained state and next decision |
|---|---|
| Before a guarded line add or payment preparation | 403; no line, intent, provider record, or event is added. |
| After preparation, before provider entry | The intent remains Pending/Refunding; provider work is denied. |
| After the provider effect, before finalization | One provider effect remains; local state stays Pending/Refunding and no terminal event is fabricated. |
| After a guarded transaction commits | Its effect remains. Later transactions and duplicates must reauthorize. |

A later permitted caller reconciles the same stored payment/refund identity.
The retained provider fingerprint prevents a second effect, and terminal state
and its outbox fact still commit together. Regranting allows a fresh policy
decision; it does not revive an old credential or observation.

The response snapshot also reauthorizes. A request can therefore return 403
after an earlier phase committed. A 403, 503, timeout, or lost response is not a
rollback receipt. Inspect and recover using current permission and the same
payment/refund key. Line additions still have no durable command identity;
never blindly replay an uncertain line POST.

## HTTP surface

Enabled mode requires one `X-Roo-Principal` matching `[A-Za-z0-9_]{1,32}`.
There is one coarse access grant per principal/scope; there are no roles or
HTTP policy administration routes.

| Request/result | Response |
|---|---|
| Missing principal in enabled mode | 401 `PrincipalRequired`, message `Principal required` |
| Malformed or repeated principal header | 400 `InvalidRequest` |
| Current policy denies access | 403 `Forbidden`, message `Access forbidden` |
| Permitted caller, missing order | 404 `ScopeNotFound` |
| `GET /v1/scopes/{scope}/authorization` | `{"authorization":{"allowed":true}}` or false; no order lookup |

The observation route is available only in fixture authorization mode, accepts
GET with no body or idempotency key, and returns 405 with `Allow: GET` for other
methods. A nonexistent scope can yield a false observation. All ordinary
snapshot and error envelopes retain their existing shape and no-store policy.

`ROO_HTTP_AUTH_GATE_LOCK` enables the test witness
`http_after_authorization_observation`. It requires fixture authorization and
test mode, and an ASCII decimal key (`[0-9]+`) in the positive signed-bigint range.
A POST observes policy without
locking it, waits at this gate, then performs a fresh protected decision.
The initial observation never rejects the command: an intervening grant can
allow execution just as an intervening revocation can deny it.

## Reproduce and inspect

Run the full reproducible qualification from the repository root:

```sh
bash case-studies/orders-payments/track/compose.sh
```

The container uses a private PostgreSQL cluster, loopback listeners, no external
network or host data mounts during tests, and synthetic policy inputs. The full
qualification includes the adoption track, legacy HTTP checks, and this
authorization extension. GitHub Actions runs it on a real AMD64 runner.

For an existing local toolchain, the HTTP entrypoint builds both languages and
runs the legacy and authorization suites serially:

```sh
bash case-studies/orders-payments/http/verify.sh
```

The shared tests use real HTTP requests and database lock witnesses to establish
revocation ordering. They test durable policy across killed/restarted API
processes and immediate PostgreSQL restart, a surviving server's generic 503
during downtime, and later reconnection/reconciliation. Timeouts bound failures;
elapsed time alone never proves which operation won.

Current receipts live in `http/.runtime/authorization-last-run.json` and
`http/.runtime/http-last-run.json`; Docker exports them under its ignored
`artifacts/roo-track/` run directory. Historical `research/` receipts retain
their original sources and results. The extension changes the adapters through
optional guarded contexts; an old source hash does not describe these new bytes.

These checks establish specified local outcomes. Policy and the simulated
provider share one PostgreSQL/WAL domain. They do not establish real identity,
an external provider's revocation contract, exhaustive interleavings, physical
power-loss durability, or production readiness.
