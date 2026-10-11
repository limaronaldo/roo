# ROO design review: orders and payments

ROO (Relationship & Ownership Oriented design) is a language-independent
method. This filled review checks relationship decisions before their Java,
Rust, storage, and protocol realizations.

## Scope and lead case

This review applies the frozen shared [orders-and-payments contract](../SPEC.md) to its Java composition, Java Template Method, and Rust composition implementations. It also reads the separately qualified [PostgreSQL](../postgres/SPEC.md) and [HTTP](../http/SPEC.md) extensions. The bounded review question is whether the relationship decisions that carry one payment intent through an uncertain result remain explicit across those boundaries.

The primary recovery row is `recover_commit` from [the original scenario set](../scenarios.tsv):

```text
add:100:2;add:50:1;pay:p1:approve:commit;reconcile:ok:none
```

The two additions total 250 USD minor units ($2.50). The application commits payment intent `p1` and Pending before calling the provider. The provider approves and records one charge; the injected terminal local commit fails, leaving Pending with one charge and no event. Reconciliation looks up the persisted `p1` request and commits Paid plus event `payment:p1`, without another charge. The [expected TSV](../expected.tsv) records the final row as Paid, 250, one charge, one event, zero consumed events, one pending outbox event, Approved, and payment ID `p1`.

The fixture's final row cannot by itself show the intermediate failure state. The [historical validation record](../../../research/orders-payments-validation.md) reports the original 42-row oracle comparison and intermediate unit assertions. Those records are prior execution evidence; this review did not rerun them. The root case is single-threaded and in-memory. Database and HTTP evidence below belongs to separate extensions.

## Evidence key

- **[SRC]** Direct source or contract inspection. It establishes the written design, not execution.
- **[RUN]** Historical root execution record for the in-memory case, dated 2026-10-11.
- **[PG]** Historical local PostgreSQL integration receipt, dated 2026-10-11.
- **[HTTP]** Historical local HTTP qualification receipt, dated 2026-10-11.
- **[REVIEW]** Prior separate AI-agent review disposition for the named bounded candidate.
- **[OPEN]** Unverified question outside the evidence inspected here.
- **[OPTIONAL]** Possible future product or protocol improvement, not a case defect.

## Review questions

| Review question | Evidence to inspect | Answer / finding |
|---|---|---|
| What scenario, invariant, allowed outcome, forbidden outcome, and failure case define this review? | Use case, relationship decisions, and expected results | **[SRC]** The lead case is `recover_commit`: persist `p1` before the effect; a failed terminal commit keeps Pending and emits no event; reconciliation of the same intent reaches Paid with one charge and event `payment:p1`. **[RUN]** The root report records all 42 original rows checked against the independent oracle and intermediate assertions. Historical, not freshly executed here. Links: [SPEC](../SPEC.md), [expected row](../expected.tsv), [validation](../../../research/orders-payments-validation.md). |
| What behavior must a boundary provide to its callers? | Requests, results, state changes, error behavior, and retry or idempotency rules | **[SRC]** The application prepares an immutable request, commits intent before the provider call, distinguishes Unknown from NotFound, and finalizes state with one event. A retry/reconcile uses the persisted ID and full request. **[PG]/[HTTP]** The extensions use short local transactions and preserve natural payment/refund identity across recovery; this is bounded to their recorded local contracts. Links: [Java coordinator](../java/src/roo/payments/CompositionApplication.java), [Rust coordinator](../rust/src/application.rs), [PostgreSQL contract](../postgres/SPEC.md), [HTTP contract](../http/SPEC.md). |
| Does each important relationship name its resource custodian and domain invariant coordinator separately? | Relationship Contract and data flow | **[SRC]** The eight-field contract separates Order's custody of intent, Store's custody of committed order/outbox, Provider's independent records/effects, Consumer's event deduplication, and Application's coordination. Custody and orchestration are not collapsed into one owner. See the [eight-field contract](../../../docs/02-relationship-design.md#21-the-eight-field-relationship-contract), [Java adapters](../java/src/roo/payments/Adapters.java), and [Rust adapters](../rust/src/adapters.rs). |
| Does a target need durable identity beyond a current value or object lifetime? | Identity scope, version, reuse, deletion, and lookup rules | **[SRC]** PaymentId and RefundId are distinct typed identities retained for one in-memory scenario; provider records last for that fresh scenario. This does not survive process restart. PostgreSQL persists scope-qualified records until harness cleanup. **[OPEN]** Real-provider key retention and lookup consistency are not established. Links: [Java guide](../java/README.md), [Rust guide](../rust/README.md), [PostgreSQL contract](../postgres/SPEC.md). |
| Are mutation authority and business authorization explicit? | API, permissions, storage model, and use case | **[SRC]** Domain mutation is routed through coordinator operations and private transitions. A PaymentId or HTTP scope is an identity/correlation value, not permission. The HTTP scope is expressly not a tenant authorization boundary; no caller authentication or authorization policy is modeled. **[OPEN]** Production principal, tenant, and refund authorization remain unverified. Links: [Java domain](../java/src/roo/payments/Domain.java), [Rust domain](../rust/src/domain.rs), [PostgreSQL contract](../postgres/SPEC.md), [HTTP contract](../http/SPEC.md). |
| Are access, aliasing, validity, and transfer decisions clear before choosing language mechanisms? | Relationship Contract and boundary crossings | **[SRC]** Java composition holds injected ports; its template variant uses stable adapter hooks. Rust Application<'a> retains exclusive mutable borrows of Store, Provider, and Consumer for its active lifetime, potentially across calls; the caller regains access after last use or drop. HTTP handlers validate owned request values and call database adapters with short transactions. These choices describe local access and lifetime; they do not confer authorization. Links: [Java composition](../java/src/roo/payments/CompositionApplication.java), [Java template](../java/src/roo/payments/TemplateApplication.java), [Rust application](../rust/src/application.rs), [HTTP contract](../http/SPEC.md). |
| Can callers bypass an invariant through fields, mutable views, setters, or reconstruction? | Visibility, mutation operations, and scenario evidence | **[SRC]** Java keeps aggregate state private and exposes snapshots; Rust keeps mutation transitions crate-private and returns shared observations. The coordinator reloads committed state after a failed candidate commit. **[RUN]** Historical Java access diagnostics and Rust E0382/E0502/E0624 checks support only their named compile-time restrictions; runtime assertions are separate. Links: [Java domain](../java/src/roo/payments/Domain.java), [Rust domain](../rust/src/domain.rs), [validation](../../../research/orders-payments-validation.md). |
| Does the execution boundary preserve the whole invariant under overlap? | Coordination, transaction, or serialization boundary and concurrent scenario | **[SRC]** The original case makes no overlap claim. PostgreSQL mutations lock the order row; provider writes use an independent transaction/advisory lock; finalization commits state and outbox together. **[PG]/[HTTP]** Historical records report seven witnessed competing schedules per variant, with HTTP adding request-level schedules. They do not prove every interleaving. Links: [Java store](../postgres/java/src/roo/postgres/Store.java), [Rust database adapter](../postgres/rust/src/database.rs), [PostgreSQL validation](../../../research/postgres-validation.md), [HTTP validation](../../../research/http-validation.md). |
| What happens on stale lookup, invalid input, cancellation, or partial external failure? | Negative behavior, recovery path, and observed results | **[SRC]** Invalid state/identity outcomes are closed; Unknown and simulator NotFound remain distinct. A post-effect local commit failure leaves the active intent recoverable by the same ID. **[RUN]** The historical report covers those bounded scenarios. **[OPEN]** Real request cancellation, provider lookup consistency, and production retry budgets are not evidenced. Links: [SPEC](../SPEC.md), [validation](../../../research/orders-payments-validation.md), [HTTP validation](../../../research/http-validation.md). |
| After the behavior is defined, do traits or interfaces expose the needed operations, and do implementations preserve their shared contract? | Port contract, implementations, and shared behavioral checks | **[SRC]** Java composition uses StorePort/ProviderPort; the Java template coordinator fixes the algorithm and finalization while exposing stable hooks. Rust uses concrete composed adapters with exclusive borrows and needs no hierarchy. **[RUN]** The prior shared oracle report records matching outcomes for the three in-memory runners. This demonstrates those recorded scenarios, not arbitrary adapter honesty. Links: [Java composition](../java/src/roo/payments/CompositionApplication.java), [Java template](../java/src/roo/payments/TemplateApplication.java), [Rust application](../rust/src/application.rs), [validation](../../../research/orders-payments-validation.md). |
| Does a hierarchy provide needed reuse, substitutability, or variation? | Alternatives and concrete extension scenario | **[SRC]** Java Template Method is a legitimate alternative: final public algorithms and private finalization own ordering; subclasses provide stable StorePort/ProviderPort hooks. A separate injected-port composition implementation is also present. Rust composition expresses the same coordination without inheritance. No finding requires a hierarchy in Rust. Links: [Java template](../java/src/roo/payments/TemplateApplication.java), [template adapter](../java/src/roo/payments/InMemoryTemplateApplication.java), [composition](../java/src/roo/payments/CompositionApplication.java), [Rust application](../rust/src/application.rs). |
| Can another language preserve the same relationship decisions with its own mechanisms? | Neutral contract and per-language enforcement limits | **[SRC]/[RUN]** The frozen contract is shared across Java composition, Java Template Method, and Rust composition. Historical fixture comparison reports the same 42-row output for each; Java visibility/final methods and Rust ownership/borrows contribute different local evidence. The observations do not establish universal language equivalence, production durability, or identical implementation mechanisms. Links: [SPEC](../SPEC.md), [Java guide](../java/README.md), [Rust guide](../rust/README.md), [validation](../../../research/orders-payments-validation.md). |

## Seven-field relationship map

The [ROO Relationship Contract](../../../docs/02-relationship-design.md#21-the-eight-field-relationship-contract) keeps these statements separate. In particular, identity and access capability do not imply business authorization.

| Field | Case decision |
|---|---|
| Owner / resource custodian | Order holds its payment/refund intent; Store owns committed order and outbox facts; Provider and Consumer retain independent records. Application coordinates calls but does not own those resources. |
| Stable identity | PaymentId and RefundId are distinct typed IDs correlated to OrderId. The in-memory horizon is one scenario; PostgreSQL uses a scope plus operation identity through harness cleanup. |
| Invariant coordinator | Application operations and private domain transitions validate state changes. Provider effects follow persisted intent. The case defines no authenticated caller or production refund policy. |
| Authorization | Not implemented in this teaching case; a live system needs an authenticated caller policy. |
| Access regime | Java uses injected ports or stable template hooks. Rust uses exclusive mutable borrows of concrete adapters; committed observations are snapshots/shared reads. |
| Validity horizon | Intent remains fixed from preparation through terminal state and recovery. Simulated provider records do not expire during a scenario; real retention is unknown. |
| Execution domain | Root fixture runner is deterministic and single-threaded. PostgreSQL and HTTP records cover selected local concurrent schedules, not all interleavings. |
| Failure boundary | Prepare, provider effect, final local commit, outbox delivery, and acknowledgement have distinct outcomes. Durable claims apply only to the separately tested synthetic PostgreSQL setup. |

## Evidence classes

Treat these sources separately; evidence in one class does not establish claims in another.

| Evidence class | What it can support | Limit to record | Case evidence and bounded status |
|---|---|---|---|
| Compiler or static analysis | Checked type, visibility, or access properties of the analyzed program | Does not establish domain correctness, authorization, runtime behavior, or external effects | **[RUN]** The in-memory report records Java private/final negative diagnostics and Rust E0382/E0502/E0624 examples. This supports only those checked restrictions. [Validation record](../../../research/orders-payments-validation.md). |
| Runtime or behavioral evidence | Observed outcomes for the executed scenarios and conditions | Does not cover unobserved states or prove every interleaving | **[RUN]** Historical record reports 42 oracle rows and 10 malformed fixtures for each in-memory runner; it names intermediate assertions. The expected `recover_commit` result is one charge and one event. No fresh run was done for this review. [Validation](../../../research/orders-payments-validation.md), [check log](../../../research/orders-payments-checks.log). |
| Database or transaction evidence | Constraints, isolation, atomicity, and durability in the examined database setup | Does not establish end-to-end behavior across an unexamined service or provider | **[PG]** The local receipt reports row-lock witnesses, independent app/provider/inbox transactions, SIGKILL recovery, and PostgreSQL immediate-restart snapshots. It is synthetic loopback evidence within one PostgreSQL/WAL domain; not external-provider or production proof. [PostgreSQL validation](../../../research/postgres-validation.md). |
| Protocol or boundary evidence | Encoded inputs and outputs, rejection behavior, and tested delivery semantics | A schema alone does not prove domain correctness or durable effects | **[HTTP]** The local HTTP receipt reports request/recovery cases across three variants. Payment/refund replay uses the same identity. A separate lost-response check shows line POST can append again because it has no durable command receipt; this is additional HTTP evidence, not an original 42-row oracle case. [HTTP contract](../http/SPEC.md), [HTTP validation](../../../research/http-validation.md). |
| Human review or operational decision | Explicit assumptions, policy choices, and reviewed tradeoffs | Is not execution evidence for behavior or infrastructure guarantees | **[REVIEW]** Earlier bounded reviews accepted their named frozen educational candidates. Those receipts do not authorize production use or verify this document's claims by themselves. [Base review](../../../research/orders-payments-review.md), [PostgreSQL review](../../../research/postgres-review.md), [HTTP review](../../../research/http-review.md). |

## Findings and remaining questions

**Demonstrated defects:** none newly demonstrated by this source inspection. The review confirms the documented split between resource custody, domain coordination, stable identity, and language mechanisms within the stated cases.

**Unverified production questions:** caller authentication and tenant authorization; a real provider's idempotency scope, retention, and lookup consistency; cancellation and end-to-end retry budgets; real external effects and failure behavior; and interleavings beyond the recorded schedules. These are outside the local contracts and receipts.

**Optional improvement:** a durable command receipt for line POST could make uncertain add responses replay-safe. The HTTP contract deliberately leaves line POST non-idempotent and requires inspection plus a caller-controlled decision after response loss. Adding such a receipt is a future protocol choice, not a demonstrated defect in this case.

## Related originals and siblings

- Start with the [original case walkthrough](../README.md), its [frozen specification](../SPEC.md), and the [template used for this review](../../../templates/design-review.md).
- Compare the [Java implementation guide](../java/README.md) and [Rust implementation guide](../rust/README.md) with their cited coordinators and adapters.
- Read the separate [PostgreSQL guide](../postgres/README.md), [contract](../postgres/SPEC.md), and [historical validation](../../../research/postgres-validation.md).
- Read the separate [HTTP guide](../http/README.md), [contract](../http/SPEC.md), and [historical validation](../../../research/http-validation.md).
- Consult the [eight-field ROO relationship contract](../../../docs/02-relationship-design.md#21-the-eight-field-relationship-contract) and the [adoption guide](../../../docs/09-adoption-guide.md).

## Boundary trace

1. **Prepare locally.** The coordinator validates a Draft order and persists an
   immutable payment request with Pending. A failed prepare returns before the
   provider is called. The request carries PaymentId, OrderId, currency, and
   amount as typed values.
2. **Observe the provider.** The simulator retains its record independently of
   local state and compares the complete request on a repeated key. A timeout
   after approval returns Unknown to the caller while retaining one charge.
   Unknown describes the observation, not an absent or declined remote effect.
3. **Finalize locally.** Approval changes a detached candidate to Paid and adds
   one stable event in the same local commit. If that commit fails, the store
   keeps Pending and the provider's charge remains. No candidate event is
   installed.
4. **Recover with identity.** Reconciliation uses the persisted request and
   provider lookup. An unavailable lookup remains Unknown; simulator NotFound
   is a separate result. A terminal observation commits once as `payment:p1`; a same-key provider replay does not create a second charge.
5. **Observe the outbox.** After recovery, the expected final row has one
   committed charge, one event, zero consumer deliveries, and one pending
   outbox record. Delivery is a separate operation; the recovery fixture does
   not imply that the event was consumed.

This trace follows the [frozen state-machine contract](../SPEC.md), the Java
[composition coordinator](../java/src/roo/payments/CompositionApplication.java),
and Rust [application](../rust/src/application.rs) and
[adapter](../rust/src/adapters.rs) sources. The executable receipt is linked
separately in the evidence-class table.

## Language mechanisms in the inspected sources

**Java composition** receives StorePort and ProviderPort in its constructor.
Add validates and commits a candidate; pay/refund prepare or reuse persisted
intents before provider calls and privately finalize terminal results. Reconcile
looks up the active intent and uses that finalization path. The [adapter source](../java/src/roo/payments/Adapters.java)
supplies detached snapshots and an independent provider. Its contract is trusted
by the coordinator; Java does not prove the provider's honesty.

**Java Template Method** fixes add, payment, refund, reconciliation, and private
finalization in final methods. Protected hooks return stable store/provider
adapters. The separate [in-memory subclass](../java/src/roo/payments/InMemoryTemplateApplication.java)
only supplies those capabilities. This is a concrete inheritance variation
point, not a hierarchy required by the domain.

**Rust composition** creates Application<'a> with exclusive mutable borrows of
Store, Provider, and Consumer for the coordinator's active lifetime, which can
span multiple method calls. The caller regains direct access after the
coordinator's last use or drop. The [domain](../rust/src/domain.rs) keeps
transition methods crate-private. These checks constrain local movement and
aliasing; provider idempotency and candidate replacement remain adapter
contracts.

## Extension boundaries

**PostgreSQL** changes the persistence evidence. Its store locks the scope's
order row with `FOR UPDATE`; prepare, provider effect, and finalization use
separate transactions, and terminal state plus outbox share one transaction.
The [Java Provider](../postgres/java/src/roo/postgres/Provider.java) and Rust [database adapter](../postgres/rust/src/database.rs)
use independent provider transactions with advisory locks. See the [Java store](../postgres/java/src/roo/postgres/Store.java)
and [coordinator](../postgres/java/src/roo/postgres/CompositionApplication.java). The [historical database receipt](../../../research/postgres-validation.md)
reports the selected schedules and restart evidence; it does not turn the synthetic provider into an external service.

**HTTP** reuses those database application operations behind a loopback
listener. A validated scope selects a synthetic data scope, not an authenticated
tenant. Payment and refund retries carry their existing operation identity.
Line POST has no durable command receipt, so an uncertain response may follow a
committed addition and an identical second request adds another line. The
[HTTP contract](../http/SPEC.md), [Java service](../http/java/src/roo/postgres/HttpService.java),
[Java protocol boundary](../http/java/src/roo/postgres/HttpProtocol.java), and
[Rust server](../http/rust/src/main.rs) make that choice explicit. The recorded
lost-line-response schedule is extra HTTP evidence, not a row in the original
42-scenario oracle.

## Historical receipt inventory

- **In-memory:** [orders-payments-validation.md](../../../research/orders-payments-validation.md)
  records the 2026-10-11 run. It reports Java's 280 explicit assertions and
  intended negative diagnostics, Rust's 20 unit tests and compile-fail checks,
  and 42 oracle rows plus ten malformed fixtures per runner. These were
  deterministic in-memory checks.
- **PostgreSQL:** [postgres-validation.md](../../../research/postgres-validation.md)
  records 42 oracle rows, seven witnessed concurrency schedules, five
  process-kill recoveries, four durable scopes per variant, five SQL probes,
  and twelve snapshots across an actual local server restart. It describes the
  owned synthetic loopback cluster and its specific durability domain.
- **HTTP:** [http-validation.md](../../../research/http-validation.md) records
  42 oracle rows, 41 invalid requests, seven competing schedules, eight
  process-kill schedules, sixteen simultaneous admission waits per variant,
  and request recovery through real local listeners. It also records the
  extra lost-response behavior for payment, refund, and line addition.
- **Prior reviews:** the [base](../../../research/orders-payments-review.md),
  [PostgreSQL](../../../research/postgres-review.md), and
  [HTTP](../../../research/http-review.md) reports accepted their named
  educational candidates. Their dispositions are historical and bounded; this
  design review adds no production approval.

## Questions left open by this evidence

| Question | What the case establishes | What remains unverified |
|---|---|---|
| Who may charge, reconcile, or refund? | Typed IDs and domain operations constrain simulator calls. | Authenticated principal, tenant isolation, and business refund authorization. |
| How long can a provider safely replay a key? | The simulator retains complete records for a scenario; PostgreSQL retains them until harness cleanup. | Real provider key scope, retention expiry, lookup consistency, and operational retry limits. |
| What if a caller cancels during a real network effect? | Selected timeout and response-loss schedules preserve operation identity. | Cancellation propagation, provider outcome, and bounded end-to-end deadlines in production. |
| Which schedules are guaranteed? | Historical receipts witness the listed lock waits and tested recoveries. | Unobserved interleavings, deployment failure modes, and production load behavior. |
| Does a committed database transaction survive every hardware failure? | The PG receipt records local immediate restart and WAL redo with configured durability settings. | Physical power-loss guarantees and storage hardware behavior. |

