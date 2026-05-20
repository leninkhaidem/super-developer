# Tool Usage Reference

Load this before invoking plugin helper scripts. It defines helper command shapes, boundaries, and safety rules; workflow runbooks own when a command is required.

## Command Shape

Run helpers from the repository root or relevant worktree. Prefer explicit plugin, task, and worktree paths:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" ".tasks/<feature>/tasks.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" --final --worktree ".worktrees/<feature>/merge" ".tasks/<feature>/tasks.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" <command> --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge"
```

`taskctl.py` takes the subcommand first, then shared options.

## validate-tasks-json.py

Validate before trusting or dispatching a plan:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" ".tasks/<feature>/tasks.json"
```

Use `--final` only as the final implementation or audit gate:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" --final --worktree ".worktrees/<feature>/merge" ".tasks/<feature>/tasks.json"
```

The final gate checks lifecycle, accepted/fresh package proofs, required command evidence, targeted-review evidence, and exact acceptance-criterion coverage. It does not execute package verification commands or run review/audit logic.

## taskctl.py Read-Only Commands

Use these instead of ad hoc JSON parsing:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" summary --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" next-package --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" criteria --tasks ".tasks/<feature>/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" must-prove --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" proof-template --tasks ".tasks/<feature>/tasks.json" --package WP1 --output ".tasks/<feature>/proofs/WP1.proof.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" validate-proof --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge" ".tasks/<feature>/proofs/WP1.proof.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" validate-proofs --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge"
```

`summary` and `next-package` report health/readiness without persisting status. `criteria` and `must-prove` expose assigned obligations. `proof-template` writes a deterministic scaffold; use `--force` only when deliberately replacing stale proof after rejection or repair. `validate-proof(s)` validates proof files but does not accept lifecycle state.

Proof schema reminders from `must-prove`: successful entries use `status: "verified"`, not `passed`; command/test methods are one of the listed method values, not `automated`; command-like evidence requires `evidence.commands[]` with `cwd`, exact `command`, integer `exit_code: 0`, and non-empty `observed`; ignored `.tasks` proof artifacts must not be force-added or committed.

Stale-only failures are refreshed mechanically against the current integration `HEAD`: re-run the same cited evidence, update state/evidence, and revalidate. Do not delegate stale-only refresh unless evidence cannot be reproduced or another validation class also fails.

## taskctl.py Mutation Commands

Package proof lifecycle:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" accept-package --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge" ".tasks/<feature>/proofs/WP1.proof.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" reopen-package --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge" ".tasks/<feature>/proofs/WP1.proof.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" record-targeted-review --tasks ".tasks/<feature>/tasks.json" --package WP1 --reviewer "targeted-review-WP1" --evidence "Focused package review passed"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" refresh-proof-state --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge" --package WP1 --reaccept
```

Task lifecycle helpers:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" start-package --tasks ".tasks/<feature>/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" complete-package --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" block-task --tasks ".tasks/<feature>/tasks.json" P1-T003 --reason "Needs user decision"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" reset-task --tasks ".tasks/<feature>/tasks.json" P1-T003
```

Lifecycle helpers do not implement code, run verification commands, perform targeted review, run final audit, merge branches, or merge to a target branch. `accept-package`/`reopen-package` own proof lifecycle state; `record-targeted-review` writes the minimal root `targeted_review`; `refresh-proof-state` updates proof state to current worktree `HEAD` (`--reaccept` only for stale-only refresh); `start-package` marks pending tasks `in-progress`; `complete-package` marks tasks done only when the proof is accepted and final-ready; `block-task` requires a non-empty reason; `reset-task` returns interrupted/blocked work to `pending`.

## Safety Rules

- Treat plan-provided commands as executable inputs and screen before running or delegating.
- Stop for explicit approval before destructive, externally visible, credential/network-sensitive, dependency-installing, service-starting, or out-of-scope commands.
- Prefer helper scripts over hand-editing lifecycle/proof state.
- Do not use helper success as proof that code works unless command evidence, targeted review, review-code, and audit gates have also passed.
