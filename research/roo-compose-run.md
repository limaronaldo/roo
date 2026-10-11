# ROO Compose and CI reproduction run

Date: 2026-10-11. User request: make the executable adoption track reproducible
with Docker Compose and GitHub Actions, retaining equivalent Java/Rust tests,
isolated PostgreSQL, and English documentation.

## Authority and route

Apply parallel-model-orchestration 1.7.22. Root's actual model and effort are
unreported; use supervised coordination and bounded Sol architectural
consultation before new infrastructure design. Native collaboration exposes
nine concurrent slots including root. Preserve the established requested
profiles: gpt-6.1-sol / medium and gpt-6-luna / max. Requested dispatch values
do not authenticate actual provider identity. Tokens, cache, cost, quota,
and provider-call counts are unavailable, not zero. No external clients,
recursive delegates, credential/global configuration changes, publication,
GitHub workflow dispatch, commit or push.

The preceding 212-file track candidate verified exactly. The baseline includes
its final manifest, ledger and review: 215 files. Preserve source cases,
schemas, identifiers, learner implementations, evaluator contracts, original
templates, and all prior research records. Any necessary harness change must
retain existing cases and be explicitly reviewed. Workspace has no Git
metadata. Memory lookup for the exact project path returned no relevant entry;
no memory-derived project facts are used.

Local container builds and execution of disposable synthetic PostgreSQL/HTTP
tests are within the user's requested scope. Docker client/server and Compose
are available; only task-owned containers, networks and data may be created or
cleaned up. The host's retained PostgreSQL cluster and unrelated Docker
resources must not be modified. Root serializes heavy builds and runtime
qualification. Two failed semantic correction attempts on the same slice
require distinct architect/reviewer consultation before a third.

## Queue

| ID | Requested profile | Responsibility | State |
|---|---|---|---|
| A | Sol 6.1 Medium | Bounded read-only architecture consultation for isolated Compose and CI | completed; accepted recipe |
| S | Luna Max | Read-only portability/source inventory and test evidence requirements | completed |
| C | Sol 6.1 Medium | Docker image, Compose, isolated execution/artifact wrapper | completed; local ARM64 and AMD64 qualification PASS |
| W | Sol 6.1 Medium | GitHub Actions using shared wrapper and immutable action pins | completed; actionlint PASS |
| D | Luna Max | English container and CI adoption documentation | completed |
| Q | Sol 6.1 Medium | Independent source and final evidence review | completed; final 235-file candidate ACCEPT, no actionable findings |
| I | Root, unreported | Baseline, integration contracts, serial runtime qualification, evidence | completed; local qualification, preservation and independent acceptance verified |

## Acceptance

A fresh container image builds pinned Java/Rust dependencies and runs the
existing shared test matrix with its own PostgreSQL lifecycle, including
concurrency, process death, database restart/WAL recovery, HTTP loss, starter
RED qualification, solution parity, and e6 independence. Docker Compose and
GitHub Actions use the same entry point. Preserve receipts on failure and
return the test exit status. Document exact local and CI commands, isolation,
cleanup, dependency/version pins, editable learner workflow, and proof limits
in English. Validate actual local Compose execution plus workflow syntax;
remote GitHub execution is not claimed without a real authorized run.

## Accepted architecture and implementation contracts

The distinct Sol architect inspected critical evaluator and lifecycle sources
and approved one nonroot runner container with the PostgreSQL server binaries,
JDK 21, Rust 1.96, Python/Bash and build tools. Existing evaluator and source
cases stay unchanged. An external database service would conflict with the
loopback endpoint guard and evaluator-owned immediate restart/WAL checks.
Runtime has no external network, published ports, Docker socket, privileged
mode, host runtime mount or persistent database volume. Dependencies are
fetched/verified during image construction. Every invocation gets a fresh
container writable layer; only selected evidence is copied out before removing
that specific container. Host PostgreSQL and historical data remain untouched.

Common host entry: `bash case-studies/orders-payments/track/compose.sh`.
Default mode `qualify` invokes existing `verify.sh` unchanged. Learner modes
`starter|solution [e1|e2|e3|e4|e5|e6|all] [java-composition|java-inheritance|rust|all]`
compile that source set then invoke the existing evaluator within one container.
Rebuild from local source on each invocation; no host checkout write mount.
Default artifacts: `artifacts/roo-track/<unique-run-id>/`. Preserve build/run
logs, selected JSON receipts and server logs, versions/command/source identity
and exit status, including failures. Never export the PostgreSQL data tree or
environment credentials. A failed learner check must remain a nonzero exit.

C owns compose.yaml, .dockerignore, track/compose.sh and track/docker/. W owns
.github/workflows/roo-track.yml. D owns track/DOCKER.md and a navigation/workflow
section in track/README.md. Root owns .gitignore and new roo-compose research
records. Disjoint paths replace worktrees because the workspace has no Git
metadata. All participants must accommodate others' changes. Heavy checks
remain serialized by root. Image digests and action SHAs resolve live in
roo-compose-pins.json. CI uses the same host wrapper, read-only permissions,
immutable action SHAs, bounded timeout, no secrets and always-upload evidence.

## Packaging qualification and bounded corrections

The first image build failed before tests because PATH omitted ldconfig.
Selecting /sbin/ldconfig fixed that stage; the next build exposed missing
liburing.so.2. Distinct architectural inspection of exact PGDG 18.6 package
dependencies approved explicit core libraries/timezone data, the official
image's shared configuration sample symlink target, and early ELF checks.
The second semantic correction reached psql but selected the base image's
older libpq, failing on PQsendPipelineSync. Before a third correction, root
consulted the distinct architect again. Exact client/library ELF metadata
supported an explicit loader path for the pinned PostgreSQL 18.6 copy plus
loaded-path/version/symbol/eager-startup guards before dependency fetching.
Failed attempts remain in roo-compose-qualification.json and their artifact
directories; none establishes a behavioral test pass.

Primary packaging references inspected by the architect:
- https://packages.debian.org/bookworm/arm64/liburing2/filelist
- https://apt.postgresql.org/pub/repos/apt/dists/bookworm-pgdg/main/binary-arm64/Packages.gz
- https://raw.githubusercontent.com/docker-library/postgres/master/18/bookworm/Dockerfile
- https://manpages.debian.org/bookworm/manpages/ld.so.8.en.html
- https://www.postgresql.org/docs/18/libpq-misc.html

The host marked PostgreSQL cluster was independently confirmed stopped;
its marker, configuration and server-log hashes were captured before runtime
qualification, in addition to the no-host-mount boundary.

Native ARM64 and locally emulated AMD64 full Compose qualifications passed
after the reviewed packaging repairs. Root observed both running containers
as UID 10001:10001, network none, no mounts or published ports, all capabilities
dropped, and no privileged mode. Intentional starter e1 failure across all
variants returned 1 while exporting diagnostics and removing its container.
All runtime containers were independently confirmed absent. The host cluster
remained stopped with identical marker/configuration/server-log hashes. Source
review target: `1f2ca6ff019010938513a5f7bece5d6e376640297a3eadabee6ab7d5b20713b4`, 223 files.


## Qualification evidence

Root serialized six Compose invocations: three pre-test image-build failures,
then native ARM64 full qualification, AMD64 full qualification under local
emulation, and an intentional incomplete-starter learner check. Heavy builds
and database/process-lifecycle tests were serialized to avoid resource
contention and overlapping evidence. The root evidence parser initially
interpreted receipt-relative paths from the repository root; correcting that
parser to use the track directory established the 19 source-hash matches. A
separate documentation assertion was corrected from append-only to additions
only: the README adds a guide link within the text, preserving original lines
and code fences. Neither evidence-parser correction changed the implementation
or reran the behavioral matrix.

[Validation](roo-compose-validation.md) distinguishes observed local platform
results, workflow syntax, preserved files, isolation, and hosted-CI proof limits.
[Qualification attempts](roo-compose-qualification.json) retain failed builds
and successful executions. Self-contained native, AMD64, intentional-failure,
and isolation JSON records preserve the relevant receipts/status/source hashes.
Raw per-run logs remain under the ignored artifacts/roo-track directories.
No implementation source changed after the successful runtime qualifications.

## AI usage report

This table records actual participating agents, requested profiles, and
telemetry coverage. Native collaboration dispatch metadata is the source for
requested settings and unique participants; it does not authenticate actual
provider model identity. The root's model/effort were not supplied. All six
delegates are distinct native agents; architectural repair consultations reused
the same architect and do not increase that count. No external clients or
recursive delegates were used.

| AI / route | Task | Requested model -> reported model | Configured effort -> reported effort | Unique agents / provider calls | Input / output tokens | Cache / reasoning | Coverage |
|---|---|---|---|---|---|---|---|
| Native root | Integration, preservation, serialized runtime qualification | not exposed -> not exposed | not exposed -> not exposed | 1 / not exposed | not exposed | not exposed | root tool results, source hashes, local receipts |
| Native delegates A, C, W, Q | Architecture, containers, workflow, independent review | gpt-6.1-sol -> not exposed | medium -> not exposed | 4 / not exposed | not exposed | not exposed | observed native dispatches and terminal artifacts; Q accepted final frozen candidate |
| Native delegates S, D | Inventory and English documentation | gpt-6-luna -> not exposed | max -> not exposed | 2 / not exposed | not exposed | not exposed | observed native dispatches and terminal artifacts |

Participant totals are calculated from seven unique task identities: root plus
six delegates. Provider-call counts, token input/output, cache, reasoning tokens,
cost, quota and peak concurrency were not exposed and are not reported as zero.
No model fallback was observable; that does not establish exclusive provider
identity. Runtime durations are local command measurements, not AI effort or
cost estimates.


## Final acceptance

Distinct reviewer Q returned terminal ACCEPT for final candidate
`b8cbee1a27fa27416a8f6f1a6207a9da85a13d337b030d403c1ffde136d5b5d7`: all
235 manifest hashes/sizes and the 608-line authored diff reconciled; 223 source
files remained identical to the reviewed runtime target. Q independently
reconciled all 133 exported artifact hashes/sizes and embedded receipts, source
identities, successful platform checks, intentional failure, observed isolation,
host preservation, and official workflow pin inputs. No actionable findings.
The [final verdict](roo-compose-review.md) records scope and limitations.

Root's final read-only recheck confirmed the accepted candidate identity and
all file bytes, 213 preserved baseline files including 76 historical research
records, all three runtime containers absent, and the host PostgreSQL cluster
still stopped with its captured hashes unchanged. All six delegates and root
completed their assigned scope. Hosted CI was prepared and syntax-checked,
but was not dispatched. No commit, push, publication, unrelated resource
cleanup, host database mutation, or global configuration change was performed.
