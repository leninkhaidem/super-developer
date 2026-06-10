# Orchestrator and Worker-Contract Surface

Boundary: load only when authoring, revising, or reviewing a skill where the entry point must
orchestrate work that is performed by delegated worker roles through explicit contract packets.

## Contract

Use this surface when a current agent must resolve context, enforce gates, gather approvals, choose
workers, preserve provenance, validate returned artifacts, or coordinate side effects before or after
a worker acts.

The orchestrator-facing `SKILL.md` is not the worker's permission slip. It owns setup, classification,
packet construction, dispatch, validation, repair routing, and user-facing summary. Concrete
worker-only action instructions live in one or more worker-contract references that are passed to the
worker with explicit source paths, expected outputs, and stop conditions.

Worker authority comes from the packet plus the worker contract. It must not depend on hidden runtime
identity such as whether the agent believes it is a main agent, sub-agent, reviewer, or worker.

## Select This Surface When

- Parent-level gates are material: approval, path safety, overwrite safety, model or worker choice,
  status transitions, merge/push/cleanup boundaries, or artifact ownership.
- Durable files, reports, reviews, or proof artifacts need a producer boundary that later review can
  inspect or trust.
- Multiple workers, specialists, reviewers, verifiers, or repair passes may be coordinated.
- The same action would be unsafe if performed inline by the current conversation without an explicit
  worker packet.
- The workflow needs fresh context isolation to avoid contamination from the orchestrator's chat.

## Authoring Rules

1. State the orchestrator boundary in `SKILL.md`: what it resolves, what it delegates, what it
   validates, and what it must not do inline.
2. Keep pre-dispatch safety, packet requirements, validation gates, repair routing, and output shape
   eager when they are universal.
3. Put worker-only instructions in a worker-contract reference with one clear role boundary. The
   reference has no frontmatter and is not a separately routed skill.
4. The worker packet should include explicit task goal, source material, safe paths, contract path,
   permitted write scope, expected outputs, validation commands or checks, and stop conditions.
5. Supporting reference paths may be passed when useful, but pair them with concrete load conditions.
   Avoid blanket packets that tell the worker to read every named reference before acting.
6. The orchestrator may pass a contract path without reading the full worker contract when its own
   eager rules are sufficient to build a safe packet.
7. Capture durable provenance in the artifact model only when the process boundary matters for later
   review, audit, resume, or repair.

## Worker Contract Shape

A worker-contract reference usually contains:

- boundary and role statement;
- required packet fields and missing-input stop rule;
- first reads or action-point reads, only where necessary;
- workflow steps owned by the worker;
- write/edit scope and forbidden actions;
- validation expectations;
- completion report fields.

Keep it compact. Do not duplicate the full parent skill, unrelated workflow doctrine, or generic
skill-authoring rules.

## Stop or Rework If

- The worker must infer authority from runtime identity or hidden chat context.
- The orchestrator still appears allowed to perform worker-only actions inline.
- The packet or contract requires all references to be read up front without action-point need.
- The worker contract is just a second copy of the parent skill.
- A reusable standalone capability would be clearer as direct invocation by skill name.
- Provenance matters but no durable artifact records the producer boundary.

If the same skill legitimately has simple direct cases and complex orchestrated cases, keep the mode
boundary explicit in `SKILL.md` and load only the surface reference needed for the mode being authored
or reviewed.
