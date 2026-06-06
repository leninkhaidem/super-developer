---
name: skill-authoring
description: Creates or revises agent skills using compact eager workflows, explicit line budgets, and true on-demand references. Use when adding a skill,
rewriting a skill, reviewing skill structure, or aligning a prompt/skill for progressive disclosure. Do not use for the domain task the skill would perform.
---

# Skill Authoring

Create or revise an agent skill whose eager instructions are enough to act safely, while detailed manuals, templates, examples, and edge cases load only when
the workflow reaches them.

This is a meta skill: it defines the skill-writing pattern, not a domain workflow.

## Line Budget

- `SKILL.md` target: 80–140 normal-width lines; hard maximum: 150. Do not satisfy line budgets by packing long lines.
- `SKILL.md` word target: 600–1,200; reference target: 300–900 words. Justify larger files by distinct safety value.
- Reference file target: 60–130 normal-width lines; hard maximum: 150 lines.
- Keep universal workflow, safety, routing, output, and pre-reference decision rules eager when they fit.
- Compression means fewer words/chars and clearer boundaries, not fewer physical lines only.
- If safety still needs more after compression, split only delayed boundaries into one-hop references or scripts.

## Folder Structure

Use `skills/<skill-name>/SKILL.md`, skill-local `references/`, skill-local `scripts/`, and package/plugin-level shared `references/`.

Do not deep-link another skill's private references; invoke that skill by name or promote the rule to a shared reference.

## Canonical Skill Shape

Use this shape unless the user explicitly asks for another format:

```md
---
name: <skill-name>
description: <capability>. Use when <specific triggers>. Do not use when <near-miss cases>.
---
# <Skill Name>
<mission paragraph>
## Always
- <non-negotiable invariant>
## Do
1. <workflow step>
2. <load mandatory reference only if this step needs it>
3. <invoke another skill by exact skill name when it owns the boundary>
## Load if needed
- <optional concrete condition> → `references/<file>.md`
## Stop if
- <condition requiring user input, safer workflow, or refusal to invent>
## Output
Return <fixed response fields, only if useful>.
```

## Reference File Shape

References are not skills. They have no frontmatter or routing description. The parent skill owns when to load them; the reference states the boundary it owns
after loading.

Shape: title, one-sentence boundary, concise `Contract`/`Do`/`Stop if` sections when useful. Each reference has one boundary and no hidden second-hop
references. Its load condition belongs in the parent skill or current workflow step.

## Reference Economy

- Fewer stronger references are better than many tiny fragments.
- Create a reference only for a distinct delayed boundary: mode-specific workflow, phase-specific gate, rare branch, long template/example, manual checklist, or
  specialized role instructions.
- If multiple references are always loaded together, consolidate them or inline universal rules into `SKILL.md`.
- Do not create references that only hold severity labels, report skeletons, generic routing rules, or tiny rules needed before reference choice.
- Mode setup and mode actions usually belong in the same mode reference unless actions are rarely reached and large enough to justify separation.
- Count reference files, words, chars, total reference lines, and long-line outliers; optimize for what the invoking agent actually loads, not just for a small
  `SKILL.md`.

## Always

- Frontmatter is routing only: capability, trigger phrases, and near-miss exclusions.
- Do not put project-specific reference names in frontmatter unless the skill itself is project-specific.
- `SKILL.md` owns mission, invariants, workflow, universal operating rules, mandatory step-local reference loads, stop gates, and output shape.
- The eager workflow must be rich enough that the agent understands what to do before opening references; do not underuse the 150-line budget or game it with
  dense prose.
- `Do` is the workflow, not a list of references.
- Load a reference in `Do` only when that step cannot be performed safely or correctly without it; otherwise make it lazy or delete it.
- Mention another skill by exact skill name only, never by relative or absolute path to its `SKILL.md`.
- Do not list another skill's private references; invoke that skill or use a shared reference.
- `Load if needed` lists only optional references triggered by concrete conditions.
- References are one-hop, boundary-specific, and loaded only at action points; always-loaded references should be rare and substantial.
- Scripts are for deterministic validation, formatting, generation, or mechanical inspection.
- Move long templates, examples, edge cases, API details, and bulky report formats out of `SKILL.md`; keep short universal formats eager when they prevent extra
  always-load refs.
- Remove broad context bundles, duplicated doctrine, background essays, stale compatibility language, tiny fragment refs, and generic advice the model can infer
  safely.

## Do

1. Identify purpose, activation triggers, and near-miss cases that should not activate the skill.
2. Decide whether a new skill is needed or whether an existing skill should be invoked by name.
3. Draft frontmatter for routing only; keep workflow, reference paths, and other skill paths out of the description.
4. Design the eager workflow first: major phases, decision gates, mandatory loads, skill invocations, stop gates, and output.
5. Spend eager budget on universal rules needed before or during mode/reference choice; stay under 150 lines.
6. Draft `Always`, `Do`, `Load if needed`, `Stop if`, and `Output`; delete optional sections that add no value.
7. Draft references only for concrete delayed boundaries; keep each under line cap and use the reference shape when useful.
8. Run a reference-economy pass: merge refs loaded together, inline tiny universal refs, and delete refs that duplicate eager routing or generic formatting.
9. Run a compression pass: remove duplicated rules, cross-skill private-reference links, long examples, stale refs, and anything better owned by a reference or
   script.
10. Verify line/word/char counts, max-line outliers, link targets, triggers, near-miss behavior, reference totals, always-loaded refs, lazy refs, and every
    reference's parent load condition.

## Load if needed

- A mode, phase, template, manual checklist, long report format, example, or edge-case rule would bloat eager instructions and is not universal → create or
  update `references/<topic>.md`
- A deterministic operation would otherwise be described repeatedly in prose → create or update `scripts/<tool>`
- A shared rule exists elsewhere → point to it only at the workflow step or optional condition that actually needs it

## Stop if

- Purpose, triggers, near-miss cases, or expected output are ambiguous.
- Safe operation would require more than 150 eager lines, an over-dense word/char budget, or a reference would exceed 150 lines after compression.
- A proposed reference has no concrete mandatory step, optional load condition, or distinct delayed boundary.
- Several proposed references would always be loaded together but have not been consolidated.
- The draft duplicates another skill instead of invoking it by name.
- The user wants hidden conversation context to substitute for durable skill instructions.

## Output

Return the skill path, `SKILL.md` line/word/char counts, reference count and total lines/words/chars, per-reference counts, long-line outliers, always-loaded
references, optional lazy references, trigger summary, near-miss exclusions, canonical-shape check, skill-name invocations, references/scripts
created/changed/removed/merged, removed over-eager or over-fragmented content, checks run, and unresolved authoring decisions.
