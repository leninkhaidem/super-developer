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
- Spend the word budget on obligations, not phrasing. Near the ceiling, prune non-operative prose, merge duplicate
  meanings, or disclose branch-only detail; never remove required obligations or compress prose to fit.
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
1. <ordered action with a checkable, exhaustive result>
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
- Treat each description or load condition as a context pointer: name its target, give each distinct branch one trigger,
  collapse synonymous triggers, and front-load the wording that discriminates when it fires.
- `SKILL.md` owns mission, invariants, ordered workflow, universal decisions, action-point loads, stops, and output.
  Progressive disclosure delays a load; only a fresh worker/session boundary provides context isolation.
- `Do` is executable work, not a list of references. Give each step a checkable, exhaustive completion criterion that
  accounts for every required artifact, case, or rule in its scope.
- Never rely on “best practices,” “clean,” “secure,” “maintainable,” or similar labels without concrete
  rules or an explicitly loaded governing contract.
- Prune unnecessary load, not required behavior. Preserve or relocate required obligations; never delete them
  because a model might infer them.
- Keep one authoritative source for each non-safety meaning. Repeat safety-critical commands, permissions, and
  prohibitions wherever omission could make the agent act unsafely.
- State the desired action positively. Retain unavoidable hard prohibitions, but pair each with its permitted action,
  safe default, or stop behavior so the target—not merely the forbidden behavior—guides execution.
- Establish authority and conflict precedence for each discoverable fact before replacing prose with an environment
  lookup; generated, local, or runtime state may govern when the task contract says so.
- Use `skills/<name>/SKILL.md`, skill-local `references/` and `scripts/`, and package-level shared `references/`.
- Invoke another skill by exact skill name. Never deep-link its private references; promote genuinely shared rules.
- Each reference holds one delayed boundary and has no frontmatter. The parent owns its load condition; a reference
  must not silently require another reference.
- Scripts perform deterministic validation, formatting, generation, or inspection; prose owns judgment.
- Fewer strong references are better than fragments. Merge references that are always loaded together.

## Pruning Gate

Before completion, prune in this order:

1. Resolve governing authority and conflicts. Inventory operative obligations: activation, authority, inputs, workflow,
   decisions, safety, scope, domain quality, verification, stops, and output. Classify superseded rules separately.
2. Collapse duplicate non-safety meanings into one authoritative location; keep action-local safety repetition.
3. Remove an environment cache only after identifying its authoritative source, conflict precedence, and a cheap,
   reliable lookup. Retain prose when lookup cannot preserve correctness, safety, reproducibility, or portability.
4. Move branch-only supporting detail behind an action-point pointer; keep selection criteria, prerequisites, authority,
   and cross-branch safety eager, and require the load before the first governed action.
5. Delete superseded, stale, or irrelevant material only after authority resolution proves it is not operative.
6. Treat a suspected no-op as empirical. Make the instruction the sole variable in bounded, side-effect-free repeated
   runs with the same candidate-specific trigger, host, model, and settings; compare every applicable completion
   criterion. Retain it when execution is unavailable, unstable, or inconclusive, and never apply the no-op label to
   an operative obligation; followability reasoning alone is not evidence.

Compare the before/after inventory. The gate fails if pruning removes, weakens, scatters, or obscures behavior, or if
shortening requires more inference. After moves, co-locate each concept's definition, rules, defaults, and caveats.

## Consumer Followability Gate

Before completion, verify that the created or revised skill tells its target agent:

- exactly when to activate and when not to activate, with each routing/load pointer covering its distinct branches;
- required inputs, where they come from, and what to do when they are missing or conflicting;
- one ordered path through the normal case, with checkable and exhaustive completion conditions;
- concrete decision rules, safe defaults, and the boundary between proceed, ask, stop, refuse, and escalate;
- which references are mandatory or optional and the exact action that requires each load;
- write scope, permissions, forbidden actions, and locally repeated safety rules where relevant;
- required verification and the fixed or bounded completion output;
- definitions for project-specific terms, artifacts, states, and role boundaries that affect action.

Without performing domain side effects, test each routing/load pointer with one positive case per branch and one
near miss, then reason through one representative normal task and one ambiguous, failure, or high-risk task. The gate
fails if the target agent must guess a material action, invent authority, infer a quality standard, read every reference
up front, or recover an obligation lost or obscured during pruning.

## Do

1. Select the mode and authority from the request:
   - **review:** inspect and report findings without modifying files unless edits are explicitly authorized;
   - **create or revise:** edit only the authorized skill scope.
2. Inspect repository instructions, the target skill and all its references/scripts when present, the existing skill
   inventory, and applicable shared contracts before deciding what belongs in the skill.
3. Identify the purpose, target agent, success condition, required inputs, activation triggers, near misses, target
   host, and invocation policy: **both** (default), **user-only**, or **model-only**.
4. Decide whether to revise an existing skill, invoke another skill by name, or create a new capability.
5. Select the execution surface from visible task behavior:
   - **standalone direct:** one agent can safely complete the task without parent-only approval, producer records,
     packet construction, or post-worker validation;
   - **orchestrator plus worker contract:** a parent must resolve context, enforce gates, authorize scope, dispatch
     work, preserve producer records, or validate a result;
   - **explicit hybrid:** both task shapes genuinely occur; state the mode decision before branch-specific loads.
   For an orchestrated or hybrid surface, load `references/orchestrator-worker-contracts.md` before evaluating or
   drafting it.
6. If the mode is **review**, evaluate the files against `Always`, both gates, reference economy, host-supported
   invocation behavior, and
   `${SUPER_DEVELOPER_PLUGIN_ROOT}/skills/skill-authoring/scripts/audit-skill.py <skill-dir-or-SKILL.md>`. Simulate
   pruning by inventorying what
   should be retained, relocated, or removed; require existing evidence for no-op claims and report missing evidence.
   Report findings and stop; do not draft, add, update, or edit files.
7. For **create or revise** mode only, draft frontmatter for routing. Keep **both** unless requirements make discovery
   or manual entry unavailable. Encode user-only/model-only with host-specific fields such as
   `disable-model-invocation` or `user-invocable` only when authoritative host evidence proves their semantics; stop
   rather than let portable frontmatter widen a restriction. Verify name, routing, and description budget.
8. Design the consumer workflow before compressing it: inputs, ordered actions, decisions/defaults, safety,
   action-point loads, checkable/exhaustive completion, verification, stops, and output.
9. Draft the canonical sections. Include concrete domain ground rules or load the applicable shared contract at the
   action it governs; a vague quality instruction is insufficient.
10. Add a reference only for a distinct delayed boundary such as a rare mode, specialized worker contract, long
    template, checklist, example set, or edge-case manual. State its parent load condition; give the reference a
    title, boundary, ordered actions when applicable, and stop rules.
11. Add or update a script when a repeatable check can be deterministic; do not encode semantic judgment as regex.
12. Run the Pruning Gate; record deletions, relocations, no-op evidence, and intentional exceptions. Define jargon
    and split dense multi-decision steps.
13. Run the Consumer Followability Gate, then run
    `${SUPER_DEVELOPER_PLUGIN_ROOT}/skills/skill-authoring/scripts/audit-skill.py <skill-dir-or-SKILL.md>` and resolve
    every error. Add `--strict` when the governing workflow requires strict auditing. Report target warnings and
    justified exceptions rather than hiding them. This plugin-root-qualified command runs the
    [shipped helper](scripts/audit-skill.py) in the skill-authoring skill's own asset folder;
    never resolve its executable path from the current or target skill directory.

## Stop if

- Purpose, target agent, triggers, near misses, required inputs, expected output, target host, or invocation policy
  remains ambiguous after one focused clarification.
- A required user-only or model-only restriction is unsupported or cannot be proven from authoritative host evidence.
- The execution surface or hybrid mode boundary cannot be selected from visible task behavior.
- The target agent would need hidden context, invented authority, or unstated quality/safety rules.
- Safe eager instructions or a reference still exceed the hard line maximum stated in `## Budgets` after honest
  compression.
- A proposed reference has no concrete parent load condition or creates a hidden second hop.
- The draft duplicates another skill instead of invoking it, or links another skill's private reference.
- Deterministic validation fails or a normal/risky dry run exposes a material guess.

## Output

- **Review:** return the skill path, execution surface, evidence-backed findings including pruning risks,
  followability dry-run results, counts/audit output, and unresolved decisions; state that no files changed.
- **Create or revise:** return the path, surface, trigger/near-miss summary, pruning summary, followability dry-run
  results, counts/audit output, loaded references, changed scripts, justified exceptions, and unresolved decisions.
