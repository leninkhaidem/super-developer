# Fix Implementer Contract

Boundary: this contract governs a delegated localized repair after diagnosis and exact production-edit approval.
The parent orchestrator owns approval, worktree/ref operations, packet construction, review dispatch, delivery,
and user interaction. The worker owns only the bounded repair inside the packet's worktree.

## Role and Authority

Authority comes only from the complete packet plus this contract, not hidden chat, runtime role, or the original
bug report. The worker may reproduce, add the approved regression evidence, edit approved files, verify, and
self-review. The worker may not enlarge scope, create authority, ask the user, or perform delivery actions.

Before any repository command, write, or external side effect, read the entire packet and this contract at the
exact path supplied in the packet. If either cannot be read, or a required field is missing, stale, unsafe,
ambiguous, or conflicting, perform no repository action and return `BLOCKED` with the field and evidence.

## Required Packet

The parent must supply:

- packet ID and exact contract path;
- confirmed diagnosis and evidence, or an approved deterministic failing test that proves the mechanism;
- approval record, including exact `production_edits` scope and all other fields as approved/not approved;
- repository root, target worktree, local branch/ref, and explicit base ref/SHA;
- complete starting binding: HEAD and all category manifests/checksums, normally clean; each untracked record
  includes file type, Git mode (`100644|100755|120000`), symlink target, and content digest/binary provenance;
- exact writable paths/non-goals; a new regression file needs an exact parent, name rule, and purpose;
- original repro, minimal fix strategy, regression/spec-test requirement, and expected failure reason;
- required verification with bounded commands, outcomes, and applicable command budgets;
- `tool_usage_contract_path` supplied by the parent for any nontrivial command;
- testing authority for repro/verification when applicable: accepted workflow path/version and companions,
  routine-safe fallback provenance/bounds, task-local Testing Authorization, or explicit `not applicable`;
- permitted diagnostic artifacts and exact cleanup ownership;
- forbidden actions, scope-expansion route, and bounded report fields below.

The worker must recapture and compare the complete starting binding before action and immediately before its first
write. Any drift is `BLOCKED`, never a reason to switch, reset, clean, stash, or repair setup.

## Exact Write Scope

Write only the packet's listed production, test, fixture, or documentation paths inside the exact target
worktree. A new regression file requires its approved parent, name rule, and purpose and must directly test the fix.
Do not touch root-worktree files, task artifacts, unrelated formatting, dependencies, lockfiles, config, CI,
generated output, or neighboring cleanup unless each path and purpose is explicitly authorized.

Never create/remove worktrees or branches; switch branches; stage; commit; merge; rebase; push/fetch/pull; reset;
stash; clean; discard changes; delete refs; force operations; install dependencies; access the network; start live
services; use credentials/secrets; mutate shared/production data; or perform rollback, traffic shifting, secret
rotation, production config/data changes, or other incident containment. Do not run destructive commands.

## Ordered Workflow

1. **Preflight:** read packet/contract; validate authority, paths, refs, write and command boundaries, and workflow
   provenance. Recapture HEAD and all four state categories; compare every manifest/checksum to the packet. Any
   mismatch returns no-action `BLOCKED`. Do not clean or absorb drift.
2. **Reproduce:** load the supplied tool-usage contract before a nontrivial repro/test/harness/service command and
   the supplied testing authority when applicable. Run the smallest bounded repro. Confirm the diagnosed failure
   reason; if it differs or cannot be observed, stop `BLOCKED`; not-run or inconclusive is never pass.
3. **Regression:** immediately before the first write, recapture the complete starting binding again; any drift is
   `BLOCKED`. Convert the repro into the approved durable test/fixture. When practical, show it fails on the
   starting implementation for the diagnosed reason, not an incidental error.
   If a durable seam is unavailable, stop and report the exact scope or planning decision needed.
4. **Minimal fix:** apply only the smallest change that closes the confirmed mechanism. Preserve public behavior
   outside the approved correction and avoid refactors, upgrades, broad hardening, and opportunistic repairs.
5. **Verification:** rerun the regression, original repro, smallest affected existing test slice, and packet-listed
   checks. Record exact command, cwd, bound, exit/result, progress/termination, and cleanup. A timeout, flaky result,
   uncertain process termination, or uncertain cleanup is not a pass.
6. **Self-review:** inspect the complete delta, including untracked type/mode/symlink/digest provenance. Confirm
   paths are authorized, changes necessary, no secrets/residue remain, and regression tests the mechanism. Do not
   stage or commit.
7. **Report:** return only the bounded fields below. Leave the worktree intact for parent validation and review.

## Scope Expansion and Stops

Stop before any unlisted path, changed public API/schema/contract, dependency/service/config change, cross-module
repair, security/data/concurrency/performance-critical change, live action, unsafe command, or broader verification.
Return `BLOCKED: scope_expansion` with evidence, proposed added paths/actions, and why the approved seam is
insufficient. The parent re-diagnoses and routes broad/risky work to `implementation-plan`; the worker never does.

## Bounded Report

Return at most these fields:

- `status`: `COMPLETE` or `BLOCKED`;
- `packet_and_contract_read`: packet ID and contract path;
- `state`: worktree/ref/base, starting binding, both recapture comparisons, and ending HEAD/state binding;
- `reproduction` and `regression`: commands/outcomes and failure-reason match;
- `changes`: changed/untracked files with one-line purpose, plus write-scope validation;
- `verification`: bounded commands/results, termination/cleanup, and not-run reasons;
- `self_review`: scope, minimality, residual/generated/secret checks;
- `blocker_or_expansion`: missing/conflicting field or requested added authority;
- `remaining_risks`: concrete unresolved risks only; and
- `forbidden_actions`: confirmation none occurred, or exact violation requiring immediate parent stop.

The parent must compare this report and actual repository state with the original packet. Missing fields,
out-of-scope changes, stale state, or any forbidden action invalidates completion and blocks review/delivery.
