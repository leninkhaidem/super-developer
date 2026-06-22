# Release Git Safety

Owns release-specific remote freshness, resume validation, merge worktree, tag/release checks, and cleanup safety.

## Remote Freshness

Before contract approval when pushing, checking remote tags, publishing, or deleting remote branches:

```bash
git fetch --prune --tags origin
git ls-remote --heads --tags origin
```

Stop if remote state cannot be refreshed or verified for a push/delete/publish contract. Re-fetch before remote feature-branch deletion.
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

Stop on any mismatch. Do not move tags, overwrite releases, force-push, or force-delete unless a new explicit contract names that destructive action.

## Merge Worktree

Never switch the user-owned root worktree. Merge the feature branch into the base branch from a worktree already on the base ref.
If none exists, create an exact temporary target-merge worktree named in the contract, for example:

```bash
git worktree add .worktrees/<feature-or-release>/target-merge <base-branch>
cd .worktrees/<feature-or-release>/target-merge
git merge --no-ff <feature-branch> -m "<contracted merge message>"
```

Use a prepare-style message for `prepare-only` and `release: vX.Y.Z` only for publish prep unless repo convention differs.
If the feature is already merged, verify ancestry instead of merging:

```bash
git merge-base --is-ancestor <feature-branch> <base-branch>
```

Resolve conflicts only within the contracted merge worktree. Stop if the conflict requires product/design decisions or uncontracted code changes.

## Base Push and Publish Checks

Before pushing the base branch, verify:

- base worktree is clean and on the contracted base branch;
- intended prepare/publish commit is `HEAD` or otherwise exactly named in the contract;
- final diff, changelog, docs, and publish-only version files/release notes match the contract;
- `prepare-only` made no version bump, tag, or GitHub release change;
- local/remote tags and GitHub release are absent for a new publish, or existing state passes the resume matrix.

After any successful base push, refresh refs and verify local/remote base sync before tag/release creation or cleanup:

```bash
git fetch --prune --tags origin
git rev-parse <base-branch>
git rev-parse origin/<base-branch>
git rev-parse HEAD  # or the exact intended prepare/publish commit named in the contract
```

The local base ref, `origin/<base>`, and intended prepare/publish commit must match. Stop on mismatch and report completed side effects.
Do not force-reset, force-push, switch the user-owned root worktree, or silently repair the local branch to make verification pass.

For `prepare-only`, push the base branch, run post-push sync verification, then run contracted cleanup. Do not create or update tags or GitHub releases.
For `publish`, push base first, run post-push sync verification, then create/push the annotated tag and create the GitHub release.
If any push, sync verification, publish, or cleanup step fails, stop and report completed side effects. Do not continue cleanup automatically.

## Cleanup Safety

Cleanup can run only for exact candidates named in the approved Release Contract.
Local feature branch/worktree cleanup requires the feature branch to be included in the target/base ref and the required target/base push to be complete.
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

Remote feature branch deletion is allowed in `prepare-only` or `publish` only when the exact `origin/<feature-branch>` ref is named in the contract.
After base push and fresh fetch, prove inclusion before deleting:

```bash
git merge-base --is-ancestor origin/<feature-branch> origin/<base-branch>
git push origin --delete <feature-branch>
```

If remote deletion verification fails, keep the remote branch and report it as remaining manual follow-up.
