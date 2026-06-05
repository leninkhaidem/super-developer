# Work Packages

## Boundary

This reference owns package semantics: sizing, dependency, assignment, parallelism, primary paths, and verification expectations. Artifact shapes live in `slice-first-artifacts.md`; completion/freshness gates live in `package-lifecycle.md`; command safety lives in `tool-usage.md`.

## Core Principle

Delegate substantial coherent work packages, not tiny fragments. Prefer the largest safe useful wave of independently substantial packages that can proceed together. Parallelism reduces latency; it must not maximize agent count or split work merely to create more agents.

## Package Roles

- **Slice Markdown:** product/design authority when present.
- **`SPEC.md`:** accepted requirements, constraints, non-goals, and verification summary.
- **Registry:** package list, paths, status signals, and dependency IDs only.
- **Package Markdown:** authoritative package assignment.
- **Proof Markdown:** package closure evidence.
- **Package verification report:** independent state-bound verification receipt.

Registry status and helper results are signals, not proof.

## Package Sizing

A good package is:

- coherent by subsystem, module, directory, user flow, data model, API surface, or test surface;
- large enough to justify dedicated agent startup;
- small enough for one agent to reason about safely;
- independently mergeable;
- explicit about initial inspection paths;
- clear about assigned Slice H3 obligations and verification expectations.

Avoid one-tiny-change packages unless the work is risky, naturally isolated, or requires focused verification.

## IDs and Dependencies

Package IDs use contiguous `WP<N>` values (`WP1`, `WP2`, ...). Renumber when packages are reordered, split, or merged so the sequence has no gaps.

Dependencies live in both the registry `depends_on` array and package Markdown `## Dependencies`; they must agree. A package is externally blocked when a dependency outside the package is not complete and freshly verified. Internal sequencing is handled by the package agent.

## Parallel Safety

Treat packages as parallel-safe only when likely file ownership, subsystem boundaries, Slice obligations, proof surfaces, and caller contracts do not overlap.

Serialize or combine packages when:

- files or generated artifacts overlap;
- subsystem, API, config, or schema surfaces overlap;
- one package's proof or verification depends on another's output;
- package boundaries would hide a material Slice obligation;
- design consistency would likely be decided differently by independent agents.

The cost of serialization is latency; the cost of unsafe parallelism is merge conflict, inconsistent design, stale proof evidence, and invalid reports.

## Primary Paths

`## Primary Paths` are starting points, not hard boundaries. Agents inspect them first and broaden only when imports, tests, Slice obligations, or verification expectations require it.

## Verification Expectations

Package Markdown `## Verification Expectations` lists the package's proof expectations: commands known to exist, static inspections, scenarios, edge/failure cases, trust-boundary checks, no-mock constraints, generated-contract checks, or manual observations.

Rules:

- Treat package-provided commands as executable input and screen them before running.
- Address every expectation in proof Markdown.
- Do not create a second command ledger in the registry.
- Batch broad or expensive full-suite, generated-contract, typecheck, or lint commands at integration/final gates unless they are cheap by project convention or the only credible package proof.

## Risk and Review Lenses

Package scope and assigned Slices should make risk visible without adding durable checklist fields to the registry.

Enhanced verification is triggered by surfaces such as:

- security, privacy, or safety;
- persistence, data integrity, migration, or rollback;
- public API, exported types, generated contracts, or external integrations;
- concurrency, idempotency, replay, cancellation, or cleanup;
- performance, resource bounds, fanout, or blocking I/O;
- cross-package integration;
- orchestration, git state, package verification, review, audit, or quality-contract changes.

Documentation-only and reference-only packages still receive baseline package verification; risk determines depth, not whether verification runs.

## Runtime Adjustment

The implementation orchestrator may merge, split, defer, or reorder planned packages when current package status, file impact, proof readiness, Slice assignment, or previous merged work makes the plan unsafe or inefficient. It must state the reason before dispatch.

If adjustment changes package scope, Slice H3 assignment, dependencies, proof path, report path, or approved deferrals, route through artifact repair or explicit user approval. Do not silently downgrade verification depth while a triggering risk remains.

## Anti-Patterns

- One package per tiny edit.
- Maximizing sub-agent count.
- Leaving substantial independent packages serialized without a concrete dependency, file-impact, proof, or contract-safety reason.
- Splitting work touching the same files, Slice obligation, subsystem, or proof surface.
- Bundling unrelated subsystems into a vague mega-package.
- Marking packages parallel-safe without checking likely file/proof/contract overlap.
- Giving a package no primary paths when relevant paths are known.
- Duplicating package scope, assigned H3 IDs, proof evidence, review receipts, or lifecycle ledgers into the registry.
- Treating registry status, helper validation, package self-review, or chat summaries as package proof.
