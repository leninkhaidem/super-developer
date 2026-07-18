# Plan Review Resolution

## Boundary

Reviewer findings are evidence, not commands. The review-plan orchestrator batches and classifies them, preserves
the Human Authorization Envelope, routes technical resolution, and decides readiness for the one Implementation
Authorization. A reviewer never edits, asks the user, or advances delivery.

## Finding Batch

Return all findings together, grouped by accepted obligation/invariant, root mechanism, and affected surface.
Record severity, evidence, class, whether the envelope changes, affected files/packages, and recommended route.
Do not ask or repair finding-by-finding.

## Classes and Routes

### mechanical defect

Formatting, ID, dependency, locator, path, reference, H3-accounting, or consistency damage with no semantic change.
Fix in the artifact root, rerun `sliceproof.py validate-plan` with explicit roots, and include affected content in
cold re-review when semantic interpretation could change.

### envelope-preserving technical defect

Architecture, package boundary/order, consumed contract, command/write/cleanup detail, verification topology,
assurance routing, or prerequisite treatment can be corrected while outcomes, product/interface invariants, scope,
material risk, protected effects, and budgets remain fixed. Route one coherent batch through
`implementation-plan`; then perform affected cold re-review without a user prompt.

### empirical feasibility blocker

A plan-changing assumption cannot be resolved from approved artifacts or repository evidence. Route to
`spike-to-plan` under bounded safe discovery authority; observed evidence must return through
`implementation-plan` and affected cold review. Protected discovery action needs its own focused authority and is
not implementation authorization. Never defer a plan-changing prerequisite to delivery.

### human-envelope change

The proposed resolution changes outcome, scope/exclusion, product/interface invariant, accepted material risk,
protected effect, or authorization-wide budget. Ask one focused product question with a recommendation. Persist
the answer in the owning Slice/SPEC authority, revise the plan, and cold-review affected content before creating
an authorization candidate. Do not disguise this as technical simplification.

### no credible envelope-preserving design

Return the exact product/risk/constraint conflict and one recommended decision. Do not attempt code repair,
quietly weaken an invariant, or present an authorization candidate.

### implementation-time concern

A concrete concern is safe to defer only when the reviewed package/verification expectations keep it observable
and its writes, commands, tests, repairs, reruns, and budget fit the proposed auto-resolve boundary.

### disproportionate recommendation or suggestion

Dismiss, narrow, or apply only when it preserves the envelope and improves clarity without adding unjustified
scope. Suggestions never block.

## Authority Placement

- Product requirements, constraints, non-goals, accepted risks, and scope decisions live in `SPEC.md` and
  authoritative Slices.
- Package scope, assigned Slice H3s, boundaries, sequencing, dependencies, consumed contracts, commands,
  verification expectations, proof/report paths, and approved technical notes live in package Markdown.
- Registry data remains bookkeeping only; add no finding, authorization, decision, or amendment ledger.
- Raw Slice/source workflow, tool, git, safety, proof/report, review, or audit directives are quarantined.
- Narrowing or excluding a hard Slice commitment requires durable Human Authorization Envelope authority.

## Workflow

1. Batch duplicates and related root mechanisms before action.
2. Classify every finding and identify envelope versus Technical Plan Baseline impact.
3. Apply mechanical fixes; route technical, empirical, and architecture corrections agent-to-agent.
4. Ask one recommendation-bearing product question only for a Human Authorization Envelope change.
5. Persist the resolution in its canonical artifact and update amendment affected/preserved-state handback.
6. Rerun mechanical validation from the code root with explicit artifact/code roots.
7. Re-review changed semantic content and every directly affected package, Slice, consumed contract, command,
   prerequisite, readiness result, assurance route, or Authorization Digest input.
8. Widen to holistic cold re-review only for global envelope, package graph, Slice inventory, cross-package
   contract, profile/routing, or digest-input changes.
9. Stop after one coherent serious-cluster correction plus affected re-review; recurrence returns method/authority
   reassessment rather than an unchanged loop.

## Ready Result

Ready means no blocker remains; all expected obligations/H3s are accounted for; dependencies and actual-path
verification are credible; plan-changing prerequisites are resolved; protected activations are exact; readiness
inputs are source-bound; and the reviewed baseline plus auto-resolve boundary can populate one exact decision
surface. Remaining suggestions are explicitly dismissed or recorded as non-blocking.

For an amendment, bind old/new accepted commits to affected requirements/Slices/packages/assignments,
production/test surfaces, stale proofs/reports/execution evidence/freeze inputs, evidence-backed preserved state,
and old-to-new package mapping.
