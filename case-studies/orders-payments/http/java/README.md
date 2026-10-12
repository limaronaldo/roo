# Java HTTP adapters

ROO — Relationship & Ownership Oriented design is a language-independent
method for tracing request relationships and failure boundaries before
choosing Java and HTTP mechanisms.

Start with a payment or refund POST whose response is lost: persisted intent
and the same operation identity allow recovery, while line POST has no durable
receipt and must be inspected before a caller chooses another attempt. The
[HTTP contract](../SPEC.md), [PostgreSQL tutorial](../../postgres/README.md), and
[original case](../../README.md) define the behavior. Chapter 2's [contract](../../../../docs/02-relationship-design.md#21-the-eight-field-relationship-contract)
and [worksheet](../../../../templates/relationship-contract.md) help separate
request custody, durable scope and operation identity, invariant coordination,
caller authorization, access, horizon, execution,
and failure before choosing HTTP and Java mechanisms. IDs do not authorize
callers; this service models no caller authentication or authorization.

These two entrypoints compile the unchanged PostgreSQL domain, store, provider,
and coordinators alongside new same-package HTTP adapters:

* `roo.postgres.HttpCompositionServer`: composition coordinator.
* `roo.postgres.HttpTemplateServer`: final Template Method coordinator.

Dependencies are JDK 26 targeting Java 21, standard module `jdk.httpserver`,
pgJDBC `42.7.14` at `../../postgres/.deps/postgresql-42.7.14.jar`, and Jackson-core
`2.22.3` at `../.deps/jackson-core-2.22.3.jar`. No databind, annotations, framework,
dependency download or schema reset is used by these scripts.
Expected artifact SHA-256 values are:

```text
postgresql-42.7.14.jar 73914527305a40cce504b0d3d90b23caf565136912d607ae8ae7c5895512332c
jackson-core-2.22.3.jar 8a501126a385b25841915d839508f8a66e2a0dbc8a6709d055ef3b3e852b094c
```

From this directory, with the verified dependencies already present:

```sh
bash build.sh
ROO_HTTP_HOST=127.0.0.1 ROO_HTTP_PORT=0 \
ROO_PG_HOST=127.0.0.1 ROO_PG_PORT=55432 ROO_PG_DATABASE=roo_test ROO_PG_USER=roo_test \
bash run.sh composition
```

The dedicated synthetic PostgreSQL database and accepted schema must already
exist, installed by the root harness. Replace the example port with that harness's
port. Use `bash run.sh template` for the other coordinator. Startup prints one
JSON readiness line with the actual loopback port; sanitized diagnostics use
stderr. Explicit host configuration is validated before binding or connecting.

The [HTTP contract](../SPEC.md) defines the exact routes, request fields, status
mapping, eleven string snapshot fields, and recovery protocol. Input is immutable
and validated before SQL. Jackson rejects duplicate properties and trailing JSON;
strict UTF-8 decoding and an actual streamed 8192-byte cap precede parsing. Up to
16 database-bearing requests run concurrently, with 32 HTTP worker threads and
a bounded 64-task executor queue. The additional HTTP workers can reject excess
database-bearing requests with JSON `503 Busy` while all database slots are occupied.
When the queue fills the dispatcher handles a task under that same admission
limit. No application
mutex spans a request; the accepted database locks remain authoritative.

Test controls are absent by default. Set exactly `ROO_HTTP_TEST_MODE=1` to enable
the contracted simulation fields/probe. Existing paired `ROO_GATE_POINT` and
`ROO_GATE_LOCK`, and optional `ROO_HTTP_GATE_LOCK`, are immutable startup settings
and require test mode. The HTTP gate opens a separate bounded diagnostic
connection after a POST's action and snapshot, before any response headers. Its
application name is `roo:<ROO_WORKER_ID>:http_after_snapshot`. It performs no
domain writes. A fresh gated server and an ordinary server share the harness's
scopes without mutating process environment. SIGTERM closes the listener and
allows bounded work to drain; intentional SIGKILL bypasses graceful shutdown.

`build.sh` compiles both source directories into this extension's separate
`build/classes`, with `--release 21 -Xlint:all -Werror`, then runs pure parsing,
configuration, stream-cap, and mapping checks. The verification scripts execute all
builds and checks serially. Authored source and pure checks do not establish real
HTTP, concurrency, response-loss, or WAL-recovery acceptance; the shared root
harness and recorded receipts provide those separate evidence lanes.

Payment/refund recovery retains the same operation identity. A lost response
does not prove rollback. Line POST has no durable command receipt and must not
be blindly replayed. This is a local educational simulator, with one database/WAL
domain and no real payment network, authentication, production, or throughput claim.
