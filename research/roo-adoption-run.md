# Practical ROO adoption guide run

Date: 2026-10-11. User request: create a practical English adoption guide,
complete the three ROO templates using orders and payments, and show how the
same decisions translate into Java and Rust.

## Scope and authority

Documentation only. Preserve executable identifiers, source, fixtures,
specifications, generic templates, dependencies, scripts, existing fenced
examples, and historical evidence. No build, runtime test, HTTP, SQL, cluster,
network, publication, or credential operation is needed. Root owns qualification
and navigation edits. Current baseline verifies all 168 prior candidate files;
roo-adoption-baseline.json includes the prior final ledger, manifest, and review,
for 171 protected starting paths. The workspace has no Git metadata; use exact
file manifests rather than inventing a commit or repeatedly probing Git.

Apply parallel-model-orchestration 1.7.22. Root model/effort are not independently
reported, so use supervised coordination with a bounded Sol consultation before
new editorial decomposition. The user's established native profiles are Luna
Max and Sol 6.1 Medium. Nine concurrent slots including root are available.
No external clients, recursive delegates, profile/account changes, or quota
probes. Provider tokens, cache, cost, quota, and call totals are unavailable,
not zero. Native spawn arguments record requested profiles, not independently
verified provider identity.

## Queue

| ID | Requested profile | Role / ownership | Dependency | State |
|---|---|---|---|---|
| A | Sol 6.1 Medium | Read-only editorial consultation for the requested guide and worked templates | Existing templates and case contracts | completed; adoption_architect |
| S | Luna Max | Read-only source and scenario evidence map | Actual Java/Rust/PG/HTTP source | completed; adoption_source_map |
| W1 | Sol 6.1 Medium | docs/09-adoption-guide.md | Accepted editorial recipe | completed; adoption_guide_writer |
| W2 | Sol 6.1 Medium | adoption/relationship-contract.md | Accepted editorial recipe | completed; adoption_contract_writer |
| W3 | Sol 6.1 Medium | adoption/architecture-decision.md | Accepted editorial recipe | completed; adoption_decision_writer |
| W4 | Luna Max | adoption/design-review.md | Accepted editorial recipe | completed; adoption_review_example_writer |
| I | Root, unreported profile | Navigation, integration, protected-byte/link/template checks, evidence | Authored documents | completed; static qualification PASS |
| Q | Sol 6.1 Medium | Independent read-only frozen-candidate review | Integrated candidate and static evidence | completed; adoption_final_review; ACCEPT |

## Acceptance

All three examples retain the generic template's fields/questions and fill them
with specific decisions, evidence, and open assumptions. The guide gives a
usable adoption sequence and traces the same neutral decisions to actual Java
and Rust symbols and scenarios. Preserve seven contract fields, distinguish
custody/responsibility/identity/authorization, avoid invented signatures and
universal parity claims, and keep historical results explicitly historical.
Links, source references, source protection, completed fields, and independent
review qualify this documentation; unaffected runtime suites need no rerun.
Two failed corrections to one slice require a distinct architect/reviewer
consultation before a third attempt.

## Accepted editorial recipe

Root accepted the Sol consultation after it inspected actual templates, case
contracts, and coordinators. The four new documents share `recover_commit`:
`add:100:2;add:50:1;pay:p1:approve:commit;reconcile:ok:none`.
The source-described intermediate result is Pending with one provider charge
and zero outbox events; reconciliation reuses p1 and reaches Paid with one
charge and one payment:p1 event. Local in-memory intent survives calls within
a scenario, not process restart. Only the PostgreSQL extension provides
restart persistence; HTTP adds request/retry boundaries without another domain
workflow. Relay and refund remain secondary exercises with separate effects.

The filled relationship worksheet covers Coordinator → LocalStore and
Coordinator → RemoteProvider as a tightly related group. Preserve every source
template section, seven field names, supporting prompt, candidate row, and
review question, with answers and explicit evidence limits. The new decision
record is proposed documentary analysis, not invented historical approval.
Composition and Java Template Method are alternative realizations of the same
policy; Rust composition need not emulate inheritance. The guide includes
actual source-symbol mapping, an incremental adoption sequence, hands-on
source/scenario exercises, and links to all three worked artifacts.

Root may add navigation links only to README.md and the parent case README.
All other baseline files remain byte-identical. Independent source discovery
is advisory; each writer reads critical sources directly before making claims.

## Source inspection and integration

The Luna investigator inspected actual Java/Rust domain, coordinator, adapter,
and extension source plus scenario/oracle and historical validation receipts.
It mapped line custody, typed identity, prepare-before-effect, unknown outcomes,
state/outbox finalization, refund compensation, inbox deduplication, and the
additional HTTP lost-line-response case. Root also checked the actual Java
composition algorithm, Rust capability fields and methods, and the cited
intermediate-failure test symbol. Each writer read critical sources directly.

All four documents were delivered. Root added navigation in the two allowed
READMEs, separated policy alternatives from code-shape alternatives in the
guide, and made standalone ROO naming explicit. One correction pass on the
review example fixed money units (250 minor USD units, not USD 250), limited
the Java prepare/provider/finalize description to the applicable operations,
and clarified that Rust's exclusive resource borrows can span multiple calls
over the coordinator's active lifetime. Root corrected a brief's relative link
depth from four parent components to three before qualification.

The review-example writer disclosed one initial read-only Git status attempt,
which failed because this workspace is not a repository. It ran no subsequent
Git command and changed only its assigned new Markdown file. No application
builds, tests, network, SQL, HTTP, or cluster operations were performed.

## Static qualification

roo-adoption-validation.json records PASS. Of 171 baseline files, only the two
allowed README navigation files changed; the other 169 are byte-identical,
including all 59 historical research artifacts and all three original templates.
The 13 fenced blocks in the two edited READMEs are byte-identical. Four requested
new documents exist. All template sections, 20 relationship/context/support/
evidence prompts, seven fields, six realization candidates, seven ADR evidence
categories, and all twelve review questions are retained and filled. No worked
table cell or generic title/date/role placeholder remains blank. All 277 local
links and four anchor links resolve. The primary fixture and its final oracle
row match the preserved source. External links were not fetched.

The first check incorrectly treated an end-of-row pipe plus the next row's
opening pipe as an empty cell because its whitespace expression crossed a
newline. Root changed the checker to parse cells within each table row and
reran qualification, which passed. That false positive was a checker issue,
not a content defect. The final diff includes all four new documents and both
navigation changes. Runtime evidence is historical; no fresh test claim is made.

The independent reviewer inspected the full frozen diff and found one
source-accuracy issue in the guide's participant table: conflicting-content
validation for a repeated event ID is implemented by the Java consumer, while
the Rust consumer deduplicates only by event ID. Root narrowed the shared
statement to applying each unique EventId once, matching both implementations
and the base specification. Root reran static qualification and refreshed the
candidate for the reviewer's final verification.

The independent review returned ACCEPT for final candidate
`8c83e69c9106b79489d0efdc7ef8dd52b52c5e8f39b0c28920411bb5f4b1a16c`.
It verified all 178 hashes, independently reconstructed the complete diff,
confirmed preserved baseline/fences and valid links, and reported no unresolved
actionable findings. Root saved the terminal report in roo-adoption-review.md.
Acceptance is limited to documentation accuracy, completeness, usability, and
preservation; it does not create new runtime or production evidence.

## AI usage and coverage

| AI / route | Task group | Requested model → independently reported | Configured effort → reported | Agents / provider calls | Input/output tokens | Cache/reasoning tokens | Coverage |
|---|---|---|---|---|---|---|---|
| Native collaboration | Consultation, guide, relationship contract, decision, independent final review | gpt-6.1-sol → unavailable | medium → unavailable | 5 completed / unavailable | unavailable | unavailable | Spawn arguments and task completion reports; independent final review ACCEPT |
| Native collaboration | Source map and filled design review | gpt-6-luna → unavailable | max → unavailable | 2 completed / unavailable | unavailable | unavailable | Spawn arguments and task completion reports |
| Root | Integration, navigation, static qualification, evidence | unavailable → unavailable | unavailable → unavailable | 1 coordinator / unavailable | unavailable | unavailable | Direct tool results and saved artifacts |

Agent counts are unique task allocations, not model-call counts or measured
cost. No independent provider telemetry verifies actual model/effort, usage,
cache, cost, or quota. Unavailable values are not zero. No recursive delegate
or external client was used. Writers were parallel because files were disjoint;
integration and final qualification are serialized by dependency.

## Provenance and drift note (2026-10-13)

Added after the fact; the earlier text is not rewritten. This report relies on the adoption manifests listed below. Those manifests list `{path, sha256, bytes}` for a working tree as it stood **before** it was committed; they are preserved unedited. Measured on 2026-10-13 against git with `python3 -I research/manifest-audit.py --rev 8bf017f --also 0c3e2bb --also v0.1.0` (full results: [manifest-provenance-8bf017f.json](manifest-provenance-8bf017f.json)):

| Manifest | Entries | Match no git blob | Identical at `0c3e2bb` | Identical at `8bf017f` (v0.4.3) | Identical at `0c3e2bb` but changed by later commits |
|---|---:|---:|---:|---:|---:|
| `roo-adoption-baseline.json` | 171 | 3 | 168 | 126 | 42 |
| `roo-adoption-candidate.json` | 178 | 4 | 174 | 129 | 45 |

- **Pre-commit state.** "Match no git blob" counts entries whose recorded SHA-256 equals no blob reachable from any git ref: those bytes were never committed, and the repository does not retain their intermediate content. `0c3e2bb` is the commit that first contains these manifests.
- **What "matched" means here.** Where this report says the candidate files matched the manifest, that was a working-tree comparison made at review time. This note neither repeats nor disproves it; it only shows that the claim cannot be reproduced from git for the entries counted above.
- **Drift after acceptance.** "Frozen" and "unchanged" in this report hold for the acceptance date only. At `8bf017f`, 49 of 178 entries in `roo-adoption-candidate.json` differ from the manifest (by area: 32 in `case-studies/`, 10 in `docs/`, 4 in `repository root files`, 2 in `templates/`, 1 in `src/`). 45 of those were byte-identical at `0c3e2bb` and were changed by later commits; the rest were already different from git at the first commit. The manifest was not updated, because historical manifests are not edited.
