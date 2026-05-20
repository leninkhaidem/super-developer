# Work Packages

Work packages are the delegation unit for Super Developer implementation. Tasks remain the tracking and acceptance-criteria unit. A work package groups related tasks so one sub-agent can amortize its context-loading cost across a substantial coherent assignment.

## Core Principle

Delegate substantial coherent work packages, not individual small tasks. Use parallel sub-agents for multiple substantial packages that can proceed safely at the same time.

## Task vs Work Package

- **Task:** A self-contained, verifiable outcome with status, dependencies, and acceptance criteria.
- **Work package:** A coherent implementation bundle containing one or more tasks that should share a single codebase exploration pass and one package worktree.

Tasks answer: "What must be done and verified?"
Work packages answer: "How should implementation work be delegated?"

## Package Sizing

A good work package usually contains several related tasks or one task large enough to justify a dedicated sub-agent. Avoid one-task packages unless the task is substantial, risky, or naturally isolated.

Prefer packages that are:
- coherent by subsystem, module, directory, user flow, data model, API surface, or test surface
- large enough to justify sub-agent startup context
- small enough for one agent to reason about safely
- independently mergeable
- clear about which paths to inspect first

## Package IDs

Package IDs use the `WP<N>` format with sequential numbering and no gaps (`WP1`, `WP2`, `WP3`, ...). Renumber when packages are reordered, split, or merged so the sequence stays contiguous.

## Internal Dependencies

A work package may contain tasks that depend on each other. The sub-agent handles internal dependencies sequentially and commits after each task ID. A package is blocked only by dependencies outside the package that are not yet done or integrated.

## Parallel Safety

Mark packages as parallel-safe only when likely file ownership and subsystem boundaries do not overlap. When unsure, combine or serialize packages. The cost of serialization is latency; the cost of unsafe parallelism is merge conflicts and inconsistent design.

`parallel_safe_with` is a symmetric relation: if `WPx` lists `WPy`, then `WPy` must list `WPx`. A package never lists itself.

## Primary Paths

`primary_paths` are starting points for code exploration, not hard boundaries. Agents should inspect those paths first and broaden only when imports, tests, or acceptance criteria require it.

## Verification Commands

Each package's `verification_commands` lists concrete shell commands the orchestrator runs after the package merges (for example, `npm test -- auth`). Populate it only with commands known to exist in the project or strongly implied by it. Use `[]` rather than inventing commands; an empty list is preferable to a guessed one.

Treat `verification_commands` as executable inputs from a plan artifact. They must be scoped, deterministic, and known-safe. If a command is destructive, externally visible, credential/network-sensitive, installs dependencies or services, mutates data outside the worktree, or exceeds the advertised verification scope, the Execution Contract must stop for explicit user approval before it runs.

Accepted package proofs must include passing command evidence for every listed `verification_commands` entry. Do not create a second command ledger; cite the command under the relevant proof entry's existing `evidence.commands`.

Prefer targeted, deterministic package commands. If a command is listed in package
`verification_commands`, it is required package proof and must run before package acceptance. Broad or
expensive full-suite, generated-contract, typecheck, or lint commands should usually be kept out of
package `verification_commands` and batched as integration/final checks unless they are cheap by
project convention or the only credible proof for an assigned acceptance criterion.


## Package Proof Files

Each package writes exactly one `.tasks/<feature>/proofs/<WP-ID>.proof.json` file. The validator derives the package's required acceptance criteria from `tasks.json`; proof files must cover every criterion assigned to that package and no criteria from other packages. Final feature proof validation requires exactly one proof file per work package and exact aggregate acceptance-criterion coverage.

Pipeline review-code state does not add another proof file or acceptance ledger. If a review-code fix
touches a package's acceptance surface, proof-cited files, verification commands, targeted-review
evidence, or audit handoff assumptions, the orchestrator reopens and refreshes that package's same
proof file before final audit readiness. Uncertain impact fails closed by refreshing candidate
package proofs or by recording explicit no-impact evidence; it is not silently ignored because a
single exact criterion was hard to identify.

## Risk Metadata and Targeted Review

Plans include:

- `risk_tags`: controlled tags used for targeted package review and edge-case checklist obligations.
- `required_context_bundles`: context bundle IDs package agents must read and cite.
- `targeted_review_required`: `true` when tags or planner judgment require package-level review.

When `targeted_review_required` is true, the accepted package proof must include a minimal root `targeted_review` object: `required`, `performed`, `reviewer`, `result`, `evidence`, and `reviewed_at`. Keep `evidence` to a concise pointer or summary of the targeted review report; do not add review histories or event logs.

Targeted-review-triggering tags include:

- `security`, `privacy`, `safety`
- `persistence`, `data-integrity`, `migration`
- `runtime-contract`, `library-contract`
- `public-api`, `exported-types`
- `concurrency`, `idempotency`, `replay`
- `performance`, `resource-bounds`
- `cross-package-integration`
- `schema`, `traceability`, `validation`
- `orchestration`, `git-state`, `integration`, `subagent-contract`
- `review`, `audit`, `fix-loop`, `quality-contract`

Documentation-only tags such as `documentation`, `docs`, `consistency`, and `validation-samples` do not require targeted review by themselves. A package with any targeted-review-triggering tag must set `targeted_review_required: true`; a package may also set it true conservatively even without a triggering tag.

### Risk-Bearing Package Rubric

A risk-bearing package needs independent targeted package review before its tasks are marked done when it touches sensitive, cross-cutting, irreversible, or shared-contract surfaces. Examples include security/privacy/safety; auth, permissions, tenancy, admin/user authority; secrets, tokens, credentials, PII, logs, telemetry, or data exposure; persistence, data integrity, migrations, destructive data changes, ownership conversion, lifecycle cleanup, audit/fail-closed behavior; public APIs, schemas, generated contracts, exported types; concurrency, caches, resource bounds, performance; cross-package/shared configuration or integration invariants; and orchestration, tool authority, sub-agent contracts, proof lifecycle, review/audit, or fix-loop behavior.

Targeted package review is local package-risk review, not a replacement for final `review-code`. It should consume package self-review, proof evidence, targeted checks, risk tags, and the integrated package delta. Do not expand the risk-tag taxonomy or add schema fields for this rubric; the orchestrator derives risk-bearing status from existing plan metadata and runtime discovery. Runtime-upgraded reviews on packages whose plan flag is false are recorded as optional targeted-review evidence (`required: false`) and enforced by the orchestrator checkpoint rather than by the schema.

## Rationale

Every package carries a `rationale` field explaining why its tasks should share one sub-agent context. For multi-task packages, the rationale describes the shared subsystem, file surface, or coherent outcome. For one-task packages, the rationale must explain why the task is substantial, risky, or naturally isolated enough to warrant a dedicated package. Rationale text is reviewer-judged, not mechanically enforced.

## Runtime Adjustment

The implementation orchestrator may merge, split, defer, or reorder planned packages when current task status, file impact, or previous merged work makes the plan unsafe or inefficient. It must briefly state the reason before dispatching.

When runtime adjustment changes package risk, context-bundle needs, verification commands, or targeted-review decisions, the orchestrator must state the reason and update the Execution Contract before dispatch. It must not silently downgrade a package from targeted review when a triggering risk tag remains.

## Anti-Patterns

- One work package per small task.
- Maximizing sub-agent count just because tasks are independent.
- Splitting tasks that touch the same files or subsystem.
- Bundling unrelated subsystems into a vague mega-package.
- Marking packages parallel-safe without checking likely file overlap.
- Giving a sub-agent a package with no primary paths when relevant paths are known.
