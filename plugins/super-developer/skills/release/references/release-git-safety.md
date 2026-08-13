# Release Git Safety
Owns release-specific remote freshness, resume validation, merge worktree, tag/release checks, sidecar state, and cleanup safety.
## Remote Freshness
Before contract approval when pushing, checking remote tags, publishing, or deleting remote branches:
```bash
git fetch --prune --tags origin
git ls-remote --heads --tags origin
```
Stop if remote state cannot be refreshed or verified for a push/delete/publish contract. Re-fetch before remote feature or sidecar deletion.
Use remote-tracking refs only after refresh. Never infer deletion safety from stale `origin/*` refs.
For `publish`, preflight GitHub state:
```bash
gh auth status
gh repo view --json nameWithOwner
gh release view vX.Y.Z --json tagName,targetCommitish,isDraft,isPrerelease,url  # ok to fail when absent
```
Stop if auth, repo identity, existing release state, or target commit is ambiguous.
## Resume Matrix
If any release step already exists, verify exact identity before resuming:
- Prepare integration commit exists: merge contents, `Unreleased` changelog entries, docs, checks, pushed-base state, and cleanup state match the contract.
- Publish release commit exists: version files, changelog/docs, release notes, and checks match intended `vX.Y.Z`.
- Local tag exists: `git rev-parse vX.Y.Z^{}` equals the intended publish commit.
- Remote tag exists: `git ls-remote --tags origin refs/tags/vX.Y.Z` target or peeled target equals the intended publish commit.
- GitHub release exists: tag, target commitish/tag target, draft/prerelease state, and notes match the contract.
- Base branch already pushed: `origin/<base>` contains the intended prepare/publish commit.
- Artifact sidecar cleanup exists: final checkpoint, contracted exact cleanup/default-keep list, and target/base push sync match the contract.
Stop on any mismatch. Do not move tags, overwrite releases, force-push, or force-delete unless a new explicit contract names that destructive action.
## Canonical Root Preflight
Before approval or publication, invoke `worktree`'s primary-root resolver and bind the canonical root's path, branch,
HEAD, porcelain status, local base SHA (or absence), and a SHA-256 receipt of the sorted, canonical, NUL-delimited
paths of all worktrees occupying the base branch. Require an attached, clean root; stop on a detached root rather than switching away
from a commit that may otherwise lack durable reachability. Require the binding stable and the local base equal to
or an ancestor of fresh `origin/<base>`. If root is not on the base branch, require that branch unoccupied elsewhere
so root can normalize immediately before publication; use a temporary integration ref rather than occupying it. Stop before
publication on dirt, drift, divergence, or any non-fast-forward/occupied-branch blocker. Do not switch or write root
during preflight or integration.
## Merge Worktree
Do not use the user-owned root worktree for integration. Refresh `origin`, bind the exact remote-base SHA, and
require any local base ref to equal or be an ancestor of it. Use a clean non-root checkout already on that exact
base only when it will not block the contracted canonical-root normalization. Otherwise create a named temporary
integration branch/worktree from the remote-base SHA—not from the locked local branch:
```bash
set -euo pipefail
BOUND_BASE=$(git rev-parse origin/<base>)
if git show-ref --verify --quiet refs/heads/<base>; then BOUND_LOCAL_BASE=$(git rev-parse --verify refs/heads/<base>); else REF_STATUS=$?; test "$REF_STATUS" -eq 1; BOUND_LOCAL_BASE=; fi
test -z "$BOUND_LOCAL_BASE" || git merge-base --is-ancestor "$BOUND_LOCAL_BASE" "$BOUND_BASE"
INTEGRATION_BRANCH=integrate/release-<name>; INTEGRATION_REF=refs/heads/$INTEGRATION_BRANCH
INTEGRATION_WORKTREE=.worktrees/release-<name>/target-merge
if git show-ref --verify --quiet "$INTEGRATION_REF"; then false; else REF_STATUS=$?; test "$REF_STATUS" -eq 1; fi
test ! -e "$INTEGRATION_WORKTREE"; test ! -L "$INTEGRATION_WORKTREE"
git worktree add --no-track -b "$INTEGRATION_BRANCH" "$INTEGRATION_WORKTREE" "$BOUND_BASE"
cd "$INTEGRATION_WORKTREE"
git merge --no-ff <feature-sha> -m "<contracted merge message>"
```
Use a prepare-style message for `prepare-only` and `release: vX.Y.Z` only for publish prep unless repository
convention differs. If the feature is already included, verify immutable-SHA ancestry instead. Resolve conflicts
only in the integration worktree and stop when they require uncontracted decisions.
## Base Push and Publish Checks
Before pushing, require the final diff/files, checks, changelog, publish state, and cleanup candidates to match the
contract; `prepare-only` still permits no version/tag/release change. Bind every value below from parent-owned
preflight receipts. Run this as one fresh Bash process after replacing each quoted placeholder with its bound
literal; it deliberately carries no hidden state from an integration shell.
```bash
set -euo pipefail
PROJECT_ROOT='<parent-bound-canonical-primary-root>'; BOUND_ROOT_BRANCH='<parent-bound-named-root-branch>'
BOUND_ROOT_HEAD='<parent-bound-root-head-sha>'; BOUND_LOCAL_BASE='<parent-bound-local-base-sha-or-empty>'
BOUND_BASE_OCCUPANCY_SHA256='<parent-bound-canonical-base-occupant-set-sha256>'; RESULT_SHA='<parent-bound-result-sha>'
EXPECTED='<parent-bound-remote-base-sha-from-preflight>'
TARGET_REF='refs/heads/<parent-bound-base-branch>'
BASE_BRANCH="${TARGET_REF#refs/heads/}"; REMOTE_TRACKING_REF="refs/remotes/origin/$BASE_BRANCH"
remote_sha() { git ls-remote --heads origin | awk -v ref="$TARGET_REF" '$2 == ref {print $1}'; }
base_occupancy_digest() { git worktree list --porcelain -z | python3 -c '
import hashlib, os, sys
if len(sys.argv) != 2: raise SystemExit("target ref argument required")
target = os.fsencode(sys.argv[1])
if not target.startswith(b"refs/heads/") or target == b"refs/heads/": raise SystemExit("invalid target ref")
paths = []
for record in (item for item in sys.stdin.buffer.read().split(b"\0\0") if item):
    fields = record.split(b"\0")
    branches = [field[7:] for field in fields if field.startswith(b"branch ")]
    if target not in branches: continue
    worktrees = [field[9:] for field in fields if field.startswith(b"worktree ")]
    malformed = any(field.startswith((b"branch", b"worktree")) and not field.startswith((b"branch ", b"worktree ")) for field in fields)
    if malformed or len(branches) != 1 or branches[0] != target or len(worktrees) != 1 or not os.path.isabs(worktrees[0]): raise SystemExit("ambiguous target-branch occupancy record")
    paths.append(os.path.realpath(worktrees[0]))
paths.sort()
sys.stdout.write(hashlib.sha256(b"\0".join(paths) + (b"\0" if paths else b"")).hexdigest())
' "$TARGET_REF"; }
expected_occupancy_digest() { python3 -c 'import hashlib,os,sys; p=sorted(os.path.realpath(os.fsencode(x)) for x in sys.argv[1:]); sys.stdout.write(hashlib.sha256(b"\0".join(p)+(b"\0" if p else b"")).hexdigest())' "$@"; }
test -n "$PROJECT_ROOT"; test "$(cd "$PROJECT_ROOT" && pwd -P)" = "$PROJECT_ROOT"
test -n "$BOUND_ROOT_BRANCH"; test -n "$BOUND_ROOT_HEAD"; test -n "$BOUND_BASE_OCCUPANCY_SHA256"; test -n "$RESULT_SHA"; test -n "$EXPECTED"
test -n "$BASE_BRANCH"; test "$TARGET_REF" = "refs/heads/$BASE_BRANCH"; git check-ref-format "$TARGET_REF"
COMMON_GIT_DIR="$(git -C "$PROJECT_ROOT" rev-parse --path-format=absolute --git-common-dir)"
ROOT_GIT_DIR="$(git -C "$PROJECT_ROOT" rev-parse --path-format=absolute --git-dir)"
test "$(cd "$COMMON_GIT_DIR" && pwd -P)" = "$(cd "$ROOT_GIT_DIR" && pwd -P)"; cd "$PROJECT_ROOT"
test "$(git branch --show-current)" = "$BOUND_ROOT_BRANCH"; test "$(git rev-parse HEAD)" = "$BOUND_ROOT_HEAD"
ROOT_STATUS=$(git -C "$PROJECT_ROOT" status --porcelain --untracked-files=all); test -z "$ROOT_STATUS"
if git show-ref --verify --quiet "$TARGET_REF"; then LOCAL_BASE_SHA=$(git rev-parse --verify "$TARGET_REF"); else REF_STATUS=$?; test "$REF_STATUS" -eq 1; LOCAL_BASE_SHA=; fi
test "$LOCAL_BASE_SHA" = "$BOUND_LOCAL_BASE"
test "$(git rev-parse --verify "$REMOTE_TRACKING_REF")" = "$EXPECTED"
test "$(git rev-parse --verify "$RESULT_SHA^{commit}")" = "$RESULT_SHA"
test -z "$BOUND_LOCAL_BASE" || git merge-base --is-ancestor "$BOUND_LOCAL_BASE" "$EXPECTED"
if REMOTE_SHA=$(remote_sha); then :; else false; fi; test "$REMOTE_SHA" = "$EXPECTED"; git merge-base --is-ancestor "$EXPECTED" "$RESULT_SHA"
if OCCUPANCY_SHA256=$(base_occupancy_digest); then :; else false; fi
test "$OCCUPANCY_SHA256" = "$BOUND_BASE_OCCUPANCY_SHA256"
if test "$BOUND_ROOT_BRANCH" = "$BASE_BRANCH"; then EXPECTED_PATH="$PROJECT_ROOT"; else EXPECTED_PATH=; fi
if EXPECTED_OCCUPANCY_SHA256=$(expected_occupancy_digest ${EXPECTED_PATH:+"$EXPECTED_PATH"}); then :; else false; fi
test "$OCCUPANCY_SHA256" = "$EXPECTED_OCCUPANCY_SHA256"
# Immediately recapture and revalidate root, status, ref, and exact occupancy before the first root mutation.
test "$(git -C "$PROJECT_ROOT" branch --show-current)" = "$BOUND_ROOT_BRANCH"
test "$(git -C "$PROJECT_ROOT" rev-parse HEAD)" = "$BOUND_ROOT_HEAD"
ROOT_STATUS=$(git -C "$PROJECT_ROOT" status --porcelain --untracked-files=all); test -z "$ROOT_STATUS"
if git -C "$PROJECT_ROOT" show-ref --verify --quiet "$TARGET_REF"; then LOCAL_BASE_SHA=$(git -C "$PROJECT_ROOT" rev-parse --verify "$TARGET_REF"); else REF_STATUS=$?; test "$REF_STATUS" -eq 1; LOCAL_BASE_SHA=; fi
test "$LOCAL_BASE_SHA" = "$BOUND_LOCAL_BASE"
if OCCUPANCY_SHA256=$(base_occupancy_digest); then :; else false; fi
test "$OCCUPANCY_SHA256" = "$BOUND_BASE_OCCUPANCY_SHA256"; test "$OCCUPANCY_SHA256" = "$EXPECTED_OCCUPANCY_SHA256"
if test "$BOUND_ROOT_BRANCH" = "$BASE_BRANCH"; then
  test "$BOUND_LOCAL_BASE" = "$BOUND_ROOT_HEAD"
elif test -n "$BOUND_LOCAL_BASE"; then
  git -C "$PROJECT_ROOT" switch --no-overwrite-ignore "$BASE_BRANCH"
else
  git -C "$PROJECT_ROOT" switch --no-overwrite-ignore --track -c "$BASE_BRANCH" "origin/$BASE_BRANCH"
fi
test "$(git -C "$PROJECT_ROOT" branch --show-current)" = "$BASE_BRANCH"
ROOT_STATUS=$(git -C "$PROJECT_ROOT" status --porcelain --untracked-files=all); test -z "$ROOT_STATUS"
test "$(git -C "$PROJECT_ROOT" rev-parse "$TARGET_REF")" = "${BOUND_LOCAL_BASE:-$EXPECTED}"
if REMOTE_SHA=$(remote_sha); then :; else false; fi; test "$REMOTE_SHA" = "$EXPECTED"
git -C "$PROJECT_ROOT" merge --ff-only --no-overwrite-ignore "$RESULT_SHA"
test "$(git -C "$PROJECT_ROOT" rev-parse HEAD)" = "$RESULT_SHA"
test "$(git -C "$PROJECT_ROOT" rev-parse "$TARGET_REF")" = "$RESULT_SHA"
ROOT_STATUS=$(git -C "$PROJECT_ROOT" status --porcelain --untracked-files=all); test -z "$ROOT_STATUS" # Never use: test "$(git -C "$PROJECT_ROOT" status --porcelain)" = ""
# Never use the maskable form: test "$(remote_sha)" = "$EXPECTED"
if REMOTE_SHA=$(remote_sha); then :; else false; fi; test "$REMOTE_SHA" = "$EXPECTED"; git merge-base --is-ancestor "$EXPECTED" "$RESULT_SHA"
# Publish the synchronized exact result once, then refresh and prove complete equality.
git push --force-with-lease="$TARGET_REF:$EXPECTED" origin "$RESULT_SHA:$TARGET_REF"
git -C "$PROJECT_ROOT" fetch --prune --tags origin
ROOT_STATUS=$(git -C "$PROJECT_ROOT" status --porcelain --untracked-files=all); test -z "$ROOT_STATUS" # Never use: test "$(git -C "$PROJECT_ROOT" status --porcelain)" = ""
test "$(git -C "$PROJECT_ROOT" branch --show-current)" = "$BASE_BRANCH"
test "$(git -C "$PROJECT_ROOT" rev-parse HEAD)" = "$RESULT_SHA"
test "$(git -C "$PROJECT_ROOT" rev-parse "$TARGET_REF")" = "$RESULT_SHA"
test "$(git -C "$PROJECT_ROOT" rev-parse "$REMOTE_TRACKING_REF")" = "$RESULT_SHA"
# Never use the maskable form: test "$(remote_sha)" = "$RESULT_SHA"
if REMOTE_SHA=$(remote_sha); then :; else false; fi; test "$REMOTE_SHA" = "$RESULT_SHA"
```
Ancestry plus the exact lease makes the one base push fast-forward-only; it does not authorize history rewriting.
Use the already established canonical `PROJECT_ROOT`, never the integration/current worktree. Do not use reset,
force-update, stash, clean, an unconstrained pull, a divergent merge, or any unrelated root mutation.
Handle failures by phase. On a pre-push failure, stop before publication, report any partial local synchronization,
and retain every safety net. On a push failure, report the partial local result and uncertain/unchanged remote state,
retain every safety net, and stop. On a post-push failure, report the partial verified state and published remote
result, retain every safety net, stop cleanup, and do not claim synchronization complete.
For `prepare-only`, run contracted cleanup only after the equality checks; never create/update tags or GitHub
releases. For `publish`, create/push the annotated tag and create the GitHub release only after those checks, then
clean up. Remove a temporary integration ref/worktree normally only after every contracted action succeeds.

## Cleanup Safety

Cleanup can run only for exact candidates named in the approved Release Contract.
The contract should delete/remove eligible feature code and artifact sidecar candidates by default; keep only with a named blocker or explicit user request.
Local feature branch/worktree cleanup requires the feature branch to be included in the target/base ref and the required target/base push to be complete.
Artifact sidecar cleanup requires final target/base push sync, exact contract listing, and no active package/integration/review/audit work needing the sidecar.
Keep a target/base worktree available until local branch deletion finishes.

For local cleanup:

```bash
git merge-base --is-ancestor <feature-branch> <base-branch-or-origin/base>
git worktree list --porcelain
git status --short  # in each candidate worktree
git worktree remove <exact-worktree-path>
git branch -d <feature-branch>
git worktree remove <exact-temporary-target-worktree>
git update-ref --no-deref -d refs/heads/integrate/release-<name> <verified-result-sha>
```

Stop on dirty worktrees, checked-out branches without removable worktrees, failed ancestry, or branch deletion refusal. Do not force-remove by default.
Never delete unrelated branches/worktrees or sweep by namespace.

For contracted artifact sidecar cleanup, run only the contract-listed subset:

```bash
git status --short  # in .worktrees/<feature>/artifacts before local removal
git worktree remove .worktrees/<feature>/artifacts
git branch -D artifacts/<feature>
git push origin --delete artifacts/<feature>
```

`artifacts/<feature>` is an orphan branch, so local `-D` is allowed only when that exact sidecar ref
was listed in the approved Release Contract after final target/base push. Remote sidecar deletion is not
ancestry-based; prove fresh remote state and exact contract listing instead. Never merge `artifacts/<feature>` into the base branch.

Remote feature deletion is the default, but only for the exact contracted `origin/<feature-branch>` ref.
After base push and fresh fetch, prove inclusion before deleting:

```bash
git merge-base --is-ancestor origin/<feature-branch> origin/<base-branch>
git push origin --delete <feature-branch>
```

If remote feature deletion verification fails, keep/report it. If sidecar deletion fails, keep/report the blocker.
