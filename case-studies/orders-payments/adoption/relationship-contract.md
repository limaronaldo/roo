# Relationship Contract worksheet: payment finalization recovery

Filled from the [relationship worksheet](../../../templates/relationship-contract.md).
Use with the [adoption guide](../../../docs/09-adoption-guide.md),
[architecture decision](architecture-decision.md), and [design review](design-review.md).
This is new documentation based on inspected source and existing evidence;
authoring this worksheet does not execute or requalify the example.

ROO (Relationship & Ownership Oriented design) is language-independent: begin
with the scenario and invariant before choosing types, APIs, storage, or
synchronization. Resource custody, domain responsibility, stable identity,
and authorization are separate decisions throughout this worksheet.

## Context

- Scenario or operation: the shared `recover_commit` row in
  [scenarios.tsv](../scenarios.tsv):
  `add:100:2;add:50:1;pay:p1:approve:commit;reconcile:ok:none`.
  Each in-memory scenario begins with a fresh Draft `O1`, store, provider,
  outbox, and consumer; the two additions total 250 minor units in USD.
- Expected outcome, forbidden outcome, and relevant failure: persist payment
  intent `p1` and Pending before the provider effect. Approval followed by the
  injected terminal commit failure leaves committed Pending, one independent
  charge, and zero events (`LocalCommitFailed`). Reconcile the same persisted
  `p1` to reach Paid, still one charge, and exactly one `payment:p1`
  PaymentApproved event. Never advertise uncommitted Paid, charge under a new
  key to recover, or install the candidate event after a failed commit.
  These are specified/source behaviors and the existing oracle's expected
  outcomes, not observations produced by this worksheet.
- Relationship: `Source → Target` (cardinality): a small group governed by this
  payment invariant: `Coordinator → LocalStore` (one configured capability)
  and `Coordinator → RemoteProvider` (one configured capability). The affected
  aggregate relationships are `Order → payment intent/state` (zero or one
  intent; one current state) and `Order → terminal outbox facts` (zero or more
  facts, with exactly one fact per terminal intent transition). Relay to
  consumer/inbox crosses a separate delivery/acknowledgement boundary.
- State that must agree and the invariant it must preserve: frozen order
  total and immutable intent agree on `(PaymentId=p1, OrderId=O1, USD, 250)`.
  Local terminal status and its event install together. Provider approval may
  exist while local state remains Pending; reconciliation closes that gap
  without another effect. There is no atomic commit spanning local store and
  provider, nor spanning outbox acknowledgement and consumer application.
- Domain responsibility / invariant coordinator: which participant decides changes that must preserve the invariant?
  The application coordinator orders prepare, provider interaction, and
  finalization. Domain operations validate legal state changes and create
  terminal facts; store/provider adapters implement their separate commit and
  identity contracts. Holding a resource does not authorize arbitrary changes.
- Value, entity, resource, service, or event; independent lifecycle, if any:
  Order is an entity; Money and request fingerprints are values; local store
  and provider are independently retained resources behind services; outbox
  entries are immutable historical events with separate acknowledgement state.
  An event can remain after the active coordinator invocation ends.

The [shared specification](../SPEC.md) defines the bounded state machine;
[expected.tsv](../expected.tsv) retains `commit_failure` and `recover_commit`
as separate final observations so a successful recovery does not erase the gap.

## Seven fields

| Field | Language-neutral decision | Questions to answer |
|---|---|---|
| Owner / resource custodian | The scenario fixture retains the in-memory store, provider, and consumer. The store retains committed Order and outbox/ack state; provider retains its independent complete typed key records and effect counts; consumer retains applied identities/facts. The coordinator uses these capabilities and detached working candidates. PostgreSQL adapters retain records through the database and own/close each short connection/transaction. Custody does not confer domain or caller authority. | Who retains the resource and handles its local lifecycle, release, or cleanup? Custody does not by itself grant authority to change domain state. |
| Stable identity | Distinct OrderId, PaymentId, RefundId, and EventId concepts are preserved. This recipe uses O1, p1, and payment:p1. A provider key recognizes the full immutable request, including order, currency, amount, and operation kind; refunds additionally bind parent payment. PostgreSQL/HTTP add scope to identity. Matching key with changed fingerprint conflicts; identifiers are not addresses. No replacement payment, key reuse after deletion, expiry, or identity versioning is modeled. Records remain for the fresh in-memory scenario or until explicit persistent-harness cleanup. | Does the target need an identity beyond its current value or lifetime? If so, state its scope, version, reuse, and deletion rules. A reference or storage address is not durable identity. |
| Mutation authority | Coordinator commands request validated domain transitions, and adapters install committed results. Prepare freezes lines and intent before provider execution; finalization installs terminal state and copied event together. Provider alone records its simulated independent effect; consumer alone applies delivered facts. Public observers cannot arbitrarily replace aggregate state. Permission to request a command is a separate, unmodeled authorization decision. | Which operation changes state, and who is responsible for preserving the invariant at that transition? Record who may request it as a separate authorization decision. |
| Access regime | Observe committed values/snapshots, create detached candidates, request commits and provider changes, and transfer copied request/event facts. Do not retain mutable aliases to committed state or hold an order view through candidate replacement. The baseline is single-threaded; persistent writers coordinate through locked/revalidated rows rather than sharing mutable order objects. | What interaction is required: observe, resolve, request a change, share state, or transfer facts? Which aliases or overlapping access are allowed? Defer language mechanisms to realization. |
| Validity horizon | A candidate is valid only for its local operation and cannot represent a failed commit as committed truth. Immutable intent remains meaningful through Pending and recovery; snapshots remain historical observations and need not stay fresh after return. Borrow/reference lifetime is distinct from business state and freshness. The in-memory retention horizon is one scenario, with no restart durability. Persistent scopes survive only within the separately documented database contract/evidence. Cancellation/revocation are outside the case. | When is access valid, stale, or revoked? Distinguish memory lifetime, business lifecycle, freshness, and cancellation. |
| Execution domain | In-memory coordination is one deterministic thread/process. PostgreSQL prepare and finalize use separate short app transactions with order-row serialization; the provider uses an independent connection/transaction and per-scope advisory exclusion. No app transaction spans its provider call. HTTP handlers own validated input/invocation and use the existing transactional workflow, with bounded admission. Relay deliberately holds the app row lock across its small independent local inbox transaction; this is a separate simulator tradeoff. | Where must overlapping operations be coordinated: one operation, task or thread, process, service, or transaction? |
| Failure boundary | Failed preparation precedes any effect. Failed finalization discards local candidate state/event while provider approval survives. Unknown does not mean decline or no effect; NotFound is distinct and authoritative only under the simulator's complete retention contract. Recovery reads persisted intent and reuses p1. Outbox send/ack failure leaves independently committed consumer facts available for deduplicated redelivery. HTTP loss or uncertain database COMMIT is not proof of rollback; never blindly replay the whole command. | Which effects may survive failure? Who handles rollback, compensation, retry, cancellation, uncertainty, or redelivery? |

## Supporting decisions

- Authorization: who or what may request each operation, its scope, and how permission is checked or revoked:
  No user, tenant, permission check, or revocation model is implemented. Fixture
  validation and loopback/scope restrictions are input/environment constraints,
  not authorization. A real service needs a separate caller policy.
- Creation, replacement, deletion, release, and cleanup responsibilities:
  Fixture setup creates fresh in-memory resources. Store commit replaces only
  validated detached state on success; failed candidates are discarded.
  Provider and event records are not evicted within a scenario. Persistent
  harness setup/cleanup owns synthetic scopes and cluster lifecycle; adapters
  close short transaction resources. HTTP initialization preserves an existing
  scope instead of resetting it. Business deletion/retention policy is unmodeled.
- Reverse navigation: is it needed, and who maintains the relation or index?
  Recovery follows the order's stored intent to the provider, not a back-pointer
  to the coordinator. Typed provider maps/records resolve operation identity;
  the store maintains ordered outbox records/ack flags and consumer maintains
  deduplication records. No live reverse object relation is required.
- Identity resolution: behavior for a missing, stale, version-mismatched, or unauthorized target:
  Missing provider record yields NotFound; unavailable lookup yields Unknown;
  changed request content yields KeyConflict; a different active payment ID
  yields IntentConflict. Persistent/HTTP missing scope is a distinct boundary
  error. Version mismatch and unauthorized lookup have no modeled result.
- Consistency: which state must agree, and at what observation boundary (local invariant, transaction, eventual agreement, or snapshot)?
  Order lines/total/state/intent obey local domain checks. Terminal state and
  outbox fact agree at local commit. Provider/local state and delivery/ack may
  disagree temporarily and converge only when explicit recovery succeeds.
  A PostgreSQL snapshot is consistent at its read boundary, yet a response can
  include another worker's later commit; it is not an atomic command receipt.
- Boundary crossing: which facts or identities cross a process, persistence, or wire boundary?
  Immutable payment/refund request fingerprints and copied event facts cross
  logical adapter boundaries. PostgreSQL persists scoped identities and facts;
  HTTP carries validated identity/numeric strings and snapshot values, never
  live Order references. Optional Idempotency-Key equals the body operation ID;
  it does not create a generic response cache or command receipt.
- Cancellation and retry: which state and resources remain, and is repetition idempotent?
  Cancellation is outside scope. Retry/reconcile uses retained p1, never a new
  intent. Same-key provider requests compare the full immutable fingerprint;
  local terminal no-ops add no event. Relay redelivery applies no duplicate
  consumer effect. Line addition is explicitly non-idempotent: HTTP line POST
  has no durable replay receipt and uncertain completion requires inspection
  and a caller decision, not automatic replay.
- Resource budget: queue capacity, retained snapshots, lock duration, allocation, and cleanup limits:
  Baseline maps/outbox and candidate copies grow with the bounded fixture; no
  general capacity/eviction policy is claimed. The persistent adapter bounds
  transaction/connection waits and known-abort retries; app locks end before
  provider access. HTTP admits at most 16 database-bearing operations; Java
  has 32 workers and queue capacity 64, Rust at most 16 blocking workers.
  These configured bounds do not establish production capacity or latency.

## Optional realization and enforcement

Neutral decisions above precede these choices. A database foreign key does not
determine an in-memory representation, and no Rust representation is required.

| Candidate realization | What it may express | Cost or obligation | Selected? |
|---|---|---|---|
| Embedded owned value | Store's committed aggregate and copied immutable request/event facts. | Retain validated total/state together; copy candidate facts without making provider effects part of local ownership. | Yes, within the local aggregate/store boundary. |
| Temporary shared or exclusive view | Short observation or command access to independently retained capabilities. | End stale views before replacement; coordinate overlapping mutations at the actual execution boundary. | Yes; Java capability calls and Rust borrows realize this differently. |
| Stable ID and resolver | Persisted p1 identifies recovery independently of a coordinator object's lifetime. | Scope and type the key; compare full immutable fingerprints; define retention and missing/unknown behavior. | Yes, for intent/provider/event recovery. |
| Independent snapshot or copy | Detached candidate, copied request, immutable event, and returned snapshot. | Allocation/copy cost; a snapshot is not guaranteed fresh and a failed candidate is not committed truth. | Yes, explicitly. |
| Owned message or command | Copied request/event facts crossing an adapter or delivery boundary. | Retention, deduplication, and send/ack recovery remain explicit; a broker requires a separate contract. | Yes for facts/requests; a message queue is not required or introduced by this recipe. |
| Explicit shared ownership and coordination | Potential common access to a long-lived capability. | Requires a real alias/synchronization policy; shared retention alone cannot enforce payment invariants. | Not required for baseline resources; HTTP may share immutable configuration/stateless adapters while database locks coordinate state. No Rc/Arc-style shared aggregate is prescribed. |

## Cross-language interpretation

Keep relationship decisions stable while allowing platform-specific mechanisms.

| Language, runtime, store, or protocol | Realization chosen | Enforcement and limits |
|---|---|---|
| Java composition | [CompositionApplication](../java/src/roo/payments/CompositionApplication.java) receives final StorePort and ProviderPort references; [Adapters](../java/src/roo/payments/Adapters.java) supply detached load/commit and independent typed-key maps. | [Domain](../java/src/roo/payments/Domain.java) private mutation and immutable records restrict arbitrary updates; coordinator fixes prepare/reload/call/finish ordering. References and encapsulation do not establish restart durability or authorization. |
| Java Template Method | [TemplateApplication](../java/src/roo/payments/TemplateApplication.java) fixes public final algorithms and private finalization; protected store/provider hooks return stable adapters for the coordinator lifetime. | Subclasses supply capabilities under the same port contracts, without reordering public orchestration. Stable hook behavior is a documented obligation; inheritance does not replace provider or commit contracts. |
| Rust composition | [Application<'a>](../rust/src/application.rs) temporarily exclusively borrows Store, Provider, and Consumer. It clones persisted request facts before provider mutation; [adapters](../rust/src/adapters.rs) own committed candidates/maps and [domain](../rust/src/domain.rs) owns transition rules. | Borrow checking limits overlapping local access and escape; detached candidates/copies avoid a cached mutable Order across calls. Runtime state/identity checks remain necessary; borrowing cannot roll back a remote effect. |
| PostgreSQL adapters | [Java coordinator](../postgres/java/src/roo/postgres/CompositionApplication.java), [Store](../postgres/java/src/roo/postgres/Store.java), and [persistent contract](../postgres/SPEC.md) split prepare, provider effect, and finalize into short independent transactions. | Locked fresh rows and full-request revalidation handle concurrent changes; terminal state/outbox commit atomically. Independent provider/inbox records share one database/WAL domain. Snapshot consistency is distinct from freshness and command receipt semantics. |
| HTTP boundary | [HttpService](../http/java/src/roo/postgres/HttpService.java) validates per-request input and invokes existing application adapters; [HTTP contract](../http/SPEC.md) defines natural-key retry/reconcile and bounded workers. | Transport does not duplicate domain orchestration. Lost responses require same-identity recovery; line POST has no durable receipt. A returned snapshot may include a later worker's commit, and matching retries need not return identical responses. |

## Observed evidence

This worksheet's direct observation is source/document inspection. The dated
receipts below report earlier integrator runs on 2026-10-11; they are historical
evidence with their original scope, not a new run or a proof of every schedule.

- Compiler or static analysis: inspected Java private/final boundaries and Rust
  borrowed capabilities above. Existing [in-memory validation](../../../research/orders-payments-validation.md)
  and [negative diagnostic receipt](../../../research/orders-payments-negative-evidence.json)
  report intended compiler restrictions. Those restrictions do not prove effect
  uniqueness, distributed atomicity, or caller permission.
- Runtime or behavioral scenario: inspected `recover_commit`, `commit_failure`,
  and the [oracle](../expected.tsv); [Rust application test source](../rust/src/application.rs)
  asserts the intermediate Pending/one-charge/zero-event gap and recovery.
  The dated in-memory validation reports shared oracle execution across three
  variants; this worksheet has not rerun them.
- Database or transaction behavior: inspected persistent Store transaction code
  and the [PostgreSQL specification](../postgres/SPEC.md).
  [Dated validation](../../../research/postgres-validation.md) and
  [integration receipt](../../../research/postgres-integration-evidence.json)
  separately record lock witnesses, process recovery, and PostgreSQL immediate
  restart/WAL recovery. In-memory retention supplies none of that durability.
- Protocol or boundary behavior: inspected HTTP dispatch/recovery contracts;
  [dated HTTP validation](../../../research/http-validation.md) and
  [integration receipt](../../../research/http-integration-evidence.json)
  record real loopback response-loss and recovery schedules, including the
  deliberate second line POST demonstrating the absent replay receipt.
- Human review or operational decision: this filled worksheet records an
  adoption decision for one bounded recipe. The sibling architecture decision
  and design review capture its rationale/questions; the historical
  [HTTP review](../../../research/http-review.md) is a separate earlier
  candidate review. No new runtime acceptance or production decision is implied.

## Remaining assumptions and open questions

- Assumptions, unverified claims, and unresolved decisions: provider retention,
  full-fingerprint comparison, and authoritative NotFound are simulator
  contracts; external-provider equivalents need independent documentation and
  evidence. Authorization, cancellation, replacement intents, deletion/expiry,
  real payment networks, physical power-loss survival, exhaustive interleavings,
  production throughput, and operational capacity remain outside this recipe.
  A durable replay-safe line command would need a separate atomic
  line/fingerprint/receipt design. None of these bounded unknowns prevents
  using this worksheet to review the existing recovery protocol.
