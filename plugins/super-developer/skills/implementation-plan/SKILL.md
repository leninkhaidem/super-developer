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

Translate a completed brainstorming or requirements discussion into a structured, agent-executable task plan. Produces a feature directory under `.tasks/` containing a requirements specification (`SPEC.md`) and a JSON task file.

Execute this directly as the main agent — do not delegate to a sub-agent. The main agent has the conversation context needed to create the plan.

## Arguments

- `$ARGUMENTS` — Optional feature name in kebab-case (e.g., `auth-system`). If not provided, infer from the discussion context.

---

## Step 1: Identify the Feature

Review the full conversation history from this session. Extract only requirements, constraints, acceptance criteria, and out-of-scope decisions that the user stated or approved. If core requirements are missing or contradictory, ask for clarification before writing files. Determine a short, descriptive kebab-case name (e.g., `user-auth`, `api-redesign`, `search-indexing`).

**Infer the feature name from the discussion context.** Do not ask the user for a name unless the conversation is genuinely ambiguous with multiple unrelated features discussed. If `$ARGUMENTS` is provided, use that directly.

**Validate the feature name:** Ensure it matches `^[a-z0-9][a-z0-9-]*$` (lowercase alphanumeric and hyphens only). Reject names containing path traversal sequences (`../`), shell metacharacters, or spaces. This name is used in filesystem paths and git branch names.

If `.tasks/<feature-name>/` already exists, ask whether to overwrite or pick a different name.

## Step 2: Create Directory Structure

```
.tasks/<feature-name>/
├── SPEC.md
└── tasks.json
```

## Step 3: Generate SPEC.md

SPEC.md is a **concise requirements specification** — not an architecture brief and not an implementation plan. It is the source of truth for WHAT the user wants, how success is judged, and what is excluded. All task decomposition and implementation detail belongs in tasks.json or in the codebase exploration done during implementation.

**Requirement source rule:** For normative product content, include only requirements, constraints, acceptance criteria, and exclusions stated or explicitly approved by the user in the prior discussion. Code References are non-normative and may include only verified path-level references from lightweight codebase inspection. Do not invent product behavior, architecture, or non-functional requirements to make the spec feel complete. If a needed requirement is ambiguous, ask before writing files.

Structure:

```markdown
# <Feature Name — Human Readable> Specification

## Overview
1-2 sentences: user goal and intended outcome.

## Requirements
User-facing functional requirements. Use stable IDs for traceability.
- REQ-1: ...
- REQ-2: ...

## Acceptance Criteria
Feature-level, user-visible outcomes. Use stable IDs; prefer Given/When/Then when useful.
- AC-1: ...
- AC-2: ...

## Constraints
Non-negotiable user-stated constraints: compatibility, security, performance, policy, timing.

## Code References
Verified existing files/modules to inspect. Reference paths only; no code excerpts or change instructions. Use `None identified` when no safe references are known.
- `path/to/file`: why it is relevant.

## Out of Scope
User-stated exclusions and boundaries.
```

Rules:
- Keep concise, but never omit a user-stated requirement to satisfy brevity.
- Redact secrets, credentials, tokens, PII, and proprietary sensitive values; use placeholders and describe the requirement without persisting raw sensitive data.
- SPEC.md may reference file paths, APIs, or existing modules, but must not include code snippets, pseudo-code, line numbers, or instructions for how to change code.
- Include Code References only after lightweight codebase inspection verifies the paths. If no relevant paths are known, write `None identified`.
- Do not include architecture/design decisions unless the user explicitly made them a requirement.
- Do not include task breakdowns or implementation sequencing.
- Use requirement/acceptance IDs so tasks.json can trace to the spec without duplicating whole sections.

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
          "description": "WHAT to build and key constraints. References affected files/modules. Includes non-discoverable constraints. Does NOT prescribe exact code or implementation steps.",
          "status": "pending",
          "dependencies": [],
          "acceptance_criteria": [
            "Specific, verifiable criterion"
          ],
          "context": "Why this task exists — the SPEC.md requirement or acceptance criterion that motivated it"
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

- **Descriptions state WHAT to build, not HOW to code it.** Reference affected files and modules so the agent knows where to work. Include constraints that aren't discoverable from the codebase — external API contracts, security policies, performance bounds, requirements confirmed during planning. The implementing agent derives the actual code from codebase exploration.
- **"Discoverable" means:** exists in SPEC.md, the referenced files, or their immediate imports. If an agent reading those files would find it, don't repeat it in the description.
- **Anchor patterns, don't prescribe code.** When a task should follow an existing pattern, reference it: "Follow middleware pattern in `src/middleware/cors.ts`." The agent explores, finds the pattern, follows it.
- **Description budget:** Target 200-400 characters. Descriptions exceeding 600 characters likely contain implementation prescriptions — review and trim.
- The `description` field covers WHAT + constraints. The `context` field covers WHY — one or two sentences linking back to a SPEC.md requirement or acceptance criterion. Don't mix them.
- Each task: scoped for a single focused agent session.
- Group tasks into phases that deliver a testable increment.
- Dependencies must not be circular. Tasks in phase N may depend on tasks in phases 1..N only.
- Task IDs must be unique across all phases.

#### Description Anti-Patterns

Do not include in task descriptions:
- Exact code snippets or function bodies
- Line number references (fragile, become stale)
- Step-by-step implementation instructions
- Library or parser choices (unless security-mandated — see acceptance criteria guidance below)
- Defensive coding prescriptions the agent should already know

When deviating from these guidelines for a legitimate reason (external API contract, complex migration ordering), note the justification in the task's `context` field.

#### Reference Example

```
✅ INTENT-DRIVEN (285 chars):
"Implement JWT authentication middleware protecting all `/api/*` routes.
Reject invalid/missing tokens with 401. Attach decoded user identity to
request context. Add rate limiting (100 req/15min/IP). Follow existing
middleware pattern in `src/middleware/cors.ts`."
```

#### Acceptance Criteria Guidance

Criteria must describe **verifiable outcomes**, not implementation details:
- ✅ "Returns empty list on any network or parse error" (behavioral)
- ✅ "XML parsing is safe against XXE attacks (use defusedxml or equivalent)" (security outcome with verification hint)
- ✅ "Response latency ≤200ms at p95 under 100 concurrent requests" (measurable)
- ❌ "Uses `express-rate-limit` library" (implementation prescription)
- ❌ "Parser tries lxml first, falls back to html.parser" (internal implementation detail)

**Security-mandated specifics are acceptable.** When a security outcome requires a specific implementation (XXE-safe parser, bcrypt over MD5, parameterized queries), name it in the criterion as a verification hint — this is a security constraint, not an implementation detail.

### Task Substance Rule

Each task must have a **self-contained, verifiable outcome** — a change that is independently meaningful when described in one sentence.

**Merge tasks that lack standalone intent.** If a task is only a mechanical step toward another task's goal (adding an import, creating a type alias, updating a config key), it is usually not a task — it is part of the task that needs that change. Fold it into the task that gives it meaning, unless the integration step itself has independent acceptance criteria (e.g., configuring a DI container registration that requires specific binding rules).

**Independence test:** For each candidate task, ask: *"Can a reviewer verify this task's acceptance criteria without seeing any other task?"* If the answer is no, the task is too thin — merge it with the task it serves.

**Description quality test:** For each task, ask: *"Does this description tell the agent WHAT to achieve, or HOW to code it?"* If it reads like a code tutorial, trim to intent + constraints.

Examples of tasks that **fail** this test and should be merged:
- "Add import for `UserService`" → merge into the task that uses `UserService`
- "Create empty migration file" → merge into the task that defines the migration
- "Add route constant" → merge into the task that implements the route handler

Examples of tasks that **pass** despite being small:
- "Add rate-limiting middleware to auth endpoints" (3 lines, but independently verifiable and meaningful)
- "Configure CORS policy for the new API namespace" (small, but self-contained security concern)

## Step 5: Validate

Before writing files, verify:

- SPEC.md contains all user-stated requirements, acceptance criteria, constraints, and out-of-scope items from the discussion
- SPEC.md contains no raw secrets, credentials, tokens, PII, or proprietary sensitive values
- SPEC.md contains no implementation details, code snippets, pseudo-code, line numbers, or task breakdowns
- SPEC.md Code References are verified path-only references or `None identified`
- No unnecessary verbatim duplication between SPEC.md and tasks.json; tasks should trace to spec IDs while adding task-level verification detail
- No circular dependencies
- All dependency references point to valid task IDs
- Every task has at least one acceptance criterion
- Every task passes the independence test (self-contained, verifiable outcome)
- Every task passes the description quality test (intent + constraints, not implementation tutorial)
- Phase order is sequential with no gaps
- Task IDs are unique across all phases

## Step 6: Write Files

1. Create `.tasks/<feature-name>/` directory.
2. Write `SPEC.md`.
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
