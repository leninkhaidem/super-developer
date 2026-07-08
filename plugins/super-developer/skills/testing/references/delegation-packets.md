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
- Required first step: read the canonical workflow entry and companions; receipt/report must cite them.
- Allowed scope: <test files/fixtures/helpers/docs/commands/evidence surfaces>
- Disallowed scope: <production/runtime code, unapproved config/dependencies/CI/orchestration, etc.>
- Current-task approvals already granted: <exact approvals or none>
- Approval-gated actions to stop for: <commands/writes/browser/live/network/etc.>
- Command safety: classify commands, use bounded timeouts, no unsafe/default live side effects.
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
- commands proposed/run with cwd, provenance, classification, timeout, result, and cleanup status;
- sanitized evidence, artifacts, summaries, skipped items, and blocked approvals;
- outcomes such as passed, failed, blocked-precondition, unsafe-needs-approval, inconclusive/flaky,
  or skipped/not-run when the project workflow uses these terms;
- product-failure routing with reproduction evidence, without modifying product/runtime code;
- privacy/redaction actions for secrets, credentials, tokens, PII, proprietary content, screenshots,
  videos, logs, local paths, and environment details.

## No-Executor Fallback

When no executor/sub-agent mechanism is available, return the complete packet plus a short explanation
that downstream test authoring, alteration, or execution was not performed. Do not run commands or edit
tests directly as a substitute for missing delegation.

## Orchestrator Follow-up

Review executor output for workflow consultation, scope compliance, approval violations, evidence
quality, cleanup/timeout status, and product-failure routing. If the workflow appears stale or
conflicting, stop and shift to workflow update mode before further test work.
