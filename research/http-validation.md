# HTTP orders/payments: executed validation

Date: 2026-10-11. This local qualification extends the accepted PostgreSQL
case through real HTTP listeners. All payments, orders, provider records and
consumer events are synthetic. Java composition, Java final Template Method
and Rust composition use the same request harness and independent business
oracle.

## Reproduce

```sh
bash case-studies/orders-payments/http/verify.sh
bash case-studies/orders-payments/http/regression.sh
```

The first command fetches checksum-pinned jars and locked Rust dependencies,
compiles serially, starts only the marked private PostgreSQL cluster, applies
the unchanged schema if necessary, tests actual HTTP, and cleans up its
processes. The second requalifies the earlier in-memory, PostgreSQL and original
ROO laboratories. It runs the unchanged PostgreSQL verifier while redirecting
only its evidence-file destination to a new HTTP regression receipt. Historical
source and evidence remain intact.

See [http-checks.log](http-checks.log),
[http-integration-evidence.json](http-integration-evidence.json),
[http-regression.log](http-regression.log), and
[http-environment.json](http-environment.json). The
[contract](../case-studies/orders-payments/http/SPEC.md) and
[tutorial](../case-studies/orders-payments/http/README.md) explain the model.

## Shared HTTP results

The completed HTTP qualification exited zero. Each of the three variants
passed the following exact shared observations:

| Lane | Per variant | Observed outcome |
|---|---:|---|
| Existing independent oracle | 42 scenarios | Every field matches the original eleven-field expected result |
| Invalid requests | 41 cases | Exact status/error envelope and no change to the existing order snapshot |
| Positive negotiation | 2 cases | Media case/charset whitespace, wildcard and absent Accept accepted consistently |
| Ordinary mode | 8 cases | Five synthetic controls rejected; same payment/refund keys replay safely; PUT preserves state |
| Startup configuration | 4 cases | Invalid listener/test-gate settings fail before readiness |
| Admission saturation | 16 simultaneous operations | All sixteen witnessed waiting in PostgreSQL; request seventeen receives `503 Busy`; capacity recovers |
| Active graceful stop | 1 schedule | SIGTERM closes listener while admitted request remains alive; gate release completes response and clean exit |
| Competing requests | 7 schedules | Database lock witnesses establish the intended overlap and expected outcomes |
| Process crash recovery | 8 schedules | Five durable gaps and three completed-response losses recovered through fresh HTTP processes |
| PostgreSQL recovery | 4 scopes | Pending payment, pending refund, inbox acknowledgement gap and terminal payment survive and recover |

The harness validates the actual scope in every successful response before
relabeling it for the original fixture oracle. Snapshot fields are all strings;
status codes and error messages use the closed contract vocabulary. The
malformed suite includes duplicate/escaped JSON names, strict UTF-8, unknown
fields, numeric strings, missing scope segments, raw path punctuation, repeated
headers, mismatched keys and an actual chunked body exceeding 8192 bytes.

The concurrent schedules cover different and identical payment keys, different
and identical refund keys, add-before-pay, pay-before-add, and competing relays.
Sixty-three lock witnesses establish the race, crash and graceful-drain gates.
Admission has another sixteen simultaneously observed advisory waits per
variant, recorded separately in the receipt. Timing sleeps alone do not stand
in for a PostgreSQL wait observation.

Twenty-four HTTP process SIGKILL tests observed connection loss before response
headers. Fresh processes then inspected committed state and recovered. Three
of each variant's schedules kill after the completed action and snapshot but
before response delivery: payment, refund and line addition. Payment/refund
replays retain one provider effect. The line test inspects the committed total
and deliberately makes a second add, demonstrating that line POST has no
durable idempotency receipt. It does not automatically retry an uncertain add.

One owned PostgreSQL immediate shutdown/restart preserved twelve exact
snapshots. WAL redo was observed with fsync, synchronous_commit and
full_page_writes enabled. The same three HTTP process IDs each returned the
generic `503 DatabaseUnavailable` while PostgreSQL was stopped, then opened
fresh connections and completed recovery after restart. All owned HTTP
processes and the private database were stopped at qualification exit; synthetic
data remains available for inspection.

## Compiler and protocol checks

Java compiles the unchanged PostgreSQL sources plus the new HTTP sources into
an independent build directory with release 21, all lint warnings enabled and
warnings treated as errors. Seventy-two pure HTTP protocol checks passed. Both
entrypoints were then independently exercised by the shared HTTP harness.

The HTTP Rust crate passed five unit tests, formatting, all-target Clippy with
warnings denied, locked offline build and documentation generation. Tests
include route/header parity corrections. A path dependency reuses the accepted
PostgreSQL application. The new crate forbids unsafe code and moves each
admission permit into its synchronous blocking operation.

These local test counts differ by language because implementation-level tests
exercise different representations. Behavioral parity is established by the
same real HTTP scenarios, independent expected observations and recovery
schedules, rather than matching unit-test counts.

## Review corrections

The historical regression also exited zero. The unchanged in-memory case again
passed 42 oracle rows and 10 malformed fixtures in each variant; its Java
280 checks/two compiler negatives and Rust 20 unit/two positive/three negative
examples passed. The original ROO laboratory passed its 17 tests. The unchanged
PostgreSQL case passed, per variant, 42 oracle rows, 10 malformed fixtures,
three persistent guards, seven races, five SIGKILL recoveries and four restart
scopes, plus five shared SQL-constraint probes. Java's 52 pure checks/two
compiler negatives and Rust's six unit/two positive/four negative examples
passed. The compiler-negative receipt confirms the intended diagnostic codes.

All 120 previous candidate files were rechecked after regression: 118 remain
byte-identical; only root README navigation and cache-ignore patterns were
intentionally extended. The original schemas, implementations, oracle,
documentation and historical receipts are preserved.

Documentation review caught a hardcoded Rust snapshot label. The implementation
now reports the actual scope, and the shared harness asserts it for every
success response. Independent source review found missing-scope/raw-path and
charset-whitespace differences; source, contract and shared requests were
aligned before the final passing qualification.

The new admission test uses 32 bounded Java HTTP workers, a queue of 64 and
16 database permits, so it can emit Busy while all database slots are occupied.
Rust uses 16 database permits and at most 16 blocking workers. The permits
remain held until actual work finishes, including after a client disconnect.
The active graceful-stop test proves its recorded schedule; it does not prove
the worst-case sum of every stalled transport and runtime shutdown deadline.

The [security review](http-security.md) separates initial findings from their
source corrections. Final acceptance is separately recorded in
[http-review.md](http-review.md) against the frozen candidate manifest.

## Evidence limits

This is a loopback educational API with a deterministic provider simulator in
the same PostgreSQL durability domain. It establishes the recorded HTTP,
transaction, concurrency and recovery behavior. It does not establish real
payment-network behavior, hardware power-loss durability, authenticated tenant
isolation, production capacity, every possible interleaving or native HTTP
parser parity for malformed framing. No endpoint executes an arbitrary script,
SQL string or external payment call.

The caller must distinguish response loss from effect absence. `503` or a
disconnected socket does not prove rollback. Natural operation identities,
persisted intent, provider fingerprints, short transactions, finalization and
inbox deduplication carry the recovery protocol; a Rust borrow or Java final
method cannot make those durable boundaries atomic.

## Notes added 2026-10-13

Added after the fact; the text above is not rewritten.

**Exit status of the Java servers (line 44, "clean exit").** In the "Active graceful stop" row, "clean exit" means the server stopped on its own without being force-killed. It does not mean exit status 0. The retained receipt [http-integration-evidence.json](http-integration-evidence.json) records `"exit_code": 143` in the `graceful_drain` block of both Java variants (Java composition and Java inheritance) and `0` for Rust composition. 143 is 128 + 15, the shell convention for termination by SIGTERM (signal 15), and is the status a JVM normally reports when it shuts down in response to SIGTERM after running its shutdown hooks. It is the expected result of a graceful stop of the Java servers, not a failure. The harness accepts both values: `case-studies/orders-payments/http/verify.py` line 197 (`if gated.process.returncode not in (0, 143):`, checked in the `8bf017f` tree) raises `AssertionError("Graceful drain required forced termination")` for any other status, and the `"forced_termination": false` field is only written after that check passes.
