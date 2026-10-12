# Authorization at execution

A caller observes permission to approve an order. An administrator revokes it
before the caller executes. The order must stay `Draft`, with zero approvals.
Java and Rust implement this same decision in a small, in-memory example.

This slice isolates caller authorization from the existing payment simulations.
Order approval here changes local business state; it is not card authorization
or a call to a payment provider. The PostgreSQL and HTTP cases keep their
existing behavior and authorization limitations.

## Relationship Contract

**Relationship:** Principal → Order approval. **Invariant:** only a currently
permitted principal can install `Draft → Approved`, at most once per order.

| Field | Decision |
|---|---|
| Custodian | One coordinator retains local orders and the policy registry. Callers receive detached values. |
| Identity | Synthetic principal and order strings are exact-match keys. Possessing an ID grants no permission. |
| Coordinator | `approve` checks permission, checks order state, and installs one transition under a single lock. |
| Authorization | Deny by default. An explicit `(principal, order)` grant permits only approval. Read current policy on every execution, including duplicates. |
| Access | The coordinator exposes operations and snapshots, never its mutable maps. Observation is a hint, not a capability or credential. |
| Horizon | Policy lasts until revoked or process exit. Observations may become stale immediately. Revocation does not undo completed approvals. |
| Execution | Policy changes and approval use the same process-local lock. No external calls, callbacks, or suspension occur inside it. |
| Failure | Denied, missing-order, and duplicate requests leave order state unchanged. Rust lock poisoning returns `Unavailable`; the runner fails. |

**Evidence:** [shared command traces](cases.tsv), [shared expected results](expected.tsv),
and equivalent native thread tests. The oracle is project-authored; it is kept
separate from both implementations, not supplied to either fixture runner.
**Open:** authenticate principals and establish a shared policy/commit boundary
before applying this rule across services or durable stores.

## When revocation takes effect

The execution decision uses current policy while holding the lock that also
protects the order transition. The successful state replacement is the approval's
linearization point: the instant it takes effect relative to other operations.
Revocation takes effect when its registry entry is removed under that same lock.

```mermaid
sequenceDiagram
    participant Caller
    participant Coordinator
    participant Administrator
    Caller->>Coordinator: observe(alice, order-1)
    Coordinator-->>Caller: allowed (detached observation)
    Administrator->>Coordinator: revoke(alice, order-1)
    Coordinator-->>Administrator: revoked
    Caller->>Coordinator: approve(alice, order-1)
    Coordinator-->>Caller: Forbidden; order remains Draft
```

- A revocation that completes before execution denies it, even after an
  `allowed` observation. A queued request receives no exemption.
- If approval acquires the lock first, it may complete before revocation.
  Revocation waits and then affects later requests. Returning from `observe`
  does not reserve a place in this ordering.
- Regranting before execution permits a fresh decision. This design does not
  issue permits bound to a policy version. An earlier `denied` observation
  similarly cannot overrule a new grant.
- Permission is checked before order lookup. An unpermitted request receives
  `Forbidden` for both an existing and a missing order. A permitted missing
  order returns `NotFound`; a permitted duplicate returns `AlreadyApproved`.

Checking outside the critical section and then locking only for mutation would
leave a gap in which a revocation could complete before an obsolete decision
was used. Private fields and correct order invariants alone do not close it.

## The same design in Java and Rust

| Decision | Java | Rust |
|---|---|---|
| Retain state without exposing mutation | `final Coordinator`, private maps and lock | `Coordinator`, private `State` inside `Mutex` |
| Serialize policy and business state | One `synchronized (lock)` section | One `MutexGuard` spanning check and replacement |
| Return detached observations | Immutable records | Copied values, with no borrowed guard or state reference |
| Reject expected operations | `Outcome` enum | `Result<(), Error>` |
| Share the coordinator between callers | Threads share its reference | Scoped threads share `&Coordinator`; the mutex permits interior mutation |

Both implementations use composition. A superclass or trait would not establish
caller permission. Rust's exclusive guard prevents simultaneous access to this
state, but the code must still check the right principal, operation, and order.
Java's monitor enforces the same local ordering; records prevent callers from
editing returned observations. Neither mechanism authenticates a principal.

## Run the equivalent tests

From the repository root, with Python 3.10+, JDK 21+, and Rust 1.96+:

```sh
python3 case-studies/orders-payments/authorization/verify.py
```

No dependencies are downloaded. Java compiles for release 21 with all warnings
treated as errors. The verifier runs four native tests per language, then
compares all 53 checkpoints in 14 scenarios against the same oracle, including
both orders' status and approval count after every command.
The scoped-revocation case approves the second order while the same principal's
grant on the first order is revoked, checking both isolation and a positive path.

Three thread tests use explicit synchronization, without sleeps: observation
then revocation then execution; execution then revocation; and competing
approvals, where exactly one succeeds. A fourth test checks detached values.
Timeouts bound failed schedules; they do not decide whether revocation won.
The [authorization workflow](../../../.github/workflows/authorization.yml)
runs these checks, the full root Rust suite, formatting, and Clippy on Linux.

## Boundaries

Principal identities, `grant`, `revoke`, and diagnostic `snapshot` access are
trusted fixture inputs. They are not public HTTP endpoints. There is no identity
provider, tenant model, policy service, expiry, permission cache, or protection
against a malicious administrator. Only the `approve` operation is modeled.

Policy and orders are process-local and disappear on restart. This example
does not add authorization to the existing PostgreSQL or HTTP implementations.
A separately committed database write or provider effect would require an
explicit cross-boundary policy; a local mutex cannot serialize either one.

Rust's poisoned-lock failure has no Java monitor equivalent. Java fatal runtime
failures propagate; neither implementation provides crash rollback or availability
guarantees. Passing the paired scenarios demonstrates these specified outcomes,
not every thread interleaving or production security. See
[Claims and limits](../../../docs/claims-and-limits.md).
