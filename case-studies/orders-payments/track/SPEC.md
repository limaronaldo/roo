# Executable ROO adoption track contract

ROO means Relationship & Ownership Oriented design. This track implements
caller recovery decisions around the unchanged orders/payments applications.
Students edit a policy, not the existing domain or transaction implementation.
The same observations and obligations apply to Java composition, Java Template
Method, and Rust composition. All amounts are signed 64-bit USD minor units.

## Policy process protocol

Build separate starter and solution executables. Each accepts `policy` followed
by exactly these eleven arguments, in order:

`exercise phase state total payment_id last_result pending_outbox requested_payment_id unit quantity lookup`

The caller supplies observations and requested input, never expected results.
Return exactly one LF-terminated action on stdout, exit zero, with no logging
on stdout. Permitted actions are the existing `add:UNIT:QUANTITY`,
`pay:ID:approve:none`, `reconcile:LOOKUP:none`, `relay:ok`, plus caller decisions
`inspect` and `stop`. The evaluator validates actions before executing them,
obtains snapshots independently, and observes again after each action.
It never executes shell text or accepts learner-provided state as evidence.

Reject malformed input before policy evaluation: wrong arity, unknown exercise
or phase, invalid state/outcome, invalid identity, invalid integer, negative
total/pending count, or invalid lookup. Exit 2, no stdout, generic English
diagnostic. Payment identities are ASCII `[A-Za-z0-9]{1,64}` or `-` for absence,
matching the bounded in-memory domain. PostgreSQL scope names are separate.
Integers use optional ASCII minus plus one or more ASCII digits, within i64;
no plus sign, whitespace, decimal, Unicode digit, or overflow. States are
Draft, Pending, Paid, Declined, Refunding, Refunded. Outcomes are `-` or the
existing base Domain.Result/Outcome names. Lookup is `ok` or `unavailable`.
Validate the entire input even when an exercise does not use every field.

| Exercise | Allowed phase | Completed next action |
|---|---|---|
| e1 | add | `add:unit:quantity`, including invalid domain inputs; domain rejection must be observed, not filtered away. |
| e2 | recover | Pending with a persisted payment ID: `reconcile:lookup:none`; otherwise `inspect`. |
| e3 | retry | `pay:requested_payment_id:approve:none`; absent requested ID: `inspect`. Use the caller's identity so a changed identity is rejected by the domain. |
| e4 | redeliver | Positive pending count: `relay:ok`; zero: `stop`. |
| e5 | uncertain_commit, recover | uncertain_commit: `inspect`; recover Pending with a persisted payment ID: `reconcile:lookup:none`; otherwise `inspect`. |
| e6 | payment_response_lost, line_response_lost, line_inspected | payment loss: retry `pay` using persisted ID, or requested ID if no intent exists; if neither exists, `inspect`. Line loss: `inspect`. After inspection: `stop`; a separate explicit caller decision may append again. |

The starter compiles and returns `stop` at each of the six exercise gaps.
Implement each decision separately. Do not hardcode p1, 250, expected snapshots,
or exercise pass flags. Native tests and common policy cases use varied inputs.
The full solution is a distinct source implementation, not a runtime answer mode.

## Native exercises e1–e4

Each executable also accepts `native EXERCISE VARIANT`. Java VARIANT is
`composition` or `inheritance`; Rust VARIANT is `composition`. Test one exercise
independently. A missing/wrong learner decision fails exit 1 with stderr prefix
`BEHAVIOR eN:`. Infrastructure/argument errors are not behavioral failures.
Successful checks print an English PASS line and exit zero. Do not catch all
exceptions/panics as successful starter failures.

- e1: seed two valid lines totaling 250. Use the learner action for invalid
  quantity, invalid price, multiplication overflow, and sum overflow. Check
  exact preserved order/line facts, total, Draft, no effect/event after each.
  Also vary valid input and verify the requested addition actually occurs.
- e2: seed 250, pay using p1 with an approved provider and failed terminal
  commit. Assert LocalCommitFailed, Pending, p1, one charge, zero events before
  consulting the learner. Execute recovery and assert Paid, same p1, one
  charge, exactly one PaymentApproved event with ID payment:p1. Repeat with
  a different ID and amount. An unavailable lookup must preserve Pending.
- e3: after timeout-after approval, execute same-ID retry from the learner;
  verify one effect and finalization. Exercise a changed caller ID while
  Pending and expect IntentConflict with unchanged intent/effect. Invoke the
  existing fixture's test-only conflict action to verify KeyConflict for a
  changed amount; do not widen private provider APIs.
- e4: approve a payment, relay with acknowledgement failure, and assert one
  consumer fact, one event still pending. Execute learner redelivery and
  assert one applied fact, no pending event; zero pending selects stop.
  Check delivery identity/content through the public observers available in
  each language; Rust's common guarantee is ID deduplication.

## PostgreSQL exercise e5

Reuse the existing marked loopback-only cluster, schema, protected persistent
runners, and PostgreSQL barrier helpers. Never reset/drop existing test data.
Use fresh random synthetic scopes. Require a stopped cluster at entry before
assuming lifecycle ownership; refuse an already running cluster so another
test's database is never restarted or stopped. Start/apply schema; always
terminate owned workers/servers and stop only this marked cluster on exit.

For each Java realization and Rust:

1. Witness pay-before-add row locking and the contender's wait. Release the
   barrier, assert Approved/InvalidState and a single 250-minor charge/event.
2. Kill a pay process at the observed after_effect gate. A fresh process must
   read Pending, persisted p1, one charge, zero events. Keep the snapshot.
3. The learner's uncertain_commit decision must select inspection, not replay.
   This checks recovery policy; an actually uncertain COMMIT is not injected.
4. Immediately stop/restart PostgreSQL once for all three retained scopes.
   Verify a changed server start time, WAL redo, and byte-equivalent normalized
   snapshots after restart. Invoke learner recovery using the fresh observed
   Pending snapshot; assert Paid, same identity, one charge, one event.

Known SIGKILL windows and immediate server recovery are bounded observations,
not hardware power-loss, arbitrary network failure, or exhaustive interleaving
proof. Provider and inbox transactions remain independent but share one server.

## HTTP exercise e6

Use the actual existing Java/Rust servers and retained PostgreSQL. For each
variant, gate after action and snapshot but before response headers, kill the
server, and require the client's connection-loss exception. Recover through a
fresh server and GET. Invoke learner decisions on those observations:

- Lost payment response: Paid, one charge/event; same-ID replay must return
  AlreadyApplied and preserve effects and identity. Include a separate Pending
  timeout-after case: HTTP 202 starts no worker; explicitly reconcile.
- Lost line response: inspect the committed Draft total 300, then select stop.
  Assert the policy transcript sent no automatic line POST and total stayed
  300. An explicitly authorized second caller action adds 50 to reach 350,
  demonstrating that line POST has no durable replay receipt.

Reject wrong boundary policies (new payment ID, blind line replay, skipped
reconciliation) with specific action or state assertions. Do not classify a
missing dependency, compilation failure, database error, server startup failure,
or missing lock witness as expected learner failure.

## Qualification and evidence

The root evaluator owns common policy cases/oracles and integrated checks.
Compile both starters successfully; require specific independent behavioral
failures for all six groups in all three realizations. Require solved native
e1–e4, policy parity including malformed input, PostgreSQL e5, and HTTP e6 to
pass. Build/compiler/format checks and runtime evidence are separate.

Record current run evidence under this track's runtime directory or new
research files. Do not overwrite existing historical validation receipts.
Keep source, fixtures, dependencies, identifiers, schemas, original templates,
and previous research records unchanged. Navigation and new ignore entries
are permitted. Document progressive commands, student edit locations,
comparison with solutions, architecture translation, and evidence limits in
English. No publication is part of this track.
