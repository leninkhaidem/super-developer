# Implement Package Dispatch

Load this reference at implement Step 5/6, after `SPEC.md`, validated `tasks.json`, and `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/work-packages.md` are read. `work-packages.md` remains the canonical source for package semantics, risk metadata, targeted-review triggers, and anti-patterns; this file is the implement runbook for applying those rules.

## Package Shape

Use `work_packages` from `tasks.json` as the starting point. Plans without `work_packages` are invalid for implementation; do not infer a new package graph at runtime.

Validate each candidate package before dispatch:

- ID is a valid package ID from the plan (`WP<N>`), and every listed task ID exists.
- It contains at least one `pending` task.
- It is coherent by subsystem, module, directory, user flow, data model, API surface, or test surface.
- It is substantial enough to justify a sub-agent. A one-task package is acceptable only when the task is substantial, risky, or naturally isolated.
- `primary_paths` are useful starting points. They are not hard boundaries; agents broaden only when imports, tests, or acceptance criteria require it.
- `risk_tags`, `required_context_bundles`, `targeted_review_required`, and `verification_commands` are carried into the Execution Contract.

Do not dispatch a package whose dependency state is externally blocked. Internal dependencies between tasks in the same package are sequenced by the package agent.

## File-Impact Analysis

Before selecting a batch, infer likely file impact from:

- SPEC requirements and accepted design decisions.
- Task descriptions and acceptance criteria.
- Package `primary_paths`.
- Known module ownership and imports discovered during narrow exploration.
- Prior merged package changes.

Classify likely overlap, not just listed path overlap. Packages that touch the same exported surface, schema, generated artifact, build config, or runtime contract overlap even when their initial files differ.

Also scan `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/known-risk-patterns.md` for applicable generic probes. Use it only as a prompt source; do not create new risk tags, durable checklist sections, or feature-specific taxonomy entries from it.

When file impact is ambiguous, serialize. The cost of serialization is latency; the cost of unsafe parallelism is merge conflicts or inconsistent design.

## Runtime Adjustment Rules

The orchestrator may merge, split, defer, or serialize planned packages when current status, dependency state, file impact, or previous merged work makes the planned shape unsafe or inefficient. State the adjustment and reason before dispatch.

Allowed adjustments:

- **Merge** small or tightly coupled packages that would otherwise force duplicate exploration or conflict.
- **Split** only when a planned package is too broad to reason about safely and the split preserves acceptance-criterion traceability.
- **Defer** when dependencies, blocked tasks, missing facts, or unsafe command approval prevent dispatch.
- **Serialize** when likely file impact overlaps or prior package output must be integrated first.

When adjustment changes risk, context-bundle needs, verification commands, or targeted-review decisions, update the Execution Contract before dispatch. Do not silently downgrade targeted review while a triggering risk tag remains.

## Known-Risk and Must-Prove Prompts

For each candidate package, derive the pre-dispatch must-prove prompts from existing acceptance criteria, verification hints, risk tags, context bundles, verification commands, and the known-risk reference. Use `taskctl.py must-prove <WP-ID>` as the routine read-only helper when available. Keep the result transient in the dispatch/agent instructions.

Include a pollution-sensitive test-ordering requirement when changed tests mutate import caches, module registries such as `sys.modules`, environment variables, globals, singleton caches, import stubs, monkeypatches, or equivalent shared process state. The package proof should cite checks for the test alone, the test before and after likely consumers, and the combined affected suite, or state a concrete reason the trigger does not apply.

When acceptance criteria involve boundary payloads, requests, configs, command descriptors, generated defaults, optional fields, default precedence, or contract drift, prefer a small exported pure builder plus observable contract tests over ad hoc construction in high-level orchestration, UI, or glue code. Do not require builders for trivial local values or purely presentational state.

## Semantic Package Review Triggers

Before dependent downstream packages proceed, require a focused semantic package review after merge or fix when the package has high-risk cache semantics, lifecycle cleanup, boundary serialization, generated contract defaults, persistence, concurrency, public API, shared configuration, or similar cross-cutting impact.

This review is narrower than final `review-code`: it checks the integrated package delta, risk-class edge cases, package proof adequacy, and downstream contract safety. It does not replace the mandatory final whole-feature review-code pass or final audit.

## Batch Selection

Collect all externally actionable packages, then choose the safest useful batch:

1. Prefer packages whose dependencies are satisfied and whose likely file impact does not overlap.
2. Parallelize only substantial packages with safe dependency and file boundaries.
3. Do not maximize sub-agent count for its own sake.
4. If a downstream package needs earlier feature work, run it only after prerequisite packages merge into `feature/<feature>`; branch it from the feature ref.
5. If two packages are both actionable but share a contract, API, schema, or config surface, serialize them or merge them.

## Delegation Mode

Every selected planned-feature package is delegated to a sub-agent in its own worktree:

- Worktree: `.worktrees/<feature>/wp-<WP-ID>`.
- Branch: `task/<feature>/<WP-ID>`.
- One package branch is merged once, even when the package contains multiple task commits.

The orchestrator must not implement substantive package work inline. If the package seems too small for a sub-agent, merge it with related work or keep it serialized.

## Batch Announcement

Before spawning agents, announce:

- package IDs and task IDs;
- package branch/worktree names;
- primary paths and likely file impact;
- required context bundles;
- risk tags and targeted-review decision;
- screened verification commands and any commands needing approval;
- model selection;
- parallel or serial rationale;
- any runtime package adjustments.
