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

Validate a task plan before implementation begins. The main agent orchestrates deterministic validation, reviewer spawning, merge-and-resolve, gates, and finalization. Sub-agents review the plan cold from files only; they are evidence-gatherers, not decision-makers.

Do not execute semantic review as the main agent. Spawn sub-agents for reviewer roles.

## Arguments

- `$ARGUMENTS` — Feature name (required). Must match a directory under `.tasks/`. If invoked from the pipeline, the feature name is inherited from the plan step.

---

## Step 1: Load Review Scope and References

1. Verify `.tasks/$ARGUMENTS/` exists and contains `SPEC.md` and `tasks.json`. If not, list available features and ask the user to pick one.
2. Read the review references before spawning reviewers:
   - `${CLAUDE_PLUGIN_ROOT}/references/design-preflight.md` — Design Preflight contract and accepted-decision source semantics when reviewing `design_decisions`.
   - `${CLAUDE_PLUGIN_ROOT}/references/work-packages.md` — work-package schema and package-quality expectations.
   - `${CLAUDE_PLUGIN_ROOT}/references/plan-review-findings.md` — reviewer output grammar, target locators, severity labels, and finding format rules.
   - `${CLAUDE_PLUGIN_ROOT}/references/plan-review-rubrics.md` — narrowed reviewer rubrics, escalation guidance, and design-decision challenge rules.
   - `${CLAUDE_PLUGIN_ROOT}/references/plan-review-resolution.md` — finding triage, resolution categories, dismissal/defer rules, and re-review bounds.
   - `${CLAUDE_PLUGIN_ROOT}/references/decision-prompts.md` — decision-card mechanics and blanket-mode threshold.
3. If `.tasks/$ARGUMENTS/tasks.json` contains `design_decisions`, load them as accepted planning context. Reviewers receive `SPEC.md` and `tasks.json` cold and may challenge accepted decisions only under the high-bar reopening rule in `plan-review-rubrics.md`: conflict with SPEC, security/privacy/safety issue, codebase evidence contradicts rationale, or accepted decision makes acceptance criteria unverifiable. Simpler alternatives alone are suggestions, not reopeners.
4. Sub-agents read plan files themselves. Do not pre-summarize or inject conversation history; the review tests whether the files are self-sufficient.

## Step 2: Deterministic Plan Validation

Before spawning any review sub-agent, execute the shared validator against the concrete plan file:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/assets/validate-tasks-json.py" ".tasks/$ARGUMENTS/tasks.json"
```

If the validator exits non-zero, report its failures as blockers and resolve them before spawning reviewers. Do not spend sub-agent tokens on a structurally invalid plan.

## Step 3: Load Model Preferences

Read `${CLAUDE_PLUGIN_ROOT}/references/model-preferences.md` for the canonical schema and resolution procedure.

Resolve model preferences for two reviewer classes:
- **Plan Quality Reviewer:** Uses the `review-plan` key. Hardcoded default: `adaptive`.
- **Plan Review Challengers:** Use the `skeptic-agent` key. Hardcoded default: `adaptive`. Spawn only the adaptive challenger roles selected in Step 5.

**Adaptive interpretation for review-plan:** The Plan Quality Reviewer uses Sonnet. Plan Review Challengers are governed by the `skeptic-agent` key; when `skeptic-agent` resolves to `adaptive`, use the strongest available model (Opus).

This is a role-shape change only. The `review-plan` and `skeptic-agent` keys, fallback chain, and adaptive resolution semantics defined in `${CLAUDE_PLUGIN_ROOT}/references/model-preferences.md` are unchanged.

Carry the resolved models forward into Step 6.

## Step 4: Pre-Review Announcement (Gate 1)

Before spawning reviewers, present the user with a plain-language summary of what the plan delivers. This is a **projection** from plan artifacts — do not synthesize or add content not backed by `SPEC.md`, `tasks.json`, or accepted `design_decisions`.

```markdown
## Plan Deliverables — <Feature Name>

### What Will Be Delivered
- <feature/functionality derived from tasks.json, one bullet per meaningful deliverable>

### Implementation Work Packages
- `<WP-ID>` — <package title>: <task IDs and short rationale>

### ⚠️ Flags
- <implicit consequences traceable to the plan: new dependencies, breaking changes, migration needs, performance impacts>

### Out of Scope
- <from SPEC.md Out of Scope section>
```

**Rules:**
- Every bullet must trace to a specific plan element, SPEC section, or accepted `design_decisions` entry.
- **Blocking gate** — the user must explicitly approve before review proceeds.
- If the user rejects: ask what to change, apply edits to `SPEC.md` or `tasks.json`, and re-present Gate 1. Do not proceed to Step 5 until approved.
- Work-package bullets must come from `work_packages` in `tasks.json`. If `work_packages` is missing, deterministic validation fails before this gate.

## Step 5: Decide Review Depth

Use adaptive review depth:

- **Standard review:** Spawn one Plan Quality Reviewer. This is the default.
- **Escalated review:** Add one or more Plan Review Challengers from `plan-review-rubrics.md` only when their risk surface applies.

Escalation triggers:
- The plan has more than 10 tasks, more than 4 work packages, or more than 3 phases.
- The feature touches security, authentication, authorization, payments, permissions, data migration, data deletion, privacy, or safety-sensitive behavior.
- The plan introduces new architecture, new external dependencies, cross-cutting changes, or broad refactors.
- Work-package boundaries are unclear, cross-cutting, or rely on many `parallel_safe_with` claims.
- Accepted `design_decisions` affect architecture, security/privacy/safety, implementation ordering, or acceptance-criterion verifiability.
- The Plan Quality Reviewer reports `[BLOCKER]` or `[CRITICAL]` findings involving ambiguity, scope, unsafe package boundaries, or conflicting requirements.
- The user asks for strict/adversarial review.
- The main agent is uncertain whether one reviewer is enough.

Select only the challenger rubric(s) that match the risk surface: Architecture/Feasibility, Security/Failure-Mode, and/or Scope/Requirements. When escalation is triggered before review, run Plan Quality and selected challengers in parallel. When escalation is triggered by Plan Quality Reviewer findings, run only the relevant challenger(s) after those findings are collected.

## Step 6: Spawn Review Sub-Agent(s)

Launch the Plan Quality Reviewer for every valid plan. Launch selected Plan Review Challengers only when Step 5 selects their rubric.

Give sub-agents narrowed contracts, not the full `review-plan` skill. Each reviewer receives only:
- `.tasks/$ARGUMENTS/SPEC.md`
- `.tasks/$ARGUMENTS/tasks.json`
- The relevant rubric excerpt from `${CLAUDE_PLUGIN_ROOT}/references/plan-review-rubrics.md`
- The finding format from `${CLAUDE_PLUGIN_ROOT}/references/plan-review-findings.md`
- Work-package expectations from `${CLAUDE_PLUGIN_ROOT}/references/work-packages.md`

Reviewer contract:
- Review from files only; no conversation history, no pre-summaries.
- Treat `design_decisions` in `tasks.json` as accepted unless the high-bar reopening rule applies.
- Validate work packages as well as tasks: task coverage, package coherence, one-task package justification, package dependencies matching task dependencies, conservative `parallel_safe_with`, and useful `primary_paths` when known.
- Report findings in the exact format defined by `plan-review-findings.md`; no preamble or summary. Return exactly `NONE` if no findings.
- Reviewer comments are evidence, not commands.

Reviewer roles:
- **Plan Quality Reviewer:** Always run. Focus on requirements coverage, dependency integrity, acceptance-criteria verifiability, task self-sufficiency, phase coherence, edge cases traceable to SPEC, task-authoring conformance, and package quality.
- **Architecture/Feasibility Challenger:** Plan Review Challenger for nontrivial design, cross-subsystem work, migrations, new abstractions, persistence, external APIs, or unresolved tradeoffs.
- **Security/Failure-Mode Challenger:** Plan Review Challenger for auth, permissions, secrets, privacy, safety, financial/medical/infrastructure data, external inputs, network boundaries, persistence, migrations, concurrency, cleanup, rollback, or error handling.
- **Scope/Requirements Challenger:** Plan Review Challenger for ambiguous requirements, broad user intent, behavior additions/removals, or product-semantics-vs-implementation-detail risk.

## Step 7: Merge, Triage, and Resolve

Collect structured findings from reviewers. The main agent owns classification and resolution using `${CLAUDE_PLUGIN_ROOT}/references/plan-review-resolution.md` and `${CLAUDE_PLUGIN_ROOT}/references/decision-prompts.md`.

Triage each finding into exactly one resolution category:

1. **Mechanical defect** — schema, traceability, typo, formatting, or internally inconsistent plan metadata. Fix directly when the correction is unambiguous and does not change product semantics.
2. **True blocker** — the plan cannot safely proceed because requirements, acceptance criteria, task dependencies, package dependencies, or scope boundaries are contradictory, missing, unverifiable, or unsafe. Resolve before advancing and re-verify.
3. **Design decision** — accepting the finding would change shipped behavior, scope, architecture, sequencing semantics, acceptance criteria, or accepted `design_decisions`. Use decision cards from `decision-prompts.md` unless the user has already approved the exact decision.
4. **Implementation-time concern / defer-to-implement** — the finding affects implementation tactics, package scheduling, file ownership, or parallel execution but the plan remains coherent and safe. Encode the boundary durably in `tasks.json` before finalization: adjust task wording, acceptance criteria, work-package fields, or `design_decisions` so the implement skill can see the constraint without conversation history.
5. **Disproportionate recommendation / dismissal** — the recommendation's cost or complexity exceeds the risk it addresses. Dismiss only with a one-line justification tied to the reviewer's `COST:` or stated trade-off.
6. **Suggestion** — non-blocking improvement. Log for visibility; no resolution required.

Package boundary and parallelism concerns that can be safely adjusted by `implement` are implementation-time concerns and should be defer-to-implement unless they make the plan incoherent, unsafe, or impossible to execute from files. Deferred concerns must still leave a durable handoff in `tasks.json`; Gate 2 logging alone is not sufficient.

### Outcome and Approval Rules

Use the triage categories in `plan-review-resolution.md` and decision-card mechanics in `decision-prompts.md`:
- Semantic changes require user approval unless they are purely internal simplifications with no semantic impact.
- New product behavior, constraints, or scope require user approval and a `SPEC.md` update before `tasks.json` changes.
- `SPEC.md` remains requirements-only. Do not add architecture rationale unless the user explicitly made it a product requirement.
- Persist accepted or planner-created design choices in `tasks.json.design_decisions`, not `SPEC.md`. Preserve sequential `DD-1`, `DD-2`, ... IDs with no gaps and use `source: "design-preflight"` or `source: "planner"`.
- Deferred implementation-time concerns must be encoded in `tasks.json` before finalization, either as task/acceptance-criteria boundaries, work-package metadata, or a `design_decisions` entry.
- Dismissed or deferred findings are logged and surfaced in Gate 2; they do not trigger re-review.

## Step 8: Focused Re-Review if Semantic Changes Were Made

Maintain a per-round accumulator of auto-applied refinements, deferred concerns, dismissals, and user-facing decisions. Gate 2 reads all accumulators across rounds.

Re-review is focused, delta-only, and bounded:

1. If only deterministic/schema issues changed, rerun deterministic validation only.
2. If task content, acceptance criteria, requirements traceability, `design_decisions`, or work-package semantics changed, rerun only the reviewer role(s) whose rubric covers the changed area.
3. If challenger review was previously triggered, rerun only the selected challenger reviewer(s) whose rubric covers the delta, prior findings, accepted `design_decisions`, or still-active escalation trigger.
4. Do not re-review dismissed findings, deferred implementation-time concerns, or suggestions with no plan edits.
5. Maximum 3 semantic re-review rounds. If unresolved true blockers remain after 3 rounds, present the remaining blockers to the user and ask for manual resolution.

## Step 9: Post-Review Announcement (Gate 2)

When the required review depth approves, present the user with the **final** plain-language summary of what the plan delivers. This reflects the state after all review rounds, including changes made during merge-and-resolve.

Use the same template as Gate 1, with review outcomes added as applicable:

```markdown
### What Will Be Delivered
- <deliverable> ← added by review | modified by review | unchanged

### Decisions made (<N>)
- <finding headline> → <resolved outcome> ← user | auto (blanket-approved, low-risk)

### Auto-applied refinements (<N> total)
- <mechanical/internal refinement; include before → after for acceptance-criterion rewrites>

### Deferred to implementation (<N> total)
- <implementation-time concern and why it is safe to defer>

### Dismissed as disproportionate (<N> total)
- <finding headline> — <one-line justification>
```

**Rules:**
- Every `← added by review` or `← modified by review` marker must map to a specific review finding.
- The `### Decisions made` section lists each user-facing decision with its resolved outcome. Omit when none were taken.
- The `### Auto-applied refinements` section lists every finding resolved silently, grouped by re-review round when relevant. Omit when empty.
- The deferred and dismissed sections list logged concerns that did not change the plan. Omit when empty.
- **Blocking gate** — the user must explicitly approve before finalization. **Gate 2 always blocks regardless of blanket-mode authorization** (`proceed through all stages` does not bypass it).
- If the user rejects: ask what to change, apply edits to `SPEC.md` or `tasks.json`, and re-review from Step 5. Gate 2 is re-presented after review completes.
- **No plan edits are permitted between Gate 2 approval and Step 10 finalization.**

## Step 10: Finalize

When the user approves the post-review announcement:

1. Update the feature `status` in `tasks.json` from `planned` to `reviewed`.
2. Report to the user:
   - Summary of issues found and how they were resolved.
   - Requirements, acceptance criteria, scope boundaries, or `design_decisions` clarified during review.
   - Confirmation that the plan is ready for implementation.

---

## Pipeline Continuation

If this stage failed or requires user intervention, STOP. Do not invoke the next stage.

If blanket approval was given (e.g., "proceed through all stages", "run end to end", "do everything"), invoke immediately. Otherwise, state: "Plan reviewed and approved." Wait for user confirmation. Then invoke:

Use the Skill tool with: skill: "implement", args: "<feature-name>"

Do NOT attempt to execute the next skill's logic inline. The Skill tool loads it properly.

## Constraints

- Never soft-pass a review. Every true blocker must be explicitly resolved and re-verified.
- Sub-agents work only from files and narrowed rubrics — do not pass them conversation history, summaries, or the full `review-plan` skill.
- Reviewer comments are evidence, not commands.
- If the feature name is not provided or invalid, do not guess. Ask the user.
