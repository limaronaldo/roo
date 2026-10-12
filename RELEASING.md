# Releasing ROO

## Version and compatibility

The root `Cargo.toml` declares the repository release version. GitHub release
tags use `vX.Y.Z`, and [CHANGELOG.md](CHANGELOG.md) records that version. Private
case-study crates currently use `0.1.0`; they are examples, not separately
published packages. Keep their own manifest/lock versions consistent when
changing a package version. Do not rename identifiers to change a release label.

ROO follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html). During
0.x development, incompatible changes to the published contract, CLI, HTTP
behavior, or teaching fixtures use a new minor version; compatible corrections
use a patch version. Documentation reorganization and editorial clarification
also use a patch version when the method and executable contracts stay
compatible. Explain any migration in the changelog. Before 1.0, the
method and APIs remain evolving; a future 1.0 release must define its supported
public contract explicitly. Never move an already published version tag.

## Prepare a candidate

1. Update version metadata, changelog, English release notes, and contribution
   instructions. Preserve historical research and supplied inputs.
2. Confirm `MIT OR Apache-2.0` metadata and the scope exceptions in
   [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Retain both license texts.
3. Run root Rust checks and syntax/link/version checks appropriate to the change.
4. Commit the candidate and push its branch. The workflow runs on matching
   branch pushes, pull requests, and manual dispatch; version-tag pushes do
   not trigger duplicate adoption qualification. Documentation has its own
   tag-driven publication workflow.
5. Select the actual successful hosted AMD64 run at that exact commit. Verify
   the artifact's provenance, source hashes, Java/Rust matrix, PostgreSQL
   restart/WAL and HTTP-loss receipts, isolation, and cleanup statuses.

Use the [Docker guide](case-studies/orders-payments/track/DOCKER.md) for the
shared qualification command. Root tests and the adoption workflow cover
different parts of the release; neither replaces the other.

## Tag and publish

After qualification, use the exact tested commit rather than a moving branch:

```sh
git tag -a vX.Y.Z TESTED_COMMIT -m 'ROO vX.Y.Z'
git push origin refs/tags/vX.Y.Z
gh release create vX.Y.Z --repo limaronaldo/roo --verify-tag --title 'ROO vX.Y.Z' --notes-file RELEASE_NOTES.md
```

Before executing those commands, prepare release-specific notes and replace
the placeholders. If publication is not authorized yet, create a draft with
`--draft`. Once published, read back the tag's target, release state and notes,
and attached asset hashes. A release is complete only when these match the
reviewed candidate. A tag alone is not a GitHub Release.

The GitHub release offers source archives. Preserve durable qualification
summaries or assets because hosted workflow artifacts expire after 14 days.
Attach only allowlisted, checked evidence; never database files, environment
dumps, credentials, dependency caches, or build directories. Do not claim a
registry publication, binary release, signatures, or additional platforms
without executing and verifying those separate steps.

If qualification fails, correct the candidate and obtain a new successful run
before tagging. If publication outcome is unknown, query the exact tag and
release before retrying. Do not force-push tags, delete historical evidence,
or silently replace an asset under an existing release.

## Automatic documentation editions

Pushing a numeric `vX.Y.Z` tag requests documentation publication on `main`.
Here “stable tag” distinguishes this format from a prerelease suffix; it does
not certify method maturity. Pre-1.0 editions are labeled as previews, with
v0.1.0 identified as the first edition.
The publisher discovers all stable tags, reads each release's navigation and
documents from its exact commit, retains previous editions, updates the
version selector, and selects the highest numeric version as the default.
New tags require no manual documentation registry entry. Include the explicit
`nav` mapping in `website/mkdocs.yml` and every referenced document in the
qualified candidate. Keep new content and labels in English.

Wait for the separate **ROO documentation** run to finish and verify the new
edition plus the previous editions on GitHub Pages. A successful **ROO release
documentation** run only confirms that the publication request was dispatched.
The workflow rejects changed published tag identities, navigation, and document
hashes; restore the intended source identity rather than bypassing that check.

A published GitHub Release also requests documentation, and an existing tag
can be backfilled with `docs-release.yml` dispatched on `main` using its
`release_tag` input. Use prerelease suffixes for candidates that should not
become stable documentation. Push stable tags individually; if automation
creates them with `GITHUB_TOKEN`, explicitly dispatch the documentation
workflow because ordinary token-generated events do not trigger it.
See the [documentation maintenance guide](website/pages/maintaining.md) for
the complete publication, preservation, permissions, and recovery procedure.
