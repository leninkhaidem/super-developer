# Local Code Review Workflow

Instructions specific to reviewing local code changes before committing or pushing.

**Requirement:** `git` installed, inside a Git repository. No GitHub dependency — works offline.

**User context:** If the user provides additional context (intent, constraints, known trade-offs,
focus areas), pass it to all specialist agents. This reduces false positives significantly
because agents can distinguish intentional decisions from oversights.

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

After setup, return to SKILL.md for the shared review pipeline (Steps 2-3).

_(Phases 2-3 are shared pipeline steps defined in SKILL.md — return there now.)_

---

## Phase 4 — Review Report

Present to the user.

Use the canonical report template from SKILL.md with:
- **HEADER:** `Local Code Review`
- **METADATA:** `**Branch:** \`<current branch>\` | **Scope:** <staged | uncommitted | branch diff against origin/<branch>>` + `**Files:** <count> changed`

**Verdict** (shown after the report, not inside it):
- **CLEAN** — No 🔴 or 🟠 findings.
- **ISSUES FOUND** — One or more 🔴 or 🟠 findings confirmed.

There is no third option. Every review is either clean or has actionable issues.

> **Full stop. Await explicit user response.**

---

## Phase 5 — Gated Actions

Only proceed when the user responds with one of these keywords:

| Keyword | Action |
|---|---|
| `fix` | Auto-fix confirmed 🔴 and 🟠 findings (Workflow A below) |
| `commit` | Stage and commit as-is — only if no 🔴 BLOCKERS (Workflow B below) |
| `details <N>` | Expand finding N with full context, code snippet, and recommended fix. Return to Phase 5. |
| `abort` | No action. Close session cleanly. |

> Any response other than these keywords → clarification prompt.
> **Never interpret ambiguity, silence, or partial confirmation as approval.**

---

### Workflow A — `fix`

Triggered when user responds `fix`.

For each confirmed 🔴 BLOCKER and 🟠 CRITICAL finding, in order of severity:

1. **Show the proposed fix** — display the exact code change as a diff preview.
2. **Wait for user confirmation** — the user must respond `yes` or `skip` for each fix.
3. **Apply confirmed fixes** — make the edit only after explicit approval.
4. **Report results** — show which fixes were applied and which were skipped.

> **Safety Rule:** Never apply a fix without showing it to the user first. Each fix
> requires individual approval.

---

### Workflow B — `commit`

Triggered when user responds `commit` **AND** no 🔴 BLOCKERS exist.

```bash
# Only stage changes if scope was uncommitted or branch diff.
# If SCOPE="staged", the staged area is already set — do NOT modify it.
if [ "$SCOPE" != "staged" ]; then
  # Stage ONLY the files that were included in the reviewed diff — never git add -A.
  $DIFF_CMD --name-only | xargs git add --
fi

# Commit with a summary
git commit -m "<concise summary of changes>"
```

> If 🔴 BLOCKERS exist and the user responds `commit`, **refuse** and report:
> *"Blockers detected. Resolve before committing. Run the review again after fixing, or
> respond `fix` to attempt auto-fixes."*

---

### Blanket-mode override

When the user has authorized blanket mode (`proceed through all stages` or equivalent), the per-fix `yes/skip` flow above is replaced by the design-decision filter in the parent SKILL — see `### Design-Decision Filter` in `${CLAUDE_PLUGIN_ROOT}/skills/review-code/SKILL.md`. Design-decision findings present a card via `${CLAUDE_PLUGIN_ROOT}/references/decision-prompts.md`; all other fixes apply silently.
