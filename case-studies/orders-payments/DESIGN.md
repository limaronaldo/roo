# Design case: payment recovery

An order totals 250 minor units. A provider charges it, but the application
fails before recording the terminal result. Recovery must finish the original
payment without charging again. This case introduces the decisions before any
language, database, or transport is selected.

Use the [canonical procedure](../../docs/02-relationship-design.md#23-the-six-step-decision-procedure)
and the [completed worksheet](adoption/relationship-contract.md) to review it.

## Participants and invariant

The order coordinates legal commercial transitions. An application coordinator
sequences preparation, provider work, and finalization. A local store retains
the payment intent and committed facts; the provider retains its independent
result. A consumer has a separate delivery/deduplication boundary.

**Invariant:** recovery preserves the original payment identity and immutable
request facts. Terminal local state and its event become visible together.
The required provider contract must prevent another effect for that retained
identity and fingerprint.

## States and failure outcomes

| Boundary | Observable state | Required next behavior |
|---|---|---|
| Before preparation | Draft; no retained payment intent | Reject invalid input without an effect |
| After preparation | Pending with a fixed intent | Call or inspect the provider with the same identity |
| Provider result uncertain | Pending; a charge may already exist | Preserve uncertainty and reconcile the original attempt |
| Provider approved, local finalization failed | Pending; one independent charge; no terminal local event | Recover local finalization from retained facts |
| Finalization committed | Paid and its terminal event; one charge | Duplicate recovery retains that result |

A timeout is an observation failure and can follow a successful effect.
Releasing a local object cannot establish that an external charge was undone.
Provider not-found is usable only under an explicit lookup/retention contract.

## Relationship Contract

| Field | Decision |
|---|---|
| Custodian | Store retains order, intent, and terminal facts; provider retains its result. |
| Identity | One scoped attempt key binds order, currency, amount, and operation kind through recovery. |
| Coordinator | Application sequences prepare/call/finalize; domain checks transitions; store enforces the local commit boundary. |
| Authorization | Baseline recovery leaves caller policy open; the separate authorization case supplies a policy. |
| Access | Commands carry immutable facts; observations are detached and have no mutation privilege. |
| Horizon | Retain identity/fingerprint through the recovery window; refresh stale state before installation. |
| Execution | Preparation, provider work, and finalization have separate effect boundaries. Coordinate overlapping local updates. |
| Failure | Keep Pending after uncertain or partially successful work; inspect/reconcile the same attempt. |

## Decisions before mechanisms

Choose how intent and terminal state/event survive failure; how competing
writers recognize the same attempt; and what the provider guarantees about
key retention, fingerprint conflicts, and authoritative lookup. A key name or
interface alone supplies none of those guarantees.

[Technology selection](../../docs/technology-selection.md) provides questions
for alternative stores and execution models. If atomic local state/event
installation is unavailable, a new protocol or changed contract is necessary.

## Implementations and evidence

The existing [in-memory laboratory](README.md) implements the bounded case in
Java composition, Java Template Method, and Rust composition. The
[PostgreSQL laboratory](postgres/README.md) adds durable coordination and
restart checks. The [HTTP laboratory](http/README.md) adds request validation,
overlap, and response-loss scenarios.

Those are reference realizations with different evidence boundaries. The
persistent simulator puts application and provider records in one physical
storage domain; it does not establish a real external provider's durability.
See [implementations](../../docs/implementations.md) and
[Claims and limits](../../docs/claims-and-limits.md).

Continue with [authorization and revocation](authorization/DESIGN.md),
then compare the [filled architecture decision](adoption/architecture-decision.md)
and [design review](adoption/design-review.md).
