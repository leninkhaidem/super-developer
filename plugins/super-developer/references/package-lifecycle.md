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
6. independent package verification returned `PASS` with a clean deliverable matrix bound to proof/source/code state;
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

Freshness is lost when any package-owned implementation, test, documentation, assignment, proof, report, verification output, Semgrep evidence cited by proof/report, merge-resolution edit, implementer report, or semantic report body changes after proof/report capture.

Freshness is also lost when package Markdown verification expectations/digest, assigned Slice source/digest (`must_satisfy` section digest), assigned Slice set, matrix source snapshot, deliverable matrix rows, or matrix evidence anchors change. `context_only` section-digest drift emits a validation advisory and is non-blocking by default; route it through affected-surface classification before deciding whether evidence refresh is needed.

When freshness is lost, refresh affected proof rows and command/file evidence, rerun `validate-proof` for
every dirty package, rerun focused/full package verification as affected surfaces require, rerun
`validate-package-complete` before acceptance/unlock/final readiness, replace stale reports, and rerun
affected review-code or audit checks when the change occurs after those gates reached readiness.

## Impact Classification and Repair Handling

Before choosing rerun scope for any post-gate repair, merge edit, proof/report refresh, validation advisory, or verification-output change, record a generic affected-surface classification: affected packages, Slice H3s, verification expectations, deliverables, evidence refs, matrix rows, reports, commands, implementation state, contracts, integration seams, safety/security/privacy/data surfaces, review-code state, audit conclusions, and selected rerun scope.

If impact is narrow, bounded, and justified, rerun only targeted checks needed to reestablish freshness. If impact touches delivered behavior, evidence bindings, proof/report/matrix claims, package/Slice source bindings, public or internal contracts, integration seams, safety/security/privacy/data surfaces, stacked readiness, or cannot be bounded, fail closed to broader package verification, review-code, audit, or final validation as applicable. Advisory-only `context_only` drift is classification input rather than a hard blocker by default, but material risk may still be escalated. Do not run full final gates solely because a commit exists when the classification supports targeted refresh.

Before delegating repair, map each confirmed finding or fix batch to affected packages, Slice H3 IDs, proof rows, verification expectations, matrix rows, and proof-cited files/commands when identifiable.

After repair: run relevant commands/inspections, refresh affected proof evidence, rerun `validate-proof`, rerun focused/full package verification, rerun `validate-package-complete`, and rerun affected final code-review or focused/full audit checks as the classification requires. Do not refresh proof evidence for failed or partial intermediate attempts as accepted evidence.

## Report Freshness

A package verification report must bind to package ID, package Markdown path/digest, proof path/digest, assigned Slice paths, section-scoped tier-aware assigned Slice digests, `Matrix Source Snapshot` over package Markdown plus `must_satisfy` section blocks only, worktree, git ref/commit, reviewed verification output, verifier, timestamp, verdict, open findings, and optional Semgrep evidence.

Reports block completion when missing, failed, stale, root-ambiguous, contradicted by code/proof/Slice content, bound to pre-repair evidence, missing state binding, malformed binding, hard-tier section drift, or missing/dirty deliverable matrices. A `context_only_slice_drift` advisory is surfaced for classification and does not block completion by default unless reviewer/auditor judgment finds material risk.

Binding-only refresh is allowed only when semantic verification already reviewed identical code tree/diff, proof content/digest, package Markdown/digest, assigned Slice set and `must_satisfy` section digests/snapshot, implementer report/`SELF_REVIEW`, verification output, deliverable matrix, and evidence anchors. Section changes outside the package's assigned H3s are irrelevant; advisory-only `context_only` drift may be refreshed through State Binding after affected-surface classification finds no material risk. Any uncertainty, repair, merge-resolution edit, proof-evidence change, hard-tier package/Slice/output change, matrix/evidence-anchor change, implementer-report change, or reviewed-code change requires focused/full package verification.

## Final Readiness

Before final review-code or audit, every package in every included task set must have:

- valid package Markdown and mechanically valid proof Markdown;
- no unresolved `GAP`, `OPEN`, `TODO`, unapproved `DEFERRED`, unsupported `N/A`, or Slice plan defect;
- a fresh `PASS` package verification report with clean deliverable matrix;
- a clean `validate-package-complete` result for the current proof/package/report/Slice state;
- closed repair/delta verification and a clean integration worktree for the intended final state.

Run package completion checks for every package, then run root-aware `sliceproof.py validate-final` for each
included artifact root/task set. For bounded stacked readiness, the packet must identify the top integrated
worktree/code state and all relevant task/Slice artifact sets; do not audit only a follow-up task set when the top state includes base feature deliverables; stop if included sets are unknown or omit base deliverables.

This allows dispatching final review-code and final audit against the same top state. Merge/readiness still requires review-code readiness and final audit PASS clean for that state; helper success, registry mutation, manual proof edits, or dashboard output cannot bypass those gates.

## End-to-End Final Loop

1. Complete all packages through the package completion gate and run final package validation.
2. Run final review-code and final audit as sibling checks against the same top integrated state when practical; audit receives review-code state/report when already available, or explicit `none`.
3. Batch compatible final findings, delegate repair, classify affected surfaces (including matrix rows, source bindings, evidence anchors, and stacked readiness), refresh affected proof/report/package-verification state, rerun `validate-proof`/package verification/`validate-package-complete`, and rerun affected code-review plus focused/full audit checks as scope requires.
4. If either final check was not run, is stale, or is affected by repair, run or rerun it before readiness.
5. Declare readiness only when package evidence, review-code readiness, and final audit PASS are clean for the same integrated state.

## Dashboard Rule

Dashboards are read-only. They may surface registry status and dependency readiness; package/proof/report paths; proof validation state; matrix cleanliness; report presence/binding state; `validate-package-complete`/`validate-final` helper result; and review-code readiness state when present.

Dashboards must not mutate lifecycle state or present mechanical signals as semantic proof.
