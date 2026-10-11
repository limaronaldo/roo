# ROO Concept Atlas

**First edition · English · 2026-10-11**

ROO means **Relationship & Ownership Oriented design**: a language-independent method for making domain responsibilities, relationships, identity, authority, and lifecycle decisions explicit. Useful object-oriented concepts are inputs to that method. Rust is the executable laboratory used here to explore one implementation; Java and other languages can realize the same domain decisions through their own mechanisms.

This atlas starts with domain intent and invariants, decides the relationships needed to preserve them, and only then asks how a language expresses those decisions. It is not a Java-to-Rust syntax conversion, a complete language reference, or a proof that a model is correct. The working sequence is:

1. State the responsibility and behavioral contract in domain terms.
2. Assign domain responsibility, resource custody, mutation authority, access, identity, validity, execution, and failure boundaries for each relation.
3. Choose an implementation in the target language; the Rust laboratory uses structs, enums, generic bounds, trait objects, and module boundaries.
4. Record the tradeoff and the domain rules that still need tests, review, or runtime checks.

**Portable reading.** In Java, C#, C++, and other languages, keep the same questions about identity, mutation authority, collaborator lifetime, and who closes a resource. Map the answers to each language's own mechanisms, such as `AutoCloseable`, RAII, or managed references. Rust makes more aliasing and lifetime constraints visible in types; it does not make the underlying responsibility irrelevant elsewhere.

For every stored relation, distinguish **domain identity** (which entity this is) from **memory ownership** (which value controls its lifetime). A database key does not own an object in memory; an `Arc` does not by itself establish domain identity. Rust's ownership checks constrain aliasing and lifetimes, while domain invariants and behavioral promises remain design responsibilities. The [Rust Book](https://doc.rust-lang.org/stable/book/ch04-01-what-is-ownership.html) and [Rust Reference](https://doc.rust-lang.org/reference/) describe language rules; this atlas adds a design reading of those rules.

Record seven fields for each important relation: **Owner/resource custodian; Stable identity; Mutation authority; Access regime; Validity horizon; Execution domain; Failure boundary.** The custodian retains or releases a resource; the domain role answers for a business rule. A durable identity survives replacement of a representation, while authorization decides which principal may act. Neither a reference, a key, nor custody alone grants business authorization. Access may be exclusive, shared, read-only, or mediated; validity may end at a call, workflow, lease, or explicit revocation; execution and failure boundaries must describe asynchronous and distributed relations too.

The entries follow **Classical intent → Relationship decision → Rust translation → Rust ownership mapping → Tradeoff.** Any model sketch below is conceptual pseudocode, not a claim that a snippet was compiled. The executable laboratory, when available, is the source of compile evidence; this atlas makes no compiler claim.

## 1. Core concepts

### Encapsulation

**Classical intent.** Give callers a stable set of operations while keeping representation choices and invariant-preserving decisions inside a boundary. In Java this is commonly a class with private fields and public methods.

**Relationship decision.** Assign one domain boundary responsibility for each invariant. Name the operations and authorized actors that can change it, what observers may see, and how rejected changes leave a valid state. Keeping a resource alive does not grant permission to change its business meaning.

**Rust translation.** Put data in a `struct` or `enum`, behavior in inherent `impl` blocks or trait implementations, and control access with module privacy. Keep fields private when arbitrary writes could break an invariant; expose methods that express allowed operations. Rust's [module privacy rules](https://doc.rust-lang.org/stable/book/ch07-02-defining-modules-to-control-scope-and-privacy.html) form part of this boundary.

**Rust ownership mapping.** Use `&self` for observation, `&mut self` for exclusive in-place change, or a consuming `self` method when an operation transfers or replaces the value. A method's receiver is an ownership and authority choice, not just syntax.

**Tradeoff.** More invariants can be protected at the API boundary, but callers may need purpose-built methods instead of direct field access. Privacy does not prove that a business rule is correct; it only limits where the representation can be changed.

### Abstraction

**Classical intent.** Let a client depend on a useful promise rather than a concrete implementation. The abstraction should say what a client may rely on and leave mechanism open to change.

**Relationship decision.** State the shared promise, including allowed effects and failure outcomes, before choosing interchangeable providers. Decide who selects and replaces a provider, whether clients retain it beyond a call, and how withdrawal or unavailability is reported.

**Rust translation.** Use a public trait for shared behavior, a generic bound for compile-time requirements, a trait object for runtime erasure, or a module/API boundary for a concrete service. Use an enum when the alternatives are a known, closed set. The [Rust Book's treatment of traits](https://doc.rust-lang.org/stable/book/ch10-02-traits.html) explains shared behavior; its [trait-object chapter](https://doc.rust-lang.org/stable/book/ch18-02-trait-objects.html) compares open-ended runtime alternatives.

**Rust ownership mapping.** A trait method that borrows `&self` grants observation; `&mut self` grants temporary exclusive mutation; taking `self` can consume an implementation. Lifetimes on references state how long a borrowed implementation must remain valid. A `Box<dyn Trait>` owns the erased value; `&dyn Trait` borrows it.

**Tradeoff.** A narrow abstraction decouples callers, but an abstraction introduced before there is real variation can add indirection and maintenance. An interface or trait is a contract, not an automatic architectural seam.

### Objects, classes, structs, and enums

**Classical intent.** A class commonly combines a representation, operations, access control, construction rules, and a place in a subtype hierarchy. An object is one runtime instance with state and behavior.

**Relationship decision.** Separate a domain role from its current representation. Decide whether replacement preserves identity, who maintains its invariants, who has custody of its resources, and when collaborators must stop using it; a class-shaped representation is optional.

**Rust translation.** A struct or enum stores a value; `impl` blocks attach methods; modules govern visibility; traits describe behavior shared across types. Rust does not have class inheritance, and the Rust Book deliberately distinguishes Rust structs/enums from the bundled state-and-behavior object model used by many OO languages ([OO characteristics](https://doc.rust-lang.org/stable/book/ch18-01-what-is-oo.html)).

**Rust ownership mapping.** Decide whether a value is stored inline, boxed, borrowed, reference-counted, or represented by a stable key. The representation follows from its lifecycle and sharing needs, not from the word “object.”

**Tradeoff.** Rust separates concerns that a class may bundle, making ownership and reuse more explicit. It also means a design may span a data type, one or more traits, and a module rather than a single class declaration.

### Identity, value objects, and entities

**Classical intent.** A value object is defined by its values; an entity is tracked by identity across changing state. Two entity instances with equal fields may still represent different people, orders, or accounts.

**Relationship decision.** Choose equality from domain meaning. Specify which authority issues durable identities, which component is responsible for authoritative updates, and whether retained links resolve current state or a snapshot. Define deletion and stale-link behavior independently of in-memory custody.

**Rust translation.** Give value objects value equality when that is their domain meaning; derive or implement `PartialEq`/`Eq` only when those semantics are right. Give entities an explicit newtype key such as `CustomerId`, and define equality or lookup in terms of that key when required. Keep the domain model independent of whether an instance currently lives in a database, cache, or process.

**Rust ownership mapping.** An aggregate or repository may own the in-memory entity value; other components can borrow it during a call or hold a typed ID and look it up later. Use `Rc`/`Arc` only when shared lifetime ownership is actually part of the in-memory model. `Rc::ptr_eq`/`Arc::ptr_eq` answers an allocation-identity question, not a domain-identity question.

**Tradeoff.** Value semantics make copying and comparison straightforward, but cloning an entity can create competing mutable snapshots. Identity keys support long-lived and cyclic domain graphs, but require lookup and failure handling. Memory ownership and persistence identity are separate axes.

### Association, aggregation, composition, and dependency

**Classical intent.** These relationship names describe different promises. An association says instances are related. Aggregation is a weak whole/part relation whose shared-part semantics are intentionally loose in UML. Composition is stronger containment: a part belongs to at most one composite at a time, and the composite is responsible for its disposition. A dependency means one component uses another without necessarily retaining it. UML's [aggregation semantics](https://www.omg.org/spec/UML/2.5.1/PDF) make clear that shared aggregation is not a precise synonym for ownership.

**Relationship decision.** For each edge, state its purpose, cardinality, custodian, authorized changes, and termination rule. Composition requires an exclusive whole/part commitment and an explicit disposition or transfer policy; association alone implies neither custody nor authorization. Define what a disconnected or unavailable collaborator means to the workflow.

**Rust translation.** Represent an association with the least powerful link that fits: a borrowed reference for a scoped relation, an ID for a relation resolved elsewhere, or an owning handle when the object retains another value. A dependency may be only a function argument, generic parameter, imported trait, or service field. Represent a composed part as an owned field, `Box<T>`, or owned collection when the whole controls its lifetime. Model intentionally shared ownership with `Rc<T>` or `Arc<T>`; pair with `RefCell<T>` or a synchronization primitive only if shared mutation is required.

**Rust ownership mapping.** Name the owner, borrowers, mutation authority, sharing rule, and destruction rule for each relation. If a part can leave the whole, provide an explicit transfer operation. If two aggregates need the same entity, consider a stable ID or shared handle rather than claiming unique composition. For queued or spawned work, decide whether the task takes owned data or IDs or only borrows during a bounded call; state how it reports a missing target or failed operation.

**Tradeoff.** Inline composition is simple and makes destruction follow ownership, but Rust references cannot outlive their referents. IDs make persistence and cycles easier but move resolution and missing-target errors to runtime. Reference counting permits shared lifetimes but introduces counting overhead and can leak on strong reference cycles; it does not make mutation automatically safe.

### Cardinality and object graphs

**Classical intent.** Multiplicity states how many related values are valid: exactly one, optional one, many, or a bounded or non-empty set. It is a domain constraint, not merely a field type.

**Relationship decision.** Define permitted counts, uniqueness, reachability, and cycles as domain rules. Assign authority for adding, moving, and removing links, require both ends to remain consistent, and specify whether removal deletes a target or only ends the relation.

**Rust translation.** Use `T` for exactly one, `Option<T>` for zero-or-one, `Vec<T>` for an ordered zero-or-more collection, and a map or set when keyed lookup or uniqueness is part of the contract. A non-empty or bounded collection needs a wrapper/newtype whose constructors and operations preserve that rule. Rust's [`Option`](https://doc.rust-lang.org/std/option/enum.Option.html) is an explicit sum type, so absence must be handled by the caller.

**Rust ownership mapping.** A collection of owned values owns its elements. A collection of references borrows them for one shared lifetime. A collection of IDs expresses links without owning the targets. Model both ends of a bidirectional relation deliberately; storing back-pointers can require IDs, arenas, or reference counting.

**Tradeoff.** The type can rule out some invalid cardinalities, but collection types alone do not enforce uniqueness, lower bounds, or cross-record consistency. Strongly connected object graphs often need IDs or an arena rather than ordinary references or mutually strong `Rc` links.

### Mutability and invariants

**Classical intent.** Encapsulate changes so each state transition preserves the object's valid-state rules. Mutability may be visible to a client or hidden behind methods.

**Relationship decision.** List valid transitions and the role authorized to initiate each. Decide whether competing updates serialize, reject, or reconcile, which observations may be stale, and what atomicity or recovery is required after a partial failure. Separate derived-cache changes from domain changes.

**Rust translation.** Ordinary mutation requires mutable access. A shared `&T` cannot normally be used to mutate the value; `Cell<T>` and `RefCell<T>` provide single-threaded interior mutability, while `Mutex<T>`, `RwLock<T>`, and atomics support selected cross-thread patterns. The standard library's [interior-mutability discussion](https://doc.rust-lang.org/stable/book/ch15-05-interior-mutability.html) explains the runtime-checked `RefCell` tradeoff.

**Rust ownership mapping.** Prefer one clear owner with `&mut` access when possible. Add shared ownership (`Rc`/`Arc`) and interior mutability only for a concrete sharing requirement. Identify which methods may change domain state and which only cache derived data.

**Tradeoff.** Exclusive mutation is visible in the API and statically constrained. Interior mutability moves some checks to runtime or synchronization and can make state changes less obvious. The borrow checker does not prove an invariant such as “balance never becomes negative”; constructors and every mutating path must preserve it.

### Invariants, construction, and lifecycle

**Classical intent.** Construction establishes the object's valid initial state; every operation preserves its invariants; destruction releases resources at the right time.

**Relationship decision.** Name the role that establishes a valid instance, the custodian that releases resources, and the authority that approves activation or shutdown. Define when a relation becomes usable, what survives transfer, and how failed construction or shutdown is observed and recovered.

**Rust translation.** Use associated functions such as `new` or `try_new` rather than a language-defined constructor. Validate input and use private fields or newtypes to make invalid states harder to create. A builder is useful for many optional settings; a typestate builder can make required steps explicit. Resource-owning values release resources through `Drop` when ownership ends. Rust's [ownership chapter](https://doc.rust-lang.org/stable/book/ch04-01-what-is-ownership.html) connects scope, moves, and cleanup; [Drop](https://doc.rust-lang.org/stable/book/ch15-03-drop.html) covers custom cleanup.

**Rust ownership mapping.** A constructor returning `Self` transfers the new value to its caller; a fallible constructor returns `Result<Self, E>`. A consuming transition (`self -> Next`) transfers ownership to the next valid state. The owner controls when the value is dropped; ordinary borrows cannot extend that lifetime.

**Tradeoff.** RAII makes cleanup reliable on normal scope exit and early returns, but `Drop` is not a good place for fallible business shutdown. Provide an explicit `close`, `commit`, or `finish` operation returning `Result` when callers must observe failure; keep `Drop` as best-effort cleanup. A builder adds ceremony, and typestate can increase the number of types and make dynamic workflows harder to express.

### Delegation and composition

**Classical intent.** A component forwards a responsibility to a collaborator rather than inheriting implementation or accumulating unrelated responsibilities.

**Relationship decision.** Keep the delegating role accountable for its public promise while assigning a specific task to the collaborator. Decide which capabilities it receives, whether it may retain inputs, who can replace it, and how its failure affects the enclosing operation.

**Rust translation.** Store the collaborator as a field and call it explicitly; implement a trait for a wrapper by forwarding selected methods. A wrapper can add policy before or after delegation. `Deref` is for pointer-like ergonomics and should not be treated as a general substitute for inheritance or explicit forwarding.

**Rust ownership mapping.** Own a collaborator when the wrapper controls its lifetime; borrow it for a scoped operation; use `Box<dyn Trait>` for an owned runtime-selected implementation; use `Arc<dyn Trait + Send + Sync>` only when shared cross-thread ownership is needed. Generic `Wrapper<C>` keeps the collaborator's concrete type static.

**Tradeoff.** Delegation makes dependencies and lifetimes visible and supports independent variation. It can require forwarding methods and add wrapper types. If forwarding obscures the API, reconsider which responsibility belongs on the wrapper.

## 2. Polymorphism and type extension

### Three forms of polymorphism

**Classical intent.** Polymorphism lets one algorithm work with multiple forms, but the mechanism matters. Subtype polymorphism substitutes one implementation for a contract; parametric polymorphism abstracts over a type parameter; ad hoc polymorphism selects behavior for a type-specific operation.

**Relationship decision.** Identify the behavior that varies and the common observable promise. Decide who chooses an implementation, whether that choice may change during a workflow, and which data, effects, and failure obligations every alternative must respect.

**Rust translation.** Use a trait plus `T: Trait` for statically selected behavior over generic types; use `dyn Trait` behind a pointer for heterogeneous runtime values; use trait implementations such as `Add` or `Display` for ad hoc operations. Rust does not overload an ordinary function name by argument type, and trait implementations are constrained by coherence.

**Rust ownership mapping.** Generic methods borrow, mutate, or consume `T` according to their parameter and receiver types. A trait object also needs an explicit ownership form such as `&dyn Trait`, `Box<dyn Trait>`, or `Arc<dyn Trait>`.

**Tradeoff.** Generics preserve concrete type information and permit static dispatch but generally instantiate code for each used type. Trait objects permit mixed concrete types behind one API but use dynamic dispatch and pointer indirection. Ad hoc trait implementations provide a uniform operation but must be coherent and should match the operation's semantics.

### Static dispatch, dynamic dispatch, and open sets

**Classical intent.** Dynamic dispatch supports calling an overridden operation through a base reference; static dispatch chooses an implementation before runtime. An extensible framework may also need types unknown when the framework was compiled.

**Relationship decision.** Decide who may introduce alternatives and when they are selected. Define compatibility, replacement, and withdrawal rules for extensions, including the lifetime of outstanding calls; openness is a product and governance decision before it is a dispatch mechanism.

**Rust translation.** `T: Trait` and argument-position `impl Trait` are statically dispatched. `dyn Trait` is dynamically dispatched through a trait-object pointer and vtable. A finite `enum` is a closed set whose matches can be exhaustive; a public trait can permit downstream types to implement behavior, subject to coherence and object-compatibility rules. The [Reference's trait-object rules](https://doc.rust-lang.org/reference/types/trait-object.html) and [trait rules](https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility) define the boundary.

**Rust ownership mapping.** Use a generic collection when every element has the same concrete type; use an enum when alternatives are known and closed; use `Vec<Box<dyn Trait>>` when one owned collection must hold different runtime implementations. Borrow a trait object if the collection does not own its elements.

**Tradeoff.** Static dispatch enables optimization and keeps calls concrete, but can increase code size or expose concrete types through APIs. Dynamic dispatch allows heterogeneous extension, at the cost of an indirect call, pointer-sized metadata, and limits on which trait methods can be dispatched. Choose the openness the product needs rather than pre-emptively making every type extensible.

### Interfaces, traits, bounds, and supertraits

**Classical intent.** An interface names a capability or contract without requiring a shared state layout. Abstract classes often mix that contract with inherited fields and implementation.

**Relationship decision.** Name a capability by the promise clients need, including effects and failures. Combining capabilities must not silently combine custody or grant broader authorization; specify what access each operation needs and how long it may retain collaborators.

**Rust translation.** A trait describes associated functions, types, and constants implemented separately for concrete types. Default methods offer reusable behavior. A trait bound (`T: Read`) constrains a generic caller. A trait object (`dyn Read`) erases a concrete type for runtime dispatch. A supertrait (`trait Writer: Read`) requires that implementors also satisfy another capability; it is a behavioral/type requirement, not a parent class carrying fields. See the [Rust Reference](https://doc.rust-lang.org/reference/items/traits.html) and Java's official [interface and inheritance guide](https://docs.oracle.com/javase/tutorial/java/IandI/interfaceDef.html).

**Rust ownership mapping.** Method receivers make borrowing explicit. Bounds do not imply ownership: accepting `&T` borrows, while accepting `T` takes ownership. A trait object needs a pointer because the concrete size is erased. Trait objects can also carry lifetime and auto-trait bounds such as `Send` or `Sync` where appropriate.

**Tradeoff.** Traits separate capability from data layout and can be implemented without inheriting fields. Their method set and associated items affect extensibility. A trait with generic methods, some `Self` uses, or generic associated types may not be dyn-compatible; keep a generic interface and a smaller object-safe façade when both use cases are needed.

### Associated types, variance, and coherence

**Classical intent.** Generic contracts define how types relate. Subtyping and covariance/contravariance explain safe substitution in a hierarchy; multiple inheritance and mixins add implementation reuse but create conflicts.

**Relationship decision.** State which input, output, and collaborator types must remain compatible and who governs extensions to that contract. A substitution must preserve validity and permitted effects, not merely reuse a name; resolve conflicting meanings at the contract boundary.

**Rust translation.** Associated types name a type selected by an implementation (for example, an iterator's `Item`). A generic trait parameter is useful when one type can implement the trait in multiple distinct ways. Variance describes how lifetime/type subtyping passes through a generic type; it is not class inheritance. Rust's [variance reference](https://doc.rust-lang.org/reference/subtyping.html) identifies covariant, contravariant, and invariant cases. Coherence rejects overlapping impls and foreign-trait/foreign-type impls under the [orphan rules](https://doc.rust-lang.org/reference/items/implementations.html#trait-implementation-coherence).

**Rust ownership mapping.** Bind an associated type in a trait-object use when the trait permits it; prefer static bounds if a generic associated type or method prevents dynamic dispatch. Use a local newtype to adapt a foreign type or trait while respecting coherence. Lifetimes on borrowed types are where variance most often matters to ordinary API design.

**Tradeoff.** Coherence makes trait resolution predictable and lets libraries evolve without arbitrary conflicting implementations, but it limits downstream extension combinations. Variance is usually a property to understand when designing reference-containing abstractions, not a feature to tune casually. It does not grant permission to weaken ownership or aliasing rules.

## 3. Inheritance, contracts, and responsibility

### Inheritance has several meanings

**Classical intent.** “Inheritance” can mean at least four different things: **state inheritance** (subclass gets fields), **implementation inheritance** (subclass reuses code), **interface/type inheritance** (subclass is assignable to a parent type), and **behavioral inheritance** (subclass preserves the parent's promised behavior). A design that gains one does not automatically gain the others.

**Relationship decision.** Decide separately whether roles share state, reuse behavior, or promise substitution. Shared state needs one authoritative update policy and a stated custodian; reused code does not imply shared identity, lifecycle, or business authority.

**Rust translation.** Rust has no class inheritance. Use struct fields or composition for state; helper functions, delegation, or default trait methods for code reuse; traits and bounds for capabilities; and explicit contracts for behavior. Use an enum for a closed family of variants. The Rust Book's [OO chapter](https://doc.rust-lang.org/stable/book/ch18-01-what-is-oo.html) and trait-object example show how common OO intents map without subclassing.

**Rust ownership mapping.** State reused by multiple concepts can be owned as an inner value, borrowed for an operation, or referenced by an ID. A trait implementation owns no shared base state by virtue of implementing the trait. Decide who owns each field before selecting a reuse mechanism.

**Tradeoff.** Composition and traits avoid coupling a subtype to a base representation, but may require explicit delegation and do not create automatic field reuse. In Java or C++, inheritance remains useful when there is a stable subtype relationship and its state and behavior contracts are genuinely substitutable.

### Liskov substitution and behavioral contracts

**Classical intent.** A subtype should preserve the expectations that clients may rely on through the supertype: it must not strengthen required preconditions, weaken guaranteed postconditions, or invalidate the supertype's invariants and history constraints. Liskov and Wing frame behavioral subtyping in terms of specifications, not just matching method signatures ([paper](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf)).

**Relationship decision.** Specify what every implementation preserves: preconditions, postconditions, invariants, history, side effects, and failure outcomes. A replacement must respect clients’ retained relationships and authorization limits, including across deferred work or retries.

**Rust translation.** The compiler checks trait implementation shape and type compatibility, not the truth of a behavioral promise. A type can implement `Iterator`, `Read`, or a domain trait while still violating expectations in its documentation. Write trait contracts in terms of preconditions, results, side effects, and state guarantees; test implementations against those contracts.

**Rust ownership mapping.** Choose receivers that expose mutation authority: `&self` should not secretly imply an externally observable state change unless interior mutability is part of the contract; `&mut self` makes exclusive mutation visible; a consuming method signals that the prior value is replaced or no longer available.

**Tradeoff.** Explicit ownership narrows some aliasing hazards, but it cannot establish logical substitutability. Favor a smaller capability trait or a sum type when a proposed subtype has exceptions to the parent contract.

### The diamond problem

**Classical intent.** In multiple inheritance, a diamond occurs when two branches share a base. Questions include whether the base state exists once or twice and which inherited implementation wins. Java avoids multiple class inheritance but permits multiple interfaces and defines conflict-resolution rules for defaults ([Oracle guide](https://docs.oracle.com/javase/tutorial/java/IandI/override.html)).

**Relationship decision.** Determine whether the apparent shared base denotes one domain entity or two independent roles. For shared state, assign one update authority and a coherent lifecycle; for duplicated state, state how divergence is handled. Resolve competing behavior explicitly rather than relying on inheritance order.

**Rust translation.** There is no class-state diamond. A type can implement multiple traits, and traits can have supertraits, but overlapping method names may need fully qualified calls or an explicit wrapper decision. Trait coherence limits conflicting implementations; it does not decide which domain behavior is correct.

**Rust ownership mapping.** Put shared state in one composed field or aggregate and expose narrow traits over it. If two capabilities need a common dependency, let the implementation hold one owner and delegate both capabilities to it; do not duplicate state just to satisfy two interfaces.

**Tradeoff.** Composition makes shared state ownership explicit and avoids virtual-base semantics. Multiple traits still can create naming and API complexity; favor explicit delegation when the result clarifies authority and behavior.

### SOLID and GRASP as design prompts

**Classical intent.** SOLID and GRASP are heuristics for managing change and assigning responsibility, not language laws. Robert C. Martin's [SOLID material](https://cleancoder.com/files/solid.md) names SRP, OCP, LSP, ISP, and DIP. Craig Larman describes GRASP as a set of responsibility-assignment principles such as Information Expert and Creator ([book excerpt](https://www.informit.com/articles/article.aspx?p=360440&seqNum=2)).

**Relationship decision.** Assign decisions to roles with the needed information and domain accountability, then grant only the capabilities they require. State which role coordinates a use case and which preserves each invariant; resource custody may belong to a different component. Introduce a boundary only for a real responsibility or variation.

**Rust translation.** Apply them to modules, types, traits, functions, and service boundaries, not only classes:

- **SRP:** group behavior around one cohesive reason to change. A Rust type need not be split merely because it has several methods.
- **OCP:** protect a demonstrated variation point with a trait, enum, or composition boundary. A closed enum is often simpler when the alternatives are fixed. “Open” does not mean never edit existing code.
- **LSP:** preserve documented trait behavior; compile-time conformance is weaker than behavioral proof.
- **ISP:** keep capabilities focused on the needs of their clients, without fragmenting one coherent contract into needless micro-traits.
- **DIP:** let policy depend on a capability and inject an implementation where substitution is needed. Choose generic/static or `dyn`/runtime injection deliberately.
- **GRASP Information Expert:** keep a decision near the value that owns the data and invariant required to make it. **Creator:** let an aggregate or component with the required data/lifecycle create its owned parts. **Controller:** use an application/service boundary to coordinate a use case without turning one stateful object into a god object.

**Rust ownership mapping.** Treat responsibility assignment as a question about which owner has authority to change which state, and which layer owns a collaborator. A service can borrow an adapter for a call or own an injected adapter; neither choice is prescribed by SOLID or GRASP.

**Tradeoff.** These heuristics help expose coupling and scattered responsibility, but maximizing abstraction, traits, or class count is not the goal. Keep a direct concrete design until a real change boundary or test seam justifies an abstraction.

## 4. State and failure modeling

### Null, absence, exceptions, and `Result`

**Classical intent.** A nullable reference encodes absence but can let absence leak into ordinary operations. Exceptions represent failures that may be handled across a call boundary, though unchecked exceptions can hide the failure set from signatures.

**Relationship decision.** Distinguish legitimate absence, an expired relation, denied access, and a failed operation. Assign the role that handles or propagates each outcome, define the state left behind, and bound diagnostic disclosure and retry authority. A missing link must not silently become permission to create or replace its target.

**Rust translation.** Use `Option<T>` when a value may be absent and `Result<T, E>` when an operation can fail with a reason the caller should handle. Use a domain error enum when callers need structured alternatives. Reserve `panic!` for broken assumptions or unrecoverable programming errors, not routine input or I/O failures. The Book covers [`Result`](https://doc.rust-lang.org/stable/book/ch09-02-recoverable-errors-with-result.html) and [when to panic](https://doc.rust-lang.org/stable/book/ch09-03-to-panic-or-not-to-panic.html); the standard library documents [`Result<T, E>`](https://doc.rust-lang.org/std/result/enum.Result.html).

**Rust ownership mapping.** Error values are ordinary values returned to the caller; decide whether they own context, borrow it, or carry a stable ID. `?` propagates an error while transferring it according to the return type. `Option<&T>` borrows an optional target; `Option<T>` owns an optional value.

**Tradeoff.** Absence and recoverable failure become visible in the type and must be handled or propagated. Rich errors can improve diagnosis but may expose implementation detail; translate lower-layer failures at a boundary when the caller needs domain meaning. `Option` says nothing about why a value is absent.

### Typestate and state machines

**Classical intent.** A stateful object changes what operations are legal as it moves through a workflow. Runtime state patterns often use subclasses or state objects to vary behavior.

**Relationship decision.** Define legal states and transitions, their authorizing actors, and the invariants preserved at each step. Decide whether identity survives transition, what concurrent observers may see, and what a failed transition leaves usable. External or persisted state requires validation regardless of representation.

**Rust translation.** For a small closed set of runtime states, use an enum and match on it. For a protocol whose legal transitions should be enforced at compile time, use distinct types or a type parameter and consuming transitions from one state type to the next. The [Rust Book's state-pattern chapter](https://doc.rust-lang.org/stable/book/ch18-03-oo-design-patterns.html) demonstrates a runtime trait-object implementation and a typestate redesign.

**Rust ownership mapping.** A consuming transition takes the old state and returns the new state, so callers cannot keep using the pre-transition value. If the state must change behind a stable handle at runtime, store the state in one owned value and use an enum or a state trait object; shared mutable handles require a separate synchronization decision.

**Tradeoff.** Typestate can make illegal sequences unrepresentable for code compiled against the API, but creates more types and can be cumbersome when states come from external data, persistence, or user input. Parse and validate external state at the boundary; compile-time states do not replace runtime validation.

## 5. Worked hierarchy redesigns

These are design exercises, not complete implementations. Sketches are deliberately schematic and must not be treated as compilable Rust.

### A. `Rectangle` / `Square`

**Classical hierarchy and failure.** Suppose mutable `Rectangle` promises that changing width preserves height, while `Square : Rectangle` must keep width and height equal. A `Square` that changes both dimensions when the caller sets only width violates the caller's expectation; one that changes only width violates the square invariant. The issue is behavioral, not a spelling problem. Liskov and Wing's specification-based account explains why a subtype must preserve the parent's contract.

**Relationship decision.** Preserve each shape’s dimensional invariant and offer only operations with a shared behavioral promise. Decide whether shapes are values or identity-bearing entities, who may replace dimensions, and how invalid dimensions are rejected. A shared area query does not require a shared mutation contract.

**Rust redesign.** First decide whether the product needs a closed geometry set or an open plugin API:

- For a fixed set, model the alternatives with a private enum containing `Rectangle { width, height }` and `Square { side }`, behind a public `Shape` wrapper with validating constructors and operations such as `area`. Public enum variants would expose their fields, so the wrapper is necessary if callers must not bypass dimension validation. There is no mutable rectangle supertype for a square to contradict.
- For external shapes, define a small `Shape` trait whose contract is meaningful for every implementation, such as a read-only `area` operation. Keep `Rectangle` and `Square` as independent value types. Store homogeneous values generically, mixed owned shapes as `Box<dyn Shape>`, or borrowed shapes as `&dyn Shape`.

**Rust ownership mapping.** Dimensions are owned by each shape value; a collection owns its members if stored by value/`Box`, and borrows members if stored as references. If shapes need persistent entity identity, add an explicit ID rather than comparing addresses.

**Tradeoff.** The enum makes alternatives and exhaustive handling visible but requires a coordinated edit when a new variant is added. The trait supports external implementations but commits the API to a contract and dynamic-dispatch boundary if heterogeneous values must coexist. The redesign preserves area behavior while removing the invalid “is-a” promise.

### B. `StorageBackend` / encryption / retry subclasses

**Classical hierarchy and failure.** A base storage class may own a path or connection and define `put`; `LocalStorage` and `CloudStorage` override transport, while `EncryptedStorage` and `RetryingStorage` add cross-cutting behavior. Inheritance then mixes “where data goes” with “how policy wraps each operation,” and combinations tend to multiply subclasses.

**Relationship decision.** Separate transport responsibility, confidentiality policy, and retry authority. Specify who holds credentials, which operations may repeat without duplicate effects, the validity of each dependency, and what failures reach the caller. Wrapping a service must not enlarge the caller’s authorization.

**Rust redesign.** Model a storage capability as a `Store` trait with explicit operations and a typed error result. Implement it for concrete local and remote adapters. Represent encryption and retry as wrappers that each contain an inner store and add one policy around delegation. A service can be generic over `S: Store` for static composition or hold `Box<dyn Store>` when implementations are selected at runtime. This is composition around a capability, not base-class state reuse.

**Rust ownership mapping.** Each wrapper owns its inner store when it controls its lifetime; a borrowed store is appropriate for one call or a service that does not own the adapter. Keep the encryption key in the narrowest secure owner that can perform the operation; do not copy key material into every object merely to mimic an inherited field. The service borrows or owns a configured wrapper based on application lifetime.

**Tradeoff.** Wrappers make policy order explicit (`Retry(Encrypt(Local))` can differ from `Encrypt(Retry(Local))`) and can be assembled without defining every subclass combination. They add forwarding types and may complicate error translation. Use a direct adapter when no real policy variation exists; introduce the wrapper only for a responsibility that can be tested independently.

## 6. Coverage index

| Concept | Section |
|---|---|
| Encapsulation, abstraction, objects/classes | [Core concepts](#1-core-concepts) |
| Identity, value objects, entities | [Identity, value objects, and entities](#identity-value-objects-and-entities) |
| Association, aggregation, composition, dependency | [Relationships](#association-aggregation-composition-and-dependency) |
| Cardinality, object graphs | [Cardinality](#cardinality-and-object-graphs) |
| Mutability, invariants | [Mutability and invariants](#mutability-and-invariants) |
| Constructors, destructors, RAII, lifecycle | [Invariants and lifecycle](#invariants-construction-and-lifecycle) |
| Delegation, composition | [Delegation](#delegation-and-composition) |
| Subtype, parametric, ad hoc polymorphism | [Polymorphism](#three-forms-of-polymorphism) |
| Static/dynamic dispatch; open/closed types | [Dispatch and extension](#static-dispatch-dynamic-dispatch-and-open-sets) |
| Interfaces, traits, bounds, trait objects, supertraits | [Traits](#interfaces-traits-bounds-and-supertraits) |
| Associated types, variance, coherence | [Advanced trait design](#associated-types-variance-and-coherence) |
| State/implementation/interface/behavioral inheritance | [Inheritance meanings](#inheritance-has-several-meanings) |
| LSP contracts, diamond issue | [Contracts](#liskov-substitution-and-behavioral-contracts); [diamond](#the-diamond-problem) |
| SOLID, GRASP | [Design prompts](#solid-and-grasp-as-design-prompts) |
| Null, `Option`, exceptions, `Result` | [Failure modeling](#null-absence-exceptions-and-result) |
| Typestate | [Typestate](#typestate-and-state-machines) |
| Two hierarchy redesigns | [Worked redesigns](#5-worked-hierarchy-redesigns) |

## Sources and limits

The references below are primary language documents, standards, or the original/authoritative OO material used for terminology. They establish the cited language rules or historical design concepts; the ownership recommendations and examples are ROO's design guidance, not claims made by those sources.

- The Rust Project, [The Rust Programming Language](https://doc.rust-lang.org/stable/book/): ownership and borrowing; structs and methods; enums; traits; modules; smart pointers; errors; and the OO/state-pattern chapters. Living documentation; consult the edition/toolchain in use when relying on version-specific details.
- The Rust Project, [The Rust Reference: trait objects](https://doc.rust-lang.org/reference/types/trait-object.html), [traits and dyn compatibility](https://doc.rust-lang.org/reference/items/traits.html), [subtyping and variance](https://doc.rust-lang.org/reference/subtyping.html), and [implementation coherence](https://doc.rust-lang.org/reference/items/implementations.html).
- The Rust Project, standard library documentation for [`Option`](https://doc.rust-lang.org/std/option/enum.Option.html) and [`Result`](https://doc.rust-lang.org/std/result/enum.Result.html).
- Oracle, [Java Tutorials: Object-Oriented Programming Concepts](https://docs.oracle.com/javase/tutorial/java/concepts/), [interfaces](https://docs.oracle.com/javase/tutorial/java/IandI/interfaceDef.html), and [method overriding and defaults](https://docs.oracle.com/javase/tutorial/java/IandI/override.html). These tutorials include Java SE 8-era material; use the current Java Language Specification for release-specific rules.
- Object Management Group, [Unified Modeling Language 2.5.1](https://www.omg.org/spec/UML/2.5.1/PDF), especially association ends and composite aggregation. Shared aggregation semantics are intentionally less prescriptive than composition.
- Barbara Liskov and Jeannette Wing, [“A Behavioral Notion of Subtyping”](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf), ACM Transactions on Programming Languages and Systems, 16(6), 1994.
- Robert C. Martin, [The SOLID Principles of Software Design](https://cleancoder.com/files/solid.md), course outline and associated design material.
- Craig Larman, [Applying UML and Patterns excerpt on responsibility assignment and GRASP](https://www.informit.com/articles/article.aspx?p=360440&seqNum=2).

This first edition is a practical atlas, not an exhaustive survey or formal proof of the recommendations. The executable laboratory, when included, is the place to verify code examples; this document deliberately labels its hierarchy sketches as conceptual and does not assert compiler success for them.
