# 1. Foundations: objects with explicit relationships

ROO — Relationship & Ownership Oriented design — is a proposed language-independent software design method.
It starts with recognizable object-oriented concerns: abstraction, encapsulation, behavior, identity, collaboration, and substitutability.
It starts each design exercise with a scenario and its invariants, then describes the relationship contract of each collaboration before choosing language, runtime, storage, or protocol mechanisms.
Rust is this edition's laboratory language: its executable examples explore selected realizations of the method, while the relationship decisions remain useful in other languages.
This is a v0.1 proposal, not new Rust semantics, a formal calculus, or an empirically proven superior methodology.

## 1.1 The premise and its limits

A class diagram can show that an Order has LineItems and belongs to a Customer without explaining who destroys what, who may mutate it, or what survives a request.
Those omissions are tolerable while discussing vocabulary; they become expensive when treated as an implementation specification.
ROO adds a relationship contract to the diagram and follows the contract into APIs, execution, persistence, and failure handling.

The central design question is: **what may each participant do to this data, during which interval, under which consistency rules?**
A memory address, a domain identifier, and a permission to modify an entity answer different parts of that question.
Making them explicit is useful even when a garbage collector manages memory.

Rust supports encapsulated data with methods and multiple forms of polymorphism; it does not provide class inheritance of implementation and fields.
Calling Rust object-oriented depends on the chosen definition of OO.
ROO does not require resolving that naming dispute before designing useful software. [Rust Book: OO characteristics](https://doc.rust-lang.org/book/ch18-01-what-is-oo.html)

Compiler friction is evidence to inspect, not a verdict that a design is wrong.
A rejection may expose an accidental long-lived borrow, an inadequate API, a genuinely difficult graph, conservative static analysis, or an implementation mistake.
A sound design can need carefully encapsulated runtime checks or unsafe implementation behind a safe abstraction.
Conversely, a program can compile and still charge the wrong customer or lose a payment notification.

## 1.2 Precise working vocabulary

| Term | ROO meaning | Question to answer |
|---|---|---|
| Object | Encapsulated state and behavior, possibly represented by a struct plus implementations | Which invariants does this API protect? |
| Value | Data interpreted by its content for the operation under discussion | Would an equal replacement change the meaning? |
| Entity | A domain participant tracked across state changes by an identity rule | What makes it the same entity tomorrow? |
| Owner / resource custodian | The participant or mechanism responsible for keeping state or a resource available and arranging its release | What retains this state or resource, and when is it released? |
| Domain responsibility | The component accountable for a business rule or transition | Where is the rule decided? |
| Stable identity | A key with a specified scope, uniqueness, and reuse policy | What does this key identify, and for how long? |
| Authority | Permission to perform a named action under policy | Who may approve, mutate, delete, or publish? |
| Capability | An API value or interface that grants a specific operational ability | What can its holder actually invoke? |
| Borrow | Temporary access without taking ownership of the borrowed resource | What must remain valid during access? |
| Snapshot | A separately retained description of state at a declared time or version | How old may this observation be? |
| Aggregate | A chosen domain consistency boundary containing related state | Which rules must change together? |
| Execution domain | The thread, task, actor, process, or service in which access is coordinated | How can operations overlap? |

These are design terms, not replacements for Rust's specification vocabulary.
In particular, resource custody, domain responsibility, durable identity, and authorization are independent obligations.
Custody retains a resource; responsibility protects a rule; identity recognizes an entity; authorization permits a principal to act.
Domain responsibility is not synonymous with the owner of a Rust value.
A request handler may own an Order loaded from storage while an Order service remains responsible for its business policy.
A database row may identify a customer while many Rust values hold snapshots of that row.

## 1.3 Ownership is not identity

A move transfers a Rust value without inherently changing the represented customer's domain identity.
An independently loaded value may represent the same database entity at a different version.
A cloned handle may refer to the same allocation; a cloned record may hold independent state with the same identifier.
Therefore “clone the customer” is incomplete: specify whether it means duplicate a snapshot, share a handle, or create a new entity with a new identity.

Rust moves and `Copy` are language operations; value semantics and entity identity are domain interpretations.
Passing a non-`Copy` value by value normally transfers it; passing a `Copy` value makes a copy instead.
Neither operation decides whether the business considers the represented entity the same. [Rust Book: ownership](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html)

Avoid using addresses as durable domain keys.
Values can move, allocations can be released, and addresses can be reused.
If stable address is actually required, state that requirement separately from stable identity.
`Pin` addresses particular movement guarantees under its contract; it neither supplies durable identity nor turns an arbitrary graph into a valid borrowed structure. [Standard library: pinning](https://doc.rust-lang.org/std/pin/index.html)

ROO v0.1 assumes typed IDs for durable entities and explicit constructors for new identities.
Whether an ID is globally unique, tenant-local, or repository-local belongs in its contract.
An ID should not be treated as authorization merely because it is difficult to guess.

## 1.4 Encapsulation protects meaningful transitions

Private fields let an API concentrate checks, but private fields alone do not establish a domain invariant.
An `Order::add_item` operation can validate quantity, currency, lifecycle state, and total arithmetic together.
A public `items_mut()` escape hatch can undermine that promise by returning unrestricted access to the representation.
Prefer operations that name intended transitions when representation changes require coordinated checks.
Expose read-only views or iterators when callers only need observation.

A method receiver also communicates an access requirement:

| Receiver or input | Typical operational reading | Additional contract still needed |
|---|---|---|
| `&self` | Shared access | Interior mutation, I/O, authorization, and observational consistency |
| `&mut self` | Exclusive borrowed access | Business permission and preservation of invariants |
| `self` | Consuming operation for a non-`Copy` receiver | Outcome on error and identity after transition |
| `&T` parameter | Temporary shared view | Freshness, validity interval, and allowed hidden effects |
| `T` parameter | Transfer or copy according to the type | Whether retry or duplication is meaningful |
| `Id` parameter | Deferred resolution | Existence, version, tenant scope, and access checks |

Shared references do not guarantee that all observable state is immutable.
Interior-mutability types deliberately allow controlled mutation through shared access.
`RefCell` performs borrow checks at runtime; it can panic on conflicting borrows, so it is an access-policy choice rather than a way to erase the policy. [Standard library: cell types](https://doc.rust-lang.org/std/cell/index.html)

A capability should offer no more authority than its collaboration needs.
For example, a quoting operation can receive a price reader rather than a repository interface that also permits deletion.
Rust visibility and types can restrict available calls, but an application must still authenticate principals and enforce context-dependent policy.
An `&mut Payment` proves an access condition; it does not prove the caller is entitled to issue a refund.

## 1.5 Seven core commitments

1. **Name the scenario and invariant before the mechanism.** State the expected and forbidden outcomes and participating state before selecting a language representation, storage model, or protocol.
2. **Separate custody, responsibility, identity, and authorization.** Record these independently even when one component performs all four roles.
3. **Give mutation a coordinator.** Each invariant needs a defined place where conflicting changes are prevented or detected.
4. **Keep access no longer than required.** Prefer operation-scoped borrowing when the relationship itself is temporary.
5. **Choose sharing deliberately.** Explain why independent values, transfers, or IDs do not meet the actual requirement before introducing shared mutable state.
6. **Design time and failure with structure.** Document suspension, cancellation, stale observations, and partial external success as part of the relationship.
7. **Match the guarantee to evidence.** Separate compiler/static checks, runtime checks, database guarantees, protocol evidence, and human review; record assumptions and the scope of tests explicitly.

These are heuristics, not absolute bans.
Shared mutable caches, cyclic graphs, dynamic plugins, and inheritance in other languages can be appropriate.
ROO asks their contracts to make the resulting coordination cost visible.
The simplest representation is the one that meets the real requirements with comprehensible guarantees, not necessarily the one with the fewest types.

## 1.6 Behavioral subtyping and inheritance

Inheritance discussions often bundle three independent goals: substitutable behavior, reuse of representation or implementation, and an extension mechanism.
Separate them before translating a hierarchy.
A Rust trait can describe common operations without promising shared fields.
A composed member can reuse state and delegate implementation without creating a subtype relationship.
An enum can represent a closed family whose variants require exhaustive handling.
A generic parameter can select an implementation statically; a trait object can select one dynamically when the trait supports dynamic dispatch. [Rust Reference: trait objects](https://doc.rust-lang.org/reference/types/trait-object.html)

Behavioral subtyping is a semantic promise: clients relying on the supertype's specified behavior must remain correct with a subtype.
Signatures alone cannot generally establish that promise.
Contracts must account for preconditions, postconditions, invariants, and allowed histories of mutable state. [Liskov and Wing, 1994](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf)

Consider a `PaymentMethod` interface whose successful authorization guarantees a reservation for the requested amount.
An implementation that silently authorizes less violates that promise even if every method signature matches.
An implementation that may time out can fit only if the contract already admits an uncertain outcome and defines reconciliation.
ROO requires those semantic conditions to travel with the trait and its tests.

| Original goal | Candidate Rust representation | Design review question |
|---|---|---|
| Common behavior | Trait with a small contract | Are all implementations substitutable under the documented errors and effects? |
| Shared fields | Owned component plus delegation | Does the component have a coherent invariant of its own? |
| Optional policy | Generic strategy or function/closure | Who owns captured state, and can the policy outlive its inputs? |
| Runtime extension | Trait object behind an appropriate pointer | Are lifecycle, thread requirements, and dynamic-dispatch restrictions acceptable? |
| Closed alternatives | Enum and pattern matching | Is extension intentionally controlled by this module? |
| State-dependent operations | Enum state machine or consuming typestate API | How does persistence, recovery, or dynamic state enter the model? |

Do not recreate a base-class-shaped object merely to retain familiar names.
Do not eliminate a hierarchy merely because Rust uses a different mechanism.
Translate the underlying obligation, then select a representation that carries it accurately.
Default trait methods can reuse behavior, but a supertrait requirement does not inherit another struct's storage.

## 1.7 Lifetimes describe access validity

A Rust lifetime parameter relates reference validity requirements; annotating a reference does not keep its referent alive longer.
Use a borrowed view when its provider can guarantee the data remains valid for the needed interval.
Use owned data, a snapshot, or a resolved handle when the consumer must become independent of that provider. [Rust Book: lifetimes](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html)

A request-scoped `OrderView<'a>` can be appropriate for rendering an in-memory Order.
A background delivery job should usually retain an owned message or stable identifier instead of a request's borrowed view.
This is a v0.1 default, not a prohibition on futures borrowing data: scoped asynchronous work can borrow when its actual lifetime contract allows it.

Distinguish three clocks: memory validity, business validity, and observation freshness.
A reference can remain memory-valid after an order becomes cancelled.
A snapshot can remain memory-valid while its price becomes outdated.
A durable identifier can remain syntactically valid after its entity is deleted.
Each clock needs its own checks.

## 1.8 Intellectual lineage and claim boundary

Ownership and alias control predate Rust and this proposal.
Clarke, Potter, and Noble's *Ownership Types for Flexible Alias Protection* (OOPSLA 1998) is a canonical ownership-types reference; its publisher record is [DOI 10.1145/286936.286947](https://doi.org/10.1145/286936.286947).
The publisher blocked full-text retrieval during this edition's research, so this chapter makes no detailed comparison with that calculus.

Separation logic provides assertions for disjoint storage and local reasoning through a frame rule.
That is an important conceptual antecedent to asking which state an operation can affect; a ROO relationship table is not a separation-logic proof. [Reynolds, 2002](https://www.cs.cmu.edu/~jcr/seplogic.pdf)

RustBelt formalized a realistic subset of Rust and conditions for safely extending it with unsafe libraries using Iris.
It connects Rust's safety story to rigorous semantic reasoning; it does not prove this methodology or every program compiled by every Rust version correct. [RustBelt project and paper](https://plv.mpi-sws.org/rustbelt/popl18/)

ROO's contribution in this edition is a teachable integration: a relationship contract, a decision procedure, worked translations, and a small lab.
No priority claim is made for ownership-aware OO, composition, capability restriction, typestate, or explicit consistency boundaries.
Its usefulness remains a hypothesis to evaluate through design reviews and implementation experience.

## 1.9 What success means in this edition

A successful ROO design can explain each important relationship without appealing to an unexplained pointer choice.
It shows which transitions protect an invariant and how clients obtain the authority to request them.
It accounts for retention, suspension, concurrency, and failure at the relevant boundary.
It states what compiler/static checks, runtime checks, databases, protocols, and human review establish, and which assumptions remain unverified.
The next chapter turns those obligations into a reusable artifact.
