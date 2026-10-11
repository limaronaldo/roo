# ROO design review

ROO (Relationship & Ownership Oriented design) is language-independent. Review one use case and its relationships against observable requirements; start with behavior and the invariant, then inspect traits, interfaces, or class hierarchies only after defining the behavior a boundary must preserve. Do not score a design by counting patterns or compiler errors.

| Review question | Evidence to inspect |
|---|---|
| What scenario, invariant, allowed outcome, forbidden outcome, and failure case define this review? | Use case, relationship decisions, and expected results |
| What behavior must a boundary provide to its callers? | Requests, results, state changes, error behavior, and retry or idempotency rules |
| Does each important relationship name its resource custodian and domain invariant coordinator separately? | Relationship Contract and data flow |
| Does a target need durable identity beyond a current value or object lifetime? | Identity scope, version, reuse, deletion, and lookup rules |
| Are mutation authority and business authorization explicit? | API, permissions, storage model, and use case |
| Are access, aliasing, validity, and transfer decisions clear before choosing language mechanisms? | Relationship Contract and boundary crossings |
| Can callers bypass an invariant through fields, mutable views, setters, or reconstruction? | Visibility, mutation operations, and scenario evidence |
| Does the execution boundary preserve the whole invariant under overlap? | Coordination, transaction, or serialization boundary and concurrent scenario |
| What happens on stale lookup, invalid input, cancellation, or partial external failure? | Negative behavior, recovery path, and observed results |
| After the behavior is defined, do traits or interfaces expose the needed operations, and do implementations preserve their shared contract? | Port contract, implementations, and shared behavioral checks |
| Does a hierarchy provide needed reuse, substitutability, or variation? | Alternatives and concrete extension scenario |
| Can another language preserve the same relationship decisions with its own mechanisms? | Neutral contract and per-language enforcement limits |

## Evidence classes

Treat these sources separately; evidence in one class does not establish claims in another.

| Evidence class | What it can support | Limit to record |
|---|---|---|
| Compiler or static analysis | Checked type, visibility, or access properties of the analyzed program | Does not establish domain correctness, authorization, runtime behavior, or external effects |
| Runtime or behavioral evidence | Observed outcomes for the executed scenarios and conditions | Does not cover unobserved states or prove every interleaving |
| Database or transaction evidence | Constraints, isolation, atomicity, and durability in the examined database setup | Does not establish end-to-end behavior across an unexamined service or provider |
| Protocol or boundary evidence | Encoded inputs and outputs, rejection behavior, and tested delivery semantics | A schema alone does not prove domain correctness or durable effects |
| Human review or operational decision | Explicit assumptions, policy choices, and reviewed tradeoffs | Is not execution evidence for behavior or infrastructure guarantees |

Classify findings as a demonstrated defect, an unverified question, or an optional improvement. Include the violated requirement and a concrete scenario. Review code and sources directly rather than relying only on the author's description.
