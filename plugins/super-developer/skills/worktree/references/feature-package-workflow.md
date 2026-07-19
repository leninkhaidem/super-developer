# Feature Package Workflow
Use for planned-feature sidecar, package, integration, and checkpoint work. The parent-supplied artifact-store
contract owns authority, roots, migration, permission, and state; this file alone owns Git/CAS commands.
## Contract
- Sidecar: orphan `refs/heads/artifacts/<feature>` at `.worktrees/<feature>/artifacts`; artifacts only.
- Feature: `refs/heads/feature/<feature>` at `.worktrees/<feature>/merge`; package:
  `refs/heads/wp/<feature>/<WP-ID>` at `.worktrees/<feature>/wp-<WP-ID>`.
- Immutable code checkpoint: `refs/heads/checkpoints/<feature>/<slot>/g<generation>`; unique and never moved.
- Package agents edit assigned code worktrees. Delivery Owner owns refs/worktrees/merges/checkpoints/cleanup. Never
  switch/edit the user root; roots are distinct and `.worktrees/` is ignored.
- Sidecar Portability Authorization covers the exact artifact ref **and push endpoint** for discovery/planning.
  Implementation Authorization separately covers every exact code/artifact/feature push endpoint and ref. Neither
  covers target/release/force/delete operations.
## Exact Push Endpoint Fence
For every root that will read or write a remote ref, authorization names one exact configured push endpoint. In
that root capture the operational endpoint once; reject no endpoint, multiple endpoints, an authorization mismatch,
or a later config change. Assertions re-read config only to compare; they never replace the capture. Keep using the
captured value as one quoted argv value—never the remote name—for `ls-remote`, `push`, `fetch`, and post-check:
```bash
capture_push_endpoint() {
  local name="$1" authorized="$2" output; local -a endpoints
  output="$(git remote get-url --push --all "$name")" || return 1; mapfile -t endpoints <<<"$output"
  test "${#endpoints[@]}" -eq 1 && test -n "${endpoints[0]}" && test "${endpoints[0]}" = "$authorized"
  printf '%s' "${endpoints[0]}"
}
assert_push_endpoint_unchanged() { test "$(capture_push_endpoint "$1" "$2")" = "$2"; }
create_untrusted_recovery_ref() {
  local ref="$1" sha="$2"
  if git symbolic-ref -q "$ref" >/dev/null; then echo "symbolic recovery-ref collision" >&2; return 1; else test "$?" -eq 1; fi
  if git show-ref --verify --quiet "$ref"; then echo "existing recovery-ref collision" >&2; return 1; else test "$?" -eq 1; fi
  printf 'create %s %s\n' "$ref" "$sha" | git update-ref --no-deref --stdin
  if git symbolic-ref -q "$ref" >/dev/null; then return 1; else test "$?" -eq 1; fi; test "$(git show-ref --verify --hash "$ref")" = "$sha"
}
```
A fetch URL is not evidence about a distinct `pushurl`. Do not let endpoint aliases, rewrites, or fallback remote
selection cross the authorization boundary.
## Layout and Local Sidecar Setup
Under `.worktrees/<feature>/`, use `artifacts/` for the sidecar, `wp-<WP-ID>/` for package code, and `merge/` for integration. Create before artifact writes; destination absent/empty, Git >=2.42, ref absent:
```bash
set -euo pipefail
cd "$PROJECT_ROOT"
test ! -e .worktrees/<feature>/artifacts
mkdir -p .worktrees/<feature>
git show-ref --verify --quiet refs/heads/artifacts/<feature> && exit 1 || test $? -eq 1
git worktree add --orphan -b artifacts/<feature> .worktrees/<feature>/artifacts
```
Legacy import creates this empty sidecar first, records provenance, and never moves source.
## Initial Authorized Sidecar Publication
Prove Sidecar Portability Authorization for the exact endpoint/ref and generation-1 initial/null topology. Stage
only finalized Slices/Index, migration provenance when any, and Lifecycle State; initial publication cannot contain
a code checkpoint.
```bash
set -euo pipefail
cd "$PROJECT_ROOT/.worktrees/<feature>/artifacts"
ARTIFACT_ROOT="$PWD"; CODE_ROOT=<resolved-distinct-code-root>
ARTIFACT_REF=refs/heads/artifacts/<feature>
AUTHORIZED_ARTIFACT_PUSH_ENDPOINT='<exact-authorized-push-endpoint>'
ARTIFACT_PUSH_ENDPOINT="$(capture_push_endpoint origin "$AUTHORIZED_ARTIFACT_PUSH_ENDPOINT")"
test "$(git rev-parse --show-toplevel)" = "$PWD"
assert_push_endpoint_unchanged origin "$ARTIFACT_PUSH_ENDPOINT"
test -z "$(git ls-remote --heads -- "$ARTIFACT_PUSH_ENDPOINT" "$ARTIFACT_REF")"
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
assert_push_endpoint_unchanged origin "$ARTIFACT_PUSH_ENDPOINT"
git push -- "$ARTIFACT_PUSH_ENDPOINT" "$SIDECAR_SHA:$ARTIFACT_REF"
assert_push_endpoint_unchanged origin "$ARTIFACT_PUSH_ENDPOINT"
git fetch --no-tags -- "$ARTIFACT_PUSH_ENDPOINT" "$ARTIFACT_REF"
test "$(git rev-parse FETCH_HEAD)" = "$SIDECAR_SHA"
assert_push_endpoint_unchanged origin "$ARTIFACT_PUSH_ENDPOINT"
test "$(git ls-remote --heads -- "$ARTIFACT_PUSH_ENDPOINT" "$ARTIFACT_REF" | awk 'NR==1 {print $1}')" = "$SIDECAR_SHA"
```
## Feature and Package Setup
Create `feature/<feature>` from the authorized base, package branches/worktrees from accepted predecessors, and
`.worktrees/<feature>/merge` as the top code state for integration. Branch dependents only after prerequisite
acceptance; merge there with `git merge wp/<feature>/<WP-ID> --no-edit`. Stacked readiness names every
base/follow-up artifact set. Any feature publication uses its own captured, authorized endpoint
and exact ref; target merge/push and sidecar cleanup remain separate.
## Quiescent Code-Before-Sidecar Checkpoint
Verify owner/generation/budgets, clean code, exact authorized endpoints/remote parents, and finalized paths. In one
shell, capture `CODE_PUSH_ENDPOINT` in the code root and `ARTIFACT_PUSH_ENDPOINT` in the artifact root with the
fence above. For each endpoint, assert unchanged immediately before every command below:

```bash
set -euo pipefail
cd "$CODE_ROOT"; CODE_PUSH_ENDPOINT="$(capture_push_endpoint origin "$AUTHORIZED_CODE_PUSH_ENDPOINT")"; test -z "$(git status --porcelain)"
CODE_SHA="$(git rev-parse HEAD)"; CODE_REF=refs/heads/checkpoints/<feature>/<slot>/g<generation>
assert_push_endpoint_unchanged origin "$CODE_PUSH_ENDPOINT"; REMOTE_SHA="$(git ls-remote --heads -- "$CODE_PUSH_ENDPOINT" "$CODE_REF" | awk 'NR==1 {print $1}')"
if [ -n "$REMOTE_SHA" ] && [ "$REMOTE_SHA" != "$CODE_SHA" ]; then echo "immutable remote checkpoint mismatch" >&2; exit 1; fi
if git symbolic-ref -q "$CODE_REF" >/dev/null; then echo "symbolic checkpoint ref" >&2; exit 1; else test "$?" -eq 1; fi
if git show-ref --verify --quiet "$CODE_REF"; then test "$(git show-ref --verify --hash "$CODE_REF")" = "$CODE_SHA";
else test "$?" -eq 1; printf 'create %s %s\n' "$CODE_REF" "$CODE_SHA" | git update-ref --no-deref --stdin; fi
if git symbolic-ref -q "$CODE_REF" >/dev/null; then exit 1; else test "$?" -eq 1; fi; test "$(git show-ref --verify --hash "$CODE_REF")" = "$CODE_SHA"
assert_push_endpoint_unchanged origin "$CODE_PUSH_ENDPOINT"; git push -- "$CODE_PUSH_ENDPOINT" "$CODE_REF:$CODE_REF"
assert_push_endpoint_unchanged origin "$CODE_PUSH_ENDPOINT"; git fetch --no-tags -- "$CODE_PUSH_ENDPOINT" "$CODE_REF"; test "$(git rev-parse FETCH_HEAD)" = "$CODE_SHA"
assert_push_endpoint_unchanged origin "$CODE_PUSH_ENDPOINT"; test "$(git ls-remote --heads -- "$CODE_PUSH_ENDPOINT" "$CODE_REF" | awk 'NR==1 {print $1}')" = "$CODE_SHA"
cd "$ARTIFACT_ROOT"; ARTIFACT_PUSH_ENDPOINT="$(capture_push_endpoint origin "$AUTHORIZED_ARTIFACT_PUSH_ENDPOINT")"
ARTIFACT_REF=refs/heads/artifacts/<feature>; EXPECTED_PARENT=<last-verified-sidecar-sha>
assert_push_endpoint_unchanged origin "$ARTIFACT_PUSH_ENDPOINT"; test "$(git ls-remote --heads -- "$ARTIFACT_PUSH_ENDPOINT" "$ARTIFACT_REF" | awk 'NR==1 {print $1}')" = "$EXPECTED_PARENT"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-lifecycle-state \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" --feature <feature> --previous-commit "$EXPECTED_PARENT"
FINALIZED_PATHS=(<exact-finalized-paths-including-lifecycle-state>)
git add -- "${FINALIZED_PATHS[@]}"
mapfile -d '' -t EXPECTED < <(printf '%s\0' "${FINALIZED_PATHS[@]}" | sort -z); mapfile -d '' -t STAGED < <(git diff --cached --name-only -z | sort -z)
test "${#EXPECTED[@]}" -eq "${#STAGED[@]}"; for I in "${!EXPECTED[@]}"; do test "${EXPECTED[$I]}" = "${STAGED[$I]}"; done
git commit -m "artifacts: checkpoint <feature> g<generation>"
SIDECAR_SHA="$(git rev-parse HEAD)"
assert_push_endpoint_unchanged origin "$ARTIFACT_PUSH_ENDPOINT"; git push -- "$ARTIFACT_PUSH_ENDPOINT" "$SIDECAR_SHA:$ARTIFACT_REF"
assert_push_endpoint_unchanged origin "$ARTIFACT_PUSH_ENDPOINT"; git fetch --no-tags -- "$ARTIFACT_PUSH_ENDPOINT" "$ARTIFACT_REF"
test "$(git rev-parse FETCH_HEAD)" = "$SIDECAR_SHA"
assert_push_endpoint_unchanged origin "$ARTIFACT_PUSH_ENDPOINT"; test "$(git ls-remote --heads -- "$ARTIFACT_PUSH_ENDPOINT" "$ARTIFACT_REF" | awk 'NR==1 {print $1}')" = "$SIDECAR_SHA"
```

Also compare sorted staged paths exactly as in initial publication and prove the candidate differs only by the
approved status mutation. No force, mutable ref reuse, sidecar-first publication, local-only referenced code, broad
staging, or cross-endpoint verification.

## Safe Resume and Stops
Resume is legal only from one committed remotely authoritative `parked`/quiescent snapshot. Remote reachability belongs here, not to the helper. Capture one unchanged authorized endpoint per root; fetch/verify the exact sidecar ref first, never a local branch. Roots must be clean; quarantine a later clean local commit under an immutable CAS-created local-only untrusted ref, then reset to `FETCH_HEAD` without adopting any file/receipt:
```bash
set -euo pipefail
cd "$ARTIFACT_ROOT"; test -z "$(git status --porcelain)"; ARTIFACT_PUSH_ENDPOINT="$(capture_push_endpoint origin "$AUTHORIZED_ARTIFACT_PUSH_ENDPOINT")"; ARTIFACT_REF=refs/heads/artifacts/<feature>
assert_push_endpoint_unchanged origin "$ARTIFACT_PUSH_ENDPOINT"; mapfile -t REMOTE < <(git ls-remote --heads -- "$ARTIFACT_PUSH_ENDPOINT" "$ARTIFACT_REF"); test "${#REMOTE[@]}" -eq 1; REMOTE_SHA="${REMOTE[0]%%[[:space:]]*}"
assert_push_endpoint_unchanged origin "$ARTIFACT_PUSH_ENDPOINT"; git fetch --no-tags -- "$ARTIFACT_PUSH_ENDPOINT" "$ARTIFACT_REF"; test "$(git rev-parse FETCH_HEAD)" = "$REMOTE_SHA"
LOCAL_SHA="$(git rev-parse HEAD)"; if [ "$LOCAL_SHA" != "$REMOTE_SHA" ]; then RECOVERY_REF=refs/recovery-untrusted/<feature>/g<local-generation>; create_untrusted_recovery_ref "$RECOVERY_REF" "$LOCAL_SHA"; git reset --hard "$REMOTE_SHA"; fi
```
Read stage/actions and all refs only from that committed blob. Prove `parked`, quiescence, exact owner/no concurrent claimant, CAS parent/generation, deadline, fixed maxima/issued usage and role consumption, no reservation/active wave, package IDs/states, clusters/strikes, freeze/receipts, routing/map, and recorded resume point. For every named direct code ref (including replacement baseline provenance when present), repeat this exact fetch/direct-ref block before trust:
```bash
set -euo pipefail
cd "$CODE_ROOT"; test -z "$(git status --porcelain)"; CODE_PUSH_ENDPOINT="$(capture_push_endpoint origin "$AUTHORIZED_CODE_PUSH_ENDPOINT")"
assert_push_endpoint_unchanged origin "$CODE_PUSH_ENDPOINT"; git fetch --no-tags -- "$CODE_PUSH_ENDPOINT" "$CODE_REF"; test "$(git rev-parse FETCH_HEAD)" = "$CODE_SHA"
if git symbolic-ref -q "$CODE_REF" >/dev/null; then echo "symbolic checkpoint ref" >&2; exit 1; else test "$?" -eq 1; fi
if git show-ref --verify --quiet "$CODE_REF"; then test "$(git show-ref --verify --hash "$CODE_REF")" = "$CODE_SHA";
else test "$?" -eq 1; printf 'create %s %s\n' "$CODE_REF" "$CODE_SHA" | git update-ref --no-deref --stdin; fi
if git symbolic-ref -q "$CODE_REF" >/dev/null; then exit 1; else test "$?" -eq 1; fi; test "$(git show-ref --verify --hash "$CODE_REF")" = "$CODE_SHA"
LOCAL_CODE_SHA="$(git rev-parse HEAD)"; if [ "$LOCAL_CODE_SHA" != "$CODE_SHA" ]; then RECOVERY_REF=refs/recovery-untrusted/<feature>/code-g<local-generation>; create_untrusted_recovery_ref "$RECOVERY_REF" "$LOCAL_CODE_SHA"; git reset --hard "$CODE_SHA"; fi
git cat-file -e "$CODE_SHA^{commit}"; git merge-base --is-ancestor "$BASE_SHA" "$CODE_SHA"
```
Materialize code only at verified SHAs, then run `validate-lifecycle-state` against the parked blob's exact `last_verified` parent. Re-read the remote sidecar parent before the lifecycle-only resume CAS; restore only recorded stage/actions while preserving owner/authority/budgets/packages/clusters/refs/receipts/map. No active-active, lease-time takeover, local-only fallback, or degraded best-effort coordinator.
Stop on zero/multiple/changed endpoint or missing remote ref; unsupported Git, remote, atomic non-force ref, or direct-ref capability; dirty/unsafe/equal roots; current-root/migration ambiguity; symbolic/missing/mismatched ref, SHA, ancestry, owner, deadline, budget, cluster, parent or CAS; no exact parked checkpoint; or target/force/release/delete/cleanup effects.
