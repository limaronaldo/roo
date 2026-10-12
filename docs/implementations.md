# Implementations and evidence

ROO's [method](02-relationship-design.md) defines decisions. These laboratories
show particular mechanisms and collect bounded evidence. Java, Rust,
PostgreSQL, HTTP, Docker, and CI are current reference choices; adopting the
method does not require them.

Start with the [payment recovery](../case-studies/orders-payments/DESIGN.md) or
[authorization](../case-studies/orders-payments/authorization/DESIGN.md) design
case. Choose an implementation only after stating its contract.

## Language mappings

| Guide | What it contributes |
|---|---|
| [Cross-language transfer](06-cross-language.md) | Different language realizations of the same relationship decisions |
| [Rust relationship mapping](rust-relationship-mapping.md) | Receivers, ownership, handles, synchronization, and limits of compiler evidence |
| [OO concept atlas](03-concept-atlas.md) | Classical concepts translated into concrete language mechanisms |
| [GoF pattern translations](04-pattern-catalog.md) | Pattern intent, Rust candidates, and tradeoffs |
| [Rust and object design](08-rust-and-object-design.md) | Worked object-design translations, including CI-tested chapter snippets |
| [Rust laboratory](laboratory.md) | Executable root examples and expected compiler rejections |
| [Guided learning laboratory](07-learning-path.md) | A syllabus that pairs neutral design practice with Rust implementation |

## Case-study laboratories

| Laboratory | Implementations and observed boundary | Limits to retain |
|---|---|---|
| [In-memory orders/payments](../case-studies/orders-payments/README.md) | Java composition, Java Template Method, Rust composition; shared outcomes and injected failure | Simulated retention and single-process effects |
| [Local authorization](../case-studies/orders-payments/authorization/README.md) | Java/Rust approval and revocation schedules | Process-local policy and synchronization |
| [PostgreSQL persistence](../case-studies/orders-payments/postgres/README.md) | Durable identities, witnessed concurrency, restart/recovery | Selected storage semantics and one physical provider/app storage domain |
| [HTTP adapters](../case-studies/orders-payments/http/README.md) | Java/Rust requests, idempotency, overlap, response loss | Teaching transport and simulated provider |
| [Persistent operation permissions](../case-studies/orders-payments/http/AUTHORIZATION.md) | Exact-operation policy, revocation, and recovery across the three API variants | Synthetic principal assertions, not real authentication |
| [Executable adoption track](../case-studies/orders-payments/track/README.md) | Six starter/solution exercises with shared expectations | Bounded educational tasks and intentionally incomplete starters |

The lab specifications retain their exact APIs, identifiers, schemas, and
failure semantics. Editorial separation does not change executable behavior.

## Other technologies

Use the [technology-selection guide](technology-selection.md) to evaluate
another language, runtime, storage model, policy service, or transport. Carry
the invariant and relevant scenarios into that candidate; state changes to
promises explicitly. Proposed alternatives have no implementation or test
coverage here until separate evidence is collected.

For reproduction, see [Docker and CI](../case-studies/orders-payments/track/DOCKER.md)
and [hosted qualification](10-github-reproduction.md). Report evidence for the
actual candidate rather than reusing an older result as a current run.
[Claims and limits](claims-and-limits.md) separates those evidence classes.
