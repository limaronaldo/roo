# How ROO was made

**Maintainer: [Ronaldo Martins](https://github.com/limaronaldo).**

ROO began as a request to connect object-oriented design and software
architecture with explicit ownership. The method, chapters, templates, and
Java/Rust teaching cases were developed with AI assistance. The
[initial run ledger](../research/run-ledger.md) records parallel drafting,
integration, automated checks, and review on 2026-10-11.

## Authorship and review

The ledger records requested Luna and Sol model profiles. A separate Sol
agent reviewed the initial integrated candidate; some authors used the same
model family. The historical phrase “independent review” means a different
agent with a separate read-only assignment. It does not mean an independent
human reviewer or an external validation of the method.

Test receipts identify the automated workflow or authoring process that ran
each check. They do not document a completed human audit.

## Verification readers can inspect

The [root Rust validation](../research/validation.md),
[case validation](../research/orders-payments-validation.md),
[PostgreSQL validation](../research/postgres-validation.md), and
[HTTP validation](../research/http-validation.md) identify specific runs and
their limits. The [hosted reproduction guide](10-github-reproduction.md)
connects the executable track to GitHub Actions evidence.

Current chapter examples are checked from their Markdown sources in CI;
the [example runner](../scripts/check_doc_examples.py) documents the command.
The [claims and limits](claims-and-limits.md) page distinguishes those checks
from field evidence and broader architectural claims.

## Editorial direction and open work

ROO is intended for practitioners making design decisions. The learning track
demonstrates the method; the authoring pipeline is provenance rather than the
method's justification. The v0.2.0 edition consolidates the contract
into eight fields, separates invariant coordination from authorization, and
uses one procedure across chapters and templates. The homepage was adapted
from a provided HTML layout.

The v0.1.0 tag, its source documents, and historical research records remain
available unchanged. The site interface labels that edition as a preview;
development pages carry subsequent corrections. Homepages use the contract
and chapter links of the selected edition.

Open work includes review by Rust and DDD/architecture practitioners,
documented use in a real system, and measurement of what the contract catches.
Orders/payments remains a synthetic teaching case. Proposed reviews and case
studies become evidence only when their actual scope and results are recorded.

The project keeps the identifier **ROO** and documents its historical expansion. A
future naming decision should consider discoverability and existing projects;
this editorial revision does not rename published identifiers.
