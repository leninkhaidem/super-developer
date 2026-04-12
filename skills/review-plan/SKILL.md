---
name: review-plan
description: >
  This skill should be used when the user asks to "review the plan", "validate the plan", "design
  review", "check the plan", "review tasks before implementing", or wants to validate a task plan
  before implementation begins. Triggers on phrases like "review plan", "design gate", "plan
  review", "validate design", "check plan quality". Also activates automatically as part of the
  development pipeline after plan creation.
---

# Review Plan: Design Review Gate

Validate a task plan through adversarial and completeness review before implementation begins. Sub-agents review the plan cold — from files only — simulating what an implementing agent will experience.

Do not execute this as the main agent. Spawn sub-agents for each reviewer role.

## Arguments

- `$ARGUMENTS` — Feature name (required). Must match a directory under `.tasks/`. If invoked from the pipeline, the feature name is inherited from the plan step.

---

## Step 1: Load Review Scope

1. Verify `.tasks/$ARGUMENTS/` exists. If not, list available features and ask the user to pick one.
2. Sub-agents read the files themselves. Do not pre-summarize or inject context — the point is to test whether the files are self-sufficient.

## Step 2: Spawn Review Sub-Agents in Parallel

Launch **two Opus-class sub-agents in parallel**, each reading `.tasks/$ARGUMENTS/CONTEXT.md` and `.tasks/$ARGUMENTS/tasks.json` from scratch:

---

### Agent A — Completeness Reviewer

Evaluates the plan for structural soundness. Must assess:

- **Coverage gaps:** Are there tasks or steps implied by CONTEXT.md that are missing from tasks.json?
- **Dependency integrity:** Are dependencies correctly specified? Are there implicit dependencies not captured?
- **Acceptance criteria quality:** Can every criterion be objectively verified? Are any vague or untestable?
- **Context sufficiency:** Could an agent with only these two files execute every task without guessing? Are there unstated assumptions?
- **Phase coherence:** Does each phase deliver a testable increment? Are tasks in the right phase?
- **Edge cases:** Are failure modes, error handling, and boundary conditions accounted for?

---

### Agent B — Adversarial Design Challenger

Aggressively challenges design decisions — not just correctness, but *whether this is the right approach*. Must:

- **Question every non-obvious choice:** For each significant decision in CONTEXT.md, ask "Why this approach and not [concrete alternative]?" Demand reasoning grounded in project constraints, performance, maintainability, or user needs.
- **Propose counter-alternatives:** Present plausible alternatives with trade-off analysis.
- **Flag unjustified complexity:** Identify elements that introduce complexity without a clear stated benefit. Challenge whether simpler alternatives were considered.
- **Probe for missing "why not" reasoning:** Surface approaches the plan implicitly rejects and require explicit reasoning for their exclusion.
- **Challenge task decomposition:** Is the breakdown the right granularity? Too coarse (risky for a single session) or too fine (overhead without value)?
- **Stress-test CONTEXT.md:** Does it actually give enough direction, or would an implementing agent make different design choices than intended?

---

## Step 3: Merge and Resolve

Collect findings from both agents. For each issue:

1. **Blockers from Agent A:** Resolve by updating CONTEXT.md or tasks.json.
2. **Challenges from Agent B:** Either provide documented rationale and record it in CONTEXT.md under "Design Decisions", OR accept the alternative and revise the plan.

## Step 4: Re-Review if Changes Were Made

If any changes were made to CONTEXT.md or tasks.json:

1. Spawn both agents again in parallel to re-review the updated plan.
2. Repeat until both agents approve — zero open blockers AND all design challenges resolved with recorded justifications.

**Maximum 3 re-review rounds.** If issues remain unresolved after 3 iterations, present the remaining issues to the user with a summary of what was resolved and what remains. Ask for manual resolution rather than continuing to loop.

## Step 5: Finalize

When both agents approve:

1. Update the feature `status` in tasks.json from `planned` to `reviewed`.
2. Report to the user:
   - Summary of issues found and how they were resolved
   - Design decisions that were strengthened with additional rationale
   - Confirmation that the plan is ready for implementation

---

## Pipeline Continuation

After the plan is reviewed and approved:
- If the user has given blanket approval to proceed through all stages (e.g., "proceed through all stages", "run end to end", "do everything"), continue immediately to implementation without asking.
- Otherwise, state: "Plan reviewed and approved. I'll proceed to implementation." Wait for user confirmation before proceeding.
- To proceed: Follow the implement skill instructions for this feature.

Pipeline: plan → **review-plan** → implement → [audit] → review-code

## Constraints

- Never soft-pass a review. Every blocker must be explicitly resolved and re-verified.
- Sub-agents work only from files — do not pass them conversation history or summaries.
- If the feature name is not provided or invalid, do not guess. Ask the user.
