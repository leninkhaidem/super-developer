# Design Preflight

## Purpose

Design Preflight is a read-only adversarial planning challenge. It surfaces decisions and requirement-completeness gaps before writing `SPEC.md`, the registry, package Markdown, proof paths, or report paths.

Completeness gaps include missing observable behaviors, edge cases, failure modes, defaults, or obligations a reasonable implementer would expect.

It is not an implementation plan, persisted transcript, or instruction stream for sub-agents.

## Trigger

Run for nontrivial or risky plans, including:

- new architecture, data model, permission boundary, external integration, persistence, or generated contract behavior;
- security, privacy, safety, reliability, migration, concurrency, rollback, or destructive-action risk;
- ambiguous requirements where multiple designs could satisfy the same request;
- cross-cutting changes across skills, commands, subsystems, or generated artifacts;
- semantic tradeoffs that should be explicit before package authoring.

Skip only for narrow, mechanical, low-risk plans where the existing architecture and caller contract are clear.

## Authority Split

- Main agent: orchestration, final interpretation, user interaction, durable artifact writing, and decisions.
- Challengers: read-only evidence. They inspect bounded context and return bounded output. They do not edit files, spawn agents, ask the user, write packages, or run review-plan.

Sub-agent output is advisory. The main agent may accept, reject, combine, or reframe it, but must not silently persist unresolved semantic choices.

## Model Preferences

Before spawning challengers, resolve `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/model-preferences.md`:

- standard planning/design challengers use the `review-plan` key;
- adversarial/security/privacy/safety/failure-mode challengers use `skeptic-agent`;
- `inherit` omits the model parameter;
- `adaptive` uses the same role interpretation as plan review;
- explicit model names are passed directly.

Do not add a Design Preflight-specific model key.

## Timing and Persistence

Run before creating or editing durable planned-feature artifacts.

The Preflight Brief is ephemeral and must not be persisted under `.tasks/`.

Persist accepted outcomes only in the artifact that owns them:

- `SPEC.md` for product requirements, constraints, non-goals, acceptance summary, or approved scope/override notes;
- package Markdown for package boundaries, assigned Slice scope, sequencing, notes, dependencies, and verification expectations;
- proof Markdown expectations through package closure rows and verification expectations;
- Slice approval/deferral metadata when a Slice-derived commitment changes, narrows, or is excluded;
- registry bookkeeping only for package paths, statuses, and dependencies.

Keep `SPEC.md` requirements-focused. Do not store architecture rationale unless the user made it a requirement, constraint, or approved scope decision.

## Brief Format

```markdown
# Preflight Brief

## User Request
<verbatim or tightly summarized request, without design advocacy>

## Known Constraints
- <explicit user/repo/tool constraint>

## Current Evidence
- <observed file, command, or repo fact>

## Open Design Surface
- <area where multiple viable approaches may exist>

## Non-Goals
- <scope explicitly excluded or not implied>
```

If the main agent has a hypothesis, label it as a hypothesis under `Open Design Surface`, not as a conclusion.

## Challenger Assignment

```markdown
# Role
You are a read-only design challenger for Design Preflight.

# Inputs
- Preflight Brief: <brief text or path>
- Relevant files/context: <bounded list>
- Model preference: <resolved value; omit dispatch model parameter when inherit>

# Task
Evaluate the design surface before durable artifacts are written. Identify decisions needed for a coherent plan and surface requirement-completeness gaps: missing expected behaviors, edge cases, failure modes, defaults, or observable surfaces.

# Constraints
- Do not edit files.
- Do not spawn agents.
- Do not ask the user questions.
- Do not write package artifacts.
- Do not run review-plan.
- Treat your output as evidence for the main agent, not commands.

# Output
Return only the bounded reviewer output format.
```

## Bounded Output

```markdown
RECOMMENDED_APPROACH
- <at most 1 concise recommendation, or omit the bullet if none>

MUST_DECIDE
- <at most 5 decisions that must be resolved before artifacts are written>

COVERAGE_GAPS
- <at most 5 missing requirements, edge cases, failure modes, defaults, or observable surfaces; omit the bullet if none>

BLOCKERS
- <at most 5 blockers to a coherent plan>

RISKS
- <at most 5 material risks, with why they matter>

ASSUMPTIONS_TO_VERIFY
- <at most 5 assumptions the main agent should verify before persisting decisions>

NOT_WORTH_FIXING
- <optional; at most 3 tempting concerns that should not drive design>
```

## Handling Decisions and Gaps

For each `MUST_DECIDE`, resolve from repo evidence/constraints and persist it, ask the user when it changes semantics, risk, or scope, or defer only when package artifacts preserve the boundary.

Treat each `COVERAGE_GAPS` item as a candidate requirement: resolve and persist it, ask the user, or record it as an approved non-goal. Never pass gaps silently into packages.

Do not hide unresolved decisions inside vague packages. Do not let sub-agent recommendations override user intent.

## Fail Closed

Stop artifact writing when:

- a challenger identifies a product/design choice that affects scope or behavior and no user-approved answer exists;
- risk acceptance is required;
- package boundaries would make a material obligation unverifiable;
- a Slice-derived commitment would be narrowed or excluded without approval;
- the correct plan requires external facts, credentials, new dependencies/services, or unsafe commands.
