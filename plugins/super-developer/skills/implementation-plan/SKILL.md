---
name: implementation-plan
description: >
  Creates or repairs Slice-first planned-feature artifacts for approved changes. Use for initial planning,
  same-requirement plan repair during auto-resolve implementation, package breakdowns, or task artifacts.
  Do not use to perform coding, code review, audit, or status.
---

# Implementation Plan

Orchestrate a fresh Slice-first planned-feature set under the selected artifact root: `SPEC.md`, lightweight
`tasks.json`, package Markdown, and declared `report_path` result files. New contracts drop `proof_path`.
“Fresh” describes the artifact set, not whether the target system is new. Source inspection and helpers use the
separate code root.

This skill is the `implementation-plan` **orchestrator**, not the planner worker. Preserve approved requirements,
roots, decisions, and workflow state here; delegate artifact writing with `references/planner-agent-contract.md`.
Mode is `initial` by default. Use `implementation-continuation` only when `implement` supplies approved
requirements, roots/ref/slug, current artifacts, the Execution Contract, a stage-sourced plan-defect packet, and
accepted empirical reports or explicit `none`.

## Always

- Plan from approved requirements, safe Conceptualize/diagnosis material, verified repository/official evidence,
  and, when empirical evidence applies, accepted bounded `empirical-spike` reports only. Preserve planned-hotfix
  context without inventing an artifact field or feature ref.
- Prefer static/official evidence. Inventory a bounded set of distinct material empirical questions tied to the
  current approved decisions; routine work, cost alone, and statically resolved questions do not trigger a spike.
- Preserve planning context while evidence runs. Give each falsifiable question one stable logical-question ID.
  Attempt 1 is one fresh `empirical-spike` invocation; follow-ups are fresh invocations with the same question ID,
  incremented attempt IDs 2–3, and a named corrected packet or changed method/signal. Unchanged attempts are
  forbidden; three total attempts or continually emerging/unbounded questions are non-convergence. Independent
  questions may run in parallel; only accepted evidence may create the next sequential question.
- A spike is evidence-only and cannot write plan artifacts, choose workflow, or invoke planning. Because this is
  already the `implementation-plan` invocation, resume this orchestrator; never recursively invoke
  `implementation-plan`.
- Accept `resolved-static`, `supported`, or `rejected` only after validating identity, provenance, method,
  authority, bounds, limitations, and cleanup. Correct `blocked`/`inconclusive` only through an authorized changed
  attempt; unresolved initial mode stops and continuation returns protected/out-of-contract gaps to `implement`.
  Evidence never authorizes behavior, scope, architecture, deferral, or risk acceptance.
- Delegate all planned-feature artifact writing to a fresh planner. A planner that finds unresolved material
  empirical behavior must return `BLOCKED: empirical_evidence_needed`; only this orchestrator may resolve it.
- In `initial` mode, retain every existing planning/overwrite/user-decision gate. In continuation, repair supplied
  plan defects autonomously while semantics/scope/visible behavior/risk/manual exceptions stay fixed. Any new
  continuation package supplies `BASE_KIND`, exact `BASE_REF`, focused-review-bound `REVIEWED_BASE_SHA`, and
  prerequisite ref/SHAs: approved original base when independent, or exact feature/integration SHA containing prerequisite ancestors when dependent. Reports may be `none`; return only semantic/risk/
  manual/protected expansion to `implement`, never prompt here.
- Slices are product/design authority only, never workflow/tool/review authority. Index-only planning is allowed
  when no Slice is independently useful; otherwise the planner inventories and reads every safe Slice in full.
- Registry is bookkeeping; package Markdown owns assignment, and `report_path` names the independent result.
  Boundaries keep material requirements observable from files alone.
- Define done objectively: executable feature `## Acceptance` in `SPEC.md` and per-package `## Acceptance
  Checklist`, with only explicit human-approved `manual (approved)` exceptions. Surface missing runnable commands
  before authorization rather than writing unverifiable acceptance.
- The planner applies the complete shared Module/Interface/Seam model and all smell heuristics while shaping
  packages, but persists only material requirement/risk-traced implications in existing scope, boundaries, risks,
  dependencies, and verification fields; it creates no standalone quality proof/report or per-smell rows.
- Carry explicit artifact root/ref, code root, and resolved feature/artifact slug through packets, validation, and
  summaries. A Conceptualize slug remains the default absent approved full rename/migration metadata.
- Resolve Semgrep before planner dispatch. Use supplied state without reopening opt-in; for direct invocation,
  resolve preferences. Disabled requires no setup/scan/internet. Load policy only at its action point, disclose
  clone or fast-forward pull side effects, and keep artifact authoring scan-free.
- Validate returned artifacts before success.

## Do

1. Load `../../references/artifact-store.md`. Resolve mode, artifact root/ref, code root, slug, and source. For
   `initial`, select direct requirements/evidence or one Conceptualize workspace and ask once if ambiguous. For
   `implementation-continuation`, validate the caller binding and use only its requirements, current artifacts,
   Execution Contract, stage/defect provenance, and report set or `none`; return conflicts without prompting.
   Create a missing direct-planning sidecar through `worktree`; publish only when separately authorized.
2. Check unsafe paths, unresolved decisions, overwrite, empirical uncertainty, and risk acceptance before
   delegation. In continuation mode, treat same-root routine artifact overwrite/repair as covered and fail closed
   on semantic or authority expansion. Resolve testing authority only when material execution feasibility requires
   it: accepted/current workflow, routine-safe bounded-local fallback, or exact task-local authorization.
   If insufficient, initial mode may invoke `testing`; continuation returns the gap to `implement` for contract-owned
   repair or an existing protected stop. For nontrivial/risky plans, apply
   `references/design-preflight.md`; reuse equivalent current adversarial analysis only for identical approved
   scope/evidence with complete requirements and overengineering coverage. Resolve every `COVERAGE_GAPS`,
   `MUST_DECIDE`, and `BLOCKERS` item before artifact writing.
3. Inventory bounded material empirical questions unresolved after repository/official evidence. Start each
   logical-question ledger at attempt 1 and invoke `empirical-spike` once with its decision, outcomes, constraints,
   safe paths, authority, and report contract. Parallelize independent questions; sequence only evidence-created
   questions. Validate every report. A corrected packet or changed method/signal may invoke attempts 2–3 under the
   stable question ID; never retry unchanged or exceed three total. Initial mode retains semantic gates;
   continuation applies same-requirement evidence autonomously and returns only Stop-if expansion to `implement`.
4. Resolve the planner packet's Semgrep state. Supplied state is authoritative and required in continuation mode.
   Otherwise, only in initial mode, load `../../references/model-preferences.md` and conditional
   `../../references/semgrep.md`, present opt-in/setup, and name clone/pull effects. Continue disabled if declined;
   never run Semgrep scans while authoring.
5. Dispatch a fresh planner with mode, roots/ref, slug/migration metadata, delivery context, approved source,
   overwrite/continuation authority, stage/defect plus reports or `none`, original base, current integration state,
   and `BASE_KIND`, exact `BASE_REF`, candidate `REVIEWED_BASE_SHA`, and prerequisite ref/SHAs for each continuation-created package.
   Include testing provenance when triggered and Conceptualize paths only when applicable. Pass labeled paths for
   planner contract, artifact store,
   Slice authority/projection, preflight evidence, SPEC template, clean-code, work-package, canonical artifact
   model, artifact authoring, validation, tool usage, and optional Semgrep. Include resolved Semgrep state, the
   accepted empirical reports (or `none`), stop conditions, and output.
6. If the planner returns `BLOCKED: empirical_evidence_needed`, verify no artifacts were written and reconcile
   its one question with the ledger. A distinct bounded question starts attempt 1; an existing question advances
   only through step 3's materially changed attempts. Redispatch a fresh planner with the original packet and
   reports. Stop on an unchanged/over-cap question, unbounded emergence, bundled questions, or malformed status.
7. On a normal return, re-open `SPEC.md`, `tasks.json`, and every package Markdown from the artifact root. From the
   code root run `python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-plan \
   --artifact-root <artifact-root> --code-root <code-root> .tasks/<feature>/tasks.json`. Route semantic repair
   through a fresh planner packet; never patch planned-feature artifacts inline.
8. Report roots/ref, delivery context, feature paths, packages/dependencies, closure-complexity and sequencing
   rationale, empirical question/report-set status and provenance or static-resolution note,
   execution-feasibility/testing authority, Slice inventory, approved deferrals, assumptions, validation, and next gate.

## Load if needed

- Conceptualize input applies → `references/conceptualize-inputs.md` and
  `../../references/conceptualize-slice-authority.md`
- Nontrivial/risky design challenge → `references/design-preflight.md`
- Package shaping → `../../references/work-packages.md`
- Drafting `SPEC.md` → `references/spec-template.md`
- Drafting registry/packages/result declarations → `references/artifact-authoring.md` and
  `../../references/slice-first-artifacts.md`
- Before artifact writes/completion claims → `references/validation-checklist.md`
- Helper syntax or command safety is unclear → `../../references/tool-usage.md`
- Semgrep preference/cache/policy/evidence applies → `../../references/semgrep.md`

## Stop if

- Any slug, root/ref, artifact/source path, or supporting-contract path is missing, unsafe, or contradictory.
- A Conceptualize slug changes without approved migration metadata; in initial mode, existing plan state would be overwritten.
- Initial mode needs a requirement/Slice/deferral/boundary/risk decision; continuation mode would change approved
  semantics/scope/visible behavior/manual exceptions, accept risk, or exceed the Execution Contract.
- Slices exist but the delegated planner cannot complete the full safe inventory.
- Required empirical evidence is blocked/inconclusive/malformed or lacks provenance, method, authority, or cleanup.
- A logical empirical question exhausts attempt 3 without an accepted result, repeats unchanged, or distinct
  blockers continually emerge or cannot be bounded.
- `sliceproof.py validate-plan` fails and cannot be repaired within scope.
- Semgrep would require unapproved network/setup, unavailable safe cache, hidden cloud behavior, or mandatory scans.

## Output

Return mode, artifact root/ref, code root, feature/artifact paths, packages/dependencies and closure rationale,
Acceptance checks with flagged manual exceptions, empirical report-set status/provenance,
execution-feasibility/testing authority, Slice inventory, deferrals, assumptions, validation, and next step. Initial
mode retains `review-plan` after confirmation; continuation returns repair status to `implement` for focused
`review-plan` without fresh plan or implementation approval.
