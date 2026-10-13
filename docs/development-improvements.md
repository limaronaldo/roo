# Development improvements

The 2026-10-13 correction candidate strengthens the reference laboratories,
verification controls, and evidence handling. It retains the eight-field
Relationship Contract and six-step procedure. The changes are **unreleased**;
v0.4.3 remains the published documentation edition.

This guide describes the port candidate `60406df9a44b052e7b4ca3ed24f80136040936ef`.
Its [per-finding report](../research/repo-review-2026-10-12-port-2026-10-13.md)
records the corrections, retained failures, checks, and remaining limitations.
The documentation additions on top of that candidate do not change laboratory
code or transfer qualification from another branch.

## Behavior and boundaries

| Correction | Result | Source and checks |
|---|---|---|
| Java store access | Code outside the package cannot construct the concrete store and forge a state transition. This is a package boundary; reflection is not qualified. | [Java implementation and negative compilation samples](../case-studies/orders-payments/java/README.md) |
| Declined refunds | The Java in-memory implementations and Rust PostgreSQL adapter reject the declined operation without leaving the order in `Refunding`. | [Shared case](../case-studies/orders-payments/README.md), [PostgreSQL checks](../case-studies/orders-payments/postgres/README.md) |
| Conflicting event delivery | An identical redelivery is deduplicated. A different fact under the same event ID is detected, preserves the first fact, and remains unacknowledged. The implementations use different error representations. | [Shared specification](../case-studies/orders-payments/SPEC.md), [Rust consumer](../case-studies/orders-payments/rust/README.md) |
| HTTP request handling | Size errors are distinguished from framing faults; fragments are rejected; validation precedence is explicit; slow body readers have a bounded admission and deadline. | [HTTP specification](../case-studies/orders-payments/http/SPEC.md), [HTTP verification](../case-studies/orders-payments/http/README.md) |
| Malformed authorization fixtures | An empty scenario name produces a diagnosed fixture error in Java and Rust. | [Authorization example](../case-studies/orders-payments/authorization/README.md) |

These are bounded implementation corrections. They do not establish that every
interleaving, provider failure, or production workload is safe.

## Checks and evidence

- **Real boundary probes.** The adoption track exercises the runner and HTTP
  server. Its report records three deliberately broken server behaviors caught
  by the probes. See the [track specification](../case-studies/orders-payments/track/SPEC.md).
- **Host-owned Docker status.** The wrapper obtains the exit status through
  Docker on the host and cross-checks inspection. Container output goes into
  a separate evidence directory. The configured limits are two CPUs, 4 GiB,
  and 256 processes, with external networking disabled, no host mounts, and
  no published ports. Private loopback remains available to the laboratory.
  The writable layer has no portable disk quota. See [Docker and CI](../case-studies/orders-payments/track/DOCKER.md).
- **Executable CI definitions.** The base workflow calls the base, PostgreSQL,
  HTTP, and regression verifiers, with separate receipt paths and artifact
  collection. It installs PostgreSQL 18 explicitly on Ubuntu 24.04. The source
  definition is available in the [base workflow](../.github/workflows/orders-payments-base.yml).
  A configured workflow is not a successful hosted run.
- **Privacy checks.** The [tracked-file guard](../scripts/check_local_paths.py)
  checks for authoring-machine paths, assistant transcript paths, and session
  identifiers. Its report records injected negative probes. It does not certify
  every form of sensitive information or rewrite repository history.
- **Dated provenance notes.** Claims that could not be reproduced from Git have
  dated qualifications. The [manifest audit](../research/manifest-audit.py)
  makes the comparison reproducible; a later passing check does not establish
  what happened in an earlier run.

## Reproduce without replacing historical receipts

For the complete adoption-track qualification, follow the
[Docker guide](../case-studies/orders-payments/track/DOCKER.md). For native
verification, follow [the contributor checks](../CONTRIBUTING.md#validate-the-affected-behavior)
and set a caller-owned evidence destination for each phase.

The HTTP verifier defaults to an ignored scratch receipt. An explicit
`--evidence-output` or `ROO_EVIDENCE_PATH` adds the requested output. PostgreSQL
still refreshes its tracked historical receipt when no destination is supplied:
**set `ROO_EVIDENCE_PATH` before running it locally**. This asymmetry remains a
documented follow-up, not a correction claimed here.

## Validation scope

| Evidence | What it establishes | What this evidence does not establish |
|---|---|---|
| The port report's 27 passing local checks | Recorded local qualification of the correction candidate, including verifier, compiler, documentation, privacy, and workflow-lint checks | Hosted execution of the candidate |
| Local Java qualification on JDK 26 with `--release 21` | Compilation targeting Java 21 and the recorded checks on the local runtime | Behavior on an actual JDK 21 runtime |
| Source-linked implementation and probe checks | The properties exercised by those particular scenarios and controls | Exhaustive correctness, external provider behavior, and production readiness |
| This README and site update | Presentation of the corrections, their evidence, and their remaining limitations | A new release, completed human evaluation, or evidence of ROO's efficacy |

The reported check count belongs to the dated port report; this documentation
update does not claim to have rerun its full qualification. Subsequent
[CI runs](https://github.com/limaronaldo/roo/actions) record their own checkout
and evidence; compare those source identities before transferring a result.
Publication, hosted CI, and human evaluation are separate outcomes. The frozen
MAAD pilot is preserved; no MAAD run or empirical result is introduced by this update.
