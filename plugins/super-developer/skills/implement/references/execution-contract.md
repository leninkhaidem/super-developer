# Execution Contract

## Boundary

Owns planned-feature execution authorization. It separates the retained machine contract from the compact user summary.
This reference grants no authority by itself.

## Authorization Rules

- Derive fields from accepted reviewed artifacts, safe Slice projections, resolved testing authority, current
  git/worktree state, loaded source-publication/plan-amendment/bounded-attempt contracts, and explicit user
  instructions. Approval covers only actions and bounded envelopes visible in the user summary; hidden machine detail
  cannot grant authority.
- Plan approval, execution approval, and publication approval are separate. A single presentation may request multiple
  choices only when each scope is ready, explicit, complete, independently labeled, and independently selectable.
- `approve auto-resolve` runs all and only listed actions until a stop. `step-by-step` asks before each listed package
  wave, repair loop, external effect, and final handoff. Neither mode expands the contract.
- Consume the loaded source-publication packet before selecting feature-source policy. Use `local-only` absent explicit
  remote authorization; otherwise require the user's selected remote cadence and complete final catch-up authorization.
  Same-requirement continuation packages/new IDs remain covered only when they fit the visible envelope.
- Source, target, sidecar, and planned-hotfix publication are independent. Planned hotfix publication is one exact
  `hotfix/<name>` gate and creates no feature ref.
- Target merge/push, force, tags/releases, remote deletion, local ref deletion outside exact probe/final cleanup,
  destructive action, service/dependency side effects, and credentialed/external effects require explicit listing.
- Plan-amendment authority may cover only the shared contract's exact nonsemantic procedure. Changes to obligations,
  commands/evidence, risk, acceptance, scope, dependencies, or approval use planning continuation and focused review.
- Bounded-attempt authority covers only materially changed in-scope attempts and exact stops; it creates no extra
  attempts, retries, or authority.

## Expanded Machine Contract

Construct and retain this record in orchestration context; do not create another ledger or dump it into the prompt.
Tell the user it is available and render requested sections before approval. If context cannot retain it across
handoff, pass it in the existing orchestrator packet.

Record:

1. **Identity/state:** feature, plan/review provenance, delivery context, artifact/code/project roots, base,
   integration, artifact, package, target refs, current SHAs, and fixed worktree paths.
2. **Packages:** package path/report/Slices, obligations, primary writes, dependencies, approved dependency changes,
   Acceptance items, blockers/deferrals, and existing Notes path.
3. **Verification depth:** `standard|enhanced` plus reason per package, persisted in existing Notes; later changes
   name prior/new depth and the approved material risk/scope delta. Never silently downgrade or add registry fields.
4. **Commands/checks:** exact known commands and approved bounded command families with trusted source, cwd, budgets,
   pass/completion signal, termination/cleanup, writes, evidence destinations, and stage. Bind concrete commands before
   execution. Same-requirement follow-ups must fit this visible envelope and testing authority.
5. **Writes:** exact paths and approved path/ref patterns under named roots for same-requirement continuation, local
   probes, evidence, and mechanical amendments. Bind concrete destinations before writing and preserve user state.
6. **Dynamic worktrees:** namespace/path/ref patterns, allowed bases and caller-supplied base SHAs, reviewed
   continuation IDs/base/prerequisite SHAs, receipt manifests, forbidden operations, and cleanup proofs. Probe
   authority is local-only: no stage/commit/merge/push/reset/stash/clean/force/network.
7. **Attempts/continuation:** stable logical IDs, prior outcomes, current ordinals, corrected packet or changed
   method/signal/code delta, accepted empirical report set or `none`, and bounded-attempt escalation state.
8. **Publication:** selected feature-source policy packet, exact `origin` destination/command, milestone triggers when
   applicable, final catch-up for remote cadences, and remote-SHA success check; or `local-only` without network.
   Separately record exact hotfix, sidecar, and target actions or `excluded`.
9. **Safety/exclusions/stops:** root-worktree prohibition, destructive/external/dependency/service limits, cleanup
   retention, Semgrep/network constraints, manual exceptions, unauthorized actions, missing facts/credentials, unsafe
   state, unbound commands, scheduled publication failure/SHA mismatch, and bounded-attempt exhaustion.

Probe receipts additionally bind full direct ref, expected base SHA before/after creation, clean HEAD/index/status,
non-writing index digest, exact NUL owned tracked/untracked/ignored/symlink/process/data manifests,
`remote_action=none`, and cleanup proof. Continuation packages bind `BASE_KIND`, `BASE_REF`, `REVIEWED_BASE_SHA`, and
prerequisite refs/SHAs, and are created only from that reviewed state.

## Short User-Facing Summary

Present this by default. Use concrete roots, refs, outcomes, and boundaries. Consolidate known commands by cadence;
future in-scope work needs a described bounded class/pattern, not an unexplained placeholder. Bind exact values before
action. List external commands/destinations exactly.

```text
Execution approval — <feature> (plan already approved separately: <plan/review pointer>)
Changes:
- <package IDs: concrete behavior and exact primary write paths>
Actions:
- local writes/worktrees: <known paths/refs + bounded continuation/probe patterns and cleanup limits, or none>
- commands: <known commands; permitted follow-up families with trusted source, cwd, write/resource limits, and cadence>
- checks: <Acceptance/test/build/review-code/audit checks and expected pass signal>
External effects:
- feature source: <local-only | cadence + exact origin/ref/command + milestone triggers + final same-freeze catch-up>
- sidecar: <excluded | exact command/ref/gate>
- target/hotfix/other: <excluded | exact separately authorized action>
Stops:
- <concise exact semantic/safety/facts/attempt/publication stop boundaries>
Not authorized: <target/force/release/delete/service/dependency/cleanup exclusions>
Expanded machine contract: available before approval on request.
Choose: approve auto-resolve | step-by-step | abort
```

If no remote publication was explicitly requested, the exact source line is `feature source: local-only; no fetch,
ls-remote, or push`. Omitted actions/classes, write scopes, external effects, or material stops are not authorized. A
concrete continuation path or command may be bound later without new approval only when it provably fits a visible
envelope; record the binding before acting. The `standard|enhanced` reason may be compact in the package bullet but
must remain in the machine contract and package Notes.

## Post-Approval Rules

1. Record the selected choice in current orchestration handoff; do not re-prompt for listed in-contract actions.
2. Before each action, bind exact commands/paths/refs and validate current state against visible authority and the
   retained machine contract. In-envelope same-requirement bindings proceed autonomously; out-of-envelope action stops
   or follows its owning decision route. Machine detail never widens permission.
3. Preserve a local package recovery commit/ref after each accepted package. Non-due or `local-only` source policy runs
   no network action and does not block local integration/downstream readiness.
4. At a due remote source gate, use the loaded source-publication command and close only after post-push remote SHA
   equals integration `HEAD`. Any network/credential/push/SHA failure stops with local safety nets retained.
5. Keep expanded details available in status/handoff context and disclose requested sections. Do not require the user
   to read an unsolicited machine-contract dump for approval.

## Stop if

- A summary boundary cannot be derived safely, execution feasibility remains unresolved, or plan/execution approval
  cannot be distinguished. An unresolved concrete binding stops that action, not an otherwise precise envelope.
- Remote source publication lacks explicit authorization or user-selected cadence; a milestone trigger is ambiguous;
  or final/catch-up push lacks sibling same-freeze `review-code` CLEAN and `audit` PASS.
- Any action, concrete command/write, dependency/service effect, cleanup, or publication is outside the visible
  approved scope/envelope and its action-time binding.
- Testing depth, package/Slice scope, delivery context, or authority is ambiguous enough to affect execution.

## Output

Return the short summary, selected choice, plan-versus-execution state, expanded-contract availability, testing
provenance, package depth/reasons, covered/excluded effects, publication policy, and unresolved fields.
