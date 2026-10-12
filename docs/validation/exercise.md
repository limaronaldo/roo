# Practical exercise: revocable document publication

Design one operation using synthetic data. This case is a paper exercise,
separate from the executable orders/payments laboratories. No publication
service, alternative backend, or runtime test is supplied by this kit.

Use the [kit protocol](README.md). Keep the facilitator notes closed until
your first attempt is recorded. Work without AI assistance for the independent
attempt; if assistance is needed, continue and disclose when and how it was
used. Assisted results remain useful but have a different scope.

## Requirements

A workspace contains documents with immutable numbered versions. A publisher
queues a job to publish one version to an external archive channel. An editor
may create a later version while that job waits.

- A target is `(workspace, document, version, channel)`. At most one logical
  publication attempt exists for a target, including competing workers and
  retries. A request key binds that target and its content digest; conflicting
  reuse must be rejected without changing the original attempt.
- The archive accepts an attempt key, rejects conflicting content for that
  key, and retains its result for lookup and deduplication. For this exercise,
  that guarantee lasts until 30 days after local terminal settlement. Treat it
  as a supplied provider assumption, not an observed fact. Unsettled attempts
  remain recoverable; expiration needs a separate policy.
- Reading or queueing a document does not grant execution permission. A
  revocation committed before the **publish authorization decision** prevents
  admission of a new external attempt. That decision must be ordered with
  policy changes and durably identify the admitted target and attempt before
  an external call. Revocation afterward allows that admitted attempt to
  finish or be reconciled with its original identity.
- Only a designated recovery principal may reconcile an admitted attempt
  after the publisher's permission is revoked. Recovery cannot admit a new
  target or change its content. An archive lookup is allowed on that path;
  any resend must use the already admitted key and fingerprint.
- Removing the document from normal browsing must not erase the immutable
  content, identity, or pending intent needed for recovery. Restart must retain
  those facts. Define their custodian and eventual release policy.
- A lost archive reply means an uncertain outcome. Local failure or cancellation
  does not undo an archive effect. A status observation can be stale; it cannot
  authorize publishing or prove that retry is harmless.

## Starting proposal to review

> The queue stores a pointer to the current document and a `canPublish` flag
> copied when the job is queued. A worker reads the current content, sends it
> with a fresh request key, and marks the job complete after a reply. Timeout
> returns the job to the queue. Deleting a document deletes its queued jobs.
> Each worker uses its own local mutex, so retries are safe.

Treat this as a deliberately weak proposal. Explain its consequences before
replacing it; a list of patterns is insufficient.

## Procedure and deliverables

Follow the canonical [six steps](../02-relationship-design.md#23-the-six-step-decision-procedure).
Suggested budget: 10 minutes for the initial review, 35 for contracts, 20 for
scenario walkthroughs and mappings, and 10 for the report.

1. Before using the worksheet, record concerns and predicted failures in the
   starting proposal. Save this initial text and time spent.
2. Triage the relationships. Complete the [eight-field worksheet](../../templates/relationship-contract.md)
   for `PublicationJob -> DocumentVersion` and
   `PublicationAttempt -> ArchiveResult`; explain any extra relationship needed
   to coordinate policy or uniqueness. State invariants and observation points.
3. Sketch admission, dispatch, settlement, and recovery. Record unresolved
   decisions; do not fill gaps with assumed library or database behavior.
4. Predict P1–P7 below. Name the enforcing boundary and what evidence would
   test it. Mark walkthroughs as predictions, not executed checks.
5. Propose two technology mappings for the same contract. Change at least one
   storage or execution model, such as a relational transaction and a durable
   single-coordinator log. Name each needed guarantee, its cost, and any open
   assumption. Language choice is optional; implementation is outside this task.
6. Record what changed after the worksheet, actual time, unresolved questions,
   and help received in the [results template](../../templates/validation-results.md).
   Preserve this first attempt before discussion or facilitator feedback.

## Scenario cards

| ID | Controlled sequence | Predict and explain |
|---|---|---|
| P1 | Queue version 3; an editor creates version 4; execute the job | Which immutable content and digest may reach the archive? |
| P2 | Observe permission; commit revocation; reach the publish authorization decision | Which local and external effects are permitted? |
| P3 | Admit the attempt; commit revocation; the archive succeeds but its reply is lost | Who may finish recovery, and using which identity? |
| P4 | Two processes admit the same target concurrently with different request keys | What prevents two logical attempts and two publications? |
| P5 | The archive commits; the worker stops before local settlement; restart and recover | Which facts survive, and how is the uncertain outcome resolved? |
| P6 | Reuse a request key with a different target or digest | What is rejected, and what remains unchanged? |
| P7 | Hide the document while an admitted attempt is pending; recover after restart | Where does recovery find the original content and correlation? |

The exercise tests explanation and design choices. Runtime implementation,
production authentication, actual archive retention, and performance require
separate evidence. For an executable comparison, use the existing
[implementation index](../implementations.md) with its own specifications.
