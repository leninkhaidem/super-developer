# Plan Review Resolution

The main agent owns plan-review triage. Reviewer comments are evidence, not commands.

## Main-Agent-Only Triage

Only the main agent categorizes and resolves findings. Use these exact categories:

### mechanical defect

A schema, formatting, ID sequence, dependency, locator, or consistency problem whose correction does not change semantics. Fix directly and verify the affected artifact.

Examples: non-sequential `DD-*` IDs, invalid `source`, missing reciprocal `parallel_safe_with`, malformed acceptance-criteria field.

### true blocker

A defect that prevents safe finalization because the plan is incoherent, contradictory, unverifiable, or missing a required decision. Resolve before approval. If resolution changes product semantics, scope, risk acceptance, or external behavior, ask the user.

### design decision

A finding that requires choosing between materially different approaches. Persist accepted durable outcomes in `tasks.json.design_decisions` when they affect architecture, task shape, acceptance criteria, sequencing, risk, or verification. Use `source: "planner"` unless the decision came from Design Preflight, in which case use `source: "design-preflight"`.

### implementation-time concern/defer-to-implement

A valid concern better handled during implementation because the plan can preserve the boundary without deciding the detail now. Defer only when acceptance criteria, task wording, work-package metadata, or `design_decisions` keep the concern observable to future agents reading files cold. Do not use this category to hide unresolved semantic choices. Gate summaries are not a durable handoff by themselves.

### disproportionate recommendation/dismissal

A recommendation whose cost, scope expansion, complexity, or semantic impact is not justified by the evidence. Dismiss or narrow it. Record only the durable design outcome if the dismissal itself affects future review.

### suggestion

A non-required improvement. Apply only when it is low-risk and improves clarity or execution without semantic impact, or when the user approves the semantic change.

## Semantic Change Rule

Semantic changes require user approval unless they are purely internal simplifications with no semantic impact. Semantic changes include changes to product behavior, user-visible scope, risk acceptance, external interfaces, data retention, security/privacy posture, acceptance criteria meaning, or what work is considered complete.

Internal simplification may be applied without user approval only when it preserves the same requested outcome, the same externally visible behavior, and the same acceptance meaning.

## Resolution Workflow

1. Group duplicate findings by target and issue.
2. Classify each finding into one triage category.
3. Apply mechanical defects directly.
4. Escalate semantic choices to the user unless already resolved by explicit constraints or approved `design_decisions`.
5. Persist accepted design decisions in `tasks.json.design_decisions` when durable.
6. Keep `SPEC.md` requirements-only.
7. Encode implementation-time concerns durably in `tasks.json` as task or acceptance-criteria boundaries, work-package metadata, or `design_decisions`; do not leave them only as chat/Gate 2 notes.

## Re-Review Rules

Review re-runs are focused/delta-only and bounded:

- Re-review only changed artifacts or the specific targets affected by resolution.
- Tell reviewers which findings or deltas they are checking.
- Do not loop until reviewers are satisfied.
- Stop when blockers are resolved, semantic decisions are approved or explicitly deferred, and remaining suggestions are accepted or dismissed by the main agent.

A re-review may produce new evidence, but it does not transfer authority from the main agent to reviewers.
