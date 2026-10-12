# Learning path

This is an initial syllabus for learning ROO (Relationship & Ownership Oriented design), a proposed, language-independent method for describing and reviewing important software relationships. It pairs method practice with a Rust laboratory; it is not a claim to cover all object-oriented, Rust, pattern, or architecture literature.

Use the [canonical contract and six-step procedure](02-relationship-design.md) throughout the stages below.

The Rust implementation and evidence in Stages 3 and 6 provide this syllabus's required Rust laboratory qualification. ROO can be adopted independently in another language by carrying the same scenarios, invariants, and relationship contracts into that language and collecting its own evidence; that adoption does not qualify the Rust laboratory.

Use the same small domain throughout: a library lends physical book copies to members. Returning to one domain makes it easier to see which design decisions come from the problem and which come from a language or pattern.

## Stage 1 — Classical object design: behavior, data, and boundaries

**Read:** selected chapters on object modeling and abstraction from Grady Booch and colleagues' [*Object-Oriented Analysis and Design with Applications*](https://www.pearson.com/en-us/subject-catalog/p/object-oriented-analysis-and-design-with-applications/P200000000143/9780201895513); David Parnas's [module-decomposition paper](https://doi.org/10.1145/361598.361623); and Barbara Liskov's [paper on data abstraction and hierarchy](https://doi.org/10.1145/62139.62141).

**Exercise:** model catalog titles, physical copies, members, and loans. Write rules in plain language before choosing classes. Decide which concepts have identity and which are values. Draw a state transition for checkout and return. Add one inheritance proposal, then explain what substitutability promise it would create.

**Deliver:** a one-page domain vocabulary, invariant list, state diagram, and a first relationship map. Include at least one example where identity is required and one where value equality is enough.

**Review question:** can another implementation replace a subtype without violating the promises clients rely on? If not, prefer a distinct role, value, or capability until a true subtype contract is clear.

## Stage 2 — Make the relationships explicit

**Read:** [ROO foundations](01-foundations.md) and [relationship design](02-relationship-design.md) in this project. Then use the Relationship Contract in [cross-language portability](06-cross-language.md).

**Exercise:** for `Library → Copy`, `Library → Loan`, and `Loan → Member`, fill all eight Relationship Contract fields. In the owner/resource-custodian field, distinguish memory or external-resource custody from domain responsibility when they differ. Decide which object graph links are useful only in memory and which relationships must survive loading from a store.

**Deliver:** a contract table for five relationships that fills all eight fields, plus a short note for each boundary where a reference, ID, copied value, or command is the right interface. Mark every promise by its intended enforcement mechanism—compiler, runtime, storage/protocol, or convention/test—and record the available evidence.

**Review question:** are custody, stable identity, invariant coordination, and caller authorization each explicit rather than collapsed into one answer?

## Stage 3 — Learn Rust ownership by implementing the small model

**Read in order:** the Rust Book chapters on [ownership](https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html), [structs and methods](https://doc.rust-lang.org/book/ch05-00-structs.html), [enums and pattern matching](https://doc.rust-lang.org/book/ch06-00-enums.html), [collections](https://doc.rust-lang.org/book/ch08-00-common-collections.html), [smart pointers](https://doc.rust-lang.org/book/ch15-00-smart-pointers.html), and [concurrency](https://doc.rust-lang.org/book/ch16-00-concurrency.html). Keep the [Rust Reference](https://doc.rust-lang.org/reference/) nearby for precise language rules. Defer unsafe Rust until a safe design and a specific need for unsafe code have been demonstrated.

**Exercise:** implement the library's checkout and return commands with a single `Library` owner, private state, newtypes for durable IDs, immutable loan facts, and typed errors. First expose reads as snapshots. Then add a concurrent service boundary only if the use case requires one.

**Deliver:** a small crate, allowed and rejected transition examples, and at least one compile-fail example showing an unwanted alias or invalid reference lifetime. For each compiler error fixed, record what relationship decision it revealed.

### Borrow-checker friction as design information

Treat an error as evidence about the code's current access graph, not an automatic instruction to add a clone, `Rc`, or `RefCell`.

| Symptom | Questions and common design responses |
| --- | --- |
| A value was moved and is used again | Is the operation transferring ownership, borrowing briefly, or returning a copied value? Make the intended transfer explicit; clone only if a distinct copy is semantically correct. |
| A second mutable borrow is rejected | Do two operations need to mutate at once, or can one aggregate method perform the transition? Can disjoint fields be borrowed separately? Shorten the first borrow before introducing interior mutability. |
| A reference does not live long enough | Which object owns the referent, and what is the promised validity horizon? Shorten the reference's use, return an owned value/ID, or carry an explicit lifetime when the API truly borrows. Do not use `'static` to silence a real horizon mismatch. |
| A borrow escapes into a stored callback or async task | Does the task need a durable owned snapshot, a stable ID for later lookup, or shared ownership? State cancellation and stale-data behavior before selecting an owned value, `Arc`, or a message. |
| Many `Rc<RefCell<_>>`, `Arc<Mutex<_>>`, or clones appear | Is sharing actually required, or is the domain owner unclear? Try one owner plus IDs and commands first. Retain shared state only when its access and synchronization contract is explicit. |

For each friction point, reduce the code to a small example, name the desired invariant and validity horizon, choose the narrowest access regime that meets them, and then re-run the example. Compiler acceptance proves only the language property being checked; it does not prove the lending policy or persistence behavior.

## Stage 4 — Translate the GoF catalog by intent

**Read:** the [original *Design Patterns* publisher record](https://www.informit.com/store/design-patterns-elements-of-reusable-object-oriented-software-9780201633610) and the project's [pattern catalog](04-pattern-catalog.md). Study the intent, trade-offs, and collaboration of all 23 patterns, but implement only patterns that solve a stated problem.

**Exercise:** choose one behavioral, one structural, and one creational pattern from a real feature. For each, describe the pressure it addresses, then compare the original object participants with Rust alternatives such as enums, traits, closures, owned components, or borrowed collaborators. Try at least one design that uses no named pattern.

**Deliver:** three short pattern decision records. Each record names the relationship contract for its participants, expected lifetime, invariant coordinator, caller permissions, and reason to keep or remove the indirection. Include one pattern that is not a fit and why.

**Review question:** did the pattern make a variation or collaboration easier to change, or did it merely add types and allocations?

## Stage 5 — Move from objects to architecture

**Read:** Martin Fowler's [*Patterns of Enterprise Application Architecture*](https://martinfowler.com/books/eaa.html) and [pattern catalog](https://martinfowler.com/eaaCatalog/index.html), Eric Evans's [Domain Language course](https://www.domainlanguage.com/), and the SEI authors' [*Documenting Software Architectures: Views and Beyond*](https://www.sei.cmu.edu/library/documenting-software-architectures-views-and-beyond-second-edition/). These are complementary lenses on domain boundaries, recurring application structures, and architecture communication.

**Exercise:** separate the lending policy from persistence and from an HTTP or command-line adapter. Draw a dependency view and one runtime sequence. Evaluate two quality pressures, such as concurrent checkouts and availability during storage failure. Record the consistency and failure boundary rather than saying only “the repository owns it.”

**Deliver:** one context/dependency diagram, one sequence, two short architecture decisions, and a test plan showing which boundary verifies each invariant.

## Stage 6 — Capstone: build, explain, and translate

Implement a small lending service in Rust. Include copy/member/loan IDs, checkout and return, conflict and not-found failures, an in-memory repository, and a persistence-facing boundary. Keep durable identity distinct from memory ownership. Use the Java example in [cross-language portability](06-cross-language.md) as a mapping exercise; CI compiles and executes its assertions separately from the Rust doctests. Those checks cover the chapter examples, not a complete lending service. For a complete shared Java/Rust exercise with persistence and failure recovery, follow the [orders and payments track](../case-studies/orders-payments/track/README.md).

**Capstone deliverables:**

1. A relationship-contract ledger covering every mutable or externally managed relationship.
2. Rust code with focused unit tests for success, duplicate checkout, stale IDs, return of an unknown loan, and repository failure.
3. One test or executable scenario for concurrent checkout if concurrency is in scope; otherwise state the single-thread confinement rule.
4. An optional Java mapping with the same domain invariants and a clear note about garbage collection, resource closure, and aliasing. Keep it separate from Rust build and test evidence.
5. An architecture diagram and decision record explaining one pattern used, one declined, and why.
6. A short reflection separating compiler guarantees, runtime enforcement, and conventions that still need tests or operational discipline.

### Assessment rubric

Score each dimension from 0 to 3: **0** absent or incorrect; **1** named but implicit; **2** explicit and backed by code or tests; **3** survives a relevant failure/alias/concurrency case and the trade-off is justified.

| Dimension | Evidence for a strong result |
| --- | --- |
| Ownership and responsibility | Memory owner, domain invariant owner, and external resource custodian are identified separately. |
| Identity and validity | IDs survive serialization as intended; stale or missing IDs produce defined outcomes; borrowed references have a stated horizon. |
| Mutation and access | Commands protect invariants; read paths avoid leaking mutable internals; concurrency matches the declared execution domain. |
| Lifecycle and failure | Files/connections/transactions have explicit cleanup; partial failure does not silently violate the invariant. |
| Pattern and architecture | Pattern choice follows a concrete pressure; boundaries and quality trade-offs are communicated with useful diagrams. |
| Language evidence | Claims distinguish compiler checks, runtime checks, and conventions; tests exercise the properties that the language does not prove. |

## Curated starter shelf

This is a first route through a broad subject. Use the primary language and author/publisher sources above for foundations; choose deeper references in response to a concrete project question.

| Topic | Starting source | Why it is in the path |
| --- | --- | --- |
| Object analysis and design | Booch et al., [*Object-Oriented Analysis and Design with Applications*](https://www.pearson.com/en-us/subject-catalog/p/object-oriented-analysis-and-design-with-applications/P200000000143/9780201895513) | A practical foundation for modeling classes, responsibilities, and collaborations. |
| Modularity and abstraction | Parnas, [“On the Criteria to Be Used in Decomposing Systems into Modules”](https://doi.org/10.1145/361598.361623); Liskov, [“Data Abstraction and Hierarchy”](https://doi.org/10.1145/62139.62141) | Classic arguments for hiding decisions and treating subtype promises as behavioral contracts. |
| Rust mechanics | [The Rust Programming Language](https://doc.rust-lang.org/book/) and [Rust Reference](https://doc.rust-lang.org/reference/) | The Book teaches the workflow; the Reference is a closer source for language rules. |
| Reusable designs | Gamma, Helm, Johnson, and Vlissides, [*Design Patterns*](https://www.informit.com/store/design-patterns-elements-of-reusable-object-oriented-software-9780201633610) | A shared vocabulary and trade-off catalog, to apply by intent rather than checklist. |
| Domain and application architecture | Evans's [Domain Language](https://www.domainlanguage.com/); Fowler's [PoEAA catalog](https://martinfowler.com/eaaCatalog/index.html) | Connects domain language and invariants with recurring application structures. |
| Architecture communication | Clements et al., [*Views and Beyond*](https://www.sei.cmu.edu/library/documenting-software-architectures-views-and-beyond-second-edition/) | Teaches how to describe architecture for different stakeholders and concerns. |

