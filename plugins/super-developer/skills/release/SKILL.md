---
name: release
description: >
  Prepares or publishes completed work through a contract-bound release. Use when asked to prepare,
  publish, version, tag, ship, or finish release cleanup. Do not use for development, review, audit,
  or unrelated cleanup.
---

# Release

Prepare feature work for a future release or publish an actual release through one explicit Release Contract,
with exact state, side effects, artifact-sidecar handling, and cleanup candidates named before action.

## Arguments

- `$ARGUMENTS` — Optional version, release type (`patch`, `minor`, `major`), feature branch/name, or mode: `prepare-only` / `publish`.

## Always

- Use one approval gate per release attempt: **Release Contract Approval**.
- Always present the exact Release Contract before the first side effect.
- Skip only the approval prompt when the current turn unambiguously approves the full normal lifecycle and all release targets are known.
- Current-turn approval never implies remote feature-branch or sidecar deletion unless the exact remote ref deletion is listed in the Release Contract.
- Default cleanup disposition is delete/remove for every eligible feature code worktree,
  local feature branch, remote feature branch, and artifact sidecar worktree/ref after final
  base/target push sync.
- Keep cleanup candidates only for a hard blocker (dirty worktree, failed ancestry/inclusion,
  active review/audit/package need, missing final sidecar checkpoint, checked-out branch without
  removable worktree, unverifiable remote state) or explicit user keep request.
- The approved contract covers only listed file edits, feature merge, commits, pushes, tag/GitHub release actions, and cleanup candidates.
- `prepare-only` is feature integration: merge to the base branch, update `CHANGELOG.md` under `Unreleased`,
  push the base branch, and delete/remove exact eligible feature refs/worktrees and artifact sidecar candidates named in the contract.
- `prepare-only` never bumps version files, creates/pushes/moves tags, or creates/updates a GitHub release.
- Do not ask for staged re-approvals after approval; report checkpoints unless observed state invalidates the contract.
- Use `--no-ff` when merging a feature branch into the base branch.
- Never switch or detach the user-owned root worktree. If it locks the base branch, use a named temporary
  integration ref/worktree from the exact fresh remote-base SHA; never ask the user to detach the root.
- Clean up only exact feature branches, remote refs, artifact sidecar refs/worktrees, and worktrees named in the approved contract.
- Sidecar cleanup is default when eligible after final base/target push sync; never merge `artifacts/<feature>` into the base branch.
- After a base push, verify the intended commit, `origin/<base>`, and fresh remote base match. Require local
  base equality only when it was the integration ref; a root-locked local base stays unchanged and may lag.
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
   - fresh remote-base SHA, local-base ancestry, and whether the protected root locks the local base;
   - current working tree cleanliness and unrelated changes;
   - version sources when publishing, and latest `vX.Y.Z` tag for changelog/source-range context;
   - feature branch merge status and candidate cleanup refs/worktrees, including default
     delete/remove disposition or hard blocker for any `artifacts/<feature>` sidecar;
   - `CHANGELOG.md` presence, most recent release format, and whether the proposed lightweight format needs user choice;
   - GitHub CLI auth/repo/release state when publishing.
4. Load `references/release-git-safety.md` before relying on remote refs, existing tags/releases, feature merge, publish, sidecar state, or cleanup.
5. Stop before contract approval if local base is ahead/diverged from the fresh remote base, publish version sources disagree,
   a worktree has unrelated changes, the push target is ambiguous, remote state cannot be verified, or an existing
   tag/release conflicts. A clean root-locked local base may lag only when it is an ancestor of the remote base.
6. Load `references/release-contract.md` and present the compact Release Contract, including
   changelog format choices and default delete/remove cleanup candidates when needed.
   Ask once unless the current turn already approved the full contract.
7. After approval, execute only contracted actions:
   - merge with `--no-ff` from an exact non-root base checkout or the named temporary integration worktree;
   - load `references/changelog-and-release-notes.md` when changelog or GitHub release notes are updated/drafted;
   - update contracted changelog/docs/version files, with `prepare-only` changelog entries under `Unreleased` and no version-file bump;
   - run contracted validation checks;
   - commit contracted prep/integration changes, using `release: vX.Y.Z` only for publish prep unless repo convention differs;
   - revalidate clean state, final diff, and publish-only tag/release absence or resume match;
   - push by the exact result-SHA/target-ref lease procedure, then verify result, `origin/<base>`, and fresh
     remote base match; preserve a root-locked local base unchanged and prove it is an ancestor of result;
   - for `prepare-only`, push the base branch, run post-push sync verification, and perform contracted default cleanup for exact
     local/remote feature and sidecar refs/worktrees after verification;
   - for `publish`, push the base branch, run post-push sync verification, create/push annotated tag,
     create GitHub release, then perform contracted default cleanup for exact feature/sidecar candidates
     when applicable, and report URL;
   - load `references/release-git-safety.md` before exact contracted cleanup.
8. If any push, publish, or cleanup step fails, stop, report completed side effects, and do not continue cleanup automatically.

## Load if needed

- Release Contract template and approval choices → `references/release-contract.md`.
- Changelog updates or GitHub release-note drafting → `references/changelog-and-release-notes.md`.
- Remote freshness, resume checks, merge worktree, tag/release, sidecar state, or cleanup safety → `references/release-git-safety.md`.
- Broad feature-branch worktree strategy is unclear or outside release scope → invoke `worktree` by name.

## Stop if

- Release mode, base branch, feature branch, repository, base push target, or cleanup candidate is ambiguous;
  GitHub publish target or publish version is ambiguous when publishing.
- The requested action is not in the approved Release Contract.
- Remote state is stale/unverifiable, local base is ahead/diverged, or the expected remote/result binding mismatches.
- Existing local/remote tag or GitHub release points anywhere other than the intended publish commit.
- Merge conflict, failing release check, publish version-source disagreement, unrelated dirty files, missing credentials, or changed publish target appears.
- Cleanup would touch an unnamed branch/ref/worktree, a dirty worktree, an unmerged branch,
  active sidecar, or remote ref whose exact deletion is not listed in the approved Release Contract.
- A new dependency/service/account, destructive action, force push/delete, credential need, or external side effect is required but uncontracted.

## Output

Return:

- release mode and version action;
- published URL or prepared integrated state;
- base branch and commit SHA;
- post-push result/remote sync and root-locked local-base status;
- tag/GitHub release status;
- cleanup performed, blocked, or explicitly kept, including sidecar artifact cleanup;
- completed side effects and remaining manual follow-up.
