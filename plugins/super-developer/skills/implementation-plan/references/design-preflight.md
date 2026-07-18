# Design Preflight

## Purpose

Design Preflight is a read-only adversarial challenge before durable plan artifacts. It surfaces requirement
completeness gaps and, when triggered, settles architecture invariants that implementation and verification must
share. It is not a universal gate, implementation plan, persisted transcript, or instruction stream.

## Trigger

Run for nontrivial or risky plans involving:

- new architecture, data model, permission/credential boundary, external integration, persistence, migration,
  generated contracts, or destructive behavior;
- security, privacy, safety, reliability, concurrency, cancellation, replay, rollback, shared mutable state,
  registration/discovery, lifecycle, publication, or novel runtime/harness behavior;
- ambiguous requirements with materially different valid designs;
- cross-cutting changes across skills, commands, subsystems, public contracts, or generated artifacts.

Skip narrow, mechanical, low-risk plans whose architecture, ownership, caller contract, and evidence path are clear.

## Authority and Model

- Main agent: orchestration, interpretation, user decisions, and durable artifact projection.
- Challenger: bounded read-only evidence; no edits, agents, user questions, package artifacts, or review-plan.
- For the `design-preflight` role, resolve `models.design-preflight` → `models.default-model` → `inherit` from
  `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/model-preferences.md`.

Challenger output is advisory. The main agent may accept, reject, combine, or reframe it, but never silently
persists an unresolved semantic choice.

## Brief

```markdown
# Preflight Brief
## User Request
<verbatim or tightly summarized request without advocacy>
## Known Constraints
- <explicit user/repo/tool constraint>
## Current Evidence
- <observed file, command, contract, or repo fact>
## Open Design Surface
- <area with material uncertainty>
## Triggered Architecture Surfaces
- <authority/state/ordering/cancellation/replay/privacy/publication/test-seam surface, or none>
## Non-Goals
- <scope explicitly excluded or not implied>
```

Label main-agent hypotheses as hypotheses under `Open Design Surface`.

## Challenger Task

Challenge whether the request can become a coherent, finite plan. Identify missing observable behavior, defaults,
edge/failure cases, assumptions, and disproportionate additions. For each triggered architecture surface, inspect:

- authoritative owner plus every ingress and mutation path;
- state model, legal transitions, and forbidden transitions;
- ordering and linearization/publication point;
- winning and losing generation/lease/owner behavior;
- cancellation, abort reentrancy, settlement, termination, and cleanup;
- replay/idempotence and restart behavior;
- default versus injected/provider-specific branches;
- credential, privacy, and data minimization boundaries;
- actual-production-path seams that can force and observe the invariant;
- earliest credible affected broad-regression tripwire.

Do not prescribe fields that are irrelevant to the triggered surface.

## Bounded Output

```markdown
RECOMMENDED_APPROACH
- <at most 1 concise recommendation, or none>
MUST_DECIDE
- <at most 5 decisions, or none>
COVERAGE_GAPS
- <at most 5 missing requirements/behaviors/failures/defaults, or none>
ARCHITECTURE_INVARIANTS
- <at most 8 concise authority/state/transition/ordering/forbidden/test-seam invariants, or none triggered>
BLOCKERS
- <at most 5 blockers, or none>
RISKS
- <at most 5 material risks>
ASSUMPTIONS_TO_VERIFY
- <at most 5 assumptions>
NOT_WORTH_FIXING
- <at most 3 disproportionate concerns, or none>
```

## Resolution and Projection

Before artifact writing:

1. Resolve each `MUST_DECIDE`, `COVERAGE_GAPS`, and `BLOCKERS` item from approved intent and repository evidence,
   ask the user when semantics/scope/risk changes, or record an approved non-goal.
2. Resolve empirical uncertainty through `spike-to-plan`; never convert an observation gap into a guessed invariant.
3. Accept only architecture invariants supported by requirements, user decisions, existing contracts, or evidence.
4. Persist concise accepted invariants—not debate or rationale—through existing owners:
   - `SPEC.md` acceptance criteria/constraints for feature-wide observable rules;
   - Slice interface contracts for applicable product/design interfaces;
   - package `Notes` for ownership, sequencing, and reassessment triggers;
   - package verification expectations for actual-path evidence and broad-regression placement.
5. Require package boundaries and dependencies to preserve the invariant and its verification seam.
6. Carry unresolved non-blocking risks explicitly; do not hide them in vague package prose.

The ephemeral Preflight Brief/output is not stored under `.tasks/`. Do not add an architecture ledger, registry
field, proof type, or report. Architecture rationale stays out of `SPEC.md` unless it is itself an approved
requirement, constraint, or scope decision.

## Fail Closed

Stop artifact writing when:

- product behavior, scope, risk acceptance, or a locked commitment lacks authority;
- a triggered surface lacks an authoritative owner, legal/forbidden transition, publication/order rule, or
  credible actual-path verification seam;
- package boundaries make a material requirement or invariant unverifiable;
- empirical behavior, external facts, credentials, dependencies/services, or unsafe commands remain required;
- a Slice commitment would be narrowed/excluded without approval;
- later agents would need hidden Preflight chat to implement or verify the accepted design.
