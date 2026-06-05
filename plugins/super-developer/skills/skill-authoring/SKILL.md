---
name: skill-authoring
description: Creates or revises agent skills using compact eager workflows, explicit line budgets, and true on-demand references. Use when adding a skill, rewriting a skill, reviewing skill structure, or aligning a prompt/skill for progressive disclosure. Do not use for the domain task the skill would perform.
---

# Skill Authoring

Create or revise an agent skill whose eager instructions are enough to act safely, while detailed manuals, templates, examples, and edge cases load only when the workflow reaches them.

This is a meta skill: it defines the skill-writing pattern, not a domain workflow.

## Line Budget

- Target: 80–100 lines for a normal nontrivial skill.
- Acceptable compact skill: 40–80 lines when the workflow is simple.
- Soft ceiling: 120 lines.
- Hard maximum: 150 lines.
- If safety requires more than 150 eager lines, split details into one-hop references or scripts instead of expanding `SKILL.md`.

## Canonical Shape

Use this shape unless the user explicitly asks for another format:

```md
---
name: <skill-name>
description: <capability>. Use when <specific triggers>. Do not use when <near-miss cases>.
---

# <Skill Name>

<mission paragraph: what outcome this skill produces and how to think about it.>

## Always

- <non-negotiable invariant>

## Do

1. <high-level workflow step>
2. <load mandatory reference inline only if this step needs it>

## Load if needed

- <optional concrete condition> → `references/<file>.md`

## Stop if

- <condition requiring user input, safer workflow, or refusal to invent>

## Output

Return <fixed response fields, only if useful>.
```

## Always

- Frontmatter is routing only: capability, trigger phrases, and near-miss exclusions.
- Do not put project-specific reference names in frontmatter unless the skill itself is project-specific.
- `SKILL.md` owns mission, invariants, high-level workflow, mandatory step-local reference loads, stop gates, and output shape.
- The eager workflow must be rich enough that the agent understands what to do before opening references.
- `Do` is the workflow; it is not a list of references.
- Inline a reference in `Do` only when that step cannot be performed safely or correctly without it.
- `Load if needed` lists only optional references triggered by concrete conditions.
- Do not list second-hop references in the top-level skill just because another reference may load them.
- References are one-hop, boundary-specific, and loaded only at action points.
- Scripts are for deterministic validation, formatting, generation, or mechanical inspection.
- Move detailed templates, long examples, checklists, edge cases, API details, and report formats out of `SKILL.md`.
- Remove broad context bundles, duplicated doctrine, background essays, stale compatibility language, and generic advice the model can infer safely.

## Do

1. Identify the skill purpose, exact activation triggers, and near-miss cases that should not activate it.
2. Decide whether a new skill is needed or whether an existing skill should be routed to instead.
3. Draft frontmatter for routing only; keep workflow and reference details out of the description.
4. Design the eager workflow before drafting references: sequence the major phases, decision gates, mandatory loads, stop gates, and final output.
5. Draft `Always` as non-negotiable invariants only.
6. Draft `Do` as numbered workflow steps. Put mandatory references inline at the precise step where their rules are required.
7. Draft `Load if needed` for optional refs only. Delete the section if no optional refs remain.
8. Draft `Stop if` for ambiguity, unsafe action, missing authority, scope conflict, or places where the agent must ask instead of inventing.
9. Draft `Output` only when the skill needs a fixed handoff or response shape.
10. Run a compression pass: remove duplicated rules, second-hop refs, long examples, and anything better owned by a reference or script.
11. Verify line count, link targets, activation triggers, near-miss behavior, and that every reference has a concrete load condition.

## Load if needed

- A template, checklist, report format, example, or edge-case rule would bloat eager instructions → create or update `references/<topic>.md`
- A deterministic operation would otherwise be described repeatedly in prose → create or update `scripts/<tool>`
- A shared rule exists elsewhere → point to it only at the workflow step or optional condition that actually needs it

## Stop if

- Purpose, triggers, near-miss cases, or expected output are ambiguous.
- Safe operation would require more than 150 eager lines.
- A proposed reference has no concrete mandatory step or optional load condition.
- The draft duplicates another skill instead of routing to it.
- The user wants hidden conversation context to substitute for durable skill instructions.

## Output

Return the skill path, line count, trigger summary, near-miss exclusions, canonical-shape check, mandatory inline references, optional lazy references, references/scripts created or changed, removed over-eager content, checks run, and unresolved authoring decisions.
