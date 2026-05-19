---
name: release
description: >
  Prepare and publish a project release on demand after development is complete. Use when the user
  asks to prepare a release, publish a release, bump a version, tag a release, create GitHub release
  notes, ship completed work, or clean up release worktrees/feature branches.
---

# Release: Prepare and Publish

Create a release through one explicit Release Contract. Keep this workflow concise and state-aware.

## Arguments

- `$ARGUMENTS` — Optional version, release type (`patch`, `minor`, `major`), feature branch/name, or `prepare-only` / `publish`.

## Rules

- Use one approval gate per release attempt: **Release Contract Approval**. The approved contract covers every listed release side effect end-to-end: file edits, feature merge, release commit, branch push, tag creation/push, GitHub release publication, and exact cleanup candidates.
- Interpret an explicit current-turn request such as "create the release", "publish the release", or "ship vX.Y.Z" as approval for the normal full lifecycle only when version, base branch, feature branch, repository, and publish target are unambiguous. Still state the exact Release Contract before the first side effect. Stop if any blocker, ambiguity, or uncontracted action appears.
- For `prepare-only`, the contract covers only local release preparation and optional branch push. It does not imply tag or GitHub release publication, and it must not delete a remote feature branch.
- Do not ask for staged re-approvals after an approved contract. Report checkpoints as status updates, not gates.
- Stop and ask only when observed state invalidates the contract or requires a new action not listed in it: base branch behind/diverged, unrelated dirty files, version-source disagreement, merge conflict, failing release checks, existing local/remote tag, missing credentials, changed publish target, destructive cleanup not named in the contract, or a new dependency/service/external side effect.
- Detect the base branch: use the current branch if it is `main` or `master`; otherwise use `origin/HEAD` only if it resolves to `main` or `master`; otherwise use the only local `main`/`master`; if ambiguous, ask.
- Use `--no-ff` when merging a feature branch into the base branch.
- Clean up only exact release-related branches, remote refs, and worktrees named in the approved Release Contract and verified as merged. Never delete unrelated branches/worktrees or sweep by namespace.
- Remote feature branch deletion is a separate opt-in cleanup decision. Offer the visible approve/delete vs keep call to action only in `publish` mode when a remote feature branch candidate exists. Default to keeping the remote branch unless the user explicitly approves deleting the exact remote ref. In `prepare-only`, state that remote feature branch deletion is not available in that contract.
- If the workflow is already partially complete, resume from the observed state instead of repeating completed side effects.

## Step 1: Preflight

Inspect and report:

- Base branch (`main` or `master`) and upstream state.
- Current working tree cleanliness.
- Current version source(s) and latest `vX.Y.Z` tag.
- Whether a feature branch is already merged into the base branch.
- Whether `CHANGELOG.md` exists.
- Whether GitHub CLI release operations are available when publishing is requested.

Block before the Release Contract if the base branch is behind/diverged, version sources disagree, the working tree has unrelated changes, or the release target is ambiguous.

## Step 2: Release Contract Approval

Present one compact contract before the first release side effect unless the current user request already unambiguously approves the full lifecycle. The contract must list:

- Mode: `prepare-only` or `publish`.
- Base branch and feature branch, if any.
- Proposed version and bump reason.
- Changelog action.
- README/docs action.
- Version files to update.
- Local release checks to run.
- Merge strategy and expected release commit message.
- Remote actions: branch push, annotated tag creation/push, and GitHub release publication.
- Exact cleanup candidates, if any.
- Remote feature branch cleanup policy: publish-mode approve/delete vs keep call to action, prepare-only keep notice, or no-candidate notice.
- Stop conditions specific to this release.

Keep release checks limited to validation commands. Do not hide changelog, docs, or version-file edits under release checks; list them as planned file changes.

Use this structure, adapting details to the observed repository state:

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
- Changelog: <update/create/skip and why>
- README/docs: <update/skip and why>
- Version files: <exact files to update>

Release checks to run:
- <validation command or documented check>
- <validation command or documented check>

Merge/release strategy:
- Merge <feature-branch> into <base-branch> with --no-ff, unless already merged
- Release commit: release: vX.Y.Z
- Annotated tag: vX.Y.Z

Remote actions:
- Push <base-branch> to origin, if publishing
- Push tag vX.Y.Z to origin, if publishing
- Create GitHub release for vX.Y.Z, if publishing

Cleanup candidates:
- Delete local feature branch: <feature-branch>, after merge verification
- Remove release/merge worktree: <path>, if created

Remote feature branch cleanup:
- <Use exactly one block: publish-mode CTA, prepare-only keep notice, or no-candidate notice.>

Stop conditions:
- <specific blocker>
- <specific blocker>

Approve this Release Contract? Reply with:
- <matching approval choices for the selected remote cleanup block>
```

For `publish` mode when a remote feature branch exists, use this visible cleanup call to action and approval choices:

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

For `prepare-only`, replace the remote cleanup block with: `Remote feature branch cleanup: not offered in prepare-only; keep origin/<feature-branch> until a later publish/cleanup contract verifies it is merged into the pushed base branch.` Replace approval choices with `approve` / `reject`.

If no remote feature branch exists, replace the remote cleanup block with: `Remote feature branch cleanup: no remote feature branch candidate found.` Replace approval choices with `approve` / `reject`.

If the user has not already approved the full contract in the current request, ask once. After approval, execute the contract without further approval prompts unless a stop condition occurs.

## Step 3: Execute Release Contract

1. Merge the contracted feature branch into the detected base branch with `--no-ff` only if it is not already merged.
2. If `CHANGELOG.md` exists, update it using Keep a Changelog style with human-friendly entries. If missing, follow the contracted changelog action; default to skipping creation unless the contract explicitly creates a durable changelog convention.
3. Update README/docs only when the release changes user-visible behavior or the docs are stale. If no docs update is needed, leave them unchanged and say so.
4. Bump all authoritative project version sources. If multiple version files are present, keep them consistent.
5. Draft GitHub release notes in simple human language.
6. Run relevant release checks that are documented or discoverable for the project; do not invent expensive checks.
7. Commit release-prep changes with `release: vX.Y.Z` unless the repo convention clearly differs.
8. Before publishing, revalidate that the base branch is clean, includes the release commit, the tag does not already exist locally or remotely unless resuming, and release notes match the final diff.
9. For `publish` mode, push the base branch to its upstream.
10. For `publish` mode, create annotated tag `vX.Y.Z` if it does not already exist, then push the tag.
11. For `publish` mode, create the GitHub release for `vX.Y.Z` with the contracted notes and report the release URL.
12. Clean up only exact contracted cleanup candidates after verifying each branch with `git merge-base --is-ancestor`. Delete an exact remote feature branch only in `publish` mode when the approved contract chose `approve + delete remote branch`, after the base branch push has succeeded and `git merge-base --is-ancestor origin/<feature-branch> origin/<base-branch>` proves the remote feature branch is included in the pushed base branch. Use the exact remote ref named in the contract. Never delete a remote feature branch in `prepare-only`.

If any publish step fails, stop, report the exact completed side effects, and do not clean up automatically.

## Step 4: Final Report

Report:

- Published version and URL, or prepared-but-unpublished state.
- Base branch and commit SHA.
- Tag status.
- Cleanup performed or intentionally skipped.
- Any remaining manual follow-up.
