# Generic Testing Reference

Use this reference for stack-agnostic test design, command safety, durable planning/reporting, and
write boundaries. It does not authorize stack-specific, live, browser, network, credentialed, or
configuration side effects by itself.

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
3. Preconditions, fixtures, seeded data, mocks/stubs, live services, and privacy constraints.
4. Actions/inputs, including boundary, negative, regression, and conditional cases when relevant.
5. Expected outputs, assertions, side effects, invariants, and cleanup expectations.
6. Determinism/isolation risks, command provenance or discovery blocker, and evidence format.
7. Unresolved risks, skipped scope, or approval-gated follow-up.

Maintainable tests are deterministic, behavior-focused, clear in name and setup, aligned with repo
conventions, minimal in mocking, and resilient to implementation-detail churn. Do not weaken a test
to make a product failure disappear.

## Command Safety Classifier

Record every proposed/run command as: command, cwd, provenance (repo file/script/doc or explicit user
instruction), mode, timeout, expected writes, environment assumptions without secrets, classification,
and approval/blocker reason.

Default-run only when all are true: repo-discovered, deterministic, non-destructive, non-network,
non-credentialed, non-watch, non-interactive, bounded, local to the repo, and no live/browser/service
or shared-data mutation risk. Use bounded timeouts and report spawned-process termination/cleanup.

Stop for explicit current-task approval before live-stack, browser E2E, network, credentialed,
destructive, production, data-mutating, dependency/tooling/config, CI, orchestration,
package-manifest, lockfile, watch/interactive, daemon/server, long-running, or opaque actions.
Script names such as `test` or `e2e` are not sufficient provenance; inspect what they run when safe.

## Durable Plan/Report Gate

Nontrivial/high-risk work includes live integration, browser E2E, cross-stack behavior, multi-scenario
coverage, risky data/setup, or approval-gated tooling/config changes. Before covered writes or
execution, create a Markdown plan, present it, and wait for explicit approval in the current task.
Reuse a repo convention; otherwise write collision-safe fallback paths:
`docs/testing/<topic>.test-plan.md` and `docs/testing/<topic>.test-report.md`.

Plan schema:

- Topic, scope, risk level, requester goal, and exclusions.
- Scenario-to-test mapping with mode, files/artifacts to change, commands, data/preconditions,
  cleanup, evidence, and redaction notes per scenario.
- Approval-gated actions not yet authorized, plus blockers and alternatives.

Report schema:

- Approved plan path/version and report date.
- Changed test artifacts by category.
- Scenario-to-test-to-evidence matrix with outcome, command, cwd, provenance, timeout,
  termination/cleanup status, sanitized snippets, artifact links, exclusions, and follow-up route.
- Redaction decisions for secrets, credentials, tokens, PII, proprietary content, screenshots,
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
  is uncertain; do not report it as a deterministic regression.
- `skipped/not-run`: out of scope or intentionally omitted, with reason.

Production/application/runtime fixes are out of scope. Report failing commands/assertions and route
product repair to the appropriate existing workflow with evidence.

## Write Boundary

Direct writes: tests, fixtures, test helpers, safe snapshots/golden data, and testing docs/plans/reports.
Approval required: dependencies, manifests, lockfiles, package-manager config, test tooling, browser
or reporting config, CI, orchestration, project-wide test config, and any production/runtime surface.
