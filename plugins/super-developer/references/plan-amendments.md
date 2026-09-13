# Mechanical Plan Amendments

## Boundary

This is the only inline-edit exception to planner-owned artifact authoring. Load it before classifying or applying
an amendment in planning, plan review, or implementation. It grants no write scope and never replaces semantic
planning or review.

## Whitelist

An edit is mechanical only when existing approved authority determines one exact correction:

- Markdown presentation or explanatory spelling outside protected meaning;
- a duplicated bookkeeping locator corrected to an independently established, already-approved in-root locator;
- JSON formatting or display order with every value and meaning unchanged.

The exception permits **no** change to requirements, behavior, scope, risk, manual exceptions, Acceptance items or
IDs, commands or expected outcomes, evidence, package/work identity, ownership, dependency edges, Slice assignments,
approvals/deferrals, report evidence, Plan gaps, verification depth, roots, or reviewed-state binding. A locator
edit cannot move/rename a file, redirect a command, select among plausible targets, or change a code/evidence root.
Never renumber or reuse a package ID. Length does not make an edit mechanical; uncertainty uses normal repair.

## Procedure

1. Confirm active authority covers the exact safe artifact target and that no user change will be overwritten.
   Establish the authoritative before/after values from existing files.
2. State the exact correction and why every protected meaning above is unchanged. Record a concise note in existing
   package Notes or the caller's existing decisions record; create no ledger or approval artifact.
3. The owning orchestrator applies only that edit. Workers may report candidates but gain no artifact authority.
4. Re-open the files, inspect the exact diff against the whitelist, and run `sliceproof.py validate-plan` with
   explicit artifact/code roots. Ambiguity or failure returns to planner-owned repair.
5. Reuse unaffected semantic review only for proven equivalence. Initial review and plan approval remain mandatory;
   helper success cannot mark an unreviewed plan reviewed. Any semantic change follows normal review and approval.
6. If a frozen final-gate input changed, establish a new integrated freeze and apply existing same-state
   review/audit freshness rules.

Missing write authority or a new semantic/risk decision returns to the user-facing owner. Nonmechanical
same-requirement defects use `implementation-plan` and focused `review-plan` during implementation, or ordinary
initial planning/review before approval. Never send a plan-owned defect to a code repair worker.
