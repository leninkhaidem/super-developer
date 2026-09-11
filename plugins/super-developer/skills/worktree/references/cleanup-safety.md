# Cleanup and Delivery Safety
Load before removal, pushes, target merge, or teardown. For planned-feature source publication, consume the
parent-supplied source-publication contract loaded at this action by `worktree`. Every block is fresh Bash with
`set -euo pipefail`; failed proof stops later SHA capture, push, removal, or deletion. Root checkout files/index
remain untouched.
## Cleanup Authority Binding
Normal cleanup binds canonical path, HEAD/complete state, full direct ref/SHA, landing/base state when required,
and remote expected state only for separately authorized remote actions. Recapture immediately; direct-ref deletion
uses `git update-ref --no-deref -d <full-ref> <old-sha>` CAS after normal worktree removal. Never force.
## Receipt-Bound Probe Boundary
A probe authorized by an auto-resolve Execution Contract or exact current-task probe approval may clean only through
its creation receipt and `probe-cleanup.md`: classify NUL deltas, restore/remove exact owned state, and prove full
ref/expected base/index digest/status/process/data closure before normal removal/direct full-ref CAS. Locally verify
no tracking config and `remote_action=none`; perform no network/credential check or remote mutation. A coincidental
remote ref stays untouched. Any unowned/uncertain delta preserves the probe and stops.
Continuation package worktrees/refs—active or retired—never use receipt-bound probe cleanup and remain through final gates.
## Package Cleanup — Whole Feature Only
No active or retired package cleanup occurs before all packages, final integrated review/audit, every source
publication gate actually due under the approved policy, and contracted later delivery gates pass. `local-only` or
publication not yet due creates no remote-synchronization prerequisite. Planned hotfix applies the same tip
eligibility at its separate final cleanup gate against final hotfix integration HEAD.
At final cleanup, bind kind (`initial|continuation`), creation base SHA, tip/ref, path/HEAD/state, and final clean
integration HEAD/state. Remove only when tip is integrated, or a continuation tip equals its creation base:
```bash
set -euo pipefail
PKG="$PROJECT_ROOT/.worktrees/<feature>/wp-<WP-ID>"; LANDING="$PROJECT_ROOT/.worktrees/<feature>/merge"
REF=refs/heads/wp/<feature>/<WP-ID>; TIP=<bound-tip>; BASE=<bound-creation-base>; KIND=<initial|continuation>
test "$(git -C "$PKG" symbolic-ref -q HEAD)" = "$REF"; test "$(git -C "$PKG" rev-parse HEAD)" = "$TIP"
test "$(git -C "$PROJECT_ROOT" rev-parse "$REF")" = "$TIP"
test "$RECAPTURED_WORKTREE_STATE_CHECKSUM" = "<bound-clean-state>"; test -z "$(git -C "$PKG" status --porcelain)"
FINAL="$(git -C "$LANDING" rev-parse HEAD)"; test "$FINAL" = "<bound-final-integration-head>"
test "$RECAPTURED_LANDING_STATE_CHECKSUM" = "<bound-final-clean-state>"
if git -C "$LANDING" merge-base --is-ancestor "$TIP" "$FINAL"; then :
elif test "$KIND" = continuation && test "$TIP" = "$BASE"; then :
else printf 'preserve: unique unmerged package commits ref=%s tip=%s base=%s final=%s\n' "$REF" "$TIP" "$BASE" "$FINAL" >&2; exit 1
fi
cd "$PROJECT_ROOT"; git worktree remove "$PKG"
if git symbolic-ref -q "$REF"; then exit 1; fi
git update-ref --no-deref -d "$REF" "$TIP"
```
If unique unmerged commits remain, retain and report the safety net. Never force, reset, stash, or delete it.
## Feature Source and Sidecar Publication
For delivery context `feature`, use only the loaded source-publication policy and exact scheduled command. Preserve a
local recovery commit/ref for every package. A `local-only` or non-due gate performs no source network action; a due
remote gate stops on any network/credential/push/SHA-verification failure. Planned hotfix creates no feature ref and
uses only its separately contracted exact `hotfix/<name>` source gate.

Sidecar publication remains independently authorized and runs only from its artifact worktree:
```bash
set -euo pipefail
cd "$PROJECT_ROOT/.worktrees/<feature>/artifacts"
git push -u origin artifacts/<feature>
```
Neither source nor sidecar publication approves the other, target delivery, or cleanup. Never merge artifact refs
into code history.
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
## Sidecar and Bugfix/Hotfix Cleanup
Sidecars require exact approved path/HEAD/state and direct-ref CAS:
```bash
set -euo pipefail
WT=<approved-sidecar-worktree>; REF=refs/heads/artifacts/<feature>
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
Remote deletion, when approved, runs its exact remote-SHA lease only after successful local CAS. Probe cleanup is
local-only under its receipt procedure; package cleanup occurs only at the final whole-feature gate above.
