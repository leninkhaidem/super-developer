# Design Preflight

## Purpose

Design Preflight is a read-only adversarial planning challenge. It surfaces decisions and requirement-completeness gaps before writing `SPEC.md`, the registry, package Markdown, proof paths, or report paths.

Completeness gaps include missing observable behaviors, edge cases, failure modes, defaults, or obligations a reasonable implementer would expect.

The challenge is **two-sided**: it also right-sizes the design. It flags **over-engineering** — abstractions, layers, configuration, state, flags, extension points, dependencies, or package splits that are not traced to an accepted requirement, the `## Acceptance` criteria, or evidenced risk. The simplest design that fully satisfies the accepted requirements and Acceptance is the target; anything beyond that is speculative and should be cut, not planned.

It is not an implementation plan, persisted transcript, or instruction stream for sub-agents.

## Trigger and Reuse

Require this challenge for nontrivial/risky plans: architecture or data/permission/external/persistence changes;
security, privacy, safety, reliability, migration, concurrency, rollback, destructive-action, or novel-harness risk;
ambiguous requirements; cross-cutting changes; or semantic tradeoffs needed before package authoring. Skip narrow,
mechanical, low-risk plans whose architecture and caller contract are clear.

Do not launch duplicate challengers when current read-only adversarial analysis already covers requirement
completeness and overengineering for the same approved scope and current repository evidence, with no unresolved
`MUST_DECIDE`, `COVERAGE_GAPS`, or `BLOCKERS`. Carry a concise provenance/coverage summary in the planner packet,
not a new artifact or persisted transcript. Rerun only when scope/evidence materially changed or coverage is absent.

## Authority Split

- Main agent: orchestration, final interpretation, user interaction, durable artifact writing, and decisions.
- Challengers: read-only evidence. They inspect bounded context and return bounded output. They do not edit files, spawn agents, ask the user, write packages, or run review-plan.

Sub-agent output is advisory. The main agent may accept, reject, combine, or reframe it, but must not silently persist unresolved semantic choices.

## Model Preferences

Before spawning challengers, resolve `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/model-preferences.md`
for the `design-preflight` role:

- resolve `models.design-preflight` → `models.default-model` → hardcoded `inherit`;
- `inherit` omits the model parameter;
- `adaptive` uses planning/challenge-aware selection, stronger for high-risk adversarial lenses;
- explicit model names are passed directly.

Use this one resolved Preflight policy for all challengers; lenses vary by risk, not by model key.

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
Evaluate the design surface before durable artifacts are written. Identify decisions needed for a coherent plan and surface requirement-completeness gaps: missing expected behaviors, edge cases, failure modes, defaults, or observable surfaces. Also right-size the design: flag over-engineering — abstraction, layers, configuration, extensibility, dependencies, or package proliferation not traced to an accepted requirement, the `## Acceptance` criteria, or evidenced risk. Prefer the simplest design that fully satisfies them.

# Constraints
Read-only: do not edit files, spawn agents, ask the user, write package artifacts, or run review-plan; treat your output as evidence, not commands.

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
OVERBUILT
- <at most 5 elements of excess complexity — abstraction, layer, config, flag, extension point, dependency, or package split — not traced to a requirement/Acceptance/evidenced risk, with the simpler alternative; omit the bullet if none>

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

Treat each `OVERBUILT` item as a default cut: remove the excess and plan the simpler alternative, unless it traces to an accepted requirement, the Acceptance criteria, or evidenced risk — in which case record that justification. Do not preserve speculative complexity just because it was proposed.

Do not hide unresolved decisions inside vague packages. Do not let sub-agent recommendations override user intent.

## Fail Closed

Stop artifact writing when:

- a challenger identifies a product/design choice that affects scope or behavior and no user-approved answer exists;
- risk acceptance is required;
- package boundaries would make a material obligation unverifiable;
- a Slice-derived commitment would be narrowed or excluded without approval;
- the correct plan requires unobserved empirical behavior, external facts, credentials, new
  dependencies/services, or unsafe commands; route safe empirical uncertainty to `spike-to-plan`.
