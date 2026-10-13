# Claims and limits

The [method](02-relationship-design.md), [design cases](../case-studies/orders-payments/DESIGN.md),
and [implementations](implementations.md) have different claims. Java, Rust,
PostgreSQL, and HTTP are qualified only to the extent of their recorded checks.
Other [technology candidates](technology-selection.md) are design alternatives,
with no additional implementation or qualification implied by this reorganization.


ROO is a practitioner-method proposal with an executable teaching laboratory.
Every pre-1.0 edition is a preview, and the version selector and release tag
identify which one you are reading; a published snapshot is not a maturity
certification. The project has no documented field study demonstrating that
ROO improves delivery speed, defect rates, or architectural quality.

## Academic position

ROO proposes a compact, language-independent design and review method for
relationships that cross lifecycle, process, transaction, or trust boundaries.
Its candidate contribution is the integration of eight explicit decisions —
**Custodian, Identity, Coordinator, Authorization, Access, Horizon, Execution,
and Failure** — with a [six-step procedure](02-relationship-design.md#23-the-six-step-decision-procedure):
describe the scenario, select critical relationships, complete their contracts,
choose realizations, challenge them with counterexamples, and record evidence
and a decision. Relationship/cardinality, Invariant, Evidence, and Open frame
the record; they are not additional fields.

This is a proposed synthesis and operationalization of existing ideas. It is
not a new ownership theory, formal contract calculus, authorization model, or
distributed consistency protocol. Responsibilities before representation,
explicit relations, and counterexample analysis all have substantial prior art.

ROO complements data abstraction and modular reasoning. Its triage also covers
local lifecycle or trust boundaries and unclear invariant coordination; it
does not require documenting every object pair or moving each responsibility
into a separate component. Neither entity-first nor relationship-first design
is established here as universally superior. The eight fields are proposed
review distinctions, without a proof of independence, minimality, or completeness.

### What already existed

The [literature ledger](../research/literature.md) records primary sources,
access levels, and limits. These are essential comparisons, rather than a
claim that ROO exhausts or supersedes these traditions.

| Existing tradition | Relevant antecedents | Implication for ROO |
|---|---|---|
| Responsibility and collaboration before implementation structure | [Responsibility-Driven Design, 1989](../research/literature.md#s29--responsibility-driven-design); [CRC, 1989](../research/literature.md#s30--crc-cards) | Neither responsibility-first design nor compact collaboration records originate with ROO. |
| Relations and interaction as explicit design entities | [Rumbaugh, 1987](../research/literature.md#s33--relations-as-semantic-constructs); [Allen and Garlan, 1997](../research/literature.md#s32--explicit-architectural-connectors); [Jackson and Fekete, 2001](../research/literature.md#s31--relational-analysis-of-object-interactions); [Bierman and Wren, 2005](../research/literature.md#s54--first-class-relationships-in-a-language) | Explicit relationships, connector semantics, global interaction invariants, and counterexample analysis are prior art. Full-text comparison with Rumbaugh remains open. |
| Scenario roles and relationship semantics | [DCI, 2009](../research/literature.md#s53--data-context-and-interaction); [Storey, 1993 and 2005](../research/literature.md#s52--semantic-relationship-classification) | Collaboration roles and semantic relationship classification precede ROO. DCI's example explicitly addresses transaction ordering. Access limits prevent treating these sources as complete coverage comparisons. |
| Aggregate consistency and identity | [Evans, 2015 reference](../research/literature.md#s06--domain-driven-design); [Vernon, 2011](../research/literature.md#s62--aggregate-consistency-and-identity) | Invariant boundaries, references by identity, and consistency between aggregates are prior art. ROO's separate review questions do not establish that DDD conflates these concerns. |
| Separating and composing agency concerns | [Garcia, Lucena, and Cowan, 2004; Garcia's thesis](../research/literature.md#s65--agents-and-separation-of-concerns) | Interaction and other crosscutting concerns, comparative evaluation, and diffusion metrics precede ROO. A different implementation technique does not establish greater conceptual depth or superior outcomes. |
| Ownership, resource reasoning, and state-dependent operations | [Ownership types](../research/literature.md#s21--ownership-types); [SafeJava, 2004](../research/literature.md#s100--safejava-and-persistent-object-upgrades); [separation logic](../research/literature.md#s22--separation-logic); [RustBelt](../research/literature.md#s23--rustbelt); [typestate, 1986](../research/literature.md#s35--typestate) | These provide specific mechanisms and formal results. SafeJava also addresses persistent object upgrades; a blanket volatile-heap-only description is inaccurate. Their guarantees do not automatically extend to business policy or remote effects. |
| Formal contracts, design exploration, and architectural fault models | [Benveniste et al., 2018](../research/literature.md#s34--contracts-for-system-design); [Alloy](../research/literature.md#s39--alloy-and-bounded-design-analysis); [AADL EMV2 report, 2016](../research/literature.md#s64--architectural-fault-modeling) | Failure modeling already exists in architectural formalisms. A natural-language worksheet has no automatic compatibility, composition, refinement, or proof semantics. It can supply obligations for a separate model. |
| Capabilities and relationship-based authorization | [Capability-oriented design](../research/literature.md#s24--capability-oriented-design); [Fong, 2011](../research/literature.md#s36--relationship-based-access-control); [Zanzibar, 2019](../research/literature.md#s37--zanzibar) | Permission through explicit grants and relationships precedes ROO. A reference, known ID, or completed Authorization field does not enforce a policy. |
| Distributed boundaries and recovery | [Waldo et al., 1994](../research/literature.md#s38--local-and-distributed-interaction); [Sagas, 1987](../research/literature.md#s19--sagas); [distributed transaction guarantees](../research/literature.md#s66--distributed-transaction-guarantees); [Bailis, 2015](../research/literature.md#s102--invariant-confluence-and-coordination-avoidance) | Partial failure and compensation require explicit protocols. Coordination requirements depend on operations, invariants, and assumptions. Distributed databases can provide atomic transactions within their scope; neither local rollback nor a product category establishes atomicity over independent external effects. |
| Concept-centered design and explicit synchronization | [Jackson, 2021](../research/literature.md#s40--concept-design); [Wilczynski et al., 2023](../research/literature.md#s41--industrial-concept-centric-experience); [Meng and Jackson, 2025](../research/literature.md#s42--concepts-and-explicit-synchronizations); [Jackson, 2026 preprint](../research/literature.md#s55--separating-individuals-from-modules); [Meng et al., 2026 preprint](../research/literature.md#s56--explicit-meaning-across-design-and-execution) | Close comparisons extend to identity, persistence, and execution histories. Assess ROO's procedure against the design approach and its assumptions, not only a synchronization engine. No superiority follows from different terminology. |
| AI-assisted design before implementation | [Kiro and Spec Kit](../research/literature.md#ai-assisted-design-and-current-tooling); [MetaGPT](../research/literature.md#s82--structured-architectural-handoffs-between-agents); [MAAD](../research/literature.md#s83--multi-agent-architecture-design-and-evaluation) | Structured design, interaction contracts, specialized roles, and checks have antecedents. Compare substantive obligations and outcomes; neither a vacant market nor a complete ROO equivalent is established. |
| Method-guided assistance and distributed model checking | [ADD-guided assistance](../research/literature.md#s94--add-guided-architectural-assistance); [P/PeasyAI](../research/literature.md#s95--distributed-modeling-and-ai-assisted-checker-workflows) | Architectural methods and formal distributed models already inform assisted design and checking. A model's checked properties do not establish faithful translation of policy or production behavior. |

### Contribution proposed

The research claim to investigate is whether this particular integration makes
important relationship obligations easier to state, distinguish, implement,
and review at a reasonable cost. Separating resource custody, durable identity,
invariant coordination, and caller permission is central to the proposal;
validity intervals, execution boundaries, and recovery decisions follow the
relationship into its implementation. The eight-field record and six-step
procedure are concrete artifacts that can be compared and revised.

The selection of literature supports the ingredients, but does not establish
the synthesis as historically novel or effective. This is a selective search
with recorded access limits, not a comprehensive absence claim or a systematic
review. Different names or the absence of an identical eight-field worksheet
are insufficient evidence of originality. ROO can be investigated as a design-science artifact;
[DSR methods](../research/literature.md#s44--design-science-research) provide a
research process, not a certification of contribution.

The [upstream-design comparison](../research/upstream-design-comparison.md)
also rules out positioning ROO as the invention of AI-assisted architecture
before coding. Whether this specific record and procedure add value within
existing planning workflows remains open. Product documentation is evidence
of a documented workflow, not independent proof of its effectiveness; the
selective comparison cannot certify that no equivalent integration exists.

The [expanded dossier review](../research/upstream-landscape-review.md) adds
stronger comparisons and corrects statistical and source attributions. A
completed contract does not automatically supply a correct test oracle.
One successful reconciliation witness does not establish recovery of every
accepted attempt; safety and progress claims need explicit scope, observations,
and assumptions. Counterexample roles have no established bias-reduction effect
for ROO. These remain evaluation questions, not guarantees of the procedure.

A comparison matrix derived only from ROO's own questions cannot establish
superiority by awarding ROO the most filled cells. A procedure that asks for an
obligation, a notation that can express it, and a mechanism that enforces it
are different kinds of coverage. Classifications need a source location and
scope; "not found in the examined material" does not mean "absent from the
method." Combine those comparisons with cost and outcome evidence.

The [selected-thesis ledger](../research/literature.md#selected-theses-and-architecture-tradeoffs)
further separates existing formal results, practitioner recipes, and candidate
ROO benefits. A gap in a particular language's enforced guarantees does not
establish that prior methods cannot express the obligation or that a completed
ROO record enforces it. Property-based testing studies do not validate ROO's
counterexample procedure. Architecture advice and illustrative code need
independent checking before serving as reference implementations or oracles.

The [follow-up source ledger](../research/literature.md#follow-up-sources-for-the-22-work-thesis-table)
adds selected primary reading of permissions, invariant preservation, replicated
identity, temporal validity, choreographies, connectors, recovery, and procedural
inspection. Fifteen rows have selected thesis-body evidence; six have
record/abstract/catalog evidence, and the supplied Kleppmann thesis citation
remains unresolved. Related papers do not substitute for a verified thesis.
These antecedents strengthen the comparison requirements for ROO; they do not
establish its historical distinctness or transfer formal guarantees to its
review record. The frozen MAAD/ROO pilot remains a historical, candidate-bound
artifact with its own source hashes. This evolving method page does not
establish that the pilot's frozen source matches the current canonical method.

### What remains to validate

| Question | Current status | Evidence still needed |
|---|---|---|
| Are the ingredients grounded in published work? | Supported by the selective ledger, subject to each entry's access limits | Deeper primary-source reading for partial or metadata-only entries. |
| Is the integration meaningfully distinct from existing methods? | Candidate contribution; no historical priority established | Reproducible literature mapping and semantic comparison with RDD/CRC, relational analysis, connectors, concept design, architecture review, and assisted specification/contract planning. |
| Are the fields necessary and sufficient for the intended scope? | Proposed vocabulary exercised in teaching cases | Independent counterexamples, missing/redundant obligation analysis, and field/procedure ablations. A filled record alone is not completeness. |
| Do individual contracts preserve system-wide invariants and progress? | No general composition or liveness result | Explicit assumptions and system models; formal analysis or scoped implementation evidence for each claimed property. |
| Does using ROO improve engineering outcomes enough to justify its cost? | No comparative efficacy or field-adoption result | A competent baseline, predefined outcomes, independent assessment, uncertainty and cost reporting, and replication in real projects. |

The [research agenda](../research/agenda-revised-2026-10-12.md) specifies these next investigations.
The academic dossier and ledger are exploratory, not a systematic review or an
independent human validation. The [academic reading guide](academic-research.md)
separates the source ledger, proposed instruments, and next evidence needs. Teaching examples demonstrate realizations of
selected obligations; their receipts do not measure the method's benefit to
teams.

The [Relationship Contract prompts](02-relationship-design.md) are proposed
review questions whose comprehensibility and assessor agreement remain to be
evaluated. Reduced field sets are experimental conditions, not
recommended editions. Hypothetical results, efficiency curves, and coverage
heatmaps cannot validate a method. Preserved working reviews informed the agenda and recorded rejected claims;
they are not additional evidence of method effectiveness.
Tooling and executable counterexamples are candidates for evaluation, not
demonstrated prerequisites for human adoption. Filling a form or linking a
test cannot establish that its assumptions remain correct.
The [Garcia/Lucena source ledger](../research/literature.md#s65--agents-and-separation-of-concerns)
separates the earlier agent/aspect evidence from ROO's proposed relationship
review unit. Its metric adaptation
is an unvalidated measurement proposal; lower diffusion counts cannot certify
invariant preservation, method benefit, or completeness.

### Adoption and assistance

ROO targets selected consequential relationships. Its scope includes local
lifecycle, trust, and invariant boundaries; there is no blanket exclusion of
CRUD, frontend, or in-memory code and no fixed coverage quota. Reuse existing
records and review changed decisions rather than requiring a new worksheet
for every PR.

Documentation effort, stale decisions, superficial answers, and review delay
are adoption risks to measure. ROO has no evidence establishing inevitable
abandonment, fewer incidents, or a productivity multiplier. Executable
counterexamples can strengthen scoped evidence; models and reasoning remain
useful when execution is unavailable or insufficient. AI drafts and CI checks
are possible aids whose mistakes, maintenance, and review costs also count.
The [adoption analysis](../research/historical-paradigms-and-ai-revival.md)
corrects the cited historical rates and specifies a bounded assistance workflow.

The [assisted design proposal](../research/assisted-design-protocol.md) explores
using the record to compare alternatives before coding as well as to review an
existing implementation. Required policy, observed behavior, and proposed
changes must remain distinct. The record is not a formal intermediate language
or a proof that code generation preserves its obligations. Specialized roles
provide no established exhaustive coverage, near-perfect accuracy, independent
judgment, or negligible marginal cost. ROO remains a method proposal; continuous
agent governance is a possible application to investigate.

## What the evidence supports

| Claim | Relevant evidence | Boundary |
|---|---|---|
| A relationship can be described before choosing a language mechanism | [Canonical method](02-relationship-design.md) and [completed templates](../case-studies/orders-payments/adoption/relationship-contract.md) | A proposed design and review vocabulary |
| The root Rust lab checks selected ownership and API restrictions | [Source](../src/lib.rs), positive and compile-fail doctests, [original validation](../research/validation.md) | Safe local code, the tested API, and intended diagnostics |
| Chapter Rust and Java examples compile and exercise stated behaviors | [Documentation example checks](../scripts/check_doc_examples.py) and the documentation workflow | Declared snippets and assertions; illustrative protocol/configuration blocks are excluded |
| Three case variants match one expected-result fixture | [In-memory specification](../case-studies/orders-payments/SPEC.md), [oracle](../case-studies/orders-payments/expected.tsv), [dated validation](../research/orders-payments-validation.md) | Deterministic simulator scenarios; the shared oracle is project-authored |
| Persistent recovery handles the tested competing workers and restarts | [PostgreSQL specification](../case-studies/orders-payments/postgres/SPEC.md) and [dated validation](../research/postgres-validation.md) | A dedicated local PostgreSQL cluster; provider and inbox use that same server/WAL |
| HTTP retry and response-loss recovery preserve the specified effects | [HTTP specification](../case-studies/orders-payments/http/SPEC.md) and [dated validation](../research/http-validation.md) | Loopback APIs, bounded inputs/workers, synthetic provider |
| The adoption track ran on a hosted AMD64 runner | [Hosted reproduction](10-github-reproduction.md) with run and artifact references | The identified commit, run, platform, and scenarios |
| Durable HTTP operation policy is rechecked at each protected transaction and survives restart | [HTTP authorization extension](../case-studies/orders-payments/http/AUTHORIZATION.md) and shared HTTP verifier | Eight explicit permissions, asserted synthetic principals, one PostgreSQL/WAL domain; constituent response reads use the request permission; no real authentication |
| Execution rechecks permission after an observed grant is revoked | [Authorization example](../case-studies/orders-payments/authorization/README.md), paired thread tests and shared oracle | Trusted synthetic principals, one process-local policy/transition lock; no authentication or durable effects |

A green badge identifies the latest workflow result. For a behavioral claim,
inspect the run's commit, executed scenarios, and receipts. Historical receipts
describe their original candidate; editing a chapter does not rerun them.

## What requires further work

The payment simulators omit real caller authentication, tenant policy, and real
payment networks. The HTTP extension adds opt-in synthetic authorization by
scope, principal, and operation, with durable revocation checks. Its asserted
principal header is not authentication. It has no roles, tenant boundaries,
field-level filtering, or HTTP policy administration.
Legacy HTTP mode remains unauthenticated. The separate authorization example
checks process-local revocation using trusted
synthetic principals; it does not retrofit security into those services.
Scope keys and loopback restrictions are fixture controls. A live system must
implement an authorization policy, verify its provider's idempotency/key-retention
contract, and define operational handling
of unresolved attempts, cancellation, retention, and deletion.

Local rollback does not reverse an independent provider effect. Borrow checking
does not serialize another process's database writes. Crash-restart/WAL tests
exercise configured PostgreSQL recovery, rather than physical power loss or
every possible interleaving. Capacity and performance need separate workloads.

Compilation checks types and access rules; runtime tests observe selected
behaviors; database checks cover the examined storage boundary; protocol tests
cover the exercised exchange. Human review evaluates policy and tradeoffs.
Evidence from one boundary cannot substitute for evidence at another.

## Review and authorship

The initial review used a separate AI agent from the same requested model
family as some authors. This is separation of roles, not independent human
validation. No completed external Rust or DDD/architecture human review is
documented. [How ROO was made](how-roo-was-made.md) links the preserved records.

The [validation kit](validation/README.md) prepares those human reviews and a
small practitioner exercise. Its briefs, criteria, and blank results form are
evaluation materials, not completed review or field evidence. Reports must
identify the reviewed candidate, participant assistance, and observed scope.

The underlying concepts have established prior art. ROO proposes their
integration into a compact relationship contract and adoption procedure;
it makes no priority claim for ownership types, composition, capabilities,
typestate, or consistency boundaries.
