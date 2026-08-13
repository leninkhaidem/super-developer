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
- Never use the user-owned canonical root for integration or release edits. Bind its branch, HEAD, and status before
  side effects and require it clean, unchanged, and safely synchronizable. A named temporary integration
  ref/worktree from the exact fresh remote-base SHA remains required when root locks the base branch.
- Immediately before the one base push, an approved Release Contract may normalize the canonical root to the base
  branch when necessary and fast-forward it to exact `RESULT_SHA`. This exact release-sync action is the sole tracked
  root-checkout mutation; never reset, force, stash, clean, merge divergent history, or overwrite ignored/user files.
- Clean up only exact feature branches, remote refs, artifact sidecar refs/worktrees, and worktrees named in the approved contract.
- Sidecar cleanup is default when eligible after final base/target push sync; never merge `artifacts/<feature>` into the base branch.
- Before the base push, synchronize the canonical primary checkout and local base to exact `RESULT_SHA`; then perform
  the one exact-lease push. Fetch afterward and verify root HEAD, local base, `origin/<base>`, and fresh server base
  all equal that result and the root remains clean.
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
   - canonical primary root path plus its bound branch, HEAD, and status; require it clean and unchanged, its local
     base no more than an ancestor of fresh `origin/<base>`, the base branch not occupied by another worktree when
     root normalization will be needed, and both root/base refs capable of the contracted fast-forward;
   - current integration working tree cleanliness and unrelated changes;
   - version sources when publishing, and latest `vX.Y.Z` tag for changelog/source-range context;
   - feature branch merge status and candidate cleanup refs/worktrees, including default
     delete/remove disposition or hard blocker for any `artifacts/<feature>` sidecar;
   - `CHANGELOG.md` presence, most recent release format, and whether the proposed lightweight format needs user choice;
   - GitHub CLI auth/repo/release state when publishing.
4. Load `references/release-git-safety.md` before relying on remote refs, existing tags/releases, feature merge, publish, sidecar state, or cleanup.
5. Stop before contract approval if local base is ahead/diverged from the fresh remote base, the canonical root is
   dirty, drifted, or not safely synchronizable, the base branch is occupied elsewhere when root normalization is
   needed, publish version sources disagree, a worktree has unrelated changes, the push target is ambiguous, remote
   state cannot be verified, or an existing tag/release conflicts. A clean local base omitted from temporary
   integration may lag only when it is an ancestor of the remote base and the contract will fast-forward it to the
   exact release result immediately before publication.
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
   - revalidate the root binding, normalize the canonical root to `<base>` if necessary, and fast-forward-only merge
     exact `RESULT_SHA` there without overwriting ignored or user files;
   - prove the server still equals `EXPECTED` and `EXPECTED` is an ancestor of `RESULT_SHA`, then perform exactly one
     exact-lease result-SHA/target-ref base push, fetch, and verify canonical root HEAD, local `<base>`,
     `origin/<base>`, and fresh server base equal the result while root status remains clean;
   - for `prepare-only`, perform contracted default cleanup for exact local/remote feature and sidecar refs/worktrees
     only after post-push verification;
   - for `publish`, create/push the annotated tag and create the GitHub release only after post-push verification,
     then perform contracted default cleanup for exact feature/sidecar candidates when applicable and report URL;
   - load `references/release-git-safety.md` before exact contracted cleanup.
8. Handle failures by phase. On a pre-push failure, stop before publication, report partial local effects, and
   retain every safety net. On a push failure, report partial local/remote effects, retain every safety net, and
   stop. On a post-push failure, report partial published/verified effects, retain every safety net, and stop cleanup.

## Load if needed

- Release Contract template and approval choices → `references/release-contract.md`.
- Changelog updates or GitHub release-note drafting → `references/changelog-and-release-notes.md`.
- Remote freshness, resume checks, merge worktree, tag/release, sidecar state, or cleanup safety → `references/release-git-safety.md`.
- Broad feature-branch worktree strategy is unclear or outside release scope → invoke `worktree` by name.

## Stop if

- Release mode, base branch, feature branch, repository, base push target, or cleanup candidate is ambiguous;
  GitHub publish target or publish version is ambiguous when publishing.
- The requested action is not in the approved Release Contract.
- Remote state is stale/unverifiable, local base is ahead/diverged, the bound canonical root is dirty/drifted,
  root normalization is blocked by an occupied base branch, a required root update is non-fast-forward, or an
  expected root/local-base/origin/server/result binding mismatches.
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
- post-push result/remote sync plus canonical-root branch, HEAD, local-base equality, and clean status;
- tag/GitHub release status;
- cleanup performed, blocked, or explicitly kept, including sidecar artifact cleanup;
- completed side effects and remaining manual follow-up.
