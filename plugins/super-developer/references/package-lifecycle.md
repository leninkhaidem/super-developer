# Taskctl Package Lifecycle Boundary

This cold reference indexes the `taskctl.py` package-proof lifecycle command boundary. The canonical workflow owner is `plugins/super-developer/skills/implement/references/package-proof-lifecycle.md`, which owns accepted/reopened state, stale-only refresh, dirty-proof handling, targeted-review proof requirements, and final proof validation semantics.

## Command Boundary

`accept-package` and `reopen-package` are package-level proof lifecycle writers. They update only the selected `.tasks/<feature>/proofs/WP<N>.proof.json` lifecycle object.

Read-only commands remain read-only: `proof-template`, `validate-proof`, `validate-proofs`, `must-prove`, `summary`, and `next-package`.

Lifecycle commands are not task-status helpers, feature finalizers, audit replacements, review-state ledgers, or future pipeline cutover instructions. They do not execute recorded package verification commands.

## Transition Safety Kernel

`accept-package` requires a current valid package proof; `reopen-package` makes an accepted proof non-accepted until validation and acceptance pass again; unsupported transitions fail closed. For the current transition matrix, helper-shaped provenance, freshness rules, stale-only refresh, dirty-proof repair flow, and final gate semantics, load the canonical package proof lifecycle reference.

## Non-Bypass Rule

A generic status mutation, historical `verification.json`, `review-code-state.json`, or hand-edited lifecycle object is not accepted package proof evidence. Final implementation and audit success require completed task lifecycle plus one valid, current, lifecycle-accepted package proof per work package.
