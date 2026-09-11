# Feature Package Workflow

Use for planned-feature execution. Boundary: artifact sidecar setup/checkpoints, package/integration worktrees, merge
order, dependencies, and feature-source handoff. The caller supplies artifact-root semantics and the loaded
source-publication packet before a source gate.

## Contract

- One artifact sidecar per feature: orphan ref `artifacts/<feature>` at `.worktrees/<feature>/artifacts`; it holds
  `.planning/`, `.tasks/`, package reports, and minimal metadata only.
- One worktree/ref per reviewed package: `wp/<feature>/<WP-ID>` at `.worktrees/<feature>/wp-<WP-ID>`.
- Auto-resolve may create, never remove, focused-reviewed continuation packages; each artifact fixes `BASE_KIND`,
  exact `BASE_REF`, `REVIEWED_BASE_SHA`, and prerequisite ref/SHA evidence.
- The feature ref is `feature/<feature>` with sole integration checkout `.worktrees/<feature>/merge`.
- Stacked-feature final readiness names the top code state plus every relevant base/follow-up artifact set.
- Package agents implement inside assigned package worktrees only. The orchestrator creates resources, runtime-
  validates dynamic envelopes, merges, applies scheduled source publication, and handles cleanup.
- Each accepted package retains a local recovery commit/ref regardless of source policy.
- Never use the root worktree for managed development or assume root is on `main`.

## Directory Layout and Names

```text
project/
+-- .worktrees/
|   +-- auth/
|   |   +-- artifacts/   -> artifacts/auth
|   |   +-- wp-WP1/      -> wp/auth/WP1
|   |   +-- wp-WP2/      -> wp/auth/WP2
|   |   +-- merge/       -> feature/auth
```

Keep `.worktrees/` ignored. `<feature>` is the resolved artifact slug; never prompt for routine naming or silently
remap paths. `<WP-ID>` names a package. `<base-ref>` defaults only when the owning contract allows; `<target-ref>` is
approved later.

## Artifact Sidecar Setup

Create the sidecar immediately before the first actual durable artifact write because `git worktree add` refuses a
non-empty path. Invocation, discussion, or slug resolution is not a trigger. `--orphan` needs git >= 2.42; stop rather
than improvise on older git.

```bash
cd "$PROJECT_ROOT"
mkdir -p .worktrees/<feature>
git worktree add --orphan -b artifacts/<feature> .worktrees/<feature>/artifacts
```

Resume an existing sidecar instead of creating a new orphan branch:

```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/<feature>/artifacts artifacts/<feature>   # local branch exists
git fetch origin artifacts/<feature> && \
  git worktree add -b artifacts/<feature> .worktrees/<feature>/artifacts origin/artifacts/<feature>
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
`BASE_REF`, `REVIEWED_BASE_SHA`, and prerequisite ref/SHA arrays; never recompute or accept a moved ref:

```bash
set -euo pipefail; cd "$PROJECT_ROOT"
WP_ID=<reviewed-WP-ID>; [[ "$WP_ID" =~ ^WP[1-9][0-9]*$ ]]
BASE_KIND=<independent|dependent>
BASE_REF=<focused-reviewed-exact-ref>
REVIEWED_BASE_SHA=<focused-reviewed-full-sha>
ORIGINAL_BASE_REF=<approved-original-ref>
PREREQ_REFS=(<reviewed-refs>); PREREQ_SHAS=(<reviewed-shas>)
test "${#PREREQ_REFS[@]}" = "${#PREREQ_SHAS[@]}"
if test "$BASE_KIND" = independent; then
  test "$BASE_REF" = "$ORIGINAL_BASE_REF"; test "${#PREREQ_REFS[@]}" = 0
else
  test "$BASE_KIND" = dependent
  test "${#PREREQ_REFS[@]}" -gt 0
  test "$BASE_REF" = "feature/<feature>"
  INTEGRATION="$PROJECT_ROOT/.worktrees/<feature>/merge"
  test "$(git -C "$INTEGRATION" symbolic-ref --short HEAD)" = "$BASE_REF"
  test -z "$(git -C "$INTEGRATION" status --porcelain)"
  test "$(git -C "$INTEGRATION" rev-parse HEAD)" = "$REVIEWED_BASE_SHA"
  for I in "${!PREREQ_REFS[@]}"; do
    test "$(git rev-parse "${PREREQ_REFS[$I]}")" = "${PREREQ_SHAS[$I]}"
    git merge-base --is-ancestor "${PREREQ_SHAS[$I]}" "$REVIEWED_BASE_SHA"
  done
fi
test "$(git rev-parse "$BASE_REF")" = "$REVIEWED_BASE_SHA"
WT="$PROJECT_ROOT/.worktrees/<feature>/wp-$WP_ID"; REF="wp/<feature>/$WP_ID"
test ! -e "$WT"; test ! -L "$WT"
test -z "$(git show-ref --verify --hash "refs/heads/$REF" 2>/dev/null || :)"
git worktree add --no-track -b "$REF" "$WT" "$REVIEWED_BASE_SHA"
test -z "$(git for-each-ref --format='%(upstream)' "refs/heads/$REF")"
test -z "$(git config --get "branch.$REF.remote" || :)"
test -z "$(git config --get "branch.$REF.merge" || :)"
test -z "$(git config --get "branch.$REF.pushRemote" || :)"
test "$(git rev-parse "$BASE_REF")" = "$REVIEWED_BASE_SHA"
test "$(git -C "$WT" rev-parse HEAD)" = "$REVIEWED_BASE_SHA"
```

Retain the worktree/ref through final whole-feature cleanup.

### 3. Work inside the package worktree

```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/wp-<WP-ID>"
# implement all work assigned to this package
# commit the package's source/reference/test changes on wp/<feature>/<WP-ID>
```

Package result reports stay in the artifact root. Create no internal branches unless the plan split the package.

### 4. Create the integration worktree

```bash
cd "$PROJECT_ROOT"
git worktree add .worktrees/<feature>/merge feature/<feature>
cd .worktrees/<feature>/merge
```

This is the only checkout of `feature/<feature>`. Keep it through final delivery and approved cleanup.

### 5. Merge and apply selected source policy

After package completion gates, stabilize the package's local recovery commit/ref and merge:

```bash
set -euo pipefail
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
git merge wp/<feature>/<WP-ID> --no-edit
```

Close parent-owned post-merge freshness/repair gates, then use the loaded source-publication packet. Non-due or
`local-only` gates run no network action and do not block downstream readiness. Due gates run the packet's scheduled
push and require remote SHA = integration `HEAD`; failure stops with safety nets retained. Final remote catch-up waits
for sibling same-freeze review-code CLEAN and audit PASS. Source publication never authorizes target, sidecar, or
planned-hotfix work.

## Sidecar Checkpoints

A sidecar is checkpoint-eligible only at artifact-store gates: after an actual Conceptualize artifact write, accepted
review-plan, each package delivery, and final review/audit. Run a checkpoint only when that exact sidecar push is
authorized. From the artifact worktree only:

```bash
cd "$PROJECT_ROOT/.worktrees/<feature>/artifacts"
git status --short
git add -A
if ! git diff --cached --quiet; then git commit -m "artifacts: <feature> <gate>"; fi
git push -u origin artifacts/<feature>
```

This push targets only `origin artifacts/<feature>` and must not push `main`, `feature/<feature>`, or package refs.

## Multi-Phase and Concurrent Features

Phase 1 packages branch from `<base-ref>` when independent; dependent packages branch from `feature/<feature>` after
prerequisite packages merge. Separate active features by namespace; package IDs may repeat across features. Clean up
only the namespace being finalized.

## Stop if

- `.worktrees/` is not ignored.
- Artifact sidecar creation would reuse a non-orphan/deliverable branch or require source files in the artifact
  worktree.
- A sidecar checkpoint would push anything except `origin artifacts/<feature>` from the artifact worktree.
- A package needs predecessor output that has not merged into `feature/<feature>`.
- Package ownership/dependencies do not permit parallel package work.
- Feature-source policy is absent/ambiguous, a remote cadence lacks explicit authorization, a push is not due, or a
  scheduled push fails/does not verify remote SHA.
- Any package cleanup is requested before final whole-feature gates.
- A target merge, target push, cleanup, force action, or remote deletion is requested inside this playbook.
