# 2. Relationship design: from arrows to enforceable contracts

A diagram shows connectivity. A Relationship Contract describes what each
connection permits, retains, and risks. This chapter is the **canonical
definition** of the ROO contract, compact notation, and adoption procedure.
Other chapters apply it; they do not define alternative versions.

Write a contract when a relationship crosses a **lifecycle, process,
transaction, or trust boundary**, or carries an invariant whose coordinator is
unclear. A plain local value with no consequential boundary rarely needs its
own worksheet. Split a contract when access modes have different obligations.

## 2.1 The eight-field Relationship Contract

First name the scenario, relationship/cardinality, allowed and forbidden
outcomes, and the invariant's observation boundary. Then answer these fields:

| Field | Compact key | Required question |
|---|---|---|
| Owner / resource custodian | Custodian | Who retains the state or resource, and who releases it? |
| Stable identity | Identity | What identifies the target across replacement or restart, with what scope, version, reuse, and deletion rules? |
| Invariant coordinator | Coordinator | Which operations and component preserve the invariant when state changes? |
| Authorization | Authorization | Which principal may request each operation, under what policy and revocation rule? |
| Access regime | Access | What may be observed, resolved, changed, copied, shared, or transferred, and which aliases are allowed? |
| Validity horizon | Horizon | When does access expire or an observation become stale in memory, business lifecycle, or freshness terms? |
| Execution domain | Execution | Where are overlapping operations coordinated, including suspension, reentrancy, processes, and transactions? |
| Failure boundary | Failure | Which effects survive rejection, cancellation, or partial failure, and who retries, reconciles, or compensates? |

Custody retains a resource; coordination protects a rule; identity recognizes
an entity; authorization permits a principal to act. Even when one component
fills all four roles, record them separately. Capability possession, a mutable
borrow, and knowledge of an ID are not substitutes for a caller policy.

Use `not applicable` with a reason or `not implemented` with its consequence.
An unknown field is an open design issue. Evidence and assumptions accompany
the eight decisions; they are not additional relationship fields.

**Change from v0.1.0:** the first edition used seven fields and grouped coordination with
caller permission under “Mutation authority.” This edition splits those roles.
The tagged first edition remains available with its original wording.

## 2.2 Compact notation

Use this one-line-per-field format in a PR or ADR. These keys map directly to
the table above; they are review text, not executable syntax.

```text
Relationship: Order -> LineItem [0..n]
Invariant: positive quantity; one currency; checked total
Custodian: Order retains line values until removal or order release
Identity: line identity is local to its order; no independent lifecycle
Coordinator: Order.add/remove/reprice validates before installing changes
Authorization: caller policy is outside this local example and must be supplied
Access: callers read line views; mutation passes through Order operations
Horizon: views end with the operation; submission freezes commercial facts
Execution: one loaded-order coordinator; durable writers need store coordination
Failure: reject an invalid candidate without changing the order
Evidence: private representation, runtime validation, and invariant tests
Open: revisit identity if returns or fulfillment require independent line tracking
```

The [worksheet](../templates/relationship-contract.md) provides a blank form.
A complete [payment-recovery example](../case-studies/orders-payments/adoption/relationship-contract.md)
records the decision before its implementation mappings. The [design case](../case-studies/orders-payments/DESIGN.md) introduces the states and failure outcomes without a toolchain.
Add longer explanations only where a consequential tradeoff needs them.

The [authorization design case](../case-studies/orders-payments/authorization/DESIGN.md)
defines a caller-permission policy with revocation after observation but before
execution. Under that policy, an earlier observation cannot authorize a later
order approval. The [laboratory](../case-studies/orders-payments/authorization/README.md)
provides implementation and test evidence for that selected policy.

## 2.3 The six-step decision procedure

1. **Describe the scenario.** Name the allowed result, forbidden result, relevant
   failure, and state that must agree at a specified observation boundary.
2. **Triage the relationships.** Select lifecycle, process, transaction, and
   trust crossings; separate modes whose obligations differ.
3. **Complete the contract.** Answer all eight fields before selecting types,
   pointers, class hierarchies, locks, or queues. Record unknowns explicitly.
4. **Choose realizations.** Map the decisions to each language, runtime, store,
   and protocol. Compare alternatives against the same invariant.
5. **Check a counterexample.** Try deletion, stale state, duplicate request,
   cancellation after an external effect, or competing updates. Revise the
   contract if the boundary cannot preserve its promise.
6. **Record evidence and decide.** Link checks actually observed and unresolved
   assumptions; accept the tradeoff with its scope or leave the decision open.

A representation decision follows the contract. Compare policies before
selecting language or storage mechanisms:

| Requirement | Relationship policy | Cost or limitation to examine |
|---|---|---|
| Part exists only inside its whole | Whole retains and controls parts | Removal must preserve the whole's invariants |
| Read during one operation | Temporary observation | Provider retention, hidden effects, and freshness |
| Exclusive local update | One updater during the operation | Local exclusivity and caller permission are separate |
| Independent entity or graph edge | Resolve identity through its custodian | Missing targets, reuse, permissions, and versions |
| Independently retained observation | Retain a detached snapshot | Memory independence does not preserve freshness |
| Transfer to another coordinator | Transfer command custody | Rejection, cancellation, and acknowledgement |
| Shared retained data | Define retention and permitted changes | Aliasing, synchronization, cycles, and release |
| One mutation coordinator | Submit commands to a defined execution domain | Capacity, delivery, shutdown, and recovery |

The [Rust mapping](rust-relationship-mapping.md#candidate-representations)
provides concrete language candidates. [Technology selection](technology-selection.md)
asks the corresponding questions about runtimes, stores, and protocols.

## 2.4 Worked commerce relationship matrix

Assume a small ordering application, one currency per Order, local validation before persistence, and an external payment provider.
LineItems belong to one Order; Customers and Payments have independent durable identity.
This baseline design leaves caller policy open. The separate [authorization design case](../case-studies/orders-payments/authorization/DESIGN.md) supplies an operation/revocation policy; it is not a prerequisite for every domain model.
A submitted order retains commercial snapshots needed to explain its historical total.
Events are immutable descriptions of committed transitions, copied or transferred to consumers.
These are teaching assumptions, not universal commerce rules or a production payment design.

| Relationship | Custodian / identity | Coordination, authorization, and access | Horizon and execution | Failure / consistency |
|---|---|---|---|---|
| Order → LineItem | Order owns item values; line ID local to Order if needed | Order coordinates mutation; callers get shared views | Until removal or release; commercial data frozen at submission; local operation | Reject invalid quantity/currency/overflow before installing change; persist aggregate consistently |
| Order → Customer | Order owns CustomerId and checkout snapshot; customer store owns customer state | Customer service mutates Customer; Order resolves authorized read view | ID may outlive any loaded Customer; snapshot is intentionally historical | Missing/deleted customer has explicit policy; no automatic cascade from Order deletion |
| Order → Payment | Order retains PaymentId/status observation; payment component owns attempt state | Payment component controls charge/capture/refund; Order requests commands | Separate lifecycles; calls can cross tasks/processes | Timeout may mean unknown provider outcome; reconcile using stable attempt identity |
| Payment → Order | Payment stores OrderId and agreed amount snapshot | Lookup or message; no unrestricted mutable back-reference | Durable correlation; caller-policy decision boundary must be stated | Reject amount/version mismatch; handle missing Order according to retention policy |
| Order → Event | Order operation produces event value; outbox/log takes custody if persisted | Event payload fixed after construction; publisher has delivery capability | Event retention independent of loaded Order | State and outbox require a real transaction if atomicity is claimed; duplicate delivery needs consumer policy |
| Event → Customer/Order/Payment | Event owns copied IDs and minimal necessary facts | Consumer resolves through its authorized API or uses historical facts | Durable fact, potentially stale relative to current state | Missing entity is representable; replay does not imply permission to repeat the original effect |

The matrix shows why Customer navigation needs an access contract and why Payment need not be an Order-controlled mutable child.
Independent retention and failure semantics often make IDs and messages more accurate than long-lived pointers.
In a purely local application with no independent payment lifecycle, an owned Payment value may instead satisfy the actual requirements.
Record the requirement before adopting the teaching model.

An illustrative submission protocol is:

```text
load Order at version v
resolve an authorized Customer view and create needed checkout snapshot
validate Order and calculate checked total
persist submitted Order + payment-attempt request atomically, if supported
send payment request with stable attempt identity
record confirmed result or explicit unknown/pending outcome
publish committed transition events through the delivery mechanism
```

This is pseudocode for responsibilities, not a guarantee supplied by the lab.
Without a transaction joining the persisted Order and request record, there is a failure gap.
Without provider support and a defined deduplication policy, a stable request key alone cannot guarantee one charge.
Local memory mechanisms do not close those store or provider failure gaps.

## 2.5 Cycles and graphs

A cyclic domain graph does not require mutual resource retention. Navigation
can use identity lookup, checked handles, or links whose targets may expire.
If both ends retain each other, specify how the cycle terminates and resources
are released. The [Rust mapping](rust-relationship-mapping.md#cycles-suspension-and-cancellation)
examines concrete reference-counting and handle mechanisms.

When a store reuses positions, a bare position can name a replacement entity.
A checked handle may include store identity, position, and generation. Define
validation, exhaustion, serialization, and missing-target outcomes; a local
handle is not automatically a durable identifier.

Deletion also needs an edge policy: reject while referenced, remove incoming
edges, retain a tombstone, or allow a representable missing target. Memory-safe
lookup can still violate a business rule. Specify traversal limits, cycle
detection, and overlapping mutation where the graph requires them.

## 2.6 Lifecycle boundaries are not transaction boundaries

A business lifecycle defines when a participant may exist or change. A local
resource scope defines retention in one execution. A transaction defines which
changes become visible together under an actual storage contract. Align them
only when the implementation makes that alignment true.

Releasing a loaded Order does not delete stored state or undo a provider
charge. Exclusive local access does not coordinate another process updating
the same order. Choose a durable coordination protocol for that boundary.

For a rejected transition, state whether the original input is returned,
retained unchanged, partially changed, or consumed. If repair and retry are
required, preserve enough state to support them. A detached candidate can keep
validation separate from installation; the store must still establish its
claimed commit behavior.

## 2.7 Suspension, concurrency, and reentrancy

At each wait or handoff, identify retained state, active guards, and capabilities.
An operation may remain memory-valid while its business facts or permissions
change. Revalidate at the boundary named in the contract.

Keep slow external work outside local guards when the design permits it.
Holding a guard across external work requires a latency, cancellation, and
contention policy. Cancellation can end local execution after a remote effect
succeeded; retain and recover an explicit uncertain result.

A lock coordinates only participating access. Specify lock order and callback
reentrancy. A sequential coordinator still needs policies for queued work,
retries, shutdown, and partial external success. Platform threading and async
rules belong in the [implementation guides](implementations.md).

For authorization, name the principal, operation, policy, decision point, and
ordering with revocation. State what an earlier observation permits, what an
accepted operation may finish after revocation, and how recovery is authorized.
Rechecking every local transaction is one [reference policy](../case-studies/orders-payments/authorization/DESIGN.md),
not a universal requirement imposed by the method.

## 2.8 The evidence ledger for invariants

Attach evidence at the boundary enforcing the claim. Keep language checks,
runtime checks, storage guarantees, protocol behavior, and human review
separate. Unverified expectations remain assumptions.

| Claim | Enforcement boundary | Evidence and unresolved assumptions |
|---|---|---|
| Access ends with a declared scope | Language/runtime API | Applicable static or runtime checks; unsafe escape paths |
| Only legal transitions are exposed | Domain API | Encapsulation review and allowed/rejected transition tests |
| A handle identifies its original target | Custodian lookup | Scope, generation/reuse checks, and exhaustion policy |
| Overlapping updates preserve the invariant | Actual execution/store coordinator | Controlled competing-update scenarios and coordination contract |
| Revocation orders with protected effects | Policy/effect decision boundary | Observation/revocation/execution scenarios and retained-effect checks |
| Recovery does not add another charge | Durable intent and provider boundary | Original fingerprint, provider lookup/deduplication contract, failure scenarios |
| State and event become visible together | Selected commit boundary | Documented atomicity plus failure/restart evidence |

The [Rust evidence mapping](rust-relationship-mapping.md#rust-evidence-and-its-boundary)
shows what a particular compiler can contribute. A successful compilation or
selected test is evidence for its checked property and candidate, with its
stated limits. It cannot certify unrelated storage, policy, or remote behavior.

## 2.9 Review exit criteria and open questions

A relationship is ready for implementation when all eight fields have concrete answers and important invariants have named enforcement mechanisms.
A relationship is ready for production only after its real persistence, authorization, execution, and failure assumptions have been verified in that environment.
This edition's local lab cannot establish those production properties.

Open evaluation questions include how much notation teams will maintain, how contracts should evolve with schema versions, and which review metrics predict reduced defects.
The initial convention is to document significant relationships rather than every scalar field, and to update their contracts when custody, coordination, authorization, or failure behavior changes.
Evaluate ROO by whether another engineer can predict an operation's effects and failure outcomes from the contract and API.
Use that evaluation to improve the method without claiming that compilation alone validates the architecture.
