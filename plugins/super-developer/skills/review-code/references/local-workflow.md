# Local Code Review Workflow

Instructions specific to reviewing local code changes before committing or pushing.

**Requirement:** `git` installed, inside a Git repository. No GitHub dependency — works offline.

**User context:** If the user provides additional context (intent, constraints, known trade-offs,
focus areas), pass it to all review agents. This reduces false positives significantly because
agents can distinguish intentional decisions from oversights.

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

After setup, return to SKILL.md for the shared review pipeline (Steps 2-3).

_(Phases 2-3 are shared pipeline steps defined in SKILL.md — return there now.)_

---

## Phase 4 — Review Report

Present to the user.

Use the canonical report template from SKILL.md with:

- **HEADER:** `Local Code Review`
- **METADATA:** ``**Branch:** `<current branch>` | **Scope:** <staged | uncommitted | branch diff against origin/<branch>> | **Files:** <count> changed``

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
| `fix` | Delegate fixes for confirmed 🔴 and 🟠 findings to a Fix Implementer, then require delegated Fix Verification Review before any post-fix commit or readiness action (Workflow A below). |
| `commit` | Stage and commit the reviewed state as-is — only if no 🔴 BLOCKERS and state revalidation passes (Workflow B below). |
| `details <N>` | Expand finding N with full context, code snippet, and recommended fix. Return to Phase 5. |
| `abort` | No action. Close session cleanly. |

> Any response other than these keywords → clarification prompt.
> **Never interpret ambiguity, silence, or partial confirmation as approval.**

### Local State Gate

Before mutating files, applying fixes, staging, creating commits, or reporting post-fix readiness,
revalidate the immutable reviewed state captured in Phase 0:

- The current branch and `HEAD` SHA still match, unless the only new commits are the approved local
  fix commits from this flow.
- The reviewed file list and reviewed diff checksum still match for unchanged findings.
- Staged content still matches when `SCOPE="staged"`.
- No new unreviewed files or broadened diff scope appeared.
- The base ref and base SHA still match for branch-diff reviews.

If state is stale or broadened, reject the action and instruct the user to rerun review. Do not
partially apply fixes or create a commit against a state that was not reviewed.

---

## Workflow A — `fix`

Triggered when user responds `fix`.

Local fixing has two separate delegated roles:

- **Fix Implementer:** applies bounded fixes for confirmed findings.
- **Fix Reviewer:** verifies the resulting fix delta and decides whether each original finding is
  closed without introducing security/privacy/safety/failure-mode regressions.

The main agent does not implement local review-finding fixes that change code behavior, public
surface, tests, documentation structure, or substantive content. Delegate those changes to the Fix
Implementer. The main agent may apply only super-simple mechanical typo or formatting fixes inline;
report every inline exception explicitly, including why it was mechanical and behavior-preserving.

### Fix Implementer Input

Pass the Fix Implementer:

- Confirmed 🔴 and 🟠 findings, including dedupe keys, Skeptic verdicts, evidence, and recommendations
- Reviewed-state metadata from Phase 0
- Target paths and exact scope boundaries
- User constraints, repository constraints, and mode constraints
- Instruction to avoid unrelated cleanup, opportunistic refactors, broad rewrites, or touching files
  outside the target paths unless required to close a confirmed finding
- Any decision-card outcomes from the SKILL.md Design-Decision Filter

The Fix Implementer returns the fix delta, files changed, findings attempted, findings intentionally
left unresolved, and any scope-expansion request. A scope-expansion request must identify the exact
trigger and why the original scope cannot close the finding.

### Local Fix Verification Review

After fixes are applied, run delegated Fix Verification Review by default. The Fix Reviewer receives:

- The fix delta only, plus enough surrounding context to evaluate it
- The original confirmed findings and dedupe keys
- Reviewed-state metadata and current post-fix state metadata
- Widening triggers raised by the Fix Implementer or detected by the main agent
- Required closure output for every original finding: `closed`, `partially-closed`, `not-closed`, or
  `reopened`
- Required baseline security/privacy/safety/failure-mode regression sniff for the fix delta

The Fix Reviewer checks that:

1. Each fixed finding is actually closed by the delta.
2. The fix remains inside approved scope or documents a valid widening trigger.
3. The fix does not introduce new security, privacy, safety, data-integrity, or failure-mode risk.
4. The fix does not silently change public surface, tests, or documentation structure beyond the
   approved finding scope.

Local fix verification widens beyond delegated sub-agent delta review only for documented triggers:
new touched modules outside target paths, public API or schema changes, security/privacy/safety
sensitive fixes, migration/persistence changes, data-integrity fixes, concurrency/performance risk,
or a Fix Reviewer verdict of `partially-closed`, `not-closed`, or `reopened`.

Repeated local fix-verification expansion must stop instead of looping indefinitely. After one widened
verification pass, if more scope expansion is still needed, report the unresolved findings, the
expansion trigger, and the exact unreviewed scope to the user. Do not keep widening recursively.

Post-fix commit or readiness actions may proceed only when delegated Fix Verification Review passes,
all fixed findings are `closed`, no new serious regressions are found, and the Local State Gate still
passes.

---

## Workflow B — `commit`

Triggered when user responds `commit` **AND** no 🔴 BLOCKERS exist.

Before staging or committing, run the Local State Gate. Reject stale or broadened state.

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
> respond `fix` to attempt delegated fixes."*

---

## Blanket-mode override

When the user has authorized blanket mode (`proceed through all stages` or equivalent), per-finding
fix confirmation is replaced by the design-decision filter in the parent SKILL — see
`### Design-Decision Filter` in `${SUPER_DEVELOPER_PLUGIN_ROOT}/skills/review-code/SKILL.md`. Design-decision
findings present a card via `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/decision-prompts.md`; all other
eligible local fixes are delegated to the Fix Implementer silently.

Blanket mode does not bypass the Code Reviewer's baseline security/privacy/safety sniff, Skeptic
verification for serious findings, the Local State Gate, delegated Fix Verification Review, or the
requirement to stop and report repeated fix-verification scope expansion.
