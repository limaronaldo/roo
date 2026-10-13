# ROO executable learning track

ROO means **Relationship & Ownership Oriented design**. Start with an operation
and the invariant it must preserve, make the relationship decisions, and then
choose how Java, Rust, a database, or a protocol will enforce them. This track
turns that method into six small caller policy exercises around the existing
orders and payments case.

The learner edits recovery decisions. The existing domain, application,
database, and HTTP adapters still validate and execute those decisions. The
policy cannot set state, report an expected snapshot, or run shell text. The
evaluator applies an allowed action and reads state independently.

Start with the [track contract](SPEC.md) and the [original case walkthrough](../README.md).
The [ROO adoption guide](../../../docs/09-adoption-guide.md) explains how to
apply this method to an existing project. Its [filled relationship contract](../adoption/relationship-contract.md),
[architecture decision](../adoption/architecture-decision.md), and [design review](../adoption/design-review.md)
show the full payment recovery decision. Blank worksheets are in
[`templates/`](../../../templates/).

## A first neutral trace

Consider a fresh order with two valid lines totaling 250 USD minor units
($2.50). Payment `p1` is prepared and persisted as Pending. The provider
approves once, but local finalization fails. A caller now observes Pending and
the persisted identity `p1`; the provider effect is independent of that local
snapshot.

| Step | What happens |
|---|---|
| Observation | Pending, payment ID `p1`, lookup `ok` |
| Policy decision | `reconcile:ok:none` |
| Effect owner | The existing application and adapters perform reconciliation; the learner policy does not mutate an order or provider |
| Independent observation | The evaluator reads the resulting state, event, and charge count |

The caller never supplies the expected result. In particular, the fixture's
`case_id` and expected oracle column are not policy inputs. `last_result` is an
observation from the preceding action, not a test answer or proof that an
independent effect did or did not occur.

## Work through the track

For an isolated Docker Compose run and the matching GitHub Actions workflow,
see the [Docker and CI guide](DOCKER.md).

Run commands from the repository root. First compile the track and its existing
Java and Rust PostgreSQL and HTTP targets:

```sh
bash case-studies/orders-payments/track/build.sh
```

For a first look, qualify one unmodified starter exercise. The starter compiles
and returns `stop` at every exercise gap, so the expected learner failure is a
behavioral red for `e1`:

```sh
python3 case-studies/orders-payments/track/verify.py --source starter --exercise e1 --variant java-composition --expect-incomplete
```

`--expect-incomplete` is for starter qualification only. It recognizes the
specified missing learner behavior; it does not turn compiler, dependency,
database, server startup, or missing barrier errors into a pass. After editing
the starter, rebuild it before verifying it. Otherwise `verify.py` would run
the previously compiled policy:

```sh
bash case-studies/orders-payments/track/build.sh starter
python3 case-studies/orders-payments/track/verify.py --source starter --exercise e1 --variant java-composition
```

Repeat an individual exercise with `--variant java-inheritance` or
`--variant rust`. Java exercises run against both composition and Template
Method applications; Rust uses composition. After solving the exercises, run
each rebuilt source matrix separately:

```sh
bash case-studies/orders-payments/track/build.sh starter
python3 case-studies/orders-payments/track/verify.py --source starter --exercise all --variant all
bash case-studies/orders-payments/track/build.sh solution
python3 case-studies/orders-payments/track/verify.py --source solution --exercise all --variant all
```

The repository qualification entry point is for the untouched starter. It
builds first, requires every starter group to show its expected behavioral
failure, then checks all completed solution groups. It also compiles temporary
learners with only e6 completed and verifies real HTTP recovery while e2 still
returns `stop`; your starter files are not edited:

```sh
bash case-studies/orders-payments/track/verify.sh
```

After solving any starter group, this entry point is no longer the right check:
it deliberately expects those starter failures. Use `build.sh starter` and
`verify.py --source starter` to check your work, then build and check the
solution source separately. Exercises `e1` to `e4` use the in-memory adapters
and need no database at runtime. The build still compiles the configured
PostgreSQL and HTTP targets. Exercises `e5` and `e6` use the existing marked
loopback PostgreSQL cluster and real local HTTP servers.

The build runs targets serially. It needs Python 3, Bash, JDK 21 or newer,
Rust/Cargo 1.96, and PostgreSQL 18 server tools for the integrated boundary
checks. It verifies the pinned JDBC and Jackson jars through the existing
fetch helpers, and the Rust boundary builds run offline. If the dependency
cache is cold, prime the pinned Java artifacts and locked Rust dependencies
first:

```sh
python3 case-studies/orders-payments/postgres/fetch_jdbc.py
python3 case-studies/orders-payments/http/fetch_json.py
cargo fetch --locked --manifest-path case-studies/orders-payments/postgres/rust/Cargo.toml
cargo fetch --locked --manifest-path case-studies/orders-payments/http/rust/Cargo.toml
```

The Java helpers reuse an existing verified jar and fetch a missing one. Cargo
fetch may use the network to fill a cold cache; the later boundary builds use
the exact locked dependency graphs offline. The local PostgreSQL checks also
need the case's documented server tools and supported runtime versions.

The integrated database checks require that marked cluster to be stopped when
they begin. The runner refuses an already running cluster, starts its own
marked cluster, applies the schema, and stops only that cluster at normal
cleanup. It retains its test data. Do not treat a refusal or missing lock
witness as an exercise failure; those are environment or harness failures to
resolve before judging the policy.

## The policy boundary

Each policy process receives `policy` followed by exactly eleven fields, in
this order:

| Field | Meaning |
|---|---|
| `exercise` | `e1` through `e6` |
| `phase` | The permitted point in the exercise |
| `state` | Latest observed order state |
| `total` | Latest observed non-negative signed 64 bit USD minor units |
| `payment_id` | Persisted payment identity or `-` |
| `last_result` | Result of the preceding action or `-` |
| `pending_outbox` | Latest observed number of unacknowledged events |
| `requested_payment_id` | Caller supplied payment identity or `-` |
| `unit` | Caller supplied line price in minor units |
| `quantity` | Caller supplied line quantity |
| `lookup` | `ok` or `unavailable` |

All fields are validated, including fields a particular decision does not use.
Payment IDs must match `[A-Za-z0-9]{1,64}` or be `-` for absence. Integers use
ASCII digits with an optional leading `-` and must fit signed 64 bit; `+`,
whitespace, decimals, and Unicode digits are rejected. Leading zeroes and
`-0` are accepted and normalized (`0007` becomes `7`, `-0` becomes `0`)
before the policy runs. `total` and `pending_outbox` must be non-negative.
States are `Draft`, `Pending`, `Paid`, `Declined`, `Refunding`, and `Refunded`;
`last_result` is `-` or one of `Added`, `InvalidLine`, `Overflow`,
`InvalidOrder`, `InvalidState`, `IntentConflict`, `Approved`, `Declined`,
`Unknown`, `NotFound`, `AlreadyApplied`, `AlreadyDeclined`,
`LocalPrepareFailed`, `LocalCommitFailed`, `KeyConflict`, `RelayOk`,
`RelaySendFailed`, and `RelayAckFailed`. The [track contract](SPEC.md) lists
the complete accepted values and exercise phases.
The policy returns one LF terminated action and writes no other text to stdout.
The available actions are `add:UNIT:QUANTITY`,
`pay:ID:approve:none`, `reconcile:LOOKUP:none`, `relay:ok`, `inspect`, and
`stop`. It must not hardcode the example ID `p1`, the example total `250`, or
an expected snapshot. For e1, forward the caller's line values even when they
are invalid: domain validation owns rejection and preservation of prior lines.

The policy owns **which next action to request**. Existing domain transitions,
application ordering, and adapters own **whether that action preserves their
invariants**. PostgreSQL owns committed rows and transaction boundaries; the
HTTP handler owns transport validation and response behavior. No language type
can replace those runtime contracts.

The process boundary is visible in [Java's `TrackInput`](java/common/roo/payments/TrackInput.java)
and the [Rust shared runner](rust/shared.rs); native checks that exercise the
existing in-memory applications live in [Java's `TrackNative`](java/common/roo/payments/TrackNative.java)
and the same Rust runner.

## Keep the eight fields neutral

Before thinking about Java or Rust syntax, answer the eight Relationship
Contract fields for the operation. The filled contract linked above gives the
case answers; use the blank worksheet when applying ROO elsewhere.

Use the [canonical field questions](../../../docs/02-relationship-design.md#21-the-eight-field-relationship-contract)
rather than a separate track-specific definition.

For this case, `p1` is the stable payment operation identity, while the order,
provider effect, and outbox fact have different custodians and lifetimes. The
same neutral decision can be expressed with different language mechanisms.

## Read the implementation differences

The [Java composition implementation](../java/src/roo/payments/CompositionApplication.java)
injects store and provider capabilities. The [Java Template Method implementation](../java/src/roo/payments/TemplateApplication.java)
is a real reuse option: its final public workflows keep the orchestration
fixed while subclasses supply stable store and provider hooks. It is useful
when those are the intended variation points and each hook implementation
honors the same contract. Both delegate domain checks and state installation to
the [Java domain](../java/src/roo/payments/Domain.java) and
[adapters](../java/src/roo/payments/Adapters.java).

Rust uses composed adapters and an application that holds exclusive mutable
borrows while it coordinates them. Those borrows constrain local aliasing and
access lifetime. They do not decide whether a provider effect happened, make
separate commits atomic, or define caller authorization. See the [Rust application](../rust/src/application.rs)
and [adapter implementation](../rust/src/adapters.rs). Compare the bounded
implementations in [`java/`](java/) and [`rust/`](rust/); the exercises point
directly to the starter and completed policy files.

## What each result can establish

Compilation establishes that the selected source builds. A starter behavioral
red establishes that its decision is still missing. Passing a selected
exercise establishes only the checked behavior in that scenario and variant.
Matching Java and Rust outcomes demonstrates parity for this bounded policy
contract, not universal equivalence between the languages or implementations.

The PostgreSQL exercise uses the existing application and actual local database
transactions. It witnesses selected concurrency, kills a process after the
provider effect commits, inspects the surviving Pending intent, then performs
an immediate PostgreSQL restart and checks WAL redo and normalized snapshots.
That is bounded evidence for this marked local database and its durability
settings, not hardware power loss or a production payment provider. The
[PostgreSQL contract](../postgres/SPEC.md), [Java store](../postgres/java/src/roo/postgres/Store.java),
and [Rust database adapter](../postgres/rust/src/database.rs) show those
transaction and row lock boundaries.

Each `verify.py` run writes its current receipt to the ignored
`.runtime/last-run.json`; `verify.sh` also keeps separate starter and solution
receipts there, plus `.runtime/e6-independent-last-run.json` for the temporary
learner regression. These run artifacts and a successful source build are not a
substitute for a qualification record. This guide records the workflow and
evidence limits; it does not claim a fresh runtime pass.

The separate [2026-10-11 qualification record](../../../research/roo-track-validation.md)
reports the executed starter and solution matrix, observed database restart,
HTTP response losses, cleanup, and proof limits.

The HTTP exercise loses the response after the action and snapshot but before
headers reach the client. Recovery uses a fresh server and the existing
database. A payment retry keeps the same identity; a lost line response requires
inspection because line POST has no durable replay receipt. These checks do not
prove arbitrary network behavior, every interleaving, or production readiness.
The [HTTP contract](../http/SPEC.md), [Java service](../http/java/src/roo/postgres/HttpService.java),
[Java protocol](../http/java/src/roo/postgres/HttpProtocol.java), and [Rust server](../http/rust/src/main.rs)
make the response boundary explicit; the [Rust protocol](../http/rust/src/lib.rs)
defines request and status handling.

Read [EXERCISES.md](EXERCISES.md) for the six tasks and their recovery hints.
