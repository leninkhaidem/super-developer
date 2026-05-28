# PR Review Workflow

Load this reference for PR mode setup and report preview only. Load `pr-actions.md` only after the user reaches the gated action phase.

**Requirement:** [GitHub CLI (`gh`)](https://cli.github.com/) must be installed and authenticated. All GitHub interactions go through `gh` or `gh api` — no direct REST calls, no scraping.

PR mode is review-only for code changes. It can post review comments, approve, request changes, or merge when explicitly gated by `pr-actions.md`, but it does not offer or perform code-fix actions and does not invoke delegated local Fix Verification Review.

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

# 5. Create a detached worktree at the PR's HEAD (root worktree stays on its current branch)
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

> **Worktree Cleanup:** After the review is complete (after `pr-actions.md` finishes or the user aborts), remove the worktree: `git worktree remove .worktrees/pr-review/${PR_NUMBER}`
> The root worktree is never switched — no branch restore needed.

### Hard Stop Rules

- Authentication failure → halt. Do not proceed.
- PR state is `MERGED` or `CLOSED` → halt. Report to user.
- Branch has merge conflicts → halt. Report conflict details.

After setup, return to SKILL.md for the shared review pipeline (Steps 2-3).

_(Phases 2-3 are shared pipeline steps defined in SKILL.md — return there now.)_

---

## Phase 4 — Review Preview

Compile and **present the following to the user — do NOT post anything to GitHub yet.**

Use `report-template.md` with:

- **HEADER:** ``PR Review — #<number> `<head branch>` → `<base branch>` ``
- **METADATA:** _(none for PR mode)_
- **OPTIONAL_VERDICT_LINE:** ``**Verdict:** <APPROVE | REQUEST_CHANGES>`` based on findings
- **Findings count line:** aggregate 🔴 | 🟠 | 🟡 counts

The report should read exactly as it would appear when posted as a single PR review body (no inline
diff comments). All finding locations are expressed via explicit `Path:` fields for AI-agent
parseability. Do not include internal `DISCOVERY_COVERAGE`, raw tags, or dedupe/tracking keys in the
PR body.

**Verdict** (shown after the preview, not inside it):

- **APPROVE** — No 🔴 or 🟠 findings.
- **REQUEST CHANGES** — One or more 🔴 or 🟠 findings confirmed.

There is no third option. Every review is either clean or has actionable issues.

> **Full stop. Do not touch GitHub. Await explicit user response.**

When the user responds with a gated action keyword, load `pr-actions.md`. Do not load PR side-effect runbooks during setup or preview.