---
name: implement
description: >
  This skill should be used when the user asks to "implement", "execute the plan", "start building",
  "run implementation", "build the feature", "start coding", "execute tasks", or wants to execute
  tasks from a structured plan. Triggers on phrases like "implement", "execute", "build", "start
  development", "run tasks", "begin implementation". Also activates automatically as part of the
  development pipeline after plan review.
---

# Implement: Execute Tasks from Plan

Execute tasks from a feature's task plan. The main agent acts as an orchestrator — analyzing the dependency graph, assessing task complexity, managing git worktrees, and dispatching work. For complex tasks, sub-agents write the code in isolated worktrees. For simple, well-defined tasks, the main agent executes directly.

**The main agent orchestrates and may execute simple tasks inline. Sub-agents handle complex or parallel work.**

## Arguments

- `$ARGUMENTS` — Feature name (required). Must match a directory under `.tasks/`. If invoked from the pipeline, inherited from the review-plan step.

---

## Step 1: Load and Assess

1. Verify `.tasks/$ARGUMENTS/` exists and contains `SPEC.md` and `tasks.json`. If not, list available features and ask.
2. Read `.tasks/$ARGUMENTS/SPEC.md` and `.tasks/$ARGUMENTS/tasks.json` to assess current state.
3. Display status summary:

```
Feature: <title> (<status>)
Progress: <done>/<total> tasks
Current phase: <phase name>
```

## Step 2: Load Model Preferences

Read `${CLAUDE_PLUGIN_ROOT}/references/model-preferences.md` for the canonical schema and resolution procedure.

Resolve the model preference for the `implement` skill key. Hardcoded default: `adaptive`.

**Adaptive interpretation for implement:** Opus for complex/ambiguous tasks, Sonnet for simple/patterned ones. The inline/delegate boundary from Step 5.2 captures complexity — delegated tasks are complex enough to warrant a sub-agent. Within delegated tasks, bias toward Opus when uncertain.

Carry the resolved preference forward into Step 6d.

## Step 3: Initialize Git Worktree Infrastructure

invoke `worktree` skill for the complete git workflow reference.

Resolve the project root and set up the feature:

```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel)
```

1. Ensure `.worktrees/` is in `.gitignore`.
2. Create the feature branch as a ref (not a worktree): `git branch feature/<name> main`
3. If any tasks will be delegated to sub-agents (per Step 5.2), create the feature namespace directory: `mkdir -p .worktrees/<feature>/`. If all actionable tasks are classified as inline, defer worktree directory creation until a delegated task appears.

**The main working tree always stays on `main`.** Never run `git checkout` in the project root.

## Step 4: Analyze Actionable Tasks

A task is **actionable** when:
- Its `status` is `pending`
- Every task ID in its `dependencies` array has `status: "done"`

Collect **all** currently actionable tasks — not just the next one.

**Edge cases:**
- **All tasks `done`:** Update feature `status` to `completed`. Proceed to pipeline continuation.
- **Tasks `blocked`:** List with `blocked_reason`. Ask how to proceed.
- **Tasks `in-progress`:** Likely from an interrupted session. Show details and ask: continue, or reset to `pending`?

## Step 5: Plan Dispatching

For each set of actionable tasks, reason through these sub-steps in order:

### 5.1. Analyze File Impact

Read SPEC.md plus each task's description and acceptance criteria. Determine which files each task will likely create or modify. This analysis drives all subsequent decisions.

### 5.2. Classify Execution Mode

For each task, decide:

- **Inline** — execute as the main agent. No sub-agent, no worktree. Use when: the task affects ≤3 files, follows an existing pattern in the codebase, and has unambiguous acceptance criteria.
- **Delegate** — spawn a sub-agent in a worktree. Use when: the task is complex enough to benefit from focused context, needs parallel execution with other work, or requires isolation.

When the resolved model preference (Step 2) is `adaptive`, apply model selection to delegated tasks only. Inline tasks do not use model preferences.

### 5.3. Detect and Resolve Overlap

Compare file-impact maps across all tasks planned for concurrent execution. If any two tasks could touch the same file:

- **Serialize them** (run one after the other), OR
- **Consolidate them** into a single sub-agent in a single worktree

Never parallelize tasks with potential file overlap. When file-impact is ambiguous or unpredictable from the task description, default to serialization — the cost of unnecessary serialization is latency; the cost of incorrect parallelization is merge conflicts.

### 5.4. Consolidate Where Natural

Tasks in the same module, directory, or logical subsystem that are all being delegated — prefer consolidating into fewer sub-agents rather than one-agent-per-task. Fewer agents with related work produce more coherent code than many agents working in isolation.

### 5.5. Announce and Justify

Before executing, present the dispatching plan. For each task, state whether it is inline or delegated, which tasks are consolidated, and briefly why. This lets the user validate dispatching reasoning before execution begins.


## Step 6: Create Worktrees and Execute

For each batch of tasks:

### 6a. Create Task Worktrees

**For inline tasks (classified in Step 5.2):** Skip worktree creation. The main agent creates a task branch without a worktree: `git branch task/<feature>/<task> <base>` (where `<base>` is `main` for independent tasks or `feature/<feature>` for dependent tasks). The main agent works directly and commits to this branch.

**For delegated tasks — independent (no dependencies on earlier feature work):**
```bash
git worktree add .worktrees/<feature>/task-<task> -b task/<feature>/<task> main
```

**For delegated tasks — dependent (needs earlier phases merged into feature ref):**
```bash
git worktree add .worktrees/<feature>/task-<task> -b task/<feature>/<task> feature/<feature>
```

**Consolidated delegated tasks:** Use the first task ID in the group for the worktree and branch name. For example, if P1-T002, P1-T003, and P1-T004 are consolidated, create one worktree:
```bash
git worktree add .worktrees/<feature>/task-P1-T002 -b task/<feature>/P1-T002 main
```
The sub-agent implements all consolidated tasks within this single worktree.

Branching from the feature ref gives the task access to all previously merged work.

### 6b. Update Status

Set assigned tasks to `in-progress` in tasks.json. Write immediately.

### 6c. Execute Inline Tasks

For tasks classified as inline in Step 5.2, the main agent executes directly:

1. Read SPEC.md to understand the feature requirements holistically.
2. Read the task's description and acceptance criteria from tasks.json.
3. Read existing files relevant to the task before making changes.
4. Implement the changes and commit to the task branch with a descriptive message.
5. Verify each acceptance criterion.
6. Update task status to `done` with `completed_at` timestamp.

**Inline failure handling:** If an inline task turns out to be more complex than expected (ambiguous requirements, unexpected codebase interactions), reclassify it as delegated. Reset the task branch (`git branch -D task/<feature>/<task>` and recreate), then spawn a sub-agent for it in the next batch.

**Mixed batch ordering:** When a batch contains both inline and delegated tasks, execute inline tasks first, then spawn sub-agents for delegated tasks. This ensures inline commits are on their task branches before merge operations.

**All-inline scenario:** When all tasks in the feature are executed inline, no merge worktree is needed. Step 7 still updates tasks.json. Step 8 runs tests from the working directory or a feature branch checkout instead of a merge worktree. The Pipeline Continuation prompt applies only when sub-agents produced work requiring a merge worktree.

### 6d. Spawn Sub-Agents

For tasks classified as delegated in Step 5.2, spawn sub-agents.

**Model selection** depends on the resolved preference from Step 2:

**`inherit`:** Do not pass a `model` parameter to sub-agents. They inherit the orchestrator's model.

**`adaptive` (default):** Use the complexity classification from Step 5.2. The inline/delegate boundary already captures this: delegated tasks are complex enough to warrant a sub-agent. Within delegated tasks, bias toward Opus when uncertain — the cost of a wrong downgrade is a subtle bug that survives audit. Use Sonnet only for delegated tasks that follow well-established patterns and have unambiguous scope.

**Specific model name (e.g., `claude-opus-4`):** Pass it directly as the `model` parameter to all sub-agents.

Each sub-agent receives:
- `.tasks/$ARGUMENTS/SPEC.md` — requirements specification
- `.tasks/$ARGUMENTS/tasks.json` — for specific task details
- The assigned task ID(s)
- **The worktree path to work in** (e.g., `.worktrees/<feature>/task-<task>/`)
- `${CLAUDE_PLUGIN_ROOT}/references/clean-code-rules.md` — code quality rules to follow
- Project-level instructions (CLAUDE.md, AGENTS.md) if they exist

Each sub-agent must:
- Read SPEC.md to understand the feature requirements holistically
- Locate its assigned task(s) by ID in tasks.json
- Read the clean code rules and follow them while writing code
- Read existing files relevant to the task(s) before making changes
- **Work exclusively within the assigned worktree directory**
- Implement the changes and commit within the worktree
- **When handling multiple consolidated tasks, commit after completing each task** (separate commit per task ID) so the orchestrator can assess per-task completion
- Verify each acceptance criterion
- Report what was done and which criteria were verified

**Do not pass conversation history to sub-agents.** They work from files only.

### 6e. Merge Completed Tasks into Feature Branch

After all sub-agents in the current batch complete, merge their work before starting the next batch. Merge once **per sub-agent branch** (not per task ID). For consolidated batches, multiple tasks share one branch — merge it once. For inline tasks, merge the task branch into the feature branch the same way.

```bash
# Create merge worktree on the feature branch (if not already created)
git worktree add .worktrees/<feature>/merge feature/<feature>
cd .worktrees/<feature>/merge

# Merge each task branch (one branch per sub-agent or inline task)
git merge task/<feature>/<task-name> --no-edit
```

**Merge conflict handling:** If `git merge` reports conflicts:
1. Inspect the conflicting files. If conflicts are trivially resolvable (adjacent non-overlapping changes in the same file), resolve them and commit.
2. If conflicts are substantive (overlapping logic, incompatible changes), abort the merge: `git merge --abort`
3. Set the conflicting task's status to `blocked` with `blocked_reason: "merge conflict with <other-task> in <file(s)>"`. For consolidated batches, block all tasks in the group.
4. Report the conflict to the user and suggest re-sequencing the conflicting tasks (run them serially instead of in parallel).

Complete Steps 6e and 6f for the current batch before returning to Step 4. Dependent tasks in the next batch require the feature ref to contain all previously merged work.

### 6f. Verify and Clean Up Task Worktrees

**Pre-cleanup verification (mandatory):**
```bash
cd .worktrees/<feature>/merge
git merge-base --is-ancestor task/<feature>/<task> HEAD && echo "merged" || echo "NOT MERGED"
# Verify each sub-agent's branch (one per sub-agent). ALL must print "merged".
```

**Only if ALL verify as merged:**
```bash
cd $PROJECT_ROOT
git worktree remove .worktrees/<feature>/task-<task>
git branch -d task/<feature>/<task>
```

For consolidated batches, there is one worktree and one branch to remove (named after the first task ID in the group).

**Keep the merge worktree** — it holds the feature branch checkout needed for subsequent steps.

## Step 7: Collect Results and Update

1. Update each completed task's `status` to `done` in tasks.json. Add `completed_at` timestamp.
2. If a sub-agent could not complete a task, set `status` to `blocked` with `blocked_reason`.
3. **Consolidated batch partial failures:** If a sub-agent reports partial completion of a consolidated batch, assess per-task status from the sub-agent's report and the per-task commits (as required in Step 6d). Mark completed tasks as `done` and failed ones as `blocked`. Merge the branch to preserve completed work; blocked tasks can be retried in a future batch.
4. Report to the user:

```
Batch complete:
  ✅ P1-T001 — Create user model
  ✅ P1-T002 — Add email validation
  ✅ P1-T003 — Login page component
  🚫 P1-T004 — Session store (blocked: Redis not configured)

Progress: 7/24
```

4. **Re-evaluate.** Completing tasks may unlock new actionable tasks. Loop back to Step 4 to find the next batch.

## Step 8: Phase and Feature Completion

When all tasks in a phase are `done`:
- Note the phase completion to the user.
- If more phases exist, continue to the next phase.

When all phases are complete:
1. Update feature `status` to `completed` in tasks.json.
2. Run tests to validate the integrated feature. If a merge worktree exists (`.worktrees/<feature>/merge`), run from there. If all tasks were executed inline (no merge worktree), run from a temporary feature branch checkout or the working directory.
3. Push the feature branch: `git push -u origin feature/<feature>`.
4. **Do NOT merge to main.** Wait for explicit user approval per the git worktree strategy. "Push to remote" does NOT mean "merge to main."

---

## Pipeline Continuation

If this stage failed or requires user intervention, STOP. Do not invoke the next stage.

If blanket approval was given (e.g., "proceed through all stages", "run end to end", "do everything"), default to `both` without asking.

Otherwise, present:

```
Implementation complete. Merge worktree at `.worktrees/<feature>/merge/`.

How do you want to proceed?

  audit   — Verify acceptance criteria and clean code compliance
  review  — Multi-agent code review (security, logic, performance, architecture)
  both    — Audit first, then code review if audit passes (sequential)
  done    — No further verification
```

| Selection | Action |
|---|---|
| `audit` | Use the Skill tool with: skill: "audit", args: "<feature-name>" |
| `review` | Use the Skill tool with: skill: "review-code", args: "<feature-name>" |
| `both` | Use the Skill tool with: skill: "audit", args: "<feature-name>". Treat as blanket pipeline approval — audit will automatically proceed to review-code upon PASS. |
| `done` | No action. Pipeline ends. |

Do NOT attempt to execute audit or review-code logic inline. The Skill tool loads each properly.

## Rules

- **The main agent orchestrates and may execute inline.** For simple, well-defined tasks (per Step 5.2), the main agent implements directly. For complex or parallel work, sub-agents write the code.
- **The main agent owns git infrastructure.** Sub-agents work in assigned worktree directories only. They do not create worktrees, branches, or run merge operations.
- **Maximize parallelism, respect dependencies.** Spawn concurrent sub-agents for independent tasks. Never parallelize tasks that share file dependencies, have potential file overlap (per Step 5.3), or have explicit dependency links.
- **Do not modify SPEC.md** during implementation.
- **Do not add new tasks** during implementation. If additional work is discovered, note it and suggest a plan update separately.
- **Follow project conventions.** Ensure sub-agents read CLAUDE.md / AGENTS.md if present.
- **Never merge to main without explicit user approval.** Even if the user says "push to remote."
