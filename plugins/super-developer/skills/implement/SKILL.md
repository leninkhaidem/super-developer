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

Execute tasks from a feature's task plan. The main agent acts as an orchestrator — presenting the Execution Contract, validating dependency and file-impact boundaries, screening verification commands, managing git worktrees, dispatching work packages to sub-agents, validating their evidence ledger entries, merging completed package branches, running integration checkpoints, coordinating delegated fixes, and invoking final review/audit gates.

**Tasks remain the tracking unit. Work packages are the delegation unit. Sub-agents implement and self-verify substantial coherent packages; the main agent orchestrates git, package dispatch, evidence validation, merge, and checkpoint verification. In the planned-feature pipeline, the orchestrator does not perform substantive production/test/documentation implementation or fixes.**

## Arguments

- `$ARGUMENTS` — Feature name (required). Must match a directory under `.tasks/`. If invoked from the pipeline, inherited from the review-plan step.

---

## Step 1: Load and Assess

1. Verify `.tasks/$ARGUMENTS/` exists and contains `SPEC.md` and `tasks.json`. If not, list available features and ask.
2. Execute the shared validator before trusting `tasks.json`:

   ```bash
   python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" ".tasks/$ARGUMENTS/tasks.json"
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

Read `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/model-preferences.md` for the canonical schema and resolution procedure.

Resolve the model preference for the `implement` skill key. Hardcoded default: `adaptive`.

**Adaptive interpretation for implement:** Opus for complex/ambiguous packages, Sonnet for simple/patterned ones. Delegated packages are substantial enough to warrant a sub-agent; bias toward Opus when uncertain. Use Sonnet only for delegated packages that follow well-established patterns and have unambiguous scope.

Carry the resolved preference forward into Step 7d.

## Step 3: Load Work Package Rules

Read `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/work-packages.md`. Use it to validate planned packages, decide runtime adjustments, and avoid one-sub-agent-per-small-task dispatch.

## Step 4: Execution Contract Gate

Before creating worktrees or dispatching packages, present an **Execution Contract** derived only from `SPEC.md`, `tasks.json`, and accepted `design_decisions`:

```text
Execution Contract for <feature>

Packages:
- <WP-ID>: <title>
  tasks: <task IDs>
  branch/worktree: task/<feature>/<WP-ID> / .worktrees/<feature>/wp-<WP-ID>
  primary paths: <paths>
  risk tags: <risk_tags>
  targeted package review: yes/no and why
  required context bundles: <bundle IDs or none>
  verification commands: <safe/scoped commands or commands requiring approval>

Pipeline:
1. package implementation + sub-agent self-verification
2. orchestrator evidence/integration checkpoint
3. risk-triggered targeted package review and delegated fixes
4. full review-code/fix loop
5. final internal audit

Stop conditions:
- design/product behavior changes
- existing-feature contract changes
- destructive actions
- new dependencies or services
- security/privacy risk acceptance
- missing external facts or credentials
- scope expansion beyond SPEC/tasks
- stale git state or reviewed state
- repeated same-class failure needing strategy change

Choices:
  approve auto-resolve  — recommended; run until clean or a stop condition
  step-by-step          — ask before each major gate/fix round
  abort                 — stop before worktree creation
```

The user must approve the Execution Contract unless blanket approval was already given. Blanket approval selects `approve auto-resolve`. If any verification command is destructive, externally visible, credential/network-sensitive, installs dependencies/services, mutates outside the worktree, or exceeds the advertised verification scope, stop for explicit user approval before it can run even in auto-resolve.

## Step 4b: Initialize Git Worktree Infrastructure

invoke `worktree` skill for the complete git workflow reference.

Resolve the project root and set up the feature:

```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel)
```

1. Ensure `.worktrees/` is in `.gitignore`.
2. Create the feature branch as a ref (not a worktree): `git branch feature/<name> main`
3. Create the feature namespace directory: `mkdir -p .worktrees/<feature>/`.

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
- **All tasks `done`:** Do not update feature `status` here. Proceed directly to Step 9 final validation/completion.
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

### 6.5. Confirm Delegation Mode

Every selected planned-feature work package is delegated to a sub-agent in its own worktree. The orchestrator does not perform substantive implementation or fixes inline. If a package looks too small for a sub-agent, merge it with a related package or keep it serialized; do not turn the orchestrator into the implementer.

### 6.6. Announce and Justify

Before execution, present package IDs, task IDs, worktree branch names, primary paths, required context bundles, risk tags, targeted-review decisions, screened verification commands, and whether packages run in parallel or serially. This is the concrete Execution Contract for the selected batch.


## Step 7: Create Worktrees and Execute

For each batch of tasks:

### 7a. Create Package Worktrees

**For delegated packages — independent (no dependencies on earlier feature work):**
```bash
git worktree add .worktrees/<feature>/wp-<package-id> -b task/<feature>/<package-id> main
```

**For delegated packages — dependent (needs earlier phases merged into feature ref):**
```bash
git worktree add .worktrees/<feature>/wp-<package-id> -b task/<feature>/<package-id> feature/<feature>
```

**Each work package gets one worktree and one branch.** Use the work package ID for the worktree directory and branch name. The sub-agent implements all of the package's tasks within this single worktree, committing after each task ID.

Branching from the feature ref gives the package access to all previously merged work.

**Keep branch prefix `task/<feature>/`** to avoid broad branch naming refactors, but note that `<package-id>` names a package branch (one branch per work package, not one per task).

### 7b. Update Status and Ledger Shell

Set assigned tasks to `in-progress` in tasks.json. Write immediately. If `.tasks/$ARGUMENTS/verification.json` does not exist, create a minimal ledger shell with `schema_version: 1`, `feature`, and empty `entries` before dispatch so sub-agents append/update a shared artifact rather than inventing report formats.

### 7c. No Inline Implementation

The orchestrator does not implement planned-feature package work inline. Its direct edits are limited to workflow metadata (`tasks.json`, `verification.json` merge/rejection bookkeeping), mechanical merge-conflict/status artifacts, and explicit user-approved plan/status changes. If work requires production code, tests, substantive documentation, generated artifacts, or behavior changes, delegate it.

### 7d. Spawn Sub-Agents

For every selected package, spawn a sub-agent.

**Model selection** depends on the resolved preference from Step 2:

**`inherit`:** Do not pass a `model` parameter to sub-agents. They inherit the orchestrator's model.

**`adaptive` (default):** Delegated packages are substantial enough to warrant a sub-agent. Bias toward Opus when uncertain — the cost of a wrong downgrade is a subtle bug that survives audit. Use Sonnet only for packages that follow well-established patterns and have unambiguous scope.

**Specific model name (e.g., `claude-opus-4`):** Pass it directly as the `model` parameter to all sub-agents.

Each sub-agent receives:
- `.tasks/$ARGUMENTS/SPEC.md` — requirements specification
- `.tasks/$ARGUMENTS/tasks.json` — task and work-package details
- `.tasks/$ARGUMENTS/verification.json` — current evidence ledger, creating it if absent
- The assigned work package ID and task IDs
- The structured acceptance criteria assigned to those tasks, including stable criterion IDs and source refs
- Required context bundle IDs and bundle content from `tasks.json`
- Package `primary_paths` to inspect first
- Package `verification_commands` that the orchestrator has classified as safe to run; unsafe commands require explicit approval before delegation
- Package `risk_tags`, targeted-review decision, and required risk-class edge-case checklist
- The worktree path to work in (e.g., `.worktrees/<feature>/wp-WP1/`)
- `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/clean-code-rules.md` — the Development Quality Contract to follow
- Project-level instructions (CLAUDE.md, AGENTS.md) if they exist

Each sub-agent must:
- Locate its assigned work package in tasks.json
- Complete the package's tasks in dependency order when internal dependencies exist
- Start code exploration with package `primary_paths`, then broaden only when imports, tests, or acceptance criteria require it
- Read existing files relevant to the assigned package before making changes
- Read and cite required context bundles; do not infer or mock external/library/runtime contract shapes that a bundle defines
- Work exclusively within the assigned worktree directory
- Commit after completing each task ID so the orchestrator can assess per-task completion
- Run package `verification_commands` when provided, plus tests/checks it adds or modifies and the cheapest relevant existing tests/checks for touched paths
- Update `verification.json` with one entry per assigned acceptance criterion, including criterion ID, source refs, state binding, files/symbols, commands/results, observed behavior, edge cases, mock disclosure, and context-bundle citations
- Report completed task IDs, acceptance criteria verified, ledger entries written, Quality Contract Evidence, files changed, commands run, and any unresolved risks or scope-expansion requests

**Do not pass conversation history to sub-agents.** They work from files only.

### 7e. Merge Completed Tasks into Feature Branch

After all sub-agents in the current batch complete, validate their reports and ledger entries before merge. Merge once **per package branch** (not per task ID). For packages containing multiple tasks, the tasks share one branch — merge it once.

```bash
# Create merge worktree on the feature branch (if not already created)
git worktree add .worktrees/<feature>/merge feature/<feature>
cd .worktrees/<feature>/merge

# Merge each package branch
git merge task/<feature>/<package-id> --no-edit
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
3. Review each sub-agent report for completed task IDs, acceptance criteria verification, ledger entries written, commands run, context-bundle citations, mock disclosures, state binding, and unresolved risks.
4. Validate `verification.json` for the package's assigned criteria. Reject the package if entries are missing, malformed, not tied to assigned criterion IDs/source refs, lack file/symbol or command evidence, omit required context bundles, lack state binding, contain failed/blocked/manual-required statuses, or are stale against the integrated branch.
5. Run package `verification_commands` from the merge worktree only after command-safety screening. Stop for user approval before destructive, externally visible, credential/network-sensitive, dependency-installing, or out-of-scope commands.
6. Run cheap relevant global checks when discoverable and appropriate for the project, such as targeted tests, typecheck, or lint. Do not run expensive full-suite checks after every package unless project convention indicates they are cheap.
7. If verification fails, do not dispatch downstream packages. Reject the package and delegate a fresh repair/verification agent with SPEC.md, tasks.json, context bundles, rejection report, package diff, current ledger, failed command output, and exact acceptance criteria still unproven.

### 7e-ter. Risk-Triggered Targeted Package Review

After a package passes the integration checkpoint, run targeted package review before dispatching dependent packages when `targeted_review_required` is true or the package has a triggering risk tag. The targeted review focuses on the integrated package delta, risk-class edge cases, context-bundle fidelity, no-mocks-for-contract compliance, and whether the package evidence proves its assigned criteria. Confirmed issues are delegated as package-scope fix/repair work before downstream dispatch.

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

1. Update each completed task's `status` to `done` in tasks.json only after the package integration checkpoint, ledger validation, and any required targeted package review/fix pass. Add `completed_at` timestamp.
2. If a sub-agent could not complete a task or its evidence was rejected, set `status` to `blocked` with `blocked_reason` or delegate the fresh repair/verification agent described in Step 7e-bis when the issue is within scope.
3. **Package partial failures:** Treat a package as not merge-ready when any assigned acceptance criterion lacks valid evidence. Do not mark a task `done` merely because code was committed; `done` requires verified criteria and accepted ledger entries.
4. Report to the user:
   Include delegated sub-agent evidence locations, ledger-entry status, commands rerun by the orchestrator, targeted package review outcome when applicable, and unresolved risks.

```
Batch complete:
  ✅ P1-T001 — Create user model
  ✅ P1-T002 — Add email validation
  ✅ P1-T003 — Login page component
  🚫 P1-T004 — Session store (blocked: Redis not configured)

Progress: 7/24
```

5. **Re-evaluate.** Completing tasks may unlock new actionable work packages. Loop back to Step 5 to find the next batch.

## Step 9: Phase and Feature Completion

When all tasks in a phase are `done`:
- Note the phase completion to the user.
- If more phases exist, continue to the next phase.

When all phases are complete:
1. Run final ledger validation with `python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" --final ".tasks/<feature>/tasks.json"` from the integrated merge worktree when one exists. Reject stale, missing, failed, blocked, or unapproved manual-required entries.
2. Update feature `status` to `completed` in tasks.json only after ledger validation passes.
3. Run integrated tests/checks to validate the feature. If a merge worktree exists (`.worktrees/<feature>/merge`), run from there.
4. Push the feature branch: `git push -u origin feature/<feature>`.
5. **Do NOT merge to main.** Wait for explicit user approval per the git worktree strategy. "Push to remote" does NOT mean "merge to main."

---

## Pipeline Continuation

If this stage failed or requires user intervention, STOP. Do not invoke the next stage.

If blanket approval or `approve auto-resolve` was given, invoke immediately:

1. Use the Skill tool with: skill: "review-code", args: "<feature-name>". Treat as pipeline auto-resolve: confirmed 🔴/🟠 findings are delegated in coherent fix batches unless a stop condition or design-decision card requires the user.
2. After every delegated review-code fix batch, rerun review-code against the post-fix state. Continue the review-code/fix loop until review-code returns CLEAN or a defined stop condition requires user input.
3. Only after a CLEAN post-fix review-code result, use the Skill tool with: skill: "audit", args: "<feature-name>". This is the final internal acceptance gate and verifies the post-review/fix state.

If step-by-step mode was selected, present:

```
Implementation complete. Merge worktree at `.worktrees/<feature>/merge/`.

Next recommended gate:
  review-code  — Full code review and delegated fix loop

Final gate after clean review:
  audit        — Internal acceptance-completeness verification of the final state
```

Do NOT offer separate `audit`, `review`, and `both` choices as the normal post-implementation UX. Audit remains explicitly invocable standalone, but the planned-feature pipeline runs review-code before final audit.

Do NOT attempt to execute audit or review-code logic inline. The Skill tool loads each properly.

## Rules

- **The main agent orchestrates and verifies.** It does not perform substantive planned-feature production/test/documentation implementation or fixes. Direct edits are limited to workflow metadata, mechanical merge-conflict/status artifacts, and explicit user-approved plan/status changes.
- **Sub-agents implement and self-verify.** They must run targeted tests/checks before returning, update `verification.json`, and report evidence tied to acceptance criterion IDs.
- **The main agent owns git infrastructure.** Sub-agents work in assigned worktree directories only. They do not create worktrees, branches, or run merge operations.
- **Delegate work packages, not individual small tasks.** Sub-agents should receive substantial coherent packages that amortize context-loading cost.
- **Use parallelism selectively.** Parallelize substantial packages only when dependencies and likely file impact are safe. Do not maximize sub-agent fanout for its own sake.
- **Verify before downstream delegation.** After merging a package batch, run the integration checkpoint, validate ledger evidence, and complete any required targeted package review before marking tasks done and unlocking later packages.
- **Fix findings by delegation.** Audit/review/package-review fixes are batched by root cause/package/risk class and assigned to fresh fix agents with the finding evidence, current diff, context bundles, ledger, and exact criteria still unproven.
- **Do not modify SPEC.md** during implementation.
- **Do not add new tasks** during implementation. If additional work is discovered, note it and suggest a plan update separately.
- **Follow project conventions.** Ensure sub-agents read CLAUDE.md / AGENTS.md if present.
- **Never merge to main without explicit user approval.** Even if the user says "push to remote."
