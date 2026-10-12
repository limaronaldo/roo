# Rust HTTP adapter

ROO — Relationship & Ownership Oriented design is a language-independent
method; this adapter shows Rust's local access rules meeting the same persistent
HTTP contract.

Begin with a lost payment or refund response: recovery reuses the persisted
operation identity, while line POST has no durable receipt and requires state
inspection before another attempt. The [HTTP contract](../SPEC.md),
[PostgreSQL tutorial](../../postgres/README.md), and [original case](../../README.md)
define the boundary. Chapter 2's [Relationship Contract](../../../../docs/02-relationship-design.md#21-the-eight-field-relationship-contract)
and [worksheet](../../../../templates/relationship-contract.md) guide decisions
about request custody, durable scope and operation identity, invariant coordination,
caller authorization, access, horizon, execution, and failure before choosing Rust
mechanisms. Rust ownership and borrows govern local
access; SQL coordinates processes. IDs are not credentials, and the service
models no caller authentication or authorization.

This standalone Rust 2024 crate serves the resource API in [the HTTP contract](../SPEC.md).
The executable is `roo-http`. It directly depends on the accepted PostgreSQL crate;
it does not spawn a runner or duplicate domain SQL. The dependency pins are Axum
0.8.9, Tokio 1.53.2, serde_json 1.0.154, serde 1.0.229, and postgres 0.19.14.
Serde uses a handwritten object visitor, without its derive feature.

From this directory, run these checks serially:

```sh
cargo test --locked
cargo build --locked
```

The root harness owns the dedicated marked synthetic PostgreSQL cluster and
installs the unchanged accepted schema before launch. Startup never installs,
resets, or connects to a database. Example launch, using that cluster's assigned
port in place of `54321`:

```sh
ROO_PG_HOST=127.0.0.1 ROO_PG_PORT=54321 ROO_PG_DATABASE=roo_test ROO_PG_USER=roo_test \
ROO_HTTP_HOST=127.0.0.1 ROO_HTTP_PORT=0 ./target/debug/roo-http
```

After binding, stdout contains a JSON readiness line with the chosen port.
Diagnostics contain bounded generic messages on stderr. Responses use JSON,
`Cache-Control: no-store`, and `Connection: close`. GET and PUT snapshots use
the original eleven string fields and `last_result="-"`.

At most sixteen database-bearing requests execute at once. Additional work
receives `503 Busy`. Each admitted request owns its action and a blocking-worker
permit until the synchronous adapter calls finish, even after client disconnect.
The existing adapters create their own short-lived connections and transactions;
there is no application mutex or shared PostgreSQL client. SIGINT/SIGTERM closes
the listener and drains handlers for up to 180 seconds. Runtime teardown allows
another bounded 180 seconds for uncancellable blocking work. SIGKILL bypasses
graceful termination.

Synthetic body controls and the provider conflict probe require immutable
`ROO_HTTP_TEST_MODE=1` at process launch. Accepted paired `ROO_GATE_POINT` and
`ROO_GATE_LOCK` settings also require this mode. Optional `ROO_HTTP_GATE_LOCK`
selects the response boundary after POST action and snapshot; GET/PUT never
enter it. This instrumentation opens a separate connection with thirty-second
statement/lock timeouts and application name
`roo:<ROO_WORKER_ID>:http_after_snapshot`. It only acquires/releases the advisory
lock. No code mutates process environment. Start a separate process for each
configuration. `X-Roo-Test-Drop-Response` is always rejected.

Pure unit tests cover duplicate/non-string JSON, numeric grammar versus domain
overflow, control and idempotency policy, route/status distinctions, header
duplicates, and the eleven-field snapshot envelope. They do not prove HTTP,
PostgreSQL concurrency, restart, or lost-response behavior. Those require the
shared real-HTTP acceptance harness and separately recorded execution receipts.

Line POST has no durable command identity and is not replay-safe. An uncertain
payment/refund response requires reading persisted state and retaining the same
operation ID. A successful action's snapshot may include another worker's later
commit. This local case study does not claim authentication, production payment
network behavior, production readiness, throughput, or exhaustive interleavings.
