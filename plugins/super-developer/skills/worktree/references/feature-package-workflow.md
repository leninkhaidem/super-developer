# Feature Package Workflow

Use this reference for planned-feature execution. Boundary: package/integration worktree setup,
package branch creation, package merge order, dependency examples, and feature-push handoff.

## Contract
- One package worktree and one package branch per work package.
- Package branches use `wp/<feature>/<WP-ID>`.
- Package worktrees live at `.worktrees/<feature>/wp-<WP-ID>`.
- The feature ref is `feature/<feature>` and its integration worktree is `.worktrees/<feature>/merge`.
- Package agents implement inside assigned package worktrees only.
- The orchestrator creates worktrees/branches, merges packages, pushes feature refs, and handles cleanup.
- Never put worktree-managed development in the root worktree or assume the root is on `main`.

## Directory Layout
```text
project/                            <- root worktree; user-owned branch
+-- .worktrees/
|   +-- auth/
|   |   +-- wp-WP1/                 <- branch wp/auth/WP1
|   |   +-- wp-WP2/                 <- branch wp/auth/WP2
|   |   +-- merge/                  <- branch feature/auth
|   +-- search/
|   |   +-- wp-WP1/                 <- branch wp/search/WP1
|   |   +-- merge/                  <- branch feature/search
+-- src/
```
Keep `.worktrees/` ignored before creating these paths.

## Branch Naming
| Type | Pattern | Example |
|---|---|---|
| Feature ref | `feature/<feature>` | `feature/auth` |
| Package branch | `wp/<feature>/<WP-ID>` | `wp/auth/WP1` |

`<WP-ID>` is a work package ID (`WP1`, `WP2`, ...). `<base-ref>` starts the feature and defaults
to `main`; stacked features may use `feature/base-capability`. `<target-ref>` is the later merge
destination after explicit approval and defaults to `main`.

## Feature and Package Commands

### 1. Create the feature ref
```bash
cd "$PROJECT_ROOT"
git branch feature/<feature> <base-ref>
```
No feature worktree is created here. `feature/<feature>` starts from `<base-ref>` and package
branches merge into it later.

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
Branch from `feature/<feature>` only after prerequisite packages have merged into that feature ref.

### 3. Work inside the package worktree
```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/wp-<WP-ID>"
# implement all work assigned to this package
# commit the package's work on wp/<feature>/<WP-ID>
```
Do not create smaller internal branches unless the plan split them into separate work packages.

### 4. Create the integration worktree
```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/<feature>/merge feature/<feature>
cd .worktrees/<feature>/merge
```
This is the only checkout of `feature/<feature>`. Keep it until feature merge, push, and final
cleanup complete.

### 5. Merge package branches into the feature ref
```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git merge wp/<feature>/WP1 --no-edit
git merge wp/<feature>/WP2 --no-edit
```
Resolve conflicts in the integration worktree. Verification for the integrated feature runs there.

### 6. Push feature branch for review/testing
```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git push -u origin feature/<feature>
```
This publishes the feature branch only. If the exact `origin feature/<feature>` push was listed in
the approved implement Execution Contract, run it without a second approval prompt. If the contract
omitted it or the remote/ref changes, stop for approval.

A feature-branch push does not authorize merging into `<target-ref>` or pushing `<target-ref>`.

### 7. Merge to target only after explicit approval
After the user explicitly approves merge into the named `<target-ref>`, leave this playbook and use
the parent skill's target-merge gate before any merge command. Keep the integration worktree as a
safety net until target merge and push complete.

## Multi-Phase Dependency Examples
Phase 1 packages can branch from `<base-ref>` when they do not depend on earlier feature work:
```bash
git worktree add .worktrees/billing/wp-WP1 -b wp/billing/WP1 <base-ref>
git worktree add .worktrees/billing/wp-WP2 -b wp/billing/WP2 <base-ref>
```
After `WP1` and `WP2` merge into `feature/billing`, dependent packages branch from the feature ref:
```bash
git worktree add .worktrees/billing/wp-WP3 -b wp/billing/WP3 feature/billing
```
Wrong: branch `WP3` from `<base-ref>` when it requires Phase 1 code.

If `WP4` owns several internal steps, keep them in `.worktrees/<feature>/wp-WP4` on
`wp/<feature>/WP4`. The package agent sequences internal dependencies there.

## Concurrent Features
Separate active features by namespace:
```text
.worktrees/auth/wp-WP1      -> wp/auth/WP1
.worktrees/auth/merge       -> feature/auth
.worktrees/search/wp-WP1    -> wp/search/WP1
.worktrees/search/merge     -> feature/search
```
Clean up only the namespace being finalized. Package IDs such as `WP1` can repeat across features.

## Stop if
- `.worktrees/` is not ignored.
- A package needs predecessor output that has not merged into `feature/<feature>`.
- Package ownership/dependencies do not permit parallel package work.
- A target merge, target push, cleanup, force action, or remote deletion is requested inside this playbook.
