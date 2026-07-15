# Generic Testing Reference

Use this reference only as an optional proposal/adaptation aid for stack-agnostic test design,
command safety, durable planning/reporting, and write boundaries. Approved project workflow docs
(`docs/testing/workflow.md` and linked companions) and exact task-local testing authority govern
repository-specific testing behavior; this reference must not override them or authorize standalone
test edits/runs by itself. It does not authorize stack-specific, live, browser, network,
credentialed, dependency, tooling, configuration, CI, or orchestration side effects by itself.

## Test Modes

Each chosen mode must state target surface, environment, command or discovery blocker, data and
cleanup, assertions/invariants, evidence, and exclusions.

- **Unit**: isolated function/module behavior; local fixtures or mocks only; fastest deterministic
  command available from repo evidence; evidence is assertion result plus focused snippet.
- **Local integration**: multiple local components in one process or controlled local fixture; no
  live service/network/shared data by default; include setup/teardown and side-effect assertions.
- **Live-stack integration**: controlled non-production dev stack or service boundary. Requires
  explicit approval, preflight, owned/seeded data, cleanup/idempotency, stable assertions, and a
  clear `blocked-precondition` outcome when the environment is unavailable.
- **Frontend unit/component/integration**: user-visible UI logic or component behavior under the
  project's local harness. Browser or live backend use is not default-safe unless separately approved.
- **Browser E2E**: realistic browser journeys for delivered UX behavior. Requires explicit approval,
  environment/data preflight, artifact/redaction plan, bounded execution, and cleanup reporting.

Prefer the smallest mode that proves the behavior, but do not stop at unit tests when the risk is at
an integration, service, UI, or user-journey boundary.

## Test Case Structure

For each case or scenario capture:

1. Objective/behavior under test and why it matters.
2. Scope/test level and selected mode.
3. Preconditions, fixtures, seeded data, mocks/stubs, live services, privacy constraints, and authoritative
   contract/configuration sources. Validate data shapes, limits, defaults, client/runtime compatibility, and
   shared resource/rate/concurrency budgets when applicable.
4. Actions/inputs, including boundary, negative, regression, and conditional cases when relevant.
5. Expected outputs, assertions, side effects, invariants, and cleanup expectations.
6. Determinism/isolation risks, command provenance or discovery blocker, and evidence format.
7. Unresolved risks, skipped scope, or approval-gated follow-up.

Maintainable tests are deterministic, behavior-focused, clear in name and setup, aligned with repo
conventions, minimal in mocking, and resilient to implementation-detail churn. Do not weaken a test
to make a product failure disappear.

## Executable Verification Preflight

Before executable verification, establish all of the following from project authority and repository evidence:

- command/harness provenance and a configured, discoverable runner rather than a guessed command;
- prerequisites and compatibility, including dependencies, fixtures/data, services, permissions, and resources;
- a safe non-production environment and explicit target, with shared or live effects separately approved;
- bounded, idempotent setup plus owned teardown/cleanup, including interruption and partial-failure paths;
- an evidence destination/capture capability for the required confidence, with secrets and sensitive data redacted;
- assertions, checkpoints, and terminal signals strong enough for the stated confidence goal, not mere execution;
- bounded action/suite timeouts, observable progress, owned-process termination, and cleanup verification.

A failed, missing, stale, or uncertain item blocks execution or narrows it to an approved safe probe. Domain
references may specialize this preflight but cannot silently weaken it or override project authority.

## Command Safety and Execution Discipline

For every proposed/run command, record a stable identity, command, cwd, repo/user provenance, selected mode,
scope, expected writes, environment assumptions without secrets, classification, approval/blocker reason,
timeout, progress/completion signal, termination method, and cleanup obligation.

Default-run only when the routine-safe fallback is satisfied: repo-local/project-owned, deterministic,
non-destructive, non-network, non-credentialed, non-watch, non-interactive, bounded, local, clear provenance,
no source/fixture/snapshot/config writes except known local cache/report artifacts, trivial owned cleanup, and
free of live/browser/service/shared-data risk. Stop for explicit approval before live, browser, network,
credentialed, destructive, production, mutating, dependency/config/CI, orchestration, manifest/lockfile,
interactive, daemon/server, long-running, or opaque actions. A script name is not provenance; inspect what it
runs when safe.

For costly or uncertain execution, use a readiness ladder: deterministic contract/fixture/config preflight,
command/test discovery, then the smallest credible bounded check. Broaden after clean narrower evidence; when no
credible narrower check exists, document why and run an explicitly bounded broad command after clean preflight
and discovery. Keep independent ready work parallel; do not impose universal serialization.

Use project-approved action, barrier, case, and suite budgets. Inner actions must not inherit an entire outer
timeout. Require observable progress and an awaited terminal state. On timeout/cancel/interruption, terminate
owned descendants, await exit, run cleanup, and report cleanup status; uncertain termination or cleanup is not a
pass. Do not enlarge timeouts to mask missing preconditions, bad selectors, unresolved barriers, or deadlocks.
Do not repeat unchanged failing assertions or commands; require a relevant state or diagnostic-strategy change.
Return control after each bounded stage or failure instead of hiding follow-up runs in one opaque long call.

## Durable Plan/Report Gate

Use this schema when the approved project workflow calls for a plan/report or when drafting a
workflow proposal. Nontrivial/high-risk work includes live integration, browser E2E, cross-stack
behavior, multi-scenario coverage, risky data/setup, or approval-gated tooling/config changes. Before
covered writes or execution, create a Markdown plan, present it, and wait for explicit approval in
the current task. Reuse a repo convention; otherwise propose collision-safe fallback paths:
`docs/testing/<topic>.test-plan.md` and `docs/testing/<topic>.test-report.md`. These plan/report
paths are not substitutes for the canonical workflow entry point.

Feature/domain plan starter (high-level scenario contract, not a command recipe):

- Plan path/version, topic, scope, risk level, confidence goal, requester goal, and exclusions.
- Scenario-to-deliverable mapping with selected surface/mode, files or artifacts expected, evidence
  needed, data/preconditions, cleanup, redaction, and approval gates per scenario.
- Selected execution choice(s) under consideration, choices intentionally not run, blockers, and
  alternatives.

Concise plan-to-result report starter:

- Approved plan path/version, report date, selected execution choice(s), and approvals used.
- Changed test artifacts by category.
- Scenario-to-test-to-evidence matrix with outcome, command or not-run reason, cwd, provenance,
  timeout, termination/cleanup status, sanitized snippets, artifact links, exclusions, and route.
- Skipped/not-run items, blocked approvals/preconditions, cleanup-failed/uncertain follow-up, and
  redaction decisions for secrets, credentials, tokens, PII, proprietary content, screenshots,
  videos, logs, and local environment details.

## Outcomes and Follow-up

Use only these outcomes: `passed`, `failed`, `blocked-precondition`, `unsafe-needs-approval`,
`inconclusive/flaky`, and `skipped/not-run`.

- `passed`: assertions succeeded under the stated preconditions.
- `failed`: deterministic test failure or test-artifact error with reproduction evidence.
- `blocked-precondition`: required command, service, data, dependency, credential, or environment was
  unavailable and no unsafe action was taken.
- `unsafe-needs-approval`: a command/write was correctly not run because it needs approval.
- `inconclusive/flaky`: result is ambiguous, flaky, timed out without deterministic signal, or cleanup
  is uncertain; do not count it as passed or report it as a deterministic regression.
- `skipped/not-run`: out of scope or intentionally omitted, with reason.

Production/application/runtime fixes are out of scope. Report failing commands/assertions and route
product repair to the appropriate existing workflow with evidence.

Starter execution choices may be renamed by the accepted workflow, but should stay user-facing: focused
check, feature confidence, active browser review, broad regression, or do not run yet. Each choice
needs what it proves, approvals, stop conditions, evidence, and cleanup/reporting expectations.

## Write Boundary

Within an approved workflow and delegated scope, test-surface writes may include tests, fixtures,
test helpers, safe snapshots/golden data, and testing docs/plans/reports. Approval is required for
workflow documentation writes, dependencies, manifests, lockfiles, package-manager config, test
tooling, browser or reporting config, CI, orchestration, project-wide test config, test writes when
the project workflow requires approval, and any production/runtime surface.
