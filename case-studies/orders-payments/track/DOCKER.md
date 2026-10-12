# Docker Compose and GitHub Actions

Use this guide to run the ROO adoption track in a fresh, isolated container or
through the repository's GitHub Actions workflow. Run the commands below from
the repository root.

## Requirements and isolation

The host needs Bash, common POSIX utilities, Docker Engine, and the Docker
Compose plugin. It does not need a host installation of Python, Java, Rust, or
PostgreSQL. The first image build needs network access to retrieve the pinned
base images, Bookworm package metadata and packages, locked Rust dependencies,
and verified Java jars; the tests run with loopback available and external
networking disabled.

One nonroot container includes PostgreSQL 18.6 server tools, JDK 21, Rust
1.96.0, Python, and Bash. PostgreSQL runs in that same container on a dynamic
loopback port. The evaluator owns its start, stop, and immediate restart/WAL
checks, and its endpoint guard requires loopback; a separate database service
would not satisfy that lifecycle. The test container has no published ports,
external network, host mounts, Docker socket, or persistent database volume.
Each run starts with a fresh container filesystem, so the synthetic database
is discarded after evidence is copied out.

The base image index digests and GitHub Action commit pins are recorded in
[`research/roo-compose-pins.json`](../../../research/roo-compose-pins.json).
Cargo dependencies are locked, and the Java jars are verified by their
existing fetch helpers. Debian Bookworm OS packages are installed from the
current security repository during image construction; they are not pinned to
a dated package snapshot, so a later rebuild can include newer Bookworm
security updates. The captured package list records the actual packages in a
run.

## Run the full qualification

With the starter files untouched, run:

```sh
bash case-studies/orders-payments/track/compose.sh
```

The default `qualify` mode builds an image from the current checkout, starts one
new container, and runs the existing track `verify.sh`. It checks the
starter's expected behavioral RED groups, the completed solution across Java
composition, Java Template Method, and Rust composition, and the regression
that completes only e6 while confirming e2 remains incomplete. It then checks
PostgreSQL/HTTP Rust formatting, native tests, and Clippy, and runs both the
legacy HTTP verifier and the [durable authorization suite](../http/AUTHORIZATION.md).
The latter uses the same matrix in all three language variants, including
revocation between observation and execution and recovery after restart.
The wrapper
returns the qualification's nonzero status if a check fails.

This full qualification deliberately expects the starter gaps to remain
incomplete. After you solve any starter exercise, use a learner mode below;
the full qualification will no longer be the appropriate check for that
edited starter.

## Check learner edits

Choose `starter` or `solution`, then provide an exercise (`e1` through `e6`, or
`all`) and a variant (`java-composition`, `java-inheritance`, `rust`, or
`all`). For example, check e1 in Java composition after editing the starter:

```sh
bash case-studies/orders-payments/track/compose.sh starter e1 java-composition
```

After completing the starter, run all exercises in all three realizations:

```sh
bash case-studies/orders-payments/track/compose.sh starter all all
```

To compare the completed implementation across the full matrix, run:

```sh
bash case-studies/orders-payments/track/compose.sh solution all all
```

Each accepted invocation builds a new image from the current local source,
compiles the selected `starter` or `solution` source set, and runs the selected
exercise and realization inside one fresh container. The container has no
bind mount and cannot modify the host checkout. The host wrapper writes run
evidence under `artifacts/roo-track/`. Edit only the starter policy files:
[Java](java/starter/roo/payments/LearnerPolicy.java) and
[Rust](rust/starter/src/learner.rs). The solution files provide the completed
comparison.

## Evidence and cleanup

Every accepted invocation writes to a new directory under
`artifacts/roo-track/<unique-run-id>/` and prints that path at the end. It
records the host command and Docker version output, any build log and build
status, and the wrapper exit status. Container run logs and selected exit
statuses are recorded when available. After a container starts, it also
records image and container identifiers, tool versions, installed OS
packages, source identity, test status, and collection status. Selected track,
PostgreSQL, and HTTP receipts and logs are copied out when checks pass or fail;
image-build failures retain the host build diagnostics and exit status.

The wrapper exports this allowlisted evidence before removing only the
container it created. It does not export the PostgreSQL data directory or
environment credentials. Docker may keep the built image and build cache for
later runs; the wrapper does not prune unrelated or shared Docker resources.
Use this wrapper for local runs: invoking the Compose service directly runs the
container entry point but does not perform the wrapper's host-side evidence
export.

The wrapper also records a restricted container inspection and image platform.
It verifies the configured nonroot user, disabled external networking, absent
mounts and port bindings, dropped capabilities, and no-new-privileges before
waiting for test completion. This evidence omits container environment values.

## GitHub Actions

The [ROO adoption track workflow](../../../.github/workflows/roo-track.yml)
runs on matching pushes and pull requests, and can also be started manually
with `workflow_dispatch`. It uses `ubuntu-24.04`, invokes the same command as
the local full qualification, grants only `contents: read`, disables checkout
credential persistence, pins each action to a commit SHA, and uses no secrets.
It always attempts to upload `artifacts/roo-track/`, including after a failed
qualification; uploaded artifacts are kept for 14 days.

Before qualification, the workflow verifies a GitHub-hosted Linux X64 runner,
an x86_64 host, an AMD64 Docker engine, and checkout correspondence with the
event commit. It records those allowlisted values, the run and attempt, Git
tree, and SHA-256 hashes of the checked-out files in `hosted/provenance.json`
within the uploaded artifact. The test step requires a Linux AMD64 image.
Together with the container inspection and existing evaluator receipts, these
records bind a hosted qualification to its actual architecture, source, and
isolation boundary.

The workflow definition alone does not establish a hosted run result. Check an
actual GitHub Actions job and its uploaded evidence before reporting CI
qualification. Local and hosted runs are separate evidence: a successful
Linux ARM64 run does not prove an AMD64 CI execution. The pinned image indexes
support both architectures, and Docker selects for the local daemon because
the Compose service does not force a platform.

## Reading failures and results

In full `qualify` mode, the starter's specified `BEHAVIOR eN:` failures are
expected only for untouched starter code. In a `starter` learner mode, a
`BEHAVIOR eN:` failure means the selected learner behavior did not pass.
Compiler, dependency download, PostgreSQL startup, HTTP startup, and missing
lock-witness failures are environment or infrastructure failures; they are not
expected starter RED results. The wrapper prints the evidence directory and
preserves a nonzero status so the corresponding logs and receipts can be
inspected.

Passing these checks demonstrates the bounded scenarios exercised by this
track, including selected concurrency, process-death recovery, immediate
PostgreSQL restart/WAL redo, and HTTP response loss. It does not establish
hardware power-loss behavior, arbitrary provider or network behavior, every
interleaving, or production readiness. See the [track contract](SPEC.md) for
the scope and limits of those checks.
