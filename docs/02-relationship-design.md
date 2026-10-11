# 2. Relationship design: from arrows to enforceable contracts

A relationship is a continuing or operation-scoped obligation between participants.
An arrow in a model describes connectivity; a ROO relationship contract describes how that connectivity is allowed to work.
ROO — Relationship & Ownership Oriented design — is a language-independent method for making those obligations explicit.
This chapter proposes notation and a procedure for v0.1.
Begin with a scenario and its invariants, use the seven fields to decide relationships, then select mechanisms that realize those decisions.
The notation is a language-independent review aid, not executable syntax or a formal proof language; Rust supplies the laboratory realizations in this edition.

## 2.1 The seven-field Relationship Contract

For every architecturally significant relationship, write these seven fields.
Supporting questions refine the fields rather than replacing them.

| Field | Required statement | Supporting questions |
|---|---|---|
| Owner / resource custodian | What keeps the related state or resource available? | Is ownership nested, independent, shared, or transferred? Who releases it? |
| Stable identity | What identifies the target, if identity is needed? | What are the scope, reuse, deletion, and version rules? Is cardinality zero, one, or many? |
| Mutation authority | Who may request and execute which changes? | Which operations preserve invariants? Are authorization and access capability distinct? |
| Access regime | How access and aliasing are coordinated | Value, shared borrow, exclusive borrow, checked handle, snapshot, lock, actor, or other policy? |
| Validity horizon | During which interval is the relationship usable? | Memory lifetime, business lifecycle, freshness deadline, and revocation conditions? |
| Execution domain | Where and how operations may overlap | Thread, task, process, service? May access cross suspension or reentrancy? |
| Failure boundary | What happens if the interaction fails partway? | Atomicity, rollback, retry, cancellation, uncertain outcome, and recovery responsibilities? |

A relationship may require several entries if its operating modes differ.
For example, `Order → Customer` during validation uses a resolved read view, while the stored Order retains only an ID and selected snapshot data.
Calling both modes simply “a reference” conceals a major distinction.
An unknown field is an open design issue; it is not permission to assume an unlimited lifetime or arbitrary mutation.

## 2.2 Reusable notation

Use a named arrow followed by the seven fields:

```text
R(name: Source -> Target [cardinality]) {
  owner: custodian and retention rule;
  identity: key/scope/version/reuse policy, or value-only;
  authority: permitted operations and their coordinator;
  access: regime and aliasing rule;
  horizon: validity/freshness/lifecycle interval;
  execution: execution domain and suspension/reentrancy rule;
  failure: atomicity, error outcomes, retry/recovery rule;
}
```

Use additional `invariant`, `evidence`, and `open` lines when useful.
`evidence` records the mechanism and its verified scope: compiler/static check, runtime validation, database constraint or transaction, protocol behavior, or human review.
Tests provide observations about the mechanism exercised; documented assumptions remain assumptions until supported by evidence at their own boundary.
`open` records an unresolved requirement so it cannot be mistaken for an implemented guarantee.
A shorthand label such as `owned`, `borrowed`, `identified`, `snapshot`, `shared`, or `transferred` is an index into a complete contract, not its substitute.

Example for a contained part:

First decide that the whole retains its parts, coordinates their commercial transitions, and rejects invalid candidate changes before installation.
The following notation realizes that policy with Rust storage vocabulary; `Vec<LineItem>` is a representation choice rather than the premise of the relationship.

```text
R(order_items: Order -> LineItem [0..n]) {
  owner: Order owns Vec<LineItem>; removing an item releases that value;
  identity: line identity is scoped to the Order; no independent lifecycle;
  authority: Order operations add/remove/reprice before submission;
  access: shared item views; mutation stays inside Order operations;
  horizon: owned until removal/drop; submission freezes commercial facts;
  execution: one coordinator per loaded Order; short local operations;
  failure: validate candidate change first, then install or return error;
  invariant: quantity > 0; one currency; total arithmetic is checked;
  evidence: private fields + runtime validation + invariant tests;
}
```

If a line needs returns or fulfillment tracked independently, revisit the identity and lifecycle assumptions.
The initial representation is not a permanent law of the domain.

## 2.3 A decision process

1. **Describe behavior.** Write the scenario, expected outcome, forbidden outcome, and relevant failure.
2. **Locate the invariant.** List the exact pieces of state that must agree, and at which observation boundary.
3. **Identify clocks and identities.** Decide what survives a call, a task, a restart, a deletion, and a business transition.
4. **Assign responsibility, custody, and authorization.** Name the domain coordinator, each resource custodian, and the principals permitted to request changes independently.
5. **Choose access.** Decide observation, controlled mutation, transfer, and coordination policy for the required sharing and overlap before choosing a pointer, lock, or queue.
6. **Specify crossing points.** Define transfer, lookup, snapshot creation, serialization, suspension, and external effects.
7. **Select mechanisms and design the API.** Choose language, runtime, storage, and protocol realizations; restrict operations and receivers to communicate the selected authority and access regime.
8. **Assign evidence.** Mark compiler/static checks, runtime checks, database guarantees, protocol evidence, human review, and unresolved assumptions separately.
9. **Try a counterexample.** Delete a target, reuse a slot, cancel after an external effect, or race two changes.
10. **Revise the model.** Change boundaries when the counterexample reveals a missing responsibility rather than adding a pointer mechanically.

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
A submitted order retains commercial snapshots needed to explain its historical total.
Events are immutable descriptions of committed transitions, copied or transferred to consumers.
These are teaching assumptions, not universal commerce rules or a production payment design.

| Relationship | Custodian / identity | Authority and access | Horizon and execution | Failure / consistency |
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
On return, revalidate any facts whose version or authority could have changed.
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

A relationship is ready for implementation when all seven fields have concrete answers and important invariants have named enforcement mechanisms.
A relationship is ready for production only after its real persistence, authorization, execution, and failure assumptions have been verified in that environment.
This edition's local lab cannot establish those production properties.

Open v0.1 questions include how much notation teams will maintain, how contracts should evolve with schema versions, and which review metrics predict reduced defects.
The initial convention is to document significant relationships rather than every scalar field, and to update their contracts when ownership, authority, or failure behavior changes.
Evaluate ROO by whether another engineer can predict an operation's effects and failure outcomes from the contract and API.
Use that evaluation to improve the method without claiming that compilation alone validates the architecture.
