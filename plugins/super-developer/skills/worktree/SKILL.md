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

- Treat the root worktree as user-owned. Never switch its branch or assume it is on `main`.
- Resolve `PROJECT_ROOT=$(git rev-parse --show-toplevel)` before creating or removing worktrees.
- Keep agent-managed checkouts under `$PROJECT_ROOT/.worktrees/`; ensure `.worktrees/` is ignored.
- Feature branches are refs, not root checkouts. Create `feature/<feature>` from an explicit `<base-ref>`.
- Use `.worktrees/<feature>/merge` as the only checkout of `feature/<feature>` for integration.
- Planned-feature package branches use `wp/<feature>/<WP-ID>` with worktrees at `.worktrees/<feature>/wp-<WP-ID>`.
- Artifact sidecars use orphan ref `artifacts/<feature>` at `.worktrees/<feature>/artifacts`; they are not source checkouts or deliverable refs.
- Package agents never create worktrees, branches, merges, target pushes, or cleanup operations.
- Base and target refs are explicit. Default both to `main`; stacked features may use another feature branch.
- A branch checked out in one worktree is locked for other worktrees; create separate refs instead of reusing checkouts.
- Remove package branches only after `git merge-base --is-ancestor` proves they are included in integration `HEAD`.
- Feature-branch push, sidecar checkpoint push, target merge/push, and cleanup are separate boundaries.
- Never merge or push `<target-ref>`/`main` without explicit approval for that exact target.
- Keep integration, target-merge, and active artifact sidecar worktrees until the authorized lifecycle boundary is complete.
- Clean up only the named feature namespace; never remove another active feature's worktrees or refs.

## Do

1. Identify the active workflow: planned-feature package, bugfix, hotfix, diagnostic spike, cleanup, feature push, or target merge.
2. Resolve project root, current branch/worktree state, base ref, feature ref, target ref, artifact ref, and candidate paths.
3. For planned-feature artifact sidecars, load `../../references/artifact-store.md` before setup, checkpoint, or cleanup.
4. Load `references/feature-package-workflow.md` for planned-feature package, integration, sidecar setup, and checkpoint commands.
5. Load `references/bugfix-hotfix-workflow.md` for diagnostic spikes, feature bugfixes, production hotfixes, or hotfix propagation.
6. Before cleanup, branch removal, feature push, target merge, target push, sidecar deletion, or final teardown, load `references/cleanup-safety.md`.
7. Run commands only from the worktree named by the loaded playbook; never repair convenience by switching the root worktree.
8. Report created refs/worktrees, current checkout paths, approval boundaries, and cleanup candidates before destructive steps.
9. Stop instead of forcing branch deletion, worktree removal, target merge, target push, sidecar deletion, or remote action when proof or approval is missing.

## Load if needed

- Planned feature/package commands → `references/feature-package-workflow.md`
- Artifact-root/code-root terms for sidecars → `../../references/artifact-store.md`
- Bugfix, hotfix, or diagnostic spike commands → `references/bugfix-hotfix-workflow.md`
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

Only remove a package worktree/branch when this check succeeds for that package branch.

## Approval Boundaries

- Creating local package/feature/artifact worktrees requires the approved worktree action, the implementation Execution Contract, or the planned-feature setup step that owns it (Conceptualize or implementation-plan artifact-sidecar setup). Local creation has no remote side effect; the sidecar checkpoint push and sidecar cleanup stay separately gated.
- Sidecar checkpoints push only `origin artifacts/<feature>` from `.worktrees/<feature>/artifacts` at accepted gates.
- Pushing `origin feature/<feature>` is covered by the approved Execution Contract by default when that exact push is named.
- Target merge and target push require explicit approval for the exact `<target-ref>`.
- Sidecar cleanup after final target merge/push requires exact user-approved local worktree, local ref, and remote ref actions.
- Remote branch deletion is never implied by local cleanup, target merge, feature push, or sidecar push;
  release preparation may delete only exact remote refs named in its approved Release Contract.
- Force deletion/removal is allowed only for disposable spikes, exact approved sidecar ref deletion after
  final target merge/push, or a separately proven redundant branch.

## Stop if

- The root worktree would need a branch switch.
- `.worktrees/` is not ignored and cannot be safely ignored.
- Base ref, feature ref, target ref, artifact ref, package branch, worktree path, or cleanup namespace is ambiguous.
- A branch is already checked out elsewhere and the playbook does not provide a safe alternative.
- Merge-base proof fails for package branch cleanup.
- A sidecar checkpoint would push anything except `origin artifacts/<feature>` from the artifact worktree.
- A feature push was not named in the approved Execution Contract.
- A target merge/push lacks exact explicit approval for the named target.
- Cleanup would remove another active feature namespace, dirty worktree, unmerged branch, active sidecar, or safety-net checkout.
- A force push/delete, tag/release action, remote branch deletion, or external side effect is requested but not explicitly approved.

## Output

Return the workflow type, base/feature/target/artifact refs, worktree paths, commands run or proposed,
approval boundary status, cleanup performed or skipped, and remaining safety-net refs/worktrees.
