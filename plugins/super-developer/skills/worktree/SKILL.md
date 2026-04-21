---
name: worktree
description: >
  Git worktree strategy for branch-isolated development. Use this skill when the user wants to
  work with git worktrees, implement a feature with branch isolation, do a bug fix in an isolated
  branch, apply a hotfix, or manage feature branches. Triggers on phrases like "use worktrees",
  "worktree", "branch isolation", "feature branch workflow", "bugfix branch", "hotfix",
  "isolated branch", "worktree setup". Also used by the implement skill for git infrastructure.
---

# Git Worktree Strategy

A branch-isolated, agent-managed git workflow using worktrees. Designed for AI coding agents that manage all git operations on behalf of the user.

---

## Golden Rule

**The main working tree always stays on `main`.** The user never runs manual git commands. The agent manages everything: worktrees, branches, merges, cleanup, and push.

## Setup

Resolve the project root once at the start of every session:

```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel)
```

## Directory Layout

All worktrees live under `.worktrees/` from the project root. Add `.worktrees/` to `.gitignore`.

```
project/                                  <- main repo, ALWAYS on 'main'
+-- .worktrees/
|   +-- auth/                             <- feature namespace
|   |   +-- task-login/                   <- task worktree (branch: task/auth/login)
|   |   +-- task-signup/                  <- task worktree (branch: task/auth/signup)
|   |   +-- merge/                        <- merge worktree (branch: feature/auth)
|   +-- search/                           <- another feature namespace
|   |   +-- task-indexer/                 <- (branch: task/search/indexer)
|   |   +-- merge/                        <- (branch: feature/search)
|   +-- bugfix-null-check/                <- bugfix worktree
|   +-- hotfix-crash-on-load/             <- hotfix worktree (urgent, off main)
+-- src/
```

## Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/<name>` | `feature/auth` |
| Task | `task/<feature>/<task>` | `task/auth/login` |
| Bugfix | `bugfix/<name>` | `bugfix/null-check` |
| Hotfix | `hotfix/<name>` | `hotfix/crash-on-load` |

Feature-namespaced task branches prevent collisions when multiple features use identical task names.

## Core Rules

1. **`main` never switches.** No `git checkout` in the project root -- ever.
2. **Feature branches are refs, not worktrees.** Create them with `git branch`, never `git worktree add`. This keeps them unlocked -- available for merging and testing from any worktree.
3. **All development happens in worktrees.** Task, bugfix, and hotfix branches each get their own worktree under `.worktrees/`.
4. **A branch checked out in a worktree is locked.** Git prevents the same branch from being checked out in two places. Keeping feature branches as refs avoids this lock.
5. **Bugfixes branch off their relevant context.** A bugfix for a feature branches off that feature ref. A hotfix for production branches off `main`.

---

## Feature Workflow

### Step 1 -- Create feature branch (ref only)

```bash
git branch feature/<name> main
```

No worktree. The feature branch is a ref that task branches merge into.

### Step 2 -- Create task worktrees

**For independent tasks (no dependencies between them):**

```bash
git worktree add .worktrees/<feature>/task-<task> -b task/<feature>/<task> main
```

Each task branches from `main` and works in isolation.

**For dependent tasks (needs earlier work):**

```bash
# Merge earlier tasks into the feature ref first, then:
git worktree add .worktrees/<feature>/task-<task> -b task/<feature>/<task> feature/<feature>
```

Branching from the feature ref gives the task access to all previously merged work.

### Step 3 -- Work in task worktrees

All code changes happen inside `.worktrees/<feature>/task-<task>/`. Commit normally within each worktree.

### Step 4 -- Merge tasks into feature branch

Create a merge worktree to integrate all completed task branches:

```bash
# Create merge worktree on the feature branch
git worktree add .worktrees/<feature>/merge feature/<feature>
cd .worktrees/<feature>/merge

# Merge each task branch
git merge task/<feature>/login --no-edit
git merge task/<feature>/signup --no-edit
```

### Step 5 -- Test on the integrated feature branch

```bash
cd .worktrees/<feature>/merge
# Run tests, linting, build validation
# NEVER merge to main until tests pass on the feature branch.
```

### Step 6 -- Clean up task worktrees (after merge to feature)

Once all task branches are merged into the feature branch, their worktrees are redundant.

**Pre-cleanup verification (mandatory):**

```bash
cd .worktrees/<feature>/merge

# Verify each task branch is an ancestor of the feature branch HEAD
git merge-base --is-ancestor task/<feature>/login HEAD && echo "merged" || echo "NOT MERGED"
git merge-base --is-ancestor task/<feature>/signup HEAD && echo "merged" || echo "NOT MERGED"
# ALL must print "merged" before proceeding
```

**Only if ALL verify as merged:**

```bash
cd $PROJECT_ROOT

# Remove task worktrees
git worktree remove .worktrees/<feature>/task-login 2>/dev/null
git worktree remove .worktrees/<feature>/task-signup 2>/dev/null

# Delete task branches (no longer needed)
git branch -D task/<feature>/login task/<feature>/signup 2>/dev/null
```

**KEEP the merge worktree** -- it holds the feature branch checkout needed for the merge-to-main step.

### Step 7 -- Push feature branch for review / testing

```bash
cd .worktrees/<feature>/merge
git push -u origin feature/<feature>
```

"Push to remote" means push the **feature branch only**. It does NOT mean merge to main. These are separate steps.

### Step 8 -- Wait for user approval

Do NOT merge to main until the user explicitly says "merge to main" or gives equivalent clear confirmation. "Looks good", "it works", or "push to remote" do NOT authorize a merge.

### Step 9 -- Safety check (before merge)

```bash
cd .worktrees/<feature>/merge
git status                    # must be clean -- no uncommitted changes
git log --oneline -5          # confirm all task merges are present
```

Only proceed if both checks pass.

### Step 10 -- Merge into main

```bash
cd $PROJECT_ROOT
git merge --no-ff feature/<feature> -m "feat: <feature> -- <summary>"
git push
```

`--no-ff` is mandatory -- it preserves sub-task commit history for traceability and `git bisect`. Use `git log --first-parent --oneline` for a clean feature-level view.

### Step 11 -- Final cleanup

```bash
# Remove merge worktree (last remaining worktree)
git worktree remove .worktrees/<feature>/merge

# Remove feature namespace directory if empty
rmdir .worktrees/<feature> 2>/dev/null

# Delete feature branch
git branch -d feature/<feature>
```

NEVER remove any worktree before the merge to main is complete and pushed.

---

## Bugfix Workflow

### Bugfix against a feature (non-urgent)

When the bug relates to an in-progress feature:

```bash
# Create bugfix worktree off the feature ref
git worktree add .worktrees/bugfix-<name> -b bugfix/<name> feature/<feature>
cd .worktrees/bugfix-<name>
# fix, commit, test
```

Merge back into the feature ref:

```bash
git worktree add .worktrees/merge-bugfix-<name> feature/<feature>
cd .worktrees/merge-bugfix-<name>
git merge bugfix/<name> --no-edit
cd $PROJECT_ROOT
git worktree remove .worktrees/merge-bugfix-<name>
# Clean up bugfix worktree + branch after merge to main is complete
```

### Hotfix against main (urgent / production)

When the bug is in production and needs to land on `main` directly:

```bash
# Create hotfix worktree off main
git worktree add .worktrees/hotfix-<name> -b hotfix/<name> main
cd .worktrees/hotfix-<name>
# fix, commit, test
```

Merge to main:

```bash
cd $PROJECT_ROOT
git merge --squash hotfix/<name>
git commit -m "hotfix: <name> -- <summary>"
git push
git worktree remove .worktrees/hotfix-<name>
git branch -d hotfix/<name>
```

After a hotfix lands on `main`, propagate to any active feature refs:

```bash
git worktree add .worktrees/merge-hotfix-propagate feature/<feature>
cd .worktrees/merge-hotfix-propagate
git merge main --no-edit
cd $PROJECT_ROOT
git worktree remove .worktrees/merge-hotfix-propagate
```

---

## Multi-Phase Dependencies

When later phases depend on earlier phases' changes:

**Independent tasks within the same phase** can branch from `main` -- they don't need each other's work.

**Dependent tasks** must branch from the feature ref (which has earlier phases merged):

```bash
git worktree add .worktrees/<feature>/task-<task> -b task/<feature>/<task> feature/<feature>
```

Never assume a worktree branched from `main` sees feature branch changes.

```
WRONG (missing earlier work):
main --- task-phase2 (branches from main, missing Phase 1)
  +-- feature/<feature>
        +-- Phase 1 merged here

RIGHT (has earlier work):
main
  +-- feature/<feature>
        +-- Phase 1 merged here
        +-- task-phase2 (branches from feature, has Phase 1)
```

## Concurrent Features

Multiple features run concurrently without collision because:

- The main working tree stays on `main` -- never switches branches
- Each feature has its own namespace: branches under `task/<feature>/`, worktrees under `.worktrees/<feature>/`
- `.worktrees/` is gitignored
- Clean up only your feature's worktrees -- other features may be active

---

## Rules Summary

| Rule | Rationale |
|------|-----------|
| Never `git checkout` in the main working tree | Prevents accidental branch switches in the shared root |
| Feature branches are refs, not worktrees | Keeps them unlocked for merging from any worktree |
| `--no-ff` for feature merges to main | Preserves sub-task history for bisect and traceability |
| `--squash` for hotfix merges to main | Keeps main history clean for urgent fixes |
| Verify with `merge-base --is-ancestor` before cleanup | Prevents deleting unmerged work |
| Never remove worktrees before merge+push to main | Worktrees are your safety net if something goes wrong |
| Never merge to main without explicit user approval | "Push to remote" != "merge to main" |
| Push feature branch first, merge to main separately | Allows user review/testing before integration |
