# Pipeline Review Report and Actions

Load this reference only in planned-feature pipeline context after the shared review pipeline. It owns
pipeline report slots, verdicts, fix implementer packet, and stale-state gates. Load
`decision-filter.md` only when a pipeline fix may require a design-decision card.

## Pipeline Report Slots

Use `report-template.md` with:

- **HEADER:** ``Feature Branch Review — `feature/<name>` vs `<target-ref>` ``
- **METADATA:** ``**Worktree:** `.worktrees/<feature>/merge/` | **Files:** <count> changed``

## Verdict

- **CLEAN** — No 🔴 or 🟠 findings. Pipeline review is ready for final audit; merge approval is only
  appropriate after audit passes.
- **ISSUES FOUND** — One or more 🔴 or 🟠 findings confirmed.

There is no third option. Every review is either clean or has actionable issues.

## Design-Decision Filter

Load `decision-filter.md` when a pipeline fix may require a product or architecture choice. It owns promotion rules, examples, blanket-mode non-bypass rules, and decision-card display handoff. Pipeline-specific side effects and stale-state gates remain below.

## Pipeline Gated Actions

| Keyword | Action |
|---|---|
| `fix` | Pipeline-context only: delegate confirmed 🔴 and 🟠 findings in coherent batches by root cause, work package, risk class, or shared invariant. Use the Fix Implementer packet below. Under blanket/auto-resolve mode, design-decision findings require a decision card first; all other eligible fixes are delegated silently after state revalidation passes. |
| `details <N>` | Expand finding N with full context and recommended fix. Return to gated actions. |
| `abort` | No changes. Close review. |

`commit` is not offered: feature branch code is already committed. Use `fix` to delegate
corrections, which are committed to the feature branch in the merge worktree after verification.

## Fix Implementer Packet

Each Fix Implementer receives:

- Confirmed 🔴 and 🟠 findings, including dedupe keys, Skeptic verdicts, evidence, and recommendations
- Reviewed-state metadata
- `SPEC.md`, `tasks.json`, `verification.json`, relevant context bundles, prior targeted package
  review/audit results when available, and exact acceptance criteria or ledger entries affected
- Target paths, current diff, and exact scope boundaries
- User constraints, repository constraints, and mode constraints
- Decision-card outcomes from `decision-filter.md` when any finding required a prompt
- Instruction to avoid unrelated cleanup, opportunistic refactors, broad rewrites, or touching files
  outside target paths unless required to close a confirmed finding

The Fix Implementer must reproduce or locate each finding, state the bug-class/equivalence class for
every 🔴/🟠 finding, add or adjust regression/table-driven coverage where applicable, fix minimally,
run targeted checks, update `verification.json` with state-bound evidence when a planned-feature
criterion or ledger entry is affected, and report unresolved scope/design blockers. Do not patch only
the exact reported example when the finding represents a class of inputs or states.

## Stale-State Gate

Pipeline side-effect gates stay tied to the reviewed state captured before the review. Before any
pipeline fix or readiness action, revalidate that all still match the reviewed state:

- Feature branch head
- Base branch and base SHA/ref
- Reviewed diff checksum or exact saved diff
- Reviewed file list and status
- Merge worktree metadata

Reject stale, broadened, or ambiguous state and instruct the user to rerun review. Pipeline fixes use
the delegated Fix Implementer contract above; the main agent does not apply substantive
production/test/documentation fixes inline.
