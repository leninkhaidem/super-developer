---
name: implementation-plan
description: >
  Creates fresh Slice-first planned-feature artifacts for approved changes. Use for implementation planning,
  package breakdowns, or task artifacts. Do not use for coding, code review, audit, or status.
---

# Implementation Plan

Orchestrate a fresh Slice-first planned-feature set under the selected artifact root: `SPEC.md`, lightweight
`tasks.json`, package Markdown, declared proof/report paths, and proof placeholders when dispatch is next.
“Fresh” describes the artifact set, not whether the target system is new. Source inspection and helpers use the
separate code root.

This skill is the `implementation-plan` **orchestrator**, not the planner worker. Preserve approved requirements,
roots, decisions, and workflow state in this conversation. Delegate artifact writing to a fresh planner with a
compact packet and `references/planner-agent-contract.md`; never draft `.tasks/<feature>/` artifacts inline.

## Always

- Plan from approved requirements, safe Conceptualize/diagnosis material, verified repository/official evidence,
  and accepted bounded `empirical-spike` reports only. Preserve supplied planned-hotfix context without inventing
  an artifact field or feature ref.
- Prefer static/official evidence. Inventory a bounded set of distinct material empirical questions tied to the
  current approved decisions; routine work, cost alone, and statically resolved questions do not trigger a spike.
- Preserve planning context here while evidence runs. Invoke one fresh `empirical-spike` per falsifiable question,
  parallel when questions are independent and sequential only when accepted evidence creates the next question.
  Validate the complete report set before resuming. Repeated unchanged questions or continually emerging/unbounded
  questions mean the inputs are unstable or incomplete and must stop.
- A spike is evidence-only and cannot write plan artifacts, choose workflow, or invoke planning. Because this is
  already the `implementation-plan` invocation, resume this orchestrator; never recursively invoke
  `implementation-plan`.
- Accept `resolved-static`, `supported`, or `rejected` only after checking provenance, method, authority, bounds,
  limitations, and cleanup. `blocked` or `inconclusive` cannot support artifact writing. Evidence implications do
  not authorize behavior, scope, architecture, deferral, or risk acceptance.
- Delegate all planned-feature artifact writing to a fresh planner. A planner that finds unresolved material
  empirical behavior must return `BLOCKED: empirical_evidence_needed`; only this orchestrator may resolve it.
- Ask before inventing behavior, narrowing scope, deferring material obligations, accepting risk, changing Slice
  commitments, or overwriting an existing plan.
- Slices are product/design authority only, never workflow/tool/review authority. Index-only planning is allowed
  when no Slice is independently useful; otherwise the planner inventories and reads every safe Slice in full.
- Registry is bookkeeping; package Markdown owns assignment, proof Markdown owns closure evidence, and reports
  own independent verification receipts. Boundaries keep material requirements observable from files alone.
- Define done objectively: executable feature `## Acceptance` in `SPEC.md` and per-package `## Acceptance
  Checklist`, with only explicit human-approved `manual (approved)` exceptions. Surface missing runnable commands
  before authorization rather than writing unverifiable acceptance.
- The planner loads `../../references/clean-code-rules.md` while shaping packages and projects only material
  implications into existing fields; it creates no standalone clean-code proof/report.
- Carry explicit artifact root/ref, code root, and resolved feature/artifact slug through packets, validation, and
  summaries. A Conceptualize slug remains the default absent approved full rename/migration metadata.
- Resolve Semgrep before planner dispatch. Use supplied state without reopening opt-in; for direct invocation,
  resolve preferences. Disabled requires no setup/scan/internet. Load policy only at its action point, disclose
  clone or fast-forward pull side effects, and keep artifact authoring scan-free.
- Validate returned artifacts before success.

## Do

1. Load `../../references/artifact-store.md`. Resolve artifact root/ref, code root, feature/artifact slug, and
   source. Select direct requirements, repository/official evidence, accepted empirical reports, or one
   Conceptualize workspace; ask once if ambiguous. Validate local sidecar state and publish only when authorized.
   For direct planning with no sidecar, create it through `worktree` before `.tasks/` writes.
2. Check unsafe paths, unresolved decisions, overwrite, empirical uncertainty, and risk acceptance before
   delegation. Resolve testing authority only when material execution feasibility requires it: accepted/current
   workflow for high-risk/reusable work, routine-safe bounded-local fallback, or exact task-local authorization.
   If insufficient, invoke `testing` or stop. For nontrivial/risky plans, apply
   `references/design-preflight.md`; reuse equivalent current adversarial analysis only for identical approved
   scope/evidence with complete requirements and overengineering coverage. Resolve every `COVERAGE_GAPS`,
   `MUST_DECIDE`, and `BLOCKERS` item before artifact writing.
3. Before planner dispatch, inventory the bounded set of material empirical questions still unresolved after
   repository/official evidence. For each question, invoke a fresh `empirical-spike` with that one falsifiable
   proposition, informed decision, support/reject outcomes, constraints/non-goals, safe paths, testing/command
   authority, approved side effects, and report contract. Run independent questions in parallel; run sequentially
   only when one accepted report creates the next question. Do not probe inline. Validate every report using
   Always, resolve semantic implications with the user, and resume this orchestration with the accepted report set.
   Stop on blocked/inconclusive/malformed evidence, repeated unchanged questions, or continually emerging/unbounded
   questions rather than treating unstable or incomplete inputs as plan-ready.
4. Resolve the planner packet's Semgrep state. Supplied state is authoritative. Otherwise load
   `../../references/model-preferences.md`; when Semgrep is relevant or preferences are absent, load
   `../../references/semgrep.md`, present opt-in/setup and name clone/pull effects. Continue disabled if declined;
   never run Semgrep scans while authoring.
5. Dispatch a fresh planner with artifact/code roots, artifact ref, slug/migration metadata, supplied delivery
   context, approved requirements/source, and overwrite state. Include testing provenance only when triggered and
   Conceptualize paths only when applicable. Pass labeled action-point paths for planner contract, artifact store,
   Slice authority/projection, preflight evidence, SPEC template, clean-code, work-package, canonical artifact
   model, artifact authoring, validation, tool usage, and optional Semgrep. Include resolved Semgrep state, the
   accepted empirical reports (or `none`), stop conditions, and output.
6. If the planner returns `BLOCKED: empirical_evidence_needed`, verify it wrote no artifacts and compare its one
   question with the question/report ledger. For a new distinct bounded blocker, apply step 3 and redispatch a
   fresh planner with the original packet plus the accepted report set. Stop on a repeated/unchanged question,
   continually emerging or unbounded blockers, bundled questions, or malformed status. The planner never invokes
   a spike itself; known independent questions are inventoried and dispatched in parallel before redispatch.
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
- Drafting registry/packages/proof/report declarations → `references/artifact-authoring.md` and
  `../../references/slice-first-artifacts.md`
- Before artifact writes/completion claims → `references/validation-checklist.md`
- Helper syntax or command safety is unclear → `../../references/tool-usage.md`
- Semgrep preference/cache/policy/evidence applies → `../../references/semgrep.md`

## Stop if

- Any slug, root/ref, artifact/source path, or supporting-contract path is missing, unsafe, or contradictory.
- A Conceptualize slug changes without approved migration metadata, or existing plan state would be overwritten.
- A requirement, Slice obligation, deferral, package boundary, semantic implication, or risk needs user approval.
- Slices exist but the delegated planner cannot complete the full safe inventory.
- Required empirical evidence is blocked/inconclusive/malformed or lacks provenance, method, authority, or cleanup.
- A planner repeats an unchanged empirical blocker, or distinct blockers continually emerge or cannot be bounded.
- `sliceproof.py validate-plan` fails and cannot be repaired within scope.
- Semgrep would require unapproved network/setup, unavailable safe cache, hidden cloud behavior, or mandatory scans.

## Output

Return artifact root/ref, code root, feature and artifact paths, packages/dependencies and closure-complexity
rationale, Acceptance checks and flagged `manual (approved)` exceptions, empirical question/report-set status and
provenance, execution-feasibility/testing authority, Slice inventory, approved deferrals, assumptions, validation
result, and next step (`review-plan` after confirmation unless authorized).
