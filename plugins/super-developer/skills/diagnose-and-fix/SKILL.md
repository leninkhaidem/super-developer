---
name: diagnose-and-fix
description: >
  Diagnoses defects evidence-first, obtains human-readable fix authorization, and routes repairs. Use for bugs,
  failing tests, regressions, troubleshooting, or "fix this". Do not use for planned features, ordinary review,
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
- Keep repairs minimal. Classify a repair by cost, not by category. A repair is `localized` only when both (i) the
  mechanism is confirmed by evidence, ideally a deterministic failing test, and (ii) the change is bounded and
  cheaply reversible. Check (i) and (ii) separately and require both; neither one alone is enough. When both hold,
  fix and review it here whatever subsystem or category it touches.
- A repair is `broad/risky`, and therefore goes through `implementation-plan`, only when one of these holds: the
  mechanism is unconfirmed and the fix requires choosing between viable designs; the change is hard to reverse,
  such as a schema or data migration or a published contract or API; or the blast radius cannot be bounded.
- `implementation-plan` may plan approved changes to existing systems. “Fresh” describes its Slice-first
  planned-feature artifacts, not a new-code-only or new-system restriction. For a broad/risky production repair,
  preserve the confirmed diagnosis and explicit production-base/hotfix/target delivery context; do not silently
  convert it into feature-branch delivery.
- Delegate localized edits to a fresh Fix Implementer. The parent constructs the authority packet, passes
  `references/fix-implementer-contract.md`, and validates its report and repository state.
- Never infer approval from silence, “fix this,” diagnosis approval, or another approved action.
- This skill never executes live incident containment or production mutation, including rollback, traffic
  shifting, secret rotation, or live data/config changes. With an owning incident procedure and exact approval,
  hand off to that procedure; without both, stop.

## Fix Authorization and Internal Receipt

Ask for one compact, human-readable Fix Authorization:

- approved paths and behavior goal, with explicit non-goals;
- isolated route plus human branch/base names;
- delivery: `local only`, `commit reviewed fix`, or `commit and push reviewed branch`;
- exceptional side effects such as diagnostic writes, network, credentials, or service use; and
- the routine enabling steps this repair needs: testing authority for the named bounded repro/verification
  commands, and gitignored local creation of `.superdeveloper/preferences.yml` when it is missing.

One response may authorize the displayed localized route through the selected branch delivery, including the
testing authority and the `preferences.yml` creation it names, so neither becomes a separate ask. It also covers
one exhaustion fallback: if that localized repair exhausts its three attempts, re-diagnose and hand the confirmed
diagnosis to `implementation-plan` without another ask. That handoff is planning only, and planning keeps its own
separate approval gate before anything is implemented, so it grants no implementation authority and never converts
the authorized `localized` repair into a `broad/risky` one. Unnamed scope, delivery, or side effects remain
unauthorized. Target merge/push and cleanup stay at their existing owning
boundaries. Users never need to understand or approve raw SHAs, checksums, leases, or state receipts.

The orchestrator derives mandatory internal receipts at action time from the `worktree` and review contracts:
authorized paths, non-root worktree/base/ref identity, reviewed state, exact commit/push/merge bindings, expected
remote state, cleanup proofs, and authorized diagnostic side effects. Revalidate every binding immediately before
its action. Orchestrator-owned progress within the authorized semantic action may bind/rebind without another user
approval; unexpected/external drift, conflict, scope/risk change, or failed preconditions stop for a human decision.
Never silently absorb drift. Keep receipts internal unless requested, needed for audit/debug, or required to explain
a blocker. Existing exact leases, ancestry checks, and separate target-merge/target-push bindings remain mandatory.
Approval of an `implementation-plan` route authorizes only the diagnosis handoff and planning; the later Execution
Contract and delivery gates separately own implementation, source/sidecar publication, target merge/push, and release.

## Do

1. Record symptom, expected/observed behavior, surface, explicit context/base, environment, and supplied evidence.
2. Inspect repository status, files, history, tests, and docs read-only. Do not mutate files, create refs/worktrees,
   access the network, start services, or use credentials.
3. Before nontrivial repro, test, harness, or service commands, load `../../references/tool-usage.md` and
   resolve testing authority. Use accepted/current `docs/testing/workflow.md` for high-risk/reusable work,
   routine-safe fallback for one clearly bounded local command, or task-local Testing Authorization for an exact
   focused approval, which the Fix Authorization may supply up front for its named commands. Missing workflow alone
   does not block read-only diagnosis or static analysis. Resolve authority; never fabricate it. If authority is
   insufficient, invoke `testing` or stop with `blocked`/`not-run`; never report not-run work as passed.
4. Ask exact approval before instrumentation, validation writes, unsafe commands, credentials, network, service
   use, or any task-local Testing Authorization the Fix Authorization did not already name. Put approved diagnostic
   spikes in a throwaway `worktree`; never promote their history.
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
   - proposed human-readable Fix Authorization for the selected route.
7. Ask once for Fix Authorization. Unspecified or altered semantic actions remain unauthorized.
8. For an approved localized fix, select one route and invoke `worktree` for approved setup:
   - active-feature: `bugfix/<name>` from explicit `feature/<feature>`;
   - maintenance: `bugfix/<name>` from an explicit maintenance base name;
   - production hotfix: `hotfix/<name>` from an explicit production base name, without live containment.
   Creation, commit, branch push, target merge, target push, and cleanup retain separate internal bindings. Never
   use root as the repair or delivery checkout.
9. From the approved target worktree, resolve `implement` through `../../references/model-preferences.md` before
   binding state. If `.superdeveloper/preferences.yml` is missing, display the shared contract's gitignored local
   creation; a Fix Authorization that named that exceptional write covers it, and otherwise ask before creating it
   there; never create it in root or silently. Then bind HEAD and committed/staged/unstaged/untracked
   manifests/checksums. Untracked records include file type, Git/index-compatible mode, symlink target, and content
   digest or binary provenance. Dispatch with the `references/fix-implementer-contract.md`, and that path.
   Do not implement substantive edits inline.
10. Validate the report against packet, contract, starting binding, and actual worktree. Reject drift, out-of-scope
    paths, forbidden actions, missing regression evidence, incomplete outcomes, or unreported residuals. Route
    expansion back to diagnosis and broad/risky work to `implementation-plan`; never expand authority implicitly.
11. Bind post-fix `review-code` to exact base/HEAD/ref/worktree and every category snapshot/checksum, including
    untracked type, mode, symlink target, and digest/binary provenance. Never omit metadata or a category.
12. Invoke `review-code` with that binding plus `repair_owner=diagnose-and-fix` and
    `repair_contract_path=references/fix-implementer-contract.md`. Review findings use review-code’s action gate.
    On explicit `fix`, accept the confirmed repair packet/action back; then this parent dispatches a fresh worker
    under its contract, validates it, rebinds the complete state, and reruns review. Initial approval never repairs.
    One confirmed mechanism gets at most three total repair attempts. Attempt 1 is the initial fix; attempts 2 and 3
    must each name a material delta in mechanism, evidence, or strategy. Never retry unchanged and never exceed three
    total attempts. On exhaustion, do step 15, then re-diagnose and hand the confirmed diagnosis to
    `implementation-plan` under that fallback — at most one such escalation per confirmed mechanism, and a
    relabeled mechanism earns no second one. If the same mechanism exhausts three attempts again, stop for the
    user. Never halt silently.
13. Commit only under the exact internal `commit` receipt, CLEAN unchanged snapshot, passing verification, and
    reviewed-only staging. For each authorized delivery action invoke `worktree` and revalidate its binding.
    After target merge, capture its result SHA before deriving `target_push`; merge never pushes by itself.
14. Return observed facts and next boundary. Preserve useful fixtures; clean only approved throwaway artifacts.
15. On attempt exhaustion, or on any stop once the fix loop has begun, do not return empty-handed. In the authorized
    non-root worktree preserve the deterministic reproducing test, if one was produced, in the repository's normal
    test location, and a short written diagnosis as `DIAGNOSIS.md` at that worktree's root, naming the confirmed
    mechanism or the exact blocker plus the attempts made. Land them only at the
    delivery level already authorized: under `local only` leave them in that worktree and report their paths; commit
    them on the bugfix branch only when the authorization covers a commit. This adds no new approval gate, and never
    pushes or merges.

## Load if needed

- Localized implementation or review repair → pass `references/fix-implementer-contract.md` to a fresh worker.
- Nontrivial repro/test/harness/service command → `../../references/tool-usage.md` and testing authority.
- Worktree/ref creation, push, merge, or cleanup → invoke `worktree`.
- Broad/risky existing-system or feature change → invoke `implementation-plan` with the diagnosis handoff; for
  production repair, apply `../worktree/references/bugfix-hotfix-workflow.md` planned-hotfix delivery context.
- Delivered localized state → invoke `review-code` with complete binding, repair owner, and contract path.

## Stop if

- Root cause is unconfirmed and next evidence requires unavailable input or an unapproved action.
- Authorization or an internal path/ref/SHA/remote/worktree/snapshot binding is missing or conflicting.
- State is dirty, drifted, or ambiguous enough to mix, hide, or overwrite user changes.
- A localized fix expands beyond approved paths or crosses a broad/risky boundary.
- Live containment/production mutation is requested: hand off only when procedure and exact approval exist;
  otherwise stop. Never execute it within this skill.
- A command needs credentials, network/external effects, destructive behavior, unsafe changes, or missing testing
  authority without exact approval and the governing command/testing contract.

Any stop reached after the fix loop has begun still performs step 15 before returning.

## Output

Return a concise diagnosis, Fix Authorization consumed, changed files, verification/review, delivery/cleanup,
risks, and next boundary. On a stop after the fix loop began, also report the preserved repro/diagnosis paths.
Include the internal receipt only on request or to explain audit/debug/drift/blockers.
