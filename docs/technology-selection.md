# Choose technologies from the contract

ROO is independent of programming language, runtime, database, and protocol.
That independence means starting with obligations and evaluating mechanisms
against them. It does not make technologies interchangeable or transfer
qualification from one implementation to another.

## State the required behavior first

Use the [eight fields and six steps](02-relationship-design.md). Keep the
invariant and permitted failure outcomes fixed while comparing candidates.
If an alternative needs a weaker promise, record a changed contract and its
consequences in an [architecture decision](../templates/architecture-decision.md).
Do not hide that change behind an adapter interface.

| Obligation | Questions for a candidate implementation |
|---|---|
| Custody | What retains data/resources, releases them, and survives restart? |
| Identity | What scopes a key, prevents conflicting reuse, and retains its fingerprint? |
| Coordination | Where are competing changes prevented or detected? |
| Authorization | Where does current policy order with effects and revocation? |
| Access | What observations, commands, aliases, and transfers cross the boundary? |
| Horizon | What expires, becomes stale, or must be revalidated? |
| Execution | Which operations may overlap, suspend, retry, or continue after a caller leaves? |
| Failure | Which effects remain, and how are they inspected, retried, or reconciled? |

## Evaluate storage and execution alternatives

These are design candidates, not a list of supported backends. Determine the
actual product, configuration, and failure behavior before accepting a row.

| Candidate family | Contract questions to resolve |
|---|---|
| Local memory | Is single-process retention sufficient? Who coordinates concurrent access, and what is lost on restart? |
| Relational storage | Which changes share an atomic commit? What isolation, uniqueness, policy ordering, and restart behavior apply? |
| Document or key/value storage | Which keys/documents can change together? Can conditional updates coordinate policy and effects, and how are conflicts recovered? |
| Append-only event storage | What orders appends and detects conflicting versions? How are replay, projection freshness, schema evolution, and external effects handled? |
| Single-coordinator or actor execution | Who retains durable intent? What do queue admission, acknowledgement, coordinator failure, and retry mean? |
| Separate policy service | How does a policy decision remain applicable at the effect boundary? What happens during policy unavailability, partition, or revocation? |

For the [payment design case](../case-studies/orders-payments/DESIGN.md), an
adapter must preserve intent identity and the promised state/event boundary.
If those writes cannot commit together, introduce an explicit recovery protocol
or revise the invariant. For [authorization](../case-studies/orders-payments/authorization/DESIGN.md),
a policy cache or earlier allow result needs a stated validity and revocation
contract; it cannot silently replace the selected decision boundary.

## Compare languages without importing their syntax into the method

Local retention may use garbage collection, deterministic resource scopes,
borrowing, handles, or another mechanism. Record what must remain valid and
who may change it before choosing that mechanism. Inheritance and composition
are options for realizing behavior and reuse; both need the same observable
contract when offered as alternatives.

The [cross-language guide](06-cross-language.md) and
[Rust mapping](rust-relationship-mapping.md) describe particular translations.
Neither a local reference nor exclusive local access establishes durable
coordination or caller authorization by itself.

## Carry scenarios and collect new evidence

For each candidate, test allowed transitions and relevant counterexamples:
conflicting reuse, stale observations, competing updates, revocation before
execution, failure after an external effect, restart, and lost acknowledgement.
Report the actual commit, environment, checks, and remaining assumptions.
Equivalent expected outcomes make a comparison useful; they do not imply
identical internals or exhaustive coverage.

The repository currently has Java and Rust reference implementations with
PostgreSQL persistence and HTTP adapters. Other storage/runtime families above
are evaluation paths, with no executable backend or qualification claimed here.
See [implementations](implementations.md) and [Claims and limits](claims-and-limits.md).
