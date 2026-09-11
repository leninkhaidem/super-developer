# Implement Package Integration Gates

Load after package return and before acceptance, merge, `done`, downstream dispatch, or final readiness. Owns
re-run/result, freshness, repair, and final handoff gates. `worktree` owns git safety. Use the loaded
source-publication packet to decide due feature-source pushes. Artifact checks use artifact root; source validation
uses package/integration roots.

## Package Return Checkpoint

For each returned package:

1. Validate package-agent report, `SELF_REVIEW`, evidence, disclosures, and plan-defect assessment. Route plan-owned
   defects through continuation before code repair or acceptance.
2. Re-run every executable frozen Acceptance Checklist item into the declared result file, recording exit/status and
   bounded output. Failed, skipped, or missing orchestrator re-run is automatic FAIL with no LLM retry.
3. Reject if executable evidence is missing/stale/placeholder, Verdict is FAIL, an item is non-pass, or a blocker
   remains.
4. Run safe package verification expectations from the package or stable integration worktree and record output. Semgrep
   evidence must come from the helper scan command with valid `.tasks/<feature>/semgrep/` raw/summary paths/digests;
   reject stale, escaped, unpaired, raw direct `semgrep`, or raw JSON evidence. Findings are advisory unless authorized
   review/verifier marks material risk.
5. Commit package source/test/reference changes before final result binding so the report names an exact recovery
   commit/ref; for no-delta packages, bind/retain the clean unchanged tip. Never commit ignored `.tasks` artifacts.
6. Read persisted `Verification depth` and reason from `## Notes`. After re-run, dispatch independent verifier only for
   `enhanced`; `standard` skips. Missing, stale, downgraded, or registry-only metadata blocks acceptance.
7. Write or refresh the single declared result report in the shape owned by
   `plugins/super-developer/references/package-verification-report.md`, adding enhanced verifier findings when
   applicable. Open `## Plan gaps` route below and block `done`/dependent unlock until closed in place; never delete one
   to clear the gate.
8. Run the pre-done helper after the result exists and before accepting/merging, marking `done`, unlocking dependents,
   or final readiness:

   ```bash
   python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-package-complete \
     --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" \
     ".tasks/<feature>/tasks.json" --package <WP-ID>
   ```

9. Helper success is mechanical. Semantic truth remains with orchestrator re-run, enhanced verifier when applicable,
   and final audit. `context_only_slice_drift` is reviewer judgement, default non-blocking unless review escalates.
10. Confirm package branches did not force-add/commit ignored `.tasks`; if they did, preserve artifacts in artifact
    root, repair the branch to code/doc changes only, and keep the package incomplete.
11. Merge each accepted branch at most once through integration via `worktree`. Retain feature safety nets until
    cleanup eligibility; planned hotfix uses separate delivery/cleanup gates.
12. After merge, classify semantic impact from behavior/contracts, not descendants: owners/consumers, observable
    contracts, generated/config/migration, dynamic/unknown consumers, shared fixtures/oracles, security/data/concurrency
    invariants, merge resolutions, and evidence-only invalidation. Unknown widens; refresh only affected evidence/seams.
13. Preserve the local recovery commit/ref and close freshness. `local-only` and non-due gates run no network and never
    block readiness. Due remote gates run the source-push packet through `worktree`; remote SHA must equal integration
    `HEAD`, otherwise stop with safety nets retained. Planned hotfix, sidecar, and target publication are independent.

Mark package `done` as local evidence only after re-run PASS, verification expectations,
`validate-package-complete`, ignored-artifact handling, repair/delta closure, and Slice plan-defect gates pass. `done`
alone does not unlock dependents; merge, freshness, and due publication gates must close.

## Plan-Defect Continuation Gate

A plan defect is any readiness/package-agent/verifier/integration/review/audit finding that reviewed artifacts
misstate or omit assignment, acceptance, dependency, result-file, feasibility, or Slice projection. Slice plan defects
include missing projected hard requirements, contradictions, invalid deferral/override metadata, or control-plane text
overriding workflow, tools, git/worktree/package scope, result lifecycle, gates, or higher instructions.

Before amendment classification, consume the plan-amendments contract; only its exact nonsemantic case is inline. If
semantics/scope/visible behavior/risk/manual exceptions stay fixed, invoke `implementation-plan` continuation with
provenance and reports or `none`, then focused `review-plan`. Otherwise stop. Never PASS, mark `done`, unlock, or send
an unresolved plan defect to code repair.

## Report Shape and Re-Verification

Package result reports use `plugins/super-developer/references/package-verification-report.md`; no separate matrix,
receipt, or state-binding artifact exists.

After blocking repair, re-verify affected checklist/result evidence and focused seams, then rewrite reports. Run/reuse
minimum commands only when code/artifact state, cwd, environment/data, isolation/order, and evidence mapping are
equivalent. Exact-state output may be reused; distinct package, isolation, cleanup, and nondeterministic checks run.
Unknown impact widens; unaffected results remain reusable. `context_only_slice_drift` stays advisory.

## Rejection and Repair

Only blocking correctness, security, data-loss, or contract-break findings reject a package; plan-owned findings route
above. Keep a package incomplete while result FAIL, blocker, continuation, or repair remains open. Dependency, failure,
commit, or ancestry alone does not stale unaffected work.

Before repair, record identity, prior outcome, unresolved state, affected packages/paths/checklists/reports/seams, and
screened commands. One worker owns a cluster sharing cause, scope, and verification envelope. Use the loaded
bounded-work contract for observed progress, shared remaining repair time, round history/reassessment, and stop
reporting. Reopen planning only for an evidenced plan defect, never a failed-round count. Stop on non-convergence,
exhausted budget, uncertain cleanup/readiness, missing history/authority/facts, or scope/safety/risk change.

## Conflict Handling

Resolve mechanical conflicts only in integration and never switch root. For substantive logic, API, contract, test,
result-file, package-scope, or design conflicts, abort when possible, keep incomplete, and name conflicting files.
Do not dispatch dependents until conflicts/freshness close.

## Final Readiness Handoff

Before final `review-code` and `audit`, every package must have re-run PASS for every executable frozen AC item,
required evidence, fresh PASS with no blocker, clean `validate-package-complete`, no unresolved Slice defect, clean
integration, branches merged once and retained, and every due feature-source gate completed with remote SHA equal to
its scheduled integration `HEAD`. `local-only` or not-yet-due publication is not a readiness blocker.

For bounded stacked-feature readiness, name the top code state and each relevant task/Slice artifact set, all with
clean package completion and `validate-final` prerequisites. Do not audit only a follow-up set when top includes base
deliverables; stop when sets are unknown/out of scope.

Run affected focused/integrated checks. If final Semgrep is enabled, keep package scans primary and run one integrated
helper scan only for named cross-package/shared risk. Do not widen/fix/rescan without a newly named surface.

Finalize runtime evidence, termination, and cleanup; refresh affected result-file state. Then run from the code root
for every included artifact root/task set:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-final \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" \
  ".tasks/<feature>/tasks.json"
```

Freeze exact integrated code, artifacts, and runtime evidence. Run independent sibling checks on that same freeze;
neither output is a freeze input, substitute, or cross-role authority:

- `review-code` requires `CLEAN` for cross-package seams/integration deltas and every `standard` package production
  delta that lacked an independent verifier.
- `audit` requires a fresh cold same-freeze `PASS` reconciling all retained/refreshed package and SPEC Acceptance
  evidence, with code inspection triggered by missing, stale, contradictory, risk-significant, or acceptance-critical
  claims.

Route either gate's plan blockers before code repair. Each repair/continuation creates a new freeze after affected
checks and feature Acceptance. Pass shared remaining repair time/deadline to review/closure and audit; exhausted
checks are incomplete, never waived. Focused Fix Verification may restore `CLEAN`; a fresh cold auditor still must
issue same-freeze `PASS`.

After same-freeze CLEAN+PASS, apply source-publication final push/catch-up for approved remote cadences only if SHA
differs as specified; use `worktree` and require post-push remote SHA equality. `local-only` stays network-free.
Sidecar, target, and hotfix gates run only when separately authorized. Report publication state and retain safety nets.
Publication never changes evidence truth; scheduled failure blocks only at that due gate.

Declare readiness only when package evidence, production/integration review-code CLEAN, and audit PASS bind the same
integrated state, plus any due publication gate has succeeded.

## Status Output

Include package ID/title, result path, checklist result, `validate-package-complete`, branch/worktree, integration
state, plan-defect, repair/follow-up, next gate, and blockers.
