# Relationship Contract: payment finalization recovery

Use with the [worksheet](../../../templates/relationship-contract.md),
[adoption guide](../../../docs/09-adoption-guide.md),
[architecture decision](architecture-decision.md), and [design review](design-review.md).
The [canonical method](../../../docs/02-relationship-design.md) defines the fields.

## Scenario

The shared `recover_commit` scenario starts with Draft order `O1`.
The actions `add:100:2;add:50:1;pay:p1:approve:commit;reconcile:ok:none`
produce a total of 250 minor units in USD. The provider approves `p1`, but
the injected terminal local commit fails.

At that failure point, committed local state must remain **Pending**, with one
independent provider charge and zero terminal events. Reconciliation of the
same persisted attempt must reach **Paid**, still one charge, with exactly one
`payment:p1` event. A new recovery key or an uncommitted Paid response would
violate the contract.

This record covers `Coordinator -> LocalStore` and
`Coordinator -> RemoteProvider` for one payment invariant. Event delivery
crosses another acknowledgement boundary and needs its own contract.

## Compact record

```text
Relationship: Coordinator -> stored intent and independent provider
Invariant: local terminal state and event commit together; recovery adds no charge
Custodian: store retains order/intent/outbox; provider retains its effect record
Identity: p1 binds O1, USD, 250, and operation kind; payment:p1 names the event
Coordinator: application orders prepare/call/finalize; domain validates transitions
Authorization: absent in the teaching case; caller policy is required for live use
Access: read committed intent, construct detached candidates, send immutable facts
Horizon: intent remains fixed through recovery; observations can become stale
Execution: short app transactions; provider commits in an independent transaction
Failure: final commit failure retains Pending and charge; reconcile p1, never replace it
Evidence: shared oracle and separate in-memory, PostgreSQL, and HTTP validation records
Open: real-provider retention, authorization, cancellation, deletion, and operations policy
```

## Decisions that make recovery possible

**Persist before the effect.** Preparation freezes the amount and intent before
the provider call. Failed preparation produces no charge. The request key
recognizes the full immutable fingerprint; same key with different facts is
`KeyConflict`, rather than permission to change a previous operation.

**Commit local state and event together.** Work on a detached candidate.
Failed finalization discards both candidate state and event while the provider
effect survives. Recovery loads the stored intent; it does not reconstruct a
new request from mutable order data.

**Treat uncertainty as a state.** Unknown differs from decline and from
NotFound. In this simulator, NotFound is authoritative only because complete
provider-key retention is part of its contract. A real provider must document
its equivalent lookup and retention guarantees.

**Separate the three clocks.** A candidate's memory lifetime can end while
the business intent remains Pending. A returned status snapshot can stay
memory-valid and already be stale. Revalidate the persisted intent under the
store's coordination boundary before finalizing.

**Separate permission from access.** Fixture validation, scope keys, and
loopback restrictions do not implement customer or operator authorization.
A real service must authenticate the caller and check pay/refund permission
and revocation at its declared boundary.

## The same decisions in Java and Rust

| Realization | Mechanism | Obligation retained |
|---|---|---|
| [Java composition](../java/src/roo/payments/CompositionApplication.java) | Final store/provider references, private domain mutation, immutable request records, detached load/commit | Application fixes prepare/call/finalize ordering; references do not make remote effects local |
| [Java Template Method](../java/src/roo/payments/TemplateApplication.java) | Final public workflows and private finalization; protected hooks supply stable adapters | Subclasses preserve the port contract and cannot reorder the public workflow |
| [Rust composition](../rust/src/application.rs) | Temporary exclusive borrows of capabilities; copied persisted request facts before provider mutation | Borrow checking restricts local overlap; runtime identity/state checks and independent-effect recovery remain necessary |
| [PostgreSQL](../postgres/SPEC.md) | Order-row locks, fresh reload/revalidation, separate short app/provider transactions, atomic state/outbox writes | Other processes coordinate at PostgreSQL; no app transaction spans the provider call |
| [HTTP](../http/SPEC.md) | Validated owned input, bounded admission, natural operation IDs, existing persistent workflow | A lost response requires same-identity recovery or inspection, not blind replay |

Java inheritance and Rust composition can satisfy the same contract. Their
reuse and access mechanisms differ; neither replaces provider idempotency,
database atomicity, or caller policy.

## Adjacent boundaries

For event delivery, the consumer can commit before the app records its
acknowledgement. Redelivery compares EventId and event fingerprint so an
identical fact is applied once. That is a separate boundary from payment
finalization.

An HTTP response is an observation, not a durable command receipt. It may
include another worker's later commit. Payment/refund retries reuse a natural
operation ID; line addition has no replay receipt and is explicitly
non-idempotent. An uncertain line POST requires inspection and a caller
decision. Do not extend payment retry semantics to every endpoint.

The persistent simulator stores app, provider, and inbox records in one
PostgreSQL/WAL domain. Their transactions commit independently, but that setup
does not model a real external provider's physical durability.

## Evidence to inspect

| Boundary | Requirement or source | Dated execution record |
|---|---|---|
| Local failure and recovery | [Specification](../SPEC.md), `commit_failure`/`recover_commit` in [expected.tsv](../expected.tsv), [Rust assertions](../rust/src/application.rs) | [In-memory validation](../../../research/orders-payments-validation.md) |
| Competing writers and restart | [Persistent specification](../postgres/SPEC.md), locked fresh-row transitions | [PostgreSQL validation](../../../research/postgres-validation.md) |
| Response loss and same-identity recovery | [HTTP specification](../http/SPEC.md), including non-idempotent line POST | [HTTP validation](../../../research/http-validation.md) |
| Hosted adoption track | [Track specification](../track/SPEC.md) | [Hosted reproduction](../../../docs/10-github-reproduction.md) |

These links identify earlier runs; this worksheet itself reports source and
contract inspection. Refer to [claims and limits](../../../docs/claims-and-limits.md)
for common evidence boundaries and omitted production requirements.

## Decision to carry into a real project

Keep the recovery identity and immutable request facts durable before the
external effect. Give finalization a coordinator at the actual transaction
boundary. Add the missing caller policy and verify the provider's guarantees
before accepting the live design. Record unresolved assumptions in the
architecture decision rather than treating a compiler result as acceptance.
