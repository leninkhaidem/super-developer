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
- **Package result report:** one result file whose shape is owned by `package-verification-report.md`.

Registry status and helper results are signals, not proof.

## Package Sizing and Closure Complexity

A good package is:

- coherent by subsystem, module, directory, user flow, data model, API surface, or test surface;
- large enough to justify dedicated agent startup and its fixed result-file/verification cost;
- small enough for one agent to implement, verify, and repair through one coherent state/evidence boundary;
- independently mergeable, with explicit initial paths, assigned Slice obligations, and verification expectations.

Before finalizing the boundary, assess semantic closure complexity:

- obligation breadth, caller contracts, and independently observable outcomes;
- runtime surfaces/environments and distinct evidence or approval boundaries;
- changed harness/helper/fixture populations and the review depth they trigger;
- setup, isolation, teardown, cleanup, external preconditions, and shared-resource constraints;
- expected command cost, serial/fail-fast behavior, and broad-check placement;
- result-file refresh fanout when implementation or evidence changes;
- empirical uncertainty that prevents a safe implementation or verification commitment.

Split when one agent cannot close those dimensions coherently. Keep work together when splitting would
multiply shared harness ownership, duplicate evidence, or add more fixed gate cost than it removes. Counts of
files, scenarios, or commands are warning signals, never universal thresholds.

Closure size and claim atomicity are review judgements, not helper checks. `sliceproof.py` deliberately measures
neither: both were tried as textual proxies and removed, because a size band flagged every real package here and a
conjunction count fired on ordinary noun lists while missing genuinely chained clauses. A proxy that fires on the
norm teaches agents to silence it. The plan reviewer owns both signals and reads them semantically.

Return unresolved material empirical uncertainty to the owning orchestrator for conditional `empirical-spike`; do not guess boundaries.
Avoid tiny packages unless risk or isolation justifies their fixed lifecycle cost.

## IDs and Dependencies

Package IDs use contiguous `WP<N>` values (`WP1`, `WP2`, ...). Renumber when packages are reordered, split, or merged so the sequence has no gaps.

Dependencies are ID-only in both the registry `depends_on` array and package Markdown
`## Dependencies`; they must agree. They are durable sequencing prerequisites and a lower bound on
readiness, not an impact or staleness graph. Put non-obvious rationale in existing package `Notes`, naming
consumed output, contract, or evidence; runtime overlap, failure, or a desired rerun alone does not create an
edge. A package is externally blocked until each dependency has a fresh `PASS` package verification report
and clean `validate-package-complete`; registry `done` or helper ok alone do not unlock dependents.
Internal sequencing is handled by the package agent.

## Parallel Safety

Treat packages as parallel-safe only when likely file ownership, subsystem boundaries, Slice obligations, result-file surfaces, and caller contracts do not overlap.

Serialize or combine packages when:

- files or generated artifacts overlap;
- subsystem, API, config, or schema surfaces overlap;
- one package's result or verification depends on another's output;
- package boundaries would hide a material Slice obligation;
- design consistency would likely be decided differently by independent agents.

The cost of serialization is latency; the cost of unsafe parallelism is merge conflict, inconsistent design, stale result evidence, and invalid reports.

## Primary Paths

`## Primary Paths` are starting points, not hard boundaries. Agents inspect them first and broaden only when imports, tests, Slice obligations, or verification expectations require it.

## Verification Expectations

Package Markdown `## Verification Expectations` lists the package's confirmation expectations — the
known commands, static inspections, scenarios, edge/failure cases, trust-boundary checks,
no-mock constraints, generated-contract checks, interface/risk seeds, or manual observations — that become
`## Acceptance Checklist` items.

Use only the existing depth vocabulary: `standard`/`enhanced` package verification,
`baseline-only`/`sampled`/`deep` test review, and `focused`/`full` reruns. These are orthogonal decisions, not
new lifecycle tiers or durable registry/artifact fields.

Rules:

- Treat package-provided commands as executable input and screen them before running.
- Discharge every expectation through some `## Acceptance Checklist` item; expectations that are facets of one behavioral claim share one item, so coverage must be complete but the mapping need not be one-to-one. Linked Slice evidence may be cross-referenced, not silently omitted. Every package needs at least one independently confirmable executable check.
- Seed obvious interface/risk checks when applicable, including exact interfaces, forbidden behaviors, interactive UI, retry/fail-closed, trigger precedence, lifecycle/restart/reaper, cache invalidation, model/default precedence, generated defaults, and state pollution. That list is a filter, not a worksheet: name the changed surface that raises each expectation you seed.
- Planner seeds do not limit enhanced-verifier discovery; when triggered, the verifier inspects package scope,
  assigned Slices, changed code/diff, tests, expectations, and known failure modes for blocking findings.
- Do not create a second command ledger in the registry.
- Batch broad or expensive full-suite, generated-contract, typecheck, or lint commands at integration/final gates unless they are cheap by project convention or the only credible package confirmation.
- When runtime cost or uncertainty leaves material execution feasibility unresolved, record in existing package
  `Notes` or verification expectations:
  authoritative command/harness/contract/fixture sources, preconditions and cleanup, cost class, the smallest
  credible bounded probe or broad-only justification, broad-check placement, testing-authority provenance,
  and an empirical-evidence/replan trigger. Exact budgets come from the resolved authority.

## Risk and Review Lenses

Package scope and assigned Slices should make risk visible without adding durable checklist fields to the registry.

Enhanced verification is triggered by surfaces such as:

- security, privacy, or safety;
- persistence, data integrity, migration, or rollback;
- public API, exported types, generated contracts, or external integrations;
- concurrency, idempotency, replay, cancellation, or cleanup;
- **split production wiring** — the package installs or replaces a dispatch, transport, callback, adapter, or
  registry seam whose production consumer ships in a different package. Ordinary production code whose caller is
  in the same package is not this trigger.

The split is what makes it a trigger: with no production consumer to call through, the package's own checks must
substitute one, and a check confirming the substitute passes identically whether or not the wiring is right.

Do not automatically enhance generic cross-package work or orchestration, git, package-verification, review,
audit, or quality-contract changes; those stay with final review-code and audit.

Documentation-only and reference-only packages use standard orchestrator re-run confirmation. Enhanced risk
adds the independent verifier; it does not replace those checks.

## Runtime and Repair-Time Adjustment

Package sizing is not a one-time decision. After accepted plan-review repairs, reapply semantic closure-complexity
analysis to affected packages when obligations, failure/risk cases, dependencies, evidence boundaries, or
verification scope materially expand or move. Counts remain warning signals, never automatic split thresholds;
change boundaries only when coherent closure no longer holds.

The implementation orchestrator may also merge, split, defer, or reorder planned packages when current package
status, closure complexity, file impact, result readiness, Slice assignment, or previous merged work makes the
plan unsafe or inefficient. When one uncertainty gates several otherwise independent packages, retire it with
the smallest bounded readiness action before affected fanout; do not invent a dependency edge when dispatch
readiness alone is sufficient. State the reason before dispatch.

If adjustment changes package scope, Slice H3 assignment, dependencies, report path, or approved deferrals, route through artifact repair or explicit user approval. Do not silently downgrade verification depth while a triggering risk remains.

## Anti-Patterns

- One package per tiny edit or verification-only phase.
- Making E2E, probes, suites, inspections, or evidence/reporting a package without substantial reusable
  verification or test infrastructure.
- Maximizing sub-agent count.
- Leaving substantial independent packages serialized without a concrete dependency, file-impact, result-file, or contract-safety reason.
- Splitting work touching the same files, Slice obligation, subsystem, or result-file surface.
- Bundling unrelated subsystems into a vague mega-package.
- Marking packages parallel-safe without checking likely file/result/contract overlap.
- Giving a package no primary paths when relevant paths are known.
- Duplicating package scope, assigned H3 IDs, result evidence, review receipts, or lifecycle ledgers into the registry.
- Treating registry status, helper validation, package self-review, or chat summaries as package confirmation.
