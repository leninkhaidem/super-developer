# Dashboard Display Rules

## Contract

- Show registry/package/proof/report mechanics only.
- Do not mutate artifacts or lifecycle state.
- Do not call any status, proof, report, or helper result semantic proof.
- Prefer compact output; expand only for a requested feature or invalid artifact.

## All-Feature View

For each `.tasks/<feature>/tasks.json` candidate:

1. Run `sliceproof.py validate-plan`.
2. If invalid, show feature slug as `invalid` and include a one-line helper reason.
3. If valid, read registry fields and show:
   - feature/title/status;
   - package counts by registry status;
   - proof path existence counts;
   - package report signal counts;
   - review-code readiness state when present;
   - notes for invalid/missing mechanical signals.

Suggested columns:

```text
Feature              Status       Packages          Proofs              Reports             Notes
────────────────────────────────────────────────────────────────────────────────────────────────────
checkout-flow        in_progress  ✅2 🔄1 ⬜2        pass 2 / missing 1  pass 2 / missing 1  next: WP4
search-index         completed    ✅4               pass 4              pass 4              review ready
billing-ui           invalid      —                 —                   —                   invalid registry path
```

Sort incomplete active work first: `in_progress`, `planned`, `reviewed`, `blocked`, `on_hold`, `completed`, then invalid/unknown.

## Single-Feature View

Show:

- feature title and registry status;
- `validate-plan` result;
- package progress by registry status;
- package table with ID/title, status, dependencies, package path, proof path/state, report path/signal, and notes;
- dependency-ready packages: registry `pending` and every dependency registry `done`;
- interrupted packages: registry `in_progress`;
- blocked packages: registry `blocked` plus visible reason if present;
- review-code readiness signal from `.tasks/<feature>/reviews/review-code-state.json` when present;
- final mechanical check result when `validate-final` was run.

## Signal Labels

### Registry status

| Status | Icon | Meaning |
|---|---|---|
| `pending` | ⬜ | Not started. |
| `in_progress` | 🔄 | Work or repair underway. |
| `done` | ✅ | Completion gate claimed elsewhere; dashboard does not prove it. |
| `blocked` | 🚫 | Authority or artifact blocker. |

### Proof mechanical state

- `not-created` — declared proof path missing.
- `mechanically PASS` — `sliceproof.py validate-proof` exited 0.
- `mechanically incomplete/invalid` — `validate-proof` failed; show compact reason.
- `not checked` — proof check was not run.

### Report signal

Use weak report labels unless a deterministic helper/report parser proves more:

- `missing` — declared or conventional report path absent.
- `PASS reported` — report exists and visibly states `Result: passed` or equivalent package-verification PASS.
- `FAIL reported` — report exists and visibly states failed/open findings.
- `state-binding warning` — report exists but digest, commit, worktree, package path, proof path, or Slice path binding is missing/unclear from visible fields.
- `unreadable/unknown` — cannot safely read or classify.

Never convert report signal into package acceptance. Freshness and semantic sufficiency remain package-verification/review/audit work.

### Review-code readiness signal

For `.tasks/<feature>/reviews/review-code-state.json`:

- `missing` — no readiness state.
- `ready_for_audit` — file parses, records the expected feature with `mode: "pipeline"`, `state: "ready_for_audit"`, empty `findings.open_serious`, and true `closure_status.ready_for_audit` plus `closure_status.proofs_and_reports_fresh`.
- `not ready` — state says not ready, proof/report freshness is false, or open serious findings remain.
- `stale/unknown` — state is malformed, for another feature, or not state-bound enough for dashboard confidence.

Dashboard display does not validate semantic readiness. Audit may run with review-code context `none`; final merge/readiness remains blocked until review-code readiness and audit PASS are clean for the same integrated state.

## Final Mechanical Check

If the user asks for final readiness, run `sliceproof.py validate-final` only as a read-only mechanical check and label it:

- `final mechanical PASS` — all helper mechanics passed, including report binding checks implemented by the helper;
- `final mechanical FAIL` — helper reported missing/invalid mechanics;
- `not final-ready by dashboard alone` — always include this note.

## Edge Cases

- No `.tasks/`: `No planned-feature registries found.`
- Specific feature missing: list available feature slugs and closest obvious match if any.
- Unsafe path or invalid registry: show failure and do not derive progress.
- Missing package/proof/report path: show warning; do not infer ownership or readiness.
- User asks to mutate status: stop and explain dashboard is read-only; use the implementation/repair workflow for lifecycle changes.

## Footer

Always include:

```text
Dashboard signals are mechanical routing signals only; they are not semantic proof and do not replace package verification, review-code, or audit.
```
