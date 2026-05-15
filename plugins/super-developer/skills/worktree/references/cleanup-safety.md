# Cleanup Safety

Use this reference before removing worktrees, deleting branches, pushing a feature branch for review, merging to `main`, or doing final teardown. Cleanup must protect unmerged work first.

## Pre-Cleanup Merge-Base Checks

From the integration worktree for the target feature:

```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git merge-base --is-ancestor task/<feature>/<WP-ID> HEAD
```

Interpretation:

- Exit 0: the package branch is an ancestor of the integration branch HEAD and may be eligible for cleanup.
- Non-zero: stop cleanup for that package branch/worktree. It is not proven integrated.

Check every package branch individually. Do not delete a batch if any member fails its merge-base check.

Example for two package branches:

```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git merge-base --is-ancestor task/<feature>/WP1 HEAD
git merge-base --is-ancestor task/<feature>/WP2 HEAD
```

Only package branches with successful checks can be removed.

## Package Worktree and Branch Removal

After a package branch is proven integrated into `feature/<feature>`:

```bash
cd "$PROJECT_ROOT"
git worktree remove .worktrees/<feature>/wp-<WP-ID>
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git branch -d task/<feature>/<WP-ID>
```

Run `git branch -d` from the feature integration worktree so Git checks merge status against `feature/<feature>` rather than root `main`. Use force deletion only for explicitly disposable spike branches or when the orchestrator has separately proven the branch is redundant and safe to discard.

Do not remove the feature integration worktree at this stage. It is the safety-net checkout for verification, review updates, final merge, and rollback while the feature is not fully merged and pushed.

## Push and Merge-to-Main Separation

Pushing a feature branch publishes review/test state only:

```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git push -u origin feature/<feature>
```

This is not approval to merge to `main`. Never infer merge approval from:

- "push it"
- "looks good"
- successful tests/builds
- remote branch creation
- review requested

Proceed to merge `feature/<feature>` to `main` only when the user explicitly says to merge to `main` or gives equivalent unambiguous approval for that exact action.

## Pre-Main-Merge Safety Checks

Before an approved merge to `main`:

```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git status
git log --oneline -5
```

The integration worktree must be clean and must contain the intended package merges. Resolve any uncertainty before merging.

After approval, merge from the root worktree while leaving the integration worktree in place:

```bash
cd "$PROJECT_ROOT"
git merge --no-ff feature/<feature> -m "feat: <feature> -- <summary>"
git push
```

The merge and push are one safety boundary. If push fails, keep the integration worktree and feature ref until the remote state is resolved.

## Final Cleanup Rules

Only after the authorized merge to `main` and push are complete:

```bash
cd "$PROJECT_ROOT"
git worktree remove .worktrees/<feature>/merge
git branch -d feature/<feature>
rmdir .worktrees/<feature>
```

Final cleanup rules:

- Never remove safety-net worktrees before merge and push complete.
- Never delete a package branch before its merge-base check proves it is included.
- Never delete another active feature namespace while cleaning up the current feature.
- If cleanup fails because a worktree is dirty, stop and inspect; do not force-remove by default.
- If cleanup fails because a branch is not merged, keep it and resolve ancestry/integration first.
- Remote branch deletion is a separate policy decision; do not assume local cleanup means remote deletion.

## Bugfix, Hotfix, and Spike Cleanup

Feature bugfix branches should be merged into `feature/<feature>` and checked with merge-base before removal:

```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git merge-base --is-ancestor bugfix/<name> HEAD
```

Production hotfix worktrees stay until the hotfix merge to `main` and push complete:

```bash
cd "$PROJECT_ROOT"
git worktree remove .worktrees/hotfix-<name>
git branch -d hotfix/<name>
```

Spike branches are disposable only if their evidence and durable changes have been captured elsewhere:

```bash
cd "$PROJECT_ROOT"
git worktree remove .worktrees/spike-<name>
git branch -D spike/<name>
```

Do not use spike cleanup rules for package, bugfix, hotfix, or feature branches.
