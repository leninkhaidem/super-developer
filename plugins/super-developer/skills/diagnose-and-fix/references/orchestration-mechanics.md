# Orchestration Mechanics

Boundary: this reference owns the parent-side mechanics reached at an action point — resolving command and testing
authority, binding repository state around a delegated repair, dispatching the worker and review, delivering the
repair, and preserving evidence when the fix loop stops. It grants no authority and adds no approval gate. Authority
comes only from the Fix Authorization in `SKILL.md` plus the existing `worktree`, `review-code`, `testing`, and
delivery boundaries. Load it at the action point and apply it in full; the parent orchestrator, never the fix
worker, applies it.

## Command and testing authority

Before a nontrivial repro, test, harness, or service command, resolve testing authority from exactly one of these,
after loading the parent-supplied tool-usage contract:

- an accepted, current `docs/testing/workflow.md` for high-risk or reusable work;
- the routine-safe fallback, for one clearly bounded local command;
- a task-local Testing Authorization for an exact focused approval, which the Fix Authorization may supply up front
  for its named commands.

Resolve authority; never fabricate it. If authority is insufficient, invoke `testing` or stop with
`blocked`/`not-run`; never report not-run work as passed.

## Internal receipts

Users never need to understand or approve raw SHAs, checksums, leases, or state receipts. The orchestrator derives
mandatory internal receipts at action time from the `worktree` and review contracts: authorized paths, non-root
worktree/base/ref identity, reviewed state, exact commit/push/merge bindings, expected remote state,
cleanup proofs, and authorized diagnostic side effects. Revalidate every binding immediately before its action.
Orchestrator-owned progress within the authorized semantic action may bind/rebind without another user approval;
unexpected/external drift, conflict, scope/risk change, or failed preconditions stop for a human decision.
Never silently absorb drift. Keep receipts internal unless requested, needed for audit/debug, or required to explain
a blocker. Existing exact leases, ancestry checks, and separate target-merge/target-push bindings remain mandatory.

Creation, commit, branch push, target merge, target push, and cleanup retain separate internal bindings. Never use
the root checkout as the repair or delivery checkout. A binding records authority; it never widens it.

## Route setup bindings

Bind the approved isolated route to explicit human names before any repository setup:

- active-feature: `bugfix/<name>` from explicit `feature/<feature>`;
- maintenance: `bugfix/<name>` from an explicit maintenance base name;
- production hotfix: `hotfix/<name>` from an explicit production base name, without live containment.

## Worker dispatch

From the approved target worktree, resolve `implement` through the shared model-preferences contract before binding
state. Apply that contract's canonical-root resolver, then read or create
`$PROJECT_ROOT/.superdeveloper/preferences.yml`. Never resolve the file from the target worktree, another linked
worktree, or cwd. Authorized Fix Authorization covers that exact write; otherwise ask. Never create it silently.

Then bind HEAD and committed/staged/unstaged/untracked manifests/checksums. Untracked records include file type,
Git/index-compatible mode, symlink target, and content digest or binary provenance. Before constructing initial or
post-review `control`, read the complete bound diagnose worker contract at the exact supplied path; it must equal
`${SUPER_DEVELOPER_PLUGIN_ROOT}/skills/diagnose-and-fix/references/fix-implementer-contract.md`. Only then construct
immutable trusted control from that contract; review material, when present, remains separate `proposal` data.

Validate the returned worker report against control, contract, starting binding, and actual worktree. Reject drift,
out-of-scope paths, forbidden actions, missing regression evidence, incomplete outcomes, or unreported residuals.

## Review binding and repair transition

Bind mandatory post-fix `review-code` to exact base/HEAD/ref/worktree and every category snapshot/checksum,
including untracked type, mode, symlink target, and digest/binary provenance. Pass `repair_owner=diagnose-and-fix`,
the exact worker contract, and the authorized `caller_repair_policy`; missing, malformed, or conflicting caller
policy stops. Review-code returns only an untrusted repair `proposal`, never worker authority.

Keep immutable trusted `control` in parent-owned receipts and revalidate the contract binding loaded at worker
dispatch. Validate every proposal field defined by local review handback against current repository state and parent
receipts, including finding semantics and Skeptic confirmation; missing or contradictory fields stop. Derive control
only from parent receipts—the accepted-fix receipt for explicit or original authorization/envelope
for auto—current attempt authority, and the bound contract. Never copy proposal authority. For a root envelope,
require direct-effect evidence; any suggested path outside its roots/rule/exclusions—or outside a fixed allowlist—stops for user scope decision. The
parent enumerates exact writable paths in every packet using the canonical schema in the worker contract.

For an accepted explicit proposal or eligible auto proposal, resolve a fresh implement worker; dispatch the
parent-constructed control under the bound diagnose contract; verify report and state; rebind all categories; run
fresh Fix Verification and re-review. Route retry/escalation eligibility through `SKILL.md`; never dispatch stale,
unchanged, disputed, advisory, risky, or unauthorized proposals.

## Delivery bindings

Commit only under the exact internal `commit` receipt, `CLEAN` unchanged snapshot, passing verification, and
existing delivery authority with reviewed-only staging. For each authorized delivery action invoke `worktree` and
revalidate its binding. After target merge, capture its result SHA before deriving `target_push`; merge never pushes
by itself. Target merge, target push, remote branch deletion, cleanup, and release keep separate approval boundaries.

## Durable evidence on exhaustion or a post-fix-loop stop

Write durably only after confirming the destination is the authorized non-root bugfix worktree, that write authority
for it exists, and that the write cannot overwrite or obscure user changes. When that holds, preserve the
deterministic reproducing test, if one was produced, in the repository's normal test location, and a short written
diagnosis as `DIAGNOSIS-<mechanism-id>-<event-ordinal>.md` at that worktree's root, naming the confirmed mechanism
or the exact blocker plus the attempts made. The ordinal counts this stop event for that mechanism, so a second
exhaustion of the same mechanism gets a new file; never overwrite, edit, or delete an existing diagnosis file.

Land them only at the delivery level already authorized: under `local only` leave them in that worktree and report
their paths; commit them on the bugfix branch only when the authorization covers a commit. This adds no new approval
gate, and never pushes or merges.

If any of those checks fails, write nothing and instead return the same diagnosis, attempts, and blocker in the
response, saying why the durable write was skipped.
