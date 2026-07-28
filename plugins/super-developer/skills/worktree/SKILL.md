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

- Root files/index are user-owned: never switch, edit, merge, or deliver there. Commands may run from
  `$PROJECT_ROOT` to create/remove approved non-root worktrees/refs.
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
- Planned-feature setup may visibly propose `main` only when its owning contract allows. Bugfix, hotfix, and spike
  base/target refs must be explicit and are never inferred.
- A branch checked out in one worktree is locked for other worktrees; create separate refs instead of reusing checkouts.
- Retain all package branches/worktrees throughout active feature work. Ancestry proof is necessary at final
  cleanup but never authorizes incremental cleanup after an individual package merge.
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

1. Identify the active workflow: planned-feature package, planned production-hotfix package, localized bugfix/hotfix, disposable empirical/diagnostic probe, cleanup, source push, or target merge.
2. Resolve project root, state, refs, and paths. For bugfix/hotfix/probe, require explicit base/target refs.
3. For planned-feature artifact sidecars, load `../../references/artifact-store.md` before setup, checkpoint, or cleanup.
4. Load `references/feature-package-workflow.md` for normal planned-feature package, integration, sidecar setup, and checkpoint commands.
5. Load `references/bugfix-hotfix-workflow.md` for disposable empirical/diagnostic probes, feature bugfixes, localized or planned production hotfixes, and hotfix propagation.
6. Before cleanup, branch removal, feature push, target merge, target push, sidecar deletion, or final teardown, load `references/cleanup-safety.md`.
7. Run commands only from the worktree named by the loaded playbook; never repair convenience by switching the root worktree.
8. Report created refs/worktrees, current checkout paths, approval boundaries, and cleanup candidates before destructive steps.
9. Stop instead of forcing branch deletion, worktree removal, target merge, target push, sidecar deletion, or remote action when proof or approval is missing.

## Load if needed

- Planned feature/package commands → `references/feature-package-workflow.md`
- Artifact-root/code-root terms for sidecars → `../../references/artifact-store.md`
- Bugfix, hotfix, or disposable empirical/diagnostic probe commands → `references/bugfix-hotfix-workflow.md`
- Cleanup, branch removal, feature push, target merge, target push, or teardown → `references/cleanup-safety.md`

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

Run this for every package only at whole-feature cleanup. Success proves ancestry but never permits cleanup
before all packages, final integrated gates, remote feature synchronization, and the later delivery boundary pass.

## Approval Boundaries

- Creating local package/feature/artifact worktrees requires the approved worktree action, the implementation Execution Contract, or the planned-feature setup step that owns it (Conceptualize or implementation-plan artifact-sidecar setup). Local creation has no remote side effect; the sidecar checkpoint push and sidecar cleanup stay separately gated.
- Sidecar checkpoints push only `origin artifacts/<feature>` from `.worktrees/<feature>/artifacts` at accepted gates.
- Diagnose bugfix/hotfix branch publication binds remote/ref, source SHA, snapshot, and expected remote SHA/absence.
- Normal planned-feature contracts cover the repeated non-force `feature/<feature>` checkpoint after each
  accepted package merge and remote-SHA verification. Sidecar and planned-hotfix pushes remain separately gated;
  do not claim those contracts contain user-known SHA/snapshot fields.
- Target merge binds source/pre-target SHAs, snapshot, strategy, and non-root worktree. Target push separately binds
  result and expected remote SHA; exact lease plus ancestry enforces compare-and-swap without non-FF rewrite.
- Cleanup binds worktree path/HEAD/state, `local_ref_kind=direct` plus ref/SHA, current landing
  worktree/HEAD/state when ancestry is required, remote expected state, and each action; revalidate all.
- Remote branch deletion is never implied by local cleanup, target merge, feature push, or sidecar push;
  release preparation may delete only exact remote refs named in its approved Release Contract.
- Force deletion/removal is allowed only for disposable spikes, exact approved sidecar ref deletion after
  final target merge/push, or a separately proven redundant branch.

## Stop if

- Root checkout files/index would be switched, written, merged, or used as the delivery checkout.
- `.worktrees/` is not ignored and cannot be safely ignored.
- Base ref, feature ref, target ref, artifact ref, package branch, worktree path, or cleanup namespace is ambiguous.
- A branch is already checked out elsewhere and the playbook does not provide a safe alternative.
- Merge-base proof fails for package branch cleanup.
- A sidecar checkpoint would push anything except `origin artifacts/<feature>` from the artifact worktree.
- A feature push was not named in the approved Execution Contract.
- A target merge or target push lacks its separate exact ref/SHA approval.
- In normal `delivery context: feature`, package cleanup is requested before every package is delivered, verified,
  merged, remotely checkpointed, and retained through final integrated review/audit and the applicable later
  delivery boundary. Planned-hotfix follows its separately contracted hotfix publication/cleanup gate instead.
- Cleanup would remove another active feature namespace, dirty worktree, unmerged branch, active sidecar, or safety-net checkout.
- A force push/delete, tag/release action, remote branch deletion, or external side effect is requested but not explicitly approved.

## Output

Return the workflow type, base/feature/target/artifact refs, worktree paths, commands run or proposed,
approval boundary status, cleanup performed or skipped, and remaining safety-net refs/worktrees.
