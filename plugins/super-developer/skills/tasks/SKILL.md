---
name: tasks
description: >
  Show a read-only planned-feature status dashboard. Use when the user asks for task status,
  progress, package status, dashboard, what is left, or available planned-feature work. Do not use to
  mutate registry/package/proof/report state.
---

# Tasks Dashboard

Display Slice-first planned-feature registry/package/proof/report signals without changing state or claiming semantic proof.

## Always

- Dashboard is read-only: never edit `tasks.json`, package Markdown, proof Markdown, reports, Slices, review state, commits, or lifecycle status.
- Treat registry status, dependency readiness, helper output, proof rows, and report labels as mechanical signals only.
- Package verification, review-code, and audit own evidence sufficiency and final readiness.
- Use `sliceproof.py` checks only through `../../references/tool-usage.md`; helper success is not implementation proof.

## Do

1. Resolve optional feature argument. If omitted, scan `.tasks/*/tasks.json` for all-feature overview.
2. Load `references/dashboard-display.md` for display rules and signal labels.
3. Load `../../references/tool-usage.md` before running any helper command.
4. Validate each candidate registry with:

   ```bash
   python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-plan ".tasks/<feature>/tasks.json"
   ```

5. If validation fails, show `invalid` with a compact helper summary and do not infer package/proof/report readiness.
6. For valid features, read registry bookkeeping plus declared package/proof/report paths for display only.
7. For a single feature, optionally run read-only proof/final checks when useful for the requested detail level:

   ```bash
   python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-proof ".tasks/<feature>/tasks.json" --package WP1
   python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-final ".tasks/<feature>/tasks.json"
   ```

8. Report package statuses, dependency readiness, proof mechanical state, report signal, review-code readiness signal when present, and blockers/unknowns.

## Load if needed

- Detailed display rules, icons, proof/report labels, and output sections → `references/dashboard-display.md`.
- Helper commands and command-safety rules → `../../references/tool-usage.md`.
- Package lifecycle semantics for explaining non-bypass/freshness → `../../references/package-lifecycle.md`.

## Stop if

- The user asks the dashboard to mark work done, override statuses, edit proof/report files, or bypass implement/review/audit gates.
- A registry path is unsafe, unreadable, or invalid.
- A helper command would be destructive, externally visible, credentialed, network-sensitive, dependency-installing, or out of dashboard scope.

## Output

Return a compact dashboard with:

- feature title/status;
- package counts and next dependency-ready packages;
- per-package path/proof/report mechanical signals;
- invalid or missing artifact warnings;
- clear note: `Dashboard signals are not semantic proof and do not replace package verification, review-code, or audit.`
