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
maps the same decisions to Java composition, Java inheritance, and Rust.
Add longer explanations only where a consequential tradeoff needs them.

The [authorization example](../case-studies/orders-payments/authorization/README.md)
implements the separate caller-permission field in Java and Rust. It tests a
revocation after observation but before execution; the earlier observation
cannot authorize a later order approval.

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

A representation decision follows the contract. The middle column gives language-independent policies; the next column offers Rust realizations:

| Requirement | Relationship policy | Initial Rust candidate | Cost or limitation to examine |
|---|---|---|---|
| Part exists only inside its whole | Whole retains and controls parts | Owned field, `Vec<T>`, or `Box<T>` | Moving/removing the part must respect whole invariants |
| Read during one operation | Temporary observation | `&T` or iterator/view | Provider must outlive access; interior effects may still exist |
| Exclusive local update | One updater during the operation | `&mut T` | Exclusive access does not authorize every business operation |
| Independent entity or arbitrary graph edge | Resolve identity through a custodian | Typed ID plus owner/repository lookup | Existence, stale handles, permissions, and versions need checking |
| Independent retained observation | Retain a separate snapshot | Owned snapshot | Memory independence trades away automatic freshness |
| Transfer to another coordinator | Transfer command custody | Move an owned command/value | Define outcome on rejection and cancellation |
| Shared retained immutable data | Shared retention with immutable content | `Rc<T>` locally or `Arc<T>` across suitable threads | Reference counts affect retention; immutability needs an actual type contract |
| Shared mutable local graph | Checked local access | `Rc<RefCell<T>>`, if required | Dynamic borrow conflicts, cycles, and reentrancy |
| Shared mutable concurrent state | Synchronize participating access | `Arc<Mutex<T>>` or another synchronization design | Lock duration, deadlock, poisoning, contention, and business races |
| Single mutation coordinator | Commands go to one coordinator | Actor/task owning state and accepting commands | Queueing, acknowledgement, shutdown, retries, and delivery semantics |

These are candidates, not equivalences: an ID graph can also live inside one aggregate, and an actor can own a graph.
`Arc` makes reference-count updates thread-safe; it does not automatically make arbitrary inner data safe for concurrent use. [Standard library: Arc](https://doc.rust-lang.org/std/sync/struct.Arc.html)

## 2.4 Worked commerce relationship matrix

Assume a small ordering application, one currency per Order, local validation before persistence, and an external payment provider.
LineItems belong to one Order; Customers and Payments have independent durable identity.
The teaching case has no caller authorization implementation; a real service must supply that policy.
A submitted order retains commercial snapshots needed to explain its historical total.
Events are immutable descriptions of committed transitions, copied or transferred to consumers.
These are teaching assumptions, not universal commerce rules or a production payment design.

| Relationship | Custodian / identity | Coordination, authorization, and access | Horizon and execution | Failure / consistency |
|---|---|---|---|---|
| Order → LineItem | Order owns item values; line ID local to Order if needed | Order coordinates mutation; callers get shared views | Until removal/drop; commercial data frozen at submission; local operation | Reject invalid quantity/currency/overflow before installing change; persist aggregate consistently |
| Order → Customer | Order owns CustomerId and checkout snapshot; customer store owns customer state | Customer service mutates Customer; Order resolves authorized read view | ID may outlive any loaded Customer; snapshot is intentionally historical | Missing/deleted customer has explicit policy; no automatic cascade from Order deletion |
| Order → Payment | Order retains PaymentId/status observation; payment component owns attempt state | Payment component controls authorization/capture/refund; Order requests commands | Separate lifecycles; calls can cross tasks/processes | Timeout may mean unknown provider outcome; reconcile using stable attempt identity |
| Payment → Order | Payment stores OrderId and agreed amount snapshot | Lookup or message; no unrestricted mutable back-reference | Durable correlation; authorization checks on every command | Reject amount/version mismatch; handle missing Order according to retention policy |
| Order → Event | Order operation produces event value; outbox/log takes custody if persisted | Event payload fixed after construction; publisher has delivery capability | Event retention independent of loaded Order | State and outbox require a real transaction if atomicity is claimed; duplicate delivery needs consumer policy |
| Event → Customer/Order/Payment | Event owns copied IDs and minimal necessary facts | Consumer resolves through its authorized API or uses historical facts | Durable fact, potentially stale relative to current state | Missing entity is representable; replay does not imply permission to repeat the original effect |

The matrix shows why a Customer field is not automatically `&Customer` and why Payment should not automatically be an Order-owned mutable child.
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
No Rust move, borrow, or destructor closes those gaps.

## 2.5 Cycles and graphs

A domain graph can be cyclic without its memory-ownership graph being cyclic.
Customer-to-Order and Order-to-Customer navigation can use IDs into independently owned stores.
A tree can own its descendants and use weak back-links when upward navigation is truly needed.
An arena can own all nodes while edges contain handles; then the arena is the resource custodian and the node graph describes connectivity.

When both ends must keep each other alive, explain the termination protocol explicitly.
Strong `Rc` or `Arc` cycles prevent ordinary reference-count reclamation.
Weak pointers do not retain the target strongly; upgrading must account for a target that no longer exists. [Standard library: Arc cycles and Weak](https://doc.rust-lang.org/std/sync/struct.Arc.html#breaking-cycles-with-weak)

Do not call a weak link a reliable lifetime guarantee.
Do not call an arena handle a Rust reference: lookup is a checked operation with its own validity rule.
Neither IDs nor weak pointers establish business permission to navigate an edge.

For an arena that reuses slots, a bare index can accidentally name a replacement object.
A generational handle can contain `(arena_identity, slot, generation)`; resolution checks the arena, occupancy, and generation before returning access.
Typed handles prevent some category mix-ups; generations detect some reuse, while arena identity prevents accidental cross-arena interpretation.
The API must prevent forging unchecked handles or must validate untrusted handles every time.
Choose a generation exhaustion policy: reject reuse or retire a slot rather than silently wrap into an old handle's generation.
Specify whether serialization is supported; a process-local arena handle is usually not a durable entity ID.

Deletion also needs an edge policy: reject deletion while referenced, remove incoming edges, retain tombstones, or allow explicit dangling logical edges.
An arena lookup returning `None` is memory-safe and can still violate a domain rule if callers silently omit required nodes.
Graph algorithms require their own cycle detection, traversal limits, and mutation semantics.
The borrow checker does not prove a directed graph is acyclic.

## 2.6 Lifecycle boundaries are not transaction boundaries

An aggregate can describe who owns a part's business lifecycle.
A transaction describes which persisted changes become visible atomically under a storage system's actual guarantees.
A Rust value's scope describes resource retention in one execution.
They can align in a simple program, but none implies the other two.

Dropping an in-memory Order does not delete its database row.
Dropping a payment request does not undo a provider charge.
Holding `&mut Order` does not serialize changes made by another process to the same durable Order.
Use persistence versions, conditional updates, transactions, or another stated coordination protocol when durable concurrency requires them.

For a consuming transition returning `Result<SubmittedOrder, Error>`, decide what happens to the rejected draft.
Return it with the error if callers need to repair and retry; alternatively, keep mutation borrowed and guarantee no change on validation failure.
If mutation can fail after partial installation, document partial state or use a candidate value and commit only after validation.
Memory ownership makes such choices expressible; it does not select rollback semantics automatically.

## 2.7 Suspension, concurrency, and reentrancy

An asynchronous operation may retain inputs in its future across suspension.
Borrowing across `.await` can be valid when lifetimes and the executor's requirements permit it; it may still hold access longer than the design intends.
Review the retained state and capabilities, not merely whether the function is written `async`. [Standard library: Future](https://doc.rust-lang.org/std/future/trait.Future.html)

As a v0.1 default, gather a minimal owned command or snapshot, release local guards, then perform slow external work.
On return, revalidate any facts whose version or permissions could have changed.
A deliberate transaction or lock spanning an external operation needs a stronger latency, cancellation, and contention justification.
The future's cancellation can drop local state while a remote operation has already succeeded.
Represent an uncertain external result explicitly instead of claiming rollback from local destruction.

`Send` describes values that can transfer safely between threads; `Sync` describes types whose shared references can transfer safely between threads.
These bounds are useful static evidence about thread safety, not proofs of business ordering, fairness, or distributed consistency. [Send](https://doc.rust-lang.org/std/marker/trait.Send.html), [Sync](https://doc.rust-lang.org/std/marker/trait.Sync.html)

A mutex coordinates participating accesses, but a lock can protect the wrong boundary or preserve an invalid state.
Specify lock ordering when several locks can be acquired and avoid calling unknown callbacks under a guard unless reentrancy is part of the protocol.
Poisoning requires a recovery policy; the standard mutex documentation explicitly cautions that poisoning is advisory. [Standard library: Mutex](https://doc.rust-lang.org/std/sync/struct.Mutex.html)
An actor avoids shared mutation of its owned state but does not automatically solve retries, queue overload, or partial external effects.

## 2.8 The evidence ledger for invariants

For every claim, distinguish compiler/static evidence, runtime evidence, database evidence, protocol evidence, and human review.
The table below shows what the Rust realization can contribute; a database transaction must be verified at the store boundary, a remote deduplication promise at the protocol boundary, and an authorization policy through its implementation and review.
None of those guarantees follows from a local compilation result, and an unverified expectation belongs in the assumptions ledger.

| Claim | Evidence Rust can contribute | Evidence still needed |
|---|---|---|
| Borrowed access does not outlive its referent | Lifetime checking for safe references | Correct contracts inside any unsafe implementation |
| Conflicting ordinary reference access is excluded | Borrow checking under Rust's rules | Interior-mutability policy and external aliases/state |
| Some values are not reused after transfer | Move checking for non-`Copy` values | Business uniqueness and duplication rules |
| Only valid operations are publicly callable | Module visibility, types, trait bounds | Runtime authorization and policy context |
| Thread transfer/sharing satisfies type bounds | `Send` / `Sync` constraints | Deadlock, ordering, fairness, and business-race analysis |
| Every LineItem has positive quantity | Private constructor can restrict creation | Validation, arithmetic checks, deserialization boundaries, and tests |
| A handle still identifies its original node | Type can encode handle category | Runtime arena/generation checks and exhaustion policy |
| A payment happens once | An owned command can limit local reuse | Provider guarantees, durable deduplication, reconciliation, and failure tests |
| State and event are committed together | API can make intended boundary visible | Real transaction semantics and verified integration |

Safe Rust's reference rules support memory safety; they are not a universal immutability or business-correctness proof. [Rust Book: references and borrowing](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html)
For each claim, put the actual check beside it and avoid promoting a test into a proof about all possible executions.
Compile-fail examples are valuable evidence for a specific rejected access pattern; runtime scenarios exercise the domain conditions the compiler does not know.

## 2.9 Review exit criteria and open questions

A relationship is ready for implementation when all eight fields have concrete answers and important invariants have named enforcement mechanisms.
A relationship is ready for production only after its real persistence, authorization, execution, and failure assumptions have been verified in that environment.
This edition's local lab cannot establish those production properties.

Open v0.1 questions include how much notation teams will maintain, how contracts should evolve with schema versions, and which review metrics predict reduced defects.
The initial convention is to document significant relationships rather than every scalar field, and to update their contracts when custody, coordination, authorization, or failure behavior changes.
Evaluate ROO by whether another engineer can predict an operation's effects and failure outcomes from the contract and API.
Use that evaluation to improve the method without claiming that compilation alone validates the architecture.
