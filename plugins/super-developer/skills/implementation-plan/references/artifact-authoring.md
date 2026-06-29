# Implementation Artifact Authoring

## Contract

- Load `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/slice-first-artifacts.md` for the canonical artifact model.
- Write `.tasks/`, proof/report declarations, and Slice inventory paths under the artifact root; keep source/plugin/test paths code-root-relative.
- `tasks.json` is a lightweight registry: feature metadata, Slice inventory, package paths, proof paths, report paths, status signals, and dependencies only.
- Package Markdown is the package assignment source of truth.
- Proof Markdown is generated from package assignment before dispatch and filled by package agents.
- Package verification reports are declared during planning and written by independent package verification; their matrices consume package `## Verification Expectations` as `VE-<n>` row sources.
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

- `feature` must match the safe feature/artifact slug and `.tasks/<feature>/` directory.
- If Conceptualize supplied the plan, `feature` defaults to the concept slug; divergent slugs require explicit approved migration metadata.
- `spec_path` points to the written `SPEC.md` file.
- `authoritative_slices` lists the full safe Slice inventory when Slices exist.
- Each package entry contains only `id`, `path`, `proof_path`, `report_path`, `status`, and `depends_on`.
- Dependencies are package IDs and must match package Markdown.
- Keep registry, package, proof, report, and Slice paths artifact-root-relative POSIX paths.
- Reject absolute, traversal, home, drive-qualified, empty-segment, symlink-escape, or out-of-root paths.

## Package Markdown Template

```md
# Work Package: WP1 — <title>

## Scope
<Package-specific outcome, boundaries, caller contracts, externally observable surfaces when relevant, and explicitly excluded nearby work.>

## Assigned Slices
- None.

## Primary Paths
- `path/to/inspect/first`

## Verification Expectations
- <Expected command, static inspection, edge/failure case, no-mock boundary, audience-surface check, risk/interface seed, or manual observation; this becomes `VE-<n>` in the deliverable matrix.>

## Proof
- `.tasks/<feature-name>/proofs/WP1.proof.md`

## Package Verification Report
- `.tasks/<feature-name>/reports/WP1.package-verification.md`

## Dependencies
- None.

## Notes
- Optional: approved deferrals, risk/replan triggers, package-specific constraints, parallel/serialization rationale.
```

`sliceproof.py` mechanically requires `Scope`, `Assigned Slices`, `Primary Paths`, `Verification Expectations`, `Proof`, `Package Verification Report`, and `Dependencies`. `Notes` is optional.

When Slices exist, replace the `- None.` body with Slice subsections:

```md
### `.planning/<concept-slug>/slices/<slice-name>.md`
Must satisfy:
- `<H3-ID>` — <H3 title or short obligation>

Context only:
- `<H3-ID>` — <why this package must read it even though closure belongs elsewhere>
```

## Semgrep Verification Expectations

When the orchestrator packet says Semgrep is disabled, package Markdown must not require Semgrep setup, scan evidence, or internet access.

When Semgrep is enabled, verification expectations should stay helper-owned and package-scoped:

- use helper `index`/`retrieve` to refresh `.superdeveloper/semgrep/stack-profile.yml`; do not inspect `index.json` or encode static stack-to-rule mappings;
- run package scans through `python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/semgrep_rules.py" scan ...`
  using local configs only, with raw output `.tasks/<feature>/semgrep/<WP-ID>.semgrep.json` and
  summary output `.tasks/<feature>/semgrep/<WP-ID>.semgrep-summary.json`; never require raw direct
  `semgrep` scans;
- cite raw path, raw digest, summary path, summary digest, scan scope, and a concise bounded finding/no-finding summary in proof/report evidence;
- consume findings through `summarize`, then filtered/limited `list-findings`, then
  `show-finding` only for selected refs; excerpts require `--target` plus expected summary digest;
  never require raw JSON dumps;
- integrated scans are conditional one-shot expectations only for concrete cross-package/shared-surface risk.

## Package Rules

- Scope states owned behavior and boundaries in implementation-agent terms.
- If a package creates or changes externally observable surfaces, Scope names them. Surfaces
  include user/operator/consumer-facing UI, CLI output, API responses/errors, generated docs,
  README/operator docs, exported reports/files, logs intended for operators, SDK examples, and
  prompts/templates.
- Delivered surfaces use audience/domain language rather than Super Developer planning workflow,
  package-boundary, implementation-staging, placeholder, or unreleased-work terminology. Terms such
  as `WP`, `work package`, `Slice`, `contract`, `seam`, `downstream package`, `deferred wiring`,
  `stub`, `placeholder`, `fixture`, or `review/audit gate` are leakage indicators only when used
  with internal planning/package/staging meaning; legitimate domain, API, SDK, operator, explicit
  developer-diagnostic, or escaped raw user/provider uses are allowed when audience-appropriate.
- `Must satisfy` IDs are package closure obligations and require proof rows.
- `Context only` IDs are required reading/context; do not use them to hide package obligations.
- Every material H3 in the full Slice inventory must be assigned, context-only with a concrete reason, or explicitly approved as deferred/out of scope/rejected.
- Primary paths are code-root-relative starting points, not hard boundaries.
- Verification expectations must be package-specific and cover relevant edge, failure,
  trust-boundary, data, security, privacy, performance, concurrency, generated-contract,
  audience-surface, and lifecycle cases or state why not applicable.
- Each listed expectation becomes a mandatory deliverable-matrix `VE-<n>` row in package order; if a Slice row proves it, keep the `VE-<n>` row and cross-reference the same evidence.
- Seed visible interface/risk expectations without boilerplate: exact interfaces, forbidden behaviors, interactive UI, retry/fail-closed, trigger precedence, lifecycle/restart/reaper, cache invalidation, model/default precedence, generated defaults, and state pollution when applicable.
- Planner seeds do not limit verifier discovery; verifier packets still require inspection of package scope, assigned Slices, changed code/diff, tests, verification expectations, and known failure modes for emergent triggered-risk rows.
- For externally observable surfaces, verification expectations include surface-appropriate checks
  that delivered text, examples, errors, exports, logs, or prompts are audience-appropriate,
  actionable where needed, redacted when sensitive, and free of planning/workflow leakage.
- Proof and report paths are declared during planning; evidence and reports are produced later.
- Dependencies are package-level sequencing constraints and must match the registry; do not add dependency edges merely to serialize independent work.

## Fail Closed When

- Registry contains package assignment or evidence details.
- Package Markdown omits a required section or declared proof/report path.
- A package boundary hides a material Slice obligation.
- Verification expectations are generic boilerplate, omit visible interface/risk seeds, or imply verifier discovery is limited to planner-declared risks.
- A package changes externally observable surfaces without identifying them or without an audience-language/leakage verification expectation.
- A package cannot be verified independently with the declared proof/report surfaces.
