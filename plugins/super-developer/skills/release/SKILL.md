---
name: release
description: >
  Prepare and publish a project release on demand after development is complete. Use when the user
  asks to prepare a release, publish a release, bump a version, tag a release, create GitHub release
  notes, ship completed work, or clean up release worktrees/feature branches.
---

# Release: Prepare and Publish

Create a release with explicit approval before durable or external side effects. Keep this workflow concise and state-aware.

## Arguments

- `$ARGUMENTS` — Optional version, release type (`patch`, `minor`, `major`), feature branch/name, or `prepare-only` / `publish`.

## Rules

- Do not push, tag, publish a GitHub release, merge branches, or delete branches/worktrees without explicit approval at the matching gate.
- Detect the base branch: use the current branch if it is `main` or `master`; otherwise use `origin/HEAD` only if it resolves to `main` or `master`; otherwise use the only local `main`/`master`; if ambiguous, ask.
- Use `--no-ff` when merging a feature branch into the base branch.
- Clean up only exact release-related branches/worktrees named by the user or observed during this release. Never delete unrelated branches/worktrees or sweep by namespace.
- If the workflow is already partially complete, resume from the observed state instead of repeating completed side effects.

## Step 1: Preflight

Inspect and report:

- Base branch (`main` or `master`) and upstream state.
- Current working tree cleanliness.
- Current version source(s) and latest `vX.Y.Z` tag.
- Whether a feature branch is already merged into the base branch.
- Whether `CHANGELOG.md` exists.
- Whether GitHub CLI release operations are available when publishing is requested.

Block and ask before proceeding if the base branch is behind/diverged, version sources disagree, the working tree has unrelated changes, or the release target is ambiguous.

## Gate 1: Release Plan Approval

Present the proposed plan:

- Base branch and feature branch, if any.
- Proposed version and bump reason.
- Changelog action.
- README/docs action.
- Local release checks to run.
- Publish actions, if requested.
- Cleanup candidates, if any.

Ask for approval before editing files or merging.

## Step 2: Prepare Local Release

1. Merge the approved feature branch into the detected base branch with `--no-ff` only if it is not already merged.
2. If `CHANGELOG.md` exists, update it using Keep a Changelog style with human-friendly entries. If missing, ask whether to create it or skip it; recommend skipping unless the user wants a durable changelog convention.
3. Update README/docs only when the release changes user-visible behavior or the docs are stale. If no docs update is needed, leave them unchanged and say so.
4. Bump all authoritative project version sources. If multiple version files are present, keep them consistent.
5. Draft GitHub release notes in simple human language.
6. Run relevant release checks that are documented or discoverable for the project; do not invent expensive checks.

## Gate 2: Release Commit Approval

Show the diff summary, version, checks run, changelog/docs decision, and release-note draft. Ask before committing release-prep changes.

If approved, commit with `release: vX.Y.Z` unless the repo convention clearly differs.

## Gate 3: Publish Approval

Before external side effects, revalidate that:

- Base branch is clean.
- Base branch includes the release commit.
- Tag `vX.Y.Z` does not already exist locally or remotely, unless resuming an existing release.
- Release notes match the final diff.

Ask explicit approval to push the base branch, create/push the annotated tag, and create/publish the GitHub release. Approval to prepare a release is not approval to publish it.

## Step 3: Publish

After Gate 3 approval:

1. Push the base branch to its upstream.
2. Create annotated tag `vX.Y.Z` if it does not already exist.
3. Push the tag.
4. Create the GitHub release for `vX.Y.Z` with the approved notes.
5. Report the release URL.

If any publish step fails, stop, report the exact completed side effects, and do not clean up automatically.

## Gate 4: Cleanup Approval

After a successful publish, list only exact cleanup candidates tied to this release:
- Feature branch named by the user or observed during this release, if merged into the base branch.
- Other release branches/worktrees only when they were explicitly named or observed in this release.

Verify each branch with `git merge-base --is-ancestor` before proposing deletion. Ask before removing exact worktrees or deleting exact branches. If verification fails, skip that cleanup item and report what remains.

## Step 4: Final Report

Report:

- Published version and URL, or prepared-but-unpublished state.
- Base branch and commit SHA.
- Tag status.
- Cleanup performed or intentionally skipped.
- Any remaining manual follow-up.
