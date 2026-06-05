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
- Package final readiness for the resolved integrated state must exist before planned-feature pipeline audit.
- Review-code state/report are optional audit context: use a safe path when supplied or available, otherwise pass explicit `none`; absence does not block audit dispatch.
- Helper success, dashboard status, package self-review, proof rows, or package reports are necessary signals, never sufficient alone.
- Spawn one cold read-only audit sub-agent from file paths; do not rely on conversation history.
- PASS means final audit passed for the same integrated state only; merge/readiness still requires clean review-code readiness for that same state.

## Do

1. Resolve required feature argument under `.tasks/<feature>/`.
2. Require `SPEC.md`, `tasks.json`, `packages/`, `proofs/`, and `reports/`; stop on missing or unsafe artifacts.
3. Resolve audit worktree: prefer `.worktrees/<feature>/merge/`, otherwise current repository root. Record git ref/commit.
4. Load `../../references/tool-usage.md`, then run the read-only final mechanical gate:

   ```bash
   python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-final ".tasks/<feature>/tasks.json"
   ```

5. Confirm every declared package proof Markdown and package verification report is present, current enough to dispatch, and bound to the final integrated state at a mechanical level.
6. Resolve optional review-code context: use supplied safe state/report paths, or safe canonical `.tasks/<feature>/reviews/review-code-state.json` and final report when available, otherwise record explicit `none`. When state is present, validate same feature/integrated state, `mode: "pipeline"`, `state: "ready_for_audit"`, empty `findings.open_serious`, and true `closure_status.ready_for_audit` plus `closure_status.proofs_and_reports_fresh`; absence is not a dispatch blocker.
7. Load `references/audit-subagent-contract.md` and dispatch a cold read-only sub-agent with exact paths, optional review-code state/report paths or explicit `none`, and resolved git/worktree state.
8. Return only audit PASS/FAIL, blocking findings, review-code context status, and repair handoff targets.

## Load if needed

- Helper command safety → `../../references/tool-usage.md`.
- Slice path and product/control-plane authority → `../../references/conceptualize-slice-authority.md`.
- Artifact shapes → `../../references/slice-first-artifacts.md`.
- Package proof/report freshness → `../../references/package-lifecycle.md`.
- Audit sub-agent packet, procedure, and report contract → `references/audit-subagent-contract.md`.

## Stop if

- Required artifacts, proof Markdown, package reports, Slice paths, or final code state are missing, unsafe, unreadable, stale, malformed, contradictory, or uncertain.
- `sliceproof.py validate-final` fails.
- Package final readiness is missing, malformed, stale, not bound to the audited integrated state, or cannot be validated mechanically.
- A non-`none` review-code context is unsafe or unreadable; if review-code context is missing or not clean, audit may still run but final merge/readiness must remain blocked until review-code readiness is clean for the same integrated state.
- A user asks audit to fix, mark done, accept risk, bypass final readiness requirements, bypass package verification, or infer semantic proof from dashboard/helper output.
- The correct result requires product/design choice, scope change, new dependency/service, credentials, unsafe command, or risk acceptance.

## Output

Return:

- `PASS` with final audited state, merge-worktree path, and review-code context status when audit gates pass;
- `FAIL` with blocking audit categories, affected Slices/packages/proof rows/reports/code paths, and the minimal repair handoff;
- no artifact mutations.
