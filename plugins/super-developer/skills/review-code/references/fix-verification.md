# Shared Fix Verification Review

Load only after local or pipeline mode has applied a delegated fix batch. PR mode is report-only for code changes and does not load this reference.

Fix Verification Review is a closure gate, not a second discovery review. It proves whether assigned confirmed findings are closed by the fix delta and whether that delta introduced serious regressions on affected surfaces.

## Inputs

Provide:

- original confirmed 🔴/🟠 findings with dedupe keys, Skeptic verdicts, evidence, recommendations, and bug-class notes;
- Fix Implementer report: fix delta, touched files, checks run, attempted findings, unresolved findings, and raised widening triggers;
- pre-fix reviewed-state metadata and current post-fix state metadata;
- active mode constraints, user constraints, target paths, and exact batch boundaries;
- affected planned-feature package/proof/report context when pipeline evidence may be stale;
- enough surrounding context to verify the fix delta without reopening unrelated discovery.

## Required Output

```text
FIX_VERIFICATION
reviewed_fix_batch: <batch id, commit(s), or delta summary>
assigned_findings:
  - dedupe_key: <stable key>
    original_severity: 🔴|🟠
    verdict: closed|partially_closed|not_closed|reopened
    evidence: <file/line, behavior, command, or artifact evidence>
    remaining_or_reopened_risk: <none or exact residual risk>
    next_action: none|same_scope_fix|widened_verification|full_rereview|authority_boundary
regression_sniff:
  verdict: pass|fail
  affected_surfaces_checked: <sensitive/data/failure/public-contract/concurrency/performance surfaces actually affected>
  evidence: <concrete evidence or serious regression details>
widening_triggers: <none or exact trigger names and affected scope>
readiness: ready_for_audit|needs_fix|needs_widened_review|needs_user_authority
```

Closure verdicts:

- `closed` — the whole reported bug class/equivalence class is fixed with no serious fix-introduced regression.
- `partially_closed` — the example improved but the reported class/path/state/planned impact remains partly open.
- `not_closed` — the delta does not close the finding or lacks evidence to prove closure.
- `reopened` — a previously closed finding is failing again, reverted, or reintroduced.

Non-closed verdicts block readiness and route to the active mode's fix, widening, escalation, or authority-boundary flow.

## Strategy Changes

Do not repeat the same fix/review prompt with more tokens. The next automated attempt must change agent strength, scope split, evidence requirement, specialist lens, or verification seam.

| Failure mode | Required next strategy |
|---|---|
| Same dedupe key remains open after same-scope fix | Use stronger Fix Implementer or changed verification seam. |
| Fix patched only one example | Expand next fix packet to the full equivalence class and require scenario/table evidence. |
| Fix introduced serious regression | Use the matching specialist or stronger Fix Implementer for that surface, then rerun delta verification. |
| Finding reopened | Compare post-fix lineage, identify reverting/conflicting delta, and delegate fresh fix with regression evidence. |
| Widened verification finds same-surface serious misses | Run stronger discovery or specialist review on that affected surface. |
| Scope crosses packages or invalidates proof/report evidence | Split by package/surface and resolve freshness before audit handoff. |
| Delta too broad to isolate | Batch by semantic surface; use full rereview only when batching cannot preserve confidence. |

If no bounded verification seam remains, return `next_action: authority_boundary` and `readiness: needs_user_authority`.

## Regression Sniff

Check only the fix delta and surfaces affected by that delta. Cover serious regressions in security, privacy, safety, data integrity, failure modes, public contracts, concurrency, and performance when touched or plausibly affected.

Report a new issue only when it is a serious regression introduced by the fix or needed to explain a widening trigger. Do not report unrelated cleanup, suggestions, or pre-existing discovery issues from this phase.

## Widening Trigger Names

Use exact names with concrete evidence:

- `scope_expansion` — fix needs behavior, files, packages, or user-visible scope beyond the approved finding scope.
- `public_contract_change` — public API, CLI/user interface, storage, generated contract, or migration behavior changes.
- `sensitive_risk_surface` — security, privacy, safety, data integrity, concurrency, or performance became newly implicated.
- `cross_package_impact` — fix touches or invalidates multiple packages, package boundaries, integration assumptions, or package coverage.
- `proof_report_invalidation` — proof Markdown, package report, verification output, or audit handoff may no longer match final state.
- `large_delta` — delta is too broad to verify confidently as one isolated patch.
- `non_closed_verdict` — assigned finding is `partially_closed`, `not_closed`, or `reopened`.

Route widening to the affected surface first: delta verification, affected package/seam/surface review, proof/report refresh, package verification rerun, or specialist review. Reserve full rereview for deltas whose affected surfaces cannot be isolated or whose breadth invalidates original discovery.

## Non-Discovery Boundary

Do not rediscover the whole feature by default, search unrelated modules, reopen package internals without an assigned seam/coverage trigger, or turn suggestions into a loop. If a serious risk outside the assigned delta is noticed, report the smallest trigger and affected scope; the mode reference decides the next gate.
