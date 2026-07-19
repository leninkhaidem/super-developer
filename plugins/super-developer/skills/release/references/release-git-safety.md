# Release Git Safety

Owns release-specific remote freshness, exact-state resume, merge worktrees, publish checks, and the distinct safety
rules for ordinary feature cleanup and portable-evidence retention/cleanup.

## Remote Freshness and Evidence Identity

Before approval when pushing, publishing, or deleting an ordinary remote feature branch:

```bash
git fetch --prune --tags origin
git ls-remote --heads --tags origin
```

Use remote-tracking refs only after refresh. Stop if the push endpoint or state cannot be verified. Re-fetch
immediately before remote feature deletion; never infer safety from stale `origin/*`.

For planned-feature evidence, resolve one exact push endpoint and query each full ref directly:

```bash
git ls-remote --heads -- "$EVIDENCE_ENDPOINT" refs/heads/artifacts/<feature>
git ls-remote --heads -- "$EVIDENCE_ENDPOINT" \
  refs/heads/checkpoints/<feature>/<slot>/g<generation>  # repeat for each exact required ref
```

Match the final sidecar SHA and every final Lifecycle State/`F`/`V`-required checkpoint ref/SHA. Fetch only exact
required refs to verify that final `V` and all named objects resolve. Missing, symbolic-only local, unexpected,
changed, duplicate-endpoint, or mismatched state stops. Reading evidence grants no deletion authority.

For `publish`, also verify `gh auth status`, repository identity, and exact existing/absent release state. Stop if
credentials, repository, tag target, draft/prerelease state, or release identity is ambiguous.

## Resume Matrix

Verify exact identity before resuming any existing step:

- prepare commit: merge contents, `Unreleased`, docs, checks, pushed-base state, and ordinary cleanup match;
- publish commit: version files, changelog/docs, notes, and checks match intended `vX.Y.Z`;
- local/remote annotated tag: peeled target equals the intended publish commit;
- GitHub release: repository, tag/target, draft/prerelease state, and notes match;
- pushed base: local base, `origin/<base>`, and intended commit are equal;
- planned evidence: final `V`, sidecar ref/SHA, required code refs/SHAs, and retention state match the contract;
- any separate evidence decision: final sync/publish snapshot and preservation/deletion results match exactly.

Stop on mismatch. Never move tags, overwrite releases, reset/force-push base, or infer permission from an earlier
Sidecar Portability Authorization, Implementation authorization, release action, or cleanup.

## Merge Worktree

Never switch the user-owned root worktree. Use an existing base worktree or create the exact temporary target-merge
worktree named in the contract:

```bash
git worktree add .worktrees/<feature-or-release>/target-merge <base-branch>
cd .worktrees/<feature-or-release>/target-merge
git merge --no-ff <feature-branch> -m "<contracted merge message>"
```

If already merged, prove `git merge-base --is-ancestor <feature> <base>`. Resolve conflicts only within contracted
scope; stop when resolution needs product/design or other uncontracted changes.

## Base Push and Publish Checks

Before base push, verify the contracted base worktree/ref, clean state, intended commit, final diff, changelog/docs,
publish-only version/notes, tag/release absence or resume match, and planned evidence inventory. `prepare-only` must
have no version/tag/release action.

After base push, fetch and require all three SHAs to match:

```bash
git fetch --prune --tags origin
git rev-parse <base-branch>
git rev-parse origin/<base-branch>
git rev-parse <intended-prepare-or-publish-commit>
```

Stop on mismatch without repair by root switch, reset, or force. `prepare-only` may then run contracted ordinary
cleanup. `publish` may create/push the annotated tag and GitHub release only after sync, must verify both exactly,
and may then run ordinary cleanup. No portable-evidence decision is eligible before these applicable final checks.
Do not prompt for that decision unless evidence cleanup was explicitly requested; otherwise retain and report refs.

## Ordinary Feature and Local Code Cleanup

Initial Release Contract approval may cover only exact ordinary candidates: local code worktrees, local feature
branch, temporary target worktree, and remote feature branch. It never covers sidecar/checkpoint evidence.

For local cleanup, prove inclusion, enumerate worktrees, and inspect each exact candidate:

```bash
git merge-base --is-ancestor <feature-branch> <base-branch-or-origin/base>
git worktree list --porcelain
git status --short  # in each candidate worktree
git worktree remove <exact-clean-code-worktree>
git branch -d <feature-branch>
```

Stop on dirty/in-use worktrees, failed ancestry, or deletion refusal; do not force-remove or sweep. Keep a base
worktree until local branch deletion completes.

For an exact contracted remote feature ref, refresh, match its expected SHA, prove remote inclusion, delete only it,
and verify absence:

```bash
git fetch --prune origin
git merge-base --is-ancestor origin/<feature-branch> origin/<base-branch>
git push origin --delete <feature-branch>
git ls-remote --exit-code --heads origin refs/heads/<feature-branch>  # must report absent
```

Any mismatch/failure keeps the branch and stops remaining cleanup.

## Portable Evidence Retention/Cleanup Safety

Default and recommended disposition is to retain the remote sidecar and every required checkpoint ref through and
after release. Before any local or remote evidence cleanup, resolve final `V` from the sidecar and verify every
Lifecycle/`F`/`V`-required object at its exact retained ref/SHA. The initial Release Contract cannot override this.

Run evidence cleanup only from an approved separate post-sync decision. It must name every exact endpoint, full
remote ref, expected SHA, equivalent durable preservation location, local evidence worktree/direct-ref action, and
pre/post verification. Verify preservation first. Deleting the only resolvable final `V` or required object is
forbidden. Remove a local evidence worktree/ref only after portable preservation is verified and only at its exact
clean path/ref/expected SHA.

Immediately before each remote delete, query the exact endpoint/ref and require the expected SHA; delete that one
full ref without rewrite, then independently query absence and re-resolve `V` plus every preserved object. Never use
a wildcard, namespace sweep, target/tag/release action, implicit candidate, or force rewrite. A changed remote,
rejected delete, failed absence check, or preservation mismatch stops all remaining cleanup, retains safety refs,
and reports completed effects and blockers.
