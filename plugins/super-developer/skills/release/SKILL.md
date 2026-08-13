---
name: release
description: >
  Prepares or publishes completed work with version bumps, tags, release notes, and cleanup. Use when
  asked to prepare, publish, version, tag, ship, or finish a release. Do not use for development,
  code review, audit, or unrelated cleanup.
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
- Never switch or detach the user-owned root worktree. If that checkout occupies `<base>`, use a named
  temporary integration ref/worktree from the exact fresh remote-base SHA; never ask the user to detach the root.
- Clean up only exact feature branches, remote refs, artifact sidecar refs/worktrees, and worktrees named in the approved contract.
- Sidecar cleanup is default when eligible after final base/target push sync; never merge `artifacts/<feature>` into the base branch.
- After a successful base push and `origin/<base>` == RESULT_SHA, the release is not complete until the
  canonical local base checkout is at RESULT_SHA. Resolve `$PROJECT_ROOT` and apply the post-push
  fast-forward only as specified in `references/release-git-safety.md`. `--show-toplevel`, cwd, and a
  linked worktree must not anchor it.
- If that checkout is dirty, detached, not on `<base>`, or the update is not a fast-forward: do not switch,
  reset, stash, clean, or force. Stop before tag, GitHub release, and cleanup. Report the published result
  and the exact manual follow-up. Temporary lag is not a successful end state.
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
   - fresh remote-base SHA, local-base ancestry, and whether the protected root occupies `<base>`;
   - current working tree cleanliness and unrelated changes;
   - version sources when publishing, and latest `vX.Y.Z` tag for changelog/source-range context;
   - feature branch merge status and candidate cleanup refs/worktrees, including default
     delete/remove disposition or hard blocker for any `artifacts/<feature>` sidecar;
   - `CHANGELOG.md` presence, most recent release format, and whether the proposed lightweight format needs user choice;
   - GitHub CLI auth/repo/release state when publishing.
4. Load `references/release-git-safety.md` before relying on remote refs, existing tags/releases, feature merge, publish, sidecar state, or cleanup.
5. Stop before contract approval if local base is ahead/diverged from the fresh remote base, publish version sources disagree,
   a worktree has unrelated changes, the push target is ambiguous, remote state cannot be verified, or an existing
   tag/release conflicts. A root checkout that occupies `<base>` may stay on an ancestor of the remote base until
   the post-push fast-forward; that occupancy is not itself a preflight blocker.
6. Load `references/release-contract.md` and present the compact Release Contract, including
   changelog format choices and default delete/remove cleanup candidates when needed.
   Ask once unless the current turn already approved the full contract.
7. After approval, execute only contracted actions:
   - merge with `--no-ff` from the named temporary integration worktree; never occupy `<base>` there;
   - load `references/changelog-and-release-notes.md` when changelog or GitHub release notes are updated/drafted;
   - update contracted changelog/docs/version files, with `prepare-only` changelog entries under `Unreleased` and no version-file bump;
   - run contracted validation checks;
   - commit contracted prep/integration changes, using `release: vX.Y.Z` only for publish prep unless repo convention differs;
   - revalidate clean state, final diff, and publish-only tag/release absence or resume match;
   - push by the exact result-SHA/target-ref lease procedure, then verify result, `origin/<base>`, and fresh
     remote base match; apply the post-push canonical fast-forward in `references/release-git-safety.md`;
     if that update cannot run, stop before the next bullets;
   - for `prepare-only`, only after that fast-forward succeeds, perform contracted default cleanup for exact
     local/remote feature and sidecar refs/worktrees;
   - for `publish`, only after that fast-forward succeeds, create/push the annotated tag, create the GitHub
     release, then perform contracted default cleanup for exact feature/sidecar candidates when applicable,
     and report URL;
   - load `references/release-git-safety.md` before exact contracted cleanup.
8. If any push, publish, or cleanup step fails, stop, report completed side effects, and do not continue cleanup automatically.

## Load if needed

- Release Contract template and approval choices → `references/release-contract.md`.
- Changelog updates or GitHub release-note drafting → `references/changelog-and-release-notes.md`.
- Remote freshness, resume checks, merge worktree, post-push canonical fast-forward, tag/release,
  sidecar state, or cleanup safety → `references/release-git-safety.md`.
- Broad feature-branch worktree strategy is unclear or outside release scope → invoke `worktree` by name.

## Stop if

- Release mode, base branch, feature branch, repository, base push target, or cleanup candidate is ambiguous;
  GitHub publish target or publish version is ambiguous when publishing.
- The requested action is not in the approved Release Contract.
- Remote state is stale/unverifiable, local base is ahead/diverged, or the expected remote/result binding mismatches.
- After a successful base push, the canonical checkout is dirty, detached, not on `<base>`, or cannot
  fast-forward to RESULT_SHA.
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
- post-push result/remote sync and canonical-checkout fast-forward status, or the named follow-up if not updated;
- tag/GitHub release status;
- cleanup performed, blocked, or explicitly kept, including sidecar artifact cleanup;
- completed side effects and remaining manual follow-up.
