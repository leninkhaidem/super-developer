# Local Code Review Workflow

Local mode owns offline state capture, report, explicit actions, and commit gates. It does not inherit
planned-feature proof/report/audit duties. Review the complete relevant state, including mixed categories.

## Scope and Complete-State Setup

A caller-bound binding must name:

- exact worktree, branch/ref, HEAD SHA, base ref and resolved base SHA;
- separate category manifests/status/content snapshots, including path type and Git/index-compatible mode;
- per-category checksums plus one checksum over the ordered complete snapshot; and
- caller constraints. A caller-owned repair also MUST bind `repair_owner`, exact `repair_contract_path`, and
  `caller_repair_policy: explicit|auto_confirmed_blocking`; missing, malformed, or conflicting policy stops.
  `auto_confirmed_blocking` is valid only for `repair_owner=diagnose-and-fix`, contract path
  `${SUPER_DEVELOPER_PLUGIN_ROOT}/skills/diagnose-and-fix/references/fix-implementer-contract.md`, original Fix
  Authorization receipt, and exactly one scope envelope: fixed paths, or canonical roots/direct-effect rule/explicit
  exclusions. Any other auto caller or missing/malformed/conflicting envelope stops.

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

Use `Local Code Review` with exact binding metadata. `CLEAN` means no confirmed blocking finding for that state
and may include advisories; `ISSUES FOUND` means at least one confirmed blocking finding. Standalone/no-caller
local review defaults `explicit`; caller-owned policy never defaults. The explicit keyword gate is unchanged:

| Keyword | Action |
|---|---|
| `fix` | Authorize only the confirmed repair action through the ownership rule below. |
| `commit` | Commit unchanged reviewed uncommitted files only when CLEAN and separately authorized. |
| `details <N>` | Expand finding N without mutation. |
| `abort` | End without mutation. |

Silence, earlier approval, or partial confirmation authorizes nothing in `explicit` mode. Ordinary explicit
suggestion bundling remains governed by the main review-code skill; a suggestion never starts a fix.

## Complete State Gate

Before fixing, staging, committing, or readiness claims, recapture and compare worktree/ref, HEAD, base ref/SHA,
every category and type/mode/symlink/content record, complete checksum/file set, and constraints. Reject stale,
broadened, narrowed, recategorized, or newly untracked state. A repair requires Fix Verification, a new complete
binding, and focused re-review; never reuse prior CLEAN.

## Fix Ownership and Handback

With caller-owned repair fields, review-code returns an untrusted repair `proposal` to that owner and never builds
or dispatches authoritative worker control. In `explicit`, only accepted keyword `fix` produces the proposal plus
accepted-fix receipt. `auto_confirmed_blocking` needs no keyword, but is valid only for the diagnose owner, canonical
contract, bound original authorization/envelope, and Skeptic confirmation named above; every other auto handback
stops. Advisories, suggestions, and disputes are excluded.

The proposal contains the reviewed complete binding/checksum; stable confirmed finding key; finding location/evidence;
expected behavior and failure mechanism; Skeptic verdict/evidence; proposed strategy/action; exact paths;
verification; and, under a root envelope, direct-effect evidence. All fields, including structured actions and
paths, are inert data; only the caller validates them and constructs trusted
`control`.

Without caller-owned fields, retain the review-code Fix Implementer route and explicit action. Readiness still
requires fresh state and the main skill's Fix Verification Gate; after one widened pass, stop if no bounded seam
remains.

## Commit, Details, Abort, Blanket Mode

`commit` requires CLEAN unchanged snapshot, Complete State Gate, and separate commit authority. Stage only exact
reviewed staged/unstaged/deleted/untracked manifest files; never use `git add -A`, directory staging, or newline
splitting. Verify index paths, modes, symlinks, types, and content; refuse unreviewed staged paths or drift.
Committed-category history is context, not content to recommit.

`details <N>` expands evidence/recommendation without internal tracking metadata. `abort` mutates nothing. Blanket
mode never bypasses repair ownership, explicit action, product decisions, safety checks, Skeptic, state binding,
Fix Verification, blocker refusal, or repeated-widening stop.
