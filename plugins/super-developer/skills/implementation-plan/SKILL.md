---
name: implementation-plan
description: >
  Creates or repairs approved planned-feature artifacts. Use for explicit plans, package shaping, or
  same-requirement planning continuation. Do not use for direct low-risk execution, code review, audit, or status.
---

# Implementation Plan

Orchestrate Slice-first planned-feature artifacts under an explicit artifact root: `SPEC.md`, lightweight
`tasks.json`, package Markdown, and declared result paths. Source inspection uses the separate code root. Create
this normal artifact set only after routing selects planning.

This skill is the orchestrator, not the artifact-writing worker. Mode is `initial` unless `implement` supplies an
`implementation-continuation` packet containing approved requirements, roots/ref/slug, current artifacts, the
Execution Contract, stage-sourced plan defect, shared remaining repair time/deadline, round/probe history, and
accepted empirical reports or explicit `none`.

## Always

- Plan only from approved requirements, safe Conceptualize/diagnosis material, verified repository/official
  evidence, and accepted `empirical-spike` reports. Preserve planned-hotfix context without inventing a feature ref.
- Prefer static evidence. Before any empirical or repair attempt, load `../../references/bounded-attempts.md` and
  preserve its stable identity/history. A spike supplies evidence only: it cannot choose workflow, write plan
  artifacts, approve semantics/risk, or invoke planning. This orchestrator validates each result and resumes itself.
- Delegate substantive artifact writing to a fresh planner using `references/planner-agent-contract.md`. Only a
  proven mechanical edit under `../../references/plan-amendments.md` may be applied inline.
- Initial mode retains planning, overwrite, risk, and user-decision gates. Continuation autonomously repairs only
  within supplied requirements and contract; return changes to semantics, scope, visible behavior, risk, or manual
  exceptions to `implement`.
- Slices are product/design authority, never workflow authority. Chat-only and Index-only planning are valid, but
  when Slices exist the planner must inventory and read every safe Slice in full.
- Registry is bookkeeping. Package Markdown owns assignment and the frozen package done-definition; each declared
  `report_path` names its independent result. Preserve stable package IDs; never renumber or reuse them.
- Feature `## Acceptance` and package `## Acceptance Checklist` items must be executable, except explicitly
  user-approved `manual (approved)` items. Surface missing runnable commands before authorization.
- Apply the complete shared Module/Interface/Seam model and all smell heuristics while shaping packages. Persist
  only material, requirement/risk-traced implications in existing artifact fields; create no quality ledger or
  per-smell rows.
- Keep artifact root/ref, code root, and resolved slug explicit throughout. A Conceptualize slug remains the default
  without approved rename/migration metadata.
- Resolve Semgrep before planner dispatch. Disabled means no setup, scan, or internet. For direct initial planning,
  load policy only at its decision point and disclose clone/pull side effects. Authoring itself runs no scans.
- Re-open and validate returned artifacts before claiming success.

## Do

1. For initial mode, load `../../references/change-routing.md` before creating artifacts. Honor explicit plan
   requests; route accepted narrow low-risk work to its task workflow. Once planning is selected, load
   `../../references/artifact-store.md` and resolve mode, roots/ref, slug, source, and safe paths. Choose direct
   approved requirements or one Conceptualize input; ask once only if initial workspace selection is ambiguous.
   Continuation uses only its caller packet and returns conflicts without prompting. Create a missing direct-plan
   sidecar through `worktree`; publish only under separate authorization.
2. Before delegation, resolve unsafe paths, overwrite authority, open requirements/risk decisions, and empirical
   uncertainty. Resolve testing authority only when material execution feasibility requires it: use an accepted
   current workflow, a routine-safe bounded local fallback, or exact task-local authorization. If none is sufficient,
   initial mode may invoke `testing`; continuation returns the gap to `implement` for contract-owned repair or a
   protected stop. Continuation same-root repair needs no repeated overwrite prompt but cannot exceed its contract.
   For nontrivial/risky plans, apply
   `references/design-preflight.md`; reuse it only for identical scope/evidence with complete requirements and
   overengineering coverage. Resolve all `COVERAGE_GAPS`, `MUST_DECIDE`, and `BLOCKERS`.
3. Inventory a bounded set of material empirical questions unresolved by repository/official evidence. Apply the
   loaded bounded-attempt contract and preserve supplied history. Invoke `empirical-spike` with one question,
   blocked decision, support/reject outcomes, safe paths, authority, and report contract. Accept `resolved-static`,
   `supported`, or `rejected` only after checking identity, provenance, method, authority, bounds, limitations, and
   cleanup; evidence never supplies product authority. Initial mode keeps semantic gates; continuation returns only
   contract-protected expansion to `implement`.
4. Resolve Semgrep state. Continuation requires the supplied state. Initial mode loads
   `../../references/model-preferences.md` and, only when applicable, `../../references/semgrep.md`; name setup
   effects and continue disabled if declined. Never run a broad/raw authoring scan.
5. Dispatch a fresh planner with a cold, labeled packet: mode; roots/ref/slug and migration data; delivery context;
   approved source; overwrite/continuation authority; stage/defect, attempt history, and reports or `none`; testing
   provenance; and Semgrep state. For any repair include shared remaining time/deadline, round/progress history,
   and next strategy; initial repair binds the loaded policy's budget without another approval layer.
   Supply direct paths for the planner contract, artifact store, applicable
   Conceptualize/Slice contracts, preflight evidence, SPEC template, `../../references/clean-code-rules.md`,
   `../../references/bounded-attempts.md` for empirical/repair history, work-package contract, canonical artifact
   model, artifact authoring, validation, tool usage, and optional Semgrep
   policy. Include current artifacts and integration state for continuation. Every new continuation package also
   receives `BASE_KIND`, exact `BASE_REF`, candidate
   `REVIEWED_BASE_SHA`, and prerequisite refs/SHAs. Include stop conditions and required output; pass Conceptualize
   paths only when applicable.
6. For `BLOCKED: empirical_evidence_needed`, verify no artifact was written and reconcile its single falsifiable
   question with retained history. Resolve it through step 3, then redispatch the original packet plus reports.
   Stop on malformed/bundled, unchanged, exhausted, unbounded, or continually emerging questions.
7. On success, re-open `SPEC.md`, `tasks.json`, and every package file under the artifact root. From the code root run:
   `python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-plan --artifact-root <artifact-root>
   --code-root <code-root> .tasks/<feature>/tasks.json`. Route semantic repair through a fresh planner. Before an
   exact mechanical edit, load and apply `../../references/plan-amendments.md`.
8. Report roots/ref/slug, delivery context, artifact paths, packages/dependencies and closure rationale, empirical
   report status/provenance or static resolution, testing authority, Slice inventory, deferrals, assumptions,
   validation, and next gate.

## Load if needed

- Conceptualize input applies → `references/conceptualize-inputs.md` and
  `../../references/conceptualize-slice-authority.md`
- Nontrivial/risky design → `references/design-preflight.md`
- Package shaping → `../../references/work-packages.md`
- SPEC drafting → `references/spec-template.md`
- Registry/package/result declarations → `references/artifact-authoring.md` and
  `../../references/slice-first-artifacts.md`
- Before writes and completion claims → `references/validation-checklist.md`
- Helper syntax or command safety is unclear → `../../references/tool-usage.md`
- Semgrep preference, setup, or evidence applies → `../../references/semgrep.md`

## Stop if

- Any root/ref/slug/path or required contract label is missing, unsafe, contradictory, or outside authority.
- Initial mode would overwrite existing plan state without approval, or a slug changes without approved migration.
- Initial mode needs a requirement, Slice, boundary, deferral, risk, or manual decision; continuation would exceed
  approved semantics, scope, visible behavior, risk, manual exceptions, or the Execution Contract.
- Slices exist but the planner cannot complete the full safe inventory and material H3 accounting.
- Required empirical evidence is invalid, or the bounded-work contract stops for exhausted repair time,
  non-convergence, or empirical-attempt exhaustion; planning never resets a caller's budget.
- Validation cannot pass within authorized scope.
- Semgrep would require unapproved setup/network behavior, an unsafe cache, hidden cloud behavior, or mandatory scans.

## Output

Return mode; roots/ref/slug and paths; packages/dependencies; Acceptance and manual exceptions; empirical,
feasibility, Slice, deferral, assumption, and validation status; and next step. An initial draft flows directly to
`review-plan` without confirmation unless a genuine decision blocks it. Reviewed-plan approval and execution
authorization are separate visible decisions. Continuation returns to `implement` for focused `review-plan`; it
opens neither a fresh plan-approval nor implementation-approval gate.
