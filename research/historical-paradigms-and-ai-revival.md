# Adoption cost and assisted relationship review

ROO's practical question is whether reviewing selected relationship obligations
improves engineering outcomes enough to justify authoring, review, and
maintenance effort. Bureaucracy, stale records, and superficial answers are
credible risks to investigate. Neither inevitable rejection nor rescue through
AI follows from the historical comparisons. The proposed response is selective
use, reuse of maintained decisions, concrete counterexamples, and assistance
whose costs and mistakes are measured.

## What the adoption evidence supports

| Supplied assertion | Source-supported interpretation | Consequence for ROO |
|---|---|---|
| ADL-rejection and causal-percentage claim | [Malavolta et al., S69](literature.md#s69--industry-needs-from-architectural-languages) examine 48 practitioners from 40 companies in 15 countries and identify needs for usability, analysis, and greater formality. This sample does not establish a universal rejection rate or a single cause. | Evaluate integration, communication, analysis, and effort together. |
| ADR-abandonment and time-to-abandonment claim | [Buchgeher et al., S71](literature.md#s71--architecture-decision-records-in-open-source-projects) report that about half of repositories with ADRs contain one to five records. Few records can suggest experimentation; they do not measure a team's decision to abandon the practice or when that occurred. | Measure eligible changes and continued project activity, then confirm discontinuation and its reasons. |
| Mandatory eight-field checklists cause generic answers and LGTM rubber-stamping | [McIntosh et al., S72](literature.md#s72--review-participation-and-software-quality) associate review participation, coverage, and expertise with defects. [Sadowski et al., S68](literature.md#s68--industrial-code-review-practice) describe LGTM as approval after comments are addressed. Neither evaluates that worksheet intervention. | Treat copied answers and shallow approval as observable risks, not an established causal result. |

The alleged Wyrich ESEM 2023 ADR-abandonment study remains unidentified. Targeted
searches and the [institutional publication list](https://www.se.cs.uni-saarland.de/publications/lists/wyrich.html)
did not locate a matching paper; that is a citation gap, not proof that no
relevant study exists. It supplies no usable percentage here.

## Historical comparisons need matching guarantees

The supplied twelve-family narrative combines formal specification, contracts,
ontologies, architectural languages, testing, static analysis, model-driven
engineering, consensus, types, capabilities, literate programming, and session
types. It supplies neither a comparable adoption measure across these families
nor evidence for a universal cycle of death and AI-enabled revival. Its narrated
twelve-agent dispatch is not an auditable search record. Those topics remain
research leads rather than twelve established causal histories.

Two checked comparisons already show why the framing needs narrowing.
[AWS's formal-methods experience, S76](literature.md#s76--selective-formal-modeling-in-industry)
reports specification and model checking for critical designs from 2011,
complementing conventional verification. [Raft, S75](literature.md#s75--understandability-as-an-evaluated-design-objective)
evaluates student learnability against Paxos. These support selective modeling
and measured understandability, without showing that earlier methods died or
that ROO would achieve similar results.

A proposed replacement also needs a property-by-property comparison. A borrow
checker does not enforce arbitrary business postconditions; a service mesh does
not select a domain invariant's coordinator. A cloud service still has a
specified transaction and failure scope. Existing [ownership](literature.md#s25--rust-ownership),
[architectural fault-modeling](literature.md#s64--architectural-fault-modeling),
and [transaction-scope](literature.md#s66--distributed-transaction-guarantees)
entries make those distinctions. Broader replacement claims about RDF/RAG,
dependent/gradual types, or session types/API schemas require separate primary
comparisons before being used as evidence of equivalent guarantees.

The same fairness applies to object-oriented design. Competent OO practice can
address responsibilities, permissions, concurrency, and recovery. ROO has no
comparative result showing rarer bugs, lower incident cost, or easier long-term
maintenance. Earlier [responsibility-driven design](literature.md#s29--responsibility-driven-design)
is part of the baseline, not a practice ROO invented.

## Select relationships and reuse decisions

The [canonical triage](../docs/02-relationship-design.md) selects consequential
lifecycle, process, transaction, or trust boundaries and unclear invariant
coordination. It requires no code-coverage quota. A formatting helper rarely
needs its own record; a CRUD endpoint with tenant permissions or a local object
exposing a mutable alias can need one. Excluding all local or frontend code
would miss some of the method's stated scope.

Keep a maintained contract near the relevant code or ADR and link it from
reviews. Record changed decisions and their affected checks rather than copying
unchanged answers into each PR. Recheck inherited assumptions when their
conditions change. Progressive explanation can start with the largest
uncertainty, but all eight decisions remain accounted for: local code can still
have authorization, freshness, cancellation, and resource-release obligations.

Local aggregates, external providers/outboxes, and read projections are useful
starting prompts. They are not preapproved contracts: memory operations do not
automatically roll back, an outbox does not make an HTTP effect atomic, and a
read-only snapshot can still be stale or disclosed to the wrong caller.

## Make counterexamples reviewable

Step 5 can be brief: identify the initial state, adverse event or ordering,
forbidden outcome, and expected observation. Prefer an executable check when
feasible; use a reasoning trace or model when it better exposes the issue.
The [orders/payments case](../case-studies/orders-payments/README.md#3-treat-timeouts-as-uncertainty)
includes a scripted provider that can charge before the caller sees a timeout.
Its [verifier](../case-studies/orders-payments/verify.py) compares prebuilt runners
with a shared oracle. This is a bounded teaching realization, not a live-provider
integration result or an adoption experiment.

A proposed new check should distinguish the relevant faulty behavior from the
intended result. Compilation and a passing test alone do not establish the
correctness of the expected policy. Tests, formal models, and review cover
different scopes; link their assumptions rather than requiring an essay or
claiming that a finite test proves all executions.

## Bound assistance and CI checks

An assisted workflow can separate four responsibilities:

1. The engineer states the intended invariant, allowed outcomes, and relevant
   boundary, including decisions the implementation does not yet enforce.
2. An assistant drafts contract answers with source locations, distinguishes
   observed behavior from proposed policy, and leaves unknowns explicit.
3. The assistant proposes an adverse scenario and a check. A reviewer assesses
   its expected result independently of the generated implementation.
4. Tools run the scoped checks and retain evidence for the reviewed candidate;
   the responsible engineer decides the tradeoff and unresolved questions.

[TestGen-LLM, S73](literature.md#s73--filtered-test-generation-with-llms) illustrates
filtering generated tests, but discards initially failing tests when their
assertions cannot be trusted. It does not demonstrate an exhaustive adversarial
reviewer. Likewise, [Tricorder, S74](literature.md#s74--program-analysis-integrated-into-review)
is a 2015 program-analysis integration precedent, not evidence that LLMs remove
semantic mistakes. Faster review and fewer omissions are hypotheses for a ROO
assistant, not measured benefits.

The [assisted design proposal](assisted-design-protocol.md) extends assistance
to requirements and alternatives before coding, while retaining the canonical
procedure. [Brooks, S77](literature.md#s77--essential-and-accidental-difficulties)
distinguishes conceptual and representational difficulties; this motivates a
design question, not a claim that modern LLMs solve essential complexity.
[Decision-drafting research, S78](literature.md#s78--llms-and-architectural-decision-drafting)
and [multi-agent failure analysis, S79](literature.md#s79--multi-agent-system-failures)
provide closer comparisons. Neither establishes nearly free review or automatic
superiority from specialized personas.

The supplied dossier also contains quantitative claims about industry use of
AI, gains from adversarial roles, and accuracy on narrow tasks. This review did
not verify primary studies, sampling frames, metrics, or comparison conditions
for those claims, so it excludes them from the evidence base.
Processing every PR is different from detecting every consequential relationship,
and human policy review has no established seconds-long upper bound. Location
also cannot define safe autonomy: local caches may hold consequential stale
permissions. A generated contract does not make implementation a trivial or
verified syntactic translation.

| Proposed check | What it can establish in its declared scope | What still needs evaluation |
|---|---|---|
| Required keys and evidence links | Record structure and resolvable references | Concrete policy, relevant evidence, and continued agreement with code |
| Network-call and timeout rules | Matches against supported APIs or annotations | Calls hidden behind wrappers, SDK defaults, retries, and end-to-end deadlines |
| Idempotency checks | Named protocol rules or specified replay scenarios | Durable identity, atomic effect/deduplication, and actual provider guarantees |
| Scenario execution | Observed behavior for the checked implementation and environment | Untested interleavings, real dependencies, and the correctness of the oracle |

CI repeats checks; it can also repeatedly accept an incomplete rule. Scope,
false alarms, missed cases, bypasses, and maintenance matter. Git co-location
makes review easier but cannot guarantee zero drift. This analysis proposes no
new mandatory linter or automatic merge rule.

## Evaluate cost alongside outcomes

The [adoption protocol in the agenda](agenda-revised-2026-10-12.md#evaluate-adoption-cost-and-assistance)
separates manual and assisted conditions, competent baselines, substantive
coverage, stale decisions, and discontinuation. Measure total effort and
independent comprehension/defect outcomes. Define acceptable cost with the
participating team before the pilot, and narrow or discontinue the intervention
when the observed tradeoff fails that criterion. Record failures as well as
successful cases. Neither a record count nor a lower diffusion metric is a
substitute for that evidence.
