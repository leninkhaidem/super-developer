---
name: worktree
description: >
  Git worktree strategy for branch-isolated development. Use for planned-feature package work,
  isolated bugfixes, hotfixes, spikes, feature-branch management, or worktree cleanup. Do not use
  for direct implementation without an approved worktree action.
---
# Git Worktree Strategy

Protect the user-owned root worktree by using branch-isolated `.worktrees/` checkouts for package, bugfix, hotfix,
spike, integration, target-merge, and artifact-sidecar work.

## Always

- Root files/index are user-owned: never switch, merge, reset, stash, clean, force, or deliver there. Commands may run
  from `$PROJECT_ROOT` to create/remove approved non-root worktrees/refs. Exact root exceptions: authorized gitignored
  creation of `$PROJECT_ROOT/.superdeveloper/preferences.yml`, and an approved Release Contract post-release fetch plus
  fast-forward of the canonical checkout already on the base branch. Neither permits unrelated root edits or switching.
- Resolve the primary root with the NUL-safe common-directory procedure below; `--show-toplevel` alone may be a linked
  worktree and must not anchor nested `.worktrees/`.
- Keep agent-managed checkouts under `$PROJECT_ROOT/.worktrees/`; ensure `.worktrees/` is ignored.
- Feature branches are refs, not root checkouts. `feature/<feature>` is created from explicit `<base-ref>` and has one
  integration checkout: `.worktrees/<feature>/merge`.
- Planned packages use `wp/<feature>/<WP-ID>` at `.worktrees/<feature>/wp-<WP-ID>`. Normal feature packages integrate
  into `feature/<feature>`. Planned production-hotfix packages integrate into the exact non-root `hotfix/<name>`
  worktree/ref from explicit production base and create no feature ref.
- Artifact sidecars use orphan ref `artifacts/<feature>` at `.worktrees/<feature>/artifacts`. They are not source or
  deliverable refs. Create one only immediately before the first actual durable artifact write.
- Package agents never create worktrees, branches, merges, target pushes, or cleanup operations.
- Auto-resolve may authorize matching receipt-owned probes and focused-reviewed continuation packages; exact current-
  task approval may authorize one diagnostic probe. Both bind base/ref/path, effects, cleanup, clean state, manifests,
  and `remote_action=none`; neither grants package cleanup, root/remote/force, other namespace, or arbitrary authority.
- Other planned setup may propose `main` only when its contract allows. Bugfix/hotfix/spike bases are explicit and
  never inferred. Branches checked out in one worktree are locked; create separate refs instead of reusing checkouts.
- Stabilize each accepted package in a local recovery commit/ref and retain active or retired package worktrees/refs
  through final gates. Whole-feature cleanup removes one only after exact proofs show its tip is integrated, or a
  continuation tip equals its bound creation base.
- Feature-source publication, sidecar push, target merge/push, planned-hotfix publication, and cleanup are separate
  approvals. Load `../../references/source-publication.md` before selecting or executing feature-source publication;
  absent explicit remote authorization the policy is `local-only`.
- Never merge or push `<target-ref>`/`main` without explicit approval for that exact target.
- Keep integration, target-merge, and active artifact sidecar worktrees until the authorized lifecycle boundary is
  complete. Clean up only the named namespace; never remove another active feature's worktrees or refs.

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

Stop on any failure. All managed paths are rooted at `$PROJECT_ROOT/.worktrees/`, even when invocation began inside a
linked worktree.

## Do

1. Identify the workflow: planned-feature package, planned production-hotfix package, localized bugfix/hotfix,
   disposable probe, auto-resolve dynamic resource, cleanup, source push, or target merge.
2. Resolve root, state, refs, and paths. Probe creation validates its envelope or exact current-task approval, then
   records a receipt; cleanup validates both authority and receipt. Other base/target refs are never inferred.
3. For planned-feature artifacts, load `../../references/artifact-store.md`; create/resume a sidecar only when an
   actual durable write is now required, or load its checkpoint/cleanup rules at those actions.
4. Load `references/feature-package-workflow.md` for normal package/integration/sidecar commands. Before selecting or
   executing a feature-source publication gate, also load `../../references/source-publication.md`.
5. Load `references/bugfix-hotfix-workflow.md` for probe/bugfix/hotfix creation and delivery mechanics.
6. For receipt-bound probe cleanup load `references/probe-cleanup.md`; before any removal, push, merge, or teardown
   also load `references/cleanup-safety.md`.
7. Run commands only from the worktree named by the loaded playbook; never fix convenience by switching root.
8. Report created refs/worktrees, checkout paths, approval boundaries, and cleanup candidates before destructive steps.
9. Stop instead of forcing branch deletion, worktree removal, target merge, target push, sidecar deletion, or remote
   action when proof or approval is missing.

## Load if needed

- Planned feature/package commands → `references/feature-package-workflow.md`
- Feature-source cadence or scheduled push → `../../references/source-publication.md`
- Artifact-root/code-root terms, first durable sidecar write, sidecar checkpoint →
  `../../references/artifact-store.md`
- Bugfix, hotfix, or probe creation → `references/bugfix-hotfix-workflow.md`
- Receipt-bound probe cleanup → `references/probe-cleanup.md` plus `references/cleanup-safety.md`
- Other cleanup, branch removal, push, merge, or teardown → `references/cleanup-safety.md`

## Planned Feature Contract

- Base ref: `<base-ref>`; target ref: `<target-ref>`.
- Feature ref/worktree: `feature/<feature>` at `.worktrees/<feature>/merge`.
- Artifact ref/root: `artifacts/<feature>` at `.worktrees/<feature>/artifacts`.
- Package branch/worktree: `wp/<feature>/<WP-ID>` at `.worktrees/<feature>/wp-<WP-ID>`.

`<WP-ID>` is a work package ID such as `WP1`; do not split package-internal steps unless the reviewed plan did.
`<feature>` is the resolved slug; do not prompt for routine remaps.

Package cleanup check from the integration worktree, final cleanup only:

```bash
git merge-base --is-ancestor wp/<feature>/<WP-ID> HEAD
```

Ancestry permits removal; a continuation tip equal to its bound creation base has no unique commit. Otherwise preserve
and report it. No package cleanup occurs before final gates.

## Approval Boundaries

- Fixed creation requires its owning action/contract. A dynamic envelope or exact current-task probe approval authorizes
  matching receipt-owned probe creation/cleanup; only the envelope may also create reviewed continuation packages.
  Neither grants package cleanup, remote action, or implementation.
- Sidecar checkpoints push only `origin artifacts/<feature>` from `.worktrees/<feature>/artifacts` at accepted gates.
- Diagnose bugfix/hotfix branch publication binds remote/ref, source SHA, snapshot, and expected remote SHA/absence.
- Planned-feature source uses the loaded source-publication policy. Non-due/`local-only` runs no source network action
  and cannot block downstream readiness; due pushes must verify remote feature SHA equals integration `HEAD`, or stop
  with recovery refs retained. Sidecar and planned-hotfix pushes stay separately gated.
- Target merge binds source/pre-target SHAs, snapshot, strategy, and non-root worktree. Target push separately binds
  result and expected remote SHA; exact lease plus ancestry enforces compare-and-swap without non-FF rewrite.
- Cleanup binds path/HEAD/index/state, direct ref/SHA, landing/base ancestry when required, ownership, and action.
  Probe cleanup records `remote_action=none`; normal delivery cleanup retains separate remote-state bindings.
- Remote branch deletion is never implied by local cleanup, target merge, feature push, or sidecar push. Release may
  delete only exact remote refs named in its approved Release Contract.
- Probe cleanup never forces. Force deletion/removal is limited to separately approved exact sidecar ref deletion after
  final target delivery or another independently proven redundant branch.

## Stop if

- Root checkout files/index would be switched, used as delivery checkout, or written except for the two root exceptions.
- `.worktrees/` is not ignored and cannot be safely ignored.
- Base, feature, target, artifact, package, worktree path, or cleanup namespace is ambiguous.
- A branch is already checked out elsewhere and no playbook alternative applies.
- Merge-base proof fails for package cleanup.
- A sidecar checkpoint would push anything except `origin artifacts/<feature>` from the artifact worktree.
- A feature push is not due under approved cadence, lacks explicit authorization, or cannot verify remote SHA after
  success. Due network/credential/push/mismatch failure stops; non-due/`local-only` runs no source network action and
  raises no publication stop.
- Target merge/push lacks separate exact ref/SHA approval.
- Any active or retired package cleanup is requested before final whole-feature gates. Planned-hotfix follows its
  separate publication/cleanup gate.
- Cleanup would remove another namespace, unowned/uncertain state, unique unmerged package commits, an active sidecar,
  or a safety-net checkout; owned dirty probes must first pass exact receipt cleanup without force.
- Force push, forced deletion, tag/release, remote branch deletion, or external side effect lacks exact approval.

## Output

Return workflow type, base/feature/target/artifact refs, worktree paths, commands run/proposed, approval boundary
status, cleanup performed/skipped, and remaining safety-net refs/worktrees.
