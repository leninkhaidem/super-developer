# PR Review Workflow

PR mode owns setup, preview, posting, approval, merge, synchronization, and cleanup. Code remains review-only:
no fixes, Fix Implementer, or Fix Verification Review. Require authenticated `gh`; use only `gh`/`gh api` for GitHub.
Run command blocks with `set -euo pipefail`; any failed proof stops subsequent actions.

## Setup and Reviewed State

1. Run `gh auth status`, then `gh pr view <PR_IDENTIFIER> --json
   url,number,title,body,author,baseRefName,headRefName,mergeable,state,headRefOid,baseRefOid`.
   Bind canonical PR repository identity from its URL: `HOST`, `REPO=owner/name`, `PR_REPO=HOST/owner/name`,
   numeric `PR_NUMBER`, and `PR_TITLE=title`. Use `--repo "$PR_REPO"` for every subsequent PR command and
   `gh api --hostname "$HOST" "/repos/$REPO/..."` for API calls; never rely on current-directory defaults.
2. Invoke **worktree** to resolve canonical `PROJECT_ROOT`/`COMMON_GIT_DIR`. Resolve exactly one configured fetch
   remote `REMOTE` whose effective URL identifies that same host/repository (account for URL rewrites/SSH aliases).
   Missing, ambiguous, multiple-URL, wrong-repository, or unprovable mapping stops; never add/change remotes.
3. Bind `REVIEWED_HEAD=headRefOid`, `REVIEWED_BASE=baseRefOid`, `BASE=baseRefName`, both ref names, mergeability,
   and `BASE_REF=refs/heads/$BASE`, `TRACKING_REF=refs/remotes/$REMOTE/$BASE`; validate full ref names.
   Stop for MERGED/CLOSED, CONFLICTING, or UNKNOWN after one retry. Capture
   `gh pr diff "$PR_NUMBER" --repo "$PR_REPO"`, its checksum, and file list/status.
4. Set `REVIEW_WT="$PROJECT_ROOT/.worktrees/pr-review/$PR_NUMBER"`. Require ignored `.worktrees/`, safe canonical
   parents with no symlink traversal, and absent destination: both `test ! -e "$REVIEW_WT"` and
   `test ! -L "$REVIEW_WT"`. Inspect common-repository `git worktree list --porcelain -z` with a NUL-aware parser;
   any registered destination, including prunable/missing entries, is a collision. Preserve it and stop, never remove.
5. Fetch/create only after those checks; recapture destination absence immediately before creation:

```bash
git -C "$PROJECT_ROOT" -c core.hooksPath=/dev/null -c submodule.recurse=false \
  fetch --no-tags --no-recurse-submodules --refmap= \
  "$REMOTE" "pull/$PR_NUMBER/head"
PR_SHA=$(git -C "$PROJECT_ROOT" rev-parse FETCH_HEAD)
test "$PR_SHA" = "$REVIEWED_HEAD"
git -C "$PROJECT_ROOT" -c core.hooksPath=/dev/null -c submodule.recurse=false \
  worktree add --detach "$REVIEW_WT" "$PR_SHA"
```

Capture successful creation ownership in existing reviewed-state metadata: canonical path/common repository,
HEAD/detached state, index, tracked/untracked/ignored state and content checksums. No ownership on collision or
uncertain setup. Revalidate PR head/base/diff after setup, then return to the main skill for reviewer dispatch.
Never switch root or reuse an existing checkout.

## Preview and Action Keywords

Present a body-only review preview; no GitHub writes. Header: `PR Review — #<number> <head> → <base>`.
Use explicit `Path:` locations, no metadata/footer/internal coverage or tracking rows. Verdict is `APPROVE`
without confirmed blocking findings, otherwise `REQUEST_CHANGES`.
Outside the postable body, show merge's synchronization target: repository/remote, exact base ref, canonical root,
and existing target checkout or unchecked-out/absent ref. `merge` includes safe local synchronization, not deletion.
Keep local paths and synchronization metadata out of the GitHub review body.

Full stop for one explicit keyword:

| Keyword | Action |
|---|---|
| `request-changes` | Post request-changes review. |
| `approve` | Post approval only; refuse with confirmed blockers. |
| `merge` | Same-head approved clean PR: merge, then synchronize the displayed base. |
| `edit` | Edit report body, then select action again. |
| `abort` | No GitHub action; owned cleanup only. |

Ambiguity needs clarification. Silence/blanket approval never means merge; `approve` never implies merge.

## Revalidation and Posting

Immediately before posting/merging, repeat bound-repository PR metadata and diff reads. Require OPEN, identical
head/base ref names and SHAs, repository identity, mergeability/context, and diff checksum. Recheck remote mapping
and synchronization target before merge. Retargeting, stale/broadened state, or uncertainty requires review rerun.

For explicit `request-changes` or blocker-free `approve`, post exactly one body-only review:

```bash
gh api --hostname "$HOST" --method POST "/repos/$REPO/pulls/$PR_NUMBER/reviews" \
  --field event="$EVENT" --field body="$REVIEW_BODY"
```

Set `EVENT=REQUEST_CHANGES` or `APPROVE`; append `— Changes Requested` or `— Approved ✅` to the header,
respectively, with matching verdict. Approval does not merge/delete. Refuse blocker-bearing approval and offer
`request-changes` or `abort`.

## Merge Action

Require explicit `merge`, clean review, and fresh revalidation. Read `reviewDecision,latestReviews,headRefOid`
through bound `gh pr view` and all approval records through the bound reviews API (paginate).
Require an approving review for exact `REVIEWED_HEAD`, not dismissed, stale, superseded by later change-request,
or another commit; ambiguous/absent approval stops. Check the bound repository API's `delete_branch_on_merge`;
if server auto-deletion would remove the source without separate deletion authority, stop, never change settings.

```bash
gh pr merge "$PR_NUMBER" --repo "$PR_REPO" --squash --match-head-commit "$REVIEWED_HEAD" \
  --subject "$PR_TITLE (#$PR_NUMBER)"
gh pr view "$PR_NUMBER" --repo "$PR_REPO" --json state,mergeCommit,headRefOid,baseRefName
```

Squash only; no automatic rebase, `--delete-branch`, or repository-setting changes. Preserve local/remote source
branches; deletion requires separate explicit authority. The expected-head guard closes the head race, not every
base/queue race. A successful command is not proof: require actual `MERGED`, nonempty `mergeCommit.oid` as
`MERGE_SHA`, and matching head/base bindings. Queued, OPEN, unknown, or failed verification means no completed-merge
sync/cleanup. Inspect uncertain outcomes before retrying; never blindly merge again.

## Safe Local Base Synchronization

This is part of the displayed merge action, not another prompt. Never switch unrelated HEAD, reset, stash, clean,
force, create commits, or use an unrelated feature tip. A root exception applies only to the checkout already on
this exact bound base, after verified remote merge; it grants no development/delivery authority.

1. Revalidate repository/remote/base identity. Reject symbolic/ambiguous tracking refs. Fetch only the exact base:

```bash
git -C "$PROJECT_ROOT" -c core.hooksPath=/dev/null -c submodule.recurse=false \
  fetch --no-tags --no-recurse-submodules --refmap= "$REMOTE" "$BASE_REF:$TRACKING_REF"
SNAPSHOT=$(git -C "$PROJECT_ROOT" rev-parse --verify "$TRACKING_REF^{commit}")
git -C "$PROJECT_ROOT" merge-base --is-ancestor "$MERGE_SHA" "$SNAPSHOT"
```

2. Identify the caller's checkout and exact target ref; do not freeze unrelated branches or worktrees. Inventory
   `git --git-dir="$COMMON_GIT_DIR" worktree list --porcelain -z` NUL-safely; match exact
   `branch $BASE_REF`, not display names. Resolve the exact local ref as direct/absent and capture `OLD` if present.
   Symbolic/ambiguous refs, multiple occupancy, locked/prunable/inaccessible target, active operations, or uncertain
   ownership/concurrent writers stop. Check per-worktree Git paths for locks, MERGE_HEAD, CHERRY_PICK_HEAD,
   REVERT_HEAD, rebase-merge/rebase-apply, sequencer, and bisect state; missing safety facts are not permission.
   For apparently unoccupied refs, rule out detached rebase/bisect ownership of this base in every worktree;
   unreadable or uncertain ownership stops rather than bypassing its index/files.
3. If present, require `git -C "$PROJECT_ROOT" merge-base --is-ancestor "$OLD" "$SNAPSHOT"`.
   Local-ahead/diverged histories stop. Recapture ref kind/SHA and occupancy immediately before any update;
   drift or inability to establish a quiescent target stops. Choose exactly one case:

**Already checked out:** `TARGET_WT` is its canonical, approved code-root path (primary or linked), already on
`BASE_REF` at `OLD`. Require clean index/tracked files using `git diff --cached --quiet` and `git diff --quiet`,
including submodule dirt (`--ignore-submodules=none`), with both commands run in `TARGET_WT`.
Check incoming paths against NUL-safe untracked/ignored path inventories, including parent/child and type collisions.
Coalesce unrelated directories; do not traverse/hash `.pi`, other worktrees, or caches just to prove them untouched.
Harmless unrelated files are allowed; collisions stop. Git's refusal and `--no-overwrite-ignore` remain mandatory.
No automatic hooks/submodule updates:

```bash
test "$(git -C "$TARGET_WT" symbolic-ref -q HEAD)" = "$BASE_REF"
test "$(git -C "$TARGET_WT" rev-parse HEAD)" = "$OLD"
git -C "$TARGET_WT" -c core.hooksPath=/dev/null -c submodule.recurse=false \
  merge --ff-only --no-autostash --no-overwrite-ignore "$SNAPSHOT"
```

**Present, not checked out:** after fresh no-occupancy/direct-ref/`OLD` checks and ancestry proof:

```bash
git -C "$PROJECT_ROOT" -c core.hooksPath=/dev/null -c submodule.recurse=false \
  update-ref --no-deref "$BASE_REF" "$SNAPSHOT" "$OLD"
```

**Absent, not checked out:** prove true absence (not lookup failure/symbolic ref), recapture no occupancy, then
create-if-absent without changing HEAD/worktree or any existing tracking configuration:

```bash
printf 'option no-deref\ncreate %s %s\n' "$BASE_REF" "$SNAPSHOT" |
  git -C "$PROJECT_ROOT" -c core.hooksPath=/dev/null -c submodule.recurse=false update-ref --stdin
```

Never use `update-ref` on an occupied branch; equal tips still require safety/completion checks.

4. Require local direct base and tracking ref both equal `SNAPSHOT` and merge ancestry. For a target checkout,
   verify HEAD/index/tracked files match the snapshot. Limit writes to that target; unrelated concurrent work is not
   a synchronization failure or permission to alter it. Run
   `git -C "$PROJECT_ROOT" ls-remote --exit-code --heads "$REMOTE" "$BASE_REF"`; require exactly that ref
   with SHA `SNAPSHOT`. Only then report synchronized at that observation. Remote advance/failure is not success.

Any failure after confirming MERGED (even mismatched merge bindings): report
**PR merged; local synchronization blocked**, actual local/remote observations,
partial movement, and retained safety nets. Do not roll back or perform completed-action cleanup. Resume only
synchronization from the bound merged-PR context: require still MERGED with the same repository, head, base name,
and `MERGE_SHA`, then repeat sync from its fresh fetch. This resume uses no OPEN/setup gate and never merges again.

## Cleanup and Blanket Mode

On abort or completed posting/merge-and-sync, remove only this invocation's successfully created detached
`REVIEW_WT`. Invoke **worktree** for cleanup safety. Recapture canonical path/common repository, detached HEAD,
index and complete tracked/untracked/ignored state; require exact captured matches, clean state, and no locks,
active use, or ownership uncertainty. Run only normal removal:

```bash
git -C "$PROJECT_ROOT" -c core.hooksPath=/dev/null -c submodule.recurse=false worktree remove "$REVIEW_WT"
```

Failure preserves it; never force or clean. No cleanup on setup collision; never delete source branches here.

Blanket mode may cover preview/posting only with explicit GitHub authority and passing gates; never auto-merge,
create a PR fix path, or bypass safety/privacy/security sniff or Skeptic verification.
