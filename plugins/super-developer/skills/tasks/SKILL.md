---
name: tasks
description: >
  This skill should be used when the user asks to "show tasks", "task status", "show progress",
  "task dashboard", "what's the status", "list tasks", "check progress", "mark task as done",
  or wants to view or modify the status of implementation tasks. Triggers on phrases like "tasks",
  "status", "progress", "dashboard", "show me the plan status", "what's left to do".
---

# Tasks: Implementation Status Dashboard

Display current status of task plans. Quick overview of progress across all features or detailed view for a specific one. Also supports modifying task status on request.

## Arguments

- `$ARGUMENTS` — Feature name (optional). If omitted, show all features.

---

## All Features View (no argument)

1. Scan `.tasks/` for subdirectories.
2. For each feature, read `tasks.json` and compute: feature name, title, status, total tasks, count by status, progress percentage.
3. Display sorted by status (`in-progress` first, then `planned`/`reviewed`, then `completed`, then `on-hold`):

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

1. Read `.tasks/$ARGUMENTS/tasks.json`.
2. If `work_packages` exists, display a package summary before the phase breakdown:

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

3. Display phase-by-phase breakdown:

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

4. At the bottom, show:
   - **Next actionable task** — first `pending` task with all dependencies `done`.
   - **Next actionable work package** — first package with pending work whose package dependencies and external task dependencies are done. Show this only when `work_packages` exists.
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

- **Marking `done`:** Update status and add `completed_at` with current ISO 8601 timestamp.
- **Marking `blocked`:** Ask for a `blocked_reason` and add it to the task.
- **Marking `skipped`:** Ask for confirmation first.
- **All tasks `done` or `skipped`:** Update feature `status` to `completed`.

Work package status is derived from task statuses. Do not directly mark a work package done; update the contained task statuses instead.

## Edge Cases

- `.tasks/` does not exist or is empty: "No task plans found. Start a planning session to create one."
- Specific feature directory does not exist: List available features and suggest the closest match.
