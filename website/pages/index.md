---
hide:
  - toc
---

<div class="roo-hero" markdown="1">

<p class="roo-eyebrow">RELATIONSHIP &amp; OWNERSHIP ORIENTED DESIGN</p>

# Relationships first.

Design who owns data, who may change it, how long access lasts, and what
happens when an operation fails. Then choose the language and mechanisms
that uphold those decisions.

ROO is a **language-independent design method** with executable Java and Rust
studies. Rust provides compiler feedback; the relationship decisions apply
across languages.

[Start with the foundations](../../docs/01-foundations.md){ .md-button .md-button--primary }
[Adopt ROO in a project](../../docs/09-adoption-guide.md){ .md-button }

</div>

<div class="roo-release" markdown="1">

**v0.1.0 · First public release**

The method, three templates, orders/payments studies, and six executable
exercises are available under **MIT OR Apache-2.0** for original ROO material.
The release includes source archives and qualification evidence from a
GitHub-hosted AMD64 runner with isolated PostgreSQL.

[Release notes](../../RELEASE_NOTES.md) ·
[Download v0.1.0](https://github.com/limaronaldo/roo/releases/tag/v0.1.0) ·
[License and exceptions](license.md)

</div>

## Choose a path

<div class="roo-paths" markdown="1">

<div markdown="1">

### Understand the method

Read the foundations, relationship design, OO concept atlas, and pattern
catalog. Continue through architecture and cross-language mappings.

[Explore the chapters](../../docs/01-foundations.md)

</div>

<div markdown="1">

### Make a design decision

Use the Relationship Contract, architecture decision, and design review
templates. Compare your choices with completed orders/payments examples.

[Use the templates](../../templates/relationship-contract.md)

</div>

<div markdown="1">

### Run the evidence

Follow one domain from in-memory objects to PostgreSQL and HTTP. Compare
Java composition, Java Template Method, and Rust against a shared oracle.

[Open the case study](../../case-studies/orders-payments/README.md)

</div>

</div>

## One domain, increasing obligations

| Stage | Design questions | Read next |
|---|---|---|
| In memory | Who owns the order? Where can mutation occur? When is composition or inheritance useful? | [Orders and payments](../../case-studies/orders-payments/README.md) |
| PostgreSQL | What is durable? Who coordinates concurrent changes? How do uncertain payments recover? | [Persistence and recovery](../../case-studies/orders-payments/postgres/README.md) |
| HTTP | Which requests are safe to retry? What happens when a response is lost? | [HTTP APIs](../../case-studies/orders-payments/http/README.md) |
| Practice | Can each design decision pass the same tests in Java and Rust? | [Six executable exercises](../../case-studies/orders-payments/track/EXERCISES.md) |

## Run the adoption track

```sh
git clone --branch v0.1.0 https://github.com/limaronaldo/roo.git
cd roo
bash case-studies/orders-payments/track/compose.sh
```

You need Docker, Compose, Bash, and common POSIX utilities. The evaluator
owns PostgreSQL inside the isolated container. The untouched starter is
expected to be incomplete; the solution is expected to pass.
See [Docker reproduction](../../case-studies/orders-payments/track/DOCKER.md)
for learner commands and [hosted validation](../../docs/10-github-reproduction.md)
for the evidence and its limits.

ROO v0.1.0 is an evolving educational method. Its compiler checks and tests
support specific obligations in bounded scenarios. They do not establish
production readiness or every possible failure and interleaving.
