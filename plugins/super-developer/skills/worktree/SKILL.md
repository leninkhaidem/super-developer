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

Branch-isolated, agent-managed git workflow using worktrees. This skill is the invariant contract and router; load the referenced playbook for the active mode only.

## Golden Rule

**The main/root working tree always stays on `main`.** The agent manages worktrees, branches, merges, cleanup, and push. The root worktree never switches branches: no root `git checkout`, no root branch checkout by any other command.

## Core Invariants

1. **Main/root worktree never switches branches.** Treat the project root as shared integration state. Never run `git checkout` there.
2. **Feature branches are refs, not worktrees.** Create `feature/<name>` as a branch ref; do not check it out in the root. Use a dedicated merge/integration worktree only when a feature ref must be checked out.
3. **Development happens in worktrees.** Package, bugfix, hotfix, and temporary spike changes happen under `.worktrees/`, not in the project root.
4. **Package branches are one worktree/branch per work package for planned-feature execution.** Tasks remain tracking units; work packages are the implementation/delegation unit. Do not normalize the unified pipeline around one worktree per small task.
5. **Planned-feature branch prefix stays compatible.** Package branches use `task/<feature>/<WP-ID>` even though `<WP-ID>` is a work package ID. Do not rename the prefix to `wp/`.
6. **A checked-out branch is locked.** Git cannot check the same branch out in two worktrees. Keeping feature branches as refs avoids locking them during package work.
7. **Bugfixes branch from the relevant context.** Feature bugfixes branch from the feature ref; production hotfixes branch from `main`.
8. **Cleanup is gated by merge proof.** Before removing package worktrees or branches, verify each package branch is already included with `git merge-base --is-ancestor` from the integration worktree.
9. **Push and merge-to-main are separate.** Pushing a feature branch for review/testing never authorizes a merge to `main`.
10. **Never merge to main without explicit user approval.** "Looks good", "push it", or successful tests are not approval. Proceed only when the user clearly asks to merge to `main`.
11. **Never remove safety-net worktrees before merge/push is complete.** Keep the integration/safety-net worktree until the authorized merge and push are complete; keep package worktrees until merge-base checks prove their branches are integrated.

## Reference Router

Load exactly the reference needed for the active workflow:

- **Planned feature / implementation package:** load `plugins/super-developer/skills/worktree/references/feature-package-workflow.md` for directory layout, branch naming, feature/package commands, multi-phase dependencies, and concurrent feature examples.
- **Bugfix, hotfix, or diagnostic spike:** load `plugins/super-developer/skills/worktree/references/bugfix-hotfix-workflow.md` for temporary spike, feature bugfix, production hotfix, and hotfix propagation playbooks.
- **Cleanup, branch removal, push/merge boundary, or final teardown:** load `plugins/super-developer/skills/worktree/references/cleanup-safety.md` before removing any worktree or branch, pushing for review, or merging to `main`.

## Setup Contract

Resolve the project root once at the start of a worktree-managed session:

```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel)
```

All worktrees live below `$PROJECT_ROOT/.worktrees/`. Ensure `.worktrees/` is ignored before creating worktrees.

## Planned Feature Contract

Use package-centric execution:

- Feature ref: `feature/<feature>`.
- Package worktree: `.worktrees/<feature>/wp-<WP-ID>`.
- Package branch: `task/<feature>/<WP-ID>`.
- Integration worktree: `.worktrees/<feature>/merge` checking out `feature/<feature>`.

`<WP-ID>` is a work package ID such as `WP1`; it is not a small task name. Multiple tasks inside one work package share the same package worktree and branch.

## Merge and Cleanup Gates

Before cleanup, prove every package branch to be removed is an ancestor of the integration branch HEAD:

```bash
git merge-base --is-ancestor task/<feature>/<WP-ID> HEAD
```

Only remove branches/worktrees whose merge-base check succeeds. If any check fails, stop cleanup and keep the worktree/branch.

Never merge `feature/<feature>` to `main` until the user explicitly approves that exact action. After an approved merge, push completion is part of the same safety boundary: do not remove the final integration/safety-net worktree until merge and push are complete.

## Merge Style Defaults

- Feature merge to main: use a non-fast-forward merge when explicitly approved, preserving package/task history for traceability.
- Production hotfix merge to main: use the hotfix playbook; keep urgent history compact only when the playbook/user direction calls for it.

## Concurrent Work

Concurrent features are safe only when each feature owns its namespace:

- worktrees under `.worktrees/<feature>/`
- package branches under `task/<feature>/`
- feature ref `feature/<feature>`

Clean up only the active feature's worktrees and branches. Other feature namespaces may be active.
