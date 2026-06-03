# Design Preflight

Design Preflight is the optional adversarial design pass for `implementation-plan`. It happens before any durable plan artifacts are written.

## Purpose

Use Design Preflight to surface consequential design choices before the planner commits to `SPEC.md` or `tasks.json`. The output is evidence for the main agent; it is not an implementation plan, not a persisted spec, and not an instruction stream for sub-agents to execute.

## Trigger Conditions

Run Design Preflight only for nontrivial or risky plans, including plans with any of these signals:

- New architecture, data model, permission boundary, external integration, or persistence behavior.
- Security, privacy, safety, reliability, migration, concurrency, or rollback risk.
- Ambiguous requirements where different designs could satisfy the same user request.
- Cross-cutting changes across multiple subsystems, skills, commands, or generated artifacts.
- A likely semantic tradeoff that should be explicit before task generation.

Skip Design Preflight for mechanical, narrow, low-risk changes where the existing architecture and caller contract are already clear.

## Authority Split

- **Main agent:** owns orchestration, final interpretation, user interaction, durable artifact writing, and all design decisions.
- **Sub-agents:** are read-only challengers. They receive a narrowed reviewer contract, inspect only the provided context/files, and return bounded evidence. They must not edit files, spawn agents, ask the user questions, write tasks, or run the full `review-plan` skill.

Sub-agent output is advisory evidence. The main agent may accept, reject, combine, or reframe it, but must not silently convert unresolved semantic choices into durable decisions when user approval is required.

## Model Preference Resolution

Before spawning any Preflight challenger, resolve model preferences using the existing
`references/model-preferences.md` procedure:

- Standard planning/design challengers use the existing `review-plan` key.
- Adversarial, security, privacy, safety, or failure-mode challengers use the existing
  `skeptic-agent` key.
- Do not add or document a Design Preflight, `implementation-plan`, or other new model-preference key.
- If the resolved value is `inherit`, omit the model parameter so the challenger inherits the
  orchestrator model.
- If the resolved value is `adaptive`, use the same role interpretation as plan review: standard
  planning challengers use the Plan Reviewer adaptive behavior; adversarial/failure-mode challengers
  use the skeptic adaptive behavior.
- If the resolved value is a model name, pass that exact model name to the challenger.

## Timing and Persistence

- Run before writing `.tasks/<feature-name>/SPEC.md`, `.tasks/<feature-name>/tasks.json`, or any equivalent durable task artifact.
- The Preflight Brief is ephemeral and neutral.
- The Preflight Brief must not be persisted under `.tasks/`.
- For schema-version-4 Slice-first plans, durable preflight outcomes are persisted in the normal v4 artifact that owns the obligation: product-level requirements/constraints/out-of-scope or approved override metadata in `SPEC.md`; package-level boundaries, notes, assigned Slice IDs, and verification expectations in work-package Markdown; and closure expectations that flow into proof Markdown.
- For legacy schema-version-2/3 plans only, durable design outcomes may be persisted as `design_decisions` in `tasks.json`.
- `SPEC.md` remains requirements/manifest-only. Do not put architecture rationale in `SPEC.md` unless the user explicitly made that rationale a product requirement, constraint, or approved scope decision.

## Neutral Preflight Brief Format

The main agent prepares a short brief for reviewers using neutral language:

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

The brief must not include a preferred solution unless the user already selected one. When the main agent has an initial hypothesis, label it as a hypothesis and place it under `Open Design Surface`, not as a conclusion.

## Reviewer Assignment Template

```markdown
# Role
You are a read-only design challenger for Design Preflight.

# Inputs
- Preflight Brief: <brief text or path>
- Relevant files/context: <bounded list>
- Model preference: <resolved `review-plan` or `skeptic-agent` value; omit the dispatch model parameter when this is `inherit`>

# Task
Evaluate the design surface before durable plan artifacts are written. Identify the smallest set of decisions that must be made now to produce a coherent plan.

# Constraints
- Do not edit files.
- Do not spawn agents.
- Do not ask the user questions.
- Do not write implementation tasks.
- Do not run the full `review-plan` skill.
- Treat your output as evidence for the main agent, not commands.

# Output
Return only the bounded reviewer output format.
```

## Bounded Reviewer Output Format

Reviewers must use these exact sections and caps:

```markdown
RECOMMENDED_APPROACH
- <at most 1 concise recommendation, or omit the bullet if none>

MUST_DECIDE
- <at most 5 decisions that must be resolved before writing tasks>

BLOCKERS
- <at most 5 blockers to producing a coherent plan>

RISKS
- <at most 5 material risks, with why they matter>

ASSUMPTIONS_TO_VERIFY
- <at most 5 assumptions the main agent should verify before persisting decisions>

NOT_WORTH_FIXING
- <optional; at most 3 tempting concerns that should not drive design>
```

`RECOMMENDED_APPROACH` is capped at one because the reviewer is not the planner. If multiple viable approaches exist, put the choice in `MUST_DECIDE` instead.

## Handling `MUST_DECIDE`

For each `MUST_DECIDE` item, the main agent must do one of the following before writing durable artifacts:

- Resolve it from observed repo evidence or explicit user constraints and persist the result in the artifact that owns the obligation. In v4, use `SPEC.md` for product-level requirements/constraints/out-of-scope or approved override metadata, and work-package Markdown/proof expectations for package-level design, boundaries, verification, sequencing, risk, or implementation constraints. In legacy v2/v3, use `tasks.json.design_decisions` when that schema owns the decision ledger.
- Ask the user when the decision changes product semantics, external behavior, risk acceptance, or scope.
- Defer it only when it is genuinely implementation-time detail; if deferred, v4 artifacts must preserve the decision boundary through approved scope metadata, package notes, assigned Slice scope, and verification/proof expectations. Legacy v2/v3 tasks must preserve the boundary in task acceptance criteria.

Do not hide unresolved `MUST_DECIDE` items inside vague tasks or packages. Do not let sub-agent recommendations override user intent.

## Persistence Rules by Plan Schema

For schema-version-4 Slice-first plans:

- Do not add `design_decisions`, task acceptance matrices, context bundles, or rich handoff records to `tasks.json`.
- Persist product-level outcomes in `SPEC.md` only when they are requirements, constraints, acceptance implications, out-of-scope items, or explicit approved scope/override metadata.
- Persist package-level outcomes in work-package Markdown `## Scope`, `## Assigned Slices`, `## Verification Expectations`, `## Dependencies`, or optional `## Notes`.
- Ensure proof-relevant outcomes appear as package verification expectations or assigned `must_satisfy` IDs so generated proof Markdown has closure rows.
- Do not persist the Preflight Brief itself.

For legacy schema-version-2/3 plans only, accepted design decisions may be persisted in `tasks.json` under `design_decisions`:

- IDs use `DD-1`, `DD-2`, ... sequentially with no gaps.
- `source` is exactly `design-preflight` or `planner`.
- Each entry records the decision, concise rationale, and any material constraints or rejected alternatives needed for future review.
- Persist only decisions that affect design, task shape, acceptance criteria, sequencing, risk, or verification.
- Do not persist the Preflight Brief itself.
