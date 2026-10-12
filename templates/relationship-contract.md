# Relationship Contract worksheet

Use this compact record in a PR, issue, or architecture decision. Start with
one relationship that crosses a lifecycle, process, transaction, or trust
boundary, or whose invariant is difficult to explain.
The [canonical fields and procedure](../docs/02-relationship-design.md#21-the-eight-field-relationship-contract)
define the method; this worksheet is its fill-in form.

```text
Relationship: Source -> Target [cardinality]
Invariant: allowed outcome; forbidden outcome; when state must agree

Custodian:
Identity:
Coordinator:
Authorization:
Access:
Horizon:
Execution:
Failure:

Evidence: mechanism, observed check, and reference
Open: unresolved decisions and assumptions
```

Write one operational sentence per field. Use `not applicable` with a reason,
or `not implemented` with the consequence; an empty authorization field must
not look like permission. Split a record when modes have different custody,
validity, or failure rules.

## Realization, when needed

| Language, runtime, store, or protocol | Selected mechanism | Check that supports it |
|---|---|---|
| | | |

Keep the relationship decision constant when comparing languages. An ID,
borrow, Java interface, or SQL foreign key is a mechanism chosen afterward.
Add detail only for a consequential question: deletion and reuse, reverse
navigation, snapshot freshness, capacity, cancellation, or provider retention.

Try one success and one counterexample before accepting the decision. Compare
with the [completed payment-recovery record](../case-studies/orders-payments/adoption/relationship-contract.md),
then capture the tradeoff in the [architecture decision](architecture-decision.md)
and review it with the [design review](design-review.md).
