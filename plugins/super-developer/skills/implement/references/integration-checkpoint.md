# Implement Integration Checkpoint

Load this reference at implement Step 7 after package agents return and before marking tasks `done` or dispatching downstream packages. It owns integration checkpoint order and targeted package review; `package-proof-lifecycle.md` owns proof lifecycle runbooks.

## Checkpoint Order

For each completed package batch:

1. Validate sub-agent reports, required `SELF_REVIEW` blocks, and assigned package proof entries before merge.
2. Merge each package branch once into `.worktrees/<feature>/merge`.
3. Verify package branches are ancestors of the integration HEAD.
4. Copy or otherwise hand off the assigned package proof file into `.tasks/<feature>/proofs/WP<N>.proof.json` for the integration feature state. `.tasks/` is ignored by git, so branch merges do not carry proof files.
5. Confirm package branches did not force-add or commit ignored `.tasks` proof artifacts. If they did, save the proof to the shared task store, reset or repair the package branch to code/doc changes only, and reject the package until the branch is clean.
6. Confirm the integration worktree is clean or contains only intentional merge-resolution commits.
7. Run package verification commands from the integration worktree after command-safety screening, and ensure the package proof cites each required command as passing evidence.
8. Run mandatory targeted package review for every work package. Risk tags and runtime signals determine depth and lenses, not whether review runs.
9. After the package review and any required repair/delta verification close, add the minimal passing root `targeted_review` proof object with `required`, `performed`, `reviewer`, `result`, `evidence`, and `reviewed_at`.
10. Load `package-proof-lifecycle.md` and run `taskctl.py accept-package --tasks .tasks/<feature>/tasks.json --worktree .worktrees/<feature>/merge .tasks/<feature>/proofs/WP<N>.proof.json` for the package proof after code, verification, and review checks pass.
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

Do not duplicate the stale refresh runbook here. If `validate-proof` fails only because evidence is stale, load `package-proof-lifecycle.md` and follow its stale-only refresh procedure against the current integration `HEAD`.

Local safety kernel: do not mark tasks done, rerun targeted review when proof freshness invalidates review evidence, or unlock dependents until the refreshed proof validates and is accepted. Do not delegate stale-only refresh by default; delegate or block only when evidence cannot be reproduced, a criterion may no longer be true, or any non-stale validation class fails too.

## Targeted Package Review

After a package passes integration verification, run targeted package review before marking its tasks done or dispatching dependent packages. This is mandatory for every work package, including low-risk, docs-only, and test-only packages. `targeted_review_required`, risk tags, runtime risk upgrades, and conservative orchestrator judgment determine whether the review uses only the standard baseline or enhanced lenses for security/privacy/safety/data/runtime/API/concurrency/performance/integration, proof/review/audit/fix-loop, or shared-contract sensitivity; they do not determine whether review runs.

Use one focused reviewer by default. The reviewer must be independent from the package implementation agent; the package `SELF_REVIEW` block is input evidence, not a substitute for this review. Do not run the full `review-code` topology, Skeptic, or multiple specialists for routine clean packages; run Skeptic only for serious package-review finding candidates before they can block repair. Provide the reviewer the integrated package delta, package self-review block, relevant proof entries, targeted checks, risk tags, runtime risk signals, context bundles, and assigned acceptance criteria.

Every package review has the same standard baseline. Enhanced lenses add depth, not a separate review gate. The reviewer must return a compact transient report with explicit rows for:

- integrated package delta and changed surface;
- acceptance-criterion and proof coverage: assigned criteria, changed files/symbols, command/manual evidence, context-bundle fidelity, edge/failure/default coverage, and any uncovered surface;
- test scope declaration: `sampled`, `deep`, or `not applicable`, with rationale and named files/commands inspected. Sampling is the default; deepen when tests are proof-critical, tests changed helpers/mocks/snapshots/skips/generated fixtures, tests cover security/privacy/data/concurrency/contract risk, or tests are themselves the feature/risk surface;
- baseline security/privacy/safety sniff for every package: secrets/PII/logging exposure, authority/tool/subprocess/network boundaries, destructive/persistence/data-integrity risks, generated artifacts, and fail-closed behavior. Missing, vague, or concerning safety coverage blocks package acceptance until repaired or escalated at an authority boundary;
- mock/stub/fixture/generated-snapshot disclosure. Reject or escalate proof when mocks/stubs replace the external, library, runtime, API, or generated contract under test; mocks behind already-verified seams may pass only when disclosed and justified;
- Quality Contract compliance, package self-review quality, unresolved concerns, and depth-within-scope completeness: whether the package solved the relevant behavior/risk class rather than only the narrow happy path.

Suggestions are non-blocking unless they are bundled into the repair for an already confirmed serious issue under the existing serious-fix rules. A serious candidate from package review must be verified by Skeptic before it rejects the package or triggers repair delegation; unverified candidates remain suggestions or review notes, not blockers. Confirmed serious issues are delegated as package-scope repair work before downstream dispatch. The orchestrator does not fix them inline. The package review is local package-risk review, not whole-feature rediscovery.

When targeted review passes, record only the minimal passing `targeted_review` proof object with `taskctl.py record-targeted-review` after the review, any required repairs, and delta verification are closed. The receipt evidence must be compact and specific to the reviewed integrated package state, depth/lenses, test-scope declaration, safety sniff, and serious-finding closure; it must not store transcripts or histories. If a legacy plan has `tasks.json.targeted_review_required: false`, the recorded object may have `required: false`; the orchestrator still enforces the mandatory review checkpoint before marking tasks done. Do not hand-edit `targeted_review.required`, add failed review receipts, review histories, event streams, transcripts, or a parallel review ledger.

## Rejection and Repair

Reject a package when code, evidence, verification, or package review fails. Do not mark any task in the package `done` while assigned criteria remain unproven, confirmed review findings are open, repair verification has not closed, or proof refresh obligations remain.

A serious package-review candidate becomes blocking only after Skeptic verification confirms it. For confirmed in-scope findings, delegate a fresh repair/verification agent using the repair dispatch packet in `delegation-dispatch.md`; instruct the repair agent to read `repair-agent-contract.md`. Route package-review repairs in the integration worktree and bound them to the rejected work package, its confirmed findings, affected proof entries, and approved verification commands. Batch coherent findings for the same work package when feasible to avoid repeated repair loops. The orchestrator does not fix package findings inline and does not leave confirmed issues as report-only.

After a repair returns, default to delta closure review: verify the assigned findings, changed files, affected proof entries, and cited commands/test scope against the repaired integrated state. Run a full package rereview only when the repair widens scope, changes package contracts beyond the findings, touches previously unreviewed risk surfaces, invalidates the original coverage/test-scope/safety/mock disclosure, or produces repeated non-closing/contradictory evidence. Do not record the passing `targeted_review` receipt, accept the proof, mark tasks done, or unlock dependents until delta verification or required rereview closes.

Terminal handling is fail-closed. If repair is unsafe, out of scope, requires credentials/external facts/new dependency/product or design change/risk acceptance, fails verification, or repeatedly does not close the findings after a bounded retry and strategy change, keep the package unaccepted. Revert or isolate partial integration-worktree edits from the failed attempt before continuing, leave affected proofs reopened or refresh-required as applicable, and set `blocked` with `blocked_reason` only at the documented authority boundary. Do not silently retain unsafe edits, downgrade confirmed findings to suggestions, or unlock downstream packages on partial repair.

## Status Output

When a batch checkpoint completes, report compact status:

```text
Batch complete:
  ✅ P1-T001 — <title>
  ✅ P1-T002 — <title>
  🚫 P1-T003 — <title> (blocked: <reason>)

Progress: <done>/<total>
Evidence: <accepted>/<required> criteria accepted
Targeted review: <passed/repaired/blocked>
```

Include evidence locations, orchestrator-rerun commands, targeted-review outcome, files changed, and unresolved risks. Do not present a task as complete unless accepted package proof evidence exists for its criteria.
