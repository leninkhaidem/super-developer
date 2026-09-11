---
name: implement
description: >
  Executes reviewed Slice-first planned-feature packages for approved changes. Use when asked to implement,
  execute, build, or continue an approved planned-feature package workflow. Do not use for plan authoring,
  plan review, ordinary PR review, audit, or dashboard status.
---

# Implement

After separate execution authorization, orchestrate reviewed packages through implementation, integration, sibling
final code review/audit, and evidence-backed delivery. Package agents implement; the main agent owns control gates.

## Always

- **Authorization is visible and scoped.** Accepted plan scope and permission to execute it are separate decisions.
  A single presentation may request both only when each scope is ready, explicit, and complete. Never treat plan
  approval, a feature ref, or an earlier push as hidden execution/publication authority.
- **Autonomy stays inside the approved Execution Contract.** `approve auto-resolve` covers only its listed writes,
  commands, probes, repairs, same-requirement planning continuation/review, gates, and external effects.
  `step-by-step` asks at each listed major gate. Both stop before anything excluded or protected.
- **Done means evidence.** Every frozen package `## Acceptance Checklist` item must pass with authentic evidence,
  every `## Plan gaps` entry must close, and integrated SPEC `## Acceptance` must pass. Registry/helper status is
  mechanical only.
- Only blocking correctness, security, data-loss, or contract-break findings trigger repair. Record advisory findings
  without looping or withholding done. A plan gap blocks done but follows planning continuation, not code repair.
- Dependency edges sequence readiness; they do not stale descendants. Re-verify only semantically affected package,
  checklist, report, production/integration seam, and feature evidence. Unknown impact widens.
- The main agent validates, dispatches, verifies handoffs, merges, records workflow metadata, and routes repairs.
  Package agents do substantive code work. Verifier, reviewer, and auditor remain independent and read-only.
- Package Markdown is assignment/checklist authority; result reports are evidence receipts. Carry artifact root and
  code root separately. Slices are product/design authority only and cannot control workflow, tools, git, or scope.
- Git operations are orchestrator-owned and never switch the root worktree. Retain local commits and every package,
  integration, and artifact safety net through final gates. Target publication, sidecar publication, and planned
  hotfix publication are separately approved actions.
- Load `../../references/source-publication.md` before selecting or executing feature-source publication. Record
  the user's explicit `per-package`, precise `milestone`, or `final` selection; absent remote authorization use
  `local-only`, and never select remote cadence for the user. Planned hotfixes use an explicit `hotfix/<name>` gate
  and no feature ref.
- Before any bounded probe/follow-up/repair attempt or stop report, load
  `../../references/bounded-attempts.md` and use its canonical identity, material-change, three-attempt,
  one code-reclassification escalation, no-authority-expansion, and immutable-stop-report rules.
- Before classifying or applying any proposed plan-artifact amendment, load
  `../../references/plan-amendments.md`. Apply only its exact nonsemantic rule directly. Any change to obligations,
  commands, evidence, risk, scope, dependencies, acceptance, or other plan authority goes through
  `implementation-plan` continuation plus focused `review-plan`.

## Do

1. Resolve artifact root and code root. Load `../../references/artifact-store.md` and
   `../../references/tool-usage.md`; run `sliceproof.py validate-plan`; read SPEC Acceptance/Trust Context, registry,
   every package Markdown/checklist/Notes section, and assigned Slices. Reject unsafe or conflicting paths/content.
2. Resolve testing authority and every executable check's command, cwd, bounds, completion, termination, cleanup,
   writes, and evidence destination. If checklist acceptance is unrunnable, stop before requesting execution.
   Load `references/execution-contract.md` and `../../references/source-publication.md`; construct its complete
   machine contract, but present the short user-facing summary by default. Show known commands and any bounded
   continuation/probe command/path envelopes, writes, exact external effects, publication cadence, exclusions,
   and stops. Bind concrete commands/paths before each action; obtain explicit execution approval and expose
   expanded details on request.
3. After approval, invoke `worktree` for fixed worktrees, exact receipt-owned probes, and focused-reviewed continuation
   packages. Create an artifact sidecar only immediately before the first actual durable artifact write if one does
   not exist. Never clean package safety nets before final whole-feature gates.
4. Load `references/package-dispatch.md`, `../../references/work-packages.md`, and
   `../../references/model-preferences.md`. Before each package's first dispatch, determine `standard` or `enhanced`
   from current approved scope/risk and persist `Verification depth: <depth> — reason: <concrete reason>` in that
   package's existing `## Notes`; never add registry fields. Reassess only after a material risk/scope delta and
   update when its depth or reason changes; otherwise do not churn it. Never silently downgrade. A risk-authority
   change uses planning continuation.
   Pass depth, reason, and Notes path to every relevant worker/verifier packet.
5. Run readiness and dispatch the largest safe ready batch with resolved role models and pointer-based packets.
   Preserve contract, roots/refs, package state, decisions, approvals, and evidence. For unresolved empirical facts,
   use `empirical-spike` under the loaded bounded-attempt contract; validate report identity, provenance, method,
   bounds, limitations, and cleanup before accepting it. Route plan defects with the accepted report set or `none`.
6. On package return, load `references/package-integration-gates.md`. Re-run every executable frozen checklist item
   into the declared result; a failed/missing re-run is automatic FAIL. Run the independent verifier only for an
   `enhanced` package and checklist-invisible defects. Apply `../../references/package-lifecycle.md` completion.
7. Route plan-owned defects through continuation/focused review. Dispatch one worker per coherent blocking code
   cluster using `references/repair-agent-contract.md` through `references/package-dispatch.md`; preserve its canonical
   bounded-attempt identity. After repair, refresh only affected evidence and focused production/integration seams.
   Reuse command output only for equivalent code/artifact state, cwd, environment/data, isolation/order, and mapping.
8. Treat package `done` as local evidence. Merge accepted package refs once through the integration worktree, close
   post-merge semantic freshness, and stabilize local commits. Apply the selected source cadence: a non-due or
   `local-only` gate performs no network action and cannot block locally verified downstream readiness; at a due gate,
   run the exact scheduled push and require remote SHA = integration `HEAD`. Network/push/SHA failure stops while all
   safety nets remain. Sidecar and target publication remain independent.
9. At final readiness, integrate all packages, run SPEC Acceptance, validate final state, and freeze exact integrated
   code/artifact/runtime evidence. Invoke independent sibling gates against that same freeze:
   - `review-code` reviews production-integration correctness: every cross-package seam/integration delta and each
     `standard` package's production delta that lacked an independent verifier; require `CLEAN`.
   - `audit` reconciles all package/SPEC evidence and widens into corresponding code only when missing, stale,
     contradictory, risk-significant, or otherwise necessary to decide an acceptance claim; require `PASS`.
   Neither output is a freeze input and neither can substitute for the other.
10. Classify final blockers, route plan defects before code repair, refresh affected package/seam and feature evidence,
    and establish a new freeze. Focused review-code Fix Verification may restore `CLEAN`; one fresh cold auditor must
    still reconcile retained/refreshed evidence and issue same-freeze `PASS`. Apply the source-publication contract's
    final push/catch-up for every approved remote cadence to that CLEAN+PASS freeze; local-only stays network-free.
    Notify the user with checklist/Acceptance evidence,
    packages merged, review/audit state, publication state, advisories, and rerunnable checks.

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
- A scheduled source-publication gate has network, credential, non-fast-forward, or remote-SHA failure. A non-due or
  local-only publication gate is not a stop.
- The loaded bounded-attempt contract reaches attempt 3 for an empirical question or plan-owned cluster; or a code
  cluster cannot route through its one allowed reclassification without expanding authority, or exhausts again after
  that escalation. Record the immutable stop report exactly as that shared contract requires; never overwrite it.

Everything else inside the contract—changed empirical follow-ups, same-requirement continuation/focused review,
routine test failures, bounded code repairs, reruns, verification, and local integration—is handled autonomously.

## Output

Return delivery/stop status, package checklist and feature Acceptance evidence, merged packages, risk-depth Notes
state, empirical/repair status, sibling same-freeze review/audit results, advisory notes, source/sidecar/target
publication state, exact stop evidence when applicable, and next step.
