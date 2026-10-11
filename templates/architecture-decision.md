# Architecture decision: [title]

Status: proposed / accepted / superseded. Date: [date]. Owner: [role].

ROO (Relationship & Ownership Oriented design) is language-independent; record relationship decisions before their platform realization.

## Problem and invariant

Describe the concrete operation, participants, state it touches, required behavior, and failure the design must prevent. Record the allowed and forbidden outcomes and the observation boundary for the invariant.

## Relationship Contracts

Link the affected contracts. State the domain responsibility for preserving each invariant separately from resource custody, durable identity, authorization, and transaction scope.

## Alternatives

| Alternative | Invariant preservation | Extensibility | Lifecycle / concurrency | Operational cost |
|---|---|---|---|---|
| | | | | |

## Decision and reasons

Record the language-neutral decision first: who coordinates the invariant, what needs independent identity, who is authorized to request each change, how participants access or transfer information, when it remains valid, where operations are coordinated, and what may happen on failure. Explain why this policy fits and what evidence or requirement would cause it to change.

## Optional realization

After the neutral decision, record the implementation choices that matter for the target language, runtime, store, or protocol. Specify public operations and their observable effects. Describe consuming, borrowing, copying, lookup, or ownership transfer only when those concepts apply to the chosen platform; they are realization choices, not the relationship decision.

| Layer, language, runtime, store, or protocol | Realization | Enforcement or constraint |
|---|---|---|
| | | |

## Failure and recovery

State rejected-input behavior, partial effects, cancellation, retry, cleanup, and delivery semantics. Distinguish local rollback from external compensation.

## Evidence and limits

Separate evidence by what it can establish:

- Compiler or static analysis:
- Runtime or behavioral evidence:
- Database constraints, transactions, and durability:
- Protocol, wire, or remote-boundary behavior:
- Human review and operational assumptions:
- Sources and established precedent:
- Remaining assumptions, untested properties, and risks:

## Consequences

State benefits, costs, migration steps, and rollback options. Record the scope of acceptance; passing tests alone does not accept an architectural tradeoff.
