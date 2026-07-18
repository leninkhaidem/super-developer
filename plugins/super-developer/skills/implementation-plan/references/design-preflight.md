# Design and Feasibility Preflight

## Purpose and Order

Preflight always occurs before plan authoring. Its depth is adaptive: a narrow, mechanical, low-risk request may
finish with a concise evidence-backed no-trigger result, while nontrivial/risky work gets a fresh adversarial
challenger. Skip narrow, mechanical, low-risk plans only for challenger dispatch—not for the preflight decision.
Preflight establishes whether a credible plan can name architecture, prerequisites, actual production paths, and
verification seams without guessing. It is not an implementation plan, transcript, or new ledger.

## Triggered Challenge

Dispatch the challenger for new architecture/data/permission/external/persistence/generated-contract surfaces;
security, privacy, safety, reliability, concurrency, cancellation, replay, rollback, shared state, lifecycle,
publication, or novel runtime/harness behavior; materially ambiguous designs; and cross-cutting public contracts.

- Main agent: discovery authority, interpretation, user decisions, budget reservation, durable projection.
- Challenger: bounded read-only evidence; no edits, agents, user questions, packages, or review-plan.
- For the `design-preflight` role resolve `models.design-preflight` → `models.default-model` → `inherit` from the
  parent-supplied model-preferences contract.

Challenger output is advisory. Resolve every material item before artifact writing.

## Discovery Authority

**Safe disposable discovery** may proceed without implementation authorization when it is bounded and consists of
repository inspection, read-only local probes, or reversible experiments in a disposable spike worktree. Record
exact command/provenance, expected disposable writes, timeout, observed result, and verified cleanup. It must not
change production branches, manifests/lockfiles, shared services/data, credentials, remotes, or external systems.

**Protected discovery** includes credentials, network/external effects, paid/live/shared services, destructive or
persistent changes, manifest/lockfile/dependency changes, remote writes, or any production/public-contract
mutation. Ask one focused discovery-authority question for the exact action, or stop. Permission is probe-specific,
does not authorize implementation, and is not inherited by later execution.

## Preflight Brief

```markdown
# Preflight Brief
## User Request
<verbatim or lossless summary>
## Human Authorization Envelope Inputs
<outcomes, constraints, exclusions, product/interface invariants, risks or unknowns>
## Current Evidence
<repository/contract/command facts>
## Open Design Surface
<material hypotheses, labeled as hypotheses>
## Triggered Architecture Surfaces
<authority/state/ordering/privacy/publication/path/seam, or none>
## Prerequisites
<required/optional dependency, tool, credential, service, environment>
## Non-Goals
<explicit exclusions>
```

## Challenger Task

Challenge requirement completeness, defaults, edge/failure behavior, assumptions, feasibility, and disproportionate
scope. For each triggered architecture surface inspect:

- authoritative owner plus every ingress and mutation path;
- state model, legal/forbidden transitions, ordering and linearization/publication point;
- winning and losing generation/lease/owner behavior;
- cancellation, abort, settlement, cleanup, replay/idempotence, and restart;
- default/provider branches, credential/privacy/data boundaries, and public/generated contracts;
- actual-production-path seams that force and observe the invariant; and
- earliest credible affected broad-regression tripwire and the layer that owns it.

## Bounded Output

```markdown
RECOMMENDED_APPROACH
- <one or none>
MUST_DECIDE
- <at most 5 or none>
COVERAGE_GAPS
- <at most 5 or none>
ARCHITECTURE_INVARIANTS
- <at most 8 or none>
PREREQUISITES
- <required|optional; evidence; proven-ready|protected-activation-required|blocked>
PRODUCTION_PATH_AND_SEAMS
- <entry/path/observable/failure signal/affected broad placement>
BLOCKERS
- <at most 5 or none>
RISKS
- <at most 5>
ASSUMPTIONS_TO_VERIFY
- <at most 5>
NOT_WORTH_FIXING
- <at most 3 or none>
```

## Resolution and Projection

Before writing artifacts:

1. Resolve every `MUST_DECIDE`, `COVERAGE_GAPS`, and `BLOCKERS` item through approved intent/evidence, a focused
   user decision for envelope changes, or an approved non-goal.
2. Resolve plan-changing empirical uncertainty through `spike-to-plan`; never guess an invariant.
3. Classify every required prerequisite: `proven-ready` has source-bound evidence;
   `protected-activation-required` can only be checked under later authority and names an exact probe/remedy before
   product writes/fanout; `blocked` includes known-unavailable required capability and prevents planning readiness.
   Disclose and exclude unavailable optional capability.
4. Accept architecture invariants only from requirements, user decisions, existing contracts, or observations.
5. Persist concise results through existing owners: Human Authorization Envelope and Technical Plan Baseline in
   `SPEC.md`; package scope/Notes; confidence-oriented Verification Expectations; authoritative Slices when useful.
6. Preserve package boundaries, consumed contracts, actual-path seams, and affected broad-regression placement.

Do not add an architecture ledger, prerequisite ledger, test inventory, registry field, proof type, or report.
The compact Lifecycle State owns only monotonic budget/continuation mechanics.

## Fail Closed

Stop before plan authoring when product behavior/scope/risk lacks authority; a required prerequisite is `blocked`;
protected activation is vague or cannot safely wait; a triggered surface lacks owner/transitions/order/forbidden
behavior; actual production path or credible causal seam is absent; broad placement is unknown; safe cleanup is
uncertain; a Slice would be narrowed without approval; or later agents would need hidden preflight chat.
