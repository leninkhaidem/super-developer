# Local Code Review Workflow

Load this reference for local mode scope detection, setup, and report only. Load `local-actions.md` only after the user reaches the gated action phase.

**Requirement:** `git` installed, inside a Git repository. No GitHub dependency — works offline.

**User context:** If the user provides additional context (intent, constraints, known trade-offs, focus areas), pass it to all review agents. This reduces false positives significantly because agents can distinguish intentional decisions from oversights.

---

## Phase 0 — Determine Review Scope

Detect what to review, in priority order:

1. **Staged changes** (`git diff --cached --stat` non-empty) → review staged only.
2. **Unstaged changes** (`git diff --stat` non-empty) → review all uncommitted (staged + unstaged).
3. **No uncommitted changes** → diff current branch against upstream/default branch.

```bash
STAGED=$(git diff --cached --stat)
UNSTAGED=$(git diff --stat)

if [ -n "$STAGED" ]; then
  SCOPE="staged"
  DIFF_CMD="git diff --cached"
elif [ -n "$UNSTAGED" ]; then
  SCOPE="uncommitted"
  DIFF_CMD="git diff HEAD"
else
  DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null \
    | sed 's@^refs/remotes/origin/@@' || echo "main")
  SCOPE="branch"
  DIFF_CMD="git diff origin/${DEFAULT_BRANCH}...HEAD"
fi
```

Capture reviewed-state metadata before reviewing:

- Current branch name
- `HEAD` SHA
- Base ref and base SHA when reviewing a branch diff
- Scope (`staged`, `uncommitted`, or `branch`)
- Reviewed file list and file status
- Diff checksum or exact saved diff used for review
- Staged checksum when reviewing staged changes

Report scope before proceeding:

```
Review Scope: <staged | uncommitted | branch diff against origin/<branch>>
Files changed: <count>
Insertions: +<count>  Deletions: -<count>
```

> **Hard Stop:** If the diff is empty (no changes in any mode), report to the user and halt.

---

## Phase 1 — Setup & Preflight

Run in order. **Halt and report to the user if any step fails.**

```bash
# 1. Verify inside a Git repository
git rev-parse --is-inside-work-tree

# 2. Collect the full diff (using DIFF_CMD from Phase 0)
$DIFF_CMD

# 3. File list with change stats
$DIFF_CMD --stat

# 4. Current branch name
git branch --show-current

# 5. Recent commits for context
git log --oneline -10
```

### Hard Stop Rules

- Not inside a Git repository → halt. Report to user.
- Diff is empty → halt. Report "nothing to review."

After setup, return to `../SKILL.md` to load the shared review engine and finding contract.

---

## Phase 4 — Review Report

Present to the user.

Use `report-template.md` with:

- **HEADER:** `Local Code Review`
- **METADATA:** ``**Branch:** `<current branch>` | **Scope:** <staged | uncommitted | branch diff against origin/<branch>> | **Files:** <count> changed``
- **OPTIONAL_MODE_FOOTER:** _(none)_

**Verdict** (shown after the report, not inside it):

- **CLEAN** — No 🔴 or 🟠 findings.
- **ISSUES FOUND** — One or more 🔴 or 🟠 findings confirmed.

There is no third option. Every review is either clean or has actionable issues.

> **Full stop. Await explicit user response.**

When the user responds with a gated action keyword, load `local-actions.md`. Do not load local mutation runbooks during scope detection, setup, review, or report rendering.