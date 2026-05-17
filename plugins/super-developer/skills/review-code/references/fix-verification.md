# Shared Fix Verification Review

Load this reference only after a mode that is allowed to change code has applied a delegated fix batch. Pipeline and local modes use it after their mode-specific state gates pass. PR mode is report-only for code changes and must not load this reference to create a code-fix path.

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

`partially_closed`, `not_closed`, and `reopened` are non-closed verdicts. They block readiness and must route to the mode-specific fix, widening, escalation, or authority-boundary flow.

## Regression Sniff

Check only the fix delta and surfaces affected by that delta. The required sniff covers serious regressions in security, privacy, safety, data integrity, failure modes, compatibility, public API, schema, concurrency, and performance when those surfaces are touched or plausibly affected.

Report a new issue from this phase only when it is a serious regression introduced by the fix or when it is required to explain a widening trigger. Do not report unrelated cleanup, suggestions, or pre-existing discovery issues as fix-verification findings.

## Non-Discovery Boundary

The reviewer must not rediscover the whole feature by default, search unrelated modules for fresh findings, or turn suggestions into a separate loop. If the reviewer notices a serious risk outside the assigned fix delta, it reports the smallest applicable widening trigger and affected scope; the orchestrator decides whether to run targeted widened verification or a full rereview under the mode-specific governance rules.
