---
name: release
description: >
  Prepare and publish a project release on demand after development is complete. Use when the user
  asks to prepare a release, publish a release, bump a version, tag a release, create GitHub release
  notes, ship completed work, or clean up release worktrees/feature branches. Do not use for ordinary
  development, code review, or unrelated branch cleanup.
---

# Release

Prepare feature work for a future release or publish an actual release through one explicit Release Contract,
with exact state, side effects, and cleanup candidates named before action.

## Arguments

- `$ARGUMENTS` — Optional version, release type (`patch`, `minor`, `major`), feature branch/name, or mode: `prepare-only` / `publish`.

## Always

- Use one approval gate per release attempt: **Release Contract Approval**.
- Always present the exact Release Contract before the first side effect.
- Skip only the approval prompt when the current turn unambiguously approves the full normal lifecycle and all release targets are known.
- Current-turn approval never implies remote feature-branch deletion unless the exact remote ref deletion was explicitly approved.
- The approved contract covers only listed file edits, feature merge, commits, pushes, tag/GitHub release actions, and cleanup candidates.
- `prepare-only` is feature integration: merge to the base branch, update `CHANGELOG.md` under `Unreleased`,
  push the base branch, and clean up exact feature refs/worktrees named in the contract.
- `prepare-only` never bumps version files, creates/pushes/moves tags, or creates/updates a GitHub release.
- Do not ask for staged re-approvals after approval; report checkpoints unless observed state invalidates the contract.
- Use `--no-ff` when merging a feature branch into the base branch.
- Never switch the user-owned root worktree to make a release merge or cleanup possible.
- Clean up only exact feature branches, remote refs, and worktrees named in the approved contract and proven merged.
- After any contracted base push, refresh remote refs and verify local base, remote-tracking base,
  and the intended prepare/publish commit match; never force-reset or switch root to repair mismatch.
- If partially complete, resume only from observed state that matches the intended prepare/publish commit,
  tag/release state when publishing, remote state, and notes.

## Do

1. Resolve mode, feature branch if any, repository, and base push target; resolve proposed version,
   bump type, or GitHub publish target only for `publish`.
2. Detect the base branch:
   - use current branch only if it is `main` or `master`;
   - otherwise use `origin/HEAD` only if it resolves to `main` or `master`;
   - otherwise use the only local `main`/`master`; ask if ambiguous.
3. Preflight and report:
   - base branch/upstream freshness and divergence;
   - current working tree cleanliness and unrelated changes;
   - version sources when publishing, and latest `vX.Y.Z` tag for changelog/source-range context;
   - feature branch merge status and candidate cleanup refs/worktrees;
   - `CHANGELOG.md` presence, most recent release format, and whether the proposed lightweight format needs user choice;
   - GitHub CLI auth/repo/release state when publishing.
4. Load `references/release-git-safety.md` before relying on remote refs, existing tags/releases, feature merge, publish, or cleanup.
5. Stop before contract approval if base is behind/diverged, publish version sources disagree, working tree has unrelated changes,
   base push target is ambiguous, GitHub publish target is ambiguous when publishing, remote state cannot be verified for
   push/delete/publish, or an existing tag/release would conflict with the intended publish commit.
6. Load `references/release-contract.md` and present the compact Release Contract, including changelog format choices when needed.
   Ask once unless the current turn already approved the full contract.
7. After approval, execute only contracted actions:
   - merge the feature branch from a base/target worktree, with `--no-ff`, unless already merged;
   - load `references/changelog-and-release-notes.md` when changelog or GitHub release notes are updated/drafted;
   - update contracted changelog/docs/version files, with `prepare-only` changelog entries under `Unreleased` and no version-file bump;
   - run contracted validation checks;
   - commit contracted prep/integration changes, using `release: vX.Y.Z` only for publish prep unless repo convention differs;
   - revalidate clean state, final diff, and publish-only tag/release absence or resume match;
   - after any base branch push, fetch remote refs and verify local base, `origin/<base>`, and the
     intended commit all match before tag/release creation or cleanup;
   - for `prepare-only`, push the base branch, run post-push sync verification, and clean up exact local/remote feature refs/worktrees after merge verification;
   - for `publish`, push the base branch, run post-push sync verification, create/push annotated tag, create GitHub release, and report URL;
   - load `references/release-git-safety.md` before exact contracted cleanup.
8. If any push, publish, or cleanup step fails, stop, report completed side effects, and do not continue cleanup automatically.

## Load if needed

- Release Contract template and approval choices → `references/release-contract.md`.
- Changelog updates or GitHub release-note drafting → `references/changelog-and-release-notes.md`.
- Remote freshness, resume checks, merge worktree, tag/release, or cleanup safety → `references/release-git-safety.md`.
- Broad feature-branch worktree strategy is unclear or outside release scope → invoke `worktree` by name.

## Stop if

- Release mode, base branch, feature branch, repository, base push target, or cleanup candidate is ambiguous;
  GitHub publish target or publish version is ambiguous when publishing.
- The requested action is not in the approved Release Contract.
- Base/upstream/remote branch state is stale, unverifiable, behind, diverged, or mismatched; publish tag/release state is stale or mismatched.
- Existing local/remote tag or GitHub release points anywhere other than the intended publish commit.
- Merge conflict, failing release check, publish version-source disagreement, unrelated dirty files, missing credentials, or changed publish target appears.
- Cleanup would touch an unnamed branch/ref/worktree, a dirty worktree, an unmerged branch, or remote feature branch without explicit delete approval.
- A new dependency/service/account, destructive action, force push/delete, credential need, or external side effect is required but uncontracted.

## Output

Return:

- release mode and version action;
- published URL or prepared integrated state;
- base branch and commit SHA;
- post-push local/remote base sync verification status;
- tag/GitHub release status;
- cleanup performed or intentionally skipped;
- completed side effects and remaining manual follow-up.
