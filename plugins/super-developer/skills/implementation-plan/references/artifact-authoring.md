# Implementation Artifact Authoring

## Contract

- Apply the packet-supplied canonical artifact model; return `BLOCKED` if its labeled path is missing.
- Write `.tasks/`, Slice inventory, and proof/report declarations under artifact root; source/test paths stay
  code-root-relative. Do not add a requirement, architecture, prerequisite, routing, test, or event ledger.
- `tasks.json` is lightweight bookkeeping. Package Markdown owns assignment and confidence obligations; proof and
  independent report content is produced later.

## Registry Shape

```json
{
  "feature": "<feature-name>",
  "title": "Human-readable title",
  "status": "planned",
  "spec_path": ".tasks/<feature-name>/SPEC.md",
  "authoritative_slices": [".planning/<concept-slug>/slices/<slice-name>.md"],
  "work_packages": [{
    "id": "WP1",
    "path": ".tasks/<feature-name>/packages/WP1.md",
    "proof_path": ".tasks/<feature-name>/proofs/WP1.proof.md",
    "report_path": ".tasks/<feature-name>/reports/WP1.package-verification.md",
    "status": "pending",
    "depends_on": []
  }]
}
```

Use an empty Slice array only for Index-only/no-Slice plans. Registry entries contain only shown fields.
Dependencies are ID-only durable sequencing prerequisites; rationale belongs in package `Notes`. Runtime impact or
failure alone does not create an edge. All artifact paths are root-relative POSIX paths; reject absolute,
traversal, home, drive-qualified, empty-segment, symlink-escape, or out-of-root paths.

## Package Template

```md
# Work Package: WP1 — <title>

## Scope
<Owned outcome/boundaries/caller and consumed contracts/actual production path/observable surfaces/exclusions.>

## Assigned Slices
- None.

## Primary Paths
- `path/to/inspect/first`

## Verification Expectations
- <Confidence obligation: accepted observable or forbidden behavior; distinct mechanism/triggered risk; actual
  production-path seam; cheapest credible causal evidence; substitutes; failure signal; affected broad placement.>

## Proof
- `.tasks/<feature-name>/proofs/WP1.proof.md`

## Package Verification Report
- `.tasks/<feature-name>/reports/WP1.package-verification.md`

## Dependencies
- None.

## Notes
- <prerequisite activation/cleanup, consumed-boundary rationale, assurance `boundary|final` proposal, replan trigger>
```

Required sections are `Scope`, `Assigned Slices`, `Primary Paths`, `Verification Expectations`, `Proof`, `Package
Verification Report`, and `Dependencies`. `Notes` is optional. With Slices, use:

```md
### `.planning/<concept-slug>/slices/<slice-name>.md`
Must satisfy:
- `<H3-ID>` — <title/obligation>
Context only:
- `<H3-ID>` — <concrete reason>
```

## Verification Expectations: Minimum Confidence

- An expectation is a confidence obligation, not a prescribed test or inventory item. It becomes a stable
  `VE-<n>` row source, but one causal test/observation may prove multiple related requirements, H3s, and rows.
  Consolidate overlapping behavior/mechanism/risk obligations rather than creating one test per row.
- Cover accepted observable behavior through the actual-production-path seam; materially relevant forbidden/failure
  outcomes; triggered security/privacy/safety/data/concurrency/lifecycle/compatibility/public-contract risk;
  meaningful consumed contracts at their owning layer; and distinct discovered defect mechanisms.
- State cheapest credible causal evidence level, forced precondition/branch, observed result/transition, forbidden
  outcome, substitutes/mocks/fixtures, and discriminating failure signal. Labels and row counts are not evidence.
- Place earliest credible affected broad regression before freeze for shared discovery/state, lifecycle,
  generated/public contracts, or recursive control flow; do not broaden merely to increase suite volume.
- Seed exact interfaces and forbidden behavior plus applicable interactive UI, retry/fail-closed, trigger precedence, lifecycle/restart/reaper, cache invalidation, model/default precedence, generated defaults, state pollution, authority/publication/cancellation/replay risk. Planner seeds do not limit verifier discovery from package scope, assigned Slices, changed code/diff, selected evidence, and known failure modes.
- Once accepted behaviors and triggered risks have credible causal evidence and required commands pass, test
  authoring stops. Do not add speculative permutations, duplicate layer confidence, trivial wiring/type checks,
  private-detail tests already covered by behavior, or tests merely to populate rows/reports.
- Test count, test LOC, test-to-production ratio, coverage percentage, and suite volume are never acceptance gates.
  Do not require exhaustive suite review or reject/clean existing tests solely for volume. Block only concrete
  evidence defects: false positives, wrong/weakened assertions, hidden skip/focus/xfail, flaky/inconclusive result,
  unsafe side effects, materially unacceptable required runtime, or trust-undermining harness/config change.

## Feasibility and Assurance Notes

When material execution feasibility remains unresolved, record authoritative sources, prerequisites/cleanup, cost,
smallest credible bounded probe or broad-only justification, broad placement, testing-authority provenance, and a
spike/replan trigger; exact budgets come from the resolved authority. A required prerequisite is only
`proven-ready`, `protected-activation-required` with exact later probe/remedy, or `blocked`.

Propose `standard` assurance unless named evidence supports `low` or triggers `high`. Propose `boundary` when output
is independently consumed or is a material shared/public/sensitive/lifecycle boundary; otherwise `final` may be
credible. This remains in SPEC/package authority until the canonical routing contract exists.

## Semgrep Expectations

Disabled means no helper/setup/scan/network requirement. When enabled, use helper `index`/`retrieve`, then
`python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/semgrep_rules.py" scan ...` with local configs; store package raw
and summary outputs under `.tasks/<feature>/semgrep/`, cite both digests, and consume bounded summary/findings.
Never inspect `index.json`, hard-code rule mappings, run raw direct scans, or dump raw JSON.

## Package Rules and Stops

- Scope names owned behavior, actual path, caller/consumed contracts, externally observable UI/CLI/API/docs/logs/
  exports/examples/prompts, and exclusions. Delivered surfaces use audience/domain language, not internal planning.
- Every material Slice H3 is `Must satisfy`, concrete `Context only`, or approved deferred/out-of-scope. Primary
  paths are starting points. Package closure uses semantic complexity; fixed gates count, numeric thresholds do not.
- Dependencies model consumed durable prerequisites, not convenience serialization; use `Notes` for rationale.
- Fail closed for hidden Slice obligations, generic/unverifiable expectations, missing actual path/seam, unresolved
  `blocked` prerequisite, visible surfaces without audience checks, unsafe paths, or unverifiable boundaries.
