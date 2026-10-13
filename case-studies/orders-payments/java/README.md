# Java variants

ROO — Relationship & Ownership Oriented design is a language-independent
method; this README carries one scenario and invariant into Java relationship
decisions, implementation mechanisms, and evidence.

Start with timeout-after-effect: the order stays Pending and the same PaymentId
drives reconciliation when the caller cannot know the provider outcome. The
[shared contract](../SPEC.md) and [case walkthrough](../README.md) fix that
invariant; chapter 2's [Relationship Contract](../../../docs/02-relationship-design.md#21-the-eight-field-relationship-contract)
and [worksheet](../../../templates/relationship-contract.md) guide custody,
stable identity, invariant coordination, caller authorization, access, horizon,
execution, and failure decisions. This in-memory PaymentId lasts one scenario,
not a restart, and grants no authorization. Java types, private APIs, and final
methods express local boundaries, but do not statically enforce exclusive
resource custody or prove adapter honesty. No caller authorization policy is
modeled.

Both entrypoints consume the frozen parent SPEC and share typed immutable request
facts, the encapsulated aggregate, detached store snapshots, provider records,
and deduplicating consumer. CompositionApplication injects StorePort and
ProviderPort directly. TemplateApplication owns final add/payment/refund/recovery
algorithms and private finalization; InMemoryTemplateApplication supplies only
stable store/provider hooks. The small coordinator algorithms deliberately appear
in both implementations so the comparison exposes the actual composition and
inheritance structures rather than selecting a flag inside one coordinator.

The template hook contract requires stable adapters obeying the documented port
semantics. A malicious adapter can violate a capability contract in either
variant. Java final methods prevent replacing the algorithm; they do not prove
adapter honesty or distributed consistency. Money uses checked long arithmetic;
typed IDs prevent accidental domain API identity substitution. Public snapshots
and line lists cannot mutate the committed aggregate.

From the repository root, run:

```sh
bash case-studies/orders-payments/java/build.sh
java -cp case-studies/orders-payments/java/build/classes roo.payments.CompositionRunner case-studies/orders-payments/scenarios.tsv
java -cp case-studies/orders-payments/java/build/classes roo.payments.TemplateRunner case-studies/orders-payments/scenarios.tsv
```

The build requires a JDK supporting `--release 21`, compiles with all lint warnings
as errors, runs explicit unit assertions for each coordinator, then checks the
negative examples fail with private-access, final-override, and non-public-store
diagnostics. Those samples compile under an English locale
(`-J-Duser.language=en -J-Duser.country=US`) so the expected diagnostic text stays
stable on a localized JDK. It uses no Maven, third-party dependencies,
assertion-enable flag, clock, or network. Negative diagnostics are retained under
build/negative. The build script uses standard bash arrays compatible with macOS
bash 3.2.

Unit tests inspect intermediate failures, immutable snapshots, overflow parsing,
persisted-before-remote ordering, refund identity conflict, declined refunds
rejected before any local write, stable event facts, provider request fingerprints
including order/currency/amount/payment identity, terminal replay, independent
remote effects, and consumer redelivery deduplication.
Compiler-negative examples establish only their named Java access restrictions.
The parent SPEC describes simulator assumptions and production limitations.
Execution results belong in the parent evidence ledger; authored tests alone are
not evidence that checks passed.
