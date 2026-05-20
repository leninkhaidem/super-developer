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

Strict verification that all planned feature requirements and acceptance criteria are complete in
the current codebase. Audit checks SPEC.md, tasks.json, accepted package proofs, final code state,
and Development Quality Contract MUST-level compliance. It is not a full code review, and it cannot
be bypassed or replaced by review-code, targeted review, helper validation, review-state snapshots,
or self-review summaries.

**Spawn a read-only audit sub-agent from files only — no conversation history.** In the planned-feature
pipeline, audit is the final internal acceptance gate after review-code discovery, delegated fixes,
Fix Verification Review, and any triggered widening/escalation have reached audit readiness.

## Arguments

- `$ARGUMENTS` — Feature name (required). Must match a directory under `.tasks/`.

## Step 1: Orchestrator Readiness Gate

1. Verify `.tasks/$ARGUMENTS/` exists and contains `SPEC.md`, `tasks.json`, and `proofs/`. If not,
   list available features and ask.
2. Resolve the audit worktree before validation. Prefer `.worktrees/$ARGUMENTS/merge/` when it
   exists; otherwise use the current repository root.
3. Read `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/tool-usage.md` before invoking helper scripts.
4. Execute the shared final validator before spawning the audit sub-agent, pointing stale-evidence
   checks at the resolved audit worktree:

   ```bash
   python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" --final --worktree "<audit-worktree>" ".tasks/$ARGUMENTS/tasks.json"
   ```

   If it exits non-zero, stop and resolve the reported `tasks.json` / package-proof blockers before
   auditing implementation completeness.
5. Enforce the local non-bypass proof gate: planned-feature audit requires accepted, fresh package
   proof evidence for every package. `package-proof-lifecycle.md` owns lifecycle mechanics, but audit
   must fail closed on missing, malformed, stale, reopened/unaccepted, contradictory, or uncertain
   proof evidence. Pipeline `reviews/review-code-state.json` is only a governance readiness signal;
   it is not proof or audit evidence.
6. In planned-feature pipeline context, confirm review-code reached audit readiness: every known
   confirmed serious finding has a `closed` Fix Verification Review verdict, triggered widened
   checks/escalations are complete, no serious fix-introduced regression remains unresolved, and any
   review-code fix that could affect package evidence has reopened, refreshed, validated, and
   reaccepted affected package proofs. If readiness is missing, malformed, stale, contradictory, or
   uncertain, stop and return to the governed fix/verification/proof-refresh flow.

## Step 2: Spawn Audit Sub-Agent

Before dispatch, load `references/audit-subagent-contract.md` from this audit skill directory. That
one-hop reference owns the audit sub-agent packet, verification procedure, report contract, and result
handling; do not activate unrelated review-code or implement runbooks for those details.

Launch an Opus-class sub-agent with:

- `.tasks/$ARGUMENTS/SPEC.md`
- `.tasks/$ARGUMENTS/tasks.json`
- `.tasks/$ARGUMENTS/proofs/WP<N>.proof.json` files
- the resolved audit worktree path, preferably `.worktrees/<feature>/merge/` for worktree features
- access to the project codebase from that worktree

The sub-agent must read the plan cold and verify against the actual codebase in the correct worktree.

## Step 3: Result Boundary

Use the report contract in `references/audit-subagent-contract.md`.

- **PASS:** Confirm the feature implementation is complete and verified. State: `Final audit passed.
  Merge worktree at .worktrees/<feature>/merge/ is ready for merge approval.` Do not invoke
  review-code after PASS; review-code already reached audit readiness before final audit in the
  planned-feature pipeline.
- **FAIL:** Present the issues, suggest whether each needs a plan update, bug fix, or manual
  verification, and STOP. Do not invoke another broad review/audit loop automatically. In
  auto-resolve mode, return findings to the implement/review-code governed fix delegation and Fix
  Verification Review flow with bug-class guidance.

## Constraints

- Audit proves planned acceptance criteria, enforces BLOCKER/CODE-QUALITY outcomes from the
  Development Quality Contract, and may report non-blocking ADVISORY outcomes; review-code remains
  responsible for broader diff-risk analysis.
- The sub-agent must not modify code or `tasks.json`.
- If `tasks.json` status is out of sync with reality, flag it but do not auto-correct.
