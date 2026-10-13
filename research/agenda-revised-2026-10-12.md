# Research agenda — revised proposal

Prepared through AI-assisted review on 2026-10-12 and curated for development
on 2026-10-13. The earlier [published agenda](agenda.md) remains unchanged.
The separately preserved frozen pilot retains its own method, agenda, cases,
keys, budgets, and source inventory; this evolving proposal does not update
or execute it.

Updated **2026-10-12** for the current eight-field contract and six-step
procedure. ROO is a pre-1.0 practitioner-method proposal. This agenda describes
future investigations, not completed experiments or promised release dates.
The existing Rust/Java, PostgreSQL, HTTP, and authorization laboratories
demonstrate selected realizations; they do not measure the effect of adopting
the method. See [claims and limits](../docs/claims-and-limits.md).

## Separate the research questions

| Question | Candidate hypothesis | What would challenge it? |
|---|---|---|
| Distinctness | ROO integrates obligations in a useful way not already supplied by a comparable method | An existing method covers the same decisions and procedure with equivalent scope. |
| Coverage | Custodian, Identity, Coordinator, Authorization, Access, Horizon, Execution, and Failure expose critical relationship obligations | Independent examples require missing decisions, or fields are persistently ambiguous or redundant. |
| Review benefit | The procedure improves detection and correction of consequential design omissions | A competent baseline achieves equivalent or better outcomes at comparable cost. |
| Transfer | The decisions remain useful across language and execution models | Benefits depend on Rust familiarity, one domain, or local memory safety alone. |
| Adoption cost | A bounded relationship review provides benefit worth its time and maintenance | Documentation, false alarms, training, or update costs outweigh observable gains. |

These hypotheses are distinct. Established ingredients do not prove the
integration is original; distinctness does not prove utility; useful local
contracts do not establish system-wide safety or liveness.

## Map prior art before claiming originality

Use the [selective literature ledger](literature.md) as a seed, not the result
of a systematic search. Follow a documented review/mapping protocol such as
[Kitchenham/Charters and Petersen et al.](literature.md#s47--structured-literature-review-and-mapping).
Record databases, queries, search dates, inclusion/exclusion criteria, duplicate
handling, backward/forward citation searches, and available full texts. Use
independent screening and extraction with disagreements retained and resolved;
report inaccessible sources rather than inferring their content.

Compare semantics and procedure, not matching field names. The extraction
matrix should cover the eight decisions, the unit of design, scenario and
counterexample use, relationship selection, realization mapping, evidence
boundaries, composition semantics, and evaluation evidence. Include RDD/CRC,
relational object analysis, architectural connectors, formal contracts,
concept design and synchronizations, DDD, security models, and architecture
review practices. Record the procedural classifications defined below and
separate enforcement or proof evidence; do not collapse both axes into an
ambiguous explicit/partial/absent score. Absence from examined text is not proof of historical
absence. Revise the contribution statement if a predecessor subsumes it.

Extend the seed comparisons with [methodology comparison](literature.md#s51--comparing-analysis-and-design-methodologies),
[relationship semantics](literature.md#s52--semantic-relationship-classification),
[DCI](literature.md#s53--data-context-and-interaction), and
[first-class language relationships](literature.md#s54--first-class-relationships-in-a-language).
Include the [2026 concept-design manuscripts](literature.md#s55--separating-individuals-from-modules)
as versioned preprints, distinct from verified final publications. Compare
their design procedures and operational assumptions, not just implementation
syntax. Finding a concern in an antecedent does not establish complete
coverage; failing to locate it does not establish ROO's exclusivity.

Repository discovery can locate tools and implementations. Record its queries,
dates, search limits, and relevant versions when used. Repository names,
popularity, and missing exact-name matches do not establish academic novelty.
Treat further supplied citations as leads until their identity, access level,
and claim-bearing passages have been checked. Multiple search summaries are
not independent screening or a reproducible mapping protocol.

### Make each comparison cell traceable

Build the obligation inventory from independent requirements, incidents,
counterexamples, and antecedent methods as well as ROO. Deduplicate synonymous
obligations and check coverage and counts against that frozen inventory.
Separate papers, method editions, specification tools, and implementations;
combining separation logic with RustBelt, or ReBAC with Zanzibar, can hide
different scopes and guarantees.

For each cell, retain the method/version, obligation, primary source and
page/section, access level, interpretation, assessor, and any disagreement.
Use these descriptive classifications rather than a quality ranking:

| Classification | Evidence required |
|---|---|
| Explicit procedural obligation | The examined procedure asks the designer to address it. This does not mean the resulting answer is correct. |
| Expressible or optional | The notation or practice can address it, without requiring that decision in every use. |
| Delegated | A named external technique or mechanism is required for it. |
| Not located | The specified examined material did not establish coverage; broader coverage remains unknown. |
| Not assessed | Access or interpretation is insufficient for classification. |
| Outside declared scope | The comparison identifies why the obligation is outside that work's stated purpose. |

Record enforcement or proof evidence in a separate column from procedural
coverage. Do not total these categories into a superiority score: an explicit
question in ROO and a proved property in a formal system are not equivalent
achievements. Independent assessors should check both ROO and its antecedents.

### Mapping the earlier Garcia comparison labels

The [Garcia comparison](garcia-lucena-comparison.md) used
labels for direct textual evidence about problems, artifacts, implementations,
and results. Those labels are not already procedural-coverage codes.

| Earlier label | Use in this agenda's codebook |
|---|---|
| Explicit | Re-read the cited passage. Code Explicit procedural obligation only if the procedure requires the decision; expressive capability is Expressible or optional, a required external mechanism is Delegated, and implementation/proof evidence belongs on its separate axis. |
| Partial | Split the overlapping and missing obligations, then code each from the passage. There is no automatic one-label translation; an unsplit cell remains Not assessed for pooled procedural comparison. |
| Not located | Retain Not located with the examined source boundaries. |
| Not assessed | Retain Not assessed, including access/interpretation limits. |
| Outside scope | Retain Outside declared scope with a source-based reason. |

Expressible/optional and Delegated were not separately coded in that earlier
matrix. Its cells must be re-extracted before combining coverage counts or
assessor agreement with this six-category protocol. This mapping does not
retroactively classify a textual result as a required design step.

## Operationalize the method and pilot its use

Freeze a method edition, worksheet, training materials, and scoring rubric.
Define a consequential omission independently of whether a participant uses
ROO terminology: for example, a retry can produce a duplicate effect, a stale
permission can authorize execution, or a claimed rollback excludes an external
commit. A nonempty field is not automatically correct or sufficient.

The [Relationship Contract](../docs/02-relationship-design.md) supplies
starting questions, not a validated scoring instrument. Assess whether a decision
names the participant/operation, boundary or trigger, effect, enforcement,
evidence, and assumptions relevant to its obligation. Test vague answers,
justified non-applicability, inconsistent fields, and invariants spanning
multiple relationships. Check assessor agreement and revise ambiguous criteria
before confirmatory use. More documented decisions are not necessarily better
decisions; count corrections to consequential omissions separately.

Published failure studies can inform independent scenario selection. For
example, [Yuan et al.](literature.md#s57--failure-handling-evidence) motivate
error-handling cases within their sampled systems. Preserve each study's
denominator and sampling limits. Such evidence does not validate ROO's field
partition, promise a defect-reduction percentage, or justify universal
failure-prevention and review-time claims.

[Concurrency bug characteristics](literature.md#s58--concurrency-bug-characteristics),
[TaxDC](literature.md#s59--distributed-concurrency-bugs),
[microservice fault cases](literature.md#s60--microservice-fault-cases), and
[architecture anti-pattern evidence](literature.md#s61--architecture-anti-pattern-evidence)
provide further case-selection leads. Record the table/section, unit of
analysis, denominator, overlapping categories, and comparison behind any
statistic used. Distinguish selected cases from population rates and
associations from causal effects. Do not infer a one-to-one mapping between
failure categories and contract fields.

Compare specific method versions and mechanisms. For example,
[aggregate guidance](literature.md#s62--aggregate-consistency-and-identity)
already addresses consistency boundaries and identity references, while
[AADL EMV2](literature.md#s64--architectural-fault-modeling) represents fault
propagation and recovery behavior. Test ROO's incremental value against these
actual capabilities rather than assuming entire traditions omit an obligation.

Pilot bounded tasks such as a document tree with reverse navigation, an order
workflow with external payment, and event subscriptions. Measure feasibility,
rubric agreement, task duration, and outcome variability; collect cases where
the vocabulary fails. Use those results for a power analysis and an appropriate
sample size, rather than inventing a participant count. Freeze the subsequent
protocol before its confirmatory data collection. Pilots are not confirmation.

## Compare against a competent baseline

Compare ROO with ordinary scenario-based design using ADRs, peer review, and
tests. Both groups receive identical requirements, implementation tools,
support, and time budgets; both may reason about ownership, permission, and
failure. ROO's intervention is its explicit record and procedure. Comparing it
with an intentionally incomplete class diagram would not test added value over
competent engineering practice. [ATAM](literature.md#s43--architecture-tradeoff-evaluation)
provides related scenario/tradeoff practices to consider when defining that
baseline, rather than an interchangeable relationship worksheet.

Distinguish two controls. Ordinary competent practice tests ROO's incremental
value. A checklist with the same obligation content, evidence requirements,
training time, and review budget tests the effect of grouping that content into
fields. Calling a checklist "generic" does not make it an independent baseline
if its questions were copied from ROO. Relevant threat analysis and adverse
scenarios must be available to both groups, not reserved for the treatment.

The [Porter/Votta/Basili inspection experiment](literature.md#s63--scenario-based-inspection)
provides a methodological precedent for separating scenario content from the
reading procedure. Its requirements-inspection result is not an expected ROO
effect size; architecture tasks and experienced practitioners require their
own assessment.

Randomize at the working-pair or team level, stratifying where feasible by
language, domain, and experience. Prefer parallel groups for the primary
comparison: teaching ROO can change how participants later perform a baseline
task, so method crossover has a learning carryover problem. Account for
task/team clustering in the analysis and keep the number of tasks practical.
Predefine permitted tool and AI assistance and record its actual use in both
groups. Equal training time and assessment of comprehension help expose
training differences.

Freeze observable requirements, extension tasks, and independent evaluation
scenarios before implementation. Hold out test instances, not requirements:
participants must know the obligations being assessed. Use independent
assessors, blinded to assignment where practical, and document when artifact
style reveals the method. Keep design omissions, implementation errors, and
disagreements distinguishable.

| Outcome | Operational measure | Interpretation limit |
|---|---|---|
| Primary: invariant preservation | Proportion of predefined, independently assessed critical scenarios whose required/forbidden outcomes hold | Scenario and invariant selection bound the claim. Report uncertainty and failures. |
| Review detection and false alarms | Recall of independently established defects and false-positive findings under a fixed review budget | Record severity and adjudication; raw finding count rewards noise. |
| Total effort | Training, design, review, implementation, rework, and contract maintenance time | Separate one-time learning cost from repeated use; do not count only coding. |
| Reader understanding | Correct answers to predefined lifecycle, authorization, freshness, and recovery questions | Use multiple readers and report agreement and experience. |
| Extension and operational costs | Time/correctness for a specified change; measured resource or coordination cost where relevant | Extra abstractions, locks, and documentation can shift rather than remove cost. |
| Subjective workload, if collected | A prespecified NASA-TLX administration and scoring procedure | Self-reported workload is not objective correctness or a direct measure of all cognitive demands. |

For workload, freeze the language, timing, and scoring variant and report the
six subscales. The [NASA instrument](literature.md#s48--subjective-workload)
uses weighted ratings; label any unweighted adaptation and assess its suitability
for these tasks. Do not infer engineering quality from its total score.

Predeclare the primary endpoint, analysis, exclusions, missing-data handling,
and stopping rule. Report effect sizes and uncertainty, including null and
adverse results. Compiler errors, line counts, `unsafe`, shared pointers, or
completed fields must not stand alone as quality scores. Rust expertise,
language/runtime, task difficulty, and team experience are potential
confounders, not explanations to add only after unfavorable results.

### Explore concern-diffusion measures without treating them as correctness

[Sant'Anna et al.'s joint assessment framework](literature.md#s70--concern-oriented-assessment-framework)
and [Garcia's agent/aspect studies](literature.md#s65--agents-and-separation-of-concerns)
provide precedents for connecting goals, questions, and structural metrics.
An exploratory ROO adaptation could measure how an independently defined
obligation is distributed across components and operations. Preserve the
original CDC/CDO definitions, including references to primary concern
implementations; counting files that contain a field name is not equivalent.
Predefine coding rules, generated-code handling, component size, assessor
agreement, and treatment of shared infrastructure. Report structural measures
alongside invariant outcomes, comprehension, effort, and maintenance: fewer
components do not automatically imply better separation or correctness.

The [proposed concern-diffusion protocol](roo-concern-diffusion-protocol.md)
now specifies CDC-R/CDO-R populations, a signature-only reference fixture,
distinct original-shading and lexical-transition profiles, and missing-data
rules. The [joint 2003 framework](literature.md#s70--concern-oriented-assessment-framework)
and thesis use different CDO wording; record the chosen interpretation rather
than silently reconciling it. A synthetic example in the protocol shows lower
counts accompanying an omitted permission check. Pilot coding reliability and
predictive value for actual evolution effort before interpreting these measures
as useful outcomes. The [focused comparison](garcia-lucena-comparison.md)
records the later complete chapter-8 retrieval (printed pp. 231–254), the
same four participants in both versions, fixed OA-first order, and remaining
metric/aggregation disagreements. The earlier access gap is historical;
complete retrieval does not remove the study-design limitations.

### Challenge scope and operational coverage

Include local lifecycle/trust cases and small tasks where the worksheet may
add little value. Test triage errors and the cost of unnecessary contracts;
do not document every possible pair or assume separate decisions require
separate runtime components. Compare transaction realizations against their
actual isolation, participating resources, and failure assumptions, using
[S66](literature.md#s66--distributed-transaction-guarantees) as a scope example.

Add held-out requirements for diagnostic correlation, bounded queues and
resource use, and behavior under overload where relevant. Existing
[tracing/backpressure standards](literature.md#s67--tracing-and-stream-backpressure)
motivate such cases, without proving that three new fields are needed.
Record whether a requirement can be expressed and enforced through the current
fields and scenario framing, needs an extension, or exposes a limitation.
Do not resolve every missing requirement by renaming it as an existing field.

## Ablate content and structure separately

The following are candidate experimental conditions, not adopted ROO editions
or a claim that the retained fields are more original. Freeze the exact set
and materials before recruitment; a count such as "ROO-4" is insufficient if
different drafts retain different fields.

| Candidate condition | Retained fields or intervention | Contrast it can address |
|---|---|---|
| Full contract | Custodian, Identity, Coordinator, Authorization, Access, Horizon, Execution, Failure | Reference condition for this experiment. |
| Without Execution and Failure | Custodian, Identity, Coordinator, Authorization, Access, Horizon | The joint effect of explicit Execution and Failure prompts in the tested tasks. |
| Four retained fields | Custodian, Identity, Authorization, Horizon | The joint effect of also omitting Coordinator and Access. |
| Identity and Horizon only | Identity, Horizon | A more strongly reduced set; not a recommended minimum contract. |
| Same content as a checklist | The full condition's obligation prompts without field grouping | Presentation/organization, if content and other treatment elements are matched. |

Keep the scenario, framing records, six-step procedure, requirements, evidence
expectations, and task budget constant where the intended intervention is the
field set. If a variant changes these too, it tests a treatment bundle. Do not
teach the full contract before measuring reduced conditions without accounting
for learned prompts; counterbalancing cannot make learned content disappear.
Do not confound a variant with one domain or a fixed task position. Balance
task assignment and estimate participant/team and task effects as the design
requires.

Removing several fields estimates a joint contrast, not each field's marginal
causal contribution. For individual attribution, plan a leave-one-field-out or
factorial contrast and examine interactions; descriptive overlap between
reported risks is not proof of redundancy. Even a single-field contrast is
conditional on the other retained prompts, task distribution, and training.

Deduplicate risk findings against independently adjudicated requirements.
Report severity and missed critical risks as well as recall, false alarms,
effort, and maintenance. A risks-per-minute ratio can favor many trivial
findings; retain the underlying outcomes and an explicit treatment of zero
counts. A ratio of group means is not generally the mean of individual ratios.

### Define what a result could justify

Non-significance does not establish equivalence. To support simplification,
predefine a meaningful equivalence or non-inferiority margin, plan sample size
for that question, and report compatible intervals and cost outcomes. See
[Lakens, 2017](literature.md#s49--equivalence-testing). A wide interval can leave
the question unresolved. An observed advantage of eight over four fields
does not establish that every omitted field is necessary in every domain.

Plan power before collection using justified effect/precision targets and
pilot uncertainty. Do not diagnose an inconclusive result using "observed
power" computed from that result's effect estimate; see
[Hoenig and Heisey, 2001](literature.md#s50--power-and-inconclusive-results).
Choose analysis for the outcome distribution and assignment/clustering, rather
than listing interchangeable tests. Prespecify multiplicity handling for the
actual confirmatory contrasts and distinguish exploratory analysis.

Hypothetical scenarios can explain interpretations, but they are not data.
Any numerical simulation needs a documented generating model, assumptions,
code, random seed, repetitions, and reproducible analysis. Means and marginal
standard deviations alone do not determine paired-test results without the
within-pair information. Label hypothetical numbers in every table/figure and
caption that can circulate independently. Such material cannot support a
recommendation to remove fields or a claim of observed productivity gains.

## Check composition, replication, and adoption

For a claimed system property, model interactions between contracts and state
their shared assumptions. A local invariant can hold while contracts conflict
or recovery never progresses. Alloy or another formal method can investigate
specific properties; bounded exploration does not certify every execution.
Authorization freshness, transaction boundaries, and independent external
effects need explicit models or scoped implementation evidence.

After feasibility and comparison work, conduct field cases with independent
engineers and varied domains, using an evidence chain and the reporting
guidance of [Runeson and Höst](literature.md#s46--software-engineering-case-studies).
Study where teams select relationships, update contracts, abandon fields, and
resolve disagreements. Replicate across languages and organizations; avoid
generalizing a single payments laboratory to all software design.

Complement the field contrasts with planned tests of the counterexample step,
evidence recording, and extra review time. Investigate combining or omitting
fields and report consequences. Machine-readable contracts or tooling should
follow demonstrated needs; a generator would not establish the correctness of
an elicited policy.

[Industrial code review evidence](literature.md#s68--industrial-code-review-practice)
and [architectural-language adoption needs](literature.md#s69--industry-needs-from-architectural-languages)
motivate measuring burden and usability rather than declaring manual use
impossible. If a linter or executable-counterexample requirement is prototyped,
evaluate it as a separate intervention. Measure stale evidence, false alarms,
copied answers, bypasses, maintenance cost, and defects actually detected.
Syntactic presence cannot validate a policy or the relevance of a linked test.
Record whether counterexamples are reasoning traces, formal models, executable
tests, or unverified scenarios; assess the benefit and cost of each form.

### Evaluate adoption cost and assistance

The [adoption analysis](historical-paradigms-and-ai-revival.md) motivates a
prospective field pilot. Define an eligible relationship change before counting
compliance. Record how many such changes occur, receive substantive review,
reuse a still-applicable contract, or leave stale decisions. Document inactivity,
project completion, withdrawal, and deliberate discontinuation separately.
Few records or no edits to an unchanged decision cannot establish abandonment.
Predefine follow-up intervals and discontinuation criteria, confirm reasons
with participants, and report missing observations and project activity.

Measure authoring, review, correction, training, and maintenance time as well
as delivery delay. Assess comprehension and defect detection against independent
requirements and adverse scenarios; copied text, record counts, test coverage,
and CDC/CDO/CDLOC adaptations are diagnostics, not benefit by themselves.
Count false alarms, missed consequential relationships, bypasses, and failures
to update contracts after behavior changes. Report how those cases were found.

Separate the method from its assistance. If a pilot supports the cost, compare
competent practice and ROO both with and without the same AI support, balancing
expertise, requirements, time, and review access. Freeze model/version, prompts,
available context, retries, and actual tool use. Evaluate any added linter
separately, including wrapper/SDK calls it misses and correctly suppressed
warnings. [TestGen-LLM](literature.md#s73--filtered-test-generation-with-llms)
offers a filtering precedent, not evidence that generated counterexamples are
correct. Preserve an independent expected-behavior oracle in every condition.

Agree with the participating team on acceptable effort and meaningful outcome
criteria before the pilot; no universal percentage or review-time target is
established here. Revise, narrow, or discontinue the intervention when its
observed cost exceeds that budget without the predefined benefit. Report that
outcome alongside successful adoption.

### Compare design assistance and role decomposition

The [assisted design protocol](assisted-design-protocol.md) proposes two distinct
comparisons. First, compare assistance from requirements before implementation
with review that reconstructs decisions from existing code. Hold the underlying
requirements and target outcomes fixed, define the information available at
each stage, and account for downstream correction cost. Recovered behavior
must not silently become the expected policy. Include competent unassisted
design as a baseline; more plausible prose is not an architecture outcome.

Second, compare one assistant with staged roles and, if feasible, multiple
agents. Match requirements, available context, model/version, tools, expected
behavior oracle, and total model/tool budget. Record intentional differences
in information sharing, parallelism, context separation, and retry allocation.
If a condition receives more resources, report that comparison separately.
Include contract-structure and role ablations so any gain is not automatically
attributed to ROO or to agent count.

The [upstream-design comparison](upstream-design-comparison.md) adds concrete
comparators: specification/interaction-contract planning (S80–S81), architectural
agent handoffs (S82–S83), and formal-specification-assisted test generation (S84).
Choose a feasible subset for a budgeted pilot and justify exclusions; a weak
prompt that skips design cannot stand for existing practice. Compare a competent
planning workflow with and without the ROO record, holding its tools and access
fixed. Separately vary the counterexample step and role allocation. Use an
independent, requirement-derived rubric that accepts valid alternative designs
without rewarding ROO terminology.

For a procedural comparison, implement the selected documented procedures with
the same model and tool access where feasible. A reproduction of an older
paper's configuration is a distinct study. For product comparisons, freeze
versions, enabled features, and actual check execution; a capability appearing
in vendor documentation does not show that it ran on a given task. Report
unmatched capabilities and budget differences as comparisons of complete
workflows, rather than isolated effects of ROO. Any formal-intermediate-language
extension needs its own semantics and translation validation.

The [focused MAAD audit](maad-critical-review.md) reinforces the need to check
evaluation artifacts themselves. Reconcile reported counts with unique
requirements and findings, audit parsing and denominators, and independently
adjudicate mismatch labels. Separate an evaluator's judgment from verified
behavior and preserve source-version conflicts. A current-model procedural
comparison and reproduction of the original MAAD study are distinct; the
comparison unit must be shared relationship decisions rather than unequal
whole-system deliverables.

Predefine expert-assessed missing/incorrect obligations, valid counterexamples,
irrelevant warnings, comprehension, and behavior against held-out adverse
scenarios derived from shared requirements. Check model and test assertions
independently of the generated realization. Record error agreement between
roles, unresolved disagreements, failed checks, and integration effort; role
labels and majority agreement do not establish independent assessment.

For broad discovery, freeze an eligible boundary set and supported languages,
configuration, wrappers, and dynamic behavior. Evaluate misses as well as
reported candidates against an independently assessed reference, recording
uncertainty and assessor disagreement. Distinguish PR coverage from relationship
detection, substantive review, and verified outcomes. Measure total cost and
human review time across consequential local, persistence, trust, and remote
cases; do not assign autonomy or a field subset from physical location alone.

### Pilot MAAD with and without ROO

A prospective study can compare a competent MAAD-adapted four-role workflow
with and without the complete ROO procedure. Freeze task requirements,
scenarios, independent oracles, model/tool access, and equal resource caps
before either condition runs. Use matched-content controls and report design,
implementation, evaluation, correction, and maintenance costs separately.
A feasibility sample cannot establish efficacy or equivalence.

The existing experimental packages, cases, candidate keys, cost journals, and
launch gates remain separately preserved. They are not dependencies of this
public research synthesis and are not revised or executed by it. Preparing an
agenda is neither a live-provider calibration nor an empirical result. The
[source-level MAAD review](maad-critical-review.md) motivates the comparison
and distinguishes inspected artifacts from an executed replication.

### Evaluate obligations and verification authority

The [expanded dossier review](upstream-landscape-review.md) adds a comparison
with guarded external evaluation (S90), ADD-guided assistance (S94), and
distributed modeling/checker workflows (S95). Select feasible procedures and
declare their actual capabilities; a formal-model baseline cannot be represented
by an assistant that merely emits notation. Separate record structure,
counterexample challenge, and verification authority as experimental factors.
Keep model, context, tool access, and total budget matched where feasible;
otherwise report a comparison of complete workflows rather than a ROO effect.

Freeze the requirement-derived expected policy, observation/model mapping, and
held-out checks independently of the generated realization. In the benchmark,
record who may propose changes and who may accept them; preserve the original
oracle and report deviations. Check the evaluator's policy interpretation as
well as the design: a deterministic rejection may reflect a wrong mapping,
an overly restrictive policy, or a real violation. Include valid alternative
designs and cases where a check should not reject them. Agreement between
agents does not establish correctness or independent verification.

Define obligations at the logical-attempt level. Legitimate retries may produce
multiple requests; specify which business effect must occur at most once and
under what retention, payload, and provider assumptions. For Horizon, define
timestamp meaning, validity, permissible staleness, clock assumptions, and
revocation. For recovery, distinguish a bounded deadline under a fault envelope
from unbounded eventual progress with explicit environment/fairness assumptions.
A single successful witness is not recovery of every accepted attempt. Report
violations, inconclusive pending attempts, vacuous checks, missed violations,
and false alarms against an independent reference; assertion counts are not
coverage. See [S96–S97](literature.md#s96--assertion-encounters-and-existential-witnesses).

Measure policy elicitation, model mapping, instrumentation, domain review,
correction, and maintenance effort alongside design and behavior outcomes.
Assess translation correctness separately from checker results; a field name
does not determine a model or a unique implementation. These are evaluation
requirements, not an implemented generator or new empirical result.

Use [FEDS, S98](literature.md#s98--evaluation-purpose-context-and-timing) to state
the evaluated artifact (method, contract, model, or implementation), the episode's
purpose and context, and its timing separately. A formative challenge to one
design is not a summative evaluation of ROO. Any proposed reduction of human
or assistant bias also needs its own outcome assessment; adversarial roles
are not established debiasing interventions for this method.

## Reproducible evidence package

Publish the protocol, literature extraction matrix, frozen method/materials,
requirements, scenarios, toolchain versions, exact candidate revisions,
commands, assessor rubric, disagreement records, and analysis sufficient for
reproduction. Include failed attempts, deviations, uncertainty, training and
maintenance costs, and authors' involvement. Obtain appropriate participant
consent and publication rights, and use synthetic or properly de-identified
data. Preserve source hashes and distinguish archived receipts from later
method revisions.

[Design Science Research](literature.md#s44--design-science-research) and its
[methodology](literature.md#s45--a-dsr-process) can frame artifact development,
demonstration, and evaluation. The next claim should follow the evidence:
retain, narrow, revise, or reject the candidate contribution as the comparisons
and counterexamples require.
