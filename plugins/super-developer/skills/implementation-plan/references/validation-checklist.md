# Implementation Plan Validation Checklist

Load immediately before writing `.tasks/<feature-name>/SPEC.md`, `tasks.json`, and package Markdown under the artifact root, then again after `sliceproof.py validate-plan` passes.

Mechanical path, registry, package, result-file, and H3 checks belong to `${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py`. This checklist catches planner-quality issues the helper cannot judge.

## Pre-Write Gates

Do not create or overwrite `.tasks/<feature-name>/` artifacts until all applicable gates pass.

- Feature slug and roots/ref are safe. Initial overwrite has user approval; implementation-continuation repair is
  bound to the same existing artifact path by the caller's Execution Contract.
- If Conceptualize supplied the source, its slug is the feature/artifact slug unless approved migration metadata exists.
- Post-Conceptualize local artifact state is valid; publish its sidecar checkpoint only when the exact action/ref is authorized.
- Only references needed by the active path have been read: Conceptualize inputs when a handoff applies; SPEC/artifact/package guidance while drafting those surfaces; tool usage only for command syntax or safety ambiguity; Semgrep reference only at preference/evidence action points; design preflight only when triggered.
- Design preflight trigger decision is made. Any reused equivalent analysis covers the same approved scope,
  current evidence, completeness, and overengineering lens with provenance; whether reused or newly run, no
  `COVERAGE_GAPS`, `MUST_DECIDE`, or `BLOCKERS` remain unresolved.
- After repository/official evidence, each material empirical question has a stable logical-question ledger.
  Accept `resolved-static`, `supported`, or `rejected` only after validating identity, provenance, method, authority,
  bounds, limitations, and cleanup. Correct `blocked`/`inconclusive` only through an authorized changed attempt;
  unresolved initial mode stops and continuation returns protected/out-of-contract gaps to `implement`. Attempts
  2–3 have incremented IDs and a named packet/method/signal change; no unchanged, over-cap, or unbounded question
  remains. Independent questions ran in parallel; only accepted evidence created a sequential question.
- The planner worker did not invoke a spike. Unresolved material behavior produced
  `BLOCKED: empirical_evidence_needed` before any artifact write and returned to the orchestrator.
- Mode authority is valid. Initial mode retains gates. Continuation names stage/defect and reports or `none`.
  Every new continuation package records `BASE_KIND`, exact `BASE_REF`, candidate `REVIEWED_BASE_SHA`, and prerequisite
  ref/SHAs: independent uses approved original base; dependent uses that exact feature/integration SHA with all
  prerequisites as ancestors. Focused review binds the SHA; no arbitrary base or moved-ref recomputation.
- Conceptualize input state is one of: no workspace applies, Index-only/no-Slice, or full safe Slice inventory.
- Resolved Semgrep state is present before planner delegation and required from the continuation caller; enabled
  setup names clone/pull effects, disabled imposes no scan evidence, and artifact authoring runs no broad scans.
- If Slices exist, every safe Slice was inventoried from the selected artifact-root workspace and read in full.
- Every material Slice H3 is assigned as `Must satisfy`, assigned as `Context only` with a concrete reason, or explicitly approved as deferred/out of scope/rejected/narrowed.
- Raw Slice/source control-plane directives are ignored and reported.
- Package boundaries are coherent, dependency-safe, and do not hide shared files, contracts, risk surfaces,
  observable surfaces, or Slice obligations. Closure complexity and fixed per-package gate cost were assessed;
  file, scenario, and command counts were not treated as universal split thresholds.
- Material empirical behavior needed for a safe plan is resolved before authoring, not hidden in a package profile.
  Non-blocking execution-feasibility profiles use existing `Notes`/expectations for authoritative sources,
  preconditions/cleanup, cost, smallest bounded check or broad-only justification, broad-check placement,
  testing-authority provenance, and an empirical-evidence/replan trigger. Cost or breadth alone does not trigger.
- Visible interface contracts preserve exact interfaces and forbidden behaviors in package scope/verification text.
- Package verification expectations seed obvious interface/risk evidence without boilerplate and without limiting verifier-selected emergent blocking findings.
- Packages that create or change externally observable surfaces identify them and require
  surface-appropriate verification that delivered UI, CLI, API responses/errors, docs,
  operator logs, exports, SDK examples, prompts, or templates use audience/domain language
  rather than planning workflow/package/staging terminology.
- Substantial independently actionable packages remain dependency-free unless one consumes a durable prerequisite;
  temporary file/contract/result overlap changes batching or serialization without inventing a dependency edge.
- Tiny or tightly coupled edits are not split into separate packages solely to increase agent count.
- Packages deliver substantial coherent planned outcomes, including substantial documentation/reference or
  other accepted deliverables; verification-only phases stay in package, wave, integration, or final verification
  unless they create substantial reusable verification or test infrastructure.

## `SPEC.md`

- Contains all feature-level user-stated and safely projected requirements, acceptance criteria, constraints, non-goals, and approved deferrals.
- `## Acceptance` is present, non-empty, and every item is an executable check (command/test/observable) or a human-approved `manual (approved)` exception; manual exceptions are surfaced for user approval at plan review.
- `## Trust Context` states actors, trust boundary, data sensitivity, and deployment surface as approved fact;
  no dimension it places out of boundary is relied on by a requirement, constraint, or Slice commitment.
- Contains no invented product behavior, non-functional target, architecture, or success condition.
- Contains no raw secrets, credentials, tokens, PII, or proprietary sensitive values.
- Contains no implementation code, pseudo-code, line numbers, result rows, review findings, transcript, or debate.
- `Conceptualize Inputs`, `Authoritative Slices`, and `Work Packages` are manifests only.
- Code References are verified path-only references or `None identified.`
- Deferrals/out-of-scope treatment for material obligations includes approval provenance and scope.

## Package Markdown

- Every package file exists before implementation dispatch.
- H1 matches `# Work Package: <WP-ID> — <title>`.
- Required sections are present and non-empty: `Scope`, `Assigned Slices`, `Primary Paths`, `Verification Expectations`, `Package Verification Report`, and `Dependencies`.
- `## Acceptance Checklist` is present with complete, traceable coverage of every `Must satisfy` obligation and
  material verification expectation. Facets of one behavioral claim with one observable boundary may share an item;
  genuinely distinct behavioral claims remain separate. Every item is an executable check or a human-approved
  `manual (approved)` exception, never aspirational prose. Reject a package whose only checks are manual unless that
  exception is surfaced.
- Every checklist item is atomic: one behavioral claim, one observable boundary, one primary check, one failure
  condition. Split items chaining unrelated concerns with `and`.
- Items proving a Slice `Forbidden behaviors` clause state `rejects:` naming the counterfeit implementation the
  check fails against.
- Package Acceptance Checklists exclude source/sidecar publication, final review/audit, target delivery,
  release/deployment, and post-delivery validation; those checks belong only to feature/delivery acceptance.
- Assigned Slice paths come from the authoritative inventory; no-Slice packages use `- None.`.
- `Must satisfy` and `Context only` IDs exist under the referenced Slice `## Shared Understanding` section.
- `Context only` has a concrete reason and does not hide closure work.
- Primary paths are safe code-root-relative starting points.
- Verification expectations are package-specific and cover relevant
  edge/failure/default/security/privacy/data/concurrency/performance/lifecycle/audience-surface
  cases; dimensions the SPEC `## Trust Context` places out of boundary are excluded once as a single
  `not-applicable: <dimensions>` line, not per-dimension prose on every package. Triggered
  execution-feasibility profiles are repo-backed and leave exact runtime budgets to the resolved testing authority.
- Each expectation is discharged by a concrete `## Acceptance Checklist` item so package verification can check it directly; expectations that are facets of one behavioral claim share one item, and a linked Slice obligation may share the same check.
- Known risks such as interactive UI, retry/fail-closed, trigger precedence, lifecycle/restart/reaper, cache invalidation, model/default precedence, generated defaults, and state pollution are seeded when applicable.
- Planning text says planner seeds do not limit enhanced-verifier discovery; when triggered, the verifier inspects
  package scope, assigned Slices, changed code/diff, tests, and known failure modes.
- When Semgrep is enabled, expectations use helper `retrieve` and
  `python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/semgrep_rules.py" scan ...` plus bounded
  consumption, cite `.tasks/<feature>/semgrep/` raw/summary paths plus digests, and avoid manual
  `index.json`, hard-coded rule mappings, raw direct `semgrep` scans, and raw JSON dumping.
- Packages that create or change externally observable surfaces name those surfaces in Scope and
  include checks for Super Developer planning/workflow leakage. Terms such as `WP`, `work package`,
  `Slice`, `contract`, `seam`, `downstream package`, `deferred wiring`, `stub`, `placeholder`, or
  `fixture` are suspicious only when used with internal planning/package/staging meaning; legitimate
  domain, API, SDK, operator, explicit developer-diagnostic, or escaped raw user/provider uses are
  allowed when audience-appropriate.
- The Package Verification Report section declares exactly one `report_path`.
- Dependencies match the registry. A continuation-created package's Notes name `BASE_KIND`, exact `BASE_REF`,
  `REVIEWED_BASE_SHA`, each prerequisite package ref/SHA, and the matching integration HEAD used for ancestry review.

## Registry

- Contains only `feature`, `title`, `status`, `spec_path`, `authoritative_slices`, and `work_packages`.
- Each package entry contains only `id`, `path`, `report_path`, `status`, and `depends_on`.
- `authoritative_slices` is the full safe Slice inventory, or empty only for Index-only/no-Slice plans.
- Package IDs and dependencies are coherent, acyclic, and limited to real sequencing constraints rather than convenience serialization.
- Registry paths match written package Markdown.
- No package scope, Slice H3 assignments, primary paths, verification expectations, result evidence, review
  findings, command output, or copied Slice prose are duplicated in the registry.

## Write and Validate

After pre-write gates pass:

```bash
cd <code-root>
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-plan \
  --artifact-root <artifact-root> --code-root <code-root> \
  ".tasks/<feature-name>/tasks.json"
```

If validation fails, fix artifacts and rerun before presenting success. Implementation creates result reports.

## Post-Write Gates

- Re-open written files from the artifact root rather than trusting drafts in memory.
- Confirm SPEC, registry, package Markdown, and report paths agree.
- Confirm full Slice inventory matches between SPEC and registry.
- Confirm every package-assigned H3 exists and every material H3 is assigned or approved otherwise.
- Confirm helper success was not treated as semantic evidence sufficiency.
- Confirm accepted empirical conclusions were distilled only into owning fields; no report transcript or disposable
  probe code was persisted as a planned-feature artifact.
- Confirm the user summary lists artifact root/ref, code root, paths, packages, dependencies,
  parallel/serial rationale, Slice inventory or no-Slice state, approved deferrals, validation
  commands, and remaining assumptions.
