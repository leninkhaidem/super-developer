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

1. Verify `.tasks/$ARGUMENTS/` exists and contains `SPEC.md` and `tasks.json`. If not, list available features and ask.
2. Execute the shared validator before spawning the audit sub-agent:

   ```bash
   python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" ".tasks/$ARGUMENTS/tasks.json"
   ```

   If the validator exits non-zero, stop and resolve the reported `tasks.json` blockers before auditing implementation completeness.
3. Launch an **Opus-class sub-agent** with:

- `.tasks/$ARGUMENTS/SPEC.md`
- `.tasks/$ARGUMENTS/tasks.json`
- **The merge worktree path** — if the feature was implemented using git worktrees (see the worktree skill for path conventions), direct the sub-agent to work from `.worktrees/<feature>/merge/` where the feature branch is checked out. If no worktree exists (e.g., standalone audit), use the current working directory.
- Access to the project codebase from that worktree

The sub-agent must **not** receive any conversation history. It reads the plan cold and verifies against the actual codebase in the correct worktree.

## Step 2: Audit Procedure (executed by sub-agent)

First, read SPEC.md and verify every listed requirement and feature-level acceptance criterion against the current codebase:

- If a SPEC item describes a user-visible behavior, confirm the behavior exists and matches the requirement.
- If a SPEC item describes a constraint, confirm the implementation respects it.
- If a SPEC item cannot be verified programmatically, note it as "manual verification required."
- If no task covers a SPEC requirement or acceptance criterion, flag it as `[GAP]` even if all task-level criteria pass.

For every task marked `done` in tasks.json:

### 2a. Task Acceptance Criteria Verification

Go through each task acceptance criterion and verify it holds in the current codebase:

- If a criterion specifies a file, function, or endpoint — confirm it exists and behaves as described.
- If a criterion specifies a testable behavior — run the relevant test or command if possible.
- If a criterion cannot be verified programmatically — note it as "manual verification required."

### 2b. Clean Code Compliance

Read `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/clean-code-rules.md` and verify the implemented code follows the rules:

- **File-level:** No file exceeds 300 lines. Each file has a single concern. No orphan files.
- **Function-level:** No function exceeds 50 lines. No more than 4 parameters. No nesting beyond 3 levels.
- **Naming and structure:** No magic numbers/strings. Follows existing patterns in the codebase.
- **Safety:** No `any` types (TypeScript), no empty catch blocks, no hardcoded secrets.
- **Anti-patterns:** No unnecessary abstractions or speculative code.

Flag violations as `[CODE-QUALITY]` issues in the audit report. Note the file, line, and which rule was violated.

### 2c. Completeness Check

- Cross-reference SPEC.md against the implementation. Are there requirements described in the specification that no task addresses?
- Are there tasks marked `skipped` or `blocked`? Flag these with their reasons.
- Are there any TODO, FIXME, or HACK comments introduced during implementation that indicate incomplete work?

### 2d. Integration Sanity Check

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
- SPEC requirements/acceptance criteria: X/Y verified, N require manual check
- Task acceptance criteria: X/Y verified, N require manual check

### Issues Found
1. [SPEC] <description> — SPEC item <REQ/AC ID>
2. [ISSUE] <description> — task <ID>, criterion <N>
3. [GAP] <description> — requirement from SPEC.md not covered
4. [TODO] <file:line> — incomplete work marker found

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

Use the Skill tool with: skill: "review-code", args: "<feature-name>"

Do NOT attempt to execute the next skill's logic inline. The Skill tool loads it properly.

## Constraints

- This is an audit, not a code review. It checks "did we build what we said we would" — not "is the code well-written."
- The sub-agent must not modify any code or tasks.json. It is read-only.
- If the audit finds that tasks.json status is out of sync with reality (e.g., a task marked `done` but the code doesn't reflect it), flag it but do not auto-correct.
