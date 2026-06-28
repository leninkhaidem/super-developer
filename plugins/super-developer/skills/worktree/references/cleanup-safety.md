# Cleanup Safety

Use this reference before removing worktrees, deleting branches, pushing a feature branch, merging into a
target branch, pushing a target branch, deleting an artifact sidecar, or doing final teardown. Boundary:
protect unmerged work and enforce approval gates for destructive or remote git actions.

## Pre-Cleanup Merge-Base Checks
From the integration worktree for the target feature:
```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git merge-base --is-ancestor wp/<feature>/<WP-ID> HEAD
```
Exit 0 means that package branch may be eligible for cleanup. Non-zero means stop cleanup for that
package branch/worktree. Check every package branch individually; do not delete a batch if any member fails.

Example:
```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git merge-base --is-ancestor wp/<feature>/WP1 HEAD
git merge-base --is-ancestor wp/<feature>/WP2 HEAD
```

## Package Worktree and Branch Removal
After a package branch is proven integrated into `feature/<feature>`:
```bash
cd "$PROJECT_ROOT"
git worktree remove .worktrees/<feature>/wp-<WP-ID>
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git branch -d wp/<feature>/<WP-ID>
```
Run `git branch -d` from the feature integration worktree so Git checks merge status against
`feature/<feature>`, not the root worktree's current branch. Do not remove the feature integration or
artifact sidecar worktree at package-cleanup time; they stay available for verification, review, audit,
final merge, and artifact checkpoints.

## Push and Merge-to-Target Separation
Pushing a feature branch publishes review/test state only:
```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git push -u origin feature/<feature>
```
This exact `origin feature/<feature>` push is covered by an approved implement Execution Contract only
when named there. It does not approve target merge/push, sidecar cleanup, or any remote deletion.
Never infer merge approval from "push it", "looks good", successful checks, remote branch creation, or
review requested. Merge `feature/<feature>` into `<target-ref>` only when the user explicitly names or
approves that exact target branch.

Sidecar checkpoint pushes are separate and run only from the artifact worktree:
```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/artifacts"
git push -u origin artifacts/<feature>
```
They target only `origin artifacts/<feature>` at accepted gates; never push `main`, `feature/<feature>`,
or `wp/<feature>/<WP-ID>` as an artifact side effect.

## Pre-Target-Merge Safety Checks
Before an approved merge into `<target-ref>`:
```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git status
git log --oneline -5
git merge-base --is-ancestor feature/<feature> <target-ref>
```
The integration worktree must be clean and contain the intended package merges. If the ancestry check
exits 0, feature is already merged; skip the target merge and report the no-op. Otherwise resolve any
uncertainty before merging.

After final integrated review/audit acceptance and before target merge/cleanup, run the final sidecar
checkpoint from `.worktrees/<feature>/artifacts` so final evidence is durable on `origin artifacts/<feature>`.
Do not merge `artifacts/<feature>` into `<target-ref>` or any deliverable branch.

Merge from a worktree that is already on `<target-ref>`. Never switch the root worktree. If none exists,
create a temporary target-merge worktree:
```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/<feature>/target-merge <target-ref>
cd .worktrees/<feature>/target-merge
git merge --no-ff feature/<feature> -m "feat: <feature> -- <summary>"
git push origin <target-ref>
```
If `<target-ref>` is already checked out elsewhere, use that existing worktree without switching it.
Target merge and target push are one safety boundary and require explicit approval for the named target.
If target push fails, keep integration, artifact sidecar, target-merge worktree, and feature ref.

## Final Code Cleanup Rules
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
```
Rules:
- Never remove safety-net worktrees before merge and push complete.
- Never delete a package branch before merge-base proves it is included.
- Never delete another active feature namespace while cleaning up the current feature.
- If a worktree is dirty or a branch is not merged, stop; do not force-remove by default.
- Remote feature branch deletion is separate and must be named exactly in an approved contract.

## Artifact Sidecar Cleanup
Offer sidecar cleanup only after final target merge/push is complete. Ask the user to approve the exact
actions, either separately or as one explicit list:
- remove local artifact worktree `.worktrees/<feature>/artifacts`;
- delete local sidecar branch `artifacts/<feature>`;
- delete remote sidecar branch `origin/artifacts/<feature>`.

Treat the sidecar as active and keep it if package/integration/review/audit work remains, target push did
not complete, the artifact worktree is dirty without an approved commit/checkpoint, or another feature uses
that namespace. When cleanup is approved:
```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/artifacts"
git status --short
cd "$PROJECT_ROOT"
git worktree remove .worktrees/<feature>/artifacts
cd "<worktree-not-on-artifacts-ref>"
git branch -D artifacts/<feature>
git push origin --delete artifacts/<feature>
```
Run only the approved subset. Local `-D` is permitted only for the exact sidecar ref after final target
merge/push approval because the orphan branch is intentionally not merged. If approved cleanup fails, stop
and report the remaining blocker; do not silently leave an approved sidecar ref/worktree behind.

## Bugfix, Hotfix, and Spike Cleanup
Feature bugfix branches should be merged into `feature/<feature>` and checked before removal:
```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git merge-base --is-ancestor bugfix/<name> HEAD
```
Production hotfix worktrees stay until the hotfix merge to `<base-branch>` and push complete:
```bash
cd "$PROJECT_ROOT"
git worktree remove .worktrees/hotfix-<name>
cd "<worktree-on-base-branch>"
git branch -d hotfix/<name>
```
Spike branches are disposable only after evidence and durable changes have been captured elsewhere:
```bash
cd "$PROJECT_ROOT"
git worktree remove .worktrees/spike-<name>
git branch -D spike/<name>
```
Do not use spike cleanup rules for package, bugfix, hotfix, feature, or artifact sidecar branches.
