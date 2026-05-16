---
name: tasks
description: >
  This skill should be used when the user asks to "show tasks", "task status", "show progress",
  "task dashboard", "what's the status", "list tasks", "check progress", "mark task as done",
  or wants to view or modify the status of implementation tasks. Triggers on phrases like "tasks",
  "status", "progress", "dashboard", "show me the plan status", "what's left to do".
---

# Tasks: Implementation Status Dashboard

Display current status of task plans. Quick overview of progress across all features or detailed view for a specific one. Also supports modifying task status on explicit request. Prefer `taskctl.py` for proof-backed lifecycle reads/mutations that it supports; manual overrides are allowed only when the user asks for them and they do not create package proof.

## Arguments

- `$ARGUMENTS` — Feature name (optional). If omitted, show all features.

---

## All Features View (no argument)

1. Scan `.tasks/` for subdirectories.
2. For each feature, execute the shared validator before reading `tasks.json`:

   ```bash
   python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" ".tasks/<feature>/tasks.json"
   ```

   If validation fails for a feature, display it as invalid with the validator failure summary and skip derived progress calculations for that file.
3. For each valid feature, read `tasks.json` and compute: feature name, title, status, total tasks, count by status, progress percentage.
4. Display sorted by status (`in-progress` first, then `planned`/`reviewed`, then `completed`, then `on-hold`):

```
Task Status Dashboard
═════════════════════════════════════════════════════════════════
Feature              Status       Progress        Breakdown
─────────────────────────────────────────────────────────────────
auth-system          in-progress  ████░░░░ 12/24  ✅12 🔄1 ⬜9 🚫2
search-indexing      reviewed     ░░░░░░░░  0/18  ⬜18
payment-flow         completed    ████████  8/8   ✅8
```

## Single Feature View (argument provided)

1. Execute the shared validator before reading `tasks.json`:

   ```bash
   python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" ".tasks/$ARGUMENTS/tasks.json"
   ```

   If validation fails, show the validator output and stop; the dashboard cannot reliably compute status from an invalid plan.

   If package proof files under `.tasks/$ARGUMENTS/proofs/` are missing or invalid, continue showing task status but include an **Evidence: missing/invalid** warning. Status alone is not proof that completed acceptance criteria are verified.
2. Read `.tasks/$ARGUMENTS/tasks.json`.
3. If `work_packages` exists, display a package summary before the phase breakdown:

   ```
   Work Packages
     🔄 WP1  Authentication backend flow      tasks: P1-T001, P1-T002, P1-T003
     ⬜ WP2  Login UI flow                     deps: WP1
     ✅ WP3  Documentation updates             tasks: P2-T004
   ```

   Package status is computed from contained task statuses:
   - ✅ all tasks `done` or `skipped`
   - 🚫 any contained task `blocked`
   - 🔄 any contained task `in-progress`
   - ⬜ otherwise

4. Display phase-by-phase breakdown:

```
Feature: <title> (<status>)
Progress: <done>/<total> (<percentage>%)
═════════════════════════════════════════════════════════════════

Phase 1: <phase name>
  ✅ P1-T001  Create user model
  ✅ P1-T002  Add email validation
  🔄 P1-T003  Implement password hashing          ← current
  ⬜ P1-T004  Create login endpoint                 deps: P1-T003

Phase 2: <phase name>
  🚫 P2-T001  Integrate OAuth provider              blocked: API credentials not configured
  ⬜ P2-T002  Add session management                deps: P1-T004, P2-T001
  ⬜ P2-T003  Write auth middleware                  deps: P2-T002
```

5. At the bottom, show:
   - **Evidence health** — for planned-feature pipelines, whether `.tasks/$ARGUMENTS/proofs/<WP-ID>.proof.json` files validate for completed package criteria. Use `taskctl.py --tasks ".tasks/$ARGUMENTS/tasks.json" summary` for routine proof health when available. Do not treat `failed`, `blocked`, stale, wrong-package, or unapproved `manual_required` proof entries as verified work.
   - **Next actionable task** — first `pending` task with all dependencies `done`.
   - **Next actionable work package** — first package with pending work whose package dependencies and external task dependencies are done. Prefer `taskctl.py --tasks ".tasks/$ARGUMENTS/tasks.json" next-package` when available. Show this only when `work_packages` exists.
   - **Blocked tasks** — with `blocked_reason` if present.

## Status Icons

| Status | Icon |
|---|---|
| `pending` | ⬜ |
| `in-progress` | 🔄 |
| `done` | ✅ |
| `blocked` | 🚫 |
| `skipped` | ⏭️ |

## Modifying Task Status

If the user asks to change a task's status (e.g., "mark P1-T003 as done", "block P2-T001"):

- **Proof-backed package acceptance:** In implementation workflow, use `taskctl.py accept-package <WP-ID>` only after the package proof file validates, package verification passes, and required targeted/focused review gates pass.
- **Marking `done` manually:** Update status and add `completed_at` with current ISO 8601 timestamp only when the user explicitly requests a status override. Warn that this does not create package proof and that audit/implement gates still require valid per-package proof files.
- **Marking `blocked`:** Prefer `taskctl.py block-task <task-id> --reason "<reason>"` when available. If editing manually, require a `blocked_reason` and add it to the task.
- **Resetting interrupted work:** Prefer `taskctl.py reset-task <task-id>` when returning a blocked/interrupted task to `pending`.
- **Marking `skipped`:** Ask for confirmation first.
- **All tasks `done` or `skipped`:** Do not treat feature completion as proof-backed until all package proofs validate and final review/audit gates have passed.

Work package status is derived from task statuses. Do not directly mark a work package done; update the contained task statuses instead. Manual overrides are status-only; they never write `.tasks/<feature>/proofs/<WP-ID>.proof.json`.

## Edge Cases

- `.tasks/` does not exist or is empty: "No task plans found. Start a planning session to create one."
- Specific feature directory does not exist: List available features and suggest the closest match.
