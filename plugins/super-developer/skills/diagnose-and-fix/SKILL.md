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
- Keep root checkout files/index user-owned: never switch it, merge there, or use it as the repair or
  delivery checkout. The only root write in this workflow is authorized gitignored creation of
  `$PROJECT_ROOT/.superdeveloper/preferences.yml` when missing; it grants no tracked source or index
  change. Orchestration may run from `$PROJECT_ROOT` to manage approved non-root worktrees/refs through
  `worktree`.
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
  `references/fix-implementer-contract.md`, and validates its report and repository state. Post-fix `review-code`
  is mandatory; a successful implementation report is not delivery readiness.
- Before diagnostic follow-ups, Fix Authorization, or repair, load `../../references/bounded-attempts.md`. Carry repair
  history and applicable limits across fixes, verification, and review; apply its progress rules inside inner loops too.
  Revisit a contradicted diagnosis before more edits. Failed rounds alone never authorize planning or wider scope.
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
  commands, and gitignored creation of `$PROJECT_ROOT/.superdeveloper/preferences.yml` when missing; and
- `caller_repair_policy: explicit|auto_confirmed_blocking`. Review-code's global default remains `explicit`, but a
  localized diagnose fix MUST propose `auto_confirmed_blocking` unless the user explicitly opts out. It covers
  evidence-backed repair rounds for confirmed blockers within the same behavior goal and localized seam; and
- exactly one scope envelope: (a) a fixed exact-path allowlist, or (b) canonical root allowlist plus the direct-effect
  rule—only implementation, directly affected callsites, and regression tests for the same confirmed mechanism—and
  explicit exclusions. Every worker still receives parent-enumerated exact writable paths; and
- any explicit user/approved limits and their scope, when present; do not request a default repair quota.

One response may authorize the displayed localized route through the selected branch delivery, including the
testing authority and the `preferences.yml` creation it names, so neither becomes a separate ask. Reassessment
stays inside authorized diagnostic scope; a revised mechanism must still fit the approved goal, seam, and write
scope. Planning requires an evidenced plan defect or broad/risky decision and its owning authorization, not retry
exhaustion. Unnamed scope, delivery, or side effects remain unauthorized. Target merge/push and cleanup retain
separate authority.

Internal receipts are orchestrator-owned mechanics, never a user-facing ask: apply
`references/orchestration-mechanics.md` in full at every binding, revalidation, and delivery action point.
Approval of an `implementation-plan` route authorizes only the diagnosis handoff and planning; the later Execution
Contract and delivery gates separately own implementation, source/sidecar publication, target merge/push, and release.

## Do

1. Record symptom, expected/observed behavior, surface, explicit context/base, environment, and supplied evidence.
2. Inspect repository status, files, history, tests, and docs read-only. Do not mutate files, create refs/worktrees,
   access the network, start services, or use credentials.
3. Before nontrivial repro, test, harness, or service commands, load `../../references/tool-usage.md` and resolve
   testing authority through the authority ladder and stop rules in `references/orchestration-mechanics.md`.
   Missing workflow alone does not block read-only diagnosis or static analysis.
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
8. For an approved localized fix, select one isolated route, bind it and every later delivery action through
   `references/orchestration-mechanics.md`, and invoke `worktree` for approved setup. Never
   use root as the repair or delivery checkout.
9. From the approved target worktree, complete the worker-dispatch prerequisites in
   `references/orchestration-mechanics.md` in order: resolve `implement` through
   `../../references/model-preferences.md`, settle any missing
   `$PROJECT_ROOT/.superdeveloper/preferences.yml` at the canonical primary root, and bind the complete
   starting state. Bind and pass the exact worker contract path
   `${SUPER_DEVELOPER_PLUGIN_ROOT}/skills/diagnose-and-fix/references/fix-implementer-contract.md`; do not implement
   substantive edits inline.
10. Validate the returned report and the actual worktree against `references/orchestration-mechanics.md`. Route
    expansion back to diagnosis and broad/risky work to `implementation-plan`; never expand authority implicitly.
11. Bind mandatory post-fix `review-code` to the complete state receipt and authorized
    `caller_repair_policy` that `references/orchestration-mechanics.md` requires.
12. Invoke `review-code` with that binding plus `repair_owner=diagnose-and-fix` and
    `repair_contract_path=${SUPER_DEVELOPER_PLUGIN_ROOT}/skills/diagnose-and-fix/references/fix-implementer-contract.md`.
    Under `explicit`, wait for accepted `fix`; under
    valid `auto_confirmed_blocking`, accept an eligible proposal without another ask. A proposal is never a packet or
    authority: apply the complete validation, control construction, fresh dispatch, verification, rebinding, and
    re-review transition in `references/orchestration-mechanics.md`. Only Skeptic-confirmed blocking findings enter
    the automatic loop; advisories, suggestions, and disputes remain report-only.
    Apply the loaded bounded-work contract: preserve repair/progress history and applicable limits, reassess
    diagnosis when progress stalls, and never retry unchanged or reset effort by relabeling the mechanism. Normal
    edit/test cycles are not failed rounds. Stop for non-convergence or an exhausted applicable limit using step 15,
    not an automatic planning handoff. Explicit repair gates and scope/risk boundaries still apply.
13. Commit and deliver only under the delivery bindings in `references/orchestration-mechanics.md`, invoking
    `worktree` for each authorized delivery action.
14. Return observed facts and next boundary. Preserve useful fixtures; clean only approved throwaway artifacts.
15. On non-convergence, an exhausted applicable limit, or any stop once the fix loop has begun, preserve the
    deterministic reproducing test, if one was produced, and a short written diagnosis naming the confirmed mechanism
    or exact blocker plus observed progress, failed hypotheses, and any applicable limit state. Apply the evidence
    safety preconditions, naming/never-overwrite rule, and delivery limits in `references/orchestration-mechanics.md`;
    return evidence in the response as it directs when a durable write is unsafe.

## Load if needed

- Command/testing authority, any state binding or revalidation, receipt reporting, worker or review dispatch,
  delivery, or durable evidence on exhaustion or a post-fix-loop stop → `references/orchestration-mechanics.md`.
- Diagnostic follow-ups, Fix Authorization, or repair → `../../references/bounded-attempts.md`; pass its exact path,
  repair evidence/history, and any applicable limit state with `references/fix-implementer-contract.md` to the worker
  and through review handoffs.
- Nontrivial repro/test/harness/service command → `../../references/tool-usage.md` and testing authority.
- Worktree/ref creation, push, merge, or cleanup → invoke `worktree`.
- Broad/risky existing-system or feature change → invoke `implementation-plan` with the diagnosis handoff; for
  production repair, apply `../worktree/references/bugfix-hotfix-workflow.md` planned-hotfix delivery context.
- Delivered localized state → invoke `review-code` with complete binding, repair owner, and contract path.

## Stop if

- Root cause is unconfirmed and next evidence requires unavailable input or an unapproved action.
- Authorization, policy, scope envelope, or an internal path/ref/SHA/remote/worktree/snapshot binding is missing,
  malformed, or conflicting.
- State is dirty, drifted, or ambiguous enough to mix, hide, or overwrite user changes.
- An applicable limit blocks the next action or its binding state is unknown; essential repair context cannot be
  recovered safely; or no evidence-backed next step remains after reassessment. No default quota/counter is required.
- A localized fix expands beyond its selected scope envelope or crosses a broad/risky boundary; disputed or
  advisory findings, design/product choices, hard-to-reverse contracts, unbounded scope, unsafe/external actions,
  risk acceptance, stale state, or missing authority are never automatic repairs.
- Live containment/production mutation is requested: hand off only when procedure and exact approval exist;
  otherwise stop. Never execute it within this skill.
- A command needs credentials, network/external effects, destructive behavior, unsafe changes, or missing testing
  authority without exact approval and the governing command/testing contract.

Any stop reached after the fix loop has begun still performs step 15 before returning; step 15's own safety and
authority checks decide whether that evidence is written durably or returned in the response instead.

## Output

Return a concise diagnosis, Fix Authorization consumed, changed files, verification/review, delivery/cleanup,
risks, and next boundary. On a stop after the fix loop began, also report the preserved repro/diagnosis paths, or
the returned diagnosis and the reason the durable write was skipped.
Include the internal receipt only on request or to explain audit/debug/drift/blockers.
