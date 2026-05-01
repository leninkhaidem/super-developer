# Plan Review Findings

This contract defines the output format for plan-review sub-agents. Findings are evidence for the main agent, not commands.

## Finding Schema

Each finding must use this shape:

```text
[SEV] TARGET — TITLE
ISSUE: <observed problem and why it matters>
FIX: <smallest concrete correction or decision needed>
COST: <complexity burden of the proposed fix; required when specified below>
```

Rules:

- `SEV`, `TARGET`, and `TITLE` are all on one line.
- `ISSUE` must cite observable plan/spec/codebase evidence or explicitly label an inference.
- `FIX` must be actionable and scoped to the plan artifacts, not implementation work.
- `COST` is required for all `BLOCKER` and `CRITICAL` findings, and for any finding whose fix changes semantics, expands scope, adds tasks/packages, or may be dismissed as disproportionate. It is optional for `SUGGESTION` findings.

## Severity Taxonomy

- `BLOCKER`: Must resolve before implementation. The plan cannot safely proceed because requirements, dependencies, acceptance criteria, or design boundaries are incoherent, missing, contradictory, or security/safety-invalid.
- `CRITICAL`: Strongly recommended to resolve. The plan can be finalized only with an explicit applied fix, approved alternative, dismissal, or defer-to-implement rationale.
- `SUGGESTION`: Non-blocking improvement or simplification. Suggestions do not require resolution.

Reviewers must not inflate severity to force action. Severity describes risk if the plan ships unchanged.

## Target Locator Grammar

`TARGET` identifies the smallest affected plan element:

```text
SPEC:<section-or-heading>
TASK:<task-id>
TASK:<task-id>.<field>
WP:<work-package-id>
WP:<work-package-id>.<field>
DD:<design-decision-id>
SCHEMA:<field-or-path>
GLOBAL:<pipeline-or-cross-cutting-area>
```

Examples:

```text
[BLOCKER] TASK:P1-T003.acceptance_criteria — Missing observable outcome
[CRITICAL] DD:DD-2 — Rationale contradicts codebase evidence
[SUGGESTION] WP:WP1.parallel_safe_with — Symmetric relation is incomplete
```

Use `DD:<design-decision-id>` for findings that challenge or depend on an accepted design decision.

## Caps

Reviewers must report:

- All `BLOCKER` findings.
- All `CRITICAL` findings.
- Up to 10 `SUGGESTION` findings, prioritized by implementation risk and review value.

Do not pad the review. If there are no findings, respond with exactly `NONE`.

## Reviewer Prohibitions

Reviewers must not:

- Edit files.
- Spawn agents or delegate review.
- Ask the user questions.
- Implement fixes.
- Rewrite the plan.
- Run unrelated project-wide commands.
- Treat their findings as commands to the main agent.

A reviewer may recommend that the main agent ask the user only when the issue requires a semantic choice that cannot be resolved from the plan, repository, or explicit constraints.
