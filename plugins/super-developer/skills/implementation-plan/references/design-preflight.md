# Design Preflight

## Purpose
Design Preflight is a read-only adversarial planning challenge. It surfaces decisions and requirement-completeness gaps before writing `SPEC.md`, the registry, package Markdown, or result `report_path`s.

Completeness gaps include missing observable behavior, edge cases, failures, defaults, or expected obligations.
The two-sided challenge also cuts abstractions, layers, config, state, flags, extensions, dependencies, or package
splits not traced to requirements, Acceptance, or evidenced risk. It is not a plan, transcript, or sub-agent
instruction stream.

## Trigger and Reuse

Require this challenge for nontrivial/risky plans: architecture or data/permission/external/persistence changes;
security, privacy, safety, reliability, migration, concurrency, rollback, destructive-action, novel-harness risk,
ambiguity, cross-cutting changes, or semantic tradeoffs. For material design, apply the complete shared model and
all smells: challenge shallow/pass-through Modules, wide/leaky Interfaces, hypothetical Seams, unjustified Adapters,
scattered ownership, and tests reaching past the Interface. Persist only material implications. Skip narrow,
mechanical plans with no material Module/Interface decision and a clear caller contract.

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
- result-file expectations through package Acceptance Checklist items and verification expectations;
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
- Relevant files/context: <bounded list>; Model preference: <resolved value; omit dispatch model parameter when inherit>
- Shared clean-code contract: ${SUPER_DEVELOPER_PLUGIN_ROOT}/references/clean-code-rules.md

# Task
Read and apply the complete shared clean-code contract before reviewing. For material design, challenge the Module/Interface/Seam/Adapter model, Depth/Leverage/Locality, and every smell with evidence-calibrated findings; retain harmless shapes and avoid speculative cleanup. Identify decisions needed for a coherent plan and surface requirement-completeness gaps: missing expected behaviors, edge cases, failure modes, defaults, or observable surfaces. Also right-size the design: flag over-engineering — abstraction, layers, configuration, extensibility, dependencies, or package proliferation not traced to an accepted requirement, the `## Acceptance` criteria, or evidenced risk. Prefer the simplest design that fully satisfies them.

# Constraints
Read-only: do not edit files, spawn agents, invoke `empirical-spike`, ask the user, write package artifacts, or run review-plan; treat your output as evidence, not commands. Do not persist anything; only the planner may persist accepted outputs through existing handling.

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

Return blockers to the `implementation-plan` orchestrator and stop artifact writing when:

- a challenger identifies a product/design choice that affects scope or behavior and no user-approved answer exists;
- risk acceptance is required;
- package boundaries would make a material obligation unverifiable;
- a Slice-derived commitment would be narrowed or excluded without approval;
- the correct plan requires external facts, credentials, new dependencies/services, or unsafe commands;
- material empirical behavior remains unresolved after bounded repository/official evidence. Identify distinct
  questions/decisions; only the orchestrator invokes one `empirical-spike` per question. Routine work does not.
