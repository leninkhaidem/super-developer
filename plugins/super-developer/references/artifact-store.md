# Artifact Store Boundary

## Boundary

This shared reference owns the artifact-root/code-root contract for planned-feature artifacts. Detailed
worktree commands, helper flags, package execution, review gates, audit gates, and cleanup prompts stay in
the workflow or helper reference that owns that action.

## Core Contract

- Artifact root: the selected root for one feature's planning/task store. With the sidecar model it is
  `.worktrees/<feature>/artifacts`.
- Artifact branch/ref: the orphan, artifacts-only sidecar branch `artifacts/<feature>` checked out at the
  artifact root.
- Code root/worktree: the active source checkout used for production, reference, test, and validation code.
  It may be the main repo, an integration worktree, a package worktree, or an audit worktree.
- Artifact paths are rooted at the artifact root: `.planning/<concept-slug>/`,
  `.tasks/<feature>/`, package proofs/reports, review state, Semgrep evidence when enabled, and minimal
  lifecycle metadata.
- Code paths are rooted at the code root/worktree: source files, plugin files, tests, scripts, generated code,
  and command execution that requires a real code checkout.
- The artifact worktree is not a full code checkout. Do not require source files, plugin files, dependencies,
  or source validation to run from it.
- The sidecar branch is not deliverable code. Do not merge `artifacts/<feature>` into `main`, a feature
  branch, or a package branch.
- Legacy/current-root artifact stores remain valid only when explicitly selected as the artifact root. A
  workflow must still name or carry artifact-root and code-root semantics; do not rely on chat-only defaults.

## Slug Contract

- Conceptualize derives `<concept-slug>` autonomously; that value is the default `<feature>` artifact slug.
- The default mapping is exact for `artifacts/<feature>`, `.worktrees/<feature>/artifacts`,
  `.planning/<concept-slug>/`, and `.tasks/<feature>/`.
- Do not ask the user for routine slug naming or confirmation.
- If a later step needs a different feature/artifact slug, stop before creating divergent paths. Continue only
  with explicit user-approved rename/migration metadata covering `.planning/`, `.tasks/`, the sidecar branch,
  and the artifact worktree path.

## Consumer Rules

- Any workflow that creates, reads, validates, pushes, or cleans artifacts must make the artifact root explicit
  in durable packets, prompts, commands, or metadata.
- Resolve `.planning/` and `.tasks/` paths against the artifact root; resolve code references against the code
  root. Never infer artifact locations only from `Path.cwd()` or the current code checkout.
- Pass helper/plugin paths from the code root when a validator or script needs plugin files; the artifact
  worktree must not be treated as the plugin source.
- Invoke `sliceproof.py` with `--artifact-root <artifact-root>` and `--code-root <code-root>` when the
  roots differ; omitted flags select the current directory for both roots.
- Forbidden behavior checks must falsify: artifacts written only to the current code checkout, a required full
  code checkout in the artifact worktree, sidecar merges into `main`, `artifacts/<feature>` treated as
  deliverable code, silent slug divergence, and chat-only artifact-root assumptions.

## Shared Lifecycle Vocabulary

- Sidecar checkpoint: an artifact-root commit/push to `origin artifacts/<feature>` at an accepted lifecycle
  gate. Checkpoint commands run from `.worktrees/<feature>/artifacts`, not a code worktree.
- Accepted checkpoint gates: after Conceptualize before planning, after accepted review-plan before
  implementation, after each package delivery/WP merge-push boundary, and after final integrated
  review/audit acceptance before target merge/cleanup.
- Do not checkpoint after every incidental edit, and do not push `main`, `feature/<feature>`, or
  `wp/<feature>/<WP-ID>` as an artifact side effect.
- Package-delivery checkpoint: the sidecar checkpoint associated with a work-package delivery boundary after
  package proof/report artifacts are written.
- Active sidecar: any feature package, integration, review, audit, target-merge, or release work still needs
  the artifact root, or final target merge/push is incomplete.
- Cleanup eligibility: after final target merge/push only; local or remote sidecar deletion still requires the
  user's exact approved cleanup action.

## Reference Economy

Centralize durable sidecar doctrine here. Other shared references may point here one hop and should restate
only the local safety-critical path or command fact needed at their action point.
