# Work Packages

## Boundary

This reference owns package semantics: sizing, dependency, assignment, parallelism, primary paths, and verification expectations. Artifact shapes live in `slice-first-artifacts.md`; completion/freshness gates live in `package-lifecycle.md`; command safety lives in `tool-usage.md`.

## Core Principle

Delegate packages that deliver substantial coherent planned deliverables, not tiny fragments. Deliverables may
include implementation, substantial documentation/reference work, or other accepted plan outcomes. Prefer the
largest safe useful wave of independently substantial packages that can proceed together. Parallelism reduces
latency; it must not maximize agent count or split work merely to create more agents. Verification-only phases
are not packages unless they create substantial reusable verification or test infrastructure.

## Package Roles

- **Slice Markdown:** product/design authority when present.
- **`SPEC.md`:** accepted requirements, constraints, non-goals, and verification summary.
- **Registry:** package list, paths, status signals, and dependency IDs only.
- **Package Markdown:** authoritative package assignment.
- **Proof Markdown:** package closure evidence.
- **Package verification report:** independent state-bound verification receipt.

Registry status and helper results are signals, not proof.

## Package Sizing and Closure Complexity

A good package is:

- coherent by subsystem, module, directory, user flow, data model, API surface, or test surface;
- large enough to justify dedicated agent startup and its fixed proof/report/verification cost;
- small enough for one agent to implement, verify, and repair through one coherent state/evidence boundary;
- independently mergeable, with explicit initial paths, assigned Slice obligations, and verification expectations.

Before finalizing the boundary, assess semantic closure complexity:

- obligation breadth, caller contracts, and independently observable outcomes;
- runtime surfaces/environments and distinct evidence or approval boundaries;
- changed harness/helper/fixture populations and the review depth they trigger;
- setup, isolation, teardown, cleanup, external preconditions, and shared-resource constraints;
- expected command cost, serial/fail-fast behavior, and broad-check placement;
- proof/report refresh fanout when implementation or evidence changes;
- empirical uncertainty that prevents a safe implementation or verification commitment.

Split when one agent cannot close those dimensions coherently. Keep work together when splitting would
multiply shared harness ownership, duplicate evidence, or add more fixed gate cost than it removes. Counts of
files, scenarios, or commands are warning signals, never universal thresholds. Route unresolved empirical
uncertainty to a spike instead of guessing package boundaries. Avoid tiny packages unless risk or isolation
justifies their fixed lifecycle cost.

## IDs and Dependencies

Package IDs use contiguous `WP<N>` values (`WP1`, `WP2`, ...). Renumber when packages are reordered, split, or merged so the sequence has no gaps.

Dependencies are ID-only in both the registry `depends_on` array and package Markdown
`## Dependencies`; they must agree. They are durable sequencing prerequisites and a lower bound on
readiness, not an impact or staleness graph. Put non-obvious rationale in existing package `Notes`, naming
consumed output, contract, or evidence; runtime overlap, failure, or a desired rerun alone does not create an
edge. A package is externally blocked until each dependency has a fresh `PASS` package verification report
and clean `validate-package-complete`; registry `done` or proof rows alone do not unlock dependents.
Internal sequencing is handled by the package agent.

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

Package Markdown `## Verification Expectations` lists the package's proof expectations and mandatory
`VE-<n>` row sources: known commands, static inspections, scenarios, edge/failure cases, trust-boundary checks,
no-mock constraints, generated-contract checks, interface/risk seeds, or manual observations.

Use only the existing depth vocabulary: `standard`/`enhanced` package verification,
`baseline-only`/`sampled`/`deep` test review, and `focused`/`full` reruns. These are orthogonal decisions, not
new lifecycle tiers or durable registry/artifact fields.

Rules:

- Treat package-provided commands as executable input and screen them before running.
- Address every expectation in proof Markdown and preserve it as a `VE-<n>` package-verification matrix source; linked Slice evidence may be cross-referenced, not silently omitted.
- Seed obvious interface/risk checks when applicable, including exact interfaces, forbidden behaviors, interactive UI, retry/fail-closed, trigger precedence, lifecycle/restart/reaper, cache invalidation, model/default precedence, generated defaults, and state pollution.
- Planner seeds do not limit verifier discovery; verifiers still inspect package scope, assigned Slices, changed code/diff, tests, expectations, and known failure modes for emergent triggered-risk rows.
- Do not create a second command ledger in the registry.
- Batch broad or expensive full-suite, generated-contract, typecheck, or lint commands at integration/final gates unless they are cheap by project convention or the only credible package proof.
- When runtime cost or uncertainty leaves material execution feasibility unresolved, record in existing package
  `Notes` or verification expectations:
  authoritative command/harness/contract/fixture sources, preconditions and cleanup, cost class, the smallest
  credible bounded probe or broad-only justification, broad-check placement, testing-authority provenance,
  and a spike/replan trigger. Exact budgets come from the resolved authority.

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

Documentation-only and reference-only packages still receive standard package verification; risk determines
whether verification is standard or enhanced, not whether it runs.

## Runtime Adjustment

The implementation orchestrator may merge, split, defer, or reorder planned packages when current package
status, closure complexity, file impact, proof readiness, Slice assignment, or previous merged work makes the
plan unsafe or inefficient. When one uncertainty gates several otherwise independent packages, retire it with
the smallest bounded readiness action before affected fanout; do not invent a dependency edge when dispatch
readiness alone is sufficient. State the reason before dispatch.

If adjustment changes package scope, Slice H3 assignment, dependencies, proof path, report path, or approved deferrals, route through artifact repair or explicit user approval. Do not silently downgrade verification depth while a triggering risk remains.

## Anti-Patterns

- One package per tiny edit or verification-only phase.
- Making E2E, probes, suites, inspections, or evidence/reporting a package without substantial reusable
  verification or test infrastructure.
- Maximizing sub-agent count.
- Leaving substantial independent packages serialized without a concrete dependency, file-impact, proof, or contract-safety reason.
- Splitting work touching the same files, Slice obligation, subsystem, or proof surface.
- Bundling unrelated subsystems into a vague mega-package.
- Marking packages parallel-safe without checking likely file/proof/contract overlap.
- Giving a package no primary paths when relevant paths are known.
- Duplicating package scope, assigned H3 IDs, proof evidence, review receipts, or lifecycle ledgers into the registry.
- Treating registry status, helper validation, package self-review, or chat summaries as package proof.
