# Contributing to ROO

Contributions should improve **Relationship & Ownership Oriented design** as
a method that applies across languages. Rust is a laboratory language; a
useful design obligation also needs a clear mapping to other implementations.

## Propose a change

Open a [GitHub issue](https://github.com/limaronaldo/roo/issues) or a focused
pull request. Describe the problem, expected behavior, and affected contract.
For a pattern or architecture contribution, include the classical intent,
relationship decisions, tradeoffs, prior art, and evidence. Distinguish a
proposal, an executable example, and an established result.

Use English for new documentation, comments, tests, changelog entries, and
pull request descriptions. Preserve existing public historical records; add
new evidence instead of rewriting old results. Supplied inputs are not
automatically approved for publication: do not archive attachments or raw
review text by default. Publish only a relevant summary with material that is
authorized for this public project. Do not rename crate,
package, fixture, or scenario identifiers as a side effect of a prose change.

Keep private case studies private. A public case report should use a generic
system description and synthetic data, with publication rights confirmed by
the contributor. Exclude credentials, configuration secrets, personal data,
and private organizational or personal context from documentation and evidence.

## Work on a focused branch

```sh
git clone https://github.com/limaronaldo/roo.git
cd roo
git switch -c describe-your-change
```

Change the smallest relevant area. Use the [Relationship Contract](templates/relationship-contract.md),
[architecture decision](templates/architecture-decision.md), and
[design review](templates/design-review.md) templates when they clarify the
design. If behavior changes, keep the Java and Rust realizations and shared
oracle equivalent, or document an intentional implementation-specific check.

Learners can edit the starter policies and run the learner modes described in
the [track guide](case-studies/orders-payments/track/DOCKER.md). An intentional
solution to a starter exercise is not a suitable change to the untouched
starter shipped for qualification unless the teaching contract is also updated.

## Validate the affected behavior

For current method vocabulary:

```sh
python3 scripts/check_vocabulary.py
```

Use Coordinator and Authorization as separate contract fields. The check
rejects retired labels and old field lists in current prose while allowing
ordinary uses of “authority.” Exact migration quotations, released notes,
tagged sources, and historical records retain their wording.

For chapter examples, with Rust 1.96+, JDK 21+, and Python 3:

```sh
python3 scripts/check_doc_examples.py
```

Keep every chapter Rust/Java fence visibly classified and registered with that
check. Rust fences run as doctests through `include_str!`; Java fences compile
for release 21 with warnings denied and execute their assertions. Configuration,
protocol pseudocode, and diagrams carry an **Illustrative** label. The
[claims page](docs/claims-and-limits.md) explains the scope of each evidence class.

For root Rust laboratory changes, with Rust 1.96 or newer:

```sh
cargo fmt --all -- --check
cargo test --locked --offline
cargo clippy --locked --offline --all-targets -- -D warnings
```

For the authorization example, with Python 3.10+, JDK 21+, and Rust 1.96+:

```sh
python3 case-studies/orders-payments/authorization/verify.py
```

Keep the command traces, oracle, and controlled thread scenarios equivalent in
both languages. Revocation must be checked at execution, with no order effect
on rejection. Diagnostic observations are never caller credentials.

For the shared adoption track, with Docker, Compose, Bash, and common POSIX
utilities:

```sh
bash case-studies/orders-payments/track/compose.sh
```

The full qualification expects the shipped starter to be incomplete. It runs
the same matrix for Java composition, Java Template Method, and Rust
composition, with its own isolated PostgreSQL lifecycle. Keep payment intent
identities stable, preserve uncertain-outcome recovery, and do not replace
lock witnesses or restart/HTTP-loss checks with timing guesses. The
[case specification](case-studies/orders-payments/track/SPEC.md) defines the
observable obligations and proof limits.

For persistent HTTP authorization, the same qualification also runs the shared
[HTTP authorization suite](case-studies/orders-payments/http/AUTHORIZATION.md).
Keep fixture authorization opt-in, recheck policy in each protected transaction,
and preserve the same denied outcomes and restart recovery in Java and Rust.
An observed grant is not an execution permit. Retain denied policy rows and
recover uncertain payment/refund effects with the original identity.

Inspect the receipts as well as the exit status. Report the source commit,
command, platform, checks passed, and remaining limits. Hosted CI validates
AMD64 on GitHub; a local emulated run is different evidence. Never commit
credentials, dependency caches, build output, database data, or ignored runtime
artifacts. Follow the [hosted guide](docs/10-github-reproduction.md) to retrieve
the exact run and attempt artifact.

## Submit and review

In the pull request, explain the resulting behavior, relevant tests, and any
compatibility or provenance impact. Add a concise entry under `Unreleased` in
[CHANGELOG.md](CHANGELOG.md) for a user-visible change. Keep evidence tied to
the actual candidate and avoid weakening the oracle to obtain a green result.
Reviewers should be able to reproduce an important success and failure case.

By intentionally submitting original material for inclusion, you agree to
make it available under both [MIT](LICENSE-MIT) and
[Apache-2.0](LICENSE-APACHE), so recipients may choose either. Submit only
material you are entitled to contribute, identify third-party terms, and
preserve applicable notices. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
No separate contributor license agreement or sign-off requirement is imposed
by this guide.

Maintainers use [RELEASING.md](RELEASING.md) for versioning and release evidence.
