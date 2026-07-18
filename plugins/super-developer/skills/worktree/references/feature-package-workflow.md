# Feature Package Workflow

Use for planned-feature sidecar, package, integration, and checkpoint work. The parent-supplied artifact-store
contract owns authority, roots, migration, permission, and state; this file alone owns Git/CAS commands.

## Contract

- Sidecar: orphan `refs/heads/artifacts/<feature>` at `.worktrees/<feature>/artifacts`; artifacts only.
- Feature: `refs/heads/feature/<feature>` at `.worktrees/<feature>/merge`; package:
  `refs/heads/wp/<feature>/<WP-ID>` at `.worktrees/<feature>/wp-<WP-ID>`.
- Immutable code checkpoint: `refs/heads/checkpoints/<feature>/<slot>/g<generation>`; unique and never moved.
- Package agents edit/commit assigned code worktrees. Delivery Owner owns refs/worktrees/merges/checkpoints/cleanup.
  Never switch/edit the user root. `.worktrees/` is ignored; roots are distinct. Never silently remap `<feature>`.
- Sidecar Portability Authorization covers only discovery/planning CAS to the artifact ref. Implementation
  Authorization separately covers named code checkpoints. Neither covers target/release/force/delete operations.

## Layout and Local Sidecar Setup

```text
.worktrees/<feature>/
  artifacts/   # artifacts/<feature>; artifact root
  wp-WP1/      # wp/<feature>/WP1; package code root
  merge/       # feature/<feature>; integration code root
```

Create before artifact writes; destination absent/empty, Git >=2.42, ref absent:

```bash
set -euo pipefail
cd "$PROJECT_ROOT"
test ! -e .worktrees/<feature>/artifacts
mkdir -p .worktrees/<feature>
git show-ref --verify --quiet refs/heads/artifacts/<feature> && exit 1 || test $? -eq 1
git worktree add --orphan -b artifacts/<feature> .worktrees/<feature>/artifacts
```

Legacy artifacts do not alter this ordering: create empty sidecar, then provenance-bound import; never move source.

## Initial Authorized Sidecar Publication

Prove Sidecar Portability Authorization and absent remote ref. Validate schema generation 1 before staging exact
finalized files (Slices/Index, migration provenance when any, Lifecycle State; never wildcard):

```bash
set -euo pipefail
cd "$PROJECT_ROOT/.worktrees/<feature>/artifacts"
ARTIFACT_ROOT="$PWD"; CODE_ROOT=<resolved-distinct-code-root>
ARTIFACT_REF=refs/heads/artifacts/<feature>
test -z "$(git ls-remote --heads origin "$ARTIFACT_REF")"
test "$(git rev-parse --show-toplevel)" = "$PWD"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-lifecycle-state \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" --feature <feature>
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
test "$(git ls-remote --heads origin "$ARTIFACT_REF" | awk 'NR==1 {print $1}')" = "$SIDECAR_SHA"
```

Any error, unexpected staged path/parent, rejection, or SHA mismatch blocks. This publishes no code, feature,
target, tag, or release ref and permits no other remote effect.

## Feature and Package Setup

```bash
set -euo pipefail
cd "$PROJECT_ROOT"
git branch feature/<feature> <base-ref>
git worktree add .worktrees/<feature>/wp-<WP-ID> -b wp/<feature>/<WP-ID> <base-ref>
git worktree add .worktrees/<feature>/merge feature/<feature>
```

The integration worktree is the top code state; stacked readiness also names every base/follow-up artifact set.
Branch dependents only after prerequisite acceptance. Merge there with `git merge wp/<feature>/<WP-ID> --no-edit`.
Feature publication is separate covered authority; it never authorizes target merge/push or sidecar cleanup.

## Quiescent Code-Before-Sidecar Checkpoint

Verify owner/generation/budgets, clean code, expected remote parents, and finalized paths. Publish/verify code,
then update Lifecycle State; validate it against the exact committed sidecar parent before path-specific staging:

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
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-lifecycle-state \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" --feature <feature> \
  --previous-commit "$EXPECTED_PARENT"
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

No force, mutable ref reuse, sidecar-first publication, local-only referenced code, or broad staging. Before the
checkpoint, prove the candidate differs only by the
approved status mutation; any other drift blocks.

## Safe Resume

Fetch/verify exact artifact ref/SHA, check out that commit, derive its sole Git parent for generation >1, and run
`validate-lifecycle-state` with that full parent SHA. Then fetch and verify every named code ref/SHA using the Git
commands above. Helper digest success does not prove remote reachability. Ignore unreferenced checkpoints and treat
later local files/commits as untrusted. On parent/owner/generation/budget/deadline/quiescence/ref uncertainty, do
not push or take over; report only the validated `last_verified` fallback.

## Stop If

Stop on unsafe/equal roots, current-root authority, incomplete migration, ref/path collision, dirty code, missing
permission, unexpected parent, non-fast-forward/CAS rejection, staged-path mismatch, unverified code SHA,
predecessor not integrated, or any target merge/push, force, release/tag, cleanup, or deletion request.
