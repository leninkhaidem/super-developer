---
name: implementation-plan
description: >
  Creates structured implementation task plans from discussions and requirements. Use this skill
  whenever the user wants to turn a brainstorming session, design discussion, or feature request
  into a structured task breakdown with dependencies. Triggers on "create an implementation plan",
  "plan this feature", "break this down into tasks", "write implementation tasks", "structure
  this into tasks", "convert to implementation plan", "task breakdown". Also trigger when the user
  says "plan this" or "create tasks" in the context of building or implementing something — this
  skill handles the planning-to-execution bridge, not general-purpose planning.
---

# Plan: Convert Discussion to Structured Implementation Tasks

Translate the current brainstorming or research session into a structured, agent-executable task plan. Produces a feature directory under `.tasks/` containing a self-contained context document and a JSON task file.

Execute this directly as the main agent — do not delegate to a sub-agent. The main agent has the conversation context needed to create the plan.

## Arguments

- `$ARGUMENTS` — Optional feature name in kebab-case (e.g., `auth-system`). If not provided, infer from the discussion context.

---

## Step 1: Identify the Feature

Review the full conversation history from this session. Determine a short, descriptive kebab-case name (e.g., `user-auth`, `api-redesign`, `search-indexing`).

**Infer the feature name from the discussion context.** Do not ask the user for a name unless the conversation is genuinely ambiguous with multiple unrelated features discussed. If `$ARGUMENTS` is provided, use that directly.

**Validate the feature name:** Ensure it matches `^[a-z0-9][a-z0-9-]*$` (lowercase alphanumeric and hyphens only). Reject names containing path traversal sequences (`../`), shell metacharacters, or spaces. This name is used in filesystem paths and git branch names.

If `.tasks/<feature-name>/` already exists, ask whether to overwrite or pick a different name.

## Step 2: Create Directory Structure

```
.tasks/<feature-name>/
├── CONTEXT.md
└── tasks.json
```

## Step 3: Generate CONTEXT.md

CONTEXT.md is a **concise architectural brief** — not a detailed spec. It answers "what are we building and why" so a sub-agent can orient itself. All implementation detail belongs in tasks.json.

**Hard constraint: CONTEXT.md must not exceed 50 lines.** If writing more, move implementation detail to task descriptions.

Structure:

```markdown
# <Feature Name — Human Readable>

## Overview
1-2 sentences: what we are building and why.

## Design Decisions
Key decisions with brief rationale. Include rejected alternatives to prevent re-exploration.
- Decision A: chose X over Y because Z.
- Decision B: ruled out W because V.

## Architecture
How this integrates with the existing system. Key components, entry points, relevant files.

## Constraints
Non-negotiable requirements: security, performance, compatibility.

## Out of Scope
What we explicitly excluded.
```

Rules:
- Every section: terse bullets or single sentences, not paragraphs.
- Reference specific file paths and integration points, but do not describe what to do with them (that goes in task descriptions).
- **No duplication with tasks.json.** Task-level concerns belong only in tasks.

## Step 4: Generate tasks.json

Create a JSON file following this schema:

```json
{
  "feature": "<feature-name>",
  "title": "Human-readable feature title",
  "description": "One-line summary of what this feature delivers",
  "created_at": "<ISO 8601>",
  "status": "planned",
  "phases": [
    {
      "id": "P1",
      "name": "Phase name",
      "description": "What this phase accomplishes as a unit",
      "order": 1,
      "tasks": [
        {
          "id": "P1-T001",
          "title": "Short descriptive title",
          "description": "Detailed implementation guidance. Include what to build, how, which files to touch, and technical approach. A sub-agent should execute from CONTEXT.md + this description alone.",
          "status": "pending",
          "dependencies": [],
          "acceptance_criteria": [
            "Specific, verifiable criterion"
          ],
          "context": "Why this task exists — the design decision or requirement that motivated it"
        }
      ]
    }
  ]
}
```

### Schema Reference

| Level | Field | Type | Values |
|---|---|---|---|
| Feature | `status` | string | `planned`, `reviewed`, `in-progress`, `completed`, `on-hold` |
| Feature | `created_at` | string | ISO 8601 timestamp |
| Phase | `id` | string | `P<N>` (e.g., `P1`, `P2`) |
| Phase | `order` | number | Sequential, no gaps |
| Task | `id` | string | `<PhaseID>-T<NNN>` (e.g., `P1-T001`) |
| Task | `status` | string | `pending`, `in-progress`, `done`, `blocked`, `skipped` |
| Task | `dependencies` | string[] | Task IDs within this feature |
| Task | `completed_at` | string | ISO 8601 timestamp (added when status changes to `done`) |
| Task | `blocked_reason` | string | Reason for blocking (added when status changes to `blocked`) |

### Task Authoring Guidelines

- **Tasks carry the implementation detail, not CONTEXT.md.** The task `description` must contain everything a sub-agent needs: files to create or modify, patterns to follow, specific technical instructions.
- Each task: scoped for a single focused agent session.
- Group tasks into phases that deliver a testable increment.
- The `context` field: a brief "why" — one or two sentences linking back to a design decision.
- Dependencies must not be circular. Tasks in phase N may depend on tasks in phases 1..N only.
- Task IDs must be unique across all phases.

### Task Substance Rule

Each task must have a **self-contained, verifiable outcome** — a change that is independently meaningful when described in one sentence.

**Merge tasks that lack standalone intent.** If a task is only a mechanical step toward another task's goal (adding an import, creating a type alias, updating a config key), it is usually not a task — it is part of the task that needs that change. Fold it into the task that gives it meaning, unless the integration step itself has independent acceptance criteria (e.g., configuring a DI container registration that requires specific binding rules).

**Consolidation test:** For each candidate task, ask: *"Can a reviewer verify this task's acceptance criteria without seeing any other task?"* If the answer is no, the task is too thin — merge it with the task it serves.

Examples of tasks that **fail** this test and should be merged:
- "Add import for `UserService`" → merge into the task that uses `UserService`
- "Create empty migration file" → merge into the task that defines the migration
- "Add route constant" → merge into the task that implements the route handler

Examples of tasks that **pass** despite being small:
- "Add rate-limiting middleware to auth endpoints" (3 lines, but independently verifiable and meaningful)
- "Configure CORS policy for the new API namespace" (small, but self-contained security concern)

## Step 5: Validate

Before writing files, verify:

- CONTEXT.md is under 50 lines
- No content duplicated between CONTEXT.md and tasks.json
- No circular dependencies
- All dependency references point to valid task IDs
- Every task has at least one acceptance criterion
- Every task passes the substance consolidation test (self-contained, verifiable outcome)
- Phase order is sequential with no gaps
- Task IDs are unique across all phases

## Step 6: Write Files

1. Create `.tasks/<feature-name>/` directory.
2. Write `CONTEXT.md`.
3. Write `tasks.json` (pretty-printed, 2-space indentation).

## Step 7: Present Summary

Display:
1. Feature name and path
2. Phase-by-phase task listing (ID, title, dependencies)
3. Any assumptions that should be verified

---

## Pipeline Continuation

If this stage failed or requires user intervention, STOP. Do not invoke the next stage.

If blanket approval was given (e.g., "proceed through all stages", "run end to end", "do everything"), invoke immediately. Otherwise, state: "Plan created for `<feature-name>`." Wait for user confirmation. Then invoke:

Use the Skill tool with: skill: "review-plan", args: "<feature-name>"

Do NOT attempt to execute the next skill's logic inline. The Skill tool loads it properly.
