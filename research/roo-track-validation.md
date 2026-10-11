# Executable ROO adoption track qualification

Date: 2026-10-11. Scope: the separate orders/payments adoption track, with
unchanged base, PostgreSQL, and HTTP applications. All amounts are USD minor
units. These are current local execution results, distinct from the preserved
historical case-study receipts.

Root ran `bash case-studies/orders-payments/track/verify.sh` successfully.
Both starter and solution sources compiled. The untouched starter produced
18 specific behavioral RED groups: six exercises in each of Java composition,
Java Template Method, and Rust composition. Infrastructure errors were not
accepted as expected learner failures.

| Completed solution | Shared policy cases | Malformed inputs rejected | Native intermediate-state groups | PostgreSQL e5 | HTTP e6 |
|---|---|---|---|---|---|
| Java composition | 31 | 23 | 4 | PASS | PASS |
| Java Template Method | 31 | 23 | 4 | PASS | PASS |
| Rust composition | 31 | 23 | 4 | PASS | PASS |

The six exercise groups passed for all three solutions. A separate regression
compiled temporary starters with only e6 completed, verified that e2 still
returned `stop`, and passed actual e6 HTTP recovery in all three variants.
Every learner observation in those HTTP transcripts belonged to e6. The
supplementary HTTP 202 demonstration uses an explicitly recorded harness/caller
reconciliation action, with no prerequisite on another exercise's policy.

Native scenarios use
the same line inputs, recovery identities/amounts, changed identity/fingerprint,
and acknowledgement-loss obligations. Java checks actual line records; Rust
compares cloned orders, retaining encapsulation of private line storage.

## Observed boundaries

- Fifteen database lock witnesses: pay/add coordination, process after-effect
  gates, and HTTP after-snapshot gates. Waiting is observed in PostgreSQL,
  rather than inferred from elapsed time.
- Three pay processes killed with SIGKILL after provider approval committed.
  Fresh runner processes observed Pending, one charge, no event, and the same
  intent identity.
- One immediate PostgreSQL restart preserved all three Pending snapshots.
  The server start time changed and server logs showed WAL redo. Recovery
  finalized each existing intent with one charge and one terminal event.
- Six HTTP response losses before headers, observed as client exceptions:
  payment and line addition for each implementation. Fresh servers read the
  committed state. Same-ID payment replay preserved the effect; line recovery
  selected inspection and stop before a separate deliberate caller append.
- Explicit reconciliation after HTTP 202; new-key conflict and injected wrong
  policy actions were rejected. All owned HTTP processes ended, and root
  independently confirmed the marked PostgreSQL cluster stopped afterward.

Java compilation used release 21 with warnings denied. Both new Rust crates
passed formatting, offline build, and Clippy with warnings denied. The first
Clippy attempt identified two helper-style issues; both were corrected and
rechecked without suppressing the warnings. Existing Java PostgreSQL pure and
compiler-negative checks and HTTP protocol checks also ran during the serial
build. Their older research receipts were not overwritten.

## Evidence and limits

The [starter receipt](roo-track-starter-evidence.json) and
[solution receipt](roo-track-solution-evidence.json) retain cases, source
hashes, action transcripts, normalized snapshots, gates, negative controls,
and restart evidence. The [exercise independence receipt](roo-track-independence-evidence.json)
records temporary policy hashes, incomplete e2 probes, and real e6 outcomes.
[Command qualification](roo-track-qualification.json)
retains successful checks and the initial Clippy failure. The
[static validation](roo-track-validation.json) records protected-file, local
link, original-fence, and runtime-source identity checks. The
[run ledger](roo-track-run.md) describes task ownership and available AI usage.

The policy receives facts and chooses actions; the completed applications own
domain transitions and effect/transaction ordering. Compiler acceptance alone
does not establish those runtime properties. An actually uncertain COMMIT is
not injected: its inspection policy is checked separately from the witnessed
SIGKILL window. Provider and inbox transactions share one local PostgreSQL/WAL
domain. The checks do not establish external-provider behavior, hardware
power-loss survival, authenticated tenant isolation, production capacity, or
all interleavings. Java/Rust parity applies to this bounded exercise contract.

Starter and solution are separate source implementations. Rebuild after
editing a starter. The full `verify.sh` entry point intentionally qualifies an
untouched starter's failures; use normal `verify.py --source starter` for
completed learner work, as explained in the [track guide](../case-studies/orders-payments/track/README.md).
