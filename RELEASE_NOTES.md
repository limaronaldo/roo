# ROO v0.4.3

**First human validation round preparation (preview).** ROO — Relationship &
Ownership Oriented design — now supplies a coordination plan, unsent English
invitations, and a consolidation form for the published validation kit.
The round is prepared, not started: no invitations, accepted participants,
human reviews, or practitioner results are established by this release.

## What changed

- Add the [first-round plan](docs/validation/first-round.md), with frozen sources,
  Rust and DDD review roles, a practitioner exercise, and a staged sequence.
- Supply [unsent invitation drafts](docs/validation/invitations.md) for Rust
  and DDD/architecture reviewers. The maintainer chooses recipients, agrees
  privately on scope and dates, and sends invitations separately.
- Add a [round summary form](templates/validation-round-summary.md) that preserves
  first attempts, assistance, role overlap, dissent, missing evidence, and
  separate first-attempt and later assessments.
- Explain consolidation without score averaging or majority votes. Keep
  incomplete work distinct from a negative result, and paper predictions
  distinct from executed implementation checks.
- Link the pack from the overview, validation kit, contributor guidance, and
  edition navigation. Keep recruitment, originals, and consent private;
  publish only an approved synthetic summary through a separate contribution.

## Why a patch release

This is a compatible documentation addition. The eight-field contract,
canonical six-step procedure, Java/Rust APIs, operation permissions,
PostgreSQL schemas, idempotency, and restart recovery are unchanged.
No migration from v0.4.2 is required. The method remains independent of
language, runtime, database, and protocol; the reference implementations
remain bounded laboratories. See the [release policy](RELEASING.md).

## Use the prepared round

Start with the [coordination plan](docs/validation/first-round.md) and preserve
three separate source identities before inviting anyone:

- Method/code: v0.4.1, `f6670a109d7dbfef8f72078b4cd361079ac6a10a`.
- Kit, exercise, criteria, and individual results form: v0.4.2,
  `9a149882a3bb2e65cbfa7f569420ba2fc40ae2d4`.
- Coordination plan and round summary form: record the exact accepted v0.4.3
  commit, or another explicitly agreed revision, before sending invitations.

Do not replace those pins with a moving Development URL during the round.
Save independent reviews and the practitioner's first attempt before feedback;
perform the second-reader cross-check before showing the facilitator key.
Record assistance, prior exposure, overlaps, and work not performed. Human
participation and approval of the exact public summary are separate decisions.
The exercise needs no code or toolchain.

Read the [v0.4.3 documentation](https://limaronaldo.github.io/roo/v0.4.3/).
The automatic publisher selects v0.4.3 as the highest numeric release tag;
the selector retains v0.1.0–v0.4.2 and Development. Earlier edition sources,
navigation, tags, and historical records remain preserved.

## Reproduce the reference laboratories

With Docker, Compose, Bash, and common POSIX utilities:

```sh
git clone --branch v0.4.3 https://github.com/limaronaldo/roo.git
cd roo
bash case-studies/orders-payments/track/compose.sh
```

The shared qualification compares Java composition, Java Template Method, and
Rust composition with isolated PostgreSQL. It exercises concurrency,
idempotency, operation permissions, revocation, restart recovery, outbox
delivery, and lost responses. Shipped starters remain intentionally incomplete.
See the [Docker guide](case-studies/orders-payments/track/DOCKER.md) and
[contribution checks](CONTRIBUTING.md#validate-the-affected-behavior).

The GitHub Release identifies the exact qualified source and hosted Linux
AMD64 runs. Qualification and publication summaries, allowlisted workflow
evidence, and `SHA256SUMS` retain checked receipts beyond hosted artifact
retention. Automatic documentation dispatch, Pages deployment, the selector,
and public source manifests are verified separately.

## License and evidence limits

Original material remains **MIT OR Apache-2.0**, with
[third-party exceptions](THIRD_PARTY_NOTICES.md). Documentation is in English.
This is a GitHub source release; Rust packages remain `publish = false`.

Automated checks and AI review do not complete the human round. This release
does not establish novelty, superiority, a field study, production readiness,
real authentication, alternative-backend qualification, exhaustive
interleavings, or physical power-loss durability. See
[Claims and limits](docs/claims-and-limits.md) and the [changelog](CHANGELOG.md).
