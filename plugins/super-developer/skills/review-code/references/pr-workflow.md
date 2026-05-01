# PR Review Workflow

Instructions specific to reviewing a GitHub Pull Request.

**Requirement:** [GitHub CLI (`gh`)](https://cli.github.com/) must be installed and authenticated.
All GitHub interactions go through `gh` or `gh api` — no direct REST calls, no scraping.

PR mode is review-only for code changes. It can post review comments, approve, request changes, or
merge when explicitly gated, but it does not offer or perform code-fix actions and does not invoke
delegated local Fix Verification Review.

---

## Phase 1 — Setup & Preflight

Run in order. **Halt and report to the user if any step fails.**

```bash
# 1. Verify GitHub CLI is authenticated
gh auth status

# 2. Fetch PR metadata
gh pr view <PR_IDENTIFIER> --json number,title,body,author,baseRefName,headRefName,mergeable,state,headRefOid,baseRefOid

# 3. Check mergeability
# CONFLICTING → halt, report merge conflict to user
# UNKNOWN → wait and retry once, then halt if still unresolved

# 4. Fetch the full diff
gh pr diff <PR_IDENTIFIER>

# 5. Create a detached worktree at the PR's HEAD (main working tree stays on its branch)
PR_NUMBER=<extracted from metadata>
git fetch origin pull/${PR_NUMBER}/head
PR_SHA=$(git rev-parse FETCH_HEAD)
git worktree remove .worktrees/pr-review/${PR_NUMBER} 2>/dev/null || true
git worktree add .worktrees/pr-review/${PR_NUMBER} $PR_SHA --detach
```

Capture reviewed-state metadata before returning to the shared review pipeline:

- PR number and repository
- PR head ref and immutable head SHA
- PR base ref and immutable base SHA
- Mergeability result and merge context observed during review
- Full reviewed diff checksum or exact saved diff
- Reviewed file list and file status

> **Worktree Cleanup:** After the review is complete (Phase 5 actions finished or aborted),
> remove the worktree: `git worktree remove .worktrees/pr-review/${PR_NUMBER}`
> The main working tree is never switched — no branch restore needed.

### Hard Stop Rules

- Authentication failure → halt. Do not proceed.
- PR state is `MERGED` or `CLOSED` → halt. Report to user.
- Branch has merge conflicts → halt. Report conflict details.

After setup, return to SKILL.md for the shared review pipeline (Steps 2-3).

_(Phases 2-3 are shared pipeline steps defined in SKILL.md — return there now.)_

---

## Phase 4 — Review Preview

Compile and **present the following to the user — do NOT post anything to GitHub yet.**

Use the canonical report template from SKILL.md with:

- **HEADER:** ``PR Review — #<number> `<head branch>` → `<base branch>` ``
- **METADATA:** _(none for PR mode)_

The report should read exactly as it would appear when posted as a PR comment.

**Verdict** (shown after the preview, not inside it):

- **APPROVE** — No 🔴 or 🟠 findings.
- **REQUEST CHANGES** — One or more 🔴 or 🟠 findings confirmed.

There is no third option. Every review is either clean or has actionable issues.

> **Full stop. Do not touch GitHub. Await explicit user response.**

---

## Phase 5 — Gated Actions

Only proceed when the user responds with one of these keywords:

| Keyword | Action |
|---|---|
| `approve` | Post approval review only (Workflow B) — **blocked if 🔴 BLOCKERS or 🟠 CRITICALS exist; see Workflow A** |
| `merge` | Merge an already-approved clean PR only (Workflow C) — requires explicit `merge` response and a fresh revalidation gate immediately before merge |
| `request-changes` | Post request-changes review (Workflow A below) |
| `edit` | Accept user edits to the report, then return to start of Phase 5 |
| `abort` | No GitHub action. Close session cleanly. |

`fix`, local code edits, delegated Fix Implementer, and delegated Fix Verification Review are not
available in PR mode. If the user asks to fix PR code, explain that PR mode is review-only and the
author must update the PR or the user must switch to an explicit local workflow.

> Any response other than these five → clarification prompt.
> **Never interpret ambiguity, silence, or partial confirmation as approval.**

### PR Reviewed-State Revalidation Gate

Before posting approval, posting request-changes, or merging, re-fetch and compare immutable state:

```bash
gh pr view <PR_IDENTIFIER> --json number,state,baseRefName,headRefName,mergeable,headRefOid,baseRefOid
```

The gate passes only when:

- PR state is still open.
- Current head SHA equals the reviewed head SHA.
- Current base ref and base SHA equal the reviewed base ref and base SHA.
- Mergeability and merge context have not changed in a way that invalidates the reviewed diff.
- The diff checksum or reviewed file list still matches the reviewed state.

If any value is stale, broadened, or ambiguous, do not post approval, request changes, or merge.
Report that the PR changed after review and must be reviewed again. Side-effect actions apply only
to the immutable reviewed state.

---

## Workflow A — `request-changes`

Triggered only when the user explicitly responds `request-changes`. Confirmed 🔴 BLOCKERS or 🟠
CRITICALS block approval, but they do not authorize posting to GitHub without that explicit response.

Run the PR Reviewed-State Revalidation Gate immediately before posting. If it fails, halt without
posting and report the stale state.

```bash
gh api \
  --method POST \
  /repos/{owner}/{repo}/pulls/{pull_number}/reviews \
  --field event="REQUEST_CHANGES" \
  --field body="<review body>"
```

**Review body:** Use the canonical report template from SKILL.md with:

- **HEADER:** `PR Review — Changes Requested`
- **METADATA:** _(none)_

> **Approval Block Rule:** If 🔴 BLOCKERS or 🟠 CRITICALS are present and the user responds
> `approve`, refuse approval and do not post to GitHub. Inform the user:
> *"Blockers or critical issues were detected, so approval is blocked. Respond with
> `request-changes` to post the review, or `abort` to take no GitHub action."*

---

## Workflow B — `approve`

Triggered when user responds `approve` **AND** no 🔴 BLOCKERS or 🟠 CRITICALS exist.

Run the PR Reviewed-State Revalidation Gate immediately before approval. If it fails, halt without
posting and report the stale state.

Approval is a standalone side effect. It posts the approval review only; it must not merge the PR,
delete the branch, or run any merge command.

```bash
gh pr review <PR_IDENTIFIER> \
  --approve \
  --body "## PR Approved ✅

Multi-agent review completed. No blockers or critical issues found.

### 🟡 Suggestions _(non-blocking)_
<list actionable deduplicated suggestions if any, or state 'None'>

---
_Review generated via bounded multi-agent analysis. All serious findings were independently
verified by the Skeptic Agent before reporting._"
```

Report: Approval posted. Merge was not performed; respond with `merge` to run the separate merge workflow.

---

## Workflow C — `merge`

Triggered only when the user explicitly responds `merge` after a clean review and approval. Merge is
separate from approval and is never implied by `approve`, including under blanket mode.

Before merging, re-run the PR Reviewed-State Revalidation Gate immediately. Revalidate PR head SHA,
base SHA, mergeability, merge context, and reviewed diff/file-list state against the immutable state
captured during review. If the gate fails, do not merge; report that the PR changed or became
ambiguous and must be reviewed again before merge.

Then verify the PR's actual approval state for the same reviewed head state. Use `gh pr view` and
`gh api` as appropriate to inspect review decision, latest reviews, review dismissal state, and the
reviewed commit SHA before any merge command:

```bash
# 1. Fetch current PR approval/review metadata
gh pr view <PR_IDENTIFIER> --json number,reviewDecision,latestReviews,headRefOid

# 2. If needed, inspect full review records including commit IDs and dismissed/stale state
gh api /repos/{owner}/{repo}/pulls/{pull_number}/reviews
```

The approval-state gate passes only when:

- At least one approving review exists for the exact current head SHA already validated against the
  reviewed head SHA.
- The approving review is not stale, dismissed, superseded by a later change-request review, or tied
  to a different commit SHA.
- The review decision and review records are consistent enough to prove approval for the reviewed
  head state.

If approval is absent, stale, dismissed, superseded, tied to another head SHA, or ambiguous, halt
without merging and report that the PR must be approved for the reviewed head state first.

Do not merge if 🔴 BLOCKERS or 🟠 CRITICALS exist, if the PR is not approved for the reviewed state,
or if mergeability is not clean for the reviewed state.

```bash
# 3. Squash & Merge
gh pr merge <PR_IDENTIFIER> \
  --squash \
  --delete-branch \
  --subject "<PR title> (#<PR number>)"

# 4. Confirm merge success
gh pr view <PR_IDENTIFIER> --json state,mergeCommit
```

Report: `Merged successfully. Merge commit: <SHA>. Branch deleted.`

```bash
# 5. Remove review worktree
git worktree remove .worktrees/pr-review/${PR_NUMBER}
```

**Why Squash & Merge is hardcoded:** One PR = one commit on `main`. Clean, readable history.
Easy single-commit revert if needed. Granular commit history preserved within the PR on GitHub.
Rebase is never automated — it is a deliberate, manual operation only.

---

## Blanket-mode override

When the user has authorized blanket mode (`proceed through all stages` or equivalent), the
side-effect gates above still apply. Blanket mode may proceed through preview and gated posting only
when the user's authorization explicitly covers GitHub side effects and the PR Reviewed-State
Revalidation Gate passes at each side-effect boundary.

Blanket authorization may cover posting a request-changes or approval review, but it never flows
directly from approval to merge. Blanket mode does not auto-merge, does not treat approval as merge
authorization, and still requires the user to give an explicit `merge` response/action before
Workflow C may run.

Blanket mode does not create a PR code-fix path, does not invoke delegated Fix Verification Review,
does not bypass the Code Reviewer's baseline security/privacy/safety sniff, and does not bypass
Skeptic verification for serious findings.
