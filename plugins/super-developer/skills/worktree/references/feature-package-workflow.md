# Feature Package Workflow
Use for planned-feature sidecar/package/checkpoint work. The parent-supplied artifact-store contract owns authority,
roots, migration, and permission; this file owns Git/CAS commands.
## Contract
- Sidecar: orphan `refs/heads/artifacts/<feature>` at `.worktrees/<feature>/artifacts`; artifacts only.
- Feature: `refs/heads/feature/<feature>` at `.worktrees/<feature>/merge`; packages use
  `refs/heads/wp/<feature>/<WP-ID>` at `.worktrees/<feature>/wp-<WP-ID>`.
- Code checkpoints are unique immutable `refs/heads/checkpoints/<feature>/<slot>/g<generation>` refs.
- Package agents edit assigned code worktrees. The Delivery Owner owns refs/worktrees/merges/checkpoints/cleanup;
  never switch/edit the user root. Sidecar Portability and Implementation Authorizations cover only exact refs and
  endpoints, never target/release/force/delete operations.
## Exact Push Endpoint Fence
Require one configured push endpoint per owning root. Capture it; reject zero/multiple endpoints, authorization
mismatch, or config change. Pass the endpoint—not a remote name—as one quoted argv value:
```bash
capture_push_endpoint() {
  local name="$1" authorized="$2" output; local -a endpoints
  output="$(git remote get-url --push --all "$name")" || return 1; mapfile -t endpoints <<<"$output"
  test "${#endpoints[@]}" -eq 1 && test -n "${endpoints[0]}" && test "${endpoints[0]}" = "$authorized"
  printf '%s' "${endpoints[0]}"
}
assert_push_endpoint_unchanged() { test "$(capture_push_endpoint "$1" "$2")" = "$2"; }
verify_remote_direct_ref() {
  local name="$1" endpoint="$2" ref="$3" sha="$4" advertised advertised_ref; local -a rows
  assert_push_endpoint_unchanged "$name" "$endpoint"; mapfile -t rows < <(git ls-remote --heads -- "$endpoint" "$ref")
  test "${#rows[@]}" -eq 1; read -r advertised advertised_ref <<<"${rows[0]}"
  test "$advertised" = "$sha"; test "$advertised_ref" = "$ref"; assert_push_endpoint_unchanged "$name" "$endpoint"
  git fetch --no-tags -- "$endpoint" "$ref"; test "$(git rev-parse FETCH_HEAD)" = "$sha"
  if git symbolic-ref -q "$ref" >/dev/null; then echo "symbolic direct ref" >&2; return 1; else test "$?" -eq 1; fi
  if git show-ref --verify --quiet "$ref"; then test "$(git show-ref --verify --hash "$ref")" = "$sha"; else test "$?" -eq 1; printf 'create %s %s\n' "$ref" "$sha" | git update-ref --no-deref --stdin; fi
  if git symbolic-ref -q "$ref" >/dev/null; then return 1; else test "$?" -eq 1; fi; test "$(git show-ref --verify --hash "$ref")" = "$sha"; git cat-file -e "$sha^{commit}"
}
create_untrusted_recovery_ref() {
  local ref="$1" sha="$2"
  if git symbolic-ref -q "$ref" >/dev/null; then echo "symbolic recovery-ref collision" >&2; return 1; else test "$?" -eq 1; fi
  if git show-ref --verify --quiet "$ref"; then echo "existing recovery-ref collision" >&2; return 1; else test "$?" -eq 1; fi
  printf 'create %s %s\n' "$ref" "$sha" | git update-ref --no-deref --stdin
  if git symbolic-ref -q "$ref" >/dev/null; then return 1; else test "$?" -eq 1; fi; test "$(git show-ref --verify --hash "$ref")" = "$sha"
}
stage_exact_finalized_paths() (
  set -euo pipefail; test "$#" -gt 0; git diff --cached --quiet --
  INVENTORY="$(mktemp -d)"; trap 'rm -rf -- "$INVENTORY"' EXIT
  printf '%s\0' "$@" | LC_ALL=C sort -zu >"$INVENTORY/EXPECTED"
  git -c diff.renames=false diff --name-only --no-renames -z -- >"$INVENTORY/TRACKED"
  git ls-files --others --exclude-standard -z >"$INVENTORY/UNTRACKED"
  cat "$INVENTORY/TRACKED" "$INVENTORY/UNTRACKED" | LC_ALL=C sort -zu >"$INVENTORY/DIRTY"
  cmp -s "$INVENTORY/EXPECTED" "$INVENTORY/DIRTY"
  git add -- "$@"
  git -c diff.renames=false diff --cached --name-only --no-renames -z -- | LC_ALL=C sort -zu >"$INVENTORY/STAGED"
  cmp -s "$INVENTORY/EXPECTED" "$INVENTORY/STAGED"; test -s "$INVENTORY/STAGED"
)
```
A fetch URL cannot prove a distinct `pushurl`; aliases, rewrites, and fallback selection cannot cross roots.
## Layout and Local Sidecar Setup
Use `.worktrees/<feature>/{artifacts,merge,wp-<WP-ID>}`. Before writes require Git >=2.42, absent/empty destination,
ignored `.worktrees/`, and absent artifact ref. Create the empty orphan sidecar; legacy import records provenance and never moves source.
## Initial Authorized Sidecar Publication
Prove Sidecar Portability Authorization and generation-1 null topology. Finalized files must already exist as the
only dirty paths; a clean artifact root here would make publication impossible.
```bash
set -euo pipefail; cd "$PROJECT_ROOT/.worktrees/<feature>/artifacts"
ARTIFACT_ROOT="$PWD"; CODE_ROOT=<distinct-code-root>; ARTIFACT_REF=refs/heads/artifacts/<feature>
ARTIFACT_PUSH_ENDPOINT="$(capture_push_endpoint origin "$AUTHORIZED_ARTIFACT_PUSH_ENDPOINT")"
test "$(git rev-parse --show-toplevel)" = "$PWD"; test -z "$(git -C "$CODE_ROOT" status --porcelain=v1 --untracked-files=all)"
git diff --cached --quiet --; assert_push_endpoint_unchanged origin "$ARTIFACT_PUSH_ENDPOINT"
REMOTE_OUTPUT="$(git ls-remote --heads -- "$ARTIFACT_PUSH_ENDPOINT" "$ARTIFACT_REF")"; test -z "$REMOTE_OUTPUT"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-lifecycle-state --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" --feature <feature>
FINALIZED_PATHS=(<exact-finalized-paths>); stage_exact_finalized_paths "${FINALIZED_PATHS[@]}"
git commit -m "artifacts: initialize <feature>"; test -z "$(git status --porcelain=v1 --untracked-files=all)"; SIDECAR_SHA="$(git rev-parse HEAD)"
assert_push_endpoint_unchanged origin "$ARTIFACT_PUSH_ENDPOINT"; git push -- "$ARTIFACT_PUSH_ENDPOINT" "$SIDECAR_SHA:$ARTIFACT_REF"
verify_remote_direct_ref origin "$ARTIFACT_PUSH_ENDPOINT" "$ARTIFACT_REF" "$SIDECAR_SHA"
```
## Feature and Package Setup
Create feature/package worktrees from accepted predecessors; dependents branch only after prerequisite acceptance.
Use `merge/` as top code state. Stacked readiness names every base/follow-up artifact set. Feature publication has
its own authorized endpoint/ref; target effects remain separate.
## Quiescent Code-Before-Sidecar Checkpoint
Verify owner/generation/budgets, exact endpoints/parents, and finalized paths; publish code before sidecar:
```bash
set -euo pipefail; cd "$CODE_ROOT"; test -z "$(git status --porcelain=v1 --untracked-files=all)"; CODE_PUSH_ENDPOINT="$(capture_push_endpoint origin "$AUTHORIZED_CODE_PUSH_ENDPOINT")"
CODE_SHA="$(git rev-parse HEAD)"; CODE_REF=refs/heads/checkpoints/<feature>/<slot>/g<generation>
assert_push_endpoint_unchanged origin "$CODE_PUSH_ENDPOINT"; REMOTE_SHA="$(git ls-remote --heads -- "$CODE_PUSH_ENDPOINT" "$CODE_REF" | awk 'NR==1 {print $1}')"
if [ -n "$REMOTE_SHA" ] && [ "$REMOTE_SHA" != "$CODE_SHA" ]; then exit 1; fi
if git symbolic-ref -q "$CODE_REF" >/dev/null; then exit 1; else test "$?" -eq 1; fi
if git show-ref --verify --quiet "$CODE_REF"; then test "$(git show-ref --verify --hash "$CODE_REF")" = "$CODE_SHA"; else test "$?" -eq 1; printf 'create %s %s\n' "$CODE_REF" "$CODE_SHA" | git update-ref --no-deref --stdin; fi
if git symbolic-ref -q "$CODE_REF" >/dev/null; then exit 1; else test "$?" -eq 1; fi; test "$(git show-ref --verify --hash "$CODE_REF")" = "$CODE_SHA"
assert_push_endpoint_unchanged origin "$CODE_PUSH_ENDPOINT"; git push -- "$CODE_PUSH_ENDPOINT" "$CODE_REF:$CODE_REF"
verify_remote_direct_ref origin "$CODE_PUSH_ENDPOINT" "$CODE_REF" "$CODE_SHA"
cd "$ARTIFACT_ROOT"; git diff --cached --quiet --; ARTIFACT_PUSH_ENDPOINT="$(capture_push_endpoint origin "$AUTHORIZED_ARTIFACT_PUSH_ENDPOINT")"
ARTIFACT_REF=refs/heads/artifacts/<feature>; EXPECTED_PARENT=<last-verified-sidecar-sha>; test "$(git rev-parse HEAD)" = "$EXPECTED_PARENT"
assert_push_endpoint_unchanged origin "$ARTIFACT_PUSH_ENDPOINT"; test "$(git ls-remote --heads -- "$ARTIFACT_PUSH_ENDPOINT" "$ARTIFACT_REF" | awk 'NR==1 {print $1}')" = "$EXPECTED_PARENT"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-lifecycle-state --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" --feature <feature> --previous-commit "$EXPECTED_PARENT"
FINALIZED_PATHS=(<exact-finalized-paths>); stage_exact_finalized_paths "${FINALIZED_PATHS[@]}"
git commit -m "artifacts: checkpoint <feature> g<generation>"; test -z "$(git status --porcelain=v1 --untracked-files=all)"; SIDECAR_SHA="$(git rev-parse HEAD)"
assert_push_endpoint_unchanged origin "$ARTIFACT_PUSH_ENDPOINT"; git push -- "$ARTIFACT_PUSH_ENDPOINT" "$SIDECAR_SHA:$ARTIFACT_REF"
verify_remote_direct_ref origin "$ARTIFACT_PUSH_ENDPOINT" "$ARTIFACT_REF" "$SIDECAR_SHA"
```
The NUL-safe inventory rejects every unrelated dirty path before exact staging; post-stage equality and post-commit
cleanliness are mandatory. No broad staging, force, mutable ref, sidecar-first, local-only, or cross-endpoint trust.
## Safe Resume and Stops
Remote reachability belongs here. Start only from the exact committed remotely authoritative `parked`/quiescent
snapshot, never a local branch. Roots must be clean; quarantine later clean state without adopting files/receipts:
```bash
set -euo pipefail; cd "$ARTIFACT_ROOT"; test -z "$(git status --porcelain)"; ARTIFACT_REF=refs/heads/artifacts/<feature>
ARTIFACT_PUSH_ENDPOINT="$(capture_push_endpoint origin "$AUTHORIZED_ARTIFACT_PUSH_ENDPOINT")"; PARKED_SHA=<expected-sha>
assert_push_endpoint_unchanged origin "$ARTIFACT_PUSH_ENDPOINT"; git fetch --no-tags -- "$ARTIFACT_PUSH_ENDPOINT" "$ARTIFACT_REF"; test "$(git rev-parse FETCH_HEAD)" = "$PARKED_SHA"; LOCAL_SHA="$(git rev-parse HEAD)"
if [ "$LOCAL_SHA" != "$PARKED_SHA" ]; then create_untrusted_recovery_ref refs/recovery-untrusted/<feature>/g<local-generation> "$LOCAL_SHA"; git reset --hard "$PARKED_SHA"; fi
```
Read only that blob. Prove exact owner/no concurrent claimant, parent/generation, deadline, fixed maxima/issued usage
and role consumption, packages, clusters/strikes, freeze/receipts, routing/map, and recorded resume point.
For every named direct code ref call `verify_remote_direct_ref`; quarantine differences under `refs/recovery-untrusted/`.
Then restore only recorded stage/actions; use the same token/host or takeover bound to the parked token, host,
generation, and canonical state digest. Re-read the remote sidecar parent and CAS. No active-active, lease-time
takeover, local-only fallback, impersonation, reset, or degraded coordinator.
## Supersede Baseline Before Terminal CAS
Capture the replacement artifact and any non-null code endpoint independently:
```bash
cd "$REPLACEMENT_ARTIFACT_ROOT"; REPLACEMENT_ARTIFACT_PUSH_ENDPOINT="$(capture_push_endpoint origin "$AUTHORIZED_REPLACEMENT_ARTIFACT_PUSH_ENDPOINT")"
verify_remote_direct_ref origin "$REPLACEMENT_ARTIFACT_PUSH_ENDPOINT" "$REPLACEMENT_ARTIFACT_REF" "$REPLACEMENT_ARTIFACT_SHA"
if [ -n "${REPLACEMENT_CODE_REF:-}" ]; then
  cd "$REPLACEMENT_CODE_ROOT"; REPLACEMENT_CODE_PUSH_ENDPOINT="$(capture_push_endpoint origin "$AUTHORIZED_REPLACEMENT_CODE_PUSH_ENDPOINT")"
  verify_remote_direct_ref origin "$REPLACEMENT_CODE_PUSH_ENDPOINT" "$REPLACEMENT_CODE_REF" "$REPLACEMENT_CODE_SHA"
fi
```
The endpoint values remain in authorization/covered actions. Reject absent/local-only/unfetched/symbolic/mismatched refs
or same-old commits. Require active/null-supersession replacement State parent/digest/transition/ancestry, mapped
targets, and exact null-or-object code equality. Only then re-check old endpoint/parent and commit/non-force
push/verify terminal `superseded` through the sidecar checkpoint flow.
Stop on zero/multiple/changed endpoint; unsupported Git, remote, atomic non-force ref, or direct-ref capability;
no exact parked
checkpoint; dirty/unsafe/equal roots; SHA, ancestry, owner, budget, deadline, cluster, parent, inventory, or staged-
path mismatch; or target/force/release/delete/cleanup effects; prove the candidate differs only by the
approved status mutation.
