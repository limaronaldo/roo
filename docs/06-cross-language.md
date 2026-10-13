# Cross-language portability

ROO — Relationship & Ownership Oriented design — is a language-independent method. Begin with a scenario, its expected and forbidden outcomes, and the invariant connecting them. Then decide relationships: who is responsible for a domain invariant, who retains and releases a resource, which identity survives replacement or restart, who may mutate state, and where access and failure are bounded. This can guide Rust, Java, C#, C++, Go, TypeScript, and Python. Rust is this edition's laboratory language. The language changes how some parts can be enforced; it does not decide the domain contract for us.

Apply the [canonical contract and six-step procedure](02-relationship-design.md)
in each language. The four roles—custodian, invariant coordinator, durable
identity, and authorization—remain separate even when mechanisms differ.

## How to read the comparison

`Compile-time` means the type checker or compiler rejects a class of use before execution. `Runtime` means a runtime check or execution mechanism enforces a rule. `Convention` means an API design, review rule, or test must keep the promise. Many languages combine all three. Guarantees are also bounded by escape hatches such as `unsafe`, reflection, native code, `dynamic`, or unchecked casts.

Keep database guarantees, protocol evidence, and human review distinct from compiler/static and runtime evidence. A uniqueness constraint needs evidence from the authoritative store; remote retry safety needs a protocol contract and exercised failure behavior; an authorization rule needs implemented checks and policy review. Tests observe the boundaries they exercise, while unverified expectations remain assumptions.

| Language | Allocation, aliases, and identity | Lifecycle and mutation | What the type system or runtime really guarantees |
| --- | --- | --- | --- |
| **Rust** | A non-`Copy` value has one current owner by default; moving it transfers that ownership. `&T` and `&mut T` are borrows, while `Rc<T>` and `Arc<T>` opt into shared ownership. Bindings and shared references are immutable by default; a reference is not a persistent entity ID. | `Drop` runs as an owned value is dropped, commonly at scope end. In safe code, `&mut T` gives exclusive access while that borrow is live; `Cell`, `RefCell`, `Mutex`, and similar types opt into other mutation regimes. `RefCell` checks borrow rules at runtime and can panic. | In safe Rust, references are checked for validity and conflicting mutable access is rejected. `Rc`/`Arc` cycles can retain allocations; `mem::forget`, process exit, and other cases can skip destructors. `Arc<T>` makes reference counting atomic; it does not make `T` itself thread-safe. See the [Rust Book on borrowing](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html), [interior mutability](https://doc.rust-lang.org/book/ch15-05-interior-mutability.html), [Send and Sync](https://doc.rust-lang.org/book/ch16-04-extensible-concurrency-sync-and-send.html), [`Arc`](https://doc.rust-lang.org/std/sync/struct.Arc.html), and [`mem::forget`](https://doc.rust-lang.org/core/mem/fn.forget.html). |
| **Java** | Variables of class type hold references; multiple variables can reach and mutate the same object. `==` on references checks whether they denote the same object, while `equals` can define value equality. Object reachability governs garbage collection. | `final` prevents reassignment of a field after initialization; it does not freeze the referenced object. Use `AutoCloseable` and try-with-resources for deterministic resource closure. Mutation control generally comes from encapsulation, immutable value design, and synchronization. | The JVM reclaims unreachable heap objects at an unspecified time; it does not infer domain ownership or promptly close files, sockets, or transactions. The Java Memory Model defines synchronization effects, not automatic thread safety for arbitrary objects. See the [JLS reference equality rule](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.21.3), [JLS memory model](https://docs.oracle.com/javase/specs/jls/se25/html/jls-17.html), and [`AutoCloseable`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/AutoCloseable.html). |
| **C#** | Class variables are references and may alias; structs are values with copy semantics. Reference identity can be tested with `ReferenceEquals`, but classes may override value equality. The garbage collector follows reachability. | `readonly` on a reference field prevents replacing the reference, not mutation through it. Records synthesize value equality and usually provide shallow, not transitive, immutability. `IDisposable` with `using` scopes deterministic cleanup. | The compiler checks language-level access and assignment rules. It does not assign one domain owner to an object graph or make arbitrary mutable classes thread-safe. The .NET GC manages managed memory; `Dispose` remains an explicit resource-lifecycle contract. Instance data is not synchronized by default. See [C# `readonly`](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/readonly), [records](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/record), the [.NET dispose pattern](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/dispose-pattern), and [.NET synchronization guidance](https://learn.microsoft.com/en-us/dotnet/standard/threading/synchronizing-data-for-multithreading). |
| **C++** | Values, references, and pointers have distinct semantics. `unique_ptr` models strict ownership and is movable but not copyable; `shared_ptr` shares ownership. Raw pointers and references can alias without carrying ownership. Addresses are not durable IDs. | Scope-based object lifetimes and RAII make destruction deterministic for ordinary automatic objects and smart-pointer owners. `const` restricts mutation through that access path; it does not prove global immutability. A `shared_ptr` cycle can keep objects alive. | The language and library specify object lifetime and smart-pointer behavior, but raw-pointer validity and synchronization remain obligations of the program. A data race on ordinary shared mutable state is not made safe by having a pointer or `shared_ptr`. See the C++ working draft sections for [`unique_ptr`](https://eel.is/c++draft/unique.ptr.general), [`shared_ptr`](https://eel.is/c++draft/util.sharedptr), [object lifetime](https://eel.is/c++draft/basic.life), and [library object-sharing rules](https://eel.is/c++draft/res.on.objects). |
| **Go** | Values can contain pointers, slices, maps, channels, or interfaces that refer to shared state. Assigning such a value may copy a descriptor while retaining aliases to underlying data. Pointer equality ordinarily asks whether pointers designate the same variable; the specification permits pointers to distinct zero-sized variables to compare equal. Neither case says whether a domain entity is still current. Interfaces are satisfied implicitly by method sets. | Garbage collection manages reachable memory; it does not provide a general deterministic destructor. `defer` is a common scope-bound cleanup tool for a function. Private fields and methods constrain package access, while synchronization or actor-style ownership is a design obligation. | The compiler checks static types and interface satisfaction; it does not enforce unique ownership or borrow lifetimes. The runtime detects some errors such as invalid memory access, but races still require correct synchronization. Finalizers and cleanups are best-effort fallbacks, not reliable resource-lifecycle contracts. See the [Go specification](https://go.dev/ref/spec), [Effective Go on interfaces and `defer`](https://go.dev/doc/effective_go), and the [Go GC guide](https://go.dev/doc/gc-guide). |
| **TypeScript and Python** | Both commonly use references to shared objects; aliasing is easy. JavaScript strict equality on objects compares reference identity ([ECMAScript equality](https://tc39.es/ecma262/2022/multipage/abstract-operations.html#sec-isstrictlyequal)); TypeScript interfaces are structural and its types are erased from emitted JavaScript. Python exposes object identity through `is`; `id()` is an object identity token for that runtime, not a durable key. | TypeScript `readonly` constrains writes through a checked type view but does not freeze nested objects or stop writes through aliases. Python uses encapsulation and conventions; its `with` protocol scopes resources. CPython reference counting is an implementation detail, and other Python implementations may differ. | TypeScript's checker rejects some invalid programs but does not change JavaScript runtime behavior. JavaScript memory reclamation is not a deterministic disposal contract. Python explicitly advises closing external resources rather than relying on finalization. See TypeScript's [type-erasure explanation](https://www.typescriptlang.org/docs/handbook/typescript-from-scratch.html), [`readonly` object properties](https://www.typescriptlang.org/docs/handbook/2/objects.html#readonly-properties), and the [Python data model](https://docs.python.org/3/reference/datamodel.html). |

## Capabilities and concurrency

An interface or trait can restrict the operations visible to a collaborator. It does not by itself establish memory ownership, authorize a user, or guarantee safe concurrent use.

| Language | Capability surface | Concurrency boundary |
| --- | --- | --- |
| Rust | Traits name available operations; `&self`, `&mut self`, and consuming receivers express different access shapes. Trait bounds such as `Send` and `Sync` express cross-thread transfer and sharing requirements. See the [trait Reference](https://doc.rust-lang.org/reference/items/traits.html). | Safe Rust checks `Send`/`Sync` requirements for thread transfer/sharing, but application invariants still need synchronization. `Arc` alone does not make its contents safe to mutate concurrently. |
| Java | Nominal interfaces expose declared methods, not a reference's ownership or full effect set. See [JLS interface declarations](https://docs.oracle.com/javase/specs/jls/se25/html/jls-9.html). | The [Java Memory Model](https://docs.oracle.com/javase/specs/jls/se25/html/jls-17.html) specifies synchronization effects; mutable objects need a deliberate synchronized, immutable, or confined design. |
| C# | Nominal interfaces restrict callable members through that view, but aliases may expose other operations. See the [C# interface reference](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/interface). | Instance data is not thread-safe by default; use an explicit lock, concurrent collection, or confinement rule. See [Microsoft's synchronization guidance](https://learn.microsoft.com/en-us/dotnet/standard/threading/synchronizing-data-for-multithreading). |
| C++ | Concepts check whether an interface of operations exists at compile time; abstract base classes provide runtime polymorphism. Neither expresses ownership by itself. See the [C++ draft's concepts clause](https://eel.is/c++draft/temp.concept). | Synchronization is an explicit library/program contract. Accessing shared mutable state without the required synchronization can cause a data race; see [C++ object-sharing rules](https://eel.is/c++draft/res.on.objects). |
| Go | Interfaces are satisfied by method sets, usually implicitly, so they describe a narrow behavioral capability without requiring the implementing type to name the interface. | The [Go memory model](https://go.dev/ref/mem) requires concurrently accessed mutable data to be serialized, for example with channels or locks. |
| TypeScript and Python | TypeScript uses structural interfaces and erases types at runtime. Python `Protocol` primarily supports static structural checking; optional runtime checks only inspect limited shape. See [TypeScript type compatibility](https://www.typescriptlang.org/docs/handbook/type-compatibility) and [Python `Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol). | Execution models vary by runtime and host. Do not infer that a mutable object is thread-safe from a structural type. Python's thread and free-threaded builds have different runtime conditions; choose and document the synchronization boundary. |

## Transfer and stale identities

| Language | What a “transfer” commonly means |
| --- | --- |
| Rust | Moving a non-`Copy` value transfers its owner; `Clone` is explicit. Cloning an `Arc` adds a shared owner, not an independent object. |
| Java and C# | Assigning a class/reference variable usually copies a reference and creates another alias. Value types are copied, but their fields may themselves contain references. Use APIs and immutable snapshots to communicate a semantic transfer. |
| C++ | Moving a `unique_ptr` transfers its owning handle; copying a `shared_ptr` shares ownership; copying a raw pointer copies only an address. Ordinary object copies depend on the type's copy operations. |
| Go | Assignment and channel send copy a value. A copied slice/map/channel/interface may still refer to shared underlying state; “sent” does not automatically mean uniquely owned. |
| TypeScript and Python | Assignment usually creates another reference to the same object. A deep copy, serialized message, or runtime-specific transfer is a separate operation with its own semantics. |

Staleness is a domain/version question, not a garbage-collector question. A safe Rust borrow cannot dangle, but a `CopyId` can still name a deleted row or old generation. A Java, C#, TypeScript, or Python reference may keep an allocation reachable while its entity is no longer active. A C++ pointer may dangle when the object lifetime ends; a smart pointer controls allocation lifetime, not database validity. A Go pointer can keep an allocation reachable without proving that the entity represented by it still exists in an external system. Use a typed ID with a scope and reuse/version rule, then validate it on resolution. For reusable local slots, include a generation counter; for persisted entities, use a store-level key and define deletion and version conflicts.

This comparison is about ordinary language behavior, not a claim that every project uses each feature in the same way. Frameworks may add scopes, transactions, actor confinement, or lifecycle rules. Those become part of the Relationship Contract only when the application can rely on them and tests or runtime checks preserve them.

In runtimes that trace reachability, an unreachable object cycle can be collected; an object retained by a cache, registry, listener, or global root cannot be recognized as logically expired by the collector. Garbage collection does not remove the need to design cache eviction, subscription removal, or domain lifecycle.

## Immutable values and controlled mutation

“Immutable” can describe one access path, a binding, a shallow object, or a transitive object graph. Name the exact level in a contract.

| Language | Typical checked boundary | Common convention or runtime limit |
| --- | --- | --- |
| Rust | Bindings and shared references are immutable by default; `mut` and `&mut` make mutation explicit. Interior-mutable wrappers mark a different regime. See the [Rust Book](https://doc.rust-lang.org/book/ch03-01-variables-and-mutability.html). | Shared ownership with `Rc`/`Arc` does not imply immutable contents if interior mutability is used; unsafe code can invalidate ordinary safe-code assumptions if unsound. |
| Java | `final` checks that a variable/field is assigned only as allowed by the language. [JLS §4.12.4](https://docs.oracle.com/javase/specs/jls/se25/html/jls-4.html#jls-4.12.4). | A final reference can still point to mutable state. Deep immutability needs encapsulation and no mutable aliases escaping. |
| C# | `readonly` constrains re-assignment of fields; `init` and record features support initialization-oriented value models. | Reference-type fields remain mutable through aliases; record immutability is shallow unless referenced values are immutable too. |
| C++ | `const` restricts operations through a const-qualified access path; see the [C++ draft's cv-qualification rules](https://eel.is/c++draft/dcl.type.cv). | Another non-const alias can still mutate an object that was not created as const. `const` is not a global proof of immutability. |
| Go | Constants apply to constant values, not arbitrary mutable object graphs; private fields and methods can define a controlled package API. See the [Go constants specification](https://go.dev/ref/spec#Constants). | Pointers, slices, and maps can alias mutable storage; callers and package authors coordinate mutation through API and synchronization conventions. |
| TypeScript and Python | TypeScript `readonly` constrains writes during type checking. Python distinguishes immutable and mutable object types in its [data model](https://docs.python.org/3/reference/datamodel.html#objects-values-and-types). | TypeScript readonly views are shallow and can be changed through aliases. Python immutable containers may contain references to mutable objects. |

## A single relationship contract in Rust and Java

Consider a library that checks out a physical book copy to a member. The example keeps the same domain invariant in both languages: a copy has at most one active loan, and checkout and return are the only operations that change availability.

Before selecting either language, decide that one domain coordinator controls availability, callers request named transitions, loans retain durable IDs, reads are snapshots, and concurrent commands must be serialized at the chosen boundary. The table records that policy first; the sketches then show different realizations. Caller authorization is an application obligation outside these sketches, whose supplied IDs are not evidence of permission.

| Field | Contract |
| --- | --- |
| Owner / resource custodian | The loaded `Library` retains copy, member, and loan state; a repository/service separately retains database connections and transaction scopes. Domain responsibility for copy availability and active loans belongs to `Library`'s command boundary. |
| Stable identity | `CopyId`, `MemberId`, and `LoanId` are durable value IDs. `Loan` stores IDs rather than pointers/references to a `Copy` or `Member`. |
| Invariant coordinator | `Library.checkout` and `return_copy`/`returnCopy` keep availability and active-loan state consistent through controlled commands. Loan facts are immutable after creation. |
| Authorization | Not implemented in this teaching case; a live system needs an authenticated caller policy. |
| Access regime | Reads return a value snapshot. Commands go through the aggregate. Concurrent commands are serialized at the chosen boundary. |
| Validity horizon | An in-memory borrow/reference is valid only during its language-defined lifetime. A durable ID can outlive an object instance, but every lookup must still handle deletion or stale state. |
| Execution domain | Serialize commands for the same loaded aggregate. Rust realizes this with exclusive `&mut self` access in the single-threaded API; a shared service can place the aggregate behind a lock. Java serializes methods on this instance with `synchronized`, or can confine it to one executor. |
| Failure boundary | Checkout rejects an unknown copy, an unknown member, an already-loaned copy, or a duplicate loan ID. Return rejects an unknown loan or inconsistent state; the Rust sketch also reports an unknown copy. Rust distinguishes failures by enum variant; the Java sketch uses one exception type and distinguishes cases only by message text. The persistence adapter separately reports transaction and I/O failures. |

The Rust example makes one local writer explicit and checks checkout rejection and return behavior.

<!-- roo-example: library-checkout-rust -->
**Compiled and tested in CI · Rust.**

```rust
use std::collections::HashMap;

#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
struct CopyId(u64);
#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
struct MemberId(u64);
#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
struct LoanId(u64);

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum CopyStatus { Available, OnLoan(LoanId) }

#[derive(Clone, Debug)]
struct Loan { id: LoanId, copy: CopyId, borrower: MemberId, due_day: u32 }

#[derive(Debug)]
enum CheckoutError { UnknownCopy, UnknownMember, AlreadyOnLoan, DuplicateLoanId }
#[derive(Debug)]
enum ReturnError { UnknownLoan, UnknownCopy, InconsistentState }

struct Library {
    copies: HashMap<CopyId, CopyStatus>,
    members: HashMap<MemberId, ()>,
    loans: HashMap<LoanId, Loan>,
}

impl Library {
    fn checkout(&mut self, copy: CopyId, borrower: MemberId, id: LoanId,
                due_day: u32) -> Result<LoanId, CheckoutError> {
        let status = self.copies.get(&copy).ok_or(CheckoutError::UnknownCopy)?;
        if !self.members.contains_key(&borrower) { return Err(CheckoutError::UnknownMember); }
        if *status != CopyStatus::Available { return Err(CheckoutError::AlreadyOnLoan); }
        if self.loans.contains_key(&id) { return Err(CheckoutError::DuplicateLoanId); }
        self.copies.insert(copy, CopyStatus::OnLoan(id));
        self.loans.insert(id, Loan { id, copy, borrower, due_day });
        Ok(id)
    }

    fn return_copy(&mut self, id: LoanId) -> Result<(), ReturnError> {
        let copy_id = self.loans.get(&id).ok_or(ReturnError::UnknownLoan)?.copy;
        let status = self.copies.get_mut(&copy_id).ok_or(ReturnError::UnknownCopy)?;
        if *status != CopyStatus::OnLoan(id) { return Err(ReturnError::InconsistentState); }
        *status = CopyStatus::Available;
        self.loans.remove(&id);
        Ok(())
    }
}

let copy = CopyId(1);
let member = MemberId(1);
let loan = LoanId(1);
let mut library = Library {
    copies: HashMap::from([(copy, CopyStatus::Available)]),
    members: HashMap::from([(member, ())]),
    loans: HashMap::new(),
};
assert!(matches!(library.checkout(CopyId(9), member, loan, 30), Err(CheckoutError::UnknownCopy)));
assert!(matches!(library.checkout(copy, MemberId(9), loan, 30), Err(CheckoutError::UnknownMember)));
assert_eq!(library.checkout(copy, member, loan, 30).unwrap(), loan);
assert!(matches!(library.checkout(copy, member, LoanId(2), 30), Err(CheckoutError::AlreadyOnLoan)));
assert_eq!(library.loans.len(), 1);
library.return_copy(loan).unwrap();
assert!(matches!(library.return_copy(loan), Err(ReturnError::UnknownLoan)));
assert_eq!(library.copies[&copy], CopyStatus::Available);
assert!(library.loans.is_empty());

```

The example is an in-memory API. Durable IDs need a creation and reuse
policy at the persistence boundary. An exclusive local borrow does not lock
another process's database session.

The Java example exercises the same scenarios. Private fields and command
methods define the local mutation boundary; `synchronized` serializes calls
on this instance. Persistence needs its own transaction and revalidation.

<!-- roo-example: library-checkout-java -->
**Compiled and tested in CI · Java.**

```java
import java.time.Instant;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

final class CheckoutException extends Exception {
    private static final long serialVersionUID = 1L;
    CheckoutException(String message) { super(message); }
}

record CopyId(UUID value) {}
record MemberId(UUID value) {}
record LoanId(UUID value) {}
record Loan(LoanId id, CopyId copy, MemberId borrower, Instant dueAt) {}

final class Library {
    private final Set<CopyId> copies = new HashSet<>();
    private final Map<CopyId, LoanId> activeLoanByCopy = new HashMap<>();
    private final Set<MemberId> members = new HashSet<>();
    private final Map<LoanId, Loan> loans = new HashMap<>();

    synchronized LoanId checkout(CopyId copy, MemberId borrower,
                                 LoanId id, Instant dueAt) throws CheckoutException {
        if (!copies.contains(copy)) throw new CheckoutException("unknown copy");
        if (!members.contains(borrower)) throw new CheckoutException("unknown member");
        if (activeLoanByCopy.containsKey(copy)) throw new CheckoutException("already on loan");
        if (loans.containsKey(id)) throw new CheckoutException("duplicate loan id");
        activeLoanByCopy.put(copy, id);
        loans.put(id, new Loan(id, copy, borrower, dueAt));
        return id;
    }

    synchronized void returnCopy(LoanId id) throws CheckoutException {
        Loan loan = loans.get(id);
        if (loan == null) throw new CheckoutException("unknown loan");
        if (!id.equals(activeLoanByCopy.get(loan.copy())))
            throw new CheckoutException("inconsistent loan state");
        activeLoanByCopy.remove(loan.copy());
        loans.remove(id);
    }

    static void expectFailure(String expected, CheckedAction action) throws Exception {
        try {
            action.run();
            throw new AssertionError("expected " + expected);
        } catch (CheckoutException error) {
            if (!expected.equals(error.getMessage())) throw new AssertionError(error);
        }
    }

    interface CheckedAction { void run() throws Exception; }

    public static void main(String[] args) throws Exception {
        Library library = new Library();
        CopyId copy = new CopyId(new UUID(0, 1));
        MemberId member = new MemberId(new UUID(0, 1));
        LoanId loan = new LoanId(new UUID(0, 1));
        library.copies.add(copy);
        library.members.add(member);
        expectFailure("unknown copy", () -> library.checkout(
            new CopyId(new UUID(0, 9)), member, loan, Instant.EPOCH));
        expectFailure("unknown member", () -> library.checkout(
            copy, new MemberId(new UUID(0, 9)), loan, Instant.EPOCH));
        if (!library.checkout(copy, member, loan, Instant.EPOCH).equals(loan))
            throw new AssertionError("checkout identity");
        expectFailure("already on loan", () -> library.checkout(
            copy, member, new LoanId(new UUID(0, 2)), Instant.EPOCH));
        if (library.loans.size() != 1) throw new AssertionError("rejected checkout mutated state");
        library.returnCopy(loan);
        expectFailure("unknown loan", () -> library.returnCopy(loan));
        if (!library.activeLoanByCopy.isEmpty() || !library.loans.isEmpty())
            throw new AssertionError("return did not release copy");
    }
}

```

The Java `record` values here contain immutable ID wrappers and an `Instant`; choosing mutable members would make the record only shallowly immutable. An ORM may also require a different identity/equality strategy. If the aggregate is persisted, use a transaction and re-check availability against the authoritative store; an in-process monitor protects only this in-process instance.

## Refactoring toward portable contracts

- Describe the scenario and write its domain invariant. Identify expected, forbidden, and failure outcomes before selecting a language mechanism.
- Inventory meaningful relationships and complete the eight fields. Separate resource custody, domain responsibility, durable identity, and authorization; do not infer those roles from the word “has-a.” Put transitions behind the smallest coordinator/API that can check the invariant, then test both allowed and rejected transitions.
- Add stable ID value types where lookup must survive reload, serialization, or object replacement. Treat lookup failure and version mismatch as normal outcomes. Never persist an address, runtime object identity, or collection position as if it were durable.
- Mark each API as read view, controlled mutation, borrowed access, value copy, or ownership transfer. Avoid returning mutable internals when a snapshot or narrow interface suffices.
- State the lifecycle boundary for files, locks, sockets, database transactions, and subscriptions. Prefer deterministic close/using/defer/RAII scopes. Garbage collection alone does not close resources at a predictable time.
- State the execution boundary. A single-thread rule, lock, actor queue, or transaction is part of the design only if callers cannot silently bypass it.
- Test stale IDs, duplicate commands, aliases to returned data, failure after partial work, concurrent commands, serialization, and resource cleanup. Add a compile-fail case when a static guarantee is a deliberate part of a Rust or C++ API.
- Introduce reference counting, interior mutability, inheritance, or shared mutable graphs only after naming the needed sharing semantics and the cleanup/failure behavior they imply.

The resulting design is portable at the level that matters: the domain invariant and relationship policy stay the same, while each language uses the enforcement mechanism it actually provides.
