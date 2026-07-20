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
- `.tasks/<feature>/proofs/<WP-ID>.proof.md` — package closure evidence.
- `.tasks/<feature>/reports/<WP-ID>.package-verification.md` — lightweight independent package verification result (Acceptance Checklist Result + blocking/advisory findings + reviewed state).
- `.tasks/<feature>/semgrep/<WP-ID>.semgrep.json` and `.semgrep-summary.json` — optional local Semgrep evidence when enabled or contracted.

## Lightweight Registry

`tasks.json` is bookkeeping only. It contains no package scope prose, Slice assignment details, proof evidence, review findings, lifecycle history, command output, or detailed task bodies.

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
      "proof_path": ".tasks/<feature>/proofs/WP1.proof.md",
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

## Proof
- `.tasks/<feature>/proofs/WP1.proof.md`

## Package Verification Report
- `.tasks/<feature>/reports/WP1.package-verification.md`

## Dependencies
- None.
```

`Must satisfy` Slice IDs require proof rows. `Context only` IDs must be read and respected but do not create closure rows unless another package owns them. `## Acceptance Checklist` is the frozen closed done-definition (see `package-lifecycle.md`).

## Proof Markdown Closure

A package proof file must contain:

- `## Package Scope`
- `## Assigned Slice Scope`
- `## Slice Closure Table`
- `## Acceptance / Verification Closure`
- `## Commands Run`
- `## Files Changed / Inspected`
- `## Gaps, Deviations, or Deferred Items`
- `## Package Agent Completion Statement`

Closure tables use `PASS`, `DEFERRED`, or `N/A`. `OPEN` and `GAP` block closure. `DEFERRED`, `N/A`, or any non-empty gap/deviation text requires explicit approval, provenance, and scope. Missing rows, duplicate rows, placeholder evidence, unresolved markers, and unapproved gap text fail closed.

## Package Verification Report

A lightweight result confirming the package was verified against its frozen `## Acceptance Checklist`. See
`plugins/super-developer/references/package-verification-report.md` for the full shape. It contains, in order:

- `### Verdict` with `PASS` or `FAIL`;
- `## Acceptance Checklist Result` — each checklist item → `pass`/`fail` + one resolvable evidence pointer;
- `## Blocking findings` — correctness/security/data-loss/contract-break findings, or `none`;
- `## Advisory notes` — non-blocking observations, or `none`;
- `## Reviewed state` — worktree/ref/commit of the verified code.

PASS requires every checklist item `pass` with authentic evidence and no open blocking finding. There is no
deliverable-completeness matrix, test-review receipt, or digest state-binding block. Mechanical helper output is
advisory; it never fails a package whose checklist passes.
