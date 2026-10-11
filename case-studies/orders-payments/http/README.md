# Orders and payments over HTTP

This tutorial adds a long-lived HTTP boundary to the accepted PostgreSQL
orders-and-payments case. It keeps the same order rules, payment and refund
identities, short PostgreSQL transactions, provider record fingerprints, outbox
facts, inbox deduplication, and eleven-field snapshot. The HTTP layer translates
requests and responses; it does not own another copy of the payment workflow.
The accepted PostgreSQL source/evidence baseline remains
`d1594cd230a03bcad6edbb2b590cbcb3bbcbc5f94604cdc4fbb0af59596bd7ac`.

The normative wire and runtime contract is [SPEC.md](SPEC.md). The accepted
database behavior is in the [PostgreSQL tutorial](../postgres/README.md) and
[PostgreSQL contract](../postgres/SPEC.md). This page walks through how the HTTP
request becomes one of those existing operations, how clients interpret the
result, and what to do when a response disappears.

> **Evidence boundary.** The HTTP contract specifies behavior but does not prove
> execution or recovery. See the [run](../../../research/http-run.md),
> [validation](../../../research/http-validation.md), [integration receipt](../../../research/http-integration-evidence.json), and
> [separate AI-agent review](../../../research/http-review.md) for results, and the
> [source ledger](../../../research/http-sources.md) for dependency facts.
> [Regression](../../../research/http-regression.log) and
> [PostgreSQL observations](../../../research/http-postgres-regression-evidence.json)
> remain separate from the accepted PostgreSQL baseline.

## Carry the method across a request boundary

ROO (Relationship & Ownership Oriented design) is a language-independent method.
Here it asks how the same scenario and invariants hold when a caller can lose a
response. Keep the seven relationship fields and decide which identity the next
request must reuse, who can perform a
transition, and which committed facts survive that loss. Java and Rust realize
the local request handling; the accepted PostgreSQL adapters realize persistence
and serialization. HTTP adds representation, addressing, and response semantics.
The recorded evidence below supports specific local schedules; it does not turn
the simulator's provider or deployment assumptions into production guarantees.

The handler has custody of request and response bytes. Domain/application code
retains responsibility for order transitions, and PostgreSQL retains committed
facts. The path's `scope` addresses one synthetic persistent scenario whose
domain `OrderId` remains `O1`; its line rows retain the dependent
`(scope, line_no)` key. A route or row key introduces neither an independent
domain line identity nor caller authorization. This case's scope validation is
input validation, not an authentication or tenant-isolation mechanism.

## The request still enters the same domain protocol

The listener accepts one request, validates its path, headers, body size, UTF-8,
JSON shape, field names, field types, and typed identifiers, then creates the
existing `Action`. Only after that boundary does it invoke the accepted
application and PostgreSQL adapters. A bad body is rejected before a database
operation is admitted.

For payment and refund, a successful prepare transaction persists the intent
before the provider adapter runs. The provider simulator commits its record on
an independent connection. The final application transaction reloads and
revalidates the same intent before writing terminal state and its outbox fact
together. The handler then obtains one consistent snapshot and serializes it.

```mermaid
sequenceDiagram
    autonumber
    participant C as HTTP client
    participant H as HTTP adapter
    participant A as Existing application
    participant D as roo_app
    participant P as roo_provider
    participant O as outbox / inbox

    C->>H: POST resource + JSON
    H->>H: Validate route, headers, bytes, JSON, IDs
    H->>A: One immutable validated Action
    A->>D: Prepare: lock and reload order; persist intent
    D-->>A: Commit; release order-row lock
    A->>P: Independent provider transaction, same full fingerprint
    P-->>A: Retained result or explicit Unknown / NotFound
    A->>D: Finalize: lock, reload, revalidate
    D->>D: Commit terminal state + outbox fact
    A-->>H: Closed domain result
    H->>D: Read one consistent snapshot
    H-->>C: JSON status + snapshot
```

The diagram shows the ordinary payment/refund path. A line add is one local
application transaction and has no provider phase. Reconciliation reads the
persisted intent and asks the provider simulator for its retained record.
Relay commits a consumer inbox fact on its own connection before acknowledging
the outbox in the application transaction. The relay order-row lock intentionally
spans that small local inbox transaction in this simulator; provider calls never
run while holding that application lock.

## Run the local case

From the repository root, the shared HTTP qualification command is:

```sh
bash case-studies/orders-payments/http/verify.sh
```

It is the reproducible entry point for the Java composition server, Java
Template Method server, and Rust server. It owns the marked synthetic loopback
PostgreSQL lifecycle, schema setup, builds, real HTTP requests, receipts, and
cleanup. The final local qualification on 2026-10-11 passed across all three
variants; its observed coverage is summarized under
[Reading the evidence](#reading-the-evidence). On a cold dependency cache, the
script fetches the pinned Java and Rust dependencies from their public package
sources; the source ledger records versions and integrity values.

To requalify the earlier in-memory, PostgreSQL, and ROO cases after the HTTP
addition, run the separate historical regression command:

```sh
bash case-studies/orders-payments/http/regression.sh
```

It writes new HTTP-scoped regression receipts and preserves the earlier
PostgreSQL evidence files.

For a manual server session, start only the marked synthetic cluster and apply
its shared schema from the repository root:

```sh
python3 case-studies/orders-payments/postgres/cluster.py start
python3 case-studies/orders-payments/postgres/cluster.py schema
```

Export the explicit loopback settings in the same shell. The cluster chooses
its PostgreSQL port and records it in `postgres/.runtime/config.json`; read that
JSON value with Python instead of treating `cluster.py env` output as shell
syntax:

```sh
export ROO_PG_HOST=127.0.0.1
export ROO_PG_PORT="$(python3 -c 'import json; from pathlib import Path; print(json.loads(Path("case-studies/orders-payments/postgres/.runtime/config.json").read_text())["port"])')"
export ROO_PG_DATABASE=roo_test
export ROO_PG_USER=roo_test
export ROO_HTTP_HOST=127.0.0.1
export ROO_HTTP_PORT=8080
```

The [PostgreSQL tutorial](../postgres/README.md) describes this owned cluster
and its schema. Do not point the manual server at a personal, shared, staging,
or production database.

The two Java entrypoints can be selected with
[`java/run.sh`](java/run.sh):

```sh
bash case-studies/orders-payments/http/java/build.sh
```

After building and starting the dedicated PostgreSQL cluster above, start one
variant in the foreground using the same exported environment:

```sh
bash case-studies/orders-payments/http/java/run.sh composition
# Press Ctrl-C to stop it before starting another variant.
bash case-studies/orders-payments/http/java/run.sh template
```

Press Ctrl-C before switching from the Java server to Rust. Port `0` asks the
operating system for a free HTTP port; the server prints the bound port as one
JSON readiness line after the listener binds. Server startup neither installs
nor resets the PostgreSQL schema.

The Rust HTTP binary is named `roo-http` and is built from
[`rust/Cargo.toml`](rust/Cargo.toml). After the shared verifier has prepared the
local dependencies and build, and the dedicated PostgreSQL cluster is running,
it can be started in the same shell with the exported `ROO_PG_*` and
`ROO_HTTP_*` configuration:

```sh
cargo run --locked --offline \
  --manifest-path case-studies/orders-payments/http/rust/Cargo.toml \
  --bin roo-http
```

Press Ctrl-C to stop the active server. After every server process has stopped,
stop the owned synthetic PostgreSQL cluster:

```sh
python3 case-studies/orders-payments/postgres/cluster.py stop
```

The Java and Rust listeners reject any host other than `127.0.0.1` before they
bind. Both require a port in `0..65535`. The database settings remain the
accepted structured loopback settings; neither server reads an ambient DSN or
connects to an arbitrary existing service. Configuration is captured at
startup and does not change between requests.

## Start with a scope and a line

The scope is the durable identity for one synthetic order. Initialize it with
`PUT`; this creates a Draft if it is absent and reads the existing state if it
is already present. Repeating the request does not reset the scope.

```sh
BASE=http://127.0.0.1:8080

curl -i -X PUT "$BASE/v1/scopes/demo" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  --data '{}'
```

The response is a JSON snapshot. Its fields are the same eleven fields as the
accepted TSV oracle, and every field value is a string:

```json
{
  "snapshot": {
    "scenario": "demo",
    "state": "Draft",
    "total": "0",
    "charge_count": "0",
    "refund_count": "0",
    "event_count": "0",
    "consumer_count": "0",
    "pending_outbox": "0",
    "last_result": "-",
    "payment_id": "-",
    "refund_id": "-"
  }
}
```

Add one line with a resource-shaped request:

```sh
curl -i -X POST "$BASE/v1/scopes/demo/lines" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  --data '{"unit_minor":"125","quantity":"2"}'
```

Money is integer minor units. The JSON values are decimal strings, not JSON
numbers, so no floating-point conversion is involved. This example adds 250
minor units to the order total. The domain retains the accepted checked signed
integer arithmetic and line validation.

Read the current committed snapshot at any time:

```sh
curl -i "$BASE/v1/scopes/demo" -H 'Accept: application/json'
```

`GET` is observational. It does not create a scope or change `last_result`.
A missing, well-formed scope produces `404 ScopeNotFound`; a client must first
initialize it with `PUT`.

## Prepare a payment and refund

Payment and refund requests name their natural operation identities. The
server derives the order ID, currency, and amount from the frozen persisted
order. A client cannot change the order, currency, parent payment, or amount in
the HTTP body.

```sh
curl -i -X POST "$BASE/v1/scopes/demo/payments" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -H 'Idempotency-Key: pay1' \
  --data '{"payment_id":"pay1"}'
```

The optional `Idempotency-Key` header is an exact alias for the body identity.
The body field remains required. If present, the single header value must be the
same ASCII identity token. A mismatch, duplicate value, or header on another
route is `400 InvalidRequest`.

After the payment is approved, request the full refund with its own identity:

```sh
curl -i -X POST "$BASE/v1/scopes/demo/refunds" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -H 'Idempotency-Key: refund1' \
  --data '{"refund_id":"refund1"}'
```

The refund is bound to the stored approved payment and its full amount. The
parent `PaymentId` is retained in the persisted refund intent; the caller does
not supply or override it. Payment IDs and refund IDs occupy separate typed
domain namespaces even though both arrive as JSON strings.

On a scope with an active unresolved payment or refund, reconciliation asks the
existing application to resolve its persisted intent. Relay delivers retained
outbox facts to the independent inbox:

```sh
# Relay may be called for a terminal scope with pending outbox facts.
curl -i -X POST "$BASE/v1/scopes/demo/relay" \
  -H 'Content-Type: application/json' --data '{}'
```

These endpoints expose specific operations. There is no HTTP endpoint that
accepts an arbitrary fixture script or SQL statement.

## Routes and method rules

The route set is intentionally small and exact. Paths are case-sensitive.

| Method and path | Ordinary JSON body | Behavior |
|---|---|---|
| `PUT /v1/scopes/{scope}` | `{}` | Create if absent; otherwise return current state without reset |
| `GET /v1/scopes/{scope}` | no body | Return one consistent snapshot |
| `POST /v1/scopes/{scope}/lines` | `unit_minor`, `quantity` | Append one line in Draft |
| `POST /v1/scopes/{scope}/payments` | `payment_id` | Prepare or retry the stored payment intent |
| `POST /v1/scopes/{scope}/refunds` | `refund_id` | Prepare or retry the stored refund intent |
| `POST /v1/scopes/{scope}/reconciliation` | `{}` | Look up and finalize the active stored intent |
| `POST /v1/scopes/{scope}/relay` | `{}` | Deliver pending outbox facts |

Scope names use `[A-Za-z0-9_]{1,96}`. Payment and refund identities use
`[A-Za-z0-9]{1,64}`. Encoded path segments, query strings, fragments,
malformed scopes, extra or trailing path segments, and empty-body substitutions
are rejected. A known path used with the wrong method returns `405
MethodNotAllowed` and an `Allow` header. An unknown well-formed path returns `404
RouteNotFound`.

`PUT` returns `200` both when it creates a scope and when it reads one that
already exists. `POST`, including reconciliation and relay, does not create a
scope. The scope lookup happens before the action is run, so a missing scope is
not confused with an application result.

## JSON validation and bounded requests

Every request with a body needs `Content-Type: application/json`; the optional
`charset=utf-8` parameter is case-insensitive and permits whitespace around
`=` (for example, `charset = UTF-8`). The body cap is 8192 bytes including
whitespace and is enforced on streamed request bytes, including when the client
omits `Content-Length` or uses chunked transfer.

The body must be strict UTF-8 containing exactly one JSON object. Property names
must be unique. Unknown fields, non-string values, missing required fields,
trailing JSON, invalid enum values, arrays, scalars, `null`, and an empty body
are rejected as `400 InvalidRequest` before SQL. For a no-field request, send
`{}`; an empty body is not another spelling of an empty object. `GET` accepts no
body.

`Accept` may be absent, `application/json`, or `*/*`. This educational contract
does not implement weighted media ranges. Multiple `Content-Type`, `Accept`,
`Idempotency-Key`, or synthetic control header values are rejected. Normal
responses carry `Content-Type: application/json`, `Cache-Control: no-store`,
and `Connection: close`; clients should make a fresh HTTP connection for each
request.

The parser limits and body cap protect the contract's input shape. They do not
establish header-count limits or a slow-client defense. Native HTTP parser
rejections for malformed wire framing and header syntax are outside the
cross-language JSON parity contract.

Decimal text follows `[+-]?[0-9]+` and is limited to 128 ASCII characters.
Malformed spelling or overlong text is `400 InvalidRequest`. Syntactically
valid values outside the signed 64-bit range reach the domain and produce
`422 Overflow`; valid zero or negative line amounts and quantities produce
`422 InvalidLine`. Checked multiplication and total addition remain in the
existing domain and adapter path.

## Status codes are part of the recovery contract

An HTTP status groups an application result; it does not replace the result
name in `snapshot.last_result`.

| Status | Domain result or transport error |
|---:|---|
| `200` | `Added`, `Approved`, `Declined`, `AlreadyApplied`, `AlreadyDeclined`, `RelayOk`; also successful `GET` and `PUT` snapshots |
| `202` | Provider observation `Unknown` or provider `NotFound` |
| `400` | `InvalidRequest` |
| `404` | Unknown route (`RouteNotFound`) or absent well-formed scope (`ScopeNotFound`) |
| `405` | `MethodNotAllowed`, with `Allow` |
| `406` | `NotAcceptable` |
| `413` | `BodyTooLarge` |
| `415` | `UnsupportedMediaType` |
| `409` | `InvalidState`, `IntentConflict`, `KeyConflict` |
| `422` | `InvalidLine`, `Overflow`, `InvalidOrder` |
| `500` | Unexpected internal error (`InternalError`) |
| `503` | `LocalPrepareFailed`, `LocalCommitFailed`, `RelaySendFailed`, `RelayAckFailed`, `DatabaseUnavailable`, or bounded admission (`Busy`) |

`Declined` is a completed terminal observation and returns `200`. `202` means
the provider outcome remains unresolved; it does not promise that a background
worker will act later. The caller can explicitly read, retry with the same
identity, or reconcile.

Provider `NotFound` is a domain observation: the lookup found no provider record
and the persisted intent remains pending. It is not HTTP `404`. HTTP
`ScopeNotFound` says the local order row does not exist. Keeping these meanings
separate helps clients choose between recovery and initialization.

Non-domain errors use a bounded JSON envelope, for example:

```json
{"error":{"code":"ScopeNotFound","message":"Scope not found"}}
```

Error bodies do not contain exception text, SQL, credentials, DSNs, stack
traces, or submitted request values. A database failure returns a generic
`503 DatabaseUnavailable` without inventing a domain result or snapshot.

## Natural-key retries and lost responses

There is no generic response cache. The stable retry behavior belongs to the
existing payment/refund identities and provider records. The provider stores a
complete request fingerprint and returns a result only when the request matches
the stored record.

| Operation | Stable identity or fingerprint |
|---|---|
| Payment | `(scope, payment kind, PaymentId, O1, USD, amount)` |
| Refund | `(scope, refund kind, RefundId, PaymentId, O1, USD, amount)` |
| Relay delivery | `(scope, EventId)` plus the full copied event fingerprint |
| Line addition | No durable command identity in this extension |

The immutable order intent records the operation identity and derived facts
before the provider call. A retry of a matching payment or refund can finish a
pending operation or return a terminal no-op. A new identity while another
intent is active conflicts. The provider compares the full retained request, so
reusing an operation key with a changed order, currency, amount, kind, or refund
parent is a conflict. Synthetic provider modes and failure controls are
observations; they do not alter the fingerprint.

A retry need not return the same HTTP bytes or the same domain outcome as the
first call. For example, a timeout-after-effect can first return `202 Unknown`
and a later request with the same identity can observe the retained approval.
`Cache-Control: no-store` makes the snapshot's observation-only role explicit.

When a payment or refund response is missing, a timeout occurs, or the server
returns `503`, first read the scope. Then use the same operation identity to
continue or reconcile the persisted intent. Do not generate a replacement key.
The call may have committed even if the client received no headers or body.

| Operation after uncertain response | Safe next step |
|---|---|
| Payment or refund | `GET` the scope, then retry the same natural ID or explicitly reconcile the persisted intent |
| Relay | Retry; the inbox checks the complete event fingerprint and deduplicates the same `EventId` |
| `PUT` initialization | Retry; it reads an existing scope and never resets it |
| Reconciliation | Read state and retry if needed; it may return `InvalidState` after another request has already finalized |
| Line `POST` | Read the committed snapshot and decide as a caller; do not automatically replay |

For example, in a fresh scope, a test-mode `timeout_after` payment simulates a
provider effect that committed while the app still reports `Unknown`. Start the
server with `ROO_HTTP_TEST_MODE=1` before trying this sequence; test mode cannot
be enabled for an already running process.

```sh
curl -i -X PUT "$BASE/v1/scopes/recovery1" \
  -H 'Content-Type: application/json' --data '{}'
curl -i -X POST "$BASE/v1/scopes/recovery1/lines" \
  -H 'Content-Type: application/json' --data '{"unit_minor":"250","quantity":"1"}'
curl -i -X POST "$BASE/v1/scopes/recovery1/payments" \
  -H 'Content-Type: application/json' \
  --data '{"payment_id":"p2","mode":"timeout_after"}'
curl -i "$BASE/v1/scopes/recovery1"
curl -i -X POST "$BASE/v1/scopes/recovery1/reconciliation" \
  -H 'Content-Type: application/json' --data '{}'
```

The payment step returns `202 Unknown` with a persisted `Pending` intent. The
last request looks up that intent's existing provider key and completes local
finalization; it does not create another provider effect. A repeat of the
example should use a new scope because `PUT` deliberately preserves existing
state.

Line addition is deliberately not replay-safe. The same successful request
twice appends two lines. There is no durable add-command ID or receipt, so a
lost response cannot be correlated to one particular add under concurrent
writes. The returned total is not a command receipt. An exactly-once add would
need the line, complete command fingerprint, and receipt to commit atomically
inside the adapter transaction. Wrapping the existing self-owned add
transaction in another transaction does not create that property, and this
extension adds no receipt table or schema migration.

## PostgreSQL remains the serialization authority

The HTTP process owns immutable parsed request values and one application call.
It does not hold a mutable order object or a database cursor between requests.
The existing adapters open and close a connection for each short transaction.
Every app writer locks and reloads the scope's `roo_app.orders` row with
`SELECT ... FOR UPDATE`; that row lock serializes add, payment/refund intent,
finalization, and relay work across HTTP workers and server processes.

The lock is released by commit or rollback. The provider transaction happens
after payment/refund preparation commits and runs on a separate connection. A
provider result may survive a later application failure. Finalization locks and
reloads the order again, checks the same immutable intent, then commits terminal
state with its outbox event in one application transaction.

The retained provider result and consumer inbox entry live in separate schemas
and transactions from application state. All three authorities use the same
local PostgreSQL instance and WAL durability domain in this exercise. They model
independent commit boundaries; they are not different database servers or an
external payment network.

The handler's `snapshot` is read from a single consistent database snapshot.
It includes order facts, retained effects, outbox events, inbox entries, and
pending-delivery counts. Under concurrency, an action's `last_result` reports
that action's own decision while its following snapshot may include another
worker's later commit. It is not an atomic command receipt.

Both Java entrypoints and the Rust server bound database-bearing work to 16
concurrent requests. Java's `HttpServer` also uses a separately bounded pool of
32 workers and a queue capped at 64 requests; the admission gate still limits
database work to 16. Rust holds one of 16 admission permits through a
`spawn_blocking` PostgreSQL call, keeping the synchronous client off the async
reactor thread. A full admission gate returns `503 Busy`. No global application
mutex hides the row-lock schedule. Different requests can therefore contend at
PostgreSQL and the test harness can witness the actual database lock wait.

## ROO's eight-field relationship contract at the HTTP boundary

The matrix applies the eight fields from
[ROO relationship design](../../../docs/02-relationship-design.md): owner or
resource custodian, stable identity, mutation authority, access regime, validity
horizon, execution domain, and failure boundary. Memory custody, domain
responsibility, and durable database identity are named separately where they
differ.

| Relationship | Owner / custodian | Stable identity | Invariant coordinator | Authorization | Access regime | Validity horizon | Execution domain | Failure boundary |
|---|---|---|---|---|---|---|---|---|
| HTTP request → validated command | Handler owns body bytes and immutable parsed input | Scope plus typed PaymentId or RefundId where applicable | Protocol adapter validates and constructs one accepted `Action` | Not implemented; synthetic callers only | Owned input; no mutable domain alias | One request; body buffers die after response handling | One bounded HTTP worker or Tokio blocking task | Invalid syntax, duplicate fields, or bad identity reject before SQL |
| Handler task → application invocation | Composition root owns long-lived stateless adapters; request owns its invocation | Scope and the action's explicit identity | Application coordinator alone orders domain operations | Not implemented; synthetic callers only | One call using immutable input; no shared cursor or order object | Until the operation and response snapshot finish | Concurrent server workers; no global operation mutex | Domain result is distinct from infrastructure failure and a lost socket |
| Application → PostgreSQL transaction | Database adapter owns the connection; PostgreSQL owns committed rows | Scope key and operation IDs | Existing domain/application validates; adapter performs only the bounded persistence unit | Not implemented; synthetic callers only | Fresh connection, short transaction, order row lock | Through that transaction's commit or rollback | Across threads, Java/Rust processes, and concurrent sessions | Known abort may retry a short transaction; unknown commit requires inspection |
| Order → lines and state | `roo_app.orders` is the serialization row; line rows retain accepted facts | Scope plus `(scope, line_no)` | Add and transition operations in the accepted application | Not implemented; synthetic callers only | Reload under `FOR UPDATE`; no cached mutable order | Row facts remain through the synthetic scenario | PostgreSQL serializes writers across processes | Rejected add leaves line and total unchanged; add after uncertain commit is inspected |
| Order intent → provider record | Provider schema owns its independently committed record | Scope, operation kind, natural ID, and complete fingerprint | Application submits only the persisted intent; provider adapter compares every field | Not implemented; synthetic callers only | Separate provider connection and transaction, outside the app lock | Retained for scenario recovery and replay | Competing provider calls use the provider advisory lock and uniqueness rules | Same fingerprint returns retained result; changed fingerprint conflicts; timeout can be Unknown |
| Outbox event → inbox record | App owns outbox/ack; consumer schema owns copied inbox fact | Scope and EventId, with copied event fingerprint | Relay requests delivery; inbox uniqueness/deduplication controls effect | Not implemented; synthetic callers only | Consumer commit is independent; app acknowledges afterward | Inbox can outlive a failed or rolled-back acknowledgement | Multiple relay workers; app row lock serializes this simulator's relay | Redelivery is safe for the same fingerprint; conflicting content is rejected |
| Database snapshot → HTTP response | Database owns the observed rows; handler owns serialized response bytes | Scope and the snapshot's eleven named fields | `GET` observes; POST reports its result and then snapshots | Not implemented; synthetic callers only | One consistent read; response is a detached value | Fresh only as of that database observation | The next concurrent transaction may commit before the client reads bytes | Response loss says nothing about commit; caller follows operation-specific recovery |

This is the concrete ROO contract, not an abstract analogy. A Rust borrow can
keep a `Transaction` tied to its `Client` inside one process. It cannot lock an
order row against a Java connection. PostgreSQL's row lock supplies that
cross-session coordination. Java's `final` field can preserve an adapter
reference; it does not make a referenced object deeply immutable. The contract
must name the database rule and the in-memory rule separately.

## Java and Rust keep different code shapes

The HTTP adapter is intentionally thinner than either application
implementation. It maps resource paths to the accepted action grammar, invokes
the selected coordinator once, and maps the result to JSON. The original
transaction SQL and domain rules remain in the PostgreSQL case. No HTTP request
starts a command-line runner as a subprocess.

### Java: composition and final Template Method

[`HttpService.java`](java/src/roo/postgres/HttpService.java) owns listener
configuration, bounded request handling, and the call into the application.
[`HttpProtocol.java`](java/src/roo/postgres/HttpProtocol.java) parses and
validates the HTTP representation. `HttpCompositionServer` chooses the accepted
`CompositionApplication`; `HttpTemplateServer` chooses the accepted
`JdbcTemplateApplication`.

In the composition path, the application receives the existing Store,
Provider, and Database capabilities directly. In the Template Method path,
`TemplateApplication.execute()` is `final` and owns the prepare, provider, and
finalize ordering. The subclass supplies narrow adapter hooks. The final method
prevents replacing that algorithm; it does not prove that a hook obeys its
behavioral contract or make the provider transaction part of an app transaction.

Both Java entry points compile the accepted `roo.postgres` source set with the
new HTTP sources into a separate build directory. The HTTP layer uses JDK
`HttpServer` and the Jackson-core streaming parser/generator, with no JSON
databinding layer. Strict duplicate-member detection runs before the input is
translated to an `Action`. The exact jar pin and integrity value are in the
[source ledger](../../../research/http-sources.md).

### Rust: direct path dependency and blocking admission

[`rust/src/lib.rs`](rust/src/lib.rs) owns route, header, JSON, status, and
snapshot conversion. Its custom Serde map visitor rejects duplicate properties;
deserializing through `serde_json::Value` alone would overwrite them. The
server binary calls the accepted `roo_postgres_case` crate through the direct
path dependency in [`rust/Cargo.toml`](rust/Cargo.toml). It uses the public
`Database::init`, `Database::step`, `Database::snapshot`, and fixture action
parser interfaces instead of repeating the accepted persistence SQL.

Axum handles HTTP parsing and routing, while Tokio sends synchronous PostgreSQL
work to a bounded `spawn_blocking` pool. An admission permit stays with the
blocking task through completion even if a client disconnects. Rust's borrow
rules describe local access to a `Client` and transaction; they do not replace
the database lock, provider fingerprint, or recovery protocol. The HTTP crate
forbids unsafe code and retains an exact dependency lockfile.

The Java inheritance comparison asks whether a final algorithm with narrow
hooks is useful alongside composition. Rust uses direct composition because it
has no class implementation inheritance. The business contract stays the same
in both languages; syntax and local access checks differ.

## Deterministic gates and real response loss

Synthetic controls are disabled unless `ROO_HTTP_TEST_MODE=1`. The setting is
fixed at startup. The server never mutates process-global environment; start a
separate process with explicit settings for each ordinary or gated scenario.
With test mode enabled, payment/refund requests
may include the accepted `mode` and `failure` controls, reconciliation may
include `lookup` and `failure`, and relay may include `mode`. They use the
existing action enums; they do not create another scripting API. The
test-only provider conflict route checks a retained record without changing
local order state.

The HTTP boundary gate is configured before startup with
`ROO_HTTP_GATE_LOCK` and test mode. The existing database gates use their
paired `ROO_GATE_POINT` and `ROO_GATE_LOCK` settings. Each server process keeps
one immutable configuration. Do not change process environment between
requests or pass synthetic controls in headers.

The HTTP gate is placed after a POST's domain decision and consistent snapshot,
but before the handler sends its response. It is identified in PostgreSQL
activity as `http_after_snapshot`. This allows the harness to hold the
advisory lock, observe the waiting server through database lock metadata, and
SIGKILL that server while the client has received no response. Because the gate
is after the snapshot for any POST, it can witness response loss for a line add
as well as payment, refund, reconciliation, or relay. The harness then inspects
the retained database state over a new HTTP process.

The application does not kill itself or silently discard normal responses.
`X-Roo-Test-Drop-Response` is rejected with `400 InvalidRequest`; it is not an
automatic retry or a fake transport-failure switch. A gate timeout is reported
as infrastructure failure, not as evidence that the gate was released.

The database gates locate existing boundaries: inside an uncommitted prepare,
after intent commit, after provider observation, after terminal finalization,
and after consumer delivery before outbox acknowledgement. They let a controlled
test distinguish which authority already committed at each interruption.
Parent PostgreSQL gates are described in the [database contract](../postgres/SPEC.md).

## Keep failure claims at the right boundary

There are three different restart stories in this case:

| Failure event | What the next request must do | Evidence meaning |
|---|---|---|
| HTTP process is killed | The client connection ends; a fresh process reconnects from immutable startup configuration and reads persisted scope state | Application-process recovery across already committed PostgreSQL facts |
| PostgreSQL is taken through an immediate shutdown and restart while the HTTP server stays alive | In-flight DB work can fail with a generic `503`; a later request opens a fresh connection after PostgreSQL starts and WAL recovery completes | Database restart/WAL recovery plus reconnection by one long-lived API process |
| Physical power loss, device-cache failure, or external provider outage | Outside this local test's failure injection and evidence | No hardware durability or real-provider claim |

The HTTP adapters do not keep a JDBC or Rust client connection shared across
requests. Each accepted persistence operation creates its own connection for a
short unit of work, so a server that survives a PostgreSQL restart can open a
new connection after the database is ready. Requests made while PostgreSQL is
unavailable receive bounded, generic failure responses; the handler does not
reuse a stale transaction or fabricate an outcome.

An immediate PostgreSQL restart tests PostgreSQL's own crash-recovery path with
its configured durability settings and startup WAL evidence. It does not
simulate sudden physical power loss across every hardware cache. The simulator's
provider table is another schema in the same PostgreSQL durability domain, not a
remote company or payment network. These checks also do not establish
authentication, tenant isolation, PCI compliance, deployment safety, real
provider key-expiry policy, exhaustive interleavings, or production throughput.

## Reading the evidence

The HTTP case maps the original accepted scenario actions to resource requests
and compares the same eleven observations with the unchanged independent
[`expected.tsv`](../expected.tsv). The shared harness owns the three server
variants and real HTTP clients; direct coordinator calls alone would not prove
transport behavior.

The final local qualification passed on 2026-10-11. Each variant passed 42
oracle rows, 41 rejection cases, two negotiation cases, eight ordinary-mode
cases, and four startup rejections. The harness witnessed all 16 database
slots; request 17 received `503 Busy` and capacity recovered. Each variant also
completed one active-request SIGTERM drain, seven concurrency schedules, eight
SIGKILL recoveries (five durable gaps and three completed-response losses for
payment, refund, and add), and four PostgreSQL restart scopes. Across variants,
all 12 snapshots recovered while the same three HTTP processes returned
`503 DatabaseUnavailable` during downtime and reconnected afterward.

Java passed 72 pure protocol checks; Rust passed five unit tests plus formatting,
Clippy, build, and documentation checks. The run verified pinned JDBC and
Jackson hashes. All owned processes and the synthetic PostgreSQL cluster
stopped with test data retained. This proves only recorded local scenarios, not
physical-power-loss durability, external-provider behavior, or production
readiness.

Historical regression passed too: all three in-memory variants matched 42
oracle rows and 10 malformed fixtures, and the original ROO laboratory passed
17 tests. PostgreSQL passed across all three variants with 42 oracle rows, 10
malformed fixtures, three persistent guards, seven concurrency schedules, five
SIGKILL recoveries, four restart scopes, and five SQL constraint probes. New
receipts are in the [regression log](../../../research/http-regression.log) and
[PostgreSQL regression record](../../../research/http-postgres-regression-evidence.json);
the earlier accepted PostgreSQL evidence remains intact.

For exact commands, toolchain, and checks, see the dated [run](../../../research/http-run.md),
[validation](../../../research/http-validation.md), and [qualification log](../../../research/http-checks.log).
The [integration receipt](../../../research/http-integration-evidence.json) records
scenarios, statuses, counters, process IDs, and recovery schedules; the
[separate AI-agent review](../../../research/http-review.md) assesses the frozen scope.
The earlier PostgreSQL evidence remains in the [PostgreSQL tutorial](../postgres/README.md)
and its own research records. A source route or compiled server alone does not
prove transport parity or safe recovery after response loss; use the receipt to
check where the server was stopped, what the client observed, and what recovery found.

## Source map

| File | What it owns |
|---|---|
| [HTTP contract](SPEC.md) | Routes, validation, statuses, natural-key idempotency, gates, and acceptance scope |
| [HTTP Java protocol](java/src/roo/postgres/HttpProtocol.java) | Request parsing, validation, snapshot JSON, status/error mapping |
| [HTTP Java service](java/src/roo/postgres/HttpService.java) | Listener, bounded workers, database admission, routing into accepted application |
| [Java composition entrypoint](java/src/roo/postgres/HttpCompositionServer.java) | Selects the accepted composition coordinator |
| [Java Template Method entrypoint](java/src/roo/postgres/HttpTemplateServer.java) | Selects the accepted final Template Method coordinator |
| [Java launch script](java/run.sh) | Starts one persistent Java HTTP server variant |
| [Rust HTTP crate](rust/src/lib.rs) | Route and JSON boundary, duplicate-name rejection, snapshots, status mapping |
| [Rust HTTP binary](rust/src/main.rs) | Axum/Tokio listener, bounded blocking admission, shutdown, and DB calls |
| [Rust crate manifest and lockfile](rust/Cargo.toml) | Direct accepted-crate reuse and pinned HTTP dependency graph |
| [HTTP schema note](schema.sql) | Documents that HTTP uses the accepted PostgreSQL schema with no receipt-table migration |
| [Shared HTTP verifier](verify.sh) | Owns the three-variant local qualification lifecycle |
| [Historical regression runner](regression.sh) | Rechecks the original in-memory, PostgreSQL, and ROO cases with new receipts |
| [Accepted PostgreSQL Java adapters](../postgres/java/src/roo/postgres/Database.java) | Structured loopback connections, short transaction policy, database gates |
| [Accepted PostgreSQL Rust API](../postgres/rust/src/database.rs) | `Database::{init,step,snapshot}` and existing persistence protocol |
| [ROO relationship contract](../../../docs/02-relationship-design.md) | Seven-field review frame used in the matrix above |
| [Architecture boundaries](../../../docs/05-architecture.md) | Memory/resource, transaction, semantic, and deployment boundaries |
| [Cross-language guide](../../../docs/06-cross-language.md) | Java and Rust access, identity, and concurrency distinctions |
