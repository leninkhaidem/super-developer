# Slice-First Planned-Feature Artifacts

## Boundary

This reference owns artifact roles and file shapes. Slice authority lives in `conceptualize-slice-authority.md`; package sizing lives in `work-packages.md`; completion and freshness live in `package-lifecycle.md`; command shapes live in `tool-usage.md`.

## Artifact Set

Planned-feature state is file-based and Slice-first:

- `.planning/<concept>/slices/*.md` — authoritative product/design Slices when present.
- `.tasks/<feature>/SPEC.md` — accepted requirements, constraints, non-goals, Slice inventory, and package-level verification summary.
- `.tasks/<feature>/tasks.json` — lightweight registry only.
- `.tasks/<feature>/packages/<WP-ID>.md` — package assignment.
- `.tasks/<feature>/proofs/<WP-ID>.proof.md` — package closure evidence.
- `.tasks/<feature>/reports/<WP-ID>.package-verification.md` — independent package verification receipt.
- `.tasks/<feature>/reviews/review-code-state.json` — review-code governance readiness for audit handoff.

## Lightweight Registry

`tasks.json` is bookkeeping only. It contains no package scope prose, Slice assignment details, proof evidence, review findings, lifecycle history, command output, or detailed task bodies.

Required shape:

```json
{
  "feature": "feature-slug",
  "title": "Human title",
  "status": "planned",
  "spec_path": ".tasks/<feature>/SPEC.md",
  "authoritative_slices": [".planning/<concept>/slices/example.md"],
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
- all paths are repo-relative POSIX paths and must stay inside the repository;
- package IDs are contiguous `WP<N>` values and dependencies reference declared packages.

## Package Markdown Assignment

Package Markdown owns assignment and must be self-sufficient for a package agent reading files cold.

Required sections:

```md
# Work Package: WP1 — <title>

## Scope
<owned behavior and boundaries>

## Assigned Slices
### `.planning/<concept>/slices/example.md`
Must satisfy:
- `SLICE-001` — <summary>

Context only:
- `SLICE-002` — <summary and reason>

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

`Must satisfy` Slice IDs require proof rows. `Context only` IDs must be read and respected but do not create closure rows unless another package owns them.

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

A report confirms independent package verification occurred after proof evidence was available and binds that verification to current proof content through helper metadata.

Canonical source report body:

```md
## Package Verification: WP1

### Verdict
PASS | FAIL

### Slice Closure Review
| Slice ID | Proof status | Evidence sufficient? | Notes |
|---|---|---|---|
| `<Slice ID>` | `PASS` | yes | <concise closure note> |

### Code Review Findings
- None.
```

For failures, add `### Blocking Findings` and `### Repair Guidance` under the same `## Package Verification: WP1` H2. For lifecycle freshness, append helper metadata separately:

```md
## State Binding
Helper/package-lifecycle metadata; the source report body above remains canonical.
- Package: `WP1`
- Package Markdown: `.tasks/<feature>/packages/WP1.md`
- Proof: `.tasks/<feature>/proofs/WP1.proof.md`
- Proof Digest: `sha256:<digest>`
- Assigned Slices: `<comma-separated repo-relative Slice paths in lexicographic order, or none>`
- Worktree: `<absolute reviewed worktree root>`
- Git Ref: `<reviewed branch/ref/commit>`
- Commit: `<reviewed commit hash>`
- Verified At: `<ISO-8601 timestamp>`
```

If proof content or reviewed implementation state changes after the report, freshness is lost until a new source report/state binding is produced. The old H1 / `## Verification Result` replacement shape is not canonical.

## Review-Code Governance State

Canonical path: `.tasks/<feature>/reviews/review-code-state.json`.

`review-code-state.json` is governance readiness only. It is not proof evidence, package evidence, a review transcript, an event stream, or lifecycle history.

Minimum clean audit-handoff state includes:

- `feature`, `mode: "pipeline"`, `state: "ready_for_audit"`, and `captured_at`;
- `reviewed_state` with feature/base/target refs, reviewed commit, diff/file-list checksums, and merge worktree;
- `artifact_context` with SPEC, registry, package/proof/report paths, report freshness, authoritative Slices, and changed-file ownership;
- `lenses` with completed coverage evidence;
- `findings.open_serious: []`;
- `closure_status` with serious findings closed, no serious regression, widening complete, proofs/reports fresh, and ready-for-audit true.

Keep the state compact: bounded current-state summaries and pointers are allowed; package proof bodies, report bodies, transcripts, status history, lifecycle ledgers, and format markers are not.

Audit may run with this state or explicit `none` as optional context. Final merge/readiness fails closed when review-code readiness is missing, not `mode: "pipeline"`, not `state: "ready_for_audit"`, not bound to the reviewed integrated state, has any `findings.open_serious` entry, or has false/uncertain `closure_status.ready_for_audit` or `closure_status.proofs_and_reports_fresh`.
