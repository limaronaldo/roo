# Critical review of the expanded upstream-design dossier

**Status:** selective documentary review, **2026-10-12**. The supplied dossier
contains useful research leads alongside unsupported exclusions, incorrect
attributions, and proposed mechanisms presented as established results. Only
the bounded findings and evaluation proposals below are incorporated into ROO.

The earlier [comparison](upstream-design-comparison.md) already identifies
overlap with specification planning, interaction contracts, architectural agents,
and property testing. This review adds academic comparisons, formal distributed
modeling, test-oracle distinctions, and a correction to the proposed assertions.
It does not establish a complete ROO equivalent, historical priority, or efficacy.

## Review method and limits

The supplied arXiv identifiers, paper titles, and DOI were checked against
primary records. Selected full-text passages were inspected where available;
institutional and conference abstracts remain explicitly abstract-level
evidence. Tool capabilities were checked in official documentation, without
installing or executing those products. Access locations are recorded in
[S89–S99](literature.md#expanded-upstream-landscape-and-evaluation).

The dossier's narrated twelve-agent search is not an independently verified run
of this review. No search exports, full screening/extraction trail, or comparable
coverage evidence establishes its systematic or exhaustive label. This review
is itself selective. It does not inherit completeness from a cited systematic
review or treat every bibliography entry as a paper read in full.

The supplied landscape drafts and detailed working records remain separately
preserved. Their presence is not endorsement. The bounded synthesis below and
the [focused comparison](upstream-design-comparison.md) retain supported
antecedents and explicit evidence limits without publishing the raw dossiers.

## Corrections to cited findings

| Source | Supported finding and correction | Consequence for ROO |
|---|---|---|
| [Schmid et al., 2025](https://arxiv.org/html/2505.16697v1), §§2–3.1 (S89) | The review analyzes 18 papers. Its 71% refers to automated LLM use, not retrospective architecture recovery. Its categories include design generation and assistance. | Use its search and classifications as research leads; it does not establish an empty upstream market. |
| [Wang and Liu, 2026](https://arxiv.org/html/2609.17221v1), §§6–7 (S90) | The Architecture-0 preprint studies guarded external evaluation and reports residual semantic/auditor failures. Its static ledgers, small design-task scope, and potential data leakage limit generalization. | Compare verification authority and mapping effort. Its reported gains neither validate ROO nor prove inevitable failure without ROO. |
| [Konrad et al., 2026](https://arxiv.org/abs/2604.04990), abstract (S91) | Prompt-dependent architecture choices are discussed with an illustrative demonstration and proposed governance practices. | A useful failure hypothesis, not a measured industry-wide collapse or a ROO intervention study. |
| [Adnan et al., 2026](https://arxiv.org/abs/2603.09004), abstract and validity threats (S92) | The study reports 81–98% integration-test pass rates in clean-state generation and lower unit-test rates in a different incremental scenario. It reports contract adherence alongside inconsistent correctness. | Retain both outcomes. Different scenarios and test suites do not support a causal superiority comparison or a blanket claim of contract failure. |
| [Cao et al., ICSA 2026](https://conf.researchr.org/details/icsa-2026/icsa-2026-papers/33/Leveraging-Large-Language-Models-for-Event-Storming-in-Domain-Driven-Design-A-Contro), conference abstract (S93) | Generated Event Storming elements were generally reliable, with omissions and benefits from optimized prompts; complex logic remained difficult. | The abstract does not establish the alleged severe errors in translating events into technical aggregates. Compare omissions and consistency within its actual task. |
| [Cervantes, Kazman, and Cai, 2026](https://researchdiscovery.drexel.edu/esploro/outputs/journalArticle/Better-Together-An-LLM-assisted-approach-to/991022193898304721), institutional abstract (S94) | ADD-guided architectural assistance, iteration plans, design documents, and professional assessment are reported. Human guidance remains necessary. | A direct method-guided upstream comparator, rather than evidence that only retrospective architecture tools exist. |

The [MAST entry, S79](literature.md#s79--multi-agent-system-failures) concerns
multi-agent workflow failures. The examined evidence does not establish the
dossier's payment-timeout snippet as an observed study result or its claim that
all named coding agents fail distributed invariants. Without a traceable source
location, that snippet is a synthetic warning, not empirical evidence.

## Disposition of the twelve claimed gaps

| Dossier axis | Review disposition |
|---|---|
| E01 — Specification-first products | S80–S81 already contradict a purely syntactic classification. Funding, valuation, throughput figures, the unattributed quotation, and Tessl's alleged causal pivot were not verified or incorporated; they cannot establish methodological novelty. |
| E02 — Large-company research | [P/PeasyAI](https://p-org.github.io/P/getstarted/peasyai/) documents generation of P types, state machines, specifications, and test drivers from a supplied plain-text design document, followed by compilation and PChecker feedback with human guidance when automated fixes fail. Corporate rankings, philosophical rejection, and exclusive research-focus claims are unsupported here. Cedar's scope does not classify all formal design research. |
| E03 — Architecture research | S89–S94 include prospective design methods and bounded experiments. The supplied 71% interpretation is incorrect. |
| E04 — Coding agents | S79, S82, and S85 do not support the categorical syntax-only or universal distributed-failure claim. Roles and checks still need outcome assessment. |
| E05 — Formal methods | [P's two-phase-commit tutorial](https://p-org.github.io/P/tutorial/twophasecommit/) models atomicity, a timer, node-failure injection, and a conditional progress property. The tutorial assumes reliable message delivery and says coordinator or participant failure can block progress indefinitely; it is not a guarantee for every external business effect (S95). |
| E06 — DDD and Event Modeling | S06, S53, S62, and S93 provide relevant antecedents. A notation's omission from a selected example cannot establish that a whole tradition lacks consistency, time, or recovery reasoning. |
| E07 — Simulation and chaos | S96–S97 distinguish exploration from expected-behavior oracles. Simulator perfection and automatic ROO invariant generation are unestablished; the proposed assertion mapping needs correction below. |
| E08 — API contracts | S81 explicitly includes observable behavior and failure/retry semantics. The listed API vendors were not individually evaluated; their limits cannot be inferred from their category. |
| E09 — Threat modeling | The named products and approaches were not sufficiently inspected to establish blanket exclusions. Keep authorization, state access, trust, and recovery questions available for a symmetric comparison. |
| E10 — ADRs and governance | S78 and S94 provide decision/design assistance antecedents. The listed governance products were not benchmarked. An ADR need not be written after implementation or exclude linked evidence. |
| E11 — Human/AI evaluation | S83, S90, and S94 motivate bounded assistance and independent assessment. FEDS and human debiasing research do not establish that ROO's counterexample step removes bias. |
| E12 — Architectural intermediate representations | An exclusive vacancy is unestablished. ROO currently lacks formal operational/composition semantics and verified translation; its compact record must be compared with existing models and procedures. |

P/PeasyAI's official workflow is a particularly relevant extension of the
comparison: a supplied design document is an input for generating P artifacts,
which are then compiled and checked, with human guidance available when
automated fixes fail (S95). These are capabilities to examine, not independently measured
accuracy or automatic design-to-production correctness. This review did not
run the assistant, checker, or a distributed model.

## Correcting the proposed assertion bridge

The [Antithesis documentation](https://antithesis.com/docs/product/writing_tests/assertions/)
distinguishes assertions over observed encounters (S96). A successful
`sometimes` witness does not show that every outstanding operation progresses.
The following are **proposed review obligations**, not SDK code, model-checking
results, or an implemented ROO integration.

| Supplied mapping | Replacement obligation to define and check |
|---|---|
| Invariant → `always(condition)` | Specify the state, observation points, and instrumented transitions. Passing encounters do not establish coverage of every relevant state. |
| Failure → `sometimes(reconciled)` | Track each accepted attempt and its unresolved state. Specify allowed terminal outcomes and the recovery/environment assumptions. Check each attempt's promised progress; one successful reconciliation can coexist with another attempt stuck forever. |
| Identity → `duplicate_requests <= 1` | Retries may legitimately produce multiple requests. Define at-most-one specified business effect per stable logical attempt, with the deduplication scope, retention, payload consistency, and provider assumptions explicit. Identity alone does not enforce it. |
| Horizon → `read_timestamp >= expiry_limit` | Define what the timestamp measures, the validity interval, clock/skew assumptions, permissible staleness, and revocation policy. The supplied comparison is not a general freshness condition. |

A bounded test can check a recovery deadline under a declared fault envelope;
unbounded eventual progress requires a temporal property and its assumptions.
Distinguish a deadline violation from a run ending with an inconclusive pending
operation. An external evaluator also needs a correct policy and a faithful
observation/model mapping. Neither ROO nor a deterministic checker can invent
those obligations from field names.

The [oracle survey, S97](literature.md#s97--the-test-oracle-problem) describes
specification-, model-, contract-, and metamorphic approaches as well as human
judgment. ROO can help elicit candidate expectations; it does not resolve the
oracle problem or replace domain decisions. `Invariant` frames the record and
is not a ninth contract field.

There is also no direct, unique lowering from a field to a mechanism. A SQL
foreign key does not specify runtime custody; `Box` and `Arc` implement different
sharing choices. A cache lease is one validity mechanism, and an outbox addresses
a particular durable-publication boundary. Their sufficiency depends on the
rest of the contract and system. See [S20](literature.md#s20--transactional-outbox)
and the [canonical realization procedure](../docs/02-relationship-design.md#23-the-six-step-decision-procedure).

## Counterexamples, bias, and evaluation classification

Trying adverse cases continues established design-analysis practice; it is not
a demonstrated revolutionary or exhaustive acceptance test. ROO step 5 accepts
reasoning traces and models as well as executable scenarios. Its relevance,
expected behavior, and evidence remain reviewable decisions.

[FEDS, S98](literature.md#s98--evaluation-purpose-context-and-timing) distinguishes
formative/summative purpose and artificial/naturalistic evaluation context;
it also discusses timing separately. Define the evaluated artifact and episode.
A hypothetical preimplementation challenge and an executed test of a completed
design need not have the same timing classification. Neither label establishes
the engineering utility of ROO as a method.

The direct [consider-the-opposite study, S99](literature.md#s99--considering-the-opposite-in-human-judgment)
is by Lord, Lepper, and Preston, not Kahneman and Tversky. Human judgment results
do not establish that an adversarial agent reliably reduces automation bias or
that the strategy is the most effective intervention for ROO. Popper and Simon
can inform conceptual interpretations, but no causal method benefit follows
from those analogies.

## Incorporation and remaining work

The supported additions are stronger comparison baselines, recorded evidence
limits, independent verification responsibilities, and explicit assertion
obligations. The eight fields and six-step procedure remain unchanged. A
formal-language extension, semantic-to-model translation, and simulator
integration would each require implementation and separate evaluation.

The [agenda](agenda-revised-2026-10-12.md#evaluate-obligations-and-verification-authority) now
separates record structure, adversarial challenge, and verification authority;
holds required policy independent of generated code; and counts mapping,
instrumentation, review, and maintenance costs. It permits no-benefit findings
and valid alternatives from competent existing methods. No product run,
automatic invariant generator, or new ROO efficacy experiment was performed.
