# ROO validation kit

Use this kit to evaluate whether ROO helps another engineer explain and review
a design. It prepares human review and a small practitioner trial; it records
no completed review, field study, or new implementation qualification.

The method stays independent of language, runtime, database, and protocol.
Rust inspection is one review lane. DDD and architecture review evaluates the
decisions before their implementation. The practical exercise needs no code
or toolchain.

## Freeze the target

Use **v0.4.1**, commit
`f6670a109d7dbfef8f72078b4cd361079ac6a10a`, as the initial method and code
baseline. Record the separate commit containing this kit. A later trial may
select another exact commit, but every participant in that trial must use the
same method, case requirements, and kit revision. Do not silently follow
Development during a review.

Read the selected checkout's [canonical eight fields and six-step procedure](../02-relationship-design.md),
[worksheet](../../templates/relationship-contract.md), and
[Claims and limits](../claims-and-limits.md). The guides below link current
paths for navigation; inspect method and code at the recorded baseline.
The kit remains Development material until included in a future tagged edition.

## Run the review

1. Assign a human Rust reviewer and a human DDD/software architecture reviewer.
   Prefer distinct people. Record relevant experience, prior involvement in
   ROO, and any assistance. One person doing both lanes provides one person's
   evaluation; an AI-only run provides automated feedback.
2. Give each reviewer the frozen sources, the relevant
   [Rust](rust-review.md) or [DDD](ddd-review.md) brief, and a blank
   [results template](../../templates/validation-results.md). Have them write
   initial findings separately before discussing them.
3. Ask a practitioner to complete the [publication exercise](exercise.md).
   They may also be a reviewer; record that overlap. Preserve their first
   attempt before showing the [facilitator guide](facilitator-guide.md).
4. Reconcile findings against requirements and sources. Keep disagreements,
   unknowns, assistance, and checks that were not run visible. Use the
   [design review](../../templates/design-review.md) for implementation findings.

Suggested time: 60–90 minutes per reviewer and 75 minutes for the exercise.
These are planning budgets, not measured ROO performance. Record actual time
and use the same budget for comparable trials. Do not contact reviewers or
publish their material without their agreement.

## Criteria agreed before the trial

| Area | Success criterion | Record when unmet |
|---|---|---|
| Traceability | Every report identifies method, kit, inspected sources, reviewer role, assistance, and actual checks | Missing scope; trial remains partial |
| Clarity | A reviewer can explain the invariant, all eight decisions, and one failure path from the submitted contract | Ambiguous field or contradictory interpretation |
| Exercise completeness | Each selected relationship answers eight fields; all P1–P7 scenarios have a predicted outcome and a named enforcement boundary | Open decision or missing scenario |
| Transfer | Two proposed technology mappings preserve the same observable promises, or explicitly identify a changed promise | Hidden reliance on a language, store, or protocol |
| Practical value | The participant records at least one concrete clarification, changed decision, or useful confirmation, with before/after text | No observed benefit in this attempt |
| Candor | Findings distinguish defects, questions, and improvements; walkthroughs, executed checks, and assumptions remain separate | Unsupported claim or unavailable evidence |

Exercise coverage is scored using the facilitator guide after the first
attempt. These criteria evaluate this trial, not production readiness. An
honest negative or inconclusive report is a useful result.

Protocol completion requires both review lanes, an exercise report, and
findings triage. Report completion separately from the outcome: **ready for
another trial** when the scoped criteria are met and required decisions are
resolved; **revise** for identified gaps; **inconclusive** when missing evidence
or unresolved questions prevent a judgment.
Do not infer reduced defect rates, delivery speed, or superiority over DDD from
one trial. The before/after exercise has learning and order effects and no
control group.

## Share only authorized results

Keep working notes private by default. Publish a contributor-approved summary
with synthetic examples and only authorized evidence. Exclude raw review text,
private system details, personal context, secrets, and real customer data.
Follow [Contributing](../../CONTRIBUTING.md); leave historical records and
released editions unchanged. A kit or an invitation is not a completed review.
