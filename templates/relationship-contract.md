# Relationship Contract worksheet

Use this worksheet for one relationship or a small group governed by the same invariant. ROO (Relationship & Ownership Oriented design) is language-independent: start with the scenario and invariant, then make relationship decisions before choosing types, APIs, storage, or synchronization. This is a design aid, not a compiler annotation or formal proof. Keep resource custody (retention and release), domain responsibility (invariant-preserving decisions), stable identity (recognition across lifetimes), and authorization (permission to request an operation) separate.

## Context

- Scenario or operation:
- Expected outcome, forbidden outcome, and relevant failure:
- Relationship: `Source → Target` (cardinality):
- State that must agree and the invariant it must preserve:
- Domain responsibility / invariant coordinator: which participant decides changes that must preserve the invariant?
- Value, entity, resource, service, or event; independent lifecycle, if any:

## Seven fields

| Field | Language-neutral decision | Questions to answer |
|---|---|---|
| Owner / resource custodian | | Who retains the resource and handles its local lifecycle, release, or cleanup? Custody does not by itself grant authority to change domain state. |
| Stable identity | | Does the target need an identity beyond its current value or lifetime? If so, state its scope, version, reuse, and deletion rules. A reference or storage address is not durable identity. |
| Mutation authority | | Which operation changes state, and who is responsible for preserving the invariant at that transition? Record who may request it as a separate authorization decision. |
| Access regime | | What interaction is required: observe, resolve, request a change, share state, or transfer facts? Which aliases or overlapping access are allowed? Defer language mechanisms to realization. |
| Validity horizon | | When is access valid, stale, or revoked? Distinguish memory lifetime, business lifecycle, freshness, and cancellation. |
| Execution domain | | Where must overlapping operations be coordinated: one operation, task or thread, process, service, or transaction? |
| Failure boundary | | Which effects may survive failure? Who handles rollback, compensation, retry, cancellation, uncertainty, or redelivery? |

## Supporting decisions

- Authorization: who or what may request each operation, its scope, and how permission is checked or revoked:
- Creation, replacement, deletion, release, and cleanup responsibilities:
- Reverse navigation: is it needed, and who maintains the relation or index?
- Identity resolution: behavior for a missing, stale, version-mismatched, or unauthorized target:
- Consistency: which state must agree, and at what observation boundary (local invariant, transaction, eventual agreement, or snapshot)?
- Boundary crossing: which facts or identities cross a process, persistence, or wire boundary?
- Cancellation and retry: which state and resources remain, and is repetition idempotent?
- Resource budget: queue capacity, retained snapshots, lock duration, allocation, and cleanup limits:

## Optional realization and enforcement

Complete this section only after the neutral decisions above. Choose relevant implementation approaches; no Rust representation is required. A database foreign key does not determine an in-memory representation.

| Candidate realization | What it may express | Cost or obligation | Selected? |
|---|---|---|---|
| Embedded owned value | | | |
| Temporary shared or exclusive view | | | |
| Stable ID and resolver | | | |
| Independent snapshot or copy | | | |
| Owned message or command | | | |
| Explicit shared ownership and coordination | | | |

## Cross-language interpretation

Keep the relationship decision stable while mapping it to each relevant language, runtime, store, or protocol. A mapping may differ by platform; do not require every implementation to reproduce another language's type shapes.

| Language, runtime, store, or protocol | Realization chosen | Enforcement and limits |
|---|---|---|
| | | |

## Observed evidence

Record evidence that was actually observed, with a link or artifact reference where available. Use only the categories relevant to this relationship.

- Compiler or static analysis:
- Runtime or behavioral scenario:
- Database or transaction behavior:
- Protocol or boundary behavior:
- Human review or operational decision:

## Remaining assumptions and open questions

- Assumptions, unverified claims, and unresolved decisions:
