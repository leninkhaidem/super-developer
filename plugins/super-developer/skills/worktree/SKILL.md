---
name: worktree
description: >
  Git worktree strategy for branch-isolated development. Use for planned-feature package work,
  isolated bugfixes, hotfixes, spikes, feature-branch management, or worktree cleanup. Do not use
  for direct implementation without an approved worktree action.
---
# Git Worktree Strategy
Protect the user-owned root worktree while using branch-isolated `.worktrees/` checkouts for
package, bugfix, hotfix, spike, integration, target-merge, and artifact-sidecar work.
## Always
- Root files/index are user-owned: never switch, edit, merge, or deliver there except for two exact operations:
  create the gitignored developer-local `$PROJECT_ROOT/.superdeveloper/preferences.yml` when its governing contract
  authorizes it, or perform an approved Release Contract's clean canonical-root base normalization and fast-forward
  synchronization. Neither exception permits unrelated root changes. Commands may otherwise run from
  `$PROJECT_ROOT` only to create/remove approved non-root worktrees/refs.
- Resolve the primary root with the NUL-safe common-directory procedure below; `--show-toplevel` alone may be a
  linked worktree and must not anchor nested `.worktrees/`.
- Keep agent-managed checkouts under `$PROJECT_ROOT/.worktrees/`; ensure `.worktrees/` is ignored.
- Feature branches are refs, not root checkouts. Create `feature/<feature>` from an explicit `<base-ref>`.
- Use `.worktrees/<feature>/merge` as the only checkout of `feature/<feature>` for integration.
- Planned-package branches use `wp/<feature>/<WP-ID>` with worktrees at `.worktrees/<feature>/wp-<WP-ID>`.
  Normal feature work integrates into `feature/<feature>`; a planned production hotfix integrates into the exact
  non-root `hotfix/<name>` worktree/ref from its explicit production base and creates no feature ref.
- Artifact sidecars use orphan ref `artifacts/<feature>` at `.worktrees/<feature>/artifacts`; they are not source checkouts or deliverable refs.
- Package agents never create worktrees, branches, merges, target pushes, or cleanup operations.
- An auto-resolve Execution Contract may authorize matching probes and focused-reviewed continuation packages;
  exact current-task approval may authorize one diagnostic probe. Both probe routes bind expected base/full ref/path,
  owned effects and cleanup; neither grants package cleanup, root/remote/force, other-namespace, or arbitrary authority.
- Probe creation proves the base ref equals its supplied expected SHA before/after creation and captures clean
  HEAD/index/worktree plus exact owned manifests. Revalidate every runtime binding; uncertainty stops.
- Other planned setup may visibly propose `main` only when its contract allows. Bugfix/hotfix/spike bases are
  explicit and never inferred.
- A branch checked out in one worktree is locked for other worktrees; create separate refs instead of reusing checkouts.
- Retain every active or retired package worktree/ref through final gates. Whole-feature cleanup removes one only
  when exact bindings pass and its tip is integrated, or a continuation package has no commit beyond creation base.
- Feature checkpoint, sidecar push, target merge, target push, and cleanup are separate boundaries.
- Never merge or push `<target-ref>`/`main` without explicit approval for that exact target.
- Keep integration, target-merge, and active artifact sidecar worktrees until the authorized lifecycle boundary is complete.
- Clean up only the named feature namespace; never remove another active feature's worktrees or refs.
## Primary Root Resolver
Run from any primary or linked worktree. Select the first NUL-delimited `worktree` record from the common Git
directory, canonicalize it, and prove its Git directory is the common directory:

```bash
set -euo pipefail
COMMON_GIT_DIR="$(git rev-parse --path-format=absolute --git-common-dir)"
COMMON_GIT_DIR="$(cd "$COMMON_GIT_DIR" && pwd -P)"
PROJECT_ROOT=""
while IFS= read -r -d '' FIELD; do
  case "$FIELD" in
    "worktree "*) PROJECT_ROOT="${FIELD#worktree }"; break ;;
  esac
done < <(git --git-dir="$COMMON_GIT_DIR" worktree list --porcelain -z)
test -n "$PROJECT_ROOT"
PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd -P)"
PRIMARY_GIT_DIR="$(git -C "$PROJECT_ROOT" rev-parse --path-format=absolute --git-dir)"
PRIMARY_GIT_DIR="$(cd "$PRIMARY_GIT_DIR" && pwd -P)"
test "$PRIMARY_GIT_DIR" = "$COMMON_GIT_DIR"
export PROJECT_ROOT
printf 'PROJECT_ROOT=%s\n' "$PROJECT_ROOT"
```

Stop on any failure. All managed paths are then rooted at `$PROJECT_ROOT/.worktrees/`, even when invocation began
inside a linked worktree.

## Do

1. Identify the active workflow: planned-feature package, planned production-hotfix package, localized bugfix/
   hotfix, disposable probe, auto-resolve dynamic resource, cleanup, source push, or target merge.
2. Resolve root, state, refs, and paths. Probe creation validates its envelope or exact current-task approval, then
   records a receipt; cleanup validates both authority and receipt. Other base/target refs are never inferred.
3. For planned-feature artifact sidecars, load `../../references/artifact-store.md` before setup, checkpoint, or cleanup.
4. Load `references/feature-package-workflow.md` for normal planned-feature package, integration, sidecar setup, and checkpoint commands.
5. Load `references/bugfix-hotfix-workflow.md` for probe/bugfix/hotfix creation and delivery mechanics.
6. For any receipt-bound probe cleanup load `references/probe-cleanup.md`; before any removal, push, merge, or
   teardown also load `references/cleanup-safety.md`.
7. Run commands only from the worktree named by the loaded playbook; never repair convenience by switching the root
   worktree. Only the exact preferences creation and approved release synchronization exceptions in `Always` may
   write or switch the canonical root.
8. Report created refs/worktrees, current checkout paths, approval boundaries, and cleanup candidates before destructive steps.
9. Stop instead of forcing branch deletion, worktree removal, target merge, target push, sidecar deletion, or remote action when proof or approval is missing.

## Load if needed

- Planned feature/package commands → `references/feature-package-workflow.md`
- Artifact-root/code-root terms for sidecars → `../../references/artifact-store.md`
- Bugfix, hotfix, or probe creation → `references/bugfix-hotfix-workflow.md`
- Receipt-bound probe cleanup → `references/probe-cleanup.md` plus `references/cleanup-safety.md`
- Other cleanup, branch removal, push, merge, or teardown → `references/cleanup-safety.md`

## Planned Feature Contract

Use package-centric execution plus one artifact sidecar:

- Base ref: `<base-ref>`.
- Feature ref: `feature/<feature>`.
- Target ref: `<target-ref>`.
- Artifact ref: `artifacts/<feature>`.
- Artifact worktree/root: `.worktrees/<feature>/artifacts`.
- Package worktree: `.worktrees/<feature>/wp-<WP-ID>`.
- Package branch: `wp/<feature>/<WP-ID>`.
- Integration worktree: `.worktrees/<feature>/merge` checking out `feature/<feature>`.

`<WP-ID>` is a work package ID such as `WP1`, not a small task name. Multiple internal package
steps share the same package worktree and branch unless the approved plan split them into separate
work packages. `<feature>` is the resolved feature/artifact slug; do not prompt for routine remaps.

Merge-base cleanup check from the integration worktree:

```bash
git merge-base --is-ancestor wp/<feature>/<WP-ID> HEAD
```

Use this only at final whole-feature cleanup. Ancestry permits removal; a continuation tip equal to its bound
creation base also has no unique commit. Otherwise preserve/report it. No package cleanup occurs before final gates.

## Approval Boundaries

- Fixed creation requires its owning action/contract. The dynamic envelope or exact current-task probe approval
  authorizes matching receipt-owned probe creation/cleanup; only the envelope may also create reviewed continuation
  packages. Neither grants package cleanup, remote action, or implementation.
- Sidecar checkpoints push only `origin artifacts/<feature>` from `.worktrees/<feature>/artifacts` at accepted gates.
- Diagnose bugfix/hotfix branch publication binds remote/ref, source SHA, snapshot, and expected remote SHA/absence.
- Normal planned-feature contracts cover the repeated non-force `feature/<feature>` checkpoint after each
  accepted package merge and remote-SHA verification. Sidecar and planned-hotfix pushes remain separately gated;
  do not claim those contracts contain user-known SHA/snapshot fields.
- Target merge binds source/pre-target SHAs, snapshot, strategy, and non-root worktree. Target push separately binds
  result and expected remote SHA; exact lease plus ancestry enforces compare-and-swap without non-FF rewrite.
- Cleanup binds path/HEAD/index/state, direct ref/SHA, landing/base ancestry when required, ownership, and action.
  Probe cleanup records `remote_action=none`; normal delivery cleanup retains its separate remote-state bindings.
- Remote branch deletion is never implied by local cleanup, target merge, feature push, or sidecar push;
  release preparation may delete only exact remote refs named in its approved Release Contract.
- Probe cleanup never forces. Separately approved force deletion/removal is limited to exact sidecar ref deletion
  after final target delivery or another independently proven redundant branch.

## Stop if

- Root checkout files/index would be switched, written, merged, or used as the delivery checkout outside the exact
  developer-local preferences creation or approved clean release fast-forward synchronization exceptions above.
- `.worktrees/` is not ignored and cannot be safely ignored.
- Base ref, feature ref, target ref, artifact ref, package branch, worktree path, or cleanup namespace is ambiguous.
- A branch is already checked out elsewhere and the playbook does not provide a safe alternative.
- Merge-base proof fails for package branch cleanup.
- A sidecar checkpoint would push anything except `origin artifacts/<feature>` from the artifact worktree.
- A feature push was not named in the approved Execution Contract.
- A target merge or target push lacks its separate exact ref/SHA approval.
- Any active or retired package cleanup is requested before final whole-feature gates. Planned-hotfix follows its
  separately contracted publication/cleanup gate.
- Cleanup would remove another namespace, unowned/uncertain state, a package with unique unmerged commits, an active
  sidecar, or safety-net checkout; owned dirty probes must first pass exact receipt cleanup without force.
- A force push, forced deletion, tag/release, remote branch deletion, or external side effect lacks exact approval.
## Output

Return the workflow type, base/feature/target/artifact refs, worktree paths, commands run or proposed,
approval boundary status, cleanup performed or skipped, and remaining safety-net refs/worktrees.
