# Local Gated Actions

Load this reference only after local scope detection/setup/review/report is complete and the user has
reached the gated action phase. It owns local fix, verification, commit, details, and abort behavior.
Shared discovery review output may recommend fixes, but local code mutation starts only after an
explicit `fix` action or an existing blanket-mode authorization under this reference; pipeline
auto-resolve authority does not leak into ordinary local mode.

## Phase 5 — Gated Actions

Only proceed when the user responds with one of these keywords:

| Keyword | Action |
|---|---|
| `fix` | Delegate fixes for confirmed 🔴 and 🟠 findings to a Fix Implementer, then require delegated Fix Verification Review before any post-fix commit or readiness action (Workflow A below). |
| `commit` | Stage and commit the reviewed state as-is — only if no 🔴 BLOCKERS and state revalidation passes (Workflow B below). |
| `details <N>` | Expand finding N with full context, code snippet, and recommended fix. Return to Phase 5. |
| `abort` | No action. Close session cleanly. |

> Any response other than these keywords → clarification prompt.
> **Never interpret ambiguity, silence, or partial confirmation as approval.**

## Local State Gate

Before mutating files, applying fixes, staging, creating commits, or reporting post-fix readiness, revalidate the immutable reviewed state captured in `local-workflow.md` Phase 0:

- The current branch and `HEAD` SHA still match, unless the only new commits are the approved local fix commits from this flow.
- The reviewed file list and reviewed diff checksum still match for unchanged findings.
- Staged content still matches when `SCOPE="staged"`.
- No new unreviewed files or broadened diff scope appeared.
- The base ref and base SHA still match for branch-diff reviews.

If state is stale or broadened, reject the action and instruct the user to rerun review. Do not partially apply fixes or create a commit against a state that was not reviewed.

---

## Workflow A — `fix`

Triggered when user responds `fix`.

Local fixing has two separate delegated roles:

- **Fix Implementer:** applies bounded fixes for confirmed findings.
- **Fix Verification Reviewer:** uses the shared closure contract in `fix-verification.md` to verify the resulting fix delta and affected surfaces.

The main agent does not implement local review-finding fixes that change code behavior, public surface, tests, documentation structure, or substantive content. Delegate those changes to the Fix Implementer. The main agent may apply only super-simple mechanical typo or formatting fixes inline; report every inline exception explicitly, including why it was mechanical and behavior-preserving.

### Fix Implementer Input

Pass the Fix Implementer:

- Confirmed 🔴 and 🟠 findings, including dedupe keys, Skeptic verdicts, evidence, and recommendations
- Reviewed-state metadata from `local-workflow.md` Phase 0
- Target paths and exact scope boundaries
- User constraints, repository constraints, and mode constraints
- Instruction to avoid unrelated cleanup, opportunistic refactors, broad rewrites, or touching files outside the target paths unless required to close a confirmed finding
- Any decision-card outcomes from the Design-Decision Filter
- For planned-feature contexts, available `SPEC.md`, `tasks.json`, package proofs, and relevant context bundles

The Fix Implementer returns the fix delta, files changed, findings attempted, findings intentionally left unresolved, and any scope-expansion request. A scope-expansion request must identify the exact trigger and why the original scope cannot close the finding.

The Fix Implementer must reproduce or locate each finding, state the bug-class/equivalence class for every 🔴/🟠 finding, add or adjust regression/table-driven coverage where applicable, run targeted checks, and update the affected package proof when a planned-feature criterion or proof entry is affected. Do not patch only the exact reported example when the finding represents a class of inputs or states.

### Local Fix Verification Review

After fixes are applied, run delegated Fix Verification Review by default. Load `fix-verification.md` and pass the shared inputs: the fix delta plus necessary context, original confirmed findings and dedupe keys, reviewed-state metadata, current post-fix state metadata, approved local scope, and widening triggers raised by the Fix Implementer or detected by the main agent.

The Fix Verification Reviewer must use `fix-verification.md` for canonical closure verdicts,
serious-regression sniff, widening trigger names, non-discovery boundary, and non-closed routing.
Local mode keeps only these gates: non-closed verdicts and serious fix regressions block post-fix
commit/readiness, and widening beyond delegated delta review requires a concrete trigger named by
`fix-verification.md`.

Repeated local fix-verification expansion must stop instead of looping indefinitely. After one widened
verification pass, if more scope expansion is still needed or no bounded verification seam remains,
report the unresolved findings, the expansion trigger, and the exact unreviewed scope to the user. Do
not keep widening recursively.

Post-fix commit or readiness actions may proceed only when delegated Fix Verification Review passes,
all assigned findings are `closed`, no new serious regressions are found, no unresolved widening
trigger remains, and the Local State Gate still passes.

---

## Workflow B — `commit`

Triggered when user responds `commit` **AND** no 🔴 BLOCKERS exist.

Before staging or committing, run the Local State Gate. Reject stale or broadened state.

```bash
# Only stage changes if scope was uncommitted or branch diff.
# If SCOPE="staged", the staged area is already set — do NOT modify it.
if [ "$SCOPE" != "staged" ]; then
  # Stage ONLY the files that were included in the reviewed diff — never git add -A.
  $DIFF_CMD --name-only | xargs git add --
fi

# Commit with a summary
git commit -m "<concise summary of changes>"
```

> If 🔴 BLOCKERS exist and the user responds `commit`, **refuse** and report:
> *"Blockers detected. Resolve before committing. Run the review again after fixing, or respond `fix` to attempt delegated fixes."*

---

## Workflow C — `details <N>`

Expand finding N with full context, code snippet, evidence, Skeptic verdict for serious findings, and recommended fix. Do not mutate files or state. Return to Phase 5 after presenting details.

---

## Workflow D — `abort`

No action. Close session cleanly. Do not mutate files, staging area, commits, or review metadata.

---

## Blanket-mode override

When the user has authorized blanket mode (`proceed through all stages` or equivalent), per-finding fix confirmation is replaced by the Design-Decision Filter in `decision-filter.md`; decision cards are displayed using `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/decision-prompts.md`. All other eligible local fixes are delegated to the Fix Implementer silently.

Blanket mode does not bypass the Code Reviewer's baseline security/privacy/safety sniff, Skeptic verification for serious findings, the Local State Gate, delegated Fix Verification Review, blocker commit refusal, or the requirement to stop and report repeated fix-verification scope expansion.
