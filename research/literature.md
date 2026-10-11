# ROO literature and claim ledger

Verified for this edition on **2026-10-11** through web search/open of primary papers, author sites, original publishers, or official project documentation. Verification means the cited content was retrievable or indexed as described below; it does not mean every book was read cover to cover or every linked PDF was rendered.

**Established** labels an existing published concept, not universal agreement or empirical superiority. **ROO translation** labels an interpretation for Rust. **Proposed synthesis** labels this edition's relationship contract and workflow. Neither latter label is a claim of historical priority. No secondary pattern blog is used as authority for the conceptual foundations below.

## Modular design, OO contracts, and responsibilities

### S01 — Information hiding

David L. Parnas, **1972**, “On the Criteria To Be Used in Decomposing Systems into Modules.” [University-hosted paper transcription](https://www.cs.lafayette.edu/~gexia/cs301/resources/parnas.html); [original ACM record](https://dl.acm.org/doi/10.1145/361598.361623).
**Established:** decomposing around hidden decisions rather than only execution steps. The ACM endpoint returned 403; the university transcription was accessible and explicitly warns of possible transcription inaccuracies. No exact quotation relies on it. **ROO translation:** review representation leakage and choose a sufficient module boundary.

### S02 — Behavioral subtyping

Barbara H. Liskov and Jeannette M. Wing, **1994**, “A Behavioral Notion of Subtyping,” TOPLAS 16(6), 1811–1841. [Author-hosted paper](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf).
**Established:** preservation of specified behavioral properties, invariants, and history constraints; signatures alone are insufficient. **ROO translation:** trait contracts include effects, retries, and failure semantics. This paper's safety-property account is not a proof of application liveness.

### S03 — GoF patterns

Erich Gamma, Richard Helm, Ralph Johnson, and John Vlissides, **published 1994, copyright 1995**, *Design Patterns: Elements of Reusable Object-Oriented Software*. [Original publisher listing and contents](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698).
**Established:** 23 named creational, structural, and behavioral patterns. Publisher metadata verifies attribution and organization; it is not full-text evidence for every implementation tradeoff. **ROO translation:** replace inherited implementation graphs with suitable values, traits, enums, and explicit ownership where helpful.

### S04 — SOLID

Robert C. Martin, **2020**, “Solid Relevance.” [Author's article](https://blog.cleancoder.com/uncle-bob/2020/10/18/Solid-Relevance.html).
**Established:** an authorial restatement of the five principles, including their relevance beyond inheritance. This is not evidence that Martin originated every underlying idea or that 2020 was their first publication. **ROO translation:** apply the principles to Rust dependencies and behavioral contracts without mechanically multiplying traits.

### S05 — GRASP

Craig Larman, *Applying UML and Patterns*, **second edition publisher listing: 2001**. [Publisher contents/preface](https://www.informit.com/store/applying-uml-and-patterns-an-introduction-to-object-9780130925695); [publisher sample chapter](https://www.informit.com/content/images/0130925691/samplechapter/0130925691.pdf).
**Established:** responsibility assignment patterns, including Information Expert, Creator, Controller, coupling/cohesion, Polymorphism, Pure Fabrication, Indirection, and Protected Variations. Contents and sample text were available. **ROO translation:** add authority, access, and validity questions to responsibility assignment; GRASP and SOLID remain distinct lenses.

## Domain and dependency boundaries

### S06 — Domain-driven design

Eric Evans, **2015**, *Domain-Driven Design Reference: Definitions and Pattern Summaries*. [Author organization's PDF](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf); [reference landing page](https://www.domainlanguage.com/ddd/reference/).
**Established:** domain language, entities, value objects, aggregates, repositories, domain events, and bounded contexts. PDF cover verifies 2015; the landing page describes its relation to the earlier book. **ROO translation:** separate domain identity, memory custody, and durable consistency.

### S07 — Hexagonal architecture

Alistair Cockburn, **2005**, “Hexagonal architecture.” [Author's original article](https://alistair.cockburn.us/hexagonal-architecture).
**Established:** application isolation through ports and adapters, including driving and driven interactions. The article displays a 2005 technical-report date; related author pages use different month labels, so this edition claims the year only. **ROO translation:** identify adapter resource custody and the ownership of port inputs/outputs.

### S08 — Onion architecture

Jeffrey Palermo, **2008**, “The Onion Architecture: part 1.” [Author's article](https://jeffreypalermo.com/2008/07/the-onion-architecture-part-1/).
**Established:** domain-centered dependency organization with infrastructure outside. **ROO translation:** dependency direction and runtime resource custody need separate descriptions. The article is architecture guidance, not comparative empirical evidence.

### S09 — Clean architecture

Robert C. Martin, **2012**, “The Clean Architecture.” [Author's article](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html).
**Established:** inward source dependencies and boundaries between policy/use cases and external mechanisms. **ROO translation:** boundary DTOs and capabilities must also state ownership and validity. Layered, onion, clean, and hexagonal approaches overlap without being identical.

## State, effects, and data processing

### S10 — CQRS

Martin Fowler, **2011**, “CQRS.” [Author's article](https://martinfowler.com/bliki/CQRS.html).
**Established:** distinct update/read models and substantial complexity cautions; Fowler attributes his exposure to Greg Young. **ROO translation:** query DTOs are snapshots, not mutable entity authority. Separate services and event sourcing are optional additional choices.

### S11 — Event sourcing

Martin Fowler, **2005**, “Event Sourcing.” [Author's article](https://martinfowler.com/eaaDev/EventSourcing.html).
**Established:** recording changes as events and reconstructing state through replay; external effects complicate replay. The author labels this material a draft. **ROO translation:** controlled reconstruction and separate external-effect execution. This ledger does not claim Fowler invented the technique.

### S12 — Functional core / imperative shell

Gary Bernhardt, “Functional Core, Imperative Shell.” [Author's screencast page](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell).
**Established:** separation of decision-making data transformations from effects. No publication year is asserted because the retrieved page did not establish one. **ROO translation:** return owned plans/results and let the shell enforce commit-time concurrency and failure handling.

### S13 — Data-oriented design

Richard Fabian, **2018 online release footer**, *Data-Oriented Design*. [Author's online book](https://www.dataorienteddesign.com/dodbook/).
**Established:** data, transformations, layout, and measurement as design concerns. The online edition identifies omitted material and conversion limitations. **ROO translation:** collection ownership and access patterns can matter more than per-instance object graphs.

### S14 — Entity component systems

Bevy contributors, current official “ECS” introduction. [Official documentation](https://bevy.org/learn/quick-start/getting-started/ecs/).
**Established:** entities, components, and systems as a concrete Rust framework organization. No invention date is inferred. **ROO translation:** a world/store can be the memory custodian while handles provide identity and systems receive restricted access. Framework scheduling is not database transaction isolation.

## Concurrent and distributed execution

### S15 — Actors

Carl Hewitt, Peter Bishop, and Richard Steiger, **1973**, “A Universal Modular ACTOR Formalism for Artificial Intelligence.” [Original IJCAI proceedings paper](https://www.ijcai.org/Proceedings/73/Papers/027B.pdf).
**Established:** actor-based modular computation. **ROO translation:** isolate mutable state behind owned messages and explicit reply/cancellation contracts. Actor frameworks add their own delivery and supervision semantics; those are not all established by this early paper.

### S16 — Structured concurrency

Nathaniel J. Smith, **2018**, “Notes on structured concurrency, or: Go statement considered harmful.” [Author's essay](https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/).
**Established:** scoped concurrent tasks, completion, and propagation rationale. The essay acknowledges predecessors; this edition does not claim it invented all scoped-concurrency ideas. **ROO translation:** task custody and validity horizons must be explicit, especially when request and durable-operation lifetimes differ.

### S17 — Messaging patterns

Gregor Hohpe and Bobby Woolf, *Enterprise Integration Patterns*, author-maintained catalog. [Messaging patterns overview](https://www.enterpriseintegrationpatterns.com/patterns/messaging/).
**Established:** channels, routing, transformation, and endpoints. No book year is inferred from this overview alone. **ROO translation:** owned event payloads still need schema, correlation, and operational contracts; messaging does not remove coupling.

### S18 — Distributed ordering

Leslie Lamport, **1978**, “Time, Clocks, and the Ordering of Events in a Distributed System.” [Author-hosted paper](https://lamport.azurewebsites.net/pubs/time-clocks.pdf).
**Established:** happened-before and logical-clock reasoning. **ROO translation:** distinguish causal and transport ordering from a universal real-time order. This source does not establish every modern broker's guarantees.

### S19 — Sagas

Hector Garcia-Molina and Kenneth Salem, **1987**, “Sagas.” [Original SIGMOD Record entry](https://sigmodrecord.org/1987/12/09/sagas/); [Princeton paper URL indexed by search](https://www.cs.princeton.edu/techreports/1987/070.pdf).
**Established:** decomposing long-lived transactions into steps with compensations. The original record was accessible and the Princeton abstract was indexed; direct PDF fetch failed. **ROO translation:** persist remote-operation progress and compensation intents; model unresolved outcomes instead of equating timeout with failure.

### S20 — Transactional outbox

Chris Richardson, “Pattern: Transactional outbox.” [Author's pattern catalog](https://microservices.io/patterns/data/transactional-outbox.html).
**Established:** atomically storing business changes and publication intent, with duplicate-relay consequences. No first-publication year is asserted. **ROO translation:** outbox durability is separate from remote-stock atomicity, consumer idempotency, and successful notification delivery.

## Ownership, authority, and language semantics

### S21 — Ownership types

David G. Clarke, John M. Potter, and James Noble, **1998**, “Ownership Types for Flexible Alias Protection.” [Paper in academic-hosted proceedings copy](https://cs.ioc.ee/ewscs/2010/mycroft/clarke-etal-oopsla98.pdf); [coauthor's bibliography](https://homepages.ecs.vuw.ac.nz/~kjx/cv.html).
**Established:** ownership annotations and alias-protection reasoning in object systems. Paper text was indexed and coauthor metadata confirmed authors/year. **ROO translation:** explicit representation custody continues a preexisting research tradition; Rust's ownership discipline is not identical to this type system.

### S22 — Separation logic

John C. Reynolds, **2002**, “Separation Logic: A Logic for Shared Mutable Data Structures.” [Author-hosted paper](https://www.cs.cmu.edu/~jcr/seplogic.pdf).
**Established:** reasoning about disjoint heap resources and controlled sharing, crediting joint work with Peter O'Hearn and others. **ROO translation:** local responsibility benefits from explicit resource boundaries. ROO does not provide a separation-logic calculus or proof.

### S23 — RustBelt

Ralf Jung, Jacques-Henri Jourdan, Robbert Krebbers, and Derek Dreyer, **POPL 2018**, “RustBelt: Securing the Foundations of the Rust Programming Language.” [Research project's paper and artifacts](https://plv.mpi-sws.org/rustbelt/popl18/).
**Established:** machine-checked safety for a realistic Rust subset and extensible unsafe-library verification conditions. **Limit:** not a proof of every Rust compiler version, crate, application invariant, or distributed workflow. **ROO translation:** distinguish language safety from architectural correctness.

### S24 — Capability-oriented design

Mark S. Miller and Jonathan S. Shapiro, **2003**, “Paradigm Regained: Abstraction Mechanisms for Access Control.” [Authors' article/version page](https://erights.org/talks/asian03/index.html).
**Established:** authority through capabilities and abstraction mechanisms. The author-site content was available in indexed search; direct opening was intermittent. It marks this work superseded by *Robust Composition*. **ROO translation:** pass narrowly scoped capabilities; ordinary Rust references alone do not establish security confinement.

### S25 — Rust ownership

Rust project documentation, “What Is Ownership?” [Official Rust Book](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html).
**Established:** ownership/moves and resource-lifetime basics. Current online documentation is mutable and does not pin a compiler. **ROO translation:** memory ownership is a mechanism for implementing a design, not the same concept as business ownership or stable identity.

### S26 — Futures

Rust standard library, `std::future::Future`. [Official API documentation](https://doc.rust-lang.org/std/future/trait.Future.html).
**Established:** poll-driven asynchronous computations and readiness. **ROO translation:** a suspended or dropped computation needs an application-level cancellation contract; polling semantics do not promise remote rollback.

### S27 — Async cancellation and shutdown

Tokio contributors, [`select!` cancellation-safety documentation](https://docs.rs/tokio/latest/tokio/macro.select.html) and [graceful shutdown tutorial](https://tokio.rs/tokio/topics/shutdown).
**Established:** cancellation safety varies by operation; requesting shutdown and waiting for completion are distinct. These are mutable project documents; no fixed runtime version is claimed. **ROO translation:** review suspension points and supervise cleanup/recovery instead of treating `Drop` as async compensation.

### S28 — Database transactions

PostgreSQL contributors, current tutorial, “Transactions.” [Official documentation](https://www.postgresql.org/docs/current/tutorial-transactions.html).
**Established:** grouping local changes with commit/rollback. The retrieved `current` URL resolved to PostgreSQL 18 documentation. **ROO translation:** transaction boundaries depend on the persistence mechanism, not aggregate allocation or a Rust mutable borrow. Specific isolation and retry protocols need additional implementation evidence.

## Proposed synthesis and evidence limits

**ROO proposal:** a relationship contract records memory owner/resource custodian, stable identity, mutation authority, access regime, validity horizon, execution domain, and failure boundary. The boundary walkthrough relates this contract to domain, transaction, and deployment decisions. These particular fields and their combination are an editorial method proposed here, not a demonstrated new theorem.

This is a selective foundation ledger of **28 source entries**, not a systematic review of all OO, ownership, architecture, or distributed-systems literature. Some entries group multiple URLs for one concept. URLs and bibliographic facts were checked at the level stated per entry; failures and indexed-only access are disclosed rather than counted as full-text reading.

The edition makes no empirical claim that ROO dominates other methods, is unprecedented, reduces defects by a measured amount, or guarantees production reliability. Such claims would require a search protocol, inclusion criteria, baseline methods, study data, and independent evaluation. Worked examples are proposed designs; executable laboratory results have their own validation ledger.
