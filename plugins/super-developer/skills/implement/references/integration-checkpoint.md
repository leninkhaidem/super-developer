# Implement Integration Checkpoint

Load this reference at implement Step 7 after package agents return and before marking tasks `done` or dispatching downstream packages.

## Checkpoint Order

For each completed package batch:

1. Validate sub-agent reports, required `SELF_REVIEW` blocks, and assigned package proof entries before merge.
2. Merge each package branch once into `.worktrees/<feature>/merge`.
3. Verify package branches are ancestors of the integration HEAD.
4. Copy or otherwise hand off the assigned package proof file into `.tasks/<feature>/proofs/WP<N>.proof.json` for the integration feature state. `.tasks/` is ignored by git, so branch merges do not carry proof files.
5. Confirm package branches did not force-add or commit ignored `.tasks` proof artifacts. If they did, save the proof to the shared task store, reset or repair the package branch to code/doc changes only, and reject the package until the branch is clean.
6. Confirm the integration worktree is clean or contains only intentional merge-resolution commits.
7. Run package verification commands from the integration worktree after command-safety screening, and ensure the package proof cites each required command as passing evidence.
8. Run targeted package review when required.
9. For packages requiring targeted review, add the minimal root `targeted_review` proof object with `required`, `performed`, `reviewer`, `result`, `evidence`, and `reviewed_at`.
10. Run `taskctl.py accept-package --tasks .tasks/<feature>/tasks.json --worktree .worktrees/<feature>/merge .tasks/<feature>/proofs/WP<N>.proof.json` for the package proof after code, verification, and review checks pass.
11. Accept evidence and mark tasks done only after all required checks pass.

Do not unlock downstream packages until this checkpoint passes for their dependencies.

## Package Proof Validation

Validate the assigned `.tasks/<feature>/proofs/WP<N>.proof.json` for every assigned acceptance criterion in the package. Reject the package if any entry is:

- missing or malformed;
- using invented `status` or `method` values such as `passed` or `automated`;
- not tied to an assigned criterion ID and source refs;
- missing state binding to the package/integrated branch state;
- missing file/symbol evidence;
- missing `evidence.commands` result object (`cwd`, exact `command`, `exit_code: 0`, `observed`) or concrete manual observation;
- missing required context-bundle citation;
- stale against the integrated branch;
- failed, blocked, or manual-required without explicit approval;
- hiding mocks or using mocks for a contract that had to be proven against real behavior;
- proving only a literal happy path or example input while omitting applicable behavior-class, edge/failure, default/omission, security/privacy/trust-boundary, data-integrity, concurrency, performance, or lifecycle coverage required by the package risk profile.

The package proof must prove acceptance criteria in the current integrated state, not only in an unmerged package worktree. Package completion requires accepted lifecycle state written after integrated validation.

## Package Verification

Run package `verification_commands` from `.worktrees/<feature>/merge` only after screening them under the top-level command-safety approval rule.

Also run cheap relevant global checks when discoverable and appropriate for the project, such as targeted tests, typecheck, or lint. Do not run expensive full-suite checks after every package unless project convention indicates they are cheap or the command is the only credible proof for an assigned acceptance criterion. Broad full-suite, generated-contract, typecheck, or lint checks should usually be modeled as integration/final checks instead of package `verification_commands`, unless they are required package proof.

A committed package is not complete if verification fails, evidence is stale, self-review reports unresolved concerns, or commands were skipped without approval when they are required to prove criteria. Accepted proof validation requires every listed package `verification_commands` entry to appear as passing command evidence in the package proof; listed package commands are not deferrable past package acceptance.

## Stale-Only Proof Refresh

When `validate-proof` fails only because entries are stale against the current integration worktree, keep the fix mechanical:

1. Identify only entries with stale evidence errors.
2. Re-run the same cited command(s) from the current integration worktree when commands are present, or re-inspect the same cited files/symbols when the entry is static-inspection evidence.
3. Update only those entries' `state.git_ref`, `state.commit`, `state.worktree`, `state.captured_at`, and observed evidence needed to reflect current integration `HEAD`.
4. Re-run `validate-proof`.

Do not delegate a proof-repair sub-agent, re-run targeted review, reopen task status, or edit unrelated proof entries for stale-only refresh. Delegate or block only when the command fails, the cited behavior is unclear, the evidence cannot be reproduced, a criterion may no longer be true, or validation reports schema/coverage/manual/targeted-review/lifecycle errors in addition to staleness.

## Targeted Package Review

After a package passes integration verification, run targeted package review before marking its tasks done or dispatching dependent packages when:

- `targeted_review_required` is true;
- a risk tag triggers review under `work-packages.md`;
- runtime risk upgrade classified the package as risk-bearing;
- the orchestrator conservatively decides review is needed because package impact is security/privacy/safety/data/runtime/API/concurrency/performance/integration, proof/review/audit/fix-loop, or shared-contract sensitive.

Use one focused reviewer by default. Do not run the full `review-code` topology, Skeptic, or multiple specialists for routine package review; reserve those for final review-code or exceptional high-risk disputes. Provide the reviewer the integrated package delta, package self-review block, relevant proof entries, targeted checks, risk tags, context bundles, and assigned acceptance criteria.

The review focuses on:

- integrated package delta;
- risk-class edge cases;
- package self-review quality and unresolved concerns;
- corresponding tests as evidence quality, including mocks, skips, generated snapshots/contracts, and missing negative/failure/security/privacy/data/concurrency cases;
- context-bundle fidelity;
- no-mocks-for-contract compliance;
- Quality Contract compliance;
- depth-within-scope completeness: whether the package solved the relevant behavior/risk class rather than only the narrow happy path;
- whether evidence proves assigned criteria.

Confirmed issues are delegated as package-scope repair work before downstream dispatch. The orchestrator does not fix them inline. The package review is local package-risk review, not whole-feature rediscovery.

When targeted review passes, record only the minimal `targeted_review` proof object with `taskctl.py record-targeted-review`. If the package was runtime-upgraded but `tasks.json.targeted_review_required` is false, the recorded object will have `required: false`; that is valid optional review evidence, and the orchestrator still enforces it as a runtime checkpoint before marking tasks done. Do not hand-edit `targeted_review.required`, add review histories, event streams, or a parallel review ledger.

## Rejection and Repair

Reject a package when code, evidence, verification, or review fails. Do not mark any task in the package `done` while assigned criteria remain unproven.

For in-scope failures, delegate a fresh repair/verification agent using the repair dispatch packet in `delegation-dispatch.md`; instruct the repair agent to read `repair-agent-contract.md`. Repair agents must update relevant proof evidence and report targeted verification; if they change implementation behavior, require the same compact self-review discipline before handoff. Do not duplicate the repair contract or package-agent contract in the orchestrator prompt beyond the dispatch packet.

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
