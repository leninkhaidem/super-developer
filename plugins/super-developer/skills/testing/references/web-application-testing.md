# Web Application Testing Reference

Use this reference after the generic testing workflow when the requested surface is frontend,
backend web/API, full-stack, browser, UX, or a live development stack. It adds web-specific
coverage planning but does not authorize browser, live-stack, network, dependency, tooling,
configuration, CI, or orchestration side effects by itself.

## Discover Before Decisions

Inspect repo evidence before proposing commands, files, reports, or tool changes. Name each source
or blocker for:

- frontend, backend/API, full-stack, routing, service, and browser surfaces affected by the work;
- existing test directories, naming patterns, fixtures, helpers, seed data, snapshots, and reports;
- package/script, task runner, documented command, browser harness, dashboard/report, artifact,
  video/screenshot/env-toggle conventions;
- live-stack conventions such as dev URLs, local services, containers, databases, tenants, ports,
  credentials, health checks, and cleanup tools.

Do not invent a framework, package manager, Playwright, Allure, browser command, report command,
file layout, or live target when repo evidence is absent. Record unresolved discovery as a blocker.

## Coverage Selection

Stay framework-agnostic but coverage-opinionated. Prefer the smallest test level that proves the
behavior, but do not stop at unit tests when confidence depends on backend integration, live-stack
regression, frontend integration, or browser E2E behavior.

For every selected level, record target surface, environment, command/provenance or discovery
blocker, data/preconditions, assertions, cleanup, evidence, exclusions, and follow-up route:

- backend/API unit or local integration for isolated logic and local service boundaries;
- backend live integration for controlled non-production service-boundary regression;
- frontend unit/component/integration for user-visible UI logic under the project harness;
- browser E2E for delivered user journeys, browser state, navigation, forms, dialogs,
  permissions, visual states, and conditional UX behavior.

## Backend Live Integration

Use live integration only with explicit approval and only against a controlled non-production dev
stack. Do not target production, mutate shared unsafe data, depend on uncontrolled shared state, or
claim regression confidence from flaky/environment-dependent output.

A backend live integration plan/report must include:

- preflight: dev target source without secrets, service health, credentials/approval state,
  owned tenant/database or seed namespace, required ports/services, and command blocker status;
- data: owned or seeded records, unique run identifiers, idempotent setup, and repeatable cleanup;
- assertions: stable status, response shape, persistence/side effect, emitted event, or user-visible
  invariant rather than timing-only or incidental implementation details;
- cleanup: exact cleanup action, idempotency expectation, and cleanup status per scenario;
- evidence: `passed`, `failed`, or `blocked-precondition` with sanitized command output and a clear
  reason when a precondition, service, data set, dependency, or credential is unavailable.

## Browser E2E Approval Plan

Before writing browser E2E, backend live integration, cross-stack, or multi-scenario web tests,
create an approval-ready durable plan and wait for explicit current-task approval. Simple low-risk
unit tests may proceed under the generic workflow, but unit tests are not a substitute for required
web integration or UX evidence.

Each browser scenario should map delivered behavior to a user-visible journey and itemize:

- positive, negative, boundary, and conditional cases that matter to the delivered UX;
- required assertions for visible state, navigation, form validation, permissions, dialogs,
  persisted results, API-backed state, errors, and accessibility-relevant cues when applicable;
- preconditions, owned data, setup/cleanup, selected artifact mode, commands/blockers, and risk;
- exclusions for non-essential component internals or exhaustive combinations, plus follow-up routes
  for product failures, test defects, missing tooling, or blocked environments.

## Browser Evidence Modes

`human-review` mode requires itemized evidence per scenario/test: video artifacts,
screenshots/checkpoints, dashboard/report locations, command outcome, sanitized snippets, and cleanup
status. Missing/unmapped artifacts make UX evidence partial unless explicitly justified.

`regression` mode may deliberately reduce heavy artifacts such as always-on videos or extra
screenshots when the repo convention or user-approved plan allows it. It must still preserve
per-scenario status, failure evidence when available, command provenance, cleanup status, and a
report/dashboard location or sanitized local report output.

## Browser Stack Setup Boundary

When the task asks for browser E2E stack setup, env/artifact toggles, report dashboards, Playwright +
Allure, or a reusable convention where none exists, load the browser E2E stack setup reference named
by `SKILL.md` before proposing setup. The web plan should still name project equivalents for base
URL, evidence mode, video/screenshots, report output, artifact directories, commands, and every
approval-gated config or manifest change.

## Privacy and Tooling Fallback

Plan privacy/redaction before producing, linking, or reporting screenshots, videos, logs, dashboard
links, traces, or local paths. Mask or exclude credentials, tokens, PII, proprietary content,
customer data, and sensitive local environment details; do not paste secret-bearing URLs or logs.

Use an existing browser E2E/reporting stack when it meets scenario evidence and dashboard needs. If
it is incomplete, propose approval-gated enhancements first. If no adequate stack exists, propose
Playwright + Allure as a preferred baseline only as an approval-gated plan before installation,
config, manifest, lockfile, package-manager, CI, or orchestration changes. For an existing stack,
fall back to Playwright + Allure only when current tools cannot reasonably meet evidence/dashboard
needs and user approval exists.

## Output Checklist

Return discovered web conventions, selected test levels, approval plan/report paths, scenario-to-test
mapping, command provenance/blockers, data and cleanup plan/status, stack/env toggle convention,
artifact mode, itemized evidence or missing-artifact reason, redaction handling, outcomes,
exclusions, and follow-up routes.
