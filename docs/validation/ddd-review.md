# DDD and architecture reviewer brief

Evaluate whether the contract makes domain decisions and failure boundaries
clearer. Use the [kit protocol and criteria](README.md) and a separate
[results record](../../templates/validation-results.md). Rust knowledge and
code execution are optional for this lane.

## Scope and reading route

Read the frozen [canonical method](../02-relationship-design.md),
[architecture chapter](../05-architecture.md),
[technology-selection questions](../technology-selection.md), and
[Claims and limits](../claims-and-limits.md). Inspect the neutral
[payment-recovery case](../../case-studies/orders-payments/DESIGN.md),
[authorization case](../../case-studies/orders-payments/authorization/DESIGN.md),
and [completed contract](../../case-studies/orders-payments/adoption/relationship-contract.md).
Record which artifacts you actually inspected.

## Review in four passes

1. **Translate the vocabulary.** Explain each field in terms you already use.
   Check whether Custodian, Identity, Coordinator, and Authorization answer
   distinct questions. Identify overlap with DDD, information hiding,
   capabilities, and consistency design. ROO claims a compact workflow, not
   invention of those concepts.
2. **Test the boundaries.** Can a reader identify entities and values,
   aggregate invariants, application coordination, and independent lifecycles?
   Does the design distinguish an aggregate boundary, a loaded object's
   lifetime, and a durable transaction? Check whether snapshots and messages
   state freshness, identity scope, and missing/deleted-target behavior.
3. **Challenge an operation.** Walk through permission observation, revocation,
   execution, uncertain external success, and recovery. Who may reconcile an
   existing attempt, and can that path create a new effect? Identify which
   state must agree at which observation boundary. Avoid assuming an outbox,
   event, repository, or interface supplies a guarantee by its name.
4. **Compare alternatives and cost.** Can composition and inheritance preserve
   the same behavioral contract? Would another storage/execution model need
   a changed promise? Does triage select consequential relationships rather
   than require a form for every field? Note what the record adds beyond a
   conventional ADR or design review, and what duplicates existing work.

For each finding, cite the requirement and exact wording or source, then give
a concrete sequence that exposes the issue. Classify it as a demonstrated
defect, an unverified question, or an optional improvement. Keep disagreements
about policy separate from contradictions in the selected policy.

## Practical cross-check

Review a participant's sealed [exercise contract](exercise.md) before seeing
its facilitator notes. Predict two scenario outcomes using only that record.
Have the participant explain the same outcomes and record any disagreement
before clarification. Inspect their technology mappings afterward: a store
or language choice must preserve the promises or name the change.

If no participant is available, mark this cross-check **not performed** and
review the supplied design cases instead. That narrower review can still
produce useful findings; the combined trial remains partial.

## Required output

Submit a results record with one boundary diagram or explanation, the two
predicted outcomes if the cross-check was performed, findings, and a judgment
on clarity, effort, and practical value. Name one requirement whose answer was
made clearer, or report that none was. Identify a claim that still needs
implementation or field evidence. Do not present agreement with the proposal
as measured improvement or independent confirmation of its novelty.
