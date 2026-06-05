---
name: skill-authoring
description: Creates or revises Super Developer skills using compact eager workflows and true on-demand references. Use when adding a new skill, rewriting a skill, aligning skill format, or reviewing skill progressive disclosure. Do not use for implementing product features, code review, audit, or task status.
---

# Skill Authoring

Create or revise a skill so the eager file gives enough workflow context without becoming the manual.

Target about 100 lines. Never exceed 150 lines in `SKILL.md`; if more is needed, move details into one-hop references loaded by concrete workflow conditions.

## Always

- Frontmatter is routing only: capability, specific triggers, and near-miss exclusions.
- `SKILL.md` owns mission, invariants, high-level workflow, mandatory step-local reference loads, stop gates, and output shape.
- References own detailed templates, examples, checklists, edge cases, safety rules, or artifact contracts.
- Inline a reference in `Do` only when that step cannot be performed safely or correctly without it.
- `Load if needed` lists only optional refs that are truly on-demand, not second-hop refs or broad context bundles.
- Keep references one level deep from the skill or shared `references/` directory.
- Prefer direct imperative bullets over background essays.
- Do not add tests that assert Markdown prompt/reference wording.
- Do not inspect proof artifacts or run proof lifecycle commands unless the user explicitly asks.

## Do

1. Identify the skill purpose, exact activation triggers, and near-miss cases that should not trigger it.
2. Decide the smallest useful eager workflow before writing. Use this structure unless the user requests otherwise: `Always`, `Do`, `Load if needed`, `Stop if`, `Output`.
3. Draft or revise frontmatter so the description is enough for routing but does not include workflow detail.
4. Draft `Always` as non-negotiable invariants only; remove generic advice the model can infer safely.
5. Draft `Do` as the high-level workflow. Put mandatory reference loads inline at the step where they are required.
6. Draft `Load if needed` only for optional references triggered by a concrete condition. Delete it if no optional refs remain.
7. Draft `Stop if` for conditions requiring user input, safer workflow, scope correction, or refusal to invent missing requirements.
8. Draft `Output` only when the skill needs a fixed response shape or handoff fields.
9. Run a compression pass: remove duplicated doctrine, second-hop references, stale prose, long examples, and anything better owned by a reference.
10. Check the line budget, links, and trigger fit before presenting or committing.

## Load if needed

- A detailed template, report format, checklist, or example would push `SKILL.md` past the line budget → create or update `references/<topic>.md`
- A deterministic validation, generation, or formatting step would otherwise be repeatedly described in prose → create or update `scripts/<tool>`
- A shared rule already exists outside the skill → point to the shared reference only at the workflow step or optional condition that needs it

## Stop if

- The requested skill purpose, triggers, or near-miss boundaries are ambiguous.
- The skill needs more than 150 eager lines to be safe.
- A proposed reference is not loaded by any concrete workflow step or optional condition.
- The draft duplicates another skill's responsibility instead of routing to it.
- The user asks to preserve hidden conversation context instead of durable instructions or references.

## Output

Return the changed skill path, line count, trigger summary, mandatory inline references, optional lazy references, removed/avoided over-eager content, checks run, and any unresolved authoring decisions.
