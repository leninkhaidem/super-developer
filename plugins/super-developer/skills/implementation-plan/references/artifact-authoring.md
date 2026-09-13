# Implementation Artifact Authoring

## Contract

Apply the packet-labeled canonical artifact model before drafting. Write `.tasks/`, Slice inventory, and declared
result paths under the artifact root; source/plugin/test paths are code-root-relative. `tasks.json` is bookkeeping,
package Markdown is the assignment authority, and each `report_path` names the later independent result. Return
`BLOCKED` if the contract label or safe write authority is missing.

## Registry

```json
{
  "feature": "<feature-name>",
  "title": "Human-readable title",
  "status": "planned",
  "spec_path": ".tasks/<feature-name>/SPEC.md",
  "authoritative_slices": [
    ".planning/<concept-slug>/slices/<slice-name>.md"
  ],
  "work_packages": [
    {
      "id": "WP1",
      "path": ".tasks/<feature-name>/packages/WP1.md",
      "report_path": ".tasks/<feature-name>/reports/WP1.package-verification.md",
      "status": "pending",
      "depends_on": []
    }
  ]
}
```

Rules:

- `feature` matches the safe slug and `.tasks/<feature>/`; a Conceptualize slug changes only with approved
  migration metadata. `spec_path` names the written SPEC.
- `authoritative_slices` is the full safe existing Slice inventory. It is empty only for chat-only, Index-only, or
  no-Slice plans with no authoritative Slice file.
- Package entries contain only `id`, `path`, `report_path`, `status`, and `depends_on`. Do not copy scope, H3
  assignment, primary paths, verification, evidence, findings, command output, or lifecycle history into them.
- IDs are stable `WP<N>`. Gaps and registry reorder are valid; never renumber or reuse an ID after reorder, split,
  merge, deferral, or retirement. Replacements receive fresh unused IDs.
- Dependencies are ID-only durable prerequisites and match package Markdown; rationale belongs in Notes.
- All artifact paths are artifact-root-relative POSIX paths. Reject absolute, traversal, home, drive-qualified,
  empty-segment, symlink-escape, or out-of-root paths.

## Package Template

```md
# Work Package: WP1 — <title>

## Scope
<Owned outcome, boundaries, caller contracts, visible surfaces, and excluded nearby work.>

## Assigned Slices
- None.

## Primary Paths
- `path/to/inspect/first`

## Verification Expectations
- <Package-specific command, inspection, risk/interface case, or approved manual observation.>

## Acceptance Checklist
- AC-1: <one outcome> — check: `<command or test id>` — expected: <observable pass condition>
- AC-2: <non-automatable outcome> — check: manual (approved) — verify: <step and expected result>
- AC-3: <forbidden behavior outcome> — check: `<test id>` — expected: <pass condition>
  — rejects: <wrong-but-plausible implementation this check fails against>

## Package Verification Report
- `.tasks/<feature-name>/reports/WP1.package-verification.md`

## Dependencies
- None.

## Notes
- Optional: deferrals; verification profile and evidence/risk reason; execution/replan constraints; sequencing.
```

The helper requires `Scope`, `Assigned Slices`, `Primary Paths`, `Verification Expectations`, `Package Verification
Report`, and `Dependencies`; Notes is optional. Acceptance is the frozen closed package done-definition.

For each assigned Slice, replace `- None.` with:

```md
### `.planning/<concept-slug>/slices/<slice-name>.md`
Must satisfy:
- `<H3-ID>` — <title or short obligation>

Context only:
- `<H3-ID>` — <why closure belongs elsewhere or is unnecessary>
```

## Authoring Rules

- Scope states package-owned behavior and boundaries. Name every changed externally observable surface: UI, CLI,
  API/errors, generated or operator docs, examples, reports/exports, operator logs, SDK material, prompts, or
  templates. Delivered surfaces use audience/domain language and are actionable/redacted where needed. `WP`,
  `Slice`, `contract`, `seam`, `stub`, `placeholder`, and `fixture` are leakage indicators only when they carry
  internal planning/staging meaning; legitimate domain/API/operator/developer-diagnostic or escaped raw input is
  allowed when audience-appropriate.
- `Must satisfy` IDs are closure obligations represented by Acceptance items. `Context only` requires a concrete
  reason and cannot hide work. Every material H3 in the full inventory is assigned, justified as context, or
  durably approved as deferred/out of scope/rejected/narrowed.
- Every material expectation and `Must satisfy` obligation is covered by a concrete executable Acceptance item or
  an explicit user-approved `manual (approved)` exception. Coverage may be many-to-one only for facets of one claim.
- Make each item atomic: one behavioral claim, observable boundary, primary check, and failure condition. Split
  unrelated concerns, subsystems, resource limits, or independent assertions.
- An item proving a Slice `Forbidden behaviors` clause names `rejects:` with a counterfeit implementation its check
  would fail. Prefer observable consequences over structural assertions. Use implementation structure only when no
  observable signal exists, and state why.
- Primary paths are code-root-relative starting points, not hard boundaries. Declare the result path now; produce
  evidence later.
- Apply packet-labeled package closure/dependency rules. Expectations are package-specific and cover applicable
  commands, static inspection, edge/failure/default behavior, trust boundaries, data, security, privacy,
  performance, concurrency, generated contracts, no-mock boundaries, lifecycle, and audience surfaces. A single
  `not-applicable: <dimensions>` line may name only dimensions the SPEC Trust Context already excludes and this
  package does not touch.
- Seed applicable exact-interface, forbidden-behavior, interactive UI, retry/fail-closed, trigger-precedence,
  restart/reaper, cache, model/default, generated-default, and state-pollution checks; identify the triggering
  surface instead of copying a worksheet. Planner seeds never limit verifier discovery from scope, Slices, code,
  tests, expectations, and known failure modes.
- Unresolved material behavior blocks all writes: return `BLOCKED: empirical_evidence_needed` to the orchestrator.
  For non-blocking feasibility, record repository-backed sources/bounds and testing-authority provenance in Notes
  or expectations.
- Dependencies match the registry and represent consumed durable prerequisites, not convenience serialization.
  Put non-obvious output/contract/evidence rationale in Notes.
- Record `standard`/`enhanced` profile seeds and evidence/risk reasons in Notes or expectations, never registry
  schema. A seed does not authorize later ungrounded downgrade while its risk remains.

## Semgrep Expectations

Disabled Semgrep imposes no setup, scan, or internet requirement. When enabled, keep evidence package-scoped:

- refresh the stack profile through helper `index`/`retrieve`; never inspect `index.json` or hard-code mappings;
- invoke only `python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/semgrep_rules.py" scan ...` with local configs,
  writing `<WP-ID>.semgrep.json` and `.semgrep-summary.json` under `.tasks/<feature>/semgrep/`; never require direct
  raw `semgrep` scans;
- cite raw/summary paths, digest, scan scope, and a bounded finding/no-finding summary in result evidence;
- consume via `summarize`, filtered/limited `list-findings`, then selected `show-finding`; excerpts require
  `--target` and the expected summary digest. Never dump raw JSON;
- use an integrated one-shot scan only for a concrete cross-package/shared-surface risk.

## Fail Closed

Do not write when a required section/result path is absent; assignment is hidden in the registry; checklist
coverage, atomicity, executability, or forbidden-behavior falsification fails; a Slice obligation is hidden; visible
surfaces or audience checks are missing; expectations are boilerplate; dependencies are inconsistent; or the
package cannot be independently verified through its declared report.
