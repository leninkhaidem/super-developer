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

## Step 2: Load Model Preferences

Read `${CLAUDE_PLUGIN_ROOT}/references/model-preferences.md` for the canonical schema and resolution procedure.

Resolve model preferences for two agent roles:
- **Agent A (completeness reviewer):** Uses the `review-plan` key. Hardcoded default: `adaptive`.
- **Agent B (adversarial challenger):** Uses the `skeptic-agent` key. Hardcoded default: `adaptive`.

**Adaptive interpretation for review-plan:** Agent A uses Sonnet. Agent B is governed by the `skeptic-agent` key — when `skeptic-agent` resolves to `adaptive`, use the strongest available model (Opus).

Carry the resolved models forward into Step 4.

## Step 3: Pre-Review Announcement (Gate 1)

Before spawning reviewers, present the user with a plain-language summary of what the plan delivers. This is a **projection** from plan artifacts — do not synthesize or add content not backed by CONTEXT.md or tasks.json.

```markdown
## Plan Deliverables — <Feature Name>

### What Will Be Delivered
- <feature/functionality derived from tasks.json, one bullet per meaningful deliverable>

### ⚠️ Flags
- <implicit consequences the user may not be aware of: new dependencies, breaking changes, migration needs, performance impacts>

### Out of Scope
- <from CONTEXT.md Out of Scope section>
```

**Rules:**
- Every bullet must trace to a specific plan element (task ID or CONTEXT.md section).
- **Blocking gate** — the user must explicitly approve before review proceeds.
- If the user rejects: ask what to change, apply edits to CONTEXT.md or tasks.json, and re-present Gate 1. Do not proceed to Step 4 until approved.

## Step 4: Spawn Review Sub-Agents in Parallel

Launch **two sub-agents in parallel** (models per Step 2), each reading `.tasks/$ARGUMENTS/CONTEXT.md` and `.tasks/$ARGUMENTS/tasks.json` from scratch:

### Reviewer Output Format

Both agents must return findings in this exact format — no preamble, no summary, no prose outside
the format:

```
[SEV] TARGET — TITLE
ISSUE: <1 sentence, what's wrong>
FIX: <1 sentence, concrete resolution>
```

### Severity Taxonomy

Every finding must be classified:

| Severity | Label | Meaning |
|---|---|---|
| `[BLOCKER]` | Must resolve | Plan cannot proceed to implementation. |
| `[CRITICAL]` | Strongly recommended | Significant quality, completeness, or design risk. |
| `[SUGGESTION]` | Non-blocking | Improvement opportunity. May omit the `FIX:` line. |

### TARGET Locator Grammar

Each finding must reference its plan element using one of these locator patterns:

| Pattern | Example | Use for |
|---|---|---|
| `CONTEXT:<section-slug>` | `CONTEXT:architecture` | Findings about CONTEXT.md sections |
| `TASK:<task-id>` | `TASK:P1-T003` | Findings about a specific task |
| `TASK:<task-id>.<field>` | `TASK:P2-T001.dependencies` | Findings about a specific task field |
| `PHASE:<phase-id>` | `PHASE:P1` | Findings about phase-level concerns |
| `PHASE:<phase-id>.<aspect>` | `PHASE:P1.coherence` | Findings about a specific phase aspect |
| `GLOBAL:<concern>` | `GLOBAL:scope` | Cross-cutting findings (scope, acceptance criteria patterns) |

Multi-target findings: use the primary target, note others in the ISSUE line.

### Format Rules

- All `[BLOCKER]` and `[CRITICAL]` findings reported — no count caps.
- `[SUGGESTION]` findings: report up to 10 in detail. If more exist, append: `+N more suggestions omitted`
- No introductory text, no concluding summaries.
- `[SUGGESTION]` may omit the `FIX:` line if no specific action is needed.
- If no findings: respond with exactly `NONE`
- Do NOT append `NONE` after findings — `NONE` means zero findings only.

### Severity Resolution Rules

The orchestrator applies these rules during merge-and-resolve:

- **`[BLOCKER]`** — Must be resolved before the plan advances. All blockers require plan edits and re-verification.
- **`[CRITICAL]`** — Must be explicitly accepted with documented rationale OR resolved with plan edits.
- **`[SUGGESTION]`** — Logged for consideration. No resolution required.

---

### Agent A — Completeness Reviewer

Evaluates the plan for structural soundness. Must assess:

- **Coverage gaps:** Are there tasks or steps implied by CONTEXT.md that are missing from tasks.json?
- **Dependency integrity:** Are dependencies correctly specified? Are there implicit dependencies not captured?
- **Acceptance criteria quality:** Can every criterion be objectively verified? Are any vague or untestable?
- **Context sufficiency:** For each task, can an agent determine WHAT to build from the task description alone? It should NOT need to determine exact implementation from the description — that comes from codebase exploration. If two reasonable agents would build fundamentally different things from the same description, the description needs clarifying constraints. But if the difference is only in implementation approach (not outcome), the description is sufficient.
- **Phase coherence:** Does each phase deliver a testable increment? Are tasks in the right phase?
- **Edge cases:** Are failure modes, error handling, and boundary conditions accounted for?

**Output:** Use the Reviewer Output Format above. Primarily use `TASK:*`, `PHASE:*`, and `GLOBAL:*` targets. Findings in other TARGET domains are not prohibited.

---

### Agent B — Adversarial Design Challenger

Aggressively challenges design decisions — not just correctness, but *whether this is the right approach*. Must:

- **Question every non-obvious choice:** For each significant decision in CONTEXT.md, ask "Why this approach and not [concrete alternative]?" Demand reasoning grounded in project constraints, performance, maintainability, or user needs.
- **Propose counter-alternatives:** Present plausible alternatives with trade-off analysis.
- **Flag unjustified complexity:** Identify elements that introduce complexity without a clear stated benefit. Challenge whether simpler alternatives were considered.
- **Probe for missing "why not" reasoning:** Surface approaches the plan implicitly rejects and require explicit reasoning for their exclusion.
- **Challenge task decomposition:** Is the breakdown the right granularity? Too coarse (risky for a single session) or too fine (overhead without value)?
- **Stress-test CONTEXT.md:** Does it give enough direction on intent, architecture, and constraints? An implementing agent should know WHAT to build and WHERE it fits — but derives HOW from codebase exploration. Flag missing intent or missing constraints, not missing implementation details.
- **Challenge task description verbosity:** If task descriptions prescribe exact code, line numbers, or step-by-step instructions, flag this as over-specification. Task descriptions should state intent and constraints; implementing agents derive the rest.

**Output:** Use the Reviewer Output Format above. Primarily use `CONTEXT:*`, `GLOBAL:*`, and `PHASE:*` targets. Findings in other TARGET domains are not prohibited.

---

## Step 5: Merge and Resolve

Collect structured findings from both agents. Apply severity resolution rules:

1. **`[BLOCKER]` findings:** Resolve by updating CONTEXT.md or tasks.json. All blockers must be resolved before advancing.
2. **`[CRITICAL]` findings:** Either provide documented rationale and record it in CONTEXT.md under "Design Decisions", OR accept the alternative and revise the plan. Each critical must be explicitly addressed.
3. **`[SUGGESTION]` findings:** Log for consideration. No resolution required.

## Step 6: Re-Review if Changes Were Made

If any changes were made to CONTEXT.md or tasks.json:

1. Spawn both agents again in parallel to re-review the updated plan.
2. Repeat until both agents approve — zero open `[BLOCKER]` findings AND all `[CRITICAL]` findings resolved with recorded justifications.

**Maximum 3 re-review rounds.** If issues remain unresolved after 3 iterations, present the remaining issues to the user with a summary of what was resolved and what remains. Ask for manual resolution rather than continuing to loop.

## Step 7: Post-Review Announcement (Gate 2)

When both agents approve, present the user with the **final** plain-language summary of what the plan delivers. This reflects the state after all review rounds — including any changes made during merge-and-resolve.

Use the same template as Gate 1 (Step 3), with one addition: tag items that were added or modified during review:

```markdown
### What Will Be Delivered
- JWT auth middleware on all /api/* routes
- Rate limiting (200 req/15min/IP) ← modified by review
- Error recovery for token refresh failures ← added by review
- CORS configuration for new namespace
```

**Rules:**
- Every `← added by review` or `← modified by review` marker must map to a specific review finding that caused the change.
- **Blocking gate** — the user must explicitly approve before finalization.
- If the user rejects: ask what to change, apply edits to CONTEXT.md or tasks.json, and **re-review from Step 4** (mandatory — plan changes after review require re-verification). Gate 2 is re-presented after the new review completes.
- **No plan edits are permitted between Gate 2 approval and Step 8 finalization.**

## Step 8: Finalize

When the user approves the post-review announcement:

1. Update the feature `status` in tasks.json from `planned` to `reviewed`.
2. Report to the user:
   - Summary of issues found and how they were resolved
   - Design decisions that were strengthened with additional rationale
   - Confirmation that the plan is ready for implementation

---

## Pipeline Continuation

If this stage failed or requires user intervention, STOP. Do not invoke the next stage.

If blanket approval was given (e.g., "proceed through all stages", "run end to end", "do everything"), invoke immediately. Otherwise, state: "Plan reviewed and approved." Wait for user confirmation. Then invoke:

Use the Skill tool with: skill: "implement", args: "<feature-name>"

Do NOT attempt to execute the next skill's logic inline. The Skill tool loads it properly.

## Constraints

- Never soft-pass a review. Every blocker must be explicitly resolved and re-verified.
- Sub-agents work only from files — do not pass them conversation history or summaries.
- If the feature name is not provided or invalid, do not guess. Ask the user.
