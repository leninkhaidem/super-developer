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
- `risk_tags`, `required_context_bundles`, `targeted_review_required`, and `verification_commands` are carried into the Execution Contract. `targeted_review_required` remains compatibility metadata for the existing `targeted_review` receipt shape; it is not a switch for skipping mandatory package review.

Do not dispatch a package whose dependency state is externally blocked. Internal dependencies between tasks in the same package are sequenced by the package agent.

## File-Impact Analysis

Before selecting a batch, infer likely file impact from:

- SPEC requirements and accepted design decisions.
- Task descriptions and acceptance criteria.
- Package `primary_paths`.
- Known module ownership and imports discovered during narrow exploration.
- Prior merged package changes.

Classify likely overlap, not just listed path overlap. Packages that touch the same exported surface, schema, generated artifact, build config, or runtime contract overlap even when their initial files differ.

Use `taskctl.py must-prove --package <WP-ID>` with its default known-risk source, or pass `--known-risk-source ${SUPER_DEVELOPER_PLUGIN_ROOT}/references/known-risk-patterns.md` when needed, to derive applicable generic probes without loading the risk reference into orchestrator context by default. Use known-risk output only as a prompt source; do not create new risk tags, durable checklist sections, or feature-specific taxonomy entries from it.

When file impact is ambiguous, serialize. The cost of serialization is latency; the cost of unsafe parallelism is merge conflicts or inconsistent design.

## Runtime Adjustment Rules

The orchestrator may merge, split, defer, or serialize planned packages when current status, dependency state, file impact, or previous merged work makes the planned shape unsafe or inefficient. State the adjustment and reason before dispatch.

Allowed adjustments:

- **Merge** small or tightly coupled packages that would otherwise force duplicate exploration or conflict.
- **Split** only when a planned package is too broad to reason about safely and the split preserves acceptance-criterion traceability.
- **Defer** when dependencies, blocked tasks, missing facts, or unsafe command approval prevent dispatch.
- **Serialize** when likely file impact overlaps or prior package output must be integrated first.

When adjustment changes risk, context-bundle needs, verification commands, or package-review depth/lenses, update the Execution Contract before dispatch. Do not silently downgrade enhanced review lenses while a triggering risk tag remains.

## Review Depth and Runtime Risk Signals

Every package requires package-agent self-review before handoff, and every package also requires an independent targeted package review after merge before downstream unlock. The implementer self-review is input evidence for that review, not a substitute for it. Low-risk, docs-only, and test-only packages receive the standard package review baseline; risk tags and runtime risk signals determine enhanced depth and required lenses.

The orchestrator may upgrade package review depth at runtime when package exploration, implementation reports, self-review, proof evidence, file impact, or merged behavior reveals risk not captured in the original plan. Enhanced review surfaces include security/privacy/safety; auth, authorization, permissions, tenancy, admin/user authority; secrets/tokens/credentials/PII/logging/data exposure; persistence/data integrity/migrations/destructive data/ownership conversion; audit/fail-closed behavior; public API/schema/generated contracts/exported types; concurrency/cache/lifecycle/resource/performance risk; cross-package/shared-contract invariants; and orchestration/tool authority/sub-agent contracts/proof-review-audit/fix-loop behavior.

Runtime review-depth upgrade does not require user approval unless it changes product behavior, scope, dependencies, unsafe/external actions, or authority boundaries. State the upgrade reason in the execution status and package-review depth/lens announcement. If a legacy plan has `targeted_review_required: false`, keep the schema intact and still run package review; the existing receipt helper may record `required: false`, but the orchestrator enforces the review checkpoint before marking tasks done. Do not silently downgrade enhanced lenses while a triggering risk remains.

## Known-Risk and Must-Prove Prompts

For each candidate package, derive the pre-dispatch must-prove prompts from existing acceptance criteria, verification hints, risk tags, context bundles, verification commands, and `taskctl.py must-prove` output. Use `taskctl.py must-prove --package <WP-ID>` as the routine read-only helper; it supplies known-risk prompt content from its default source without requiring the orchestrator to load that reference directly. Keep the result transient in the dispatch/agent instructions.

Include a pollution-sensitive test-ordering requirement when changed tests mutate import caches, module registries such as `sys.modules`, environment variables, globals, singleton caches, import stubs, monkeypatches, or equivalent shared process state. The package proof should cite checks for the test alone, the test before and after likely consumers, and the combined affected suite, or state a concrete reason the trigger does not apply.

When acceptance criteria involve boundary payloads, requests, configs, command descriptors, generated defaults, optional fields, default precedence, or contract drift, prefer a small exported pure builder plus observable contract tests over ad hoc construction in high-level orchestration, UI, or glue code. Do not require builders for trivial local values or purely presentational state.

## Package Review Depth Signals

Before dependent downstream packages proceed, require the targeted package review path after merge or fix for every package. Risk-bearing surfaces require enhanced package-review lenses: high-risk cache semantics, lifecycle cleanup, boundary serialization, generated contract defaults, persistence, concurrency, public API, shared configuration, proof/review/audit/fix-loop behavior, or similar cross-cutting impact.

Do not run both a separate semantic package review and a targeted package review for the same risk surface. Fold semantic concerns into the targeted package review lenses: integrated package delta, risk-class edge cases, package proof adequacy, self-review quality, test/proof evidence quality, and downstream contract safety. This review is narrower than final `review-code` and does not replace the mandatory final whole-feature review-code pass or final audit.

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
- risk tags and mandatory package-review depth/lenses;
- screened package verification commands and any commands needing approval, plus separate broad/expensive integration or final checks that are not package `verification_commands`;
- mandatory package self-review expectation;
- model selection;
- parallel or serial rationale;
- any runtime package adjustments.
