# ROO GoF Pattern Translation Catalog

This catalog examines all 23 patterns in Gamma, Helm, Johnson, and Vlissides' *Design
Patterns: Elements of Reusable Object-Oriented Software* (the Gang of Four, or GoF) through
**Relationship & Ownership Oriented design (ROO)**. ROO is language-independent: start
with domain intent and invariants, decide relationships, then choose language mechanisms.
Rust supplies the laboratory mappings in this catalog. The GoF names, groupings, and problem statements are the
established source material; each Rust realization and selection rule below is a **ROO
proposal**, not a claim that GoF prescribed Rust or that Rust has a canonical one-to-one
equivalent. [GoF / Pearson](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698)

Inline type fragments in the tables are illustrative design sketches, not complete,
compiled programs. The five longer examples below are explicitly labeled design sketches.

Rust offers structs and enums for data, traits for shared behavior, generics for static
abstraction, trait objects for runtime-selected implementations, closures for captured
callable behavior, and ownership/borrowing for lifetime and mutation control. These
tools overlap in what they can express, but they make different promises. No pattern
name settles that choice for a design. [Rust Book: enums](https://doc.rust-lang.org/book/ch06-00-enums.html), [traits](https://doc.rust-lang.org/book/ch10-02-traits.html), [trait objects](https://doc.rust-lang.org/book/ch18-02-trait-objects.html),
[closures](https://doc.rust-lang.org/book/ch13-01-closures.html), [Rust Reference: trait objects](https://doc.rust-lang.org/reference/types/trait-object.html)

## A ROO selection rule

Before choosing a mechanism, name the pressure that makes the pattern useful: variation,
coordination, resource lifetime, repeated data, delayed work, or restricted access. Name
its participants and the domain invariant each must preserve. For every important
relation record **Owner/resource custodian; Stable identity; Mutation authority; Access
regime; Validity horizon; Execution domain; Failure boundary**. Specify who retains and
releases resources, who can change state, how access is mediated, when the relation ends,
where work runs, and who handles rejection, expiry, cancellation, or partial failure.

Custody is resource retention and release; domain responsibility is accountability for a
business rule. Durable identity may outlive any one representation. Authorization is the
permission of a principal to act, and must be checked even when a component holds a
reference or identity key. These are separate decisions. A pattern name assigns none of
them automatically. For example, a queued Command can retain request data while a domain
service preserves the invariant and execution-time authorization decides whether the
request may still run.

Decide next whether alternatives are closed or extensible, who chooses them, and whether
selection occurs at construction, per call, or during a workflow. Map those decisions to
the target language. In the Rust laboratory, the mechanism choices are:

- **Enum plus `match`:** choose when the set of alternatives is owned by this module and
  intentionally closed. The compiler can require every case to be handled. This is often
  the clearest State, Strategy, Interpreter, Composite, and Visitor representation for a
  finite domain.
- **Trait plus generics:** choose when callers may supply different implementations, but
  the concrete types are known at compile time. This keeps the contract explicit and
  normally permits static dispatch.
- **Trait object (`dyn Trait`):** choose when implementations are selected at runtime or
  cross an extension boundary, and a pointer-owned or borrowed interface is acceptable.
  Trait objects use dynamic dispatch; they do not carry arbitrary per-implementation
  fields in the interface itself.
- **Closure:** choose for one callable behavior with captured state when a named,
  multi-method contract would add no useful meaning. The `Fn`, `FnMut`, and `FnOnce`
  bounds state whether the call may share, mutate, or consume its capture.
- **Concrete struct or free function:** choose when there is only one behavior and no
  real variation. A named type can still clarify authority and lifecycle; an abstraction
  is not valuable merely because a pattern has a name.

For the Rust mapping, prefer ordinary ownership by value, then borrowing where the caller
should retain resource custody. Borrowing alone does not establish business authorization. Use `Box<T>` for a single owned indirection or recursive
storage, not as shared ownership. Use `Rc<T>` or `Arc<T>` only when multiple owners must
genuinely extend one value's lifetime. Add `RefCell<T>`, `Mutex<T>`, or `RwLock<T>` only
when runtime mutation authority is part of the design; that choice introduces runtime
borrow failure, blocking, poisoning, or deadlock concerns. `Weak` and IDs express
non-owning edges. Rust's interior-mutability guidance calls compile-time checking the
default and names runtime checks as a deliberate flexibility tradeoff. [Rust Book: interior mutability](https://doc.rust-lang.org/book/ch15-05-interior-mutability.html),
[shared-state concurrency](https://doc.rust-lang.org/book/ch16-03-shared-state.html), [std::rc::Weak](https://doc.rust-lang.org/std/rc/struct.Weak.html), [std::sync::Weak](https://doc.rust-lang.org/std/sync/struct.Weak.html)

Do not translate a class diagram into a Rust class hierarchy: Rust has no class
inheritance. Translate its changing behavior, data ownership, object identity, and
authority separately. Often a composition, an enum, a trait boundary, or an ordinary
function is smaller and clearer than a family of wrapper types. [Rust Book: object-oriented features](https://doc.rust-lang.org/book/ch18-00-oop.html)

## Creational patterns — 5

GoF intent is condensed in column one. Read the portable relationship decision before
choosing a representation. Relationship decisions, Rust mappings, and cautions are ROO
proposals; the same decisions can be implemented in other languages.

| Pattern and intent | Portable relationship decision | Idiomatic Rust realization | Rust custody and access mapping | Limit or avoid when |
|---|---|---|---|---|
| **Abstract Factory** — create related product families while hiding their concrete classes. | Pressure: consistent product families. The configuring role selects a family; the factory validates compatibility and states product custody, validity, and creation failure before clients receive products. | A trait or generic factory with methods for each product; an enum factory when the family set is closed; associated types when products must remain statically related. | The factory returns owned values or borrows from a factory whose lifetime is explicit. The caller owns created products unless the factory intentionally shares them. | Avoid a boxed factory and boxed products when one concrete family is selected at startup. Rust has no virtual constructor; state how family consistency is enforced. |
| **Builder** — construct a complex value step by step while separating construction from representation. | Pressure: staged construction. The builder retains incomplete inputs; the domain constructor validates completeness and transfers a valid result. Define abandonment cleanup and what remains after failure. | A builder struct with consuming setters and `build(self) -> Result<T, E>`; a typestate builder when required steps must be compile-time obligations. | The builder owns pending inputs and transfers them to the finished value. Keep mutation local to the builder; the result owns its invariants. | Avoid for a small value with a clear constructor. Typestate can multiply types and complicate collections, deserialization, and runtime-selected steps. |
| **Factory Method** — let a creator defer which product is constructed. | Pressure: variable creation. The creator controls the creation point; the provider selects a permitted product. Define input retention, product custody, authorization, and construction failure. | A trait method returning a concrete associated type, a generic factory function, or an enum / `Box<dyn Product>` when the result really varies at runtime. | Factory input is borrowed or consumed according to the construction contract; the returned product is normally owned by the caller. | Avoid virtual-constructor emulation for a fixed mapping; a plain `match`, `From`, or constructor function is enough. Specify errors rather than hiding failure in `Option` or panic. |
| **Prototype** — create a new object by copying a prototypical instance. | Pressure: repeat configuration. The duplication policy decides whether identity is preserved or renewed, which state is independent or shared, and who may duplicate protected resources; define partial-copy failure. | `Clone` for an established value-copy contract; a named `duplicate` or domain-specific cloning method when identity, resources, or deep-copy behavior needs explanation. | The clone owns its resulting value. Document whether it shares reference-counted state, duplicates it, or retains identity-bearing handles. | `Clone` does not promise a deep copy. Avoid implying independent state when cloning `Rc`, `Arc`, handles, file descriptors, or external resources. |
| **Singleton** — ensure one instance and provide a global access point. | Pressure: one service within a named scope. The composition authority sets that scope, initialization, access permissions, mutation policy, and shutdown. Define initialization failure and concurrent access before making it global. | Prefer an explicitly constructed service passed to its users. For true process-wide state use immutable `static`, `OnceLock<T>`, or `LazyLock<T>`; add a lock only for shared mutation. | The application root owns an injected service. A static has process-wide authority and lifetime; decide who initializes it and who may mutate it. | Avoid globals for request, tenant, test, or configuration-scoped state. Statics are difficult to reset and isolate; locks add synchronization semantics. `LazyLock` initialization panic poisons future access. |

## Structural patterns — 7

| Pattern and intent | Portable relationship decision | Idiomatic Rust realization | Rust custody and access mapping | Limit or avoid when |
|---|---|---|---|---|
| **Adapter** — make an existing interface usable through another interface. | Pressure: contract mismatch. The adapter translates operations and failures between client and provider without enlarging authorization. Specify provider custody and whether retention lasts one call or the adapter lifetime. | A named newtype around the adaptee implementing the target trait; a borrowed adapter when it must not own the wrapped value; `From`/`TryFrom` for value conversion. | The wrapper explicitly owns or borrows the adaptee. It controls which operations are exposed and translates errors at the boundary. | Avoid a wrapper that merely forwards every method without renaming, conversion, policy, or isolation. Do not use `Deref` to imply a broader transparent contract than intended. |
| **Bridge** — vary an abstraction and its implementation independently. | Pressure: two independent variation axes. The abstraction remains accountable for its contract; the implementor receives bounded capabilities. Define selection, replacement during active work, custody, and failure translation. | A generic abstraction parameterized by an implementation for static composition, or a field of `Box<dyn Implementor>` when the implementation must change at runtime. | The abstraction owns or borrows its implementation handle; mutation is delegated through a narrow trait. | Avoid a second indirection when there is only one axis of change or one implementation. Choose generic versus `dyn` by whether runtime heterogeneity is required. |
| **Composite** — let clients treat a part and a whole uniformly. | Pressure: uniform part/whole operations. Decide tree versus graph, stable node identity, link-edit authority, deletion and transfer rules, and all-or-partial failure for operations over descendants. | A recursive enum such as `Node::Branch(Vec<Node>)` for an owned tree; alternatively, a trait for an open set of node types. | In the tree form, a parent owns children; there is no reverse ownership edge. For editable graph-like structures, centralize records and links in an arena and pass stable IDs. | Avoid pretending a DAG is a tree. Parent links, multiple parents, removal, and cycles need explicit graph policy; do not add `Rc<RefCell<_>>` edges without defining who may mutate or retain nodes. |
| **Decorator** — add responsibilities by wrapping an object without changing its interface. | Pressure: layered policy. Each layer preserves the component promise and receives only needed authority. Define ordering, shared identity, inner-resource custody, cancellation, and failure propagation across layers. | A generic wrapper `Decorator<T>` for static composition, or a `Box<dyn Component>` wrapper for runtime-selected layers; a concrete builder can compose layers. | Each wrapper owns its inner value or explicitly borrows it. The outermost wrapper owns the public call path and its added policy. | Avoid if a direct field or function is clearer. Deep wrapper stacks can obscure behavior, error flow, and debugging; keep ordering and drop behavior visible. |
| **Facade** — provide a simpler entry point over a subsystem. | Pressure: subsystem complexity. The facade coordinates a use case while domain participants retain their invariants. Specify dependency lifetime, caller authorization, cancellation, and recovery after partial effects. | A free function for a stateless operation or a small service struct holding explicit subsystem dependencies. | The facade borrows or owns dependencies according to its lifetime; the subsystem remains authoritative for its state. | Avoid a facade that becomes a second domain model or a universal service locator. Preserve meaningful errors and cancellation at the boundary. |
| **Flyweight** — share intrinsic state across many small logical objects, supplying context externally. | Pressure: repeated immutable data. A custodian canonicalizes intrinsic state; clients retain per-use context. Define canonical identity, eviction and invalid-handle behavior, and whether access crosses execution boundaries. | Separate immutable shared data from per-use context; use IDs, interned strings, or `Arc<T>` only where sharing has measured value. | A cache or arena owns canonical values; users carry a handle plus their own extrinsic state. Define cache lifetime and eviction authority. | Avoid premature interning and hidden global caches. Sharing saves memory only if values are repeated enough; synchronization and lookup may cost more than duplication. |
| **Proxy** — control access to another subject through a compatible interface. | Pressure: mediated access. The proxy enforces a stated access or delivery policy; the subject retains its domain responsibility. Define identity continuity, authorization, dependency lifetime, retries, and visible remote or cache failure. | A named wrapper implementing the same trait for lazy loading, authorization, caching, remote calls, or instrumentation. Async boundaries may require an explicit async trait/API design. | Proxy owns, borrows, or holds an ID for its subject. It must define whether it controls access, lifetime, failures, retries, and side effects. | Avoid “transparent” claims across errors, blocking, latency, cancellation, or identity changes. Keep remote and permission failures visible to callers. |

## Behavioral patterns — 11

| Pattern and intent | Portable relationship decision | Idiomatic Rust realization | Rust custody and access mapping | Limit or avoid when |
|---|---|---|---|---|
| **Chain of Responsibility** — pass a request along handlers until one handles it. | Pressure: variable routing. A coordinator chooses handler order and request validity. Specify each handler’s mutation authority, when custody transfers, whether rejection stops routing, and where errors are handled. | An ordered `Vec`/iterator of borrowed handlers, a chain of owned handlers, or a fold over functions; return an explicit outcome such as continue, handled, or rejected. | A dispatcher owns the order; each handler borrows the request or takes owned data only when it accepts it. | Avoid when the decision is a short, stable `match`. Define ordering, whether rejection stops traversal, and how handler errors differ from “not handled.” |
| **Command** — encapsulate a request as a value that can be queued, logged, delayed, or undone. | Pressure: delayed or replayable action. A queue retains request data; an executor checks current authorization and target identity. Define expiry, execution domain, duplicate effects, cancellation, and compensation for failure. | An enum for a closed command set; structs implementing a `Command` trait for an open set; closures for short in-process actions. | The queue owns command data. A command receives a narrow mutable context; undo requires explicit prior state or a compensating command. | Avoid storing closures when commands need serialization, inspection, stable identity, or replay. Do not promise undo without specifying side effects and failure recovery. |
| **Interpreter** — represent and evaluate a small language grammar. | Pressure: a small domain language. Grammar and evaluator define valid meaning; an environment grants bounded effects. Specify source validity, evaluation limits, and parse versus execution failure. | A recursive AST enum plus parser and evaluator functions; traits only where grammar extensions need an open boundary. | The AST owns or borrows source data under an explicit lifetime; evaluator borrows the AST and receives explicit environment authority. | Avoid when a parser, query engine, or existing language is the real need. Recursive evaluation needs limits or iterative handling for untrusted depth. |
| **Iterator** — traverse a collection without exposing its representation. | Pressure: traversal independent of representation. The collection governs structural updates; traversal governs position. Define snapshot versus live access, item validity, concurrent edits, and invalidation or traversal failure. | Implement `Iterator` for a traversal state, or return an iterator adapter over a collection. Use `IntoIterator` when owned, borrowed, and mutably borrowed traversal differ. | The iterator owns traversal state and either owns items or borrows them for a defined lifetime. The collection retains mutation authority unless the iterator consumes it. | Avoid a bespoke protocol for slices, maps, or ordinary lazy pipelines. Self-referential and lending iterators may need a different API because standard `Iterator::Item` cannot depend on each `next` borrow. |
| **Mediator** — centralize interaction among colleagues so they do not depend on each other directly. | Pressure: coordinated participants. A mediator controls routing and workflow, while participants retain domain state authority. Define registration lifetime, execution order, unavailable peers, and partial-work recovery. | An explicit coordinator that owns or borrows participants; for concurrent components, typed messages/channels can make communication and ownership boundaries visible. | The mediator owns routing policy, not necessarily participant state. Participants send requests through a narrow mediator API. | Avoid a “god mediator” that knows all rules and data. Split by cohesive use case; do not replace a clear direct call with a message bus without a decoupling need. |
| **Memento** — capture and restore an object's state without exposing its internals. | Pressure: recoverable history. The originator defines valid snapshots; a caretaker retains them without editing their meaning. Define identity/version compatibility, restoration authority, retention, and rollback limits for external effects. | A private snapshot type created by the owner; clone a value only when that clone has snapshot semantics, or serialize a versioned snapshot for durable history. | The originator creates and interprets snapshots; a caretaker may own and order them but should not mutate their meaning. | Avoid assuming `Clone` means independent rollback. External effects, resource handles, schema evolution, and snapshot size need explicit policy. |
| **Observer** — notify dependents when a subject changes. | Pressure: change notification. A registry controls subscription validity; subscribers control their reactions. Define revocation authority, delivery order, execution domain, reentry, and whether one subscriber failure stops delivery. | Prefer borrowed observers when lifetimes are nested; use an event queue/channel when asynchronous decoupling is useful; use a registry with subscription tokens for dynamic callbacks. | A subject/registry controls subscription IDs and dispatch. A token or explicit `unsubscribe` defines who can revoke a subscription. Observers should not own the subject strongly by default. | Reentrancy, unsubscribe during dispatch, event ordering, callback failure, and strong-reference cycles must be designed. See the hard case below; do not install a mutable shared callback graph by default. |
| **State** — vary an object's behavior as its internal state changes. | Pressure: lifecycle-dependent behavior. A domain role authorizes legal transitions and preserves entity identity. Define active-state access, concurrent events, and the valid state remaining after rejection or failure. | A closed enum with state-specific data and `match`; a trait object for independently extensible state implementations; typestate for transitions known at compile time. | The containing value owns its active runtime state. Typestate moves ownership into the next compile-time state; expose only operations valid for that type. | Avoid trait-object state for a small finite machine. Runtime events cannot be made compile-time known; invalid external transitions still need validation and errors. See the hard case below. |
| **Strategy** — select an algorithm behind a common policy. | Pressure: algorithm variation. A context selects a policy with a shared promise and grants bounded data access. Define replacement timing, retained-input validity, permitted effects, and comparable failure outcomes. | A generic policy trait for static choice, `dyn Trait` for runtime substitution, an enum for a closed set, or a closure for one callable operation. | The caller or context selects and owns the strategy; pass only the data or capabilities the algorithm needs. | Avoid an abstraction when one small branch is sufficient. A strategy should vary a real algorithm, not turn every option into an object. |
| **Template Method** — define algorithm steps while allowing selected steps to vary. | Pressure: invariant sequence with variable steps. The coordinator retains sequence authority; hooks receive bounded capabilities. Define hook lifetime, execution order, cancellation, and recovery if a step fails. | A function that owns the invariant sequence and accepts a policy trait or a few closures for variable steps; default trait methods can provide shared behavior where the API fits. | The sequence-owning function retains control of order and invariants. Hook implementations receive only the data/capabilities needed for their step. | Avoid emulating a superclass with many overridable hooks. Too many hooks leak the algorithm's internals; prefer an explicit pipeline when callers need to reorder steps. |
| **Visitor** — add operations over a stable set of element types without placing every operation on each element. | Pressure: new operations over stable elements. The model governs element invariants; operations receive explicit read or mutation authority. Define traversal validity, extension governance, and partial-visit failure. | For a closed enum or AST, use exhaustive `match` functions or a fold. For an open element interface, use traits; a classic `accept`/visitor pair works when element types are stable and operations are added often. | The data model owns its representation; each visitor borrows the element and receives only the access required for its operation. | Visitor does not solve simultaneous open extension of both element types and operations. Adding a new enum variant changes matches; adding a visitor method changes implementors. See the expression problem below. |

## Five hard cases

### 1. Observer: subscription, reentrancy, and cycles

**Portable decision first.** Treat a subscription as a revocable relation with a named holder of revocation authority and a defined validity horizon. Choose synchronous or queued delivery, ordering, reentry, and subscriber-failure behavior before selecting a callback or registry mechanism.

The simple picture “subject calls every observer” omits the decisions that make this
pattern safe to use. ROO treats subscription as an explicit capability rather than a
permanent object-graph edge.

- For a nested, synchronous lifetime, borrow observers from the owner that outlives
  dispatch. This avoids heap allocation and shared ownership, but the borrow correctly
  prevents conflicting mutation while the observer list is borrowed.
- For dynamic registration, give each subscription an opaque ID and return a token that
  can revoke it on drop, or expose an explicit `unsubscribe(id)`. State which party owns
  revocation. Document that dropping the token revokes the subscription; transferring it
  transfers revocation authority, while forgetting it leaves the entry registered until
  explicit cancellation or registry teardown.
- Do not invoke arbitrary callbacks while holding a `RefCell` borrow or a lock on the
  registry. A callback can re-enter dispatch, register another observer, or unsubscribe;
  holding the guard across user code can panic on a nested borrow or deadlock a thread.
- Define dispatch semantics before implementation. A useful contract is: additions apply
  to the next event; removing a not-yet-called observer suppresses its call in the
  current event; recursive notifications are queued and drained FIFO after the current
  pass. Other contracts are possible, but snapshot versus live-list behavior must not be
  accidental.
- A registry can snapshot IDs, release its borrow, and reacquire for each ID to check
  membership and obtain a callback. If callbacks need `FnMut`, the registry must also
  define what happens when the same callback is invoked reentrantly. Queue nested events
  or reject reentry; do not rely on a runtime borrow panic as policy.
- If callbacks can fail or panic, decide whether dispatch stops, records the failure and
  continues, or delivers through a result/channel. Reset dispatch-depth and
  pending-queue state on every exit path, including unwinding if unwinding is supported.
- A closure that captures a strong `Rc`/`Arc` back to its subject can form a cycle.
  Prefer `Weak` capture and handle `upgrade()` returning `None`, or route events through
  an owner-controlled queue. `Weak` prevents an owning cycle; it does not decide
  delivery semantics.
- Across threads, choose a message channel or a deliberately synchronized registry.
  `Arc` only shares ownership; it does not make the payload safe to mutate. `Mutex`
  guards can deadlock and callbacks under a lock are especially risky. [Rust Book: shared-state concurrency](https://doc.rust-lang.org/book/ch16-03-shared-state.html),
  [std::sync::Weak](https://doc.rust-lang.org/std/sync/struct.Weak.html)

**Design sketch — not executable Rust:** `SubscriptionId` is a copyable key; `EventBus`
owns a map of IDs to callbacks and a FIFO pending-event queue; `Subscription` owns a
weak handle plus its ID and removes that ID on explicit cancellation or drop. Dispatch
copies the current ID list, never holds the map borrow while calling user code, checks
whether each ID remains subscribed, and defers nested `publish` calls until the current
pass completes. A production API must still choose callback type, error policy, thread
model, and token transfer semantics.

### 2. State: runtime state and typestate promise different things

**Portable decision first.** Define legal transitions, the actor authorized to request each, the invariant maintained by the transition authority, and the identity that survives it. Decide what a failed transition leaves behind and how concurrent or persisted events are validated. Then choose a state representation.

Use a runtime enum when input, network events, persistence, or user actions choose the
next state. The enum owns the current state data, and a transition function can validate
an event and return `Result<NextState, TransitionError>`. Exhaustive matching makes
adding a state visible at compile time, but cannot prove a runtime event sequence valid
before the program receives it.

Use a state trait plus a boxed state value when the set of implementations is open,
plugins supply states, or each state needs substantial independent behavior. This buys
extension at the cost of dynamic dispatch, indirection, and a runtime transition
protocol. For a finite machine, it often hides useful exhaustiveness behind more types.

Typestate changes the type as a value moves through a known lifecycle. It can make an
operation unavailable after a transition, but it is appropriate only when the caller can
know the state statically. It does not validate external input, prevent a separate value
from being in another state, or provide a single heterogeneous collection of differently
typed states without erasure.

**Design sketch — not executable Rust:** `Document<Draft>::publish(self) ->
Result<Document<Published>, PublishError>` consumes a draft and returns a published
document. A web request handler still parses and validates a runtime request before
constructing either type. If the state comes from a database row at runtime, decode it
into an enum and validate transitions there; do not claim typestate makes the database
trustworthy.

This distinction follows the standard ownership and dispatch mechanisms, not a special
compiler guarantee attached to the pattern name. The Rust Book's state-pattern example
compares a trait-object implementation with an enum alternative and then encodes states
as types. [Rust Book: implementing an object-oriented design pattern](https://doc.rust-lang.org/book/ch18-03-oo-design-patterns.html)

### 3. Composite: trees, parent links, and arenas

**Portable decision first.** Decide whether exclusive parentage is a domain invariant or shared descendants are valid. Assign link-edit authority and resource custody separately; define atomic reparenting, deletion, retained-link validity, and cycle policy before choosing storage.

When composition is truly a tree and edits are simple, recursive ownership expresses the
invariant directly: each branch owns its children, and the tree's root owns everything
below it. A node does not need a parent pointer merely to compute ancestors; pass the
traversal context down or return the needed result up.

A parent pointer creates a graph edge in the opposite direction. Strong child-to-parent
and parent-to-child reference counts form an owning cycle. `Weak` avoids that cycle for
reference-counted trees, but upgrading may fail, and runtime mutation still needs a
borrow policy. Parent links must be updated atomically with child moves and removals.

If callers need stable identity, multiple links, frequent edits, or parent lookup, use
an arena: one owner stores node records and relations; callers hold `NodeId`s. Keep
mutation behind arena methods so moving a node updates both sides, reject cycles if the
domain requires a tree, and define stale-ID behavior after removal. A generation counter
can distinguish a reused slot from an old ID. IDs express identity, not ownership, so
the arena remains responsible for lifetime and deletion.

**Design sketch — not executable Rust:** `Arena { nodes: Vec<Slot<NodeRecord>> }`; each
record stores `parent: Option<NodeId>` and `children: Vec<NodeId>`. Methods
`attach(parent, child)` and `detach(child)` validate ownership, reachability, and cycle
constraints before changing both records. If many-parent DAGs are valid, call the
structure a graph and specify whether traversal deduplicates shared descendants.

Use `Rc<RefCell<Node>>` only when independently held nodes must truly share mutable
local identity and the runtime borrow boundary is understood. It is not the default
response to a compiler rejecting a parent pointer. [Rust Book: `Rc`](https://doc.rust-lang.org/book/ch15-04-rc.html), [interior mutability](https://doc.rust-lang.org/book/ch15-05-interior-mutability.html),
[std::rc::Weak](https://doc.rust-lang.org/std/rc/struct.Weak.html)

### 4. Visitor and the expression problem

**Portable decision first.** Decide who governs element variants and who may add operations. Each operation needs an explicit access regime and traversal-validity rule; mutation and partial failure must preserve model invariants. Then choose which extension axis the language mechanism supports.

Visitor is strongest when the element set is stable and new operations are added often.
Rust's enum-and-`match` design makes a closed element set explicit: adding an enum
variant makes incomplete matches visible. Each new operation can be a function over the
enum, without adding a method to every node.

An open trait-object element set reverses the tradeoff: new element implementations can
be added behind a trait, while adding another operation generally requires extending
that trait or using a separate dispatch mechanism. The classic GoF `accept` method plus
visitor interface provides double dispatch, but every new element type changes the
visitor interface and every visitor implementation.

This is the expression problem in practical form: should downstream code be able to add
new data variants, new operations, both, or neither? No enum, trait, or visitor
simultaneously grants unrestricted extension of both axes with static exhaustiveness and
no coordination. Pick which axis the module owns. A stable AST with many analyses is a
good fit for an enum, `match`, and shared recursive fold; an open plugin node set can
justify a trait boundary and runtime dispatch.

**Design sketch — not executable Rust:** a closed `Expr` enum is evaluated by
`eval(&Expr)` and rendered by `format(&Expr)`, each with an exhaustive match. Add
`Expr::Call` and the compiler points to every operation requiring a case. A
plugin-defined expression trait supports new node implementations, but a new operation
such as `optimize` needs a planned extension API. If both axes must be open, consider a
registry, erased representation, or external schema and state what exhaustiveness is
lost.

For syntax trees, avoid adding an `accept`/visitor interface solely to resemble Java.
Use a visitor when it solves the chosen extension direction and makes traversal policy
clearer than ordinary functions or a fold.

### 5. Singleton: global lifecycle and concurrency

**Portable decision first.** Name the uniqueness scope, initialization authority, resource custodian, authorized users, and shutdown boundary. Decide how competing calls coordinate and how failed initialization or shutdown is observed. Uniqueness alone grants neither global access nor unrestricted mutation.

“Exactly one instance” has at least two meanings: one service instance per application
composition root, or one global value per process. Prefer the first when the service has
configuration, external dependencies, mutable state, or tests; construct it once and
inject references to the places that use it. This preserves explicit ownership and
allows multiple independent application instances in one process.

Use an immutable `static` when the value is truly process-wide and constant. Use
`LazyLock<T>` for one no-argument initializer or `OnceLock<T>` when initialization is
supplied later or needs caller input. They provide initialization coordination, not a
general lifecycle manager. A static's lifetime does not match a request or test fixture;
design reset and shutdown as explicit operations if they are requirements.

Mutable process-wide state needs a concrete concurrency contract. An atomic fits a small
atomic value; a `Mutex<T>` serializes access; an `RwLock<T>` permits multiple readers
but has platform-dependent fairness and can deadlock under bad lock ordering. `Arc<T>`
only extends shared ownership and does not make `T` thread-safe; `Arc<Mutex<T>>` is
appropriate only when both shared ownership and serialized mutation are required. Handle
poisoning and lock failures rather than treating `unwrap()` as an invariant.

Static initialization can fail or panic under different semantics. In particular, the
standard `LazyLock` documentation says a panic in its initializer poisons the value and
future access panics; `OnceLock` is not poisoned on panic. Select based on that behavior
and on the required initialization inputs. [std::sync::OnceLock](https://doc.rust-lang.org/std/sync/struct.OnceLock.html), [std::sync::LazyLock](https://doc.rust-lang.org/std/sync/struct.LazyLock.html), [std::sync::Mutex](https://doc.rust-lang.org/std/sync/struct.Mutex.html),
[std::sync::RwLock](https://doc.rust-lang.org/std/sync/struct.RwLock.html), [std::sync::Arc](https://doc.rust-lang.org/std/sync/struct.Arc.html)

**Design sketch — not executable Rust:** `Application::new(config) ->
Result<Application, Error>` constructs `Database`, `Clock`, and `Metrics`; routes borrow
those services. A process-wide immutable lookup table may separately use `LazyLock`. Do
not put tenant configuration or mutable request context in that static merely to obtain
one instance.

## ROO review checklist for a proposed translation

Before retaining a pattern label in a design, record the seven relationship fields above and answer these questions in plain terms. Begin with domain intent and invariants; then use the Rust-specific questions to review a laboratory mapping:

1. Which axis varies: data shape, algorithm, policy, lifecycle, representation, or
   coordination?
2. Is the set closed and owned by this module, or open to downstream implementations?
3. Does the caller choose the implementation at compile time, at runtime, or not at all?
4. Who owns each value, who can mutate it, and who revokes or ends the relationship?
5. Is identity a value, an address, an arena ID, or an external persistence key? Do not
   confuse persistence identity with memory ownership.
6. Does a callback, shared pointer, parent link, or global introduce a cycle,
   reentrancy, hidden authority, or lifetime longer than intended?
7. Which failures are explicit: invalid transition, missing weak target, callback error,
   lock poisoning, absent cache entry, parse failure, or remote failure?
8. What becomes easier to change, and what becomes harder to inspect, test, serialize,
   debug, or extend?

Keep a pattern when its name helps communicate a decision and its mechanism earns its
cost. Remove it when the name is doing more work than the design.

## Sources and provenance

- **Established GoF catalog:** Erich Gamma, Richard Helm, Ralph Johnson, and John
  Vlissides, *Design Patterns: Elements of Reusable Object-Oriented Software*,
  Addison-Wesley Professional, 1994. Pearson lists the authors, edition, and catalog of
  23 patterns. [Publisher record](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698)
- **Established Rust language/library behavior:** the Rust Book and Reference links
  above describe enum, trait, trait-object, closure, ownership, interior-mutability, and
  concurrency mechanisms. The standard library links specify `Weak`, `Arc`, `Mutex`,
  `RwLock`, `OnceLock`, and `LazyLock` behavior.
- **ROO proposal:** the mapping tables, selection rule, ownership/authority vocabulary,
  and five hard-case designs are this catalog's recommended transfer method. They should
  be treated as design guidance to evaluate against a concrete system, not as guarantees
  from Rust, the Rust project, or the GoF authors.
- **Scope caution:** GoF patterns name recurring tradeoffs; they are not a checklist,
  evidence of quality by themselves, or a mandate to preserve class-based structure.
  Rust's compiler checks types and borrowing rules, while application-level policy such
  as correct event delivery, valid persisted state, deadlock freedom, cache eviction, or
  snapshot meaning remains a design responsibility.
