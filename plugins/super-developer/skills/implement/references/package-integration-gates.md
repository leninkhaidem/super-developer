# Package Integration Gates

Load after the implement Execution Contract is approved when setting up package/integration worktrees, accepting package returns, merging package branches, handling conflicts, deciding cleanup readiness, or preparing feature push readiness.

The `worktree` skill owns git command runbooks, root-worktree safety, branch/ref invariants, cleanup, feature push, and target-merge boundaries. This reference owns implement-specific gates: when package branches may merge, when proof/report evidence is fresh enough, and when package completion is allowed.

## Contract

- Invoke the `worktree` skill for worktree setup, merge commands, cleanup, feature push, target merge, and target push; do not deep-link its private references here.
- The orchestrator owns integration decisions. Package agents work only inside assigned package worktrees and do not create, merge, delete, or push branches.
- Merge each package branch at most once, only after package return checkpoint, proof validation, safe verification evidence, fresh `PASS` package verification report, and Slice plan-defect prechecks pass.
- Proof Markdown and package verification reports are task-store handoff artifacts, not package-branch source artifacts. Do not commit ignored `.tasks` proof/report files unless the plan explicitly requires tracked task artifacts.
- Merge resolution, repair, verifier findings, or post-merge changes that affect implementation evidence, proof rows, verification expectations, or package-report claims invalidate affected proof/report freshness.
- Mark a package done only after integration and freshness gates pass, not merely because the package branch merged.

## Do

1. During setup, invoke the `worktree` skill to create or operate the feature integration worktree and package worktrees. Branch packages from `<base-ref>` unless a package depends on already-merged feature work; then branch from `feature/<feature>` after prerequisites merge.
2. Before accepting a package return, apply the integration checkpoint: validate package-agent report, required `SELF_REVIEW`, proof Markdown rows, verification commands/inspections, Slice authority assessment, and plan-defect status.
3. Run `sliceproof.py validate-proof` for the package proof Markdown and require holistic package verification with a fresh durable `PASS` report before integration.
4. Before merging, confirm ignored `.tasks` proof/report artifacts were not force-added or committed to the package branch.
5. Merge accepted package branches through the integration worktree using the `worktree` skill. Keep package branches/worktrees until cleanup gates prove they are integrated.
6. After each merge, apply post-merge freshness checks, repair routing, and package-completion gates before updating status.
7. If merge resolution changes files, evidence, verification expectations, or package claims, refresh affected proof rows/reports, rerun proof validation, and rerun focused or full package verification before completion.
8. For repairs or verifier follow-up, keep the package incomplete, delegate through fresh agents, and repeat the affected proof/report/package-verification gates.
9. For package cleanup, feature push, target merge, target push, or teardown, invoke the `worktree` skill. Feature push is allowed only when the exact `origin feature/<feature>` action was listed in the approved Execution Contract; target merge/push always needs separate explicit approval.

## Conflict Handling

- Resolve conflicts only in the integration worktree; never switch the root worktree.
- Resolve and commit only trivial mechanical adjacency conflicts inline.
- For substantive logic, API, contract, test, proof, package-scope, or design conflicts, abort the merge if possible and keep the package incomplete with a blocker naming the conflicting package/files.
- Delegate in-scope repair when no product/design decision is needed.
- Do not dispatch dependent downstream packages until conflicts and freshness gates are closed.

## Stop if

- Package return, proof validation, verification evidence, package report, Slice plan-defect status, or ignored `.tasks` handling is missing, stale, unsafe, or contradictory.
- A package branch was already merged, cannot be cleanly attributed to one package, or needs substantive orchestrator edits to pass.
- A merge conflict requires product/design authority, scope expansion, new dependency/service, external facts, credentials, unsafe command, or risk acceptance.
- Cleanup, feature push, target merge, target push, branch deletion, or teardown lacks the required `worktree` skill boundary and approval state.
- Merge resolution or repair invalidates proof/report freshness and no fresh verification has closed it.

## Output

Return compact integration status:

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
