# Standalone Direct Skill Surface

Boundary: load only when authoring, revising, or reviewing a skill that should be invoked directly
by skill name as a self-contained capability.

## Contract

Use a standalone direct surface when the skill owns the whole task workflow. Any authorized agent
should be able to use the skill from visible inputs, without a parent orchestrator conferring extra
authority through a private worker packet.

A direct skill may still be invoked by another workflow. The parent should mention the skill by exact
skill name and pass the task-specific inputs the skill needs. The parent should not deep-link private
references or pass hidden conversation state to make the direct skill usable.

Direct does not mean eager-only. The skill may have lazy references for templates, mode-specific
steps, examples, or rare edge cases. It means the `SKILL.md` entry point is itself the portable
contract for safe use.

## Select This Surface When

- The skill can discover or receive required inputs safely from the prompt, repo, files, or standard
  tool output.
- Safety gates, setup, action steps, verification, stops, and output shape are owned by the skill.
- No separate parent must preserve provenance, choose worker roles, sequence multiple workers,
  approve high-impact side effects, or enforce artifact ownership across roles.
- Delegation can be expressed as: invoke this named skill with these explicit inputs.
- A delegated agent using the skill directly would not need to know whether it is a main agent,
  worker, reviewer, or other runtime identity.

## Authoring Rules

1. Put routing triggers and near-miss exclusions in frontmatter only.
2. Keep the eager workflow rich enough to start safely without reading optional references.
3. Put task phases, universal safety gates, mandatory step-local loads, stops, and output shape in
   `SKILL.md`.
4. Use references only for delayed details that are not always needed: templates, long examples,
   mode-specific playbooks, specialized checklists, or rare branches.
5. When another workflow should call this skill, phrase it as direct invocation by skill name with a
   compact input packet. Do not require the parent to pass this skill's private references.
6. If the direct skill delegates internally, describe that delegation as part of its own workflow and
   keep worker-only instructions behind lazy references when they are not universal.

## Inline Mention Pattern

Use inline mentions when another skill reaches a boundary owned by the direct skill:

```text
Invoke `<skill-name>` with <explicit inputs>; do not perform that workflow inline.
```

The inline mention should name the expected inputs and the reason the boundary belongs to the other
skill. It should not list that skill's private references, internal templates, or hidden assumptions.

## Stop or Switch Surface If

- A parent must approve or preserve state before the work is safe.
- Worker authority must come from a packet or contract rather than direct skill instructions.
- Multiple roles must be coordinated and validated by an orchestrator.
- Durable artifacts need provenance showing which worker contract produced them.
- The skill's direct entry point would be easy to mistake for permission to do worker-only actions.

In those cases, author an orchestrator plus worker-contract surface instead.
