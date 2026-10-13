# Assisted design exploration with ROO

**Status:** evaluation proposal. ROO's eight-field contract and six-step procedure
remain canonical. The workflow below assigns supporting responsibilities; it is
not an implemented agent platform, a new edition, or a validated autonomy policy.

The hypothesis is that assistance during design can expose consequential
obligations and useful alternatives before implementation, at an acceptable
total cost. Generating more contracts is not itself that benefit. Discovery,
drafting, challenge, realization, and checking can use different roles, or one
assistant with explicit handoffs. Their relative effectiveness needs comparison.

The field record can structure prompts and communication between engineers and
tools. That use does not define a formal intermediate representation with
composition semantics or a verified translation into implementation code.

## Inputs and decision status

Start with the intended scenario, allowed and forbidden outcomes, known boundary,
and the current design or code when available. A repository scan supplies
candidate relationships; it cannot recover unstated stakeholder intent or all
relationships hidden in configuration, dynamic calls, providers, and operations.
Retain consequential exclusions and unresolved discovery questions.

For each proposed answer, distinguish:

- A required obligation, with its requirement or responsible decision maker.
- Observed behavior, with a source location and the implementation revision.
- A proposed change, with the assumption and alternative it addresses.
- An unknown or conflict that must remain visible to the reviewer.

These labels accompany the record; they are not additional contract fields.
Extracting an existing defect into a plausible contract must not make that
behavior the intended policy. A prose scenario suggested by a model is a
candidate trace, not an executed simulation or a demonstrated counterexample.

## Supporting roles within the canonical procedure

| ROO step | Supporting responsibility | Reviewable output |
|---|---|---|
| 1. Describe the scenario | Elicit intent and challenge missing requirements with the responsible engineer | Invariant, observation boundary, allowed/forbidden outcomes, and open policy |
| 2. Triage relationships | Discover and classify candidate boundaries in requirements, code, and configuration | Scoped inventory, selection reasons, and consequential gaps |
| 3. Complete the contract | Draft all eight decisions, distinguishing required, observed, proposed, and unknown | Source-linked contract with explicit assumptions |
| 4. Choose realizations | Compare mechanisms against the same obligations | Alternatives, assumptions, costs, and implementation/model candidates |
| 5. Check a counterexample | Challenge the design and check the relevant trace, model, or executable scenario | Expected observation, actual scoped evidence when available, and disagreements |
| 6. Record evidence and decide | Consolidate the checks and unresolved questions for the responsible decision maker | Accepted tradeoff with scope, or an open decision |

Explore alternatives and counterexamples iteratively; discoveries can change
the scenario or invalidate a realization. Policy choices may need human input
earlier than step 6. Final acceptance of a checked realization follows the
relevant evidence, rather than relying on a promise that later CI will pass.
An unchecked design can remain a proposal with its verification work explicit.

Separate role outputs so a reviewer can inspect their evidence and disagreements.
Distinct personas do not establish independent errors, exhaustive exploration,
or reliable consensus. A challenger should derive the expected behavior from
requirements, not simply ratify the builder's assertion. A deterministic tool
executes a specified check; it does not arbitrate missing business policy.

## A prospective design exercise

Consider a synthetic payment requirement: when a provider charges but its reply
is lost, ending the caller's session must not erase the attempt information
needed for reconciliation. The attempt identity must remain stable, and a retry
must follow the specified provider/deduplication protocol. This is an exercise,
not a new observation from the payments laboratory.

| Candidate realization | What could satisfy the requirement | What to challenge |
|---|---|---|
| Attempt retained with a durable order aggregate | The order's retention and access policy preserves the attempt after session end or an allowed order-state change | Deletion/retention rules, competing writers, and recovery lookup |
| Attempt retained in a separate durable store | Recovery resolves the attempt independently while retaining its order correlation | Cross-store consistency, orphan records, and coordination of state changes |

The obligation is durable recoverability; it does not force a separate class,
component, or store. Dropping an in-memory order also does not imply deleting
its persisted attempt. Opaque identity and pessimistic locking answer different
questions and can coexist; they are not inherently competing alternatives.

A proposed adverse trace persists the attempt, loses a reply after the external
effect, ends the session, and asks recovery to resolve the same attempt. The
forbidden result is an unresolvable surviving effect or a retry that violates
the stated deduplication policy. Before executing a test, specify the expected
outcome independently, including what remains unknown until reconciliation.
Cancellation, compensation, authorization, and retention policy require their
own decisions; the assistant cannot infer them from a payment-method name.

Generating Java, Rust, or Go code after this discussion still requires checking
the chosen runtime, storage, permission, and protocol behavior. Agreement on a
natural-language contract supplies no verified translation or proof that
implementations preserve it. See the existing
[evidence boundaries](../docs/claims-and-limits.md).

## Discovery coverage and intervention depth

A pilot may scan broadly while reserving detailed contract work for selected
consequential relationships. Define the candidate universe, supported discovery
mechanisms, and omissions before claiming coverage. Reviewing every PR does
not establish detection of every important boundary within those PRs.

Choose assistance depth from consequences, reversibility, uncertainty, and the
project's existing decision responsibilities. Code location is insufficient:
a local cache can serve stale permission data, and a database transaction can
have well-understood, already-reviewed obligations. Broad discovery does not
justify automatic policy acceptance for local code or superficial confirmation
of persistence/concurrency semantics.

Record scanning, generation, model/tool use, waiting, integration, human review,
correction, and maintenance costs. More parallel roles can move or enlarge the
bottleneck. Expand the pilot only if measured coverage and outcomes justify its
total cost; there is no established near-zero marginal cost or seconds-long
decision bound.

## Evidence and evaluation

[Brooks, S77](literature.md#s77--essential-and-accidental-difficulties) provides a
conceptual motivation for examining design as well as representation, not an
LLM productivity result. [Dhar et al., S78](literature.md#s78--llms-and-architectural-decision-drafting)
study drafting architectural decisions from context; text similarity and
plausibility cannot establish implementation correctness. The
[multi-agent failure study, S79](literature.md#s79--multi-agent-system-failures)
motivates inspecting coordination and verification failures as well as role
specialization. None evaluates ROO.

Architectural decision assistance and agent coordination are antecedents, not
ROO inventions. The candidate artifact here is their scoped use with ROO's
obligation record, alternatives, and counterexample evidence. Its distinctness
and added value remain questions for comparison.

The [upstream-design comparison](upstream-design-comparison.md) identifies
existing specification/contract planning and architectural-agent workflows.
Early assistance, structured artifacts, agent specialization, and challenge
are not an empty design space. ROO could supply a relationship-review record
within one of those workflows; that integration has not been implemented or
shown to improve it. Compare the same competent workflow with and without
ROO before attributing benefit to the record.

The [expanded review](upstream-landscape-review.md) adds method-guided design
and distributed-model checking as relevant comparisons. Separate drafting a
record, challenging it, and deciding whether evidence satisfies independently
stated policy. A generated assertion may repeat the realization's mistaken
interpretation; deterministic checking does not correct that interpretation.
ROO field names do not automatically generate an oracle or uniquely select a
mechanism. The [verification evaluation](agenda-revised-2026-10-12.md#evaluate-obligations-and-verification-authority)
defines mapping, progress, false-alarm, and cost questions for that extension.

Use the [evaluation agenda](agenda-revised-2026-10-12.md#compare-design-assistance-and-role-decomposition)
to compare early assistance, reconstruction from code, one assistant, and
separated roles under declared budgets and context. Assess missed obligations,
incorrect policy, valid counterexamples, comprehension, implementation behavior,
and total effort. Preserve failures and disagreements. No near-perfect accuracy,
threefold gain, or general superiority over competent design follows from this
proposal.
