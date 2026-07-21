# Package Lifecycle, Proof, and Report

## Boundary
This reference owns package completion, proof creation, the verification report, and re-verification after
repair. Artifact shapes live in `slice-first-artifacts.md`; package sizing lives in `work-packages.md`; command
shapes live in `tool-usage.md`. The report shape is in `package-verification-report.md`.

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

## Proof
Each package has one artifact-root proof file declared in the registry and package Markdown:
`.tasks/<feature>/proofs/<WP-ID>.proof.md`. The package agent fills its own proof (implementation and evidence
notes) and commits; it does not mark packages done or edit unrelated proofs.

Create the placeholder before dispatch:
```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" create-proof \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" \
  ".tasks/<feature>/tasks.json" --package WP1
```
Overwrite safety: a missing proof is created; an existing exact placeholder is idempotent; an edited/filled proof
fails closed unless `--force --approved-replacement` carries approval, provenance, and scope. Filled evidence is
never silently erased.

## Verification
When a package agent returns, an independent verifier checks the package against its Acceptance Checklist per
`../skills/implement/references/package-verification.md` and writes the lightweight report
(`package-verification-report.md`). Mechanical helpers are advisory support, never the semantic gate:
```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-proof \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" \
  ".tasks/<feature>/tasks.json" --package WP1
```

## Completion gate
A package becomes `done` only when:
1. package Markdown and proof validate mechanically (`validate-proof`);
2. the verifier returned **PASS** — every Acceptance Checklist item passes with authentic evidence, no open
   blocking finding;
3. the lightweight report exists and `validate-package-complete` succeeds;
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

## Repair impact and re-verification (delta-only, bounded)
Dependency edges express readiness/sequencing only: descendants are not staleness fan-out. Classify semantic
impact from the diff and changed behavior/evidence. Include direct owners and consumers; observable/public
contracts; generated artifacts, configuration, and migrations; dynamic or unknown consumers; shared fixtures,
harnesses, and oracles; security, data, concurrency, and global invariants; merge resolutions; and evidence-only
invalidation. Unknown or unbounded impact widens conservatively, while unaffected results remain reusable.

Refresh only each affected package's checklist/proof/report evidence plus focused seam closure. Stabilize the
repaired state, then run or reuse the deduplicated minimum union of commands only when code/artifact state, cwd,
environment/data, isolation/order assumptions, and evidence mapping are equivalent. Authentic exact-state
output may be reused; distinct package, isolation, cleanup, and nondeterministic checks still run.

Cluster confirmed findings only when they share a root cause, writable scope, and verification envelope; assign
one repair worker per coherent cluster. Preserve logical cluster identity across retries and the existing
three-attempt cap: after **3** non-converging repair attempts, stop rather than rename or recluster. Widen only
for semantically affected surfaces, never merely because a dependency, commit, or merge exists.

## Final readiness
Before final `review-code` and `audit`, every package is `done`, the integrated code is assembled, and the
feature-level `## Acceptance` (SPEC) checks pass against the integrated state with captured output. Freeze that
state; run `sliceproof.py validate-final` per artifact root as advisory diagnostics. `review-code` reviews
integration seams; `audit` confirms every package checklist and the feature Acceptance passed. Their outputs are
not freeze inputs.

## Observability
Non-gating traces may surface version, stage/package timing, command identity/outcome, readiness, and repair
progress. They never mutate state, act as proof, or present timing as completion.
