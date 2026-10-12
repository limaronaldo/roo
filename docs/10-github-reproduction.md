# GitHub publication and hosted AMD64 reproduction

ROO is published at [limaronaldo/roo](https://github.com/limaronaldo/roo).
The method remains independent of language: one relationship and failure
contract is realized through Java composition, Java Template Method, and Rust
composition. The shared adoption evaluator checks equivalent behavior in all
three implementations.

## Reproduce locally

```sh
git clone https://github.com/limaronaldo/roo.git
cd roo
bash case-studies/orders-payments/track/compose.sh
```

Docker, its Compose plugin, Bash, and common POSIX utilities are the host
requirements. The image build retrieves the pinned dependencies; runtime
qualification uses no external network. PostgreSQL runs inside the disposable
nonroot test container and uses loopback only. No host database installation,
published database port, host data mount, or persistent database volume is
required. See the [Docker guide](../case-studies/orders-payments/track/DOCKER.md)
for individual starter/solution exercise commands and package pin limits.

## Execute on GitHub

The [workflow](../.github/workflows/roo-track.yml) starts automatically on
matching pushes and pull requests. It can also be dispatched from the Actions
tab or the authenticated GitHub CLI:

```sh
gh workflow run roo-track.yml --repo limaronaldo/roo --ref main
```

Use one matching run for a given commit; an automatically started push run is
already an actual workflow execution. The job uses `ubuntu-24.04` and verifies
the GitHub-hosted environment, Linux X64 runner, x86_64 host, AMD64 Docker
engine, and checkout SHA before building. The qualification step requires a
Linux AMD64 image and calls the same wrapper as the local command.

The wrapper inspects the actual container and enforces UID 10001:10001,
network mode `none`, no mounts or port bindings, dropped capabilities, and
no-new-privileges. The evaluator owns PostgreSQL start, stop, immediate
restart, and WAL recovery inside that container. A separate external
PostgreSQL service would not satisfy this test lifecycle.

## Inspect the evidence

The workflow uploads `roo-track-<run-id>-<attempt>` even when qualification
fails. Select the exact run and attempt; uploaded artifacts expire after
14 days. Download with:

```sh
gh run download RUN_ID --repo limaronaldo/roo --name roo-track-RUN_ID-ATTEMPT --dir artifacts/hosted-run
```

`hosted/provenance.json` records the event, commit, tree, runner architecture,
Docker architecture, and SHA-256 hashes of the checked-out files. The separate
run directory contains the actual image platform, restricted container
inspection, source identity, tool/package versions, test receipts, logs, and
exit statuses. Compare baked source hashes with the selected commit, not a
later checkout. Environment credentials and PostgreSQL data files are not
exported.

For an untouched checkout, a passing full qualification includes:

- 18 starter groups reported RED, with overall `EXPECTED_INCOMPLETE`.
- 18 solution groups reported PASS: six exercises in each of three variants.
- Three e6-only PASS groups while e2 remains incomplete.
- Shared policy/input checks, witnessed PostgreSQL concurrency, process-death
  recovery, immediate restart/WAL redo, and HTTP response-loss recovery.
- Successful isolation check, test, collection, export, cleanup, and wrapper
  statuses.

Edited starters should use the learner commands rather than the full
untouched-starter qualification. A green job alone is insufficient: reconcile
the receipts and source identity in its exact artifact.

## Publication validation

The initial published executable commit is
[`0c3e2bb1bae85a2dcd6ed0ad0d98a06af27048a5`](https://github.com/limaronaldo/roo/commit/0c3e2bb1bae85a2dcd6ed0ad0d98a06af27048a5).
Its actual hosted execution is
[run 38176774573, attempt 1](https://github.com/limaronaldo/roo/actions/runs/38176774573).
The job and its artifact reconciliation passed on the actual hosted AMD64
runner. All 18 solution groups and three independent e6 groups passed; the
untouched starter produced its 18 expected RED groups. The receipts include
15 solution lock witnesses, three Pending scopes retained through immediate
PostgreSQL restart/WAL redo, and six HTTP response-loss recoveries. The e6-only
check adds six lock witnesses and six response-loss recoveries while e2 remains
incomplete. All eight recorded exit statuses, including the isolation check,
were zero.

The artifact archive's SHA-256 matched the GitHub API digest. Its 242 checkout
hashes, 117 baked case-study hashes, and 19 evaluator/learner hashes per receipt
matched the tested commit. The running container inspection confirmed the
documented nonroot/network/mount/port/capability boundary. The retained cleanup
status and named-container removal log confirm scoped cleanup.

See the [hosted run metadata](../research/roo-github-hosted-run.json),
[self-contained receipts and evidence](../research/roo-github-hosted-evidence.json),
and [independent publication review](../research/roo-github-publication-review.md).
The publication update immediately following that initial run changed only
documentation and evidence. This historical receipt validates the linked
commit, not later development. For current code, select the exact PR or main
commit's workflow run and reconcile its artifact using the procedure above;
workflow, case-study, and dependency changes require their own evidence.

The scenarios are educational, bounded checks of concurrency and recovery.
They do not establish every interleaving, physical power-loss behavior,
external payment-provider behavior, or production readiness. Historical
local/emulated runs remain separate evidence from this hosted execution.
