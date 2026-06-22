# Release Contract

Owns the one approval packet for a release attempt. Load before the first release side effect.

## Contract Rules

- Present the contract every time. Skip only the approval prompt when the current turn already
  unambiguously approves the full listed lifecycle.
- The contract must list every side effect: file edits, merge, commits, base push, post-push base
  sync verification, tag creation/push, GitHub release, and local/remote cleanup.
- Keep release checks to validation commands. List changelog, docs, and version edits as planned file changes, not checks.
- If state changes, changelog format choice is missing, or a new action is needed, stop for a revised contract.
- Remote feature branch deletion requires the exact `origin/<branch>` ref to be listed in the contract and approved with the contract.
- `prepare-only` integrates the feature into the base branch, updates `Unreleased`, pushes the base branch,
  and cleans up exact feature refs/worktrees after verification.
- `prepare-only` never bumps versions, creates/pushes/moves tags, or creates/updates a GitHub release.
- Local and remote cleanup requires the target/base push to be complete; otherwise keep the safety-net refs/worktrees.

## Required Fields

Use this structure, adapted to observed repository state:

```md
## Release Contract Approval Required

Mode: publish | prepare-only

Base branch:
- <base-branch>

Feature branch:
- <feature-branch or none>

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
- Worktree: <existing base worktree or exact temporary target-merge worktree>
- Commit: <prepare-only integration/changelog commit message or publish release commit `release: vX.Y.Z`>
- Annotated tag: vX.Y.Z if publishing; none in prepare-only

Remote actions:
- Push <base-branch> to origin after merge/checks
- Post-push sync verification: fetch remote refs, then verify local <base-branch>,
  origin/<base-branch>, and the intended commit all match; stop on mismatch without force-reset or
  root branch switching
- Push tag vX.Y.Z to origin, if publishing
- Create GitHub release for vX.Y.Z, if publishing
- Delete remote feature branch: <origin/<feature-branch> after pushed-base inclusion verification, or none>

Resume state:
- Existing prepare/release commit, tag, or GitHub release: <none or exact matching state>

Cleanup candidates:
- Delete local feature branch: <feature-branch or none>
- Delete remote feature branch: <origin/<feature-branch> or none>
- Remove local worktree(s): <exact paths or none>

Stop conditions:
- <specific blocker>
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

When a remote feature branch exists and cleanup is desired by normal release/prepare flow:

```md
Remote feature branch cleanup:
- Delete `origin/<feature-branch>` after `<base-branch>` is pushed and fresh remote inclusion verification passes.
- If verification fails, keep `origin/<feature-branch>` and stop cleanup.
```

If the user explicitly asks to keep the remote feature branch, list it as intentionally skipped:

```md
Remote feature branch cleanup:
- Keep `origin/<feature-branch>` by explicit user request.
```

If no remote feature branch exists:

```md
Remote feature branch cleanup:
- No remote feature branch candidate found.
```
