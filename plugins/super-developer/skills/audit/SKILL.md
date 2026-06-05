---
name: audit
description: >
  Final read-only planned-feature completion audit. Use when the user asks to audit, verify
  implementation, check completion, validate the build, or confirm the feature matches the accepted
  plan. Do not use as ordinary code review or to repair files inline.
---

# Audit

Run the final non-bypass Slice-first completeness gate from files and integrated code state.

## Always

- Audit is read-only: never edit code, registry, packages, Slices, proof Markdown, package reports, review state, or lifecycle status.
- Final review-code readiness must exist before planned-feature pipeline audit; audit does not replace review-code.
- Helper success, dashboard status, package self-review, proof rows, or package reports are necessary signals, never sufficient alone.
- Spawn one cold read-only audit sub-agent from file paths; do not rely on conversation history.
- PASS means final audit passed for the same reviewed integrated state; FAIL blocks readiness.

## Do

1. Resolve required feature argument under `.tasks/<feature>/`.
2. Require `SPEC.md`, `tasks.json`, `packages/`, `proofs/`, and `reports/`; stop on missing or unsafe artifacts.
3. Resolve audit worktree: prefer `.worktrees/<feature>/merge/`, otherwise current repository root. Record git ref/commit.
4. Load `../../references/tool-usage.md`, then run the read-only final mechanical gate:

   ```bash
   python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-final ".tasks/<feature>/tasks.json"
   ```

5. Confirm every declared package proof Markdown and package verification report is present, current enough to dispatch, and bound to the final state at a mechanical level.
6. Confirm `.tasks/<feature>/reviews/review-code-state.json` exists for pipeline audit, matches the canonical governance state in `slice-first-artifacts.md`, is for the same feature/integrated state, has `mode: "pipeline"` and `state: "ready_for_audit"`, leaves `findings.open_serious` empty, and has true `closure_status.ready_for_audit` plus `closure_status.proofs_and_reports_fresh`.
7. Load `references/audit-subagent-contract.md` and dispatch a cold read-only sub-agent with exact paths, final review-code report path when available or explicit `none`, and resolved git/worktree state.
8. Return only PASS/FAIL, blocking findings, and repair handoff targets.

## Load if needed

- Helper command safety → `../../references/tool-usage.md`.
- Slice path and product/control-plane authority → `../../references/conceptualize-slice-authority.md`.
- Artifact shapes → `../../references/slice-first-artifacts.md`.
- Package proof/report freshness → `../../references/package-lifecycle.md`.
- Audit sub-agent packet, procedure, and report contract → `references/audit-subagent-contract.md`.

## Stop if

- Required artifacts, proof Markdown, package reports, Slice paths, or final code state are missing, unsafe, unreadable, stale, malformed, contradictory, or uncertain.
- `sliceproof.py validate-final` fails.
- Review-code readiness is missing, malformed, stale, not same-state, not pipeline/ready, has open serious findings, has unresolved widening/regression, or lacks true proof/report freshness.
- A user asks audit to fix, mark done, accept risk, bypass review-code, bypass package verification, or infer semantic proof from dashboard/helper output.
- The correct result requires product/design choice, scope change, new dependency/service, credentials, unsafe command, or risk acceptance.

## Output

Return:

- `PASS` with final audited state and merge-worktree path when all gates pass;
- `FAIL` with blocking categories, affected Slices/packages/proof rows/reports/code paths, and the minimal repair handoff;
- no artifact mutations.
