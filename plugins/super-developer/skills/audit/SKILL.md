---
name: audit
description: >
  This skill should be used when the user asks to "audit", "verify implementation", "check
  acceptance criteria", "post-implementation check", "verify the build", "validate completion",
  or wants to confirm that all tasks in a plan were completed as specified. Triggers on phrases
  like "audit", "verify", "check completion", "acceptance criteria", "did we build what we
  planned". Always runs as part of the development pipeline after implementation. Also
  invocable standalone.
---

# Audit: Post-Implementation Verification

Lightweight verification that all tasks in a feature plan have been completed as specified. Checks completeness and acceptance criteria against the plan — this is not a full code review.

**Spawn a sub-agent for the audit. It must work from files only — no conversation history.**

## Arguments

- `$ARGUMENTS` — Feature name (required). Must match a directory under `.tasks/`.

---

## Step 1: Spawn Audit Sub-Agent

Launch an **Opus-class sub-agent** with:

- `.tasks/$ARGUMENTS/CONTEXT.md`
- `.tasks/$ARGUMENTS/tasks.json`
- **The merge worktree path** — if the feature was implemented using git worktrees, direct the sub-agent to work from `.worktrees/<feature>/merge/` where the feature branch is checked out. If no worktree exists (e.g., standalone audit), use the current working directory.
- Access to the project codebase from that worktree

The sub-agent must **not** receive any conversation history. It reads the plan cold and verifies against the actual codebase in the correct worktree.

## Step 2: Audit Procedure (executed by sub-agent)

For every task marked `done` in tasks.json:

### 2a. Acceptance Criteria Verification

Go through each acceptance criterion and verify it holds in the current codebase:

- If a criterion specifies a file, function, or endpoint — confirm it exists and behaves as described.
- If a criterion specifies a testable behavior — run the relevant test or command if possible.
- If a criterion cannot be verified programmatically — note it as "manual verification required."

### 2b. Completeness Check

- Cross-reference CONTEXT.md against the implementation. Are there requirements described in the context document that no task addresses?
- Are there tasks marked `skipped` or `blocked`? Flag these with their reasons.
- Are there any TODO, FIXME, or HACK comments introduced during implementation that indicate incomplete work?

### 2c. Integration Sanity Check

- Do the implemented components connect correctly? (e.g., if Phase 1 built the data layer and Phase 2 built the API, does the API actually use the data layer as designed?)
- Are there any import errors, missing dependencies, or broken references?
- If tests exist, do they pass?

## Step 3: Audit Report

The sub-agent produces a structured report:

```
## Audit Report: <feature-name>

### Summary
- Tasks completed: X/Y
- Tasks skipped: N (with reasons)
- Tasks blocked: N (with reasons)
- Acceptance criteria: X/Y verified, N require manual check

### Issues Found
1. [ISSUE] <description> — task <ID>, criterion <N>
2. [GAP] <description> — requirement from CONTEXT.md not covered
3. [TODO] <file:line> — incomplete work marker found

### Passed
- [list of tasks that fully passed verification]

### Verdict
PASS — All tasks completed and verified.
or
FAIL — Issues require attention before feature is considered complete.
```

## Step 4: Handle Results

Based on the sub-agent's report:

- **PASS:** Confirm to the user that the feature implementation is complete and verified.
- **FAIL:** Present the issues. For each issue, suggest whether it needs a plan update (new tasks), a bug fix, or manual verification. Ask the user how to proceed.

---

## Pipeline Continuation

If audit verdict is FAIL, present issues and STOP. Do not invoke the next stage.

If PASS and blanket approval was given (e.g., "proceed through all stages", "run end to end", "do everything"), invoke immediately. If PASS without blanket approval, state: "Audit passed. Merge worktree at `.worktrees/<feature>/merge/`." Wait for user confirmation. Then invoke:

Use the Skill tool with: skill: "super-developer:review-code", args: "<feature-name>"

Do NOT attempt to execute the next skill's logic inline. The Skill tool loads it properly.

## Constraints

- This is an audit, not a code review. It checks "did we build what we said we would" — not "is the code well-written."
- The sub-agent must not modify any code or tasks.json. It is read-only.
- If the audit finds that tasks.json status is out of sync with reality (e.g., a task marked `done` but the code doesn't reflect it), flag it but do not auto-correct.
