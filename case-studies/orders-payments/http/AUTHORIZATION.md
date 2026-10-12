# Operation permissions over HTTP

A caller can observe an allowed operation, lose permission, and then send the
request. Java composition, Java Template Method, and Rust composition now make
the execution decision for each operation against current PostgreSQL policy. A detached observation
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
| Identity | Exact synthetic principal, scope, and operation strings identify one policy row. Permission tokens are separate from payment/refund identities and fingerprints. |
| Coordinator | The existing application coordinates preparation, independent provider work, and finalization. Every protected transaction checks policy before order or provider locks. |
| Authorization | Deny by default for each `(scope, principal, operation)`. The immutable request context binds one operation. Execution reads its exact current row `FOR SHARE`; revocation updates that row and waits for earlier protected transactions. |
| Access | HTTP returns detached JSON. Request values and observations expose no connection, mutable order, or reusable permit. |
| Horizon | Grants and denied tombstones survive server and database restarts. An observation can become stale immediately. Revocation does not undo committed work. |
| Execution | Policy and each local effect share a PostgreSQL transaction. Preparation, provider, and finalization remain separate transactions; no order lock spans provider work. |
| Failure | Denial returns 403. Completed effects remain durable even if a later phase or response read is denied. Recovery requires a currently permitted caller and the original operation identity. |

**Evidence:** the [shared HTTP authorization verifier](verify_authorization.py)
checks the same observable schedules in all three variants. Its oracle is
project-authored. Existing [HTTP scenarios](verify.py) retain their independent
payment oracle and legacy-mode concurrency/recovery checks.
**Open:** real authentication, roles, tenant policy,
external-provider authorization, and independent human review.

## Policy and transaction ordering

Install [schema.sql](schema.sql) after the existing PostgreSQL schema. The trusted
fixture owner administers policy through SQL; no HTTP administration endpoint is
introduced. Grant and revoke retain the same primary key:

```sql
INSERT INTO roo_authorization.operation_grants(scope, principal, operation, allowed)
VALUES ('demo', 'alice', 'pay', true)
ON CONFLICT (scope, principal, operation)
DO UPDATE SET allowed = EXCLUDED.allowed;
-- Revoke with the same statement and allowed=false; retain the row.
```

The transaction reads the exact operation policy row with `FOR SHARE` before accessing
protected order/provider state. It keeps that lock through commit or rollback.
Updating the row to revoke permission conflicts with that lock. Revoking a
different operation does not wait for this policy row lock. Missing and
false rows deny access before order lookup, including on initialization, reads,
terminal duplicates, reconciliation, relay, and the synthetic provider probe.

The relay's outer transaction retains policy and order locks through its small
independently committed inbox write. A private inbox helper inherits that active
outer protection instead of taking a second policy lock behind a waiting
revoker. It does not expose a general bypass or release the outer policy lock.

Current fixture mode reads only `operation_grants`. The old `grants` table is
preserved for older binaries; its rows confer no permissions in this version.
Applying the additive schema neither copies nor expands them. Fixture owners
must explicitly grant each desired operation. Mixed old and new binaries would
consult different policies and are outside this fixture's deployment contract.
An old operation-less observation URL also needs updating.

Java uses a request-local immutable database context, JDBC transactions, and
private adapter methods. Rust uses a cloned database configuration with an
immutable context, borrowed transaction handles, and a closed `Forbidden`
error. Both enforce the same database ordering; memory ownership alone would
not establish the caller's current permission. Adapter entrypoints also reject
a context bound to another operation before opening a connection. A context
cannot be rebound to a different scope, principal, or operation.

The [Java database adapter](../postgres/java/src/roo/postgres/Database.java)
binds an `Operation` enum in its immutable authorization record; both Java
coordinators consume that adapter. The [Rust database adapter](../postgres/rust/src/database.rs)
owns the same closed operation value in its cloned request context. Rust's
borrowed relay authority additionally ties the private inbox delivery to the
active outer transaction. Neither Java inheritance nor Rust ownership replaces
the current PostgreSQL permission decision.

## Operation boundary

| Permission token | Request | Included work |
|---|---|---|
| `read` | `GET /v1/scopes/{scope}` | Detached snapshot only |
| `init` | `PUT /v1/scopes/{scope}` | Create if absent; never reset an existing order |
| `add` | `POST /v1/scopes/{scope}/lines` | Append a line with the existing non-idempotent semantics |
| `pay` | `POST /v1/scopes/{scope}/payments` | Prepare, call the provider, finalize, or retry the retained payment key |
| `refund` | `POST /v1/scopes/{scope}/refunds` | Prepare, call the provider, finalize, or retry the retained refund key |
| `reconcile` | `POST /v1/scopes/{scope}/reconciliation` | Look up and finalize an existing Pending payment or Refunding refund |
| `relay` | `POST /v1/scopes/{scope}/relay` | Deliver retained outbox facts and acknowledge them |
| `provider_conflict` | `POST /v1/scopes/{scope}/_test/provider-conflicts` | Synthetic retained-provider fingerprint probe; test mode only |

These eight tokens form a closed set in Java, Rust, and the SQL constraint.
There are no wildcard grants or implied permissions. A `read` grant cannot
mutate an order; a `pay` grant cannot refund, reconcile, or relay.

Each operation includes the internal existence check and response snapshot for
that request. A caller with `pay` alone can receive a payment response without
`read`; a separate GET still requires `read`. All phases and constituent reads
recheck `pay`, so revoking it can deny a response after a payment effect commits.
The same rule applies to every operation. This deliberately broad snapshot is
the teaching API's operation response; it is not field-level data policy.

## Revocation across payment phases

| When revocation commits | Retained state and next decision |
|---|---|
| Before a guarded line add or payment preparation | 403; no line, intent, provider record, or event is added. |
| After preparation, before provider entry | The intent remains Pending/Refunding; provider work is denied. |
| After the provider effect, before finalization | One provider effect remains; local state stays Pending/Refunding and no terminal event is fabricated. |
| After a guarded transaction commits | Its effect remains. Later transactions and duplicates must reauthorize. |

A later caller with `reconcile` permission reconciles the same stored
payment/refund identity, even without `pay`, `refund`, or `read`. The caller may
be a different synthetic principal. Reconciliation can only look up and finalize
the stored intent; it cannot create an intent or call a new provider effect.
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
Every request requires its own operation permission; there are no roles or HTTP
policy administration routes.

| Request/result | Response |
|---|---|
| Missing principal in enabled mode | 401 `PrincipalRequired`, message `Principal required` |
| Malformed or repeated principal header | 400 `InvalidRequest` |
| Current policy denies access | 403 `Forbidden`, message `Access forbidden` |
| Permitted caller, missing order | 404 `ScopeNotFound` |
| `GET /v1/scopes/{scope}/authorization/pay` | `{"authorization":{"operation":"pay","allowed":true}}` or false; no order lookup |
| Unknown or missing operation in an enabled observation URL | 400 `InvalidRequest` |

The observation route takes any one exact permission token from the operation
table. It is available only in fixture authorization mode, accepts
GET with no body or idempotency key, and returns 405 with `Allow: GET` for other
methods. A nonexistent scope can yield a false observation. All ordinary
snapshot and error envelopes retain their existing shape and no-store policy.

`ROO_HTTP_AUTH_GATE_LOCK` enables the test witness
`http_after_authorization_observation`. It requires fixture authorization and
test mode, and an ASCII decimal key (`[0-9]+`) in the positive signed-bigint range.
A POST observes its exact operation policy without
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

The shared tests exercise each single permission against all eight request
operations. They also verify that coarse grants remain inert, a writer does not
need a separate read grant, reconciliation-only recovery retains original keys,
and revocation of an unrelated permission does not block on the active row.
The existing broad schedules explicitly seed all eight operation rows in their
test setup; this helper is not a migration rule.

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
