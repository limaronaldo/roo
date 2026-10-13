# Garcia and Lucena compared with ROO

Garcia's agent/aspect work is a substantive antecedent for separating concerns,
composing interactions, and evaluating implementations. ROO's candidate
contribution lies in a different review unit: obligations on selected
relationships. Neither different vocabulary nor later infrastructure examples
establish greater conceptual depth or superior engineering outcomes.

This comparison uses Garcia, de Lucena, and Cowan's 2004 article, thesis
chapters, and the joint 2003 Sant’Anna, Garcia, Chavez, Lucena, and von Staa
framework. The [source ledger](literature.md#s65--agents-and-separation-of-concerns)
identifies access and localizers. The complete institutional
[chapter 8](https://www.maxwell.vrac.puc-rio.br/5181/5181_9.PDF) was retrieved
after the initial partial review; its SHA-256 is
`6a185bf5c450223f2e5c8ad35b4cb25c256e4e174ccca9decd842170cc756625`.
Detailed working audits remain separately preserved. This public synthesis
retains the primary links, printed-page localizers, and unresolved differences.

## Compare units and claims symmetrically

| Dimension | Garcia and collaborators | ROO | Defensible comparison |
|---|---|---|---|
| Unit | Agency concerns and their composition across objects, roles, and aspects | Selected relationship, invariant, and eight decisions | Different units with overlapping questions; no demonstrated subsumption. |
| Problem | Scattering and tangling of agency concerns in object-oriented multi-agent implementations | Unclear obligations at lifecycle, process, transaction, or trust boundaries | Neither problem statement establishes that the other method cannot express it. |
| Procedure and artifact | Agent-design method, UML/aspect models, patterns, and implementation examples | Six-step scenario/triage/contract/realization/counterexample/evidence procedure | Both organize design work; ROO does not originate concern separation or structured methods. |
| Interaction | Explicit agency concern and collaboration roles, including Portalware request/result protocols | Explicit decisions concerning coordination, permission, access, freshness, execution, and failure | Interaction is central in the earlier work. Detailed revocation and uncertain remote outcomes were not located in the examined Portalware passages. |
| Realization | Aspect composition demonstrated with AspectJ; not tied to one MAS framework or agent communication language | Candidate types, stores, locks, actors, or protocols chosen after the record | A contract records decisions; its chosen mechanisms enforce them. Independence from a communication language is not independence from every implementation mechanism. |
| Evolution | Construction, requirement changes, and concern/role reuse examined in comparative cases | Proposed change questions and scoped teaching scenarios | Compare actual changes and their costs instead of counting stated questions. |
| Evaluation | Comparative artifact metrics and developer-built implementations | Executable laboratory evidence, without comparative method-effectiveness evidence | Historical implementation results do not quantify a ROO effect; ROO's labs do not supply a head-to-head method study. |
| Guarantees | Scoped models, implementations, and empirical observations | Proposed elicitation/review method and particular realizations | Neither a metric nor a filled worksheet is a general correctness, security, or liveness theorem. |

Article localizers: sections 2 and 5 for agency concerns, interaction, roles,
and the method; sections 7.1–7.2 and Table 2 for the evaluation. The preserved semantic audit distinguishes explicit, partial, not-located,
not-assessed, and out-of-scope textual evidence. These labels are not a
procedural-coverage ranking; the [revised agenda](agenda-revised-2026-10-12.md#make-each-comparison-cell-traceable)
defines a separate codebook for future comparison.

## What chapter 8 currently supports

The complete local Maxwell partition covers printed pp. 231–254. The thesis
describes one Portalware system and four PUC-Rio graduate-student subjects; all
four participated in both OA and OP versions (p. 237). The author explicitly
states that this was not a controlled experiment because the subjects took
part in both versions (p. 252). Two prior pattern advocates and two prior
aspect advocates were selected to reduce allegiance effects, and OA was built
first; the author also notes a possible learning effect (p. 252). These facts
do not imply random assignment or counterbalanced order. The institutional chapter and the source hash above make this account
recoverable independently of the preserved working audit.

The chapter presents seven change/reuse scenarios and one Table 7 on p. 245.
Section 8.8.3 says the table confirmed predictions from the metrics and
provided substantial evidence of their utility (p. 251). That is the authors'
interpretation of one system and seven scenarios, not a general validation or
inferential statistical result. The chapter operationalizes maintenance effort
as changed LOC following Li et al. (pp. 251–252), and says the scenario subset
came from the author's development experience (p. 254).

The page-level measurements must retain their source and aggregation. VS is
60 OP versus 56 OA (pp. 240–241), which makes the stated OP increase 7% relative
to OA. For LOC, the primary values are 1,445 OP and 1,271 OA (p. 242); 174/1,445
is 12.0%, so AO is about 12% lower relative to OP, while OP is 13.7% higher
relative to OA. The p. 240 wording reverses that denominator, and Figure 88
shows the OA/OP ratio. The chart's system-level WOC and LCOO directions also
need to be read separately from the component-level examples and discussion:
chapter 8 uses WOC/OOC/OCC labels across pp. 239, 241–242, and 249, and its
aggregate summaries and local examples do not yield one unqualified direction
for operation complexity or cohesion. The evidence correction records each
page and the unresolved aggregation questions.

The 2004 article §7.2 says the two methods were applied by different
developers, whereas thesis pp. 237 and 252 say the four subjects participated
in both and explicitly reject the controlled-experiment label. Keep these
accounts separate; this comparison uses the thesis for the thesis's design and
validity claims, without inventing a reconciliation.

## A common scenario can support a future comparison

Use a synthetic inventory reservation with a revocable mission grant and a
supplier request whose successful reply may be lost. State the required
permission, quantity, retry, and reconciliation outcomes identically for both
conditions. Garcia-style interaction/collaboration aspects and a ROO relationship
contract are possible design artifacts. Their implementations must still
demonstrate those outcomes under the same scope and tools.

Do not assume the earlier approach cannot express the added requirements,
or that the ROO record enforces them automatically. Assess omitted obligations,
actual behavior, understanding, evolution effort, and total cost. A prospective
comparison needs competent realizations of both approaches and must separate
the method intervention from implementation-language and framework differences.

## What to adapt from the assessment framework

Concern diffusion provides a structural lens, not a new correctness score.
The [proposed protocol](roo-concern-diffusion-protocol.md) defines obligations
independently of ROO field names, logical source units, distinct primary and
referring roles, missing-data states, and assessor agreement. It distinguishes
the original CDO wording across sources and original CDLOC shading judgments
from an explicitly named lexical variant.

Synthetic fixtures show why lower diffusion can accompany a missing permission
check. An evolution task must test whether a structural measure predicts actual
change effort or defects. Independent invariant outcomes and total effort remain
separate endpoints; no historical percentage supplies an expected ROO gain.

The next evidence priorities are resolving metric naming and aggregation,
reliably coding primary purpose/references and shading, and piloting the
proposed protocol before confirmatory comparison. The 2003–2004 work is a
precedent, not a ROO result: its one-system, seven-scenario predictive claim
does not establish that concern diffusion predicts ROO change effort. These
steps may support, narrow, or reject the proposed contribution.
