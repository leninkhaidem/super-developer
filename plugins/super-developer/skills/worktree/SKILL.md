---
name: worktree
description: Git worktree strategy for branch-isolated development. Use for planned-feature package work, isolated bugfixes, hotfixes, spikes, or worktree cleanup. Do not use for direct implementation without an approved worktree action.
---

# Git Worktree Strategy

Protect the user-owned root worktree while using branch-isolated `.worktrees/` checkouts for package, bugfix, hotfix, spike, integration, and target-merge work.

## Always

- Never switch the root worktree's branch. Resolve `PROJECT_ROOT=$(git rev-parse --show-toplevel)` and operate under `$PROJECT_ROOT/.worktrees/`.
- Feature branches are refs, not root checkouts. Create `feature/<feature>` from an explicit `<base-ref>` and use `.worktrees/<feature>/merge` for integration.
- Planned-feature package branches use `wp/<feature>/<WP-ID>` with worktrees at `.worktrees/<feature>/wp-<WP-ID>`.
- Base and target refs are explicit. Defaults are `main`; stacked features may use another feature branch.
- Package branches are removed only after `git merge-base --is-ancestor` proves they are included in the integration HEAD.
- Feature push and target merge/push are separate approval boundaries. Never merge or push `<target-ref>`/`main` without explicit approval for that exact target.
- Keep integration/safety-net worktrees until the authorized merge/push boundary is complete.

## Do

1. Identify the active workflow and load only its playbook.
2. For planned features, create/operate package and integration worktrees from the playbook; package agents never create worktrees or branches.
3. Before cleanup, feature push, target merge, or final teardown, load cleanup safety and run its checks.
4. Stop instead of forcing branch deletion, worktree removal, target merge, or remote action when merge proof, approval, or clean state is missing.

## Load if needed

- Planned feature/package commands → `references/feature-package-workflow.md`
- Bugfix, hotfix, or diagnostic spike commands → `references/bugfix-hotfix-workflow.md`
- Cleanup, branch removal, feature push, target merge, or teardown → `references/cleanup-safety.md`

## Planned Feature Contract

- Base ref: `<base-ref>`.
- Feature ref: `feature/<feature>`.
- Target ref: `<target-ref>`.
- Package worktree: `.worktrees/<feature>/wp-<WP-ID>`.
- Package branch: `wp/<feature>/<WP-ID>`.
- Integration worktree: `.worktrees/<feature>/merge` checking out `feature/<feature>`.

Merge-base cleanup check:

```bash
git merge-base --is-ancestor wp/<feature>/<WP-ID> HEAD
```

## Stop if

- The root worktree would need a branch switch.
- `.worktrees/` is not ignored and cannot be safely ignored.
- A branch is already checked out elsewhere and the playbook does not provide a safe alternative.
- Merge-base proof fails for a package branch cleanup.
- A feature push was not named in the approved Execution Contract, or a target merge/push lacks exact explicit approval.
- Cleanup would remove another active feature namespace or a dirty/unmerged safety-net worktree.
