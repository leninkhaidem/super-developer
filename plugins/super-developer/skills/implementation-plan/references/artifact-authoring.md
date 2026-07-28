# Implementation Artifact Authoring

## Contract

- Apply the packet-supplied canonical artifact-model contract; return `BLOCKED` if its labeled path is missing.
- Write `.tasks/`, proof/report declarations, and Slice inventory paths under the artifact root; keep source/plugin/test paths code-root-relative.
- `tasks.json` is a lightweight registry: feature metadata, Slice inventory, package paths, proof paths, report paths, status signals, and dependencies only.
- Package Markdown is the package assignment source of truth.
- Proof Markdown is generated from package assignment before dispatch and filled by package agents.
- Package verification reports are declared during planning and written by independent package verification; they record each `## Acceptance Checklist` item as pass/fail with evidence.
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
- Dependencies are ID-only durable sequencing prerequisites and must match package Markdown; rationale belongs in package `Notes`.
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
- <Expected command, static inspection, edge/failure case, no-mock boundary, audience-surface check, risk/interface seed, or manual observation.>

## Acceptance Checklist
- AC-1: <package-level outcome that proves this package is done> — check: `<command or test id>` — expected: <observable pass condition>
- AC-2: <outcome that cannot be automated> — check: manual (approved) — verify: <exact manual step and expected result>

## Proof
- `.tasks/<feature-name>/proofs/WP1.proof.md`

## Package Verification Report
- `.tasks/<feature-name>/reports/WP1.package-verification.md`

## Dependencies
- None.

## Notes
- Optional: deferrals, risk/replan triggers, closure/execution profile, constraints, and sequencing rationale.
```

`sliceproof.py` mechanically requires `Scope`, `Assigned Slices`, `Primary Paths`, `Verification Expectations`, `Proof`, `Package Verification Report`, and `Dependencies`. `Notes` is optional. `## Acceptance Checklist` is the frozen closed done-definition for the package (see Package Rules); extra sections are allowed.

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

When Semgrep is enabled, keep verification expectations helper-owned and package-scoped:

- refresh `.superdeveloper/semgrep/stack-profile.yml` via helper `index`/`retrieve` (never inspect `index.json` or hard-code stack-to-rule mappings);
- run scans only through `python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/semgrep_rules.py" scan ...` with local configs, writing `.tasks/<feature>/semgrep/<WP-ID>.semgrep.json` and `.semgrep-summary.json`; never require raw direct `semgrep` scans;
- cite raw/summary path + digest, scan scope, and a concise bounded finding/no-finding summary in proof/report evidence;
- consume via `summarize` → filtered/limited `list-findings` → selected `show-finding` (excerpts need `--target` + expected summary digest); never dump raw JSON;
- integrated scans are conditional one-shot expectations only for concrete cross-package/shared-surface risk.

## Package Rules

- Scope states owned behavior and boundaries in implementation-agent terms.
- If a package creates or changes externally observable surfaces, Scope names them. Surfaces
  include user/operator/consumer-facing UI, CLI output, API responses/errors, generated docs,
  README/operator docs, exported reports/files, logs intended for operators, SDK examples, and
  prompts/templates.
- Delivered surfaces use audience/domain language, not Super Developer planning/package/staging terminology.
  Terms like `WP`, `Slice`, `contract`, `seam`, `stub`, `placeholder`, or `fixture` are leakage indicators only
  with internal planning/staging meaning; legitimate domain, API, SDK, operator, developer-diagnostic, or escaped
  raw user/provider uses are allowed when audience-appropriate.
- `Must satisfy` IDs are package closure obligations and require proof rows.
- `## Acceptance Checklist` is the **closed, frozen done-definition**: one item per `Must satisfy` obligation and
  per material verification expectation, each an **executable** check (command, test id, or observable output)
  unless it carries a human-approved `manual (approved)` exception. The verifier checks exactly this list —
  nothing invented — so items are concrete and runnable, not aspirational prose.
- `Context only` IDs are required reading/context; do not use them to hide package obligations.
- Every material H3 in the full Slice inventory must be assigned, context-only with a concrete reason, or explicitly approved as deferred/out of scope/rejected.
- Primary paths are code-root-relative starting points, not hard boundaries; proof and report paths are declared during planning, with evidence produced later.
- Apply shared closure-complexity rules; counts are warnings, not thresholds, and fixed package gates count.
- Verification expectations are package-specific and cover relevant edge, failure, trust-boundary, data,
  security, privacy, performance, concurrency, generated-contract, audience-surface, and lifecycle cases or state
  why not applicable. Material unresolved empirical behavior blocks authoring: before writes return
  `BLOCKED: empirical_evidence_needed` to the orchestrator; never invoke `empirical-spike` or hide it in `Notes`.
  For non-blocking execution feasibility, record repo-backed sources/bounds and testing-authority provenance.
- Each listed expectation becomes a concrete `## Acceptance Checklist` item in package order; if a Slice obligation proves it, the same check may cover both.
- Seed visible interface/risk expectations without boilerplate: exact interfaces, forbidden behaviors, interactive UI, retry/fail-closed, trigger precedence, lifecycle/restart/reaper, cache invalidation, model/default precedence, generated defaults, and state pollution when applicable.
- Planner seeds do not limit verifier discovery; verifier packets still require inspection of package scope, assigned Slices, changed code/diff, tests, verification expectations, and known failure modes for emergent blocking findings.
- For externally observable surfaces, verification expectations include surface-appropriate checks
  that delivered text, examples, errors, exports, logs, or prompts are audience-appropriate,
  actionable where needed, redacted when sensitive, and free of planning/workflow leakage.
- Dependencies are ID-only durable sequencing prerequisites and must match the registry. Put non-obvious consumed output, contract, or evidence rationale in `Notes`; runtime impact or failure alone does not create an edge, and edges must not merely serialize independent work.

## Fail Closed When

- Registry contains package assignment or evidence details.
- Package Markdown omits a required section or declared proof/report path.
- A package omits `## Acceptance Checklist`, or a checklist item is neither an executable check nor a human-approved `manual (approved)` exception.
- A package boundary hides a material Slice obligation.
- Verification expectations are generic boilerplate, omit visible interface/risk seeds, or imply verifier discovery is limited to planner-declared risks.
- A package changes externally observable surfaces without identifying them or without an audience-language/leakage verification expectation.
- A package cannot be verified independently with the declared proof/report surfaces.
