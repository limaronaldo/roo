# Orders and payments: shared executable contract

Status: frozen implementation contract, 2026-10-11. This document is the common
behavioral target for Java composition, Java template-method inheritance, and
Rust composition. All three use deterministic, single-threaded, in-memory
adapters. They do not move money or establish production payment guarantees.

## Domain and invariant boundary

Each scenario starts with a new empty Draft order `O1`, currency `USD`, local
store, remote provider, outbox, and consumer. OrderId, PaymentId, RefundId, and
EventId are different domain concepts; use distinct value types/newtypes, not
interchangeable unlabelled strings in domain APIs. Fixture strings are validated
at the boundary; domain identity tokens use nonempty ASCII alphanumeric IDs
(scenario labels may additionally contain underscores).

Money is signed 64-bit integer minor units in one fixed currency. A line has a
strictly positive unit amount and quantity. Multiplication and summation are
checked against signed 64-bit maximum `9223372036854775807` in both languages.
Zero, negative, malformed, or overflowing values are rejected. No floating point
or decimal rounding is involved. Each add validates a candidate before installing
it: a rejected addition preserves every prior line and total. An empty order may
exist but cannot be paid. Once payment intent is prepared, lines are frozen.

Private mutation methods preserve these rules. Observers receive values,
immutable views, or snapshots; public callers cannot replace status, totals,
lines, payment identity, or refund identity arbitrarily. Rust move/borrow checking
and Java encapsulation contribute different evidence; both need runtime checks.

Local states are `Draft`, `Pending`, `Paid`, `Declined`, `Refunding`, `Refunded`.
An order has at most one payment intent and one full-amount refund intent.
Declined payment is terminal for this bounded order. Partial refunds, replacement
payment attempts, cancellation, multiple orders per fixture, and retries with a
new intent are outside this case. These restrictions keep recovery observable.

## Remote contract and identities

A payment request is the immutable tuple `(PaymentId, OrderId, USD, amount)`;
a refund request is `(RefundId, PaymentId, OrderId, USD, amount)`. Provider key
namespaces are typed by operation kind. A refund references a confirmed charge
and refunds its complete amount at most once. Refund and payment identity are
retained independently; neither equals the OrderId merely by convention.

For a recorded key, the identical request returns the recorded terminal result
without another effect. Reusing that key with any different request field returns
`KeyConflict` and changes nothing. This guarantee is explicitly supplied by the
simulated provider, not by the programming language. Its complete key records
are retained for the entire fresh scenario, with no expiry or eviction. Real
provider retention and retry behavior can differ. Provider records and effects
are outside the local store. A provider request returns `Approved`, `Declined`, or
`Unknown`; status lookup returns `Approved`, `Declined`, `NotFound`, or `Unknown`.
`NotFound` and unavailable/unknown lookup must never be conflated.

The script selects provider behavior for a previously unrecorded request:

| Mode | Durable remote record | Successful effect | Call result |
|---|---|---|---|
| `approve` | Approved | one charge or refund | Approved |
| `decline` (payment only) | Declined | none | Declined |
| `timeout_before` | none | none | Unknown |
| `timeout_after` | Approved | one charge or refund | Unknown |

For an existing matching record, its stable terminal result takes priority over
the script mode. Unknown is a caller observation, not a fabricated remote
terminal record. An unavailable lookup returns Unknown without changing records.
Lookup is read-only. NotFound is authoritative only within this simulator's
complete provider map; a real provider lookup requires its own documented
consistency and retention contract before inferring the absence of an effect.
A successful refund must be tied to the stored approved
payment and amount; no refund can exceed that charge.

## Application protocol and local commit simulator

The store owns the committed order snapshot and outbox. The application works on
a detached candidate and atomically replaces committed state only when the
simulated commit succeeds. A failed commit installs neither candidate state nor
candidate events. Successful add actions also install their validated candidate
in the committed store; add has no store-failure injection. After any store
failure, observations and further actions use
the reloaded committed snapshot. There is no mutable cached order that continues
to advertise an uncommitted Paid/Refunded state.

Payment steps:

1. Reject an empty order, invalid state, or conflicting intent without a remote call.
2. On Draft, persist the immutable payment intent and Pending order together.
3. Call the provider using that persisted intent and stable PaymentId.
4. Unknown leaves Pending. Approved commits Paid plus one `PaymentApproved` fact;
   Declined commits Declined plus one `PaymentDeclined` fact.
5. If step 4 fails, return LocalCommitFailed, reload Pending, and retain the
   provider's independent record/effect. Reconciliation or same-key retry can
   finish the local transition without charging again.

Refund steps follow the same structure: Paid becomes Refunding with persisted
refund intent before the remote request; Approved commits Refunded plus one
`RefundApproved` fact. Unknown or final commit failure leaves Refunding. Refund
fixture modes exclude decline to keep the single-refund state machine bounded.

Repeating pay with the stored payment ID in Paid, Refunding, or Refunded returns
AlreadyApplied; in Declined it returns AlreadyDeclined. Repeating refund with the
stored refund ID in Refunded returns AlreadyApplied. In Pending/Refunding a
matching operation retries the persisted request; a different identity returns
IntentConflict. Calling pay from non-Draft with a different PaymentId returns
IntentConflict. Calling refund from any state other than Paid/Refunding/Refunded
returns InvalidState. In Paid, a first refund may prepare its own identity.

Reconcile is valid only in Pending or Refunding. It queries the active persisted
intent and commits a terminal observation exactly as the original call would.
NotFound leaves state unchanged and returns NotFound. Unknown leaves state
unchanged and returns Unknown. Neither result creates a fresh key or an event.
Calling reconcile in other states returns InvalidState. Retrying the same key
after NotFound is allowed under this provider's explicit idempotency contract.

Failure injection `prepare` fails only the initial intent commit, returning
LocalPrepareFailed before any remote request. Failure injection `commit` fails
only the final terminal-result commit, after the remote call/lookup. A terminal
no-op, Unknown, or NotFound never performs a final commit, so that injection has
no effect there. Failure flags apply to that one script action only. Intent
preparation and finalization are deliberately separate local transactions.

## Outbox and delivery

Every terminal local transition appends exactly one immutable event in the same
candidate commit as its order change. Event IDs are deterministic and stable:
`payment:<PaymentId>` for either payment terminal fact, `refund:<RefundId>` for
the refund fact. Events own copied identities and amount facts. The outbox keeps
all committed event records plus delivery acknowledgement flags; event_count
counts records, pending_outbox counts unacknowledged records.

Relay scans unacknowledged events in insertion order. `ok` sends each event and
acknowledges it. `send_fail` stops before the first delivery or acknowledgement.
`ack_fail` sends the first pending event, then stops before acknowledgement.
The consumer remembers EventId and applies each unique event once. A redelivery
after ack_fail increments neither consumer_count nor any payment effect. No
pending messages means any relay mode returns RelayOk. The simulated successful
ack is local and infallible except for the selected ack_fail point.

## Fixture input: exact grammar

UTF-8 TSV, LF line endings, one header, exactly two columns; blank lines are
ignored. IDs and tokens contain no tabs, semicolons, colons, or whitespace.

```text
scenario\tsteps
```

Each row has a unique scenario ID and a nonempty semicolon-separated action list.
No spaces are inserted around delimiters. Parse the entire row structurally
before execution; malformed action syntax is a fixture error (nonzero process
exit), not a domain result. Signed numeric values are domain inputs, so valid
integer text outside the signed-64-bit range returns Overflow rather than
crashing. Test those boundary parsers independently as needed.

| Action | Meaning |
|---|---|
| `add:<unit_minor>:<quantity>` | Add one validated line to Draft |
| `pay:<payment_id>:<mode>:<failure>` | Prepare/retry payment; mode above; failure none/prepare/commit |
| `refund:<refund_id>:<mode>:<failure>` | Prepare/retry full refund; mode approve/timeout_before/timeout_after |
| `reconcile:<lookup>:<failure>` | lookup ok/unavailable; failure none/commit |
| `relay:<mode>` | mode ok/send_fail/ack_fail |
| `conflict:<payment_id>:<different_amount>` | Provider-contract probe: reuse recorded payment key for O1/USD with changed amount |

`conflict` is an explicitly labelled adapter test action: it calls the provider
directly, bypassing the order application, and must reject mismatched intent.
Its ID must already have a terminal payment record and its positive amount must
differ from that record; otherwise treat the fixture as malformed. It does not
change local order state. Do not expose this probe as a normal checkout API.

Every implementation runner accepts exactly one fixture path argument and emits
only the normalized TSV on stdout, preserving scenario row order. Diagnostics
go to stderr. Unknown operations, wrong field counts, duplicate scenario IDs,
invalid mode tokens, and malformed numeric text fail the process. There are no
dependencies on a JSON parser, clock, random source, network, or external service.

## Fixture output: exact schema and result names

```text
scenario\tstate\ttotal\tcharge_count\trefund_count\tevent_count\tconsumer_count\tpending_outbox\tlast_result\tpayment_id\trefund_id
```

Output includes this header once, then exactly one row per input row. State is
the committed store state; total is the committed order total. Counts are decimal
integers with no separators. charge_count/refund_count count successful remote
effects, not requests. consumer_count counts unique applied event IDs. Missing
payment/refund IDs are `-`. last_result belongs to the last action, even if an
earlier action failed. No output depends on implementation variant or class name.

Closed result vocabulary: `Added`, `InvalidLine`, `Overflow`, `InvalidOrder`,
`InvalidState`, `IntentConflict`, `Approved`, `Declined`, `Unknown`, `NotFound`,
`AlreadyApplied`, `AlreadyDeclined`, `LocalPrepareFailed`, `LocalCommitFailed`,
`KeyConflict`, `RelayOk`, `RelaySendFailed`, `RelayAckFailed`.

In-range negative/zero line values return InvalidLine; arithmetic overflow or
any out-of-range integer text returns Overflow. Domain failures are explicit outcomes; unexpected
exceptions/panics are runner failures. A rejected action preserves all committed
state unless its documented remote call has already produced an independent
effect. Each step still executes after earlier domain failures.

## Required common scenarios

The shared TSV input and expected-result fixtures define the comparison. The following rows are
normative inputs. `A` below is the exact prefix `add:100:2;add:50:1` (total 250),
expanded literally in the fixture. Each scenario starts fresh.

| Scenario | Steps (expand A) | Final state; relevant observation |
|---|---|---|
| success | A;pay:p1:approve:none;relay:ok | Paid; 1 charge, 1 event, 1 consumer, 0 pending |
| invalid_quantity | add:100:0 | Draft; total 0; InvalidLine |
| invalid_price | add:-1:1 | Draft; total 0; InvalidLine |
| multiplication_overflow | add:9223372036854775807:2 | Draft; total 0; Overflow |
| sum_overflow | add:9223372036854775807:1;add:1:1 | Draft; total max; Overflow |
| empty_order | pay:p1:approve:none | Draft; InvalidOrder; no payment ID |
| decline | A;pay:p1:decline:none | Declined; 0 charges, 1 event, 1 pending |
| timeout_before | A;pay:p1:timeout_before:none | Pending; 0 charges, 0 events; Unknown |
| timeout_after | A;pay:p1:timeout_after:none | Pending; 1 charge, 0 events; Unknown |
| lookup_not_found | A;pay:p1:timeout_before:none;reconcile:ok:none | Pending; NotFound |
| lookup_unavailable | A;pay:p1:timeout_after:none;reconcile:unavailable:none | Pending; 1 charge; Unknown |
| reconcile_payment | A;pay:p1:timeout_after:none;reconcile:ok:none | Paid; 1 charge, 1 event; Approved |
| retry_same_key | A;pay:p1:timeout_after:none;pay:p1:approve:none;pay:p1:approve:none | Paid; 1 charge, 1 event; AlreadyApplied |
| retry_after_not_found | A;pay:p1:timeout_before:none;reconcile:ok:none;pay:p1:approve:none | Paid; 1 charge, 1 event; Approved |
| key_conflict | A;pay:p1:approve:none;conflict:p1:999 | Paid; 1 charge, 1 event; KeyConflict |
| intent_conflict | A;pay:p1:timeout_after:none;pay:p2:approve:none | Pending; 1 charge; IntentConflict; ID p1 |
| prepare_failure | A;pay:p1:approve:prepare | Draft; total 250; 0 charges, no intent/event; LocalPrepareFailed |
| commit_failure | A;pay:p1:approve:commit | Pending; 1 charge, 0 events; LocalCommitFailed |
| recover_commit | A;pay:p1:approve:commit;reconcile:ok:none | Paid; 1 charge, 1 event; Approved |
| reconciliation_commit_failure | A;pay:p1:timeout_after:none;reconcile:ok:commit;reconcile:ok:none | Paid; 1 charge, 1 event; Approved |
| relay_retry | A;pay:p1:approve:none;relay:send_fail;relay:ok | Paid; 1 consumer, 0 pending; RelayOk |
| duplicate_delivery | A;pay:p1:approve:none;relay:ack_fail;relay:ok | Paid; 1 consumer, 0 pending; RelayOk |
| relay_send_failure | A;pay:p1:approve:none;relay:send_fail | Paid; 0 consumers, 1 pending; RelaySendFailed |
| relay_ack_failure | A;pay:p1:approve:none;relay:ack_fail | Paid; 1 consumer, 1 pending; RelayAckFailed |
| frozen_lines | A;pay:p1:approve:none;add:10:1 | Paid; total 250; InvalidState |
| refund | A;pay:p1:approve:none;refund:r1:approve:none;relay:ok | Refunded; 1 charge, 1 refund, 2 events/consumers, 0 pending |
| refund_timeout | A;pay:p1:approve:none;refund:r1:timeout_after:none | Refunding; 1 charge, 1 refund, 1 event; Unknown |
| reconcile_refund | A;pay:p1:approve:none;refund:r1:timeout_after:none;reconcile:ok:none | Refunded; 1 charge/refund, 2 events; Approved |
| refund_commit_recovery | A;pay:p1:approve:none;refund:r1:approve:commit;reconcile:ok:none;refund:r1:approve:none | Refunded; 1 charge/refund, 2 events; AlreadyApplied |
| refund_prepare_failure | A;pay:p1:approve:none;refund:r1:approve:prepare | Paid; 1 charge, 0 refunds, 1 event; LocalPrepareFailed; refund ID - |

Required unit-level evidence supplements the terminal fixture rows: snapshot
unchanged on invalid additions, failed commits install neither state nor event,
NotFound differs from Unknown, request mismatch considers order/currency/amount
(not just key), event fact identity stays stable across retries, and duplicate
consumer delivery does not reapply. Add intermediate assertions where a final
successful step would otherwise conceal a failure. Include an invalid cross-state
operation, refund timeout_before retry, and refund identity conflict in unit tests
or additional shared fixture rows. Do not claim all interleavings are proved.

## Comparison implementation boundaries

Java compiles with `javac --release 21` on installed JDK 26. Rust is a standalone
std-only crate targeting installed Rust 1.96, edition 2024. The reference variants
share the same domain and failure contract; they may share domain types and
adapters within a language. A flag/entrypoint can select the Java variant, but
both must execute every common row and meaningful tests.

The Java inheritance variant is legitimate template-method inheritance: a base
coordinator owns a final payment/recovery algorithm and exposes only narrow,
documented protected hooks for provider/store policy. Concrete subclasses may
supply adapters; they cannot reorder intent persistence and remote effects or
replace invariant-preserving domain transitions. Composition delegates these
capabilities to injected interfaces/objects. Keep neither a deliberately unsafe
subclass nor a broken baseline as the comparison's principal implementation.
Rust uses composition and explicit borrowing/ownership over its local resources;
traits or concrete adapters may express the same strategy boundaries.

Compiler-negative examples must demonstrate a specific actual restriction (such
as private mutation in Java; move-after-use or conflicting borrow in Rust), check
that compilation fails for that intended reason, and avoid claiming a failed
example proves distributed invariants. Document local runtime test evidence
separately from compiler evidence and externally unverified assumptions.

## Limits and acceptance

The in-memory candidate replacement models atomic local commit only within one
single-threaded run. It does not test filesystem durability, process crash,
concurrent writers, real network timeouts, provider retention windows, PCI scope,
authorization, fraud, tax, FX, cryptographic integrity, or operational scale.
There is no empirical claim that one language/paradigm is faster, safer in every
dimension, cheaper, or universally superior. The comparison identifies what each
representation enforces and which recovery responsibilities remain application
and infrastructure contracts.

Acceptance requires matching expected TSV for every row in all three variants,
meaningful language unit tests, the intended compiler-negative checks, and a
documented eight-field relationship analysis in the companion case README.
The schema is frozen before implementation; changes require an explicit shared-contract review
and synchronized fixtures, implementations, and documentation.
