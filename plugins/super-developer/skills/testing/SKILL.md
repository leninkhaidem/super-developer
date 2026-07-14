---
name: testing
description: >
  Establish, document, and apply project-specific testing workflows. Use for testing strategy,
  workflow setup/revision, test authoring/alteration, or execution. Do not use for bug fixes,
  feature implementation, code review, audit, or release.
---

# Testing

Resolve the repository's testing authority, establish durable workflow docs when needed, then
route downstream test authoring, alteration, or execution with authority-aware instructions. Do not
default to standalone broad test edits or commands.

## Always

- Canonical interface: root `AGENTS.md` should contain only a concise lazy pointer for testing work,
  and root-relative `docs/testing/workflow.md` is the reusable workflow entry point. Companion docs
  live under `docs/testing/` and are loaded only when the workflow points to them.
- Authority precedence: system/developer/current user/current skill safety rules outrank project
  workflow docs; approved project workflow docs outrank optional skill-local references.
- Keep this eager prompt meta-level. Put project methodology in `docs/testing/workflow.md` or linked
  companion docs; use skill references only as optional proposal/adaptation aids.
- Choose a mode before acting: initialize/update workflow, author/alter tests, execute a bounded command, or
  delegate execution-oriented work.
- Testing authority is required before test writes, harness/test commands, or delegation. Authority is canonical
  workflow, routine-safe fallback for one parent-run local command, or task-local Testing Authorization.
- Canonical workflow remains the durable authority for broad/reusable delegation, recurring, browser/E2E, live service,
  shared-data, network, credentialed, dependency/config/CI/orchestration, multi-stage harness, long-running,
  destructive, or unclear-cleanup test work.
- Routine-safe fallback is narrow and command-specific: repo-local/project-owned, provenance clear from existing
  scripts/docs, bounded timeout/scope/completion, no network/credentials/browser/live/shared data/dependency/
  config/CI/destructive effects, no source/fixture/snapshot/config writes except known local cache/report artifacts,
  and trivial owned cleanup. It is not enough for delegation.
- Task-local Testing Authorization is a current-task one-off. It must explicitly name exact paths, commands,
  writes, timeout, cleanup, and side effects; it is not reusable, not project policy, and does not weaken higher
  safety gates or make high-blast-radius work routine-safe.
- Explicit initialize/update/adopt/migrate/link/revise requests require a strategy interview after repository
  inspection, including greenfield/no-strategy repositories or minimal-test repositories; existing docs are
  source material, not a skip.
- Missing workflow alone permits read-only discovery and planning. It does not force workflow creation unless the
  requested write/command/delegation lacks applicable authority, or the policy should be reusable.
- Initialization/update is recommendation-led: inspect repo evidence before broad questions, propose the best
  project-fit strategy, ask focused confirmation questions one at a time, starting with confidence goals, resolve
  mandatory strategy domains or user deferrals, then present a draft summary and proposed file changes before
  writing workflow docs.
- Workflow documentation writes to root `AGENTS.md` or `docs/testing/*` require explicit current-task approval
  after the draft. Preserve unrelated existing `AGENTS.md` content surgically.
- Authoring, alteration, and execution are delegated only after canonical workflow or task-local Testing
  Authorization covers the delegated act. If no executor/sub-agent is available, return a packet and stop.
- Current-task approval is required for workflow doc writes, task-local Testing Authorization, test writes when
  the governing authority requires approval, browser/live/network/dependency/config/CI/orchestration actions,
  unsafe commands, and any other gated side effect.
- Strategy establishment, including browser E2E strategy, may recommend/adapt optional references from repo
  evidence; it does not authorize installs, test writing, test runs, live services, recordings, secrets, network
  access, config/CI edits, or orchestration changes.
- Redact secrets, credentials, tokens, PII, proprietary content, sensitive screenshots/videos/logs, and local
  environment details from prompts, summaries, docs, packets, and reports.
- Skipped, not-run, timed-out, flaky, inconclusive, or cleanup-uncertain work is never reported as passed.

## Do

1. Resolve the user's testing goal, target repo/worktree, requested mode, allowed scope, risk boundaries, and
   whether they are asking to establish/update strategy, change tests, execute tests, or receive a reusable packet.
2. Resolve testing authority. Check `docs/testing/workflow.md` first; if accepted/current and adequate, load it
   and relevant companions. If absent or inadequate, load `references/workflow-contract.md`, classify the request,
   and use bounded read-only candidate discovery only as source material. Do not edit tests or run harness commands
   until authority covers the act; do not delegate without canonical workflow or task-local Testing Authorization.
3. For initialization/update, inspect relevant repo evidence, load `references/strategy-interview.md`, optionally
   load proposal references, recommend the project-fit workflow, ask focused confidence-first confirmation/approval
   questions, and present a draft covering the `AGENTS.md` lazy pointer, `docs/testing/workflow.md`, companion docs,
   plan/report paths, execution choices, approval gates, evidence/reporting, reliability/cleanup, redaction,
   stale/conflict handling, and update procedure.
4. After explicit approval, the main agent may create or surgically update root `AGENTS.md` and `docs/testing/*`
   in the target repo. Without approval, continue discovery or stop with the draft; leave no partial workflow docs
   as accepted.
5. For author/alter or execution with sufficient authority, or delegation with canonical/task-local authority, load
   `references/delegation-packets.md`, build a packet naming the authority source, scope, approval gates, outcome
   language, and cleanup. Executors must report that they consulted the authority before edits or commands.
6. Treat executor output as evidence, not authority. Verify authority provenance, files changed, command identity/
   classification/bounds, readiness order, sanitized evidence, progress/termination/cleanup, rerun deltas,
   product-failure routing, blocked approvals, skipped/not-run handling, and unresolved risks.
7. If optional generic, web, or browser references are useful, load them only after testing authority is resolved
   or while drafting an initialization/update proposal; never let them override approved project workflow docs.

## Load if needed

- Testing authority model, canonical workflow interface, candidate discovery, routine-safe fallback,
  task-local Testing Authorization, approval-gated docs, and browser E2E strategy establishment →
  `references/workflow-contract.md`
- Explicit initialize/update/adopt/migrate/link/revise strategy interview domains, confidence-first sequencing,
  starter plan/report/execution contracts, conditional browser/web prompts, legacy handling, and reliability/
  cleanup defaults → `references/strategy-interview.md`
- Authority-aware delegation packet, no-executor fallback, executor receipt/report, stop conditions,
  product-failure routing, and command/write safety boundaries → `references/delegation-packets.md`
- Optional stack-agnostic test design, command safety, outcomes, durable plan/report schema, and write boundaries
  → `references/core/generic-testing.md`
- Optional web/frontend/backend/API/live/browser coverage planning and evidence concerns →
  `references/web/application-testing.md`
- Optional browser E2E stack/evidence/reporting setup proposal material, including Playwright/Allure conventions
  → `references/web/browser-e2e-stack-setup.md`
- The request is actually bug diagnosis/fixing, feature implementation, code review, audit, release, or README/docs
  polish → use the owning skill instead of this one.

## Stop if

- Required testing authority is absent, stale, ambiguous, conflicting, unsafe, refused, or insufficient, and no
  applicable routine-safe fallback or task-local Testing Authorization covers the exact next action.
- The next action is broad, reusable, recurring, browser/E2E, live, shared-data, network, credentialed,
  dependency/config/CI/orchestration, multi-stage, long-running, destructive, or unclear-cleanup test work and the
  user has not approved establishing, updating, adopting, migrating, or linking the canonical workflow needed for it.
- The user refuses canonical workflow creation/update when reusable or high-risk policy is needed, or does not
  approve proposed workflow doc writes needed for the next step.
- No executor/sub-agent is available for downstream delegated work; return the prepared packet instead of doing the
  delegated work directly.
- The next action crosses an approval-gated category without explicit current-task approval.
- Optional references conflict with approved project workflow docs, or repo evidence contradicts the authority enough
  that proceeding would be unsafe or misleading.
- The next useful step needs credentials, secrets, production access, unsafe data mutation, or unredacted sensitive
  evidence.
- Passing tests requires production/application/runtime code changes or weakening assertions; route product failures
  with reproduction evidence.

## Output

Return testing authority status, consulted paths/candidates, recommendation or adoption decision, approval status,
docs changed or proposed, approved plan/report linkage, selected execution choices, delegation packet or executor
receipt/report, files changed by allowed category, commands proposed/run with identity/classification/bounds/outcome,
readiness/rerun decisions, sanitized evidence, skipped/not-run items, progress/termination/redaction/cleanup status,
blocked approvals, product-failure routing, and risks.
