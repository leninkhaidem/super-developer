# Slice-First Planned-Feature Artifacts

## Boundary

This reference owns artifact roles and file shapes. Use `artifact-store.md` for artifact root/code root,
sidecar branch/worktree, slug mapping, and sidecar checkpoint vocabulary. Slice authority lives in
`conceptualize-slice-authority.md`; package sizing lives in `work-packages.md`; completion and repair
live in `package-lifecycle.md`; command shapes live in `tool-usage.md`. The lightweight package verification
report shape is shared in `plugins/super-developer/references/package-verification-report.md` and should be
passed directly to package verifiers.

## Artifact Set

Planned-feature state is file-based and Slice-first. Paths below are artifact-root-relative unless a
current-root artifact store is explicitly selected; code, plugin, and test paths resolve under the code root.

- `.planning/<concept-slug>/slices/*.md` — authoritative product/design Slices when present.
- `.tasks/<feature>/SPEC.md` — accepted requirements, constraints, non-goals, Slice inventory, and the executable feature-level `## Acceptance` gate.
- `.tasks/<feature>/tasks.json` — lightweight registry only.
- `.tasks/<feature>/packages/<WP-ID>.md` — package assignment, including the frozen `## Acceptance Checklist`.
- `.tasks/<feature>/reports/<WP-ID>.package-verification.md` — independent package result (Verdict, Acceptance Checklist Result, Blocking findings, Advisory notes, Reviewed state, Gaps).
- `.tasks/<feature>/semgrep/<WP-ID>.semgrep.json` and `.semgrep-summary.json` — optional local Semgrep evidence when enabled or contracted.

## Lightweight Registry

`tasks.json` is bookkeeping only. It contains no package scope prose, Slice assignment details, result evidence,
review findings, lifecycle history, command output, or detailed task bodies.

Legacy registry entries that declare `proof_path` are not new-shape and must not be migrated silently.

Required shape:

```json
{
  "feature": "feature-slug",
  "title": "Human title",
  "status": "planned",
  "spec_path": ".tasks/<feature>/SPEC.md",
  "authoritative_slices": [".planning/<concept-slug>/slices/example.md"],
  "work_packages": [
    {
      "id": "WP1",
      "path": ".tasks/<feature>/packages/WP1.md",
      "report_path": ".tasks/<feature>/reports/WP1.package-verification.md",
      "status": "pending",
      "depends_on": []
    }
  ]
}
```

Rules:

- `feature` is a filesystem-safe slug.
- feature `status` is one of `planned`, `reviewed`, `in_progress`, `completed`, `blocked`, or `on_hold`.
- package `status` is one of `pending`, `in_progress`, `done`, or `blocked`.
- `authoritative_slices` may be empty only for Index-only plans with no independent Slice obligations.
- all artifact paths are POSIX paths relative to the selected artifact root and must stay inside it;
- package IDs are contiguous `WP<N>` values and dependencies reference declared packages.

## Package Markdown Assignment

Package Markdown owns assignment and must be self-sufficient for a package agent reading files cold.

Required sections:

```md
# Work Package: WP1 — <title>

## Scope
<owned behavior and boundaries>

## Assigned Slices
### `.planning/<concept-slug>/slices/example.md`
Must satisfy:
- `SLICE-001` — <summary>

Context only:
- `SLICE-002` — <summary and reason>

## Primary Paths
- `plugins/...`

## Verification Expectations
- <command, inspection, or scenario expectation>

## Acceptance Checklist
- AC-1: <package outcome> — check: `<command or test id>` — expected: <observable pass condition>

## Package Verification Report
- `.tasks/<feature>/reports/WP1.package-verification.md`

## Dependencies
- None.
```

`Must satisfy` Slice IDs map onto Acceptance Checklist items. `Context only` IDs must be read and respected but do not create result rows unless another package owns them. `## Acceptance Checklist` is the frozen closed done-definition (see `package-lifecycle.md`). Every package needs at least one independently confirmable executable check.

## Package Verification Report

A lightweight result confirming the package was verified against its frozen `## Acceptance Checklist`. See
`plugins/super-developer/references/package-verification-report.md` for the full shape. It contains, in order:

- `### Verdict` with `PASS` or `FAIL`;
- `## Acceptance Checklist Result` — each item → pass/fail, pointer, and orchestrator-observed output;
- `## Blocking findings` — correctness/security/data-loss/contract-break findings, or `none`;
- `## Advisory notes` — non-blocking observations, or `none`;
- `## Reviewed state` — worktree/ref/commit of the verified code;
- `## Gaps` — `none` or approved provenance and scope.

PASS requires every checklist item `pass` with authentic observed evidence, no open blocking finding, and no
unapproved gap. Mechanical helper output is structural only; it does not establish semantic completion.
