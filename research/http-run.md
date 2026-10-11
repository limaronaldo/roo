# HTTP case evolution: execution record

Date: 2026-10-11. User request: evolve the orders/payments case to Java and Rust
HTTP APIs, preserving PostgreSQL, idempotency, failure recovery, shared test
parity and English documentation.

## Authority and baseline

The request authorizes local HTTP listeners, synthetic HTTP clients, builds,
isolated PostgreSQL SQL, controlled interruption/restart of our own processes
and qualification. No existing services, real payment gateways, credential
stores, publication or deployment are in scope. Preserve the previous accepted
PostgreSQL candidate and evidence, identified by
d1594cd230a03bcad6edbb2b590cbcb3bbcbc5f94604cdc4fbb0af59596bd7ac.
The previous cluster is stopped with retained synthetic data. No Git repository
is present. Do not overwrite prior research receipts.

The user-invoked parallel-model-orchestration skill remains applicable, version
1.7.22. Native agents use the established Luna Max and Sol 6.1 Medium allocation.
The integrator's exact model/effort is not exposed; apply supervised coordination
and consult an eligible Sol architect before introducing new HTTP contracts.
No recursive delegates or external agent clients. All compiler/build/database
qualification phases remain serial under integrator ownership. Provider token,
cache, cost and quota telemetry are unavailable, not zero.

## Initial queue

| ID | Requested profile | Exclusive ownership | Dependency | State |
|---|---|---|---|---|
| A | Sol 6.1 Medium | HTTP contract/schema, proposed integration boundaries | Existing PostgreSQL source and current request | completed; http_contract |
| S | Luna Max | Primary-source HTTP/dependency evidence, research/http-sources.md | Current request | completed; http_sources |
| J | Sol 6.1 Medium | New HTTP Java implementation | Accepted A | implemented and qualified; http_java |
| R | Sol 6.1 Medium | New HTTP Rust implementation | Accepted A | implemented and qualified; http_rust |
| D | Luna Max | New HTTP English tutorial | Accepted A and actual source | completed; http_documentation |
| I | Integrator | Shared HTTP oracle/recovery harness, lifecycle, integration/evidence/navigation | Accepted A | completed; qualified and accepted |
| Q | Sol 6.1 Medium | Independent security and final frozen-candidate review | Candidate and executed receipts | completed; http_security and http_final_review |

## Acceptance intent

Both languages expose the same HTTP request/response and error contract over
real PostgreSQL. Original business semantics and payment/refund identities remain
compatible. New transport failures must distinguish an observed response from a
durable effect and document safe recovery. Tests must exercise real HTTP, not
only direct handlers, and compare against shared independent observations.
Concurrency, duplicate requests, malformed input, request conflicts, application
restart and PostgreSQL recovery need bounded synthetic evidence. Preserve the
existing CLI/in-memory regressions and explain language ownership, transaction
scope, inheritance/composition and HTTP transport limits in English.

## Accepted consultation and dispatch

The Sol architect inspected both actual adapter APIs. The accepted plan reuses
them directly: Java same-package compilation into a separate build, Rust path
dependency, no subprocess per request or duplicated business SQL. Payments and
refunds keep their persisted natural identities and full fingerprints; optional
Idempotency-Key must equal the corresponding body identity. Line addition remains
explicitly non-idempotent because a separate receipt cannot make the accepted
self-owned add transaction atomic. No schema migration is needed.

The frozen HTTP SPEC defines exact routes, eleven-string JSON snapshots, status
and error vocabularies, strict input/header limits and disabled-by-default
synthetic controls. Separate startup-configured gated and ordinary processes
avoid mutation of global environment. A small HTTP after-snapshot advisory gate
supports witnessed lost-response SIGKILL tests without custom HTTP framing or
unsupported automatic connection-drop claims.

Java, Rust and English documentation consumers were dispatched once this
contract was accepted. Current public dependencies are pinned: Jackson-core
2.22.3 (already fetched with verified SHA), Axum 0.8.9, Tokio 1.53.2, serde_json
1.0.154, serde 1.0.229, and the accepted PostgreSQL/JDBC versions. Root owns all
fetch/build/HTTP/database qualification. Prior PostgreSQL source/evidence hashes
were verified before intentional root cache-ignore/navigation updates.

## Qualification and corrections

The first live shared HTTP suite passed. Documentation review caught a Rust
snapshot label before that run; root added an actual-scope assertion to every
successful HTTP response. Independent Sol security review then found two low
severity route/header parity defects. Rust and SPEC were corrected, and common
requests were added before final qualification.

Root Clippy found mechanical warnings in successive modules. After the second
failed lint pass, root consulted the Sol architect before the third pass; the
architect confirmed the focused correction and complete rerun. Final formatting,
unit tests, lint, build and documentation all passed. The Java executor now has
32 bounded transport workers, 64 queued tasks and 16 database permits, enabling
an immediate Busy response while all database slots are held.

Final HTTP qualification and historical regression both exited zero. See
http-validation.md for the full shared observations, http-checks.log and
http-regression.log for commands/results, and the new machine-readable HTTP and
PostgreSQL regression receipts. Sixty-three race/crash/drain lock witnesses and
48 separate saturation witnesses support the concurrency assertions. All owned
HTTP processes and the dedicated cluster are stopped. No historical candidate
source or receipt changed; root README and .gitignore are the only intentional
baseline extensions, verified against all 120 previous manifest entries.

The historical PostgreSQL verifier is executed unchanged by a tiny wrapper;
only its evidence destination is redirected to the new HTTP regression receipt.
No historical receipt is overwritten and no business assertion is replaced.

## AI usage summary

Native dispatch accepted the requested profiles: Luna Max for http_sources and
http_documentation; Sol 6.1 Medium for http_contract, http_java, http_rust and
http_security. Root coordinates integration and all heavy executions. A separate
Sol final reviewer will inspect the frozen source/evidence candidate. These are
requested dispatch profiles; returned native tool metadata does not independently
report billed model, token counts or effective effort. Exact root profile is
unavailable. No global model settings or external agent clients were changed.

Provider input/output/cache tokens, cost and quota remain unavailable, not zero.
No credential stores were inspected for telemetry. Independent file ownership,
serial qualification, architect consultation and review records are the
observable orchestration evidence.

| AI / route | Tasks | Requested model → independently reported | Configured effort → reported | Observed participants / model calls | Input/output, cache/reasoning | Coverage |
|---|---|---|---|---|---|---|
| Codex native integrator | Integration, harness, execution, acceptance | Root profile unavailable → unavailable | Unavailable → unavailable | 1 / unobserved | Unavailable | All retained root receipts |
| Codex native delegates | Primary sources, English tutorial | gpt-6-luna → unobserved | max → unobserved | 2 / unobserved | Unavailable | http_sources, http_documentation artifacts |
| Codex native delegates | Contract, Java, Rust, security, final review | gpt-6.1-sol → unobserved | medium → unobserved | 5 / unobserved | Unavailable | Named assignments and returned artifacts/reports |

## Frozen candidate

The initial integrated HTTP candidate is
7111a514cad56aafbd02107d4b7a00c92649f986b799a46c7a051a68fed75af7,
covering 154 source, documentation and evidence files. The manifest excludes
build/dependency caches, private runtime, current HTTP ledger, manifests and
final review status; historical manifests/reviews/ledgers remain included.
An independent Sol 6.1 Medium reviewer, http_final_review, received the exact
manifest, original baseline, source contract and executed receipts. Its mandate
is read-only, without builds/HTTP/SQL or file writes; root will preserve its
returned assessment. This is the seventh delegated participant in the HTTP
evolution; root is the eighth participant. Model-call totals and provider
telemetry remain unobserved.

## Final acceptance

The independent final reviewer returned ACCEPT for the exact 154-file candidate,
after recomputing all listed hashes and reconciling the source, contract,
documentation and retained qualification. No blocking defect or unresolved
actionable finding remained. Root preserved the terminal report in
http-review.md and accepted the bounded local educational deliverable. The
initial and final candidate IDs are identical: no source or evidence changed
during final review. Root rechecked all candidate hashes and local documentation
links after saving the report. Review/run status artifacts are excluded from
the candidate's self-referential hash as declared in its manifest.

This was a manifest review under the parallel task-and-review contract. The
reviewer considered code-review-rm's freeze/coverage concepts; no Git comparison
or full code-review-rm engine/profile approval is claimed. All seven delegated
assignments are terminal. No external publication or deployment occurred.
