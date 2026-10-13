# ROO literature and claim ledger

Selective literature ledger, updated on **2026-10-12** for the current eight-field contract. Entries S01–S28 retain their original access notes. Entries S29–S47 consolidate the primary sources examined in the dated academic investigation; each states the level of access supporting its claims. This update does not assert a fresh full-text reading of every source.

Entries S48–S50 support the proposed evaluation instruments and interpretation
rules, following the review of additional academic materials.
Entries S51–S57 add targeted checks of further prior-art suggestions, including
two June 2026 preprints. These checks extend the selective ledger; they do not
certify the supplied search synthesis as comprehensive or systematic.
Entries S58–S64 check empirical statistics and narrower comparisons raised
by subsequent reviews. Findings retain their study populations, source
locations, and access limits; none is a measurement of ROO's benefit.
Entries S65–S69 examine the later dialectical dossier and agent/aspect
comparison. The critical synthesis separates
verified antecedents, proposed adaptations, and unverified assertions.
S70 and the focused comparison deepen the
agent/aspect assessment framework and record the initial partial chapter 8 reading; S65 records the later complete chapter retrieval.
Entries S71–S76 examine adoption, review, filtered test generation, analysis
integration, understandability, and selective formal modeling. The
[adoption analysis](historical-paradigms-and-ai-revival.md) preserves their
distinct evidence scopes.
Entries S77–S79 support the [assisted design proposal](assisted-design-protocol.md)
with conceptual-design, architectural-decision drafting, and multi-agent failure
comparisons. They do not evaluate ROO or establish agent-role superiority.
Entries S80–S88 check the later claim of an empty upstream-design market. The
[focused comparison](upstream-design-comparison.md) separates research papers,
mutable product documentation, and language guarantees; none is a ROO benchmark.
Entries S89–S99 examine the expanded landscape dossier's academic leads,
formal distributed modeling, assertion semantics, and evaluation claims. The
[critical review](upstream-landscape-review.md) records corrections and proposed
validation work without accepting its exhaustive-search or novelty conclusions.
Entries S100–S109 check selected thesis leads and the CAP/PACELC foundations
raised by the later thesis synthesis and architecture handbook. The
material review
records duplicates, incomplete access, and unsupported extrapolations. These
checks do not validate every thesis listed in the supplied synthesis.
Entries S110–S123 follow up the remaining fourteen table rows. The
22-work audit
accounts for every row, including unresolved thesis identity and unavailable
full text. Papers used to investigate a thesis lead remain separately labeled;
selected passage reading is not a complete critical reading of a dissertation.

Development integration note (2026-10-13): the dated source-access notes below
are retained; this integration is not a fresh full-text audit of 123 sources.
Detailed AI-assisted working records and frozen experimental packages remain
privately preserved outside this documentation candidate.
References to those records below describe that prior investigation; primary
URLs, source locations, access limits, and unresolved claims are retained here.
This is not independent human validation.

**Established** labels an existing published concept, not universal agreement or empirical superiority. **ROO translation** labels an interpretation for Rust. **Proposed synthesis** labels this edition's relationship contract and workflow. Neither latter label is a claim of historical priority. No secondary pattern blog is used as authority for the conceptual foundations below.

**ROO relevance** in the additional entries is a language-independent comparison, not a claim that a source defines the ROO fields. Papers, books, technical reports, practitioner essays, and runtime documentation are identified separately; they are not interchangeable evidence of methodological efficacy. See [academic position and validation limits](../docs/claims-and-limits.md#academic-position) and the [research agenda](agenda-revised-2026-10-12.md).

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

Gary Bernhardt, **2012**, “Functional Core, Imperative Shell.” [Author's screencast page](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell), which states publication on 2012-07-12 (rechecked 2026-10-12).
**Established:** separation of decision-making data transformations from effects. **ROO translation:** return owned plans/results and let the shell enforce commit-time concurrency and failure handling.

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
**Established:** channels, routing, transformation, and endpoints. The overview's site footer states © 2003, 2023; this is not by itself a first-publication date for every pattern. **ROO translation:** owned event payloads still need schema, correlation, and operational contracts; messaging does not remove coupling.

### S18 — Distributed ordering

Leslie Lamport, **1978**, “Time, Clocks, and the Ordering of Events in a Distributed System.” [Author-hosted paper](https://lamport.azurewebsites.net/pubs/time-clocks.pdf).
**Established:** happened-before and logical-clock reasoning. **ROO translation:** distinguish causal and transport ordering from a universal real-time order. This source does not establish every modern broker's guarantees.

### S19 — Sagas

Hector Garcia-Molina and Kenneth Salem, **1987**, “Sagas.” [Original SIGMOD Record entry](https://sigmodrecord.org/1987/12/09/sagas/); [Princeton technical-report scan](https://www.cs.princeton.edu/techreports/1987/070.pdf).
**Access update, 2026-10-12:** the 20-page image-only scan was retrieved; PDF page 2 identifies the authors, abstract, and report date January 7, 1987, distinct from the December record date. The abstract, not the entire scanned paper, was visually inspected. **Established:** long-lived transactions decomposed into interleaved steps with compensations. **ROO translation:** persist remote-operation progress and compensation intents; model unresolved outcomes instead of equating timeout with failure.

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

Mark S. Miller and Jonathan S. Shapiro, **2003**, “Paradigm Regained: Abstraction Mechanisms for Access Control.” [Authors' article/version page](http://www.erights.org/talks/asian03/index.html).
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

## Responsibilities, relations, and architectural interaction

### S29 — Responsibility-Driven Design

Rebecca Wirfs-Brock and Brian Wilkerson, **1989**, “Object-Oriented Design: A Responsibility-Driven Approach.” OOPSLA '89 / *ACM SIGPLAN Notices* 24(10), 71–75. [DOI](https://doi.org/10.1145/74877.74885); [author's publication record](https://wirfs-brock.com/rebecca/about/cv/); [later author exposition](https://wirfs-brock.com/PDFs/Responsibility-Driven.pdf).
**Access:** original metadata and author exposition; the later exposition is not the original conference paper. **Established:** responsibilities and collaborations guide design before implementation structure. The later author exposition also develops client/server contracts and scenario-driven checks, refining general responsibilities into request details and pre/postconditions (sections 1–4; selectively rechecked 2026-10-13). **ROO relevance:** this ordering is prior art; the candidate distinction is a compact record of separate relationship obligations across lifecycle, trust, execution, and failure boundaries.

### S30 — CRC cards

Kent Beck and Ward Cunningham, **1989**, “A Laboratory for Teaching Object-Oriented Thinking.” OOPSLA '89 / *ACM SIGPLAN Notices* 24(10), 1–6. [DOI](https://doi.org/10.1145/74878.74879); [full author-hosted text](https://c2.com/doc/oopsla89/paper.html).
**Access:** full text. **Established:** class, responsibility, collaborator cards and scenario enactment as a teaching/design practice. **ROO relevance:** compact collaboration records and scenario-driven discovery precede ROO. The authors' teaching observations are not a controlled efficacy study of CRC or ROO.

### S31 — Relational analysis of object interactions

Daniel Jackson and Alan Fekete, **2001**, “Lightweight Analysis of Object Interactions.” TACS 2001, LNCS 2215, 492–513. [DOI](https://doi.org/10.1007/3-540-45500-0_25); [author-hosted paper](https://people.csail.mit.edu/dnj/publications/tacs-01.pdf).
**Access:** full text. **Established:** relational models of identity, sharing, collaboration, and global invariants, with tool-supported counterexample analysis. **ROO relevance:** an especially close antecedent to interaction as a unit of reasoning and the counterexample step. ROO's natural-language worksheet does not supply this formal semantics or analysis.

### S32 — Explicit architectural connectors

Robert Allen and David Garlan, **1997**, “A Formal Basis for Architectural Connection.” *ACM Transactions on Software Engineering and Methodology* 6(3), 213–249. [DOI](https://doi.org/10.1145/258077.258078); [authors' institutional abstract](https://www.cs.cmu.edu/afs/cs/project/able/www/paper_abstracts/wright-tosem97.html).
**Access:** institutional abstract and metadata; full text was also accessed by the concepts research lane. **Established:** connectors as explicit semantic entities with participant protocols and compatibility analysis. **ROO relevance:** making interactions explicit is not new; compare ROO's decision/review granularity with connector specification rather than claiming to originate relationship-centered architecture.

### S33 — Relations as semantic constructs

James Rumbaugh, **1987**, “Relations as Semantic Constructs in an Object-Oriented Language.” OOPSLA '87, 466–481. [DOI](https://doi.org/10.1145/38765.38850).
**Access:** bibliographic record; full text was not opened in the investigation. **Established at this access level:** an earlier published proposal explicitly taking relations as semantic constructs. **ROO relevance:** a necessary priority comparison; metadata alone does not establish how many ROO obligations the method covers.

## Formal contracts, state, and authorization

### S34 — Contracts for system design

Albert Benveniste, Benoît Caillaud, Dejan Nickovic, Roberto Passerone, Jean-Baptiste Raclet, Philipp Reinkemeier, Alberto Sangiovanni-Vincentelli, Werner Damm, Thomas A. Henzinger, and Kim G. Larsen, **2018**, “Contracts for System Design.” *Foundations and Trends in Electronic Design Automation* 12(2–3), 124–400. [DOI](https://doi.org/10.1561/1000000053); [institutional record](https://research-explorer.ista.ac.at/record/5677); [author version](https://hal.science/hal-01971429/).
**Access:** metadata and abstract; the formal-contracts lane additionally accessed an open version. No claim of a cover-to-cover reading of the monograph. **Established:** formal contract theories support composition, compatibility, abstraction, and refinement. **ROO relevance:** the worksheet can elicit obligations for later formalization; it has no such operators or proofs merely because it is called a contract.

### S35 — Typestate

Robert E. Strom and Shaula Yemini, **1986**, “Typestate: A Programming Language Concept for Enhancing Software Reliability.” *IEEE Transactions on Software Engineering* SE-12(1), 157–171. [DOI](https://doi.org/10.1109/TSE.1986.6312929); [university-hosted paper](https://www.cs.cmu.edu/~aldrich/papers/classic/tse12-typestate.pdf).
**Access:** full text in the ownership research lane. **Established:** allowed operations depend on an object's state. **ROO relevance:** informs lifecycle and access decisions; local typestate does not establish snapshot freshness, durable identity, or recovery of a remote effect.

### S36 — Relationship-based access control

Philip W. L. Fong, **2011**, “Relationship-Based Access Control: Protection Model and Policy Language.” CODASPY '11, 191–202. [DOI](https://doi.org/10.1145/1943513.1943539); [author-hosted paper](https://cspages.ucalgary.ca/~pwlfong/Pub/codaspy2011.pdf).
**Access:** full text in the authorization research lane. **Established:** an authorization model and policy language using relationships. **ROO relevance:** relationship-based permission is prior art, while ROO asks which policy and revocation rule govern an operation. A domain relation, known ID, or mutable borrow does not itself implement that policy.

### S37 — Zanzibar

Ruoming Pang et al., **2019**, “Zanzibar: Google's Consistent, Global Authorization System.” USENIX ATC '19, 33–46. [Official paper and proceedings record](https://www.usenix.org/conference/atc19/presentation/pang).
**Access:** full paper in the authorization research lane. **Established:** a production authorization design using relationships and explicit consistency mechanisms. **ROO relevance:** Authorization, Horizon, and Execution require a coordinated policy. A zookie constrains snapshot freshness; it is not a grant or an automatic atomic commit with an application's business effect. Reported Google operation does not validate ROO.

### S38 — Local and distributed interaction

Jim Waldo, Geoff Wyant, Ann Wollrath, and Sam Kendall, **1994**, “A Note on Distributed Computing.” Sun Microsystems Laboratories technical report SMLI TR-94-29, November. [Author's record](https://waldo.scholars.harvard.edu/publications/note-distributed-computing); [report](https://scholar.harvard.edu/files/waldo/files/waldo-94.pdf).
**Access:** abstract and report text retrieved across the investigation. **Established:** latency, concurrency, memory access, and partial failure distinguish distributed interaction from local calls. **ROO relevance:** a rationale for separate Execution and Failure decisions. This is a technical report, not a controlled evaluation of a design method.

### S39 — Alloy and bounded design analysis

Daniel Jackson, **2019**, “Alloy: A Language and Tool for Exploring Software Designs.” *Communications of the ACM* 62(9), 66–76. [DOI](https://doi.org/10.1145/3338843); [MIT manuscript](https://hdl.handle.net/1721.1/129357). For the earlier language account: Jackson, **2002**, “Alloy: A Lightweight Object Modelling Notation,” *TOSEM* 11(2), 256–290, [DOI](https://doi.org/10.1145/505145.505149).
**Access:** metadata and open manuscripts in the formal-contracts research lane. **Established:** relational specification and automated design exploration. The 2019 article is not the origin of Alloy. **ROO relevance:** selected obligations can become model properties; absence of a counterexample in a bounded check is not an unrestricted proof or validation of the worksheet.

## Concept design and adoption

### S40 — Concept design

Daniel Jackson, **2021**, *The Essence of Software: Why Concepts Matter for Great Design*. Princeton University Press. [JSTOR book record and DOI](https://doi.org/10.2307/j.ctv1nj340p).
**Access:** record, synopsis, contents, and partial material; not the complete book. **Established at this access level:** a concept-centered approach to software design. **ROO relevance:** conceptual units before implementation are prior art; detailed comparisons must use accessible primary descriptions such as S41 and S42, not infer the entire method from a synopsis.

### S41 — Industrial concept-centric experience

Peter Wilczynski, Taylor Gregoire-Wright, and Daniel Jackson, **2023**, “Concept-Centric Software Development: An Experience Report.” Onward! '23, 120–135. [DOI](https://doi.org/10.1145/3622758.3622894); [author-hosted paper](https://groups.csail.mit.edu/sdg/pubs/2023/concepts-onward-23.pdf).
**Access:** full text. **Established:** a reported Palantir adoption experience with explicit concepts and organizational challenges. **ROO relevance:** informs adoption questions and evidence collection. An industrial experience report is not a causal demonstration of productivity or defect reduction, and does not evaluate ROO.

### S42 — Concepts and explicit synchronizations

Eagon Meng and Daniel Jackson, **2025**, “What You See Is What It Does: A Structural Pattern for Legible Software.” Onward! '25, 178–193. [DOI](https://doi.org/10.1145/3759429.3762628); [authors' full text](https://arxiv.org/html/2508.14511).
**Access:** full author version, with conference metadata. **Established:** independent concepts composed through explicit synchronization rules, illustrated and evaluated on a RealWorld case. **ROO relevance:** a recent, close comparison for explicit interactions and composition. ROO proposes a decision/review procedure across realizations rather than this execution mechanism. The case study does not establish ROO's efficacy or the historical uniqueness of its eight questions.

**Targeted recheck, 2026-10-13:** sections 6.6 and 9 describe durable synchronization provenance for idempotent firing and recovery. The described implementation runs concept modules and the engine in one thread; separate/distributed execution is discussed as a possibility. These scoped mechanisms deserve comparison without equating them to the ROO review procedure or guarantees over independent external effects.

## Research and evaluation methods

### S43 — Architecture tradeoff evaluation

Rick Kazman, Mark Klein, Mario Barbacci, Tom Longstaff, Howard Lipson, and Jeromy Carriere, **1998**, *The Architecture Tradeoff Analysis Method*, CMU/SEI-98-TR-008. [SEI report](https://www.sei.cmu.edu/library/the-architecture-tradeoff-analysis-method/). Rick Kazman, Mark Klein, and Paul Clements, **2000**, *ATAM: Method for Architecture Evaluation*, CMU/SEI-2000-TR-004. [SEI report](https://insights.sei.cmu.edu/library/atam-method-for-architecture-evaluation/).
**Access:** official reports located in the evaluation research lane. **Established:** scenario-based evaluation of architectural risks and quality tradeoffs. **ROO relevance:** a comparison and source of baseline review practices; a relationship worksheet is not a replacement for full architectural evaluation.

### S44 — Design Science Research

Alan R. Hevner, Salvatore T. March, Jinsoo Park, and Sudha Ram, **2004**, “Design Science in Information Systems Research.” *MIS Quarterly* 28(1), 75–105. [Journal record](https://aisel.aisnet.org/misq/vol28/iss1/6/); [DOI](https://doi.org/10.2307/25148625).
**Access:** journal metadata and abstract confirmed; the evaluation lane additionally located the full text. **Established:** building and evaluating an artifact can produce research contributions. **ROO relevance:** a possible research framing for a method; classification as DSR does not establish novelty or utility.

### S45 — A DSR process

Ken Peffers, Tuure Tuunanen, Marcus A. Rothenberger, and Samir Chatterjee, **2007**, “A Design Science Research Methodology for Information Systems Research.” *Journal of Management Information Systems* 24(3), 45–77. [DOI](https://doi.org/10.2753/MIS0742-1222240302).
**Access:** publisher record; an open university version was located by the evaluation lane. **Established:** a process connecting problem, objectives, design, demonstration, evaluation, and communication. **ROO relevance:** executable examples are demonstration; benefit to engineers requires a separate evaluation.

### S46 — Software-engineering case studies

Per Runeson and Martin Höst, **2009** (online December 2008), “Guidelines for Conducting and Reporting Case Study Research in Software Engineering.” *Empirical Software Engineering* 14(2), 131–164. [DOI and open article](https://doi.org/10.1007/s10664-008-9102-8).
**Access:** full text. **Established:** case-study planning, collection, analysis, reporting, and evidence chains in a natural context. **ROO relevance:** guides future adoption studies; a laboratory comparison and a field case answer different questions.

### S47 — Structured literature review and mapping

Barbara Kitchenham and Stuart Charters, **2007**, *Guidelines for Performing Systematic Literature Reviews in Software Engineering*, v2.3, EBSE-2007-01. [Institution-hosted report](https://ebse.webspace.durham.ac.uk/wp-content/uploads/sites/49/2022/08/Systematic-reviews-5-8.pdf). Kai Petersen, Robert Feldt, Shahid Mujtaba, and Michael Mattsson, **2008**, “Systematic Mapping Studies in Software Engineering,” EASE, 68–77, [DOI](https://doi.org/10.14236/ewic/EASE2008.8). Kai Petersen, Sairam Vakkalanka, and Ludwik Kuzniarz, **2015**, “Guidelines for Conducting Systematic Mapping Studies in Software Engineering: An Update,” *Information and Software Technology* 64, 1–18, [DOI](https://doi.org/10.1016/j.infsof.2015.03.007).
**Access:** open report/paper for 2007/2008; publisher abstract and metadata for 2015. **Established:** reproducible search, selection, extraction, and classification procedures. **ROO relevance:** these procedures remain to be applied; this ledger and its exploratory dossier are not a completed systematic review.

### S48 — Subjective workload

NASA Ames Human Systems Integration Division, *NASA Task Load Index (TLX)*. [Official instrument description and publications](https://www.nasa.gov/human-systems-integration-division/nasa-task-load-index-tlx/).
**Access:** official description. **Established:** subjective workload ratings on six subscales: mental, physical, and temporal demand, performance, effort, and frustration; the described overall score uses weighting. **ROO relevance:** a possible secondary evaluation instrument. Freeze administration, language, and scoring; suitability for ROO tasks remains to be assessed. A workload rating is not an objective measure of design correctness.

### S49 — Equivalence testing

Daniël Lakens, **2017**, “Equivalence Tests: A Practical Primer for t Tests, Correlations, and Meta-Analyses.” *Social Psychological and Personality Science* 8(4), 355–362. [DOI](https://doi.org/10.1177/1948550617697177); [university-hosted published article](https://pure.tue.nl/ws/portalfiles/portal/80918653/lakeequi2017.pdf).
**Access:** full text. **Established:** non-significance alone does not support absence of a meaningful effect; equivalence testing requires justified bounds. **ROO relevance:** any simplification claim needs a prespecified equivalence or non-inferiority question and suitable analysis, rather than interpreting a nonsignificant difference as interchangeable methods.

### S50 — Power and inconclusive results

John M. Hoenig and Dennis M. Heisey, **2001**, “The Abuse of Power: The Pervasive Fallacy of Power Calculations for Data Analysis.” *The American Statistician* 55(1), 19–24. [DOI](https://doi.org/10.1198/000313001300339897); [university-hosted article](https://edwebcontent.ed.ac.uk/sites/default/files/atoms/files/the_abuse_of_power.pdf).
**Access:** full text retrieved; observed-power argument inspected. **Established:** calculating observed power from the observed effect cannot explain a nonsignificant result. **ROO relevance:** use prospective design planning and report effect estimates and uncertainty; do not certify a study's adequacy with retrospective observed power.

## Additional prior-art checks

### S51 — Comparing analysis and design methodologies

Robert G. Fichman and Chris F. Kemerer, **1992**, “Object-Oriented and Conventional Analysis and Design Methodologies.” *Computer* 25(10), 22–39. [DOI](https://doi.org/10.1109/2.161278); [author-hosted article](https://sites.pitt.edu/~ckemerer/CK%20research%20papers/OO%26ConventionalAnalysis_FichmanKemerer92.pdf).
**Access:** published PDF retrieved; introduction, selection criteria, and comparison material inspected. **Established:** comparison of three OOA and three OOD methodologies with conventional approaches, including responsibility-driven design. The supplied summary's count of nine OO methodologies is incorrect. **ROO relevance:** a precedent for comparing methods by their concepts, procedures, and adoption implications; a 1992 comparison cannot establish the absence of a later method or validate ROO's integration.

### S52 — Semantic relationship classification

Veda C. Storey, **1993**, “Understanding Semantic Relationships.” *The VLDB Journal* 2, 455–488. [DOI](https://doi.org/10.1007/BF01263048); [journal-hosted paper](https://www.vldb.org/journal/VLDBJ2/P455.pdf). Storey, **2005**, “Comparing Relationships in Conceptual Modeling: Mapping to Semantic Classifications.” *IEEE Transactions on Knowledge and Data Engineering* 17(11), 1478–1489. [DOI](https://doi.org/10.1109/TKDE.2005.175).
**Access:** 1993 full text retrieved, with introduction and relationship-classification material examined; 2005 publisher-deposited metadata checked through Crossref, without full-text assessment. These are different publications, not interchangeable dates for one paper. **Established:** the 1993 work examines semantic relationships beyond common data abstractions and their implications for database design. **ROO relevance:** relationship semantics and their classification precede ROO. The 2005 work is a further comparison lead; metadata alone cannot classify its coverage of ROO obligations.

### S53 — Data, Context, and Interaction

Trygve Reenskaug and James O. Coplien, **2009**, “The DCI Architecture: A New Vision of Object-Oriented Programming,” March 20. [Authors' Artima article](https://www.artima.com/articles/the-dci-architecture-a-new-vision-of-object-oriented-programming).
**Access:** article text, role/context discussion, and money-transfer example inspected. **Established:** a practitioner architecture separating domain data from use-case roles and interactions. The example explicitly places the balance check inside a transaction to avoid an intervening withdrawal. **ROO relevance:** scenario-based collaboration and transaction-aware interaction are prior art; the claim that DCI leaves transactions completely unmodeled is untenable. This example does not establish a distributed recovery protocol or a complete eight-decision review procedure. The article acknowledges limited research evidence for its cognitive claims.

### S54 — First-class relationships in a language

Gavin Bierman and Alisdair Wren, **2005**, “First-Class Relationships in an Object-Oriented Language.” ECOOP 2005, LNCS 3586, 262–286. [DOI](https://doi.org/10.1007/11531142_12); [Cambridge extended report, UCAM-CL-TR-642](https://www.cl.cam.ac.uk/techreports/UCAM-CL-TR-642.html); [report text](https://www.cl.cam.ac.uk/techreports/UCAM-CL-TR-642.pdf).
**Access:** institutional abstract and extended-report introduction; not a complete proof review. **Established:** language constructs for relationship instances, attributes, and inheritance, with a formal type system, operational semantics, and safety properties. **ROO relevance:** explicit relationships have both modeling and programming-language antecedents. ROO proposes review obligations without providing this language's formal semantics. Commercial failure, its causes, or historical absence of other obligations cannot be inferred from this paper's chosen scope.

### S55 — Separating individuals from modules

Daniel Jackson, **2026**, “Beyond Objects,” arXiv:2606.27258v1, June 25. [Versioned author text](https://arxiv.org/html/2606.27258v1); [arXiv record](https://arxiv.org/abs/2606.27258).
**Access:** author version, particularly section 12. **Status:** preprint; the manuscript names a forthcoming Springer chapter, whose final publication was not verified here. **Proposal:** separate domain individuals from modules that partition actions and relations; compose concepts by action synchronization. The text retains persistent identity and permits separately deployed concepts. **ROO relevance:** a close conceptual comparison, not a baseline restricted to one in-memory heap. ROO's distinctness must be assessed against its design ideas and assumptions, not merely a particular runtime implementation.

### S56 — Explicit meaning across design and execution

Eagon Meng, Abutalib Namazov, Carmel Schare, Alcino Cunha, and Daniel Jackson, **2026**, “Making Software Meaningful,” arXiv:2606.11051v1, June 9. [Versioned author text](https://arxiv.org/html/2606.11051v1); [arXiv record](https://arxiv.org/abs/2606.11051).
**Access:** author version, especially sections 5.2 and 5.3. **Status:** preprint; no final venue or peer-review outcome is asserted. **Proposal:** a shared vocabulary of individuals, actions, and facts across design, code, and accountability. Section 5.2 discusses UUIDs, database persistence, action histories, and crash recovery; 5.3 discusses conditions permitting agent actions. **ROO relevance:** operational concerns cannot be declared absent from concept design as a whole. These descriptions do not establish every revocation or remote-effect guarantee, and do not evaluate ROO.

### S57 — Failure-handling evidence

Ding Yuan, Yu Luo, Xin Zhuang, Guilherme Renna Rodrigues, Xu Zhao, Yongle Zhang, Pranay U. Jain, and Michael Stumm, **2014**, “Simple Testing Can Prevent Most Critical Failures: An Analysis of Production Failures in Distributed Data-Intensive Systems.” OSDI '14, 249–265. [Official proceedings and paper](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/yuan); [authors' 2015 summary](https://www.usenix.org/publications/login/feb15/yuan).
**Access:** official abstract and authors' summary; no independent reanalysis of the dataset. **Reported finding:** incorrect handling of non-fatal errors accounted for 92% of catastrophic failures in the study's selected sample of 198 user-reported failures. This is not a population estimate for all production outages. **ROO relevance:** motivation for investigating failure-handling obligations and selecting cases; neither an eight-field completeness result nor evidence of ROO's efficacy.

## Empirical findings and additional method comparisons

### S58 — Concurrency bug characteristics

Shan Lu, Soyeon Park, Eunsoo Seo, and Yuanyuan Zhou, **2008**, “Learning from Mistakes: A Comprehensive Study on Real World Concurrency Bug Characteristics.” ASPLOS XIII, 329–339. [DOI](https://doi.org/10.1145/1346281.1346323); [university-hosted paper](https://www.cs.columbia.edu/~junfeng/08fa-e6998/sched/readings/concurrency-bugs.pdf).
**Access:** full text retrieved; Tables 1 and 4 inspected. **Reported findings:** 105 sampled bugs, including 74 non-deadlock bugs; approximately 97% of the latter involve atomicity or ordering violations. Table 4 counts 51 atomicity and 24 ordering cases, with three overlapping cases. **ROO relevance:** independent concurrency scenarios, not an exclusive 65%/35% partition or evidence of method effectiveness. The separate two-thread manifestation finding uses a different denominator.

### S59 — Distributed concurrency bugs

Tanakorn Leesatapornwongsa, Jeffrey F. Lukman, Shan Lu, and Haryadi S. Gunawi, **2016**, “TaxDC: A Taxonomy of Non-Deterministic Concurrency Bugs in Datacenter Distributed Systems.” ASPLOS '16, 517–530. [DOI](https://doi.org/10.1145/2872362.2872374); [author-hosted paper](https://ucare.cs.uchicago.edu/pdf/asplos16-TaxDC.pdf).
**Access update, 2026-10-12:** author-hosted full text retrieved; sections 1.2 and 3.3 and Finding #3 inspected. **Reported finding:** over 60% of 104 bugs from four systems involve a single untimely message delivery violating ordering or atomicity relative to other messages or computation. Finding #3 reports one to three messages, nodes, and protocols for most cases (>90% in Figures 3h–j); section 3.3 describes the node scope as mostly two or three. The supplied two-to-four-node claim is not supported by those passages. **ROO relevance:** distributed counterexamples; these sample findings establish neither checklist completeness nor a review-time bound.

### S60 — Microservice fault cases

Xiang Zhou, Xin Peng, Tao Xie, Jun Sun, Chao Ji, Wenhai Li, and Dan Ding, **2021** (online 2018), “Fault Analysis and Debugging of Microservice Systems: Industrial Survey, Benchmark System, and Empirical Study.” *IEEE Transactions on Software Engineering* 47(2), 243–260. [DOI](https://doi.org/10.1109/TSE.2018.2887384); [NSF-hosted manuscript](https://par.nsf.gov/servlets/purl/10357355); [author institution's publication record](https://smusg.elsevierpure.com/en/publications/fault-analysis-and-debugging-of-microservice-systems-industrial-s/).
**Access:** manuscript retrieved; Table 3 inspected; final issue metadata checked. **Observed table counts:** recounting the 22 fault identifiers gives 10 interaction, seven internal, and five environment cases. These selected industrial cases were replicated in TrainTicket; they are not a random sample of all production microservice faults. **ROO relevance:** candidate evaluation cases, not support for the supplied 59%/18% breakdown or a universal boundary-failure rate.

### S61 — Architecture anti-pattern evidence

Ran Mo, Yuanfang Cai, Rick Kazman, Lu Xiao, and Qiong Feng, **2021** (online 2019), “Architecture Anti-Patterns: Automatically Detectable Violations of Design Principles.” *IEEE Transactions on Software Engineering* 47(5), 1008–1028. [DOI](https://doi.org/10.1109/TSE.2019.2910856); [author institution's abstract and metadata](https://researchwith.stevens.edu/en/publications/architecture-anti-patterns-automatically-detectable-violations-of/).
**Access:** institutional abstract and metadata, plus indexed author-paper excerpts; no full statistical reanalysis. **Reported finding:** associations between detected anti-patterns and file bug/change proneness across 19 projects, with Crossing and Unstable Interface strongest among the studied patterns. **ROO relevance:** motivation for examining architectural dependencies. A generic two-to-threefold multiplier remains unverified without its metric and comparison; association does not demonstrate that ROO prevents these defects.

### S62 — Aggregate consistency and identity

Vaughn Vernon, **2011**, *Effective Aggregate Design*: [Part I: Modeling a Single Aggregate](https://www.dddcommunity.org/wp-content/uploads/files/pdf_articles/Vernon_2011_1.pdf) and [Part II: Making Aggregates Work Together](https://www.dddcommunity.org/wp-content/uploads/files/pdf_articles/Vernon_2011_2.pdf).
**Access:** both practitioner articles retrieved; Part I's consistency-boundary rule and Part II's identity-reference and eventual-consistency rules inspected. **Established guidance:** model true invariants within consistency boundaries; reference other aggregates by identity; consider eventual consistency outside the boundary. **ROO relevance:** business consistency, identity references, and cross-aggregate coordination are prior art. DDD cannot fairly be described as necessarily conflating identity, storage, and coordination or ignoring distributed interaction. This guidance does not evaluate ROO or supply every authorization/recovery mechanism.

### S63 — Scenario-based inspection

Adam A. Porter, Lawrence G. Votta, Jr., and Victor R. Basili, **1995**, “Comparing Detection Methods for Software Requirements Inspections: A Replicated Experiment.” *IEEE Transactions on Software Engineering* 21(6), 563–575. [DOI](https://doi.org/10.1109/32.391380); [authors' paper](https://www.cs.umd.edu/users/basili/publications/technical/T101.pdf).
**Access:** full text retrieved; experimental design, section III-C.2, and conclusion inspected. **Reported finding:** roughly 35% better fault detection with scenarios than ad hoc/checklist methods in this experiment involving 48 graduate students and two requirements specifications. Scenario content was a principal contributor to performance. **ROO relevance:** compare content and procedure separately. This result neither quantifies a ROO gain nor establishes that checklists are generally ineffective; transfer to architectural review requires evaluation.

### S64 — Architectural fault modeling

Peter H. Feiler, John J. Hudak, Julien Delange, and David P. Gluch, **2016**, *Architecture Fault Modeling and Analysis with the Error Model Annex, Version 2*. CMU/SEI-2016-TR-009. [DOI](https://doi.org/10.1184/R1/6572018.v1); [official SEI report description](https://www.sei.cmu.edu/library/architecture-fault-modeling-and-analysis-with-the-error-model-annex-version-2/).
**Access:** official abstract and metadata, not a full annex/standard assessment. **Established:** EMV2 augments AADL models with faults, error propagation, detection/management, and recovery/repair behavior states. **ROO relevance:** a counterexample to the blanket claim that architecture description languages omit failure modeling. Coverage of each ROO obligation still requires source-specific analysis; a worksheet inherits none of the modeling language's analysis capabilities automatically.

## Agent concerns, transaction scope, and adoption comparisons

### S65 — Agents and separation of concerns

Alessandro F. Garcia, Carlos J. P. de Lucena, and Donald D. Cowan, **2004**, “Agents in Object-Oriented Software Engineering.” *Software: Practice and Experience* 34(5), 489–521. [DOI](https://doi.org/10.1002/spe.578). Alessandro Fabricio Garcia, **2004**, *Objetos e Agentes: Uma Abordagem Orientada a Aspectos*, doctoral thesis, PUC-Rio, advised by Carlos José Pereira de Lucena. [Institutional front matter](https://www.maxwell.vrac.puc-rio.br/5181/5181_1.PDF); [chapter 6](https://www.maxwell.vrac.puc-rio.br/5181/5181_7.PDF); [chapter 7](https://www.maxwell.vrac.puc-rio.br/5181/5181_8.PDF); [chapter 8](https://www.maxwell.vrac.puc-rio.br/5181/5181_9.PDF).
**Access update, 2026-10-12:** supplied article manuscript, thesis front matter, selected chapters 6–7, and the complete 24-page institutional chapter 8 (printed pp. 231–254) retrieved. Chapter-8 SHA-256: `6a185bf5c450223f2e5c8ad35b4cb25c256e4e174ccca9decd842170cc756625`. The front-matter PDF is not the complete thesis. **Reported work:** all four subjects participated in both versions; OA was developed first, and prior allegiance was balanced two/two without making this a controlled experiment. One Table 7 relates predictions to seven author-selected maintenance scenarios, using changed LOC as an effort proxy. Internal cohesion/complexity discrepancies must remain explicit. **ROO relevance:** concern separation, structural metrics, and predictive usefulness claims precede ROO. See the focused audit, S70 for joint metric attribution, and the adaptation proposal; this single-system evidence does not validate ROO or establish cross-method superiority.

### S66 — Distributed transaction guarantees

James C. Corbett et al., **2012**, “Spanner: Google's Globally-Distributed Database.” OSDI '12. [Official proceedings and paper](https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett). PingCAP, *TiDB Transaction Isolation Levels*, v8.5 documentation. [Versioned vendor documentation](https://docs.pingcap.com/tidb/v8.5/transaction-isolation-levels/).
**Access:** Spanner proceedings abstract; TiDB isolation documentation checked on 2026-10-11. **Established:** Spanner supports externally consistent distributed transactions; the examined TiDB documentation describes snapshot isolation, not a blanket strict-serializability guarantee. **ROO relevance:** distribution does not preclude atomic transactions, and product categories do not determine isolation. State the actual participating resources and guarantees; a database transaction does not automatically include an independent HTTP provider. Neither Sagas nor a particular database is universally required.

### S67 — Tracing and stream backpressure

W3C Distributed Tracing Working Group, **2021**, *Trace Context*, Recommendation, November 23. [Versioned specification](https://www.w3.org/TR/2021/REC-trace-context-1-20211123/). Reactive Streams initiative, **2022**, *Reactive Streams for the JVM*, version 1.0.4. [Official overview](https://www.reactive-streams.org/); [versioned specification](https://github.com/reactive-streams/reactive-streams-jvm/blob/v1.0.4/README.md#specification).
**Access:** Trace Context overview/security/privacy sections and Reactive Streams scope/version notes. **Established:** interoperable trace-context propagation and asynchronous stream protocols with non-blocking backpressure, respectively. **ROO relevance:** precedents for scenario-specific operational requirements; neither establishes an additional canonical ROO field, a universal production checklist, or FinOps/SLO coverage. Trace identifiers are not authorization credentials.

### S68 — Industrial code review practice

Caitlin Sadowski, Emma Söderberg, Luke Church, Michal Sipko, and Alberto Bacchelli, **2018**, “Modern Code Review: A Case Study at Google.” ICSE-SEIP. [Authors' publication page](https://research.google/pubs/modern-code-review-a-case-study-at-google/); [paper](https://storage.googleapis.com/gweb-research2023-stg-media/pubtools/4476.pdf).
**Access:** paper retrieved; change-size results, section 5.1 approval flow, and static-analysis discussion inspected. **Reported finding:** the median change modifies 24 lines in the studied Google logs, not fewer than 24. The exploratory study combines interviews, a survey, and review logs; LGTM marks approval after comments are addressed. **ROO relevance:** measure review burden and fit with existing practice. Neither the approval label nor this study establishes checklist-induced rubber-stamping, a worksheet-size threshold, or that ROO cannot work without a linter.

### S69 — Industry needs from architectural languages

Ivano Malavolta, Patricia Lago, Henry Muccini, Patrizio Pelliccione, and Antony Tang, **2013**, “What Industry Needs from Architectural Languages: A Survey.” *IEEE Transactions on Software Engineering* 39(6), 869–891. [DOI](https://doi.org/10.1109/TSE.2012.74); [institutional abstract](https://iris.gssi.it/handle/20.500.12571/17799); [author-uploaded text](https://www.researchgate.net/publication/233953518_What_Industry_Needs_from_Architectural_Languages_A_Survey).
**Access:** abstract and selected author-uploaded full-text passages, including discussion of formality and communication; no dataset reanalysis. **Reported finding:** 48 practitioners from 40 companies in 15 countries reported needs including better analysis, greater formality, and usability. Reported use categories include 17% ADL only, 35% ADL plus UML, and 42% UML/profile only; these sample categories are not a rejection rate (targeted recheck, 2026-10-13). **ROO relevance:** assess these tradeoffs together. This does not substantiate the dossier's universal rejection rate or causal explanation that mathematical formality caused commercial failure.

### S70 — Concern-oriented assessment framework

Cláudio Sant'Anna, Alessandro Garcia, Christina Chavez, Carlos Lucena, and Arndt von Staa, **2003**, “On the Reuse and Maintenance of Aspect-Oriented Software: An Assessment Framework.” SBES 2003, 15–30. [Publisher paper](https://sol.sbc.org.br/index.php/sbes/article/download/23850/23678).
**Access:** publisher PDF retrieved; section 3.1 checked against thesis chapter 6, section 6.4.1, pp. 197–200. **Established:** joint CDC/CDO/CDLOC definitions, building on earlier metric work. CDO's primary-unit wording differs between paper and thesis. CDLOC counts concern transitions after shading, not concern-line totals; thesis merging rules require judgment. **ROO relevance:** precise, versioned counting rules and new-domain validation are prerequisites for adaptation. Definition audit; proposed protocol.

## Adoption and assistance evidence

### S71 — Architecture decision records in open source projects

Georg Buchgeher, Stefan Schöberl, Verena Geist, Bernhard Dorninger, Philipp Haindl, and Rainer Weinreich, **2023**, “Using Architecture Decision Records in Open Source Projects—An MSR Study on GitHub.” *IEEE Access* 11, 63725–63740. [DOI](https://doi.org/10.1109/ACCESS.2023.3287654); [institutional PDF](https://phaidra.ustp.at/api/object/o%3A5493/download).
**Access:** full PDF retrieved; abstract, RQ2.1/RQ2.3 results, discussion, and validity threats inspected. **Reported finding:** about half the repositories with ADRs contain one to five records; the authors interpret this cautiously as possible experimentation without definitive adoption. Counts and unchanged records do not establish team abandonment within weeks. **ROO relevance:** define eligible changes, follow-up, continued activity, and reasons for discontinuation before measuring adoption.

### S72 — Review participation and software quality

Shane McIntosh, Yasutaka Kamei, Bram Adams, and Ahmed E. Hassan, **2016** (online 2015), “An Empirical Study of the Impact of Modern Code Review Practices on Software Quality.” *Empirical Software Engineering* 21, 2146–2189. [Publisher](https://doi.org/10.1007/s10664-015-9381-9); [author preprint](https://sail.cs.queensu.ca/data/pdfs/EMSE_AnEmpiricalStudyOfTheImpactOfModernCodeReviewPracticesOnSoftwareQuality.pdf).
**Access:** author preprint retrieved; abstract, introduction, and quality discussion inspected against publisher metadata. **Reported finding:** review coverage, participation, and expertise are associated with post-release defects in Qt, VTK, and ITK. **ROO relevance:** substantive review and independent outcomes matter. This observational study does not test mandatory eight-field worksheets or show that checklists cause superficial approval.

### S73 — Filtered test generation with LLMs

Nadia Alshahwan et al., **2024**, “Automated Unit Test Improvement using Large Language Models at Meta.” [Author preprint](https://arxiv.org/abs/2402.09171); [version 1 full text](https://arxiv.org/html/2402.09171v1).
**Access:** version 1 sections 1–2 inspected, including the test-oracle discussion. **Reported finding:** TestGen-LLM filters improvements to existing tests for buildability, repeated passing, and coverage gain; 73% acceptance concerns proposed improvements in its deployment. Initially failing tests are discarded because their assertions may be wrong. **ROO relevance:** filtering is an assistance precedent, not evidence of exhaustive adversarial generation, correct policy, or ROO adoption benefit.

### S74 — Program analysis integrated into review

Caitlin Sadowski, Jeffrey van Gogh, Ciera Jaspan, Emma Söderberg, and Collin Winter, **2015**, “Tricorder: Building a Program Analysis Ecosystem.” ICSE. [Authors' publication page](https://research.google/pubs/tricorder-building-a-program-analysis-ecosystem/).
**Access:** official publication metadata and abstract; integration and feedback also described in S68. **Established:** a program-analysis platform designed for integration into developers' workflows, evaluated at Google. **ROO relevance:** study actionable checks and feedback together. This 2015 description is not evidence that LLMs eliminate false alarms or that CI prevents semantic drift.

### S75 — Understandability as an evaluated design objective

Diego Ongaro and John Ousterhout, **2014**, “In Search of an Understandable Consensus Algorithm.” USENIX ATC, 305–319. [Official proceedings and abstract](https://www.usenix.org/conference/atc14/technical-sessions/presentation/ongaro).
**Access:** official abstract and bibliographic record. **Reported finding:** Raft's decomposed consensus structure was evaluated for student learnability relative to Paxos. **ROO relevance:** comprehension is a measurable outcome. This comparison does not establish the extinction of Paxos, industrial adoption causality, or the superiority of a proposed ROO presentation.

### S76 — Selective formal modeling in industry

Chris Newcombe, Tim Rath, Fan Zhang, Bogdan Munteanu, Marc Brooker, and Michael Deardeuff, **2015**, “How Amazon Web Services Uses Formal Methods.” *Communications of the ACM* 58(4), 66–73. [DOI](https://doi.org/10.1145/2699417); [authors' publication page](https://www.amazon.science/publications/how-amazon-web-services-uses-formal-methods).
**Access:** official publication page and indexed primary-paper opening; direct PDF fetch failed. **Reported experience:** AWS engineers used formal specification and model checking for critical distributed designs from 2011. **ROO relevance:** selective modeling can complement review and testing. This experience neither validates ROO nor supports a universal history of formal-method failure followed by rescue through LLMs.

## Conceptual design and staged assistance

### S77 — Essential and accidental difficulties

Frederick P. Brooks Jr., **1986**, “No Silver Bullet: Essence and Accidents of Software Engineering.” UNC technical report TR86-020; journal version in *Computer* 20(4), **1987**, 10–19. [Institutional report](https://www.cs.unc.edu/techreports/86-020.pdf); [journal DOI](https://doi.org/10.1109/MC.1987.1663532).
**Access:** institutional PDF, cover, selected sections 2 and 5 passages, including requirements and incremental development; journal metadata checked with Crossref, but journal-page access failed. **Established argument:** conceptual specification/design/testing and representational difficulties differ, while requirements and design need iteration. **ROO relevance:** motivates exploring obligations before implementation. This historical essay supplies no LLM benchmark or evidence that a completed natural-language contract makes implementation trivial or verified.

### S78 — LLMs and architectural decision drafting

Rudra Dhar, Karthik Vaidhyanathan, and Vasudeva Varma, **2024**, “Can LLMs Generate Architectural Design Decisions? — An Exploratory Empirical Study.” [Author preprint](https://arxiv.org/abs/2403.01709); [version 1 full text](https://arxiv.org/html/2403.01709v1).
**Access:** version 1 data collection, discussion, and validity threats inspected. **Reported investigation:** decision generation from ADR context using 95 ADRs from five repositories, text-generation metrics, and manual observations. The authors describe incomplete decisions and a need for human involvement; fine-tuning reused validation/test data because of limited data. **ROO relevance:** upstream decision assistance has prior art, but plausibility/similarity and this exploratory sample do not establish architectural correctness, field adoption, or implementation fidelity.

### S79 — Multi-agent system failures

Mert Cemri et al., **2025**, “Why Do Multi-Agent LLM Systems Fail?” *Advances in Neural Information Processing Systems* 38, Datasets and Benchmarks Track. [Official proceedings abstract](https://proceedings.neurips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html); [author preprint](https://arxiv.org/abs/2503.13657).
**Access:** official proceedings abstract; full paper not audited. **Reported investigation:** MAST categorizes system-design, inter-agent alignment, and task-verification failures in studied multi-agent systems. **ROO relevance:** specialize and evaluate coordination and verification, rather than assuming roles yield independent judgment or exhaustive coverage. These benchmark findings neither prove that multi-agent assistance always loses nor supply a gain, accuracy, or cost estimate for ROO. Proceedings and initial preprint descriptions have different sample scopes; their counts are not combined here.

## AI-assisted design and current tooling

### S80 — Specification-driven design and property testing

Kiro documentation, checked **2026-10-12**. [Specs](https://kiro.dev/docs/specs/); [correctness with property-based tests](https://kiro.dev/docs/specs/correctness/).
**Access:** core workflow, design phase, and property-testing limitations inspected; correctness page rechecked 2026-10-12. **Documented workflow:** requirements, architectural design, error handling, and tasks precede implementation; requirements-derived properties, extracted during the design phase, guide generated tests and shrinking. The capability table lists property testing for IDE only; tests are optional by default. **ROO relevance:** design plus attempts to expose violations already exist in a product workflow. These mutable vendor pages are not independent efficacy evidence, formal verification, or a demonstrated ROO equivalent; no product run was performed here.

### S81 — Interaction contracts in specification-driven development

GitHub Spec Kit maintainers, current guide, checked **2026-10-12**, “Contract-Driven Development.” [Official repository guide](https://github.com/github/spec-kit/blob/main/docs/guides/contract-driven-development.md).
**Access:** contract contents, ownership, workflow, and examples inspected. **Documented workflow:** agree on observable interaction obligations before dependent implementation, including effects, failures, idempotency, ordering, retries/timeouts, and verification. Boundaries need not cross processes or repositories. **ROO relevance:** a close procedural comparison. The guide supplies neither automatic runtime conformance nor an assessment of ROO's incremental value. Mutable documentation was read; the workflow was not executed.

### S82 — Structured architectural handoffs between agents

Sirui Hong et al., **ICLR 2024**, “MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework.” [Official proceedings record](https://proceedings.iclr.cc/paper_files/paper/2024/hash/6507b115562bb0a305f1958ccc87355a-Abstract-Conference.html); [author preprint, version 7](https://arxiv.org/html/2308.00352v7).
**Access:** proceedings metadata and preprint §§3.1–3.3 inspected; version 7 is a later revision, not assumed identical to the conference text. **Established antecedent:** structured requirements and architectural/interface artifacts pass between specialized roles before implementation; executable feedback follows. **ROO relevance:** neither upstream agent roles nor structured handoffs originate with ROO. Reported benchmark gains were not independently reproduced or transferred to relationship-design outcomes.

### S83 — Multi-agent architecture design and evaluation

Ruiyin Li et al., **2025**, “MAAD: Automate Software Architecture Design through Knowledge-Driven Multi-Agent Collaboration.” [Author preprint](https://arxiv.org/abs/2507.21382); [version 1 full text](https://arxiv.org/html/2507.21382v1).
**Access:** selected §§3–7 and version-1 metadata inspected; selected historical repository artifacts/source paths also checked. **Reported approach:** Analyst, Modeler, Designer, and Evaluator agents produce architectural views, connector/behavioral contracts, alternatives, and mismatch reports. Case-based evaluation includes architect interviews and model-generated assessments, with trust, granularity, and subjective-evaluation limits. **ROO relevance:** a direct upstream architectural-assistance antecedent. No independent correctness guarantee, ROO benefit, or general multi-agent superiority follows.

The [focused MAAD review](maad-critical-review.md) corrects the percentage
interpretation and records conflicts in reviewer-selected repository snapshots.
Those snapshots are not author-pinned v1 execution receipts. Documented feedback,
inspected code paths, generated scaffolding, and executed verification remain
distinct evidence levels. The later repository README must not silently replace
the 2025 study's inputs or outcomes.

### S84 — Formal specifications between source inputs and tests

Tasmim Rashid and Muhammad Zubair Malik, **2026**, “LM2Alloy: Investigating LLM-Generated Formal Specifications for Automated Test Derivation in Production Software.” [Author preprint](https://arxiv.org/abs/2607.18555); [version 1 full text, headed LLM2Alloy](https://arxiv.org/html/2607.18555v1).
**Access:** metadata and selected §§III–V inspected. **Reported investigation:** documentation/code-derived Alloy specifications guide pytest generation for two Python libraries. The described pipeline records pytest execution, without an Alloy Analyzer verification stage. The reported Flipper defect had not been submitted for maintainer confirmation. **ROO relevance:** keep intended constraints distinct from recovered code and evaluate the intermediate step. This exploratory preprint supplies no verified translation, general adoption result, or ROO validation.

### S85 — Architectural planning in coding assistants

Cursor and Anthropic documentation, checked **2026-10-12**. [Cursor Plan Mode](https://cursor.com/docs/agent/plan-mode); [Claude Code best practices](https://code.claude.com/docs/en/best-practices).
**Access:** Cursor's workflow/use cases and Claude's exploration/planning/verification sections inspected. **Documented capabilities:** architectural decisions are an explicit Cursor use case; Claude's guidance separates exploration from implementation and requests executable checks. **ROO relevance:** coding-assistant planning cannot categorically be reduced to syntax or file lists. Mutable vendor documentation does not measure obligation coverage or architectural reasoning reliability; no assistant evaluation was run.

### S86 — Planning offered by a review-tool vendor

CodeRabbit, current product page, checked **2026-10-12**. [CodeRabbit Plan](https://www.coderabbit.ai/plan).
**Access:** workflow and FAQ inspected. **Advertised workflow:** codebase-informed, editable plans reviewed before handoff to a coding agent. **ROO relevance:** the vendor's offerings cannot be classified as exclusively downstream. A product description is not independent evidence of design quality, successful architectural repair, or ROO equivalence; this review did not execute the service.

### S87 — Technical content in a requirements template

ChatPRD, current “PRD Template,” checked **2026-10-12**. [Vendor template](https://www.chatprd.ai/templates/prd-product-requirement-document-template).
**Access:** technical specifications and Technical Requirements inspected. **Documented prompts:** system architecture, component interactions, security, performance, and integrations. **ROO relevance:** a product-requirements category does not establish inability to discuss technical design. This template is not a test of generated answers or evidence of correct concurrency, partial-failure, or idempotency analysis.

### S88 — Rust concurrency guarantees beyond a heap-only description

Rust project, current *The Rust Programming Language*, checked **2026-10-12**, “Extensible Concurrency with Send and Sync.” [Official chapter](https://doc.rust-lang.org/book/ch16-04-extensible-concurrency-sync-and-send.html).
**Access:** chapter inspected. **Established mechanisms:** `Send` constrains value transfer across threads; `Sync` constrains sharing references between threads. Manual implementations require unsafe code and upheld safety conditions. **ROO relevance:** these guarantees exceed a heap-only characterization, while not establishing business invariants, remote atomicity, or compensation policy. As with S23, language/library assumptions and application properties must remain separate.

## Expanded upstream landscape and evaluation

### S89 — A review of architecture and LLM research

Larissa Schmid et al., **2025**, “Software Architecture Meets LLMs: A Systematic Literature Review.” [Author preprint](https://arxiv.org/abs/2505.16697); [version 1 full text](https://arxiv.org/html/2505.16697v1).
**Access:** selected §§2–3.1 inspected. **Reported review:** 18 included articles, with classification/detection, extraction/generation, assistance, and reference-architecture categories. The reported 71% concerns automated LLM use, not retrospective recovery. **ROO relevance:** an architecture-research map and source-search lead, including prospective design. Its selection and date cannot establish market completeness or ROO novelty.

### S90 — Guarded evaluation in Architecture-0 design

Zhongkai Wang and Yan Liu, **2026**, “Grounding SWE-Agent Decisions in Architecture-0 Design: Navigating Unknown Unknowns through Physical Mapping.” [Author preprint](https://arxiv.org/abs/2609.17221); [version 1 full text](https://arxiv.org/html/2609.17221v1).
**Access:** metadata and selected §§6–7 inspected. The record identifies a manuscript under review, not an accepted TOSEM paper. **Reported investigation:** PMG separates design generation from externally guarded physical/validation checks, while semantic reinterpretation and auditor overreach remain. Static resource ledgers, limited archetypes/public tasks, and possible data leakage constrain generalization. **ROO relevance:** compare verification authority and semantic/model mapping; no ROO benefit or universal agent-failure result follows.

### S91 — Prompt-dependent architectural decisions

Phongsakon Mark Konrad, Tim Lukas Adam, Riccardo Terrenzi, and Serkan Ayvaz, **2026**, “Architecture Without Architects: How AI Coding Agents Shape Software Architecture.” [Author preprint](https://arxiv.org/abs/2604.04990).
**Access:** metadata and abstract only. **Reported argument:** five mechanisms, six prompt/architecture coupling patterns, an illustrative demonstration, and governance recommendations. **ROO relevance:** implicit design choices motivate reviewable decisions. The abstract supplies no industry-wide collapse rate, exhaustive distributed-system benchmark, or ROO evaluation; detailed methods remain to inspect.

### S92 — Microservice generation and contract tests

Bassam Adnan, Matteo Esposito, Davide Taibi, and Karthik Vaidhyanathan, **2026**, “Can AI Agents Generate Microservices? How Far are We?” [Author preprint](https://arxiv.org/abs/2603.09004); [version 1 full text](https://arxiv.org/html/2603.09004v1). The record reports ICSA 2026 acceptance; the camera-ready paper was not inspected.
**Access:** abstract and selected validity-threat passages. **Reported investigation:** 144 generated services; clean-state integration-test pass rates of 81–98%, alongside inconsistent correctness and limited generalizability. Incremental unit tests concern a different scenario. **ROO relevance:** retain positive contract results and limitations; test passing is not general architectural correctness or ROO efficacy.

### S93 — LLM-assisted Event Storming

Lingli Cao et al., **ICSA 2026**, “Leveraging Large Language Models for Event Storming in Domain-Driven Design: A Controlled Experiment.” [Official conference abstract](https://conf.researchr.org/details/icsa-2026/icsa-2026-papers/33/Leveraging-Large-Language-Models-for-Event-Storming-in-Domain-Driven-Design-A-Contro).
**Access:** conference metadata and abstract only. **Reported experiment:** 240 postgraduate participants in 60 teams, comparing manual modeling and basic/optimized LLM prompts. Generated elements were generally reliable, with important omissions and consistency limits for complex logic. **ROO relevance:** compare missing obligations and assistance conditions. The abstract does not substantiate the dossier's claimed severe event-to-aggregate translation errors; the full methodology and results remain to inspect.

### S94 — ADD-guided architectural assistance

Humberto Cervantes, Rick Kazman, and Yuanfang Cai, **2026**, “Better Together: An LLM-assisted approach to designing software architectures using Attribute-Driven Design.” *IEEE Transactions on Software Engineering*, early metadata pages 1–17. [DOI](https://doi.org/10.1109/TSE.2026.3706446); [coauthor's institutional abstract](https://researchdiscovery.drexel.edu/esploro/outputs/journalArticle/Better-Together-An-LLM-assisted-approach-to/991022193898304721).
**Access:** institutional abstract and Crossref-deposited metadata; full paper not audited. **Reported approach:** ADD instructions and an architect persona guide iterative design documents, compared with a proven design and assessed by four professional architects. Human guidance remains necessary. **ROO relevance:** a direct method-guided upstream comparator; abstract-level findings do not establish industrial generality or ROO superiority.

### S95 — Distributed modeling and AI-assisted checker workflows

P project, current official documentation, checked **2026-10-12**. [Two-phase-commit tutorial](https://p-org.github.io/P/tutorial/twophasecommit/); [PeasyAI](https://p-org.github.io/P/getstarted/peasyai/).
**Access:** tutorial conclusion/examples and PeasyAI features/workflow inspected. **Documented capabilities:** transaction-atomicity, timeout, failure, and progress modeling; design-document generation of P models/specifications with compilation, PChecker feedback, and human fallback. **ROO relevance:** formal distributed design and assisted checking are antecedents. Model checks remain scoped to the model, properties, assumptions, and explored executions; no product run or verified design-to-production translation was performed here.

### S96 — Assertion encounters and existential witnesses

Antithesis, current official documentation, checked **2026-10-12**. [Asserting correctness](https://antithesis.com/docs/product/writing_tests/assertions/).
**Access:** assertion categories and evaluation semantics inspected. **Documented distinction:** an `always` failure can refute the observed property; one passing `sometimes` encounter supports an existential witness. **ROO relevance:** one reconciliation witness is not eventual recovery of every accepted attempt. Monitoring scope, request identity, environment assumptions, and independent expected behavior need definition. No SDK integration or test run was performed.

### S97 — The test-oracle problem

Earl T. Barr, Mark Harman, Phil McMinn, Muzammil Shahbaz, and Shin Yoo, **2015**, “The Oracle Problem in Software Testing: A Survey.” *IEEE Transactions on Software Engineering* 41(5), 507–525. [DOI](https://doi.org/10.1109/TSE.2014.2372785); [coauthor's manuscript](https://philmcminn.com/publications/barr2015.pdf).
**Access:** manuscript abstract/opening and Crossref-deposited journal metadata. **Established problem:** generating inputs differs from judging desired behavior; specifications, models, contracts, metamorphic relations, and human knowledge provide oracle approaches. **ROO relevance:** eliciting candidate obligations does not automatically produce a correct oracle. This survey neither makes all simulation perfect nor validates a ROO invariant generator.

### S98 — Evaluation purpose, context, and timing

John Venable, Jan Pries-Heje, and Richard Baskerville, **2016**, “FEDS: a Framework for Evaluation in Design Science Research.” *European Journal of Information Systems* 25, 77–89. [DOI](https://doi.org/10.1057/ejis.2014.36); [institutional paper](https://rucforsk.ruc.dk/ws/files/58874543/art_10.1057_ejis.2014.36.pdf).
**Access:** selected printed pp. 78–80 inspected. **Established distinctions:** formative/summative purpose and artificial/naturalistic paradigm form the FEDS axes; ex-ante/ex-post timing is discussed separately. **ROO relevance:** define the evaluated artifact, purpose, context, and episode. A pre-code counterexample label does not automatically classify every episode or demonstrate method utility.

### S99 — Considering the opposite in human judgment

Charles G. Lord, Mark R. Lepper, and Elizabeth Preston, **1984**, “Considering the opposite: A corrective strategy for social judgment.” *Journal of Personality and Social Psychology* 47(6), 1231–1243. [DOI](https://doi.org/10.1037/0022-3514.47.6.1231); [coauthor-profile paper copy](https://www.researchgate.net/profile/Mark-Lepper-2/publication/16669522_Considering_the_Opposite_A_Corrective_Strategy_for_Social_Judgment/links/56107d7508ae48337519fedb/Considering-the-Opposite-A-Corrective-Strategy-for-Social-Judgment.pdf).
**Access:** paper opening and Crossref-deposited metadata; detailed experiments not audited. **Established antecedent:** considering opposite possibilities as a human social-judgment intervention. **ROO relevance:** correct the attribution to Kahneman/Tversky and treat transfer to software or LLM review as a hypothesis. No optimal-debiasing claim or ROO effect is established.

## Selected theses and architecture tradeoffs

### S100 — SafeJava and persistent object upgrades

Chandrasekhar Boyapati, **2004**, *SafeJava: A Unified Type System for Safe Programming*. PhD thesis, MIT. [Institutional record and abstract](https://dspace.mit.edu/entities/publication/956f1374-301f-48fc-813e-d72ab2ac2843).
**Access:** institutional metadata and abstract; not a full thesis reading. **Reported scope:** ownership-based encapsulation, effects, race/deadlock prevention, regions, and software upgrades in persistent object stores. **ROO relevance:** a blanket characterization of this ownership work as volatile-heap-only is incorrect. These results do not establish a payment provider's recovery protocol; compare the specific property and model, rather than declaring all durable concerns absent.

### S101 — Rust language foundations in a doctoral thesis

Ralf Jung, **2020**, *Understanding and Evolving the Rust Programming Language*. PhD thesis, Saarland University. [Institutional record and abstract](https://publikationen.sulb.uni-saarland.de/handle/20.500.11880/29647?locale=en), DOI 10.22028/D291-31946.
**Access:** record and abstract; full thesis not critically read. **Reported scope:** RustBelt and Stacked Borrows address Rust's safety foundations, including reasoning about unsafe implementations. **ROO relevance:** memory and thread safety have formal antecedents; they are neither a complete business-policy guarantee nor evidence that formal methods cannot express broader obligations. See also S23 and S88.

### S102 — Invariant confluence and coordination avoidance

Peter Bailis, **2015**, *Coordination Avoidance in Distributed Databases*. PhD thesis, UC Berkeley; technical report UCB/EECS-2015-206. [Institutional record](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2015/EECS-2015-206.html); [author-hosted thesis](https://www.bailis.org/papers/bailis-thesis.pdf).
**Access:** metadata and selected full-text passages, especially section 3.2, Theorem 1, printed pages 28–29; no independent proof verification. **Established within the model:** invariant confluence of the transaction set characterizes coordination-free execution with global invariant validity, transactional availability, and convergence. **ROO relevance:** Coordinator should identify the operations, invariant, merge behavior, and assumptions. The result is not simply “all nonmonotonic invariants require synchronous global coordination,” and does not prescribe a global lock or one particular coordinator.

### S103 — Robust composition of authority and concurrency

Mark Samuel Miller, **2006**, *Robust Composition: Towards a Unified Approach to Access Control and Concurrency Control*. PhD thesis, Johns Hopkins University. [Author's thesis page](http://www.erights.org/talks/thesis/).
**Access:** search-indexed primary landing-page metadata and abstract; direct page/PDF retrieval failed. **Reported scope:** robust cooperation among concurrent, potentially malicious distributed components, with E and CapDesk as embodiments. **ROO relevance:** compare authority and concurrency together. This access does not support a chapter-level negative claim about revocation or failure recovery. S24 provides a separately identified capability-design antecedent.

### S104 — TOCTTOU as an operating-system security problem

Jinpeng Wei, **2009**, *Improving Operating Systems Security: Two Case Studies*. PhD thesis, Georgia Institute of Technology. [Institutional record and abstract](https://repository.gatech.edu/entities/publication/9a43b285-341b-4b72-bfd2-fbac4b18f7b2).
**Access:** record and abstract. **Reported scope:** Unix filesystem time-of-check-to-time-of-use attacks and K-Queue, a kernel-queue-driven hiding technique, with an integrity defense. K-Queue here is not the BSD event-notification facility; the earlier ledger description was incorrect. **ROO relevance:** an antecedent for checking what remains valid between observation and use. Applying this concern to a revocable business permission requires its own policy and execution model; no universal zero-delay remedy follows from the abstract.

### S105 — Explicit organization and reorganization of agents

Jomi Fred Hübner, **2003**, *Um modelo de reorganização de sistemas multiagentes*. PhD thesis, Escola Politécnica, Universidade de São Paulo. [Institutional record and abstract](https://teses.usp.br/teses/disponiveis/3/3141/tde-17052004-151854/pt-br.html), DOI 10.11606/T.3.2003.tde-17052004-151854.
**Access:** record and abstract, not full thesis. **Reported scope:** MOISE+ organizational structure, functioning, obligations/permissions, and an explicit reorganization process. **ROO relevance:** organizational and deontic constraints precede agent-assisted ROO proposals. Do not equate this 2003 thesis with the later JaCaMo platform or assume an institution of subsequent affiliation awarded the degree.

### S106 — Declarative application assembly from concepts

Santiago Perez De Rosso, **2020**, *Declarative Assembly of Web Applications from Predefined Concepts*. PhD thesis, MIT. [Author's bibliography](https://spderosso.github.io/writings.html); [thesis](https://spderosso.github.io/phd-thesis.pdf).
**Access:** title pages/abstract and selected full-text implementation/study passages, chapter 7 pp. 110–112 and chapter 8 pp. 145, 156–157. **Reported scope:** reusable behavioral concepts, declarative synchronization, and an implemented Déjà Vu library, gateway, compiler, and catalog. The author replicated 12 student applications; author implementation and the course-project sample limit generalization. Detailed and summary code-reduction percentages disagree, so no single percentage is adopted here. **ROO relevance:** implemented concept composition and its evaluation precede ROO. This thesis is distinct from the Onward! 2019 paper and supplies no comparative ROO result.

### S107 — Empirical Python property-based testing

Isadora de Oliveira, **2026**, *Property-Based Testing in Python: Empirical Insights*. Master's dissertation, UFMG. [University-hosted dissertation](https://homepages.dcc.ufmg.br/~mtov/diss/2026-isadora.pdf).
**Access:** front matter, abstract, and selected methods/threats passages in chapters 3–5. **Reported evidence:** 367 tests sampled from 7,612 identified tests in 244 repositories; the sample covers 108 repositories. Further studies examine 213 Stack Overflow posts and manually classify Ghostwriter-template eligibility for 203 tests: 18.23% fully eligible, 30.05% partially eligible, 51.72% ineligible. **ROO relevance:** motivates measuring property-authoring and automation limits; does not demonstrate universal human cognitive blindness or a benefit from ROO's counterexample step. Language, sampling, tool, and classification limits remain material.

### S108 — CAP under explicit system assumptions

Seth Gilbert and Nancy Lynch, **2002**, “Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services,” *ACM SIGACT News*. [Author-hosted paper](https://www.comp.nus.edu.sg/~gilbert/pubs/BrewersConjecture-SigAct.pdf).
**Access:** full text retrieved; abstract and introductory scope passages examined. **Established:** an impossibility result under the paper's definitions and asynchronous network assumptions, with discussion of partially synchronous models. **ROO relevance:** state consistency, availability, and failure assumptions precisely. Attribute the conjecture to Brewer and this formal treatment to Gilbert/Lynch. CAP is not an unconditional product-ranking rule.

### S109 — PACELC and latency/consistency tradeoffs

Daniel J. Abadi, **2012**, “Consistency Tradeoffs in Modern Distributed Database System Design,” *Computer*, February 2012, 37–42. [Author-hosted paper](https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf).
**Access:** full text retrieved; formulation and scope passages examined. **Established proposal:** PACELC distinguishes partition-time availability/consistency choices from latency/consistency choices otherwise. **ROO relevance:** architecture alternatives need operational assumptions outside failure periods too. A taxonomy and its historical examples do not certify current database products, configurations, or external-effect guarantees. Neither CAP nor PACELC evaluates ROO.

## Follow-up sources for the 22-work thesis table

The audit reports retain URLs, cached-source
hashes, selected page/section locations, retrieval failures, and unresolved
metadata. The following entries distinguish thesis evidence from related
papers. Their count is not a count of verified or fully read theses.

### S110 — Replicated identity: papers and an unresolved thesis citation

The supplied Martin Kleppmann thesis title, *Data Consistency and High Availability in Distributed Systems*, was **not verified**. Cambridge's [departmental list](https://www.cl.cam.ac.uk/lists/phd/) records a start date and a committee approval entry, with a conditional-approval caveat; it does not establish that title or final conferral. His [2019 retrospective](https://martin.kleppmann.com/2019/10/30/research-update.html) says he obtained his PhD in 2018. A [Cambridge news profile](https://www.cst.cam.ac.uk/news/new-associate-professor-computer-security-and-privacy) calls the supplied phrase his PhD topic and gives 2019. This supports a topic attribution, not a verified formal thesis title or body; the year conflict remains unresolved (targeted recheck, 2026-10-13).
**Separate primary papers:** Kleppmann, Gomes, Mulligan, and Beresford, **2018**, [*OpSets: Sequential Specifications for Replicated Datatypes*](https://arxiv.org/abs/1805.04263), §§2.1–2.3; Gomes, Kleppmann, Mulligan, and Beresford, **2017**, [*Verifying Strong Eventual Consistency in Distributed Systems*](https://martin.kleppmann.com/papers/crdt-isabelle-oopsla17.pdf), §§5.2–5.3, 6.1, 9, DOI 10.1145/3133933. **Access:** selected full-text passages of these papers; no thesis body. **ROO relevance:** operation/message/element identities and scoped CRDT proofs precede ROO. They do not establish provider-side deduplication or a general impossibility of reconciling noncommutative effects. A stable intent key requires provider and recovery semantics.

### S111 — Invariant preservation in geo-replicated stores

Valter Balegas de Sousa, **2017**, *Invariant preservation in geo-replicated data stores*. Doctoral thesis, NOVA FCT, advised by Nuno Preguiça; the supplied co-advisor attribution remains unverified. [Institutional record](https://run.unl.pt/entities/publication/390b8f18-d7a4-439d-b96f-6b920f439eb6); [thesis](https://run.unl.pt/server/api/core/bitstreams/57aabc25-0eae-408a-9661-de3f6c764db9/content).
**Access:** full PDF retrieved; research-lane reading of selected chapters 3–5 and 7, including pp. 26, 38–40, 51–53, 63–82, 119–123; independent reviewer additionally checked §6.1.2/Table 6.1, pp. 85–87. **Established within the models:** explicit invariants and operation effects guide coordination/reservation choices. Bounded Counter escrow preserves numeric resource bounds; referential constraints use separate reservation mechanisms. Operation-delivery assumptions are not payment-provider guarantees. **ROO relevance:** invariant elicitation and enforcement selection are substantive antecedents. ROO records such decisions but implements no reservation protocol; neither a counter nor a completed Identity field guarantees one external charge.

### S112 — Database replication by ordered certification

Fernando Pedone, **1999**, *The Database State Machine and Group Communication Issues*. EPFL thesis 2090, Doctor ès sciences, directed by André Schiper. UFRGS is his prior MSc institution. [Official thesis](https://infoscience.epfl.ch/record/32566/files/EPFL_TH2090.pdf); [Cornell-hosted copy](https://www.cs.cornell.edu/courses/cs734/2000FA/cached%20papers/Ped99-statemachine-thesis.pdf).
**Access:** institutional front matter and selected full-text §§3.1–3.3, 6.1–6.2, pp. 21–30, 104–106; mirror retained because direct official download failed. **Established within the model:** local execution with strict two-phase locking, Atomic Broadcast, and deterministic certification coordinate fully replicated databases. Two-phase locking is distinct from two-phase commit. The partial-replication discussion reintroduces coordination/atomic commitment. **ROO relevance:** a concrete Coordinator mechanism with explicit assumptions, not a general replacement for 2PC across arbitrary resources or independent providers. The later 2003 journal article is a separate publication.

### S113 — Typestate and aliased-object permissions

Kevin Bierhoff, **2009**, *API Protocol Compliance in Object-Oriented Software*. PhD thesis, CMU, advised by Jonathan Aldrich; CMU-ISR-09-108, 23 April. [Author's thesis page](https://www.cs.cmu.edu/~kbierhof/thesis/); [thesis](https://www.cs.cmu.edu/~kbierhof/thesis/bierhoff-thesis.pdf).
**Access:** selected §§3.1–3.2, 4.1.3, 4.2.6, 9.1, pp. 21–31, 39–40, 51, 122–124. **Established within the model:** typestates and unique/full/share/immutable/pure permissions track access, aliasing, and protocol-state knowledge. The cited soundness proof covers a narrower full/share/pure calculus without inheritance, state dimensions, or nondeterministic specifications; it is not a theorem for the complete tool. **ROO relevance:** strong Access antecedent. Object-reference permission differs from business-principal authorization or revocation; unmodeled domains are not proved inexpressible. Java case studies do not validate ROO.

### S114 — Local heap reasoning and abstraction

Matthew J. Parkinson, **2005**, *Local reasoning for Java*. Cambridge PhD submitted August; UCAM-CL-TR-654 issued November. Supervisors **Gavin Bierman and Andrew Pitts**; Peter O'Hearn is acknowledged for comments. [Institutional record](https://www.cl.cam.ac.uk/techreports/UCAM-CL-TR-654.html); [thesis-based report](https://www.cl.cam.ac.uk/techreports/UCAM-CL-TR-654.pdf).
**Access:** selected chapters 2–7, especially Theorem 3.7.15 pp. 59–62, chapter 5 pp. 79–85, chapter 6 pp. 92–105, and open questions pp. 109–110. **Established within the model:** separation logic, abstract predicates, counted read-sharing, and class-indexed predicate families support modular resource reasoning. Read-sharing and predicate families are distinct mechanisms; the soundness result is conditional partial correctness for the defined Java subset. **ROO relevance:** Access and resource-transfer antecedents, without a transferred guarantee for durable storage, business authorization, or observation freshness.

### S115 — Cache leases with bounded validity and waiting

Cary G. Gray, *Performance and Fault-Tolerance in a Cache for Distributed File Service*, STAN-CS-91-1363, cataloged **May 1991**. [Stanford report-catalog scan](https://ftpmirror.your.org/pub/misc/bitsavers/pdf/stanford/Stanford_CS_TR_Collection_2025-12-12/OCR/CS-TR-94-1507-ocr.pdf). **Access:** catalog entry only; original thesis, degree date, and formal advisor remain unverified. The supplied title is inaccurate; catalog issue and thesis submission/award dates must not be conflated.
**Separate primary paper:** Gray and David R. Cheriton, **1989**, [“Leases: An Efficient Fault-Tolerant Mechanism for Distributed File Cache Consistency”](https://cs.wheaton.edu/~cgray/writing/leases-sosp.pdf), SOSP, DOI 10.1145/74850.74870. **Access:** selected §§2, 3, 5, pp. 202–207. Conflicting writes can wait for holder approval or lease expiry, including when a holder is unreachable. Clock bounds and server recovery behavior matter. **ROO relevance:** an implemented temporal-access antecedent for Horizon; leases bound some waits rather than eliminate blocking. A review field enforces no lease or clock protocol.

### S116 — Database dependency and snapshot semantics

Atul Adya, **1999**, *Weak Consistency: A Generalized Theory and Optimistic Implementations for Distributed Transactions*. MIT PhD, supervised by Barbara H. Liskov, title page 18 March; MIT-LCS-TR-786. [Institutional record](https://dspace.mit.edu/entities/publication/aff3d91b-ec87-4861-9725-b2501f242771); [university-hosted thesis copy](https://www.csd.uoc.gr/~hy460/pdf/adya99weak.pdf).
**Access:** full PDF retrieved from the mirror; selected §§3.1.3–3.1.4, 4.3, pp. 37–43, 78–82. **Established within the model:** predicate operations, read/write anti-dependencies, and graph-based isolation specifications, including Snapshot Isolation as PL-SI. “Generalized Snapshot Isolation” and “Predicate Leases” were not found in the complete extraction; GSI is named in the separate Elnikety/Pedone/Zwaenepoel 2005 paper. **ROO relevance:** makes observation/version and dependency assumptions explicit. Database isolation is not a business freshness SLA or a durable-workflow history guarantee.

### S117 — Choreographies and endpoint projection

Fabrizio Montesi, **2013**, *Choreographic Programming*. PhD thesis, IT University of Copenhagen, advised by Marco Carbone. [Author-hosted thesis](https://www.fabriziomontesi.com/files/choreographic_programming.pdf); [institutional record](https://portal.findresearcher.sdu.dk/da/publications/choreographic-programming/).
**Access:** selected §§1.4–1.5, Theorems 2.3.2/2.4.2, endpoint projection §2.5, and partial-choreography §3.5, printed pp. 5–7, 20, 29, 38–42, 69–70. **Established within the calculi:** deadlock/progress and operational-correspondence results under specified sorting, typing, projection, and structural restrictions; Chor compiles to Jolie endpoints. **ROO relevance:** protocol ordering and implementable interactions are substantial Execution antecedents. The theorems do not establish freedom from every deployed API incompatibility, network failure, or provider error; ROO inherits none of these guarantees by recording an execution decision.

### S118 — Refined multiparty protocols and generated endpoints

Fangyi Zhou, **2024 title page**, *Refining Multiparty Session Types*. PhD thesis, Imperial College London. [Institutional record](https://spiral.imperial.ac.uk/entities/publication/fa1a6b94-eaf8-4e58-b6c5-dac24a195de6); [author-hosted thesis](https://fangyi.io/assets/phd-thesis.pdf). The record's issued date is August 2023 and award date March 2024; preserve those distinct dates and its supervisor metadata.
**Access:** selected introductory publication list, §§2.4–2.5, chapters 3–4, and §6.2, pp. 3–6, 25–26, 32–62, 74–88, 109–110. **Established within the model:** refinements and SESSION* generation to F*, with OCaml extraction and SMT checking. The main semantics assumes failure-free processes/links. Crash-stop papers are explicitly listed as publications without corresponding thesis parts; cited Rust projects are separate work. **ROO relevance:** a formal protocol/refinement comparator. Neither mixed-party deployment nor arbitrary production failure handling follows automatically; ROO provides no such theorem.

### S119 — Distributed failure diagnosis and reproduction

Yongle Zhang, **2021**, *Automating Failure Diagnosis for Distributed Systems* (title page); the Toronto catalog uses *Automatic*. PhD thesis, University of Toronto, supervised by Ding Yuan. [Institutional record](https://utoronto.scholaris.ca/items/5ae55c95-6e58-4812-8a02-ddba2746ec02/full); [thesis](https://utoronto.scholaris.ca/server/api/core/bitstreams/bffd5f3b-f3e5-4cda-aeb3-3e3325938702/content). The dissertation award was in 2022.
**Access:** selected §§3.5, 4.4, 4.6, printed pp. 32–36, 57–60, 68. **Reported evidence:** Kairux localized 7/10 sampled failures; one case informed tool design. Pensieve fully reproduced 13/18 sampled failures, with two partial results and log-dependent sampling. Missing tests, non-log symptoms, and large event chains limit results. **ROO relevance:** concrete failure evidence and limits, not a study of design review. The 92% statistic belongs to the separate 2014 study S57 and its selected catastrophic cases; it is not a thesis result or a timeout-specific ROO benefit.

### S120 — Main-memory transaction recovery, distinct from Sagas

Kenneth Salem, **January 1989 dissertation**, *Failure Recovery in Memory-Resident Transaction Processing Systems*. Princeton PhD, advised by Hector Garcia-Molina; CS-TR-188-88 is dated December 1988. [Institutional record](https://www.cs.princeton.edu/research/techreps/716); [scanned dissertation](https://www.cs.princeton.edu/techreports/1988/188.pdf).
**Access:** complete scan retrieved; selected pages read visually, including §§2.5, 3.4, 5.1, 8.3, printed pp. 16–17, 37–39, 64, 123–124. No usable full-text layer. **Reported scope:** checkpoints, logs, durability, recovery strategies, performance models, and a testbed. Sagas appear in the concluding discussion of long-lived transactions, not as the dissertation's central contribution. Cite Garcia-Molina and Salem's separate **1987 Sagas** work (S19) for semantic compensation. **ROO relevance:** recovery and durable acknowledgment are prior art. Database reconstruction, compensation, and an independent provider's uncertain outcome require different assumptions; none is a universal 2PC replacement.

### S121 — Formal architectural connectors in Wright

Robert J. Allen, **1997**, *A Formal Approach to Software Architecture*. CMU PhD, advised by David Garlan, CMU-CS-97-144. [Institutional degree record](https://csd.cs.cmu.edu/academics/doctoral/degrees-conferred/robert-j-allen); [thesis](https://csd.cs.cmu.edu/sites/default/files/phd-thesis/CMU-CS-97-144.pdf).
**Access:** selected chapter 3 pp. 40–80, chapter 7 pp. 155–162, chapter 9 pp. 190–194, and chapter 10 pp. 202–205. **Established within the model:** first-class connector roles/glue and CSP refinement checks for defined compatibility/deadlock properties. FDR automation needs finite-state models; some checks were not automated, general style conformance is undecidable, and the architecture scope is static/asynchronous. **ROO relevance:** explicit interaction contracts and analysis precede ROO (see S32). This is neither a general business-invariant checker nor empirical proof of industry-wide ADL rejection; different review units establish no ROO superiority.

### S122 — Relationships as programming-language constructs

Alisdair Wren, **2007**, *Relationships for object-oriented programming languages*. Cambridge PhD submitted March; UCAM-CL-TR-702 issued November. Supervisors Gavin Bierman and Andrew Pitts. [Institutional thesis-based report](https://www.cl.cam.ac.uk/techreports/UCAM-CL-TR-702.pdf).
**Access:** selected §§1.2–1.4, 2.2–2.8, and chapter 6, pp. 19–24, 31–68, 137–139. **Established within the calculi:** RelJ relationships with state/methods/inheritance, Qς, and scoped type-safety/abstraction-preservation results. The base model has one-way binary many-to-many relations and omits automatic enforcement of common relational constraints; unlinking can leave a reachable inactive relationship object. **ROO relevance:** explicit relations are direct prior art (see S54). The critique targets error-prone mutable reference encodings, not pointers universally destroying modularity. Implementation/user experience remained future work; this is not commercial-rejection evidence.

### S123 — Perspective-based reading and contextual evaluation

Forrest J. Shull, **1998**, *Developing Techniques for Using Software Documents: A Series of Empirical Studies*. PhD dissertation, University of Maryland, advised by Victor R. Basili. [Completed dissertation archive](https://www.cs.umd.edu/projects/SoftEng/ESEG/papers/postscript/shull_diss.ps.gz). NASA/GSFC SEL was a study collaborator, not the degree-granting institution.
**Access:** full PostScript archive retrieved and converted; selected chapter 2 pp. 69–86, chapter 3 pp. 149–155, and synthesis pp. 163–165. **Reported evidence:** PBR was compared with the usual NASA/SEL review process; team unions were constructed from individual defect lists. Results vary with document/context and study version. Thesis §2.1.1 also summarizes a separate earlier DBR comparison against ad hoc/checklist review; that is not the later PBR study. This is distinct from S63's direct checklist/scenario experiment (clarified 2026-10-13). **ROO relevance:** procedural reading perspectives and contextual method evaluation precede ROO. Neither universal checklist failure, maximal detection, an executable-test requirement for every counterexample, nor a ROO benefit follows.

## Proposed synthesis and evidence limits

**ROO proposal:** for a selected relationship, record **Custodian, Identity, Coordinator, Authorization, Access, Horizon, Execution, and Failure**. The [canonical six-step procedure](../docs/02-relationship-design.md#23-the-six-step-decision-procedure) describes the scenario, triages relationships, completes the contract, chooses realizations, checks a counterexample, and records evidence and a decision. Relationship/cardinality, Invariant, Evidence, and Open frame those decisions; they are not additional fields.

The candidate contribution is their integration into a compact, language-independent design/review procedure, with separate custody, identity, invariant coordination, and caller permission, and explicit validity, execution, and recovery obligations. Neither the ingredients, the priority of responsibilities over representation, explicit relations, nor counterexample analysis are claimed as inventions. Exact field names or a missing match in this search do not establish historical originality. A natural-language contract provides no automatic formal composition, refinement, authorization enforcement, or proof of progress.

This ledger contains **123 source entries**, some grouping several publications or URLs and one retaining an unresolved thesis lead alongside separately checked papers. It is a selective foundation and related-work ledger, not a systematic review. The exploratory investigation did not perform exhaustive database exports, independent double screening, or a preregistered synthesis. Source access notes distinguish metadata, abstract, partial text, and full-text retrieval; retrieval alone is not a complete critical reading. Later targeted checks do not retroactively make the dated dossier systematic.

Three questions remain separate: whether the underlying concepts have published support, whether the integration contributes a distinct method, and whether using it improves outcomes enough to justify its cost. Only the first has support from this literature selection. The latter two require the comparisons and independent evaluation in the [research agenda](agenda-revised-2026-10-12.md). Laboratory receipts concern their identified implementations and scenarios, not method superiority or production readiness.
