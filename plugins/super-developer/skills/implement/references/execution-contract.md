# Execution Contract

## Boundary

This reference owns planned-feature execution authorization. It separates an expanded machine contract used by the
orchestrator from the short summary shown to the user by default. It grants no authority by itself.

## Authorization Rules

- Derive every field from accepted reviewed artifacts, safe Slice projections, resolved testing authority, current
  git/worktree state, and explicit user instructions. Approval covers only actions and bounded authority envelopes
  visibly described in the user summary; unshown machine detail cannot grant additional authority.
- Plan approval and execution approval are separate decisions. They may share one presentation only when both scopes
  are ready, explicit, complete, independently labeled, and independently selectable. Never infer execution or
  publication from accepted artifacts, a prior push, or `auto-resolve` wording.
- `approve auto-resolve` runs all and only listed actions until a stop. `step-by-step` asks before each listed package
  wave, repair loop, external effect, and final handoff. Neither mode expands the contract.
- Consume the parent-supplied source-publication contract before selecting feature-source policy. Use `local-only`
  absent explicit remote authorization; otherwise require the user's `per-package`, precise `milestone`, or `final`
  selection. Never choose a remote cadence for the user.
- Source, target, and sidecar publication are independent. Planned hotfix publication is one separately authorized
  exact `hotfix/<name>` gate and creates no feature ref.
- Target merge/push, force, tags/releases, remote deletion, local ref deletion outside exact probe/final cleanup,
  destructive action, service/dependency side effects, and credentialed/external effects require explicit listing.
- Consume the parent-supplied plan-amendments contract before classifying or applying a proposed amendment. The
  execution contract may cover its exact nonsemantic procedure; obligations, commands/evidence, risk, acceptance,
  scope, dependencies, or approval changes still require planning continuation and focused review.
- Consume the parent-supplied bounded-attempts contract before any attempt or stop report. Authorization covers only
  materially changed in-scope attempts and its exact stops; it never creates extra attempts or authority.

## Expanded Machine Contract

Construct and retain this complete record in the current orchestration context. Do not create another ledger or dump
it into the user-facing prompt. Tell the user it is available and render all or any requested section before approval.
If context cannot reliably retain it across handoff, pass the complete record in the existing orchestrator packet.

Record:

1. **Identity/state:** feature, accepted plan/review provenance, delivery context, artifact/code/project roots, base,
   integration, artifact, package, target refs, exact current SHAs, and fixed worktree paths.
2. **Packages:** each package path/report/Slices, assigned obligations, primary write paths, dependencies, approved
   dependency changes, Acceptance items, blockers/deferrals, and existing Notes path.
3. **Verification depth:** `standard` or `enhanced` plus concrete reason per package. Persist it in existing package
   Notes before dispatch; no registry field. A later change records prior/new depth and reason only after the governing
   approved risk delta, and never silently downgrades.
4. **Commands/checks:** known exact commands plus any explicitly approved bounded command families, their trusted
   source (frozen Acceptance/current testing authority), cwd, budgets, completion, termination/cleanup, allowed
   writes, evidence destinations, and stages. Before execution bind each concrete command with no unresolved
   placeholders. Same-requirement follow-ups must satisfy both this visible envelope and testing authority;
   arbitrary shell, new external effects, or broadened verification do not inherit permission.
5. **Writes:** known exact paths plus visibly approved path/ref patterns under named roots for same-requirement
   continuation, local probes, evidence, and mechanical amendments. Bind exact destinations before writing and
   preserve existing user state. A pattern is not permission to expand product scope or edit unrelated files.
6. **Dynamic worktree envelope:** exact namespace/path/ref patterns, allowed base refs and caller-supplied base SHAs,
   focused-reviewed continuation package IDs/base/prerequisite SHAs, receipt manifests, forbidden operations, and
   cleanup proofs. Probe authority is local-only: no stage/commit/merge/push/reset/stash/clean/force/network.
7. **Attempts/continuation:** logical IDs, prior outcomes, current ordinals, corrected packet or changed
   method/signal/code delta, accepted empirical report set or `none`, and shared-contract escalation state.
8. **Publication:** selected feature-source policy, exact `origin` destination/command, precise milestone triggers
   when applicable, final catch-up for remote cadences, and remote-SHA success check; or `local-only` without network.
   Separately record exact hotfix, sidecar, and target actions or `excluded` for each.
9. **Safety/exclusions:** root-worktree prohibition, external/destructive boundaries, dependency/service restrictions,
   cleanup retention, Semgrep/network constraints, manual exceptions, and every action not authorized.
10. **Stops:** new semantic/risk/manual authority, missing facts/credentials, unsafe or unowned state, missing command
    bounds, scheduled publication failure/SHA mismatch, and shared bounded-attempt exhaustion.

A probe receipt additionally binds full direct ref, expected base SHA before/after creation, clean HEAD/index/status,
non-writing index digest, exact NUL owned tracked/untracked/ignored/symlink/process/data manifests,
`remote_action=none`, and exact cleanup proof. A continuation package binds `BASE_KIND`, exact `BASE_REF`,
`REVIEWED_BASE_SHA`, and prerequisite ref/SHAs; create it only from that reviewed state.

## Short User-Facing Summary

Present this by default. Use concrete feature roots, outcomes, and boundaries. Known commands can be consolidated
by cadence; future in-scope work must have an explicitly described bounded class/pattern, never an unexplained
placeholder. Bind exact command/path values before acting. List external commands/destinations exactly; never hide
an external effect in prose such as “normal git steps.”

```text
Execution approval — <feature> (plan already approved separately: <plan/review pointer>)
Changes:
- <package IDs: concrete behavior and exact primary write paths>
Actions:
- local writes/worktrees: <known paths/refs + bounded continuation/probe patterns and cleanup limits, or none>
- commands: <known commands; permitted follow-up families with trusted source, cwd, write/resource limits, and cadence>
- checks: <Acceptance/test/build/review-code/audit checks and expected pass signal>
External effects:
- feature source: <local-only | cadence + exact origin/ref/command + milestone triggers + final catch-up>
- sidecar: <excluded | exact command/ref/gate>
- target/hotfix/other: <excluded | exact separately authorized action>
Stops:
- <concise exact semantic/safety/facts/attempt/publication stop boundaries>
Not authorized: <target/force/release/delete/service/dependency/cleanup exclusions>
Expanded machine contract: available before approval on request.
Choose: approve auto-resolve | step-by-step | abort
```

If no remote publication was explicitly requested, the exact source line is `feature source: local-only; no fetch,
ls-remote, or push`. A summary that omits an action or its bounded class, write scope, external effect, or material
stop does not authorize it. A concrete continuation path or command need not have been enumerated initially when it is proven to fit a
visibly approved envelope; record its binding before the action, without another approval. A package's
`standard`/`enhanced` reason may be compacted into the package bullet but must remain in the machine
contract and package Notes.

## Post-Approval Rules

1. Record the selected choice in the current orchestration handoff; do not re-prompt for listed in-contract actions.
2. Before each action, bind exact commands/paths/refs and validate current state against both the visible authority
   envelope and retained machine contract. In-envelope same-requirement bindings proceed autonomously; anything
   outside them stops or follows its owning decision route. Detailed machine state never widens permission.
3. Preserve a local package recovery commit/ref after each accepted package regardless of source cadence. Non-due or
   local-only publication performs no network action and does not block local integration/downstream readiness.
4. At a due remote gate, use the loaded source-publication command and close the gate only after successful post-push
   verification that remote SHA equals integration `HEAD`. Any network/credential/push/SHA failure stops progression
   with all local safety nets retained.
5. Keep expanded details available in status/handoff context and disclose any requested section. Do not make approval
   depend on the user reading an unsolicited machine-contract dump.

## Stop if

- A summary boundary cannot be derived safely, execution feasibility remains unresolved, or plan and execution
  approval cannot be distinguished. An unresolved concrete binding stops that action, not initial authorization
  of an otherwise precise dynamic envelope.
- Remote publication lacks explicit authorization or a user-selected cadence; a milestone trigger is ambiguous;
  or a final/catch-up push lacks sibling same-freeze `review-code` CLEAN and `audit` PASS.
- An action, concrete command/write, dependency/service effect, cleanup, or publication is not covered by the
  visible approved scope/envelope and its action-time machine binding.
- Testing depth, package/Slice scope, delivery context, or authority is ambiguous enough to affect execution.

## Output

Return the short summary, selected choice, plan-versus-execution authorization state, expanded-contract availability,
testing provenance, package depth/reasons, covered/excluded effects, publication policy, and unresolved fields.
