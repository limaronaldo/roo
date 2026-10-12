# Design case: permission observation and revocation

A caller observes permission to act on an order. Permission is then revoked
before execution. Decide what execution may do and what survives if revocation
occurs after an earlier effect. This case is independent of HTTP headers,
language access rules, and database locking syntax.

The [Authorization field](../../../docs/02-relationship-design.md#21-the-eight-field-relationship-contract)
asks each project to choose its policy and decision boundary. The policy below
is a selected teaching contract, not a universal rule for every system.

## Selected policy

Each request names one principal, scope, and operation. Observation is advisory
and reserves no future permission. Each protected local phase decides against
current policy and coordinates that decision with its effect and revocation.
An accepted phase may commit before a waiting revocation; later phases must
make a new decision. Revocation does not undo earlier commits.

Policy permission and memory access are separate. A reference, identity key,
or detached status value does not itself authorize an operation. Authentication
is a separate prerequisite in a real system; the laboratories use synthetic
principal inputs.

## Relationship Contract

| Field | Decision |
|---|---|
| Custodian | Policy custodian retains grants/denials; business custodian retains state and recovery intent. |
| Identity | Principal, scope, and operation identify policy; payment/refund identity separately binds immutable effect facts. |
| Coordinator | A protected-phase coordinator orders the current decision and effect against revocation. |
| Authorization | Deny absent permission for the named operation; observation confers no continuing permission. |
| Access | Detached observations and immutable requests expose no reusable execution permit. |
| Horizon | Policy may change after observation; retained intent survives the declared recovery window. |
| Execution | Serialize or otherwise coordinate revocation with each protected phase at the chosen boundary. |
| Failure | Denial adds no effect in that phase; prior effects remain and need currently authorized recovery. |

## Counterexamples to check

| Schedule | Required result under this policy |
|---|---|
| Observe allow; revoke; execute | Execution denies without a new phase effect |
| Observe deny; grant; execute | Execution makes a fresh decision and may proceed |
| Execute enters its protected boundary; revocation waits | Accepted phase may finish; later phases recheck |
| Grant one operation; request another | Deny the ungranted operation |
| Revoke after intent preparation | Preserve intent; deny later unpermitted work |
| Revoke after provider effect | Preserve the effect and uncertain local state; do not fabricate completion |
| Recover with reconciliation permission | Inspect/finalize the original intent; create no new intent or provider effect |
| Restart during recovery | Retain the declared identity/policy state and resume under current permission |

The process-local example exercises a smaller approval decision. Persistent
payment phases and restart outcomes require separate storage and protocol
evidence. Another authorization policy may deliberately choose a different
admission horizon; document that as a different contract.

## Reference mechanisms and limits

The [process-local Java/Rust example](README.md) coordinates approval and
revocation under one local lock. The [persistent HTTP implementation](../http/AUTHORIZATION.md)
uses operation policy rows and transaction-level PostgreSQL locking. Its
precise permission tokens, routes, retained tombstones, response codes, and
shared tests belong to that implementation contract.

A separate policy service or another store would need its own ordering,
unavailability, retention, and recovery design. No alternative backend is
implemented or qualified by this page. Use
[technology selection](../../../docs/technology-selection.md) and record the
tradeoff in an [architecture decision](../../../templates/architecture-decision.md).
