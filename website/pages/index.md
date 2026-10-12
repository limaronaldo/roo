---
hide:
  - navigation
  - toc
---

<div class="roo-home-hero" markdown="1">

<div class="roo-home-intro" markdown="1">

# Relationships first.

ROO (Relationship & Ownership Oriented design) is a proposed practitioner method for deciding what
each important connection in a design means: who keeps the data, who coordinates
its rules, who may request a change, how long access lasts, and what survives a failure. Decide that
first, then pick the classes, references, locks, or messages that uphold it,
in Java, Rust, or any other language.

Maintained by [Ronaldo Martins](https://github.com/limaronaldo).

[Try it on one relationship](#try-it){ .md-button .md-button--primary }
[Read the foundations](../../docs/01-foundations.md){ .md-button }

</div>

<figure class="roo-contract">
<div class="roo-diagram" role="img" aria-label="Class diagram: an arrow from Order to PaymentAttempt">
<span class="roo-class"><span class="roo-class__name">Order</span></span>
<span class="roo-edge"></span>
<span class="roo-class"><span class="roo-class__name">PaymentAttempt</span></span>
</div>
<div class="roo-attach" aria-hidden="true"></div>
<div class="roo-note">
<dl>
<dt>custodian</dt>
<dd>Local store keeps intent; provider keeps its result.</dd>
<dt>identity</dt>
<dd>One scoped attempt ID binds the order, currency, and amount.</dd>
<dt>coordinator</dt>
<dd>Application prepares, calls, then finalizes; domain checks transitions.</dd>
<dt>authorization</dt>
<dd>Caller policy is not implemented in this teaching case.</dd>
<dt>access</dt>
<dd>Order keeps an attempt ID and a read-only status snapshot.</dd>
<dt>horizon</dt>
<dd>Intent survives restart; a status snapshot can become stale.</dd>
<dt>execution</dt>
<dd>Short local transactions; the provider commits separately.</dd>
<dt>failure</dt>
<dd>Timeout can follow a charge. Keep Pending; reconcile by the same ID.</dd>
</dl>
</div>
</figure>

</div>

<div class="roo-home-body" markdown="1">

## Three clocks, not one

Holding a value doesn’t mean it is still true. ROO separates three ways that
access can expire, because each one needs its own check.

<figure class="roo-clocks">
<p class="roo-clocks__setup">At 10:00, a fulfillment job loads order 1042 and starts packing it.</p>
<div class="roo-clock roo-clock--memory">
<p class="roo-clock__name">Memory validity</p>
<div class="roo-clock__track" aria-hidden="true"><span class="roo-clock__bar"></span></div>
<p class="roo-clock__text">The job’s copy stays safe to read until the job ends at 10:05.</p>
</div>
<div class="roo-clock roo-clock--business">
<p class="roo-clock__name">Business validity</p>
<div class="roo-clock__track" aria-hidden="true"><span class="roo-clock__bar"><span class="roo-clock__end">10:02</span></span></div>
<p class="roo-clock__text">The customer cancelled at 10:02. The copy is still readable, but the order is no longer open.</p>
</div>
<div class="roo-clock roo-clock--freshness">
<p class="roo-clock__name">Observation freshness</p>
<div class="roo-clock__track" aria-hidden="true"><span class="roo-clock__bar"><span class="roo-clock__end">10:01</span></span></div>
<p class="roo-clock__text">The shipping address changed at 10:01. From then on, the copy shows the old one.</p>
</div>
<div class="roo-clock__axis" aria-hidden="true"><span>10:00</span><span>10:05</span></div>
</figure>

Lifetimes and garbage collectors manage the first clock. The other two are
managed only where the design says how; that is what the `horizon` line in a
contract is for.

## Try it on one relationship { #try-it }

Pick one arrow in a system you know, preferably one that crosses a process, a
transaction, a lifecycle, or a trust boundary. Fill in the eight fields. A line you can’t
fill is an open design decision, not permission to assume.

```text
Relationship: Source -> Target [cardinality]
Invariant: allowed result; forbidden result; when state must agree

Custodian: who retains the resource and releases it
Identity: key, scope, version, reuse, and deletion rules, or value only
Coordinator: component and operations that preserve the invariant
Authorization: principal, permitted operations, policy, and revocation rule
Access: observation, controlled command, snapshot, lookup, sharing, or transfer
Horizon: memory validity, business lifecycle, and freshness limits
Execution: task, process, transaction, and overlap coordination
Failure: surviving effects, retry, reconciliation, and compensation

Evidence: observed checks and references
Open: unresolved requirements and assumptions
```

No installs. Paste the result into a pull request or an architecture decision
record. Follow the [canonical six-step procedure](../../docs/02-relationship-design.md#23-the-six-step-decision-procedure).
The [Relationship Contract worksheet](../../templates/relationship-contract.md)
is the edition's reusable form; the
[payment recovery contract](../../case-studies/orders-payments/adoption/relationship-contract.md)
is a finished one to compare against.

</div>

## Go deeper

<div class="roo-paths" markdown="1">

<div markdown="1">

### Learn the method

Foundations and relationship design first, then classical OO concepts, all 23
GoF patterns, and architecture, each translated into relationship decisions.

[Read the foundations](../../docs/01-foundations.md)

</div>

<div markdown="1">

### Review a design

A worksheet, an architecture decision template, and a design review guide,
each paired with a completed orders/payments example.

[Open the templates](../../templates/relationship-contract.md)

</div>

<div markdown="1">

### Check the evidence

One orders/payments domain, from in-memory objects to PostgreSQL restarts and
lost HTTP responses, built in Java and Rust and checked against the same
expected results. Six exercises run in Docker.

[Open the case study](../../case-studies/orders-payments/README.md)

</div>

</div>

<div class="roo-home-close" markdown="1">

## Bring it a real design

**Pre-1.0 editions are previews.**
The [claims and limits](../../docs/claims-and-limits.md)
page maps evidence to its scope;
[How ROO was made](../../docs/how-roo-was-made.md)
describes AI-assisted authorship and same-family agent review.
Original material uses [MIT OR Apache-2.0](license.md).
What ROO needs most is evidence from real systems: if you write a contract for a design of yours, share what it caught
and what it missed.

[Share a case](https://github.com/limaronaldo/roo/issues/new?title=Case%20report%3A%20){ .md-button .md-button--primary }
[Read the release notes](../../RELEASE_NOTES.md){ .md-button }

</div>
