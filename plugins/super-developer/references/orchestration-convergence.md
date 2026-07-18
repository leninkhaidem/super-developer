# Planned-Feature Orchestration Convergence

## Boundary

This reference owns authority separation, finite preauthorization, planned-feature continuation, nested
call/return, post-acceptance finding classification, serious-cluster circuit state, logical implementation
ownership, focused amendment handback, and behavior-before-evidence ordering. It does not replace artifact,
command, worktree, verification, review, or audit contracts.

## Human Envelope and Technical Baseline

- **Human Authorization Envelope:** user-owned outcomes, scope/exclusions, product/interface invariants, accepted
  material risks, protected effects, and spending/command/time bounds. Agents cannot alter it.
- **Technical Plan Baseline:** versioned architecture, packages/consumed contracts, commands/writes/cleanup,
  prerequisite activation, verification topology, assurance profile/routing proposal, and execution details.
  Agents may correct technical means only while the Human Authorization Envelope remains unchanged and the
  correction receives the required cold review.

A product/interface decision, material risk acceptance, protected effect, scope change, or bound expansion returns
to the user. An envelope-preserving architecture/feasibility correction returns through preflight/planning. Do not
create a second requirement, decision, amendment, or authorization ledger; Slices/SPEC/package authority remains
canonical and the compact Lifecycle State stores mechanical continuation only.

## Preauthorization Budget

At the Conceptualize-to-planning handoff, initialize or resume one finite budget in
`.tasks/<feature>/lifecycle-state.json`. Defaults: at most eight total delegated planning/review/specialist calls;
two total planner-correction waves; two total spike waves, at most one per empirical cluster; an explicit finite
command-unit maximum; and an absolute deadline. Stricter project/user bounds win.

Before every dispatch, correction/spike wave, or command, CAS-reserve its units and increment issued usage. Issued
usage is monotonic and abandoned work remains charged. Replanning, a new technical baseline, agent, host, model,
prompt, commit, or timeout never resets usage or deadline. Interactive user answers do not consume a planner
correction wave. Uncertain state fails closed. Exhaustion returns one batched `needs_decision` packet containing
unresolved clusters, observations, and a recommended scope/evidence choice. Only an explicit focused user decision
may establish a new finite budget; it does not authorize implementation. No event ledger is added.

## Delivery Owner

After Gate 2 accepts and checkpoints an exact artifact state, `implement` is the Delivery Owner through final
readiness. Only the Delivery Owner advances the planned-feature lifecycle, selects repair or reassessment,
preserves active authorization and circuit state, and declares the next gate.

A child called by the Delivery Owner performs bounded work and returns. It never invokes the next stage, restarts
`implement`, independently delegates repair, or treats inherited authorization as continuation authority.

## Nested Call Envelope

Every nested planned-feature call/return names:

- caller and exact `return_to` stage; mode (`create|amend|resume`);
- accepted artifact and reviewed code state when any;
- Human Authorization Envelope and current Technical Plan Baseline identity;
- inherited authorization, excluded/protected actions, and finite open items;
- preauthorization maxima/issued/deadline and reservation when planning remains active;
- serious-cluster identity, prior closure cycles, and circuit disposition when relevant; and
- terminal disposition: `done`, `blocked`, `needs_decision`, `architecture_invalidated`, or `parked`.

Keep this in active owner context, child packets/returns, and the existing compact Lifecycle State where mechanical.
Do not create a registry field, standalone ledger, report, dashboard, or hidden chat-only continuation rule.

## Accepted State and Amendments

Gate 2 approves the mechanically validated candidate plus only declared `status -> reviewed` mutation. Revalidate
before broad staging; unexpected drift invalidates approval. Implementation consumes the exact accepted commit.

A focused amendment returns old/new accepted commits and affected requirements, Slices, packages, assignments,
production/test surfaces, proof/report state, and final-freeze inputs. Preserve unaffected identity only with
evidence; otherwise map old-to-new explicitly. The child planner/reviewer does not start or resume implementation itself. An envelope-preserving Technical Plan Baseline revision does not silently mutate the Human Authorization
Envelope or reset any budget/circuit.

## Finding Classification

The Delivery Owner classifies every post-acceptance serious finding before repair:

- `requirement-gap`: accepted behavior/scope missing or ambiguous; return for authority/amendment;
- `architecture-invalidation`: ownership/state/routing cannot satisfy an invariant; stop and reassess design;
- `implementation-defect`: accepted design encoded incorrectly; bounded repair may proceed;
- `integration-regression`: another mode/caller/public contract is broken; repair bounded impact;
- `test-fidelity-gap`: evidence misses claimed behavior; repair evidence seam first;
- `evidence-stale-or-contradicted`: refresh only after behavior stabilizes;
- `confidence-enhancement`: non-blocking absent accepted contract or demonstrated serious risk.

Mixed findings use highest authority: requirement/scope, architecture, implementation/integration, test/evidence,
then confidence enhancement.

## Serious-Cluster Circuit

A serious-cluster identity is the accepted invariant or contract plus failure mechanism, architectural surface,
and verification signature. One strike is one failed closure cycle, not duplicate finding/command/report rows.

- First failed closure: permit one bounded repair after classification.
- Second failed closure for the same cluster: open circuit and stop for focused design reassessment.
- Confirmed architecture invalidation opens immediately.
- A new agent, model, prompt, commit, status, report, matrix row, timeout, or renamed attempt does not reset it.
- Reset only after accepted design/invariant change, decisive evidence, or demonstrated mechanism closure.
- Continuing an open circuit requires explicit user approval naming new information and bounded action.

Design reassessment exits only with revised invariants, focused plan review, new accepted artifact commit, and an
affected-state/invalidation handback.

## Logical Implementation Owner

Keep one logical primary implementation owner per package/architectural surface. Prefer session resume; otherwise
rehydrate one successor with accepted invariants, worktree state, outcomes, cluster/strikes, and next action. Do not
run concurrent owners or reset state because runtime identity changed. Independent verification stays cold.

## Behavior-First Evidence

Inspect: (1) accepted requirements/contracts/invariants; (2) bound production diff and actual execution path;
(3) minimum sufficient causal tests/observations; (4) proof and self-review; (5) matrix reconciliation. One causal
test may prove multiple rows. A PASS forces the production precondition/branch, observes a real outcome/transition,
falsifies forbidden outcomes, and would fail when the invariant breaks. Disclose cache/mocks/fixtures/hooks/
substitutes. Labels, counters, row counts, proof wording, and synthetic outcomes alone are insufficient.

Once accepted behavior and triggered risks are credibly demonstrated and required checks pass, stop adding tests.
Test count/LOC/ratio/coverage/suite volume and exhaustive suite review never gate. Existing tests block only for a
concrete correctness, fidelity, flakiness, skip/focus/weakening, unsafe-effect, material-runtime, or
trust-undermining harness/config defect—not volume.

## Repair and Freeze Order

Classify, reproduce the mechanism, repair one root cause, establish actual-path targeted evidence, run earliest
credible affected broad regression (or justified bounded substitute), then refresh proof/report and freeze. Shared
discovery/registration/global state/lifecycle/generated-public contracts/recursive control flow require broad
regression before freeze. Classify broad failure before another repair.

## Stops

Stop for missing caller/return or budget state; envelope ambiguity; protected action; unknown cluster/class;
artifact/code drift; scope/risk authority; budget/deadline exhaustion; second same-cluster failure; architecture
invalidation; concurrent owner; or evidence unable to force the claimed production path.
