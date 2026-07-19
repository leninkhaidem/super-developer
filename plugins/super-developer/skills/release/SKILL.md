---
name: release
description: >
  Prepare and publish completed work. Use for release preparation, version/tag/GitHub publishing,
  or release worktree/feature-branch cleanup. Do not use for ordinary development, code review,
  or unrelated branch cleanup.
---

# Release

Prepare feature work or publish a release through an initial Release Contract. Portable planned-feature evidence
is retained by default; an explicitly requested cleanup uses a separate post-sync decision.

## Arguments

- `$ARGUMENTS` — Optional version, release type (`patch`, `minor`, `major`), feature branch/name, or mode:
  `prepare-only` / `publish`.

## Always

- Present and approve the exact **Release Contract** before the first release side effect. Skip only its prompt when
  the current turn unambiguously approves the full listed release lifecycle and all targets are known.
- The contract covers only listed edits, merge, commits, pushes, publish actions, ordinary feature cleanup, and
  local worktree cleanup. Keep target merge, target push, tag, GitHub release, remote feature deletion, portable
  evidence deletion, and local cleanup as exact separate authority boundaries.
- Sidecar Portability Authorization, Implementation auto-resolve, target merge/push, tag/release approval, and
  ordinary cleanup never grant or imply portable-evidence deletion.
- Retain the remote `artifacts/<feature>` sidecar and every final Lifecycle State, `F`, or `V`-referenced immutable
  `refs/heads/checkpoints/<feature>/...` ref through and after release by default. They are portable authority and
  evidence, not ordinary cleanup candidates.
- `V` is an index with no verdict and proves nothing. For planned features, inventory its path/digest/bound `F`
  only after fresh successful read-only `sliceproof.py validate-agentic-completion` on exact fetched roots/state.
- Bind the artifact endpoint and each code endpoint independently in their owning roots. Assert each configured push
  endpoint unchanged; sidecar reads use only artifact endpoint and checkpoint reads only their code endpoint.
- Present a separate **Portable Evidence Retention/Cleanup Decision** only when cleanup was explicitly requested,
  and only after final target/base sync plus exact tag/GitHub release state when publishing. Recommend retain.
- Without an explicit evidence-cleanup request, `prepare-only` and `publish` retain and report all exact evidence
  refs; do not add a routine retention prompt.
- Preserve and resolve index-only `V` plus every ref/object it names before evidence cleanup. Never delete
  the only resolvable portable authority/evidence; remote deletion requires a verified equivalent preservation.
- Ordinary local feature/worktree and remote feature-branch cleanup remains exact, ancestry/inclusion-checked,
  race-aware, and separate from evidence cleanup.
- `prepare-only` merges to base, updates `CHANGELOG.md` under `Unreleased`, and pushes base. It never bumps version
  files, creates/pushes/moves tags, or creates/updates a GitHub release.
- Use `--no-ff` for feature merges. Never switch the user-owned root worktree.
- After a base push, refresh and verify local base, remote-tracking base, and intended commit exactly. Never force
  reset/rewrite or switch root to repair mismatch.
- Resume only when observed commit, remote, notes, and publish state exactly match the intended release state.

## Do

1. Resolve mode, feature branch, repository, base push target, and publish-only version/GitHub target.
2. Detect base from current `main`/`master`, then `origin/HEAD` if it resolves to either, then the only local
   `main`/`master`; ask if ambiguous.
3. For a planned feature, load `../../references/artifact-store.md`; preflight base/publish/cleanup state and resolve
   exact clean artifact/code roots, full refs/SHAs, and independently authorized artifact/code push endpoints.
4. Load `references/release-git-safety.md`. In each owning root capture/assert its endpoint, directly query/fetch only
   its refs, reject cross-endpoint names, materialize exact direct refs/HEADs, then run read-only
   `sliceproof.py validate-agentic-completion --artifact-root <absolute> --code-root <absolute> --feature <feature>`.
5. Stop before approval if validation fails or the predecessor graph, final state, endpoint, ref/SHA, root cleanliness,
   base/version/tag/release state, target, or required object is missing, stale, ambiguous, or mismatched.
6. Only after that success load `references/release-contract.md`; inventory index-only `V` path/digest/bound `F`,
   exact split endpoints/refs, retention, and independent actions. Ask once unless already fully approved.
7. Execute only contracted release actions:
   - merge from a base/target worktree with `--no-ff`, unless exact ancestry proves already merged;
   - load `references/changelog-and-release-notes.md` for changelog or release-note changes;
   - make only listed changelog/docs/version edits and run listed validation checks;
   - commit the exact prep state, using `release: vX.Y.Z` only for publish unless convention differs;
   - re-fetch from each owning endpoint and repeat completion validation before the first action and whenever any
     artifact/code root, endpoint, ref, object, or relevant state could have changed; failure blocks all release action;
   - revalidate clean state, final diff, evidence inventory, and publish-only absence/resume identity;
   - push base, fetch, and verify local base, `origin/<base>`, and intended commit match;
   - for `publish`, only after base sync create/push the annotated tag and create the GitHub release, then verify
     their exact intended state;
   - perform only contracted ordinary feature/worktree cleanup under `release-git-safety.md`.
8. If evidence cleanup was explicitly requested, only after step 7's applicable final state present the separate
   retention/cleanup decision from `release-contract.md`. Execute only its exact bounded actions under
   `release-git-safety.md`; any mismatch or failure stops, retains safety refs, and is reported.
9. If no evidence cleanup was requested, retain it without prompting and report final `V`, sidecar ref/SHA, and all
   required checkpoint refs/SHAs.

## Stop if

- Any mode, repository, base, feature, owning endpoint, cleanup candidate, version, publish target, required object,
  predecessor graph, or fresh completion-validation identity is ambiguous, stale, missing, changed, or unverifiable.
- An action is outside its exact approval boundary; an initial contract is treated as evidence-deletion authority;
  or a cleanup decision is offered before final sync/publish verification or without an explicit cleanup request.
- Cleanup names an in-use/dirty or unverified item, sweeps a namespace, force-rewrites, lacks expected SHAs or
  post-delete verification, or could remove the only resolvable `V` or required object.
- A conflict, failing check, unrelated dirty file, credential need, new service/dependency, destructive action, or
  external effect is uncontracted.

## Output

Return mode/version action, base and commit, post-push sync, tag/release/URL state, ordinary cleanup, and completed
side effects. For planned features, report validation result plus index-only `V` path/digest/bound `F`, artifact
endpoint/ref/SHA, each code endpoint/ref/SHA, retention or separately approved cleanup, blockers, and follow-up.
