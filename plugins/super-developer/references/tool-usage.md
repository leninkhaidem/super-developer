# Tool Usage Reference

Load this before invoking plugin helper scripts. It defines helper command shapes, boundaries, and safety rules; workflow runbooks own when a command is required.

## Command Shape

Run helpers from the repository root or relevant worktree. Prefer explicit plugin, task, and worktree paths.

Schema-version-4 Slice-first planned-feature artifacts use the small Markdown helper:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-plan ".tasks/<feature>/tasks.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" create-proof ".tasks/<feature>/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-proof ".tasks/<feature>/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-final ".tasks/<feature>/tasks.json"
```

Legacy schema-version-2/3 artifacts continue to use the existing JSON helpers:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" ".tasks/<feature>/tasks.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" --final --worktree ".worktrees/<feature>/merge" ".tasks/<feature>/tasks.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" <command> --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge"
```

`taskctl.py` takes the subcommand first, then shared options. Do not use `taskctl.py proof-template`, `accept-package`, `reopen-package`, or JSON proof lifecycle commands as the v4 Slice-first proof mechanism.

## sliceproof.py for v4 Slice-First Artifacts

Use `sliceproof.py` only for mechanical validation and proof-placeholder generation. It reads the v4 registry, work-package Markdown, authoritative Slice H3 IDs, and package proof Markdown. It does not run tests, inspect git freshness, judge semantic evidence sufficiency, accept/reopen packages, mutate registry status, or replace package review/final audit.

Read-only v4 commands:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-plan ".tasks/<feature>/tasks.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-proof ".tasks/<feature>/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-final ".tasks/<feature>/tasks.json"
```

`validate-plan` checks schema/version-4 registry shape, safe repo-relative registry/package/proof/Slice paths, required package Markdown sections, dependency references, and assigned Slice H3 ID existence. `validate-proof` checks package proof Markdown rows and unresolved markers mechanically. `validate-final` applies the same checks across all packages and requires final package registry state.

Status/dashboard workflows may use these read-only commands to display registry/package-path/dependency/proof mechanical health. The v4 `summary` and `next-package` concepts are dashboard calculations over the validated registry, not helper lifecycle commands; there is no v4 `accept-package` or `reopen-package` command. Dashboards read the validated registry and package Markdown paths directly, then label helper results as mechanical signals only. Do not use helper success, package assignment, registry status, or proof `PASS` rows as semantic implementation proof.

The only normal v4 write command creates the declared package proof Markdown placeholder:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" create-proof ".tasks/<feature>/tasks.json" --package WP1
```

Overwrite safety: `create-proof` fails when the proof file already exists. `--force` is destructive and is permitted only after screening confirms the existing file is an empty pre-dispatch placeholder. Filled proof evidence must not be silently erased: replacement requires `--force --approved-replacement "<approval/provenance/scope>"`, and the helper preserves the previous proof beside the proof path before writing the new placeholder. Without those preconditions the command fails closed.

## validate-tasks-json.py (legacy v2/v3)

Validate before trusting or dispatching a plan:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" ".tasks/<feature>/tasks.json"
```

Use `--final` only as the final implementation or audit gate:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" --final --worktree ".worktrees/<feature>/merge" ".tasks/<feature>/tasks.json"
```

The final gate checks lifecycle, accepted/fresh package proofs, required command evidence, targeted-review evidence, and exact acceptance-criterion coverage. It does not execute package verification commands or run review/audit logic.

## taskctl.py Read-Only Commands (legacy v2/v3)

Use these instead of ad hoc JSON parsing for schema-version-2/3 plans. These commands are compatibility helpers, not the v4 Slice-first proof lifecycle:

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

For legacy schema-version-2/3 only, stale-only refresh, dirty-proof handling, accepted/reopened state, and final proof validation semantics are owned by `skills/implement/references/package-proof-lifecycle.md` plus the legacy helper commands below; this reference preserves command shape and command-safety boundaries. Do not delegate stale-only refresh unless that lifecycle guidance says the evidence cannot be reproduced or another validation class also fails.

## taskctl.py Mutation Commands (legacy v2/v3)

Package proof lifecycle for schema-version-2/3 plans:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" accept-package --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge" ".tasks/<feature>/proofs/WP1.proof.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" reopen-package --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge" ".tasks/<feature>/proofs/WP1.proof.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" record-targeted-review --tasks ".tasks/<feature>/tasks.json" --package WP1 --reviewer "targeted-review-WP1" --evidence "integrated <commit/range>; mandatory package review passed; depth=standard; tests=sampled; safety=clean; serious findings 0 closed; repairs none; delta verification n/a"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" refresh-proof-state --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge" --package WP1 --reaccept
```

Task lifecycle helpers:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" start-package --tasks ".tasks/<feature>/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" complete-package --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" block-task --tasks ".tasks/<feature>/tasks.json" P1-T003 --reason "Needs user decision"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" reset-task --tasks ".tasks/<feature>/tasks.json" P1-T003
```

Lifecycle helpers do not implement code, run verification commands, perform targeted review, run final audit, merge branches, or merge to a target branch. `accept-package`/`reopen-package` write proof lifecycle state; `record-targeted-review` writes the minimal root `targeted_review`; `refresh-proof-state` is only for lifecycle-approved stale-only refresh; `start-package`, `complete-package`, `block-task`, and `reset-task` mutate task state within their named boundaries. `complete-package` marks tasks done only when the proof is accepted and final-ready, including the present/performed/passed mandatory package-review receipt in the existing `targeted_review` object.

## Safety Rules

- Treat plan-provided commands as executable inputs and screen before running or delegating.
- Stop for explicit approval before destructive, externally visible, credential/network-sensitive, dependency-installing, service-starting, or out-of-scope commands.
- Prefer helper scripts over hand-editing proof or legacy lifecycle state.
- For v4 dashboards, report registry status, package/proof paths, dependency readiness, and proof Markdown mechanical state as signals only.
- Do not use helper success as proof that code works unless command evidence, v4 package verification or legacy targeted review as applicable, review-code, and audit gates have also passed.
