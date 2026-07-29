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

## Merge Worktree

Never switch or detach the user-owned root worktree. Refresh `origin`, bind the exact remote-base SHA, and require
any local base ref to equal or be an ancestor of it. Use a clean non-root checkout already on that exact base when
available. Otherwise create a named temporary integration branch/worktree from the remote-base SHA—not from the
locked local branch:

```bash
EXPECTED=$(git rev-parse origin/<base>)
LOCAL_BASE=$(git rev-parse refs/heads/<base> 2>/dev/null || :)
test -z "$LOCAL_BASE" || git merge-base --is-ancestor "$LOCAL_BASE" "$EXPECTED"
git worktree add --no-track -b integrate/release-<name> \
  .worktrees/release-<name>/target-merge "$EXPECTED"
cd .worktrees/release-<name>/target-merge
git merge --no-ff <feature-sha> -m "<contracted merge message>"
```

Use a prepare-style message for `prepare-only` and `release: vX.Y.Z` only for publish prep unless repository
convention differs. If the feature is already included, verify immutable-SHA ancestry instead. Resolve conflicts
only in the integration worktree and stop when they require uncontracted decisions.

## Base Push and Publish Checks

Before pushing, require the final diff/files, checks, changelog, publish state, and cleanup candidates to match the
contract; `prepare-only` still permits no version/tag/release change. Then bind the clean integration `RESULT_SHA`,
re-read the remote target, prove a fast-forward, and use an exact lease plus explicit result/target refspec:

```bash
RESULT_SHA=$(git rev-parse HEAD)
EXPECTED=<contracted-remote-base-sha>
TARGET_REF=refs/heads/<base>
test -z "$(git status --porcelain)"
REMOTE_LINE=$(git ls-remote --heads origin "$TARGET_REF"); test -n "$REMOTE_LINE"
test "${REMOTE_LINE%%$'\t'*}" = "$EXPECTED"
git merge-base --is-ancestor "$EXPECTED" "$RESULT_SHA"
git push --force-with-lease="$TARGET_REF:$EXPECTED" origin "$RESULT_SHA:$TARGET_REF"
git fetch --prune --tags origin
test "$(git rev-parse origin/<base>)" = "$RESULT_SHA"
test "$(git ls-remote --heads origin "$TARGET_REF" | cut -f1)" = "$RESULT_SHA"
```

Ancestry makes this lease push fast-forward only; it does not authorize history rewriting. For an existing base
checkout, require its local base ref to equal `RESULT_SHA`. For temporary integration, keep the root/local base
unchanged and prove its bound SHA is an ancestor of `RESULT_SHA`; report the intentional local lag rather than
asking for detachment or forcing local/remote equality.

For `prepare-only`, verify the target then run contracted cleanup; never create/update tags or GitHub releases.
For `publish`, verify the target, create/push the annotated tag, create the GitHub release, then clean up. Retain a
temporary integration ref/worktree on any failure and remove it normally only after every contracted action and
other cleanup succeeds.

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

Remote feature branch deletion is the default for feature releases, but allowed only when the exact
`origin/<feature-branch>` ref is named in the contract.
After base push and fresh fetch, prove inclusion before deleting:

```bash
git merge-base --is-ancestor origin/<feature-branch> origin/<base-branch>
git push origin --delete <feature-branch>
```

If remote feature deletion verification fails, keep the remote branch and report it as remaining manual follow-up.
If approved sidecar deletion fails, keep the remaining sidecar ref/worktree and report the blocker.
