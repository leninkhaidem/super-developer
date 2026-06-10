# Delegation Surfaces

Boundary: choose and document one skill's delegation surface: standalone direct,
orchestrator plus worker-contract reference, or rare explicit hybrid.

## Contract

- Make authority visible in durable instructions, not inferred from agent identity.
- Prefer one primary surface; use hybrid mode only when two task shapes are truly valid.
- Keep routing in the parent skill frontmatter and load condition, not in this reference.
- Keep worker-only instructions in a contract reference when delegation authority matters.
- Do not add hidden second-hop local links, frontmatter, or local project-specific examples.
- Apply existing line, word, reference-economy, and one-boundary rules while choosing the surface.

## Standalone Direct Surface

Choose standalone direct when the skill owns the complete safe workflow.

Use it when:

- Setup, gates, actions, verification, and output are self-contained.
- Any authorized agent can use the skill by exact skill name with task-specific inputs.
- Required context can be supplied in the prompt or discovered safely by the skill.
- No parent agent must preserve separate provenance, approvals, status transitions, or artifact ownership.
- Delegation is clearer as "use the named skill for this task" than as a private worker contract.

Document it by making `SKILL.md` sufficient for the whole task:

- Frontmatter says capability, triggers, and near misses only.
- Eager workflow covers the normal path, safety gates, stops, and verification shape.
- Optional references cover delayed manuals or examples, not missing authority.
- Output tells the caller what was done, checked, changed, and left unresolved.

Example shape: a focused tool-setup skill can be direct when it contains install checks,
configuration steps, troubleshooting, verification, and refusal gates without parent orchestration.

## Orchestrator Plus Worker-Contract Surface

Choose orchestrator-facing design when the current agent must coordinate authority before
worker actions create durable artifacts or high-impact outcomes.

Use it when the parent-level workflow owns:

- Approval gates, source selection, path safety, package or artifact ownership, or status changes.
- Model or worker choice, multi-agent routing, independent verification separation, or provenance capture.
- A self-contained packet that gives a worker its goal, source paths, safe edit paths, expected outputs,
  required reference paths, validation commands, and stop conditions.
- A process boundary that review or validation must detect from files alone.

Document it by separating responsibilities:

- The skill entry point stays orchestrator-facing: resolve inputs, enforce gates, prepare packets,
  dispatch workers when allowed, validate returned artifacts, and summarize results.
- The worker-contract reference owns concrete worker actions and proof/output requirements.
- The worker acts from the packet and contract, not from hidden chat history or runtime labels.
- Durable provenance lives in the artifact model when process authority matters.
- Do not expose a private worker role as a routed skill unless it is reusable as a standalone capability.

Never make perceived caller role or delegated status the mode or authority boundary. Use visible task
shape, approved scope, gates, artifact ownership, packet contents, and explicit contract paths instead.

## Rare Explicit Hybrid Surface

Choose hybrid only when the same capability is legitimately direct for simple task shapes and
orchestrated for higher-risk task shapes.

Document hybrid mode by naming both modes in `SKILL.md`:

- Direct mode: the skill completes the simple case from its eager workflow and optional references.
- Orchestration mode: the skill enforces gates, prepares a packet, and uses a worker-contract reference.
- The switch is based on visible inputs such as risk, artifact ownership, approvals, durable outputs,
  or user-approved scope.
- Worker-only instructions still live outside eager prose when inline authority would be ambiguous.

Stop and choose a single surface, split the skill, or redesign if the mode boundary cannot be stated
compactly, safely, and without identity detection.

## Verification Questions

- Can a future agent choose the surface from task shape, inputs, gates, artifacts, or packet contents?
- Is direct mode complete without private reference paths or hidden caller context?
- Is orchestrator mode clearly prevented from doing worker-only durable actions inline?
- Can the worker act from the packet and contract without guessing authority?
- Are provenance, validation, and output fields owned by the artifact or workflow that needs them?
- Does the draft avoid runtime identity detection, local named examples, frontmatter, second-hop links,
  and duplicated generic authoring doctrine?
