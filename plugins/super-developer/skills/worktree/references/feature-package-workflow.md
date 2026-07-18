# Feature Package Workflow

Use for planned-feature sidecar, package, integration, and checkpoint work. The parent-supplied artifact-store
contract owns authority, roots, legacy import, permission, state, and ordering; this file owns Git commands.

## Contract

- Sidecar: orphan `refs/heads/artifacts/<feature>` at `.worktrees/<feature>/artifacts`; artifacts only.
- Feature: `refs/heads/feature/<feature>` at `.worktrees/<feature>/merge` when integrated.
- Package: `refs/heads/wp/<feature>/<WP-ID>` at `.worktrees/<feature>/wp-<WP-ID>`.
- Immutable code checkpoint: `refs/heads/checkpoints/<feature>/<slot>/g<generation>`; unique and never moved.
- Package agents edit/commit only assigned code worktrees. The orchestrator owns refs, worktrees, merges,
  checkpoints, and cleanup. Never develop in or switch the user-owned root worktree.
- Sidecar Portability Authorization covers only discovery/planning CAS pushes to the exact artifact ref.
  Implementation Authorization separately covers named code checkpoint refs. Neither covers target/release/force/
  delete operations.
- `.worktrees/` must be ignored. `<feature>` is the one resolved artifact slug; never remap silently.

## Layout

```text
.worktrees/<feature>/
  artifacts/   # artifacts/<feature>; .planning, .tasks, minimal metadata only
  wp-WP1/      # wp/<feature>/WP1
  merge/       # feature/<feature>
```

The artifact root is fixed. The code root is the package worktree under check or the merge worktree for the top
code state. Stacked readiness names that top code state plus every relevant base/follow-up artifact set.

## Local Sidecar Setup

Create before any artifact write. The destination must be absent/empty and Git must support `--orphan` (>=2.42):

```bash
set -euo pipefail
cd "$PROJECT_ROOT"
test ! -e .worktrees/<feature>/artifacts
mkdir -p .worktrees/<feature>
git show-ref --verify --quiet refs/heads/artifacts/<feature> && exit 1 || test $? -eq 1
git worktree add --orphan -b artifacts/<feature> .worktrees/<feature>/artifacts
```

Existing current-root artifacts do not change this ordering. Create the empty sidecar, then follow the
provenance-bound import in the artifact-store contract. Never move the legacy directory into place.

## Initial Authorized Sidecar Publication

First prove Sidecar Portability Authorization and an absent remote ref. Finalized paths are exact files, including
Slices/Index, migration provenance when present, and Lifecycle State—never a directory wildcard. Run only from the
artifact worktree:

```bash
set -euo pipefail
cd "$PROJECT_ROOT/.worktrees/<feature>/artifacts"
ARTIFACT_REF=refs/heads/artifacts/<feature>
REMOTE_LINE="$(git ls-remote --heads origin "$ARTIFACT_REF")"
test -z "$REMOTE_LINE"
test "$(git rev-parse --show-toplevel)" = "$PWD"
FINALIZED_PATHS=(<exact-finalized-path> <exact-lifecycle-state-path>)
git add -- "${FINALIZED_PATHS[@]}"
mapfile -d '' -t EXPECTED < <(printf '%s\0' "${FINALIZED_PATHS[@]}" | sort -z)
mapfile -d '' -t STAGED < <(git diff --cached --name-only -z | sort -z)
test "${#EXPECTED[@]}" -eq "${#STAGED[@]}"
for I in "${!EXPECTED[@]}"; do test "${EXPECTED[$I]}" = "${STAGED[$I]}"; done
git diff --cached --quiet && exit 1
git commit -m "artifacts: initialize <feature>"
SIDECAR_SHA="$(git rev-parse HEAD)"
git push origin "$SIDECAR_SHA:$ARTIFACT_REF"
git fetch --no-tags origin "$ARTIFACT_REF"
test "$(git rev-parse FETCH_HEAD)" = "$SIDECAR_SHA"
REMOTE_SHA="$(git ls-remote --heads origin "$ARTIFACT_REF" | awk 'NR==1 {print $1}')"
test "$REMOTE_SHA" = "$SIDECAR_SHA"
```

Any error, non-absent ref, unexpected staged path, push rejection, or SHA mismatch blocks without fallback. This
publishes no code/feature/target/tag/release ref and does not permit another remote operation.

## Feature and Package Setup

```bash
set -euo pipefail
cd "$PROJECT_ROOT"
git branch feature/<feature> <base-ref>
git worktree add .worktrees/<feature>/wp-<WP-ID> -b wp/<feature>/<WP-ID> <base-ref>
git worktree add .worktrees/<feature>/merge feature/<feature>
```

A dependent package branches from `feature/<feature>` only after its prerequisite is integrated and accepted.
Merge from the integration worktree with `git merge wp/<feature>/<WP-ID> --no-edit`. Feature publication is a
separate covered action; it never authorizes target merge/push or sidecar cleanup.

## Quiescent Code-Before-Sidecar Checkpoint

Verify active owner, generation, budgets, clean code, expected remote parents, and exact finalized path set. Then:

1. Commit clean code and choose a never-used ref
   `refs/heads/checkpoints/<feature>/<slot>/g<generation>`.
2. Prove that remote ref absent; non-force push the exact code SHA; fetch/verify remote SHA.
3. Only after verification, update Lifecycle State to reference that ref/SHA.
4. Prove artifact remote SHA equals the snapshot's expected parent. Path-stage only exact finalized files, verify
   the staged set, commit, non-force push only `artifacts/<feature>`, and fetch/verify the SHA.

```bash
set -euo pipefail
cd "$CODE_ROOT"
test -z "$(git status --porcelain)"
CODE_SHA="$(git rev-parse HEAD)"
CODE_REF=refs/heads/checkpoints/<feature>/<slot>/g<generation>
test -z "$(git ls-remote --heads origin "$CODE_REF")"
git push origin "$CODE_SHA:$CODE_REF"
git fetch --no-tags origin "$CODE_REF"
test "$(git rev-parse FETCH_HEAD)" = "$CODE_SHA"
test "$(git ls-remote --heads origin "$CODE_REF" | awk 'NR==1 {print $1}')" = "$CODE_SHA"

cd "$ARTIFACT_ROOT"
ARTIFACT_REF=refs/heads/artifacts/<feature>
EXPECTED_PARENT=<last-verified-sidecar-sha>
test "$(git ls-remote --heads origin "$ARTIFACT_REF" | awk 'NR==1 {print $1}')" = "$EXPECTED_PARENT"
FINALIZED_PATHS=(<exact-finalized-paths-including-lifecycle-state>)
git add -- "${FINALIZED_PATHS[@]}"
mapfile -d '' -t EXPECTED < <(printf '%s\0' "${FINALIZED_PATHS[@]}" | sort -z)
mapfile -d '' -t STAGED < <(git diff --cached --name-only -z | sort -z)
test "${#EXPECTED[@]}" -eq "${#STAGED[@]}"
for I in "${!EXPECTED[@]}"; do test "${EXPECTED[$I]}" = "${STAGED[$I]}"; done
git commit -m "artifacts: checkpoint <feature> g<generation>"
SIDECAR_SHA="$(git rev-parse HEAD)"
git push origin "$SIDECAR_SHA:$ARTIFACT_REF"
git fetch --no-tags origin "$ARTIFACT_REF"
test "$(git rev-parse FETCH_HEAD)" = "$SIDECAR_SHA"
test "$(git ls-remote --heads origin "$ARTIFACT_REF" | awk 'NR==1 {print $1}')" = "$SIDECAR_SHA"
```

Normal push is required: no force option, mutable ref reuse, sidecar-first ordering, local-only referenced code, or
broad staging. Before the authorization/status checkpoint, prove the candidate differs only by the
approved status mutation; any other drift blocks staging.

## Safe Resume

Fetch the exact artifact ref, verify its SHA and quiescent Lifecycle State, then fetch and verify every referenced
code ref/SHA before creating/resuming worktrees. Ignore unreferenced checkpoint refs and treat later local commits,
files, proofs, or reports as untrusted recovery input. If expected parent, owner/generation, budget/deadline,
quiescence, or ref reachability is uncertain, do not push or take over; report the last verified checkpoint.

## Stop If

Stop on unsafe/equal roots, current-root authority, incomplete migration, ref/path collision, dirty finalized code,
missing permission, unexpected remote parent, non-fast-forward/CAS rejection, staged-path mismatch, unverified code
SHA, predecessor not integrated, or any request for force, target merge/push, release/tag, cleanup, or deletion.
