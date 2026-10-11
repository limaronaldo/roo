# ROO design review

ROO (Relationship & Ownership Oriented design) is language-independent. Review one use case and its relationships against observable requirements; start with behavior and the invariant, then inspect traits, interfaces, or class hierarchies only after defining the behavior a boundary must preserve. Do not score a design by counting patterns or compiler errors.

| Review question | Evidence to inspect |
|---|---|
| What scenario, invariant, allowed outcome, forbidden outcome, and failure case define this review? | Use case, relationship decisions, and expected results |
| What behavior must a boundary provide to its callers? | Requests, results, state changes, error behavior, and retry or idempotency rules |
| Does each important relationship name its resource custodian and domain invariant coordinator separately? | Relationship Contract and data flow |
| Does a target need durable identity beyond a current value or object lifetime? | Identity scope, version, reuse, deletion, and lookup rules |
| Are invariant coordination and business authorization explicit? | API, permissions, storage model, and use case |
| Are access, aliasing, validity, and transfer decisions clear before choosing language mechanisms? | Relationship Contract and boundary crossings |
| Can callers bypass an invariant through fields, mutable views, setters, or reconstruction? | Visibility, mutation operations, and scenario evidence |
| Does the execution boundary preserve the whole invariant under overlap? | Coordination, transaction, or serialization boundary and concurrent scenario |
| What happens on stale lookup, invalid input, cancellation, or partial external failure? | Negative behavior, recovery path, and observed results |
| After the behavior is defined, do traits or interfaces expose the needed operations, and do implementations preserve their shared contract? | Port contract, implementations, and shared behavioral checks |
| Does a hierarchy provide needed reuse, substitutability, or variation? | Alternatives and concrete extension scenario |
| Can another language preserve the same relationship decisions with its own mechanisms? | Neutral contract and per-language enforcement limits |

## Evidence

Use the evidence categories and boundaries in [Claims and limits](../docs/claims-and-limits.md).
Inspect the concrete check and its source candidate, rather than transferring
a guarantee from compilation to storage, protocol behavior, or policy.

Classify findings as a demonstrated defect, an unverified question, or an optional improvement. Include the violated requirement and a concrete scenario. Review code and sources directly rather than relying only on the author's description.
