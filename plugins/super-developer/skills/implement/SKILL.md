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

Execute reviewed feature tasks from `.tasks/<feature>/`. The main agent is an orchestrator only: it validates plan state, presents the Execution Contract, manages package worktrees/branches, dispatches work packages to sub-agents, validates evidence, merges package branches, runs integration checkpoints, delegates repairs, then continues to review-code and audit.

Tasks remain the tracking unit. Work packages are the delegation unit. Planned-feature package branches/worktrees are package-scoped; the compatibility branch prefix remains `task/<feature>/<WP-ID>`.

## Arguments

- `$ARGUMENTS` — Feature name (required). Must match a directory under `.tasks/`. Pipeline invocations inherit it from review-plan.

## Step 1: Load and Validate the Plan

1. Verify `.tasks/$ARGUMENTS/` contains `SPEC.md` and `tasks.json`; if not, list available features and ask.
2. Read `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/tool-usage.md` before invoking helper scripts.
3. Run the shared validator before trusting `tasks.json`:

   ```bash
   python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" ".tasks/$ARGUMENTS/tasks.json"
   ```

   If it fails, stop and resolve reported blockers before dispatching or updating work.
4. Read `SPEC.md`, `tasks.json`, accepted `design_decisions`, and `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/work-packages.md`.
5. Display feature status, progress, and current phase.

## Step 2: Load Execution Settings

Read `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/model-preferences.md` and resolve the `implement` key. Hardcoded default: `adaptive`.

Adaptive means delegated packages usually use Opus; use Sonnet only for simple, patterned, unambiguous packages. `inherit` omits a model parameter. Specific model names are passed directly.

## Step 3: Execution Contract Gate

Before creating worktrees or dispatching packages, present an Execution Contract derived only from `SPEC.md`, `tasks.json`, accepted `design_decisions`, and validated work-package metadata:

```text
Execution Contract for <feature>

Git refs:
  base ref: <base-ref, default main unless SPEC/tasks/user selected a stacked-feature base>
  feature ref: feature/<feature>
  target ref: <target-ref, default main; may be feature/<base> for stacked features>

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
4. review-code discovery, delegated fix batches, Fix Verification Review, and trigger-based widening/escalation
5. final internal audit after all known confirmed serious findings are fixed and verified closed

Stop conditions:
- design/product behavior changes
- existing-feature contract changes
- destructive actions
- new dependencies or services
- security/privacy risk acceptance
- missing external facts or credentials
- scope expansion beyond SPEC/tasks
- stale git or reviewed state
- no viable automated strategy remains after governed escalation

Choices:
  approve auto-resolve  — recommended; run until clean or a stop condition
  step-by-step          — ask before each major gate/fix round
  abort                 — stop before worktree creation
```

The user must approve this contract unless blanket approval already applies. Blanket approval selects `approve auto-resolve`.

**Command-safety approval rule:** Treat plan verification commands as executable inputs. Stop for explicit user approval before running or delegating any command that is destructive, externally visible, credential/network-sensitive, installs dependencies/services, mutates outside the package or merge worktree, or exceeds the advertised verification scope, even in auto-resolve mode.

## Step 4: Initialize Worktree Infrastructure

Invoke the `worktree` skill for git invariants, then load `plugins/super-developer/skills/implement/references/worktree-merge-cleanup.md` for implement-specific creation, merge, conflict, and cleanup commands.

Required inline invariants:
- Root worktree is user-owned; never switch it and never assume it is on `main`.
- Base ref: `<base-ref>` (default `main`; may be a parent feature branch such as `feature/<base>`).
- Feature ref: `feature/<feature>`.
- Target ref: `<target-ref>` (default `main`; for stacked features, usually the parent feature branch).
- Package worktree: `.worktrees/<feature>/wp-<WP-ID>`.
- Package branch: `task/<feature>/<WP-ID>`; `<WP-ID>` is a work package ID, not a task ID.
- Integration worktree: `.worktrees/<feature>/merge`.
- Merge package branches into the feature ref once per package branch.
- Prove package branches are merged with `git merge-base --is-ancestor` before removing worktrees/branches.
- Push `feature/<feature>` for review/testing when final implementation validation passes, but never merge into `<target-ref>` without explicit user approval for that exact target.

## Step 5: Analyze Actionable Packages

Use `work_packages` from validated `tasks.json`; implementation does not infer packages when they are absent. Load `plugins/super-developer/skills/implement/references/package-dispatch.md` for package shape, file-impact, runtime adjustment, and batch selection rules.

A package is externally actionable when:
- it contains at least one `pending` task;
- no task is `blocked` unless the whole package is reported blocked;
- every package in `depends_on` has all tasks `done`;
- every task dependency outside the package is `done`.

Internal task dependencies do not block dispatch; the package sub-agent sequences them and commits after each task ID.

Edge cases:
- All tasks `done`: do not update feature status here; proceed to final validation/completion.
- Any task `blocked`: list `blocked_reason` and ask how to proceed.
- Any task `in-progress`: treat as interrupted state; ask whether to continue or reset to `pending`.

## Step 6: Dispatch Packages

Every selected planned-feature package is delegated to a sub-agent in its own package worktree. The orchestrator does not perform substantive production/test/documentation implementation or fixes inline. If a package is too small, merge it with a related package or serialize it; do not turn the orchestrator into the implementer.

Before spawning, announce package IDs, task IDs, branch/worktree names, primary paths, context bundles, risk tags, targeted-review decisions, screened verification commands, model choice, and parallel/serial rationale.

Before spawning package agents, set assigned task statuses to `in-progress` in `tasks.json` and write the file. Ensure `.tasks/$ARGUMENTS/proofs/` exists in the shared task-artifact location and that each dispatched package has an assigned `.tasks/$ARGUMENTS/proofs/WP<N>.proof.json` target or template. Load `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/tool-usage.md` and `plugins/super-developer/skills/implement/references/package-proof-lifecycle.md` before routine `taskctl.py` proof, status, block/reset, next-package, or must-prove operations.

Load `plugins/super-developer/skills/implement/references/subagent-contract.md` and pass its contract to each package agent. Direct orchestrator edits are limited to workflow metadata (`tasks.json`, package proof artifact handoff/validation/acceptance bookkeeping), mechanical merge-conflict/status artifacts, and explicit user-approved plan/status changes.

## Step 7: Merge and Integration Checkpoint

After all package agents in the current batch return:

1. Validate their reports and assigned package proof files before merge.
2. Merge each completed package branch once into `.worktrees/<feature>/merge`.
3. Hand off the assigned package proof file into the integration feature state before final package proof validation. `.tasks/` is ignored by git, so do not rely on package branch merges to carry proof files.
4. Run the lightweight integration checkpoint before marking tasks done or dispatching downstream packages.
5. Run targeted package review when `targeted_review_required` is true or risk tags trigger it.
6. Delegate fresh repair/verification agents for rejected packages or confirmed review findings; do not fix inline.

Load `plugins/super-developer/skills/implement/references/integration-checkpoint.md` for package proof validation, package verification, targeted package review, rejection rules, and repair packets.

Evidence/proof gate: do not mark a task `done` merely because code was committed. Done requires an accepted package proof covering every assigned acceptance criterion, successful package verification, and any required targeted package review/fix pass.

## Step 8: Update Status and Continue Batches

Only after the integration checkpoint and targeted package review pass:

1. Set completed package tasks to `done` and add `completed_at`.
2. If evidence is rejected or package work is incomplete, set `blocked` with `blocked_reason` or delegate the repair packet from the integration checkpoint reference.
3. Report delegated evidence locations, package proof status, orchestrator-rerun commands, targeted package review outcome, files changed, and unresolved risks.
4. Re-evaluate actionable packages and loop to Step 5 until no dispatchable work remains.

## Step 9: Final Feature Completion

When all phases/tasks are complete:

1. Confirm every task is `done` with accepted package proof evidence; unresolved `pending`, `in-progress`, `blocked`, or `skipped` tasks are not final.
2. Update feature `status` to `completed`.
3. Run final package proof validation with `python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" --final --worktree ".worktrees/<feature>/merge" ".tasks/<feature>/tasks.json"` when an integrated merge worktree exists. Reject incomplete task lifecycle, missing required command evidence, missing targeted-review evidence, invalid, stale, unaccepted, or reopened package proofs.
4. Run integrated feature tests/checks from `.worktrees/<feature>/merge` when it exists, applying the command-safety approval rule.
5. Push the feature branch: `git push -u origin feature/<feature>`.
6. **Do not merge to the target branch.** Wait for explicit user approval for the named `<target-ref>`. "Push to remote" does not mean "merge to target."

## Pipeline Continuation

If implementation failed or requires user intervention, stop. Do not invoke the next stage.

If blanket approval or `approve auto-resolve` was given:
1. Invoke `review-code` with `<feature-name>` for the initial discovery review.
2. Delegate confirmed 🔴/🟠 findings in coherent fix batches unless a stop condition or design-decision card requires the user.
3. After each fix batch, use the review-code pipeline Fix Verification Review for the assigned dedupe keys. Do not rerun the full discovery review by default.
4. When Fix Verification Review returns non-closed verdicts, serious fix-introduced regressions, or widening triggers, follow the review-code pipeline widening/escalation rules before asking the user. User prompts are reserved for authority boundaries: product/design changes, scope expansion beyond SPEC/tasks, new dependencies/services, destructive or external actions, risk acceptance, credentials/external facts, unsafe commands, or no viable verification seam after escalation.
5. Invoke `audit` with `<feature-name>` only after all known confirmed serious findings are fixed and verified `closed`, required widened checks are complete, and no unresolved serious regression remains.

If step-by-step mode was selected, present review-code as the next recommended gate and audit as the final gate after review-code reaches audit readiness. Do not offer separate `audit`, `review`, and `both` choices as the normal post-implementation UX.

Do not execute review-code or audit logic inline; load each skill normally.

## Rules

- The main agent orchestrates and verifies; it does not implement planned-feature packages or fixes inline.
- Sub-agents implement and self-verify; they update only their assigned package proof file with criterion-level evidence tied to stable acceptance criterion IDs.
- The main agent owns git infrastructure. Sub-agents work only in assigned worktrees and do not create worktrees, branches, or merges.
- Delegate work packages, not individual small tasks. Parallelize selectively only when dependencies and likely file impact are safe.
- Validate package evidence, integrated state, and required targeted review before downstream delegation.
- Fix findings by delegation with current evidence, diff, context bundles, package proof state, and exact criteria still unproven.
- Do not modify `SPEC.md` or add tasks during implementation. Surface discovered additional work as a plan-update need.
- Follow project conventions and ensure package agents read CLAUDE.md / AGENTS.md if present.
- Never merge into `main` or any other target branch without explicit user approval for that exact target.
