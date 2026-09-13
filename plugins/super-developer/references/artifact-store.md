# Artifact Store Boundary

## Boundary

Owns planned-feature artifact-root/code-root semantics. Worktree commands, helper validation, package execution,
review/audit, publication, and cleanup stay with the workflow that performs that action.

## Core Contract

- **Artifact root:** the selected store for one feature, normally `.worktrees/<feature>/artifacts`.
- **Artifact ref:** orphan artifacts-only branch `artifacts/<feature>` checked out at the artifact root.
- **Sidecar setup:** create the orphan worktree immediately before the first actual durable artifact write. Invocation,
  discussion, slug resolution, or a chat-only result creates nothing. Local setup performs no push. `git worktree add`
  refuses a non-empty path; `--orphan` needs git >= 2.42, otherwise stop and report.
- **Code root/worktree:** the source checkout used for production, reference, test, generated, and validation code. It
  may be the root checkout, a package worktree, the integration/top worktree, or an audit worktree.
- Artifact paths resolve under the artifact root: `.planning/<concept-slug>/`, `.tasks/<feature>/`, package reports,
  review state, Semgrep evidence, and minimal lifecycle metadata.
- Code paths resolve under the code root: source, tests, scripts, generated files, plugin files, and commands that need
  a real source checkout.
- The artifact worktree is not a code checkout. Do not require source files, dependencies, or validation there.
- The sidecar is not deliverable code. Never merge `artifacts/<feature>` into a code branch.
- Legacy/current-root artifact stores remain valid only when explicitly selected; still carry both artifact-root and
  code-root semantics in durable packets, prompts, commands, or metadata.

## Slug Contract

- Conceptualize derives `<concept-slug>`; that is the default `<feature>` artifact slug.
- The mapping is exact for `artifacts/<feature>`, `.worktrees/<feature>/artifacts`,
  `.planning/<concept-slug>/`, and `.tasks/<feature>/`.
- Do not ask for routine slug naming. If a later step needs a different slug, stop until the user approves rename or
  migration metadata for `.planning/`, `.tasks/`, the sidecar ref, and the artifact worktree path.

## Consumer Rules

- Resolve `.planning/` and `.tasks/` paths against the artifact root; resolve code references against the code root.
  Never infer either only from `Path.cwd()` or the current checkout.
- Pass helper/plugin paths from the code root when validators need plugin files.
- Invoke `sliceproof.py` with absolute `--artifact-root <artifact-root>` and `--code-root <code-root>` whenever the
  roots differ. Omitted flags select the current directory for both roots.
- `--code-root` is the trust anchor for code/file evidence. Derive it from resolved git/worktree state, never from
  report, Slice, or artifact text. A report's `Worktree` field is descriptive.
- Forbidden behavior checks must falsify: artifacts written only to a code checkout, source required in the sidecar,
  sidecar merges into code, `artifacts/<feature>` treated as deliverable, silent slug divergence, and chat-only
  artifact-root assumptions.

## Example

For feature `auth`, `$PROJECT_ROOT/.worktrees/auth/` contains:

```text
artifacts/  branch artifacts/auth   <- artifact root: .planning/<slug>/ and .tasks/auth/...
wp-WP1/     branch wp/auth/WP1       <- code root while implementing/verifying WP1
wp-WP2/     branch wp/auth/WP2       <- code root while implementing/verifying WP2
merge/      branch feature/auth      <- code root for integrated/final checks
```

The artifact root is fixed for the feature. The code root is the worktree holding the code under check, so package
workers edit `.worktrees/auth/wp-WP1/` while writing the assigned result at
`.worktrees/auth/artifacts/.tasks/auth/reports/WP1.package-verification.md` only through the supplied absolute path.

Helper calls keep `$ARTIFACT_ROOT` constant and bind `$CODE_ROOT` per gate:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-package-complete \
  --artifact-root "$PROJECT_ROOT/.worktrees/auth/artifacts" \
  --code-root "$PROJECT_ROOT/.worktrees/auth/wp-WP1" \
  ".tasks/auth/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-final \
  --artifact-root "$PROJECT_ROOT/.worktrees/auth/artifacts" \
  --code-root "$PROJECT_ROOT/.worktrees/auth/merge" \
  ".tasks/auth/tasks.json"
```

## Lifecycle Vocabulary

- **Sidecar checkpoint:** artifact-root commit/push to `origin artifacts/<feature>` at an accepted lifecycle gate, run
  from `.worktrees/<feature>/artifacts`.
- Source, target, and sidecar publication are separately authorized. One approval may list multiple exact actions;
  absent sidecar authorization, local artifacts remain usable but are reported unpublished.
- Checkpoint-eligible gates: after Conceptualize actually writes durable artifacts and before planning; after accepted
  review-plan before implementation; after each package delivery boundary; after final integrated review/audit before
  target merge/cleanup. Invocation, chat-only results, source cadence, and incidental edits do not create eligibility.
- Package-delivery checkpoint: the sidecar checkpoint after package result artifacts are written.
- Active sidecar: feature package, integration, review, audit, target-merge, or release work still needs the artifact
  root, or final target merge/push is incomplete.
- Cleanup eligibility: after final target merge/push only; local or remote sidecar deletion still requires exact
  approved cleanup.

## Reference Economy

Centralize durable sidecar doctrine here. Other references may point here one hop and should restate only the local
safety-critical path or command fact needed at their action point.
