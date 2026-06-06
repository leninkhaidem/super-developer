---
name: release
description: >
  Prepare and publish a project release on demand after development is complete. Use when the user
  asks to prepare a release, publish a release, bump a version, tag a release, create GitHub release
  notes, ship completed work, or clean up release worktrees/feature branches. Do not use for ordinary
  development, code review, or unrelated branch cleanup.
---

# Release

Prepare or publish a release through one explicit Release Contract, with exact state, side effects, and cleanup candidates named before action.

## Arguments

- `$ARGUMENTS` — Optional version, release type (`patch`, `minor`, `major`), feature branch/name, or mode: `prepare-only` / `publish`.

## Always

- Use one approval gate per release attempt: **Release Contract Approval**.
- Always present the exact Release Contract before the first side effect.
- Skip only the approval prompt when the current turn unambiguously approves the full normal lifecycle and all release targets are known.
- Current-turn approval never implies remote feature-branch deletion unless the exact remote ref deletion was explicitly approved.
- The approved contract covers only listed file edits, feature merge, release commit, pushes, tag, GitHub release, and cleanup candidates.
- `prepare-only` never creates/pushes tags, publishes a GitHub release, or deletes a remote feature branch.
- Do not ask for staged re-approvals after approval; report checkpoints unless observed state invalidates the contract.
- Use `--no-ff` when merging a feature branch into the base branch.
- Never switch the user-owned root worktree to make a release merge or cleanup possible.
- Clean up only exact release branches, remote refs, and worktrees named in the approved contract and proven merged.
- If partially complete, resume only from observed state that matches the intended release commit, tag, remote state, and notes.

## Do

1. Resolve mode, proposed version or bump type, feature branch if any, repository, and publish target.
2. Detect the base branch:
   - use current branch only if it is `main` or `master`;
   - otherwise use `origin/HEAD` only if it resolves to `main` or `master`;
   - otherwise use the only local `main`/`master`; ask if ambiguous.
3. Preflight and report:
   - base branch/upstream freshness and divergence;
   - current working tree cleanliness and unrelated changes;
   - version sources and latest `vX.Y.Z` tag;
   - feature branch merge status and candidate cleanup refs/worktrees;
   - `CHANGELOG.md` presence, most recent release format, and whether the proposed lightweight format needs user choice;
   - GitHub CLI auth/repo/release state when publishing.
4. Load `references/release-git-safety.md` before relying on remote refs, existing tags/releases, feature merge, publish, or cleanup.
5. Stop before contract approval if base is behind/diverged, version sources disagree, working tree has unrelated changes, publish target is ambiguous,
   remote state cannot be verified for publish/delete, or existing tag/release does not match the intended release commit.
6. Load `references/release-contract.md` and present the compact Release Contract, including changelog format choices when needed.
   Ask once unless the current turn already approved the full contract.
7. After approval, execute only contracted actions:
   - merge the feature branch from a base/target worktree, with `--no-ff`, unless already merged;
   - load `references/changelog-and-release-notes.md` when changelog or GitHub release notes are updated/drafted;
   - update contracted changelog/docs/version files;
   - run contracted validation checks;
   - commit release prep as `release: vX.Y.Z` unless repo convention differs;
   - revalidate clean state, final diff, tag/release absence or resume match, and release notes before publish;
   - for `publish`, push the base branch, create/push annotated tag, create GitHub release, and report URL;
   - load `references/release-git-safety.md` before exact contracted cleanup.
8. If any publish or cleanup step fails, stop, report completed side effects, and do not continue cleanup automatically.

## Load if needed

- Release Contract template and approval choices → `references/release-contract.md`.
- Changelog updates or GitHub release-note drafting → `references/changelog-and-release-notes.md`.
- Remote freshness, resume checks, merge worktree, tag/release, or cleanup safety → `references/release-git-safety.md`.
- Broad feature-branch worktree strategy is unclear or outside release scope → invoke `worktree` by name.

## Stop if

- Release mode, version, base branch, feature branch, repository, publish target, or cleanup candidate is ambiguous.
- The requested action is not in the approved Release Contract.
- Base/upstream/tag/release/remote branch state is stale, unverifiable, behind, diverged, or mismatched.
- Existing local/remote tag or GitHub release points anywhere other than the intended release commit.
- Merge conflict, failing release check, version-source disagreement, unrelated dirty files, missing credentials, or changed publish target appears.
- Cleanup would touch an unnamed branch/ref/worktree, a dirty worktree, an unmerged branch, or remote feature branch without explicit delete approval.
- A new dependency/service/account, destructive action, force push/delete, credential need, or external side effect is required but uncontracted.

## Output

Return:

- release mode and version;
- published URL or prepared-but-unpublished state;
- base branch and commit SHA;
- tag status;
- cleanup performed or intentionally skipped;
- completed side effects and remaining manual follow-up.
