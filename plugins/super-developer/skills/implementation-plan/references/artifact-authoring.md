# Implementation Artifact Authoring

Load when drafting `.tasks/<feature>/tasks.json` or `.tasks/<feature>/packages/<WP-ID>.md`.

## Contract

- Load `../../references/slice-first-artifacts.md` for the canonical artifact model.
- `tasks.json` is a lightweight registry: feature metadata, Slice inventory, package paths, proof paths, report paths, status signals, and dependencies only.
- Package Markdown is the package assignment source of truth.
- Proof Markdown is generated from package assignment before dispatch and filled by package agents.
- Package verification reports are declared during planning and written by independent package verification.
- Do not duplicate package scope, assigned H3 IDs, primary paths, verification expectations, proof evidence, review findings, command output, or lifecycle history in the registry.

## Registry Shape

```json
{
  "feature": "<feature-name>",
  "title": "Human-readable feature title",
  "status": "planned",
  "spec_path": ".tasks/<feature-name>/SPEC.md",
  "authoritative_slices": [
    ".planning/<concept-slug>/slices/<slice-name>.md"
  ],
  "work_packages": [
    {
      "id": "WP1",
      "path": ".tasks/<feature-name>/packages/WP1.md",
      "proof_path": ".tasks/<feature-name>/proofs/WP1.proof.md",
      "report_path": ".tasks/<feature-name>/reports/WP1.package-verification.md",
      "status": "pending",
      "depends_on": []
    }
  ]
}
```

Use an empty `authoritative_slices` array only for Index-only or no-Slice plans where no Slice is independently useful.

## Registry Rules

- `feature` must match the safe feature slug and `.tasks/<feature>/` directory.
- `spec_path` points to the written `SPEC.md` file.
- `authoritative_slices` lists the full safe Slice inventory when Slices exist.
- Each package entry contains only `id`, `path`, `proof_path`, `report_path`, `status`, and `depends_on`.
- Dependencies are package IDs and must match package Markdown.
- Keep paths repo-relative POSIX paths; reject absolute, traversal, home, drive-qualified, empty-segment, symlink-escape, or out-of-repo paths.

## Package Markdown Template

```md
# Work Package: WP1 — <title>

## Scope
<Package-specific outcome, boundaries, caller contracts, and explicitly excluded nearby work.>

## Assigned Slices

### `.planning/<concept-slug>/slices/<slice-name>.md`
Must satisfy:
- `<H3-ID>` — <H3 title or short obligation>

Context only:
- `<H3-ID>` — <why this package must read it even though closure belongs elsewhere>

Use `- None.` when the plan has no Slices.

## Primary Paths
- `path/to/inspect/first`

## Verification Expectations
- <Expected command, static inspection, edge/failure case, no-mock boundary, or manual observation.>

## Proof
- `.tasks/<feature-name>/proofs/WP1.proof.md`

## Package Verification Report
- `.tasks/<feature-name>/reports/WP1.package-verification.md`

## Dependencies
- None.

## Notes
- Optional: approved deferrals, risk/replan triggers, package-specific constraints.
```

`sliceproof.py` mechanically requires `Scope`, `Assigned Slices`, `Primary Paths`, `Verification Expectations`, `Proof`, `Package Verification Report`, and `Dependencies`. `Notes` is optional.

## Package Rules

- Scope states owned behavior and boundaries in implementation-agent terms.
- `Must satisfy` IDs are package closure obligations and require proof rows.
- `Context only` IDs are required reading/context; do not use them to hide package obligations.
- Every material H3 in the full Slice inventory must be assigned, context-only with a concrete reason, or explicitly approved as deferred/out of scope/rejected.
- Primary paths are starting points, not hard boundaries.
- Verification expectations must be package-specific and cover relevant edge, failure, trust-boundary, data, security, privacy, performance, concurrency, generated-contract, and lifecycle cases or state why not applicable.
- Proof and report paths are declared during planning; evidence and reports are produced later.
- Dependencies are package-level sequencing constraints and must match the registry.

## Fail Closed When

- Registry contains package assignment or evidence details.
- Package Markdown omits a required section or declared proof/report path.
- A package boundary hides a material Slice obligation.
- Verification expectations are generic boilerplate rather than observable package checks.
- A package cannot be verified independently with the declared proof/report surfaces.
