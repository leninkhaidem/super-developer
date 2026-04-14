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

Execute tasks from a feature's task plan. The main agent acts as an orchestrator — analyzing the dependency graph, identifying parallelizable work, managing git worktrees, and spawning sub-agents for implementation. Sub-agents write the code. The orchestrator manages all git infrastructure.

**Do not implement tasks as the main agent. Sub-agents write the code. The main agent orchestrates.**

## Arguments

- `$ARGUMENTS` — Feature name (required). Must match a directory under `.tasks/`. If invoked from the pipeline, inherited from the review-plan step.

---

## Step 1: Load and Assess

1. Verify `.tasks/$ARGUMENTS/` exists. If not, list available features and ask.
2. Read `.tasks/$ARGUMENTS/tasks.json` to assess current state.
3. Display status summary:

```
Feature: <title> (<status>)
Progress: <done>/<total> tasks
Current phase: <phase name>
```

## Step 2: Load Model Preferences

Check for `.claude/model-preferences.yml` in the project root:

```bash
cat "$PROJECT_ROOT/.claude/model-preferences.yml" 2>/dev/null
```

If the file exists and contains a valid `strategy` field (`adaptive` or `inherit`), use it.
If the file is missing, malformed, or contains an unrecognized strategy, ask the user:

```
How should sub-agent models be selected?

  adaptive  — Opus for complex tasks, Sonnet for simple ones (default)
  inherit   — All sub-agents use the same model as you (the orchestrator)
```

Save their choice (overwriting any corrupt file):

```yaml
# .claude/model-preferences.yml
# Controls how the implement skill selects models for sub-agents.
#   adaptive — Opus for complex/ambiguous tasks, Sonnet for simple/patterned ones
#   inherit  — All sub-agents use the orchestrator's model (no model override)
strategy: adaptive
```

Add `.claude/model-preferences.yml` to `.gitignore` if not already present — this is a local developer preference, not committed:

```bash
grep -qF '.claude/model-preferences.yml' .gitignore 2>/dev/null || echo '.claude/model-preferences.yml' >> .gitignore
```

Carry the resolved strategy forward into Step 6c.

## Step 3: Initialize Git Worktree Infrastructure

Read `${CLAUDE_PLUGIN_ROOT}/references/git-worktree-strategy.md` for the complete git workflow reference.

Resolve the project root and set up the feature:

```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel)
```

1. Ensure `.worktrees/` is in `.gitignore`.
2. Create the feature branch as a ref (not a worktree): `git branch feature/<name> main`
3. Create the feature namespace directory: `mkdir -p .worktrees/<feature>/`

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

## Step 5: Plan Execution Strategy

Analyze actionable tasks and decide on parallelism:

1. **Independent tasks** (no mutual dependencies, touch different files) — spawn concurrent sub-agents.
2. **Dependent or overlapping tasks** — execute serially.

Announce the plan before executing. If using the `adaptive` strategy, include model selection:

```
Actionable tasks: P1-T001, P1-T002, P1-T003, P2-T001
Strategy: adaptive

Execution plan:
  Parallel batch 1:
    Sub-agent A [Opus]:   P1-T001 (user model), P1-T002 (email validation) — new schema, no pattern to follow
    Sub-agent B [Sonnet]: P1-T003 (login page component) — matches existing component pattern
  Serial (after batch 1):
    P2-T001 (login endpoint) [Opus] — depends on P1-T001, auth-sensitive
```

If using `inherit`, omit model labels:

```
Actionable tasks: P1-T001, P1-T002, P1-T003, P2-T001
Strategy: inherit (using orchestrator model)

Execution plan:
  Parallel batch 1:
    Sub-agent A: P1-T001 (user model), P1-T002 (email validation)
    Sub-agent B: P1-T003 (login page component)
  Serial (after batch 1):
    P2-T001 (login endpoint) — depends on P1-T001
```

## Step 6: Create Worktrees and Execute

For each batch of tasks:

### 6a. Create Task Worktrees

**Independent tasks (no dependencies on earlier feature work):**
```bash
git worktree add .worktrees/<feature>/task-<task> -b task/<feature>/<task> main
```

**Dependent tasks (needs earlier phases merged into feature ref):**
```bash
git worktree add .worktrees/<feature>/task-<task> -b task/<feature>/<task> feature/<feature>
```

Branching from the feature ref gives the task access to all previously merged work.

### 6b. Update Status

Set assigned tasks to `in-progress` in tasks.json. Write immediately.

### 6c. Spawn Sub-Agents

**Model selection** depends on the strategy loaded in Step 2:

**`inherit` strategy:** Do not pass a `model` parameter to sub-agents. They inherit the orchestrator's model. Skip the complexity analysis below.

**`adaptive` strategy (default):** Select per-task based on complexity:

| Model | When to use | Examples |
|---|---|---|
| **Sonnet** | Trivial or standard tasks with well-defined scope and existing patterns to follow | Add a constant, rename a file, update an import, write tests for existing code, add a CRUD endpoint following an established pattern, add a component matching an existing one |
| **Opus** | Complex tasks with ambiguity, cross-module impact, security sensitivity, concurrency, or no clear existing pattern to follow | New architecture, cross-module refactor, concurrency logic, auth/security-sensitive code, tasks with vague acceptance criteria |

The orchestrator logs its model choice per task in the batch announcement (Step 5). Bias toward Opus when uncertain — the cost of a wrong downgrade is a subtle bug that survives audit.

Each sub-agent receives:
- `.tasks/$ARGUMENTS/CONTEXT.md` — project brief
- `.tasks/$ARGUMENTS/tasks.json` — for specific task details
- The assigned task ID(s)
- **The worktree path to work in** (e.g., `.worktrees/<feature>/task-<task>/`)
- `${CLAUDE_PLUGIN_ROOT}/references/clean-code-rules.md` — code quality rules to follow
- Project-level instructions (CLAUDE.md, AGENTS.md) if they exist

Each sub-agent must:
- Read CONTEXT.md to understand the feature holistically
- Locate its assigned task(s) by ID in tasks.json
- Read the clean code rules and follow them while writing code
- Read existing files relevant to the task(s) before making changes
- **Work exclusively within the assigned worktree directory**
- Implement the changes and commit within the worktree
- Verify each acceptance criterion
- Report what was done and which criteria were verified

**Do not pass conversation history to sub-agents.** They work from files only.

### 6d. Merge Completed Tasks into Feature Branch

After all sub-agents in the current batch complete, merge their work before starting the next batch:

```bash
# Create merge worktree on the feature branch (if not already created)
git worktree add .worktrees/<feature>/merge feature/<feature>
cd .worktrees/<feature>/merge

# Merge each completed task branch
git merge task/<feature>/<task-name> --no-edit
```

**Merge conflict handling:** If `git merge` reports conflicts:
1. Inspect the conflicting files. If conflicts are trivially resolvable (adjacent non-overlapping changes in the same file), resolve them and commit.
2. If conflicts are substantive (overlapping logic, incompatible changes), abort the merge: `git merge --abort`
3. Set the conflicting task's status to `blocked` with `blocked_reason: "merge conflict with <other-task> in <file(s)>"`.
4. Report the conflict to the user and suggest re-sequencing the conflicting tasks (run them serially instead of in parallel).

Complete Steps 6d and 6e for the current batch before returning to Step 4. Dependent tasks in the next batch require the feature ref to contain all previously merged work.

### 6e. Verify and Clean Up Task Worktrees

**Pre-cleanup verification (mandatory):**
```bash
cd .worktrees/<feature>/merge
git merge-base --is-ancestor task/<feature>/<task> HEAD && echo "merged" || echo "NOT MERGED"
# ALL must print "merged" before proceeding
```

**Only if ALL verify as merged:**
```bash
cd $PROJECT_ROOT
git worktree remove .worktrees/<feature>/task-<task>
git branch -d task/<feature>/<task>
```

**Keep the merge worktree** — it holds the feature branch checkout needed for subsequent steps.

## Step 7: Collect Results and Update

1. Update each completed task's `status` to `done` in tasks.json. Add `completed_at` timestamp.
2. If a sub-agent could not complete a task, set `status` to `blocked` with `blocked_reason`.
3. Report to the user:

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
2. Run tests from the merge worktree to validate the integrated feature.
3. Push the feature branch: `git push -u origin feature/<feature>` from the merge worktree.
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
| `audit` | Use the Skill tool with: skill: "super-developer:audit", args: "<feature-name>" |
| `review` | Use the Skill tool with: skill: "super-developer:review-code", args: "<feature-name>" |
| `both` | Use the Skill tool with: skill: "super-developer:audit", args: "<feature-name>". Treat as blanket pipeline approval — audit will automatically proceed to review-code upon PASS. |
| `done` | No action. Pipeline ends. |

Do NOT attempt to execute audit or review-code logic inline. The Skill tool loads each properly.

## Rules

- **Sub-agents own execution.** The main agent orchestrates (dependency analysis, worktree management, status updates) but does not write implementation code.
- **The main agent owns git infrastructure.** Sub-agents work in assigned worktree directories only. They do not create worktrees, branches, or run merge operations.
- **Maximize parallelism, respect dependencies.** Spawn concurrent sub-agents for independent tasks. Never parallelize tasks that share file dependencies or have explicit dependency links.
- **Do not modify CONTEXT.md** during implementation.
- **Do not add new tasks** during implementation. If additional work is discovered, note it and suggest a plan update separately.
- **Follow project conventions.** Ensure sub-agents read CLAUDE.md / AGENTS.md if present.
- **Never merge to main without explicit user approval.** Even if the user says "push to remote."
