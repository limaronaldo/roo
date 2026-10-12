# Exercise facilitator guide

Use this guide **after** the participant has saved their initial concerns,
contracts, scenario predictions, mappings, and time record. It is a teaching
key, not an independently verified implementation or a preferred technology
solution. See the [exercise requirements](exercise.md) and
[trial criteria](README.md#criteria-agreed-before-the-trial).

## Expected obligations

Accept different designs that preserve the stated requirements. Look for these
decisions across the contracts; participants may split relationships differently.

| Field | Decision the record needs |
|---|---|
| Custodian | Retain immutable content and intent through uncertainty/restart; identify the independent archive custodian and release policy |
| Identity | Scope target and attempt identities; bind request key to fingerprint; prevent conflicting reuse and competing target admission |
| Coordinator | Name operations that admit, dispatch, settle, and reconcile, with the invariant each preserves |
| Authorization | Order the durable admission decision with revocation; separate publishing from restricted recovery of an admitted attempt |
| Access | Expose observations and commands; avoid a mutable current-document pointer or copied grant as execution permission |
| Horizon | Distinguish readable content, stale observations, permission timing, and retention through pending recovery |
| Execution | Coordinate all relevant workers and policy writers; identify the durable admission boundary and the separate archive effect |
| Failure | Preserve uncertainty, original content, fingerprint, and attempt identity; recover without creating a new logical publication |

The starting proposal hides at least six issues: mutable target selection,
stale permission, fresh keys on retry, deletion of recovery state, process-local
coordination across independent workers, and a lost-reply outcome treated as
an ordinary unsent job. Record which were found before and after the worksheet.
Counts measure coverage of this supplied exercise, not real-world defect
detection or a causal benefit of ROO. Additional valid findings are welcome.

## Expected scenario outcomes

| ID | Required outcome | Evidence a future implementation would need |
|---|---|---|
| P1 | Publish version 3 with its original digest; version 4 does not retarget the job | Immutable-version lookup and captured-content assertions |
| P2 | No newly admitted attempt or archive effect; a queued job may remain rejected or blocked by a stated policy | Controlled ordering of committed revocation before admission; retained-state and archive-count checks |
| P3 | The admitted attempt may finish; designated recovery reconciles that key/fingerprint despite the publisher's revoked permission | Admission-before-revocation witness; denied publisher recovery and permitted recovery-principal checks |
| P4 | One admitted target/attempt wins; the other caller gets the existing result or an explicit conflict | Two-process admission race with target uniqueness and archive effect count |
| P5 | Durable pending identity survives; lookup or permitted same-key resend resolves it; no second logical effect | Restart between archive commit and settlement, with before/after durable state and archive assertions |
| P6 | Reject conflicting reuse; preserve the original identity, fingerprint, and result | Negative request and unchanged-state assertions |
| P7 | Hiding does not remove required recovery data; reconcile the original immutable version and attempt | Hide/restart/recovery sequence and retained-content checks |

The P3 rule deliberately permits completion of an admitted operation after
revocation. A design that rechecks every later phase may need a different
recovery policy. Do not substitute the orders/payments laboratory's policy
for this exercise's stated admission rule.

## Assess and discuss

For each scenario, record **meets**, **needs revision**, or **unknown**, with a
reason. `Meets` requires a consistent predicted outcome and a named boundary
that could enforce it; it does not mean a test passed. An unverified storage or
provider guarantee stays an assumption even when the paper design is coherent.

Have a second reader predict two outcomes from the contract before the
participant explains them. Record disagreements before editing. Compare the
two technology mappings: can each retain intent, order admission with policy,
exclude competing target admissions, and recover the same archive identity?
One mapping may be infeasible under its stated guarantees; that is a valid
finding when explicit, not a successful transfer demonstration.

Separate first-attempt results from changes after feedback. Ask what the form
clarified, duplicated, or obscured, which question needed explanation, and
whether the participant would use it on another relationship. Report failed
criteria and unknowns as well as successes. Agree on follow-up actions without
turning the report into a completed field study or production approval.
