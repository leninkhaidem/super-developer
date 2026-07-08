---
name: testing
description: >
  Establish, document, and apply project-specific testing workflows. Use for testing strategy,
  workflow setup/update, test authoring or alteration, and test execution requests; authoring and
  execution run through approved workflow docs and delegation. Do not use for bug fixing, feature
  implementation, code review, audit, or release work.
---

# Testing

Operate as a testing workflow meta-skill: first establish or load the repository's approved testing
workflow, then delegate downstream test authoring, alteration, or execution with workflow-aware
instructions. Do not default to standalone test edits or commands.

## Always

- Canonical interface: root `AGENTS.md` should contain only a concise lazy pointer for testing work,
  and root-relative `docs/testing/workflow.md` is the reusable workflow entry point. Companion docs
  live under `docs/testing/` and are loaded only when the workflow points to them.
- Authority precedence: system/developer/current user/current skill safety rules outrank project
  workflow docs; approved project workflow docs outrank optional skill-local references.
- Keep this eager prompt meta-level. Put project methodology in `docs/testing/workflow.md` or linked
  companion docs; use skill references only as optional proposal/adaptation aids.
- Choose an explicit mode before acting: initialize/update workflow, author/alter tests using an
  accepted/current canonical workflow, or delegate execution-oriented work.
- Check `docs/testing/workflow.md` before test edits, commands, or delegation. If it is missing,
  stale, ambiguous, conflicting, unsafe, refused, or not accepted/current, establish, update,
  adopt, migrate, or link through that canonical file first; do not invent one-off conventions.
- Initialization/update is recommendation-led: inspect repo evidence before broad questions, propose
  the best project-fit strategy, ask focused confirmation questions, then present a draft summary and
  proposed file changes before writing workflow docs.
- Workflow documentation writes to root `AGENTS.md` or `docs/testing/*` require explicit current-task
  approval after the draft. Preserve unrelated existing `AGENTS.md` content surgically.
- Authoring, alteration, and execution are delegated only after canonical workflow consultation. If
  no executor or sub-agent is available, return a workflow-aware instruction packet and stop.
- Current-task approval is required for workflow doc writes, test writes when the approved workflow
  requires approval, browser/live/network/dependency/config/CI/orchestration actions, unsafe
  commands, and any other gated side effect.
- Strategy establishment, including browser E2E strategy, may recommend/adapt optional references
  from repo evidence; it does not authorize installs, test writing, test runs, live services,
  recordings, secrets, network access, config/CI edits, or orchestration changes.
- Redact secrets, credentials, tokens, PII, proprietary content, sensitive screenshots/videos/logs,
  and local environment details from prompts, summaries, docs, packets, and reports.

## Do

1. Resolve the user's testing goal, target repo/worktree, requested mode, allowed scope, risk
   boundaries, and whether they are asking to establish/update strategy, change tests, execute tests,
   or receive a reusable packet.
2. Load or establish the workflow state. Check `docs/testing/workflow.md` first; if missing, stale,
   ambiguous, conflicting, unsafe, refused, or not accepted/current, load
   `references/workflow-contract.md` and use bounded read-only candidate discovery only as source
   material before establishing or updating the canonical entry. Do not edit tests, run commands, or
   delegate until `docs/testing/workflow.md` exists and is accepted/current for the task.
3. For initialization/update, inspect relevant repo evidence, optionally load proposal references,
   recommend the project-fit workflow, ask focused confirmation/approval questions, and present a
   draft covering the `AGENTS.md` lazy pointer, `docs/testing/workflow.md`, companion docs, approval
   gates, evidence/reporting, redaction, stale/conflict handling, and update procedure.
4. After explicit approval, the main agent may create or surgically update root `AGENTS.md` and
   `docs/testing/*` in the target repo. Without approval, continue discovery or stop with the draft;
   leave no partial workflow docs as accepted.
5. For author/alter or execution requests with an accepted/current canonical workflow, load
   `references/delegation-packets.md`, build an instruction packet naming `docs/testing/workflow.md`
   and relevant companions, then delegate. The executor must report that it consulted the workflow
   before edits or commands.
6. Treat executor output as evidence, not authority. Verify the report includes workflow paths,
   commands/files changed, command classifications, sanitized evidence, cleanup/timeout status,
   product-failure routing, blocked approvals, and unresolved risks.
7. If optional generic, web, or browser references are useful, load them only after canonical
   workflow state is resolved or while drafting an initialization/update proposal; never let them
   override approved project workflow docs.

## Load if needed

- Canonical workflow interface, authority precedence, candidate discovery, recommendation-led
  initialization/update, approval-gated docs, and browser E2E strategy establishment →
  `references/workflow-contract.md`
- Workflow-aware delegation packet, no-executor fallback, executor receipt/report, stop conditions,
  product-failure routing, and command/write safety boundaries → `references/delegation-packets.md`
- Optional stack-agnostic test design, command safety, outcomes, durable plan/report schema, and
  write boundaries → `references/core/generic-testing.md`
- Optional web/frontend/backend/API/live/browser coverage planning and evidence concerns →
  `references/web/application-testing.md`
- Optional browser E2E stack/evidence/reporting setup proposal material, including Playwright/Allure
  conventions → `references/web/browser-e2e-stack-setup.md`
- The request is actually bug diagnosis/fixing, feature implementation, code review, audit, release,
  or README/docs polish → use the owning skill instead of this one.

## Stop if

- `docs/testing/workflow.md` does not exist, is stale, ambiguous, conflicting, unsafe, refused, or is
  not accepted/current for an authoring, alteration, execution, or delegation request, and the user has
  not approved establishing, updating, adopting, migrating, or linking through that canonical file.
- The user refuses canonical workflow creation, adoption, migration, linking, or update, or does not
  approve proposed workflow doc writes needed for the next step.
- No executor/sub-agent is available for downstream test authoring, alteration, or execution; return
  the prepared packet instead of doing the work directly.
- The next action crosses an approval-gated category without explicit current-task approval.
- Optional references conflict with approved project workflow docs, or repo evidence contradicts the
  workflow enough that proceeding would be unsafe or misleading.
- The next useful step needs credentials, secrets, production access, unsafe data mutation, or
  unredacted sensitive evidence.
- Passing tests requires production/application/runtime code changes or weakening assertions; route
  product failures with reproduction evidence.

## Output

Return canonical workflow status, consulted paths/candidates, recommendation or adoption decision,
approval status, docs changed or proposed, delegation packet or executor receipt/report, files changed by
allowed category, commands proposed/run with classification/timeout/outcome, sanitized evidence,
cleanup status, blocked approvals, product-failure routing, and unresolved risks.
