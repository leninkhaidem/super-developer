# Package Proof Lifecycle

This reference covers the Release 2 package proof lifecycle boundary for `assets/taskctl.py`. It is intentionally separate from eager-loaded implementation and audit skill prompts.

## Command Boundary

`accept-package` and `reopen-package` are package-level proof lifecycle writers. They update only the selected `.tasks/<feature>/proofs/WP<N>.proof.json` lifecycle object.

The Release 1 read-only commands remain read-only:

- `proof-template`
- `validate-proof`
- `validate-proofs`
- `must-prove`
- `summary`

Lifecycle commands are not task-status helpers, feature finalizers, audit replacements, or future pipeline cutover instructions. They do not execute recorded package verification commands.

## State Transitions

Release 2 supports only the current lifecycle state stored in the proof file:

| Current state | Command | Next state | Notes |
|---|---|---|---|
| none | `accept-package` | accepted | Requires a current valid package proof. |
| accepted | `reopen-package` | reopened | Reopens only the selected package proof. |
| reopened | `accept-package` | accepted | Requires validation to pass again. |
| accepted | `accept-package` | accepted | Idempotent only when the accepted state still matches the same proof digest and accepted state binding. |

Unsupported transitions fail closed. Release 2 does not add finalized, blocked, skipped, review, history, event-log, checklist, targeted-review, or workflow-engine lifecycle states.

## Provenance Shape

Accepted and reopened lifecycle state is helper-shaped JSON written by `taskctl.py`. The lifecycle object records the package id, proof path, proof digest, timestamp, writer shape, and state binding with worktree, git ref, and commit.

Validation rejects malformed, mismatched, missing-provenance, and non-helper-shaped lifecycle state. Because the lifecycle state is stored in a mutable proof file, Release 2 does not claim tamper-proof authenticity against a user who can forge helper-shaped JSON.

## Freshness

Accepted lifecycle state must stay bound to current proof content and git-tracked path evidence. Validation fails closed when cited evidence cannot prove path-scoped freshness, including renamed, deleted, untracked, URL-only, and manual-evidence cases.

Reopened lifecycle state records the current proof lifecycle but is not accepted proof evidence. A reopened proof must pass validation before it can be accepted again.

## Final Gate Compatibility

Accepted package proofs do not replace `verification.json` final implementation or audit gates in Release 2. Implementation and audit final success remain driven by the planned-feature verification ledger and its criterion-level evidence.
