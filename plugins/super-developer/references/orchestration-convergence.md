# Planned-Feature Orchestration Convergence

## Boundary

This reference owns planned-feature lifecycle continuation, nested call/return, post-acceptance finding
classification, serious-cluster circuit state, logical implementation ownership, focused amendment handback,
and behavior-before-evidence ordering. It does not replace artifact, command, worktree, verification, review,
or audit contracts. Standalone skill invocations retain their documented standalone boundaries.

## Delivery Owner

After Gate 2 accepts and checkpoints an exact artifact state, `implement` is the Delivery Owner through final
readiness. Only the Delivery Owner advances the planned-feature lifecycle, selects repair or reassessment,
preserves active authorization and circuit state, and declares the next gate.

A child skill or role called by the Delivery Owner performs its bounded work and returns. It never invokes the
next lifecycle stage, restarts `implement`, independently delegates pipeline repair, or treats inherited
authorization as authority to continue after return.

## Nested Call Envelope

Every nested planned-feature call and return names:

- caller and exact `return_to` stage;
- mode: `create`, `amend`, or `resume` when applicable;
- accepted artifact state and reviewed code state when one exists;
- inherited authorization and excluded actions;
- finite open items and permitted continuation;
- serious-cluster identity, prior closure cycles, and circuit disposition when relevant;
- terminal disposition: `done`, `blocked`, `needs_decision`, `architecture_invalidated`, or `parked`.

Keep this envelope in the active owner context and explicit child packets/returns. Do not create a registry field,
standalone ledger, report, dashboard, or hidden chat-only continuation rule.

## Accepted State and Amendments

Gate 2 approves the mechanically validated artifact candidate plus only the declared `status -> reviewed`
mutation. Before broad sidecar staging, revalidate that no other artifact content changed. After the checkpoint,
record and verify the exact artifact commit; unexpected drift invalidates approval. Implementation consumes that
accepted commit, not a floating artifact branch or status alone.

A focused amendment returns to its caller with old/new accepted artifact commits and the affected requirements,
Slices, packages, assignments, production/test surfaces, proof/report state, and final-freeze inputs. Preserve
unaffected package identity when practical; otherwise return an explicit old-to-new map. Unaffected state may be
carried only with evidence. The child planner/reviewer does not start or resume implementation itself.

## Finding Classification

The Delivery Owner classifies every post-acceptance serious finding before repair:

- `requirement-gap`: accepted behavior/scope is missing or ambiguous; return for authority and amendment;
- `architecture-invalidation`: accepted ownership/state/routing cannot satisfy an invariant; stop repair and
  reassess design;
- `implementation-defect`: accepted design is encoded incorrectly; one bounded repair may proceed;
- `integration-regression`: another skill, mode, caller, or public contract is broken; repair the bounded impact;
- `test-fidelity-gap`: evidence does not exercise the claimed behavior; repair the evidence seam first;
- `evidence-stale-or-contradicted`: refresh only after behavior stabilizes;
- `confidence-enhancement`: non-blocking unless tied to an accepted requirement/contract or demonstrated
  security, privacy, safety, data, or correctness risk.

For mixed findings use the highest-authority class: requirement/scope decision, architecture invalidation,
implementation/integration defect, test/evidence defect, then confidence enhancement.

## Serious-Cluster Circuit

A serious-cluster identity is the accepted invariant or contract plus failure mechanism, architectural surface,
and verification signature. One strike is one failed closure cycle for that cluster, not every duplicate finding,
command failure, or report row.

- First failed closure: permit one bounded repair after classification.
- Second failed closure for the same cluster: open the circuit and stop automatic repair for focused design
  reassessment.
- Confirmed architecture invalidation: open the circuit immediately.
- A new agent, model, prompt, commit, status, report, matrix row, timeout, or renamed attempt does not reset it.
- Reset only after an accepted design/invariant change, decisive new evidence, or demonstrated closure of the
  original mechanism.
- Continuing an open circuit requires explicit user approval naming the new information and bounded action.

Design reassessment exits only with revised accepted invariants, focused plan review, a new accepted artifact
commit, and an affected-state/invalidation handback.

## Logical Implementation Owner

Keep one logical primary implementation owner per package or architectural surface. Prefer host session resume;
otherwise rehydrate one explicit successor with accepted invariants, worktree state, prior outcomes, cluster
identity, strikes, and allowed next action. Do not run concurrent implementation owners for the same surface or
reset circuit state because the runtime identity changed. Independent verification remains cold.

## Behavior-First Evidence

For package and affected final verification inspect in this order:

1. accepted requirements, contracts, and architecture invariants;
2. bound production diff and actual execution path;
3. causal tests and observations;
4. implementer proof and `SELF_REVIEW`/`REPAIR_SELF_REVIEW`;
5. deliverable-matrix reconciliation.

The matrix indexes evidence after semantic inspection; it does not define the test implementation. A
behavior-sensitive PASS demonstrates forced production preconditions/branch, a real collaborator outcome,
observable ordering or state transition, forbidden-outcome falsification, and a check that would fail when the
invariant is broken. Disclose cache hits, mocks, fixtures, test hooks, and synthetic substitutes. Labels, counters,
row counts, proof wording, or synthetic outcomes alone are insufficient.

## Repair and Freeze Order

For a serious finding: classify, reproduce the mechanism, repair one coherent root cause, establish actual-path
targeted evidence, run the earliest credible affected broad regression (or justified bounded substitute), and
only then refresh proof/report state and freeze final inputs. Shared discovery, registration, global state,
lifecycle, generated/public contracts, and recursive control flow require affected broad regression before
proof/report freeze. Classify broad-regression failure before another repair.

## Stops

Stop and return to the Delivery Owner for missing caller/return state, ambiguous cluster identity, uncertain
finding class, artifact/code drift, scope or risk authority, a second same-cluster failure, architecture
invalidation, concurrent owner conflict, or evidence that cannot force the claimed production path.
