---
name: skill-authoring
description: >
  Creates or revises agent skills using compact eager workflows, explicit line budgets, and true
  on-demand references. Use when adding a skill, rewriting a skill, reviewing skill structure,
  or aligning a prompt/skill for progressive disclosure. Do not use for the domain task the skill
  would perform.
---

# Skill Authoring

Create/revise skills with safe eager instructions; detailed manuals, templates, examples, and edge cases load only when needed.

## Budgets

- `SKILL.md`: target 80–140 normal-width lines, hard maximum 150, target 600–1,200 words.
- References: target 60–130 normal-width lines, hard maximum 150, target 300–900 words.
- Do not satisfy budgets by packing long lines. Justify larger files by safety value.
- Keep universal workflow, safety, routing, output, and pre-reference decision rules eager.
- Split only delayed boundaries into one-hop references or scripts after compression.

## Folder Structure

Use `skills/<skill-name>/SKILL.md`, skill-local `references/`, skill-local `scripts/`, and
package/plugin-level shared `references/`. Do not deep-link another skill's private references;
invoke that skill by name or promote the rule to a shared reference.

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

References are not skills. They have no frontmatter or routing description. The parent skill owns
load conditions; the reference states its boundary after loading. Use title, boundary sentence, and
concise `Contract`/`Do`/`Stop if` sections when useful. No hidden second-hop references.

## Reference Economy

- Fewer stronger references are better than many tiny fragments.
- Create a reference only for a distinct delayed boundary: mode workflow, phase gate, rare branch,
  long template/example, checklist, or specialized role instructions.
- If multiple references are always loaded together, consolidate them or inline universal rules.
- Do not create refs for severity labels, report skeletons, generic routing, or tiny pre-choice rules.
- Mode setup and actions usually belong together unless actions are rare and large.
- Optimize for what the invoking agent actually loads, not only for a small `SKILL.md`.
- Restate a safety-critical command, prohibition, or path at each lazily-loaded action point;
  locality there outranks deduplication, since the agent may not have loaded the shared reference.

## Always

- Frontmatter is routing only: capability, trigger phrases, and near-miss exclusions.
- Do not put project-specific reference names in frontmatter unless the skill itself is project-specific.
- Choose the delegation surface from visible task shape: standalone direct, orchestrator plus
  worker-contract, or explicit hybrid. Direct invocation needs no reference; never use runtime
  identity as the authority boundary.
- `SKILL.md` owns mission, invariants, workflow, universal rules, step-local loads, stops, and output.
- `Do` is the workflow, not a list of references.
- Load a reference in `Do` only when that step cannot be performed safely or correctly without it;
  otherwise make it lazy or delete it.
- Mention another skill by exact skill name only, never by path to its `SKILL.md`.
- Do not list another skill's private references; invoke that skill or use a shared reference.
- `Load if needed` lists only optional references triggered by concrete conditions.
- References are one-hop, boundary-specific, and loaded only at action points.
- Scripts are for deterministic validation, formatting, generation, or mechanical inspection.
- Move long templates, examples, edge cases, API details, and bulky report formats out of `SKILL.md`.
- State each fact, file role, constraint, or invariant once per file; refer back to it by name
  instead of restating it, and define each artifact or file role in exactly one place. Tokens are
  costly: do not pay for the same information twice.
- Remove broad bundles, duplicated doctrine, stale compatibility language, tiny fragment refs, and
  generic advice the model can infer safely.

## Do

1. Identify purpose, activation triggers, and near-miss cases.
2. Decide whether a new skill is needed or an existing skill should be invoked by name.
3. Classify the delegation surface before drafting detailed references:
   - standalone direct when the skill is self-contained and can be invoked by exact skill name;
   - orchestrator plus worker-contract when parent gates, packets, provenance, or role separation
     are material;
   - explicit hybrid only when visible task shapes require both surfaces and the mode boundary is
     compact enough to state eagerly.
4. Draft frontmatter for routing only; keep workflow, reference paths, and other skill paths out of
   the description.
5. Design the eager workflow first: phases, decision gates, mandatory loads, skill invocations,
   stop gates, and output.
6. Draft `Always`, `Do`, `Load if needed`, `Stop if`, and `Output`; delete optional sections that add
   no value.
7. Draft references only for concrete delayed boundaries; keep each under line cap and use the
   reference shape when useful.
8. Run reference-economy and compression passes: merge refs loaded together, inline tiny universal
   refs, collapse within-file restatements of the same fact or file role, delete duplicated routing,
   cross-skill private-reference links, stale refs, and long examples.
9. Verify counts, max-line outliers, links, triggers, near-miss behavior, reference totals,
   always-loaded refs, lazy refs, and every reference's parent load condition. Run
   `scripts/audit-skill.py --strict` when enforcing deterministic budgets.

## Load if needed

- Orchestrator/worker split, delegated authority packet, worker-contract reference, or provenance
  boundary is active → `references/orchestrator-worker-contracts.md`
- Hybrid mode is genuinely required → state the visible mode boundary eagerly; load the
  orchestrator/worker reference only for the orchestrated branch
- A mode, phase, template, checklist, long report format, example, or edge case would bloat eager
  instructions → create or update `references/<topic>.md`
- Deterministic metrics, frontmatter, link, and reference-budget checks are useful → run
  `scripts/audit-skill.py [--strict] <skill-dir-or-SKILL.md>`
- A deterministic operation would otherwise be repeated in prose → create or update `scripts/<tool>`
- A shared rule exists elsewhere → point to it only at the step or optional condition that needs it

## Stop if

- Purpose, triggers, near-miss cases, or expected output are ambiguous.
- The correct delegation surface or hybrid mode boundary is ambiguous.
- Safe operation would exceed 150 eager lines, over-dense prose, or a 150-line reference after compression.
- A proposed reference has no mandatory step, optional load condition, or distinct delayed boundary.
- Several proposed references would always be loaded together but have not been consolidated.
- The draft duplicates another skill instead of invoking it by name.
- The draft restates the same fact, file role, or constraint in multiple places within one file
  instead of stating it once.
- The user wants hidden conversation context to substitute for durable skill instructions.

## Output

Return the skill path, selected delegation surface, counts, long-line outliers, loaded/lazy refs,
trigger summary, near-miss exclusions, canonical-shape check, skill-name invocations, changed
references/scripts, removed over-eager or fragmented content, checks run, and unresolved decisions.
