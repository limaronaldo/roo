# Orders and payments: HTTP contract

Status: implementation contract, 2026-10-11. This sibling extension adds a
long-lived local HTTP process to the accepted [PostgreSQL contract](../postgres/SPEC.md).
The accepted source/evidence baseline is
`d1594cd230a03bcad6edbb2b590cbcb3bbcbc5f94604cdc4fbb0af59596bd7ac`.
The original extension preserved the accepted PostgreSQL implementation. The
[current authorization extension](AUTHORIZATION.md) adds optional guarded adapter
contexts and a separate policy schema; default behavior and historical evidence
remain preserved. The original source-hash baseline identifies the earlier bytes.
For the original transport extension, intentional
root README navigation and .gitignore cache patterns are the only changes to
accepted manifest files for this extension. No server spawns a runner subprocess per request.
In that original extension, new implementation, dependencies, and checks lived beneath this directory;
new English research/evidence documents may live beneath `research/`.

## Architecture and ownership

Reuse the existing domain, transactional application, provider, inbox, and
snapshot implementations directly. Java new sources use package `roo.postgres`
and compile alongside the accepted package-private source set into a separate
HTTP build directory. Composition and the final Template Method coordinator
remain independently selectable entry points. Rust is a standalone HTTP crate
with a path dependency on `../../postgres/rust` from `http/rust/Cargo.toml` and calls its public
`database::Database::{init,step,snapshot}` and `fixture::parse_action` APIs.
HTTP DTOs never mutate domain state or reproduce payment orchestration.

Use standard JDK `HttpServer` (`jdk.httpserver`) with Jackson-core
`com.fasterxml.jackson.core:jackson-core:2.22.3` only (no databind/annotations),
SHA-256 `8a501126a385b25841915d839508f8a66e2a0dbc8a6709d055ef3b3e852b094c`.
Enable `StreamReadFeature.STRICT_DUPLICATE_DETECTION` and bounded stream-read
constraints. Rust pins Axum `=0.8.9`, Tokio `=1.53.2`, serde_json `=1.0.154`,
and serde `=1.0.229` (hand-written visitor, no derive feature needed);
retain the complete lockfile. Use a custom serde map visitor that rejects
repeated keys: deserializing to `serde_json::Value` alone silently overwrites
duplicates and does not meet this contract. Do not hand-write HTTP framing,
request-line/header parsing, chunk decoding, or JSON parsing. Record exact
dependency versions, integrity checks and Rust lockfile in the build evidence.
Source availability and compilation are distinct from executed acceptance.

Each request owns its immutable validated input and application invocation.
Connections are created/closed by the existing adapters per short transaction;
no connection, live transaction, mutable order, or cursor is shared between
request handlers. Sharing immutable configuration and stateless adapters is
allowed. Java uses a bounded worker executor; Rust executes synchronous
PostgreSQL work on bounded blocking workers rather than an async reactor thread.
At most 16 database-bearing requests execute concurrently; excess admitted work
must be bounded or rejected with `503 Busy`. Never hold a global application
mutex through an operation: database row locks must remain the serialization
authority and allow the common lock-witness schedules to run.

Provider transactions remain independent, with no app lock spanning provider
calls. The inherited relay deliberately retains its app lock during its small
local inbox transaction. Accepted transaction timeouts and known-abort retry
limits remain unchanged. HTTP must never replay an entire failed command.

## Listener and configuration

Require explicit `ROO_HTTP_HOST=127.0.0.1` and `ROO_HTTP_PORT` in `0..65535`;
port zero asks the OS to choose a free port. Print one bounded JSON readiness
line to stdout only after a successful bind:
`{"host":"127.0.0.1","port":12345,"ready":true}`.
Diagnostics go to stderr. Reject any other host before creating a listener or
database connection. Preserve the accepted explicit `ROO_PG_*` restrictions;
do not consume a URL, ambient DSN, or an existing service. No schema installation
or reset occurs at server startup. The root harness owns cluster/schema lifecycle.

`ROO_HTTP_TEST_MODE` is absent or exactly `1`; other supplied values reject
startup. With `1`, the synthetic controls below are enabled. Supplying a gate
configuration without test mode rejects startup. The existing
paired `ROO_GATE_POINT`/`ROO_GATE_LOCK` and worker identity are server-process
configuration, never request-supplied environment overrides. Construct a fresh
server with the chosen gate for a witnessed schedule; an ordinary server seeds,
reads, and supplies competing HTTP requests to the same scopes. Do not mutate
process-global environment, including during startup: Rust edition 2024 treats
environment mutation as unsafe, and the accepted Database exposes only
`from_env()` construction. Each process uses exactly its immutable startup
configuration. Graceful termination closes the listener and drains
bounded in-flight work; SIGKILL testing intentionally bypasses that path.

## Routes and JSON

All paths are exact, case-sensitive ASCII paths; their raw character grammar
is `[A-Za-z0-9_/-]+` with a leading slash. Other punctuation rejects with 400
before route dispatch. Scope is `[A-Za-z0-9_]{1,96}`;
payment/refund IDs are `[A-Za-z0-9]{1,64}`. Reject encoded path segments, query
strings, fragments, extra/trailing slash segments, or a malformed scope with
`400 InvalidRequest` before SQL. An unknown well-formed route is `404 RouteNotFound`;
a known route with another method is `405 MethodNotAllowed` with `Allow`.

| Method and path | Exact ordinary body | Meaning |
|---|---|---|
| `PUT /v1/scopes/{scope}` | `{}` | Initialize if absent; return existing state otherwise, never reset |
| `GET /v1/scopes/{scope}` | no body | Read one consistent snapshot |
| `POST /v1/scopes/{scope}/lines` | `{"unit_minor":"100","quantity":"2"}` | Add one line, explicitly non-idempotent |
| `POST /v1/scopes/{scope}/payments` | `{"payment_id":"p1"}` | Prepare/retry the stored full payment intent |
| `POST /v1/scopes/{scope}/refunds` | `{"refund_id":"r1"}` | Prepare/retry the stored full refund intent |
| `POST /v1/scopes/{scope}/reconciliation` | `{}` | Look up and finalize the active persisted intent |
| `POST /v1/scopes/{scope}/relay` | `{}` | Deliver pending outbox facts to the independent inbox |

PUT returns `200` for both creation and existing state. POST does not create a
missing scope; GET or POST on a missing scope returns `404 ScopeNotFound`.
Default actions are `pay:<id>:approve:none`, `refund:<id>:approve:none`,
`reconcile:ok:none`, and `relay:ok`. Order ID and currency are fixed `O1`/`USD`,
and payment/refund amounts derive from the persisted frozen order. Clients
cannot submit or override those fields. There is no generic script/action API.

Requests with a body require `Content-Type: application/json` (optional
`charset=utf-8`, allowing whitespace around the charset `=` and case-insensitive
media-type matching); unsupported media types
return `415 UnsupportedMediaType`. Bodies are at most 8192 bytes including
whitespace. Enforce the actual streamed byte limit even without Content-Length;
oversize returns `413 BodyTooLarge`. Validate UTF-8 strictly, one JSON object,
no duplicate properties, no unknown properties, no trailing JSON, and string
values for every nonempty field. Empty body differs from `{}`. Malformed JSON,
null/array/scalar, missing fields, invalid types, and invalid enums return
`400 InvalidRequest` before SQL. GET rejects a nonempty body.

`Accept` may be absent, `application/json`, or `*/*` (surrounding optional
whitespace allowed); other values return `406 NotAcceptable`. This deliberately
small educational negotiation contract does not implement weighted media ranges.
Reject multiple Content-Type, Accept, Idempotency-Key, or synthetic control
header values with 400. Responses include `Connection: close`; do not depend on
persistent connections. Application-level validation errors obey the JSON error
contract; native HTTP parser rejections for invalid framing/header syntax are
outside cross-stack JSON parity. No header-count/slow-client hardening claim is
implied by a body cap.

Money and quantity are decimal **strings**, never JSON numbers or floating
point. The grammar is `[+-]?[0-9]+`, with at most 128 ASCII characters total;
it deliberately preserves the accepted signed integer parser. A syntactically
valid out-of-range value reaches domain `Overflow`; zero/negative in-range
values reach `InvalidLine`; checked multiplication/sum preserve the prior order.
Malformed or excessively long integer text is `400 InvalidRequest`.

Every completed domain decision returns `Content-Type: application/json` and
`Cache-Control: no-store`, with this envelope:

```json
{"snapshot":{"scenario":"demo","state":"Paid","total":"250","charge_count":"1","refund_count":"0","event_count":"1","consumer_count":"0","pending_outbox":"1","last_result":"Approved","payment_id":"p1","refund_id":"-"}}
```

Exactly the original eleven snapshot keys appear, all with JSON string values.
The original `-` missing-ID/diagnostic sentinels are retained. PUT/GET use
`last_result="-"`; POST uses its original closed outcome vocabulary. Conversion
to the oracle is the original ordered eleven fields joined by tabs, with the
fixture label substituted for `scenario` only by the harness. JSON member order
is immaterial. Responses do not depend on language/variant. A completed action's
snapshot can include another worker's subsequent commit; it is not an atomic
command receipt, and `last_result` describes that action's own decision.

| Domain result | HTTP status |
|---|---|
| Added, Approved, Declined, AlreadyApplied, AlreadyDeclined, RelayOk | 200 |
| Unknown, NotFound | 202 |
| InvalidState, IntentConflict, KeyConflict | 409 |
| InvalidLine, Overflow, InvalidOrder | 422 |
| LocalPrepareFailed, LocalCommitFailed, RelaySendFailed, RelayAckFailed | 503 |

`Declined` is a successful terminal observation, not a transport fault.
Domain `NotFound` means provider lookup found no record and leaves the intent
pending; it differs from missing-scope HTTP 404. `202` does not promise a
background worker: clients explicitly retry/reconcile. Infrastructure failures
return `503 DatabaseUnavailable`; unexpected internal errors return
`500 InternalError`. No false domain outcome or snapshot is fabricated.
All non-domain errors use `{"error":{"code":"InvalidRequest","message":"Invalid request"}}`.
The exact messages for the other codes are: RouteNotFound=`Route not found`,
MethodNotAllowed=`Method not allowed`, ScopeNotFound=`Scope not found`,
UnsupportedMediaType=`Unsupported media type`, BodyTooLarge=`Body too large`,
NotAcceptable=`Not acceptable`, DatabaseUnavailable=`Database unavailable`,
InternalError=`Internal error`, Busy=`Server busy`. Never expose
exception text, SQL, credentials, DSNs, stack traces, or raw submitted bodies.

## Idempotency and lost responses

On payment/refund routes only, an optional single `Idempotency-Key` header is
an exact alias of body `payment_id`/`refund_id`. It must be one ASCII identity
token equal to that body ID; a mismatch, duplicate header, comma-joined values,
or invalid token returns `400 InvalidRequest` before SQL. On all other routes
any Idempotency-Key is rejected with 400. This is natural-key idempotence, not a
general-purpose HTTP receipt or response cache.
Payment/refund operation IDs are explicit typed domain identities. A payment's
full fingerprint is `(scope, payment kind, PaymentId, O1, USD, amount)`; a refund's
is `(scope, refund kind, RefundId, PaymentId, O1, USD, amount)`. The immutable
persisted intent and accepted provider's complete record comparison enforce this
contract. Provider behavior/failure simulation controls are observations, not
fingerprint fields. Different keys against an existing intent conflict; matching
keys can progress Pending/Refunding or return terminal no-ops. A retry need not
return byte-identical JSON or the same outcome as the first call.

A lost HTTP response, timeout, disconnection, SIGKILL, or infrastructure 503
does not prove rollback. Payment/refund recovery uses GET, the **same** operation
identity, and explicit reconciliation of persisted state; never manufacture a
new key. Relay safely redelivers to the full-fingerprint deduplicating inbox.
PUT may be retried without resetting an existing scope. Reconcile may be retried
but can return InvalidState after another request has already finalized.

Line POST is intentionally **not replay-safe**: it has no durable command ID.
Two identical successful POSTs append two lines. After an uncertain response or
COMMIT, inspect persisted state and make a caller-controlled decision; do not
automatically retry. GET total alone is not a command receipt under concurrency.
No claim that arbitrary POSTs have exactly-once execution is made. A durable
add receipt would require an adapter transaction that commits line + full command
fingerprint + receipt atomically; wrapping the accepted self-owned add transaction
with another transaction cannot provide that guarantee. This narrow transport
scope preserves the accepted adapters without duplicating domain/SQL logic.
[schema.sql](schema.sql) adds only the opt-in fixture authorization policy; it
introduces no durable command receipt or change to line replay semantics.

## Optional operation permissions

The [authorization contract](AUTHORIZATION.md) defines fixture mode separately
from the default legacy mode. Current policy uses the exact
`(scope, principal, operation)` key in `roo_authorization.operation_grants`.
The closed tokens are `read`, `init`, `add`, `pay`, `refund`, `reconcile`, `relay`,
and `provider_conflict`. No token implies another. Old coarse grants remain
stored and are not consulted or expanded; fixture owners explicitly grant the
desired operations.

Fixture observations use `GET /v1/scopes/{scope}/authorization/{operation}` and
return `{"authorization":{"operation":"pay","allowed":true}}` (or false).
They accept no body, query, or idempotency key. Missing/unknown operation is 400
in fixture mode; the route is unavailable in legacy mode. Each request binds its
operation once. Every protected transaction, including the existence precheck
and response snapshot, reads its exact permission `FOR SHARE` before business
state. A command therefore needs its own permission but no additional `read`
permission; a separate GET always requires `read`.

Reconciliation permission permits only lookup/finalization of an existing
Pending payment or Refunding refund, using the retained full fingerprint. It
does not create provider effects and can belong to a different principal from
the original caller. Denials use 403 `Forbidden` / `Access forbidden`; a missing
asserted principal uses 401 `PrincipalRequired` / `Principal required`. A later
denial can follow an earlier committed phase and does not prove rollback.

## Synthetic controls and gates

With test mode enabled, payments/refunds additionally accept optional string
`mode` and `failure`; reconciliation accepts `lookup` and `failure`; relay accepts
`mode`. Their enums and applicable combinations exactly match the accepted action
grammar. Omitted controls use the ordinary defaults. With test mode disabled,
supplying any control rejects the request with 400 before SQL.

Only in test mode, `POST /v1/scopes/{scope}/_test/provider-conflicts` accepts
`{"payment_id":"p1","different_amount":"999"}` and invokes the unchanged
direct provider conflict probe. The amount must be a positive in-range integer
different from a retained terminal payment's amount; absent/matching records
or invalid probe preconditions reject with 400. The probe compares full retained
provider content and must not change local state. With test mode disabled this
route returns 404. It is not a checkout API.

`X-Roo-Test-Drop-Response` is unsupported: any presence returns 400 before SQL.
Use the explicitly configured HTTP boundary gate to test real response loss:
`ROO_HTTP_GATE_LOCK` is an optional positive signed-bigint decimal string,
permitted only with test mode. It selects `http_after_snapshot`, after a POST's
domain decision and consistent snapshot have completed but before the handler
returns any HTTP response. GET and PUT never enter this HTTP boundary gate.
Its worker uses the existing bounded `ROO_WORKER_ID` identity.

The wrapper may own a tiny dedicated instrumentation PostgreSQL connection,
using the accepted explicit loopback configuration and 30000ms statement/lock
timeouts. It sets application_name to `roo:<worker>:http_after_snapshot`, takes
`pg_advisory_lock(key)`, and unlocks after acquisition. This connection performs
no domain mutation and does not reproduce accepted adapter logic. The harness
holds the advisory session lock, observes this server waiting in database lock
metadata, then SIGKILLs only the gated server. The client must observe connection
loss without headers/body; the ordinary or fresh server inspects retained state.
The application never kills itself, mutates environment, or silently drops a
normal response. A gate timeout is infrastructure failure. Rust may add the
same exact `postgres = "=0.19.14"` direct dependency for this small test-only
instrumentation adapter.

Existing database gates remain unchanged: inside_prepare, after_prepare,
after_effect, after_finalize, after_delivery. They use their separate bounded
gate connection and harness-owned advisory session lock. For response-loss tests,
after_finalize is especially useful: retained terminal state and outbox exist
while the HTTP client has not received a response. Gate failure is an
infrastructure failure and is never treated as successful release.

## Common executable acceptance

One shared Python standard-library HTTP harness drives Java composition, Java
Template Method, and Rust composition against the root-owned marked synthetic
loopback PostgreSQL cluster. It starts persistent server processes, sends real
HTTP requests, and retains bounded receipts; it never substitutes CLI calls for
the observed HTTP action. Existing cluster utilities may be reused unchanged.
Run builds, dependency installation, SQL setup, and tests serially against the isolated fixture.

Required checks, with exact results recorded only after execution:

1. Translate all 42 original scenarios to the resource routes, including enabled
   synthetic controls/provider probe, and compare all original eleven fields
   against the unchanged independent expected TSV in all three variants.
2. Exercise malformed UTF-8/JSON, duplicate and unknown fields, bad IDs, wrong
   types, oversized body, bad media type, method/route/missing-scope distinctions,
   overflow/negative/zero boundaries, disabled controls/probe, rejected drop header, and
   accepted matching Idempotency-Key and rejected mismatched/duplicate/unsupported
   keys. Verify no state mutation for rejected input.
3. Concurrent different payment/refund identities and same-key duplicates;
   add-before-pay and pay-before-add; duplicate relay. Witness inherited database
   row/advisory lock waits rather than infer order from elapsed time. Verify no
   shared-connection corruption and no global mutex hides the database schedule.
4. Kill a server at the inherited committed-intent, provider-effect,
   terminal-event, and inbox-before-ack gaps. Use a fresh server and real HTTP to
   inspect/reconcile/retry/redeliver; counts and identities remain stable.
5. Drop a completed payment/refund HTTP response, then retry the same identity
   through HTTP and verify one effect/event. Drop an add response, inspect the
   committed line effect, and demonstrate that a deliberate identical second POST
   adds again; the client harness must not blindly replay it.
6. Prepare durable Pending/Refunding/ack-gap/completed scopes through HTTP,
   perform root-owned dedicated PostgreSQL immediate shutdown/restart, compare
   snapshots over HTTP, and recover through HTTP. A long-lived server must handle
   unavailable connections with bounded generic 503 and recover on later requests;
   record fresh-process recovery separately from surviving-server reconnection.
7. Start all listeners explicitly on loopback, reject other hosts before bind,
   retain process cleanup on every failure, and preserve the accepted source hash
   manifest. Run appropriate new checks and the accepted regressions serially.

No HTTP check is marked passed by this specification. Record compiler, dependency,
transport, concurrency, process recovery and PostgreSQL WAL-recovery evidence
separately. The simulator shares one database/WAL domain across independent
schemas/connections. This local educational service claims no real payment
network, real authentication/tenant boundary, production deployment, exhaustive
interleavings, hardware power-loss survival, or operational throughput.
