# Adopt ROO one operation at a time

ROO means **Relationship & Ownership Oriented design**. Use it as a
language-independent design method: define an operation and its invariant,
decide the relationships that preserve it, then choose representations and
enforcement mechanisms. An existing Java or Rust project can adopt this method
without changing language, framework, or its whole architecture.

This guide follows one decision through the orders/payments case: persist a
stable payment intent before asking the provider to charge, then recover local
finalization using that same intent. Read the filled artifacts alongside it:

- [Relationship Contract](../case-studies/orders-payments/adoption/relationship-contract.md)
- [Architecture decision](../case-studies/orders-payments/adoption/architecture-decision.md)
- [Design review](../case-studies/orders-payments/adoption/design-review.md)

For your own operation, copy the original [Relationship Contract worksheet](../templates/relationship-contract.md),
[architecture decision template](../templates/architecture-decision.md), and
[design review template](../templates/design-review.md). The filled examples
are a worked decision, not a prescription to build a payment service.

## 1. Choose an operation and a consequential failure

Choose one operation whose partial failure matters to a caller. “Improve our
object model” is too broad. “Recover a charged order when the final local commit
fails” gives you participants, observations, and a testable forbidden outcome.
In another project, this might be reserving inventory or publishing a document.

Use the [shared specification](../case-studies/orders-payments/SPEC.md) and
the actual `recover_commit` row in [scenarios.tsv](../case-studies/orders-payments/scenarios.tsv):

```text
add:100:2;add:50:1;pay:p1:approve:commit;reconcile:ok:none
```

Each row starts fresh with order `O1`, fixed currency `USD`, and independent
store, provider, outbox, and consumer state. Amounts are integer minor units:
the two additions total 250, or USD 2.50. `commit` injects failure of the final
local commit; it does not undo the provider's charge.

Write the behavior before drawing classes:

| Question | Decision for this operation |
|---|---|
| Required outcome | Reconciliation reaches Paid using persisted intent `p1`. |
| Allowed intermediate outcome | Pending with one remote charge and no terminal local event. |
| Forbidden outcome | A second charge, a changed intent, or a committed Paid order without its terminal event. |
| Observation boundary | Committed local snapshot and independently retained provider effects; never an uncommitted candidate. |
| Recovery | Look up the same persisted intent and finalize once. |

Unknown remote work is also a legitimate intermediate outcome. A timeout does
not establish failure of the effect. Keep `Unknown` separate from an
authoritative `NotFound`; the simulator can establish absence only because its
provider map is complete for that fresh scenario.

## 2. Name participants and responsibilities

Name the domain invariant coordinator before choosing an interface or trait.
Here the application coordinates preparation, remote observation, and local
finalization. The order's domain transitions enforce state and amount rules;
the store installs committed snapshots and events together.

| Participant | Responsibility in the selected operation |
|---|---|
| Order and lines | Validate positive amounts/quantities, checked totals, and legal transitions; freeze lines after intent preparation. |
| Application coordinator | Preserve protocol ordering and keep retries bound to the stored intent. |
| Store | Retain committed order/outbox; reject failed candidate commits without installing either. |
| Payment intent | Carry immutable PaymentId, OrderId, currency, and amount facts. |
| Provider | Retain full request fingerprints and terminal results; own its independent effect. |
| Event/outbox | Retain copied terminal facts identified by `payment:p1`. |
| Consumer | Apply each unique EventId once. |

Separate four questions that often get collapsed into “ownership”:

- **Custody:** the store retains the committed snapshot; the provider retains
  charge records. Memory retention and cleanup are local responsibilities.
- **Identity:** `O1`, `p1`, and `payment:p1` identify different domain concepts.
  An object reference, memory address, or database connection is not that identity.
- **Mutation authority:** domain transitions and the coordinator decide legal
  changes; having a reference to a store must not enable arbitrary status writes.
- **Authorization:** which customer or operator may request pay or refund is
  a separate product/security policy. This synthetic case does not implement it.

A request scope or synthetic database scope is not an authorization boundary.
Record the missing authorization decision explicitly in a real adoption.

## 3. Fill all seven relationship fields

For the relationship **application → persisted payment intent → provider**,
complete each field with an operational decision. A language keyword is not a
sufficient answer. Split contracts if relationships have different lifecycles
or failure rules; order/lines and event/consumer deserve their own analysis.

| Field | Filled decision for payment recovery |
|---|---|
| Owner / resource custodian | Store retains the intent with Pending; provider independently retains its complete key record and charge. Coordinator uses both capabilities. |
| Stable identity | PaymentId `p1` names the operation; request fingerprint includes OrderId `O1`, USD, and 250. EventId is deterministically `payment:p1`. Never substitute a new key during recovery. |
| Mutation authority | Domain transitions validate changes; application orders preparation and finalization; store commits the local invariant. Provider alone decides and records its effect. Caller authorization remains separate. |
| Access regime | Work on a detached candidate, read the committed intent, send immutable request facts, and return explicit observations. Callers receive snapshots or read-only values rather than mutable order internals. |
| Validity horizon | Candidate observations can become stale after a commit. Intent facts stay fixed once prepared. In-memory provider records last for the entire scenario, with no expiry; this is not restart durability or a real provider retention policy. |
| Execution domain | Base case is one single-threaded scenario. PostgreSQL adds per-order transaction coordination; HTTP adds overlapping requests using that database authority. |
| Failure boundary | Prepare failure precedes the charge. Final local commit failure preserves Pending and the independent charge. Reconcile or same-key retry repairs local state; event delivery has a later acknowledgement gap. |

Add supporting decisions: who creates and deletes records, how stale or missing
identities resolve, which facts cross boundaries, and how long records are
retained. In a live system, key retention and operational handling of unresolved
intents are requirements, not implementation trivia.

## 4. Compare alternatives before choosing mechanisms

The neutral decision is **persist intent, perform independent effect, finalize
state plus event, recover by stable identity**. Evaluate alternatives against
the forbidden outcomes and extension needs.

| Alternative | What must be justified |
|---|---|
| Charge first, invent intent later | A lost response can leave an effect with no stable local recovery identity; reject for this contract. |
| Persist intent, then independent charge and local finalization | Selected: explicitly represents uncertainty and supports same-intent recovery; needs provider idempotency and reconciliation policy. |
| One transaction around everything | Local state and event can share a transaction; this provider effect and consumer inbox commit independently. A wrapper transaction does not make them atomic together. |

After selecting the relationship policy, compare ways to realize it. These
code shapes can preserve the same policy; choosing one does not settle the
provider's retention or recovery contract.

| Realization option | What must be justified |
|---|---|
| Constructor-injected composition | Makes adapter selection explicit; implementations must honor detached commit and provider request contracts. |
| Template Method coordinator | Legitimate reuse when a shared final algorithm varies only stable store/provider hooks; subclasses must obey those hook contracts. |
| Shared mutable application object | Requires a defined coordination regime; a shared reference alone does not preserve the invariant under overlap. |

Record why the selected policy fits this operation and what would change it.
For example, provider key expiry may require an operational cutoff and manual
resolution. A partial-refund requirement changes the bounded domain contract;
it is not just another adapter implementation.

## 5. Walk the same decision through Java and Rust

Read these symbols in order. Keep the behavioral contract stable while allowing
the languages to use different type and reuse mechanisms.

| Decision | Java realization | Rust realization |
|---|---|---|
| Restrict order mutation | [`Domain.Order`](../case-studies/orders-payments/java/src/roo/payments/Domain.java) has private state/transitions; package-level `Domain.add`, `preparePayment`, and `finish` support coordination. | [`Order`](../case-studies/orders-payments/rust/src/domain.rs) has private fields and crate-scoped transitions such as `prepare_payment` and `finish_payment`. |
| Distinguish identity and facts | `OrderId`, `PaymentId`, `RefundId`, `EventId`, `PaymentRequest`, and `Event` are distinct records/types in `Domain.java`. | Separate identity newtypes, `PaymentRequest`, and `Event` in `domain.rs` carry owned facts. |
| Compose capabilities | [`CompositionApplication`](../case-studies/orders-payments/java/src/roo/payments/CompositionApplication.java) injects `StorePort`/`ProviderPort`; final public `add`, `pay`, `refund`, and `reconcile` fix the orchestration. | [`Application<'a>`](../case-studies/orders-payments/rust/src/application.rs) holds exclusive mutable borrows of `Store`, `Provider`, and `Consumer`. |
| Reuse the algorithm through inheritance | [`TemplateApplication`](../case-studies/orders-payments/java/src/roo/payments/TemplateApplication.java) has final public algorithms, private `finish`, and protected `store()`/`provider()` hooks whose adapters must remain stable. | No matching class hierarchy is needed; the composed coordinator preserves the same invariant. |
| Commit candidate state | [`Adapters.Store.load` / `commit`](../case-studies/orders-payments/java/src/roo/payments/Adapters.java) detach and install snapshots; failed commit installs neither terminal state nor event. | [`Store::candidate` / `commit`](../case-studies/orders-payments/rust/src/adapters.rs) clone and replace a candidate containing order and outbox. |
| Use committed intent | `pay` reloads the store after preparation, then calls `ProviderPort.charge` with `persisted.payment()`. | `pay` clones the persisted `PaymentRequest` before `Provider::pay`; no cached mutable Order spans the effect. |
| Recover and deliver | `reconcile` observes the provider; private `finish` commits state/event; `Store.relay` and `Consumer.accept` handle delivery identity. | `reconcile` and private `finish` do the corresponding work; `Store::relay` and `Consumer::deliver` handle copied event facts and deduplication. |

Java encapsulation and final methods restrict ordinary callers/subclasses;
they do not establish that every port implementation is correct. Rust borrowing
checks local access and aliasing for these safe references; it does not decide
whether a provider charge occurred or make multiple commits atomic.

The same invariants do not require identical type hierarchies. Keep a valid
Template Method if it supplies needed algorithm reuse and controlled variation;
choose composition where injected capabilities express the extension point
more clearly. Do not rewrite an existing Java system into Rust to adopt ROO.

## 6. Trace the failure, including intermediate assertions

The oracle's final row is necessary but insufficient: later success can hide
an earlier broken state. Trace `recover_commit` at each boundary:

| Boundary | Required local observation | Independent effect / result |
|---|---|---|
| After the two adds | Draft; total 250; no payment intent; no events | No charge. |
| After preparation | Pending; immutable intent `(p1, O1, USD, 250)` committed | Provider has not yet been called. |
| After provider approval | Local committed state is still Pending | Provider records approval and one charge for `p1`. |
| After injected final commit failure | Pending; payment ID `p1`; event_count 0; pending_outbox 0 | charge_count 1; result `LocalCommitFailed`. |
| After `reconcile:ok:none` | Paid; same `p1`; event_count 1; pending_outbox 1 | Still one charge; result `Approved`. |

The terminal event is `PaymentApproved`, ID `payment:p1`, carrying copied
order/payment/amount facts. Consumer count remains zero because this scenario
does not relay. Refund count is zero and refund ID is absent (`-`).

Compare the separate `commit_failure` and `recover_commit` rows in
[expected.tsv](../case-studies/orders-payments/expected.tsv). Inspect
[`UnitTests.java`](../case-studies/orders-payments/java/src/roo/payments/UnitTests.java)
and `terminal_commit_failure_keeps_pending_without_candidate_event` in
[`application.rs`](../case-studies/orders-payments/rust/src/application.rs)
for assertions at the failure boundary, rather than inferring it from the final
successful row. The provider's effect survives because it belongs to a separate
failure boundary. A later refund is compensation with its own intent and event,
not rollback of the historical charge.

## 7. Extend the reasoning across persistence and HTTP

Move to the [PostgreSQL contract](../case-studies/orders-payments/postgres/SPEC.md)
when the claim involves overlap, process death, or restart. It uses short app
transactions with the order row locked/reloaded; releases the app lock before
provider calls; and revalidates the persisted intent during finalization.
Provider records and consumer inbox use independent transactions/connections.
Terminal local state and outbox event share an app transaction. All these
transactions do not become one transaction because they share a database server.

For a lost connection around COMMIT, distinguish known abort from uncertain
commit. Reopen and inspect durable state; reconcile or retry the same payment
identity. Do not replay the whole multi-transaction command. An uncertain add
needs inspection because it lacks a durable command identity. Recorded process,
database restart, and WAL recovery checks support only their examined setup;
they do not prove hardware power-loss survival or a real payment network.

At the [HTTP boundary](../case-studies/orders-payments/http/SPEC.md), each
request owns validated input and its invocation. Handlers reuse the domain and
transactional application instead of reproducing payment logic. Database row
locks coordinate overlap; a global application mutex would conceal the intended
database schedules. Immutable configuration may be shared; live transactions,
connections, cursors, and mutable orders are not shared between requests.

Lost responses do not prove rollback. Inspect with GET, retry payments/refunds
with the **same** operation identity, and explicitly reconcile Pending/Refunding.
The optional payment/refund `Idempotency-Key` must equal the body ID. It supplies
natural-key idempotence, not a response cache: retries need not return the same
outcome or byte-identical JSON. HTTP 202 for domain Unknown/NotFound promises no
background worker. Missing scope is HTTP 404, a different meaning of not found.

Line POST is deliberately non-idempotent: two successful identical requests
append twice. After response loss, inspect and make a caller-controlled decision;
GET total alone is not a command receipt under concurrency. A future replay-safe
line API needs line, full command fingerprint, and receipt committed atomically.

## 8. Practice with bounded review questions

Answer before reading the relevant source. These are reading/review exercises;
the listed expectations are contract targets, not reports of new executions.

Implement these decisions in the [executable adoption track](../case-studies/orders-payments/track/README.md).
It supplies separate Java/Rust starter and solution policies, equivalent tests
for all six groups, and real local PostgreSQL/HTTP failure boundaries. Follow
the [exercise instructions](../case-studies/orders-payments/track/EXERCISES.md)
to progress from an expected behavioral failure to a verified solution.

| Exercise | Inspect | Bounded expected answer |
|---|---|---|
| Reject an add after two valid lines. What survives? | Base SPEC, `Order.add`, unit snapshot assertions; `valid_after_invalid` covers the opposite ordering. | Invalid/overflowing candidate preserves all previous lines and total 250. Final TSV totals alone do not prove line preservation. |
| Explain `recover_commit` without skipping the failure. | Fixture/oracle, both Java coordinators, Rust `pay`/`finish`. | Pending + one charge + zero events after failure; same `p1` reaches Paid + one charge + one `payment:p1` event. |
| Compare same-key retry, another intent, and changed fingerprint. | `retry_same_key`, `intent_conflict`, `key_conflict`, provider code. | Matching request reuses result/effect; `p2` conflicts with active intent; recorded `p1` with changed amount returns KeyConflict. The direct conflict probe is test-only. |
| Lose the relay acknowledgement after delivery. | `relay_ack_failure`, `duplicate_delivery`, relay/consumer code. | One consumed event remains pending; redelivery leaves consumer count one and successful acknowledgement clears pending. |
| Overlap pay/add, or lose the finalization process. | PostgreSQL SPEC and its documented harness/evidence. | Order locking/revalidation controls overlap; a fresh process recovers committed intent/effect. Unknown COMMIT requires inspection, not assumed rollback. |
| Lose a payment response, then lose a line response. | HTTP SPEC and its documented harness/evidence. | Same payment ID avoids another effect; blindly replaying line POST can append twice. 202 requires explicit caller recovery. |

For your operation, replace each row with a real input, expected intermediate
state, forbidden observation, and evidence source. Include cancellation only
with a stated contract: cancellation of a caller does not imply reversal of an
already committed external effect.

## 9. Review evidence and adopt incrementally

Use the [filled design review](../case-studies/orders-payments/adoption/design-review.md)
to challenge the decision, then record evidence by class:

| Evidence class | Appropriate claim | Limit |
|---|---|---|
| Compiler or static analysis | Intended private-access, final-override, move, or borrow restriction is checked. | Does not prove domain behavior, authorization, durable commits, or remote effects. |
| Runtime or behavioral scenario | Selected fixture outputs and intermediate assertions match the contract. | Does not establish unobserved failure points or all interleavings. |
| Database or transaction | Recorded locks, constraints, independent commits, process/restart recovery in the examined setup. | Does not establish real-provider behavior or production readiness. |
| Protocol or boundary | Observed HTTP validation, response loss, retry and rejection behavior. | Schema or compilation alone does not establish these outcomes. |
| Human review or operational decision | Named coordinator, retention policy, authorization, and accepted tradeoffs. | A decision is not execution evidence. |

Start with the [base validation record](../research/orders-payments-validation.md)
and the extension [PostgreSQL README](../case-studies/orders-payments/postgres/README.md)
and [HTTP README](../case-studies/orders-payments/http/README.md) for their
verification procedures and evidence links. Those records describe historical
runs; this guide does not report a new test run. A SPEC states requirements.
A successful build and an executed scenario are different evidence.

Use this small adoption backlog in an existing project:

1. **Choose:** name one operation, failure, allowed/forbidden outcomes, and
   observation boundary. Done when a teammate can predict the failure trace.
2. **Describe:** fill the seven fields and separate custody, identity, mutation
   authority, and authorization. Done when each has a named responsible party.
3. **Decide:** compare viable alternatives and map the policy to existing Java,
   Rust, storage, or protocol mechanisms. Done when extension costs are explicit.
4. **Constrain:** close one bypass or expose one explicit recovery operation.
   Done when callers cannot silently violate the selected invariant through it.
5. **Demonstrate:** add the smallest meaningful scenario and intermediate
   assertions. Done when the forbidden outcome is checked at the failure point.
6. **Review:** classify defects, unverified questions, and optional improvements;
   assign unresolved retention/authorization/operations decisions. Done when the
   accepted scope and evidence limits are recorded in the decision and review.

Expand to adjacent relationships only when their different identity, lifecycle,
coordination, or failure rules require it. The useful result is a reviewable
operation with explicit recovery responsibilities and evidence for its claims.
