# Implement Integration Checkpoint

Load this reference at implement Step 7 after package agents return and before marking tasks `done` or dispatching downstream packages.

## Checkpoint Order

For each completed package batch:

1. Validate sub-agent reports and assigned package proof entries before merge.
2. Merge each package branch once into `.worktrees/<feature>/merge`.
3. Verify package branches are ancestors of the integration HEAD.
4. Copy or otherwise hand off the assigned package proof file into `.tasks/<feature>/proofs/WP<N>.proof.json` for the integration feature state. `.tasks/` is ignored by git, so branch merges do not carry proof files.
5. Confirm the integration worktree is clean or contains only intentional merge-resolution commits.
6. Run package verification commands from the integration worktree after command-safety screening, and ensure the package proof cites each required command as passing evidence.
7. Run targeted package review when required.
8. For packages requiring targeted review, add the minimal root `targeted_review` proof object with `required`, `performed`, `reviewer`, `result`, `evidence`, and `reviewed_at`.
9. Run `taskctl.py accept-package --tasks .tasks/<feature>/tasks.json --worktree .worktrees/<feature>/merge .tasks/<feature>/proofs/WP<N>.proof.json` for the package proof after code, verification, and review checks pass.
10. Accept evidence and mark tasks done only after all required checks pass.

Do not unlock downstream packages until this checkpoint passes for their dependencies.

## Package Proof Validation

Validate the assigned `.tasks/<feature>/proofs/WP<N>.proof.json` for every assigned acceptance criterion in the package. Reject the package if any entry is:

- missing or malformed;
- not tied to an assigned criterion ID and source refs;
- missing state binding to the package/integrated branch state;
- missing file/symbol evidence;
- missing command result or concrete manual observation;
- missing required context-bundle citation;
- stale against the integrated branch;
- failed, blocked, or manual-required without explicit approval;
- hiding mocks or using mocks for a contract that had to be proven against real behavior.

The package proof must prove acceptance criteria in the current integrated state, not only in an unmerged package worktree. Package completion requires accepted lifecycle state written after integrated validation.

## Package Verification

Run package `verification_commands` from `.worktrees/<feature>/merge` only after screening them under the top-level command-safety approval rule.

Also run cheap relevant global checks when discoverable and appropriate for the project, such as targeted tests, typecheck, or lint. Do not run expensive full-suite checks after every package unless project convention indicates they are cheap.

A committed package is not complete if verification fails, evidence is stale, or commands were skipped without approval when they are required to prove criteria. Accepted proof validation requires every listed package `verification_commands` entry to appear as passing command evidence in the package proof.

## Targeted Package Review

After a package passes integration verification, run targeted package review before dispatching dependent packages when:

- `targeted_review_required` is true;
- a risk tag triggers review under `work-packages.md`;
- the orchestrator conservatively decides review is needed because package impact is security/privacy/safety/data/runtime/API/concurrency/performance/integration sensitive.

The review focuses on:

- integrated package delta;
- risk-class edge cases;
- context-bundle fidelity;
- no-mocks-for-contract compliance;
- Quality Contract compliance;
- whether evidence proves assigned criteria.

Confirmed issues are delegated as package-scope repair work before downstream dispatch. The orchestrator does not fix them inline.

When targeted review passes, record only the minimal `targeted_review` proof object. Do not add review histories, event streams, or a parallel review ledger.

## Rejection and Repair

Reject a package when code, evidence, verification, or review fails. Do not mark any task in the package `done` while assigned criteria remain unproven.

For in-scope failures, delegate a fresh repair/verification agent with the packet described in `subagent-contract.md`:

- SPEC and tasks;
- package ID and affected task/criterion IDs;
- rejection report;
- integrated diff/current files;
- current package proof entries and lifecycle state;
- failed command output or observed behavior;
- required context bundles;
- risk tags and edge cases;
- safe verification commands;
- instructions to update package proof entries and report evidence.

Set `blocked` with `blocked_reason` only when the issue requires user input, approved scope change, external credentials/facts, unsafe command approval, dependency/service approval, or a design/product decision.

## Status Output

When a batch checkpoint completes, report compact status:

```text
Batch complete:
  ✅ P1-T001 — <title>
  ✅ P1-T002 — <title>
  🚫 P1-T003 — <title> (blocked: <reason>)

Progress: <done>/<total>
Evidence: <accepted>/<required> criteria accepted
Targeted review: <passed/not required/repaired/blocked>
```

Include evidence locations, orchestrator-rerun commands, targeted-review outcome, files changed, and unresolved risks. Do not present a task as complete unless accepted package proof evidence exists for its criteria.
