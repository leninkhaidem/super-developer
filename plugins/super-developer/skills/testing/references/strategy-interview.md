# Testing Strategy Interview Reference

Use this reference for explicit requests to initialize, update, adopt, migrate, link, or revise a
repository testing workflow. It supplies interview coverage and starter contracts for project docs;
it does not authorize test writes, command execution, installs, browser/live/network actions,
configuration changes, CI changes, or accepted workflow-doc writes without the normal approvals.

## Entry and Ordering

1. Inspect repo evidence first: stack manifests, scripts, test directories, fixtures, existing docs,
   CI/config, app surfaces, report locations, data/auth boundaries, and stale/conflict signals.
2. Treat existing testing docs as source material, not a reason to skip the interview.
3. Summarize the evidence, then ask one focused strategy question at a time. Include a
   recommendation and short options when useful; do not dump a broad questionnaire.
4. Start the user-facing strategy branch with the confidence outcome the user wants before choosing
   test levels, folders, templates, commands, approval gates, or tools. Use confidence examples only
   as optional explanation, not as a mandatory visible profile menu.
5. Continue until every mandatory core domain is answered, marked not applicable from evidence, or
   explicitly deferred by the user with the risk recorded in the draft.

## Mandatory Core Domains

Resolve these for initialize/update mode before accepted workflow-doc writes:

- tech stack, product/test surfaces, and risk boundaries the workflow must cover;
- folder structure for new test plans, authored tests, fixtures/helpers, evidence, and reports;
- feature/domain test plan policy, including when a plan gates authoring or execution;
- user-friendly execution choices, current-task approvals, stop conditions, and command categories;
- evidence/reporting expectations, redaction rules, and durable report locations;
- data/setup/cleanup policy for local, integration, live, browser, or mutating tests;
- legacy tests/docs handling: stay put by default, plus adopt/migrate/link choices when requested;
- stale, ambiguous, conflicting, or unsafe workflow update procedure.

## Conditional Domains

Activate browser/web questions only when repo evidence, user scope, or selected confidence goals show
browser, frontend, web UX, UI-backed persistence, live web/API, or browser tooling relevance. When
active, evaluate material subcoverage such as accessibility cues, responsive/viewport behavior,
cross-browser needs, screenshots/video, user journeys, browser state, and UI-backed persistence. If
inactive, record why browser/web coverage is not part of the current workflow instead of imposing it.

Other conditional domains, such as backend live integration or data-heavy service tests, should be
raised only when evidence or the user's confidence goal makes them material.

## Persisted Output

Interview decisions feed the repository testing workflow, not a default standalone questionnaire.
Draft or revise `docs/testing/workflow.md` and linked `docs/testing/*` companions with the accepted
strategy decisions, then ask for explicit current-task approval before writing them. A separate
checklist or decision record is optional for large or high-risk strategy updates, not the default.

The workflow draft should name: confidence goals; mandatory and active conditional domains; plan,
test, evidence, and report paths; execution choices and approvals; reliability/cleanup semantics;
legacy stance; companion docs; redaction; and the update procedure.

## Starter Feature or Domain Test Plan

Keep plans high-level and reviewable. They are scenario/deliverable contracts, not command recipes.

- Plan path/version, owner or requester, confidence goal, scope, exclusions, and risk level.
- Scenario list with user/business intent, selected test surface, deliverables to author or execute,
  evidence expected, and approval gates.
- Data/setup/cleanup needs, isolation or unique-run approach, privacy/redaction notes, and blockers.
- Execution choices under consideration and choices intentionally not selected.
- Open questions, explicitly deferred domains, and follow-up risks.

## Starter Plan-to-Result Report

Keep reports concise and durable enough for later readers without raw log dumps.

- Approved plan path/version, report date, selected execution choice(s), and current approvals used.
- Scenario-to-test/result mapping with files/artifacts, command or not-run reason, outcome, and
  sanitized evidence links or snippets.
- Skipped/not-run items, blocked preconditions, unsafe-needs-approval items, and exclusions.
- Redaction actions for secrets, credentials, tokens, PII, proprietary content, screenshots, videos,
  logs, local paths, and environment details.
- Cleanup status, flaky or inconclusive signals, product-failure route, and follow-up risks.

## Starter Execution Choices

The final workflow may rename these, but it should keep plain user-facing choices and approval gates:

- **Focused check**: smallest safe local command or inspection that exercises the changed surface.
- **Feature confidence**: planned scenario set for the feature/domain, often across multiple levels.
- **Browser review**: active only for browser/web scope; may require screenshots/video or dashboard.
- **Broad regression**: wider suite or matrix before a lifecycle gate; approval-gated when costly,
  live, browser, networked, long-running, or otherwise risky.
- **Do not run yet**: intentional deferral; report as skipped/not-run with reason, never as passed.

Each choice should document what it proves, required approvals, command/evidence expectations,
stop conditions, cleanup duties, and how results map back to the approved plan.

## Reliability, Data, and Cleanup Defaults

Use strict outcome language: passed, failed, blocked-precondition, unsafe-needs-approval,
inconclusive/flaky, and skipped/not-run or the project-approved equivalents. Flaky, timed-out,
ambiguous, or cleanup-uncertain results are not passes.

Live, integration, browser, or data-mutating tests require owned or isolated data, idempotent setup
or equivalent isolation, unique run identifiers when useful, cleanup expectations, cleanup status,
and explicit follow-up when cleanup fails or is uncertain. Do not default to uncontrolled shared-data
mutation or hide cleanup failures in raw logs.

## Legacy and Migration Prompts

Recommend a clean structure for new plans/tests going forward, but leave legacy tests where they are
unless the user explicitly asks for migration. In adopt/migrate/link discussions, ask which existing
docs or tests remain authoritative source material, what should be linked as a companion, what should
move into the canonical workflow, and what risks are deferred to a separate migration session.
