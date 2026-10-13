# MAAD and ROO: a critical comparison

**Status:** selective source and artifact audit, **2026-10-12**. Four native
delegates were configured as GPT-6 Luna with maximum effort to examine the
supplied comparison from different perspectives. The integrator checked the
material source, arithmetic, and artifact findings before incorporating them.
Agreement between these reviewers is not independent empirical validation.

**Conclusion:** retain MAAD as an important adjacent comparator; substantially
revise the supplied argument. It neither establishes MAAD's general inadequacy
nor validates ROO's effectiveness, drift resistance, or distributed guarantees.

## Sources and inspection boundaries

The reviewed paper is [arXiv:2507.21382v1](https://arxiv.org/html/2507.21382v1).
Selected method, results, discussion, and validity passages were inspected
(§§3–7). Its [metadata](https://arxiv.org/abs/2507.21382v1) identifies a July 2025
journal submission. The earlier FSE IVR vision paper is a separate publication
(§1, reference 12); the manuscript's journal-template header is not publication
confirmation.

The author repository is mutable. Two reviewer-selected 2025 snapshots below
identify the original paper in their READMEs; neither is pinned by the paper.
The [current README at observed commit 944e711](https://github.com/RuiyinL/MAAD/blob/944e7113d1c6992cb2bba186df945a2ea73db68a/readme.md)
instead identifies a renamed 2026 paper. This audit does not combine its later
claims with the 2025 experiments or assess the newer paper in full.

No framework, generated application, benchmark, or provider inference was run
to reproduce MAAD. Source retrieval, static inspection, and local arithmetic
are distinct from reproducing its experiments. Interview transcripts were not
independently recoded. ROO was assessed against its current canonical documents,
not against the supplied essay's stronger claims.

## Corrections to the supplied interpretation

MAAD specifies behavioral contracts, error handling, reliability constraints,
and ATAM/mismatch reports (§3.2). Its views include behavioral diagrams, and
its paper describes revision feedback (§3.3). The SFS comparison and interviews
are different evidence components (§§4–5). These reported capabilities and
findings do not establish implemented correctness. [Primary paper](https://arxiv.org/html/2507.21382v1).

| Supplied claim | Disposition for ROO documentation |
|---|---|
| MAAD is the most direct benchmark for exactly the same problem. | Treat it as a close architectural-assistance antecedent. A system-wide architecture workflow and a selected-relationship procedure have different units and outputs; direct superiority needs a shared task and rubric. |
| Relationship semantics are only signatures, static boxes, or syntax. | Correct against §3.2.3 and the behavioral views. Distinguish a question a workflow asks, an artifact's expressive capacity, a proposed mechanism, and behavior actually checked. |
| The Evaluator only agrees passively or operates by consensus. | The report types and feedback description contradict that caricature. They still need external assessment; producing an evaluation narrative is not implementation verification. |
| The generated prototype is demonstrably executable. | A requested deliverable is not an execution receipt. The inspected scaffold and execution path below provide narrower evidence. |
| Equal mismatch rates prove generic architectural RAG is useless. | Retain the reported equality for this comparison (§5.2). An unchanged count cannot establish unchanged findings, zero qualitative benefit, or a domain-independent causal conclusion. |
| DeepSeek's runtime detail caused severe business-rule failures. | Separate the observed association from the proposed explanation. Neither the causal mechanism nor the added severity label is established by the cited comparison. |
| Interviews prove conventional architecture ignores custody, concurrency, and failure. | A criticism of omitted detail in generated artifacts cannot diagnose an entire tradition or show that ROO would prevent the omissions. Preserve favorable feedback and criticisms together. |
| MAAD formally proves that MetaGPT and Devin are superficial. | Restrict the comparison to its tested outputs. Devin is not its comparator (§4.2.2); a qualitative comparison supplies no such formal result. |
| Markdown gives ROO high resistance to drift. | Compactness is an artifact property, not an adoption or maintenance outcome. Measure stale decisions and update cost under changes. |
| ROO replaces ATAM/UML with guaranteed falsification. | The canonical counterexample step permits reasoning, models, or execution. It has no completeness or general safety/progress guarantee. |

ATAM should also be represented fairly. The [SEI description](https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/)
uses stakeholder scenarios to examine quality goals, risks, sensitivity points,
and trade-offs. An LLM-generated ATAM report is not automatically equivalent
to that stakeholder evaluation. Neither process should be dismissed as passive
consensus merely because its evidence includes prose.

## The percentage error originates in the paper

The manuscript itself calls the difference a 66% alignment drop in §6.2; the
supplied essay repeats it. The section also calls MetaGPT single-agent despite
its multi-agent description in §4.2.2. Both require qualification. [Paper, §§4.2.2, 5.3, 6.2](https://arxiv.org/html/2507.21382v1).

The submitted numbers can be checked independently of either interpretation:

| Quantity | Calculation | Meaning |
|---|---|---|
| Reported counts | 6 versus 10 | Four additional reported mismatches. |
| Relative increase | `(10 - 6) / 6` | **66.7% more mismatches**, not 66% less compliance. |
| Rates with the package's denominator | `6 / 32 = 0.1875`; `10 / 32 = 0.3125` | An increase of **12.5 percentage points**. |
| Hypothetical complement | `1 - 0.1875` versus `1 - 0.3125` | A 15.4% relative decline **if** this complement were defined as an alignment score. It is not an independently measured compliance outcome. |

A mismatch count need not be a count of unique failed requirements. Before
using its complement, define classification, overlapping requirements, multiple
findings per requirement, severity, and assessor reliability. A numerical footer
must be reconciled with its underlying findings before it becomes a study score.

## Artifact conflicts and implementation scope

The numerical checks use commit
`59fc5f9cc399c8aaa9d0bf5f68988365fa01d3e9`, a dated snapshot selected by the
reviewer. Its [README](https://github.com/RuiyinL/MAAD/blob/59fc5f9cc399c8aaa9d0bf5f68988365fa01d3e9/readme.md#L1-L3)
identifies the original paper. This connection supports a reproducible artifact
audit, not proof that the authors used these exact bytes for v1.

| Pinned file | Independently checked conflict or calculation |
|---|---|
| [GPT-4o without RAG, lines 34–36](https://github.com/RuiyinL/MAAD/blob/59fc5f9cc399c8aaa9d0bf5f68988365fa01d3e9/MAAD%20artifacts/GPT-4o/GPT-4o_noRAG/SFS/Evaluator/MAR.txt#L34-L36) | Count 6, denominator 32, reported rate 0.3; the arithmetic yields 0.1875. |
| [Llama 3.3 with RAG, lines 3–36](https://github.com/RuiyinL/MAAD/blob/59fc5f9cc399c8aaa9d0bf5f68988365fa01d3e9/MAAD%20artifacts/Llama3.3-70B-instruct/Llama3.3_RAG/SFS/Evaluator/MAR.txt#L3-L36) | Six labeled findings, but summary count 0 and rate 0.0. |
| [GPT-4o with RAG, lines 34–36](https://github.com/RuiyinL/MAAD/blob/59fc5f9cc399c8aaa9d0bf5f68988365fa01d3e9/MAAD%20artifacts/GPT-4o/GPT-4o_RAG/SFS/Evaluator/MAR.txt#L34-L36) | Count 6, denominator 32, and rate 0.1875 agree arithmetically. |
| [DeepSeek-R1 with RAG, lines 50–52](https://github.com/RuiyinL/MAAD/blob/59fc5f9cc399c8aaa9d0bf5f68988365fa01d3e9/MAAD%20artifacts/DeepSeek-R1/DeepSeek-R1_RAG/SFS/Evaluator/MAR.txt#L50-L52) | Count 10, denominator 32, and reported rounded rate 0.31. |

A separate source/scaffold check uses reviewer-selected commit
`a07cb4fff434553cdf4bbd4265b78919c8c93472`. The
[launcher](https://github.com/RuiyinL/MAAD/blob/a07cb4fff434553cdf4bbd4265b78919c8c93472/scripts/agents/run.py#L1-L14)
invokes the four scripts sequentially. The examined
[evaluator path](https://github.com/RuiyinL/MAAD/blob/a07cb4fff434553cdf4bbd4265b78919c8c93472/scripts/agents/evaluator.py#L52-L77)
writes reports without routing findings back for automatic redesign. The
[SFS scaffold](https://github.com/RuiyinL/MAAD/blob/a07cb4fff434553cdf4bbd4265b78919c8c93472/MAAD%20artifacts/GPT-4o/GPT-4o_RAG/SFS/Designer/AD.txt#L100-L153)
contains unimplemented method bodies. These observations concern the inspected
paths, not every version or a demonstrated inability to build such a loop.

The artifacts limit confidence in uncritically reused mismatch scores. They
do not show fabrication, establish the paper's exact execution provenance,
or supply evidence that ROO performs better. Source inspection is also no
substitute for running and assessing a reproducible system.

## Symmetric comparison and candidate contribution

Use the same distinctions for both approaches:

| Question | Fair comparison rule |
|---|---|
| What is the unit? | Compare relationship decisions within a shared architecture task. Do not penalize a complete architecture package for having more deliverables than a worksheet. |
| What must be asked? | ROO explicitly asks eight relationship questions. Assess whether the comparator elicits the same substantive decisions under the supplied requirements; unassessed coverage is not inability. |
| What can be expressed? | Prose, diagrams, and contracts can all state relevant decisions. Expressibility does not show systematic elicitation or enforcement. |
| What was implemented and checked? | Trace an obligation to its mechanism and actual evidence. Apply the same execution, oracle, and model-scope standards in both conditions. |
| What resists drift? | Assess correct updates after changed requirements and later use. Record length, artifact count, and confidence are insufficient proxies. |

The candidate ROO contribution remains its integration of **Custodian, Identity,
Coordinator, Authorization, Access, Horizon, Execution, and Failure** in the
[six-step procedure](../docs/02-relationship-design.md#23-the-six-step-decision-procedure).
It is a language-independent elicitation and review artifact. It is not an
implemented Boundary IR, a uniquely correct mechanism mapping, a formal proof,
or a demonstrated replacement for system-level architectural evaluation.

## A feasible evaluation proposal

Select a competent specification/architecture workflow, using MAAD or ADD as
a documented procedural reference. For a current-model comparison, hold its
roles, model/version, requirements, domain context, tools, oracle access, retries,
and total budget fixed. Reproducing the original MAAD configuration is a
separate study; a modern adaptation must be labeled as such.

A feasibility pilot can separate two factors: adding the eight-field record
and adding an explicit counterexample challenge. A record-only condition is
an ablation, not the complete ROO procedure. Give all conditions the same policy
and verification facilities. Add a matched-content checklist control if feasible
to distinguish organization from extra guidance. Keep verification authority
fixed initially rather than attributing access to a stronger checker to ROO.

Use synthetic cases with declared requirements, including lost payment replies,
revocable local permission, and stale observations. Define valid alternatives
and expected outcomes before seeing generated designs. Assess missed and
incorrect obligations, valid challenges, false alarms, observed behavior,
comprehension, and total elicitation/review/maintenance cost. Keep policy questions
separate from defects; preserve assessor disagreement and inconclusive outcomes.

Reconcile every reported count with findings and unique requirement identifiers.
Independently audit parsing, denominators, duplicate findings, and severity.
Do not use another generated report as unquestioned ground truth. For behavior,
distinguish at-most-one business effect from legitimate repeated requests;
state progress deadlines or fairness assumptions and the observation scope.

A controlled requirement change can study record maintenance. Actual adoption,
long-term drift, and engineering benefit require further follow-up. Preregister
the meaningful outcome and analysis after establishing feasibility; choose
confirmatory sample size from justified variability and power assumptions.
No-benefit, higher-cost, and inconclusive results remain valid findings. See
the [evaluation agenda](agenda-revised-2026-10-12.md#evaluate-obligations-and-verification-authority).

A paired feasibility study could turn these requirements into explicit cases,
independent reference criteria, matched resource caps, controlled maintenance,
and total-cost accounting. The experimental packages remain separately
preserved; this source-level critique neither changes nor executes them.

## Review participation and provenance

This is an AI-assisted documentary review. Separate agent roles do not make it
independent human validation. Its source dates and reviewer-selected public
commits remain as recorded above; they are not execution receipts for MAAD.
Detailed working snapshots and task records remain separately preserved.
The recoverable public evidence is the paper and pinned source links, not a
claim that a temporary review directory is a replication package.
