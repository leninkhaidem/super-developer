# Feature Package Workflow

Use this reference for planned-feature execution. Boundary: artifact sidecar setup/checkpoints,
package/integration worktree setup, package merge order, dependency examples, and feature-push handoff.
Use the parent-supplied artifact-store contract for root terms.

## Contract
- One artifact sidecar per feature slug: orphan ref `artifacts/<feature>` at `.worktrees/<feature>/artifacts`.
- The artifact sidecar contains `.planning/`, `.tasks/`, proof/report artifacts, and minimal metadata only.
- The artifact sidecar is not a source checkout, feature branch, package branch, or target-merge branch.
- One package worktree and one package branch per work package.
- Package branches use `wp/<feature>/<WP-ID>` and worktrees use `.worktrees/<feature>/wp-<WP-ID>`.
- The feature ref is `feature/<feature>` and its integration worktree is `.worktrees/<feature>/merge`.
- Stacked-feature final readiness names the top code state plus every relevant base/follow-up artifact set.
- Package agents implement inside assigned package worktrees only.
- The orchestrator creates worktrees/branches, merges packages, pushes refs, and handles cleanup.
- Never put worktree-managed development in the root worktree or assume the root is on `main`.

## Directory Layout
```text
project/                            <- root worktree; user-owned branch
+-- .worktrees/
|   +-- auth/
|   |   +-- artifacts/              <- orphan branch artifacts/auth; no source checkout required
|   |   +-- wp-WP1/                 <- branch wp/auth/WP1
|   |   +-- wp-WP2/                 <- branch wp/auth/WP2
|   |   +-- merge/                  <- branch feature/auth
+-- src/
```
Keep `.worktrees/` ignored before creating these paths.

## Branch Naming
| Type | Pattern | Example |
|---|---|---|
| Artifact ref | `artifacts/<feature>` | `artifacts/auth` |
| Feature ref | `feature/<feature>` | `feature/auth` |
| Package branch | `wp/<feature>/<WP-ID>` | `wp/auth/WP1` |

`<feature>` is the resolved feature/artifact slug. Do not prompt for routine slug naming or silently
remap `.planning/`, `.tasks/`, sidecar branch, or worktree paths. `<WP-ID>` is a work package ID.
`<base-ref>` defaults to `main`; stacked features may use another feature ref. `<target-ref>` is the
later merge destination after explicit approval and defaults to `main`.

## Artifact Sidecar Setup
Create the sidecar before the first artifact write; `git worktree add` refuses a non-empty path, so it
cannot be added after `.planning/` exists. `--orphan` needs git >= 2.42; on older git, stop and report
the version gap rather than improvising an orphan checkout.
```bash
cd "$PROJECT_ROOT"
mkdir -p .worktrees/<feature>
git worktree add --orphan -b artifacts/<feature> .worktrees/<feature>/artifacts
```
Resume an existing sidecar instead of creating a new orphan branch:
```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/<feature>/artifacts artifacts/<feature>   # when the local branch exists
git fetch origin artifacts/<feature> && \
  git worktree add -b artifacts/<feature> .worktrees/<feature>/artifacts origin/artifacts/<feature>  # remote-only
```
Create `.planning/<concept-slug>/` and `.tasks/<feature>/` inside the artifact worktree/root. Do not
expect plugin files, source files, dependencies, or source validation to exist there.

## Feature and Package Commands
### 1. Create the feature ref
```bash
cd "$PROJECT_ROOT"
git branch feature/<feature> <base-ref>
```
No feature worktree is created here. `feature/<feature>` starts from `<base-ref>` and package branches
merge into it later.

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
# commit the package's source/reference/test changes on wp/<feature>/<WP-ID>
```
Proof/report artifacts stay in the artifact root, not the package branch. Do not create smaller
internal branches unless the plan split them into separate work packages.

### 4. Create the integration worktree
```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/<feature>/merge feature/<feature>
cd .worktrees/<feature>/merge
```
This is the only checkout of `feature/<feature>`. Keep it until feature merge, push, and final cleanup complete.

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
This publishes only `feature/<feature>`. It does not authorize target merge/push or sidecar cleanup.

## Sidecar Checkpoints
Checkpoint only at parent-supplied gates. Before Gate-2 `git add -A`, prove the candidate differs only by the
approved status mutation; unexpected artifact drift blocks staging. Never checkpoint every incidental edit.

From the artifact worktree only:
```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/artifacts"
git status --short
git add -A   # artifact worktree is a dedicated orphan checkout: only .planning/.tasks live here
if ! git diff --cached --quiet; then git commit -m "artifacts: <feature> <gate>"; fi
git push -u origin artifacts/<feature>
```
This push targets only `origin artifacts/<feature>` and must not push `main`, `feature/<feature>`, or
`wp/<feature>/<WP-ID>` as an artifact side effect.

## Multi-Phase and Concurrent Features
Phase 1 packages branch from `<base-ref>` when independent; dependent packages branch from
`feature/<feature>` after prerequisite packages merge. Separate active features by namespace:
```text
.worktrees/auth/artifacts   -> artifacts/auth
.worktrees/auth/wp-WP1      -> wp/auth/WP1
.worktrees/auth/merge       -> feature/auth
.worktrees/search/artifacts -> artifacts/search
.worktrees/search/wp-WP1    -> wp/search/WP1
```
Clean up only the namespace being finalized. Package IDs such as `WP1` can repeat across features.

## Stop if
- `.worktrees/` is not ignored.
- Artifact sidecar creation would reuse a non-orphan/deliverable branch or require source files in the artifact worktree.
- A sidecar checkpoint would push anything except `origin artifacts/<feature>` from the artifact worktree.
- A package needs predecessor output that has not merged into `feature/<feature>`.
- Package ownership/dependencies do not permit parallel package work.
- A target merge, target push, cleanup, force action, or remote deletion is requested inside this playbook.
