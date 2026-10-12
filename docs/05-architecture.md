# 05 — Architecture through ownership and boundaries

ROO — Relationship & Ownership Oriented design — starts architectural work with scenarios and invariants, then decides relationships before choosing language, runtime, storage, or protocol mechanisms. The method is language-independent; Rust is this edition's laboratory language. It does not replace domain analysis, concurrency protocols, database constraints, or operational design. The relationship vocabulary below is a **proposed ROO synthesis**; the schools and research it draws on have independent histories. [The annotated literature ledger](../research/literature.md) records that distinction.

## 1. Start with the decision that must remain changeable

Parnas argues for decomposing a system around hidden design decisions rather than merely its processing steps. A Rust module can hide a representation behind private fields and functions, but privacy alone does not hide a decision if callers depend on SQL rows, concrete framework errors, or a particular allocation graph. [Parnas, 1972](https://www.cs.lafayette.edu/~gexia/cs301/resources/parnas.html).

For ROO, establish the scenario and invariant, then write the decision that must remain changeable: “pricing policy varies independently from transport,” or “inventory persistence may change.” Record the affected relationship's custody, identity, invariant coordination, caller authorization, access, horizon, execution, and failure policy before choosing the smallest boundary that protects it. A function parameter or private module may be sufficient; a trait, crate, service, and network protocol each add costs. This is a design recommendation, not a result proved by Parnas or Rust.

Liskov and Wing define behavioral subtyping through preserved properties, including invariants and history constraints. Compatible method signatures are insufficient. A trait implementation that silently changes ordering, idempotency, or failure semantics can violate client expectations while compiling successfully. [Liskov and Wing, 1994](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf).

Consequently a port contract should describe observable behavior before selecting signatures such as `&self`, `&mut self`, and return types. Does success mean durable acceptance? Can an error follow a completed remote effect? Which retry is safe? Keep compiler/static evidence separate from runtime checks, database guarantees, protocol evidence, and human review. Contract tests exercise particular promises; they do not establish every possible execution, and an unverified infrastructure expectation remains an assumption.

## 2. Three useful lenses with different jobs

The GoF catalog describes 23 recurring object design solutions, grouped as creational, structural, and behavioral patterns. It supplies a vocabulary of collaboration and variation, not a complete architecture prescription. The Rust translations belong in [the pattern catalog](04-pattern-catalog.md). [Gamma, Helm, Johnson, and Vlissides, published 1994 / copyright 1995](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698).

SOLID addresses change and abstraction: single responsibility concerns reasons for change; open/closed concerns extension without repeatedly modifying stable policy; Liskov substitution concerns behavioral compatibility; interface segregation limits unnecessary client dependencies; dependency inversion directs dependencies toward policy abstractions. These are heuristics to discuss, not five mechanical rules requiring five traits. [Robert C. Martin, 2020 restatement](https://blog.cleancoder.com/uncle-bob/2020/10/18/Solid-Relevance.html).

GRASP addresses responsibility assignment. Information Expert asks who has the knowledge; Creator asks who should construct; Controller receives a system operation; Low Coupling and High Cohesion assess placement; Polymorphism distributes variation; Pure Fabrication introduces a useful technical responsibility; Indirection mediates; Protected Variations stabilizes a change point. [Larman, second edition publisher contents and excerpt](https://www.informit.com/store/applying-uml-and-patterns-an-introduction-to-object-9780130925695).

ROO adds a question to each lens: which component preserves the invariant, which caller may request a change, what access is provided, and how long is it valid? A GRASP controller might borrow a store for one call; a GoF strategy might be an owned enum; dependency inversion might be a generic parameter. These choices need no dependency injection container.

## 3. DDD vocabulary, relationship decisions, and Rust realizations

DDD models a domain within an explicit language and context. An **entity** has continuity of identity; a **value object** is defined by attributes rather than identity. An **aggregate** groups related objects behind a root that protects invariants. A **repository** provides access to aggregate roots; a **domain event** represents a meaningful occurrence. A **bounded context** delimits where a particular model and language apply. [Evans, DDD Reference, 2015](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf).

The following are ROO translations, not additional DDD definitions:

| Concept | Relationship decision | Rust realization or constraint |
|---|---|---|
| Entity | Specify continuity of identity independently of loaded instances. | Give it a typed stable ID; moving a Rust value must not change its domain identity. |
| Value object | Validate construction and expose intentional operations. | `Copy` and `Clone` are separate technical decisions. |
| Aggregate | Name the invariant coordinator separately from the custodian of loaded state. | Prefer one custodian of mutable aggregate state; expose commands rather than arbitrary internal mutable references. |
| Repository | Introduce an abstraction for a domain access need, not automatically for every table. | Choose the trait or concrete API after defining lookup, failure, and consistency behavior. |
| Domain event | Retain facts from successful transitions; external publication needs a separate durability protocol. | Return owned facts when consumers must outlive local access. |
| Bounded context | Translate identities, meanings, and schemas at the boundary. | Do not pass internal mutable graphs across it. |

An aggregate root may own a `Vec<LineItem>` and store a `CustomerId` without owning the customer. Database rows may reconstruct one aggregate; one row may also feed several read projections. Allocation layout does not determine aggregate size or transaction scope.

An application service coordinates a use case: authorization, loading, calling domain behavior, persisting, and reporting an outcome. Domain services express domain behavior that has no natural entity/value owner. Infrastructure services implement technical access. Keeping these roles explicit avoids making an “OrderService” responsible for every concern.

## 4. Distinguish four boundaries

| Boundary | Main question | Example | What it does not establish |
|---|---|---|---|
| Memory / resource | Who owns this value or resource, and who may access it? | A request owns its command; a transaction guard controls a connection. | Durable atomicity or remote authorization. |
| Invariant / transaction | Which changes must become visible together? | Order, stock decrement, and outbox insertion in one database transaction. | A process or deployment boundary. |
| Semantic / context | Where does a word and model retain its meaning? | Sales order versus warehouse shipment. | A required database or service per context. |
| Deployment / failure | What can fail, restart, scale, or be released independently? | One process with modules; later, an independent warehouse service. | A guarantee that local type invariants survive network failure. |

A borrow's validity horizon is a language constraint. A reservation expiry is a domain/protocol constraint. A database transaction ends with commit or rollback. A deployment survives neither by virtue of a borrow nor because a root owns a vector. [Rust ownership rules](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html) and [PostgreSQL transaction semantics](https://www.postgresql.org/docs/current/tutorial-transactions.html) describe different mechanisms.

## 5. Hexagonal, layered, onion, and clean designs

Cockburn's ports and adapters separate the application from external devices. A driving adapter invokes a use case; a driven adapter supplies a capability the application needs. A port expresses a conversation meaningful to the application, not necessarily one Rust trait or one HTTP endpoint. [Cockburn, original 2005 article](https://alistair.cockburn.us/hexagonal-architecture).

For ROO, the composition root owns long-lived adapters; an application service borrows the needed capabilities for a call, or owns handles when its execution horizon requires that. Adapters own connections, pools, transport buffers, and serialization details. Domain values should not acquire a database lifetime merely because an adapter fetched them.

Layering organizes responsibilities and permitted dependencies; it can be strict or allow selected bypasses. Onion places domain concerns inward and infrastructure outward. Clean architecture similarly points source dependencies inward and separates use cases from external mechanisms. These are related approaches, not identical diagrams or a mandated number of folders. [Palermo, 2008](https://jeffreypalermo.com/2008/07/the-onion-architecture-part-1/); [Martin, 2012](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html).

The ROO decision is to document both dependency direction and resource custody. A domain-owned port can be implemented by an infrastructure adapter even though runtime calls flow outward. Whether a capability is generic, an enum, or `dyn Trait` depends on variation and composition requirements. Native async traits, associated futures, or an explicit boxed future are deliberate alternatives; `async-trait` is not a default dependency.

Persistence DTOs belong to the adapter's representation. Decode and validate them into domain values, and explicitly handle invalid historical records. Avoid returning references into a short-lived database row buffer. If borrowing a decoded buffer is desirable for performance, expose and document that lifetime intentionally. Use an owned response DTO when a response must outlive the loaded aggregate.

## 6. CQRS and event sourcing are separate decisions

CQRS separates update and query models; it can share a database and need not use different deployments. Fowler warns that the added complexity is often unjustified. [Fowler, 2011](https://martinfowler.com/bliki/CQRS.html).

ROO therefore permits a command to load an aggregate while a query adapter returns a projection DTO. A query result is a snapshot, not permission or access to mutate the entity. Choose an acceptable staleness contract before introducing asynchronously maintained projections.

Event sourcing records state changes as events and supports reconstruction through replay. An event log and an audit trail are not interchangeable merely because both contain events. Schema evolution, snapshots, deterministic replay, and external effects require explicit policies. [Fowler, 2005 draft](https://martinfowler.com/eaaDev/EventSourcing.html).

In ROO, replay consumes owned historical data and builds state through a controlled transition function. A replay path must not accidentally charge a payment or reserve stock again. CQRS can exist without event sourcing, and event sourcing can exist without a separately deployed query service.

## 7. Functional core, data-oriented design, and ECS

Functional core / imperative shell moves decisions into functions over data and effects into an outer coordinator. This gives a useful alternative to a large graph of interacting service objects. [Gary Bernhardt's screencast](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell).

A ROO core can consume `OrderDraft` and produce either a validated `OrderPlan` or a domain error. Its shell obtains facts, executes effects, and interprets failures. Pure decisions do not make previously read facts current: the shell must enforce versions, locking, or another concurrency protocol at commit.

Data-oriented design emphasizes actual data and transformations, layout, measurement, and access patterns. ECS separates entities, components, and systems; Bevy uses this to organize state and processing. [Fabian's online book, 2018](https://www.dataorienteddesign.com/dodbook/); [Bevy ECS documentation](https://bevy.org/learn/quick-start/getting-started/ecs/).

ROO does not require every conceptual object to become a heap allocation. A world/store may own component arrays; entity handles identify entries; systems receive restricted access. Generational handles can detect reuse, but do not replace business IDs or database concurrency control. Choose ECS for its processing needs, not to reproduce an enterprise object model under new names.

## 8. Actors, events, and structured concurrency

The actor tradition models computation through independently interacting actors and messaging. It predates Rust; messaging is not a ROO invention. [Hewitt, Bishop, and Steiger, 1973](https://www.ijcai.org/Proceedings/73/Papers/027B.pdf).

A ROO actor can exclusively own mutable state and receive owned commands. Its address is an access handle, not a borrowed reference to that state. Specify mailbox capacity, ordering scope, reply lifetime, supervision, and behavior after a caller stops waiting. Processing messages sequentially does not make a multi-actor workflow atomic.

Messaging patterns describe routing, endpoints, transformation, and channels. Event-driven systems still need explicit schemas, correlation, retries, backpressure, and duplicate handling. [Hohpe and Woolf's pattern catalog](https://www.enterpriseintegrationpatterns.com/patterns/messaging/). Causal ordering is not a global clock ordering guarantee. [Lamport, 1978](https://lamport.azurewebsites.net/pubs/time-clocks.pdf).

Structured concurrency ties child work to a scope with explicit completion and error propagation. It makes task lifetimes easier to reason about; it does not undo externally completed work. [Nathaniel J. Smith, 2018](https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/).

For Rust async code, review every suspension point: what is owned, which guard remains held, and what state survives cancellation? Rust's `Future` describes polling, not business rollback. Tokio documents cancellation safety for operations used with `select!`; its shutdown guidance separates requesting shutdown from waiting for tasks to finish. [Future](https://doc.rust-lang.org/std/future/trait.Future.html); [Tokio `select!`](https://docs.rs/tokio/latest/tokio/macro.select.html); [Tokio shutdown](https://tokio.rs/tokio/topics/shutdown).

Avoid holding a synchronous mutex guard across `.await`. Avoid detached tasks for required cleanup. A supervisor may continue durable work after an HTTP request disappears, but then its custody, shutdown, and recovery policy must be explicit. A dropped future is not evidence that the server did nothing.

## 9. Worked use case: place an order

This is a **ROO design exercise**, not an executable claim about the laboratory. The business rule is: accept an order only after its requested quantities are reserved, while preventing duplicate acceptance for the same request. Use exact monetary values and validated positive quantities; pricing and authentication are supplied facts, not hidden globals.

First decide that Order controls its line transitions, the request has a deduplication identity, and the application coordinator obtains authorized capabilities for reservation and acceptance. Resource custody does not itself grant business permission: an adapter can retain a connection while the application checks the principal's authority. Next choose a modular application in one process as this exercise's realization. `Order` owns its lines and transitions; `OrderId`, `ProductId`, and `RequestId` are stable identities. A request owns `PlaceOrder`; an application service coordinates capabilities. No `Rc<RefCell<Order>>`, service locator, or repository-per-table scheme is needed.

### Relationship contract for this use case

| Field | Concrete decision |
|---|---|
| Owner / resource custodian | Command belongs to request; aggregate belongs to use-case execution; adapter controls transaction resource; durable store retains committed state. |
| Stable identity | `OrderId` identifies the order; `RequestId` deduplicates one operation; a remote `ReservationId` identifies reservation state. |
| Invariant coordinator | `Order` methods guard local transitions; transaction capability coordinates writes; remote inventory service alone changes remote stock. |
| Authorization | The application must verify the principal's permission to place this order and request inventory reservation. This is a design requirement, not an implemented policy in this exercise. |
| Access regime | Operation-scoped access for decisions; transferred payload custody across queues; scoped transaction access. Rust realizes local access with short borrows and queue payloads with owned values. |
| Validity horizon | Local access ends with the operation; quoted price and reservation each have explicit expiry/version rules; durable identities survive reload. |
| Execution domain | Local domain decision; adapter calls may suspend; durable worker coordinates recovery if remote effects are involved. |
| Failure boundary | Local DB commit is one boundary; remote reservation, reply delivery, and event relay are separate boundaries. |

### Case A: inventory shares the transaction resource

1. Validate and authorize the command before opening a transaction where possible.
2. Open a short transaction; claim `RequestId` with a database uniqueness rule and resolve retries to the existing result.
3. Read current stock and prices under the selected concurrency protocol. Atomically condition stock updates on sufficient quantities, or use suitable locking/isolation; an earlier in-memory check alone is insufficient.
4. Construct the accepted order; write its rows, stock changes, deduplication result, and outbox record through the same transaction resource.
5. Commit; report acceptance only after a known successful commit. Let a separate relay publish committed outbox records.

If reservation or any write fails before commit, roll back the whole local transaction. A mutated in-memory aggregate must be discarded or restored rather than exposed as accepted. If commit returns an uncertain outcome after a connection failure, do not blindly repeat stock changes: query by `RequestId` using a fresh connection and reconcile whether commit occurred.

This needs a transaction-shaped capability, such as `commit_order_with_stock_and_events`, or a scoped unit of work. Three unrelated `save` methods do not promise shared atomicity. The implementation must make isolation, uniqueness, and atomic commit true; a trait name cannot do so. [PostgreSQL transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html).

### Case B: inventory is remote

The local transaction cannot roll back a remote reservation. Use a durable workflow with explicit intermediate states and idempotent operations, or choose a different business contract. Sagas divide a long transaction into steps with compensations; compensation is a business action, not time travel. [Garcia-Molina and Salem, 1987](https://sigmodrecord.org/1987/12/09/sagas/).

1. Persist `PendingReservation` and a durable reservation intent with `RequestId` before issuing remote work. A worker retries the intent using that same key.
2. Reserve remotely with idempotent semantics and a retrievable outcome. A timeout is `Unknown`, not a definitive rejection; reconcile before requesting a conflicting action.
3. After a confirmed reservation, persist its token and the next workflow state. If that local commit fails, the durable intent still permits reconciliation; do not rely only on an in-memory token for cleanup.
4. Confirm/finalize the reservation according to its expiry protocol. If a lease can expire before acceptance, revalidate or finalize it before recording `Accepted`; a remote timeout again requires reconciliation.
5. Commit `Accepted` and its outbox event locally. If acceptance cannot complete, persist a compensating release intent. Retry failed compensation and surface unresolved states for operations.

Persisting an intent alone does not provide exactly-once effects. The remote service must honor idempotency keys and permit status lookup or another reconciliation protocol. Durable workflow state must distinguish reserved, finalized, accepted, release-pending, and rejected outcomes as needed by the actual provider; token expiry and finalized-release rules are part of that provider contract.

If the client disconnects after reservation or during commit, cancellation must not erase the workflow. Stop waiting at the request boundary while a supervised worker owns the durable operation, or let recovery resume it. `Drop` cannot await a remote release; aborting a task does not establish whether a remote request committed. A graceful shutdown must drain or checkpoint required work before the process exits.

### Events, outbox, and observable success

An in-memory `OrderAccepted` is a candidate fact until the authoritative state commits. Publishing before commit can announce nonexistent acceptance; publishing after commit without durable recording can lose the event on a crash.

A transactional outbox records state and the intent to publish atomically in one database. Its relay can publish twice if it crashes after sending but before marking delivery. Consumers need deduplication and idempotent effects; ordering, retention, relay lag, poison messages, and replay remain operational obligations. [Transactional outbox pattern](https://microservices.io/patterns/data/transactional-outbox.html).

An outbox does not atomically commit stock in a remote service, ensure that an email is sent once, or guarantee immediate projection visibility. Define whether the API reports `Pending`, `Accepted`, or `Rejected`, and offer a status lookup by stable ID when a response may be lost. Test failures between each durable step, not only the happy path.

## 10. Ownership-aware predecessors and limits

Ownership types already studied ownership and alias protection in OO systems. Separation logic provides local reasoning about disjoint mutable resources. RustBelt establishes machine-checked safety results for a realistic subset of Rust and verified library extensions, not correctness of arbitrary Rust business software. [Clarke, Potter, and Noble, 1998](https://cs.ioc.ee/ewscs/2010/mycroft/clarke-etal-oopsla98.pdf); [Reynolds, 2002](https://www.cs.cmu.edu/~jcr/seplogic.pdf); [Jung, Jourdan, Krebbers, and Dreyer, POPL 2018](https://plv.mpi-sws.org/rustbelt/popl18/).

Capability-oriented work treats authority as something explicitly granted through references. ROO uses this as a design influence when it narrows a service's access to necessary operations. A Rust reference alone is not an authorization system: ambient globals, filesystem/network access, and interior mutability can grant additional powers. [Miller and Shapiro, 2003](https://erights.org/talks/asian03/index.html).

ROO's proposed contribution is a practical review discipline connecting these concerns in a relationship contract and boundary walkthrough. This edition supplies no systematic literature survey, adoption study, comparative productivity result, or novelty proof. Rust can rule out classes of memory misuse in safe code; it cannot prove a reservation protocol, a domain invariant hidden behind arbitrary code, or a deployment's availability.

## 11. Architecture review prompts

- Which decisions are hidden, and which caller dependency would expose them?
- Is domain identity independent from address, allocation, and loaded snapshot?
- Does each mutable resource have a named custodian and an intentional access regime?
- Which invariant requires atomic commit, and which external effect lies outside it?
- At every await, timeout, or restart, can the operation be recovered without inventing an outcome?
- Are interface contracts explicit about retries, unknown outcomes, ordering, and durable success?
- Does a new abstraction remove a real coupling or merely add another place to navigate?
- Can the design remain a modular monolith until an independently justified deployment boundary appears?

Continue with [cross-language transfer](06-cross-language.md).
