# Plan Review Rubrics

Plan review uses narrowed reviewer rubrics. Sub-agents work cold from the files and context supplied by the main agent; they do not receive the full `review-plan` skill and do not inherit hidden conversation context.

## Common Rules for All Reviewers

- Read only the supplied files/context plus explicitly allowed supporting files.
- Treat `SPEC.md` as requirements-only.
- Treat `tasks.json` as the durable task, work-package, and `design_decisions` source.
- Respect accepted `design_decisions` by default.
- Return findings using the `plan-review-findings.md` schema.
- Do not edit files, spawn agents, ask the user, or implement.

## Reopening Accepted `design_decisions`

Reviewers may challenge an accepted `design_decisions` entry only under one of these high-bar conditions:

- Conflict with `SPEC.md`.
- Security, privacy, or safety issue.
- Codebase evidence contradicts rationale.
- Accepted decision makes acceptance criteria unverifiable.

A materially simpler lower-risk alternative with the same outcome is not enough by itself to reopen an accepted decision. Report it as a `SUGGESTION` unless it also satisfies one of the conditions above.

Challenges must target `DD:<design-decision-id>` and cite evidence. Preference, style, or a different valid architecture is not enough.

## Plan Reviewer

Always run one Plan Reviewer. This reviewer combines challenge and artifact QA in sequence.

### Pass 1: Combined Challenge

First, challenge the plan before spending effort on detailed artifact QA:

- Does the plan choose one coherent representation instead of leaving parallel designs reachable?
- Is there a materially simpler lower-risk alternative with the same outcome?
- Are task boundaries aligned with the actual architecture and dependency direction?
- Does sequencing prevent broken intermediate states?
- Does the plan implement the actual request rather than a wished-for adjacent problem?
- Are product requirements separated from architecture and process choices?
- Are non-goals and exclusions respected?
- Are user-visible tradeoffs escalated instead of silently decided?
- Should a dedicated Security/Failure-Mode Reviewer be run?

If Pass 1 finds a `BLOCKER` or `CRITICAL` semantic issue likely to change the plan, limit Pass 2 to obvious mechanical/schema defects. Detailed QA against a plan that should change creates waste and review-loop pressure.

### Pass 2: Artifact QA

When the accepted approach is coherent enough to review, check artifact quality:

- Are requirements represented without architecture rationale leaking into `SPEC.md`?
- Are tasks self-contained, sequenced, and verifiable?
- Are acceptance criteria observable and tied to requested outcomes?
- Are dependencies, work packages, and verification commands coherent?
- Are `design_decisions` IDs sequential (`DD-1`, `DD-2`, ...) with no gaps and valid `source` values?
- Are plan artifacts internally consistent and schema-compatible?

### Security Escalation Sniff Test

The Plan Reviewer performs only a light security/failure-mode sniff test. It should recommend `ESCALATE_SECURITY_REVIEW` when the plan touches auth, permissions, secrets, privacy, safety, financial/medical/infrastructure data, external inputs, network boundaries, persistence, migrations, concurrency, cleanup, rollback, destructive actions, or error handling in a way that needs dedicated review.

Primary failure mode: implementation agents receive a plan that is coherent on paper but wrong, unsafe, ambiguous, unverifiable, or misaligned with the actual request.

## Security/Failure-Mode Reviewer

Run this reviewer only when the feature is security/privacy/safety-sensitive or when the Plan Reviewer recommends `ESCALATE_SECURITY_REVIEW`.

Rubric:

- Does the plan surface failures truthfully rather than producing plausible success?
- Are security, privacy, and safety invariants explicit and verifiable?
- Are destructive, irreversible, or externally visible actions gated appropriately?
- Are malicious or malformed inputs considered where relevant?
- Are rollback, idempotency, and partial-failure states addressed when needed?
- Do acceptance criteria cover failure modes, not only the happy path?

Primary failure mode: implementation ships a dangerous edge case because the plan never made it visible.

## Reviewer Selection

Default to one Plan Reviewer. Add the Security/Failure-Mode Reviewer only for security/privacy/safety-sensitive plans or when the Plan Reviewer requests escalation. More reviewers are not inherently better; split review only when a distinct risk surface needs dedicated attention.
