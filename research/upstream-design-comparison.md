# ROO and AI-assisted design before implementation

**Status:** selective primary-source comparison, checked on **2026-10-12**.
This review informs ROO's proposed contribution and evaluation; it does not
establish market completeness, an equivalent product, or method effectiveness.
ROO's [assisted design workflow](assisted-design-protocol.md) remains a proposal.

The supplied argument identifies a useful research target: expose consequential
relationship obligations before generating an implementation. Its assertion
that this space is empty is contradicted by documented workflows and published
research. Architectural planning, structured intermediate artifacts, specialized
agents, interaction contracts, and counterexample-oriented testing have
antecedents. A distinct ROO contribution must survive comparison with them.

## Scope and evidence rules

Targeted searches covered specification-driven tools, architectural agent
workflows, the named LM2Alloy study, and selected vendors named in the supplied
argument. Sources below were inspected at the locations recorded in the
[ledger, S80–S88](literature.md#ai-assisted-design-and-current-tooling).
Vendor documentation describes supported or advertised workflows; this review
did not run those products. Paper results are authors' reports, with the stated
access and evaluation limits. Neither kind is an independent ROO experiment.

This is not a survey of every vendor, extension, configuration, or private
system. Devin, Windsurf, Atlassian Intelligence, Snyk, and Qodo were not assessed
sufficiently to classify their capabilities here. An inaccessible page or an
omitted feature cannot establish absence. Exact worksheet names are also an
inadequate test of semantic equivalence.

## Comparisons that constrain the claim

| Source and inspected location | Documented overlap | What remains unresolved for ROO |
|---|---|---|
| [Kiro specs](https://kiro.dev/docs/specs/), Design phase; [correctness](https://kiro.dev/docs/specs/correctness/), Design phase and limitations (S80) | Requirements precede architecture, error-handling, and testing plans. Properties are extracted during design and exercised with generated inputs and shrinking; property testing is IDE-only and optional by default. | This already combines design artifacts and attempts to expose violations. Product documentation does not establish either ROO equivalence or comparative defect detection. Passing generated properties is not a proof. |
| [GitHub Spec Kit](https://github.com/github/spec-kit/blob/main/docs/guides/contract-driven-development.md), contract contents and workflow (S81) | Interaction contracts precede dependent implementation and cover effects, errors, idempotency, ordering, retries/timeouts, and verification. The scope includes boundaries within a process or repository. | This is a close procedural comparison. Contract ownership is not automatically runtime custody. Check whether ROO changes substantive decisions or merely reorganizes existing guidance. |
| [MetaGPT](https://arxiv.org/html/2308.00352v7), §§3.1–3.3 (S82) | A product manager hands structured requirements to an architect, followed by task planning, engineering, and QA. Structured design/interface artifacts and executable feedback are part of the workflow. | Specialized agents and design before coding are prior art. The reported workflow does not establish that roles make independent errors or that ROO adds useful relationship analysis. |
| [MAAD](https://arxiv.org/html/2507.21382v1), §§3.2, 5.1.3, 7 (S83) | Analyst, Modeler, Designer, and Evaluator roles produce architectural views, connector/behavioral contracts, alternatives, and requirements-mismatch reports. | Direct architectural assistance is a close antecedent. Case-based results and subjective or model-generated assessments require caution; they do not validate every generated design or ROO's incremental benefit. |
| [LM2Alloy / LLM2Alloy](https://arxiv.org/html/2607.18555v1), §§III–V (S84) | Separate documentation/code inputs generate Alloy specifications, then executable pytest tests for two Python libraries. | This contradicts the claim that such work cannot reach ordinary test execution. The reported suspected defect lacks maintainer confirmation in the paper; generality, workflow integration, and translation correctness remain unestablished. |
| [Cursor Plan Mode](https://cursor.com/docs/agent/plan-mode), use cases; [Claude Code best practices](https://code.claude.com/docs/en/best-practices), exploration/planning/verification (S85) | Cursor explicitly includes architectural decisions. Claude documents exploration before implementation and executable checks. | The categorical claim that coding agents only plan syntax is unsupported. Neither page measures coverage of ROO obligations or establishes reliable architecture reasoning. |
| [CodeRabbit Plan](https://www.coderabbit.ai/plan), workflow and FAQ (S86) | Editable, codebase-informed plans are reviewed before handoff to a coding agent. | The brand cannot be classified as exclusively downstream. This product description does not demonstrate correct concurrency, recovery, or other relationship decisions. |
| [ChatPRD template](https://www.chatprd.ai/templates/prd-product-requirement-document-template), Technical Requirements (S87) | The template requests architecture, component interactions, security, performance, and integrations. | A requirements-tool category is not evidence of technical incapacity. A template also does not demonstrate that generated answers correctly handle locks, partitions, or idempotency. |

These are overlaps in purpose and procedure, not a finding that any one source
implements the complete ROO proposal. Conversely, distributing overlap across
several sources does not make integration automatically novel. A comparison
must examine the strongest individual methods and the ordinary combinations
available to practitioners.

The later [expanded dossier review](upstream-landscape-review.md) extends this
comparison with ADD-guided assistance, Architecture-0's guarded evaluation,
and P/PeasyAI's distributed models and checker workflow (S89–S99). These are
relevant upstream and verification antecedents; formal design work cannot be
confined to memory-safety proofs. Recorded access limits and documented
capabilities still differ from executed products or a ROO comparison experiment.

## Corrections to the proposed positioning

The ROO record is a compact structure for eliciting and communicating decisions.
It currently has no formal grammar, composition/refinement semantics, or
verified translation into code. Calling it a formal intermediate representation
or mathematically precise is premature. The eight fields are proposed review
distinctions; their independence, minimality, and completeness are unvalidated.
Existing [DDD](literature.md#s06--domain-driven-design) and
[formal contract](literature.md#s34--contracts-for-system-design) traditions
cannot be dismissed from book length or notation style.

LM2Alloy's stated pipeline records test execution, not an Alloy Analyzer
verification stage. An integration with a model checker would need recorded
commands, scopes, outcomes, and independent policy-to-model checks.
Generated formal notation and passing tests do not establish a correct policy.
The supplied literacy-rate claim and universal Git/PR-integration barrier have
no traceable primary support in this review. See S84 for its exploratory scope
and access notes; neither claim is adopted.

Rust's guarantees also need accurate scope. The official
[`Send`/`Sync` explanation](https://doc.rust-lang.org/book/ch16-04-extensible-concurrency-sync-and-send.html)
describes checked transfer and sharing across threads; they are not confined
to a heap-only description (S88). Correct unsafe implementations are part of
the safety assumptions. These mechanisms do not, by themselves, establish a
business invariant, remote-effect atomicity, or a compensation policy. Prior
agent commentary is not a proof about the language.

Claims about why no company built a competing system, the industry's exclusive
benchmark priorities, inevitable production collapse, or a universal market
transition were not adopted. They need their own evidence. The BIM/CAD analogy
can motivate an interface idea, but supplies no semantics or validation.

## Contribution to investigate

The defensible candidate is a selected relationship's **Custodian, Identity,
Coordinator, Authorization, Access, Horizon, Execution, and Failure** decisions,
used with the canonical six-step procedure to compare realizations, challenge
them, and record scoped evidence. The question is whether this particular
integration exposes consequential omissions or conflicts more reliably, and
at an acceptable total cost, than competent existing design and assistance.

ROO could be used inside an existing specification, planning, or review workflow.
Such an integration would be an implementation proposal to test. It is not
evidence that ROO invented upstream design, that an identical system is absent
from the market, or that a new agent platform is already available here.

## Evaluation changes implied by the comparison

Compare substantive obligations and observed outcomes rather than matching
field names or counting artifacts. For example, ask every condition to address
the same requirement: after a payment succeeds and its reply is lost, the
attempt must remain recoverable and retries must respect the specified
deduplication policy. Include consequential local and authorization cases too.
Assess mechanisms, assumptions, missing obligations, and adverse behavior
against an independent rubric; do not reward use of ROO vocabulary.

The [evaluation agenda](agenda-revised-2026-10-12.md#compare-design-assistance-and-role-decomposition)
now includes competent specification/contract planning and architectural-agent
comparisons. Start with a budgeted pilot rather than an infeasible comparison
of every product. Compare the chosen workflow with and without the ROO record;
separately ablate its counterexample step and agent roles. Record tool versions,
configuration, context, actual checks, failures, integration effort, and total
cost. A null result, equivalence, or a cheaper existing workflow must be a
reportable outcome.
