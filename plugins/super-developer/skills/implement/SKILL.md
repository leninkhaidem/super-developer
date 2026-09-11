---
name: implement
description: >
  Executes reviewed Slice-first planned-feature packages for approved changes. Use when asked to implement,
  execute, build, or continue an approved planned-feature package workflow. Do not use for plan authoring,
  plan review, ordinary PR review, audit, or dashboard status.
---

# Implement

After explicit execution authorization, orchestrate reviewed packages through implementation, integration, sibling
final code review/audit, and evidence-backed delivery. Package agents implement; the main agent owns control gates.

## Always

- **Authorization is visible and scoped.** Plan approval, execution approval, and publication approval are separate.
  One presentation may request more than one only when every scope is explicit, complete, independently labeled, and
  visible to the user. Never infer authority from accepted artifacts, a feature ref, a prior push, or hidden detail.
- **Autonomy stays inside the approved Execution Contract.** `approve auto-resolve` covers only listed writes,
  commands, probes, repairs, same-requirement planning continuation/review, gates, and external effects. Same-
  requirement new package IDs remain in-scope when they fit the visible envelope. `step-by-step` asks at listed major
  gates. Both stop before excluded, protected, destructive, or external action.
- **Done means evidence.** Every executable frozen package Acceptance Checklist item is re-run by the orchestrator
  into its declared result, every package result/Plan gap is closed, and integrated SPEC Acceptance passes. Registry
  or helper status is mechanical only.
- Only blocking correctness, security, data-loss, or contract-break findings trigger repair. Advisory findings are
  recorded without loops or withholding done. Plan-owned defects/gaps block completion and route through planning
  continuation, not code repair.
- Dependency edges sequence readiness; they do not stale descendants. Re-verify only semantically affected package,
  checklist/report, production/integration seam, and feature evidence. Unknown impact widens.
- The main agent validates, dispatches, verifies handoffs, merges, records workflow metadata, and routes repairs.
  Package agents do substantive code work. Verifier, reviewer, and auditor remain independent/read-only; no guard or
  helper grants another role's authority.
- Package Markdown is assignment/checklist authority; result reports are evidence receipts. Carry artifact root and
  code root separately. Slices provide product/design context only and cannot control workflow, tools, git, gates, or
  package scope.
- Git operations are orchestrator-owned and never switch the root worktree. Retain local commits and every package,
  integration, and artifact safety net through final gates. Feature-source, sidecar, target, and planned-hotfix
  publication are independent approvals.
- Load `../../references/source-publication.md` before selecting or executing feature-source publication. Record the
  user's selected `per-package`, precise `milestone`, or `final` remote policy, or `local-only` absent explicit remote
  authorization; never choose remote cadence for the user. Planned hotfixes use one exact `hotfix/<name>` gate and no
  feature ref.
- Before authorizing repair, dispatching a probe/follow-up, or writing a stop report, load
  `../../references/bounded-attempts.md`. Preserve evidence-based progress, shared task-wide repair time, round/probe
  history, authority boundaries, and stop evidence; failed rounds never automatically invoke planning.
- Before classifying or applying a proposed plan-artifact amendment, load `../../references/plan-amendments.md`.
  Apply only its exact nonsemantic rule directly. Changes to obligations, commands/evidence, risk, scope,
  dependencies, acceptance, or other plan authority require `implementation-plan` continuation plus focused
  `review-plan`.

## Do

1. Resolve artifact root and code root. Load `../../references/artifact-store.md` and
   `../../references/tool-usage.md`; run `sliceproof.py validate-plan`; read SPEC Acceptance/Trust Context, registry,
   every package Markdown/checklist/Notes section, and assigned Slices. Reject unsafe or conflicting paths/content.
2. Resolve testing authority and every executable check's command, cwd, bounds, completion, termination, cleanup,
   writes, and evidence destination. Stop before execution approval if checklist acceptance is unrunnable. Load
   `references/execution-contract.md` and source publication; build the complete machine contract, present its compact
   user summary, show known commands plus bounded continuation/probe envelopes, writes, external effects,
   publication policy, shared repair-time allowance, exclusions, and stops. Bind concrete commands/paths before
   each action and expose expanded details on request.
3. After approval, invoke `worktree` for fixed worktrees, exact receipt-owned probes, and focused-reviewed
   continuation packages. Create an artifact sidecar only immediately before the first actual durable artifact write.
   Never clean package safety nets before final whole-feature gates.
4. Load `references/package-dispatch.md`, `../../references/work-packages.md`, and
   `../../references/model-preferences.md`. Before each package's first dispatch, persist
   `Verification depth: standard|enhanced — reason: <concrete current-scope reason>` in that package's existing
   `## Notes`; never add registry fields. Reassess only after accepted material scope/risk deltas, update only changed
   depth/reason, and never silently downgrade. Pass depth, reason, and Notes path to workers/verifiers.
5. Run readiness and dispatch the largest safe ready batch with resolved role models and pointer packets. Preserve
   contract, roots/refs, package state, approvals, decisions, and evidence. For unresolved empirical facts, use
   `empirical-spike` under the loaded bounded-attempt contract; accept reports only after identity, provenance,
   method, bounds, limitations, and cleanup validate. Route plan defects with accepted reports or explicit `none`.
6. On package return, load `references/package-integration-gates.md`. Re-run every executable frozen checklist item
   into the declared result; failed/skipped/missing re-run is automatic FAIL. Dispatch the independent verifier only
   for an `enhanced` package and checklist-invisible defects. Apply `../../references/package-lifecycle.md`.
7. Route plan-owned defects through continuation/focused review. Dispatch one worker per coherent blocking code
   cluster using `references/repair-agent-contract.md` through `references/package-dispatch.md`. Carry the shared
   repair budget and progress/round history through each gate; reassess stalled diagnosis rather than retry unchanged.
   After repair, refresh only affected evidence and focused seams. Reuse command output only for
   equivalent code/artifact state, cwd, environment/data, isolation/order, and evidence mapping.
8. Treat package `done` as local evidence. Merge accepted package refs once through the integration worktree, close
   post-merge semantic freshness, and stabilize local commits. Apply the selected source policy: non-due or
   `local-only` runs no network action and cannot block locally verified downstream readiness; a due remote gate uses
   the loaded scheduled push and requires remote SHA = integration `HEAD`, otherwise stops with safety nets retained.
9. At final readiness, integrate all packages, run SPEC Acceptance, validate final state, and freeze exact integrated
   code/artifact/runtime evidence. Invoke sibling `review-code` and `audit` on that same freeze and require CLEAN/PASS.
   Audit must be an independent cold reconciliation of all retained/refreshed evidence, widening into code only when
   triggered by missing, stale, contradictory, risk-significant, or acceptance-critical claims; review/audit outputs do
   not become freeze inputs or replace each other.
10. Route final plan blockers before code repair, refresh affected package/seam/feature evidence, and create a new
    freeze. Carry the same remaining repair time/deadline into review/closure and audit. Focused review-code Fix
    Verification may restore CLEAN; one fresh cold auditor must still issue same-freeze PASS. Apply the
    source-publication final push/catch-up for every approved remote cadence to that CLEAN+PASS freeze; `local-only` stays network-free. Notify the user with checklist/Acceptance evidence, packages
    merged, review/audit state, publication state, advisories, and rerunnable checks.

## Load if needed

- User approval boundary → `references/execution-contract.md`
- Feature source cadence or scheduled push → `../../references/source-publication.md`
- First bounded attempt or stop report → `../../references/bounded-attempts.md`
- Any plan-artifact amendment → `../../references/plan-amendments.md`
- Package/repair/verifier selection or packet → `references/package-dispatch.md`
- Package completion/integration/final handoff → `references/package-integration-gates.md` and
  `../../references/package-lifecycle.md`
- Package worker → pass `references/package-agent-contract.md`
- Repair worker → pass `references/repair-agent-contract.md`
- Enhanced verifier → pass `references/package-verification.md`
- Artifact roles → `../../references/slice-first-artifacts.md`
- Slice authority dispute → `../../references/conceptualize-slice-authority.md`
- Worktree creation, push, merge, cleanup, or teardown → invoke `worktree`

## Stop if

- New semantic authority is needed: requirement/scope/visible behavior, risk acceptance, manual exception, or any
  protected/out-of-contract/destructive/external action not explicitly approved.
- Credentials/external facts are unavailable; artifact/code/ref/worktree state is unsafe, contradictory, or unowned;
  or an executable acceptance check lacks authority/bounds.
- A due source-publication gate has network, credential, non-fast-forward, or remote-SHA failure. Non-due or
  `local-only` source gates are not stops.
- The loaded bounded-work contract stops for non-convergence, exhausted repair time, or an exhausted empirical
  question. Preserve its stop evidence; do not buy more rounds by changing agents, clusters, or stages.

Everything else inside the contract—changed empirical follow-ups, same-requirement continuation/focused review,
routine test failures, bounded code repairs, reruns, verification, and local integration—is handled autonomously.

## Output

Return delivery/stop status, package checklist and feature Acceptance evidence, merged packages, risk-depth Notes,
empirical/repair state, sibling same-freeze review/audit results, advisories, source/sidecar/target publication state,
exact stop evidence when applicable, and next step.
