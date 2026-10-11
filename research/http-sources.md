# Java/Rust HTTP extension: primary-source ledger

Checked 2026-10-11 against the accepted PostgreSQL contract and the sibling
[HTTP contract](../case-studies/orders-payments/http/SPEC.md). This is a
read-only source review; it did not download executable artifacts, build, run a
server, or query PostgreSQL. The HTTP contract is normative for the case. The
notes below distinguish library/protocol facts from application policy.

## Minimal implementation choices and provenance

| Component | Pin or API | Verified source facts |
|---|---|---|
| Java HTTP | JDK 21 `jdk.httpserver`, `com.sun.net.httpserver.HttpServer` | Java SE 21 provides a simple HTTP server with contexts/handlers, an explicit `Executor`, a configurable connection backlog, and `stop(delay)`. Bind only to the configured loopback address, set the executor before `start`, and stop/drain before shutting down its workers. The JDK labels this a platform-specific, minimal API intended for educational/testing use, which fits this local case but is not a production-edge claim. ([`HttpServer`](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.httpserver/com/sun/net/httpserver/HttpServer.html), [module overview](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.httpserver/module-summary.html), [networking overview](https://docs.oracle.com/en/java/javase/21/core/java-networking.html)) |
| Java JSON | `com.fasterxml.jackson.core:jackson-core:2.22.3` only | Maven Central metadata identifies 2.22.3 as latest and records updates through 2026-09-21. The official artifact checksum sidecar reports SHA-256 `8a501126a385b25841915d839508f8a66e2a0dbc8a6709d055ef3b3e852b094c`. Jackson-core supplies streaming parser/generator APIs; this contract's string-valued request/response fields do not require databind or annotations. Pin the artifact and verify the fetched JAR against the sidecar. ([Maven metadata](https://repo.maven.apache.org/maven2/com/fasterxml/jackson/core/jackson-core/maven-metadata.xml), [artifact checksum](https://repo.maven.apache.org/maven2/com/fasterxml/jackson/core/jackson-core/2.22.3/jackson-core-2.22.3.jar.sha256), [Jackson core project](https://github.com/FasterXML/jackson-core), [2.22.3 release notes](https://github.com/FasterXML/jackson-core/blob/3.x/release-notes/VERSION-2.x)) |
| Rust HTTP | `axum = "=0.8.9"` | The official project release and crates.io sparse-index record agree on 0.8.9; the index says non-yanked, Rust 1.80 minimum, SHA-256 `31b698c5f9a010f6573133b09e0de5408834d0c82f8d7475a89fc1867a71cd90`, published 2026-04-14. Axum provides routing/extractors and uses Hyper/Tower/Tokio, with a larger dependency surface than a synchronous micro-server. ([Axum release](https://github.com/tokio-rs/axum/releases/tag/axum-v0.8.9), [Axum project](https://github.com/tokio-rs/axum), [official crate index](https://index.crates.io/ax/um/axum)) |
| Rust runtime | `tokio = "=1.53.2"` | The official sparse index says non-yanked, Rust 1.71 minimum, SHA-256 `e95f91fcc7a621e8b030f6aa23c71fe9838ae2fb4d8118b75602a328f5144044`, published 2026-10-03. Declare Tokio directly with only the needed runtime, networking, and shutdown features; the existing synchronous PostgreSQL crate already brings Tokio transitively, but that does not make Tokio a direct API dependency. ([official crate index](https://index.crates.io/to/ki/tokio), [versioned runtime builder](https://docs.rs/tokio/1.53.2/tokio/runtime/struct.Builder.html), [versioned `spawn_blocking`](https://docs.rs/tokio/1.53.2/tokio/task/fn.spawn_blocking.html)) |
| Rust JSON | `serde_json = "=1.0.154"`, direct `serde = "=1.0.229"` | Registry records say both are non-yanked and Rust 1.71/Rust 1.56 minimum, respectively. Checksums: serde_json `e7e9cc8b1b85264074fbcc02a88680c4096b1e47df8f739dceb03bf482f04bd6`; serde `4148590afebada386688f18773da617792bf2ef03ffc1e4cbd2b1d45b023e0ba`. The direct serde dependency is needed for the custom `Deserialize`/map visitor that rejects duplicate object members. Keep the lockfile and record its exact resolution. ([serde_json index](https://index.crates.io/se/rd/serde_json), [serde index](https://index.crates.io/se/rd/serde), [versioned serde_json docs](https://docs.rs/serde_json/1.0.154/serde_json/), [Serde visitor API](https://docs.rs/serde/1.0.229/serde/de/trait.Visitor.html)) |

The synchronous `tiny_http` alternative is small and its 0.12.0 API can receive
requests synchronously, but the official registry record shows it was last
published 2022-10-06. That is a material maintenance-age tradeoff for a new
case. Axum 0.8.9 is the better fit for the requested maintained server, provided
the adapter keeps synchronous PostgreSQL calls off Tokio reactor threads and
places explicit limits around them. ([tiny_http 0.12.0 docs](https://docs.rs/tiny_http/0.12.0/tiny_http/), [tiny_http registry index](https://index.crates.io/ti/ny/tiny_http), [Axum releases](https://github.com/tokio-rs/axum/releases))

## Bounds, lifecycle, and parser behavior

- **The wire body cap must be exact and independent of `Content-Length`.** The
  contract sets 8192 bytes including whitespace. Java should count bytes while
  reading `HttpExchange.getRequestBody()` and reject byte 8193; Jackson stream
  constraints are an additional parser guard, not the exact transport cap.
  Jackson documents its limits as resource protections that may not be imposed
  with exact byte-for-byte precision, and its default document-length limit is
  unlimited. Configure document, nesting, string, property-name, number, and
  token limits explicitly. ([Jackson processing limits](https://github.com/FasterXML/jackson-core), [`StreamReadConstraints` API](https://javadoc.io/static/com.fasterxml.jackson.core/jackson-core/2.22.3/com/fasterxml/jackson/core/StreamReadConstraints.html))
- **Axum's JSON/bytes extractors default to a 2 MiB body cap.** Set
  `DefaultBodyLimit::max(8192)` explicitly and use an extractor that enforces
  it on streamed bytes, including requests with no declared length. The Axum
  docs warn that manually polling `Body` bypasses this default limit. ([versioned `DefaultBodyLimit`](https://docs.rs/axum/0.8.9/axum/extract/struct.DefaultBodyLimit.html))
- **Bound work before offloading synchronous PostgreSQL.** Tokio's
  `spawn_blocking` pool defaults to as many as 512 extra threads; once its limit
  is reached, calls queue. Started blocking tasks cannot be aborted, and runtime
  shutdown can wait indefinitely for them. Configure a bounded blocking-worker
  count and acquire a non-waiting permit before submitting database work; return
  the contract's generic `503 Busy` when the 16-operation limit is full. A
  request-count permit also bounds the queue of admitted database operations.
  Keep the inherited connect/statement/lock timeouts. Do not release an in-flight
  operation merely because a client disconnected. ([Tokio `Builder`](https://docs.rs/tokio/1.53.2/tokio/runtime/struct.Builder.html), [`spawn_blocking`](https://docs.rs/tokio/1.53.2/tokio/task/fn.spawn_blocking.html))
- **Bound and drain Java workers.** `HttpServer` accepts a caller-provided
  executor and separately exposes the socket backlog. Use a bounded executor
  plus 16-operation admission control; avoid its unspecified default executor
  for this bounded case. On shutdown stop accepting, allow the documented drain
  interval, then shut down/await the worker pool with a finite deadline. The
  contract explicitly makes native malformed-framing/header parser behavior and
  slow-client/header-count hardening outside cross-stack parity claims.
  ([`HttpServer`](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.httpserver/com/sun/net/httpserver/HttpServer.html))
- **Reject repeated JSON names consistently.** RFC 8259 says member names
  SHOULD be unique and warns that duplicate-name handling is unpredictable
  across implementations; many retain only the last value. Jackson exposes
  `StreamReadFeature.STRICT_DUPLICATE_DETECTION`; enable it. `serde_json::Map`
  replaces an existing value on `insert`, so parsing to `Value` alone can lose
  duplicates; use the contract's custom serde map visitor and reject a key as
  soon as it repeats. Also require exactly one root object, reject unknown
  properties, and reject trailing JSON in both implementations. ([RFC 8259 §4](https://www.rfc-editor.org/rfc/rfc8259.html#section-4), [Jackson strict duplicate feature](https://javadoc.io/static/com.fasterxml.jackson.core/jackson-core/2.22.3/com/fasterxml/jackson/core/StreamReadFeature.html), [`serde_json::Map::insert`](https://docs.rs/serde_json/1.0.154/serde_json/struct.Map.html#method.insert), [serde_json value deserializer source](https://github.com/serde-rs/json/blob/master/src/value/de.rs))
- **Keep money and quantity out of JSON-number conversion.** RFC 8259 permits
  number spellings broader than any fixed integer type and notes exact
  interoperability is constrained by binary64 implementations. The HTTP
  contract correctly carries signed minor units and quantity as decimal strings,
  with the same ASCII grammar and signed-64-bit parse boundary in both languages.
  Serialize every snapshot field as a string too. Validate UTF-8 strictly,
  separate malformed text from valid out-of-range integer text, and return a
  generic parse error without echoing submitted content. ([RFC 8259 §§6, 9](https://www.rfc-editor.org/rfc/rfc8259.html#section-6))

## HTTP status and retry claims

RFC 9110 defines idempotence as a method property: safe methods plus `PUT` and
`DELETE` are idempotent; `POST` is not. That does not prevent an application
from implementing stable-key replay for a particular POST route, but the
guarantee must come from the stored application identity and its full request
fingerprint. In this case, the existing payment/refund identities and provider
records provide that policy. A line POST has no durable command receipt, so a
repeated identical POST appends another line; an uncertain response must be
inspected by the caller, not automatically replayed. ([RFC 9110 §9.2.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2), [RFC 9110 POST](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.3.3))

The IETF `Idempotency-Key` document retrieved for this review is draft-07, an
Internet-Draft that expired on 2026-04-18; it is not an RFC or a protocol
guarantee. It proposed a Structured Field String, uniqueness rules, optional
expiry, and payload fingerprints. Therefore the case's header-as-alias for a
typed payment/refund ID is an explicitly application-defined convention. Do
not imply general header compliance, a response cache, key expiry, or exactly
once execution. ([IETF draft history](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/history/), [draft-07 text](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header))

The current status mapping is an application choice consistent with RFC 9110:
`202 Accepted` carries a still-pending provider observation (`Unknown` or
provider `NotFound`) and its snapshot; it does not claim that a background job
will run. `409 Conflict` fits state/identity conflicts; `422 Unprocessable
Content` fits syntactically valid domain inputs that cannot be applied; `413`
is the body cap; `415` is unsupported JSON media type; and `503` is transient
local unavailability or bounded admission rejection. A `503`, lost socket, or
timeout does not prove a database rollback. For payment/refund, recover by
reading the persisted scope and retrying/reconciling only the same operation
identity. Keep provider `NotFound` distinct from HTTP 404 `ScopeNotFound`.
([RFC 9110 status definitions](https://www.rfc-editor.org/rfc/rfc9110.html#section-15))

## Evidence boundary

These primary sources establish the library interfaces, versions, hashes, and
protocol semantics cited above. They do not prove implementation compilation,
transport parity, a particular executor's rejection behavior, the 16-request
runtime limit, PostgreSQL recovery, client behavior, or any HTTP acceptance
scenario. Those remain integrator-owned build and harness evidence under the
HTTP contract.
