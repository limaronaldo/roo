# Maintaining the versioned documentation

The public site is [limaronaldo.github.io/roo](https://limaronaldo.github.io/roo/).
Its default edition is **v0.1.0 (stable)**. **Development (main)** contains the
current checked-out documentation and may include unreleased changes.

## Edition policy

| Edition | Public path | Content source | Update policy |
|---|---|---|---|
| v0.1.0 (stable) | `/roo/v0.1.0/` | Tag `v0.1.0`, commit `56374f78a7e78566e9edfcbb6aa281fe838eeb4d` | Tagged chapters, templates, studies, and project documents stay fixed. |
| Development (main) | `/roo/dev/` | The workflow's checked-out commit on `main` | Relevant changes on `main` rebuild this edition. |

The release tag predates the website. Its documentation is rendered with the
current publishing interface: the introduction, license overview, this
maintenance guide, navigation controls, theme, and assets. These **publisher
pages and presentation** can improve in both editions. They are not claimed
to be part of the release tag or immutable HTML. The method, templates, case
studies, release notes, and other repository documents in the stable edition
come from the pinned tag, never from the current working tree.

Each edition has a `source-manifest.json` recording its documentation commit,
publisher commit, input hashes, and the origin of each page (`release`,
`development`, or `publisher`). Local previews also record whether the working
tree is dirty; their commit links cannot represent uncommitted edits. Release
code and evidence links point to the pinned release commit. Publisher file
links point to the publishing commit. The original
[v0.1.0 release](https://github.com/limaronaldo/roo/releases/tag/v0.1.0)
remains the source of archives and qualification evidence.

## Switching versions and preserving links

Every edition page has an English, keyboard-accessible **Version** selector.
Switching editions keeps the corresponding page, query string, and fragment
when that page exists in the destination. If it does not exist, the selector
opens the destination's home page without the previous query or fragment.
An anchor that changed between editions may require selecting a new section.
Without JavaScript, explicit links to both edition home pages are available.

The site root and all 42 previously published flat page URLs redirect to the
corresponding stable pages, retaining query strings and fragments when
JavaScript is available. Existing chapter links therefore keep working.
Unknown URLs show an English 404 page with links to the editions. Search and
canonical URLs belong to the current edition: searching Development does not
mix results from v0.1.0.

## Build and preview locally

Use Python 3.12, a Git checkout containing the release tags, and run from the
repository root. A shallow clone must first fetch its release tags and history.

```sh
git fetch origin --tags
python3.12 -m venv .site-build/venv
.site-build/venv/bin/python -m pip install --require-hashes -r website/requirements.lock
.site-build/venv/bin/python -m unittest discover -s website/tests -v
node --test website/tests/versions.test.cjs
.site-build/venv/bin/python website/build.py
.site-build/venv/bin/python -m http.server 8000 --bind 127.0.0.1 --directory .site-build/preview
```

Open `http://localhost:8000/roo/`, or use `/roo/dev/` directly. Stop the server
with Ctrl-C. Build output, virtual environments, and previews are ignored by
Git. The build extracts the tagged sources into its own temporary directory;
it does not switch branches or edit repository documentation.

[The edition registry](../versions.json) declares the default, labels, source
refs, exact release commits, and navigation files. Development navigation and
the publication allowlist are in [mkdocs.yml](../mkdocs.yml). The stable
navigation is frozen in [releases/v0.1.0.yml](../releases/v0.1.0.yml).
`README.md` appears as the chapter overview. Site-only pages are in
`website/pages/` and are identified as publisher inputs in the manifests.

Links to published documents become edition-local links. Code, directories,
and historical evidence remain on GitHub. Historical research inputs, runtime
files, caches, database data, and credentials are not copied into the site.
Literal semicolons in Mermaid sequence messages are escaped only in generated
copies. Rendering diagrams requires Material's external Mermaid module.

## Validate and publish

The [documentation workflow](../../.github/workflows/docs.yml) fetches history
and tags, installs hash-locked dependencies, runs the version-isolation and
selector regression tests, and builds both editions with MkDocs strict
validation. An HTML crawler checks every edition's navigation, canonical URL,
selected version and destination URLs, local links and fragments, English HTML
metadata, source hashes, search membership, and legacy redirects. A release
tag that no longer matches its pinned commit fails the build.

Pull requests receive validation with read-only repository access. Only a
successful build on `main` can upload and deploy the combined Pages artifact
through the `github-pages` environment. The deploy job has its own Pages/OIDC
permissions. No `gh-pages` branch or repository write token is needed. The
repository's Pages source is **GitHub Actions**; the workflow can also be
dispatched manually on `main`.

After deployment, check both public editions, version switching on a nested
chapter, search, legacy URLs, and their source manifests. A successful build
alone does not confirm publication. The documentation workflow does not run
Java/Rust/PostgreSQL qualification; that remains a separate workflow.

## Publish a future release edition

1. Complete the repository's release procedure and create the new version tag
   without changing existing tags or historical records.
2. Copy the current `nav` mapping into a new `website/releases/vX.Y.Z.yml`.
   Keep each existing release's navigation file and pinned content commit.
3. Add a registry entry with `id: vX.Y.Z`, the corresponding
   `refs/tags/vX.Y.Z`, its exact peeled commit SHA, an English label, and the new
   navigation file. Retain the `dev` entry with `source_ref: HEAD`.
4. Change the registry's `default` if the new release should become the landing
   edition. Update the publisher introduction and announcement to highlight it.
5. Run the tests and full build, review every edition, and publish through the
   existing workflow. Update tags, identifiers, and historical records only as
   authorized by their own release procedure.

Add new chapters to Development navigation first. They do not enter an older
release's frozen navigation. The selector falls back to that release's home
page when a new chapter has no counterpart. Deliberate corrections to the
shared interface must continue to preserve tagged document bytes. Keep all
new prose and labels in English. Update dependencies in
`website/requirements.in` deliberately, regenerate the hash lock, and rebuild.
