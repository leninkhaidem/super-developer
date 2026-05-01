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

## Mandatory Plan Quality Reviewer

Always run the Plan Quality Reviewer.

Rubric:

- Are requirements represented without architecture rationale leaking into `SPEC.md`?
- Are tasks self-contained, sequenced, and verifiable?
- Are acceptance criteria observable and tied to requested outcomes?
- Are dependencies, work packages, and verification commands coherent?
- Are `design_decisions` IDs sequential (`DD-1`, `DD-2`, ...) with no gaps and valid `source` values?
- Are plan artifacts internally consistent and schema-compatible?

Primary failure mode: implementation agents receive ambiguous, contradictory, or unverifiable work.

## Adaptive Architecture/Feasibility Challenger

Run when the plan includes nontrivial design, cross-subsystem work, migrations, new abstractions, persistence, external APIs, or unresolved tradeoffs.

Rubric:

- Does the plan choose one coherent representation instead of leaving parallel designs reachable?
- Are task boundaries aligned with the actual architecture and dependency direction?
- Does the plan preserve domain distinctions in types, data, or acceptance criteria?
- Does sequencing prevent broken intermediate states?
- Are rejected alternatives or constraints captured where future reviewers need them?
- Is there a materially simpler lower-risk alternative with the same outcome?

Primary failure mode: the plan can be implemented but leaves the system conceptually incoherent.

## Adaptive Security/Failure-Mode Reviewer

Run when the plan touches auth, permissions, secrets, privacy, safety, financial/medical/infrastructure data, external inputs, network boundaries, persistence, migrations, concurrency, cleanup, rollback, or error handling.

Rubric:

- Does the plan surface failures truthfully rather than producing plausible success?
- Are security, privacy, and safety invariants explicit and verifiable?
- Are destructive, irreversible, or externally visible actions gated appropriately?
- Are malicious or malformed inputs considered where relevant?
- Are rollback, idempotency, and partial-failure states addressed when needed?
- Do acceptance criteria cover failure modes, not only the happy path?

Primary failure mode: implementation ships a dangerous edge case because the plan never made it visible.

## Adaptive Scope/Requirements Reviewer

Run when requirements are ambiguous, user intent is broad, the plan adds/removes behavior, or reviewers may need to distinguish product semantics from internal implementation details.

Rubric:

- Does the plan implement the actual request rather than a wished-for adjacent problem?
- Are product requirements separated from architecture and process choices?
- Are non-goals and exclusions respected?
- Do tasks avoid unapproved semantic changes?
- Are user-visible tradeoffs escalated instead of silently decided?
- Are acceptance criteria sufficient to prove the requested outcome?

Primary failure mode: the plan is technically coherent but solves the wrong problem or changes semantics without approval.

## Reviewer Selection

The Plan Quality Reviewer is mandatory. Add adaptive reviewers only when their trigger conditions apply. More reviewers are not inherently better; each added reviewer must have a distinct risk surface and a narrowed rubric.
