---
name: testing
description: >
  Author test cases and run safe local tests across stacks. Use when asked for testing help,
  test plans/cases, test-only artifacts, or safe local test execution. Do not use for bug
  fixing, feature implementation, code review, audit, or release work.
---

# Testing

Author maintainable tests and produce trustworthy test evidence in the active repository without
assuming a language, framework, package manager, browser tool, deployment target, or external
workflow artifact store.

## Always

- Standalone-first: direct use returns a structured plan/report from the active repo or worktree;
  do not require external workflow artifacts or modify existing workflow gates.
- Discover repository conventions before proposing commands, file locations, fixtures, snapshots,
  or report paths. Do not invent commands when repo evidence is absent.
- Direct writes are limited to test files, fixtures, test helpers, safe snapshots/golden data, and
  testing docs/plans/reports.
- Do not edit production/application/runtime code, schemas, migrations, public APIs, product config,
  or behavior; do not weaken tests to hide failures. Route product failures to the owning workflow
  with reproduction evidence.
- Dependency, tooling, package manifest, lockfile, project-wide test config, CI, browser/reporting
  config, and orchestration edits are approval-gated proposals, not default actions.
- Classify every proposed or executed command before running it. Safe local commands may run by
  default only when repo-discovered, deterministic, non-destructive, non-network, non-credentialed,
  non-watch, non-interactive, bounded, and free of live/browser/service/data mutation risk.
- Stop/ask before live-stack, browser E2E, network, credentialed, destructive, production,
  data-mutating, dependency/tooling/config, CI, orchestration, package-manifest, lockfile,
  watch/interactive, daemon/server, long-running, or opaque actions.
- Use bounded timeouts for executed commands; terminate or clean up spawned processes and report
  timeout, termination, and cleanup status.
- Redact secrets, credentials, tokens, PII, proprietary content, sensitive screenshots/videos/logs,
  and local environment details from prompts, files, snippets, and reports.

## Do

1. Resolve the requested behavior, test surface, target repo/worktree, risk level, and whether the
   user wants planning only, test authoring, safe execution, or a report.
2. Inspect existing test conventions read-only: test directories, naming, fixtures, helpers,
   package/scripts, documented commands, generated artifacts, and project reporting patterns.
3. Select the smallest meaningful test mode(s), explicitly distinguishing unit, local integration,
   live-stack integration, frontend unit/component/integration, and browser E2E. For each selected
   mode, name target surface, required environment, command or discovery blocker, data/cleanup,
   assertions, and evidence.
4. For detailed test-case structure, command classification, durable plan/report schema, or
   nontrivial/high-risk work, load `references/core/generic-testing.md` before drafting artifacts or
   executing commands. For frontend, backend web/API, full-stack, browser, UX, or live dev-stack
   testing, also load `references/web/application-testing.md` after generic safety and convention
   discovery. For browser E2E stack setup, evidence toggles, reporting, or Playwright + Allure
   proposals, load `references/web/browser-e2e-stack-setup.md` before proposing setup or config.
5. If work is nontrivial/high-risk, first create an approval-ready Markdown plan using the repo's
   convention or fallback `docs/testing/<topic>.test-plan.md`; present it and wait for explicit
   current-task approval before covered test writes or execution. After execution, write the paired
   durable report.
6. For simple low-risk test authoring, write only in allowed test/documentation surfaces and follow
   the discovered project style. Keep tests deterministic, behavior-focused, named clearly, and
   resistant to over-mocking or brittle implementation-detail assertions.
7. Before execution, list each command with provenance, cwd, classification, timeout, environment
   assumptions without secrets, and why it is safe, blocked, or approval-gated.
8. Run only safe-local or explicitly approved commands. Capture sanitized evidence, exact result,
   outcome, timeout/termination, cleanup status, and any skipped/blocked reason.
9. If tests fail, distinguish test defects, product failures, precondition blockers, flaky or
   inconclusive evidence, and unsafe unrun actions. Do not repair production code; return the
   failing assertion/command and recommended route such as `diagnose-and-fix` or `implementation-plan`.

## Load if needed

- Detailed mode taxonomy, test-case structure, command classifier, durable Markdown plan/report
  schema, report outcomes, write boundaries, and redaction checklist → `references/core/generic-testing.md`
- Framework-agnostic web application coverage for frontend, backend web/API, full-stack, browser,
  UX, or live dev-stack testing → `references/web/application-testing.md`
- Browser E2E stack setup, env/artifact toggles, report dashboards, Playwright + Allure baseline,
  or missing inadequate browser/reporting conventions → `references/web/browser-e2e-stack-setup.md`
- The request is actually bug diagnosis/fixing, feature implementation, code review, audit,
  release, or README/docs polish → use the owning skill instead of this one.
- Another future stack-specific reference exists and the repo/user context needs it → load that
  reference only after generic safety and convention discovery.

## Stop if

- The requested command or write crosses an approval-gated category and is not explicitly approved
  in the current task.
- Nontrivial/high-risk work lacks an approved durable plan for the covered writes/execution.
- The next useful step needs credentials, network/live services, production access, browser E2E,
  data mutation, dependency installation, config/CI/orchestration edits, or a daemon/server.
- Existing repo conventions are absent or contradictory enough that command/file choices would be
  invented rather than evidenced.
- Passing the tests requires production/application/runtime code changes or weakening assertions.
- Sensitive data would be recorded without a clear redaction or exclusion plan.

## Output

Return scope and selected test modes, plan/report paths if used, files changed by allowed category,
commands proposed/run with provenance/cwd/classification/timeout/outcome, sanitized evidence,
cleanup status, exclusions, approval blockers, product-failure routing, and unresolved risks.
