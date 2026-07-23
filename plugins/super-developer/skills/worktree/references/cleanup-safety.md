# Cleanup and Delivery Safety

Load before removal, pushes, target merge, or teardown. Every block is fresh Bash with `set -euo pipefail`; failed
proof stops later SHA capture, push, removal, or deletion. Root checkout files/index remain untouched.

## Cleanup Approval Binding
Every named cleanup subset binds:
```text
worktree_path=<path>; worktree_head=<sha>; worktree_state=<checksum>
local_ref=<full refs/heads/...>; local_ref_kind=direct; local_ref_sha=<sha>
landing_worktree=<path|not_applicable>; landing_head=<sha|not_applicable>;
  landing_state=<checksum|not_applicable>
remote_ref=<ref|none>; expected_remote_ref_sha=<sha|absent>
```
Recapture each binding immediately before action. A local ref must be direct: `git symbolic-ref -q <full-ref>`
success is a blocker. Delete only with `git update-ref --no-deref -d <full-ref> <approved-old-sha>`; concurrent
movement fails CAS. Remote deletion never follows failed local cleanup. Orchestration may run at `$PROJECT_ROOT`.

## Package Cleanup — Whole Feature Only
Use this section only for delivery context `feature`. Do not use this section for individual-package cleanup;
enter only once whole-feature preconditions pass: all registry packages are delivered/verified and merged into
clean integration `HEAD`, final integrated review/audit passes, remote feature SHA equals that `HEAD`, and any
contracted later target/base delivery gate is complete. Ancestry alone is never sufficient. Planned-hotfix uses
its separately contracted bugfix/hotfix cleanup path and never requires a feature ref/SHA.

Bind each package and the integration worktree. Recapture integration HEAD/state immediately before ancestry:
```bash
set -euo pipefail
PKG="$PROJECT_ROOT/.worktrees/<feature>/wp-<WP-ID>"
LANDING="$PROJECT_ROOT/.worktrees/<feature>/merge"
test "$(git -C "$PKG" rev-parse HEAD)" = "<approved-worktree-head>"
test "$RECAPTURED_WORKTREE_STATE_CHECKSUM" = "<approved-worktree-state-checksum>"
LANDING_HEAD="$(git -C "$LANDING" rev-parse HEAD)"
test "$LANDING_HEAD" = "<approved-integration-head>"
test "$RECAPTURED_LANDING_STATE_CHECKSUM" = "<approved-integration-state-checksum>"
git -C "$LANDING" merge-base --is-ancestor <approved-local-ref-sha> "$LANDING_HEAD"
cd "$PROJECT_ROOT"; git worktree remove "$PKG"
REF=refs/heads/wp/<feature>/<WP-ID>
if git symbolic-ref -q "$REF"; then exit 1; fi
test "$(git rev-parse "$REF")" = "<approved-local-ref-sha>"
git update-ref --no-deref -d "$REF" <approved-local-ref-sha>
```
Remove package candidates only inside the approved whole-feature cleanup sequence. Keep integration/sidecar
safety nets through delivery. Never force-remove dirty/unmerged state.

## Normal Feature Checkpoints and Sidecar Pushes
The feature-checkpoint block applies only to delivery context `feature`; its Execution Contract covers every
repetition and implies no user-known SHA/snapshot fields. Planned-hotfix creates no feature ref/SHA and retains
its separately contracted `hotfix/<name>` source publication:
```bash
set -euo pipefail
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
test "$(git symbolic-ref --short HEAD)" = "feature/<feature>"; test -z "$(git status --porcelain)"
LOCAL_SHA="$(git rev-parse HEAD)"
git push origin "HEAD:refs/heads/feature/<feature>"
REMOTE_LINE="$(git ls-remote --heads origin refs/heads/feature/<feature>)"; test -n "$REMOTE_LINE"
REMOTE_SHA="${REMOTE_LINE%%$'\t'*}"; test "$REMOTE_SHA" = "$LOCAL_SHA"
```
```bash
set -euo pipefail
cd "$PROJECT_ROOT/.worktrees/<feature>/artifacts"
git push -u origin artifacts/<feature>
```
Neither approves target delivery or cleanup; never merge artifact refs into code history.

## Immutable Target Merge and Push
Merge approval binds source/pre-target SHAs, snapshot, strategy, integration ref/worktree. Compare immutable SHAs:
```bash
set -euo pipefail
if git merge-base --is-ancestor <source-sha> <pre-merge-target-sha>; then exit 0
else S=$?; test "$S" -eq 1; fi
cd "$PROJECT_ROOT"
git worktree add -b integrate/<delivery>-target .worktrees/<delivery>/target-merge <pre-merge-target-sha>
cd .worktrees/<delivery>/target-merge
test "$(git rev-parse HEAD)" = "<pre-merge-target-sha>"
git merge --no-ff <source-sha> -m "merge: <delivery> -- <summary>"
RESULT_SHA="$(git rev-parse HEAD)"
printf 'RESULT_SHA=%s\n' "$RESULT_SHA"
```
Status 1 alone means merge needed. A clean approved non-root target checkout may substitute. Locked local target
stays unchanged; report only the integration result, then request target-push approval.

Target push binds remote/ref, result, and expected remote SHA. Recapture, prove FF ancestry, and exact server CAS:
```bash
set -euo pipefail
RESULT_SHA=<result-sha>; EXPECTED=<expected-remote-target-sha>; TARGET_REF=refs/heads/<target-ref>
cd "$PROJECT_ROOT/.worktrees/<delivery>/target-merge"
test "$(git rev-parse HEAD)" = "$RESULT_SHA"
REMOTE_LINE="$(git ls-remote --heads <remote> "$TARGET_REF")"; test -n "$REMOTE_LINE"
REMOTE_SHA="${REMOTE_LINE%%$'\t'*}"; test "$REMOTE_SHA" = "$EXPECTED"
git merge-base --is-ancestor "$EXPECTED" "$RESULT_SHA"
git push --force-with-lease="$TARGET_REF:$EXPECTED" <remote> "$RESULT_SHA:$TARGET_REF"
```
Bare force, unqualified lease, or missing ancestry proof is forbidden. Push failure preserves safety nets.

## Feature Cleanup
Use only for delivery context `feature`. Recapture the current delivery landing state before removing its feature
worktree/ref; stale approved SHA is insufficient:
```bash
set -euo pipefail
FEATURE_WT="$PROJECT_ROOT/.worktrees/<feature>/merge"
LANDING="$PROJECT_ROOT/.worktrees/<feature>/target-merge"
test "$(git -C "$FEATURE_WT" rev-parse HEAD)" = "<approved-worktree-head>"
test "$RECAPTURED_WORKTREE_STATE_CHECKSUM" = "<approved-worktree-state-checksum>"
LANDING_HEAD="$(git -C "$LANDING" rev-parse HEAD)"
test "$LANDING_HEAD" = "<approved-delivery-result-sha>"
test "$RECAPTURED_LANDING_STATE_CHECKSUM" = "<approved-delivery-state-checksum>"
git -C "$LANDING" merge-base --is-ancestor <approved-local-ref-sha> "$LANDING_HEAD"
cd "$PROJECT_ROOT"; git worktree remove "$FEATURE_WT"
REF=refs/heads/feature/<feature>
if git symbolic-ref -q "$REF"; then exit 1; fi
git update-ref --no-deref -d "$REF" <approved-local-ref-sha>
git worktree remove "$LANDING"
```
Temporary integration refs need their own direct-ref SHA/state binding. Remote deletion is separately approved.

## Sidecar, Bugfix/Hotfix, and Spike Cleanup
Sidecar/spike require exact HEAD/state/status proof and direct-ref CAS:
```bash
set -euo pipefail
WT=<approved-sidecar-or-spike-worktree>
REF=refs/heads/artifacts/<feature> # OR: REF=refs/heads/spike/<name>
test "$(git -C "$WT" rev-parse HEAD)" = "<approved-worktree-head>"
test "$RECAPTURED_WORKTREE_STATE_CHECKSUM" = "<approved-worktree-state-checksum>"
test -z "$(git -C "$WT" status --porcelain)"
cd "$PROJECT_ROOT"; git worktree remove "$WT"
if git symbolic-ref -q "$REF"; then exit 1; fi
git update-ref --no-deref -d "$REF" <approved-local-ref-sha>
```
Bugfix/hotfix additionally recapture current landing HEAD/state and prove repair SHA ancestry before removal:
```bash
set -euo pipefail
REPAIR_WT=<approved-bugfix-or-hotfix-worktree>; LANDING=<approved-landing-worktree>
test "$(git -C "$REPAIR_WT" rev-parse HEAD)" = "<approved-worktree-head>"
test "$RECAPTURED_WORKTREE_STATE_CHECKSUM" = "<approved-worktree-state-checksum>"
LANDING_HEAD="$(git -C "$LANDING" rev-parse HEAD)"
test "$LANDING_HEAD" = "<approved-landing-head>"
test "$RECAPTURED_LANDING_STATE_CHECKSUM" = "<approved-landing-state-checksum>"
git -C "$LANDING" merge-base --is-ancestor <approved-local-ref-sha> "$LANDING_HEAD"
cd "$PROJECT_ROOT"; git worktree remove "$REPAIR_WT"
REF=<approved-full-direct-ref>
if git symbolic-ref -q "$REF"; then exit 1; fi
git update-ref --no-deref -d "$REF" <approved-local-ref-sha>
```
Remote deletion, when approved, runs its exact remote-SHA lease only after successful local CAS. Disposable rules
never apply to package, feature, bugfix, hotfix, or integration refs.
