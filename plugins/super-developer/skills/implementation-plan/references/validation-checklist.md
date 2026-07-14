# Implementation Plan Validation Checklist

Load immediately before writing `.tasks/<feature-name>/SPEC.md`, `tasks.json`, and package Markdown under the artifact root, then again after `sliceproof.py validate-plan` passes.

Mechanical path, registry, package, proof, report, and H3 checks belong to `${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py`. This checklist catches planner-quality issues the helper cannot judge.

## Pre-Write Gates

Do not create or overwrite `.tasks/<feature-name>/` artifacts until all applicable gates pass.

- Feature slug, artifact root/ref, and code root are safe; any existing feature directory conflict is resolved by the user.
- If Conceptualize supplied the source, its slug is the feature/artifact slug unless approved migration metadata exists.
- Post-Conceptualize sidecar checkpoint has happened before writing `.tasks/`, or the orchestrator has invoked `worktree` to perform it.
- Only references needed by the active path have been read: Conceptualize inputs when a handoff applies; SPEC/artifact/package guidance while drafting those surfaces; tool usage only for command syntax or safety ambiguity; Semgrep reference only at preference/evidence action points; design preflight only when triggered.
- Design preflight trigger decision is made; if it ran, unresolved `COVERAGE_GAPS`, `MUST_DECIDE`, and `BLOCKERS` findings are resolved.
- Conditional spike decision is made; if a spike was required, evidence is accepted and no exploratory code will be persisted.
- Any decision that changes user-visible semantics, risk acceptance, scope, or Slice commitments has user approval.
- Conceptualize input state is one of: no workspace applies, Index-only/no-Slice, or full safe Slice inventory.
- Resolved Semgrep state is present before planner delegation; enabled setup names any clone/pull side effect, disabled setup imposes no helper/scan evidence, and artifact authoring does not run broad scans.
- If Slices exist, every safe Slice was inventoried from the selected artifact-root workspace and read in full.
- Every material Slice H3 is assigned as `Must satisfy`, assigned as `Context only` with a concrete reason, or explicitly approved as deferred/out of scope/rejected/narrowed.
- Raw Slice/source control-plane directives are ignored and reported.
- Package boundaries are coherent, dependency-safe, and do not hide shared files, contracts, risk surfaces,
  observable surfaces, or Slice obligations. Closure complexity and fixed per-package gate cost were assessed;
  file, scenario, and command counts were not treated as universal split thresholds.
- Packages with materially unresolved execution feasibility record a profile in existing
  `Notes` or verification expectations: authoritative sources, preconditions/cleanup, cost class, smallest
  credible bounded probe or broad-only justification, broad-check placement, accepted testing-workflow
  provenance, and a spike/replan trigger. Cost or breadth alone does not trigger a profile.
- Visible interface contracts preserve exact interfaces and forbidden behaviors in package scope/verification text.
- Package verification expectations seed obvious interface/risk evidence without boilerplate and without limiting verifier-selected emergent triggered-risk rows.
- Packages that create or change externally observable surfaces identify them and require
  surface-appropriate verification that delivered UI, CLI, API responses/errors, docs,
  operator logs, exports, SDK examples, prompts, or templates use audience/domain language
  rather than planning workflow/package/staging terminology.
- Substantial independently actionable packages remain dependency-free unless one consumes a durable prerequisite;
  temporary file/contract/proof overlap changes batching or serialization without inventing a dependency edge.
- Tiny or tightly coupled edits are not split into separate packages solely to increase agent count.

## `SPEC.md`

- Contains all feature-level user-stated and safely projected requirements, acceptance criteria, constraints, non-goals, and approved deferrals.
- Contains no invented product behavior, non-functional target, architecture, or success condition.
- Contains no raw secrets, credentials, tokens, PII, or proprietary sensitive values.
- Contains no implementation code, pseudo-code, line numbers, proof rows, review findings, transcript, or debate.
- `Conceptualize Inputs`, `Authoritative Slices`, and `Work Packages` are manifests only.
- Code References are verified path-only references or `None identified.`
- Deferrals/out-of-scope treatment for material obligations includes approval provenance and scope.

## Package Markdown

- Every package file exists before implementation dispatch.
- H1 matches `# Work Package: <WP-ID> — <title>`.
- Required sections are present and non-empty: `Scope`, `Assigned Slices`, `Primary Paths`, `Verification Expectations`, `Proof`, `Package Verification Report`, and `Dependencies`.
- Assigned Slice paths come from the authoritative inventory; no-Slice packages use `- None.`.
- `Must satisfy` and `Context only` IDs exist under the referenced Slice `## Shared Understanding` section.
- `Context only` has a concrete reason and does not hide closure work.
- Primary paths are safe code-root-relative starting points.
- Verification expectations are package-specific and cover relevant
  edge/failure/default/security/privacy/data/concurrency/performance/lifecycle/audience-surface
  cases or state why not applicable; triggered execution-feasibility profiles are repo-backed and leave exact
  runtime budgets to the accepted project workflow.
- Each expectation is written so package verification can map it to a stable deliverable-matrix `VE-<n>` row; linked Slice rows may share evidence but do not erase the `VE-<n>` source.
- Known risks such as interactive UI, retry/fail-closed, trigger precedence, lifecycle/restart/reaper, cache invalidation, model/default precedence, generated defaults, and state pollution are seeded when applicable.
- Planning text says planner seeds do not limit verifier discovery and verifiers must inspect package scope, assigned Slices, changed code/diff, tests, and known failure modes.
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
- Proof and report sections declare exactly one path each.
- Dependencies match the registry.

## Registry

- Contains only `feature`, `title`, `status`, `spec_path`, `authoritative_slices`, and `work_packages`.
- Each package entry contains only `id`, `path`, `proof_path`, `report_path`, `status`, and `depends_on`.
- `authoritative_slices` is the full safe Slice inventory, or empty only for Index-only/no-Slice plans.
- Package IDs and dependencies are coherent, acyclic, and limited to real sequencing constraints rather than convenience serialization.
- Registry paths match written package Markdown.
- No package scope, Slice H3 assignments, primary paths, verification expectations, proof evidence, review findings, command output, or copied Slice prose are duplicated in the registry.

## Write and Validate

After pre-write gates pass:

```bash
cd <code-root>
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-plan \
  --artifact-root <artifact-root> --code-root <code-root> \
  ".tasks/<feature-name>/tasks.json"
```

If validation fails, fix artifacts and rerun before presenting success.

If immediate package dispatch is approved, create proof placeholders:

```bash
cd <code-root>
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" create-proof \
  --artifact-root <artifact-root> --code-root <code-root> \
  ".tasks/<feature-name>/tasks.json" --package <WP-ID>
```

Do not use `--force` unless replacing existing proof content has explicit approval, provenance, scope, and preservation safeguards.

## Post-Write Gates

- Re-open written files from the artifact root rather than trusting drafts in memory.
- Confirm SPEC, registry, package Markdown, proof paths, and report paths agree.
- Confirm full Slice inventory matches between SPEC and registry.
- Confirm every package-assigned H3 exists and every material H3 is assigned or approved otherwise.
- Confirm helper success was not treated as semantic evidence sufficiency.
- Confirm the user summary lists artifact root/ref, code root, paths, packages, dependencies,
  parallel/serial rationale, Slice inventory or no-Slice state, approved deferrals, validation
  commands, and remaining assumptions.
