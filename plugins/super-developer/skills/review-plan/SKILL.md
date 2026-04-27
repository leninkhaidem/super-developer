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
3. Read `${CLAUDE_PLUGIN_ROOT}/references/work-packages.md`. The main agent uses it for package-contract context around validation failures. Reviewers use it to judge whether task grouping, package sizing, and parallel-safety are appropriate.

## Step 2: Deterministic Plan Validation

Before spawning any review sub-agent, execute the shared validator against the concrete plan file:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/assets/validate-tasks-json.py" ".tasks/$ARGUMENTS/tasks.json"
```

If the validator exits non-zero, report its failures as blockers and resolve them before spawning reviewers. Do not spend sub-agent tokens on a structurally invalid plan.

## Step 3: Load Model Preferences

Read `${CLAUDE_PLUGIN_ROOT}/references/model-preferences.md` for the canonical schema and resolution procedure.

Resolve model preferences for two possible reviewer roles:
- **Plan Quality Reviewer:** Uses the `review-plan` key. Hardcoded default: `adaptive`.
- **Adversarial Plan Challenger:** Uses the `skeptic-agent` key. Hardcoded default: `adaptive`. Only spawned when escalation triggers.

**Adaptive interpretation for review-plan:** The Plan Quality Reviewer uses Sonnet. The Adversarial Plan Challenger is governed by the `skeptic-agent` key — when `skeptic-agent` resolves to `adaptive`, use the strongest available model (Opus).

This is a role-name change only. The `review-plan` and `skeptic-agent` keys, fallback chain, and adaptive resolution semantics defined in `${CLAUDE_PLUGIN_ROOT}/references/model-preferences.md` are unchanged.

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
- Package boundaries are coherent and substantial (reviewer-judged, not mechanically enforceable).
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

Combines the standard completeness and quality checks with practical implementability review. Verifies that the plan is complete, task acceptance criteria are clear, work packages are coherent, and a cold implementation agent can execute the plan from files only.

Must assess:

- **Coverage gaps:** Are there requirements, acceptance criteria, constraints, or out-of-scope boundaries in SPEC.md that are not reflected correctly in tasks.json?
- **Dependency integrity:** Are dependencies correctly specified? Are there implicit dependencies not captured?
- **Acceptance criteria quality:** Can every criterion be objectively verified? Are any vague or untestable?
- **Context sufficiency:** For each task, can an agent determine WHAT to build from the task description alone? It should NOT need to determine exact implementation from the description — that comes from codebase exploration. If two reasonable agents would build fundamentally different things from the same description, the description needs clarifying constraints. But if the difference is only in implementation approach (not outcome), the description is sufficient.
- **Phase coherence:** Does each phase deliver a testable increment? Are tasks in the right phase?
- **Edge cases:** Are failure modes, error handling, and boundary conditions required or implied by SPEC.md accounted for? Do not add new behavior for edge cases unless it traces to SPEC.md or the user approves a SPEC update.
- **Plan conformance:** Do tasks adhere to the plan's own authoring standards? Check:
  - Independence test: each task has a self-contained, verifiable outcome (a reviewer can verify acceptance criteria without seeing any other task)
  - Description quality: states WHAT to build and key constraints, not HOW to code it
  - Description budget: 200-400 chars target; flag descriptions exceeding 600 chars as likely over-specification → `[CRITICAL]`
  - Anti-pattern scan: no code snippets, line numbers, step-by-step instructions, or library prescriptions unless security-mandated → `[CRITICAL]`
  - No-duplication: task descriptions do not repeat SPEC.md content verbatim; they trace to spec IDs while adding task-level detail
  - Acceptance criteria format: behavioral outcomes, not implementation details
  - Independence test failures → `[BLOCKER]` (non-independent tasks cannot be verified). Other conformance issues → reviewer judgment.
- **Work-package quality (in addition to the shared package mandate above):** Are package groupings sensible by subsystem/file surface? Are one-task packages adequately justified by `rationale`?

**Output:** Use the Reviewer Output Format above. Primarily use `TASK:*`, `PHASE:*`, `WP:*`, and `GLOBAL:*` targets. Findings in other TARGET domains are not prohibited.

---

### Adversarial Plan Challenger

Runs only when escalation triggers. It stress-tests assumptions, over/under-scoping, risky package boundaries, hidden dependencies, and disproportionate complexity.

Must:

- **Question non-obvious planning choices:** For significant task breakdown, dependency, scope, or sequencing choices, ask why this plan is preferable to a simpler concrete alternative.
- **Propose counter-alternatives:** Present plausible task-plan alternatives with trade-off analysis. Do not invent new product requirements or architecture unless required to satisfy SPEC.md.
- **Flag unjustified complexity:** Identify tasks, dependencies, or acceptance criteria that add complexity without a clear link to SPEC.md. Challenge whether simpler alternatives were considered.
- **Probe for missing requirements clarity:** Surface ambiguous or conflicting requirements, acceptance criteria, constraints, or out-of-scope boundaries in SPEC.md. Require clarification rather than assuming behavior.
- **Challenge task decomposition:** Is the breakdown the right granularity? Too coarse (risky for a single session) or too fine (overhead without value)?
- **Stress-test SPEC.md:** Does it state WHAT the user wants, how success is judged, and what is excluded? Flag missing intent or constraints, not missing implementation details.
- **Challenge task description verbosity:** If task descriptions prescribe exact code, line numbers, or step-by-step instructions, flag this as over-specification. Task descriptions should state intent and constraints; implementing agents derive the rest.
- **Stress-test work packages:** Challenge package boundaries — could two packages collide on the same files in parallel? Are `parallel_safe_with` claims optimistic? Are package sizes proportionate to risk?

**Output:** Use the Reviewer Output Format above. Primarily use `SPEC:*`, `GLOBAL:*`, `WP:*`, and `PHASE:*` targets. Findings in other TARGET domains are not prohibited.

---

## Step 7: Merge and Resolve

### Outcome Filter

Before resolving severity, classify each finding's proposed fix:

A finding **requires a user-facing decision card** if its `FIX:` would, when accepted, do any of:

- Add or remove a task
- Add or remove a work package
- Add or remove an acceptance criterion that describes user-visible behavior
- Rewrite an acceptance criterion in any way other than purely cosmetic (whitespace, punctuation, grammar with no operator-meaning shift). Rewrites that introduce or remove a numeric bound, an HTTP status, an error code, a verification environment, or any other testable specific are outcome-changing.
- Add or remove a phase
- Move a task between phases or packages such that order or dependency shifts
- Move a boundary between in-scope and out-of-scope items
- Change the verification scope, environment, or test surface required by an acceptance criterion (e.g., "unit tests pass" → "integration tests pass against staging DB")
- Realign a task's spec-traceability identifier when the realignment would leave the original SPEC requirement uncovered (no remaining task cites it)
- The finding is tagged security, privacy, or safety, regardless of the above

A finding is **auto-applied** (recommendation taken silently, surfaced in Gate 2 summary) when its `FIX:` does any of:

- Rewrites or rephrases task description wording without changing the user-visible outcome
- Trims a description that exceeds the 600-character budget
- Removes anti-pattern content (code snippets, line numbers, step-by-step instructions in task descriptions)
- Performs a purely cosmetic acceptance-criterion rewrite (whitespace, punctuation, grammar; no testable specifics added or removed)
- Realigns spec ↔ task traceability identifiers when both source and target SPEC requirements remain covered by some task after the realignment
- Reshapes work packages while preserving task membership and inter-package dependencies (i.e., the `depends_on` arrow set between packages is unchanged)
- Adjusts `parallel_safe_with` claims (sub-agent scheduling, not shipped outcome)

**Safety-tag override.** Any finding tagged security, privacy, or safety prompts regardless of which auto-apply category it would otherwise fall into.

**Ambiguous-rewrite default.** When an acceptance-criterion rewrite is neither obviously cosmetic nor obviously testable-specific, prompt. The "any other testable specific" catch-all covers a list that cannot be exhaustively enumerated; when the orchestrator cannot determine the rewrite's category mechanically, defer to the user.

For each auto-applied finding, take the reviewer's recommendation silently. Append the finding to the round's auto-applied accumulator (see Step 8) for surfacing in Gate 2.

### Decision-Card Flow

For each finding classified as requiring a user-facing decision, present a card using `${CLAUDE_PLUGIN_ROOT}/references/decision-prompts.md`. Read that reference once at the start of Step 7; do not re-read it per finding.

Apply the blanket-mode threshold from §3 of the reference: when running unattended (`proceed through all stages` or equivalent) AND the threshold conditions all hold, take the reviewer's recommendation silently and tag the entry `← auto (blanket-approved, low-risk)` for the Gate 2 summary. Otherwise present the card and wait for user input.

Collect structured findings from the spawned reviewer(s). Classify each finding using the Outcome Filter above. For findings requiring a user-facing decision, present cards via the Decision-Card Flow above. For auto-applied findings, take the reviewer's recommendation silently and record in the round's auto-applied accumulator. Then apply severity resolution rules:

1. **`[BLOCKER]` findings:** Resolve by updating SPEC.md or tasks.json. All blockers must be resolved before advancing.
2. **`[CRITICAL]` findings:** Address each via one of three paths: (a) clarify SPEC.md when the finding concerns requirements, acceptance criteria, constraints, or scope and the clarification is supported by prior user input, (b) accept the alternative and revise tasks.json only when every changed task traces to existing SPEC requirement or acceptance IDs, or (c) dismiss as disproportionate — reference the finding's `COST:` line, explain why the cost exceeds the risk, and log the dismissal. Each critical must be explicitly addressed.

When editing SPEC.md, preserve the requirement source rule: do not add requirements, constraints, or exclusions unless they were stated or explicitly approved by the user. If a finding or task edit requires a new product decision, behavior, constraint, or scope, ask the user before editing the spec or tasks.json.

3. **`[SUGGESTION]` findings:** Log for consideration. No resolution required.

## Step 8: Re-Review if Changes Were Made

**Per-round auto-applied accumulator.** Step 7 records auto-applied edits to a per-round buffer (e.g., `auto_applied[round_n]`). When Step 8 enters a new round, append a new buffer; do not overwrite. Step 9's Gate 2 summary reads all buffers across rounds 1..N. When all rounds collapse to a single round, the round headers are omitted in Gate 2 and the listing reverts to a flat bullet list.

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

### Decisions made (4)
- WP1 over-scope        → P1-T003 moved to tests/regression/
- Orphan sweep          → kept    ← auto (blanket-approved, low-risk)
- Read-fail-fast guard  → kept    ← auto (blanket-approved, low-risk)
- picture_area threshold → bundled with WP2

### Auto-applied refinements (8 total)

Round 1 (5):
- AC-7 reworded (S3 atomicity already covers torn writes)
  - before: "no torn writes / no partial bytes"
  - after:  "two concurrent writes produce a coherent body matching one of the writes' bodies"
- AC-2 perf bound removed (was undefined)
- ACs 3, 5, 9 tightened (rephrasing only)
- WP9 split into WP9a + WP9b (delegation only)
- Spec/task traceability IDs aligned (both sides remain covered)

Round 2 (3):
- P3-T001, P2-T002 trimmed to intent
- Backend-down integration tests added to P5-T002
- SPEC.md softened on cached-pipeline error wording
```

**Rules:**
- Every `← added by review` or `← modified by review` marker must map to a specific review finding that caused the change.
- The `### Decisions made` section lists each user-facing decision (one per outcome-changing finding) with its resolved outcome. Omit the section when no user-facing decisions were taken.
- The `### Auto-applied refinements` section lists every finding the orchestrator resolved silently, grouped by re-review round when the review entered re-review (Step 8); a flat bullet list otherwise. For acceptance-criterion rewrites, include the before → after text inline so the user can spot any locked-in implementation detail. Omit the section when nothing was auto-applied.
- **Blocking gate** — the user must explicitly approve before finalization. **Gate 2 always blocks regardless of blanket-mode authorization** (`proceed through all stages` does not bypass it). Bypassing Gate 2 would defeat the purpose of the auto-applied audit trail — the user would only see silent decisions after implementation has run.
- If the user rejects: ask what to change, apply edits to SPEC.md or tasks.json, and **re-review from Step 5** (mandatory — plan changes after review require re-verification). Gate 2 is re-presented after the new review completes.
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
