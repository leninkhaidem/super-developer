# Local Code Review Workflow

Local mode owns offline state capture, report, explicit actions, and commit gates. It does not inherit
planned-feature proof/report/audit duties. Review the complete relevant state, including mixed categories.

## Scope and Complete-State Setup

A caller-bound binding must name:

- exact worktree, branch/ref, HEAD SHA, base ref and resolved base SHA;
- separate category manifests/status/content snapshots, including path type and Git/index-compatible mode;
- per-category checksums plus one checksum over the ordered complete snapshot; and
- caller constraints and, when repairs remain parent-owned, `repair_owner` and `repair_contract_path`.

Record empty categories. Each untracked record includes file type, Git/index-compatible mode (`100644`, `100755`,
or `120000`), symlink target when applicable, and content digest or bounded binary provenance. Validate before
dispatch; executable-bit, symlink, type, content, or category drift stops review.

Without caller binding, capture read-only identity and all local categories:

```bash
git rev-parse --is-inside-work-tree
git branch --show-current
git rev-parse HEAD
git status --porcelain=v2 --branch -z
git diff --cached --binary
git diff --binary
git ls-files --others --exclude-standard -z
```

Always resolve a local base ref and SHA for the committed category, even when uncommitted changes exist. Resolve in
this order: explicit caller/user intent; one unambiguous configured upstream; existing local symbolic
`refs/remotes/origin/HEAD`. Do not fetch. Stop if none resolves or plausible sources conflict; never set committed
base to `HEAD` merely because staged, unstaged, or untracked changes exist.

Build NUL-safe manifests and saved snapshots outside reviewed state:

- committed: `git diff --name-status -z <base-sha>...HEAD` and binary diff;
- staged: `git diff --cached --name-status -z` and binary diff;
- unstaged: `git diff --name-status -z` and binary diff;
- untracked: `git ls-files --others --exclude-standard -z`, then type, Git/index-compatible mode, symlink target,
  and content digest/reviewable binary provenance for each path;
- complete: ordered category/path/status/type/mode/symlink-target/content-digest records and one checksum.

Use a recorded local checksum tool; preserve path boundaries and avoid newline-splitting pipelines. Reviewers get
all categories together and inspect final effective content when a path appears in several. Use `complete mixed`
scope when any uncommitted category exists and `branch` otherwise; both include the committed base-to-HEAD delta.
Hard stops: unsafe path, empty complete state, ambiguous base, or identity/snapshot mismatch.

```text
Review Scope: <caller-bound | complete mixed | branch>
State: worktree=<path> ref=<ref> base=<ref/SHA> HEAD=<SHA> snapshot=<checksum>
Files: committed=<n> staged=<n> unstaged=<n> untracked=<n> unique=<n>
Repair owner/contract: <values or review-code local default>
```

Return to the main skill for reviewer dispatch.

## Report and Explicit Action Gate

Use `Local Code Review` with exact binding metadata. `CLEAN` means no confirmed 🔴/🟠 finding for that state;
`ISSUES FOUND` means at least one. Stop after the report for one keyword:

| Keyword | Action |
|---|---|
| `fix` | Authorize only the confirmed repair packet through the ownership rule below. |
| `commit` | Commit unchanged reviewed uncommitted files only when CLEAN and separately authorized. |
| `details <N>` | Expand finding N without mutation. |
| `abort` | End without mutation. |

Silence, initial diagnosis/fix approval, delivery approval, or partial confirmation authorizes nothing. Suggestions
remain report-only.

## Complete State Gate

Before fixing, staging, committing, or readiness claims, recapture and compare worktree/ref, HEAD, base ref/SHA,
every category and type/mode/symlink/content record, complete checksum/file set, and constraints. Reject stale,
broadened, narrowed, recategorized, or newly untracked state. A repair requires Fix Verification, a new complete
binding, and focused re-review; never reuse prior CLEAN.

## Fix Ownership and Action

When caller binding names `repair_owner` and `repair_contract_path`, explicit `fix` returns confirmed findings,
evidence, Skeptic verdicts, decision outcomes, exact binding, target paths, constraints, and the fix action to that
owner. Review-code must not dispatch a generic or contractless worker. The owner dispatches a fresh worker under
its supplied contract, validates the result, and returns a newly bound state for Fix Verification/re-review.

Without caller-owned repair fields, use the review-code parent-supplied Fix Implementer contract. Pass it with the
findings, explicit fix action, complete binding, permitted paths, and constraints; never dispatch contractless.
The worker follows that contract and returns changed/untracked files, checks, and blockers.

Readiness requires closed findings, no fix-introduced serious regression or widening trigger, fresh state, and the
main skill's Fix Verification Gate. After one widened pass, stop if no bounded seam remains.

## Commit, Details, Abort, Blanket Mode

`commit` requires CLEAN unchanged snapshot, Complete State Gate, and separate commit authority. Stage only exact
reviewed staged/unstaged/deleted/untracked manifest files; never use `git add -A`, directory staging, or newline
splitting. Verify index paths, modes, symlinks, types, and content; refuse unreviewed staged paths or drift.
Committed-category history is context, not content to recommit.

`details <N>` expands evidence/recommendation without internal tracking metadata. `abort` mutates nothing. Blanket
mode never bypasses repair ownership, explicit action, product decisions, safety checks, Skeptic, state binding,
Fix Verification, blocker refusal, or repeated-widening stop.
