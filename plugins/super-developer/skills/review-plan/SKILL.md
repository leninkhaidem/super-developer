---
name: review-plan
description: >
  This skill should be used when the user asks to "review the plan", "validate the plan", "design
  review", "check the plan", "review tasks before implementing", or wants to validate a task plan
  before implementation begins. Triggers on phrases like "review plan", "design gate", "plan
  review", "validate design", "check plan quality". Also activates automatically as part of the
  development pipeline after plan creation.
---

# Review Plan: Plan Review Gate

Validate a task plan through adversarial and completeness review before implementation begins. Sub-agents review the plan cold — from files only — simulating what an implementing agent will experience.

Do not execute this as the main agent. Spawn sub-agents for each reviewer role.

## Arguments

- `$ARGUMENTS` — Feature name (required). Must match a directory under `.tasks/`. If invoked from the pipeline, the feature name is inherited from the plan step.

---

## Step 1: Load Review Scope

1. Verify `.tasks/$ARGUMENTS/` exists and contains `SPEC.md` and `tasks.json`. If not, list available features and ask the user to pick one.
2. Sub-agents read the files themselves. Do not pre-summarize or inject context — the point is to test whether the files are self-sufficient.
3. Read `${CLAUDE_PLUGIN_ROOT}/references/work-packages.md`. The main agent uses it for deterministic package validation. Reviewers use it to judge whether task grouping, package sizing, and parallel-safety are appropriate.

## Step 2: Deterministic Plan Validation

Before spawning any review sub-agent, validate the plan mechanically from `.tasks/$ARGUMENTS/tasks.json`:

- JSON is valid and contains `phases` and `work_packages`.
- Task IDs are unique across all phases.
- Task dependencies reference valid task IDs and contain no cycles.
- Work package IDs are unique and sequential (`WP1`, `WP2`, ...).
- Every task appears in exactly one work package.
- Every `work_packages[].task_ids[]` reference points to a valid task ID.
- Every `depends_on` and `parallel_safe_with` reference points to a valid work package ID.
- `parallel_safe_with` is symmetric across the package list.
- No package lists itself in `depends_on` or `parallel_safe_with`.
- Package dependencies do not contradict task dependencies: if any task in package `WPa` depends on a task in package `WPb`, then `WPa.depends_on` includes `WPb`. Dependencies between tasks inside the same package do not require package-level `depends_on`.
- One-task work packages include a non-empty `rationale` (semantic adequacy is reviewer-judged, not mechanically enforced).

If deterministic validation fails, report the failures as blockers and resolve them before spawning reviewers. Do not spend sub-agent tokens on a structurally invalid plan.

## Step 3: Load Model Preferences

Read `${CLAUDE_PLUGIN_ROOT}/references/model-preferences.md` for the canonical schema and resolution procedure.

Resolve model preferences for two possible reviewer roles:
- **Plan Quality Reviewer:** Uses the `review-plan` key. Hardcoded default: `adaptive`.
- **Adversarial Plan Challenger:** Uses the `skeptic-agent` key. Hardcoded default: `adaptive`. Only spawned when escalation triggers.

**Adaptive interpretation for review-plan:** The Plan Quality Reviewer uses Sonnet. The Adversarial Plan Challenger is governed by the `skeptic-agent` key — when `skeptic-agent` resolves to `adaptive`, use the strongest available model (Opus).

This is a role-name change only. The `review-plan` and `skeptic-agent` keys, fallback chain, and adaptive resolution semantics defined in `references/model-preferences.md` are unchanged.

Carry the resolved models forward into Step 6.

## Step 4: Pre-Review Announcement (Gate 1)

Before spawning reviewers, present the user with a plain-language summary of what the plan delivers. This is a **projection** from plan artifacts — do not synthesize or add content not backed by SPEC.md or tasks.json.

```markdown
## Plan Deliverables — <Feature Name>

### What Will Be Delivered
- <feature/functionality derived from tasks.json, one bullet per meaningful deliverable>

### Implementation Work Packages
- `<WP-ID>` — <package title>: <task IDs and short rationale>

### ⚠️ Flags
- <implicit consequences the user may not be aware of: new dependencies, breaking changes, migration needs, performance impacts>

### Out of Scope
- <from SPEC.md Out of Scope section>
```

**Rules:**
- Every bullet must trace to a specific plan element (task ID or SPEC.md section).
- **Blocking gate** — the user must explicitly approve before review proceeds.
- If the user rejects: ask what to change, apply edits to SPEC.md or tasks.json, and re-present Gate 1. Do not proceed to Step 5 until approved.
- Work package bullets must come from `work_packages` in tasks.json. If `work_packages` is missing, deterministic validation fails before this gate.

## Step 5: Decide Review Depth

Use adaptive review depth:

- **Standard review:** Spawn one Plan Quality Reviewer. This is the default.
- **Escalated review:** Spawn the Adversarial Plan Challenger in addition to, or after, the Plan Quality Reviewer when risk justifies the extra sub-agent.

Escalation triggers:
- The plan has more than 10 tasks, more than 4 work packages, or more than 3 phases.
- The feature touches security, authentication, authorization, payments, permissions, data migration, data deletion, privacy, or safety-sensitive behavior.
- The plan introduces new architecture, new external dependencies, cross-cutting changes, or broad refactors.
- Work-package boundaries are unclear, cross-cutting, or rely on many `parallel_safe_with` claims.
- The Plan Quality Reviewer reports `[BLOCKER]` or `[CRITICAL]` findings involving ambiguity, scope, unsafe package boundaries, or conflicting requirements.
- The user asks for strict/adversarial review.
- The main agent is uncertain whether one reviewer is enough.

When escalation is triggered before review, run both reviewers in parallel. When escalation is triggered by the Plan Quality Reviewer findings, run the Adversarial Plan Challenger after those findings are collected.

## Step 6: Spawn Review Sub-Agent(s)

Launch the Plan Quality Reviewer for every valid plan. Launch the Adversarial Plan Challenger only when review-depth escalation triggers.

Do not execute semantic plan review as the main agent. The main agent performs deterministic validation and orchestration only.

Every spawned reviewer must validate work packages as well as tasks:
- Every task appears in exactly one work package.
- Package boundaries are coherent and substantial.
- One-task packages are justified.
- Package dependencies are consistent with task dependencies: if any task in package `WPa` depends on a task in package `WPb`, then `WPa.depends_on` includes `WPb`. Dependencies between tasks inside the same package do not require package-level `depends_on`.
- `parallel_safe_with` claims are conservative and plausible.
- `primary_paths` help future sub-agents start with focused code exploration when relevant paths are known.

### Reviewer Output Format

Reviewers must return findings in this exact format — no preamble, no summary, no prose outside
the format:

```
[SEV] TARGET — TITLE
ISSUE: <1 sentence, what's wrong>
FIX: <1 sentence, concrete resolution>
COST: <complexity burden of the proposed fix — see Format Rules>
```

### Severity Taxonomy

Every finding must be classified:

| Severity | Label | Meaning |
|---|---|---|
| `[BLOCKER]` | Must resolve | Plan cannot proceed to implementation. |
| `[CRITICAL]` | Strongly recommended | Significant quality, completeness, or plan risk. |
| `[SUGGESTION]` | Non-blocking | Improvement opportunity. May omit the `FIX:` line. |

### TARGET Locator Grammar

Each finding must reference its plan element using one of these locator patterns:

| Pattern | Example | Use for |
|---|---|---|
| `SPEC:<section-slug>` | `SPEC:requirements` | Findings about SPEC.md sections |
| `TASK:<task-id>` | `TASK:P1-T003` | Findings about a specific task |
| `TASK:<task-id>.<field>` | `TASK:P2-T001.dependencies` | Findings about a specific task field |
| `PHASE:<phase-id>` | `PHASE:P1` | Findings about phase-level concerns |
| `PHASE:<phase-id>.<aspect>` | `PHASE:P1.coherence` | Findings about a specific phase aspect |
| `GLOBAL:<concern>` | `GLOBAL:scope` | Cross-cutting findings (scope, acceptance criteria patterns) |
| `WP:<work-package-id>` | `WP:WP1` | Findings about a specific work package |
| `WP:<work-package-id>.<field>` | `WP:WP1.parallel_safe_with` | Findings about a specific work package field |

Multi-target findings: use the primary target, note others in the ISSUE line.

### Format Rules

- All `[BLOCKER]` and `[CRITICAL]` findings reported — no count caps.
- `[SUGGESTION]` findings: report up to 10 in detail. If more exist, append: `+N more suggestions omitted`
- No introductory text, no concluding summaries.
- `[SUGGESTION]` may omit the `FIX:` line if no specific action is needed.
- `COST:` line is **required** for Adversarial Plan Challenger's `[BLOCKER]` and `[CRITICAL]` findings. Must be specific: "adds 2 tasks, new caching dependency, invalidation logic" — not "some complexity." The orchestrator uses `COST:` during merge-and-resolve to weigh proportionality. Optional for the Plan Quality Reviewer and for `[SUGGESTION]` findings.
- If no findings: respond with exactly `NONE`
- Do NOT append `NONE` after findings — `NONE` means zero findings only.

### Severity Resolution Rules

The orchestrator applies these rules during merge-and-resolve:

- **`[BLOCKER]`** — Must be resolved before the plan advances. All blockers require plan edits and re-verification.
- **`[CRITICAL]`** — Must be explicitly addressed via one of: (a) SPEC.md clarification when the finding concerns requirements, acceptance criteria, constraints, or scope and the clarification is supported by prior user input, (b) task plan edits accepting the alternative when every changed task traces to existing SPEC IDs, or (c) **dismissed as disproportionate** — the fix's complexity cost exceeds the risk it addresses. New product behavior, constraints, or scope require user approval and a SPEC.md update before tasks.json changes. Dismissal requires referencing the finding's `COST:` line and recording a one-line justification. Dismissed findings are logged (not silently dropped) and appear in Gate 2 summary with a `← dismissed (disproportionate)` marker. A dismissed CRITICAL does not trigger a re-review round — it is considered resolved.
- **`[SUGGESTION]`** — Logged for consideration. No resolution required.

Package-level blockers include missing `work_packages`, a task omitted from all packages, a task assigned to multiple packages, package dependencies that contradict task dependencies, or package boundaries that would cause unsafe parallel edits to the same files.

---

### Plan Quality Reviewer

Combines the current completeness checks with practical implementability review. It verifies that the plan is complete, task acceptance criteria are clear, work packages are coherent, and a cold implementation agent can execute the plan from files only.

---

### Adversarial Plan Challenger

Runs only when escalation triggers. It stress-tests assumptions, over/under-scoping, risky package boundaries, hidden dependencies, and disproportionate complexity.

---

## Step 7: Merge and Resolve

Collect structured findings from the spawned reviewer(s). Apply severity resolution rules:

1. **`[BLOCKER]` findings:** Resolve by updating SPEC.md or tasks.json. All blockers must be resolved before advancing.
2. **`[CRITICAL]` findings:** Address each via one of three paths: (a) clarify SPEC.md when the finding concerns requirements, acceptance criteria, constraints, or scope and the clarification is supported by prior user input, (b) accept the alternative and revise tasks.json only when every changed task traces to existing SPEC requirement or acceptance IDs, or (c) dismiss as disproportionate — reference the finding's `COST:` line, explain why the cost exceeds the risk, and log the dismissal. Each critical must be explicitly addressed.

When editing SPEC.md, preserve the requirement source rule: do not add requirements, constraints, or exclusions unless they were stated or explicitly approved by the user. If a finding or task edit requires a new product decision, behavior, constraint, or scope, ask the user before editing the spec or tasks.json.

3. **`[SUGGESTION]` findings:** Log for consideration. No resolution required.

## Step 8: Re-Review if Changes Were Made

Re-review only at the depth required by the changes:

1. If only deterministic/schema issues changed, rerun deterministic validation only.
2. If task content, acceptance criteria, requirements traceability, or work-package boundaries changed, rerun the Plan Quality Reviewer.
3. If adversarial review was previously triggered, rerun the Adversarial Plan Challenger only when the changed area affects its findings or the plan still meets escalation triggers.
4. Maximum 3 semantic re-review rounds. If issues remain unresolved after 3 iterations, present the remaining issues to the user and ask for manual resolution.

## Step 9: Post-Review Announcement (Gate 2)

When the required review depth approves, present the user with the **final** plain-language summary of what the plan delivers. This reflects the state after all review rounds — including any changes made during merge-and-resolve.

Use the same template as Gate 1 (Step 4), with one addition: tag items that were added or modified during review:

```markdown
### What Will Be Delivered
- JWT auth middleware on all /api/* routes
- Rate limiting (200 req/15min/IP) ← modified by review
- Error recovery for token refresh failures ← added by review
- Distributed cache layer ← dismissed (disproportionate)
- CORS configuration for new namespace
```

**Rules:**
- Every `← added by review` or `← modified by review` marker must map to a specific review finding that caused the change.
- **Blocking gate** — the user must explicitly approve before finalization.
- If the user rejects: ask what to change, apply edits to SPEC.md or tasks.json, and **re-review from Step 6** (mandatory — plan changes after review require re-verification). Gate 2 is re-presented after the new review completes.
- **No plan edits are permitted between Gate 2 approval and Step 10 finalization.**

## Step 10: Finalize

When the user approves the post-review announcement:

1. Update the feature `status` in tasks.json from `planned` to `reviewed`.
2. Report to the user:
   - Summary of issues found and how they were resolved
   - Requirements, acceptance criteria, or scope boundaries that were clarified
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
