---
name: review-code
description: >
  This skill should be used when the user asks to review a PR, review code changes, review a pull
  request, check code quality, or wants feedback on a diff. Works for both GitHub
  PRs (provide a PR URL or number like "owner/repo#42") and local code changes (staged, unstaged,
  or branch diffs). Triggers on phrases like "review this PR", "review my code", "check these
  changes", "code review", "review", "look over my changes". Also activates as the final step
  in the development pipeline after implementation.
---

# Code Review — Multi-Agent Pipeline

A unified code review that runs 4 specialist agents in parallel, then verifies every serious
finding through an adversarial Skeptic Agent before reporting. Works in three modes depending
on context.

## Step 1 — Detect Review Mode

Determine the review scope using this priority order:

### Priority 0: Pipeline Context

If a feature was just implemented in this session (feature name and merge worktree path are
known from the implementation step), review the feature branch directly.
Worktree path conventions are defined in the `worktree` skill. Invoke it if necessary

- Work from the merge worktree at `.worktrees/<feature>/merge/`
- `DIFF_CMD="git diff main...feature/<feature>"`
- Collect file list: `git diff main...feature/<feature> --stat`
- Scope: complete feature branch diff against main

Report scope before proceeding:
```
Review Scope: feature branch `feature/<name>` vs main
Worktree: .worktrees/<feature>/merge/
Files changed: <count>
Insertions: +<count>  Deletions: -<count>
```

Then skip to Step 2 (shared pipeline).

### Priority 1: PR Mode

A PR identifier is present (URL like `https://github.com/org/repo/pull/42`, shorthand like
`owner/repo#42`, or just `#42` in a repo context).

Read `references/pr-workflow.md` for setup, report format, and post-review actions.

### Priority 2: Local Mode

No PR identifier, no pipeline context. The user wants to review local changes (staged, unstaged,
or a branch diff).

Read `references/local-workflow.md` for **scope detection (Phase 0), setup (Phase 1)**,
report format, and actions.

Complete the mode-specific **setup and preflight** from the reference file, then return here for
the shared review pipeline (Steps 2-3). After the shared pipeline, go back to the reference file
for the **report format** and **gated actions**.

---

## Step 2 — Parallel Sub-Agent Reviews

### Model Selection

Read `${CLAUDE_PLUGIN_ROOT}/references/model-preferences.md` for the canonical schema and resolution procedure.

Resolve model preferences for two agent roles:
- **Specialists** (security, logic, performance, architecture): Use the `review-code` key. Hardcoded default: `inherit`.
- **Skeptic Agent:** Uses the `skeptic-agent` key. Hardcoded default: `inherit`.

**Adaptive interpretation for review-code:** Specialists use Sonnet for focused pattern-matching. Skeptic uses Opus for adversarial reasoning across all findings (via `skeptic-agent` key — when it resolves to `adaptive`, use the strongest available model). When the resolved value is `inherit`, all agents use the orchestrator's model. When the resolved value is a specific model name, pass it directly.

**Large diff handling:** If the diff exceeds 2,000 lines, split into batches by grouping related files (by directory or module). Run the full 4-specialist + Skeptic pipeline on each batch sequentially, then merge findings into a single consolidated report. Do not ask the user to scope the review — handle the batching autonomously.

Spawn 4 specialist sub-agents **in parallel** (model per resolved preference above). Each receives:
- The full diff (or the current batch's diff if batching)
- Change context (PR description + title, commit messages, user-supplied context, or feature SPEC.md)
- **Codebase path** for file exploration: the review worktree path (`.worktrees/pr-review/<number>/` for PR mode, `.worktrees/<feature>/merge/` for pipeline mode, or the project root for local mode)

### Specialist Agents

| Agent | Mandate |
|---|---|
| **Security** | Injection risks, auth/authz issues, secrets in code, insecure dependencies, input validation gaps |
| **Logic & Correctness** | Bugs, edge cases, race conditions, incorrect assumptions, off-by-one errors |
| **Performance** | N+1 queries, unnecessary allocations, blocking I/O, missing indexes, inefficient algorithms |
| **Architecture & Maintainability** | Violations of existing patterns, coupling issues, naming inconsistencies, dead code, complexity hotspots |

When model preferences resolve to `adaptive`, specialists do focused pattern-matching (Sonnet) while the Skeptic does adversarial reasoning across all findings (Opus via `skeptic-agent` key). When resolved to `inherit`, all agents use the orchestrator's model. When resolved to a specific model name, all agents in that role use that model.

### Severity Taxonomy

Every finding must be classified — no exceptions:

| Severity | Label | Meaning |
|---|---|---|
| 🔴 | **BLOCKER** | Must be resolved before merge/commit. Correctness or security risk. |
| 🟠 | **CRITICAL** | Strongly recommended fix. Significant quality or risk issue. |
| 🟡 | **SUGGESTION** | Non-blocking improvement. |

### Specialist Output Format

Each specialist must return findings in this exact format — no preamble, no summary, no prose
outside the format:

```
[SEV] FILE:LINE — TITLE
WHY: <1 sentence, root cause>
FIX: <1 sentence, concrete action>
```

Rules:
- `SEV`: Use emoji (🔴, 🟠, or 🟡)
- No introductory text, no concluding summaries
- 🟡 findings may omit the `FIX:` line if no action is needed
- If no findings: respond with exactly `NONE`
- Do NOT append `NONE` after findings — `NONE` means zero findings only

Example:
```
🔴 src/api/users.ts:89 — SQL injection via string concatenation
WHY: User input interpolated directly into query string.
FIX: Use parameterized query with $1 placeholder.

🟡 src/api/users.ts:45 — Redundant type assertion
WHY: TypeScript already narrows the type via the guard on line 42.
```

---

## Step 3 — Adversarial Verification (Skeptic Agent)

Spawn a Skeptic Agent (model per resolved preference from Step 2) that receives all findings from Step 2.

For every 🔴 BLOCKER and 🟠 CRITICAL finding, the Skeptic Agent independently locates
supporting evidence in the diff or codebase:
- **CONFIRMED** — Evidence independently reproduced.
- **DISPUTED** — Evidence not found. Excluded from the final report.

The Skeptic Agent's job is to *disprove* findings. Confirmation is a byproduct of failed
disproof. Do not reuse the same reasoning chain from Step 2 — that defeats the purpose.

### False Positive Checklist

Before confirming any 🔴 or 🟠 finding, run every item below. A single failed check is
sufficient grounds to mark the finding **DISPUTED**.

**1 Scope Mismatch** — *Most common. Check first.*
Was this issue introduced by this change, or does it pre-exist? If the issue pre-exists and
this change didn't modify the relevant lines, mark **DISPUTED.**

**2 Context Blindness** — Does the surrounding code (20+ lines above and below the flagged
line, plus imported utilities/middleware) already handle this? If addressed in context,
mark **DISPUTED.**

**3 Framework or Library Absorption** — Is the framework, ORM, or middleware already handling
this? (SQL injection flagged with parameterized ORM; missing auth flagged with router-level
middleware guard; unhandled promise rejections with global error boundary.) If the framework
provably absorbs the concern, mark **DISPUTED.**

**4 Dead or Unreachable Code Path** — Is the flagged code reachable in any real execution
path? Check call chains, feature flags, conditional branches. If unreachable in production,
mark **DOWNGRADED** (reclassify as 🟡 SUGGESTION).

**5 Intentional Design** — Is this a deliberate, documented decision? Check PR description,
commit messages, inline comments, AGENTS.md, ARCHITECTURE.md, ADR files, user-supplied
context, and SPEC.md. If intentional and documented, mark **DISPUTED** only for non-security,
non-privacy, and non-safety findings. Security/privacy/safety risks that are real and intentional
remain reportable; mark them **CONFIRMED** and note the documented intent in the reason.

**6 Test-Scope Confusion** — Does this finding apply only to test code, fixtures, mocks,
or seed data? If exclusively in test scope, mark **DISPUTED** for 🔴/🟠.

### Skeptic Agent Output Format

```
Finding: <original finding summary>
Checklist run: 1 2 3 4 5 6
Failed check: <checklist item that caused dispute, or NONE>
Verdict: CONFIRMED / DISPUTED / DOWNGRADED
Reason: <one sentence — what the Skeptic found or failed to find>
```

---

## Report Template

All modes use this canonical report structure. Substitute `<HEADER>` and `<METADATA>` per mode.

````markdown
## <HEADER>

<METADATA>

### 🔴 Blockers
1. [Finding] — `<filename>`, Line <line>
   <explanation>

### 🟠 Critical Issues
1. [Finding] — `<filename>`, Line <line>
   <explanation>

### 🟡 Suggestions _(non-blocking)_
1. [Finding] — `<filename>`, Line <line>

---
_Review generated via multi-agent analysis. All blockers and critical issues independently
verified by adversarial Skeptic Agent before reporting._
````

**Universal format rules:**
- **Omit empty sections.** If all sections are empty: "No issues found. ✅"
- **Disputed findings:** Silently excluded. Do not list, count, or mention them.
- **Downgraded findings:** Reclassified from 🔴/🟠 to 🟡 by the Skeptic (e.g., dead code paths). Include in the 🟡 Suggestions section with their original context.
- **Show only Skeptic-confirmed findings** for 🔴 and 🟠. 🟡 Suggestions from specialists are
  included as-is (Skeptic verification applies only to 🔴 and 🟠).

---

## Step 4 — Report & Actions

Return to the mode-specific workflow:

- **PR Mode** → `references/pr-workflow.md` — Phase 4 (report preview) and Phase 5
  (approve / request-changes / edit / abort)
- **Local Mode** → `references/local-workflow.md` — Phase 4 (report) and Phase 5
  (fix / commit / details / abort)
- **Pipeline context** → Use the canonical report template above with these slot values,
  then pipeline-specific gated actions below.

### Design-Decision Filter

When applying fixes under blanket mode, a finding is **promoted to a decision card** only when **all three** conditions hold:

1. Severity is `[BLOCKER]` or `[CRITICAL]`.
2. The reviewer surfaced two or more valid fix approaches with different runtime behavior, blast radius, or public surface area.
3. Picking among the approaches is a product or architecture decision rather than a code-quality decision.

Examples that prompt:

- "SQL injection — parameterize the query (status quo) OR migrate to ORM (3 callers affected, behavior preserved)"
- "Auth bypass — fix at middleware (centralized) OR per-route guard (explicit but verbose)"
- "Race condition — pessimistic lock (slower) OR optimistic retry (more code, faster happy path)"

Examples that do **not** prompt (fixed silently with the only sensible fix):

- "SQL injection — switch to parameterized query" (only one approach)
- "Off-by-one — change `<` to `<=`" (only one approach)
- "Missing null check — add guard" (only one approach)
- Any test-only fix, regardless of approach count, since it does not change shipped runtime behavior

When promoted, the card uses the shared template at `${CLAUDE_PLUGIN_ROOT}/references/decision-prompts.md`. Outside blanket mode, the existing per-fix `yes/skip` semantics in the workflow references continue to apply.

### Pipeline Context — Report & Actions

Use the canonical report template with:
- **HEADER:** `Feature Branch Review — \`feature/<name>\` vs \`main\``
- **METADATA:** `**Worktree:** \`.worktrees/<feature>/merge/\`` + `**Files:** <count> changed`

**Verdict:**
- **CLEAN** — No 🔴 or 🟠 findings. Feature branch is ready for merge approval.
- **ISSUES FOUND** — One or more 🔴 or 🟠 findings confirmed.

**Pipeline Gated Actions:**

| Keyword | Action |
|---|---|
| `fix` | Fix confirmed 🔴 and 🟠 findings in the merge worktree. Under blanket mode, design-decision findings (see Design-Decision Filter below) are presented as decision cards via `${CLAUDE_PLUGIN_ROOT}/references/decision-prompts.md`; all other fixes apply silently. Outside blanket mode, per-fix `yes/skip` semantics from `references/local-workflow.md` and `references/pr-workflow.md` are preserved. Commit fixes to the feature branch. |
| `details <N>` | Expand finding N with full context and recommended fix. Return to gated actions. |
| `abort` | No changes. Close review. |

> `commit` is not offered — feature branch code is already committed. Use `fix` to apply
> corrections, which are committed to the feature branch in the merge worktree.

_Designed for multi-agent orchestration. Requires: `git` (always), `gh` CLI (PR mode only)._
