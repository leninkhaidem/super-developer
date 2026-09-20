# Design Preflight

## Purpose
Design Preflight is a read-only adversarial planning challenge. It surfaces decisions and requirement-completeness gaps before writing `SPEC.md`, the registry, package Markdown, or result `report_path`s.

Completeness gaps include missing observable behavior, edge cases, failures, defaults, or expected obligations.
The two-sided challenge also cuts abstractions, layers, config, state, flags, extensions, dependencies, or package
splits not needed for accepted outcomes/constraints or evidenced risk. A draft Acceptance item cannot justify the
very machinery it was written to describe. This is not a plan, transcript, or sub-agent instruction stream.

## Trigger and Reuse

Require this challenge only when a consequential design decision remains unresolved before drafting, such as
trust/data ownership, architecture, migration/rollback, or alternatives with material behavior or safety tradeoffs.
Complexity, cross-cutting scope, or sensitivity alone do not trigger preflight when approved requirements and current
repository evidence settle the relevant decisions. For ordinary settled work, draft directly and let independent
`review-plan` challenge the actual plan. Skipping preflight does not waive required plan/security review, empirical
evidence, or user decisions.

When triggered, apply the complete shared model and all smells: challenge shallow/pass-through Modules, wide/leaky
Interfaces, hypothetical Seams, unjustified Adapters, scattered ownership, and tests reaching past the Interface.
Persist only material implications.

When the trigger still applies, reuse current read-only adversarial analysis that already covers requirement
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
Read and apply the complete shared clean-code contract before reviewing. For material design, challenge the
Module/Interface/Seam/Adapter model, Depth/Leverage/Locality, and every smell with evidence-calibrated findings;
retain harmless shapes and avoid speculative cleanup. Identify decisions needed for a coherent plan and surface
requirement-completeness gaps: missing expected behaviors, edge cases, failures, defaults, or observable surfaces.
Also challenge proposed machinery against removal or reuse: what accepted outcome/constraint or evidenced risk
would the simpler alternative miss? Cut unsupported abstraction, layers, configuration, extensibility, dependencies,
or package proliferation. Do not treat a planner-created requirement or Acceptance item as independent justification
for its own design choice. Return only material implications for the planner.

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
- <at most 5 unnecessary abstractions, layers, config, flags, extension points, dependencies, or package splits;
  name the simpler alternative and why accepted outcomes/constraints and evidenced risks remain covered; omit if none>

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

Treat each `OVERBUILT` item as a default cut. Retain it only when removal or a concrete simpler alternative would
miss an accepted outcome/constraint or evidenced risk; record that material justification in existing fields.
A newly drafted requirement or Acceptance item is not independent justification. If a cut would change an explicit
user/Slice commitment or accept risk, return that decision to the owner rather than silently dropping the obligation.

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
