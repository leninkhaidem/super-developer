# Generic Testing Reference

Use this reference only as an optional proposal/adaptation aid for stack-agnostic test design,
command safety, durable planning/reporting, and write boundaries. Approved project workflow docs
(`docs/testing/workflow.md` and linked companions) and exact task-local testing authority govern
repository-specific testing behavior; this reference must not override them or authorize standalone
test edits/runs by itself. It does not authorize stack-specific, live, browser, network,
credentialed, dependency, tooling, configuration, CI, or orchestration side effects by itself.

## Minimum Sufficient Causal Evidence

Select the smallest maintainable evidence set that credibly demonstrates:

1. each accepted observable behavior through its actual production path;
2. each materially relevant forbidden/failure outcome;
3. each triggered security, privacy, safety, data, concurrency, lifecycle, compatibility, or public-contract risk;
4. each meaningful consumed/integration contract at its owning layer; and
5. a regression for a distinct discovered defect mechanism when needed.

Treat these as confidence obligations, not a test inventory. Consolidate overlapping obligations: one causal test
or observation may prove several requirements or report rows. Select the cheapest credible evidence level that
forces the production precondition/branch, observes a real result/transition/side effect, falsifies the forbidden
outcome, and would fail if the invariant broke. Disclose mocks, fixtures, cache hits, hooks, synthetic substitutes,
and shared-state effects; labels or counters alone are not evidence.

Once accepted behaviors and triggered risks have credible causal evidence and required commands pass, stop adding
tests. Do not add speculative permutations, duplicate confidence at several layers, trivial wiring/type checks,
private-detail tests already covered by behavior, or tests merely to populate a matrix/report. Reuse existing
harnesses; add infrastructure only when accepted behavior cannot otherwise be credibly demonstrated.

Test count, changed test lines, test-to-production ratio, coverage percentage, and suite volume are not gates or
required report fields. Do not perform exhaustive suite review. Existing tests are not rejected, deleted, or
cleaned up solely because they are numerous; they block only for a concrete defect: false-positive evidence,
incorrect/weakened assertions, hidden skip/focus/xfail, flaky/inconclusive outcome, unsafe side effects, materially
unacceptable required runtime, or a harness/configuration change that undermines confidence.

## Test Modes

Each selected mode states surface, environment, command/discovery blocker, data/cleanup, assertions, evidence, and
exclusions. Prefer the cheapest mode that credibly proves the behavior; do not stop at unit level when risk lives
at integration, service, UI, or user-journey boundary.

- **Unit:** isolated function/module with local fixtures/mocks and fastest repository-backed deterministic command.
- **Local integration:** controlled local components/fixtures, explicit setup/teardown and side-effect assertions.
- **Live-stack integration:** controlled non-production service boundary; exact approval, owned data, cleanup,
  stable assertions, and `blocked-precondition` when unavailable.
- **Frontend unit/component/integration:** user-visible logic under the project harness; live backend is separate.
- **Browser E2E:** realistic journey; exact approval, environment/data preflight, redaction, bounds, and cleanup.

## Causal Case Shape

For each selected scenario capture objective and risk; mode/surface; preconditions/data/mocks/services/privacy and
authoritative contract; action/input; expected outputs/side effects/forbidden outcomes; isolation/cleanup; command
provenance and evidence; unresolved or approval-gated scope. Validate relevant shapes, limits, defaults,
compatibility, shared-resource/rate/concurrency bounds, and failure behavior. Keep tests deterministic,
behavior-focused, convention-aligned, minimally mocked, and resilient to private implementation churn. Never
weaken an assertion to hide a product failure.

## Executable Verification Preflight

Before execution establish from project authority/repository evidence:

- discoverable command/harness provenance rather than a guessed command;
- dependencies, fixtures/data, services, permissions, compatibility, and resources;
- safe non-production target; separate authority for shared/live effects;
- bounded idempotent setup and owned interruption/partial-failure cleanup;
- redacted evidence destination and discriminating assertions/terminal signals; and
- bounded action/suite timeouts, observable progress, owned-process termination, and cleanup verification.

A missing/stale/uncertain item blocks execution or narrows it to an approved safe probe.

## Command Safety and Execution Discipline

Record stable command identity, cwd, repository/user provenance, mode/scope, expected writes, sanitized environment
assumptions, approval/blocker, timeout, progress/completion, termination, and cleanup. Default-run only a
repository-local, project-owned, deterministic, non-destructive, non-network, non-credentialed, non-watch,
non-interactive, bounded local command with clear provenance, no source/fixture/snapshot/config writes except known
cache/report artifacts, and trivial owned cleanup. Stop before live/browser/shared-data, destructive, production,
mutating, dependency/config/CI/orchestration, manifest/lockfile, interactive, daemon/server, long-running, or opaque
actions unless exact authority covers them.

For costly/uncertain work use a readiness ladder: deterministic contract/fixture/config preflight, command/test
discovery, then smallest credible bounded check. For shared discovery/registration/global state, lifecycle,
recursive control flow, or public/generated contracts, place the earliest credible affected broad regression
before evidence freeze. Broaden only when narrower evidence cannot establish the obligation. When no credible
narrower check exists, document why and run an explicitly bounded broad command after clean preflight. Keep
independent ready work parallel; do not impose universal serialization.

Use project-approved budgets. Inner actions do not inherit an outer timeout. On timeout/cancel/interruption,
terminate owned descendants, await exit, clean up, and report status; uncertain termination or cleanup is not a
pass. Do not inflate timeouts or repeat unchanged failures. Require relevant state/evidence/strategy change and
return after each bounded stage or failure.

## Durable Plan/Report Gate

Use only when approved workflow requires it. Nontrivial/high-risk work includes live integration, browser E2E,
cross-stack behavior, multi-scenario coverage, risky data/setup, or approval-gated tooling/config changes. For a
standalone testing task, create a Markdown plan before covered writes/execution, present it, and wait for explicit
task-local approval. In a planned-feature auto-resolve flow, the sole Implementation Authorization must already
name the testing writes, commands, effects, bounds, and cleanup; consume that authority and never add a routine
second testing prompt. Reuse repository paths; fallback examples are `docs/testing/<topic>.test-plan.md` and
`docs/testing/<topic>.test-report.md`. These paths do not replace the canonical workflow entry point.

Feature/domain plan starter (high-level scenario contract, not a command recipe): plan/version/topic, confidence
obligations, selected minimum scenarios/modes, expected artifacts/evidence, data/cleanup/redaction, approvals,
exclusions, choices not run, blockers, and alternatives.

Concise report: authority and approvals; Selected Causal Evidence mapping each chosen anchor to behavior/risk,
sufficiency rationale, substitute disclosure, command/outcome/cleanup; skipped/blocked items; sanitized artifacts;
and follow-up. Do not report test volume metrics or imply one evidence item per row.

## Outcomes and Follow-up

Use `passed`, `failed`, `blocked-precondition`, `unsafe-needs-approval`, `inconclusive/flaky`, and
`skipped/not-run`. Only discriminating assertions under stated preconditions pass. Ambiguity, timeout without signal,
flakiness, or cleanup uncertainty never passes. Production fixes are out of scope; report reproduction to owner.

Starter execution choices may be renamed by the accepted workflow, but should stay user-facing: focused check,
feature confidence, active browser review, broad regression, or do not run yet. Each choice needs what it proves,
approvals, stop conditions, evidence, and cleanup/reporting expectations.

## Write Boundary

Within approved authority, test writes may include selected tests, fixtures, helpers, safe snapshots/golden data,
and testing docs/plans/reports. Separate approval is required for workflow docs, dependencies/manifests/lockfiles,
package-manager/test/browser/reporting config, CI/orchestration, project-wide config, workflow-gated test writes,
and production/runtime surfaces.
