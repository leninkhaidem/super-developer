# Package Proof Lifecycle

Load this reference when implement needs routine taskctl proof or lifecycle operations: before package dispatch, when package agents return, when accepting a package, when blocking/resetting tasks, and before final feature completion.

`taskctl.py` is a thin helper over `tasks.json` and per-package proof files. It is not a TUI, workflow engine, generic JSON patcher, central ledger reconciler, test runner, review runner, or a reason to add heavyweight lifecycle history, event streams, checklist state, proof logs, or package status fields to `tasks.json`.

## Paths and Authority

Use one package proof file per work package:

```text
.tasks/<feature>/proofs/<WP-ID>.proof.json
```

The orchestrator owns task status transitions, package acceptance, final feature status, merge state, targeted package review, final review-code, and final audit. Package agents produce or refresh only their assigned package proof file and their package commits. They do not mark tasks done, finalize features, edit unrelated proof files, or reconcile a central evidence ledger.

## Command Form

Prefer explicit `--tasks` from the current worktree:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" --tasks ".tasks/<feature>/tasks.json" <command>
```

Use `--worktree <path>` for proof freshness checks when validating evidence against an integration worktree different from the command cwd.

## Read-Only Planning and Dispatch Queries

Use these before dispatch instead of ad hoc JSON snippets:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" --tasks ".tasks/<feature>/tasks.json" summary
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" --tasks ".tasks/<feature>/tasks.json" next-package
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" --tasks ".tasks/<feature>/tasks.json" must-prove WP1
```

`summary` reports feature, task, package, and proof health. `next-package` reports dependency-ready packages without persisting package status. `must-prove` derives a transient checklist from existing plan data and known-risk prompts; do not persist it into `tasks.json`.

## Proof Template Creation

Before spawning a package agent, create or provide the expected proof path:

```bash
mkdir -p ".tasks/<feature>/proofs"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" --tasks ".tasks/<feature>/tasks.json" proof-template WP1 --output ".tasks/<feature>/proofs/WP1.proof.json"
```

Use `--force` only when deliberately replacing stale package proof after rejection or repair. The template covers exactly the acceptance criteria assigned to that package; agents must fill current-state evidence rather than add unrelated criteria.

## Package Proof Validation

When a package agent returns, validate its proof file before accepting the package:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge" validate-proof WP1
```

Validation must pass for every assigned acceptance criterion and no criteria outside the package. Rejected proof is repaired by the package/repair agent, not by central ledger reconciliation.

## Package Acceptance

Only after package proof validation, package verification commands, and required targeted/semantic/focused repair review pass, accept the package:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge" accept-package WP1
```

`accept-package` is the routine path for marking package tasks done. It is not proof by itself; it is allowed only after the orchestrator has observed accepted proof, verification, and review gates. Manual status edits are explicit overrides and do not create package proof.

## Blocking and Resetting Tasks

Use taskctl for constrained lifecycle mutations:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" --tasks ".tasks/<feature>/tasks.json" block-task P1-T003 --reason "Needs user decision on API contract"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" --tasks ".tasks/<feature>/tasks.json" reset-task P1-T003
```

Block only when work needs user input, approved scope change, external credentials/facts, unsafe command approval, dependency/service approval, or a design/product decision. Reset interrupted work only when the orchestrator has decided it is safe to return the task to `pending`.

## Final Proof Validation and Completion

Before marking a feature complete, validate all package proofs, exact criterion coverage, package verification commands, and targeted package review gates. After the final review-code result is CLEAN and final audit result is PASS, pass those provenances through the supported final-gate writer path:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge" validate-proofs
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/taskctl.py" --tasks ".tasks/<feature>/tasks.json" --worktree ".worktrees/<feature>/merge" finalize-feature --final-review-source "<review-code CLEAN provenance>" --final-audit-source "<audit PASS provenance>"
```

`validate-proofs` catches missing, extra, stale, malformed, failed, blocked, wrong-package proof, missing package verification, and stale or mismatched targeted package review evidence. `finalize-feature` records current-commit `final_integration_review` and `final_audit` evidence only through explicit non-empty provenance options, then checks all final gates before writing completed status. It must not be used to bypass final review-code, delegated fixes, or final audit; those gates remain mandatory before completed status is authoritative.
