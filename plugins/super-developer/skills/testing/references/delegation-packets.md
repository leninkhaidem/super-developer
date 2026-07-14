# Testing Delegation Packets Reference

Use this reference only after the canonical project testing workflow at `docs/testing/workflow.md`
exists, is accepted/current, and governs the task. Candidate docs are source or companion material
only after the canonical entry incorporates or references them. The main agent remains an
orchestrator: it documents/updates workflow docs after approval, but delegates test authoring,
alteration, and execution. If no executor or sub-agent mechanism is available, return the packet to
the user and stop instead of doing the work directly.

## Delegation Preconditions

Before delegation, the orchestrator must establish:

- workflow state: `docs/testing/workflow.md` exists, is accepted/current for the task, and has been
  read by the orchestrator before delegation;
- candidate handling: any adopted, migrated, or linked candidate is incorporated or referenced by the
  canonical workflow entry before it can govern delegated work;
- companion docs: relevant `docs/testing/*` or approved source/companion paths named by the
  canonical workflow, or an explicit statement that none are needed;
- allowed scope: files, test surfaces, commands, and evidence boundaries the executor may touch;
- approved plan path/version when the workflow requires a feature/domain plan, or an explicit
  no-plan-needed statement from the accepted workflow;
- selected execution choice(s), what each choice is intended to prove, and choices intentionally
  skipped or not run;
- approval boundaries: workflow doc writes, test writes when the workflow requires approval,
  browser/live/network/dependency/config/CI/orchestration actions, unsafe commands, and other gated
  side effects are blocked unless explicitly approved in the current task;
- stop conditions: missing/stale/conflicting workflow, product/runtime fix needed, unsafe command,
  credentials/secrets, uncontrolled data mutation, absent preconditions, or unredactable evidence.

## Packet Shape

A workflow-aware packet should include:

```markdown
Testing delegation packet
- User goal: <requested testing outcome>
- Target repo/worktree: <path or explicit repo context>
- Precondition: docs/testing/workflow.md exists, is accepted/current, and governs this task.
- Workflow entry: docs/testing/workflow.md
- Companion docs to consult: <paths or none>
- Approved plan path/version: <path+version, or workflow-approved no-plan reason>
- Selected execution choice(s): <focused check/feature confidence/browser review/broad regression/do not run yet/etc.>
- Required first step: read the canonical workflow entry and companions; receipt/report must cite them.
- Allowed scope: <test files/fixtures/helpers/docs/commands/evidence surfaces>
- Disallowed scope: <production/runtime code, unapproved config/dependencies/CI/orchestration, etc.>
- Current-task approvals already granted: <exact approvals or none>
- Approval-gated actions to stop for: <commands/writes/browser/live/network/etc.>
- Command safety: classify commands, use bounded timeouts, no unsafe/default live side effects.
- Runtime envelope: carry identity, provenance, scope, action/barrier/case/suite bounds, progress/completion,
  process termination, cleanup, and approval state.
- Execution order: for costly/uncertain work, preflight and discover, then run the smallest credible bounded
  check; broaden after clean narrower evidence, or document no credible narrower check before bounded breadth.
  Return after each failure.
- Rerun rule: no unchanged failing command/assertion or timeout inflation; name the relevant state/evidence/
  diagnostic-strategy change before rerun.
- Plan-to-result report: map plan scenarios to authored tests/results, selected choices, evidence,
  skipped/not-run items, redaction, cleanup status, and follow-up risks.
- Evidence/reporting: sanitized commands, outputs, artifacts, outcomes, cleanup, blocked reasons.
- Product-failure routing: do not edit product code; report reproduction and route to owner.
- Stop if: <workflow missing/stale/conflicting, unsafe, product fix required, no precondition, etc.>
```

The packet may include optional reference paths or approved source/companion docs as aids, but must
state that `docs/testing/workflow.md` and its linked companions govern conflicting guidance.

## Executor Receipt and Report

The executor's first reportable fact should prove workflow consultation:

- workflow entry path loaded and relevant companion docs loaded or not needed;
- observed workflow constraints that shaped edits/commands;
- any stale/conflicting/unsafe workflow finding that stopped work.

Final executor reports should include:

- files changed by allowed category, or no-write explanation;
- approved plan path/version and scenario-to-test/result mapping, or workflow-approved no-plan reason;
- selected execution choice(s), current approvals used, and choices skipped/not run with reasons;
- commands proposed/run with identity, cwd, provenance, classification, bounds, progress/termination result,
  cleanup status, rerun reason, and relevant state/evidence/strategy delta;
- sanitized evidence, artifacts, summaries, blocked approvals/preconditions, and redaction actions;
- outcomes such as passed, failed, blocked-precondition, unsafe-needs-approval, inconclusive/flaky,
  or skipped/not-run when the project workflow uses these terms; flaky or inconclusive is not pass;
- product-failure routing with reproduction evidence, without modifying product/runtime code;
- privacy/redaction actions for secrets, credentials, tokens, PII, proprietary content, screenshots,
  videos, logs, local paths, and environment details, plus cleanup-failed/uncertain follow-up.

## No-Executor Fallback

When no executor/sub-agent mechanism is available, return the complete packet plus a short explanation
that downstream test authoring, alteration, or execution was not performed. Do not run commands or edit
tests directly as a substitute for missing delegation.

## Orchestrator Follow-up

Review executor output for workflow consultation, approved plan/report linkage, selected execution
choices, scope compliance, approval violations, evidence quality, skipped/not-run handling,
redaction, cleanup/timeout status, non-pass treatment for flaky or inconclusive results, and
product-failure routing. If the workflow appears stale or conflicting, stop and shift to workflow
update mode before further test work.
