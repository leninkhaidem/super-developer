# Package Lifecycle, Proof, and Report Freshness
## Boundary
This reference owns package completion, proof creation/refresh, verification reports, freshness, and non-bypass semantics. Artifact shapes live in `slice-first-artifacts.md`; package sizing lives in `work-packages.md`; command shapes live in `tool-usage.md`.

## Status Signals
Registry package status is routing only: `pending`, `in_progress`, `blocked`, or `done`. Status does not
prove implementation correctness. Dashboards may show status, dependency readiness, proof/report paths,
package matrix cleanliness, and helper results only as mechanical signals.

## Proof Ownership
Each package has one artifact-root proof Markdown file declared in the registry and package Markdown:
`.tasks/<feature>/proofs/<WP-ID>.proof.md`.
Package agents fill or refresh only their assigned proof file and package commits. They do not mark packages done, finalize features, edit unrelated proof files, or reconcile a central evidence ledger.
Proof Markdown owns package evidence for assigned `Must satisfy` H3 IDs and package verification expectations. `PASS` in a proof row is a package-agent claim, not package acceptance.
When Semgrep is enabled or contracted for a package, raw and summary outputs live under the artifact-root
`.tasks/<feature>/semgrep/` and proofs/reports cite paths and digests. These files do not replace
proof/report judgment.

## Pre-Dispatch Proof Creation
Before dispatching a package, create the declared proof placeholder:
```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" create-proof \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" \
  ".tasks/<feature>/tasks.json" --package WP1
```
`create-proof` writes the declared proof under the artifact root, generates closure rows for assigned
`Must satisfy` H3 IDs, and records `Context only` IDs as scope context without closure rows.
Overwrite safety: missing proof creates a placeholder; an existing exact placeholder is idempotent;
edited or filled proof fails closed unless `--force --approved-replacement` includes approval, provenance,
and scope and preserves prior content as described in `tool-usage.md`. Filled evidence must never be silently erased.

## Package Agent Closure
A package agent cannot claim completion until proof Markdown shows:
- every assigned `Must satisfy` H3 ID in `## Slice Closure Table`;
- concrete implementation and verification evidence for every required row;
- `PASS` for every required row, or explicitly approved `DEFERRED`/`N/A` where allowed;
- every package verification expectation covered in `## Acceptance / Verification Closure`;
- exact command/static/manual evidence in `## Commands Run` and `## Files Changed / Inspected`;
- no unresolved `TODO`, `OPEN`, or `GAP` markers;
- no unresolved Slice plan defect, context-only misuse, or contradiction with assigned Slices.

## Mechanical Validation
When a package agent returns, run:
```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-proof \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" \
  ".tasks/<feature>/tasks.json" --package WP1
```
Reject proof handoff when validation reports missing sections, rows, evidence, expectation closure, unsupported statuses, unresolved markers, unsafe paths, or missing proof files. Mechanical validation is necessary, never sufficient.

## Completion Gate
A package may become `done` only after all are true:
1. package Markdown assignment validates mechanically;
2. proof Markdown validates mechanically and closes every required Slice row and verification expectation;
3. required commands or inspections are recorded in proof evidence;
4. the package implementer supplied the required completion statement and `SELF_REVIEW` evidence;
5. no unresolved Slice plan defect, unapproved gap/deviation, or authority-boundary blocker remains;
6. independent package verification returned `PASS` with a clean deliverable matrix and canonical Test Review Scope receipt bound to proof/source/code state;
7. `validate-package-complete` succeeds for the selected package after the report exists and before accepting/merging as complete, marking `done`, unlocking dependents, or final readiness handoff;
8. repairs and delta verification are closed;
9. post-merge or integration changes did not stale proof/report/matrix evidence, or freshness was restored.
Run the pre-done helper as:
```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-package-complete \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" \
  ".tasks/<feature>/tasks.json" --package <WP-ID>
```
Dependent packages stay blocked until each source package has a fresh `PASS` report and clean `validate-package-complete` result. A registry `done` status, proof rows, self-review, or helper success alone cannot prove semantic completion.

## Freshness Rules
Classify what changed semantically before selecting refresh or rerun scope; a changed file or commit alone is
not the classification. Distinguish these surfaces:

- product/assignment inputs: SPEC, package/Slice obligations, expectations, approvals, and source bindings;
- production code, generated runtime artifacts, public docs/contracts, and integration or merge edits;
- test source, assertions/oracles, harnesses/helpers, fixtures/mocks, generators, and test configuration;
- proof/report claims: implementer `SELF_REVIEW`, repair `REPAIR_SELF_REVIEW`, statuses, matrices, risk dispositions, Test Review Scope, and evidence-sufficiency claims;
- execution evidence: command outputs, logs, observations, captured artifacts, timestamps, and Semgrep evidence;
- report metadata: ref/commit/worktree/time/digest bindings that do not alter a claim or evidence body.

Route metadata-only drift to binding-only refresh when semantic inputs, claims—including implementer `SELF_REVIEW` and repair `REPAIR_SELF_REVIEW`—and execution evidence are identical.
For evidence-only change, inspect provenance and the bound command/harness, prerequisites, environment,
assertions, cleanup, and redaction. Rebind only when regenerated evidence has identical bound semantic inputs and
method and a valid, non-contradictory outcome. Failed, inconclusive, or contradictory evidence blocks and routes
to diagnosis and affected verification; it never permits PASS rebinding. Bounded semantic-input, claim,
population, or contract changes may use fresh focused verification. Use full verification when a population or
contract change is material, unbounded, sensitive, shared, or uncertain, or impact crosses package/integration
boundaries. Fail closed when classification or carried inputs are uncertain. Keep the rationale in existing
orchestrator state or proof/report/review/audit artifacts—never a new receipt, field, or lifecycle tier.

## Impact Classification and Repair Handling
Before choosing rerun scope, keep the provisional classification in orchestrator state and repair/verifier
packets; persist consequences only in existing proof/report/review/audit artifacts, never a registry field or
standalone impact receipt. Record package Markdown/digest, assigned Slice source/digest, matrix source snapshot,
matrix evidence anchors, changed class, scope, delta, affected claims/evidence/contracts, and chosen route.
Treat `depends_on` as a sequencing lower bound, not impact proof. Inspect producing prerequisites, consumers in
any lifecycle state, and shared surfaces not represented by a dependency edge. Follow concrete semantic hops
until no new affected surface appears. Failure, commit existence, merge ancestry, or dependency reachability
alone does not stale a package; classify uncertainty as unbounded.
After code repair, reclassify the actual code diff and invalidate newly affected reports. If impact is narrow,
bounded, and justified, use fresh focused verification; widen for sensitive/shared/uncertain impact. Before
repair, map findings to packages/Slices/proof rows/expectations/matrix rows/evidence. Refresh affected proof and
command evidence and run `validate-proof`; reclassify the final code/proof/command-evidence state, repeating
closure and refresh until stable. Only then run fresh focused/full package verification,
`validate-package-complete`, and affected final review/audit gates. Never accept partial intermediate evidence.

## Report Freshness
Reports bind package/proof/Slice sources, matrix snapshot, reviewed code and execution evidence, verifier/time,
verdict/findings, Test Review Scope, and optional Semgrep evidence. Missing, failed, stale, malformed, dirty, or
contradicted bindings block completion. Existing reports without the receipt must be refreshed; no silent bypass applies.
`context_only_slice_drift` is non-blocking by default but requires affected-surface classification.
Binding-only refresh is allowed only under the metadata route above. Evidence-only changes use the guarded
route; invalid outcomes block rather than becoming a PASS binding. Bounded semantic changes may use focused
package verification. Material, unbounded, sensitive, shared, or uncertain population or contract changes require full package verification.

## Final Readiness
Before final review-code or audit, every package in every included task set must have:

- valid package Markdown and mechanically valid proof Markdown;
- no unresolved `GAP`, `OPEN`, `TODO`, unapproved `DEFERRED`, unsupported `N/A`, or Slice plan defect;
- a fresh `PASS` package verification report with clean deliverable matrix and canonical Test Review Scope receipt;
- a clean `validate-package-complete` result for the current proof/package/report/Slice state;
- closed repair/delta verification and a clean integration worktree for the intended final state.

Run package completion checks for every package, then run root-aware `sliceproof.py validate-final` for each
included artifact root/task set. For bounded stacked readiness, the packet must identify the top integrated
worktree/code state and all relevant task/Slice artifact sets; do not audit only a follow-up task set when the top state includes base feature deliverables; stop if included sets are unknown or omit base deliverables.

Role ownership is non-duplicative. Package verification owns local claims, evidence, and package-owned test
deltas. Final review trusts fresh package-local work and owns seams, integration-only/merge changes, and
contradictions; specialists run only for triggered sensitive surfaces. Audit reconciles completeness and
selectively falsifies high-value claims rather than wholesale rereview. Together they validate each fresh
receipt against its package-owned reviewed delta, reconcile the union against the integrated diff, and classify
integration-only test-relevant changes.

## Evidence Freeze and End-to-End Final Loop
1. Finish implementation and repairs; close package completion gates.
2. Run affected focused checks and integrated checks, then finalize runtime evidence, cleanup, and termination.
3. Refresh affected proofs/reports, validate, and freeze exact integrated-code, artifact, and runtime-evidence inputs consumed by final checks.
4. Run final review-code and final audit as sibling checks against the same top state and freeze. Their generated
   reports and governance state are outputs, not freeze inputs; audit receives review-code output or `none`.
5. Batch findings and delegate repairs. Any frozen-input change invalidates the binding, including metadata-only or evidence-only change.
   Classify freshness to select rebind, evidence-focused, focused, or full work; refresh state and freeze again before affected final checks.
6. Declare readiness only when package evidence, review-code readiness and final audit PASS are clean for the
   same frozen inputs; helpers, registry mutations, manual proof edits, or dashboards cannot bypass these gates.

## Observability and Dashboard Rule
Non-gating traces may surface version; stage/package/wave timing; command identity/scope/outcome/cleanup;
readiness, freshness, rerun reason/scope, and repair identity/progress. Dashboards may also show mechanical
lifecycle signals. Neither may mutate state, be required as proof, or present timing/mechanics as completion.
