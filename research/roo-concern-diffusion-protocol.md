# Adapting concern diffusion metrics to ROO evaluation

**Status: research proposal, not a validated instrument or a new ROO edition.**
CDC, CDO, and CDLOC can help describe where a software obligation appears in
an implementation. They cannot establish whether that obligation is correct,
whether its placement is appropriate, or whether ROO improves engineering.
This protocol proposes an explicit adaptation for a pilot, alongside independent
behavioral outcomes and effort measures. The [comparison with Garcia and Lucena](garcia-lucena-comparison.md)
and [primary-source ledger](literature.md#s70--concern-oriented-assessment-framework)
provide the source context.

## Original measures and proposed variants

Garcia's thesis, chapter 6, section 6.4.1, printed pages 198–200 (PDF pp. 12–14
of the 22-page official chapter-6 partition), defines concern diffusion across
primary components and their accessors, primary operations and their accessors,
and transitions between concern-shaded and unshaded code. The [joint assessment
framework](https://sol.sbc.org.br/index.php/sbes/article/download/23850/23678)
by Cláudio Sant’Anna, Alessandro Garcia, Christina Chavez, Carlos Lucena, and
Arndt von Staa is an earlier source, not a ROO contribution. The definitions
include references and declarations, not just implementations or filenames.
CDLOC includes shading and block-merging judgments, including blocks that could
be consecutive despite their present separation. A lexical transition counter
is therefore a distinct variant. The institutional [chapter 6](https://www.maxwell.vrac.puc-rio.br/5181/5181_7.PDF)
and the [focused comparison](garcia-lucena-comparison.md#what-chapter-8-currently-supports)
provide the original metric context and chapter-8 results and limits.
The CDO wording difference remains explicit rather than silently reconciled.

| Measure | Proposed use in the pilot | Required qualification |
|---|---|---|
| CDC-R | Distinct logical components implementing or directly referring to an independently defined obligation | Component mapping and reference rules are adaptations, especially outside Java/AspectJ. |
| CDO-R | Distinct source operations implementing or directly referring to that obligation | Include declared operation kinds consistently; do not count runtime invocations. |
| CDLOC-G profile | Apply the original shading/merging rules with recorded adjudication | Ambiguous boundaries and possible reordering need an explicit codebook; comparability is not established merely by retaining the name. |
| CDLOC-Lex | Count adjacent label changes in frozen source order under the convention below | A proposed reproducible diagnostic, not an equivalent implementation of original CDLOC. |

Keep the G and Lex profiles separate. Never compare one treatment measured
with one profile against another measured with a different profile.

## Define obligations independently of treatment

Start from observable requirements: for example, an approval must satisfy its
caller policy at execution, or a retry must not silently duplicate a committed
reservation. These are obligations, not requirements to fill an Authorization
or Failure cell. One obligation may involve several fields, and one field may
refer to several obligations. Overlapping concerns are permitted.

Freeze the obligation catalogue and applicable scenarios before inspecting
the treatment's worksheet or coding its implementation. Participants know
the requirements; held-out evaluation instances test those requirements.
Exclude contract prose and test files from the primary production-code
diffusion universe. Measure documentation and tests separately. A link from
a contract to a test is traceability evidence, not a component count.

## Freeze the implementation universe

Record source revision, build configuration, language, dependencies, inclusion
rules, and logical identifiers for each snapshot. For a first pilot, compare
implementations within the same language and task. Cross-language values
should remain descriptive until measurement invariance has been assessed.

For Java, components can be declared classes, interfaces, and aspects; operations
can include methods, constructors, and advice. For Rust, propose one logical
type component across its implementation blocks, a trait component for its
declared interface, and a module component for free functions. This mapping is
a pilot decision, not a claim that a Rust type equals an AspectJ aspect.
Distinct trait declarations and implementations retain distinct operation IDs.
Inline closures belong to their enclosing source operation unless the frozen
codebook deliberately defines another policy. Compiler-generated state
machines are not extra source operations.

Separate production code, handwritten adapters, generated code, framework
internals, tests, and configuration. Include handwritten adapters in the
primary scope; record excluded mechanisms and why they matter. An obligation
implemented entirely by an excluded service can have zero counted application
components without being absent. Conversely, no implementation of a required
obligation is an outcome problem, not evidence of excellent localization.

## Component and operation rules

For obligation `q` and frozen component universe `C`, record:

- `P_C(q)`: components whose primary purpose implements `q`.
- `R_C(q)`: other components with a resolved direct reference relevant to `q`
  to a primary component, including a relevant declaration, signature, variable
  use, or call.
- `P_O(q)` and `R_O(q)`: corresponding primary and referring source operations
  in the frozen operation universe `O`.

The proposed counts are `CDC-R(q) = |P_C(q) union R_C(q)|` and
`CDO-R(q) = |P_O(q) union R_O(q)|`. Deduplicate by logical identifier, not call
count or file occurrence. A component can be both primary and referring for
different obligations. Analyze each obligation separately; the totals across
obligations are not a partition of the program.

For CDO-R, choose the **2003 paper's primary-component access reading**:
include a source operation with a relevant direct reference to a primary
component through a parameter, return/raised type, local variable, or method
call, even if it never calls a primary operation. Also include an operation
that directly calls a primary operation in a mixed-purpose component. Record
which inclusion rule applies. A field-only reference contributes to CDC-R;
it does not create a CDO-R operation unless a source operation itself accesses
that component. Do not treat an operation as a type or take unbounded transitive
call closure. This chosen operationalization is an adaptation, not a silent
reconciliation with the thesis wording. Unresolved dispatch or unclear primary
purpose requires adjudication, not automatic inclusion or exclusion.

A signature-only fixture makes this choice observable: if `Policy` is primary
and `Bridge.accept(Policy p)` does nothing, `Bridge` adds one CDC-R component
and `accept` adds one CDO-R operation, despite having no call to `Policy.allowed`.
With the three units of example A below, the augmented counts are therefore
four components and four operations. An operation-call-only alternative would
exclude `accept`; if investigated, name and report that different variant
separately rather than mixing its values into CDO-R.

## Source shading and transition counting

For each obligation and component, annotate its eligible physical source lines
with a binary label: `1` implements or directly participates in the obligation
under the codebook; `0` does not. A line can be shaded for several obligations.
Save the rationale and source range, including declarations and mediation
calls where applicable. Freeze preprocessing, macro expansion, formatting,
comments, and generated-code treatment before comparing snapshots.

The proposed Lex profile excludes blank and comment-only lines, retains source
order, and counts label changes between adjacent eligible lines **within each
component**. For labels `b_1 ... b_n`, its component count is
`T = sum(i=2..n, |b_i - b_(i-1)|)`; sum `T` across included components.
There are no artificial entry/exit labels, no component-to-component boundary
transitions, and no reordering of separated blocks. A wholly shaded component
has zero internal transitions under this convention. Report its shaded-line
count so that it is distinguishable from a wholly unshaded component.

For the G profile, apply and document the original rules, including grouping
eligible concern blocks. Record each proposed merge of nonconsecutive blocks,
why it would preserve program meaning, and adjudicator agreement. The Lex
value is not a substitute for those judgments. If reliable G coding cannot be
achieved, report that limitation and retain the distinctly named Lex diagnostic.

## Synthetic counting examples

**These are invented annotation fixtures, not observations of ROO performance.**
Each string below is an ordered sequence of eligible-line labels for one
obligation; it is not executable code or proof of behavior.

In example A, a policy component implements caller permission and two components
refer to it. Its primary operation is `Policy.allowed`; `Order.submit` and
`Worker.resume` are referring operations. Both variants therefore have
`CDC-R = 3` and `CDO-R = 3`.

| Component | Variant A labels | Lex transitions | Variant B labels | Lex transitions |
|---|---|---:|---|---:|
| Policy | `11111` | 0 | `11111` | 0 |
| Order | `00111001100` | 4 | `001111100` | 2 |
| Worker | `01010` | 4 | `0011100` | 2 |
| Total | | **8** | | **4** |

The fixture describes less interleaving of annotations without changing the
component/operation counts. It establishes no defect reduction and makes no
claim that either layout is a valid program transformation.

In example B, suppose a faulty variant removes the required execution-time
permission mediation from `Worker.resume`. Its Worker labels become `00000`;
only Policy and Order participate. The resulting vector is
`(CDC-R=2, CDO-R=2, CDLOC-Lex=2)`, using Variant B's other labels. The counts
decrease while the specified scenario permits an unauthorized execution.
The independently assessed invariant must reject that result. Counting fewer
locations cannot replace checking that all required locations are protected.

## Missing values and descriptive normalization

Use `not applicable` only when the predefined obligation genuinely does not
apply to that task. Use `unknown` when source, dispatch resolution, shading,
or assessment is incomplete. Zero requires a complete eligible universe and
completed annotation; describe whether it means no application implementation,
an excluded implementation, or no internal label changes. A partial count may
be reported as a lower bound with its missing scope, not as a complete result.

Report the raw counts, included component/operation/line counts, primary versus
referring sets, and external realization notes. Optional ratios such as
`CDC-R/|C|` and `CDO-R/|O|` are descriptive and undefined for an empty denominator.
They do not remove language, size, architecture, or granularity confounding;
unrelated added code can change a ratio without improving an obligation.
Do not combine the metrics into a weighted quality or superiority score.

## Annotation records and pilot acceptance

Keep a source manifest and five related records: obligation definitions;
component/operation identities; primary/reference annotations with source
locations; line shading and merging decisions; and independent scenario
outcomes. Each annotation identifies snapshot, obligation, logical unit,
role/reference kind, coder, evidence, and uncertainty. Keep original coder
answers, disagreements, and adjudications rather than only the reconciled file.

Pilot the codebook with two independent assessors. Measure agreement on
applicability, unit identities, primary/referring roles, and shading/merges;
agreement on the final number alone can hide incompatible annotations.
Record coding time and systematic disagreements. Assessors should be unaware
of condition where feasible, while reporting visible language, worksheets, or
structure that can reveal it. Freeze revisions before confirmatory annotation.

Use a competent practice baseline and a matched-content control as specified
in the [agenda](agenda-revised-2026-10-12.md#compare-against-a-competent-baseline). Treat ROO's
effect on diffusion as exploratory until construct validity and reliability
are established. Keep teams/tasks, training, implementation tools, and review
budgets comparable; analyze clustering and within-snapshot dependence rather
than treating every line or concern as an independent participant.

Primary evaluation still concerns invariant preservation, meaningful defect
detection, false alarms, comprehension, and total effort including annotation,
contract maintenance, and tool work. The earlier thesis itself claims that
Table 7 confirmed the metric predictions and gave substantial evidence of
utility (§8.8.3, p. 251). That interpretation rests on one Portalware system,
one table of seven author-selected scenarios (p. 245; the scenario subset came
from the author's experience, p. 254), and changed LOC as the maintenance-effort
proxy following Li et al. (pp. 251–252); the chapter reports no inferential
test, confidence interval, or p-value. Treat this as a historical predictive-
usefulness claim, not validation for ROO. Add an evolution task to test whether
diffusion predicts actual change effort or defects. Correlation with those
outcomes is a separate question from a randomized treatment effect. No sample
size, favorable threshold, or anticipated ROO gain is supplied by the historical
studies; feasibility and precision planning must precede confirmation.
