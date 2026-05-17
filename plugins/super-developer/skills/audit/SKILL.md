---
name: audit
description: >
  This skill should be used when the user asks to "audit", "verify implementation", "check
  acceptance criteria", "post-implementation check", "verify the build", "validate completion",
  or wants to confirm that all tasks in a plan were completed as specified. Triggers on phrases
  like "audit", "verify", "check completion", "acceptance criteria", "did we build what we
  planned". Runs as the final internal acceptance gate in the planned-feature pipeline after the governed review-code discovery/fix-verification flow. Also
  invocable standalone.
---

# Audit: Post-Implementation Verification

Strict verification that all planned feature requirements and acceptance criteria are complete in the current codebase. Checks SPEC.md, tasks.json, accepted package proofs, final code state, and Development Quality Contract MUST-level compliance — this is not a full code review.

**Spawn a sub-agent for the audit. It must work from files only — no conversation history. In the planned-feature pipeline, audit is the final internal acceptance gate after review-code discovery, delegated fixes, Fix Verification Review, and any triggered widening/escalation have reached audit readiness.**

## Arguments

- `$ARGUMENTS` — Feature name (required). Must match a directory under `.tasks/`.

---

## Step 1: Spawn Audit Sub-Agent

1. Verify `.tasks/$ARGUMENTS/` exists and contains `SPEC.md`, `tasks.json`, and `proofs/`. If not, list available features and ask.
2. Resolve the audit worktree before validation. Prefer `.worktrees/$ARGUMENTS/merge/` when it exists; otherwise use the current repository root.
3. Read `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/tool-usage.md` before invoking helper scripts.
4. Execute the shared validator before spawning the audit sub-agent, pointing stale-evidence checks at the resolved audit worktree:

   ```bash
   python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" --final --worktree "<audit-worktree>" ".tasks/$ARGUMENTS/tasks.json"
   ```

   If the validator exits non-zero, stop and resolve the reported `tasks.json` / package proof blockers before auditing implementation completeness.
5. In planned-feature pipeline context, confirm review-code reached audit readiness before spawning audit: every known confirmed serious finding has a `closed` Fix Verification Review verdict or an approved verification downgrade, every triggered widened check/escalation is complete, and no serious fix-introduced regression remains unresolved. If not, stop and return to the governed fix/verification flow.
6. Launch an **Opus-class sub-agent** with:

- `.tasks/$ARGUMENTS/SPEC.md`
- `.tasks/$ARGUMENTS/tasks.json`
- `.tasks/$ARGUMENTS/proofs/WP<N>.proof.json` files
- **The merge worktree path** — if the feature was implemented using git worktrees (see the worktree skill for path conventions), direct the sub-agent to work from `.worktrees/<feature>/merge/` where the feature branch is checked out. If no worktree exists (e.g., standalone audit), use the current working directory.
- Access to the project codebase from that worktree

The sub-agent must **not** receive any conversation history. It reads the plan cold and verifies against the actual codebase in the correct worktree.

## Step 2: Audit Procedure (executed by sub-agent)

First, read SPEC.md, tasks.json, and the package proof files under `.tasks/<feature>/proofs/`. Accepted package proof evidence is required for every planned-feature audit, including standalone invocation against `.tasks/<feature>/`.

Verify every listed requirement and feature-level acceptance criterion against the current codebase and final integrated state:

- If a SPEC item describes a user-visible behavior, confirm the behavior exists and matches the requirement.
- If a SPEC item describes a constraint, confirm the implementation respects it.
- If a SPEC item cannot be verified programmatically, require durable user-approved manual evidence in the relevant package proof; otherwise flag `[SPEC]` and fail.
- If no task acceptance criterion covers a SPEC requirement or acceptance criterion, flag it as `[GAP]` even if all task-level criteria pass.
- Verify every task acceptance criterion has a package proof entry tied to its criterion ID and source refs.

For every task marked `done` in tasks.json:

### 2a. Task Acceptance Criteria Verification

Go through each task acceptance criterion and verify it holds in the current codebase:

- If a criterion specifies a file, function, endpoint, command, behavior, edge case, or context bundle — confirm the referenced implementation/evidence exists and behaves as described.
- If a criterion specifies testable behavior — run the relevant test or command if possible, using the command safety rules from the plan and Execution Contract.
- If package proof evidence is missing, malformed, stale, failed, blocked, reopened/unaccepted, or has unapproved `manual_required` evidence for the criterion — flag `[ISSUE]` and fail.
- If a criterion cannot be verified programmatically and no complete user-approved manual evidence exists — flag `[ISSUE]` and fail.

### 2b. Development Quality Contract Compliance

Read `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/clean-code-rules.md` and verify the implementation against the **Development Quality Contract**:

- Enforce **BLOCKER** findings for MUST-level violations, missing required verification, fake success states, caller-contract failures, unsafe trust-boundary behavior, security/privacy/safety/data-integrity risks, incompatible API/contract changes, or unresolved acceptance criteria.
- Enforce **CODE-QUALITY** findings for unjustified SHOULD-level maintainability violations, unclear boundaries, harmful duplication, unnecessary coupling, complexity, or spreading legacy-bad patterns.
- Use **ADVISORY** for optional, actionable, non-blocking improvements grounded in the diff and local conventions.
- Do not rely only on legacy file/function-size heuristics. Use the contract's workflow gates: discovery, design, implementation, testing/verification, completion evidence, and audit/review enforcement.
- Verify non-trivial changes include the compact Quality Contract Evidence block or equivalent evidence: inspection outcome, boundary/design choice, affected artifacts, verification run, and rule exceptions.

Note the file, line, severity, and violated contract clause for each finding.

### 2b-bis. Package Proof Check

Apply this section for every audit. Missing or non-accepted package proof evidence is a [PROOF] failure.

- Missing package proof files, invalid package proof files, or non-accepted package proof lifecycle state are [PROOF] failures.
- For each completed task acceptance criterion, confirm the package proof entry references the correct criterion ID, task ID, package ID, source refs, context bundles, state/commit/worktree, files or symbols, commands/results when applicable, observed result, edge cases when relevant, and mock disclosure.
- Fail stale evidence when cited files, symbols, commands, or package outputs changed after the recorded proof state.
- `manual_required` passes only when durable manual evidence includes affected criterion IDs, approval provenance or supplied artifact, observed result, scope, limits, approval date, and state reference. A bare approval boolean is never enough.

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
- SPEC requirements/acceptance criteria: X/Y verified, N failed, N approved manual
- Task acceptance criteria: X/Y verified, N failed, N approved manual

### Issues Found
1. [BLOCKER] <description> — violated requirement/criterion/contract clause
2. [CODE-QUALITY] <description> — maintainability contract clause
3. [ADVISORY] <description> — optional improvement
4. [SPEC] <description> — SPEC item <REQ/AC ID>
5. [ISSUE] <description> — task <ID>, criterion <N>
6. [GAP] <description> — requirement from SPEC.md not covered
7. [TODO] <file:line> — incomplete work marker found
8. [PROOF] <description> — package proof missing, malformed, stale, unaccepted/reopened, blocked/failed, or unapproved manual evidence

### Passed
- [list of tasks that fully passed verification]

### Verdict
PASS — All tasks completed and verified in the final state, with no [BLOCKER], [CODE-QUALITY], [SPEC], [ISSUE], [GAP], [TODO], or [PROOF] findings. [ADVISORY] findings may be listed without blocking completion.
or
FAIL — Any [BLOCKER], [CODE-QUALITY], [SPEC], [ISSUE], [GAP], [TODO], or [PROOF] finding requires attention before the feature is considered complete. Manual-required criteria are failures unless durable user-approved manual evidence is present and scoped to the criterion.
```

## Step 4: Handle Results

Based on the sub-agent's report:

- **PASS:** Confirm to the user that the feature implementation is complete and verified.
- **FAIL:** Present the issues. For each issue, suggest whether it needs a plan update (new tasks), a bug fix, or manual verification. Ask the user how to proceed.

---

## Pipeline Continuation

If audit verdict is FAIL, present issues and STOP. Do not invoke another broad review/audit loop automatically. In auto-resolve mode, return findings to the implement/review-code governed fix delegation and Fix Verification Review flow with bug-class guidance.

If PASS, state: "Final audit passed. Merge worktree at `.worktrees/<feature>/merge/` is ready for merge approval." Do not invoke review-code after PASS; review-code already reached audit readiness before final audit in the planned-feature pipeline.

## Constraints

- This is an audit, not a full code review. It proves planned acceptance criteria, enforces BLOCKER/CODE-QUALITY outcomes from the Development Quality Contract, and may report non-blocking ADVISORY outcomes; review-code remains responsible for broader diff-risk analysis.
- The sub-agent must not modify any code or tasks.json. It is read-only.
- If the audit finds that tasks.json status is out of sync with reality (e.g., a task marked `done` but the code doesn't reflect it), flag it but do not auto-correct.
