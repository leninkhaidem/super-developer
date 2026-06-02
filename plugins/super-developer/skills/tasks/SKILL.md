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
2. Read `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/tool-usage.md` before invoking helper scripts.
3. For each feature, execute the shared validator before reading `tasks.json`:

   ```bash
   python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" ".tasks/<feature>/tasks.json"
   ```

   If validation fails for a feature, display it as invalid with the validator failure summary and skip derived progress calculations for that file.
4. For each valid feature, read `tasks.json` and compute: feature name, title, status, total tasks, count by status, progress percentage, and a compact Conceptualize Slice projection-health indicator (`ok`, `zero-slices`, `absent/legacy`, or `⚠ incomplete`) from `conceptualize.slice_coverage`. This is a signal only; detailed Slice authority rules live in `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/conceptualize-slice-authority.md`.
5. Display sorted by status (`in-progress` first, then `planned`/`reviewed`, then `completed`, then `on-hold`). Surface `⚠ incomplete` or absent coverage in the Notes column, but do not claim implementation proof from dashboard status:

```
Task Status Dashboard
═════════════════════════════════════════════════════════════════
Feature              Status       Progress        Breakdown             Notes
───────────────────────────────────────────────────────────────────────────────
auth-system          in-progress  ████░░░░ 12/24  ✅12 🔄1 ⬜9 🚫2      slices: ok
search-indexing      reviewed     ░░░░░░░░  0/18  ⬜18                 ⚠ slices incomplete
payment-flow         completed    ████████  8/8   ✅8                  slices: zero
```

## Single Feature View (argument provided)

1. Read `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/tool-usage.md` before invoking helper scripts.
2. Execute the shared validator before reading `tasks.json`:

   ```bash
   python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" ".tasks/$ARGUMENTS/tasks.json"
   ```

   If validation fails, show the validator output and stop; the dashboard cannot reliably compute status from an invalid plan.

   If package proofs are missing, invalid, stale, reopened, or unaccepted, continue showing task status but include an **Evidence: missing/invalid/unaccepted** warning. Status alone is not proof that completed acceptance criteria are verified.
3. Read `.tasks/$ARGUMENTS/tasks.json`.
4. Compute **Slice coverage health** from visible top-level `conceptualize.slice_coverage` fields only: `zero_slices`, `covered`, incomplete/stale-looking, or absent/legacy/unknown. Show entry/disposition counts and obvious schema-level warnings such as missing projected refs, missing rationale, visible approval gaps, suspicious `informational`, or package-assignment inconsistency. This is a dashboard signal only, never proof that Slice-derived requirements were implemented. Review-plan and audit remain the authoritative coverage/proof gates; load `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/conceptualize-slice-authority.md` for canonical rules.
5. If `work_packages` exists, display a package summary before the phase breakdown:

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

6. Display phase-by-phase breakdown:

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

7. At the bottom, show:
   - **Evidence health** — for planned-feature pipelines, whether `.tasks/$ARGUMENTS/proofs/WP<N>.proof.json` files exist, validate, and are accepted for completed package criteria. Do not treat missing, invalid, stale, reopened/unaccepted, `failed`, `blocked`, or unapproved `manual_required` proof entries as verified work.
   - **Slice coverage health** — absent, zero-slices, covered, or incomplete/stale-looking coverage summary. Warn on absent, empty-without-zero-state, incomplete, package-inconsistent coverage, suspicious `informational` dispositions, or missing projected refs/approval metadata, and state that status is not proof of Slice-derived implementation outcomes.
   - **Next actionable task** — first `pending` task with all dependencies `done`.
   - **Next actionable work package** — first package with pending work whose package dependencies have accepted proof evidence and whose external task dependencies are done. Show interrupted `in-progress` packages separately rather than redispatching them. Show this only when `work_packages` exists.
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

- **Marking `done`:** Update status and add `completed_at` with current ISO 8601 timestamp only when the user explicitly requests a status override. Warn that this does not create verification evidence and that audit/implement gates still require accepted package proof entries.
- **Marking `blocked`:** Ask for a `blocked_reason` and add it to the task.
- **Marking `skipped`:** Ask for confirmation first.
- **All tasks `done` or `skipped`:** Update feature `status` to `completed`.

Work package status is derived from task statuses. Do not directly mark a work package done; update the contained task statuses instead.

## Edge Cases

- `.tasks/` does not exist or is empty: "No task plans found. Start a planning session to create one."
- Specific feature directory does not exist: List available features and suggest the closest match.
