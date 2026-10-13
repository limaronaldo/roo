# HTTP security and correctness source review

Date: 2026-10-11. Status: initial source review; not acceptance of a frozen
candidate. This reviewer executed no build, dependency fetch, HTTP request, SQL,
cluster operation, or Git command. Only this review document was written.

Scope: `case-studies/orders-payments/http/SPEC.md`, Java HTTP protocol/service,
Rust HTTP library/binary, shared `support.py`/`verify.py`/`verify.sh`, and the
accepted PostgreSQL configuration, transaction, action-parser, cluster, and
barrier code needed to understand their reuse. Concurrent implementer edits are
preserved. References below identify the source as inspected, not a frozen hash.

## Actionable findings

### HSEC-1 — Low — route syntax has different error semantics

Unresolved at inspection. In `http/rust/src/lib.rs:90-94`, the combined
`parts.len() < 4`/prefix condition returns `404 RouteNotFound` for
`GET /v1/scopes`. Java recognizes the resource prefix, then rejects the absent
scope with `400 InvalidRequest` in
`http/java/src/roo/postgres/HttpProtocol.java:48-49`. The HTTP contract requires
malformed scopes to return 400 before SQL and shared response parity.

Separate recognition of `/v1/scopes` from scope validation in Rust, so an absent
scope is treated like the other invalid scope forms. Add this exact request to
the shared validation matrix and verify the fixed error envelope in all three
variants. Neither implementation reaches SQL for this request; the impact is
contract correctness, not an access-control bypass.

There is also a character-policy difference: Java's raw path allowlist
(`[A-Za-z0-9_/-]*`, `HttpProtocol.java:44-46`) rejects
`/v1/scopes/s/unknown.ext` with 400; Rust only excludes non-ASCII, percent,
fragment, repeated slash, and trailing slash before matching the suffix
(`lib.rs:80-88,103-113`), so this ASCII unknown resource returns 404. The
contract's phrase "unknown well-formed route" needs an explicit common raw-path
character grammar. Adopt the same allowlist in both stacks, or explicitly allow
ASCII punctuation and change Java accordingly. Add `unknown.ext`, a punctuation
case such as `unknown!`, and a normal unknown resource to shared requests. This
does not affect the already strict scope-token validation.

### HSEC-2 — Low — Content-Type parameter whitespace differs across stacks

Unresolved at inspection. Java permits whitespace around the charset equals
sign in `http/java/src/roo/postgres/HttpProtocol.java:112`, while Rust compares
the entire trimmed parameter with `charset=utf-8` in
`http/rust/src/lib.rs:164-172`. For example, a valid body with
`Content-Type: application/json; charset = utf-8` is accepted by Java and
rejected with 415 by Rust. The present shared validation matrix checks wrong
charset but does not cover this divergence.

Choose one explicit parameter grammar in the contract and apply it in both
implementations. A narrow split on one equals sign with ASCII whitespace
trimming in Rust matches Java's current behavior. Add shared accepted cases for
the selected whitespace and case variants, plus rejected extra/duplicate
parameters. This is a transport interoperability defect; no mutation occurs on
the Rust rejection.

## Lifecycle verification gap

Low-priority follow-up, not a demonstrated implementation failure:
`http/support.py:103-115` allows ten seconds for ordinary termination before
SIGKILL. The Java service allows up to sixty seconds for listener draining plus
sixty for its executor (`HttpService.java:61-67`); Rust allows 180 seconds for
server draining and a separate bounded runtime teardown
(`rust/src/main.rs:18,263-269,295-297`). Normal verifier shutdown occurs after
requests complete, and the explicit crash lane intentionally uses SIGKILL.
Consequently those lanes do not establish graceful draining of active work.

For a future graceful-drain claim, add an explicit active-request schedule:
witness a gated request, send SIGTERM to that owned server, release the gate,
observe completion and process exit, and retain the response and exit status.
Use a cleanup timeout compatible with the selected server drain contract, or
document the ten-second harness timeout as a stricter test policy. Keep the
intentional SIGKILL lane separate.

## Source-corrected issue

The known Rust scenario-label defect is corrected in the inspected source:
`http/rust/src/main.rs:143-146` calls `snapshot(scope, scope, &last)` rather than
supplying a hardcoded demo label. The shared client now asserts that returned
`scenario` equals the requested scope before fixture-label substitution
(`http/support.py:146-156`). This is source confirmation only; root must rebuild
and execute the updated candidate before recording a passed result.

## Safeguards confirmed from source

- Both stacks strictly decode UTF-8, reject duplicate properties, require a
  string-valued object, reject trailing JSON and unknown/missing fields, bound
  the streamed body to 8192 bytes, and bound numeric text before invoking the
  accepted action parser. Java uses Jackson duplicate detection; Rust uses a
  custom Serde visitor rather than duplicate-overwriting `Value` parsing.
- Payment/refund IDs and scope are bounded ASCII tokens. The optional
  Idempotency-Key is checked against the corresponding body ID, rejected on
  other resources, and rejected when repeated or comma-joined. Synthetic
  controls remain startup-enabled, with no request-supplied environment changes.
- Java admission is capped at sixteen database-bearing handlers, with a bounded
  executor queue. Rust acquires one of sixteen permits before `spawn_blocking`
  and moves that permit into the blocking task, so client cancellation cannot
  release capacity while its database work continues. No global application
  mutex or shared database client was introduced.
- Both adapters validate explicit loopback listener configuration before binding
  and reuse accepted structured PostgreSQL configuration. Startup does not
  install/reset schemas or open a domain connection. Readiness is emitted after
  bind and contains only the fixed host, selected port, and readiness flag.
- HTTP errors use closed codes and fixed messages. Java SQLException handling,
  Rust database error mapping, and the Rust panic hook do not expose submitted
  bodies, exception text, SQL, DSNs, or stack traces through responses/logging in
  the inspected HTTP code. Both emit no-store and connection-close headers.
- HTTP gate SQL is parameterized, instrumentation-only, separate from domain
  connections, and has explicit connection/statement/lock timeouts. Gate failure
  maps to infrastructure failure rather than a successful domain response.
- Shared scenarios are translated into real HTTP requests, compare all eleven
  observations with the unchanged independent TSV, and distinguish domain
  NotFound from a missing scope. Lost responses are checked as connection loss
  before headers, followed by fresh-process HTTP inspection/recovery. The add
  response-loss example deliberately inspects before a second explicit add.
- Cleanup retains exact child-process handles; SIGKILL targets those handles.
  The reused PostgreSQL helper checks ownership markers/data path and prepends
  an endpoint guard to SQL. The verifier's immediate-restart lane uses that
  helper, separately verifies surviving HTTP PIDs/reconnection, and retains WAL
  recovery observations. No claim of production authentication, tenant isolation,
  slow-client protection, or real payment-network behavior is inferred.

No critical or high-severity vulnerability was identified in this bounded source
review. Dependency pins/lockfile are visible, but this review did not fetch or
audit dependencies for current advisories. Baseline-hash verification, executed
regressions, candidate freezing, and final independent acceptance remain root
responsibilities and are not established by this document.

## Focused resolution review

Later source recheck on 2026-10-11, while root qualification was running. These
notes supersede the initial unresolved labels above without overwriting the
history. This reviewer again performed source reads only and makes no new
runtime pass claim.

- **HSEC-1: source-corrected.** Rust `lib.rs:80-94` now uses the same ASCII raw
  path allowlist as Java and explicitly rejects `/v1/scopes`. `http/SPEC.md`,
  Routes and JSON, now declares `[A-Za-z0-9_/-]+` and rejects other punctuation
  before route dispatch. The shared validation matrix includes
  `missing_scope_segment` and `punctuation_route` (`verify.py:71-72`) and retains
  an ordinary unknown-resource 404 case (`verify.py:84`). Each rejection is
  followed by a no-state-change assertion (`verify.py:100-104`).
- **HSEC-2: source-corrected.** Rust's charset check now splits once at `=` and
  trims the parameter name/value while matching case-insensitively
  (`lib.rs:167-180`). The SPEC explicitly permits whitespace around `=`. The
  shared negotiation lane sends `Application/JSON ; charset = UTF-8` and
  wildcard Accept, verifies unchanged state, and separately exercises absent
  Accept (`verify.py:107-117`).
- **Scope regression guard retained.** `support.py:146-156` still checks the
  returned scenario against the requested scope before any oracle fixture-label
  replacement. The earlier source correction is therefore not hidden by the
  common TSV normalization.
- **Graceful-drain coverage gap addressed in test source.** The new
  `graceful_drain` lane (`verify.py:153-183`) witnesses the active POST at the
  after-snapshot PostgreSQL gate, sends SIGTERM to that exact child, observes a
  refused/reset/closed listener while both child and original request remain
  active, releases the gate, requires the original response, checks clean
  termination without forced kill, and reads the persisted increment through
  the ordinary server. Cleanup now waits 190 seconds (`support.py:110`), which
  exceeds the individual 180-second Rust drain phase. This schedule addresses
  successful draining of admitted work; it is not an exhaustive proof of the
  maximum combined duration of stalled server and runtime teardown phases.
- **Capacity coverage strengthened in test source.** `admission`
  (`verify.py:120-150`) starts sixteen requests on separate scopes, requires
  sixteen simultaneously observed advisory waits for the exact gated worker,
  checks request seventeen receives the fixed `503 Busy` envelope, releases
  the gate, observes all sixteen results and persisted increments, and checks
  capacity is usable again. Java now has 32 HTTP workers, sixteen database
  permits, and a bounded 64-entry queue (`HttpService.java:52-54`), enabling the
  overflow request to reach admission while all database permits are held.

No unresolved actionable source defect remains from HSEC-1/HSEC-2 or the
initial drain-coverage observation. Executed results for these additions,
cleanup outcomes, preserved baseline hashes, and final frozen-candidate
acceptance must still come from root's retained qualification receipts and
independent final review.

## Note added 2026-10-13: fragment handling in the Rust server

Added after the fact; the text above is left as written.

**The original statement was wrong.** Lines 32-34 say Rust "only excludes non-ASCII, percent, fragment, repeated slash, and trailing slash". The word *fragment* in that list was not true when the review was written (2026-10-11) and was still not true in the published v0.4.3 source (`8bf017f`):

- At `8bf017f`, `route_with_authorization` in `case-studies/orders-payments/http/rust/src/lib.rs` inspects only `uri.path()` and `uri.query()` of an already-parsed `http::Uri`. `git grep -n -E "'#'|\"#\"" 8bf017f -- case-studies/orders-payments/http/rust/src` finds no check for `#` in `lib.rs` or `main.rs`.
- `http::Uri` discards the fragment while parsing. Checked on 2026-10-13 with a throwaway crate pinned to `http` 1.5.0, the version in this crate's `Cargo.lock`: `/v1/scopes/s/orders#frag` parsed to path `/v1/scopes/s/orders` with no query, and `/v1/scopes/s/orders?x=1#f` to path `/v1/scopes/s/orders`, query `x=1`. A request line carrying a fragment therefore reached routing as if it had none.
- The contract already required rejection: `http/SPEC.md:87` and `http/README.md:324` list fragments among the rejected forms at `8bf017f`. The Rust server did not implement that.

**Behaviour after the fix (2026-10-13).** The fix landed on 2026-10-13 in this port's working tree and, when this note was written, was an uncommitted change. `request_line` in `case-studies/orders-payments/http/rust/src/main.rs` now reads the raw request line and rejects any request whose target field contains `#` before `http::Uri` or routing see it. The comment in that function states the reason: check the raw second field before `http::Uri` can discard a fragment.

**Not claimed here.** I did not build or run the fixed server, so this note does not say that its tests pass. The Java HTTP path and the other findings in this report are unaffected by this note.
