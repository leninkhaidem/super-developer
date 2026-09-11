# Mechanical Plan Amendments

## Boundary

This is the narrow inline-edit exception to planner-owned artifact authoring. Load it before classifying or
applying a proposed mechanical amendment in planning, plan review, or implementation. It grants no new write
scope and does not replace semantic planning continuation or review.

## Eligible Corrections

An amendment is mechanical only when the existing approved authority determines one exact correction:

- Markdown presentation or explanatory spelling outside requirements, Slice commitments, commands, Acceptance
  Checklists, approval/deferral text, and recorded evidence;
- a duplicated bookkeeping locator that disagrees with its already-approved authoritative locator, where both
  identity and the existing in-root destination are independently established;
- JSON formatting or display order that preserves every value, stable package ID, dependency edge, and meaning.

A locator correction cannot move/rename a file, redirect a command, change a code/evidence root, rebind a reviewed
state, or select among plausible targets. Never renumber packages to make a list contiguous.

## Exclusions

Changes to requirements, behavior, scope, risk, manual exceptions, Acceptance items/IDs, test commands or expected
outcomes, package ownership, dependency edges, Slice assignments, approvals, report evidence, or Plan gaps are
not mechanical. Neither changing a verifier's depth nor closing a finding is a spelling fix. A short edit can
still be semantic; uncertainty uses the ordinary planner/focused-review route, not this exception.

## Procedure

1. Confirm the active authorization covers the exact artifact writes and that the files/targets are safe and
   user changes will not be overwritten. Establish the authoritative before/after values from existing files.
2. State the correction and why every excluded meaning is unchanged. Record a concise amendment note in existing
   package Notes or the caller's existing decisions record; do not create a new ledger or approval artifact.
3. The owning orchestrator may make only that correction. Workers report candidates; they do not acquire wider
   artifact authority from this reference.
4. Re-open the affected artifacts and run `sliceproof.py validate-plan` with explicit artifact/code roots.
   Verify the exact diff against the exclusions. Failure or ambiguous equivalence returns to normal repair;
   never mark reviewed from the mechanical helper alone.
5. Reuse unaffected semantic review without launching a fresh planner/reviewer just for this correction. An
   initially unreviewed plan still needs initial review and approval. Existing reviewed status can be retained
   only for proven mechanical equivalence; semantic changes follow the normal route and approval boundaries.
6. If frozen final-gate inputs changed, establish a new integrated freeze and apply the existing same-state
   review/audit freshness rules. A mechanical amendment never grants an exemption from final-state binding.

## Stop or Route

Missing write authority or a new semantic/risk decision goes to the user-facing owner. Same-requirement plan
repair outside this exception uses `implementation-plan` and focused `review-plan` during implementation, or
the ordinary initial planning/review path before approval. Never send a plan-owned defect to a code repair worker.
