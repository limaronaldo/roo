# Architecture decision: Preserve payment intent across independent effects and local recovery

Status: proposed. Date: 2026-10-11. Owner: case-study maintainer (role).

This is retrospective documentation of the existing frozen case-study policy.
It proposes an adoption record, not a new implementation or a historical approval.
ROO (Relationship & Ownership Oriented design) is language-independent: the
relationship decision precedes its realization.
Use the [adoption guide](../../../docs/09-adoption-guide.md) to apply this
record alongside the [Relationship Contract](relationship-contract.md) and
[design review](design-review.md).

## Problem and invariant

An application coordinates an order, a local store/outbox, an independent payment
provider, and a consumer. The provider can approve a charge while local terminal
finalization fails. Treating that failure as if the charge disappeared can create
a duplicate charge or expose an uncommitted Paid order.

The shared primary scenario is `recover_commit` in [scenarios.tsv](../scenarios.tsv):

```text
add:100:2;add:50:1;pay:p1:approve:commit;reconcile:ok:none
```

The two lines total 250 USD minor units. Before the provider effect, payment
intent `(p1, O1, USD, 250)` and Pending must commit together. Terminal finalization
then commits Paid and the immutable `PaymentApproved` event `payment:p1` together.
The committed store is the local observation boundary; provider effects are
observed independently. Delivery acknowledgement is a later boundary.

| Observation point | Required observation | Forbidden observation |
|---|---|---|
| Failed initial preparation | Draft, no intent, no charge/event | Provider call using an uncommitted intent |
| Failed terminal commit after approval | Pending, p1, one charge, zero events | Paid from a cached candidate, or loss/replacement of p1 |
| Successful same-intent reconciliation | Paid, p1, one charge, one `payment:p1` event | A second charge or a second terminal event |

[expected.tsv](../expected.tsv) supplies the independent terminal oracle:
`commit_failure` records the intermediate failure as its final observation;
`recover_commit` records the subsequent recovery. The recovery row has one
pending outbox record and zero consumers because this recipe performs no relay.

## Relationship Contracts

The [filled contract](relationship-contract.md) owns the detailed eight-field
analysis. This decision covers Order → payment intent → provider record and
Order → terminal event → consumer fact. An order has at most one payment intent
and one full refund intent in this bounded model.

| Field | Decision relevant to this invariant |
|---|---|
| Owner / resource custodian | Store retains committed order/outbox; provider retains its independent key records; consumer retains applied facts. The coordinator uses these capabilities without merging their custody. |
| Stable identity | OrderId, PaymentId, RefundId, and EventId are distinct. Preserve p1 and its complete immutable request across uncertainty; `payment:p1` identifies the terminal fact. PostgreSQL additionally scopes identities by scenario scope. |
| Invariant coordinator | Domain transitions validate state and money; the application coordinates preparation, provider observation, and finalization; store commits local changes. Permission to request an operation is a separate concern. |
| Authorization | Not implemented in this teaching case; a live system needs an authenticated caller policy. |
| Access regime | Observe committed snapshots, submit copied immutable requests, resolve retained provider status, and transfer event facts. Callers cannot arbitrarily replace committed commercial state. |
| Validity horizon | Freeze lines at preparation; retain the same intent throughout Pending and terminal replay. In-memory records last only for one fresh scenario; persisted extensions retain committed facts across their tested process restarts. |
| Execution domain | In-memory coordination is single-threaded. PostgreSQL coordinates local writers with short transactions and order row locks; provider calls occur outside the application transaction. |
| Failure boundary | A provider effect can survive failed local finalization. Retain intent, reload committed state, and reconcile; local rollback cannot undo that independent effect. |

Domain responsibility is the application's invariant-preserving protocol plus
domain validation. Resource custody, durable recognition, and requester
authorization do not follow automatically from that responsibility. No
authentication, authorization policy, tenant permission check, or revocation
mechanism is modeled; the fixture/HTTP caller is a synthetic requester.

## Alternatives

| Alternative | Invariant preservation | Extensibility | Lifecycle / concurrency | Operational cost |
|---|---|---|---|---|
| Selected: coordinator, stable intent, independent provider, atomic local finalization | Preserves request identity and state/event agreement at their stated boundaries | Add adapters without replacing the relationship policy | Retained intent bridges separate lifetimes; database locking coordinates local overlap | Recovery, retention, and delivery obligations remain explicit |
| One transaction spanning store and provider | Could provide atomic agreement only with an actual shared transaction protocol | Requires participating infrastructure | Such a transaction is unavailable here; the provider commits independently | Adds coordination infrastructure and failure handling beyond this case |
| New payment identity after an uncertain outcome | Violates the one-intent contract and can produce another charge | Makes every retry a new business attempt | Disconnects recovery from the surviving provider record | Apparent simplicity shifts cost to duplicate-effect investigation |
| Expose mutable committed state as an escape hatch | Allows bypassing validation and publishing state without its event | Arbitrary edits undermine adapter contracts | Aliases can retain uncommitted or conflicting state | Requires manual repair and forfeits the invariant |

## Decision and reasons

Keep one stable payment intent, prepare it before requesting the independent
effect, and finalize local state and its event atomically. The application
coordinates this ordering; the provider recognizes the complete request by its
typed natural key and rejects changed fingerprints. The caller requests a
domain operation; the case makes no claim about who would be authorized in a
real deployment.

Participants exchange identities and immutable facts rather than a shared
mutable order. A local failure reloads the committed view. Recovery resolves the
active retained intent and applies a terminal observation once. Unknown is an
observation, not a fabricated terminal provider record. NotFound remains distinct
and is authoritative only under the simulator's complete retained-record map.

This policy fits the existing independent-effect boundary and explicit oracle.
It would need reassessment for key expiry, inconsistent lookup, multiple attempts,
partial refunds, cancellation, or an actual shared transaction protocol. A new
provider contract must specify retention, fingerprint comparison, and recovery
semantics before this policy can be carried into a production slice.

## Optional realization

These are alternative code shapes for the same policy, not competing domain
decisions. Public operations add a validated line, prepare/retry payment or full
refund, reconcile an active intent, and relay committed events. Adds affect only
Draft; payment/refund operations can create independent effects; reconciliation
looks up rather than creates an effect; relay affects consumer facts and ack state.

| Layer, language, runtime, store, or protocol | Realization | Enforcement or constraint |
|---|---|---|
| Java composition | [CompositionApplication](../java/src/roo/payments/CompositionApplication.java) receives StorePort/ProviderPort; [Domain](../java/src/roo/payments/Domain.java) encapsulates transitions and immutable requests | Reloads committed intent before provider use; private mutation and checked arithmetic constrain local changes; adapter contracts remain trusted |
| Java Template Method | [TemplateApplication](../java/src/roo/payments/TemplateApplication.java) fixes public algorithms as final and exposes narrow store/provider hooks | Subclasses cannot reorder the algorithm; hooks must return stable, conforming capabilities |
| Rust composition | [Application](../rust/src/application.rs) borrows independent store/provider/consumer resources; cloned requests cross candidate boundaries | Borrow checking governs local access; [adapters](../rust/src/adapters.rs) replace detached candidates only on successful simulated commit |
| In-memory store/provider | Java [Adapters](../java/src/roo/payments/Adapters.java) and Rust adapters retain separate committed snapshots and provider maps | “Committed” means installed within this scenario; it is not disk durability, restart recovery, or distributed atomicity |
| PostgreSQL extension | Java [Store](../postgres/java/src/roo/postgres/Store.java), [coordinator](../postgres/java/src/roo/postgres/CompositionApplication.java), and Rust [Database](../postgres/rust/src/database.rs) split prepare/provider/finalize transactions | READ COMMITTED and `FOR UPDATE` serialize local writers; finalization reloads/rechecks; [schema](../postgres/schema.sql) supplies scoped uniqueness and checks. Provider uses independent transactions in the same local database |
| HTTP extension | Java [protocol](../http/java/src/roo/postgres/HttpProtocol.java) and Rust [protocol](../http/rust/src/lib.rs) translate validated requests to the existing application | Payment/refund IDs provide operation recovery; optional Idempotency-Key must match the body ID. Line POST remains non-idempotent; response loss does not justify whole-command replay |

## Failure and recovery

Rejected lines preserve prior lines/total; empty payment and invalid states reject
before effects. A different payment/refund identity conflicts with retained intent.
Malformed fixtures fail structurally; HTTP validates its representation before
invoking persistence. These are input rules, not requester authorization.

Preparation failure discards the candidate and makes no provider call. Final
commit failure discards candidate state/event, retains Pending or Refunding,
and leaves an independently approved effect intact. Same-key retry or status
reconciliation can finish; successful terminal replay creates no further event.
Unknown and NotFound leave active intent/state unchanged and produce no event.

Cancellation is outside the bounded model. Resource cleanup closes/releases
local transaction resources; it must not erase retained intent or provider keys.
Known-aborted short database transactions may retry under the adapter's bounded
policy; an uncertain COMMIT requires inspection, not blind replay of the command.

A full refund has its own retained identity and recovery sequence. It is an
explicit business operation, not automatic rollback or evidence that arbitrary
external compensation will succeed. No refund is triggered merely by a failed
payment finalization.

The outbox stores the event atomically with the terminal local transition. Relay
send failure leaves it pending; acknowledgement failure can leave a delivered
fact pending for redelivery. Consumer EventId deduplication prevents reapplying
that fact; PostgreSQL uses an independent inbox commit. Delivery/acknowledgement
recovery is separate from provider idempotency and payment finalization.

## Evidence and limits

- Compiler or static analysis: the dated [in-memory validation](../../../research/orders-payments-validation.md) and [negative diagnostics](../../../research/orders-payments-negative-evidence.json) report Java private-access/final-method restrictions and Rust move/borrow/private-access restrictions. These constrain local code; they do not prove remote effect uniqueness.
- Runtime or behavioral evidence: [SPEC](../SPEC.md), shared scenarios, expected rows, and intermediate assertions in Java [UnitTests](../java/src/roo/payments/UnitTests.java) and Rust Application define/check the failure and recovery observations. The 2026-10-11 validation receipt reports all three variants matching 42 oracle rows; this document introduces no new execution evidence.
- Database constraints, transactions, and durability: the [PostgreSQL contract](../postgres/SPEC.md), schema, and adapter sources explain local transaction/lock boundaries. The dated [PostgreSQL validation](../../../research/postgres-validation.md) and [integration receipt](../../../research/postgres-integration-evidence.json) report bounded concurrency, process-crash, and restart observations, not physical-power-loss or external-provider durability.
- Protocol, wire, or remote-boundary behavior: the [HTTP contract](../http/SPEC.md) distinguishes payment/refund recovery from line POST, and the dated [HTTP validation](../../../research/http-validation.md) records response-loss and rejection scenarios. The provider remains a simulator in the same PostgreSQL durability domain, not a payment network.
- Human review and operational assumptions: historical [in-memory review](../../../research/orders-payments-review.md), [PostgreSQL review](../../../research/postgres-review.md), and [HTTP review](../../../research/http-review.md) concern their frozen candidates. They do not accept this new proposed ADR or authorize production migration.
- Sources and established precedent: [architecture-decision template](../../../templates/architecture-decision.md), [relationship worksheet](../../../templates/relationship-contract.md), and the existing [source ledger](../../../research/orders-payments-sources.md) ground this record. Source-specific provider precedents are not universal provider guarantees.
- Remaining assumptions, untested properties, and risks: no new tests, builds, network calls, or database work accompany this documentation. Exhaustive interleavings, production scale, authorization, real-provider consistency/retention, and successful external compensation remain unproved. One terminal payment and one full refund per order are teaching restrictions.

## Consequences

The policy makes partial success observable, preserves recovery identity, and
keeps state/event agreement local. It costs retained intent/provider/event facts,
recovery paths, and adapter-specific coordination; language access rules do not
remove these obligations.

Adopt one vertical slice first: document its invariant and eight fields, map its
actual provider contract, preserve one immutable intent through prepare/effect/
finalize, and use independent expected observations plus intermediate failure
checks before considering broader use. The [design review](design-review.md)
records the review questions; test success alone does not accept the tradeoff.

Documentation rollback can remove or supersede this proposed record without
changing frozen sources or historical receipts. A future production rollback
needs its own reviewed plan: stop new effects if necessary, retain committed
intents and provider/inbox/outbox facts, inspect uncertainty, and route recovery
through the same identities. Never “roll back” by deleting intents or inventing
replacement keys. No production migration, deployment, or approval history is
asserted by this adoption example.
