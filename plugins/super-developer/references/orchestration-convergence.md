# Planned-Feature Orchestration Convergence

## Boundary

This reference owns Human Authorization Envelope separation, technical-plan amendments, the one Implementation
Authorization, finite budgets, planned-feature continuation, finding classification, serious-cluster state,
logical ownership, and behavior-before-evidence ordering. Other references own artifact, command, worktree,
verification, review, and audit mechanics.

## Human Envelope and Technical Baseline

- **Human Authorization Envelope:** user-owned outcomes, scope/exclusions, product/interface invariants, accepted
  material risks, protected effects, and spending/command/time bounds. Agents cannot alter it.
- **Technical Plan Baseline:** versioned architecture, packages/consumed contracts, commands/writes/cleanup,
  prerequisite activation, verification topology, assurance routing, and execution details. Agents may correct it
  only inside the unchanged envelope and after affected cold review.

Product/interface decisions, scope, risk acceptance, protected effects, and bound expansion require one focused
product question with a recommendation before another authorization candidate exists. Envelope-preserving
architecture, feasibility, package, command, or verification corrections return through preflight/planning and
cold review without a user prompt. Slices/SPEC/package authority remains canonical; add no decision ledger.

## Preauthorization Budget

At the Conceptualize-to-planning handoff, initialize or resume one finite budget in
`.tasks/<feature>/lifecycle-state.json`: at most eight total delegated planning/review/specialist calls, two total
planner-correction waves, two total spike waves (one per empirical cluster), a finite command maximum, and an
absolute deadline unless stricter bounds apply. CAS-reserve before use. Issued usage is monotonic and abandoned
work remains charged. A new baseline, agent, host, model, prompt, commit, or timeout never resets it.

Exhaustion returns one batched `needs_decision` packet with unresolved clusters and a recommendation. Only a
focused user decision may establish a new finite preauthorization budget; that decision does not authorize
implementation. No event ledger is added.

## One Implementation Authorization

Cold plan challenge and execution-readiness validation precede the user decision. One decision surface presents:

- the complete Human Authorization Envelope and reviewed initial Technical Plan Baseline;
- exact artifact candidate tree/commit, base code commit and clean-status digest, dependency/prerequisite
  snapshot, assurance profile/routing, package/receipt topology, and expected deterministic mutations;
- exact covered writes, commands, tests, repairs, reruns, evidence refresh, cleanup, delivery checkpoints and
  listed non-force refs plus the single authorized configured push endpoint for each relevant root, each under
  finite call/repair-wave/command/cost/time budgets;
- `proven-ready` results and exact `protected-activation-required` probes/remedies; and
- exclusions, escalation conditions, allowed technical-amendment policy, and the canonical Authorization Digest.

The choices are exactly **Approve and auto-resolve**, **Request changes**, and **Abort**. Approval authorizes all
listed in-scope delivery actions without routine testing, repair, evidence, checkpoint, or handoff re-prompts. It
does not inherit Sidecar Portability Authorization or authorize target merge/push, force, tag, release, deletion,
deployment, destructive/external effects, or new dependencies/services/credentials. Those remain separately
protected.

Only an **initial** clean review may present these choices. `review-plan` constructs one compact exact `inputs`
snapshot: reviewed `artifact_commit`, `artifact_tree`, `base_commit`, and digests `clean_status`, `dependencies`,
`routing`, `actions`, `budget_authority`, and `amendment_policy`. The artifact commit is the exact reviewed
predecessor candidate/checkpoint and has the named tree. `initial_digest` is the canonical JSON digest of exactly
that immutable snapshot. Approval creates one authorization ID, with initial effective digest equal to initial
digest; amendments retain initial inputs while their link advances the artifact checkpoint. `review-plan`
records/checkpoints the snapshot and exact accepted artifact commit. `implement` becomes Delivery Owner only after
verification. There is no later execution decision.

## Freshness, Activation, and Amendments

Immediately before product writes or package fanout, run a cheap equality guard over immutable authorization ID,
inputs/initial digest, effective digest, accepted artifact commit/tree, base code/status digest,
dependency/prerequisite snapshot, profile/routing, covered actions, authorized endpoints, and only expected
deterministic worktree/status mutations. Unlisted drift fails closed and returns through affected technical
review; ask the user only if protected authority or the Human Authorization Envelope changes.

Then run each listed protected activation probe. A listed remedy may auto-resolve; otherwise return one precise
prerequisite escalation before product writes. For a later envelope-preserving correction, the Delivery Owner
invokes `review-plan` in **nested amendment** mode with its return stage, existing ID/inputs/initial digest, parent
effective digest, and parent artifact. Nested review never offers choices, creates/replaces an ID, or enters fresh
gate readiness. It returns one cold amendment receipt binding unchanged envelope/inputs, parent/new baseline,
distinct reviewed descendant artifact checkpoint/tree, affected invalidation, routing, and cold verdict. Its
canonical amendment digest plus exact parent/artifact computes the next effective digest. The Delivery Owner
validates that receipt, checkpoints state, and resumes. Envelope, protected-action/endpoint, covered-action, or
budget-authority change stops for focused authority instead.

## Delivery Owner and Child Envelope

Only the Delivery Owner advances the post-checkpoint lifecycle, chooses repair or reassessment, preserves active
authorization/circuit state, and declares completion. A child performs bounded work and returns; it never invokes
the next stage, restarts `implement`, or treats inherited authorization as continuation authority.

Every nested call/return names caller and exact `return_to` stage; `create|amend|resume`; accepted artifact/code
state; envelope and current baseline identity; inherited covered/excluded actions and finite open items; budgets;
cluster/strike state when relevant; and terminal disposition `done|blocked|needs_decision|architecture_invalidated|parked`.
The child planner/reviewer does not start or resume implementation itself.

A focused amendment returns old and new accepted commits; affected requirements/Slices/packages/assignments,
production/test surfaces, proof/report/evidence/freeze inputs; evidence-backed preserved state; and old-to-new
package mapping. No child restarts implementation.

## Finding Classification and Circuit

Classify every serious finding before repair: `requirement-gap`, `architecture-invalidation`,
`implementation-defect`, `integration-regression`, `test-fidelity-gap`, `evidence-stale-or-contradicted`, or
`confidence-enhancement`. Mixed findings use that authority order. Envelope gaps return to the user; architecture
invalidation returns to bounded technical reassessment when an envelope-preserving alternative is credible;
eligible implementation/integration/test defects auto-resolve within listed budgets.

A serious-cluster identity is accepted invariant/contract + failure mechanism + architectural surface. The initial
independent rejection is strike 1 and permits one root-cause repair; failed affected closure is strike 2 and opens
the circuit. A new agent, model, prompt, commit, status, report, matrix row, signature, package label, timeout, or
wording change never resets it. Continuing an open circuit requires explicit user approval naming new information
and a new finite bound.

Keep one logical primary implementation owner per package/surface. Prefer resume; otherwise rehydrate one successor
with exact authorization, invariants, worktree, outcomes, cluster/strikes, and next action. Independent assurance
stays cold.

## Behavior-First Evidence and Stops

Inspect accepted obligations, bound production diff/actual path, minimum sufficient causal tests/observations,
proof/self-review, then matrices. Classify, reproduce, repair one root cause, run actual-path targeted and earliest
credible affected broad regression, then refresh proof/report and freeze. Test volume never gates.

Stop for envelope ambiguity/change, protected or unlisted action, blocked prerequisite, exact-state/ownership loss,
unknown class/cluster, budget/deadline exhaustion, open circuit, no credible envelope-preserving design, concurrent
owner, or evidence unable to force the claimed production path.
