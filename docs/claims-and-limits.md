# Claims and limits

ROO is a practitioner-method proposal with an executable teaching laboratory.
v0.1.0 is the first edition (preview); a published snapshot is not a maturity
certification. The project has no documented field study demonstrating that
ROO improves delivery speed, defect rates, or architectural quality.

## What the evidence supports

| Claim | Relevant evidence | Boundary |
|---|---|---|
| A relationship can be described before choosing a language mechanism | [Canonical method](02-relationship-design.md) and [completed templates](../case-studies/orders-payments/adoption/relationship-contract.md) | A proposed design and review vocabulary |
| The root Rust lab checks selected ownership and API restrictions | [Source](../src/lib.rs), positive and compile-fail doctests, [original validation](../research/validation.md) | Safe local code, the tested API, and intended diagnostics |
| Chapter Rust and Java examples compile and exercise stated behaviors | [Documentation example checks](../scripts/check_doc_examples.py) and the documentation workflow | Declared snippets and assertions; illustrative protocol/configuration blocks are excluded |
| Three case variants match one expected-result fixture | [In-memory specification](../case-studies/orders-payments/SPEC.md), [oracle](../case-studies/orders-payments/expected.tsv), [dated validation](../research/orders-payments-validation.md) | Deterministic simulator scenarios; the shared oracle is project-authored |
| Persistent recovery handles the tested competing workers and restarts | [PostgreSQL specification](../case-studies/orders-payments/postgres/SPEC.md) and [dated validation](../research/postgres-validation.md) | A dedicated local PostgreSQL cluster; provider and inbox use that same server/WAL |
| HTTP retry and response-loss recovery preserve the specified effects | [HTTP specification](../case-studies/orders-payments/http/SPEC.md) and [dated validation](../research/http-validation.md) | Loopback APIs, bounded inputs/workers, synthetic provider |
| The adoption track ran on a hosted AMD64 runner | [Hosted reproduction](10-github-reproduction.md) with run and artifact references | The identified commit, run, platform, and scenarios |

A green badge identifies the latest workflow result. For a behavioral claim,
inspect the run's commit, executed scenarios, and receipts. Historical receipts
describe their original candidate; editing a chapter does not rerun them.

## What requires further work

The teaching cases omit caller authentication, tenant authorization, revocation,
and real payment networks. Scope keys and loopback restrictions are fixture
controls. A live system must implement an authorization policy, verify its
provider's idempotency/key-retention contract, and define operational handling
of unresolved attempts, cancellation, retention, and deletion.

Local rollback does not reverse an independent provider effect. Borrow checking
does not serialize another process's database writes. Crash-restart/WAL tests
exercise configured PostgreSQL recovery, rather than physical power loss or
every possible interleaving. Capacity and performance need separate workloads.

Compilation checks types and access rules; runtime tests observe selected
behaviors; database checks cover the examined storage boundary; protocol tests
cover the exercised exchange. Human review evaluates policy and tradeoffs.
Evidence from one boundary cannot substitute for evidence at another.

## Review and authorship

The initial review used a separate AI agent from the same requested model
family as some authors. This is separation of roles, not independent human
validation. No completed external Rust or DDD/architecture human review is
documented. [How ROO was made](how-roo-was-made.md) links the preserved records.

The underlying concepts have established prior art. ROO proposes their
integration into a compact relationship contract and adoption procedure;
it makes no priority claim for ownership types, composition, capabilities,
typestate, or consistency boundaries.
