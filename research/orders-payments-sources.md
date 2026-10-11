# Orders and payments case: primary-source evidence

Checked: 2026-10-11. This ledger supports the Java/Rust case in
`case-studies/orders-payments/SPEC.md`. The specification is the simulator
contract; language specifications and provider documentation are evidence for
their own scope, not approval of a production integration.

## Scope and evidence categories

Language entries state Rust/Java behavior only; provider entries are scoped to
the cited provider and API version. Stripe API v1 and Adyen do not share one
idempotency contract. The frozen case uses deterministic, single-threaded,
in-memory adapters in a fresh scenario. It moves no money and establishes no
production guarantee. No SDK, provider account, credentials, or API request was
used.

## Rust: ownership, traits, and errors

1. [Rust Reference: move and copy expressions](https://doc.rust-lang.org/reference/expressions.html)
   `Copy` values are copied; other moved locals are deinitialized until
   reinitialized. This explains local value ownership, not ownership of a charge
   held by a payment provider.

2. [Rust Reference: destructors](https://doc.rust-lang.org/reference/destructors.html)
   Initialized values are dropped at specified scope exits, but process
   termination without unwinding and `mem::forget` can skip destructors. `Drop`
   is local cleanup, not a reliable refund, rollback, or remote compensation.

3. [The Rust Programming Language: trait objects](https://doc.rust-lang.org/book/ch18-02-trait-objects.html)
   Rust has no class inheritance; trait objects provide shared behavior without
   adding data to implementing types. Compare composition and traits here.
   Generic bounds use static dispatch; trait objects use dynamic dispatch.

4. [Rust Reference: traits](https://doc.rust-lang.org/reference/items/traits.html)
   Traits define interfaces implemented for specific types. A payment adapter
   trait is a behavior boundary, not a data-bearing base class.

5. [Rust standard library: `Result`](https://doc.rust-lang.org/std/result/enum.Result.html)
   `Result<T, E>` represents `Ok(T)` or `Err(E)`. It does not undo an earlier
   side effect or persist a recovery record.

6. [The Rust Programming Language: recoverable errors and `?`](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html)
   `?` returns an error early from the current function; it is not rollback. A
   payment call can fail locally after the remote side commits, so the domain
   needs `UnknownOutcome` and a recovery path.

**Design inference for typestate.** Marker types can restrict which operations a
local value exposes at compile time. A marker cannot establish the current state
of a remote payment after a lost response, after reload, or after an external
transition. Persist the intent and reconcile observed provider state at runtime;
do not present typestate as a distributed-state guarantee.

## Java 21: inheritance, values, access, and failures

7. [Java Language Specification 21, Chapter 8: classes](https://docs.oracle.com/javase/specs/jls/se21/html/jls-8.html)
   §§8.1.1.2 and 8.4.3.3 define `sealed`, `final`, and final methods. A final
   coordinator method can preserve template-algorithm order, but cannot make
   hooks or I/O atomic. §8.10 defines records as restricted aggregates with
   private component fields and public accessors; records suit typed identifiers
   and money, with validation in constructors.

8. [Java Language Specification 21, Chapter 9: interfaces](https://docs.oracle.com/javase/specs/jls/se21/html/jls-9.html)
   §§9.1.1.4 and 9.1.4 let a sealed interface enumerate permitted subtypes. A
   sealed interface plus records can model a closed result family; transitions
   and remote reconciliation still need runtime code and checks.

9. [Java Language Specification 21, Chapter 6: access control](https://docs.oracle.com/javase/specs/jls/se21/html/jls-6.html)
   §6.6 limits `private` member access to its enclosing top-level declaration.
   Private state plus invariant-preserving methods supports Java encapsulation;
   it is not durable storage or transactionality.

10. [Java Language Specification 21, Chapter 11: exceptions](https://docs.oracle.com/javase/specs/jls/se21/html/jls-11.html)
    §11.1.1 distinguishes checked and unchecked exceptions; checked handling is
    subject to compile-time checks (§11.2). A sealed return family can make
    domain outcomes explicit, but neither form determines whether a timed-out
    request took effect. This union is a proposed API design, not a standard
    library `Result` type.

## Provider protocol lineage: documented examples, not universal rules

11. [Stripe API v1: idempotent requests](https://docs.stripe.com/api/idempotent_requests)
    Stripe API v1 saves and replays the first status/body after endpoint
    execution starts, including `500`; it rejects a key reused with different
    parameters. Validation failures and pre-execution concurrent conflicts are
    not saved. Keys may be pruned after at least 24 hours; reuse after pruning
    starts a new request. API v2 differs, so scope this comparison to v1.

12. [Adyen API idempotency](https://docs.adyen.com/development-resources/api-idempotency)
    Adyen documents same-key timeout retries, company-account scope, and keys
    valid for 7–14 days; separate regional endpoints do not cross-check keys.
    Concurrent duplicates can return a conflict or a provider-marked transient
    error. Retention, scope, and retry rules are provider-specific.

13. [Stripe PaymentIntents API](https://docs.stripe.com/api/payment_intents)
    Stripe recommends one PaymentIntent per order/session; it moves through
    states and creates at most one successful charge. Retrieval uses its ID;
    the [object status field](https://docs.stripe.com/api/payment_intents/object)
    includes `requires_payment_method`, `requires_confirmation`, `requires_action`,
    `processing`, `requires_capture`, `canceled`, and `succeeded`. This separates
    a known object status from a caller's unknown observation after timeout.

14. [Stripe webhook delivery and duplicate handling](https://docs.stripe.com/webhooks)
    Stripe retries live deliveries for up to three days, does not guarantee
    order, and warns of duplicates. Deduplicate event IDs; distinct IDs can
    represent the same object and event type. Handlers should be idempotent and
    retrieve current objects when needed. Stripe signs events and requires
    signature verification before acting on them.

15. [Chris Richardson, transactional outbox pattern](https://microservices.io/patterns/data/transactional-outbox.html)
    Store the event in the same database transaction as the business update,
    then publish through a relay. A relay can publish twice after a crash between
    publish and recording success, so consumers must be idempotent. The pattern
    page supports this failure model, not in-memory durability.

16. [Stripe Refund object and endpoints](https://docs.stripe.com/api/refunds)
    Refunds may be partial and can have `pending`, `requires_action`, `succeeded`,
    `failed`, or `canceled` status. A refund is its own provider operation, not an
    automatic reversal when an order object is dropped or rolled back.

17. [Stripe PaymentIntent capture](https://docs.stripe.com/api/payment_intents/capture)
    Manual capture applies to `requires_capture`; `amount_to_capture` may be
    less than or equal to the original amount. The case models a complete charge.

18. [Stripe supported currencies](https://docs.stripe.com/currencies)
    API amounts use currency minor units; some currencies are zero-decimal or
    have special cases. USD-only signed-64-bit arithmetic is not a full money
    model.

19. [Stripe API authentication](https://docs.stripe.com/api/authentication)
    Stripe requires API keys and HTTPS. The simulator has no credentials, HTTP
    client, signature validation, customer data, or payment-method handling.

## Evidence mapped to the frozen simulator

- **Stable request identity:** The simulator retains one immutable payment or
  refund request tuple per typed key for the entire fresh scenario. An identical
  request returns the recorded result; any changed field returns `KeyConflict`.
  This is an explicit simulator guarantee. Stripe compares endpoint and
  parameters within its key window; Adyen defines key scope/validity differently.
  Neither provider's documented semantics are encoded in the simulator.
- **Unknown versus NotFound:** `Unknown` means the observation is inconclusive or
  lookup is unavailable. `NotFound` means the simulator's complete in-memory
  provider map contains no record. In a real integration, a local missing ID or
  a provider lookup miss must not be promoted to “no charge” without a
  provider-specific reconciliation rule. Retry only with the same persisted
  identity and within the applicable provider contract; never mint a new key to
  resolve uncertainty.
- **Remote/local boundary:** The fixture separates a remote effect from the
  later simulated local commit. A timeout after a successful remote effect leaves
  the local order pending; reconciliation finishes the local state transition
  without creating another simulated effect. A production store needs durable
  intent, recovery, and operational handling; this example has none.
- **Refund compensation:** The case permits one full refund and only approval or
  unknown outcomes. Real Stripe refunds may be partial or move through other
  states and can fail. Do not describe a refund as an atomic rollback or claim
  the case proves compensation always succeeds.
- **Outbox delivery:** The simulated local commit installs order state and an
  outbox fact together; a selected acknowledgement failure demonstrates
  redelivery and consumer deduplication. The adapter does not survive process
  loss and has no broker, durable inbox, authentication, signature check,
  concurrent relay, event reordering, or retention policy. It demonstrates the
  pattern's duplicate-delivery shape, not a durable transactional outbox.
- **Exactly-once language:** Avoid “exactly once” across systems. At most one
  simulated provider effect follows from the simulator's complete stable-key
  map. Real API idempotency is limited by key, request, scope, concurrent
  behavior, and retention; a real outbox relay may repeat. State the boundaries
  for every guarantee.

## Deliberate omissions to state in the case README

| Real-system concern | Primary evidence | Bounded case behavior |
| --- | --- | --- |
| Key retention and key scope | Stripe v1 and Adyen idempotency docs | Fresh map per scenario; no clock or expiry |
| Request mismatch and concurrent duplicate | Stripe and Adyen idempotency docs | Exact tuple mismatch is rejected; single-threaded execution |
| Partial capture/refund and refund lifecycle | Stripe capture and Refund API | No capture phase; one full refund, with approve/unknown only |
| Multiple currencies and minor-unit rules | Stripe currency guide | USD only; integer minor units |
| Webhook authentication, retries, order, duplicates | Stripe webhook docs; Adyen idempotency docs | Local relay only; selected duplicate and ack-failure cases |
| API authentication and transport | Stripe authentication docs | No credentials, network, SDK, provider account, or payment data |
| Process crashes and durable transactional outbox | Richardson outbox pattern | In-memory commit simulation; no disk/broker/crash proof |

## Retrieval record

The 20 unique URLs listed above are primary language specifications/reference
material, provider-authored documentation, or the pattern author's own page.
The Stripe PaymentIntents lifecycle guide rendered only its title and navigation
in the browser reader, so the API reference's statuses, endpoints, and events
were used instead. Current Rust Reference and standard-library pages were read;
version-pinned 1.96 URLs were inaccessible in the browser reader. No code was
compiled or executed in this source-research lane.
