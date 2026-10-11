# Maintaining the documentation site

The public site is [limaronaldo.github.io/roo](https://limaronaldo.github.io/roo/).
It presents the v0.1.0 edition and follows documentation changes on `main`.
For immutable release sources and qualification evidence, use the
[v0.1.0 release](https://github.com/limaronaldo/roo/releases/tag/v0.1.0).

## Build and preview locally

Use Python 3.12 and run from the repository root:

```sh
python3.12 -m venv .site-build/venv
.site-build/venv/bin/python -m pip install --require-hashes -r website/requirements.lock
.site-build/venv/bin/python website/build.py
.site-build/venv/bin/python -m http.server 8000 --bind 127.0.0.1 --directory .site-build/preview
```

Open `http://localhost:8000/roo/`. Stop the server with Ctrl-C. Build output,
the virtual environment, and preview files are ignored by Git.

The build renders the existing English Markdown files without editing them.
`website/mkdocs.yml` defines navigation and the publication allowlist.
`website/pages/` contains the site introduction, license overview, and this
maintenance guide. `README.md` appears as the chapter overview.

Links to published documents become site links. Links to code, directories,
and historical evidence lead to the exact source commit on GitHub. Historical
research inputs, runtime files, caches, database data, and credentials are
not copied into the site. Literal semicolons in Mermaid sequence messages are
escaped in the generated copy so they render as punctuation rather than
statement separators. A generated `source-manifest.json` records the
documentation sources and their hashes.

## Check and publish

The build uses hash-locked Python dependencies, MkDocs strict validation, and
an HTML crawler that checks navigation, internal links and fragments, assets,
English page metadata, and the search index. Mermaid diagrams use Material's
renderer; rendering diagrams requires its external Mermaid module to load.

The [documentation workflow](../../.github/workflows/docs.yml) builds on
relevant pull requests and pushes. Pull requests receive build validation
without deployment credentials. Only a successful build on `main` can deploy
through the `github-pages` environment. Deployment has its own Pages/OIDC
permissions; the build has read-only repository access.

The repository's Pages publishing source is **GitHub Actions**. The workflow
can also be dispatched manually on `main`. After deployment, check the public
URL, chapter and case-study navigation, search, diagrams, and the source
manifest. A successful build alone does not confirm that the site is live.

To add a document, add it to the navigation and keep new prose in English.
Update dependencies deliberately in `website/requirements.in`, regenerate
`website/requirements.lock` with hashes, and rebuild. Preserve version tags,
identifiers, and historical research records. The documentation build does
not run Java/Rust/PostgreSQL qualification; that remains a separate workflow.
