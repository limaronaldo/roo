# ROO policy exercises

Work from the repository root and edit only the starter policy files:

- Java: [`java/starter/roo/payments/LearnerPolicy.java`](java/starter/roo/payments/LearnerPolicy.java)
- Rust: [`rust/starter/src/learner.rs`](rust/starter/src/learner.rs)

The shared input parser and runner are in [`java/common/roo/payments/`](java/common/roo/payments/)
and [`rust/shared.rs`](rust/shared.rs). Read them to understand the boundary;
leave the shared parser, adapters, scenarios, and verifier unchanged. The
completed examples are separate files under [`java/solution/`](java/solution/)
and [`rust/solution/`](rust/solution/). Do each exercise independently and use
the observed inputs rather than a fixture label or an expected answer.

The starter compiles but returns `stop` for all six gaps. For the first check,
`--expect-incomplete` lets the evaluator require that specific behavioral red.
Remove the flag after implementing the selected group. A `BEHAVIOR eN:` failure
means the learner action or its resulting state is wrong. Invalid arguments,
malformed policy output, compiler errors, unavailable dependencies, database
errors, server startup failures, or a missing observed barrier are separate
failures; do not count them as the expected starter red.

## e1: Forward a line and let the domain validate it

**Learning objective:** keep policy decisions separate from domain validation,
and preserve a caller's requested values even when the domain must reject them.

For phase `add`, return `add:UNIT:QUANTITY` using the supplied `unit` and
`quantity`. Do not filter zero, negative, or overflowing requests in the
policy. The existing application must decide whether a line is valid and keep
the exact committed order unchanged after rejection. The native checks cover
invalid quantity, invalid unit price, multiplication overflow, and sum
overflow. They also vary valid starting lines and a valid requested addition.

**Hint:** do not calculate a replacement total or hardcode the example total.
Forward both caller values unchanged. The test observes line facts, state,
total, and effects after the domain action.

## e2: Recover a persisted pending payment

**Learning objective:** distinguish a stable operation identity from the
latest result string, then resolve the same intent through the caller's lookup
availability.

For phase `recover`, request `reconcile:LOOKUP:none` only when the latest
observation is Pending and includes a persisted `payment_id`. Otherwise return
`inspect`. A successful lookup can finalize the already approved effect using
that identity. An unavailable lookup stays Unknown and leaves Pending, the
identity, charge count, and event count unchanged.

**Hint:** the evaluator first establishes Pending, a committed intent, one
provider effect, and no terminal event. It then invokes the policy. The native
cases vary the identity and amount and include an unavailable lookup. Use the
`lookup` field; do not assume that a previous result such as
`LocalCommitFailed` proves the provider has no effect.

## e3: Retry without replacing the active identity

**Learning objective:** keep a retry attached to the operation the caller
requested and let the domain enforce intent and provider fingerprint rules.

For phase `retry`, return `pay:REQUESTED_ID:approve:none` when
`requested_payment_id` is present. If it is `-`, return `inspect`. After a
timeout following provider approval, a retry with the same ID can finalize the
existing effect. A changed ID while Pending must reach the existing domain and
be rejected as an intent conflict without changing the saved intent or charge.
A separate probe checks that a changed request fingerprint is rejected as a
key conflict; it does not add a new public policy action.

**Hint:** pass through the requested ID. Do not substitute the persisted ID,
invent a new ID, or make a policy decision from the example amount. The policy
chooses the caller's next action; the application and provider adapters enforce
the identity contract.

## e4: Redeliver a pending outbox fact

**Learning objective:** treat event delivery and acknowledgement as a separate
failure boundary, and rely on the consumer's event identity for safe
redelivery.

For phase `redeliver`, return `relay:ok` when `pending_outbox` is positive and
`stop` when it is zero. The exercise first commits a payment event, delivers
its fact to the consumer, and loses the acknowledgement. Redelivery must clear
the pending count without applying a second consumer fact or changing the
event's identity and contents.

**Hint:** the consumer already owns deduplication. Do not create a second event
or try to synthesize event facts in the learner policy. Rust's shared exercise
contract checks the public ID deduplication guarantee.

## e5: Inspect uncertainty, then recover after process and database failure

**Learning objective:** separate the caller's uncertain observation from
committed database facts, and recover a stable intent across process death and
a bounded PostgreSQL restart.

There are two policy phases. In `uncertain_commit`, return `inspect`; do not
replay payment or line work. After the evaluator obtains a fresh snapshot, in
phase `recover` request `reconcile:LOOKUP:none` only if that snapshot is Pending
with a persisted payment ID. Otherwise return `inspect`.

The PostgreSQL exercise also witnesses actual overlap: a pay operation holds
the order row while a competing add waits, then the add is rejected after pay
commits. At the `after_effect` gate, the provider transaction has committed
but the final application transaction has not started. The harness sends
SIGKILL to that pay process. A fresh process must then observe Pending with the
same `p1`, one charge, and no event. Inspection is a separate observation; the
exercise does not inject an actually uncertain PostgreSQL COMMIT.

With `--variant all`, the harness keeps one synthetic scope for each of the
three implementations, then performs one immediate PostgreSQL stop and restart
for all three. It checks a changed server start time, WAL redo, and unchanged
normalized snapshots. The restarted runners then obtain fresh Pending
observations and use the recovery decision. With one selected variant, the same
bounded sequence runs for that variant. This is evidence for the observed local
PostgreSQL setup and recovery scope, not physical power loss or an external
payment system.

**Hint:** the pay/add check uses an observed lock wait, not a sleep. The
`after_effect` gate names exactly what has committed before the process is
killed. Preserve the identity from the fresh snapshot; do not infer database
state from the old process or the action result.

## e6: Recover a lost HTTP response by identity or inspection

**Learning objective:** choose recovery according to operation semantics: a
payment has a stable replay identity, while line addition has no durable replay
receipt.

For `payment_response_lost`, use the persisted `payment_id` when present, or
`requested_payment_id` when no intent exists. Return the same-ID
`pay:ID:approve:none`; if neither ID exists, return `inspect`. The server has
already committed the payment and a snapshot when it is killed before sending
response headers. A fresh server sees Paid, and replay with the same identity
returns `AlreadyApplied` without a second charge. A changed payment ID conflicts
with the retained intent.

For `line_response_lost`, return `inspect`. The fresh GET shows the committed
Draft total of 300. At `line_inspected`, return `stop`; the policy transcript
must not automatically send another line POST. The harness makes a separate,
explicit caller action afterward to demonstrate that a second `add:50:1`
reaches 350 because the line endpoint has no durable replay receipt. That
separate action demonstrates the boundary; it is not a retry selected by the
learner policy.

The HTTP exercise also includes a timeout after provider approval. HTTP 202
does not start a background worker. A separate explicit harness/caller action
requests reconciliation of the persisted intent and verifies Paid with one
charge and one event. This supplementary demonstration does not invoke e2's
learner policy: implementing e6 requires only its three phases above.

**Hint:** the response is lost after action and snapshot but before headers.
Connection loss alone says nothing about rollback. Preserve payment identity;
inspect line state before a human or other caller explicitly decides whether
to append again.

## Compare the completed examples

Read the implementations only after trying each decision. The same neutral
policy appears in three realizations:

| Concern | Java composition | Java Template Method | Rust composition |
|---|---|---|---|
| Learner decisions | [`LearnerPolicy.java`](java/solution/roo/payments/LearnerPolicy.java) | Same policy source, exercised through the inherited application | [`learner.rs`](rust/solution/src/learner.rs) |
| Reuse shape | Constructor supplied store and provider capabilities | Final public workflow and finalization are reused; subclasses provide stable store and provider hooks | Concrete adapters are composed; there is no implementation inheritance |
| Local access rule | Encapsulated objects and port contracts | Hook implementations must keep the shared workflow contract | The application holds exclusive mutable borrows of its adapters for its active lifetime |
| What still owns correctness | Domain, application, and adapters validate transitions and effects | Domain and adapters still own the same invariants; inheritance only controls workflow reuse | Domain and adapters still own the same invariants; borrowing restricts local access and aliasing |

Template Method is a legitimate choice when a shared final workflow should be
reused and only stable capabilities vary. It does not make provider behavior
honest or replace a transaction contract. Rust borrowing gives the composed
application a different local access guarantee; it does not provide rollback
for a remote effect. The policy outcome can match across these variants without
requiring identical class or type structures.

For the neutral reasoning behind these choices, return to the [seven-field
worksheet](../../../templates/relationship-contract.md) and the [filled case
contract](../adoption/relationship-contract.md). The comparison is limited to
the checked exercises. Matching outputs do not establish universal equivalence
or a production guarantee.
