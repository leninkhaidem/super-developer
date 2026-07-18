# Super Developer Pipeline Orchestration Baseline

**Status:** Analysis baseline; input to a future pipeline amendment, not an accepted design or implementation plan
**Assessed version:** `super-developer` v1.39.0 (`df7396f`)
**Date:** 2026-07-18
**Scope:** Planned-feature orchestration, architecture planning, implementation delegation, verification, repair, final readiness, and release continuity

## Purpose

This document records the current pipeline's strengths, observed repair-loop failure modes, systemic gaps, and recommended direction. It combines:

1. a static read-only review of the v1.39.0 plugin skills, references, artifact contracts, and prompt tests;
2. two agent reports from separate feature implementations that experienced repeated fix/repair/verification cycles; and
3. an adversarial synthesis of orchestration, evidence quality, context handoff, lifecycle, and simplification concerns.

The two implementation reports are qualitative field evidence supplied by the user. Their exact executions, branches, prompts, and test artifacts were not independently replayed during this assessment. Specific implementation details from those reports should therefore be treated as reported observations, while repeated patterns across both reports are stronger evidence of a pipeline-calibration problem.

This baseline intentionally does **not** propose new scripts, helper programs, ledgers, dashboards, or agent layers. The first amendments should simplify and clarify prompt-level ownership, routing, evidence, and stop semantics.

---

## Executive Conclusion

The pipeline is effective at **detecting defects and preventing premature release**, but it is less effective at **preventing architectural mistakes and terminating expensive repair cycles**.

The primary failure is not generic sub-agent incompetence. It is:

> **Assurance recursion without one accountable end-to-end delivery owner, combined with late architecture discovery and evidence contracts that can reward checklist completion over behavioral truth.**

The current pipeline has strong local controls:

- independent verification catches real privacy, concurrency, replay, and integration defects;
- worktree, scope, and release boundaries prevent unsafe shipping;
- proof and state bindings preserve useful traceability;
- v1.39 adds semantic freshness, an evidence freeze, triggered specialists, and narrower rerun routing;
- unchanged command retries and obvious no-progress repair are explicitly prohibited.

However, the overall lifecycle can still behave as follows:

1. planning omits or underspecifies an architectural invariant;
2. a broad implementation agent changes architecture, tests, and proof together;
3. focused tests and matrix rows appear clean;
4. a verifier discovers either another architectural contradiction or a test-fidelity gap;
5. a fresh repair agent layers a bounded patch over the same design;
6. proof/report freshness expands the closure work;
7. focused checks pass while a broader regression or production-path contradiction remains;
8. final or full-suite verification finds the structural defect late;
9. the process returns to repair instead of design reassessment;
10. each changed patch technically counts as progress, so the circuit remains active.

The pipeline is therefore **good at rejection but poorly calibrated for convergence** on complex cross-layer work.

---

## Evidence From the Two Reported Implementations

### Reported planning and architecture omissions

The first implementation report stated that the original plan did not precisely define:

- all credential-authority ingress paths;
- model-registration ordering during overlapping callbacks;
- active-turn publication mechanics;
- real pending coordinator-flight behavior.

These are not minor coding details. They are authority, ordering, state-transition, and linearization invariants. Their late discovery indicates that the plan described outcomes and generations without making the governing state model sufficiently executable by implementation agents.

### Reported evidence and test-fidelity problems

Both reports described agents optimizing for:

- expected matrix rows;
- named outcomes or counters;
- passing focused tests;
- proof language that looked complete.

The resulting tests sometimes used cache-hit or synthetic paths while being described as concurrency, timeout, partial-mutation, or lifecycle evidence. A label such as `timeout`, `partial`, or `concurrent` did not prove that the real production branch produced that outcome.

### Reported repair-packet overload

The first report said agents were asked to change architecture, add extensive tests, update proof, and run all gates in one assignment. This combined several different reasoning problems:

- authority architecture;
- provider registration sequencing;
- coordinator-flight behavior;
- production-path test design;
- proof maintenance.

That breadth makes it difficult for one bounded sub-agent to preserve causal understanding and independently challenge its own tests.

### Reported late integration signal

One repair reportedly passed 374 focused tests but failed the full suite because it:

- recursively re-entered model discovery; and
- violated an existing source-contract tripwire.

This demonstrates that focused success was real but insufficient. The missing signal was not merely another matrix row; it was earlier impact analysis and an appropriately timed broad regression boundary.

### Reported circuit-breaker failure

Both reports concluded that architectural reassessment should have happened after the second serious verification failure. The current circuit rules detect unchanged work and obvious no-progress, but a sequence of materially different yet architecturally misdirected patches can continue to look like progress.

### Attribution

| Contributor | Assessment | Why |
|---|---|---|
| Planning and architecture definition | **Primary** | Critical authority, ordering, publication, and flight invariants were underspecified. |
| Global orchestration and repair routing | **Primary** | The pipeline continued patch repair after evidence indicated design-level invalidation. |
| Verification calibration | **Major** | Literal matrix closure and focused checks encouraged evidence-shaped implementation. |
| Integration-test placement | **Major** | Broad regressions surfaced structural impact after substantial proof and repair work. |
| Sub-agent capability | **Contributing** | Complex async/concurrency, default/injected branches, and large harnesses exceed reliable single-session breadth. |
| Generic sub-agent incompetence | **Not supported** | Agents produced working code and tests, while independent agents found real defects; the recurring issue was task topology and authority. |

---

## Current Strengths to Preserve

### S1. Safety and side-effect boundaries

Preserve:

- root-worktree protection;
- isolated package and integration worktrees;
- explicit approval for target merge, push, destructive operations, credentials, and external side effects;
- path and symlink validation;
- bounded commands, termination, and cleanup requirements.

### S2. Independent verification

Independent review caught defects that implementers and their focused tests missed. Independence should remain at genuine assurance boundaries even if the number of routine agents is reduced.

### S3. v1.39 semantic freshness

`plugins/super-developer/references/package-lifecycle.md` now distinguishes:

- metadata-only drift;
- evidence-only drift;
- bounded semantic change;
- material, shared, sensitive, or uncertain change.

This is preferable to rerunning every gate after every commit. It should be elevated into the global lifecycle rather than replaced.

### S4. Final evidence freeze

Freezing integrated code, artifacts, and runtime evidence before final checks is a sound invariant. Generated review and audit outputs correctly remain outside the frozen inputs.

### S5. Triggered rather than universal specialist review

Security, privacy, data, concurrency, public-contract, and similar specialists should remain risk-triggered.

### S6. Existing result vocabulary

The package matrix already distinguishes `delivered`, `missing`, `partial`, `contradicted`, and `unverified`. Adding more result labels is not the priority. The missing piece is reliable classification and behavioral evidence behind those labels.

---

## Systemic Findings

## F-01 — No durable end-to-end delivery owner or call/return contract

**Priority:** P0
**Effect:** Duplicate execution, lost repair state, repeated approval, cross-skill re-entry

`implement` can route an empirical blocker through:

```text
implement -> spike-to-plan -> implementation-plan -> review-plan -> implement
```

Each child skill has local ownership rules, but the lifecycle has no durable paused caller, return stage, inherited authorization, or active unresolved-item set. `review-plan` may invoke `implement` after Gate 2 when implementation was already authorized, creating a new execution path rather than returning to the paused one.

Repair ownership is also divided between `implement` and pipeline `review-code`, each with repair and verification behavior.

### Required direction

Designate one **Delivery Owner** for an accepted feature. Every child invocation receives and returns:

- `caller` and exact `return_to` stage;
- `mode: create | amend | resume`;
- accepted scope and inherited authorization;
- exact artifact/code state identity;
- finite unresolved-item set;
- permitted continuation;
- terminal disposition: `done | blocked | needs-decision | parked`.

A child may perform its bounded role but must never advance, restart, or recursively own the parent lifecycle.

---

## F-02 — The accepted requirement baseline is transformed rather than independently preserved

**Priority:** P0
**Effect:** Downstream artifacts can be internally consistent while omitting an original requirement

Direct user requirements are sent to the planner, which rewrites them as `REQ-*`, `AC-*`, constraints, and package artifacts. Plan reviewers and later verifiers primarily consume the transformed files. Mandatory package matrix rows come from assigned Slice H3 IDs, `VE-*` expectations, and triggered risks—not every feature-level `REQ-*` or `AC-*`.

A planner omission can therefore disappear before the first independent review and remain invisible because all downstream evidence agrees with the omission.

Gate 2 marks registry state as `reviewed` and checkpoints the sidecar, but implementation does not explicitly require the exact reviewed sidecar commit as its semantic authority.

### Required direction

Use the existing `SPEC.md` as an **Accepted Brief**, not merely planner-authored output:

- preserve a sanitized, lossless source baseline;
- assign stable requirement and acceptance IDs;
- map every accepted outcome to a package, integration/release responsibility, named external owner, or approved exclusion;
- bind Gate 2 approval to the exact artifact-sidecar commit;
- require implementation to consume that reviewed commit;
- version amendments and return an invalidation map for affected packages/evidence.

Do not add a second requirements ledger.

---

## F-03 — Design Preflight exists, but it does not guarantee an executable architecture invariant contract

**Priority:** P0 for concurrency, shared state, credentials, lifecycle, and replay work
**Effect:** Architectural defects surface during verification rather than before implementation

The current Design Preflight already triggers for concurrency, privacy, security, persistence, rollback, and cross-cutting work. Therefore the right response is **not another universal architecture gate**.

The gap is that Preflight:

- returns bounded, ephemeral recommendations and gaps;
- does not require a state-transition or authority model;
- does not require mutation/linearization/publication points;
- does not require forbidden transitions or losing-generation behavior;
- does not require actual-path test seams for the invariants;
- explicitly avoids persisting architecture rationale unless promoted to a requirement, constraint, or scope decision.

For high-risk stateful work, accepted architectural reasoning can therefore disappear before package agents read the plan cold.

### Required direction

Upgrade triggered Design Preflight into an **Architecture and Invariant Challenge** using existing artifact surfaces. When applicable, it must settle and persist concise answers for:

- authoritative owner of each mutable state;
- all ingress and mutation paths;
- state machine and legal transitions;
- ordering and linearization/publication point;
- compare-and-swap, generation, lease, or ownership rule;
- cancellation, abort reentrancy, settlement, and cleanup;
- replay/idempotence behavior;
- default versus injected/provider-specific branches;
- privacy and credential minimization boundaries;
- forbidden behavior and losing-race behavior;
- test seams that can force the real production path;
- earliest integration tripwire for architectural regressions.

Persist accepted invariants in existing `SPEC.md` constraints/acceptance criteria, package Notes and verification expectations, or Slice interface contracts. Do not create a separate architecture ledger.

---

## F-04 — Verification requirements can encourage evidence theater

**Priority:** P0
**Effect:** Agents optimize for matrix closure instead of proving production behavior

The deliverable matrix is useful for coverage and traceability, but its mechanically strict row shape, stable IDs, copy-safe wording, and mandatory `delivered` state can become the agent's optimization target.

The current contract correctly states that a syntactically valid but dishonest `complete:` claim remains possible and must be rejected semantically. The field reports show the practical version of this risk: tests and counters were named after outcomes without exercising the real collaborator, ordering, timeout, or lifecycle branch.

### Required direction

Treat the matrix as an **index to behavioral evidence**, not a test-design target.

For behavior-sensitive rows, PASS evidence must show:

1. the intended production branch was reachable and forced;
2. the relevant collaborator genuinely resolved, rejected, timed out, partially mutated, cancelled, or remained uncertain;
3. preconditions and controlled ordering were observable;
4. the expected state transition or externally observable effect occurred;
5. forbidden state transitions or publications did not occur;
6. the test would fail if the claimed invariant were broken;
7. cache-hit, mock-only, bypass, synthetic counter, or test-only hook behavior is disclosed and cannot substitute for the production path.

A row count, scenario label, counter name, or proof sentence is never evidence by itself.

For complex lifecycle and concurrency behavior, prefer a small state model plus explicit invariants and risk-based transition coverage. Use model-based tests or covering arrays only when the state space justifies them; do not replace one universal Cartesian matrix with another universal testing ceremony.

---

## F-05 — The verification rubric is not sufficiently frozen or typed after plan acceptance

**Priority:** P0
**Effect:** Fresh reviewers can expand closure obligations during every round

Fresh verifiers must remain free to discover genuine defects. However, the pipeline needs to distinguish a newly discovered defect from a newly desired confidence improvement.

Without a stable classification, a fresh reviewer can reinterpret evidence expectations, add risk rows, or demand broader combinations. Repair agents then optimize toward the expanded rubric, and the accepted definition of completion moves during implementation.

### Required direction

Freeze the accepted requirements, invariants, and named risk hypotheses at Gate 2. Every post-acceptance finding must be classified before repair:

| Finding class | Pipeline action |
|---|---|
| `requirement-gap` | Stop for Accepted Brief amendment and user authority where semantics/scope change. |
| `architecture-invalidation` | Stop patch repair; return to focused architecture/design review and invalidate affected assignments. |
| `implementation-defect` | Route one bounded behavioral repair to the Delivery Owner. |
| `integration-regression` | Repair with explicit affected-surface and broad-regression routing. |
| `test-fidelity-gap` | Repair the test/evidence seam; change production only when the gap exposes a real product defect. |
| `evidence-stale-or-contradicted` | Refresh or re-run the smallest affected evidence route; never redesign from metadata. |
| `confidence-enhancement` | Non-blocking by default; promote only through explicit risk-based authority. |

A verifier may always block a concrete security, privacy, safety, data, correctness, contract, or demonstrated regression defect. Rubric freeze must not suppress emergent truth; it prevents optional confidence expansion from silently becoming mandatory scope.

---

## F-06 — The repair circuit detects unchanged work but not repeated design-level failure

**Priority:** P0
**Effect:** Different patches can keep the circuit alive without converging

Current rules open the circuit for unchanged work, uncertain cleanup, invalid readiness, or no material progress. This is valuable but insufficient.

A repair can change code, tests, evidence, and commit identity while leaving the same architectural risk unresolved. Such a patch technically creates a material delta, allowing another round even though design-level progress is absent.

### Required direction

Elevate circuit identity from an individual command/finding to a **serious risk cluster**:

```text
accepted invariant or contract
+ failure mechanism
+ affected architectural surface
+ observed verification signature
```

Use the following default policy:

- first serious failure: one bounded repair after classification;
- second serious failure in the same risk cluster: automatically stop repair and enter design reassessment;
- any confirmed `architecture-invalidation`: enter design reassessment immediately;
- continuing beyond the stop requires explicit human approval with cost, reason, and new information;
- evidence growth, a new agent, a new prompt, a renamed attempt, or a changed commit does not reset the circuit;
- reset requires a changed accepted invariant/design, decisive new external evidence, or a repair that demonstrably narrows the unresolved mechanism.

The two-round threshold is a default for serious same-cluster failures, not a universal cap on unrelated defects.

---

## F-07 — Repair assignments combine too many responsibilities and too many implementation owners

**Priority:** P1
**Effect:** Cross-layer overload, patch layering, and correlated proof claims

Current repair contracts can require the worker to:

- reproduce the failure;
- reason about Slice and package scope;
- change production behavior;
- modify tests;
- update proof rows;
- run targeted checks;
- perform self-review;
- classify freshness impact.

For a narrow defect this is coherent. For an architectural concurrency or lifecycle failure it is too broad.

The current workflow also prefers fresh repair agents. Freshness can improve independence, but repeatedly assigning different implementers to the same architectural surface encourages patch layering and loses design context.

### Required direction

- Keep one **primary implementation owner per architectural surface** while a repair remains within the accepted design.
- Use fresh agents for independent diagnosis and verification, not automatically for every implementation patch.
- If the primary owner fails the same serious cluster twice, stop for redesign or intentional owner escalation rather than layering another patch.
- Give each repair one root cause/risk class and one coherent code/test boundary.
- Separate architecture reassessment from production repair.
- Stabilize behavior and targeted tests before proof/report refresh; do not make proof wording part of the architecture-solving assignment.
- Refresh only affected proof/report state after behavioral closure.

This is a sequencing simplification, not a proposal to add more agents.

---

## F-08 — Broad regression evidence arrives too late

**Priority:** P1
**Effect:** Focused checks pass while integration recursion or existing contracts fail

Focused checks are necessary for fast repair feedback. They are insufficient when changes affect discovery, registration, caches, shared state, public contracts, lifecycle, or recursive control flow.

The reported 374-passing-tests/full-suite-failure incident shows that the first broad regression boundary occurred after too much implementation and evidence investment.

### Required direction

Use four semantic gates, without creating four new artifacts:

1. **Architecture and invariants:** before implementation for triggered risk.
2. **Core production behavior:** real-path targeted checks before evidence expansion.
3. **Test fidelity and affected integration:** verify the tests force the claimed branch and run the earliest credible affected broad regression.
4. **Frozen final state:** final independent verification and release readiness.

For repository-wide or expensive suites, testing authority should identify the earliest credible broad command or a justified bounded substitute. Broad regression should run before final proof/report freeze whenever the affected surface includes shared discovery, registration, public API, generated contracts, global state, or lifecycle control flow.

---

## F-09 — The assurance topology remains fixed-cost for low-risk work

**Priority:** P1
**Effect:** Excessive agents, repeated context hydration, and disproportionate artifact work

A clean four-package feature implies approximately:

- one planner;
- one plan reviewer;
- four implementers;
- four package verifiers;
- one final code reviewer;
- one final auditor.

This is roughly 12 sub-agent calls before optional Preflight, security review, specialists, or repair. v1.39 narrows rereview scope but does not materially reduce the default call topology.

### Required direction

Adopt risk-adaptive assurance:

| Change profile | Default topology |
|---|---|
| Narrow, low-risk, one coherent state boundary | Delivery Owner plus one cold final verifier |
| Parallel or medium-risk packages | Package workers; package verification only at meaningful independent boundaries |
| Sensitive, cross-package, concurrency/data/privacy/public-contract work | Full package verification, triggered specialists, and final independent checks |

Agent count is not a quality metric. Each invocation should add independent information, preserve coherent ownership, or enforce a real safety boundary.

---

## F-10 — Resume, amendment, package identity, and sidecar concurrency are incomplete

**Priority:** P1
**Effect:** Duplicate dispatch, orphaned work, and partial evidence checkpoints

Observed static gaps include:

- normal interrupted `in_progress` packages lack a complete semantic resume route;
- empirical findings return through a planning skill described as creating fresh artifacts;
- package IDs may be renumbered after split, merge, or reorder;
- parallel package agents write proof files into one shared artifact worktree;
- sidecar checkpoints use `git add -A`, which can capture another package's partial proof.

### Required direction

- Define `create`, `amend`, `resume`, `park`, `cancel`, and `supersede` semantics.
- Reconstruct resume stage from existing commits, proofs, reports, and worktrees instead of restarting.
- Make package IDs immutable after Gate 2; append new IDs rather than renumbering.
- Checkpoint sidecar evidence only at quiescent wave boundaries or stage finalized package paths.
- Treat approved deferral as an Accepted Brief/assignment amendment, not a completed mandatory proof row.

---

## F-11 — Final audit and release continuity are not durably closed

**Priority:** P1
**Effect:** Verified state can be released without a durable same-state receipt

The release workflow verifies git, version, changelog, tag, GitHub, and cleanup state but does not require planned-feature review/audit receipts for the exact release candidate.

Audit is read-only and returns a structured report, while package integration guidance expects final audit PASS to be recorded in the artifact root. No canonical durable audit receipt comparable to `review-code-state.json` is clearly defined. Release then defaults to removing local and remote artifact-sidecar state after target synchronization.

### Required direction

Keep standalone release behavior, but define a pipeline-release route that consumes:

- Accepted Brief artifact commit;
- verified feature/release-candidate commit;
- final verification/audit disposition bound to both;
- outstanding external or rollout obligations;
- impact classification for release-time edits and target drift.

Retain the final remote evidence reference by default for pipeline releases, or bind an equivalent immutable reference into the release. Removing local worktrees can remain the default.

---

## F-12 — Prompt tests validate wording, not lifecycle behavior

**Priority:** P2
**Effect:** Credibility claims exceed observed orchestration evidence

The prompt test suite usefully checks that contracts contain required phrases and references. It does not demonstrate:

- loop termination;
- interruption recovery;
- false-PASS resistance;
- behavior-versus-label test fidelity;
- concurrent sidecar safety;
- agent/turn amplification;
- host enforcement of fresh, cold, read-only, or model-specific roles.

### Required direction

Before claiming measured improvement, replay a bounded set of adversarial workflow scenarios and record outcomes. This baseline does not require a new test harness or script; initial evaluation can use controlled dry runs and existing session evidence.

---

## Target Operating Model

### One owner

A single Delivery Owner retains:

- accepted scope and requirements;
- lifecycle call stack;
- implementation authority;
- active risk clusters and circuit state;
- repair routing;
- artifact/code bindings;
- final outcome and release handoff.

Sub-agents perform bounded work and return. They do not own pipeline continuation.

### Two authoritative lifecycle records

Reuse and consolidate current artifacts around:

1. **Accepted Brief** — approved requirements, invariants, exclusions, outcome ownership, version, and reviewed artifact commit.
2. **Verification Summary** — exact brief version, code state, behavioral evidence, unresolved items, independent verdict, and release disposition.

Package assignments, proofs, and reports remain conditional subordinate evidence for complex or parallel work, not peer sources of product truth.

### One global progress invariant

> A stage may repeat only when executable state, external evidence, or an explicit user decision changed and closed or narrowed a named finite item.

The following are not progress by themselves:

- a different agent or model;
- more tokens or a rewritten prompt;
- a renamed attempt;
- status/report metadata;
- another matrix row;
- a new commit with the same failure mechanism;
- refreshed proof over unchanged behavioral evidence.

### One finding classifier before repair

No finding enters a repair loop before being classified as requirement, architecture, implementation, integration, test fidelity, stale/contradicted evidence, or confidence enhancement.

### Adaptive verification

- Requirements-first independent review before consuming implementer conclusions.
- Reconcile proof and self-review only after inspecting accepted behavior and the bound diff.
- Keep package-local verification for risky or parallel boundaries.
- Keep specialists conditional.
- Use one final verification phase with distinct completeness and code-risk lenses; separate independent agents are conditional on assurance level rather than universally required.

---

## Recommended Remove / Merge / Retain Decisions

| Action | Recommendation |
|---|---|
| Remove | Blocking Gate 1 before read-only plan review; unchanged redispatches; repeated in-scope repair approvals; universal low-risk package verification; proof expansion before behavioral closure; default deletion of final remote pipeline evidence. |
| Merge | Planning and plan challenge into one phase; pipeline code review and audit into one final-verification phase with distinct lenses; all repair routing under the Delivery Owner. |
| Make conditional | Slices, package worktrees, package verifiers, specialists, Skeptics, Semgrep, model-based tests, and parallel final checks. |
| Retain | Root-worktree protection; path/symlink safety; exact SHA/diff/evidence freeze; bounded commands; explicit remote/destructive approvals; cold verification; sensitive-risk escalation. |

---

## Minimum High-Leverage Amendment Set

The smallest amendment likely to prevent the reported failure pattern is:

1. establish the Delivery Owner and universal child return contract;
2. make triggered Preflight produce durable architecture invariants through existing artifacts;
3. classify every post-acceptance finding before repair;
4. require actual-production-path evidence for behavior-sensitive matrix rows;
5. stop after the second serious failure in the same risk cluster and return to design reassessment;
6. keep one primary implementation owner per architectural surface;
7. run the earliest credible affected broad regression before proof/report freeze;
8. bind final verification and pipeline release to the exact accepted brief and code state.

This set addresses the reported loop without adding another universal agent, gate, report, or script.

---

## Likely Prompt and Reference Amendment Surfaces

This is not a file-by-file implementation plan. The likely semantic amendment surfaces are:

- `plugins/super-developer/skills/implementation-plan/references/design-preflight.md`
- `plugins/super-developer/skills/implementation-plan/references/spec-template.md`
- `plugins/super-developer/skills/implementation-plan/references/artifact-authoring.md`
- `plugins/super-developer/skills/implementation-plan/references/validation-checklist.md`
- `plugins/super-developer/skills/review-plan/SKILL.md`
- `plugins/super-developer/skills/review-plan/references/plan-review-rubrics.md`
- `plugins/super-developer/skills/review-plan/references/plan-review-resolution.md`
- `plugins/super-developer/skills/implement/SKILL.md`
- `plugins/super-developer/skills/implement/references/execution-contract.md`
- `plugins/super-developer/skills/implement/references/package-dispatch.md`
- `plugins/super-developer/skills/implement/references/repair-agent-contract.md`
- `plugins/super-developer/skills/implement/references/package-verification.md`
- `plugins/super-developer/skills/implement/references/package-integration-gates.md`
- `plugins/super-developer/references/package-lifecycle.md`
- `plugins/super-developer/references/package-verification-report.md`
- `plugins/super-developer/skills/review-code/SKILL.md`
- `plugins/super-developer/skills/review-code/references/pipeline-report.md`
- `plugins/super-developer/skills/audit/SKILL.md`
- `plugins/super-developer/skills/audit/references/audit-subagent-contract.md`
- `plugins/super-developer/skills/release/SKILL.md`
- `plugins/super-developer/skills/release/references/release-contract.md`

Changes should first remove contradictions and duplicate ownership. Avoid scattering the same new rule into every file without one canonical owner reference.

---

## Evaluation Scenarios for a Future Amendment

Use these scenarios to test the amended contracts before broad adoption:

1. **Overlapping provider callbacks:** losing callback must never publish or register after the active generation changes.
2. **Credential-authority ingress:** every default and injected provider path uses the accepted authority and exposes no unauthorized credential surface.
3. **Active-turn publication:** adoption occurs only at the accepted linearization/CAS point.
4. **Pending coordinator flight:** the test must create a real pending flight, not a cache hit or synthetic counter.
5. **Abort reentrancy:** cancellation during callback settlement cannot republish, recurse, or leak ownership.
6. **False concurrency evidence:** seed a test labeled concurrent that never overlaps operations; verification must reject it.
7. **Recursive discovery regression:** focused behavior passes while broad discovery recurses; affected integration gate must catch it before final freeze.
8. **Existing public/source contract tripwire:** package-local success cannot bypass an established contract test.
9. **Second same-cluster failure:** the pipeline must stop repair and return to architecture reassessment.
10. **Interrupted `in_progress` package:** resume must continue from durable state without recreating work or approval.
11. **Parallel proof write:** a sidecar checkpoint must not capture another worker's partial proof.
12. **Release drift:** target or release-time edits must invalidate only the affected verification scope and cannot bypass exact-state readiness.

---

## Success Targets

These are proposed targets, not measured current results:

- zero unchanged or same-signature redispatches;
- automatic design reassessment by the second serious same-cluster verification failure;
- 100% of post-acceptance findings classified before repair;
- 100% of accepted requirements mapped to evidence, approved exclusion, integration/release responsibility, or named external owner;
- 100% of behavior-sensitive PASS claims backed by real-path causal evidence;
- simple feature flow limited to approximately 3–4 agent calls;
- clean four-package flow limited to no more than approximately 7 calls unless risk triggers justify more;
- 100% of interruption drills resumable from durable state without hidden chat;
- 100% of pipeline releases bound to the accepted artifact and verified code state;
- all seeded blockers detected and at least 90% of seeded material defects detected, with fewer than 10% false blockers;
- no evidence or matrix growth after a circuit opens unless design authority explicitly reopens the work.

Agent count is a cost signal, not a quality goal. A higher count is justified when it adds independent information for a named risk.

---

## Tradeoffs and Guardrails

### Hard circuit limits can stop recoverable work

Mitigation: apply the two-round default only to serious failures in the same risk cluster. Permit explicit human continuation when new evidence or a changed design justifies it.

### A primary implementer can become anchored

Mitigation: retain a cold independent verifier and use a fresh diagnostic challenger for design reassessment. Do not confuse implementation coherence with self-approval.

### Rubric freeze can hide emergent defects if interpreted rigidly

Mitigation: concrete security, privacy, safety, data, correctness, public-contract, and demonstrated regression defects always remain blocking. Freeze optional confidence expansion, not truth.

### Architecture review can become another ceremony

Mitigation: trigger it only for named risk surfaces and persist its output in existing artifacts. Narrow, mechanical work should skip it.

### Reducing matrices can weaken traceability

Mitigation: retain a compact outcome-to-evidence index while rejecting row counts and labels as proof.

### Earlier broad tests can be costly

Mitigation: use repository testing authority to select the earliest credible affected broad regression, with a justified bounded substitute where a full suite is disproportionate.

### Retaining artifact evidence can create remote clutter or privacy concerns

Mitigation: retain only the final immutable pipeline evidence reference under an explicit retention policy; remove worktrees and intermediate branches normally.

---

## Open Decisions for Planning

1. Should two serious failures in one risk cluster be the universal default, or should the Execution Contract choose one or two based on risk?
2. Should one final verifier own both completeness and code-risk lenses by default, with a second agent only for sensitive work?
3. Which current artifact should become the canonical Verification Summary: an expanded review-code state, a durable audit receipt, or a consolidated replacement?
4. Should pipeline release retain `origin/artifacts/<feature>` indefinitely, for a defined retention window, or through an immutable release-linked ref?
5. Which feature characteristics promote low-risk work into package-level independent verification?
6. How should a session-host that cannot guarantee cold/fresh/read-only roles report degraded assurance?

These decisions should be resolved before converting this baseline into a Slice-first implementation plan.

---

## Final Recommendation

Do not respond to the reported repair loops by adding another reviewer, another matrix, or more proof fields.

Amend the pipeline around four governing ideas:

1. **one accountable Delivery Owner with explicit call/return;**
2. **architecture invariants settled before complex implementation;**
3. **behavior-first evidence and typed post-acceptance findings;**
4. **a hard design-reassessment circuit after repeated serious failure.**

The pipeline's defect-detection strengths should remain. The goal is to move discovery earlier, make evidence causal, preserve implementation coherence, and stop confidently when the accepted design—not merely the latest patch—has failed.
