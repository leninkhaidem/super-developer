# Feature Package Workflow

Use this reference for planned-feature execution. It is package-centric: one worktree and branch per work package.

## Directory Layout

```text
project/                                      <- root worktree, user-owned branch; agent never switches it
+-- .worktrees/
|   +-- auth/                                 <- feature namespace
|   |   +-- wp-WP1/                           <- package worktree, branch wp/auth/WP1
|   |   +-- wp-WP2/                           <- package worktree, branch wp/auth/WP2
|   |   +-- merge/                            <- integration worktree, branch feature/auth
|   +-- search/
|   |   +-- wp-WP1/                           <- branch wp/search/WP1
|   |   +-- merge/                            <- branch feature/search
+-- src/
```

Keep `.worktrees/` ignored. Never put worktree-managed development in the root worktree, and never assume the root worktree is on `main`.

## Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature ref | `feature/<feature>` | `feature/auth` |
| Package branch | `wp/<feature>/<WP-ID>` | `wp/auth/WP1` |
| Bugfix | `bugfix/<name>` | `bugfix/null-check` |
| Hotfix | `hotfix/<name>` | `hotfix/crash-on-load` |
| Spike | `spike/<name>` | `spike/checkout-regression` |

`<WP-ID>` is a work package ID (`WP1`, `WP2`, ...). `<base-ref>` is the starting point for the feature, defaulting to `main`. For stacked features it can be another feature branch such as `feature/base-capability`. `<target-ref>` is the branch the feature may later merge into after explicit approval; default `main`.

## Feature and Package Commands

### 1. Create the feature ref

```bash
cd "$PROJECT_ROOT"
git branch feature/<feature> <base-ref>
```

No feature worktree is created here. `feature/<feature>` is a movable integration ref that starts from `<base-ref>` and package branches merge into.

### 2. Create package worktrees

For a package that can start from the feature base:

```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/<feature>/wp-<WP-ID> -b wp/<feature>/<WP-ID> <base-ref>
```

For a package that depends on already-integrated feature work:

```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/<feature>/wp-<WP-ID> -b wp/<feature>/<WP-ID> feature/<feature>
```

Branch from `feature/<feature>` only after prerequisite packages have been merged into that feature ref.

### 3. Work inside the package worktree

```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/wp-<WP-ID>"
# implement all work assigned to this package
# commit the package's work on wp/<feature>/<WP-ID>
```

Do not create separate branches for smaller internal package steps unless the plan explicitly split them into separate work packages.

### 4. Create the integration worktree

```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/<feature>/merge feature/<feature>
cd .worktrees/<feature>/merge
```

This is the only checkout of `feature/<feature>`. Keep it until feature merge/push completion and final cleanup.

### 5. Merge package branches into the feature ref

```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git merge wp/<feature>/WP1 --no-edit
git merge wp/<feature>/WP2 --no-edit
```

Resolve conflicts in the integration worktree. Verification for the integrated feature runs from this worktree.

### 6. Push feature branch for review/testing

```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git push -u origin feature/<feature>
```

Push means publish the feature branch. When this exact `origin feature/<feature>` push is listed in the approved implement Execution Contract, run it without a second approval prompt. If the approved contract omitted it or the remote/ref changes, stop for approval. This feature-branch push does not mean merge into `<target-ref>` or push `<target-ref>`.

### 7. Merge to target only after explicit approval

After the user explicitly asks to merge into the named `<target-ref>`, load `cleanup-safety.md` and complete its Pre-Target-Merge Safety Checks before running any merge command. The integration worktree stays in place as a safety net until merge and push complete.

The actual merge/push commands live in `cleanup-safety.md`; do not duplicate or bypass that gate here.

Use the cleanup-safety reference before removing package branches, package worktrees, or the integration worktree.

## Multi-Phase Dependency Examples

### Sequential phases

Phase 1 packages can branch from `<base-ref>` when they do not depend on earlier feature work:

```bash
git worktree add .worktrees/billing/wp-WP1 -b wp/billing/WP1 <base-ref>
git worktree add .worktrees/billing/wp-WP2 -b wp/billing/WP2 <base-ref>
```

After `WP1` and `WP2` merge into `feature/billing`, Phase 2 packages that need their work branch from the feature ref:

```bash
git worktree add .worktrees/billing/wp-WP3 -b wp/billing/WP3 feature/billing
```

Wrong: branch `WP3` from `<base-ref>` when it requires Phase 1 code. It will not see the integrated feature work.

### Internal package dependencies

If `WP4` owns several internal steps, all are implemented in `.worktrees/<feature>/wp-WP4` on branch `wp/<feature>/WP4`. The package agent sequences internal package dependencies in that single worktree.

### Concurrent features

Two active features use separate namespaces:

```text
.worktrees/auth/wp-WP1      -> wp/auth/WP1
.worktrees/auth/merge       -> feature/auth
.worktrees/search/wp-WP1    -> wp/search/WP1
.worktrees/search/merge     -> feature/search
```

Clean up only the namespace being finalized. Do not remove another feature's worktrees or branches because package IDs such as `WP1` repeat across feature namespaces.

## Concurrency Rules

- Parallel package work is safe only when package file ownership and dependencies permit it.
- A package depending on previous package output must wait until that output is merged into `feature/<feature>` or branch from a package branch only when the orchestrator deliberately chooses that dependency shape.
- Prefer integrating dependency output into `feature/<feature>` before starting dependent packages; it keeps branch ancestry and cleanup checks simple.
