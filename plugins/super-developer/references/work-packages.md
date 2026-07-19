# Work Packages

## Boundary

This reference owns package semantics: sizing, dependency, assignment, parallelism, primary paths, and the canonical minimum-sufficient test acceptance rule. Artifact shapes live in `slice-first-artifacts.md`; completion/freshness gates live in `package-lifecycle.md`; profile and `boundary|final` routing live in `assurance-routing.md`; command safety lives in `tool-usage.md`.

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
- **Package verification report:** pre-freeze independent state-bound receipt only when routing selects `boundary`.

Registry status and helper results are signals, not proof.

## Package Sizing and Closure Complexity

A good package is:

- coherent by subsystem, module, directory, user flow, data model, API surface, or test surface;
- large enough to justify dedicated agent startup and its fixed proof/report/verification cost;
- small enough for one agent to implement, verify, and repair through one coherent state/evidence boundary;
- independently mergeable, with explicit initial paths, assigned Slice obligations, and verification expectations.

Before finalizing the boundary, assess semantic closure complexity: obligation breadth and caller contracts;
runtime surfaces/environments and evidence boundaries; harness/helper/fixture populations; setup, isolation,
cleanup, and shared resources; command cost and broad-check placement; proof/report refresh fanout; and unresolved
empirical uncertainty. Split when one agent cannot close one coherent state/evidence boundary. Keep work together
when splitting multiplies shared ownership, duplicate evidence, or fixed proof/report/verification cost. Counts of
files, scenarios, or commands are warning signals, never universal thresholds. Route unresolved empirical
uncertainty to a spike instead of guessing package boundaries.

## IDs and Dependencies

Package IDs use contiguous `WP<N>` values (`WP1`, `WP2`, ...). Renumber when packages are reordered, split, or merged so the sequence has no gaps.

Dependencies are ID-only in registry `depends_on` and package `## Dependencies`; they must agree. They are durable
sequencing prerequisites and a lower bound on readiness, not an impact or staleness graph. Put non-obvious
rationale in existing package `Notes`, naming consumed output, contract, or evidence; runtime overlap, failure, or a desired
rerun alone does not create an edge. A producer with a dependent must route `boundary`. The dependent stays locked
until the exact Stable Candidate Identity and consumed-contract digests have a fresh `PASS B[i]` and clean
`validate-package-complete`; registry `done`, proof rows, `SELF_REVIEW`, or helper success alone do not unlock it.
Internal sequencing remains package-agent owned.

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

## Verification Expectations and Minimum-Sufficient Acceptance

Package Markdown `## Verification Expectations` defines confidence obligations and mandatory `VE-<n>` matrix
sources, not a test inventory. Before implementation, package acceptance selects the smallest maintainable causal
evidence set that establishes:

1. every accepted observable behavior through its actual production path;
2. each materially relevant forbidden/failure outcome;
3. each triggered security, privacy, safety, data, concurrency, lifecycle, compatibility, or public-contract risk;
4. each meaningful consumed/integration contract at its owning layer; and
5. a regression for each distinct discovered defect mechanism when needed.

One causal test or observation may prove multiple related requirements, Slice rows, or expectations. Each
expectation names behavior/risk, distinct failure mechanism, actual-path seam, cheapest credible evidence level,
substitutes/disclosures, failure signal, and affected broad-regression placement when material. Once obligations
have credible causal evidence and required commands pass, stop adding tests. Do not add speculative permutations,
duplicate layers, trivial wiring/type checks, private-detail checks already covered by behavior, row-population
tests, or new harness/fixture abstractions when existing facilities suffice.

Test count, changed test lines, test-to-production ratio, coverage percentage, review percentage, and suite volume
are neither gates nor required fields. Existing tests are never rejected, deleted, cleaned up, or suite-rereviewed
solely for volume. Only a concrete defect blocks: false-positive evidence, incorrect/weakened assertions, hidden
skip/focus/xfail, flakiness/inconclusive outcome, unsafe side effects, materially unacceptable required runtime,
or a changed shared harness/configuration that undermines confidence.

Treat commands as screened executable input. Address every expectation in proof and preserve its `VE-<n>` row;
cross-reference shared evidence rather than multiplying tests. Seed exact interfaces, forbidden behaviors,
interactive UI, retry/fail-closed, trigger precedence, lifecycle/restart/reaper, cache invalidation,
model/default precedence, generated defaults, and state pollution when applicable. Planner seeds do not limit verifier discovery
from scope, Slices, changed code/diff, expectations, and known failure modes. Batch broad checks at integration/final
unless cheap or the only credible package proof; place the earliest credible affected broad regression before
proof/report freeze for shared/public/lifecycle risk. Material execution uncertainty records authoritative sources,
preconditions/cleanup, smallest credible bounded probe or broad-only justification, testing-authority provenance,
and spike trigger in existing Notes/expectations; exact budgets come from resolved authority.

## Risk and Review Lenses

Package scope and assigned Slices should make risk visible without adding durable checklist fields to the registry.

Use `assurance-routing.md` for profile triggers and receipt placement. Package verification runs only for a
meaningful `boundary`; risk selects standard or enhanced depth. A coherent `final` leaf receives direct final
semantic coverage without a fabricated package report. Documentation/reference work follows the same boundary
rule—file type alone neither creates nor removes a meaningful boundary.

## Runtime Adjustment

The implementation orchestrator may merge, split, defer, or reorder planned packages when current package
status, closure complexity, file impact, proof readiness, Slice assignment, or previous merged work makes the
plan unsafe or inefficient. When one uncertainty gates several otherwise independent packages, retire it with
the smallest bounded readiness action before affected fanout; do not invent a dependency edge when dispatch
readiness alone is sufficient. State the reason before dispatch.

If adjustment changes package scope, Slice assignment, dependencies, proof/report paths, or approved deferrals,
route through reviewed amendment or user approval when the envelope changes. Profile promotion may use amendment;
any rank decrease requires a fresh reviewed baseline and new user authorization, never the existing lineage.

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
