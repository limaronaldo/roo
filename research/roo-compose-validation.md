# ROO Compose and CI validation

Date: 2026-10-11. This record qualifies the local container implementation of
the executable adoption track. Documentation and authored implementation
content are in English. ROO remains Relationship & Ownership Oriented design;
the same relationship decisions are exercised through Java composition, Java
Template Method, and Rust composition.

Run from the repository root:

```sh
bash case-studies/orders-payments/track/compose.sh
```

See the [practical Docker guide](../case-studies/orders-payments/track/DOCKER.md)
for learner commands, requirements, evidence, cleanup, and CI behavior. The
[workflow](../.github/workflows/roo-track.yml) invokes this same command.

## Verified results

| Check | Observed result |
|---|---|
| Native Linux ARM64 full qualification | PASS; wrapper exit 0; 43.34 seconds after reviewed packaging repairs |
| Linux AMD64 full qualification | PASS; wrapper exit 0; 293.70 seconds, emulated on the ARM64 Docker host |
| Intentional incomplete starter, e1, all variants | Expected exit 1; all three groups RED; diagnostics exported and cleanup successful |
| Workflow syntax | actionlint PASS |
| Compose configuration, Bash syntax, evidence Python parsing | PASS |
| Hosted GitHub Actions execution | Not executed; workflow definition and local execution are separate evidence |

Each full qualification ran the original evaluator unchanged. It observed
18 expected starter RED groups, 18 completed solution PASS groups, and the
three e6-only PASS groups with e2 still incomplete. The completed solution
checked 31 shared policy cases and 23 malformed-input rejections per variant.
Its PostgreSQL/HTTP boundaries recorded 15 lock witnesses, three persisted
Pending scopes surviving an immediate PostgreSQL restart with WAL redo, and
six deliberately lost HTTP responses. The e6 independence check recorded six
additional HTTP lock witnesses and response-loss recoveries. All tracked HTTP
processes were stopped at the end of the passing checks.

The intentional learner failure used:

```sh
bash case-studies/orders-payments/track/compose.sh starter e1 all
```

Build, evidence collection, export, and cleanup statuses were 0; test,
container, and wrapper statuses were 1. The retained receipt reports a
behavioral failure in all three realizations, rather than an infrastructure
failure. This establishes that a failing learner exercise remains visible to
the shell and CI while preserving useful diagnostics.

## Isolation and source identity

Root observed both full-run containers while running: UID 10001:10001,
network mode `none`, no mounts or published ports, all capabilities dropped,
no privileged mode, and no-new-privileges enabled. PostgreSQL and HTTP used
loopback inside each fresh container filesystem. Both full-run containers and
the intentional-failure container were independently confirmed absent after
the wrapper removed them. Exported evidence contains no PostgreSQL data tree.

All three runs captured the same 117 baked case-study source hashes. Each
receipt's 19 evaluator/learner hashes matched the frozen source target. Image
and container identifiers, tool versions, OS package lists, artifact hashes,
statuses, and complete JSON receipts are retained in the evidence records:

- [Native ARM64 evidence](roo-compose-native-evidence.json).
- [AMD64 emulation evidence](roo-compose-amd64-evidence.json).
- [Intentional learner failure evidence](roo-compose-failure-evidence.json).
- [Host PostgreSQL preservation evidence](roo-compose-isolation-evidence.json).
- [Static validation and preservation checks](roo-compose-static-validation.json).

The host's retained PostgreSQL cluster stayed stopped. Its existing marker,
configuration, and server log hashes remained identical before and after all
container executions. The preceding 215-file baseline retained 213 files
byte-for-byte, including all 76 historical research files. Only `.gitignore`
and the track README received additions; their original text was preserved. Original application,
schema, fixture, evaluator, template, learner, identifier, and lock files were
preserved. Eight new source paths supply the Compose/CI implementation and
English guide.

## Reproduction and proof limits

The [pin record](roo-compose-pins.json) identifies immutable multiarchitecture
base image digests and action commit SHAs. Existing Cargo locks and
SHA-verified Java jar fetchers are preserved. Dependency retrieval occurs
during image construction; runtime tests passed without external networking.
Bookworm OS packages follow the current security repository, so this is
functional reproduction with recorded package versions, not a promise of
byte-identical future OS images.

The first three builds failed before behavioral tests: a missing executable
search path, a missing PostgreSQL runtime library, and selection of an older
libpq from the base image. The [qualification ledger](roo-compose-qualification.json)
retains these attempts. A distinct architect reviewed the packaging repairs;
the final builds verified the loaded libpq 18.6 path, version, required symbol,
and eager client startup. The optional PostgreSQL LLVM JIT extension closure
was not qualified by this track.

AMD64 execution here used local emulation, not a hosted GitHub runner or
native AMD64 hardware. No workflow was dispatched, no repository was
published, and no commit or push was performed. The bounded tests establish
the exercised concurrency, process-death, restart/WAL, idempotency, outbox,
and HTTP-loss behaviors; they do not establish arbitrary interleavings,
hardware power-loss behavior, external provider behavior, or production
readiness. See the [track contract](../case-studies/orders-payments/track/SPEC.md).

## Review target and AI usage

The source review target contains 223 files with identity
`1f2ca6ff019010938513a5f7bece5d6e376640297a3eadabee6ab7d5b20713b4`.
All three runtime evidence bundles bind their source identity to that target.
The final candidate manifest also includes the new qualification records.
Independent acceptance and its scope are recorded in
[the final review](roo-compose-review.md).

The [run record](roo-compose-run.md) reports the integrator and six unique
delegates: four requested Sol 6.1 Medium and two requested Luna Max. Requested
profiles are distinct from actual provider telemetry. Actual model/effort,
provider-call counts, tokens, cache, reasoning tokens, cost, and quota were
not exposed; unavailable values are not reported as zero.
