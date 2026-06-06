# PR Review Workflow

PR mode owns GitHub PR setup, preview, posting, approval, merge, and cleanup gates. It is review-only for code changes: no local code fixes, no delegated Fix
Implementer, and no Fix Verification Review.

Requirement: GitHub CLI (`gh`) installed and authenticated. Use `gh`/`gh api` only; no direct REST calls or scraping.

## Setup and Reviewed State

Run in order; halt and report if any step fails:

```bash
gh auth status
gh pr view <PR_IDENTIFIER> --json number,title,body,author,baseRefName,headRefName,mergeable,state,headRefOid,baseRefOid
gh pr diff <PR_IDENTIFIER>
PR_NUMBER=<extracted number>
git fetch origin pull/${PR_NUMBER}/head
PR_SHA=$(git rev-parse FETCH_HEAD)
git worktree remove .worktrees/pr-review/${PR_NUMBER} 2>/dev/null || true
git worktree add .worktrees/pr-review/${PR_NUMBER} $PR_SHA --detach
```

Hard stops: authentication failure, PR state `MERGED`/`CLOSED`, mergeability `CONFLICTING`, or mergeability `UNKNOWN` after one retry.

Capture immutable reviewed-state metadata: PR number/repository, head ref/SHA, base ref/SHA, mergeability/context, reviewed diff checksum or saved diff, file
list/status, and detached review worktree path. Never switch the root worktree.

After setup, return to the main skill for reviewer dispatch.

## Preview Report

Present a body-only PR review preview. Do not touch GitHub yet.

Mode values for the main report template:

- Header: `PR Review — #<number> <head branch> → <base branch>`.
- Metadata: none.
- Verdict line: `**Verdict:** APPROVE` when no confirmed 🔴/🟠 findings; otherwise `**Verdict:** REQUEST_CHANGES`.
- Footer: none.

All finding locations use explicit `Path:` fields. Do not render internal coverage rows, raw tags, dedupe keys, or state metadata.

Preview verdicts:

- `APPROVE` — no confirmed 🔴/🟠 findings.
- `REQUEST_CHANGES` — one or more confirmed 🔴/🟠 findings.

Full stop after preview. Await one explicit action keyword.

## Action Keywords

| Keyword | Action |
|---|---|
| `request-changes` | Post request-changes review body. |
| `approve` | Post approval review only; blocked when confirmed 🔴/🟠 findings exist. |
| `merge` | Merge an already-approved clean PR; requires fresh revalidation and approval-state gate. |
| `edit` | Accept user edits to report body, then return to action selection. |
| `abort` | No GitHub action; cleanup only. |

Any other response requires clarification. Never interpret ambiguity, silence, or blanket approval as merge permission. `approve` never implies `merge`.

## PR State Revalidation Gate

Before posting or merging, rerun:

```bash
gh pr view <PR_IDENTIFIER> --json number,state,baseRefName,headRefName,mergeable,headRefOid,baseRefOid
```

Gate passes only when PR is open, current head/base SHAs equal reviewed head/base SHAs, mergeability/context still match, and diff checksum or reviewed file
list still matches. If stale, broadened, or ambiguous, halt without side effects and require review rerun.

## Posting Actions

`request-changes`: allowed only after explicit keyword. Revalidate first, then post one body-only review:

```bash
gh api --method POST "/repos/{owner}/{repo}/pulls/$PR_NUMBER/reviews" \
  --field event="REQUEST_CHANGES" \
  --field body="<review body>"
```

Header becomes `PR Review — #<number> <head branch> → <base branch> — Changes Requested`; verdict line is `REQUEST_CHANGES`.

`approve`: allowed only after explicit keyword and no confirmed 🔴/🟠 findings. Revalidate first, then post approval only:

```bash
gh api --method POST "/repos/{owner}/{repo}/pulls/$PR_NUMBER/reviews" \
  --field event="APPROVE" \
  --field body="<review body>"
```

Header becomes `PR Review — #<number> <head branch> → <base branch> — Approved ✅`; verdict line is `APPROVE`. Do not merge, delete branches, or run merge
commands.

If confirmed serious findings exist and the user says `approve`, refuse and offer `request-changes` or `abort`.

## Merge Action

`merge` is allowed only after a clean review and approval for the same reviewed head state. Revalidate PR state, then verify approval records:

```bash
gh pr view <PR_IDENTIFIER> --json number,reviewDecision,latestReviews,headRefOid
gh api "/repos/{owner}/{repo}/pulls/$PR_NUMBER/reviews"
```

Approval gate passes only when an approving review exists for the exact current/reviewed head SHA and is not stale, dismissed, superseded by later
change-request review, or tied to another commit. If absent or ambiguous, halt.

Then merge:

```bash
gh pr merge <PR_IDENTIFIER> --squash --delete-branch --subject "<PR title> (#<PR number>)"
gh pr view <PR_IDENTIFIER> --json state,mergeCommit
git worktree remove .worktrees/pr-review/${PR_NUMBER}
```

Squash merge is hardcoded; rebase is never automated.

## Cleanup and Blanket Mode

On `abort` or after a terminal action, remove only `.worktrees/pr-review/${PR_NUMBER}`. Do not delete branches except through explicit merge.

Blanket mode may cover preview and posting only when it explicitly authorizes GitHub side effects and state gates pass. It never auto-merges, never creates a PR
fix path, and never bypasses security/privacy/safety sniff or Skeptic verification.
