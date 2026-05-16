# Tool Usage Reference

Load this reference before invoking plugin helper scripts. It covers command shape, helper boundaries, and safety rules; workflow-specific runbooks still own when each command is required.

## Command Shape

Run helper scripts from the repository root or the relevant worktree. Prefer explicit paths and explicit task/worktree arguments:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" ".tasks/<feature>/tasks.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" --final --worktree ".worktrees/<feature>/merge" ".tasks/<feature>/tasks.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" <command> --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge"
```

`taskctl.py` takes the subcommand first, then shared options.

## validate-tasks-json.py

Use this before trusting or dispatching a task plan:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" ".tasks/<feature>/tasks.json"
```

Use `--final` only as a final implementation or audit gate:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" --final --worktree ".worktrees/<feature>/merge" ".tasks/<feature>/tasks.json"
```

The final gate validates task lifecycle, accepted package proofs, proof freshness, required package command evidence, targeted-review evidence, and exact acceptance-criterion coverage. It does not execute package verification commands or review/audit logic.

## taskctl.py Read-Only Commands

Use these instead of ad hoc JSON parsing:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" summary --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" next-package --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" must-prove --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" proof-template --tasks ".tasks/<feature>/tasks.json" --package WP1 --output ".tasks/<feature>/proofs/WP1.proof.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" validate-proof --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge" ".tasks/<feature>/proofs/WP1.proof.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" validate-proofs --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge"
```

- `summary` reports task/package/proof health.
- `next-package` reports proof-ready candidates plus interrupted packages; it does not persist package status.
- `must-prove` emits transient acceptance/evidence obligations. Do not paste this output into `tasks.json`.
- `proof-template` writes a deterministic proof scaffold when `--output` is used. Use `--force` only when deliberately replacing stale proof after rejection or repair.
- `validate-proof` and `validate-proofs` validate proof files but do not accept lifecycle state.

`must-prove` also emits `proof_schema_contract`. Package and repair agents must follow that contract when filling proof entries:

- successful evidence uses `status: "verified"`, not `passed`;
- automated command/test evidence uses one of the listed method values, not `automated`;
- command-like methods require `evidence.commands[]` objects with `cwd`, exact `command`, integer `exit_code: 0`, and `observed`;
- stale-only validation failures should be refreshed mechanically against current integration `HEAD`; Do not delegate proof repair unless evidence cannot be reproduced or another validation class also fails;
- lifecycle state is written by `accept-package` / `reopen-package`, not by hand;
- ignored `.tasks` proof artifacts must not be force-added or committed.

## taskctl.py Mutation Commands

Package proof lifecycle:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" accept-package --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge" ".tasks/<feature>/proofs/WP1.proof.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" reopen-package --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge" ".tasks/<feature>/proofs/WP1.proof.json"
```

Task lifecycle helpers:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" block-task --tasks ".tasks/<feature>/tasks.json" P1-T003 --reason "Needs user decision"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" reset-task --tasks ".tasks/<feature>/tasks.json" P1-T003
```

- `accept-package` writes accepted lifecycle state only after proof validation passes.
- `reopen-package` marks one accepted proof as reopened before repair.
- `block-task` requires a non-empty reason.
- `reset-task` returns interrupted or blocked work to `pending` after orchestrator review.

These helpers do not implement code, run package verification commands, perform targeted review, run final audit, merge branches, or merge to a target branch.

## Safety Rules

- Treat plan-provided commands as executable inputs. Screen them before running or delegating.
- Stop for explicit approval before destructive, externally visible, credential/network-sensitive, dependency-installing, service-starting, or out-of-scope commands.
- Prefer helper scripts over hand-editing lifecycle/proof state.
- Do not use helper success as proof that code works unless the relevant command evidence, targeted review, review-code, and audit gates have also passed.
