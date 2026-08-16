# Package Lifecycle and Result File

## Boundary
This reference owns package completion, the result file, and re-verification after repair. Artifact shapes live
in `slice-first-artifacts.md`; package sizing lives in `work-packages.md`; command shapes live in `tool-usage.md`.
The report shape is in `package-verification-report.md`.

## Status Signals
Registry package status is routing only: `pending`, `in_progress`, `blocked`, or `done`. Status does not prove
correctness. Dashboards may show status, dependency readiness, and helper results as mechanical signals only.

## Definition of done
A package is **done** when its **frozen `## Acceptance Checklist`** (in the package Markdown, approved at the plan gate)
passes: every item shows a real passing check with authentic evidence, and no open blocking finding remains.
That checklist is the closed, objective done-definition — the verifier checks exactly it, inventing nothing.
Package completion is a local evidence fact: source/sidecar publication, final review/audit, target delivery,
release/deployment, and post-delivery validation are downstream gates and cannot be checklist prerequisites.
Later evidence changes may stale completion through the existing freshness rules; publication cannot create it.

## Result file
Each package has one artifact-root result file declared as registry `report_path`:
`.tasks/<feature>/reports/<WP-ID>.package-verification.md`. The package agent drafts it, the orchestrator records
its re-run evidence and any enhanced-verifier findings, and the helper remains read-only.

## Verification
When a package agent returns, the implement orchestrator re-runs every executable frozen Acceptance Checklist
item into that same result file. A failed re-run is automatic FAIL with no LLM. An independent verifier runs only
for enhanced-risk packages and only for defects the check cannot show. Mechanical helpers are advisory support,
never the semantic gate.

## Completion gate
A package becomes `done` only when:
1. the orchestrator re-run recorded PASS for every executable frozen AC item;
2. the result file records every item pass with observed output, no open blocking finding, and Gaps `none` or
   approved metadata;
3. `validate-package-complete` succeeds as a read-only structural check;
4. any blocking-finding repairs are closed.

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-package-complete \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" \
  ".tasks/<feature>/tasks.json" --package <WP-ID>
```
Dependent packages stay blocked until their source packages are `done`. A registry `done` status or helper
success alone never proves completion.

## Severity bar
Only **blocking** findings — correctness, security, data-loss, contract-break — fail a package and trigger
repair. Everything else is **advisory**: recorded in the report, never looped, never a reason to withhold done.
Do not manufacture blockers from style, taste, or speculative completeness.

Every blocking finding carries a warrant naming the authority it acts under: `warrant: AC-<id>` for a violated
frozen item, `warrant: regression:<ref>` for broken existing behavior, or `warrant: override:<class>` for a severe
correctness/security/data-loss defect the checklist cannot see. An unwarranted finding is not blocking. It becomes
an advisory note, or — when it names a real obligation the frozen checklist omits — a `## Plan gaps` entry
(`warrant: plan-gap`). Plan gaps never change the verdict or withhold done; the orchestrator routes them to
planning continuation, so a missing requirement is neither forced in by a verifier nor silently lost.

Scope assurance depth to the SPEC `## Trust Context`. Inside a declared trusted boundary, hostile-input,
authentication, race-hardening, and adversarial-filesystem concerns are advisory unless a frozen item,
requirement, or Slice obligation names them. Trust Context never scopes the control-plane boundary and never
downgrades a defect in behavior the package actually promises.

## Repair impact and re-verification (delta-only, bounded)
Dependency edges express readiness/sequencing only: descendants are not staleness fan-out. Classify semantic
impact from the diff and changed behavior/evidence. Include direct owners and consumers; observable/public
contracts; generated artifacts, configuration, and migrations; dynamic or unknown consumers; shared fixtures,
harnesses, and oracles; security, data, concurrency, and global invariants; merge resolutions; and evidence-only
invalidation. Unknown or unbounded impact widens conservatively, while unaffected results remain reusable.

Refresh only each affected package's checklist/result-file evidence plus focused seam closure. Stabilize the
repaired state, then run or reuse the deduplicated minimum union of commands only when code/artifact state, cwd,
environment/data, isolation/order assumptions, and evidence mapping are equivalent. Authentic exact-state
output may be reused; distinct package, isolation, cleanup, and nondeterministic checks still run.

Cluster confirmed findings only when they share a root cause, writable scope, and verification envelope; assign
one repair worker per coherent cluster. Preserve logical cluster identity across retries and the existing
three-attempt cap: after **3** non-converging repair attempts, never rename or recluster. A plan-owned cluster
stops there. A **code** repair cluster is re-classified once as a possible plan defect and routed through planning
continuation when that preserves approved semantics, scope, user-visible behavior, risk, and manual exceptions;
otherwise it stops. At most one such escalation per cluster identity, relabeling earns no second one, and the same
cluster's second exhaustion of **3** attempts stops. Widen only for semantically affected surfaces, never merely
because a dependency, commit, or merge exists.

## Final readiness
Before final `review-code` and `audit`, every package is `done`, the integrated code is assembled, and the
feature-level `## Acceptance` (SPEC) checks pass against the integrated state with captured output. Freeze that
state; run `sliceproof.py validate-final` per artifact root as advisory diagnostics. `review-code` reviews
integration seams; `audit` confirms every package checklist and the feature Acceptance passed. Their outputs are
not freeze inputs.

## Observability
Non-gating traces may surface version, stage/package timing, command identity/outcome, readiness, and repair
progress. They never mutate state, act as proof, or present timing as completion.
