# First human validation round: v0.4.2 kit

**Status: prepared, not started.** No invitations have been sent, participants
assigned, or human results collected by preparing this pack. The maintainer
chooses recipients and sends the [invitation drafts](invitations.md) separately.
This Development plan coordinates the published kit; it does not revise a
released edition or report a completed human review.

## Freeze the pack before inviting

Round ID: `ROO-v0.4.2-round-1`.

| Material | Frozen target | Use |
|---|---|---|
| Method and reference code | v0.4.1, `f6670a109d7dbfef8f72078b4cd361079ac6a10a` | Inspect the method, design cases, and any selected executable sources |
| Kit, requirements, criteria, and results form | v0.4.2, `9a149882a3bb2e65cbfa7f569420ba2fc40ae2d4` | Apply the published review and exercise protocol |
| This coordination plan and consolidation form | [record the exact accepted commit before sending] | Preserve the instructions actually supplied to participants |

The two release targets follow the
[published protocol](https://github.com/limaronaldo/roo/blob/9a149882a3bb2e65cbfa7f569420ba2fc40ae2d4/docs/validation/README.md).
Record all three revisions in the private round record. Do not replace them
with `main`, Development URLs, or a newer release during the round. If a source
must change, retain earlier reports and label the changed attempt separately.

Send the role's pinned brief, the
[blank individual results form](https://github.com/limaronaldo/roo/blob/9a149882a3bb2e65cbfa7f569420ba2fc40ae2d4/templates/validation-results.md),
and these method sources:

- [Canonical eight fields and six steps](https://github.com/limaronaldo/roo/blob/f6670a109d7dbfef8f72078b4cd361079ac6a10a/docs/02-relationship-design.md).
- [Relationship worksheet](https://github.com/limaronaldo/roo/blob/f6670a109d7dbfef8f72078b4cd361079ac6a10a/templates/relationship-contract.md).
- [Claims and limits](https://github.com/limaronaldo/roo/blob/f6670a109d7dbfef8f72078b4cd361079ac6a10a/docs/claims-and-limits.md).

Briefs link to other files. Inspect method/code links at the method commit
above and kit/exercise links at the kit commit. Code execution is optional;
record the exact checkout, environment, command, and outcome if performed.

## Arrange participation privately

Recruit one human Rust reviewer and one human DDD/architecture reviewer,
preferably different people. Include a practitioner for the exercise; they
may also be a reviewer. Assign role IDs `R1`, `D1`, and `E1`, keeping the mapping
to people private. Record overlaps and the actual number of distinct people.
An AI-only report does not fill a human role.

Before work begins, agree privately on availability, relevant experience,
prior ROO involvement, prior exposure to the exercise/key, assistance, time
budget, submission dates, and sharing/attribution preferences. Participation
does not authorize public attribution or publication. Participants may decline
or stop; an absent report remains missing rather than a favorable result.

Use the kit's suggested 60–90 minutes per review and 75 minutes for the
exercise. Reserve another 20–30 minutes for joint triage if participants agree.
These are planning budgets, not measured performance. Record actual time by
stage; agree on comparable budgets before starting.

Keep contact details, consent records, working notes, and original reports in
a private location selected by the maintainer. Do not commit them, raw review
text, or private project material. Use only synthetic examples. This round
does not require access to a production system or a private field study.

## Apply the kit in this order

1. **Independent reviews.** Give `R1` the
   [Rust brief](https://github.com/limaronaldo/roo/blob/9a149882a3bb2e65cbfa7f569420ba2fc40ae2d4/docs/validation/rust-review.md)
   and `D1` the
   [DDD brief](https://github.com/limaronaldo/roo/blob/9a149882a3bb2e65cbfa7f569420ba2fc40ae2d4/docs/validation/ddd-review.md).
   Each saves an initial report before seeing the other's findings or the
   exercise key. Record inspected sources, exclusions, assistance, and checks
   not run. The DDD exercise cross-check is added later, separately.
2. **Practitioner attempt.** Give `E1` the
   [exercise](https://github.com/limaronaldo/roo/blob/9a149882a3bb2e65cbfa7f569420ba2fc40ae2d4/docs/validation/exercise.md),
   worksheet, and individual form. Preserve concerns before the worksheet,
   completed contracts, P1–P7 predictions, two technology mappings, and time.
   Follow the exercise's initial attempt without AI assistance. If help is
   needed, continue and disclose when and how; do not label it unassisted.
3. **Save the first attempts.** Give each artifact an ID, exact revision, and
   recorded submission time; retain an unchanged private copy. Label later
   edits separately. No answers or corrective coaching should precede this
   checkpoint. Record prior exposure or accidental early access to the key.
4. **DDD cross-check.** Before showing the key, give `D1` only `E1`'s saved
   contract. `D1` predicts two scenario outcomes; then `E1` explains theirs.
   Record both predictions and disagreements before clarification. Inspect
   the mappings afterward. If `D1` and `E1` are the same person, this is not a
   second-reader check: recruit a distinct human reader or mark it not
   performed and retain the narrower scope.
5. **Assess and discuss.** Only now open the
   [facilitator guide](https://github.com/limaronaldo/roo/blob/9a149882a3bb2e65cbfa7f569420ba2fc40ae2d4/docs/validation/facilitator-guide.md).
   Assess P1–P7 against the exercise requirements and named enforcement
   boundaries. Preserve initial assessments, subsequent explanations, and
   changes after feedback. A coherent paper prediction is not a passed
   runtime test. Keep this exercise's admission/revocation policy distinct
   from the orders/payments laboratory's policy.

The key is public, so this is a controlled sequence, not guaranteed blinding.
Disclose contamination and role overlap rather than discarding unfavorable
reports or claiming independence that the sequence did not provide.

## Consolidate without hiding gaps

Use the [round summary form](../../templates/validation-round-summary.md).
Keep one individual form per role, linking a combined person's reports rather
than counting that person twice. The maintainer assembles the summary; reviewers
check that their findings and disagreements are represented faithfully.

- Group duplicate findings by root cause while preserving every originating
  report ID. Keep demonstrated defects, unverified questions, and optional
  improvements separate. Check requirements, source locations, and evidence;
  agreement alone does not demonstrate a defect or resolve a question.
- Record each criterion's applicable reports. A combined criterion is **unmet**
  if any applicable assessment is unmet, **unknown** if required evidence is
  missing or unresolved, and **met** only if all required applicable
  assessments are met. A role-specific exclusion cannot waive a required
  round deliverable. Do not average scores or use a majority vote.
- Transfer is **met** only when both mappings preserve every required promise.
  A changed promise or infeasible mapping is **unmet**; unresolved feasibility
  is **unknown**. This is paper assessment, not backend qualification.
- Report protocol completion separately: both human review lanes, the exercise
  report, and findings triage are required. Retain a missing cross-check and
  its impact on the agreed scope; missing required evidence prevents an
  unqualified positive outcome even if the other work is complete.
- Use **revise** for identified gaps; **inconclusive** when missing evidence or
  unresolved questions prevent judgment; **ready for another trial** only
  with complete required work, met scoped criteria, and resolved required
  decisions. Partial work can identify a reason to revise, but cannot support
  readiness. Record disputed findings and follow-up evidence explicitly.

Assign follow-up actions with an owner, exact affected revision, and acceptance
evidence. A proposed fix is open; a later verified correction does not rewrite
what the original trial found. Report useful confirmations as well as added
effort, confusing fields, and absent benefits.

## Approve a public summary separately

First circulate the proposed summary privately. Obtain approval for the exact
text and attribution from each contributor whose material it includes.
Exclude unapproved material, record exclusions, and narrow the public claim
if necessary. A declined publication permission is not a negative method
assessment; private completion and public evidence availability are distinct.

Publish only the approved synthetic summary through a separate contribution.
Leave originals private and historical records intact. Describe this as one
small human review/exercise round with its actual scope, not proof of novelty,
superiority, faster delivery, reduced defects, a field study, or production
readiness. No participant result is implied by this preparation PR.
