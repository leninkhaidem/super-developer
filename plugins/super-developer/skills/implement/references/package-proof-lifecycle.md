# Package Proof Lifecycle

Load this reference before routine `taskctl.py` proof or task-state operations: package dispatch, proof template creation, proof validation, package proof acceptance/reopen, task blocking/resetting, read-only package selection, and final proof validation.

`taskctl.py` is a thin helper over `tasks.json` and per-package proof files. It is not a TUI, workflow engine, generic JSON patcher, central ledger reconciler, test runner, review runner, or a reason to add heavyweight lifecycle history, event streams, checklist state, proof logs, or package status fields to `tasks.json`.

## Paths and Authority

Use one package proof file per work package:

```text
.tasks/<feature>/proofs/<WP-ID>.proof.json
```

The orchestrator owns git, task status transitions, package proof acceptance, final feature status, package review, final review-code, and final audit. Package agents produce or refresh only their assigned package proof file and package commits. They do not mark tasks done, finalize features, edit unrelated proof files, or reconcile a central evidence ledger.

## Command Form

The current CLI takes the subcommand first, then shared options:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" <command> --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge"
```

Use `--worktree <path>` for proof freshness checks when validating evidence against an integration worktree different from the command cwd.

## Read-Only Dispatch Queries

Use these before dispatch instead of ad hoc JSON snippets:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" summary --tasks ".tasks/<feature>/tasks.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" next-package --tasks ".tasks/<feature>/tasks.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" must-prove --tasks ".tasks/<feature>/tasks.json" --package WP1
```

`summary` reports feature, task, package, and proof health. `next-package` reports dependency-ready packages without persisting package status, excludes interrupted `in-progress` packages, and reports them separately for orchestrator resolution. `must-prove` derives a transient checklist from existing plan data and the known-risk reference; do not persist that output into `tasks.json`.

## Proof Template Creation

Before spawning a package agent, create or provide the expected proof path:

```bash
mkdir -p ".tasks/<feature>/proofs"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" proof-template --tasks ".tasks/<feature>/tasks.json" --package WP1 --output ".tasks/<feature>/proofs/WP1.proof.json"
```

Use `--force` only when deliberately replacing stale package proof after rejection or repair. The template covers exactly the acceptance criteria assigned to that package; agents must fill current-state evidence rather than add unrelated criteria.

## Package Proof Validation

When a package agent returns, validate its proof file before accepting the proof lifecycle:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" validate-proof --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge" ".tasks/<feature>/proofs/WP1.proof.json"
```

Validation must pass for every assigned acceptance criterion and no criteria outside the package. Rejected proof is repaired by the package or repair agent, not by central ledger reconciliation.

Exception: when validation fails only because entries are stale against the current integration worktree, the orchestrator performs a mechanical stale-only refresh. Refresh only the stale entries by re-running the cited commands or re-inspecting the cited files against current integration `HEAD`, then update state/evidence fields and rerun validation. Do not delegate proof repair unless the evidence cannot be reproduced or another validation class fails too.

## Package Proof Acceptance

Only after package proof validation, package verification commands, and required targeted, semantic, or focused repair review pass, accept the proof lifecycle:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" accept-package --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge" ".tasks/<feature>/proofs/WP1.proof.json"
```

`accept-package` writes accepted lifecycle state into that package proof file. It does not mark tasks done by itself; the orchestrator changes task status only after evidence, verification, and review gates pass. Manual status edits are explicit overrides and do not create package proof.

Accepted package proofs are intentionally lean, but they must carry the gates that prevent review/fix loops:

- each listed package `verification_commands` entry appears as passing command evidence under an existing proof entry;
- packages with `targeted_review_required: true` include a minimal root `targeted_review` object with `required`, `performed`, `reviewer`, `result`, `evidence`, and `reviewed_at`.

Do not add a parallel command ledger, review history, event stream, or generated checklist to the proof file.

Use `reopen-package` before a repair that invalidates accepted proof content:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" reopen-package --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge" ".tasks/<feature>/proofs/WP1.proof.json"
```

## Blocking and Resetting Tasks

Use taskctl for constrained lifecycle mutations:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" block-task --tasks ".tasks/<feature>/tasks.json" P1-T003 --reason "Needs user decision on API contract"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" reset-task --tasks ".tasks/<feature>/tasks.json" P1-T003
```

Block only when work needs user input, approved scope change, external credentials/facts, unsafe command approval, dependency/service approval, or a design/product decision. Reset interrupted work only when the orchestrator has decided it is safe to return the task to `pending`.

## Final Proof Validation and Completion

After package tasks are marked `done` and feature status is `completed`, validate all package proofs, required package command evidence, targeted-review evidence, exact criterion coverage, and final task lifecycle:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" --final --worktree ".worktrees/<feature>/merge" ".tasks/<feature>/tasks.json"
```

Final feature completion still requires the final review-code/fix loop and final audit pass. A generic status mutation or manual schema edit cannot bypass accepted package proofs, final review, or final audit.
