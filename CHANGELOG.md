# Changelog

This file records changes to public ROO releases. Versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html); the repository
release version is declared in the root `Cargo.toml` and tagged as `vX.Y.Z`.
Version 0.x is an evolving educational method and laboratory, with the
compatibility policy in [RELEASING.md](RELEASING.md).

## [Unreleased]

Apply the sustained findings of the 2026-10-12 repository review, which had been
written and locally qualified but never committed, against a branch 20 commits
behind `main`. Each finding was re-audited against `main` before any change:
some were already fixed there, and some targeted content that never reached it.
The full per-finding account, including the findings that correctly received no
fix and the limits of what this establishes, is in
[the port report](research/repo-review-2026-10-12-port-2026-10-13.md).

### Fixed

- Stop external code from mutating the in-memory Java store. The concrete store
  is package-private, so an order can no longer be driven back to `Draft` with a
  forged refund event from outside the package. A third negative-compilation
  sample pins the boundary.
- Reject a declined refund before any write, in the Java in-memory pair and the
  Rust PostgreSQL adapter. Both previously installed an intermediate state and
  only then failed, leaving the order wedged in `Refunding`.
- Distinguish an oversized HTTP body from a framing or truncation fault in the
  Rust server. Every body-read error was previously reported as `413`.
- Reject request targets carrying a URL fragment in the Rust HTTP server, which
  the Java server already rejected. Bound the Java server's body readers and
  their deadline, so stalled clients can no longer starve the listener.
- Detect a conflicting fact delivered under an already-seen `EventId` in the
  Rust in-memory consumer, matching the Java and PostgreSQL consumers. It
  previously deduplicated on identity alone and silently dropped the conflict.
- Return a fixture error instead of panicking on an empty scenario name, in both
  the Rust example and its Java counterpart.
- Measure the track boundary controls against the real runner and server. They
  previously compared two fixed strings and could never fail.
- Read the container exit status from the host rather than from a file the
  container can overwrite, so a run's status cannot be forged.
- Resolve the real path in the track verifier, which failed whenever the
  repository path contained a symlink.
- Remove the author's absolute home-directory path from seven tracked evidence
  files in this public repository, preserving every recorded hash.

### Added

- Run the base, PostgreSQL, HTTP and regression verifiers in CI. None of them
  had ever run hosted, so the shared oracle, the Java unit tests and the
  negative compilation controls were qualified only locally. Each phase writes
  its receipt to its own path, so a hosted run never replaces a dated one.
- Declare CPU, memory and PID limits for the track container. There is
  deliberately no disk limit, because the writable layer has no portable quota.
- Accept `--evidence-output` and `ROO_EVIDENCE_PATH` in the PostgreSQL and HTTP
  verifiers, validated before the long run starts.
- Fail the build when a tracked file carries an authoring machine's absolute
  home directory, an assistant transcript path, or a session identifier.
  Recorded hashes are untouched, since those are the integrity anchors.

### Changed

- Widen the documentation and example guards, which were silently skipping most
  of what they appeared to check, and refuse site links pinned to bytes that
  differ from the committed object.
- Date the evidence records that could not be reproduced from git, rather than
  editing the historical manifests or restating unsupported claims.

## [0.4.3] — 2026-10-12

Prepare the first human validation round for the published v0.4.2 kit.
This compatible documentation addition keeps the method, reference APIs,
schemas, and teaching fixtures unchanged. No migration from v0.4.2 is required.
The round is prepared, not started; no human results are claimed.

### Added

- Prepare the first human evaluation round for the v0.4.2 kit: unsent English
  Rust and DDD reviewer invitations, pinned method/kit sources, a sequenced
  review and practitioner exercise, and a round consolidation template.
  Preserve initial attempts, assistance, dissent, missing evidence, and
  contributor approval for any public summary. Preparation does not send
  invitations or claim completed human validation.

### Changed

- Publish v0.4.3 as the default documentation edition through the existing
  tag-driven workflow. Preserve v0.1.0–v0.4.2, their tagged sources and
  navigation, and historical research records. Keep the initial method/code
  baseline at v0.4.1 and the review kit at v0.4.2; record the coordination
  plan's exact accepted revision separately before outreach.

## [0.4.2] — 2026-10-12

Publish the human validation kit as a compatible documentation addition.
The eight-field contract, six-step procedure, reference APIs, schemas, and
teaching fixtures retain their v0.4.1 behavior. No migration is required.
This remains a pre-1.0 preview; a published kit is not completed human review.

### Added

- Add an English validation kit with Rust and DDD/architecture reviewer
  briefs, a technology-neutral document-publication exercise, a separate
  facilitator guide, predeclared trial criteria, and a results template.
  Record exact review scope, assistance, predictions, observed checks,
  disagreements, and publication permission without claiming completed human
  review or field validation. Link the kit from v0.4.2 and Development navigation
  and contributor guidance. Keep v0.4.1 as the initial method/code baseline and
  record the kit revision separately.

### Changed

- Make v0.4.2 the default documentation edition through the existing tag-driven
  publisher. Preserve v0.1.0–v0.4.1, their tagged sources and navigation, and
  historical research records.
- Require both proposed technology mappings to preserve every required promise
  for a successful Transfer assessment. A changed promise or infeasible mapping
  is unmet; unresolved feasibility is unknown. Keep the protocol, facilitator
  guide, and results template consistent, and separate paper assessment from
  executed implementation qualification.

## [0.4.1] — 2026-10-12

Separate the method from its reference implementations in the documentation.
This compatible documentation release keeps the eight-field contract,
six-step procedure, APIs, and teaching fixtures unchanged. No migration from
v0.4.0 is required. This remains a pre-1.0 preview.

### Changed

- Separate Method, Templates, Design cases, Implementations, and Evidence in
  site navigation. Present neutral payment/revocation cases before the
  Java, Rust, PostgreSQL, and HTTP laboratories.
- Keep the canonical eight fields and six-step procedure while moving Rust
  mechanism detail into an implementation guide. Add technology-selection
  questions with explicit evidence boundaries for alternative stores/runtimes.
- Preserve published homepage teaching while Development adopts the new
  organization; pin future release homepages to their tagged sources.
  Existing edition routes, release sources, APIs, identifiers, and historical
  research records remain unchanged. The v0.4.1 homepage comes from its own
  tagged source, while v0.1.0–v0.4.0 retain their published teaching.
- Clarify that compatible documentation reorganization uses a patch version;
  incompatible changes to the method or executable contracts still require a
  minor version during 0.x development. Alternative technologies remain
  evaluation candidates, with no new implementation support claimed.

## [0.4.0] — 2026-10-12

Operation-specific permissions for the Java and Rust HTTP teaching APIs.
The eight-field Relationship Contract is unchanged. This remains a pre-1.0
preview.

### Changed

- Align Java and Rust rejection precedence for requests with multiple invalid
  inputs, including malformed authorization routes in legacy mode. Add shared
  HTTP regressions that verify rejection leaves business effects unchanged.
- Correct current learning-path, permission-matrix, and hosted-evidence guidance;
  retain the original release documentation and historical receipts.
- Add operation-specific PostgreSQL permissions to the Java composition, Java
  Template Method, and Rust HTTP APIs. Each request binds one immutable operation;
  every protected phase rechecks its exact policy row, including retries and
  response reads. Reconciliation-only callers can recover retained payment and
  refund identities after revocation or restart.
- Replace the fixture observation route with `authorization/{operation}` and
  add an equivalent permission-isolation, revocation, and restart test matrix.
  Existing coarse grants remain stored but confer no operation permissions;
  fixture owners must explicitly seed the desired operations. Legacy mode and
  previously published documentation editions retain their behavior and content.

### Migration from 0.3.0

- Install the updated additive [HTTP policy schema](case-studies/orders-payments/http/schema.sql).
  Explicitly grant `(scope, principal, operation)` rows in
  `roo_authorization.operation_grants` through trusted SQL. The closed operation
  set is `read`, `init`, `add`, `pay`, `refund`, `reconcile`, `relay`, and the
  test-only `provider_conflict`. Retain denied rows as tombstones.
- Existing `(scope, principal)` grants remain stored but are inert for the new
  fixture binaries. There is no fallback, automatic backfill, wildcard, or
  implied permission. Plan the cutover and seed each intended operation before
  using fixture authorization with v0.4.0.
- Replace the fixture observation route with
  `GET /v1/scopes/{scope}/authorization/{operation}`. An observation is advisory;
  each protected transaction checks the bound operation again before business
  locks or effects. A grant for one operation does not grant another.
- A `reconcile` grant can recover an existing payment/refund intent after
  revocation or restart, including for a different synthetic principal. It
  cannot create a new intent or provider effect; recovery retains the original
  identity and fingerprint. A 403 or lost response can follow an earlier commit.
- Legacy mode remains the default. Fixture mode still requires
  `ROO_HTTP_AUTH_MODE=fixture`, `ROO_HTTP_TEST_MODE=1`, and exactly one
  `X-Roo-Principal`. This synthetic assertion is not authentication.
- The v0.1.0, v0.2.0, and v0.3.0 tags, edition sources, and historical research
  records remain preserved. v0.4.0 becomes the default documentation edition.

## [0.3.0] — 2026-10-12

Persistent authorization for the Java and Rust HTTP teaching APIs, with the
eight-field Relationship Contract unchanged. This remains a pre-1.0 preview.

### Changed

- Remove remaining retired contract labels from current chapters and case
  guides; distinguish invariant coordination, caller authorization, and local
  mutation access.
- Keep homepage teaching and links within the selected documentation edition,
  including an introduction matching the archived first edition.
- Shorten the worked homepage contract, separate its eight fields from framing
  lines, and remove the caveat caption and redundant release link.

### Added

- Opt-in HTTP fixture authorization backed by durable PostgreSQL policy in Java
  and Rust, with transaction-level revocation checks, equivalent HTTP schedules,
  and recovery of the original payment identity after process/database restart.
- A bounded caller-authorization example in Java and Rust: execution rechecks
  permission under the order transition's lock, with revocation between
  observation and execution, shared outcomes, controlled thread tests, and CI.
- A CI vocabulary check for retired field labels and summaries, with narrow
  migration exceptions and regression tests.

### Migration from 0.2.0

- Legacy HTTP behavior remains the default. Enable the synthetic authorization
  fixture explicitly with `ROO_HTTP_AUTH_MODE=fixture` and
  `ROO_HTTP_TEST_MODE=1`; supply one `X-Roo-Principal` header. The header asserts
  a test principal and does not authenticate a person.
- Install the additive [HTTP policy schema](case-studies/orders-payments/http/schema.sql)
  after the PostgreSQL schema. The trusted fixture owner grants or revokes
  `(scope, principal)` access through SQL, retaining denied rows as tombstones.
  No HTTP policy-administration endpoint or production identity layer is added.
- Each protected transaction rechecks current policy before business locks or
  effects. An observation does not reserve access. Revocation does not undo a
  prior commit, and even a 403 response can follow a committed payment phase.
- Reconcile uncertain payment/refund outcomes with current permission and the
  original operation identity. Line additions remain non-idempotent; never
  blindly replay an uncertain line POST.
- The eight contract fields, package/scenario identifiers, v0.1.0 and v0.2.0
  sources, and historical research records remain preserved. The numeric tag
  makes v0.3.0 the default documentation edition while retaining earlier ones.

## [0.2.0] — 2026-10-11

The eight-field Relationship Contract, with versioned documentation and
executable chapter examples. This remains a pre-1.0 preview of the method.

### Changed

- Consolidate the method into one eight-field contract and six-step procedure;
  separate invariant coordination from caller authorization throughout the
  current chapters, templates, and case documentation.
- Shorten the overview and worksheet, center the homepage on a worked payment
  relationship and three clocks, and identify pre-1.0 editions as previews.
- Describe AI-assisted authorship and same-family agent review accurately;
  collect evidence boundaries in Claims and limits.

### Added

- Compile and execute chapter Rust and Java examples directly from Markdown
  in documentation CI, with checks against unclassified or skipped fences.

- Automatic documentation editions from stable release tags, with tagged
  navigation, semantic ordering, preservation checks against published sources,
  serialized publication on main, and an idempotent release dispatcher.

- Versioned GitHub Pages documentation with a pinned v0.1.0 content edition,
  a Development edition following main, an accessible version selector,
  edition-local search, source manifests, and redirects from existing URLs.

- GitHub Pages documentation with chapter, template, and case-study navigation,
  full-text search, a v0.1.0 release introduction, and automated build/link
  validation before deployment.

### Migration from 0.1.0

- Replace the old **Mutation authority** field with **Coordinator** (the
  component and operations that preserve an invariant) and **Authorization**
  (the principal, permitted operations, policy, and revocation rule).
- Use the eight compact keys: **Custodian, Identity, Coordinator,
  Authorization, Access, Horizon, Execution, Failure**. Invariant, Evidence,
  and Open provide context; they are not additional contract fields.
- Follow the canonical six-step procedure in Chapter 2, then use the same
  decisions in Java or Rust. A reference, ID, mutable borrow, or capability
  does not by itself establish caller permission.
- Existing case-study identifiers, policy inputs, HTTP behavior, and database
  schema remain compatible. Caller authentication and authorization are still
  outside the executable teaching case; the separate field makes that gap
  explicit rather than adding a security implementation.
- The v0.1.0 tag, original seven-field chapters, navigation, and historical
  research records remain preserved. The documentation publisher selects
  v0.2.0 by default and retains v0.1.0 and Development in the version selector.

## [0.1.0] — 2026-10-11

First public release of **ROO — Relationship & Ownership Oriented design**.

### Added

- A language-independent method for describing ownership, mutation authority,
  identity, access duration, execution domains, and failure boundaries.
- Foundations, a classical OO concept atlas, all 23 GoF pattern translations,
  software architecture guidance, cross-language mappings, and a learning path.
- Three reusable templates and completed orders/payments adoption examples.
- Rust laboratory examples and positive/compile-fail tests.
- Equivalent Java composition, Java Template Method, and Rust composition
  studies, extended with PostgreSQL persistence and HTTP APIs.
- Six executable adoption exercises with starter code, completed solutions,
  shared policy cases, and malformed-input checks.
- Witnessed concurrency, process-death recovery, immediate PostgreSQL
  restart/WAL recovery, durable payment identities, outbox delivery, and HTTP
  response-loss recovery in the bounded educational scenarios.
- Docker Compose reproduction with a nonroot container, no external runtime
  network, no host mounts or published ports, and scoped cleanup.
- GitHub-hosted AMD64 qualification, commit/source provenance, restricted
  container inspection, and downloadable test evidence.
- Dual licensing for original ROO material under `MIT OR Apache-2.0`, explicit
  third-party exceptions, contribution and release guides, and README badges.

### Release scope

This is a GitHub source release. The Rust packages remain `publish = false`;
no package registry publication or executable binary distribution is included.
New documentation is in English. Historical research inputs and recorded
results retain their original bytes and meaning. Passing the test scenarios
does not establish every interleaving, physical power-loss behavior, external
provider behavior, or production readiness.

[Unreleased]: https://github.com/limaronaldo/roo/compare/v0.4.3...main
[0.4.3]: https://github.com/limaronaldo/roo/releases/tag/v0.4.3
[0.4.2]: https://github.com/limaronaldo/roo/releases/tag/v0.4.2
[0.4.1]: https://github.com/limaronaldo/roo/releases/tag/v0.4.1
[0.4.0]: https://github.com/limaronaldo/roo/releases/tag/v0.4.0
[0.3.0]: https://github.com/limaronaldo/roo/releases/tag/v0.3.0
[0.2.0]: https://github.com/limaronaldo/roo/releases/tag/v0.2.0
[0.1.0]: https://github.com/limaronaldo/roo/releases/tag/v0.1.0
