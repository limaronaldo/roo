# Maintaining automated release documentation

The public site is [limaronaldo.github.io/roo](https://limaronaldo.github.io/roo/).
Each numeric release tag (`vX.Y.Z`) has its own edition at `/roo/vX.Y.Z/`. Development is
published at `/roo/dev/`. The highest **numeric** stable version is the default;
for example, `v0.10.0` sorts after `v0.2.0`, regardless of tag creation order.

## What happens when a release tag is pushed

1. Push a qualified tag named exactly `vX.Y.Z`, with no leading zeroes. The
   [release documentation workflow](../../.github/workflows/docs-release.yml)
   validates the event and requests the documentation workflow on `main`.
2. The publisher checks out current `main` and fetches all tags. It discovers
   every stable release tag and reads each edition's navigation from that tag's
   `website/mkdocs.yml`. No manual registry or navigation copy is needed for a
   new release. Tagged plugins, dependencies, and scripts are never executed.
3. It reads the currently published edition index and source manifests over
   HTTPS. Missing editions, moved tags, changed navigation, or changed tagged
   document hashes fail validation before deployment. An unavailable or invalid
   baseline also stops publication; it never becomes an empty reset.
4. It builds every release and Development with the current publishing tools,
   updates the version selector everywhere, and makes the highest stable tag
   the default. Older editions remain accessible at their original URLs.
5. Only the fully validated combined artifact deploys through the existing
   `github-pages` environment on `main`.

Publishing a non-draft, non-prerelease GitHub Release also requests this flow,
which covers releases whose tags predate the dispatcher workflow. Repeated
requests are safe: they discover the same tag identities and rebuild the same
edition set without creating tags, releases, or registry commits. The release
request job finishing confirms **dispatch**, not deployment; check the separate
**ROO documentation** run and public manifests for completion.

Tag names with prerelease/build suffixes, unrelated names, and tag deletions
do not request publication. Stable documentation follows tag **names**, not
GitHub Release flags: pushing a numeric `vX.Y.Z` tag publishes its documentation
before a GitHub Release may be created. Use names such as `v0.2.0-rc.1` for
prerelease candidates. Publishing documentation does not qualify code, create a
GitHub Release, upload release assets, or run the Java/Rust/PostgreSQL track.

## What stays fixed

| Input | Release edition | Development edition |
|---|---|---|
| Chapters, templates, studies, and project documents | Read from the exact tag commit | Read from the checked-out `main` working tree |
| Navigation | Read from the tagged configuration | Read from `main` |
| Homepage | Preserved publisher copies for v0.1.0–v0.4.0; read from the exact tag for future editions | Current homepage and reading routes |
| License overview, this guide, controls, theme, and assets | Current publisher interface | Current publisher interface |

The v0.1.0 tag predates the website. Its exact commit and original navigation
are bootstrapped in [versions.json](../versions.json) and
[releases/v0.1.0.yml](../releases/v0.1.0.yml). Preserve these inputs. The registry
contains this historical exception and the Development configuration; new
release entries are discovered automatically. A future tag must contain an
explicit `nav` mapping in `website/mkdocs.yml` and the documents it references.

The published introductions for v0.2.0, v0.3.0, and v0.4.0 previously shared a
publisher page. Their unchanged text is preserved in
[releases/v0.2.0-v0.4.0-home.md](../releases/v0.2.0-v0.4.0-home.md), with a fixed
hash checked by the test suite. Do not edit this compatibility copy. The first
edition retains its existing [homepage](../releases/v0.1.0-home.md).
Future tags must also contain `website/pages/index.md`: the publisher reads
that homepage from the tag and records it as release content. A missing
homepage stops publication instead of borrowing the current introduction.

Release **content and navigation** stay fixed. HTML and other publisher pages can
improve so the same selector includes new versions in older editions. Each
homepage teaches its selected edition: the first edition uses its original
contract, and later editions use separate Coordinator and Authorization fields.
Chapter, worksheet, case, and review links stay in the selected edition; pages
absent from an older edition are not linked from its introduction. Each
edition's `source-manifest.json` separates `release`, `development`, and
`publisher` page inputs, their commits, and original hashes. The public
`versions.json` records exact release commit/tag identities and navigation
hashes; the next run compares them with the repository and its generated
manifests. The first automated run also accepts the preceding site's metadata
format and verifies its recorded release document hashes.

Code and historical evidence links point to each release commit; publisher
file links point to the publisher commit. Local previews record dirty working
trees, whose uncommitted edits cannot be represented by a GitHub commit link.
Historical research inputs, runtime files, caches, database data, and
credentials are excluded. Original repository Markdown is never rewritten by
the site build. Mermaid punctuation normalization only affects generated copies.

## Version switching and old URLs

The English, keyboard-accessible **Version** selector keeps the current page,
query string, and fragment when a counterpart exists. Otherwise it opens the
destination home without a stale query or fragment. Without JavaScript, links
to every edition home are available. Anchors that changed between editions may
require choosing another section.

Each edition has its own search index and canonical URLs. The unversioned
root redirects to the highest stable tag. Existing flat chapter URLs point to
the newest release containing that chapter; a removed chapter therefore remains
reachable in an older edition. JavaScript redirects retain query strings and
fragments. Unknown paths show an English 404 page with edition links.

## Build, test, and preview

Use Python 3.12, Node.js with its built-in test runner, and a Git checkout with
release history. Run from the repository root:

```sh
git fetch origin --tags
python3.12 -m venv .site-build/venv
.site-build/venv/bin/python -m pip install --require-hashes -r website/requirements.lock
.site-build/venv/bin/python -m unittest discover -s website/tests -v
node --test website/tests/versions.test.cjs
python3 scripts/check_vocabulary.py
.site-build/venv/bin/python website/release_tags.py capture --output .site-build/previous-publication.json
.site-build/venv/bin/python website/build.py --previous-state .site-build/previous-publication.json
.site-build/venv/bin/python -m http.server 8000 --bind 127.0.0.1 --directory .site-build/preview
```

Open `http://localhost:8000/roo/` or `/roo/dev/`. Stop the server with Ctrl-C.
Build output and tag snapshots stay in ignored `.site-build/` directories.
The build does not change branches or modify tags. An offline local preview
can omit `--previous-state`; that preview does **not** prove preservation of
all previously published editions. CI always captures and checks the baseline.
Use `--release-tag vX.Y.Z` to additionally require a particular existing tag.

Tests use disposable Git repositories to exercise semantic ordering, annotated
and lightweight tags, new editions, frozen content and navigation, selector
fallback, rejected moved/deleted tags, unavailable baselines, and event
validation. Homepage tests isolate the existing editions from Development and
verify that future editions use their own tagged introduction. MkDocs strict mode and an HTML crawler verify every edition's
navigation, canonical URL, selected version and targets, links and fragments,
English metadata, source hashes, search membership, and legacy redirects.
It also rejects homepage contract keys or teaching links from another edition.

## Publication, recovery, and permissions

[The documentation workflow](../../.github/workflows/docs.yml) validates
relevant pull requests and publishes relevant pushes or dispatches on `main`.
All publication runs share one concurrency group. A queued run fetches current
`main` and **all** stable tags, so a newer request also includes editions from
coalesced requests. Pull requests have separate validation groups and cannot
upload or deploy Pages artifacts.

The release dispatcher has `contents: read` and `actions: write` to request a
workflow run. The publisher build has read-only repository access. Only the
deploy job has Pages/OIDC write permissions. The `github-pages` environment
continues to allow deployment from `main` only. No personal token, repository
write access, `gh-pages` branch, or new environment access rule is required.

To retry, backfill an existing tag, or verify the dispatch chain:

```sh
gh workflow run docs-release.yml --repo limaronaldo/roo --ref main -f release_tag=vX.Y.Z
```

Replace the placeholder with a real qualified tag. You can also run `docs.yml`
on `main` with an optional `release_tag` input. A missing or malformed requested
tag fails validation. If a previous tag was moved/deleted, or its metadata is
unavailable, investigate and restore the intended immutable source identity or
site availability before retrying. Do not bypass the preservation check, reset
the baseline, force-push release tags, or remove old editions as a workaround.

GitHub does not emit tag push events for a push containing more than three
tags. Push release tags individually. Events created with `GITHUB_TOKEN`
generally do not trigger another workflow; `workflow_dispatch` is supported.
If a future release workflow creates tags/releases with that token, explicitly
dispatch `docs-release.yml` as its final documentation step. A GitHub Release
publication or manual dispatch also covers older tags lacking this workflow.

After a run completes, verify the new edition, older editions, selector,
search, root redirects, and public source manifests. Keep new prose and labels
in English. Dependency updates remain deliberate changes to
`website/requirements.in` and its hash-locked requirements file.

## Edition maturity

v0.1.0 is labeled **first edition (preview)**. Other pre-1.0 snapshots are
previews too. A stable tag here means numeric `vX.Y.Z`, without a prerelease
suffix; it is not a claim of method maturity. Version labels are publisher
metadata; tagged source content stays fixed.
