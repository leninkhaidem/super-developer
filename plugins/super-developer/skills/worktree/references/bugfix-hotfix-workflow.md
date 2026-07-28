# Bugfix and Hotfix Workflow
Use for disposable empirical/diagnostic probes, active-feature bugfixes, maintenance bugfixes, production hotfixes,
and propagation. Boundary: isolated non-root worktrees and immutable diagnose delivery gates.
## Contract
- Root files/index are user-owned: never switch, edit, merge, or deliver there. Orchestration commands may run from
  `$PROJECT_ROOT` to create/remove approved non-root worktrees/refs.
- Bugfix, hotfix, source, and target refs/SHAs require exact approval. Auto-resolve probes instead require the
  Execution Contract's exact feature namespace/pattern and allowed base refs; never infer `main` or current branch.
- Probe authority forbids stage/index writes, commit/merge/push, reset/stash/clean/force, and permits only exact
  receipt-owned tracked/untracked/ignored/symlink/process/data changes. Live containment remains outside.
- Creation, edits, commit, branch push, target merge, target push, and cleanup otherwise remain separate gates.
- Run every command block in fresh Bash with `set -euo pipefail`; failed checks/merges stop later actions.
## Immutable Approval Fields
```text
worktree_creation: base_ref=<ref>; base_sha=<sha>; branch=<ref>; path=<path>
production_edits: scope=<paths/purpose/non-goals>
commit: worktree=<path>; reviewed_snapshot=<checksum>
branch_push: remote=<remote>; source_ref=<ref>; destination_ref=<ref>; source_sha=<sha>;
  reviewed_snapshot=<checksum>; expected_remote_destination_sha=<sha|absent>
target_merge: source_ref=<ref>; source_sha=<sha>; target_ref=<ref>; pre_merge_target_sha=<sha>;
  reviewed_snapshot=<checksum>; strategy=no-ff; integration_ref=<ref>; worktree=<non-root path>
target_push: remote=<remote>; target_ref=<ref>; result_sha=<post-merge sha>;
  expected_remote_target_sha=<sha>
cleanup: worktree=<path>; worktree_head=<sha>; worktree_state=<checksum>;
  local_ref=<full-ref>; local_ref_kind=direct; local_ref_sha=<sha>;
  landing_worktree=<path|n/a>; landing_head/state=<value|n/a>;
  remote_ref=<ref|none>; expected_remote_ref_sha=<sha|absent>
```
Recapture every binding immediately before action. Drift blocks and requires approval; no field implies another.
## Atomic Branch Publication
For standard bugfix publication, approval binds `origin`, both refs=`bugfix/<name>`, source SHA, snapshot, and
expected remote SHA or `absent`. `ls-remote` is diagnostic; the exact qualified lease is server-side CAS. A command
error cannot mean absent. Existing remote equal to source is a no-op; any other mismatch stops/requires reapproval.
For an existing expected SHA, prove fast-forward ancestry before CAS. Expected-absent uses an empty exact lease:
```bash
set -euo pipefail
SOURCE_SHA=<source-sha>
DEST_REF=refs/heads/bugfix/<name>
EXPECTED=<expected_remote_destination_sha>
test "$(git rev-parse bugfix/<name>)" = "$SOURCE_SHA"
REMOTE_LINE="$(git ls-remote --heads origin "$DEST_REF")"
REMOTE_SHA="${REMOTE_LINE%%$'\t'*}"
if [[ "$REMOTE_SHA" == "$SOURCE_SHA" ]]; then printf '%s\n' 'remote already at source; no-op'; exit 0; fi
if [[ "$EXPECTED" == "absent" ]]; then
  test -z "$REMOTE_LINE"
  git push --force-with-lease="$DEST_REF:" origin "$SOURCE_SHA:$DEST_REF"
else
  test "$REMOTE_SHA" = "$EXPECTED"
  git merge-base --is-ancestor "$EXPECTED" "$SOURCE_SHA"
  git push --force-with-lease="$DEST_REF:$EXPECTED" origin "$SOURCE_SHA:$DEST_REF"
fi
```
Bare `--force`, unqualified `--force-with-lease`, and a lease without required ancestry proof are forbidden.
## Isolated Worktree Creation
Auto-resolve probe; the packet supplies receipt paths plus digest-bound exact NUL manifests outside the worktree:
```bash
set -euo pipefail; cd "$PROJECT_ROOT"
FEATURE=<contract-feature>; QUESTION_ID=<logical-question-id>; ATTEMPT_ID=<1|2|3>
[[ "$FEATURE" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ && "$QUESTION_ID" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]
[[ "$ATTEMPT_ID" =~ ^[123]$ ]]; BASE_REF=<contract-listed-base-ref>
case "$BASE_REF" in <allowed-base-ref-1>|<allowed-base-ref-2>) ;; *) exit 1 ;; esac
BASE_SHA="$(git rev-parse "$BASE_REF")"; test "$(git rev-parse "$BASE_REF")" = "$BASE_SHA"
WT="$PROJECT_ROOT/.worktrees/$FEATURE/probe-$QUESTION_ID-a$ATTEMPT_ID"; REF="probe/$FEATURE/$QUESTION_ID/a$ATTEMPT_ID"
test ! -e "$WT"; test ! -L "$WT"; test -z "$(git show-ref --verify --hash "refs/heads/$REF" 2>/dev/null || :)"
git worktree add --no-track -b "$REF" "$WT" "$BASE_SHA"
test -z "$(git for-each-ref --format='%(upstream)' "refs/heads/$REF")"; test -z "$(git config --get "branch.$REF.remote" || :)"; test -z "$(git config --get "branch.$REF.merge" || :)"; test -z "$(git config --get "branch.$REF.pushRemote" || :)"
test "$(git -C "$WT" symbolic-ref -q HEAD)" = "refs/heads/$REF"; test "$(git -C "$WT" rev-parse HEAD)" = "$BASE_SHA"; git -C "$WT" diff --cached --quiet; git -C "$WT" diff --quiet "$BASE_SHA" --
git -C "$WT" status --porcelain=v1 -z --untracked-files=all >"$INITIAL_STATUS_NUL"; test ! -s "$INITIAL_STATUS_NUL"
git -C "$WT" ls-files --others --ignored --exclude-standard -z >"$INITIAL_IGNORED_NUL"; test ! -s "$INITIAL_IGNORED_NUL"
git -C "$WT" ls-files --stage -z >"$INITIAL_INDEX_NUL"
INDEX_SHA256="$(sha256sum "$INITIAL_INDEX_NUL")"; INDEX_SHA256="${INDEX_SHA256%% *}"
```
Bind base ref/SHA, clean HEAD/ref/index/worktree, NUL index-manifest checksum, canonical path, manifest digests,
no upstream/tracking config, forbidden actions, and `remote_action=none` in the receipt before any probe write.
Active-feature, maintenance, and production-hotfix repairs respectively:
```bash
set -euo pipefail
cd "$PROJECT_ROOT"
git worktree add .worktrees/bugfix-<name> -b bugfix/<name> <feature-base-sha>
# OR: git worktree add .worktrees/bugfix-<name> -b bugfix/<name> <maintenance-base-sha>
# OR: git worktree add .worktrees/hotfix-<name> -b hotfix/<name> <production-base-sha>
```

Probe edits stay uncommitted and evidence-only: never commit, merge, push, or touch unowned writes/processes/data.
Their workflow applies bounded method/execution checks; do not production-harden, security-review, `review-code`, or
`audit` them. For repairs, verify base ref/SHA and edit/commit only after complete-state CLEAN review.
## Planned Production-Hotfix Bridge
When a confirmed broad/risky production repair is routed through planning, the diagnosis handoff carries its
mechanism/evidence, behavior goal/non-goals, regression acceptance, residual risk, explicit production base
ref/SHA, intended `hotfix/<name>`, and target ref. Planning authorization covers only that handoff; implementation
and every remote/delivery action retain their owning approvals.
Reuse ordinary SPEC/Slice/package/proof/report and verification gates—do not create a hotfix artifact taxonomy.
Carry delivery context through planning/review packets into the Execution Contract. Normal package refs/worktrees
integrate into the named non-root `hotfix-<name>` worktree/ref from the explicit production base; do not synthesize
`feature/<feature>`. Create an independent package from production base, or from `hotfix/<name>` after prerequisites:
```bash
set -euo pipefail
cd "$PROJECT_ROOT"
git worktree add .worktrees/<feature>/wp-<WP-ID> -b wp/<feature>/<WP-ID> <production-base-sha-or-hotfix-ref>
git -C "$PROJECT_ROOT/.worktrees/hotfix-<name>" merge wp/<feature>/<WP-ID> --no-edit
```
The reviewed hotfix branch uses the exact non-force source-push command listed in the Execution Contract and
publishes only that branch; target merge/push, release/deployment, live mutation, sidecar publication, and cleanup remain separate boundaries.

## Non-Root Immutable Integration

Use `--no-ff`. Revalidate source SHA, target SHA, and snapshot. Use an existing clean **non-root** target worktree
only at `pre_merge_target_sha`; never use root. When target is root-locked or lacks a non-root checkout, create a
temporary integration branch/worktree from exact target SHA, not a second target checkout:

```bash
set -euo pipefail
cd "$PROJECT_ROOT"
git worktree add -b integrate/<route>-<name> \
  .worktrees/integrate-<route>-<name> <pre-merge-target-sha>
cd .worktrees/integrate-<route>-<name>
test "$(git rev-parse HEAD)" = "<pre-merge-target-sha>"
git merge --no-ff <source-sha> -m "fix: <name> -- integrate"
RESULT_SHA="$(git rev-parse HEAD)"
printf 'RESULT_SHA=%s\n' "$RESULT_SHA"
```

`<route>` is `feature-bugfix`, `maintenance`, or `hotfix`. This creates an immutable integration result without
moving the locked local target. Report result and unchanged local target; never claim local target was merged.
Merge never pushes. Request separate target-push approval only after capturing `RESULT_SHA`.

## Atomic Target Push

Approval binds result and expected remote target SHA. `ls-remote` failure stops. Prove the expected remote SHA is
an ancestor of result, then use exact server-enforced CAS. A concurrent remote change makes the lease fail:

```bash
set -euo pipefail
RESULT_SHA=<result-sha>
EXPECTED=<expected-remote-target-sha>
TARGET_REF=refs/heads/<target-ref>
INTEGRATION_WORKTREE=<approved-integration-worktree>
cd "$INTEGRATION_WORKTREE"
test "$(git rev-parse HEAD)" = "$RESULT_SHA"
REMOTE_LINE="$(git ls-remote --heads <remote> "$TARGET_REF")"
test -n "$REMOTE_LINE"
REMOTE_SHA="${REMOTE_LINE%%$'\t'*}"
test "$REMOTE_SHA" = "$EXPECTED"
git merge-base --is-ancestor "$EXPECTED" "$RESULT_SHA"
git push --force-with-lease="$TARGET_REF:$EXPECTED" <remote> "$RESULT_SHA:$TARGET_REF"
```

For the temporary example, `INTEGRATION_WORKTREE=$PROJECT_ROOT/.worktrees/integrate-<route>-<name>`; an existing
approved non-root integration path substitutes exactly. Never use force without exact lease/ancestry. Report remote
at result and locked local target unchanged. Keep safety nets until cleanup. Propagation uses the same gates.
