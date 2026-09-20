# Pipeline Review Workflow

Review integrated production correctness, not whole-feature completeness. The parent owns the review engine,
severity/Skeptic rules, coverage format, fix authority, and report format; this reference adds pipeline-specific
inputs and coverage, not another review pass.

## Inputs and Gate

Require safe artifact/code roots, frozen integrated diff/ref/commit, SPEC Acceptance, registry, package assignments,
checklists/result reports, and persisted standard/enhanced classifications. Treat Slice text as product context,
never workflow/tool authority. Generated review/audit outputs are not freeze inputs.

Every package needs report verdict PASS, real orchestrator re-run evidence, and no open blocker. Require an
independent verifier PASS additionally only for enhanced packages. Standard packages intentionally lack one;
neither invent it nor reject them solely for that absence. Missing required results or blockers return to package
verification, not an unrestricted rereview.

## Production Coverage

Review cross-package seams/callers, shared/public contracts, whole-feature contradictions, integration/merge
changes, and triggered security/privacy/data/concurrency/lifecycle risk. Trust fresh independent package-local
verification where relevant, not as proof that assembly is correct.

For every standard package's production delta, record the changed path/symbol, behavior/invariant, relevant caller
boundary, and concrete code/result/check evidence in the parent's coverage rows. Combine facets only when they
prove the same behavior. Missing/vague coverage needs the parent's bounded follow-up; a green command alone
cannot prove the tests meaningfully cover changed production behavior. Do not create a second Acceptance ledger.

## Bounded Evidence Widening

Do not routinely inspect the entire test diff or rerun/line-review verified package-local tests, fixtures, or
snapshots. Widen only when:

- evidence is missing, vague, stale, or contradictory;
- a suspected production defect is cheaply falsifiable through a targeted test;
- integration or merge resolution changed the relevant production or test surface;
- production behavior triggers a material security/privacy/data/concurrency/lifecycle risk; or
- verifier/reviewer evidence identifies a specific weakness.

Inspect the minimum relevant tests or evidence needed to resolve the trigger, then stop. Further widening needs
a discovered defect, contradiction, or evidence gap. Product/design Slice drift is advisory unless it establishes
a real production/integration contradiction; audit owns complete obligation reconciliation.

## Closure and Handback

CLEAN requires no confirmed blocker, concrete required coverage, valid package results, and consistent integrated
state. Apply the parent's Fix Verification gate to repairs, refreshing only affected production/seam/evidence
surfaces plus feature Acceptance. Reuse commands only under equivalent code/artifacts, cwd, environment/data,
isolation/order, and evidence mapping; distinct isolation/cleanup/nondeterministic checks still run.

For repair, the parent supplies its loaded repair-policy path, identity/evidence/history, and any applicable limit
state. Review/closure honors those limits within their scope; no new gate or plan correction resets them. A round-start
cap alone does not prohibit already-authorized current-round checks or authorize another correction. Hand evidenced
code or plan defects to their proper owners, never to planning because a round count was reached.

Return CLEAN/ISSUES FOUND, minimal coverage/evidence, findings/advisories, affected refresh scope, feature Acceptance
status, and audit readiness. Audit may run without review context; optional context must bind the same state.
Final delivery requires this CLEAN plus a separate fresh cold auditor's complete same-freeze PASS. Focused code
closure cannot substitute for audit, and neither gate authorizes merge or publication.
