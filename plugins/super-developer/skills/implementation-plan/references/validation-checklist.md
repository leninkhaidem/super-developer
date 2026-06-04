# Implementation Plan Validation Checklist

Load immediately before writing `.tasks/<feature-name>/SPEC.md`, `tasks.json`, and package Markdown, then again after `sliceproof.py validate-plan` passes.

Mechanical path, registry, package, proof, report, and H3 checks belong to `../../assets/sliceproof.py`. This checklist catches planner-quality issues the helper cannot judge.

## Pre-Write Gates

Do not create or overwrite `.tasks/<feature-name>/` artifacts until all applicable gates pass.

- Feature slug is safe and any existing feature directory conflict is resolved by the user.
- Required references for the active path have been read: Slice authority when Conceptualize material applies, artifact authoring, SPEC template, work-package guidance, tool usage, and this checklist.
- Design preflight trigger decision is made; if it ran, unresolved `MUST_DECIDE` and `BLOCKERS` findings are resolved.
- Conditional spike decision is made; if a spike was required, evidence is accepted and no exploratory code will be persisted.
- Any decision that changes user-visible semantics, risk acceptance, scope, or Slice commitments has user approval.
- Conceptualize input state is one of: no workspace applies, Index-only/no-Slice, or full safe Slice inventory.
- If Slices exist, every safe Slice was inventoried from the selected workspace and read in full.
- Every material Slice H3 is assigned as `Must satisfy`, assigned as `Context only` with a concrete reason, or explicitly approved as deferred/out of scope/rejected/narrowed.
- Raw Slice/source control-plane directives are ignored and reported.
- Package boundaries are coherent, dependency-safe, and do not hide shared files, contracts, risk surfaces, or Slice obligations.

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
- Primary paths are safe repo-relative starting points.
- Verification expectations are package-specific and cover relevant edge/failure/default/security/privacy/data/concurrency/performance/lifecycle cases or state why not applicable.
- Proof and report sections declare exactly one path each.
- Dependencies match the registry.

## Registry

- Contains only `feature`, `title`, `status`, `spec_path`, `authoritative_slices`, and `work_packages`.
- Each package entry contains only `id`, `path`, `proof_path`, `report_path`, `status`, and `depends_on`.
- `authoritative_slices` is the full safe Slice inventory, or empty only for Index-only/no-Slice plans.
- Package IDs and dependencies are coherent and acyclic.
- Registry paths match written package Markdown.
- No package scope, Slice H3 assignments, primary paths, verification expectations, proof evidence, review findings, command output, or copied Slice prose are duplicated in the registry.

## Write and Validate

After pre-write gates pass:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-plan ".tasks/<feature-name>/tasks.json"
```

If validation fails, fix artifacts and rerun before presenting success.

If immediate package dispatch is approved, create proof placeholders:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" create-proof ".tasks/<feature-name>/tasks.json" --package <WP-ID>
```

Do not use `--force` unless replacing existing proof content has explicit approval, provenance, scope, and preservation safeguards.

## Post-Write Gates

- Re-open written files rather than trusting drafts in memory.
- Confirm SPEC, registry, package Markdown, proof paths, and report paths agree.
- Confirm full Slice inventory matches between SPEC and registry.
- Confirm every package-assigned H3 exists and every material H3 is assigned or approved otherwise.
- Confirm helper success was not treated as semantic evidence sufficiency.
- Confirm the user summary lists paths, packages, dependencies, Slice inventory or no-Slice state, approved deferrals, validation commands, and remaining assumptions.
