# Cleanup Safety

Use this reference before removing worktrees, deleting branches, pushing a feature branch for review, merging into any target branch, or doing final teardown. Cleanup must protect unmerged work first.

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

Run `git branch -d` from the feature integration worktree so Git checks merge status against `feature/<feature>` rather than the root worktree's current branch. Use force deletion only for explicitly disposable spike branches or when the orchestrator has separately proven the branch is redundant and safe to discard.

Do not remove the feature integration worktree at this stage. It is the safety-net checkout for verification, review updates, final merge, and rollback while the feature is not fully merged and pushed.

## Push and Merge-to-Target Separation

Pushing a feature branch publishes review/test state only:

```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git push -u origin feature/<feature>
```

If this exact `origin feature/<feature>` push was listed in the approved implement Execution Contract, it needs no second approval prompt. If it was omitted, the remote/ref changes, or force/delete/tag/release/target-branch push is needed, stop for explicit approval. This feature-branch push is not approval to merge into `main`, push `main`, or update any other `<target-ref>`. Never infer merge approval from:

- "push it"
- "looks good"
- successful tests/builds
- remote branch creation
- review requested

Proceed to merge `feature/<feature>` into `<target-ref>` only when the user explicitly names or approves that exact target branch.

## Pre-Target-Merge Safety Checks

Before an approved merge into `<target-ref>`:

```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git status
git log --oneline -5
```

The integration worktree must be clean and must contain the intended package merges. Resolve any uncertainty before merging.

Merge from a worktree that is already on `<target-ref>`. Never switch the root worktree to make this true. If no existing worktree is on `<target-ref>`, create a temporary target-merge worktree:

```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/<feature>/target-merge <target-ref>
cd .worktrees/<feature>/target-merge
git merge --no-ff feature/<feature> -m "feat: <feature> -- <summary>"
git push origin <target-ref>
```

If `<target-ref>` is already checked out in the root or another worktree, use that existing worktree without switching it:

```bash
cd "<worktree-already-on-target-ref>"
git merge --no-ff feature/<feature> -m "feat: <feature> -- <summary>"
git push origin <target-ref>
```

The target merge and target push are one safety boundary and require explicit approval for the named `<target-ref>`; implement Execution Contract approval for feature-branch push does not cover this. If target push fails, keep the integration worktree, any target-merge worktree, and feature ref until the remote state is resolved.

## Final Cleanup Rules

Only after the authorized merge into `<target-ref>` and push are complete:

```bash
cd "$PROJECT_ROOT"
git worktree remove .worktrees/<feature>/merge
cd "<worktree-on-target-ref>"
git branch -d feature/<feature>
cd "$PROJECT_ROOT"
if [ -d .worktrees/<feature>/target-merge ]; then
  git worktree remove .worktrees/<feature>/target-merge
fi
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
cd "<worktree-on-main>"
git branch -d hotfix/<name>
cd "$PROJECT_ROOT"
if [ -d .worktrees/hotfix-merge-<name> ]; then
  git worktree remove .worktrees/hotfix-merge-<name>
fi
```

Spike branches are disposable only if their evidence and durable changes have been captured elsewhere:

```bash
cd "$PROJECT_ROOT"
git worktree remove .worktrees/spike-<name>
git branch -D spike/<name>
```

Do not use spike cleanup rules for package, bugfix, hotfix, or feature branches.
