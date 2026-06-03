# Package Status and Lifecycle Boundary

Load this cold reference when a status/dashboard workflow needs package lifecycle language. Workflow runbooks own when packages may move; this reference only defines what status and helper output mean.

## V4 Slice-First Boundary

Schema-version-4 planned-feature packages use:

- `tasks.json.work_packages[]` as lightweight registry/bookkeeping;
- `.tasks/<feature>/packages/<WP-ID>.md` as the package assignment source;
- `.tasks/<feature>/proofs/<WP-ID>.proof.md` as package closure evidence;
- `.tasks/<feature>/reports/<WP-ID>.package-verification.md` as durable package verification evidence when produced by the implement workflow.

Registry `status` values such as `pending`, `in_progress`, `done`, and `blocked` are dashboard/routing signals only. `done` should be written by the implement workflow only after proof Markdown mechanically validates, verification expectations are addressed, package verification passes, repairs/delta verification are closed, and no Slice plan defect remains. Status does not prove implementation correctness and cannot bypass package verification, final code review, or final audit.

Dependency readiness shown by dashboards is also a signal: a pending package may be shown as ready when every `depends_on` package is registry `done`. If dependency proof Markdown or package verification report signals are missing, invalid, failed, or stale, surface warnings instead of treating readiness as semantic acceptance.

## V4 Helper Boundary

Use `sliceproof.py` for mechanical checks only:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-plan ".tasks/<feature>/tasks.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-proof ".tasks/<feature>/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-final ".tasks/<feature>/tasks.json"
```

`validate-plan` can support registry/package-path/dependency dashboard health. `validate-proof` and `validate-final` can support proof Markdown mechanical status. Helper success does not judge evidence sufficiency, run tests, inspect git freshness, accept/reopen packages, mutate registry status, or replace review/audit.

## Dashboard Non-Bypass Rule

A dashboard may report:

- package registry status;
- package/proof/report paths;
- dependency readiness from registry dependencies;
- proof Markdown existence and mechanical validation state;
- blocked or interrupted package signals.

A dashboard must not present package assignment, status output, helper validation, proof `PASS` rows, or manually edited files as semantic implementation proof. Missing/invalid proof Markdown, failed helper validation, blocked status, unresolved proof markers, missing package verification reports, or stale-looking evidence are warnings/blockers for workflow gates, not facts the dashboard resolves.

## Legacy Compatibility Boundary

Schema-version-2/3 plans may still use legacy JSON proof lifecycle commands documented in `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/tool-usage.md`, including `taskctl.py accept-package`, `reopen-package`, `record-targeted-review`, and `refresh-proof-state`. Keep those commands in the legacy path only. Do not use legacy `.proof.json` lifecycle state, targeted-review receipts, or accept/reopen commands to satisfy v4 Markdown proof closure.
