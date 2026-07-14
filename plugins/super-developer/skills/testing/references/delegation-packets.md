# Testing Delegation Packets Reference

Use this reference only after testing authority is resolved for the exact downstream authoring,
alteration, execution, or report task. The main agent remains an orchestrator: it documents/updates
workflow docs after approval, resolves one-off authority when allowed, then delegates. If no executor
or sub-agent mechanism is available, return the packet to the user and stop instead of doing the work
directly.

## Delegation Preconditions

Before delegation, the orchestrator must establish:

- authority state: accepted/current `docs/testing/workflow.md` plus companions; or task-local Testing
  Authorization for one focused delegated act. Broad, recurring, browser/E2E, live, shared-data,
  network, credentialed, dependency/config/CI/orchestration, multi-stage, long-running, destructive,
  or unclear-cleanup delegated work requires canonical workflow authority;
- candidate handling: any adopted, migrated, or linked candidate is incorporated or referenced by the
  canonical workflow entry before it can govern reusable/high-risk delegated work;
- companion/source docs: relevant `docs/testing/*`, approved source docs, or explicit none-needed;
- allowed scope: files, test surfaces, commands, writes, evidence destinations, and cleanup ownership;
- approved plan path/version when the authority requires a feature/domain plan, or an explicit
  no-plan-needed reason from the authority;
- selected execution choice(s), what each choice is intended to prove, and choices intentionally
  skipped or not run;
- approval boundaries: workflow doc writes, test writes when the authority requires approval,
  browser/live/network/dependency/config/CI/orchestration actions, unsafe commands, and other gated
  side effects are blocked unless explicitly approved in the current task;
- stop conditions: insufficient/stale/conflicting authority, product/runtime fix needed, unsafe
  command, credentials/secrets, uncontrolled data mutation, absent preconditions, or unredactable evidence.

## Packet Shape

An authority-aware packet should include:

```markdown
Testing delegation packet
- User goal: <requested testing outcome>
- Target repo/worktree: <path or explicit repo context>
- Testing authority: <canonical-workflow | task-local Testing Authorization>
- Authority source: <docs/testing/workflow.md + companions, or exact one-off approval text>
- Required first step: read the authority source; receipt/report must cite it.
- Approved plan path/version: <path+version, or authority-approved no-plan reason>
- Selected execution choice(s): <focused check/feature confidence/browser review/broad regression/do not run yet/etc.>
- Allowed scope: <test files/fixtures/helpers/docs/commands/evidence surfaces>
- Disallowed scope: <production/runtime code, unapproved config/dependencies/CI/orchestration, etc.>
- Current-task approvals already granted: <exact approvals or none>
- Approval-gated actions to stop for: <commands/writes/browser/live/network/etc.>
- Command safety: classify commands, use bounded timeouts, no unsafe/default live side effects.
- Runtime envelope: carry identity, provenance, scope, action/barrier/case/suite bounds,
  progress/completion, process termination, cleanup, and approval state.
- Execution order: for costly/uncertain work, preflight and discover, then run the smallest credible
  bounded check; broaden after clean narrower evidence, or document no credible narrower check before
  bounded breadth. Return after each failure.
- Rerun rule: no unchanged failing command/assertion or timeout inflation; name the relevant
  state/evidence/diagnostic-strategy change before rerun.
- Plan-to-result report: map plan scenarios to authored tests/results, selected choices, evidence,
  skipped/not-run items, redaction, cleanup status, and follow-up risks.
- Evidence/reporting: sanitized commands, outputs, artifacts, outcomes, cleanup, blocked reasons.
- Product-failure routing: do not edit product code; report reproduction and route to owner.
- Stop if: <authority insufficient/stale/conflicting, unsafe, product fix required, no precondition, etc.>
```

The packet may include optional reference paths or approved source/companion docs as aids, but must
state that canonical workflow docs govern conflicting guidance when they exist. Task-local Testing
Authorization must be quoted or summarized exactly enough to prove paths, commands, writes, timeout,
cleanup, and side effects; it must not be described as project policy.

## Executor Receipt and Report

The executor's first reportable fact should prove authority consultation:

- authority kind and source loaded;
- relevant companion docs loaded or not needed;
- observed authority constraints that shaped edits/commands;
- any stale/conflicting/unsafe authority finding that stopped work.

Final executor reports should include:

- files changed by allowed category, or no-write explanation;
- approved plan path/version and scenario-to-test/result mapping, or authority-approved no-plan reason;
- selected execution choice(s), current approvals used, and choices skipped/not run with reasons;
- commands proposed/run with identity, cwd, provenance, classification, bounds, progress/termination result,
  cleanup status, rerun reason, and relevant state/evidence/strategy delta;
- sanitized evidence, artifacts, summaries, blocked approvals/preconditions, and redaction actions;
- outcomes such as passed, failed, blocked-precondition, unsafe-needs-approval, inconclusive/flaky,
  or skipped/not-run when the authority uses these terms; flaky or inconclusive is not pass;
- product-failure routing with reproduction evidence, without modifying product/runtime code;
- privacy/redaction actions for secrets, credentials, tokens, PII, proprietary content, screenshots,
  videos, logs, local paths, and environment details, plus cleanup-failed/uncertain follow-up.

## No-Executor Fallback

When no executor/sub-agent mechanism is available, return the complete packet plus a short explanation
that downstream test authoring, alteration, or execution was not performed. Do not run commands or
edit tests directly as a substitute for missing delegation.

## Orchestrator Follow-up

Review executor output for authority consultation, approved plan/report linkage, selected execution
choices, scope compliance, approval violations, evidence quality, skipped/not-run handling,
redaction, cleanup/timeout status, non-pass treatment for flaky or inconclusive results, and
product-failure routing. If authority appears stale or conflicting, stop and shift to workflow update
or task-local authorization before further test work.
