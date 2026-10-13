# 1. Foundations: objects with explicit relationships

ROO — Relationship & Ownership Oriented design — is a proposed software design
method independent of programming language, runtime, database, and protocol.
Describe a scenario and its invariants, decide what each important relationship
means, then choose mechanisms that uphold those decisions.

Ownership here includes resource custody and lifecycle responsibility. A
language's ownership system is one possible enforcement mechanism. The
[canonical contract](02-relationship-design.md) defines eight fields and one
six-step procedure; the [implementation guides](implementations.md) translate
them into particular technologies.

## 1.1 The premise and its limits

An arrow from Order to Customer shows connectivity. It leaves questions open:
who retains customer state, who may change it, how old an observation may be,
and what survives a failed request. ROO makes those questions reviewable before
an implementation turns assumptions into behavior.

Ask: **what may each participant do to this data, during which interval,
under which consistency rules?** A memory address, a durable identifier, and
permission to act answer different parts of that question.

The method is a proposed practitioner workflow. It does not supply a type
system, a storage guarantee, or evidence that every design using it is correct.

## 1.2 Precise working vocabulary

| Term | ROO meaning | Question to answer |
|---|---|---|
| Object | Encapsulated state and behavior | Which invariants does this API protect? |
| Value | Data interpreted by its content for this operation | Would an equal replacement change its meaning? |
| Entity | A participant tracked across changes by an identity rule | What makes it the same entity tomorrow? |
| Owner / resource custodian | Participant or mechanism retaining a resource and arranging its release | What keeps it available, and when is it released? |
| Stable identity | A key with scope, version, reuse, and deletion rules | What does it identify, and for how long? |
| Coordinator | Component and operations preserving an invariant | Where are conflicting changes prevented or detected? |
| Authorization | Permission for a principal to request a named operation | Which policy applies, and how does revocation take effect? |
| Access | Observation, lookup, command, sharing, or transfer | What can this participant actually obtain or change? |
| Snapshot | Retained description of state at a declared time or version | How old may this observation be? |
| Aggregate | A chosen domain consistency boundary | Which rules must change together? |
| Execution domain | Where participating operations are coordinated | How can operations overlap or suspend? |

These terms describe design obligations. Each platform has its own vocabulary
and enforcement rules. A handler can retain loaded order data while a domain
component coordinates transitions and a store retains the stable identity.
Record those roles separately even when one component performs several.

## 1.3 Ownership is not identity

Transferring or copying a representation does not decide whether it represents
the same customer. Specify whether a copy is a detached observation, another
handle to shared state, or a new entity with a new identity.

Stable identity needs explicit scope, uniqueness, version, reuse, and deletion
rules. A local address or collection position may stop identifying the same
entity after replacement. Knowing an identifier does not by itself authorize
access. Typed IDs and checked handles are implementation choices described in
the [mapping guides](implementations.md).

## 1.4 Encapsulation protects meaningful transitions

Name operations such as add line, submit, and refund. Each should preserve its
stated invariants and return a defined outcome on rejection. Private fields
help only when callers cannot bypass those operations through mutable views,
setters, or reconstruction paths.

An observation should expose the information a caller needs with a declared
freshness limit. A command should expose an intentional transition. Decide
which effects and aliases are allowed before selecting receiver syntax,
references, interfaces, or serialization.

## 1.5 Core commitments

1. **Name the scenario and invariant before the mechanism.** State expected and
   forbidden outcomes and the boundary where state must agree.
2. **Separate custody, responsibility, identity, and authorization.** Record
   them independently even when one component performs all four roles.
3. **Give mutation a coordinator.** Name where conflicting changes are prevented
   or detected for each invariant.
4. **Keep access no longer than required.** Prefer operation-scoped access when
   the relationship itself is temporary.
5. **Choose sharing deliberately.** Explain why separate values, transfers, or
   identity lookup do not meet the requirement before adding shared mutable state.
6. **Design time and failure with structure.** Include suspension, cancellation,
   stale observations, and partial external success in the relationship.
7. **Match the guarantee to evidence.** Separate static, runtime, storage,
   protocol, and human evidence; record unverified assumptions.

This is the single commitment list. The [canonical procedure](02-relationship-design.md#23-the-six-step-decision-procedure)
turns it into a review artifact. These are heuristics: caches, cyclic graphs,
plugins, shared state, and inheritance can all fit explicit contracts.

## 1.6 Behavioral subtyping and inheritance

Separate three goals: substitutable behavior, reuse of implementation or
representation, and extension. An implementation can reuse another component
without promising to be its subtype. A subtype must preserve the behavior
clients rely on, including errors, invariants, and allowed state histories.
[Liskov and Wing, 1994](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf).

For example, a payment operation promising reservation of the requested amount
cannot silently reserve less. A timeout fits only if the contract admits an
uncertain result and defines recovery. Choose inheritance, composition, a
closed family, or another mechanism after stating that behavior.
The [concept atlas](03-concept-atlas.md) and [cross-language mappings](06-cross-language.md)
compare particular realizations.

## 1.7 Access validity and the three clocks { #17-lifetimes-describe-access-validity }

Distinguish memory validity, business validity, and observation freshness.
A readable order snapshot can describe an already cancelled order. A durable
identifier can still have valid syntax after its entity is deleted.

For each relationship, state when access ends, which business states permit
use, and when an observation must be refreshed. A task that outlives a request
needs its own custody, completion, cancellation, and recovery rules.
Platform lifetime checks address only the properties their contracts cover.

## 1.8 Intellectual lineage and claim boundary

ROO draws on information hiding, behavioral subtyping, ownership types,
separation logic, capabilities, RAII, DDD, and typestate. Its proposal connects
those ideas through a relationship worksheet and a review procedure.

Ownership types and separation logic have formal results for their own
systems; a ROO worksheet is neither of those formal systems.
[Clarke, Potter, and Noble, 1998](https://doi.org/10.1145/286936.286947),
[Reynolds, 2002](https://www.cs.cmu.edu/~jcr/seplogic.pdf).
Platform-specific results such as [RustBelt](https://plv.mpi-sws.org/rustbelt/popl18/)
likewise do not prove this methodology.

ROO makes no priority claim for these ideas. Its usefulness remains a
hypothesis to evaluate through engineering review and experience.
[Claims and limits](claims-and-limits.md) records the available evidence.

## 1.9 What success means in this edition

Another engineer should be able to predict the operation's allowed effects,
rejections, and recovery from its contract. Each field has a concrete answer
or an explicit unresolved decision. Implementation choices identify where each
obligation is enforced and what evidence supports it.

Start with the [contract](02-relationship-design.md), apply it to a
[design case](../case-studies/orders-payments/DESIGN.md), and then compare
[technology choices](technology-selection.md). Java, Rust, and PostgreSQL are
current reference implementations, with bounded evidence for each.
