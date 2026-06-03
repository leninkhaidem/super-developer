---
name: tasks
description: >
  This skill should be used when the user asks to "show tasks", "task status", "show progress",
  "task dashboard", "what's the status", "list tasks", "check progress", "mark task as done",
  or wants to view or modify the status of implementation tasks. Triggers on phrases like "tasks",
  "status", "progress", "dashboard", "show me the plan status", "what's left to do".
---

# Tasks: Implementation Status Dashboard

Display current status of planned-feature task artifacts. The dashboard is orchestration/bookkeeping only: it helps users see registry status, package paths, dependency readiness, and proof-file mechanical state, but it never proves implementation correctness or replaces implement/review/audit gates.

## Arguments

- `$ARGUMENTS` — Feature name (optional). If omitted, show all features.

## Common Rules

1. Read `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/tool-usage.md` before invoking helper scripts.
2. For any `.tasks/<feature>/tasks.json`, read only `schema_version` first to select the helper; do not trust the remaining plan data until the matching helper passes.
3. Schema-version-4 plans use the Slice-first helper:

   ```bash
   python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-plan ".tasks/<feature>/tasks.json"
   ```

4. Legacy schema-version-2/3 plans use the JSON validator:

   ```bash
   python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" ".tasks/<feature>/tasks.json"
   ```

5. If validation fails, show the feature as invalid with the helper failure summary and skip derived readiness/progress calculations for that file.
6. Treat helper output as mechanical state only. A valid registry, package assignment, dashboard status, proof `PASS`, or `sliceproof.py validate-proof` success is not semantic proof that implementation satisfies the Slice; package verification, final code review, and final audit own that judgment.

## All Features View (no argument)

1. Scan `.tasks/` for feature subdirectories.
2. Apply the common helper-selection rules to each feature.
3. For schema-version-4 features, read the validated lightweight registry and show: feature name/title/status, package count by registry status, progress by packages, and notes for missing/invalid package or proof mechanical state when cheaply available. Do not compute task acceptance progress from v4 registry data.
4. For legacy schema-version-2/3 features, read the validated plan and compute: feature name, title, status, total tasks, count by status, progress percentage, and the existing compact Conceptualize Slice projection-health indicator from `conceptualize.slice_coverage`.
5. Display sorted by status (`in_progress`/`in-progress` first, then `planned`/`reviewed`, then `completed`, then `on_hold`/`on-hold`). Surface incomplete Slice/proof/package signals in Notes, but do not claim proof from dashboard status:

```text
Task Status Dashboard
═════════════════════════════════════════════════════════════════
Feature              Mode   Status       Progress        Breakdown              Notes
────────────────────────────────────────────────────────────────────────────────────
auth-system          v4     in_progress  ████░░░░ 2/5    ✅2 🔄1 ⬜2             proofs: 2 pass, 1 missing
search-indexing      v3     reviewed     ░░░░░░░░ 0/18   ⬜18                  ⚠ slices incomplete
payment-flow         v4     completed    ████████ 4/4    ✅4                   final: mechanical pass
```

## Single Feature View (argument provided)

Apply the common helper-selection rules, then use the matching view below.

### Schema-Version-4 Slice-First View

1. Read `.tasks/$ARGUMENTS/tasks.json` as a lightweight registry only.
2. Read each package Markdown file referenced by `work_packages[].path` for package title/scope display only; the package Markdown remains the assignment artifact, not proof of completion.
3. For each package, display these dashboard signals:
   - package ID/title;
   - registry `status`;
   - package Markdown path;
   - proof Markdown path from `work_packages[].proof_path`;
   - dependency readiness from `depends_on` registry statuses only;
   - proof Markdown mechanical state.
4. Proof Markdown mechanical state may be reported as:
   - `not-created` — proof path is absent;
   - `mechanically PASS` — `sliceproof.py validate-proof` exits 0;
   - `mechanically incomplete/invalid` — `validate-proof` exits non-zero; show a compact error summary;
   - `not checked` — validation was not run, for example because the plan was invalid or the user requested a minimal overview.

   Command shape:

   ```bash
   python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-proof ".tasks/$ARGUMENTS/tasks.json" --package WP1
   ```

5. Show dependency readiness as a routing signal, not acceptance: a package is dashboard-ready when its registry status is `pending` and every `depends_on` package is registry `done`. If dependency proof/report signals are missing or invalid, show warnings; do not silently convert registry readiness into semantic readiness.
6. For final-readiness questions, optionally run the read-only final mechanical check and label it mechanical only:

   ```bash
   python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-final ".tasks/$ARGUMENTS/tasks.json"
   ```

7. Example v4 view:

```text
Feature: <title> (<status>) — schema v4
Package progress: <done>/<total> by registry status
═════════════════════════════════════════════════════════════════

Work Packages
  ✅ WP1  Backend contract
      package: .tasks/<feature>/packages/WP1.md
      proof:   .tasks/<feature>/proofs/WP1.proof.md (mechanically PASS)
      deps:    none
  ⬜ WP2  UI integration
      package: .tasks/<feature>/packages/WP2.md
      proof:   .tasks/<feature>/proofs/WP2.proof.md (not-created)
      deps:    WP1 (registry done) → dashboard-ready
```

8. At the bottom, show:
   - **Registry health** — `validate-plan` pass/fail and package count by registry status.
   - **Proof mechanical health** — proof path exists/missing plus `validate-proof` or `validate-final` result when run. State that this is not semantic proof.
   - **Dependency readiness** — next pending package whose package dependencies are registry `done`; list interrupted `in_progress` packages separately rather than redispatching them.
   - **Blocked packages** — packages with registry `blocked` and any visible reason field when present.
   - **Authority note** — package Markdown owns assignment, proof Markdown owns closure evidence, and review/audit own evidence sufficiency.

### Legacy Schema-Version-2/3 View

1. Read the validated legacy `tasks.json`.
2. Compute **Slice coverage health** from visible top-level `conceptualize.slice_coverage` fields only: `zero_slices`, `covered`, incomplete/stale-looking, or absent/legacy/unknown. This is a dashboard signal only, never proof that Slice-derived requirements were implemented.
3. If legacy `work_packages` exists, display a package summary before the phase breakdown. Package status is derived from contained task statuses:
   - ✅ all tasks `done` or `skipped`;
   - 🚫 any contained task `blocked`;
   - 🔄 any contained task `in-progress`;
   - ⬜ otherwise.
4. Display phase-by-phase task breakdown:

```text
Feature: <title> (<status>)
Progress: <done>/<total> (<percentage>%)
═════════════════════════════════════════════════════════════════

Phase 1: <phase name>
  ✅ P1-T001  Create user model
  ✅ P1-T002  Add email validation
  🔄 P1-T003  Implement password hashing          ← current
  ⬜ P1-T004  Create login endpoint                deps: P1-T003
```

5. At the bottom, show legacy signals:
   - **Evidence health** — whether legacy `.tasks/$ARGUMENTS/proofs/WP<N>.proof.json` files exist, validate, and are lifecycle-accepted for completed package criteria. Do not treat missing, invalid, stale, reopened/unaccepted, `failed`, `blocked`, or unapproved `manual_required` proof entries as verified work.
   - **Slice coverage health** — absent, zero-slices, covered, or incomplete/stale-looking coverage summary.
   - **Next actionable task** — first `pending` task with all dependencies `done`.
   - **Next actionable work package** — first package with pending work whose legacy dependencies are done and whose package evidence is not visibly invalid. Show interrupted `in-progress` packages separately.
   - **Blocked tasks** — with `blocked_reason` if present.

## Status Icons

| Status | Icon |
|---|---|
| `pending` | ⬜ |
| `in_progress` / `in-progress` | 🔄 |
| `done` | ✅ |
| `blocked` | 🚫 |
| `skipped` | ⏭️ |

## Modifying Status

Only modify status when the user explicitly requests a status override. Always warn that status mutation does not create proof evidence and cannot bypass implementation, package verification, review-code, or audit gates.

Schema-version-4:
- Modify only `work_packages[].status` bookkeeping when explicitly requested.
- Do not edit package Markdown, proof Markdown, package verification reports, Slice files, or other generated planning artifacts from the dashboard.
- Do not mark a v4 package `done` merely because `validate-proof` passes; the implement workflow owns completion after proof validation, package verification, repair/delta closure, and final gates.
- Do not mark the feature `completed` unless explicitly requested and clearly label it a registry/status override, not final readiness.

Legacy schema-version-2/3:
- **Marking `done`:** Update task status and add `completed_at` with current ISO 8601 timestamp only when explicitly requested. Warn that this does not create verification evidence and that implement/audit gates still require valid accepted package proof entries.
- **Marking `blocked`:** Ask for a `blocked_reason` and add it to the task.
- **Marking `skipped`:** Ask for confirmation first.
- **All tasks `done` or `skipped`:** Update feature `status` to `completed` only as a requested status override.

## Edge Cases

- `.tasks/` does not exist or is empty: "No task plans found. Start a planning session to create one."
- Specific feature directory does not exist: list available features and suggest the closest match.
- `tasks.json` is unreadable or lacks `schema_version`: show `invalid/unknown schema` and do not derive progress.
- Schema-version-4 package/proof paths are missing or unsafe: show helper validation failure; do not infer package readiness.
