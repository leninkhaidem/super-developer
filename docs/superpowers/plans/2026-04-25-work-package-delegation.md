# Work Package Delegation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Change Super Developer implementation from task-sized delegation to right-sized work-package delegation so each sub-agent receives a substantial coherent bundle and each integrated batch is lightly verified before downstream work starts.

**Architecture:** Add a shared `references/work-packages.md` contract, extend `tasks.json` with top-level `work_packages`, and update planning, adaptive plan review, implementation, status display, and README text to use work packages as the delegation unit. Tasks remain the source of truth for tracking and acceptance criteria; work packages become the source of truth for delegation shape. Plan review uses deterministic validation first, one combined reviewer by default, and adversarial escalation only when risk justifies the extra sub-agent.

**Tech Stack:** Markdown-based Claude/Pi skill files, JSON schema examples embedded in Markdown, git worktrees, shell verification with `rg` and `git diff`.

---

## Design Decisions

1. **Keep `tasks.json`; do not add a third generated plan document.** `SPEC.md` remains the requirements document. `tasks.json` remains the machine-readable execution state.
2. **Add `work_packages` to `tasks.json`.** Each task must belong to exactly one work package in newly generated plans.
3. **Tasks remain individually trackable.** Status, `completed_at`, `blocked_reason`, acceptance criteria, and audit remain task-based.
4. **Work packages are the delegation unit.** Implementation should dispatch package-sized assignments, not one sub-agent per small task.
5. **A work package may contain internally dependent tasks.** A sub-agent can complete those tasks sequentially in one branch/worktree, committing after each task ID.
6. **Implementation can adjust planned packages.** Runtime changes are allowed when file impact, current status, or merge state makes the planned package unsafe or inefficient.
7. **Verify integrated batches before proceeding.** After merging package branches into the feature branch, the main agent performs a lightweight integration checkpoint before marking tasks done and delegating newly unlocked work.
8. **Use adaptive plan-review depth.** The main agent performs deterministic plan validation first, runs one combined Plan Quality Reviewer by default, and adds the Adversarial Plan Challenger only for high-risk, ambiguous, large, or user-requested strict reviews.

## Proposed `tasks.json` Shape

Add a top-level `work_packages` array near the feature metadata:

```json
{
  "feature": "auth-system",
  "title": "Auth System",
  "description": "One-line summary of what this feature delivers",
  "created_at": "2026-04-25T00:00:00.000Z",
  "status": "planned",
  "work_packages": [
    {
      "id": "WP1",
      "title": "Authentication backend flow",
      "description": "Implement the backend authentication behavior across middleware, token validation, and protected route handling.",
      "task_ids": ["P1-T001", "P1-T002", "P1-T003"],
      "depends_on": [],
      "parallel_safe_with": ["WP2"],
      "primary_paths": ["src/auth/", "src/middleware/", "tests/auth/"],
      "verification_commands": ["npm test -- auth"],
      "rationale": "These tasks touch the same auth backend surface and should share one codebase exploration pass."
    }
  ],
  "phases": []
}
```

Field rules:

- `id`: `WP<N>` with sequential numbering and no gaps.
- `title`: short human-readable package name.
- `description`: what the package delivers as a coherent implementation unit.
- `task_ids`: task IDs included in this package. Every task in `phases[].tasks[]` must appear exactly once across all work packages.
- `depends_on`: work-package IDs that must be integrated before this package starts. This captures external package dependencies; internal task dependencies can remain inside the same package.
- `parallel_safe_with`: work-package IDs believed safe to run in the same batch. Empty array when unsure.
- `primary_paths`: likely files or directories to inspect first. These are starting points, not exclusive boundaries.
- `verification_commands`: package-specific checks when known. Use an empty array when no safe command is known; do not invent commands.
- `rationale`: why these tasks should share one sub-agent context.

---

## File Map

- Create: `plugins/super-developer/references/work-packages.md`
  - Defines the shared work-package rules for planning, review, and implementation.
- Modify: `plugins/super-developer/skills/implementation-plan/SKILL.md`
  - Adds `work_packages` to the generated `tasks.json` schema and task authoring flow.
- Modify: `plugins/super-developer/skills/review-plan/SKILL.md`
  - Adds deterministic plan validation, adaptive review depth, and work-package review rules.
- Modify: `plugins/super-developer/skills/implement/SKILL.md`
  - Changes dispatching from task-first to package-first and adds a lightweight integration checkpoint.
- Modify: `plugins/super-developer/skills/tasks/SKILL.md`
  - Displays work-package status when present while preserving task-level status controls.
- Modify: `plugins/super-developer/README.md`
  - Updates public docs from one-agent-per-task style language to right-sized package delegation.
- Modify: `plugins/super-developer/references/model-preferences.md`
  - Renames the review-plan reviewer roles from `Agent A`/`Agent B` to `Plan Quality Reviewer`/`Adversarial Plan Challenger`. No change to value resolution semantics.

No changes are required to `plugins/super-developer/skills/audit/SKILL.md` for this iteration because audit remains task/spec based and should tolerate extra top-level JSON fields.

---

### Task 1: Add the shared work-package reference

**Files:**
- Create: `plugins/super-developer/references/work-packages.md`

- [ ] **Step 1: Create the reference file**

Write `plugins/super-developer/references/work-packages.md` with these sections:

```markdown
# Work Packages

Work packages are the delegation unit for Super Developer implementation. Tasks remain the tracking and acceptance-criteria unit. A work package groups related tasks so one sub-agent can amortize its context-loading cost across a substantial coherent assignment.

## Core Principle

Delegate substantial coherent work packages, not individual small tasks. Use parallel sub-agents for multiple substantial packages that can proceed safely at the same time.

## Task vs Work Package

- **Task:** A self-contained, verifiable outcome with status, dependencies, and acceptance criteria.
- **Work package:** A coherent implementation bundle containing one or more tasks that should share a single codebase exploration pass and one package worktree.

Tasks answer: "What must be done and verified?"
Work packages answer: "How should implementation work be delegated?"

## Package Sizing

A good work package usually contains several related tasks or one task large enough to justify a dedicated sub-agent. Avoid one-task packages unless the task is substantial, risky, or naturally isolated.

Prefer packages that are:
- coherent by subsystem, module, directory, user flow, data model, API surface, or test surface
- large enough to justify sub-agent startup context
- small enough for one agent to reason about safely
- independently mergeable
- clear about which paths to inspect first

## Internal Dependencies

A work package may contain tasks that depend on each other. The sub-agent handles internal dependencies sequentially and commits after each task ID. A package is blocked only by dependencies outside the package that are not yet done or integrated.

## Parallel Safety

Mark packages as parallel-safe only when likely file ownership and subsystem boundaries do not overlap. When unsure, serialize or combine packages. The cost of serialization is latency; the cost of unsafe parallelism is merge conflicts and inconsistent design.

`parallel_safe_with` is a symmetric relation: if `WPx` lists `WPy`, then `WPy` must list `WPx`. A package never lists itself.

## Primary Paths

`primary_paths` are starting points for code exploration, not hard boundaries. Agents should inspect those paths first and broaden only when imports, tests, or acceptance criteria require it.

## Runtime Adjustment

The implementation orchestrator may merge, split, defer, or reorder planned packages when current task status, file impact, or previous merged work makes the plan unsafe or inefficient. It must briefly state the reason before dispatching.

## Anti-Patterns

- One work package per small task.
- Maximizing sub-agent count just because tasks are independent.
- Splitting tasks that touch the same files or subsystem.
- Bundling unrelated subsystems into a vague mega-package.
- Marking packages parallel-safe without checking likely file overlap.
- Giving a sub-agent a package with no primary paths when relevant paths are known.
```

- [ ] **Step 2: Verify the reference exists and contains the core terms**

Run:

```bash
rg -n "Work packages are the delegation unit|Internal Dependencies|Anti-Patterns" plugins/super-developer/references/work-packages.md
```

Expected: three matching lines from the new reference file.

- [ ] **Step 3: Commit Task 1**

```bash
git add plugins/super-developer/references/work-packages.md
git commit -m "docs: add work package delegation reference"
```

---

### Task 2: Update the planning skill to emit work packages

**Files:**
- Modify: `plugins/super-developer/skills/implementation-plan/SKILL.md`

- [ ] **Step 1: Add reference-loading instruction**

In `plugins/super-developer/skills/implementation-plan/SKILL.md`, add a step after feature-name validation and before directory creation:

```markdown
## Step 2: Load Work Package Rules

Read `${CLAUDE_PLUGIN_ROOT}/references/work-packages.md`. Use it when deciding task granularity, package grouping, package dependencies, and package parallel-safety.
```

Then increment the later step numbers by one. Keep the existing planning behavior otherwise.

- [ ] **Step 2: Extend the `tasks.json` schema example**

In the JSON schema example, add top-level `work_packages` before `phases`:

```json
  "work_packages": [
    {
      "id": "WP1",
      "title": "Short package title",
      "description": "Coherent implementation bundle delivered by one sub-agent.",
      "task_ids": ["P1-T001", "P1-T002"],
      "depends_on": [],
      "parallel_safe_with": [],
      "primary_paths": ["path/to/module/"],
      "verification_commands": [],
      "rationale": "Why these tasks should share one implementation context."
    }
  ],
```

- [ ] **Step 3: Add schema reference rows for work packages**

Add a Work Package section to the schema table with these rows:

```markdown
| Work Package | `id` | string | `WP<N>` (e.g., `WP1`) |
| Work Package | `task_ids` | string[] | Task IDs included in this package; every task appears exactly once across packages |
| Work Package | `depends_on` | string[] | Work package IDs that must be integrated first |
| Work Package | `parallel_safe_with` | string[] | Work package IDs safe to run in the same implementation batch |
| Work Package | `primary_paths` | string[] | Likely files/directories to inspect first; may be empty only when no safe paths are known |
| Work Package | `verification_commands` | string[] | Concrete commands for package-level checks; empty when unknown |
```

- [ ] **Step 4: Add package authoring guidelines**

After the existing task authoring guidelines, add:

```markdown
### Work Package Authoring Guidelines

- Create `work_packages` for every generated plan. Tasks remain the tracking unit; work packages are the delegation unit.
- Every task ID must appear in exactly one work package.
- Group tasks by subsystem, module, directory, API surface, UI flow, data model, or shared test surface.
- Prefer substantial coherent packages over one-task packages. A one-task package requires a clear rationale that the task is large, risky, or naturally isolated.
- A package may include tasks with internal dependencies when one sub-agent can complete them sequentially in the same worktree.
- Use `depends_on` only for dependencies on other work packages. Internal task dependencies do not require package-level dependencies.
- Fill `primary_paths` with likely files or directories to inspect first when known from Code References or task descriptions.
- Fill `verification_commands` only with commands known to exist or strongly implied by the project. Use `[]` rather than inventing commands.
- Use `parallel_safe_with` conservatively. When file impact is ambiguous, leave it empty and let implementation serialize or adjust.
```

- [ ] **Step 5: Extend validation rules**

Add these validation bullets to the validation step:

```markdown
- `work_packages` exists and contains every task exactly once
- Work package IDs are unique and sequential (`WP1`, `WP2`, ...)
- Every `work_packages[].task_ids[]` reference points to a valid task ID
- Every `depends_on` and `parallel_safe_with` reference points to a valid work package ID
- `parallel_safe_with` is symmetric: if `WPx.parallel_safe_with` includes `WPy`, then `WPy.parallel_safe_with` must include `WPx`
- A work package does not list itself in `depends_on` or `parallel_safe_with`
- Package dependencies do not contradict task dependencies
- One-task work packages include a rationale explaining why the task is substantial, risky, or isolated. This rationale is reviewer-judged, not mechanically enforced
- `parallel_safe_with` claims are conservative based on likely file/module impact
```

- [ ] **Step 6: Verify planning skill references work packages**

Run:

```bash
rg -n "work_packages|Work Package Authoring Guidelines|references/work-packages.md" plugins/super-developer/skills/implementation-plan/SKILL.md
```

Expected: matches for the reference-loading instruction, schema example, guidelines, and validation bullets.

- [ ] **Step 7: Commit Task 2**

```bash
git add plugins/super-developer/skills/implementation-plan/SKILL.md
git commit -m "feat: plan implementation work packages"
```

---

### Task 3: Update plan review for packages and adaptive review depth

**Files:**
- Modify: `plugins/super-developer/skills/review-plan/SKILL.md`

**Target step layout for `review-plan/SKILL.md` after this task completes:**

| # | Heading | Origin |
|---|---|---|
| 1 | Load Review Scope | existing (Step 1 today) |
| 2 | Deterministic Plan Validation | NEW (this task, sub-step 2) |
| 3 | Load Model Preferences | existing (was Step 2) |
| 4 | Pre-Review Announcement (Gate 1) | existing (was Step 3) |
| 5 | Decide Review Depth | NEW (this task, sub-step 4) |
| 6 | Spawn Review Sub-Agent(s) | renamed (was Step 4: "Spawn Review Sub-Agents in Parallel") |
| 7 | Merge and Resolve | existing (was Step 5) |
| 8 | Re-Review if Changes Were Made | existing (was Step 6) — content replaced in sub-step 10 |
| 9 | Post-Review Announcement (Gate 2) | existing (was Step 7) |
| 10 | Finalize | existing (was Step 8) |

When the sub-steps below say "increment later step numbers" or "add a step after X," renumber to match this final layout.

- [ ] **Step 1: Load work-package rules during review**

Add to the review scope setup:

```markdown
3. Read `${CLAUDE_PLUGIN_ROOT}/references/work-packages.md`. The main agent uses it for deterministic package validation. Reviewers use it to judge whether task grouping, package sizing, and parallel-safety are appropriate.
```

- [ ] **Step 2: Add deterministic validation before spawning reviewers**

Insert a new step after scope loading and before model preference resolution:

```markdown
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
```

Increment later step numbers as needed.

- [ ] **Step 3: Change model preferences to support adaptive review depth**

Replace the unconditional two-agent model setup with:

```markdown
Resolve model preferences for two possible reviewer roles:
- **Plan Quality Reviewer:** Uses the `review-plan` key. Hardcoded default: `adaptive`.
- **Adversarial Plan Challenger:** Uses the `skeptic-agent` key. Hardcoded default: `adaptive`. Only spawned when escalation triggers.

**Adaptive interpretation for review-plan:** The Plan Quality Reviewer uses Sonnet. The Adversarial Plan Challenger is governed by the `skeptic-agent` key — when `skeptic-agent` resolves to `adaptive`, use the strongest available model (Opus).

This is a role-name change only. The `review-plan` and `skeptic-agent` keys, fallback chain, and adaptive resolution semantics defined in `references/model-preferences.md` are unchanged.
```

- [ ] **Step 4: Add review-depth decision rules**

Add a step after Gate 1 approval and before reviewer spawning:

```markdown
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
```

- [ ] **Step 5: Include packages in the pre-review announcement**

In the Gate 1 template, add a section between deliverables and flags:

```markdown
### Implementation Work Packages
- `<WP-ID>` — <package title>: <task IDs and short rationale>
```

Add a rule below the template:

```markdown
- Work package bullets must come from `work_packages` in tasks.json. If `work_packages` is missing, deterministic validation fails before this gate.
```

- [ ] **Step 6: Replace unconditional two-reviewer spawning with adaptive spawning**

Locate the current Step 4 heading in `review-plan/SKILL.md`:

```markdown
## Step 4: Spawn Review Sub-Agents in Parallel
```

and the current opening line below it:

```markdown
Launch **two sub-agents in parallel** (models per Step 2), each reading `.tasks/$ARGUMENTS/SPEC.md` and `.tasks/$ARGUMENTS/tasks.json` from scratch:
```

Replace both with:

```markdown
## Step 6: Spawn Review Sub-Agent(s)

Launch the Plan Quality Reviewer for every valid plan. Launch the Adversarial Plan Challenger only when review-depth escalation triggers.

Do not execute semantic plan review as the main agent. The main agent performs deterministic validation and orchestration only.
```

Add this shared package-quality mandate before reviewer-specific instructions:

```markdown
Every spawned reviewer must validate work packages as well as tasks:
- Every task appears in exactly one work package.
- Package boundaries are coherent and substantial.
- One-task packages are justified.
- Package dependencies are consistent with task dependencies: if any task in package `WPa` depends on a task in package `WPb`, then `WPa.depends_on` includes `WPb`. Dependencies between tasks inside the same package do not require package-level `depends_on`.
- `parallel_safe_with` claims are conservative and plausible.
- `primary_paths` help future sub-agents start with focused code exploration when relevant paths are known.
```

Rename the current reviewer roles:

```markdown
### Plan Quality Reviewer

Combines the current completeness checks with practical implementability review. It verifies that the plan is complete, task acceptance criteria are clear, work packages are coherent, and a cold implementation agent can execute the plan from files only.

### Adversarial Plan Challenger

Runs only when escalation triggers. It stress-tests assumptions, over/under-scoping, risky package boundaries, hidden dependencies, and disproportionate complexity.
```

- [ ] **Step 7: Add target locator patterns for packages**

Add these rows to the target locator grammar table:

```markdown
| `WP:<work-package-id>` | `WP:WP1` | Findings about a specific work package |
| `WP:<work-package-id>.<field>` | `WP:WP1.parallel_safe_with` | Findings about a specific work package field |
```

- [ ] **Step 8: Update severity guidance**

Add package-specific blocker examples:

```markdown
Package-level blockers include missing `work_packages`, a task omitted from all packages, a task assigned to multiple packages, package dependencies that contradict task dependencies, or package boundaries that would cause unsafe parallel edits to the same files.
```

Keep the existing `COST:` requirement for Adversarial Plan Challenger `[BLOCKER]` and `[CRITICAL]` findings. Make `COST:` optional for the Plan Quality Reviewer.

- [ ] **Step 9: Replace remaining unconditional two-reviewer wording**

Replace leftover wording in Merge and Resolve, Re-Review, and Gate 2 that assumes both reviewers always ran:

- Replace `Collect structured findings from both agents` with `Collect structured findings from the spawned reviewer(s)`.
- Replace `Repeat until both agents approve` with `Repeat until the required review depth approves`.
- Replace `When both agents approve` with `When the required review depth approves`.
- Replace any other unconditional `both agents` wording with `spawned reviewer(s)` or `required review depth`, whichever is clearer in context.

- [ ] **Step 10: Make re-review adaptive**

Replace the unconditional instruction to spawn both agents again with:

```markdown
## Step 8: Re-Review if Changes Were Made

Re-review only at the depth required by the changes:

1. If only deterministic/schema issues changed, rerun deterministic validation only.
2. If task content, acceptance criteria, requirements traceability, or work-package boundaries changed, rerun the Plan Quality Reviewer.
3. If adversarial review was previously triggered, rerun the Adversarial Plan Challenger only when the changed area affects its findings or the plan still meets escalation triggers.
4. Maximum 3 semantic re-review rounds. If issues remain unresolved after 3 iterations, present the remaining issues to the user and ask for manual resolution.
```

- [ ] **Step 11: Verify review-plan references packages and adaptive review**

Run:

```bash
rg -n "Deterministic Plan Validation|Plan Quality Reviewer|Adversarial Plan Challenger|Escalation triggers|WP:<work-package-id>|Package-level blockers" plugins/super-developer/skills/review-plan/SKILL.md
```

Expected: matches for deterministic validation, adaptive reviewer roles, escalation rules, package locators, and package blocker guidance.

- [ ] **Step 12: Commit Task 3**

```bash
git add plugins/super-developer/skills/review-plan/SKILL.md
git commit -m "feat: use adaptive plan review depth"
```

---

### Task 4: Update implementation dispatch to use work packages

**Files:**
- Modify: `plugins/super-developer/skills/implement/SKILL.md`

- [ ] **Step 1: Change the opening description**

Replace language that frames sub-agents around individual complex tasks with package-based language:

```markdown
Execute tasks from a feature's task plan. The main agent acts as an orchestrator — analyzing planned work packages, validating dependency and file-impact boundaries, managing git worktrees, dispatching substantial coherent packages to sub-agents, merging completed package branches, and running lightweight integration checkpoints before downstream work begins.

**Tasks remain the tracking unit. Work packages are the delegation unit. Sub-agents handle substantial coherent packages; the main agent orchestrates git, package dispatch, merge, and checkpoint verification.**
```

- [ ] **Step 2: Load work-package rules**

After loading model preferences, add:

```markdown
## Step 3: Load Work Package Rules

Read `${CLAUDE_PLUGIN_ROOT}/references/work-packages.md`. Use it to validate planned packages, decide runtime adjustments, and avoid one-sub-agent-per-small-task dispatch.
```

Increment later step numbers as needed.

- [ ] **Step 3: Replace actionable-task analysis with package analysis**

Replace the actionable-task section with package-aware logic:

```markdown
## Step 5: Analyze Actionable Work Packages

Use `work_packages` from `tasks.json` as the starting point. Plans without `work_packages` are invalid and must fail deterministic validation upstream — implementation does not infer packages at runtime.

A work package is **externally actionable** when:
- It contains at least one `pending` task.
- No task in the package is `blocked` unless the whole package is being reported as blocked.
- Every package in `depends_on` has all tasks `done`.
- Any task dependency outside the package points to a task with `status: "done"`.

Task dependencies inside the same work package do not block dispatch. The sub-agent completes internal dependencies sequentially and commits after each task ID.

Collect all externally actionable work packages — not just the next task.
```

- [ ] **Step 4: Replace task-first dispatch planning with package-first planning**

Replace the current classification/consolidation subsections with:

```markdown
### Package Dispatch Planning

For each set of externally actionable work packages:

1. **Validate package shape:** Confirm each package is coherent, substantial, and has valid task IDs. One-task packages are allowed only when the task is substantial, risky, or isolated.
2. **Analyze file impact:** Use SPEC.md, task descriptions, package `primary_paths`, and acceptance criteria to determine likely files/modules touched by each package.
3. **Adjust packages when needed:** Merge, split, defer, or serialize packages if runtime file impact or current status makes the planned shape unsafe or inefficient. Briefly explain every adjustment.
4. **Select batch:** Run packages in parallel only when they are substantial and file impact does not overlap. Do not maximize fanout for its own sake.
5. **Announce and justify:** Before execution, present package IDs, task IDs, worktree branch names, primary paths, expected verification commands, and whether packages run in parallel or serially.
```

- [ ] **Step 5: Update worktree naming**

Change delegated worktree examples from task-only naming to package naming:

```bash
git worktree add .worktrees/<feature>/wp-<package-id> -b task/<feature>/<package-id> main
```

For dependent packages:

```bash
git worktree add .worktrees/<feature>/wp-<package-id> -b task/<feature>/<package-id> feature/<feature>
```

Keep branch prefix `task/<feature>/` to avoid broad branch naming refactors, but clarify that `<package-id>` names a package branch.

- [ ] **Step 6: Update sub-agent instructions**

Replace the sub-agent input list with package-oriented input:

```markdown
Each sub-agent receives:
- `.tasks/$ARGUMENTS/SPEC.md` — requirements specification
- `.tasks/$ARGUMENTS/tasks.json` — task and work-package details
- The assigned work package ID and task IDs
- Package `primary_paths` to inspect first
- Package `verification_commands`, if any
- The worktree path to work in (e.g., `.worktrees/<feature>/wp-WP1/`)
- `${CLAUDE_PLUGIN_ROOT}/references/clean-code-rules.md` — code quality rules to follow
- Project-level instructions (CLAUDE.md, AGENTS.md) if they exist
```

Replace the sub-agent obligations with:

```markdown
Each sub-agent must:
- Locate its assigned work package in tasks.json
- Complete the package's tasks in dependency order when internal dependencies exist
- Start code exploration with package `primary_paths`, then broaden only when imports, tests, or acceptance criteria require it
- Read existing files relevant to the assigned package before making changes
- Work exclusively within the assigned worktree directory
- Commit after completing each task ID so the orchestrator can assess per-task completion
- Run package `verification_commands` when provided, plus any directly relevant tests/checks discovered during implementation
- Report completed task IDs, acceptance criteria verified, commands run, files changed, and any follow-up risks
```

Keep the rule: do not pass conversation history to sub-agents.

- [ ] **Step 7: Add lightweight integration checkpoint after merges**

After merge verification and before collecting results, add:

```markdown
### Lightweight Integration Checkpoint

Before marking package tasks `done` or dispatching downstream packages, the main agent verifies the integrated feature branch state:

1. Confirm each package branch is merged into `.worktrees/<feature>/merge` using `git merge-base --is-ancestor`.
2. Confirm the merge worktree is clean or contains only intentional merge-resolution commits.
3. Review each sub-agent report for completed task IDs, acceptance criteria verification, commands run, and unresolved risks.
4. Run package `verification_commands` from the merge worktree when provided.
5. Run cheap relevant global checks when discoverable and appropriate for the project, such as targeted tests, typecheck, or lint. Do not run expensive full-suite checks after every package unless project convention indicates they are cheap.
6. If verification fails, do not dispatch downstream packages. Mark affected tasks `blocked` with a concise `blocked_reason`, or create a fix package if the issue is directly repairable within the current implementation scope.
```

- [ ] **Step 8: Update completion and cleanup wording**

Change cleanup references from one branch per sub-agent task to one branch per work package. Ensure consolidated package branches still require per-task commits before final package merge.

- [ ] **Step 9: Update rules section**

Replace the old parallelism rule with:

```markdown
- **Delegate work packages, not individual small tasks.** Sub-agents should receive substantial coherent packages that amortize context-loading cost.
- **Use parallelism selectively.** Parallelize substantial packages only when dependencies and likely file impact are safe. Do not maximize sub-agent fanout for its own sake.
- **Verify before downstream delegation.** After merging a package batch, run the lightweight integration checkpoint before marking tasks done and unlocking later packages.
```

- [ ] **Step 10: Verify implementation skill package language**

Run:

```bash
rg -n "work package|work_packages|wp-<package-id>|Lightweight Integration Checkpoint|Do not maximize sub-agent fanout" plugins/super-developer/skills/implement/SKILL.md
```

Expected: matches for package dispatch, package worktree naming, checkpoint, and selective parallelism.

- [ ] **Step 11: Commit Task 4**

```bash
git add plugins/super-developer/skills/implement/SKILL.md
git commit -m "feat: dispatch implementation work packages"
```

---

### Task 5: Update task status display for packages

**Files:**
- Modify: `plugins/super-developer/skills/tasks/SKILL.md`

- [ ] **Step 1: Add package display to single feature view**

After the feature progress header and before phase breakdown, add:

```markdown
If `work_packages` exists, display a package summary before the phase breakdown:

```
Work Packages
  🔄 WP1  Authentication backend flow      tasks: P1-T001, P1-T002, P1-T003
  ⬜ WP2  Login UI flow                     deps: WP1
  ✅ WP3  Documentation updates             tasks: P2-T004
```

Package status is computed from contained task statuses:
- ✅ all tasks `done` or `skipped`
- 🚫 any contained task `blocked`
- 🔄 any contained task `in-progress`
- ⬜ otherwise
```

- [ ] **Step 2: Add next actionable package display**

Extend the bottom summary:

```markdown
- **Next actionable work package** — first package with pending work whose package dependencies and external task dependencies are done. Show this only when `work_packages` exists.
```

- [ ] **Step 3: Keep task modification behavior task-based**

Add this clarification near status modification:

```markdown
Work package status is derived from task statuses. Do not directly mark a work package done; update the contained task statuses instead.
```

- [ ] **Step 4: Verify task skill package display text**

Run:

```bash
rg -n "Work Packages|Next actionable work package|derived from task statuses" plugins/super-developer/skills/tasks/SKILL.md
```

Expected: matches for package summary, actionable package, and derived status clarification.

- [ ] **Step 5: Commit Task 5**

```bash
git add plugins/super-developer/skills/tasks/SKILL.md
git commit -m "feat: show work package status"
```

---

### Task 6: Update README language

**Files:**
- Modify: `plugins/super-developer/README.md`

- [ ] **Step 1: Update overview language**

Replace language that implies broad parallel fanout with language like:

```markdown
Super Developer turns Claude Code into an opinionated development workflow engine. Instead of scattered slash commands and ad-hoc prompts, it provides a structured pipeline where each stage feeds the next — with right-sized sub-agent work packages, git worktree isolation, and adversarial review gates catching issues before they ship.
```

- [ ] **Step 2: Update skill table for `implementation-plan`**

Change the `implementation-plan` row to mention work packages:

```markdown
Converts a completed brainstorming or requirements discussion into a structured task plan under `.tasks/<feature>/` with `SPEC.md`, task-level acceptance criteria, and work packages that define right-sized implementation delegation.
```

- [ ] **Step 3: Update skill table for `implement`**

Change the `implement` row to:

```markdown
Orchestrator. Analyzes planned work packages, creates git worktrees per package, dispatches substantial coherent packages to sub-agents, merges package branches into the feature branch, and runs lightweight integration checkpoints before downstream work begins.
```

- [ ] **Step 4: Update Git Worktree Strategy bullets**

Replace one-task-per-worktree wording with package wording:

```markdown
- **Development happens in `.worktrees/`.** Each delegated work package gets its own worktree. Multiple substantial independent packages may run in parallel; related tasks are bundled to avoid repeated codebase exploration.
- **The orchestrator owns git.** Sub-agents receive a work package, task IDs, primary paths, and a worktree path — they write code and commit per task ID, while the orchestrator creates worktrees, merges branches, verifies integration, and cleans up.
```

- [ ] **Step 5: Update key design decisions**

Add or update a row:

```markdown
| Work packages as delegation unit | Sub-agents are valuable, but each spawn has fixed context cost. Bundling related tasks into substantial packages reduces repeated codebase exploration while preserving parallelism for independent workstreams. |
```

- [ ] **Step 6: Verify README package language**

Run:

```bash
rg -n "work package|work packages|right-sized|repeated codebase exploration" plugins/super-developer/README.md
```

Expected: matches in overview, skills table, worktree strategy, and design decisions.

- [ ] **Step 7: Commit Task 6**

```bash
git add plugins/super-developer/README.md
git commit -m "docs: describe work package delegation"
```

---

### Task 7: Rename review-plan reviewer roles in model-preferences

**Files:**
- Modify: `plugins/super-developer/references/model-preferences.md`

The `review-plan` and `skeptic-agent` keys, fallback chain, and adaptive value resolution remain semantically identical. Only the human-readable role names change to match the renamed reviewers in `review-plan/SKILL.md`.

- [ ] **Step 1: Update the Keys table**

Replace the row:

```markdown
| `skeptic-agent` | Adversarial reviewers: review-code Skeptic, review-plan Agent B | `default-model` → hardcoded default |
```

with:

```markdown
| `skeptic-agent` | Adversarial reviewers: review-code Skeptic, review-plan Adversarial Plan Challenger | `default-model` → hardcoded default |
```

Replace the row:

```markdown
| `review-plan` | Review-plan Agent A (completeness reviewer) | `default-model` → hardcoded default |
```

with:

```markdown
| `review-plan` | Review-plan Plan Quality Reviewer | `default-model` → hardcoded default |
```

- [ ] **Step 2: Update the Role-to-Key Mapping table**

Replace the row:

```markdown
| `review-plan` | `review-plan` key → Agent A (completeness) | `skeptic-agent` key → Agent B (adversarial) |
```

with:

```markdown
| `review-plan` | `review-plan` key → Plan Quality Reviewer | `skeptic-agent` key → Adversarial Plan Challenger |
```

- [ ] **Step 3: Update the Per-Skill Adaptive Interpretations table**

Replace the row:

```markdown
| `review-plan` | Sonnet for Agent A (completeness), Agent B governed by `skeptic-agent` key |
```

with:

```markdown
| `review-plan` | Sonnet for Plan Quality Reviewer, Adversarial Plan Challenger governed by `skeptic-agent` key |
```

- [ ] **Step 4: Sweep remaining `Agent A`/`Agent B` references**

Run:

```bash
rg -n "Agent A|Agent B" plugins/super-developer/references/model-preferences.md
```

Expected: no matches. If any remain, replace `Agent A` with `Plan Quality Reviewer` and `Agent B` with `Adversarial Plan Challenger` in the surrounding prose.

- [ ] **Step 5: Verify cross-skill consistency**

Run:

```bash
rg -n "Agent A|Agent B" plugins/super-developer
```

Expected: no matches anywhere under `plugins/super-developer`. Reviewer-role naming is now consistent across `review-plan/SKILL.md`, `model-preferences.md`, and any other docs.

- [ ] **Step 6: Commit Task 7**

```bash
git add plugins/super-developer/references/model-preferences.md
git commit -m "docs: rename review-plan reviewer roles"
```

---

### Task 8: Final verification

**Files:**
- Inspect all files changed by Tasks 1-7.

- [ ] **Step 1: Check working tree**

Run:

```bash
git status --short
```

Expected: clean working tree after all task commits.

- [ ] **Step 2: Check all new cross-references resolve**

Run:

```bash
rg -n "references/work-packages.md" plugins/super-developer/skills plugins/super-developer/README.md
```

Expected: references from `implementation-plan`, `review-plan`, and `implement`. README may or may not reference the path directly.

- [ ] **Step 3: Check no old implementation messaging remains dominant**

Run:

```bash
rg -n "Maximize parallelism|one-agent-per-task|Each task gets its own worktree|spawns parallel Opus-class sub-agents to write code" plugins/super-developer
```

Expected: no matches, or matches only in historical/contrast wording that explicitly says not to do this.

- [ ] **Step 4: Check plan review no longer mandates two reviewers for every plan**

Run:

```bash
rg -n "Collect structured findings from both agents|When both agents approve|Repeat until both agents approve|Launch two sub-agents in parallel|Spawn both agents again|both agents approve|two sub-agents" plugins/super-developer/skills/review-plan/SKILL.md
```

Expected: no unconditional two-reviewer requirements remain. Any matches must describe escalation or historical contrast only.

- [ ] **Step 5: Check package schema terms are consistent**

Run:

```bash
rg -n "work_packages|primary_paths|verification_commands|parallel_safe_with|depends_on" plugins/super-developer/skills plugins/super-developer/references plugins/super-developer/README.md
```

Expected: consistent field names across planning, review, implementation, tasks display, and reference docs.

- [ ] **Step 6: Check reviewer-role naming is consistent**

Run:

```bash
rg -n "Agent A|Agent B" plugins/super-developer
```

Expected: no matches. All references use `Plan Quality Reviewer` or `Adversarial Plan Challenger`.

- [ ] **Step 7: Review the diff**

Run:

```bash
git diff main...HEAD -- plugins/super-developer
```

Expected: changes are limited to the seven files listed in this plan (one created, six modified) and consistently describe package-based delegation plus adaptive plan-review depth.

---

## Self-Review

- Spec coverage: Covers planning-stage package creation, common reference rules, deterministic plan validation, adaptive plan-review depth, implementation dispatch, batch verification, status display, and README updates. No backward-compatibility surface — once a stage ships, prior plan shapes are not supported.
- Placeholder scan: No `TBD`, `TODO`, or unspecified implementation steps are present. Empty arrays in JSON examples are intentional schema examples.
- Type consistency: The same field names are used throughout: `work_packages`, `task_ids`, `depends_on`, `parallel_safe_with`, `primary_paths`, `verification_commands`, and `rationale`.
