# Disposable Probe Cleanup

Use only for an Execution Contract envelope-created empirical probe. It makes an owned dirty probe removable
without force while preserving every unowned byte and all root/remote state.

## Required Creation Receipt

Create the receipt outside the probe worktree before probe writes. Bind:

- canonical worktree path, full direct probe ref, feature/question/attempt IDs, base ref, and captured base SHA;
- initial `HEAD` and branch tip equal base SHA; clean index/worktree; digest of NUL `git ls-files --stage` output;
- NUL-delimited, digest-bound exact manifests for allowed tracked, untracked, ignored, symlink, process, and data
  records. Paths are safe repo-relative literals, never globs, prefixes, or broad directories; exact empty owned
  directories may be listed separately for later `rmdir`;
- exact process identity/start token/termination command and exact external data leaf/type/initial-state records;
- `staging=forbidden`, `index_write=forbidden`, `commit=forbidden`, `merge=forbidden`, `push=forbidden`, and
  `remote_action=none`.

Immediately after creation, capture the NUL index-manifest checksum and prove `HEAD`/ref = base SHA, cached diff empty,
`git status --porcelain=v1 -z --untracked-files=all` empty, and
`git ls-files --others --ignored --exclude-standard -z` empty. If any proof fails, do not probe.

## Classify Before Mutation

1. Revalidate canonical path/ref/base receipt and locally prove no upstream/tracking configuration:

   ```bash
   BRANCH=${REF#refs/heads/}
   test -z "$(git -C "$PROJECT_ROOT" for-each-ref --format='%(upstream)' "$REF")"
   test -z "$(git -C "$PROJECT_ROOT" config --get "branch.$BRANCH.remote" || :)"
   test -z "$(git -C "$PROJECT_ROOT" config --get "branch.$BRANCH.merge" || :)"
   test -z "$(git -C "$PROJECT_ROOT" config --get "branch.$BRANCH.pushRemote" || :)"
   test "$REMOTE_ACTION" = none
   ```

   Perform no remote lookup, fetch, push, or deletion. A coincidental remote ref is out of scope and untouched.
2. Before restoring anything, regenerate NUL `git ls-files --stage`, require its digest = receipt checksum,
   `HEAD`/direct tip = base SHA, and `git diff --cached --quiet`. Any index/staging change stops; never repair it.
3. Write classifications outside the worktree with NUL-safe Git output:

   ```bash
   git -C "$WT" diff --name-only -z "$BASE_SHA" -- >"$OBS_TRACKED"
   git -C "$WT" diff --diff-filter=D --name-only -z "$BASE_SHA" -- >"$OBS_DELETED"
   git -C "$WT" ls-files --others --exclude-standard -z >"$OBS_UNTRACKED"
   git -C "$WT" ls-files --others --ignored --exclude-standard -z >"$OBS_IGNORED"
   ```

4. Use a NUL-aware parser (for example Python bytes split on `b'\0'`, never newline/shell-word parsing) to validate
   safe literal paths and prove every observed record is an exact member of its bound owned manifest.
   `OBS_DELETED` must be a subset of owned tracked paths. Inspect base modes and current paths with `lstat` without
   following links; every base/current symlink must also match the symlink manifest and bound target/type policy.
5. NUL-safely reconcile exact process identities/start tokens and external data leaves/types with their manifests.
   Any extra, changed-identity, type-mismatched, traversal, symlink-following, unowned, or uncertain record stops.

## Restore Exact Owned State

1. Terminate only receipt-owned process identities with their bound command, await exit, and verify absence. Restore
   exact bound initial state for pre-existing owned external data; immediately revalidate its manifest and `lstat`
   before unlinking only an external leaf recorded absent at creation.
2. Before each removal, immediately revalidate the digest-bound exact manifest membership and inspect the current
   leaf with `lstat` without following links. For every NUL record in `OBS_UNTRACKED` and `OBS_IGNORED`, unlink only
   that exact owned regular file or symlink with `rm -- "$WT/$PATH"`.
3. After all leaves are gone, immediately revalidate each separately listed exact owned directory and its `lstat`
   type/emptiness, then remove only those empty directories deepest-first with `rmdir -- <exact-path>`. Never use a
   glob, recursive removal, `git clean`, reset, stash, force, or symlink following.
4. Only after owned leaves/directories are removed, restore proven changed tracked paths from the bound base SHA
   with literal NUL pathspec semantics; restoring first can silently delete an owned leaf beneath a tracked-file-to-
   directory replacement:

   ```bash
   if test -s "$OBS_TRACKED"; then
     git --literal-pathspecs -C "$WT" restore --source="$BASE_SHA" --worktree \
       --pathspec-from-file="$OBS_TRACKED" --pathspec-file-nul
   fi
   ```

5. Prove owned processes/data absent, `HEAD`/direct ref = base SHA, cached diff empty, regenerated NUL index digest
   unchanged, and both final NUL status and ignored classifications empty.
6. Only after every proof passes, run normal `git worktree remove "$WT"`, verify the ref is direct, and delete it
   with `git update-ref --no-deref -d "$REF" "$BASE_SHA"`. Record `remote_action=none`; touch no remote ref.

## Stop if

Stop and retain the worktree/ref on any receipt, identity, manifest, classification, index, HEAD/ref, process/data,
status, path-type, or cleanup uncertainty. Return exact residual state; never make it clean by force or broad action.
