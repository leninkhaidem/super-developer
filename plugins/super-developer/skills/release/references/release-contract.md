# Release Contract

Owns the one approval packet for a release attempt. Load before the first release side effect.

## Contract Rules

- Present the contract every time. Skip only the approval prompt when the current turn already
  unambiguously approves the full listed lifecycle.
- The contract must list every side effect: file edits, merge, commits, canonical primary-checkout normalization
  and fast-forward synchronization, base push, post-push server/origin verification, tag creation/push, GitHub
  release, artifact-sidecar actions, and local/remote cleanup.
- Keep release checks to validation commands. List changelog, docs, and version edits as planned file changes, not checks.
- If state changes, changelog format choice is missing, or a new action is needed, stop for a revised contract.
- Remote feature or sidecar branch deletion requires the exact `origin/<branch>` ref to be listed
  in the contract; approving that contract approves the listed deletion.
- `prepare-only` integrates the feature into the base branch, updates `Unreleased`, pushes the base branch,
  and deletes/removes exact eligible feature refs/worktrees and artifact sidecar candidates after verification.
- `prepare-only` never bumps versions, creates/pushes/moves tags, or creates/updates a GitHub release.
- Local, remote, and sidecar cleanup require the target/base push to be complete; otherwise keep the safety-net refs/worktrees.
- Default cleanup is delete/remove. List `keep` only for a hard blocker or explicit user keep request.
- Sidecar cleanup is separate from deliverable feature cleanup but defaults to exact
  removal/deletion when eligible; never merge `artifacts/<feature>` into the base branch.
- Bind the canonical root branch, HEAD, clean status, and local-base SHA-or-empty before side effects. Require the
  local base to equal or be an ancestor of fresh remote base, and preflight occupied-base blockers.
  Immediately before the one base push, revalidate the binding, normalize root to the base branch if needed, and
  fast-forward only to exact `RESULT_SHA`; never reset, force-update, stash, clean, merge divergent history, or
  overwrite ignored, untracked, or tracked user files.

## Required Fields

Use this structure, adapted to observed repository state:

```md
## Release Contract Approval Required

Mode: publish | prepare-only

Base branch:
- <base-branch>; target `refs/heads/<base>`; fresh remote-base SHA <full SHA>
- Local base: <equal | ancestor to be fast-forwarded to RESULT_SHA before publication | no local ref>

Canonical primary checkout:
- Root path: <canonical primary root>
- Preflight binding: branch <branch>; HEAD <full SHA>; status <clean>; base occupied elsewhere <yes/no>
- Synchronizability: <already on clean base | safe normalization to base>; local base is equal/ancestor; no
  occupied-branch or non-fast-forward blocker
- Pre-push action: revalidate root/status/ref/occupancy; normalize to <base> if needed with no ignored-file
  overwrite; merge --ff-only exact RESULT_SHA; permit no other tracked root mutation

Feature branch:
- <feature-branch or none>

Default cleanup policy:
- Delete/remove all eligible exact feature branch/worktree and artifact sidecar candidates after post-push sync.
- Keep only: <hard blockers or explicit user keep request; otherwise none>

Version action:
- prepare-only: no version bump, no tag, no GitHub release
- publish: vX.Y.Z
- Reason: <patch/minor/major reason, publish only>

Planned file changes:
- Changelog: <prepare-only: update/create [Unreleased]; publish: move [Unreleased]/release diff into vX.Y.Z;
  latest-format compatibility; format choice; grouping/classification style; human-readable note plan>
- README/docs: <update/skip and why>
- Version files: <publish exact files to update; prepare-only none>

Release checks to run:
- <validation command or documented check>
- <validation command or documented check>

Merge/release strategy:
- Merge <feature-branch> into <base-branch> with --no-ff, unless already merged
- Worktree: <existing exact non-root base checkout | named temporary integration ref/path
  created from the fresh remote-base SHA because the local base is locked/unavailable>
- Commit: <prepare-only integration/changelog commit message or publish release commit `release: vX.Y.Z`>
- Annotated tag: vX.Y.Z if publishing; none in prepare-only

Remote actions:
- Before publication, synchronize canonical root HEAD and local base to exact result, then re-prove the server's
  expected SHA and its ancestry to result
- Push exact result SHA to `refs/heads/<base>` exactly once, using the qualified exact lease bound to the fresh
  pre-target SHA
- Post-push: fetch, then verify clean root HEAD, local base, `origin/<base>`, and fresh server base all equal result
- Push tag vX.Y.Z to origin, if publishing
- Create GitHub release for vX.Y.Z, if publishing
- Delete remote feature branch: <origin/<feature-branch> after pushed-base inclusion verification, or keep because ... / no candidate found>
- Delete remote artifact sidecar: <origin/artifacts/<feature> after exact contract listing and target push sync, or keep because ... / no candidate found>

Resume state:
- Existing prepare/release commit, tag, or GitHub release: <none or exact matching state>

Artifact sidecar:
- Ref/worktree: <artifacts/<feature> at .worktrees/<feature>/artifacts, or none>
- Final checkpoint: <pushed to origin artifacts/<feature> before target merge, not applicable, or blocker>
- Cleanup disposition: <default remove local worktree | delete local ref | delete remote ref | keep because ...; exact list>

Cleanup candidates:
- Delete local feature branch: <feature-branch by default after ancestry proof, or keep because ...>
- Delete remote feature branch: <origin/<feature-branch> by default after remote inclusion proof, or keep because ...>
- Remove local code worktree(s): <exact clean paths by default, or keep because ...>
- Remove temporary integration ref/worktree last: <exact names, or not applicable; retain on any failure>
- Remove local artifact worktree: <.worktrees/<feature>/artifacts by default when clean, or keep because ...>
- Delete local artifact ref: <artifacts/<feature> by default, or keep because ...>
- Delete remote artifact ref: <origin/artifacts/<feature> by default after fresh remote verification, or keep because ...>

Stop conditions:
- Root is dirty or changed from its binding; base is occupied elsewhere when normalization is needed; local base or
  root cannot fast-forward to exact `RESULT_SHA`
- A pre-push failure stops publication: report partial local effects and retain every safety net
- A push failure stops immediately: report partial local/remote effects and retain every safety net
- A post-push failure stops cleanup: report partial published/verified effects and retain every safety net
- <specific blocker>

Approve this Release Contract? Reply with one:
- approve
- reject
```

## Changelog Format Choice

When the latest released changelog section does not already use the proposed lightweight format, include one choice in the contract:

```md
Changelog format decision:
- Latest release format: <compatible | incompatible | ambiguous | no changelog>
- Proposed action: adopt lightweight format for this prepare/release section | preserve existing format for this prepare/release | skip changelog update
```

If the lightweight format is chosen, use it for the current `Unreleased` or versioned section.
Do not rewrite historical release sections unless the contract explicitly names that migration.

## Remote Cleanup Rules

When a remote feature branch exists and is not hard-blocked or explicitly kept:

```md
Remote feature branch cleanup:
- Delete `origin/<feature-branch>` after `<base-branch>` is pushed and fresh remote inclusion verification passes.
- If verification fails, keep `origin/<feature-branch>` and stop cleanup.
```

If the user explicitly asks to keep the remote feature branch or a hard blocker prevents deletion, list it as intentionally skipped:

```md
Remote feature branch cleanup:
- Keep `origin/<feature-branch>` because <explicit user request | named blocker>.
```

If no remote feature branch exists:

```md
Remote feature branch cleanup:
- No remote feature branch candidate found.
```

## Artifact Sidecar Cleanup Rules

Default sidecar cleanup runs only after the target/base push and sync verification complete:

```md
Artifact sidecar cleanup:
- Remove local artifact worktree `.worktrees/<feature>/artifacts`: <default delete | keep because ...>
- Delete local sidecar branch `artifacts/<feature>`: <default delete | keep because ...>
- Delete remote sidecar branch `origin/artifacts/<feature>`: <default delete | keep because ...>
```

List a sidecar action as kept only for an explicit user keep request or hard blocker. If contracted
cleanup fails, stop and report the remaining blocker instead of leaving the sidecar silently stale.
