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

Translate completed requirements discussion into `.tasks/<feature-name>/SPEC.md` and `.tasks/<feature-name>/tasks.json`. Execute as the main agent; do not delegate the planning decision to a sub-agent because the main agent has the conversation context.

## Arguments

- `$ARGUMENTS` — Optional feature name in kebab-case. If absent, infer from discussion context.

---

## Step 1: Identify the Feature

Extract only requirements, constraints, acceptance criteria, exclusions, and decisions the user stated or explicitly approved. If core requirements are missing or contradictory, ask before writing files.

Infer a short descriptive feature name from discussion context. Use `$ARGUMENTS` directly when provided. Ask for a name only when multiple unrelated features make inference genuinely ambiguous.

Validate the feature name before using it in paths or branch names:
- Must match `^[a-z0-9][a-z0-9-]*$`.
- Reject path traversal (`../`), shell metacharacters, spaces, and uppercase characters.
- If `.tasks/<feature-name>/` already exists, ask whether to overwrite or pick a different name.

## Step 2: Load Planning Quality References

Read these now, before creating artifacts:
- `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/work-packages.md` — work-package granularity, grouping, dependencies, parallel safety, risk metadata, and targeted review rules.
- `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/clean-code-rules.md` — Development Quality Contract used as a planning lens.

Use them to shape task boundaries, acceptance criteria, verification commands, work packages, and design decisions. Do not paste generic quality rules into every task; encode only feature-specific risks that materially affect the plan and can be observed or verified.

During planning, surface foreseeable risks where relevant: caller contracts and public API compatibility; trust-boundary validation; success, failure, partial-success, and invalid-input behavior; migration, rollback, and idempotency; verification tied to acceptance criteria; module/dependency boundaries; performance or concurrency implications; and work-package boundaries that avoid unnecessary coupling or oversized edits.

## Step 3: Run Design Preflight When Triggered

Read `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/design-preflight.md`. Before creating `.tasks/<feature-name>/` or writing files, decide whether Design Preflight is triggered by nontrivial or risky planning. Skip only for straightforward, low-risk plans.

When preflight runs:
- Create an ephemeral, neutral Preflight Brief from user-stated requirements, verified code references, any proposed approach under consideration, and open assumptions.
- Do not persist the brief under `.tasks/`, include it in `SPEC.md`, or write it as a durable project file.
- Preflight challengers are read-only sub-agents. Give them only the brief plus bounded code references needed for their rubric. They must not edit files, spawn agents, ask the user, or write final JSON.
- Treat challenger findings as evidence, not commands.

Resolve every unresolved `MUST_DECIDE` or `BLOCKERS` finding before writing `SPEC.md` or `tasks.json`. Resolution may be user clarification, a planner decision recorded in `design_decisions`, or a scoped plan change. If resolution changes user-visible semantics or acceptance criteria, ask the user before writing files.

## Step 4: Run Conditional Empirical Spike When Needed

After preflight resolution, or after deciding preflight is not triggered, check for assumptions that cannot be resolved through repo/docs inspection and materially affect task shape, acceptance criteria, architecture, sequencing, risk, or feasibility.

Invoke `spike-to-plan` before creating `.tasks/<feature-name>/` or writing files only when empirical evidence is required. Appropriate triggers include uncertain API/library behavior, unknown feasibility, unclear integration path, performance or concurrency risk, risky UX/data-model choices, or multiple viable designs where repo inspection is insufficient.

Treat spike output as planning evidence only. Do not persist spike code in the planned feature. Record accepted spike outcomes as `design_decisions` in `tasks.json`; keep `SPEC.md` requirements-only.

If validating the assumption would require broad or invasive production changes, external access, irreversible side effects, or unavailable credentials, stop and ask the user instead of writing tasks around unverified assumptions.

## Step 5: Load Artifact Authoring References

Do not write files until all triggered Design Preflight and spike gates are resolved.

Load only the references needed for the artifact you are about to draft:
- `${SUPER_DEVELOPER_PLUGIN_ROOT}/skills/implementation-plan/references/spec-template.md` — SPEC.md structure plus source/purity rules.
- `${SUPER_DEVELOPER_PLUGIN_ROOT}/skills/implementation-plan/references/tasks-json-authoring.md` — tasks.json example shape, design decisions, context bundles, task substance, acceptance criteria, and work-package authoring.
- `${SUPER_DEVELOPER_PLUGIN_ROOT}/skills/implementation-plan/references/schema-reference.md` — concise human schema map; `validate-tasks-json.py` remains the machine source of truth.

## Step 6: Draft SPEC.md

`SPEC.md` is a concise requirements specification, not an architecture brief and not an implementation plan.

Inline invariants:
- Normative product content may include only requirements, constraints, acceptance criteria, and exclusions stated or explicitly approved by the user.
- Code References are non-normative and may include only verified path-level references from lightweight codebase inspection.
- Do not invent product behavior, architecture, or non-functional requirements to make the spec feel complete.
- If a needed requirement is ambiguous, ask before writing files.
- Redact secrets, credentials, tokens, PII, and proprietary sensitive values.
- Do not include code snippets, pseudo-code, line numbers, task breakdowns, implementation sequencing, architecture rationale, or design decisions unless the user explicitly made them product requirements.
- Use requirement/acceptance IDs so `tasks.json` can trace to the spec.

Use `spec-template.md` for the exact template and detailed purity rules.

## Step 7: Draft tasks.json

Create `tasks.json` with schema version 2, top-level `design_decisions`, `context_bundles`, `work_packages`, and `phases`. Use `tasks-json-authoring.md` for the example shape and authoring rules. Use `schema-reference.md` for a human schema map, and defer machine-owned details to `${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py`.

Planning invariants:
- Keep `SPEC.md` requirements-only; task decomposition and design rationale belong in `tasks.json`.
- Persist accepted preflight, spike, or planner decisions as concise `design_decisions`; do not persist reviewer debate or the Preflight Brief.
- Record only feature-specific execution constraints or replan triggers that would invalidate the plan if violated; do not add boilerplate sections, generic stop conditions, or quality-rule copies to `tasks.json`.
- Every SPEC `REQ-*` and `AC-*` must be covered by task acceptance criteria.
- Task acceptance criteria are objects with stable IDs, observable criteria, typed source refs, and verification hints when proof depends on non-obvious context.
- Every task must have a self-contained, verifiable outcome; merge tasks that are merely mechanical steps toward another task.
- Work packages are required for every plan and are the implementation delegation unit; tasks remain the tracking and acceptance-criteria unit.
- Use controlled risk tags and targeted-review semantics from `validate-tasks-json.py` and `work-packages.md`; do not maintain a competing taxonomy in the plan text.

## Step 8: Pre-Write Validation

Before creating `.tasks/<feature-name>/` or writing files, load `${SUPER_DEVELOPER_PLUGIN_ROOT}/skills/implementation-plan/references/validation-checklist.md` and run its pre-write checklist.

Minimum inline gate:
- All triggered Design Preflight `MUST_DECIDE` and `BLOCKERS` findings are resolved.
- Any required spike evidence is accepted or the user resolved the uncertainty.
- `SPEC.md` contains only sourced requirements content and verified path-only Code References.
- `tasks.json` covers all SPEC IDs, has no circular dependencies, and uses valid references for tasks, work packages, design decisions, and context bundles.

## Step 9: Write Files and Validate tasks.json

Only after the Step 8 gate passes:

1. Create `.tasks/<feature-name>/`.
2. Write `SPEC.md`.
3. Write `tasks.json` using pretty-printed JSON with 2-space indentation.
4. Execute the shared validator against the concrete file path:

   ```bash
   python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" ".tasks/<feature-name>/tasks.json"
   ```

If the validator exits non-zero, fix `tasks.json` and rerun the same command until it passes. Do not present the plan summary with an invalid `tasks.json`.

After the validator passes, run the post-write checklist in `validation-checklist.md`.

## Step 10: Present Summary

Display:
1. Feature name and path.
2. Phase-by-phase task listing: ID, title, dependencies.
3. Any assumptions that should be verified.

---

## Pipeline Continuation

If this stage failed or requires user intervention, STOP. Do not invoke the next stage.

If blanket approval was given (for example, "proceed through all stages", "run end to end", "do everything"), invoke immediately. Otherwise, state: "Plan created for `<feature-name>`." Wait for user confirmation. Then invoke:

Use the Skill tool with: skill: "review-plan", args: "<feature-name>"

Do NOT attempt to execute the next skill's logic inline. The Skill tool loads it properly.
