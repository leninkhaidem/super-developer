---
name: diagnose-and-fix
description: >
  Diagnoses defects evidence-first, records exact approvals, and routes repairs. Use for bugs, regressions,
  failing tests, troubleshooting, or "fix this". Do not use for planned features, ordinary review, incident
  containment, docs, releases, or speculative cleanup.
---

# Diagnose and Fix

Confirm the mechanism, recommend one route, and perform only approved actions. The parent orchestrates;
a fresh Fix Implementer edits under the passed contract.

## Always

- A bug report or “fix this” starts diagnosis only. Safe read-only repository inspection is allowed before
  approval; production edits and side effects are not.
- Confirm root cause only when evidence proves the mechanism. Otherwise return `blocked` or `not reproduced` with
  the exact artifact, access, command, or risk acceptance needed; do not substitute “likely.”
- Keep root checkout files/index user-owned: never switch it, edit it, merge there, or use it for delivery.
  Orchestration may run from `$PROJECT_ROOT` to manage approved non-root worktrees/refs through `worktree`.
- Keep repairs minimal. Route cross-module/service, contract, schema, security, data, concurrency, performance,
  dependency, or otherwise broad/risky change through `implementation-plan`.
- `implementation-plan` may plan approved changes to existing systems. “Fresh” describes its Slice-first
  planned-feature artifacts, not a new-code-only or new-system restriction.
- Delegate localized edits to a fresh Fix Implementer. The parent constructs the authority packet, passes
  `references/fix-implementer-contract.md`, and validates its report and repository state.
- Never infer approval from silence, “fix this,” diagnosis approval, or another approved action.
- This skill never executes live incident containment or production mutation, including rollback, traffic
  shifting, secret rotation, or live data/config changes. With an owning incident procedure and exact approval,
  hand off to that procedure; without both, stop.

## Approval Record

These fields govern diagnose bugfix/hotfix/spike work only; they do not retrofit planned-feature Execution
Contracts or sidecar checkpoint gates. One response may approve several exact independent fields:

- `production_edits`: approved paths/purpose/non-goals, or `not approved`;
- `worktree_creation`: exact base ref/SHA, local branch, and worktree path, or `not approved`;
- `commit`: exact worktree and reviewed manifest/snapshot checksum, or `not approved`;
- `branch_push`: remote, source/destination refs, source SHA, reviewed snapshot checksum, and
  `expected_remote_destination_sha` (exact SHA or `absent`), or `not approved`;
- `target_merge`: source ref/SHA, target ref and pre-merge SHA, reviewed snapshot checksum, merge strategy, and
  non-root integration worktree/ref, or `not approved`;
- `target_push`: remote/ref, exact post-merge target SHA, and expected remote target SHA, or `not approved`;
- `cleanup`: worktree path/HEAD/state, `local_ref_kind=direct` plus ref/SHA, required landing
  worktree/HEAD/state, remote ref plus expected SHA or `absent`, and each named action, or `not approved`;
- `diagnostic_actions`: each non-read-only command, instrumentation write, network use, or credential use.

No field implies another. Revalidate every bound SHA, snapshot, ref, remote, path, and worktree immediately before
its action; drift requires new approval. Never push without an exact immutable `branch_push` or `target_push` field.

## Do

1. Record symptom, expected/observed behavior, surface, explicit context/base, environment, and supplied evidence.
2. Inspect repository status, files, history, tests, and docs read-only. Do not mutate files, create refs/worktrees,
   access the network, start services, or use credentials.
3. Before nontrivial repro, test, harness, or service commands, load `../../references/tool-usage.md`. When project
   testing/harness policy applies, read accepted/current `docs/testing/workflow.md` and companions. If absent,
   stale, conflicting, or insufficient, invoke `testing` and stop command execution until it is accepted.
4. Ask exact approval before instrumentation, validation writes, unsafe commands, credentials, network, or service
   use. Put approved diagnostic spikes in a throwaway `worktree`; never promote their history.
5. Reproduce and minimize the failure. Record bounded commands/outcomes. Test falsifiable causes until evidence
   confirms one mechanism or a named blocker prevents confirmation.
6. Present the structured diagnosis report before production edits:
   - symptom and status: `reproduced`, `not reproduced`, `deterministic failing test`, or `blocked`;
   - evidence with commands/outcomes and files/symbols, or unavailable evidence;
   - confirmed root cause and proof, or exact confirmation blocker;
   - blast radius and `localized` versus `broad/risky` classification;
   - exactly one recommended route: stop/missing-info, named diagnostic spike, localized isolated fix, or
     `implementation-plan`, with rationale;
   - minimal strategy, non-goals, regression/spec test, verification, and residual risk;
   - proposed Approval Record values for only the next requested boundaries.
7. Ask approval for the recommended route and named fields. Unspecified or altered fields remain `not approved`.
8. For an approved localized fix, select one route and invoke `worktree` for approved setup:
   - active-feature: `bugfix/<name>` from explicit `feature/<feature>`;
   - maintenance: `bugfix/<name>` from an explicit maintenance base ref/SHA;
   - production hotfix: `hotfix/<name>` from an explicit production base ref/SHA, without live containment.
   Creation, commit, branch push, target merge, target push, and cleanup remain separate fields. Never use root as
   the repair or delivery checkout.
9. From the approved target worktree, resolve `implement` through `../../references/model-preferences.md` before
   binding state. If `.superdeveloper/preferences.yml` is missing, display the shared contract's gitignored local
   creation and require exact `diagnostic_actions` approval before creating it there; never create it in root or
   silently. Then bind HEAD and committed/staged/unstaged/untracked manifests/checksums. Untracked records include
   file type, Git/index-compatible mode, symlink target, and content digest or binary provenance. Dispatch with the
   `references/fix-implementer-contract.md`, and that path. Do not implement substantive edits inline.
10. Validate the report against packet, contract, starting binding, and actual worktree. Reject drift, out-of-scope
    paths, forbidden actions, missing regression evidence, incomplete outcomes, or unreported residuals. Route
    expansion back to diagnosis and broad/risky work to `implementation-plan`; never expand authority implicitly.
11. Bind post-fix `review-code` to exact base/HEAD/ref/worktree and every category snapshot/checksum, including
    untracked type, mode, symlink target, and digest/binary provenance. Never omit metadata or a category.
12. Invoke `review-code` with that binding plus `repair_owner=diagnose-and-fix` and
    `repair_contract_path=references/fix-implementer-contract.md`. Review findings use review-code’s action gate.
    On explicit `fix`, accept the confirmed repair packet/action back; then this parent dispatches a fresh worker
    under its contract, validates it, rebinds the complete state, and reruns review. Initial approval never repairs.
13. Commit only under the exact `commit` field, CLEAN unchanged snapshot, passing verification, and reviewed-only
    staging. For each approved delivery action invoke `worktree` and revalidate immutable bindings immediately.
    After target merge, capture its result SHA before proposing `target_push`; merge approval never authorizes push.
14. Return observed facts and next boundary. Preserve useful fixtures; clean only approved throwaway artifacts.

## Load if needed

- Localized implementation or review repair → pass `references/fix-implementer-contract.md` to a fresh worker.
- Nontrivial repro/test/harness/service command → `../../references/tool-usage.md` and accepted testing workflow.
- Worktree/ref creation, push, merge, or cleanup → invoke `worktree`.
- Broad/risky existing-system or feature change → invoke `implementation-plan` with the diagnosis handoff.
- Delivered localized state → invoke `review-code` with complete binding, repair owner, and contract path.

## Stop if

- Root cause is unconfirmed and next evidence requires unavailable input or an unapproved action.
- Approval, path, ref/SHA, remote, worktree state, testing policy, worker packet, or snapshot is missing/conflicting.
- State is dirty, drifted, or ambiguous enough to mix, hide, or overwrite user changes.
- A localized fix expands beyond approved paths or crosses a broad/risky boundary.
- Live containment/production mutation is requested: hand off only when procedure and exact approval exist;
  otherwise stop. Never execute it within this skill.
- A command needs credentials, network/external effects, destructive behavior, or unsafe changes without exact
  approval and the governing command/testing contract.

## Output

Return diagnosis, route, Approval Record, approvals consumed, worker validation, reviewed-state binding, changed
files, command outcomes, review actions, delivery/cleanup status, immutable SHAs/snapshots, risks, and next boundary.
