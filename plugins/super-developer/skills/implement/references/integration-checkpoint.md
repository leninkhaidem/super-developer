# Implement Integration Checkpoint

Load this reference at implement Step 7 after package agents return and before marking tasks `done` or dispatching downstream packages.

## Checkpoint Order

For each completed package batch:

1. Validate sub-agent reports and package proof files before merge.
2. Merge each package branch once into `.worktrees/<feature>/merge`.
3. Verify package branches are ancestors of the integration HEAD.
4. Confirm the integration worktree is clean or contains only intentional merge-resolution commits.
5. Run package verification commands from the integration worktree after command-safety screening.
6. Run targeted or semantic package review when required, including exact-scope post-fix review for serious findings.
7. Accept proof and mark tasks done only after all required checks pass.

Do not unlock downstream packages until this checkpoint passes for their dependencies.

## Package Proof Validation

Validate `.tasks/<feature>/proofs/<WP-ID>.proof.json` for every assigned acceptance criterion in the package, preferably through `taskctl.py validate-proof <WP-ID>` with `--worktree` pointing at the integrated merge worktree. Package proof files replace central ledger entries for package evidence; do not reconcile a shared `verification.json` as part of package acceptance.

Reject the package if any proof entry is:

- missing or malformed;
- not tied to an assigned criterion ID and source refs;
- outside the assigned package;
- missing state binding to the package/integrated branch state;
- missing file/symbol evidence;
- missing command result or concrete manual observation;
- missing required context-bundle citation;
- stale against the integrated branch;
- failed, blocked, or manual-required without explicit approval;
- hiding mocks or using mocks for a contract that had to be proven against real behavior.

The package proof must prove acceptance criteria in the current integrated state, not only in an unmerged package worktree.

## Package Verification

Run package `verification_commands` from `.worktrees/<feature>/merge` only after screening them under the top-level command-safety approval rule.

Also run cheap relevant global checks when discoverable and appropriate for the project, such as targeted tests, typecheck, or lint. Do not run expensive full-suite checks after every package unless project convention indicates they are cheap.

A committed package is not complete if verification fails, evidence is stale, or commands were skipped without approval when they are required to prove criteria.

When changed tests mutate import caches, module registries such as `sys.modules`, environment variables, globals, singleton caches, import stubs, monkeypatches, or equivalent shared process state, require pollution-sensitive ordering proof: test alone, test before and after likely consumers, and combined affected suite, or a concrete explanation for why the trigger does not apply.

## Targeted and Semantic Package Review

After a package passes integration verification, run targeted or semantic package review before dispatching dependent packages when:

- `targeted_review_required` is true;
- a risk tag triggers review under `work-packages.md`;
- package impact is security/privacy/safety/data/runtime/API/concurrency/performance/integration sensitive;
- high-risk cache semantics, lifecycle cleanup, boundary serialization, generated contract defaults, persistence, concurrency, public API, shared configuration, or similar cross-cutting impact could affect downstream packages;
- a serious finding was fixed and the exact finding class needs post-fix verification.

The review focuses on:

- integrated package delta;
- risk-class edge cases;
- context-bundle fidelity;
- no-mocks-for-contract compliance;
- Quality Contract compliance;
- whether package proof proves assigned criteria;
- downstream contract safety for dependent packages.

Confirmed issues are delegated as package-scope repair work before downstream dispatch. A fix commit alone does not close a serious finding: a focused reviewer or skeptic must verify that the exact finding class no longer reproduces against the post-fix integrated state. Keep this repair-review bounded to the confirmed finding class and fixed diff; do not reopen broad reviewer fanout, and do not treat it as a substitute for final whole-feature review-code or audit. The orchestrator does not fix issues inline.

## Rejection and Repair

Reject a package when code, evidence, verification, or review fails. Do not mark any task in the package `done` while assigned criteria remain unproven.

For in-scope failures, delegate a fresh repair/verification agent with the packet described in `subagent-contract.md`:

- SPEC and tasks;
- package ID and affected task/criterion IDs;
- rejection report;
- integrated diff/current files;
- current package proof file;
- failed command output or observed behavior;
- required context bundles;
- risk tags and edge cases;
- safe verification commands;
- instructions to update the assigned package proof and report evidence.

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

Include evidence locations, orchestrator-rerun commands, targeted/semantic review outcome, focused repair-review outcome when applicable, files changed, and unresolved risks. Do not present a task as complete unless accepted package-proof evidence exists for its criteria.
