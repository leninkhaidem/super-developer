# Release Git Safety

Owns release-specific remote freshness, resume validation, merge worktree, tag/release, and cleanup safety.

## Remote Freshness

Before contract approval when publishing, pushing, checking remote tags, or offering remote branch deletion:

```bash
git fetch --prune --tags origin
git ls-remote --heads --tags origin
```

Stop if remote state cannot be refreshed or verified for a publish/delete contract. Re-fetch before remote feature-branch deletion.
Use remote-tracking refs only after refresh. Never infer deletion safety from stale `origin/*` refs.

For publishing, preflight GitHub state:

```bash
gh auth status
gh repo view --json nameWithOwner
gh release view vX.Y.Z --json tagName,targetCommitish,isDraft,isPrerelease,url  # ok to fail when absent
```

Stop if auth, repo identity, existing release state, or target commit is ambiguous.

## Resume Matrix

If any release step already exists, verify exact identity before resuming:

- Release commit exists: version files, changelog/docs, release notes, and checks match intended `vX.Y.Z`.
- Local tag exists: `git rev-parse vX.Y.Z^{}` equals the intended release commit.
- Remote tag exists: `git ls-remote --tags origin refs/tags/vX.Y.Z` target or peeled target equals the intended release commit.
- GitHub release exists: tag, target commitish/tag target, draft/prerelease state, and notes match the contract.
- Base branch already pushed: `origin/<base>` contains the intended release commit.

Stop on any mismatch. Do not move tags, overwrite releases, or force-push unless a new explicit contract names that destructive action.

## Merge Worktree

Never switch the user-owned root worktree. Merge the feature branch into the base branch from a worktree already on the base ref.
If none exists, create an exact temporary target-merge worktree named in the contract, for example:

```bash
git worktree add .worktrees/<feature-or-release>/target-merge <base-branch>
cd .worktrees/<feature-or-release>/target-merge
git merge --no-ff <feature-branch> -m "release: vX.Y.Z"
```

If the feature is already merged, verify ancestry instead of merging:

```bash
git merge-base --is-ancestor <feature-branch> <base-branch>
```

Resolve conflicts only within the contracted merge worktree. Stop if the conflict requires product/design decisions or uncontracted code changes.

## Publish Checks

Before pushing or tagging, verify:

- base worktree is clean and on the contracted base branch;
- release commit is HEAD or otherwise exactly named in the contract;
- final diff, changelog, version files, docs, and release notes match;
- local and remote tags are absent, or existing tags pass the resume matrix;
- GitHub release is absent, or existing release passes the resume matrix.

For `publish`, push base first, then create/push the annotated tag, then create the GitHub release.
If any publish step fails, stop and report completed side effects. Do not clean up automatically.

## Cleanup Safety

Cleanup can run only for exact candidates named in the approved Release Contract.
Local feature branch/worktree cleanup requires the feature branch to be included in the target/base ref and the required target push to be complete.
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

Remote feature branch deletion is separate and allowed only in `publish` mode with `approve + delete remote branch` for the exact ref.
After base push and fresh fetch, prove inclusion before deleting:

```bash
git merge-base --is-ancestor origin/<feature-branch> origin/<base-branch>
git push origin --delete <feature-branch>
```

Never delete a remote feature branch in `prepare-only`. Default to keeping the remote branch.
