# Shared Fix Verification Review

Load this reference only after a mode that is allowed to change code has applied a delegated fix batch. Pipeline and local modes use it after their mode-specific state gates pass. PR mode is report-only for code changes and must not load this reference to create a code-fix path.

This file is the canonical owner for fix-verification closure verdicts, non-closed routing,
widening trigger names, the non-discovery boundary, and repeated-attempt strategy changes. Mode
action files own only their state/side-effect gates, authority boundaries, and local stop conditions.

Fix Verification Review is a closure gate, not a second discovery review. Its job is to prove whether assigned confirmed findings are closed by the fix delta and whether the fix introduced serious regressions on affected surfaces.

## Inputs

Provide the Fix Verification Reviewer:

- Original confirmed 🔴/🟠 findings assigned to the fix batch, including stable dedupe keys, Skeptic verdicts, evidence, recommendations, and bug-class/equivalence-class notes.
- The delegated Fix Implementer report: fix delta, touched files, tests/checks run, findings attempted, unresolved findings, intentional scope changes, and any raised widening triggers.
- Pre-fix reviewed-state metadata and current post-fix state metadata.
- Approved mode constraints, user constraints, target paths, and exact fix-batch boundaries.
- Enough surrounding context to evaluate the fix delta and affected surfaces, without reopening unrelated discovery by default.
- Planned-feature task/proof context when available and relevant to whether acceptance evidence was affected.

## Required Output

Return one compact `FIX_VERIFICATION` block:

```text
FIX_VERIFICATION
reviewed_fix_batch: <batch id, commit(s), or delta summary>
assigned_findings:
  - dedupe_key: <stable key>
    original_severity: 🔴|🟠
    verdict: closed|partially_closed|not_closed|reopened
    evidence: <concrete file/line, behavior, or command evidence>
    remaining_or_reopened_risk: <none or exact residual risk>
    next_action: none|same_scope_fix|widened_verification|full_rereview|authority_boundary
regression_sniff:
  verdict: pass|fail
  affected_surfaces_checked: <security/privacy/safety/data/failure-mode/compat/API/schema/concurrency/performance surfaces actually affected by the fix>
  evidence: <concrete evidence or serious regression details>
widening_triggers: <none or exact trigger names and affected scope>
readiness: ready_for_audit|needs_fix|needs_widened_review|needs_user_authority
```

Use only these closure verdicts per assigned finding or dedupe key:

- `closed` — the fix closes the whole reported bug class/equivalence class without serious fix-introduced regression evidence.
- `partially_closed` — the exact example is improved but some of the reported bug class, path, state, or acceptance impact remains open.
- `not_closed` — the delta does not close the assigned finding or lacks enough evidence to prove closure.
- `reopened` — a finding that had been treated as closed is failing again, was reverted, or is reintroduced by the current fix lineage.

`partially_closed`, `not_closed`, and `reopened` are non-closed verdicts. They block readiness and must route to the mode-specific fix, widening, escalation, or authority-boundary flow. The reviewer should identify the failure mode precisely enough for the orchestrator to change strategy rather than repeat the same fix prompt.

## Non-Closed Routing and Strategy Changes

Non-closed verdicts and serious fix regressions are not audit-ready. Route by the smallest proven
failure mode:

| Failure mode | Required next strategy |
|---|---|
| Same dedupe key remains `not_closed` or `partially_closed` after a same-scope fix | Use a stronger Fix Implementer or changed verification seam with bug-class/equivalence-class evidence, reproduction notes, and required regression coverage. |
| Fix patched the example but missed the class of states | Expand the next fix packet to the whole equivalence class and require table-driven or scenario coverage before another Fix Verification Review. |
| Fix introduced a serious regression on an affected risk surface | Use the matching specialist or stronger Fix Implementer for that surface, then rerun delta verification for the assigned findings and regression. |
| Finding was `reopened` after prior closure | Compare post-fix lineage, identify the reverting/conflicting delta, and delegate a fresh fix with regression evidence. |
| Widened verification finds same-surface serious issues missed by discovery | Run a stronger Discovery Reviewer or specialist on that affected surface, not a whole-feature rereview by default. |
| Scope keeps expanding, crosses packages, or invalidates proofs | Split into smaller fix batches by package/surface and resolve affected proof handling before audit readiness. |
| Delta is too broad to isolate | Batch by semantic surface; use full rereview only if semantic batching cannot preserve review confidence. |

Do not repeat the same fix or review prompt with more tokens. The next automated attempt must change
agent strength, scope split, evidence requirement, specialist lens, or verification seam. If no
bounded verification seam remains, return `next_action: authority_boundary` and
`readiness: needs_user_authority` for the mode file to stop.

## Regression Sniff

Check only the fix delta and surfaces affected by that delta. The required sniff covers serious regressions in security, privacy, safety, data integrity, failure modes, compatibility, public API, schema, concurrency, and performance when those surfaces are touched or plausibly affected.

Report a new issue from this phase only when it is a serious regression introduced by the fix or when it is required to explain a widening trigger. Do not report unrelated cleanup, suggestions, or pre-existing discovery issues as fix-verification findings.

## Widening Trigger Names

Report a widening trigger only with concrete evidence. Use these trigger names when applicable:

- `scope_expansion` — the fix needs files, behavior, tasks, or user-visible scope beyond the approved finding scope.
- `public_api_or_schema_change` — public API, exported contracts, CLI/user interface, persistence schema, storage, generated contract, or migration behavior changes.
- `sensitive_risk_surface` — concrete evidence shows security, privacy, safety, data integrity, concurrency, or performance behavior changed or became newly implicated beyond the assigned closure/regression sniff.
- `cross_package_impact` — the fix touches or invalidates multiple planned-feature packages, package boundaries, integration assumptions, or final-review package coverage boundaries.
- `proof_invalidation` — package proof evidence, targeted-review receipt evidence, acceptance criteria, test evidence, or audit handoff may no longer match the final state.
- `large_delta` — the fix delta is too large or broad to verify confidently as one isolated patch.
- `non_closed_verdict` — any assigned finding receives `partially_closed`, `not_closed`, or `reopened`.

Route widening to the affected surface first: targeted delta verification, affected package/seam/surface review, proof-impact refresh, or specialist review. Integration-triggered package coverage invalidation should remain bounded to the affected seams, package proof surfaces, receipt freshness, and fix-verification delta unless those surfaces cannot be isolated. Reserve a full rereview for deltas whose affected surfaces cannot be isolated or whose breadth invalidates the original discovery review.

## Non-Discovery Boundary

The reviewer must not rediscover the whole feature by default, search unrelated modules for fresh findings, reopen package internals without an assigned seam/coverage trigger, or turn suggestions into a separate loop. If the reviewer notices a serious risk outside the assigned fix delta, it reports the smallest applicable widening trigger and affected scope with concrete evidence; the orchestrator decides whether to run targeted widened verification or a full rereview under the mode-specific governance rules. A vague sensitive-surface or package-coverage concern is not enough to reopen whole-feature or full-package discovery.
