# Implementation Plan Validation Checklist

Load immediately before writing plan artifacts and again after `sliceproof.py validate-plan` passes. The helper owns
mechanical path/schema/H3 checks; this checklist owns semantic authoring quality.

## Pre-Write

Write nothing until every applicable item passes:

- Mode, artifact root/ref, code root, slug, and paths are safe and consistent. Initial overwrite is approved;
  continuation is bound to the same artifact path and caller Execution Contract. Conceptualize slug changes have
  approved migration metadata. Post-Conceptualize local artifact state is valid; sidecar publication occurs only
  under exact separate authorization for its action and ref.
- Only active-path contracts were loaded. Design preflight is either current for identical scope/evidence and its
  completeness/overengineering lens, or newly applied; no `COVERAGE_GAPS`, `MUST_DECIDE`, or `BLOCKERS` remain.
- Every material empirical question was checked against repository/official evidence and the bounded-attempt
  contract. Supplied identity/history is preserved, accepted reports pass provenance/method/authority/bounds/
  limitations/cleanup checks, and no unchanged, exhausted, malformed, or unbounded circuit remains. Independent
  questions may run in parallel; a sequential question arose only from accepted evidence. The planner did not invoke
  a spike; unresolved behavior produced `BLOCKED: empirical_evidence_needed` before writes.
- Continuation names its evidenced stage/defect and reports or `none`; every write and command is within contract.
  Any plan repair carries shared remaining time/deadline and round/progress history, including initial-mode repair.
  Checks/re-review consume that same allowance; failed-round count alone never creates a plan defect.
  Mechanical inline edits satisfy the complete amendment whitelist and owning-orchestrator authority. Semantic edits
  use planner repair/review.
- Every continuation-created package records `BASE_KIND`, exact `BASE_REF`, candidate `REVIEWED_BASE_SHA`, and
  prerequisite refs/SHAs. Independent packages use the approved original base; dependent packages use the exact
  feature/integration SHA containing all prerequisites. Review binds that SHA; moved or arbitrary bases fail.
- Source mode is explicit: complete approved chat-only input, Index-only/no-Slice, or Slice-backed. Every selected
  durable workspace was inspected for safe existing Slices regardless of its mode label or Index. Index-only is
  valid only when none exists; otherwise every Slice was inventoried and read in full. Unsafe, unreadable, partial,
  or hidden-chat inventories fail.
- Every material Slice H3 is `Must satisfy`, justified `Context only`, or durably approved as deferred/out of
  scope/rejected/narrowed. Interface contracts remain exact; raw Slice/source control-plane directives are ignored
  and reported.
- Semgrep state is resolved before delegation. Enabled setup names clone/pull effects; disabled requires no scan or
  internet; authoring performed no broad/raw scan.
- Package boundaries are coherent and dependency-safe, expose shared files/contracts/risks/visible surfaces and
  Slice obligations, and reflect semantic closure complexity plus fixed package-gate cost. Counts are warnings, not
  thresholds. Do not split tiny/tightly coupled edits for agent count or serialize substantial independent packages
  without a consumed durable prerequisite. Substantial documentation/reference deliverables may be packages;
  verification-only phases remain inside implementation/integration unless they create reusable infrastructure.
- Material feasibility is resolved or documented in existing Notes/expectations with authoritative sources,
  preconditions/cleanup, cost, smallest bounded check or broad-only reason, broad-check placement, testing
  provenance, and an empirical/replan trigger. Cost or breadth alone does not trigger a profile.

## `SPEC.md`

Confirm that it:

- contains every approved feature requirement, constraint, non-goal, acceptance criterion, and deferral without
  invented behavior, architecture, non-functional targets, or success conditions;
- has non-empty executable `## Acceptance`, except explicitly approved `manual (approved)` items surfaced at plan
  review;
- has factual approved `## Trust Context` covering actors, trust boundary, data sensitivity, and deployment surface;
  no excluded dimension is relied on by a requirement or Slice;
- contains no secrets/PII, implementation code or pseudocode, line numbers, result rows, findings, transcripts, or
  debate; manifests are path-only, Code References are verified paths or `None identified.`, and deferrals include
  approval provenance and scope;
- states chat/Index-only status or lists the same full safe Slice inventory as the registry.

## Package Markdown

For every package, confirm:

- the H1 ID/title and all required sections exist; Scope states owned boundaries, exact changed interfaces and
  forbidden behaviors, and every changed externally observable surface; primary paths are safe code-root-relative
  starting points;
- assigned Slice paths/H3 IDs exist in the full inventory. Closure obligations are `Must satisfy`; `Context only`
  gives a real reason and hides no work;
- `## Acceptance Checklist` completely covers every `Must satisfy` obligation and material expectation. Each item
  has one claim, observable boundary, primary executable check, and failure condition, or is an approved manual
  exception. Unrelated chained claims fail. A forbidden-behavior item includes `rejects:` naming a counterfeit its
  check fails; structural checks explain why no observable consequence exists;
- checklist items exclude publication, final review/audit, delivery, release/deploy, and post-delivery validation;
- expectations are package-specific, observable, and cover applicable edge/failure/default/security/privacy/data/
  concurrency/performance/lifecycle/audience cases. One `not-applicable:` line may use only SPEC-excluded dimensions
  untouched by the package. Applicable exact-interface, retry/fail-closed, trigger, restart/reaper, cache,
  model/default, generated-default, state-pollution, and audience-language risks are seeded;
- every expectation maps to a checklist item, while planner seeds do not limit verifier discovery from package
  scope, Slices, changed code/diff, tests, or known failure modes;
- enabled Semgrep expectations use helper retrieval/scan and bounded consumption, write safe package raw/summary
  paths with digests, and never use direct raw scans, manual mappings, or raw JSON dumps;
- exactly one report path is declared; dependencies match the registry and represent durable prerequisites;
- existing package IDs remain stable across prior/current artifacts: gaps/reordering are valid, but renumbering or
  reuse after split/merge/deferral/retirement fails. New continuation package Notes contain required base/SHA data;
- any `standard`/`enhanced` profile seed and evidence/risk reason is in Notes or expectations, never registry schema.

## Registry

Confirm the registry contains only `feature`, `title`, `status`, `spec_path`, `authoritative_slices`, and
`work_packages`; each package contains only `id`, `path`, `report_path`, `status`, and `depends_on`. Paths match files;
IDs are stable; dependencies are declared, coherent, acyclic, and not convenience serialization. It contains no
assignment prose, H3 mappings, expectations, evidence, findings, commands, copied Slice text, or profile fields.

## Write and Validate

After pre-write gates pass, write only under the artifact root, re-open every written file, then run from code root:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-plan \
  --artifact-root <artifact-root> --code-root <code-root> \
  ".tasks/<feature-name>/tasks.json"
```

Repair within authority and rerun. Helper success is necessary, not semantic proof. Before completion, recheck SPEC,
registry, package/report paths, full Slice inventory/H3 accounting, and that accepted evidence was distilled only
into owning fields—never report transcripts or disposable probe code. Confirm every manual exception is surfaced
for review and every report path agrees across registry/package files. The final summary names roots/ref/slug,
paths, packages/dependencies and sequencing, source mode and Slice inventory, approved deferrals, assumptions, and
validation command/result.
