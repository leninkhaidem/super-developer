# Feature Package Workflow
Use this reference for planned-feature execution. Boundary: artifact sidecar setup/checkpoints, package/integration
worktrees, package merge order, dependencies, and feature-push handoff. Parent supplies artifact-store root terms.
## Contract
- One artifact sidecar per feature slug: orphan ref `artifacts/<feature>` at `.worktrees/<feature>/artifacts`.
- The artifact sidecar contains `.planning/`, `.tasks/`, proof/report artifacts, and minimal metadata only.
- The artifact sidecar is not a source checkout, feature branch, package branch, or target-merge branch.
- One worktree/ref per reviewed package: `wp/<feature>/<WP-ID>` at `.worktrees/<feature>/wp-<WP-ID>`.
- Auto-resolve may create, but never remove, focused-reviewed continuation packages; each artifact fixes `BASE_KIND`, exact `BASE_REF`, `REVIEWED_BASE_SHA`, and prerequisite ref/SHA evidence.
- The feature ref is `feature/<feature>` and its integration worktree is `.worktrees/<feature>/merge`.
- Stacked-feature final readiness names the top code state plus every relevant base/follow-up artifact set.
- Package agents implement inside assigned package worktrees only.
- The orchestrator creates fixed resources or runtime-validates the dynamic envelope, then owns merges/checkpoints/
  cleanup; package agents do none of those actions.
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
`<feature>` is the resolved feature/artifact slug; never prompt for routine naming or silently remap artifact,
branch, or worktree paths. `<WP-ID>` names a package; `<base-ref>` defaults to `main` but may be a stacked feature; `<target-ref>` is later approved and defaults to `main`.
## Artifact Sidecar Setup
Create the sidecar before the first artifact write because `git worktree add` refuses a non-empty path.
`--orphan` needs git >= 2.42; on older git, stop and report rather than improvising.
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
Create `.planning/<concept-slug>/` and `.tasks/<feature>/` there; do not expect source files or validation.
## Feature and Package Commands
### 1. Create the feature ref
```bash
cd "$PROJECT_ROOT"
git branch feature/<feature> <base-ref>
```
No worktree is created here; package branches later merge into this ref from `<base-ref>`.
### 2. Create package worktrees
Initial packages use their exact contract base. Continuation Notes supply focused-reviewed `BASE_KIND`, exact
`BASE_REF`, `REVIEWED_BASE_SHA`, and prerequisite ref/SHA arrays; never recompute and accept a moved ref:
```bash
set -euo pipefail; cd "$PROJECT_ROOT"
WP_ID=<reviewed-WP-ID>; [[ "$WP_ID" =~ ^WP[1-9][0-9]*$ ]]; BASE_KIND=<independent|dependent>
BASE_REF=<focused-reviewed-exact-ref>; REVIEWED_BASE_SHA=<focused-reviewed-full-sha>; ORIGINAL_BASE_REF=<approved-original-ref>
PREREQ_REFS=(<reviewed-refs>); PREREQ_SHAS=(<reviewed-shas>); test "${#PREREQ_REFS[@]}" = "${#PREREQ_SHAS[@]}"
if test "$BASE_KIND" = independent; then
  test "$BASE_REF" = "$ORIGINAL_BASE_REF"; test "${#PREREQ_REFS[@]}" = 0
else
  test "$BASE_KIND" = dependent; test "${#PREREQ_REFS[@]}" -gt 0; test "$BASE_REF" = "feature/<feature>"; INTEGRATION="$PROJECT_ROOT/.worktrees/<feature>/merge"
  test "$(git -C "$INTEGRATION" symbolic-ref --short HEAD)" = "$BASE_REF"; test -z "$(git -C "$INTEGRATION" status --porcelain)"
  test "$(git -C "$INTEGRATION" rev-parse HEAD)" = "$REVIEWED_BASE_SHA"
  for I in "${!PREREQ_REFS[@]}"; do
    test "$(git rev-parse "${PREREQ_REFS[$I]}")" = "${PREREQ_SHAS[$I]}"; git merge-base --is-ancestor "${PREREQ_SHAS[$I]}" "$REVIEWED_BASE_SHA"
  done
fi
test "$(git rev-parse "$BASE_REF")" = "$REVIEWED_BASE_SHA"
WT="$PROJECT_ROOT/.worktrees/<feature>/wp-$WP_ID"; REF="wp/<feature>/$WP_ID"
test ! -e "$WT"; test ! -L "$WT"; test -z "$(git show-ref --verify --hash "refs/heads/$REF" 2>/dev/null || :)"
git worktree add --no-track -b "$REF" "$WT" "$REVIEWED_BASE_SHA"
test -z "$(git for-each-ref --format='%(upstream)' "refs/heads/$REF")"; test -z "$(git config --get "branch.$REF.remote" || :)"; test -z "$(git config --get "branch.$REF.merge" || :)"; test -z "$(git config --get "branch.$REF.pushRemote" || :)"
test "$(git rev-parse "$BASE_REF")" = "$REVIEWED_BASE_SHA"; test "$(git -C "$WT" rev-parse HEAD)" = "$REVIEWED_BASE_SHA"
```
No arbitrary allowed-base selection is valid. Retain the worktree/ref through final whole-feature cleanup.
### 3. Work inside the package worktree
```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/wp-<WP-ID>"
# implement all work assigned to this package
# commit the package's source/reference/test changes on wp/<feature>/<WP-ID>
```
Proof/reports stay in the artifact root. Create no internal branches unless the plan split the package.
### 4. Create the integration worktree
```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/<feature>/merge feature/<feature>
cd .worktrees/<feature>/merge
```
This is the only checkout of `feature/<feature>`. Keep it through final delivery and approved cleanup.
### 5. Merge and remotely checkpoint each accepted package
After package completion gates, merge:
```bash
set -euo pipefail
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git merge wp/<feature>/<WP-ID> --no-edit
```
Close parent-owned post-merge freshness/repair gates, then checkpoint:
```bash
set -euo pipefail
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
test "$(git symbolic-ref --short HEAD)" = "feature/<feature>"; test -z "$(git status --porcelain)"
LOCAL_SHA="$(git rev-parse HEAD)"
git push origin "HEAD:refs/heads/feature/<feature>"
REMOTE_LINE="$(git ls-remote --heads origin refs/heads/feature/<feature>)"; test -n "$REMOTE_LINE"
REMOTE_SHA="${REMOTE_LINE%%$'\t'*}"; test "$REMOTE_SHA" = "$LOCAL_SHA"
```
Non-force pushes serialize through integration; failure, mismatch, or divergence stops progression. The checkpoint
publishes only `feature/<feature>` and never authorizes target work. Retain every active/retired package worktree/
ref plus integration/artifacts through final gates; retirement alone never authorizes cleanup.
## Sidecar Checkpoints
Checkpoint at parent-supplied artifact-store gates (post-Conceptualize, post-review-plan, each package delivery,
final review/audit), never after every incidental edit.
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
- A feature checkpoint is uncontracted/non-fast-forward, mismatches integration `HEAD`, or any package cleanup is requested before final whole-feature gates.
- A target merge, target push, cleanup, force action, or remote deletion is requested inside this playbook.
