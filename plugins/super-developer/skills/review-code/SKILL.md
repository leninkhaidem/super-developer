---
name: review-code
description: >
  Review code changes with bounded multi-agent review. Use for PR review, local diff review, or the
  planned-feature pipeline review after implementation and before audit. Do not use as final
  planned-feature completion audit or as a PR/local code-fix tool unless the selected mode explicitly
  permits fixes.
---

# Review Code

Run a bounded code-risk review, then route report/actions by mode.

## Always

- Keep ordinary PR/local reviews isolated from planned-feature Slice, proof, report, and audit obligations unless planned-feature pipeline artifacts are explicitly in scope.
- Review with one default Code Reviewer, at most one risk-triggered specialist, and Skeptic verification for every serious finding.
- Treat review-code as risk discovery and fix-loop governance; final audit remains the completeness gate.
- Never mutate code, GitHub state, lifecycle state, proof Markdown, package reports, or commits before the active mode's gated action reference allows it.
- Revalidate reviewed state before any side effect, fix verification, package evidence refresh, or audit-readiness handoff.

## Do

1. Select exactly one mode:
   - Planned-feature pipeline: explicit or inherited feature context plus `.tasks/<feature>/SPEC.md`, `tasks.json`, package/proof/report artifacts, and a feature/merge worktree state to review.
   - PR: PR URL, `owner/repo#N`, or `#N` in a repo context.
   - Local: no pipeline context and no PR identifier; review staged, unstaged, or branch diff.
2. Load the selected mode setup reference and capture immutable reviewed-state metadata.
3. Load `references/review-engine.md` and `references/finding-contract.md`; read model preferences before spawning reviewers and pass the clean-code contract path to reviewers.
4. Run discovery review, coverage reconciliation, and Skeptic verification as required by the engine.
5. Render through `references/report-template.md`, then return to the active mode reference for preview/report/action routing.
6. If an allowed local or pipeline fix batch is applied, load `references/fix-verification.md` for closure and widening decisions before any readiness action.

## Load if needed

- PR setup/report preview → `references/pr-workflow.md`; PR posting/merge gates → `references/pr-actions.md`.
- Local setup/report → `references/local-workflow.md`; local fix/commit/details gates → `references/local-actions.md`.
- Planned-feature report, package evidence gate, and audit handoff → `references/pipeline-report.md`.
- Planned-feature fix batching, proof/report freshness routing, widening, and escalation → `references/pipeline-actions.md`.
- Finding severity/output contract → `references/finding-contract.md`.
- Reviewer topology, lens coverage, batching, and Skeptic routing → `references/review-engine.md`.
- Serious-finding or risky-clean challenge → `references/skeptic-checklist.md`.
- User-facing review body → `references/report-template.md`.
- Product/architecture decision card during an allowed fix flow → `references/decision-filter.md`.
- Slice path or authority detail in pipeline mode → `../../references/conceptualize-slice-authority.md`.
- Package proof/report freshness rules in pipeline mode → `../../references/package-lifecycle.md`.

## Stop if

- The requested mode is ambiguous enough to change side-effect authority.
- PR/local review is being asked to satisfy planned-feature proof/report/audit gates; switch to pipeline mode instead.
- Reviewed state is stale, broadened, or not bound to the action being requested.
- A fix requires product/design choice, scope expansion, new dependency/service, unsafe command, credentials, external facts, or risk acceptance.
- Pipeline package proof/report freshness, review-code state, or widened verification is missing, stale, contradictory, or uncertain.

## Output

Return the mode-specific report, verdict, allowed next actions, and any blocked readiness reason. In pipeline mode, state whether review-code is audit-ready; never state final audit PASS or merge readiness.
