# Release Contract

Owns initial release approval and the optional later portable-evidence decision.

## Initial Contract Rules

- Present before every release side effect; skip its prompt only when the current turn unambiguously approves every
  listed action and target.
- List each edit, check, merge, commit, push, sync check, publish action, feature deletion, and local cleanup as an
  exact boundary. Merge never implies push, tag, GitHub release, deletion, or cleanup.
- Keep checks to commands; list changelog/docs/version edits as planned changes.
- Before planned-feature approval, require fresh successful read-only `validate-agentic-completion` on exact fetched
  artifact/code state. `V` is index-only: list only path/digest/bound `F`, never request a verdict or treat it as proof.
- Bind artifact and code endpoints separately per owning root/ref; unchanged endpoint checks and reads cannot cross.
  Record every final Lifecycle/`F`/`V` checkpoint ref/SHA and retain/defer portable evidence cleanup.
- Initial approval never authorizes portable-evidence deletion. It cannot inherit that authority from Sidecar
  Portability Authorization, Implementation auto-resolve, merge/push, tag/release, or ordinary cleanup.
- `prepare-only` integrates with `--no-ff`, updates `Unreleased`, and pushes base, but never bumps versions,
  creates/pushes/moves tags, or creates/updates a GitHub release.
- Eligible local code/worktree and remote feature-branch cleanup may remain default exact cleanup after target sync.
  Portable sidecar/checkpoint refs are not ordinary cleanup candidates.
- State change, missing format choice, or a new action requires a revised contract.

## Initial Release Contract Template

```md
## Release Contract Approval Required

Mode: publish | prepare-only
Repository/target endpoint: <repository and exact target push endpoint>
Base branch: <base>
Feature branch: <feature branch or none>

Version action:
- prepare-only: no version bump, tag, or GitHub release
- publish: vX.Y.Z because <patch/minor/major reason>

Planned file changes:
- Changelog: <Unreleased/versioned action, format choice, note plan>
- README/docs: <exact paths or none>
- Version files: <publish-only exact paths or none>

Release checks:
- <validation command or documented check>

Planned-feature final evidence:
- Status: <fresh validator success | standalone/no planned-feature claim>
- Completion validation: <exact read-only command, successful result, exact fetched artifact/code state>
- Index-only V: <path, digest, bound F; no verdict; or not applicable>
- Artifact authority: <artifact root + unchanged artifact endpoint + sidecar full ref/SHA>
- Code authority: <each code root + unchanged code endpoint + required full checkpoint ref/SHA>
- Endpoint isolation: <sidecar queried/fetched only at artifact endpoint; each checkpoint only at owning code endpoint>
- Freshness: <when endpoints/refs were rechecked and validation repeated; any state-change trigger>
- Disposition: retain through and after release; portable-evidence cleanup deferred and not authorized here

Merge and commit:
- Merge <feature> into <base> with --no-ff unless already included
- Worktree: <exact existing or temporary base worktree>
- Commit: <exact prepare message | release: vX.Y.Z>

Independent release action boundaries:
- Target merge: <exact action>
- Target push: <push base to exact endpoint>
- Post-push sync: <fetch and prove local base, origin/base, and intended commit equal>
- Tag: <publish-only exact annotated tag creation/push | none>
- GitHub release: <publish-only exact repository/tag action | none>
- Remote feature deletion: <exact refs/heads/<feature> and expected SHA after fresh inclusion proof | keep/none>
- Portable evidence deletion: none; retain exact sidecar/checkpoint refs above

Independent local cleanup boundary:
- Code worktrees: <exact clean paths to remove after inclusion | keep/none>
- Feature branch: <exact local branch to delete after inclusion | keep/none>
- Evidence worktree/refs: retain; any cleanup is deferred to a separate evidence decision

Resume state: <none or exact matching commit/tag/release/cleanup state>
Stop conditions: <specific blockers, including evidence mismatch>

Approve this Release Contract? Reply: approve | reject
```

## Changelog Format Choice

For an incompatible, ambiguous, or absent latest format, choose: adopt lightweight for this section, preserve the
existing format, or skip. Never rewrite history unless the contract names it.

## Portable Evidence Retention/Cleanup Decision

This is not part of initial Release Contract approval. Present it only after (1) the user explicitly requested
portable-evidence cleanup, (2) target/base local and remote SHAs are exact after fresh sync, and (3) for `publish`,
the tag target and GitHub release state are exact. Otherwise retain and report evidence without prompting.

```md
## Portable Evidence Retention/Cleanup Decision Required

Verified final release state:
- Target/base: <endpoint, ref, local SHA, remote SHA, intended SHA>
- Publish state: <tag/ref/peeled SHA and GitHub release identity, or prepare-only/not applicable>

Protected evidence inventory:
- Index-only V: <path/digest, bound F, artifact endpoint + sidecar ref/SHA; no verdict>
- Required objects: <each owning code endpoint + Lifecycle/F/V-required ref/SHA and resolution result>
- Fresh completion validation: <successful repeated read-only command over preserved exact roots/state>

Choose one:
- retain (recommended): keep every remote sidecar/checkpoint ref through and after release
- delete only listed evidence after verified equivalent preservation

Delete choice, if selected:
- Equivalent durable preservation: <exact retained immutable location(s) proving V and every required object resolve>
- Remote deletions: <every exact push endpoint + full ref + freshly observed expected SHA; no wildcard/namespace>
- Local evidence actions: <every exact clean worktree path and direct ref/SHA to remove, or none>
- Pre-delete checks: <fresh owning endpoint/ref/SHA, endpoint-unchanged assertion, preservation, validation>
- Post-delete checks: <endpoint-isolated absence checks plus repeated completion validation of preserved state>
- Excluded: target action, tag/release change, remote feature deletion, force rewrite, namespace sweep,
  implicit deletion
- Stop: any changed/missing/mismatched state or failed action retains remaining safety refs and is reported

Approve this separate decision? Reply: retain | approve exact deletion | reject
```

Deletion is forbidden without independent preservation or when final `V` or a required object would become
unresolvable. Approval covers only listed endpoint/ref/SHA and local actions; it never expands by inference.

## Ordinary Feature Cleanup

Remote feature deletion remains separate: freshly verify expected SHA and remote-base inclusion, delete only that
ref, then verify absence. Local code cleanup requires clean exact worktrees and ancestry. Any failed check keeps the
candidate and stops cleanup; never force or sweep.
