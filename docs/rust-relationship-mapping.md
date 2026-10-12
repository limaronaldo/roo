# Rust relationship mapping

This is an implementation guide for the [ROO method](02-relationship-design.md).
Choose custody, identity, coordination, authorization, access, validity,
execution, and failure behavior first. The mechanisms below are Rust candidates
for those decisions, with their own costs and limits.

For other languages, start with [cross-language transfer](06-cross-language.md).
For storage and protocol choices, use [technology selection](technology-selection.md).
The [implementation index](implementations.md) distinguishes executable evidence
from design alternatives.

## Identity, movement, and retention

A move transfers a Rust value without inherently changing its domain identity.
`Copy` and `Clone` describe technical copying; decide separately whether a copy
is a snapshot, a shared handle, or a new entity. `Pin` addresses particular
movement guarantees and does not supply durable identity.
[Ownership](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html),
[pinning](https://doc.rust-lang.org/std/pin/index.html).

Rust supports encapsulation and polymorphism without class inheritance of
fields and implementation. Translate the intended behavior, reuse, or extension
need before choosing traits, composition, enums, or generics. Compiler friction
can expose a horizon mismatch or accidental sharing; it can also reflect a
conservative check or implementation mistake. Inspect the relationship before
adding a clone or shared pointer.

## Receivers and input policies

Private representation and named transitions can protect domain invariants.
A receiver describes local access; it does not decide caller permission.

| Receiver or input | Typical operational reading | Additional contract still needed |
|---|---|---|
| `&self` | Shared access | Interior mutation, I/O, authorization, and observational consistency |
| `&mut self` | Exclusive borrowed access | Business permission and preservation of invariants |
| `self` | Consuming operation for a non-`Copy` receiver | Outcome on error and identity after transition |
| `&T` parameter | Temporary shared view | Freshness, validity interval, and allowed hidden effects |
| `T` parameter | Transfer or copy according to the type | Whether retry or duplication is meaningful |
| `Id` parameter | Deferred resolution | Existence, version, tenant scope, and access checks |

Shared references can permit controlled interior mutation. `RefCell` checks
borrows at runtime; an `&mut Order` excludes conflicting local reference access
under Rust's rules but does not serialize another process's database writes.
Return a rejected draft if a consuming transition must support repair and retry.
[References and borrowing](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html).

## Candidate representations

| Requirement | Relationship policy | Initial Rust candidate | Cost or limitation to examine |
|---|---|---|---|
| Part exists only inside its whole | Whole retains and controls parts | Owned field, `Vec<T>`, or `Box<T>` | Moving/removing the part must respect whole invariants |
| Read during one operation | Temporary observation | `&T` or iterator/view | Provider must outlive access; interior effects may still exist |
| Exclusive local update | One updater during the operation | `&mut T` | Exclusive access does not authorize every business operation |
| Independent entity or arbitrary graph edge | Resolve identity through a custodian | Typed ID plus owner/repository lookup | Existence, stale handles, permissions, and versions need checking |
| Independent retained observation | Retain a separate snapshot | Owned snapshot | Memory independence trades away automatic freshness |
| Transfer to another coordinator | Transfer command custody | Move an owned command/value | Define outcome on rejection and cancellation |
| Shared retained immutable data | Shared retention with immutable content | `Rc<T>` locally or `Arc<T>` across suitable threads | Reference counts affect retention; immutability needs an actual type contract |
| Shared mutable local graph | Checked local access | `Rc<RefCell<T>>`, if required | Dynamic borrow conflicts, cycles, and reentrancy |
| Shared mutable concurrent state | Synchronize participating access | `Arc<Mutex<T>>` or another synchronization design | Lock duration, deadlock, poisoning, contention, and business races |
| Single mutation coordinator | Commands go to one coordinator | Actor/task owning state and accepting commands | Queueing, acknowledgement, shutdown, retries, and delivery semantics |

These are candidates, not equivalences: an ID graph can also live inside one aggregate, and an actor can own a graph.
`Arc` makes reference-count updates thread-safe; it does not automatically make arbitrary inner data safe for concurrent use. [Standard library: Arc](https://doc.rust-lang.org/std/sync/struct.Arc.html)

## Cycles, suspension, and cancellation

Strong `Rc` or `Arc` cycles can prevent ordinary reference-count reclamation.
Weak links require a missing-target outcome. Arena handles require checked
identity/generation resolution and are not Rust references or durable IDs by
default. See the core [graph obligations](02-relationship-design.md#25-cycles-and-graphs).

A lifetime parameter relates reference validity; it does not keep a referent
alive longer. Borrowing across `.await` can be valid and can still retain access
longer than intended. Review guards, captured values, cancellation, and remote
effects at each suspension point. `Send` and `Sync` concern thread transfer and
sharing; they do not establish business ordering or distributed consistency.
Mutex poisoning is advisory and needs an explicit recovery policy.
[Lifetimes](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html),
[Future](https://doc.rust-lang.org/std/future/trait.Future.html),
[Send](https://doc.rust-lang.org/std/marker/trait.Send.html),
[Sync](https://doc.rust-lang.org/std/marker/trait.Sync.html),
[Mutex](https://doc.rust-lang.org/std/sync/struct.Mutex.html).

## Rust evidence and its boundary

| Claim | Evidence Rust can contribute | Evidence still needed |
|---|---|---|
| Borrowed access does not outlive its referent | Lifetime checking for safe references | Correct contracts inside any unsafe implementation |
| Conflicting ordinary reference access is excluded | Borrow checking under Rust's rules | Interior-mutability policy and external aliases/state |
| Some values are not reused after transfer | Move checking for non-`Copy` values | Business uniqueness and duplication rules |
| Only valid operations are publicly callable | Module visibility, types, trait bounds | Runtime authorization and policy context |
| Thread transfer/sharing satisfies type bounds | `Send` / `Sync` constraints | Deadlock, ordering, fairness, and business-race analysis |
| Every LineItem has positive quantity | Private constructor can restrict creation | Validation, arithmetic checks, deserialization boundaries, and tests |
| A handle still identifies its original node | Type can encode handle category | Runtime arena/generation checks and exhaustion policy |
| A payment happens once | An owned command can limit local reuse | Provider guarantees, durable deduplication, reconciliation, and failure tests |
| State and event are committed together | API can make intended boundary visible | Real transaction semantics and verified integration |

Safe Rust's reference rules support memory safety; they are not a universal immutability or business-correctness proof. [Rust Book: references and borrowing](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html)
For each claim, put the actual check beside it and avoid promoting a test into a proof about all possible executions.
Compile-fail examples are valuable evidence for a specific rejected access pattern; runtime scenarios exercise the domain conditions the compiler does not know.

The [Rust laboratory](laboratory.md) and [Rust and object design](08-rust-and-object-design.md)
provide concrete examples. Their checks remain separate from storage,
protocol, operational, and human evaluation.
