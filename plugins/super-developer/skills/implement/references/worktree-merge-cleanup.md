# Implement Worktree Delivery Deltas

Load after the `worktree` skill at implement Steps 4/7. Worktree references own lifecycle safety and command runbooks; this file owns implement-only sequencing: proof gates before merges, package verification timing, conflict handling, and status output.

## Canonical Owners

- `skills/worktree/SKILL.md` — root-worktree protection, branch/ref invariants, push-vs-target-merge boundary, router.
- `skills/worktree/references/feature-package-workflow.md` — feature/package/integration creation commands, package branch naming, dependency examples, feature push command shape.
- `skills/worktree/references/cleanup-safety.md` — merge-base cleanup, package worktree/branch removal, target merge/push approval, final teardown.
- This file — when implement calls those runbooks and which package proof/report gates must pass first.

## Naming Contract

Use the worktree naming contract:

- refs: `<base-ref>`, `feature/<feature>`, `<target-ref>`;
- package: `.worktrees/<feature>/wp-<WP-ID>` on `task/<feature>/<WP-ID>`;
- integration: `.worktrees/<feature>/merge` on `feature/<feature>`.

`task/<feature>/<WP-ID>` keeps the compatibility `task/` prefix; `<WP-ID>` is a work package ID.

## Mandatory Local Gates

- Root worktree is user-owned: never switch it or assume `main`/`<target-ref>`.
- Package agents stay in assigned package worktrees; the orchestrator owns worktree/branch creation and merges.
- Merge each package branch at most once, after `SELF_REVIEW`, proof Markdown validation, package verification PASS/report creation, and Slice plan-defect prechecks pass.
- Before package worktree/branch removal, load `cleanup-safety.md` and pass its `git merge-base --is-ancestor` gate.
- Feature push is allowed only when the exact `origin feature/<feature>` action was listed in the approved implement Execution Contract; otherwise stop for approval.
- Never merge into or push `<target-ref>`/`main` without explicit approval for that exact target.
- Keep `.worktrees/<feature>/merge` through final validation, review-code audit readiness, audit, feature push, and any approved target-merge/push boundary.

## Setup and Package Worktrees

Use `feature-package-workflow.md` for commands. Implement deltas:

1. Create `feature/<feature>` from explicit `<base-ref>` as a ref, not a root checkout.
2. Create one package worktree/branch per work package, not per task.
3. Branch from `<base-ref>` unless the package needs earlier merged feature output; then branch from `feature/<feature>` after prerequisites merge.
4. Package agents may commit per task ID or coherent package milestone when applicable; the orchestrator merges the package branch once.

Stop for approval if a needed worktree side effect is outside the canonical runbooks.

## Integration Merge Gate

Before merging a package branch into `.worktrees/<feature>/merge`:

1. Validate package agent report, required `SELF_REVIEW`, proof Markdown rows, verification commands/inspections, and Slice authority assessment via `integration-checkpoint.md`.
2. Run `sliceproof.py validate-proof` for the package when using v4 proof Markdown; for legacy proof JSON, use the compatibility validation path from `tool-usage.md`.
3. Run or confirm holistic package verification PASS and durable report creation before accepting the package for integration.
4. Confirm ignored `.tasks` proof/report artifacts were not force-added or committed; hand proofs and reports through the task store, not package branch merges.
5. Merge one package branch using `feature-package-workflow.md`.
6. Return to `integration-checkpoint.md` for post-merge freshness checks, repair routing, and package-completion gates. If merge resolution changes package evidence, rerun affected proof validation/package verification before marking the package done.

Do not mark a package done merely because the package branch merged.

## Conflict Handling

If merge conflicts appear in the integration worktree:

1. Inspect/resolve only there; never switch the root worktree.
2. Resolve and commit only trivial mechanical adjacency conflicts.
3. For substantive logic/API/schema/design conflicts, run `git merge --abort`, keep the package incomplete with a blocker naming the conflicting package/file(s), or delegate in-scope repair when no design decision is needed.
4. Do not dispatch dependent downstream packages until resolved.
5. Any merge-resolution edit that can affect proof rows, verification expectations, or package verification freshness invalidates the affected package proof/report and requires refresh/re-verification.

The orchestrator may resolve mechanical merge/status artifacts only; substantive production/test/docs fixes are delegated.

## Cleanup, Push, and Target Merge

Do not duplicate cleanup or target-merge commands here. Load `cleanup-safety.md` before removing worktrees, deleting branches, pushing the feature branch, merging into any target branch, or final teardown.

Safety reminders:

- Failed merge-base check keeps the package worktree/branch.
- Run branch deletion from the integration worktree or cleanup-safety-prescribed target worktree, not root.
- Feature push publishes review/testing state only; target merge/push still needs explicit target approval.
- Target merge and target push are one approval boundary; keep the integration/safety-net worktree until complete.

## Status Output

Report compactly:

```text
Integrated packages: ✅ WP1 merged; ⏸ WP2 kept for repair/verification
Proofs: ✅ WP1 validate-proof PASS
Package verification: ✅ WP1 PASS report=.tasks/<feature>/reports/WP1.package-verification.md
Cleanup: ✅ WP1 removed after merge-base proof; ⏸ WP2 kept
Integration worktree: kept at .worktrees/<feature>/merge
```

Blocked conflict report:

```text
🚫 WP3 blocked — substantive merge conflict with WP2 in <file>
Next: repair package or user decision before downstream dispatch.
```
