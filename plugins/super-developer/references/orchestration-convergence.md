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
- exact artifact tree/commit, base/clean-status, dependency/prerequisite snapshot, assurance profile/modes,
  canonical package/owner/lens/side assignments, receipt topology, and deterministic mutations;
- exact covered writes, commands, tests, repairs, reruns, evidence refresh, cleanup, delivery checkpoints and
  listed non-force refs plus the single authorized configured push endpoint for each relevant root, each under
  finite call/repair-wave/command/cost/time budgets;
- `proven-ready` results and exact `protected-activation-required` probes/remedies; and
- exclusions, escalation conditions, allowed technical-amendment policy, and the canonical Authorization Digest.

The choices are exactly **Approve and auto-resolve**, **Request changes**, and **Abort**. The implementation budget
retains total delegated calls and separately caps combined-low, code-review, final-specialist, and completion-audit
calls. Total issued calls cover role calls; reserve/issue precedes later cumulative role consumption and receipt.
Consumption is monotonic across freezes, cannot exceed issuance, and may advance without PASS for abandoned calls. Profile maxima fit the selected final equation
without requiring unused-role maxima. Final completion still proves exact graph-role minimums. Approval authorizes all
listed in-scope delivery actions without routine testing, repair, evidence, checkpoint, or handoff re-prompts. It
does not inherit Sidecar Portability or target/release/force/delete authority. Exact preplanned dependency/
manifest/service/permission actions require baseline + readiness snapshot + writes/actions + protected probes/
remedies and both immutable digests; prose alone never suffices. Unlisted/new/drifted items or credentials stop.

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

Run listed activation probes; otherwise escalate before writes. For an envelope-preserving correction the Owner
invokes nested `review-plan` with return stage, immutable ID/inputs/initial digest, parent effective digest/artifact.
Nested review returns no choice/ID: it commits canonical JSON under derived `reviews/amendments/` after the distinct
reviewed descendant commit, avoiding self-reference. The receipt binds schema/kind, ID/input digest, parent
artifact/digest, reviewed commit/tree, unchanged action/dependency/budget/policy digests, old/new routing, exact
invalidated/added IDs, exact `cold-plan-reviewer`/`technical-amendment` ownership, PASS, and timestamp. Lifecycle links receipt path/digest/checkpoint and
reviewed commit/tree; effective digest hashes parent + receipt digest + reviewed commit. Load the regular canonical
blob, verify objects/linear lineage/authority/routing/invalidation, checkpoint the one-generation link, then clear
it. Reject missing/FAIL/cross-parent/ID/stale/non-descendant/drift. Protected/action/budget change needs authority.

## Delivery Owner and Child Envelope
Only the Delivery Owner advances the post-checkpoint lifecycle, chooses repair or reassessment, preserves active
authorization/circuit state, and declares completion. A child performs bounded work and returns; it never invokes
the next stage, restarts `implement`, or treats inherited authorization as continuation authority.

Every nested call/return names caller and exact `return_to` stage; `create|amend|resume`; accepted artifact/code
state; envelope/baseline, covered/excluded actions, finite open items, budgets and cluster/strike context; and terminal disposition return
`done|blocked|needs_decision|architecture_invalidated|parked|cancelled|superseded`.
The child planner/reviewer does not start or resume implementation itself. An amendment returns exact old/new commits, affected authority/surfaces,
preserved evidence, invalidation, and any old→new package map; no child restarts implementation.

## Owner Continuity Dispositions
Only the Delivery Owner may checkpoint `park`, `resume`, `cancel`, or `supersede` through the compact Lifecycle
State. Park quiesces, records return stage/actions, preserves owner token/host/prior takeover but marks it stopped,
and preserves authorization, budgets/deadline/role use, packages, clusters, freeze/receipts, refs, and routing.
After exact remote verification, resume CAS-activates that owner or a different token/host only with takeover bound
to the parked token, host, generation, and canonical digest; it cannot use lease time, later local state, reset, or
active-active. Completed cannot resume; Cancel is terminal/no-action and preserves exact owner/state without cleanup.
Supersede is terminal/no-action: first fetch exact authorized replacement artifact and any non-null code refs. The
active/null-supersession replacement State transition/digest must validate, bind mapped IDs pending, and equal nullable
code provenance without old authority/completion. Persist baselines/map; ordinary transitions cannot mutate them.

## Final Assurance Continuation
Package verifiers and package-bound specialists return pre-freeze `B[i]` for one named package/contract lens; they
cannot claim final-state coverage. After the Delivery Owner creates `F`, every assurance child is cold, read-only,
return-only, and assigned one named non-overlapping lens. It never repairs, transitions, freezes, dispatches
another assurance role, checkpoints, or notifies.

The Owner runs low `F→C(two PASS)→V`, standard `F→R(PASS)→U(F,R)→V`, or high
`F→R(PASS)→S[*](F,R)→U(F,R,S[*])→V`. Before each C/R/S/U, a dedicated checkpoint issues one role/delegated
unit and active reservation bound to F/exact predecessors; F already exists. S waits for PASS R; U waits for PASS R
and every planned PASS S. A return binds reservation ID/generation/committed SHA/state digest; fully validate the
reservation/issuance/return States on final HEAD's first-parent chain, then consume the call. Failed/abandoned calls may consume
without PASS. No batch/reuse/cross-freeze; V is non-call index. Persist canonical freeze paths, run read-only
`validate-agentic-completion`, then notify. A finding finishes repair/checks before a new F/R.

## Finding Classification and Circuit
Classify all observations before repair with precedence: human-envelope `requirement-gap` >
`architecture-invalidation` > `implementation-defect|integration-regression` >
`test-fidelity-gap|evidence-stale-or-contradicted` > `confidence-enhancement`. Route respectively to user,
technical reassessment, closure repair, test repair/evidence refresh, or report-only; lower classes cannot hide a
higher rank, while either observed class in an equal-rank group may be selected with its matching route. Assurance
may promote through reviewed technical amendment; any rank decrease needs a fresh reviewed baseline and new user
authorization and is forbidden inside the existing authorization lineage.

A serious-cluster identity is the canonical digest of accepted invariant/contract + failure mechanism +
architectural surface. Observations append; a new agent, model, prompt, commit, status, report, matrix row, signature,
package label, or timeout never resets identity. New closure-repair enters strike-1 repair-eligible; human-envelope, technical-reassessment, evidence-refresh, and
report-only enter routed without repair/closure. Human gaps cannot close or complete this authorization. Technical
reassessment closes only with its validated PASS amendment receipt and invalidation; evidence refresh needs a safe
committed/current digest fresh from predecessor; report-only may close without repair. Every closure-repair batch
increments `repair_waves` and checkpoints a new exact-cluster reservation; later clusters need a later delta and
an ID absent from every historical active reservation, including abandoned waves. Clear only after every bound cluster has immutable exact-surface evidence: PASS closes
strike 1, FAIL opens strike 2. Persist reservation commit/generation/state digest; terminal lineage is immutable and continuation requires explicit user approval.

Keep one logical primary implementation owner per package/surface. Prefer resume; otherwise rehydrate one successor
with exact authorization, invariants, worktree, outcomes, cluster/strikes, and next action. Independent assurance
stays cold.

## Behavior-First Evidence and Stops

Inspect accepted obligations, bound production diff/actual path, minimum sufficient causal tests/observations,
proof/self-review, then matrices. Classify, reproduce, repair one root cause, run actual-path targeted and earliest
credible affected broad regression, then refresh proof/report and freeze. Test volume never gates.

Stop for envelope ambiguity/change, protected or unlisted action, blocked prerequisite, exact-state/ownership loss,
unknown class/cluster, budget/deadline exhaustion, open circuit, no credible envelope-preserving design, concurrent
owner, or evidence unable to force the claimed production path. On exhaustion, ownership loss, or CAS loss, only
the one-unit control reserve may record allowlisted ownership/parent checks and safe-checkpoint or last-verified
escalation. Either operation preserves semantic/checkpoint state and budgets and may change only Lifecycle State—
never code, evidence, receipts, or semantic artifacts. Safe checkpoint preserves the exact active owner. If
ownership/expected parent is unsafe, do not mutate/take over: remain non-completed, report the exact `last_verified`
checkpoint/conflict, and treat later observations as untrusted.
