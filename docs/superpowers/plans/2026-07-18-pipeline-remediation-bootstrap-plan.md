# Super Developer Pipeline Remediation Bootstrap Plan

**Status:** Proposed execution plan; requires approval before source edits
**Source baseline:** `docs/superpowers/specs/2026-07-18-super-developer-pipeline-orchestration-baseline.md`
**Target baseline:** Super Developer v1.39.0 (`df7396f`)
**Execution model:** Parent-owned bootstrap process; the installed Super Developer planning, implementation, review, audit, and release pipelines are not used to amend themselves

## Goal

Repair the orchestration, evidence, repair-loop, lifecycle, and release gaps documented in the baseline without importing the current plugin's failure modes into its own amendment process.

The work is delivered in three phases:

1. **Convergence hardening:** stop non-progressing repair cycles and move architecture/evidence discovery earlier.
2. **Assurance simplification:** reduce clean-path agent and artifact amplification while preserving independent defect detection.
3. **Lifecycle durability:** make amendment, resume, audit, evidence retention, and release exact-state coherent.

All three phases are in program scope. Each phase must be independently reviewable and releasable; later phases do not block the first convergence fix.

---

## Bootstrap Rules

These rules govern this remediation instead of the plugin under repair.

1. **One parent owner.** The current parent agent owns design interpretation, sequencing, file changes, state, and stop decisions.
2. **No plugin self-orchestration.** Do not invoke the installed `implementation-plan`, `review-plan`, `implement`, `review-code`, `audit`, `worktree`, or `release` skills as lifecycle controllers for this remediation.
3. **Conventional repository artifacts.** Use this plan, the baseline, ordinary git commits, and normal source/tests. Do not create `.tasks/`, proof matrices, package reports, review-state JSON, or artifact sidecars for this remediation.
4. **One implementation line.** Source changes occur serially in one isolated feature worktree. Do not dispatch competing implementation agents onto the same orchestration surface.
5. **Bounded independent review.** Independent agents may perform read-only design challenge or final diff review. They return findings to the parent and never own repair or continuation.
6. **Finding classification before repair.** Every serious finding is classified before any change.
7. **One repair attempt per serious cluster.** A second failed closure for the same mechanism stops implementation and returns to design reassessment.
8. **No evidence theater.** Prompt-contract tests may guard static authority, ordering, and contradictions but are not behavioral evidence. Run the phase scenarios as controlled synthetic caller/child packets through a fresh agent and record observed routing, stop, and evidence decisions in session evidence; do not infer behavior from required phrases.
9. **No helper-first solution.** Prompt/reference semantics are repaired first. Do not add a state database, dashboard, orchestration script, or new mechanical helper.
10. **Phase boundaries are real.** A phase is not expanded merely because an adjacent baseline finding is visible.

---

## Finding Classification Used During Remediation

| Class | Meaning | Action |
|---|---|---|
| `requirement-gap` | The approved target behavior is missing or ambiguous. | Stop and amend this plan/baseline with user approval where semantics change. |
| `architecture-invalidation` | The proposed ownership, state, or routing model cannot satisfy the target invariant. | Stop ordinary repair and redesign the affected phase. |
| `implementation-defect` | The accepted design is sound but incorrectly encoded. | Apply one bounded correction. |
| `integration-regression` | The change breaks another skill, mode, public contract, or lifecycle edge. | Correct the bounded affected surface and rerun the relevant scenario set. |
| `test-fidelity-gap` | A test passes without exercising the claimed path or invariant. | Repair the test seam; change production instructions only if the test exposes a real defect. |
| `evidence-stale-or-contradicted` | Existing evidence no longer represents the current files or behavior. | Refresh only after behavior is stable. |
| `confidence-enhancement` | Additional assurance without a demonstrated accepted-risk gap. | Record as optional; do not block the phase. |

Mixed findings follow the highest-authority class in this order:

```text
requirement/scope decision
→ architecture invalidation
→ implementation or integration defect
→ test-fidelity/evidence defect
→ confidence enhancement
```

---

# Phase 1 — Convergence Hardening

## Objective

Prevent the observed fix → verification → repair → verification loop by establishing one lifecycle owner, explicit return semantics, architecture invalidation routing, causal evidence requirements, and a design-level circuit breaker.

## Phase 1 target behavior

```text
accepted plan state
    ↓
Delivery Owner (`implement` in planned-feature mode)
    ↓ delegates bounded child role
child returns: done | blocked | needs-decision | architecture-invalidated
    ↓
Delivery Owner classifies finding
    ├─ requirement gap → plan/user authority
    ├─ architecture invalidation → focused redesign and new accepted state
    ├─ implementation/integration defect → one bounded repair
    ├─ test/evidence defect → repair evidence seam
    └─ confidence enhancement → non-blocking
    ↓
first same-cluster closure failure → one bounded repair
second same-cluster closure failure → stop and redesign
    ↓
actual-path verification → affected broad regression → evidence refresh → final freeze
```

## Phase 1 design decisions

### P1-D1. Canonical convergence contract

Create one shared reference that owns:

- Delivery Owner authority;
- child call/return semantics;
- finding classification;
- same-risk-cluster identity;
- circuit rules;
- logical primary-owner continuity;
- architecture reassessment entry and exit;
- behavioral evidence ordering;
- amendment invalidation handback;
- final evidence ordering.

Local skills reference this contract and restate only action-critical boundaries. Do not duplicate the complete rules across every skill.

Proposed path:

`plugins/super-developer/references/orchestration-convergence.md`

### P1-D2. Delivery Owner

For planned-feature execution, `implement` owns progression from the exact accepted Gate-2 artifact commit through readiness.

When invoked by this owner:

- `spike-to-plan` returns evidence; it does not start a fresh autonomous lifecycle;
- `implementation-plan` performs a bounded amendment and returns old/new state plus invalidation scope;
- `review-plan` reviews and returns; it does not invoke `implement`;
- pipeline `review-code` returns classified findings; it does not own a separate fix loop;
- `audit` remains read-only and returns a result.

Standalone modes remain valid and must not accidentally inherit planned-feature continuation authority.

### P1-D3. Minimal child envelope

Every nested planned-feature call carries only:

- caller and `return_to`;
- `create | amend | resume` mode where applicable;
- accepted artifact and code state;
- inherited authorization boundary;
- finite open items;
- serious-cluster/strike context when relevant;
- allowed continuation;
- terminal disposition.

This envelope lives in invocation/return packets, not a registry or ledger.

### P1-D4. Same-risk-cluster circuit

Cluster identity is:

```text
accepted invariant or contract
+ failure mechanism
+ architectural surface
+ verification signature
```

One strike is one failed closure cycle for that cluster, not each duplicate finding or command failure.

- Strike 1: one bounded repair is permitted.
- Strike 2: automatic repair stops; return to focused design reassessment.
- Architecture invalidation: reassessment begins immediately.
- A new agent, prompt, model, status, matrix row, report, or commit does not reset the circuit.
- Reset requires an accepted design/invariant change, decisive new evidence, or demonstrated closure of the original mechanism.
- Continuing after Strike 2 requires explicit user approval.

### P1-D5. Primary implementation continuity

Ownership is logical rather than tied to a model process:

- prefer resuming the same implementation session where the host supports it;
- otherwise rehydrate one explicit successor with accepted invariants, prior attempts, cluster identity, strike state, and worktree state;
- never run concurrent implementation owners for the same package/architectural surface;
- changing owner does not reset the circuit;
- independent verification remains cold.

### P1-D6. Triggered architecture invariants

Upgrade existing Design Preflight rather than adding another universal gate.

For concurrency, shared state, credentials/privacy, cancellation, replay, lifecycle, registration, discovery, publication, or similar risk, require concise accepted invariants covering:

- state authority and every ingress/mutation path;
- legal transitions and forbidden transitions;
- ordering and linearization/publication point;
- winning and losing generation/owner behavior;
- cancellation, abort reentrancy, settlement, and cleanup;
- replay/idempotence;
- default versus injected/provider-specific paths;
- privacy/credential minimization;
- actual-production-path test seams;
- earliest affected broad-regression tripwire.

Persist these invariants in existing SPEC constraints/acceptance criteria, Slice interface contracts where applicable, and package Notes/verification expectations. Do not add an architecture ledger.

### P1-D7. Exact Gate-2 state

Gate 2 approves:

1. the validated artifact candidate; and
2. the sole expected `status → reviewed` mutation.

After the existing checkpoint, the workflow records and verifies the exact resulting artifact SHA. Any other content drift invalidates approval. Implementation must consume that SHA.

No helper modification is required.

### P1-D8. Bounded amendment return

A planned-feature amendment returns:

- old and new accepted artifact SHAs;
- affected requirements/Slices;
- affected packages and assignments;
- affected production/test surfaces;
- stale proofs/reports/evidence/freeze inputs;
- unaffected state that may remain valid;
- old→new package mapping when identity changes.

Full immutable-ID and cross-session resume redesign remains Phase 3.

### P1-D9. Behavior-first verification

Verification order becomes:

1. accepted requirements and architecture invariants;
2. bound production diff and actual execution path;
3. causal tests and observations;
4. implementer proof and self-review;
5. matrix reconciliation.

The matrix indexes evidence after semantic review; it does not define the test implementation.

Behavior-sensitive PASS evidence must show:

- forced production branch and preconditions;
- real collaborator outcome;
- observable ordering/state transition;
- forbidden-outcome falsification;
- a check that would fail if the invariant were broken;
- disclosure of cache hits, mocks, test hooks, and synthetic substitutes.

Labels, counters, row counts, proof language, or cache-hit paths are insufficient by themselves.

### P1-D10. Repair and regression ordering

For serious repair:

1. classify the finding;
2. reproduce the real mechanism;
3. repair one coherent root cause;
4. establish actual-path targeted evidence;
5. run the earliest credible affected broad regression or justified bounded substitute;
6. only then refresh proof/report state;
7. freeze final evidence after behavior and integration are stable.

Shared discovery, registration, global state, lifecycle, generated/public contracts, and recursive control flow trigger an affected broad regression before evidence freeze.

## Phase 1 file map

### Create

- `plugins/super-developer/references/orchestration-convergence.md`

### Modify — ownership and routing

- `plugins/super-developer/skills/implement/SKILL.md`
- `plugins/super-developer/skills/implement/references/package-dispatch.md`
- `plugins/super-developer/skills/implement/references/package-integration-gates.md`
- `plugins/super-developer/skills/implement/references/execution-contract.md`
- `plugins/super-developer/skills/spike-to-plan/SKILL.md`
- `plugins/super-developer/skills/implementation-plan/SKILL.md`
- `plugins/super-developer/skills/review-plan/SKILL.md`
- `plugins/super-developer/skills/review-plan/references/plan-review-resolution.md`
- `plugins/super-developer/skills/review-code/SKILL.md`
- `plugins/super-developer/skills/review-code/references/pipeline-report.md`
- `plugins/super-developer/skills/audit/SKILL.md`

### Modify — planning and invariants

- `plugins/super-developer/skills/implementation-plan/references/design-preflight.md`
- `plugins/super-developer/skills/implementation-plan/references/spec-template.md`
- `plugins/super-developer/skills/implementation-plan/references/planner-agent-contract.md`
- `plugins/super-developer/skills/implementation-plan/references/artifact-authoring.md`
- `plugins/super-developer/skills/implementation-plan/references/validation-checklist.md`
- `plugins/super-developer/skills/review-plan/references/plan-review-rubrics.md`

### Modify — verification and repair

- `plugins/super-developer/references/package-lifecycle.md`
- `plugins/super-developer/references/package-verification-report.md`
- `plugins/super-developer/skills/implement/references/repair-agent-contract.md`
- `plugins/super-developer/skills/implement/references/package-verification.md`
- `plugins/super-developer/skills/audit/references/audit-subagent-contract.md`
- `plugins/super-developer/references/work-packages.md`
- `plugins/super-developer/skills/testing/references/core/generic-testing.md`

### Modify — contract regression coverage and docs

- `plugins/super-developer/assets/tests/test_skill_prompts.py`
- `plugins/super-developer/README.md`
- `CHANGELOG.md`

Do not modify `sliceproof.py` or `semgrep_rules.py` behavior in Phase 1.

## Phase 1 implementation sequence

### Commit 1 — Canonical owner and return contract

- Add the canonical convergence reference.
- Establish `implement` as planned-feature Delivery Owner.
- Convert nested planning/review/audit paths to return-only semantics.
- Define minimal child envelope and terminal dispositions.
- Add exact Gate-2 SHA and amendment handback semantics.
- Add focused contract tests for no child self-advancement.

### Commit 2 — Architecture and accepted-state projection

- Extend triggered Preflight output with architecture invariants.
- Define how accepted invariants project into existing SPEC/Slice/package fields.
- Add plan-review checks for missing authority, transition, publication, losing-owner, cancellation, and actual-path test seams.
- Keep low-risk plans exempt.
- Add contract tests proving the gate remains triggered rather than universal.

### Commit 3 — Finding classifier and design circuit

- Add the post-acceptance classification table and mixed-finding precedence.
- Define serious-cluster identity and Strike 1/Strike 2 behavior.
- Replace the existing prompt-test assertion that forbids count-based serious-failure limits.
- Ensure changed agent/model/commit/status does not reset the cluster.
- Ensure architecture invalidation cannot route to ordinary repair.

### Commit 4 — Behavior-first verification and repair ordering

- Reorder package verifier inputs and procedure.
- Make causal production-path evidence mandatory for behavior-sensitive claims.
- Keep the existing matrix as an evidence index.
- Define logical primary-owner continuity.
- Require actual-path targeted checks and affected broad regression before proof/report refresh and freeze.
- Align review-code and audit with caller-owned repair.

### Commit 5 — Documentation and integrated contract validation

- Update README lifecycle description and CHANGELOG.
- Run prompt-contract tests and repository test suite.
- Run the Phase 1 scenario set below.
- Review the complete diff for duplicated authority and conflicting continuation rules.

## Phase 1 validation scenarios

1. **Nested empirical blocker:** `implement` calls spike/amend/review and receives control back without a second autonomous implementation run.
2. **Architecture invalidation:** a verifier reports a publication-order flaw; no ordinary repair agent is dispatched.
3. **Same-cluster Strike 2:** two failed closures for the same invariant/mechanism stop automatically.
4. **Unrelated finding:** a separate defect does not incorrectly inherit another cluster's strikes.
5. **Owner replacement:** a successor implementation agent receives prior state and cannot reset strikes.
6. **False concurrency test:** a cache-hit test labelled concurrent is rejected as insufficient evidence.
7. **Real pending flight:** evidence forces an unresolved collaborator and observable overlap.
8. **Losing generation:** a losing callback cannot publish after the accepted linearization point.
9. **Recursive discovery:** affected broad regression catches recursion before proof/report freeze.
10. **Public contract tripwire:** focused success cannot bypass an established source/public-contract check.
11. **Gate-2 drift:** unexpected artifact content after approval invalidates the accepted SHA.
12. **Confidence enhancement:** an optional exhaustive combination remains non-blocking without a named risk.

## Phase 1 acceptance criteria

- One canonical owner of planned-feature progression exists.
- Every nested child has explicit caller/return semantics.
- No nested child can restart the parent pipeline when caller context exists.
- Every post-acceptance serious finding is classified before repair.
- Architecture invalidation routes to reassessment, never ordinary repair.
- Strike 2 for the same serious cluster stops automatic repair.
- Logical owner replacement preserves prior attempts and strikes.
- Triggered architecture work has durable, testable invariants in existing artifacts.
- Gate 2 is bound to an exact reviewed artifact SHA.
- Behavior-sensitive PASS evidence demonstrates the real production path.
- Broad affected regression precedes proof/report freeze for named shared-risk surfaces.
- Proof/report refresh happens after behavioral closure.
- Existing safety, evidence-freeze, and independent-verification boundaries remain intact.
- No new helper, ledger, dashboard, universal agent, report, or registry field is added.
- Existing tests pass after deliberately replacing obsolete anti-count circuit expectations.

---

# Phase 2 — Assurance Simplification

## Objective

Reduce clean-path agent, context, and artifact amplification after Phase 1 proves that defect detection and stopping behavior remain sound.

## Planned scope

1. Introduce explicit low, standard, and high assurance selection based on named risk—not file count.
2. Make per-package independent verification conditional for low-risk coherent work.
3. Preserve package verifiers for parallel, sensitive, or independently meaningful boundaries.
4. Consolidate planning plus plan challenge into one user acceptance phase while retaining a cold challenge.
5. Consolidate pipeline final review and audit into one final-verification phase with separate completeness and code-risk lenses; use multiple agents only when risk requires.
6. Remove blocking Gate 1 before read-only plan review.
7. Remove repeated approvals for repairs already inside an accepted execution boundary.
8. Make Slices and sidecars conditional where a narrow Accepted Brief is sufficient.
9. Reduce duplicate closure prose while retaining traceability from accepted outcome to evidence.
10. Establish clean-path call budgets and report actual amplification.

## Phase 2 guardrails

- Do not eliminate cold independent verification.
- Do not weaken security/privacy/safety/data/public-contract escalation.
- Do not use agent count alone to classify risk.
- Do not hide low assurance behind an implicit default.
- Do not remove an artifact until its authority has a clear replacement.

## Phase 2 target metrics

- Narrow feature: approximately 3–4 agent calls.
- Clean four-package feature: no more than approximately 7 calls unless named risk justifies more.
- No reduction in seeded serious-defect detection compared with Phase 1.
- Fewer than 10% false blockers in the scenario set.

---

# Phase 3 — Lifecycle Durability and Release Continuity

## Objective

Make amendment, interruption, evidence retention, final audit, and release operate over exact durable state without rebuilding context from chat.

## Planned scope

1. Define complete `create`, `amend`, `resume`, `park`, `cancel`, and `supersede` semantics.
2. Make package IDs immutable after acceptance; append or map IDs instead of renumbering in-flight work.
3. Reconstruct interrupted package stages from commits, worktrees, proofs, and reports.
4. Prevent concurrent package proof writes from being captured by broad sidecar checkpoints.
5. Checkpoint sidecar state only at quiescent wave boundaries or stage finalized paths.
6. Define one durable final Verification Summary bound to Accepted Brief SHA, code SHA/tree, runtime evidence, unresolved obligations, and final verdict.
7. Resolve the current contradiction between read-only audit output and the requirement to record audit PASS in the artifact root.
8. Add a pipeline-release route that consumes the exact Verification Summary and release-candidate state.
9. Reclassify target drift, merge resolution, and release-time edits before release.
10. Retain an immutable final evidence reference or release-linked equivalent while removing local worktrees normally.
11. Define degraded assurance when the host cannot guarantee cold/fresh/read-only roles.

## Phase 3 guardrails

- Standalone release remains available and clearly distinct from pipeline release.
- No release may imply planned-feature verification when no exact-state receipt exists.
- Cleanup must not destroy the only durable evidence reference.
- Resume must not silently repeat approvals or implementation.
- Durability fields must not become a second semantic completion ledger.

---

# Independent Review Protocol

Independent review is intentionally bounded and does not use the plugin's review pipeline.

## Design review

Run once before source edits:

- one read-only reviewer receives this plan, the baseline, and v1.39 source;
- it may report only architecture invalidations, concrete omissions, or disproportionate scope;
- the parent classifies findings and updates this plan directly;
- no recursive reviewer satisfaction loop is allowed.

## Phase review

At the end of each phase:

- one cold reviewer inspects the complete phase diff against that phase's acceptance criteria;
- one additional specialist is allowed only for a named sensitive risk;
- serious findings receive one bounded correction;
- a second failure in the same cluster stops the phase for redesign;
- suggestions remain non-blocking and are recorded separately.

## Final program review

After Phase 3:

- replay the complete scenario suite;
- compare agent/turn amplification against v1.39;
- verify release and interruption drills;
- verify public documentation matches actual host-contingent guarantees;
- do not claim a tenfold improvement without observed metrics.

---

# Execution Preconditions

Before Phase 1 source edits:

- [ ] User approves this bootstrap plan and Phase 1 scope.
- [ ] Choose an isolated feature branch/worktree based on current `main`.
- [ ] Decide whether to remove the empty aborted `artifacts/pipeline-convergence-hardening` sidecar or use a different namespace.
- [ ] Confirm the baseline Markdown remains available to the feature worktree.
- [ ] Record the exact base SHA.
- [ ] Run the existing prompt-contract test suite as a baseline.
- [ ] Record any existing failures before modifications.

No remote push, target merge, cleanup, release, or publication is implied by plan approval.

---

# Stop Conditions

Stop implementation and return to the user when:

- a proposed fix requires a new product/workflow behavior not settled by the baseline or this plan;
- a Phase 1 change begins implementing Phase 2/3 scope without necessity;
- the same serious cluster fails twice;
- independent review identifies architecture invalidation;
- existing safety or exact-state protections would be weakened;
- a new helper, ledger, report, agent layer, or schema is required to make the design work;
- test evidence cannot force the claimed orchestration path;
- source state drifts from the recorded implementation base;
- unrelated active worktrees or user changes would be affected.

---

# Recommended Next Action

Approve this bootstrap plan for **Phase 1 only**. After approval:

1. remove or retain the empty aborted sidecar according to the user's explicit choice;
2. create one isolated Phase 1 feature worktree directly from current `main`;
3. capture baseline test results;
4. implement the five Phase 1 commits serially;
5. run the bounded independent review and scenario suite;
6. present the Phase 1 diff and observed metrics before any merge or Phase 2 work.
