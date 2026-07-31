---
name: skill-authoring
description: >
  Creates or revises compact, self-contained skills that mid-tier agents can execute reliably.
  Use when adding, rewriting, or structurally reviewing a skill. Do not use to perform its domain task.
---

# Skill Authoring

Create, revise, or review skills so always-needed instructions stay in `SKILL.md`, detail loads only at its
action point, and a competent mid-tier agent can follow the result without hidden context or expert inference.

## Budgets

- Frontmatter `description`: target 1–3 short content lines; hard maximum 280 folded characters.
- Judge complexity by words, not lines. A line cap is gameable — the same obligations reflowed into
  denser text still pass it — so tight line caps end up rewarding the unreadable density they were
  meant to prevent. Reformatting for clarity must always be free.
- `SKILL.md`: hard maximum 200 lines; word budget 1,800, target 600–1,500.
- References: hard maximum 200 lines; word budget 1,800, target 300–1,200.
- Only the line cap fails the audit. Word budgets and targets warn, and are author guidance.
- Keep lines at or below 120 characters where practical; never pack prose to satisfy a line budget.
- Spend the word budget on obligations, not phrasing. When a prompt nears its ceiling, remove or
  extract obligations; never compress prose to fit.
- Exceed a target only when concrete safety or workflow value justifies it; never exceed a hard maximum.

## Canonical Shape

Use this shape unless the user explicitly requires another format:

```md
---
name: <skill-name>
description: <capability>. Use when <triggers>. Do not use when <near misses>.
---
# <Skill Name>
<mission and success condition>
## Always
- <non-negotiable invariant>
## Do
1. <ordered action with an observable result>
## Load if needed
- <concrete condition> → `references/<file>.md`
## Stop if
- <ask, refuse, escalate, or do-not-invent condition>
## Output
Return <bounded result fields>.
```

Delete an optional section only when its behavior is unnecessary, not merely to save lines.

## Always

- Write for a competent mid-tier target agent with no access to hidden chat, unstated repository knowledge,
  or the author's reasoning.
- Frontmatter is routing only: capability, concrete triggers, and near-miss exclusions. Keep workflow, paths,
  rationale, examples, and evidence out of it.
- `SKILL.md` owns mission, invariants, ordered workflow, universal decisions, action-point loads, stops, and output.
- `Do` is executable work, not a list of references. Start each step with an action and make completion observable.
- Never rely on “best practices,” “clean,” “secure,” “maintainable,” or similar labels without concrete
  rules or an explicitly loaded governing contract.
- Do not remove workflow, safety, scope, domain-quality, verification, or output rules because a model might infer
  them. Remove only non-operative explanation and duplicated doctrine.
- Deduplicate explanatory prose, but repeat safety-critical commands, permissions, and prohibitions at each action
  point where the agent could otherwise act unsafely.
- Use `skills/<name>/SKILL.md`, skill-local `references/` and `scripts/`, and package-level shared `references/`.
- Invoke another skill by exact skill name. Never deep-link its private references; promote genuinely shared rules.
- Each reference holds one delayed boundary and has no frontmatter. The parent owns its load condition; a reference
  must not silently require another reference.
- Scripts perform deterministic validation, formatting, generation, or inspection; prose owns judgment.
- Fewer strong references are better than fragments. Merge references that are always loaded together.

## Consumer Followability Gate

Before completion, verify that the created or revised skill tells its target agent:

- exactly when to activate and when not to activate;
- required inputs, where they come from, and what to do when they are missing or conflicting;
- one ordered path through the normal case, with observable completion conditions;
- concrete decision rules, safe defaults, and the boundary between proceed, ask, stop, refuse, and escalate;
- which references are mandatory or optional and the exact action that requires each load;
- write scope, permissions, forbidden actions, and locally repeated safety rules where relevant;
- required verification and the fixed or bounded completion output;
- definitions for project-specific terms, artifacts, states, and role boundaries that affect action.

Without performing domain side effects, reason through one representative normal task and one ambiguous, failure,
or high-risk task. The gate fails if the target agent must guess a material action, invent authority, infer a
quality standard, or read every reference up front to know what to do.

## Do

1. Select the mode and authority from the request:
   - **review:** inspect and report findings without modifying files unless edits are explicitly authorized;
   - **create or revise:** edit only the authorized skill scope.
2. Inspect repository instructions, the target skill and all its references/scripts when present, the existing skill
   inventory, and applicable shared contracts before deciding what belongs in the skill.
3. Identify the purpose, target agent, success condition, required inputs, activation triggers, and near misses.
4. Decide whether to revise an existing skill, invoke another skill by name, or create a new capability.
5. Select the execution surface from visible task behavior:
   - **standalone direct:** one agent can safely complete the task without parent-only approval, producer records,
     packet construction, or post-worker validation;
   - **orchestrator plus worker contract:** a parent must resolve context, enforce gates, authorize scope, dispatch
     work, preserve producer records, or validate a result;
   - **explicit hybrid:** both task shapes genuinely occur; state the mode decision before branch-specific loads.
   For an orchestrated or hybrid surface, load `references/orchestrator-worker-contracts.md` before evaluating or
   drafting it.
6. If the mode is **review**, evaluate the existing files against `Always`, the Consumer Followability Gate,
   reference economy, and `scripts/audit-skill.py <skill-dir-or-SKILL.md>`. Report evidence-backed findings and
   stop; do not draft, add, update, or edit files.
7. For **create or revise** mode only, draft frontmatter for routing and verify its name, triggers, near misses,
   and description budget.
8. Design the consumer workflow before compressing it: inputs, ordered actions, decisions/defaults, safety,
   action-point loads, verification, stops, and output.
9. Draft the canonical sections. Include concrete domain ground rules or load the applicable shared contract at the
   action it governs; a vague quality instruction is insufficient.
10. Add a reference only for a distinct delayed boundary such as a rare mode, specialized worker contract, long
    template, checklist, example set, or edge-case manual. State its parent load condition; give the reference a
    title, boundary, ordered actions when applicable, and stop rules.
11. Add or update a script when a repeatable check can be deterministic; do not encode semantic judgment as regex.
12. Run economy and clarity passes: merge always-co-loaded references, remove stale or duplicated explanation,
    preserve action-local safety, define jargon, and split dense multi-decision steps.
13. Run the Consumer Followability Gate, then run `scripts/audit-skill.py <skill-dir-or-SKILL.md>` and resolve every
    error. Report target warnings and justified exceptions rather than hiding them.

## Stop if

- Purpose, target agent, triggers, near misses, required inputs, or expected output remain ambiguous after one
  focused clarification.
- The execution surface or hybrid mode boundary cannot be selected from visible task behavior.
- The target agent would need hidden context, invented authority, or unstated quality/safety rules.
- Safe eager instructions or a reference still exceed the hard line maximum stated in `## Budgets` after honest
  compression.
- A proposed reference has no concrete parent load condition or creates a hidden second hop.
- The draft duplicates another skill instead of invoking it, or links another skill's private reference.
- Deterministic validation fails or a normal/risky dry run exposes a material guess.

## Output

- **Review:** return the skill path, execution surface, evidence-backed findings, followability dry-run results,
  counts/audit output, and unresolved decisions; state that no files changed.
- **Create or revise:** return the path, surface, trigger/near-miss summary, followability dry-run results,
  counts/audit output, loaded references, changed scripts, justified exceptions, and unresolved decisions.
