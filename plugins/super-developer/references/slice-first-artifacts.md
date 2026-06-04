# Slice-First Planned-Feature Artifacts

Load when creating, validating, or consuming planned-feature artifacts.

## Artifact Set

Planned-feature state is file-based and Slice-first:

- `SPEC.md` records the accepted requirements, constraints, non-goals, and package-level verification expectations.
- `tasks.json` is a lightweight registry under `.tasks/<feature>/tasks.json`.
- Package Markdown files under `.tasks/<feature>/packages/` own package assignment.
- Proof Markdown files under `.tasks/<feature>/proofs/` own package closure evidence.
- Package verification reports under `.tasks/<feature>/reports/` are independent verification receipts.
- `review-code-state.json` is review-code governance readiness for audit handoff.

## Lightweight Registry

`tasks.json` is bookkeeping only. It contains no task bodies, proof evidence, review findings, lifecycle events, or package assignment prose.

Required shape:

```json
{
  "feature": "feature-slug",
  "title": "Human title",
  "status": "planned",
  "spec_path": ".tasks/<feature>/SPEC.md",
  "authoritative_slices": [".planning/<feature>/slices/example.md"],
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

- `feature` is a lowercase slug.
- `status` is a routing signal: `planned`, `reviewed`, `in_progress`, `completed`, `blocked`, or `on_hold`.
- Package `status` is a routing signal: `pending`, `in_progress`, `done`, or `blocked`.
- `authoritative_slices` may be empty only for Index-only plans with no independent Slice obligations.
- All paths are repo-relative POSIX paths and must stay inside the repository.
- Package IDs are `WP<N>` and dependency IDs must reference declared packages.

## Package Markdown Assignment

A package file is the assignment source. It must use:

```md
# Work Package: WP1 — <title>

## Scope
<owned behavior and boundaries>

## Assigned Slices
### `.planning/<feature>/slices/example.md`
Must satisfy:
- `SLICE-001` — <summary>

Context only:
- `SLICE-002` — <summary>

## Primary Paths
- `plugins/...`

## Verification Expectations
- <command, inspection, or scenario expectation>

## Proof
- `.tasks/<feature>/proofs/WP1.proof.md`

## Package Verification Report
- `.tasks/<feature>/reports/WP1.package-verification.md`

## Dependencies
- None.
```

`Must satisfy` Slice IDs require proof rows. `Context only` IDs must be read for package understanding but do not create proof rows.

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

## Package Verification Report Receipt

A report file confirms independent package verification occurred after proof evidence was available. It must include:

```md
# Package Verification Report: WP1 — <title>

## State Binding
- Package: `WP1`
- Proof: `.tasks/<feature>/proofs/WP1.proof.md`
- Proof Digest: `sha256:<proof markdown digest>`
- Worktree: `<verified worktree path>`
- Git Ref: `<branch or detached ref>`
- Commit: `<commit>`
- Verified At: `<ISO-8601 timestamp>`

## Verification Result
- Result: `passed`
- Reviewer: `<agent or reviewer id>`
- Scope: `<what was verified>`

## Checks
- <checks performed>

## Open Findings
- None.
```

The proof digest binds the report to the proof content. If proof content changes after the report, package freshness is lost until a new report is produced.

## Review-Code Governance State

`review-code-state.json` is written by review-code after the planned-feature review/fix loop is audit-ready. It is governance state, not proof evidence.

Minimum durable fields:

```json
{
  "feature": "feature-slug",
  "state": "ready_for_audit",
  "reviewed_ref": "feature/<feature>",
  "reviewed_commit": "<commit>",
  "captured_at": "<ISO-8601 timestamp>",
  "open_serious_findings": 0,
  "proofs_and_reports_fresh": true,
  "scope": "planned-feature review-code readiness"
}
```

Audit must fail closed when this state is missing, not `ready_for_audit`, not bound to the reviewed state, or reports unresolved serious findings.
