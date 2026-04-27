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

Execute tasks from a feature's task plan. The main agent acts as an orchestrator — analyzing planned work packages, validating dependency and file-impact boundaries, managing git worktrees, dispatching substantial coherent packages to sub-agents, merging completed package branches, and running lightweight integration checkpoints before downstream work begins.

**Tasks remain the tracking unit. Work packages are the delegation unit. Sub-agents handle substantial coherent packages; the main agent orchestrates git, package dispatch, merge, and checkpoint verification.**

## Arguments

- `$ARGUMENTS` — Feature name (required). Must match a directory under `.tasks/`. If invoked from the pipeline, inherited from the review-plan step.

---

## Step 1: Load and Assess

1. Verify `.tasks/$ARGUMENTS/` exists and contains `SPEC.md` and `tasks.json`. If not, list available features and ask.
2. Execute the shared validator before trusting `tasks.json`:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/assets/validate-tasks-json.py" ".tasks/$ARGUMENTS/tasks.json"
   ```

   If the validator exits non-zero, stop and resolve the reported `tasks.json` blockers before dispatching or updating work.
3. Read `.tasks/$ARGUMENTS/SPEC.md` and `.tasks/$ARGUMENTS/tasks.json` to assess current state.
4. Display status summary:

```
Feature: <title> (<status>)
Progress: <done>/<total> tasks
Current phase: <phase name>
```

## Step 2: Load Model Preferences

Read `${CLAUDE_PLUGIN_ROOT}/references/model-preferences.md` for the canonical schema and resolution procedure.

Resolve the model preference for the `implement` skill key. Hardcoded default: `adaptive`.

**Adaptive interpretation for implement:** Opus for complex/ambiguous packages, Sonnet for simple/patterned ones. The inline/delegate boundary from Step 6.5 captures complexity — delegated packages are substantial enough to warrant a sub-agent. Within delegated packages, bias toward Opus when uncertain.

Carry the resolved preference forward into Step 7d.

## Step 3: Load Work Package Rules

Read `${CLAUDE_PLUGIN_ROOT}/references/work-packages.md`. Use it to validate planned packages, decide runtime adjustments, and avoid one-sub-agent-per-small-task dispatch.

## Step 4: Initialize Git Worktree Infrastructure

invoke `worktree` skill for the complete git workflow reference.

Resolve the project root and set up the feature:

```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel)
```

1. Ensure `.worktrees/` is in `.gitignore`.
2. Create the feature branch as a ref (not a worktree): `git branch feature/<name> main`
3. If any packages will be delegated to sub-agents (per Step 6.5), create the feature namespace directory: `mkdir -p .worktrees/<feature>/`. If all actionable packages are classified as inline, defer worktree directory creation until a delegated package appears.

**The main working tree always stays on `main`.** Never run `git checkout` in the project root.

## Step 5: Analyze Actionable Work Packages

Use `work_packages` from `tasks.json` as the starting point. Plans without `work_packages` are invalid and must fail deterministic validation upstream — implementation does not infer packages at runtime.

A work package is **externally actionable** when:
- It contains at least one `pending` task.
- No task in the package is `blocked` unless the whole package is being reported as blocked.
- Every package in `depends_on` has all tasks `done`.
- Any task dependency outside the package points to a task with `status: "done"`.

Task dependencies inside the same work package do not block dispatch. The sub-agent completes internal dependencies sequentially and commits after each task ID.

Collect all externally actionable work packages — not just the next task.

**Edge cases:**
- **All tasks `done`:** Update feature `status` to `completed`. Proceed to pipeline continuation.
- **Tasks `blocked`:** List with `blocked_reason`. Ask how to proceed.
- **Tasks `in-progress`:** Likely from an interrupted session. Show details and ask: continue, or reset to `pending`?

## Step 6: Plan Dispatching

For each set of externally actionable work packages, reason through these sub-steps in order:

### 6.1. Validate Package Shape

Confirm each package is coherent, substantial, and has valid task IDs. One-task packages are allowed only when the task is substantial, risky, or isolated. If a planned package looks unsafe or incoherent at runtime, prefer adjustment (Sub-step 6.3) over dispatching as-is.

### 6.2. Analyze File Impact

Use SPEC.md, task descriptions, package `primary_paths`, and acceptance criteria to determine likely files/modules touched by each package.

### 6.3. Adjust Packages When Needed

Merge, split, defer, or serialize packages if runtime file impact or current status makes the planned shape unsafe or inefficient. Briefly explain every adjustment.

### 6.4. Select Batch

Run packages in parallel only when they are substantial and file impact does not overlap. Do not maximize fanout for its own sake. When file-impact overlap is ambiguous, default to serializing — the cost of unnecessary serialization is latency; the cost of incorrect parallelization is merge conflicts.

### 6.5. Classify Execution Mode

For each package selected into the batch, decide:

- **Inline** — execute as the main agent. No sub-agent, no worktree. Use when the package contains a single small task with unambiguous acceptance criteria, follows an existing pattern, and touches ≤3 files.
- **Delegate** — spawn a sub-agent in a dedicated worktree. Use for every other package, including all multi-task packages.

Inline tasks do not use sub-agent model preferences (Step 2). Delegated packages do.

### 6.6. Announce and Justify

Before execution, present package IDs, task IDs, worktree branch names, primary paths, expected verification commands, and whether packages run in parallel or serially. This lets the user validate dispatching reasoning before execution begins.


## Step 7: Create Worktrees and Execute

For each batch of tasks:

### 7a. Create Package Worktrees

**For inline tasks (classified per Step 6.5 — small or one-task packages eligible for inline execution):** Skip worktree creation. The main agent creates a task branch without a worktree: `git branch task/<feature>/<package-id> <base>` (where `<base>` is `main` for independent tasks or `feature/<feature>` for dependent tasks). The main agent works directly and commits to this branch.

**For delegated tasks — independent (no dependencies on earlier feature work):**
```bash
git worktree add .worktrees/<feature>/wp-<package-id> -b task/<feature>/<package-id> main
```

**For delegated tasks — dependent (needs earlier phases merged into feature ref):**
```bash
git worktree add .worktrees/<feature>/wp-<package-id> -b task/<feature>/<package-id> feature/<feature>
```

**Each delegated work package gets one worktree and one branch.** Use the work package ID for the worktree directory and branch name. The sub-agent implements all of the package's tasks within this single worktree, committing after each task ID.

Branching from the feature ref gives the package access to all previously merged work.

**Keep branch prefix `task/<feature>/`** to avoid broad branch naming refactors, but note that `<package-id>` names a package branch (one branch per work package, not one per task).

### 7b. Update Status

Set assigned tasks to `in-progress` in tasks.json. Write immediately.

### 7c. Execute Inline Tasks

For tasks classified as inline per Step 6.5, the main agent executes directly:

1. Read SPEC.md to understand the feature requirements holistically.
2. Read the task's description and acceptance criteria from tasks.json.
3. Read existing files relevant to the task before making changes.
4. Implement the changes and commit to the task branch with a descriptive message.
5. Verify each acceptance criterion.
6. Update task status to `done` with `completed_at` timestamp.

**Inline failure handling:** If an inline task turns out to be more complex than expected (ambiguous requirements, unexpected codebase interactions), reclassify it as delegated. Reset the task branch (`git branch -D task/<feature>/<task>` and recreate), then spawn a sub-agent for it in the next batch.

**Mixed batch ordering:** When a batch contains both inline and delegated tasks, execute inline tasks first, then spawn sub-agents for delegated tasks. This ensures inline commits are on their task branches before merge operations.

**All-inline scenario:** When all tasks in the feature are executed inline, no merge worktree is needed. Step 8 still updates tasks.json. Step 9 runs tests from the working directory or a feature branch checkout instead of a merge worktree. The Pipeline Continuation prompt applies only when sub-agents produced work requiring a merge worktree.

### 7d. Spawn Sub-Agents

For packages classified as delegated in Step 6.5, spawn sub-agents.

**Model selection** depends on the resolved preference from Step 2:

**`inherit`:** Do not pass a `model` parameter to sub-agents. They inherit the orchestrator's model.

**`adaptive` (default):** Use the complexity classification from Step 6.5. The inline/delegate boundary already captures this: delegated packages are substantial enough to warrant a sub-agent. Within delegated packages, bias toward Opus when uncertain — the cost of a wrong downgrade is a subtle bug that survives audit. Use Sonnet only for delegated packages that follow well-established patterns and have unambiguous scope.

**Specific model name (e.g., `claude-opus-4`):** Pass it directly as the `model` parameter to all sub-agents.

Each sub-agent receives:
- `.tasks/$ARGUMENTS/SPEC.md` — requirements specification
- `.tasks/$ARGUMENTS/tasks.json` — task and work-package details
- The assigned work package ID and task IDs
- Package `primary_paths` to inspect first
- Package `verification_commands`, if any
- The worktree path to work in (e.g., `.worktrees/<feature>/wp-WP1/`)
- `${CLAUDE_PLUGIN_ROOT}/references/clean-code-rules.md` — code quality rules to follow
- Project-level instructions (CLAUDE.md, AGENTS.md) if they exist

Each sub-agent must:
- Locate its assigned work package in tasks.json
- Complete the package's tasks in dependency order when internal dependencies exist
- Start code exploration with package `primary_paths`, then broaden only when imports, tests, or acceptance criteria require it
- Read existing files relevant to the assigned package before making changes
- Work exclusively within the assigned worktree directory
- Commit after completing each task ID so the orchestrator can assess per-task completion
- Run package `verification_commands` when provided, plus any directly relevant tests/checks discovered during implementation
- Report completed task IDs, acceptance criteria verified, commands run, files changed, and any follow-up risks

**Do not pass conversation history to sub-agents.** They work from files only.

### 7e. Merge Completed Tasks into Feature Branch

After all sub-agents in the current batch complete, merge their work before starting the next batch. Merge once **per package branch** (not per task ID). For packages containing multiple tasks, the tasks share one branch — merge it once. For inline tasks, merge the task branch into the feature branch the same way.

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
3. Set the conflicting task's status to `blocked` with `blocked_reason: "merge conflict with <other-task> in <file(s)>"`. For packages containing multiple tasks, block all tasks in the package.
4. Report the conflict to the user and suggest re-sequencing the conflicting tasks (run them serially instead of in parallel).

Complete Steps 7e, 7e-bis, and 7f for the current batch before returning to Step 5. Dependent packages in the next batch require the feature ref to contain all previously merged work.

### 7e-bis. Lightweight Integration Checkpoint

Before marking package tasks `done` or dispatching downstream packages, the main agent verifies the integrated feature branch state:

1. Confirm each package branch is merged into `.worktrees/<feature>/merge` using `git merge-base --is-ancestor`.
2. Confirm the merge worktree is clean or contains only intentional merge-resolution commits.
3. Review each sub-agent report for completed task IDs, acceptance criteria verification, commands run, and unresolved risks.
4. Run package `verification_commands` from the merge worktree when provided.
5. Run cheap relevant global checks when discoverable and appropriate for the project, such as targeted tests, typecheck, or lint. Do not run expensive full-suite checks after every package unless project convention indicates they are cheap.
6. If verification fails, do not dispatch downstream packages. Mark affected tasks `blocked` with a concise `blocked_reason`, or create a fix package if the issue is directly repairable within the current implementation scope.

### 7f. Verify and Clean Up Task Worktrees

**Pre-cleanup verification (mandatory):**
```bash
cd .worktrees/<feature>/merge
git merge-base --is-ancestor task/<feature>/<package-id> HEAD && echo "merged" || echo "NOT MERGED"
# Verify each package branch (one per work package). ALL must print "merged".
```

**Only if ALL verify as merged:**
```bash
cd $PROJECT_ROOT
git worktree remove .worktrees/<feature>/wp-<package-id>
git branch -d task/<feature>/<package-id>
```

For each work package, there is one worktree and one branch to remove (named after the package ID). Tasks within the package were committed individually but share the package branch.

**Keep the merge worktree** — it holds the feature branch checkout needed for subsequent steps.

## Step 8: Collect Results and Update

1. Update each completed task's `status` to `done` in tasks.json. Add `completed_at` timestamp.
2. If a sub-agent could not complete a task, set `status` to `blocked` with `blocked_reason`.
3. **Package partial failures:** If a sub-agent reports partial completion of a package, assess per-task status from the sub-agent's report and the per-task commits (as required in Step 7d). Mark completed tasks as `done` and failed ones as `blocked`. Merge the branch to preserve completed work; blocked tasks can be retried in a future batch.
4. Report to the user:

```
Batch complete:
  ✅ P1-T001 — Create user model
  ✅ P1-T002 — Add email validation
  ✅ P1-T003 — Login page component
  🚫 P1-T004 — Session store (blocked: Redis not configured)

Progress: 7/24
```

4. **Re-evaluate.** Completing tasks may unlock new actionable work packages. Loop back to Step 5 to find the next batch.

## Step 9: Phase and Feature Completion

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

- **The main agent orchestrates and may execute inline.** For small, well-defined packages (per Step 6.5), the main agent implements directly. For substantial or parallel work, sub-agents write the code.
- **The main agent owns git infrastructure.** Sub-agents work in assigned worktree directories only. They do not create worktrees, branches, or run merge operations.
- **Delegate work packages, not individual small tasks.** Sub-agents should receive substantial coherent packages that amortize context-loading cost.
- **Use parallelism selectively.** Parallelize substantial packages only when dependencies and likely file impact are safe. Do not maximize sub-agent fanout for its own sake.
- **Verify before downstream delegation.** After merging a package batch, run the lightweight integration checkpoint before marking tasks done and unlocking later packages.
- **Do not modify SPEC.md** during implementation.
- **Do not add new tasks** during implementation. If additional work is discovered, note it and suggest a plan update separately.
- **Follow project conventions.** Ensure sub-agents read CLAUDE.md / AGENTS.md if present.
- **Never merge to main without explicit user approval.** Even if the user says "push to remote."
