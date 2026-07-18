# Agentic Delivery Harness Implementation Plan

- **Status:** Candidate for cold plan challenge; not implementation authorization
- **Date:** 2026-07-18
- **Accepted design:** `docs/superpowers/specs/2026-07-18-agentic-delivery-harness-north-star.md`
- **Accepted semantic design commit:** `1fdebf33af509061ae593796e532dcc4b1a93a9e`
- **Accepted metadata/design branch base:** `b0e66e5`
- **Phase 1 safety checkpoint under reconciliation:** `790bf679466b3738e422b3eb23a951a92a239a6f`
- **Original product baseline:** v1.39.0 at `df7396f677c026cd8bfdf2d0e9baca29e5a03791`

## Objective

Implement the accepted north-star as a frictionless planned-feature harness:

1. requirements, architecture, feasibility, prerequisites, and verification seams are challenged before code;
2. the user receives one formal implementation authorization;
3. one Delivery Owner then auto-resolves ordinary work within that authority;
4. assurance is proportional and non-duplicative;
5. repair is root-cause-batched and deterministically bounded;
6. the mandatory sidecar remains portable across systems;
7. final completion is exact, independently verified, and durable.

The amendment is complete only when the fixed behavioral corpus demonstrates earlier upstream detection, zero
escaped seeded serious defects, one clean-path implementation gate, bounded repair, and no assurance regression.

## Independent Amendment Method

The plugin does not orchestrate its own amendment. One parent owner uses this conventional feature worktree,
ordinary commits, repository tests, and cold read-only reviewers. Do not create amendment `.tasks/`, proof/report
sidecars, dashboards, event ledgers, or a second orchestration service.

After this plan receives cold acceptance, present one implementation authorization. During execution, pause only
for a product/design change, new protected side effect, unsafe state, or the accepted stopping rule. Phase reviews
are autonomous quality checks, not new user gates.

## Simplicity Budget

The implementation may add only:

- one shared `assurance-routing.md` reference to avoid duplicating the profile/receipt graph;
- one compact per-feature `.tasks/<feature>/lifecycle-state.json` current snapshot;
- profile/freeze-scoped final receipt files already required by the accepted graph;
- one bounded scenario manifest and its tests;
- extensions to existing `sliceproof.py`; no new runtime script.

Do not add a service, daemon, database, distributed-lock library, event log, dashboard, graph engine, scheduler,
receipt registry, or timing gate. Git commits/refs provide history and portability. The helper validates files and
digests; it does not become an orchestrator. Any proposed addition outside this list requires redesign review.

## Baseline and Current State

- Source contracts are Phase 1 state at `790bf67`; later commits are design/plan documentation only.
- Full asset test baseline: **117 tests passing**.
- Existing affected hard-cap files at or near 150 lines must be rewritten/trimmed, not appended:
  `implementation-plan/SKILL.md`, `review-code/SKILL.md`, `package-lifecycle.md`,
  `slice-first-artifacts.md`, and `feature-package-workflow.md`.
- The untouched pre-existing `code-doc/SKILL.md` cap violation remains outside scope.
- Existing sidecar creation, root separation, Slice authority, Delivery Owner, child return envelopes,
  architecture-invariant projection, behavior-first verification, and affected-regression ordering are reusable.

## Canonical Ownership

| Contract | Canonical owner | Notes |
|---|---|---|
| Human envelope, technical-plan amendment, one gate, interruption, clusters/budgets | `references/orchestration-convergence.md` | Rewrite compactly; children point here |
| Sidecar-only authority, portability permission, lifecycle snapshot, checkpoint semantics | `references/artifact-store.md` | Remove current-root planned mode |
| Profile/routing and `B → F → C/R/S/U → V` | new `references/assurance-routing.md` | One new shared reference, ≤150 lines |
| Artifact/schema roles | `references/slice-first-artifacts.md` | Registry remains bookkeeping |
| Package stable candidate, proof/report freshness, dependency unlock | `references/package-lifecycle.md` | Do not duplicate profile graph |
| Git/worktree/checkpoint commands | `worktree/references/feature-package-workflow.md` | Ordinary non-force Git only |
| Deterministic validation | `assets/sliceproof.py` | Validation/digest emission only |
| Final code-risk receipt | `review-code` pipeline contract | Never repairs or advances lifecycle |
| Completion receipt | `audit` contract | Read-only and serial after code review where required |
| Final summary and notification | Delivery Owner contract | Summary indexes receipts; does not prove behavior |

## Minimal Artifact Changes

### `SPEC.md`

Add concise authoritative sections:

- `## Human Authorization Envelope`
- `## Technical Plan Baseline`
- `## Design and Feasibility Preflight`
- `## Assurance Profile`
- `## Execution Readiness and Auto-Resolve`

Existing requirements, invariants, Slices, packages, and verification expectations remain; do not duplicate them.

### `tasks.json`

Add only:

- top-level `assurance_profile: low | standard | high`;
- package `verification_mode: boundary | final`;
- package `report_path`: required safe path for `boundary`, `null` for `final`.

Lifecycle and receipt paths are canonical and derived, not repeated in the registry.

### Package Markdown

Replace the unconditional report-path section with:

```md
## Independent Verification
- Mode: `boundary | final`
- Report: `<safe path> | None — final assurance`
- Rationale: <named boundary/risk reason>
```

### Compact Lifecycle State

Canonical path: `.tasks/<feature>/lifecycle-state.json`. It is current mechanical state, not product authority or
history. Validate only fields required by the accepted design:

- schema/generation, feature, stage, quiescence, next legal action;
- authorization ID/initial/effective digests;
- owner token/disposition;
- assurance profile/package modes;
- exact artifact and remotely reachable code checkpoints;
- preauthorization and implementation maxima/issued usage/deadlines plus bounded active reservation;
- package/wave dispositions;
- canonical serious clusters/strikes and repair-wave use;
- current freeze and receipt pointers.

Git history preserves prior snapshots. Do not add an in-file event list.

### Final Receipt Paths

Use one freeze-scoped directory, derived from a helper-validated freeze ID:

```text
.tasks/<feature>/reviews/<freeze-id>/
  combined-final.md                 # low only: C
  review-code-state.json            # standard/high: R
  specialists/<risk>.md             # high post-R S[*], when selected
  audit.md                           # standard/high: U
  verification-summary.md           # V
```

Pre-freeze package/boundary receipts remain existing package reports `B[i]`. The freeze object lives in the compact
Lifecycle State; no separate graph store is added.

## Phase 1 Reconciliation

### Retain

- Delivery Owner and return-only child roles;
- exact accepted-state intent and focused amendment handback;
- triggered architecture-invariant projection;
- finding classification and logical implementation-owner continuity;
- behavior-before-proof/matrix ordering;
- affected broad regression before proof/report refresh;
- same-mechanism stopping principle.

### Amend

- The reviewed-candidate decision surface becomes the sole Implementation Authorization and incorporates the old
  Gate-2 and Execution Contract content without retaining either as a separate gate.
- Human-owned envelope and agent-owned technical revision are separated.
- Initial rejection is strike 1; one repair and failed closure is strike 2/open circuit.
- Cluster identity excludes agent, signature, label, commit, and timeout.
- Universal package verification becomes `boundary | final` routing.
- Sibling final review/audit becomes low combined or standard/high serial assurance.
- Owner context-only continuation gains one compact CAS-checkpointed snapshot.

### Remove

- blocking user Gate 1;
- second Execution Contract approval and step-by-step repair re-prompts on the default path;
- current-root planned-feature authority;
- universal package report requirement;
- child-owned repair/final continuation;
- sibling review/audit over a state likely to change;
- release-default sidecar/checkpoint deletion;
- broad concurrent sidecar `git add -A`.

## Implementation Slices and Commits

All slices are serial unless explicitly noted. Each commit must keep affected skills/references ≤150 lines and pass
its focused tests before the next slice.

### Slice 0 — Freeze the behavioral oracle

**Commit:** `test: establish agentic lifecycle oracle`

**Files**

- add `plugins/super-developer/assets/tests/fixtures/agentic-lifecycle-scenarios.json`
- add `plugins/super-developer/assets/tests/test_agentic_lifecycle.py`
- update `plugins/super-developer/assets/tests/test_skill_prompts.py` only for shared fixture loading

**Work**

- Encode all 21 accepted scenarios with initial-state class, seed, expected first-detection stage/class, maximum
  formal prompts, repair-wave expectation, and terminal result.
- Add fixture-schema and uniqueness tests.
- Add deterministic temporary-Git drills for sidecar-only roots, non-force code-before-sidecar publication windows,
  current-root rejection/migration, monotonic budget persistence, last-verified escalation, and cold resume.
- Record v1.39/Phase-1 expected behavior separately from candidate expectations; static prompt assertions remain
  supporting evidence, not behavioral PASS.

**Exit**

- Existing 117 tests remain green.
- New baseline/drill tests establish reproducible oracle inputs without asserting unimplemented candidate prompts.
- No runtime simulator, dashboard, or generated report is added.

---

# Phase A — Pre-implementation Correctness, One Gate, Minimum Portability

### Slice A1 — Make planned artifacts sidecar-only

**Commit:** `docs: make planned artifacts portably sidecar-only`

**Files**

- `references/artifact-store.md`
- `references/conceptualize-slice-authority.md`
- `references/tool-usage.md`
- `skills/conceptualize/SKILL.md`
- `skills/conceptualize/references/final-handoff.md`
- `skills/worktree/references/feature-package-workflow.md`
- `references/slice-first-artifacts.md`
- focused prompt tests

**Work**

- Retire current-root authority for planned features; define one safe import/migration path for legacy artifacts.
- Resolve Sidecar Portability Authorization from explicit instruction/preference or one focused discovery question.
- Fence initial non-force `artifacts/<feature>` CAS publication and initialize compact Lifecycle State.
- Replace broad checkpoint staging with path-specific finalized paths.
- Define immutable namespaced code checkpoint refs and code-before-sidecar publication, but do not add a Git wrapper.

**Exit**

- Current-root planned mode fails closed; safe migration passes.
- Initial remote sidecar publication cannot target another ref or inherit code/release authority.
- Crash-window Git drills pass.

### Slice A2 — Shift correctness before planning

**Commit:** `docs: make planning implementation-ready`

**Files**

- `skills/implementation-plan/SKILL.md`
- `skills/implementation-plan/references/{design-preflight,planner-agent-contract,spec-template,artifact-authoring,validation-checklist}.md`
- `skills/spike-to-plan/SKILL.md`
- `skills/testing/references/core/generic-testing.md`
- `references/orchestration-convergence.md`
- focused prompt tests

**Work**

- Make design/feasibility preflight precede plan authoring.
- Separate safe disposable spike actions from protected discovery actions.
- Require complete prerequisite disposition, actual-path seams, broad-regression placement, envelope/baseline split,
  assurance/routing proposal, and Planner self-challenge.
- Start and persist the finite preauthorization budget at planning handoff.
- Keep Slices authoritative where useful; do not add another requirement ledger.

**Exit**

- Requirement/architecture/public-contract/verification-seam seeds route before authorization.
- Known-unavailable and protected-only prerequisites have distinct outcomes.
- Unrelated plan findings cannot create unbounded revision/spike calls.

### Slice A3 — Consolidate one authorization

**Commit:** `docs: authorize implementation once`

**Files**

- `skills/review-plan/SKILL.md`
- `skills/review-plan/references/{plan-review-resolution,plan-review-rubrics}.md`
- `skills/implement/SKILL.md`
- `skills/implement/references/execution-contract.md`
- `references/orchestration-convergence.md`
- focused prompt tests

**Work**

- Remove blocking Gate 1.
- Run cold plan challenge before the user decision; batch findings.
- Allow envelope-preserving technical revision plus affected cold re-review without user input.
- Present reviewed plan, exact Authorization Digest inputs, readiness, budgets, actions, and exclusions as the sole
  Implementation Authorization.
- Remove the later approval and default step-by-step repair prompts.

**Exit**

- Clean planning has exactly one formal implementation authorization.
- Technical defects resolve agent-to-agent; envelope changes ask one focused question.
- No implementation starts from unreviewed or blocked prerequisites.

### Slice A4 — Validate exact lifecycle state

**Commit:** `feat: validate portable lifecycle state`

**Files**

- `assets/sliceproof.py`
- `assets/tests/test_sliceproof.py`
- `references/slice-first-artifacts.md`
- `references/artifact-store.md`
- `skills/worktree/references/feature-package-workflow.md`
- `skills/implement/references/{execution-contract,package-dispatch}.md`

**Work**

- Add minimal schema/path/digest validation for assurance profile/mode and Lifecycle State.
- Validate monotonic issued budgets/deadlines, owner/generation, sidecar root, code checkpoint ref/SHA, effective
  authorization lineage, quiescence, and last-verified fallback.
- Add deterministic digest emission/validation only where existing digest utilities cannot express it.
- Keep Git CAS commands in worktree contracts and tests; helper does not push, dispatch, or own state transitions.

**Exit**

- Temporary-Git checkpoint/resume drills and malformed-state tests pass.
- No state reset across owner/host/commit is accepted.
- Phase A cold review returns ACCEPT before Phase B begins.

---

# Phase B — Autonomous Delivery and Adaptive Assurance

### Slice B1 — Route package assurance by named boundary

**Commit:** `docs: route assurance by meaningful boundary`

**Files**

- add `references/assurance-routing.md`
- `references/{work-packages,package-lifecycle,package-verification-report,slice-first-artifacts}.md`
- `skills/implement/references/{package-dispatch,package-integration-gates,package-verification}.md`
- `skills/implementation-plan/references/{spec-template,planner-agent-contract}.md`
- focused prompt tests

**Work**

- Define `low | standard | high`, promotion precedence, `boundary | final`, and distinct receipt ownership once.
- Require `B[i]` before dependent/consumed boundary unlock.
- Permit coherent final-routed leaf work without a fabricated package report.
- Keep standard default and high named-risk triggers; file/call count never lowers assurance.

**Exit**

- Package dependency scenario cannot unlock on proof/self-review alone.
- Low candidate promotes rather than passes when a higher trigger appears.
- New shared reference and all affected capped files remain ≤150 lines.

### Slice B2 — Validate profile-specific package completion

**Commit:** `feat: validate assurance routing`

**Files**

- `assets/sliceproof.py`
- `assets/tests/test_sliceproof.py`
- artifact templates/references changed by B1

**Work**

- Extend strict registry/package parsing for profile, mode, and conditional report path.
- `validate-package-complete` requires report/state binding only for `boundary`; `final` requires valid stable proof
  and defers semantic closure explicitly.
- `validate-final` validates all pre-freeze inputs and the selected package equation without pretending final
  assurance has run.
- Reject high/consumed packages routed incorrectly, substitute reports, unknown modes, and profile downgrade.

**Exit**

- Existing proof/report safety and evidence-anchor tests remain green.
- Boundary/final/high/promotion tests pass without bypassing semantic verification.

### Slice B3 — Serialize final assurance and receipts

**Commit:** `docs: make final assurance acyclic`

**Files**

- `skills/review-code/SKILL.md`
- `skills/review-code/references/pipeline-report.md`
- `skills/audit/SKILL.md`
- `skills/audit/references/audit-subagent-contract.md`
- `skills/implement/SKILL.md`
- `skills/implement/references/{execution-contract,package-integration-gates}.md`
- `references/{orchestration-convergence,package-lifecycle,assurance-routing}.md`
- focused prompt tests

**Work**

- Implement low `F → C → V`, standard `F → R → U → V`, high `F → R → S[*] → U → V` ordering.
- Assign every package/final specialist to exactly one side of `F` and one named lens.
- Make code review reach closure before standard/high audit dispatch.
- Keep all verifier/auditor roles read-only and return-only; Delivery Owner alone repairs/continues.
- Persist freeze-scoped outputs and final notification without adding a receipt registry.

**Exit**

- Receipt-role overlap/circular/cross-freeze tests fail closed.
- A code-review repair cannot invalidate an already-running audit.
- Clean low path uses one combined cold verifier.

### Slice B4 — Validate completion and bound repair

**Commit:** `feat: validate agentic completion`

**Files**

- `assets/sliceproof.py`
- `assets/tests/test_sliceproof.py`
- `skills/implement/references/{repair-agent-contract,package-integration-gates}.md`
- `references/{orchestration-convergence,slice-first-artifacts}.md`
- focused prompt tests

**Work**

- Add profile-specific final receipt validation over the freeze subsection and canonical paths.
- Enforce initial rejection/one repair/one closure/open circuit, canonical cluster lineage, mixed-class precedence,
  total repair-wave/call/command/time budgets, and reserved control-plane fallback.
- Validate Verification Summary only as an index of clean predecessors.
- Rerun affected surfaces after repair; widen only for material/shared/sensitive/uncertain impact.

**Exit**

- Same mechanism cannot reset through agent/signature/commit/label changes.
- Budget/CAS-loss escalation uses safe checkpoint or last verified state.
- Phase B behavioral corpus and cold review return ACCEPT before Phase C.

---

# Phase C — Extended Continuity and Release Safety

### Slice C1 — Complete bounded lifecycle transitions

**Commit:** `docs: complete portable lifecycle transitions`

**Files**

- `references/{artifact-store,orchestration-convergence}.md`
- `skills/implement/SKILL.md`
- `skills/worktree/references/feature-package-workflow.md`
- affected prompt/helper tests

**Work**

- Define `resume`, `park`, `cancel`, and `supersede` over the same compact snapshot.
- Preserve immutable package IDs and append/map replacements rather than renumbering in flight.
- Recover only from quiescent remote checkpoints; later local state remains untrusted input.
- Fail closed on unsupported degraded host/remote conditions; do not build an active-active coordinator.

**Exit**

- Resume/park/cancel/supersede fixtures preserve authorization, budgets, owner, cluster strikes, code refs, and next
  legal action.
- No mode resets authority or infers package/final completion.

### Slice C2 — Retain portable evidence through release

**Commit:** `docs: retain portable evidence through release`

**Files**

- `skills/release/SKILL.md`
- `skills/release/references/{release-contract,release-git-safety}.md`
- `references/artifact-store.md`
- release prompt tests

**Work**

- Change remote sidecar/code-checkpoint cleanup from default delete to default retain.
- Require a separate exact retention/cleanup decision after final target sync.
- Preserve final Verification Summary and required refs before any cleanup.
- Keep target merge/push/tag/release/delete separately authorized; do not expand implementation auto-resolve.

**Exit**

- Release cannot delete the only portable authority/evidence by default.
- Explicit cleanup remains exact, bounded, non-force, and independently verifiable.

### Slice C3 — Integrated UX and quality closure

**Commit:** `docs: document the agentic delivery journey`

**Files**

- `plugins/super-developer/README.md`
- `CHANGELOG.md`
- `docs/superpowers/plans/2026-07-18-pipeline-remediation-bootstrap-plan.md` (mark superseded sections)
- scenario manifest/tests and any affected prompt tests

**Work**

- Document Conceptualize → preflight → plan challenge → one authorization → autonomous delivery → adaptive
  assurance → notification.
- Remove obsolete claims about Gate 1, universal verifiers, sibling final checks, and default sidecar deletion.
- Run all 21 candidate scenarios in fresh OpenAI agent contexts and compare with v1.39 baseline observations.
- Record only concise observed metrics in the final implementation report; do not add a dashboard/ledger artifact.

**Exit**

- Full repository tests and affected skill audits pass.
- All changed capped files are ≤150 lines; local links and `git diff --check` pass.
- Quality protocol thresholds pass with zero escaped seeded serious defects and one clean-path authorization.
- Final cold full-diff review and read-only completion audit return ACCEPT/PASS on exact commits.

## Test and Evidence Matrix

| Layer | Required evidence |
|---|---|
| Static contracts | Existing and updated prompt-surface tests; never sufficient alone |
| Mechanical schemas | `test_sliceproof.py` malformed/valid profile, state, freeze, receipt, path, digest, budget cases |
| Git behavior | Temporary repositories for sidecar-only migration, non-force checkpoint ordering, crash windows, retention |
| Agent behavior | Fixed 21-scenario fresh OpenAI packets with stage/class/prompt/call/repair oracles |
| Quality comparison | v1.39 baseline vs candidate: earlier upstream detection, no later serious detection, zero serious escapes |
| Scope/integrity | affected skill audits, line caps, changed-path allowlist, Markdown links, `git diff --check` |
| Independent assurance | Phase A/B/C cold reviews plus final full-diff review and final completion audit |

## Quality Thresholds

- 100% seeded serious defects detected at the required stage/class.
- 100% requirement, architecture, feasibility, plan-changing prerequisite, and verification-seam seeds detected
  before Implementation Authorization; protected-only failures before product writes/fanout.
- No serious seed detected later than v1.39; known late-discovery seeds move earlier.
- Zero escaped seeded serious defects.
- Zero serious false blockers on clean fixtures and fewer than 10% false blockers overall.
- Exactly one formal implementation authorization and zero repair waves on clean flows.
- One repair maximum per canonical cluster; failed closure opens the circuit.
- Clean low flow after discovery: Planner, Plan Reviewer, Implementer, combined final verifier.
- Cold continuation succeeds at every declared quiescent checkpoint without hidden chat or local-only code.

## Phase Review and Stopping Rules

- Each phase gets one cold full-phase review against the accepted design and scenario subset.
- One bounded correction is allowed for a serious cluster. A second failure of that mechanism stops for redesign.
- Reviewers never edit or advance lifecycle stages.
- Do not begin the next phase from a rejected phase.
- Final handoff is `completed` only after exact full-diff review, final audit, quality thresholds, docs, and clean
  worktree all pass. Otherwise return `blocked`/`needs_decision` with exact state.

## Changed-Path Boundary

Allowed implementation paths are limited to:

- `CHANGELOG.md`, `plugins/super-developer/README.md`;
- this implementation plan and the superseded bootstrap plan; the accepted north-star spec is read-only;
- `plugins/super-developer/assets/sliceproof.py` and asset tests/one scenario fixture;
- shared references named in this plan plus new `references/assurance-routing.md`;
- `conceptualize`, `implementation-plan`, `review-plan`, `implement`, `review-code`, `audit`, `worktree`,
  `spike-to-plan`, `testing`, and `release` skill/reference files named above.

No plugin metadata/version bump, unrelated skill cleanup, new executable, dependency, provider/model rule, merge,
release, tag, branch deletion, force action, or target-branch change is in scope.

## Plan Acceptance and Implementation Authorization

Before source edits:

1. run a cold OpenAI plan challenger against this plan, accepted design, Phase 1 diff, helper surfaces, and caps;
2. resolve one bounded serious finding set and obtain final Sol `ACCEPT`;
3. checkpoint the exact accepted plan commit;
4. present one Implementation Authorization covering this full A/B/C plan, expected commits, in-scope writes/tests,
   local commands, bounded agent reviews, and excluded remote/destructive actions;
5. implementation begins only after `Approve and auto-resolve`.
