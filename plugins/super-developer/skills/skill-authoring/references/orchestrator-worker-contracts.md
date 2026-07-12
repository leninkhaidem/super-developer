# Orchestrator and Worker-Contract Surface

Boundary: load only when authoring, revising, or reviewing a skill where the entry point must
orchestrate work that is performed by delegated worker roles through explicit contract packets.

## Contract

Use this surface when a current agent must resolve context, enforce gates, gather approvals, choose
workers, preserve provenance, validate returned artifacts, or coordinate side effects before or after
a worker acts. Provenance means a durable record of which worker used which inputs to produce an artifact.

The orchestrator-facing `SKILL.md` is not the worker's permission slip. It owns setup, classification,
packet construction, dispatch, validation, repair routing, and user-facing summary. Concrete
worker-only action instructions live in one or more worker-contract references that are passed to the
worker with explicit source paths, expected outputs, and stop conditions.

Worker authority comes from the packet plus the worker contract. It must not depend on hidden runtime
identity such as whether the agent believes it is a main agent, sub-agent, reviewer, or worker.

## Selection Decision

Use an orchestrator plus worker contract when at least one visible task requirement makes the parent
responsible for work the worker must not infer:

- approval, path safety, overwrite safety, worker choice, status transition, merge/push/cleanup, or
  artifact-ownership gates;
- packet construction from several authoritative inputs or a write scope narrower than the parent context;
- durable producer provenance that later review, resume, audit, or repair must inspect;
- validation or repair routing after a worker returns;
- coordination of multiple workers, specialists, reviewers, verifiers, or repair passes;
- fresh context isolation required for safety or independent judgment.

Use standalone direct execution when one agent owns the task, authority, validation, and output without
those parent-only duties. Use a hybrid only when both visible task shapes recur; select the mode before
loading branch-specific instructions. If the authority boundary remains unclear, ask rather than infer it.

## Authoring Rules

1. State the mode test and orchestrator boundary in `SKILL.md`: what the parent resolves, delegates,
   validates, and must not do inline.
2. Keep universal pre-dispatch safety, packet requirements, validation gates, repair routing, and output eager.
3. Put worker-only instructions in a worker-contract reference with one clear role boundary. It has no
   frontmatter and is not a separately routed skill.
4. Include explicit task goal, source material, defined terms, safe paths, contract path, permitted writes,
   forbidden actions, decision defaults, expected output, validation, and stop conditions in the packet.
5. Require the worker to read its packet and worker contract before any write, command, or external side effect.
   Pair every supporting reference with the exact later action that requires it.
6. The orchestrator may pass a worker-contract path without reading it when eager parent rules are sufficient
   to build and validate the packet safely; the worker may not act without reading it.
7. Fail closed when goal, authority, scope, path, approval, or governing input is missing or conflicting: perform
   no action and return `BLOCKED` with the missing field and evidence. Only the orchestrator may clarify with the
   user or expand worker authority.
8. Make the packet plus contract executable by a competent mid-tier worker without hidden chat, runtime identity,
   or guessed standards. State ask, stop, refuse, and escalation boundaries.
9. Dry-run one normal packet and one missing-input or high-risk packet before accepting the surface.
10. Capture durable provenance only when the producer boundary matters for later review, audit, resume, or repair.

## Worker Contract Shape

A worker-contract reference usually contains:

- boundary, role, authority source, and forbidden parent/worker actions;
- required packet fields and fail-closed `BLOCKED` behavior for missing or conflicting authority;
- mandatory packet/contract read before action, followed by action-point reads only where necessary;
- ordered worker actions with decisions, defaults, and observable completion;
- write/edit scope and forbidden side effects;
- validation expectations and failure routing;
- bounded completion report fields.

Keep it compact. Do not duplicate the full parent skill, unrelated workflow doctrine, or generic
skill-authoring rules.

## Stop or Rework If

- The worker must infer authority, inputs, domain standards, decisions, or output from hidden context.
- The orchestrator still appears allowed to perform worker-only actions inline.
- The worker can write, run commands, or cause side effects before reading its packet and contract.
- Missing or conflicting authority can produce anything other than a no-action `BLOCKED` return.
- The packet or contract requires supporting references to be read up front without action-point need.
- The worker contract is just a second copy of the parent skill.
- A reusable standalone capability would be clearer as direct invocation by skill name.
- A normal or high-risk dry run requires a material guess.
- Provenance matters but no durable artifact records the producer boundary.

If the same skill legitimately has simple direct cases and complex orchestrated cases, keep the mode
boundary explicit in `SKILL.md` and load only the surface reference needed for the mode being authored
or reviewed.
