# Bugfix and Hotfix Workflow

Use this reference for diagnostic spikes, feature bugfixes, production hotfixes, and hotfix
propagation. Boundary: isolated bug/hotfix worktrees and non-root merge paths.

## Contract
- The root worktree is user-owned and must not be switched.
- Diagnostic spikes are temporary evidence-gathering branches, not final delivery branches.
- Feature bugfixes land back in `feature/<feature>`.
- Production hotfixes land on the approved `<base-branch>` only after explicit approval.
- For production hotfixes, `main` may be an example value for `<base-branch>`, but this workflow is not hardcoded to it.
- Hotfix propagation updates each affected feature ref deliberately.
- Branch/worktree removal is outside this playbook; use the parent skill's cleanup gate.

## Temporary Spike Before Durable Fix
For ambiguous bugs, create a short-lived spike worktree to reproduce, instrument, and validate
candidate fixes without polluting final history.
```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/spike-<name> -b spike/<name> <base-ref>
cd .worktrees/spike-<name>
# reproduce, instrument, test candidate fixes, capture evidence
```
Rules:
- Choose `<base-ref>` from the context that exhibits the bug: `<base-branch>`, `feature/<feature>`, or another explicit ref.
- Do not merge spike branches as final work.
- Extract durable evidence, regression tests, fixtures, and the minimal fix strategy.
- Remove the spike only after the durable bugfix/hotfix branch has what it needs.

Cleanup for a completed spike:
```bash
cd "$PROJECT_ROOT"
git worktree remove .worktrees/spike-<name>
git branch -D spike/<name>
```

## Feature Bugfix
Use this when the bug belongs to an in-progress feature and should land in `feature/<feature>` before
that feature merges into its approved target branch.

### Create bugfix worktree from the feature ref
```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/bugfix-<name> -b bugfix/<name> feature/<feature>
cd .worktrees/bugfix-<name>
# fix and verify the focused bug scenario; do not commit yet
```
Commit bugfix changes only after verification and CLEAN `review-code`/approved delivery; preserve the
original approval boundaries for any remote or target-ref side effects.

### Publish bugfix branch after clean review
In `diagnose-and-fix`, approved localized bugfix delivery includes this remote side effect unless
explicitly excluded. Run only after verification and clean `review-code`; if approval excluded remote
side effects or the remote/ref differs, stop for exact approval.
```bash
cd "$PROJECT_ROOT/.worktrees/bugfix-<name>"
git push -u origin bugfix/<name>
```
This branch push is not approval to merge into or push `<base-branch>`, `feature/<feature>`, or
any target ref. No other remote side effects are implied.

### Merge bugfix back into the feature ref
Use the existing feature integration worktree when available:
```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git merge bugfix/<name> --no-edit
```
If no integration worktree exists, create a temporary one for the feature ref:
```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/merge-bugfix-<name> feature/<feature>
cd .worktrees/merge-bugfix-<name>
git merge bugfix/<name> --no-edit
```
After the merge, stop before removing the bugfix worktree or branch. Keep feature integration safety
nets until feature merge and push completion.

## Production Hotfix
Use this when production is broken and the fix must land on the approved `<base-branch>` directly.
Hotfixes start from `<base-branch>` in their own worktree; do not switch the root worktree to the
hotfix branch.

### Create hotfix worktree
```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/hotfix-<name> -b hotfix/<name> <base-branch>
cd .worktrees/hotfix-<name>
# fix and verify the production failure path; do not commit yet
```
Commit hotfix branch changes only after verification, CLEAN `review-code`, and approved delivery.

### Merge hotfix to `<base-branch>` after approval
Do not merge to `<base-branch>` without explicit user approval and clean reviewed hotfix delivery.
Once approved, merge from a worktree already on `<base-branch>`; never switch the root worktree to
make that true. If no existing worktree is on `<base-branch>`, create a temporary hotfix-merge
worktree:
```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/hotfix-merge-<name> <base-branch>
cd .worktrees/hotfix-merge-<name>
git merge --squash hotfix/<name>
git commit -m "hotfix: <name> -- <summary>"
git push origin <base-branch>
```
If the root or another worktree is already on `<base-branch>`, use that existing worktree without
switching it. Keep `.worktrees/hotfix-<name>` until merge and push complete, then stop before
cleanup.

## Hotfix Propagation
After a hotfix lands on `<base-branch>`, propagate it to active feature refs that need the fix.

Prefer the feature's existing integration worktree:
```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git merge <base-branch> --no-edit
```
If the feature has no integration worktree, create a temporary propagation worktree:
```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/merge-hotfix-propagate-<feature> feature/<feature>
cd .worktrees/merge-hotfix-propagate-<feature>
git merge <base-branch> --no-edit
cd "$PROJECT_ROOT"
git worktree remove .worktrees/merge-hotfix-propagate-<feature>
```
Propagation rules:
- Resolve conflicts in the feature integration/propagation worktree, never in the root worktree.
- Do not delete active feature package worktrees while propagating a hotfix.
- If a feature has already been pushed for review, push the updated `feature/<feature>` ref after propagation.
- If multiple active features exist, propagate deliberately to each affected feature.
