# First-round invitation drafts

These are unsent drafts for the maintainer to adapt and send privately after
choosing recipients. They do not identify, recruit, or claim acceptance by
anyone. Follow the [first-round plan](first-round.md), record its exact accepted
commit before sending, and agree on dates after a recipient accepts.

## Rust reviewer

**Subject:** Invitation: review ROO's Rust mapping with the v0.4.2 validation kit

Hello,

Would you be willing to review how ROO's relationship decisions translate into
Rust? ROO means Relationship & Ownership Oriented design: a proposed method
for describing important relationships before choosing language, storage,
and execution mechanisms. It was developed with AI assistance; independent
human evaluation remains open. Agreement with the proposal is not expected.

The initial scope is deliberately small: access and identity, rejected
transitions, and permission observation followed by revocation and execution.
Please identify where the contract clarifies Rust API design, adds paperwork,
or makes a claim its evidence does not support. PostgreSQL/HTTP inspection is
optional and must be scoped separately.

Use these frozen sources:

- Method/code: v0.4.1, `f6670a109d7dbfef8f72078b4cd361079ac6a10a`.
- Kit: v0.4.2, `9a149882a3bb2e65cbfa7f569420ba2fc40ae2d4`.
- [Protocol and criteria](https://github.com/limaronaldo/roo/blob/9a149882a3bb2e65cbfa7f569420ba2fc40ae2d4/docs/validation/README.md),
  [Rust brief](https://github.com/limaronaldo/roo/blob/9a149882a3bb2e65cbfa7f569420ba2fc40ae2d4/docs/validation/rust-review.md),
  and [blank results form](https://github.com/limaronaldo/roo/blob/9a149882a3bb2e65cbfa7f569420ba2fc40ae2d4/templates/validation-results.md).

The brief links to method/code files; inspect those at the method commit above.
Budget 60–90 minutes initially, then an optional 20–30-minute triage discussion.
These are suggested budgets. Code execution is optional; mark checks not run.
Return one contract-to-API explanation, one success and one failure trace,
findings with source references, actual time, and assistance received.

Save your initial report before reading other reviewers' findings or the
exercise facilitator key. Negative and inconclusive results are welcome.
Please reply privately with availability, relevant experience, prior ROO
involvement, and any prior exposure to the exercise. We can then agree on dates
and scope. Participation is optional, and you may stop without completing it.

Use synthetic examples only. Send your report privately; participation does
not authorize publication or attribution. Any public summary will need your
approval of its exact wording and your preferred attribution.

Thank you for considering it.

## DDD and architecture reviewer

**Subject:** Invitation: review ROO's design method with the v0.4.2 validation kit

Hello,

Would you be willing to review whether ROO helps explain domain decisions and
failure boundaries beyond a conventional ADR or design review? ROO means
Relationship & Ownership Oriented design. It combines established concepts
into a proposed practitioner workflow; it does not claim to have invented
DDD, ownership, or consistency design. It was developed with AI assistance,
and independent human evaluation remains open.

Please challenge the distinction between Custodian, Identity, Coordinator,
Authorization, Access, Horizon, Execution, and Failure. Inspect the neutral
payment/revocation cases and identify useful clarification, duplication,
confusing fields, or unsupported claims. Rust knowledge and code execution
are optional. Agreement with the proposal is not a success requirement.

Use these frozen sources:

- Method/code: v0.4.1, `f6670a109d7dbfef8f72078b4cd361079ac6a10a`.
- Kit: v0.4.2, `9a149882a3bb2e65cbfa7f569420ba2fc40ae2d4`.
- [Protocol and criteria](https://github.com/limaronaldo/roo/blob/9a149882a3bb2e65cbfa7f569420ba2fc40ae2d4/docs/validation/README.md),
  [DDD/architecture brief](https://github.com/limaronaldo/roo/blob/9a149882a3bb2e65cbfa7f569420ba2fc40ae2d4/docs/validation/ddd-review.md),
  and [blank results form](https://github.com/limaronaldo/roo/blob/9a149882a3bb2e65cbfa7f569420ba2fc40ae2d4/templates/validation-results.md).

The brief links to method/code files; inspect those at the method commit above.
Budget 60–90 minutes initially, then an optional 20–30-minute triage discussion.
These are suggested budgets. Return one boundary explanation or diagram,
concrete findings, actual time and assistance, and an assessment of practical
value, including effort without observed benefit.

Save the initial review before reading the Rust review or the exercise key.
The coordinator will later provide a practitioner's saved contract for the
brief's two-scenario cross-check, before any facilitator feedback. Record
predictions and disagreements before clarification. If that artifact or a
distinct second reader is unavailable, mark the cross-check not performed;
do not substitute a fictional result.

Negative and inconclusive findings are welcome. Please reply privately with
availability, relevant experience, prior ROO involvement, and any exposure to
the exercise. We can agree on dates and scope after acceptance. Participation
is optional, and you may stop without completing it.

Use synthetic examples only. Return working material privately. Participation
does not authorize publication or attribution; any public summary requires
your approval of its exact wording and your preferred attribution.

Thank you for considering it.
