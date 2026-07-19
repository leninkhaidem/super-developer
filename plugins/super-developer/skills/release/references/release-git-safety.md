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

For planned evidence, bind endpoints independently in exact clean owning roots. Never query a sidecar at a code
endpoint or a checkpoint at the artifact endpoint, even when the other endpoint advertises the same-named ref:

```bash
capture_one_push_endpoint() {
  local name="$1" authorized="$2" output; local -a endpoints
  output="$(git remote get-url --push --all "$name")" || return 1; mapfile -t endpoints <<<"$output"
  test "${#endpoints[@]}" -eq 1 && test -n "${endpoints[0]}" && test "${endpoints[0]}" = "$authorized"
  printf '%s' "${endpoints[0]}"
}
assert_endpoint_unchanged() { test "$(capture_one_push_endpoint "$1" "$2")" = "$2"; }
cd "$ARTIFACT_ROOT"; ARTIFACT_ENDPOINT="$(capture_one_push_endpoint origin "$AUTHORIZED_ARTIFACT_ENDPOINT")"
assert_endpoint_unchanged origin "$ARTIFACT_ENDPOINT"; git ls-remote --heads -- "$ARTIFACT_ENDPOINT" "$ARTIFACT_REF"
assert_endpoint_unchanged origin "$ARTIFACT_ENDPOINT"; git fetch --no-tags -- "$ARTIFACT_ENDPOINT" "$ARTIFACT_REF"
cd "$CODE_ROOT"; CODE_ENDPOINT="$(capture_one_push_endpoint origin "$AUTHORIZED_CODE_ENDPOINT")"  # per owning root
assert_endpoint_unchanged origin "$CODE_ENDPOINT"; git ls-remote --heads -- "$CODE_ENDPOINT" "$CODE_REF"
assert_endpoint_unchanged origin "$CODE_ENDPOINT"; git fetch --no-tags -- "$CODE_ENDPOINT" "$CODE_REF"
```

Require one exact advertised ref/SHA and `FETCH_HEAD` per query; reject local-only/unfetched/symbolic/mismatched
refs, then materialize clean roots/HEADs and exact direct refs without cross-endpoint evidence. Run:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-agentic-completion \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" --feature <feature>
```

The fresh validator establishes the exact PASS receipt graph supporting the completion claim; index-only `V` alone
proves nothing. Run before contract approval and again before the first release action.
Re-query, fetch, and repeat whenever roots, status, endpoint config, refs, objects, or relevant state could change.
A failure or missing predecessor graph blocks. Reading evidence grants no deletion authority.

For `publish`, also verify `gh auth status`, repository identity, and exact existing/absent release state. Stop if
credentials, repository, tag target, draft/prerelease state, or release identity is ambiguous.

## Resume Matrix

Verify exact identity before resuming any existing step:

- prepare commit: merge contents, `Unreleased`, docs, checks, pushed-base state, and ordinary cleanup match;
- publish commit: version files, changelog/docs, notes, and checks match intended `vX.Y.Z`;
- local/remote annotated tag: peeled target equals the intended publish commit;
- GitHub release: repository, tag/target, draft/prerelease state, and notes match;
- pushed base: local base, `origin/<base>`, and intended commit are equal;
- planned evidence: fresh completion validation plus index-only `V`, split endpoints, sidecar/ref SHAs, and
  retention match;
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

Before base push, verify the contracted worktree/ref, diff/docs/version/publish state, and planned evidence. Re-fetch
from each unchanged owning endpoint and repeat completion validation if any relevant state could have changed.
`prepare-only` must have no version/tag/release action.

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

Default is retain. Before evidence cleanup, resolve index-only `V` only from the artifact endpoint, every checkpoint
only from its owning code endpoint, and repeat successful completion validation over preserved exact state. The
initial Release Contract cannot override this.

Run evidence cleanup only from an approved separate post-sync decision. It must name every exact endpoint, full
remote ref, expected SHA, equivalent durable preservation location, local evidence worktree/direct-ref action, and
pre/post verification. Verify preservation first. Deleting the only resolvable final `V` or required object is
forbidden. Remove a local evidence worktree/ref only after portable preservation is verified and only at its exact
clean path/ref/expected SHA.

Immediately before each remote delete, assert its owning endpoint unchanged and require exact ref/SHA; delete only
that full ref, query absence at the same endpoint, then repeat endpoint-isolated resolution and completion
validation. Never use
a wildcard, namespace sweep, target/tag/release action, implicit candidate, or force rewrite. A changed remote,
rejected delete, failed absence check, or preservation mismatch stops all remaining cleanup, retains safety refs,
and reports completed effects and blockers.
