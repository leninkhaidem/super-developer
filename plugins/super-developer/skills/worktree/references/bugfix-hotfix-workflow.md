# Bugfix and Hotfix Workflow

Use this reference for diagnostic spikes, feature bugfixes, production hotfixes, and hotfix propagation. Root `main` still never switches branches.

## Temporary Spike Before Durable Fix

For ambiguous bugs, create a short-lived spike worktree to reproduce, instrument, and validate candidate fixes without polluting final history.

```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/spike-<name> -b spike/<name> <base-ref>
cd .worktrees/spike-<name>
# reproduce, instrument, test candidate fixes, capture evidence
```

Rules:

- Choose `<base-ref>` from the context that exhibits the bug: `main`, `feature/<feature>`, or another explicit ref.
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

Use this when the bug belongs to an in-progress feature and should land in `feature/<feature>` before the feature goes to `main`.

### Create bugfix worktree from the feature ref

```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/bugfix-<name> -b bugfix/<name> feature/<feature>
cd .worktrees/bugfix-<name>
# fix, commit, verify the focused bug scenario
```

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

After the merge, apply the cleanup-safety reference before removing the bugfix worktree or branch. Keep feature integration safety nets until feature merge/push completion.

## Production Hotfix

Use this when production is broken and the fix must land on `main` directly. Hotfixes start from `main` in their own worktree; the root worktree remains on `main` and does not checkout the hotfix branch.

### Create hotfix worktree

```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/hotfix-<name> -b hotfix/<name> main
cd .worktrees/hotfix-<name>
# fix, commit, verify the production failure path
```

### Merge hotfix to main after approval

Do not merge to `main` without explicit user approval. Once approved:

```bash
cd "$PROJECT_ROOT"
git merge --squash hotfix/<name>
git commit -m "hotfix: <name> -- <summary>"
git push
```

Keep `.worktrees/hotfix-<name>` until the merge and push complete. Then use cleanup-safety before branch/worktree removal.

## Hotfix Propagation

After a hotfix lands on `main`, propagate it to active feature refs that need the fix.

Prefer the feature's existing integration worktree:

```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git merge main --no-edit
```

If the feature has no integration worktree, create a temporary propagation worktree:

```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/merge-hotfix-propagate-<feature> feature/<feature>
cd .worktrees/merge-hotfix-propagate-<feature>
git merge main --no-edit
cd "$PROJECT_ROOT"
git worktree remove .worktrees/merge-hotfix-propagate-<feature>
```

Propagation rules:

- Resolve propagation conflicts in the feature integration/propagation worktree, never in the root worktree.
- Do not delete active feature package worktrees while propagating a hotfix.
- If a feature has already been pushed for review, push the updated `feature/<feature>` ref after propagation.
- If multiple active features exist, propagate deliberately to each affected feature; do not assume one propagation updates all feature refs.
