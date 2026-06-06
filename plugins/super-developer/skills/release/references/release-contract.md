# Release Contract

Owns the one approval packet for a release attempt. Load before the first release side effect.

## Contract Rules

- Present the contract every time. Skip only the approval prompt when the current turn already unambiguously approves the full listed lifecycle.
- The contract must list every side effect: file edits, merge, release commit, branch push, tag creation/push, GitHub release, and cleanup.
- Keep release checks to validation commands. List changelog, docs, and version edits as planned file changes, not checks.
- If state changes, changelog format choice is missing, or a new action is needed, stop for a revised contract.
- Remote feature branch deletion is opt-in and must name the exact `origin/<branch>` ref.
- `prepare-only` can include local preparation and an explicitly listed branch push, but never tag/GitHub release publication or remote branch deletion.
- Local cleanup that deletes the feature branch/worktree requires the target/base push to be complete; otherwise keep the safety-net refs/worktrees.

## Required Fields

Use this structure, adapted to observed repository state:

```md
## Release Contract Approval Required

Mode: publish | prepare-only

Base branch:
- <base-branch>

Feature branch:
- <feature-branch or none>

Proposed version:
- vX.Y.Z
- Reason: <patch/minor/major reason>

Planned file changes:
- Changelog: <update/create/skip; source range; latest-format compatibility; format choice; grouping/classification style; human-readable note plan>
- README/docs: <update/skip and why>
- Version files: <exact files to update>

Release checks to run:
- <validation command or documented check>
- <validation command or documented check>

Merge/release strategy:
- Merge <feature-branch> into <base-branch> with --no-ff, unless already merged
- Worktree: <existing base worktree or exact temporary target-merge worktree>
- Release commit: release: vX.Y.Z
- Annotated tag: vX.Y.Z if publishing; none in prepare-only

Remote actions:
- Push <base-branch> to origin, if publishing or explicitly contracted for prepare-only
- Push tag vX.Y.Z to origin, if publishing
- Create GitHub release for vX.Y.Z, if publishing

Resume state:
- Existing release commit/tag/GitHub release: <none or exact matching state>

Cleanup candidates:
- Delete local feature branch: <feature-branch or none>
- Remove local worktree(s): <exact paths or none>

Remote feature branch cleanup:
- <Use exactly one block below.>

Stop conditions:
- <specific blocker>
- <specific blocker>

Approve this Release Contract? Reply with:
- <matching approval choices for selected cleanup block>
```

## Changelog Format Choice

When the latest released changelog section does not already use the proposed lightweight format, include one choice in the contract:

```md
Changelog format decision:
- Latest release format: <compatible | incompatible | ambiguous | no changelog>
- Proposed action: adopt lightweight format for this release section | preserve existing format for this release | skip changelog update
```

If the lightweight format is chosen, use it for the current release section.
Do not rewrite historical release sections unless the contract explicitly names that migration.

## Remote Cleanup Blocks

For `publish` mode when a remote feature branch exists:

```md
⚠️ Remote feature branch cleanup decision required:
The remote branch `origin/<feature-branch>` will NOT be deleted unless you explicitly approve it.

Choose one:
1. Approve deleting `origin/<feature-branch>` after merge verification against the pushed base branch
2. Keep `origin/<feature-branch>`

Approve this Release Contract? Reply with one:
- approve + delete remote branch
- approve + keep remote branch
- reject
```

For `prepare-only`:

```md
Remote feature branch cleanup: not offered in prepare-only; keep `origin/<feature-branch>` until a later publish/cleanup contract verifies
it is merged into the pushed base branch.

Approve this Release Contract? Reply with one:
- approve
- reject
```

If no remote feature branch exists:

```md
Remote feature branch cleanup: no remote feature branch candidate found.

Approve this Release Contract? Reply with one:
- approve
- reject
```
