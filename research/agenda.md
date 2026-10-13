# Research agenda

ROO v0.1 is a proposal. This agenda defines how subsequent work could test its usefulness without presenting aspiration as measured evidence.

## Working hypotheses

1. Writing relationship ownership and mutation authority before implementation reduces redesign caused by hidden aliases and ambiguous lifecycles.
2. The same contract helps Java and other garbage-collected implementations expose lifecycle, mutation and concurrency defects that reachability alone does not address.
3. Translating a pattern by its intent produces simpler Rust implementations than reproducing its original class structure.
4. Explicit failure boundaries improve review of consuming transitions, asynchronous use cases and event delivery.

These are hypotheses, not established results. Rust expertise, domain complexity and implementation experience are significant confounders.

## A reproducible comparison

Choose three bounded problems: a document tree with reverse navigation, an order workflow with external payment, and an event subscription system. Freeze the same requirements, extension scenario, failure cases and acceptance tests for every implementation.

Compare a conventional OO design process with a ROO process. Have separate participants implement both Rust and Java variants; counterbalance assignment and experience where possible. Record time and design changes without exposing private credentials or production data. Reviewers should evaluate observable requirements using the same rubric and, where practical, without knowing which method produced the implementation.

| Observation | Why collect it | Important limitation |
|---|---|---|
| Time to accepted behavior | Measures delivery effort | Familiarity and task ordering influence it |
| Changes after first implementation | Reveals design revision | Productive exploration is not automatically waste |
| Missing lifecycle / mutation decisions | Tests contract usefulness | Reviewers need a shared definition |
| Defects found by negative scenarios | Measures concrete failures | The scenario set has limited coverage |
| Extension change scope | Tests intended extensibility | Extra abstraction can game this measure |
| Retained memory and allocation | Tests representation cost | Workload and profiling method matter |
| Lock duration / contention / queue pressure | Tests concurrency costs | Microbenchmarks may mislead |
| Reader understanding | Tests communication value | Requires structured questions and multiple readers |

Compiler-error count, line count, use of `unsafe`, or number of shared pointers must not stand alone as quality scores. A library can compile, be short, and still implement the wrong contract. Legitimate reference counting, locks, or advanced data structures are not failures of the method.

## Evidence package

Publish a future comparison only with requirements, toolchain versions, full candidate sources, exact checks, reviewer findings, limitations and results for both successful and failed attempts. Separate compiler-enforced properties, runtime checks, observed behavior and architectural judgment.

## Next editions

- **0.2 — Case studies:** implement the three problems in Rust and Java with matching observable behavior, not matching pointer syntax.
- **0.3 — Concurrency and persistence:** add bounded queues, cancellation, durable identity, optimistic concurrency, and an outbox case study.
- **0.4 — Evaluation:** run the comparison above and revise the method from counterexamples.
- **Later:** consider diagram tooling or machine-readable contracts only after the vocabulary has proved useful. No custom language or code generator is required for v0.1.

## Open questions

Which relationships merit a written contract, and which are obvious enough to remain local? When does explicit identity resolution add more complexity than it removes? How can capability boundaries express revocation? What vocabulary best describes temporal ownership in async APIs? Where do highly connected graphs, ECS systems, FFI, pinned values and external resource lifecycles require specialized guidance?

The method should evolve by answering these questions with concrete designs and counterexamples.

## Note added 2026-10-13

Added after the fact; the text above is not rewritten. This agenda is the v0.1 plan (line 3). The "Next editions" labels (0.2, 0.3, 0.4) were planning labels and the tagged releases did not follow that table. The release-preparation commits read: v0.2.0 "eight-field contract release", v0.3.0 "persistent authorization release", v0.4.0 "operation permissions release", v0.4.1 "method and implementations release", v0.4.2 "validation kit release", v0.4.3 "human validation round release" (`git log --oneline`; the v0.4.1 and v0.4.3 tags sit on later follow-up fix commits). The comparison protocol in "A reproducible comparison" is unchanged, and nothing in this file reports its results.
