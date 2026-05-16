# Implement Worktree, Merge, and Cleanup Runbook

Load this reference at implement Step 4 and Step 7 for package-scoped planned-feature worktree commands. It complements the worktree skill; the worktree skill owns global git invariants.

## Naming Contract

- Root worktree: project root, user-owned; never switch it or assume its branch.
- Base ref: `<base-ref>` (default `main`; may be `feature/<base>` for stacked features).
- Feature ref: `feature/<feature>`.
- Target ref: `<target-ref>` (default `main`; often the same as `<base-ref>` for stacked features).
- Package worktree: `.worktrees/<feature>/wp-<WP-ID>`.
- Package branch: `task/<feature>/<WP-ID>`.
- Integration worktree: `.worktrees/<feature>/merge`.

`task/<feature>/<WP-ID>` intentionally retains the compatibility `task/` prefix. `<WP-ID>` is a work package ID (`WP1`, `WP2`, ...), not an individual task ID.

## Initial Setup

Resolve the project root and keep all worktree commands rooted there:

```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel)
```

Ensure `.worktrees/` is ignored. Create the feature as a ref from the explicit base ref, not as a root checkout:

```bash
cd "$PROJECT_ROOT"
git branch feature/<feature> <base-ref>
mkdir -p .worktrees/<feature>/
```

Never run `git checkout` in the project root, and do not assume the root is on `main` or on the target branch.

## Create Package Worktrees

For packages that can start from the feature base:

```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/<feature>/wp-<WP-ID> -b task/<feature>/<WP-ID> <base-ref>
```

For packages that require earlier feature work already merged into `feature/<feature>`:

```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/<feature>/wp-<WP-ID> -b task/<feature>/<WP-ID> feature/<feature>
```

Each work package gets one worktree and one branch. The package agent may commit after each task ID, but the orchestrator merges the package branch once.

## Create the Integration Worktree

Create this when the first package batch is ready to merge, if it does not already exist:

```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/<feature>/merge feature/<feature>
cd .worktrees/<feature>/merge
```

Keep the integration worktree for subsequent package merges, final validation, review-code fixes, audit, push, and safety-net state.

## Merge Package Branches

After package reports and assigned package proof entries pass pre-merge checks:

```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git merge task/<feature>/<WP-ID> --no-edit
```

Merge one branch per package. For a package containing multiple tasks, merge only its package branch.

## Conflict Handling

If `git merge` reports conflicts:

1. Inspect conflicting files in the integration worktree.
2. If conflicts are trivial mechanical adjacency conflicts, resolve them and commit the merge resolution.
3. If conflicts are substantive overlapping logic, incompatible behavior, schema/API disagreement, or unclear design intent, abort:

   ```bash
   git merge --abort
   ```

4. Set the package's tasks to `blocked` with `blocked_reason: "merge conflict with <other-package> in <file(s)>"`, or delegate a repair package when the conflict is clearly in-scope and does not require a design decision.
5. Do not dispatch downstream packages depending on the conflicted package.

The orchestrator may resolve only mechanical merge-conflict/status artifacts. Substantive production/test/documentation fixes must be delegated.

## Merge-Base Cleanup Checks

Before removing any package worktree or branch, prove the branch is integrated from the integration worktree:

```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git merge-base --is-ancestor task/<feature>/<WP-ID> HEAD
```

Interpretation:

- Exit 0: the package branch is an ancestor of integration HEAD and may be eligible for cleanup.
- Non-zero: stop cleanup for that package branch/worktree; it is not proven integrated.

Check every package branch individually. Do not delete a batch if any member fails its merge-base check.

## Package Worktree and Branch Cleanup

Only after merge-base proof succeeds:

```bash
cd "$PROJECT_ROOT"
git worktree remove .worktrees/<feature>/wp-<WP-ID>
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git branch -d task/<feature>/<WP-ID>
```

Keep `.worktrees/<feature>/merge` until final implementation validation, review-code/fix loop, audit, push, and any explicitly approved merge-to-target safety boundary are complete.

## Status Examples

Useful merge/cleanup status report:

```text
Integrated packages:
  ✅ WP1 — task/<feature>/WP1 merged into feature/<feature>
  ✅ WP2 — task/<feature>/WP2 merged into feature/<feature>

Cleanup:
  ✅ .worktrees/<feature>/wp-WP1 removed after merge-base proof
  ⏸ .worktrees/<feature>/wp-WP2 kept: downstream review/fix pending
  ✅ branch task/<feature>/WP1 deleted

Integration worktree:
  kept at .worktrees/<feature>/merge
```

Blocked conflict report:

```text
Package blocked:
  🚫 WP3 — substantive merge conflict with WP2 in <file>
Reason: overlapping behavior/API change requires sequencing or design decision.
Next: repair package or user decision before downstream dispatch.
```

## Push and Target-Merge Boundary

Final implementation push runs from the integration worktree:

```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git push -u origin feature/<feature>
```

This publishes the feature branch only. It is not approval to merge into `<target-ref>`.

Never merge into `main` or any other target branch without explicit user approval for that exact target. If approval is later granted, follow the worktree skill's cleanup-safety reference and keep the integration worktree until merge and push complete.
