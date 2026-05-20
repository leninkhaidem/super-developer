# Pipeline Fix Actions

Load this reference only after `pipeline-report.md` has produced **ISSUES FOUND** or an allowed
pipeline `fix` action needs fix batching, proof-impact/dirty-proof handling, widened verification,
escalation, or Fix Verification Review handoff. Clean reviews stop at `pipeline-report.md` and final
audit readiness; they do not load this fix-path reference.

`pipeline-report.md` owns pipeline report slots, verdict selection, package coverage input, and the
clean-path stale-state/audit-readiness gate. Load `decision-filter.md` only when a pipeline fix may
require a design-decision card.

## Pipeline Fix State Snapshot

In planned-feature pipeline context, use exactly one orchestrator-owned lightweight snapshot:

```text
.tasks/<feature>/reviews/review-code-state.json
```

This file is review/fix-loop governance state only. It is not proof, audit evidence, task lifecycle,
package proof content, a review transcript, an event stream, or a second acceptance ledger. Do not
write per-round review state files or store full finding bodies, transcripts, package proof evidence,
or task status in the snapshot.

The compact snapshot must include the current versions of these fields:

- `schema_version`, `feature`, `mode: "pipeline"`, `updated_at`.
- `reviewed_state`: feature ref/head, base ref/SHA, target ref, reviewed diff or diff checksum,
  reviewed file list/status checksum, and merge worktree metadata.
- `lenses`: one compact row per required discovery lens with requested depth, completion status, and
  concrete coverage pointer/summary.
- `findings`: confirmed serious finding dedupe keys with severity, Skeptic verdict, current status,
  and assigned fix batch when applicable.
- `fix_batches`: bounded current/recent batch records with batch id, assigned dedupe keys, delegated
  fix commit(s), batch state, dirty-proof/proof-impact status, and Fix Verification Review
  reference/verdict summary.
- `closure_status`: open/closed/reopened dedupe keys, serious fix-regression status, and audit
  readiness flag.
- `widening_triggers`: trigger name, affected scope, and open/complete state.
- `escalation_tier`: `none`, stronger-fix-agent, specialist/widened verification,
  stronger-discovery, semantic-split, or authority-boundary tier.

Overwrite or refresh this snapshot in place after discovery review, fix-batch planning/delegation,
fix commit handoff, Fix Verification Review, widened verification, escalation, and audit-readiness
calculation. Keep only bounded current governance status; if more detail is needed, point to the
current review report, fix report, or verification result instead of appending history.

Sub-agents receive bounded packets derived from the snapshot: reviewed-state metadata, assigned
dedupe keys, current fix-batch id, relevant closure/widening status, target paths, and proof-impact
or dirty-proof context. They do not own, edit, or freely mutate `review-code-state.json`; they report
results to the orchestrator, and the orchestrator validates and refreshes the snapshot.

Before any pipeline fix, fix verification, widened review, escalation decision, or audit-readiness
handoff, validate the snapshot. Fail closed when it is missing, malformed, stale, contradictory, or
for the wrong feature/mode/state. Validation must at least parse JSON, check required fields/enums,
reject duplicate or unreferenced dedupe keys, ensure fix batches reference known findings, ensure
open dirty-proof entries prevent `closure_status.ready_for_audit`, ensure
`closure_status.ready_for_audit` is false when any known serious finding/regression/trigger remains
open, and bind `reviewed_state` to the Stale-State Gate lineage. A failed validation means the
pipeline is not ready; regenerate the snapshot from current review artifacts or rerun the appropriate
discovery, fix verification, or widened review gate instead of inferring a clean state.

## Pipeline Auto-Resolve Sequence

Pipeline auto-resolve uses this governed sequence instead of a full review after every fix batch:

1. Run the initial discovery review through the shared review pipeline and Skeptic verification, then
   initialize or refresh `review-code-state.json` with the reviewed state, required lenses, confirmed
   serious dedupe keys, and initial closure status.
2. If the verdict is **ISSUES FOUND**, group confirmed 🔴/🟠 findings into coherent fix batches,
   refresh the snapshot with the planned batch, and run the Stale-State Gate before delegating each
   batch.
3. The Fix Implementer commits each delegated fix batch before verification; record the delegated fix
   commit(s) in the snapshot and run Pipeline Fix Verification Review for the assigned dedupe keys.
   Track affected package proofs as a dirty set for the batch, but do not refresh/reaccept proofs for
   failed or partial intermediate states.
4. If every assigned finding is `closed`, no serious fix-introduced regression is found, and no
   widening trigger fires, refresh closure status with the current post-fix lineage as verified,
   refresh/revalidate/reaccept dirty affected package proofs once, and continue with any remaining
   known confirmed serious findings.
5. If a verdict is `partially_closed`, `not_closed`, or `reopened`, or a serious fix regression /
   widening trigger appears, refresh widening/escalation status and route to the governed widening or
   escalation flow; do not rerun full discovery by default and do not reaccept dirty proofs until the
   relevant fix batch is verified closed.
6. Enter audit readiness only after snapshot validation passes, all known confirmed serious findings
   are fixed and verified closed, required widened checks are complete, affected dirty package proofs
   are refreshed and accepted, and no unresolved serious regression remains.

There is no arbitrary pass-after-N limit: a known confirmed serious finding blocks readiness until it is fixed and verified `closed`; if an authority boundary is reached, stop instead of marking the pipeline ready. Auto-resolve remains frictionless, but repeated attempts for the same dedupe key must change strategy, evidence, scope split, reviewer/fixer strength, or verification seam instead of repeating the same prompt with more tokens.

## Design-Decision Filter

Load `decision-filter.md` when a pipeline fix may require a product or architecture choice. It owns promotion rules, examples, blanket-mode non-bypass rules, and decision-card display handoff. Pipeline-specific side effects and stale-state gates remain below.

## Pipeline Gated Actions

| Keyword | Action |
|---|---|
| `fix` | Pipeline-context only: follow the Pipeline Auto-Resolve Sequence: delegate confirmed 🔴 and 🟠 findings in coherent batches by root cause, work package, risk class, or shared invariant, then run Fix Verification Review for the assigned dedupe keys. Under blanket/auto-resolve mode, design-decision findings require a decision card first; all other eligible fixes are delegated silently after state revalidation passes. |
| `details <N>` | Expand finding N with full context and recommended fix. Return to gated actions. |
| `abort` | No changes. Close review. |

`commit` is not offered as a separate pipeline action. Use `fix` to delegate corrections; the Fix
Implementer commits each delegated batch in the merge worktree before Fix Verification Review.

## Fix Implementer Packet

Each Fix Implementer receives:

- Confirmed 🔴 and 🟠 findings, including dedupe keys, Skeptic verdicts, evidence, and recommendations
- Reviewed-state metadata
- `SPEC.md`, `tasks.json`, relevant context bundles, package self-review and targeted package review
  summaries when available, prior audit results when available, affected package proof entries or
  snippets when identifiable, and the proof-impact/dirty-proof map described below
- Exact affected package IDs, task IDs, acceptance criteria, or proof entries when identifiable
- Target paths, current diff, and exact scope boundaries
- User constraints, repository constraints, and mode constraints
- Decision-card outcomes from `decision-filter.md` when any finding required a prompt
- Instruction to avoid unrelated cleanup, opportunistic refactors, broad rewrites, or touching files
  outside target paths unless required to close a confirmed finding

## Package Proof Impact During Pipeline Fixes

`plugins/super-developer/skills/implement/references/package-proof-lifecycle.md` owns accepted/reopened proof state, stale-only refresh, dirty-proof handling, and final proof validation. Pipeline review owns only the pre-fix impact decision that prevents audit readiness from bypassing affected accepted proofs.

Before delegating a pipeline fix batch, build a compact proof-impact map from finding scope, target paths, `tasks.json` package ownership, accepted package proofs, package risk tags, and proof-cited evidence. Include:

- affected package IDs, task IDs, acceptance criteria, or proof entries when identifiable;
- evidence surfaces that may become stale: cited files/symbols, command outputs, manual evidence, targeted-review evidence, or package verification assumptions;
- impact reason, such as touched proof-cited path, changed acceptance behavior, cross-package impact, or `proof_invalidation` widening trigger;
- lifecycle action: no proof surface changed, reopen affected proof before repair, or reopen candidate proof because impact is uncertain.

Local non-bypass gates:

- If accepted proof may be invalidated, load `package-proof-lifecycle.md` and run `taskctl.py reopen-package` for each affected package before repair starts.
- Track reopened/candidate proofs as the fix batch's dirty-proof set. Do not refresh/reaccept dirty proofs for failed or partial intermediate states.
- After Fix Verification Review verifies the batch `closed`, validate refreshed dirty proofs against the integration state and accept them before audit readiness.
- Uncertain impact fails closed: reopen candidate proofs by package/path/risk ownership, or record explicit no-impact evidence that no acceptance criterion, proof-cited artifact, verification command, targeted-review evidence, or audit handoff surface changed.
- `review-code-state.json` may track proof-impact governance status, but it is not proof, audit evidence, or a substitute for accepted package proof lifecycle.

The Fix Implementer must reproduce or locate each finding, state the bug-class/equivalence class for every 🔴/🟠 finding, add or adjust regression/table-driven coverage where applicable, fix minimally, run targeted checks, update affected package proof entries with state-bound evidence when impacted, commit the delegated fix batch before Fix Verification Review, and report unresolved blockers. Do not patch only the exact reported example when the finding represents a class of inputs or states.

## Pipeline Fix Verification Review

After each delegated fix batch has been committed, load `fix-verification.md` and run a delegated Fix
Verification Review for the assigned confirmed findings or dedupe keys. Pass the fix delta, Fix
Implementer report, original finding evidence, reviewed-state metadata, current post-fix state
metadata, and any raised widening triggers.

The Fix Verification Reviewer must report `closed`, `partially_closed`, `not_closed`, or `reopened`
for every assigned finding or dedupe key with concrete evidence, then run the shared serious-regression
sniff over the fix delta and affected surfaces. Non-closed verdicts, fix-introduced serious
regressions, or widening triggers block audit readiness until the pipeline governance flow resolves
them.

Fix Verification Review is not a default full rereview. It must not report unrelated new discovery
findings unless a documented widening trigger requires the orchestrator to widen the review scope.

## Widening and Full-Rereview Triggers

Use `fix-verification.md` trigger names and route to the narrowest affected surface first. Widen only
when evidence shows one of these triggers:

- `scope_expansion` — the fix needs files, behavior, tasks, or user-visible scope beyond the approved finding scope.
- `public_api_or_schema_change` — public API, exported contracts, CLI/user interface, persistence schema, generated contracts, or migrations changed.
- `sensitive_risk_surface` — concrete evidence shows security, privacy, safety, data integrity, concurrency, or performance behavior changed or became newly implicated beyond the assigned closure/regression sniff.
- `cross_package_impact` — multiple planned-feature packages, package boundaries, or integration assumptions are affected.
- `proof_invalidation` — package proof evidence, acceptance criteria, tests, or audit handoff may no longer match the final state.
- `large_delta` — the fix delta is too large or broad to verify confidently as one isolated patch.
- `non_closed_verdict` — any assigned finding is `partially_closed`, `not_closed`, or `reopened`.

Widening actions prefer targeted affected-surface verification, specialist review for the triggered
risk domain, or semantic-batch review. Full discovery rereview is reserved for broad deltas whose
affected surfaces cannot be isolated or whose scope invalidates the original discovery review. Even
after widening, known confirmed serious findings still block readiness until fixed and verified
`closed`.

## Automated Strategy Escalation

Auto-resolve changes strategy by failure mode before asking the user:

| Failure mode | Escalation |
|---|---|
| Same dedupe key remains `not_closed` or `partially_closed` after a same-scope fix | Delegate to a stronger Fix Implementer with the bug-class/equivalence-class evidence, reproduction notes, and required regression coverage. |
| Fix patched the example but missed the class of states | Expand the fix packet to the whole equivalence class and require table-driven or scenario coverage before another Fix Verification Review. |
| Fix introduced a serious regression on a risk surface | Use the matching specialist or stronger Fix Implementer for that surface, then rerun delta verification for the affected findings and regression. |
| Finding was `reopened` after prior closure | Compare the post-fix lineage, identify the reverting or conflicting delta, and delegate a fresh fix with regression evidence. |
| Widened verification finds same-surface serious issues missed by discovery | Run a stronger Discovery Reviewer or specialist on that affected surface, not a whole-feature rereview by default. |
| Scope keeps expanding, crosses packages, or invalidates proofs | Split the work into smaller fix batches by package/surface and refresh affected proof handling before audit readiness. |
| Delta is too broad to isolate | Batch by semantic surface; use full rereview only if semantic batching cannot preserve review confidence. |

Do not merely repeat the same fix or review prompt with more tokens. Escalation should change the
agent strength, scope split, evidence requirement, specialist lens, or verification seam. If the next
automated step cannot name what changed about the strategy and what bounded evidence would prove
closure, route to the no-viable-verification-seam authority boundary instead of looping.

## User Authority Boundaries

Ask the user only when auto-resolve reaches an authority boundary:

- Product or design behavior change.
- Scope expansion beyond the accepted SPEC/tasks or beyond the user's reviewed intent.
- New dependency, service, credential, external account, or integration.
- Destructive, externally visible, credential-sensitive, network-sensitive, or unsafe command/action.
- Security, privacy, safety, data-loss, or other risk acceptance rather than a fix.
- Missing required credentials, external facts, permissions, or environment access.
- No viable verification seam remains after automated escalation.

Hard work, a large but batchable diff, or a repeated same-class failure is not by itself a user-stop
condition; use the escalation ladder first.

## Stale-State Gate

Pipeline side-effect gates stay tied to the reviewed state captured before discovery review, plus the
committed post-fix lineage produced by delegated fix batches before verification. Treat this gate as
the state-binding portion of `review-code-state.json` validation; the snapshot cannot be used for fixes,
verification, widening, escalation, or audit readiness unless this lineage check also passes. Before
the first pipeline fix action, revalidate that all still match the discovery reviewed state:

- Feature branch head
- Base branch and base SHA/ref
- Reviewed diff checksum or exact saved diff
- Reviewed file list and status
- Merge worktree metadata

After a delegated fix batch is committed before verification, the feature branch head may advance only
by the recorded Fix Implementer commit(s) for that batch. For follow-up fixes or audit readiness,
revalidate the current lineage as:

discovery reviewed state → delegated fix commit batch(es) → Fix Verification Review verdicts → any
triggered widened review/escalation results.

The base/target ref, merge worktree metadata, and reviewed state binding must remain stable except for
recorded delegated fix commits and documented widened scopes. Reject unexpected commits, broadened file impact,
missing fix-verification verdicts, ambiguous lineage, or changed base state and instruct the user to
rerun the appropriate review gate. Pipeline fixes use the delegated Fix Implementer contract above;
the main agent does not apply substantive production/test/documentation fixes inline.
