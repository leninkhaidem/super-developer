# PR Review Workflow

Instructions specific to reviewing a GitHub Pull Request.

**Requirement:** [GitHub CLI (`gh`)](https://cli.github.com/) must be installed and authenticated.
All GitHub interactions go through `gh` or `gh api` — no direct REST calls, no scraping.

---

## Phase 1 — Setup & Preflight

Run in order. **Halt and report to the user if any step fails.**

```bash
# 1. Verify GitHub CLI is authenticated
gh auth status

# 2. Fetch PR metadata
gh pr view <PR_IDENTIFIER> --json number,title,body,author,baseRefName,headRefName,mergeable,state

# 3. Check mergeability
# CONFLICTING → halt, report merge conflict to user
# UNKNOWN → wait and retry once, then halt if still unresolved

# 4. Fetch the full diff
gh pr diff <PR_IDENTIFIER>

# 5. Save current branch, then checkout the PR branch locally
ORIGINAL_BRANCH=$(git branch --show-current)
gh pr checkout <PR_IDENTIFIER>
```

> **Branch Restore:** After the review is complete (Phase 5 actions finished or aborted),
> restore the original branch: `git checkout $ORIGINAL_BRANCH`

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
- **HEADER:** `PR Review — #<number> \`<head branch>\` → \`<base branch>\``
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
| `approve` | Execute approval + merge (Workflow B) — **blocked if 🔴 BLOCKERS or 🟠 CRITICALS exist; see Workflow A** |
| `request-changes` | Post request-changes review (Workflow A below) |
| `edit` | Accept user edits to the report, then return to start of Phase 5 |
| `abort` | No GitHub action. Close session cleanly. |

> Any response other than these four → clarification prompt.
> **Never interpret ambiguity, silence, or partial confirmation as approval.**

---

### Workflow A — `request-changes`

Triggered when user responds `request-changes`, **OR when 🔴 BLOCKERS or 🟠 CRITICALS are
present regardless of user response.**

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

> **Override Rule:** If 🔴 BLOCKERS or 🟠 CRITICALS are present, the agent **must** post
> `REQUEST_CHANGES` — even if the user responds `approve`. Inform the user:
> *"Blockers or critical issues were detected. Posting as Request Changes to protect the
> branch. Resolve the issues and re-run the review to re-evaluate."*

---

### Workflow B — `approve`

Triggered when user responds `approve` **AND** no 🔴 BLOCKERS or 🟠 CRITICALS exist.

```bash
# 1. Post approval review
gh pr review <PR_IDENTIFIER> \
  --approve \
  --body "## PR Approved ✅

Multi-agent review completed. No blockers or critical issues found.

### 🟡 Suggestions _(non-blocking)_
<list suggestions if any, or state 'None'>

---
_Review generated via multi-agent analysis. Findings independently verified by adversarial
Skeptic Agent before reporting._"

# 2. Squash & Merge
gh pr merge <PR_IDENTIFIER> \
  --squash \
  --delete-branch \
  --subject "<PR title> (#<PR number>)"

# 3. Confirm merge success
gh pr view <PR_IDENTIFIER> --json state,mergeCommit
```

Report: `Merged successfully. Merge commit: <SHA>. Branch deleted.`

```bash
# 4. Restore original branch
git checkout $ORIGINAL_BRANCH
```

**Why Squash & Merge is hardcoded:** One PR = one commit on `main`. Clean, readable history.
Easy single-commit revert if needed. Granular commit history preserved within the PR on GitHub.
Rebase is never automated — it is a deliberate, manual operation only.
