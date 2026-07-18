# Slice-First Planned-Feature Artifacts

## Boundary

This reference owns artifact roles and file shapes. `artifact-store.md` owns mandatory sidecar-only authority,
legacy import, roots, portability permission, Lifecycle State, and checkpoint ordering. Slice authority lives in
`conceptualize-slice-authority.md`; sizing in `work-packages.md`; completion/freshness in `package-lifecycle.md`;
commands in `tool-usage.md`. Pass `plugins/super-developer/references/package-verification-report.md` directly to
package verifiers.

## Artifact Set

Planned-feature state is file-based, Slice-first, and authoritative only in the distinct namespaced sidecar.
Every path below is sidecar artifact-root-relative; code/plugin/test paths resolve under the named code root.
Equal/current roots fail closed and legacy copies are input only until safely migrated and revalidated.

- `.planning/<concept-slug>/slices/*.md` — authoritative product/design Slices when present.
- `.tasks/<feature>/SPEC.md` — accepted requirements, constraints, non-goals, Slice inventory, and package-level verification summary.
- `.tasks/<feature>/tasks.json` — lightweight registry only.
- `.tasks/<feature>/packages/<WP-ID>.md` — package assignment.
- `.tasks/<feature>/proofs/<WP-ID>.proof.md` — package closure evidence.
- `.tasks/<feature>/reports/<WP-ID>.package-verification.md` — independent package verification receipt with a durable deliverable completeness matrix.
- `.tasks/<feature>/semgrep/<WP-ID>.semgrep.json` and `.semgrep-summary.json` — optional local raw/summary Semgrep package evidence when Semgrep was enabled or contracted.
- `.tasks/<feature>/semgrep/integration.semgrep.json` and `.semgrep-summary.json` — optional one-shot integrated Semgrep evidence for concrete cross-package/shared-surface risk.
- `.tasks/<feature>/reviews/review-code-state.json` — review-code governance readiness for audit handoff.
- `.tasks/<feature>/lifecycle-state.json` — compact mechanical CAS continuation snapshot initialized on first
  publication; subordinate to Slices/SPEC and never a product authority, completion proof, or event history.

## Lightweight Registry

`tasks.json` is bookkeeping only. It contains no package scope prose, Slice assignment details, proof evidence,
review findings, Lifecycle State, lifecycle history, command output, or detailed task bodies.

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

A report confirms independent package verification occurred after proof evidence was available, semantically checks deliverable completion, and binds verification to current proof/source/code state through helper-readable metadata.

Canonical source body starts with `## Package Verification: <WP-ID>` and includes, in order:

- `### Verdict` with `PASS` or `FAIL`.
- `### Deliverable Completeness Matrix` using the fixed columns `Source ID`, `Row Type`, `Deliverable`, `Evidence Type`, `Evidence Refs`, `Exactness / Risk Disposition`, and `Verdict`.
- `### Triggered Risk Selection Notes`, verifier-owned `### Test Review Scope` for the package-owned reviewed delta, `### Slice Closure Review`, and `### Code Review Findings`.
- For failures, `### Blocking Findings` and `### Repair Guidance`.

Matrix rows cover assigned `Must satisfy` Slice H3 IDs, package verification expectations as stable `VE-<n>` rows, and verifier-selected triggered risks as explicit `RISK-<...>` rows. Clean completion requires every mandatory row to be `delivered` with structurally valid non-placeholder code/test/static/command/manual evidence refs and a canonical test-review receipt. Dirty verdicts (`missing`, `partial`, `contradicted`, `unverified`) block completion; `### Slice Closure Review` or proof prose alone is insufficient. Helpers validate exact receipt grammar, positive counts, controlled values, placeholders, strict table shape, typed refs, source bindings, and clean verdicts only; verifiers and final auditors judge contradictions, semantic sufficiency, and claim truthfulness.

Append `## State Binding` from `emit-state-binding` with package path, package Markdown digest, proof path/digest, assigned Slice paths, section-scoped tier-aware `Assigned Slice Digests` (`path|tier|H3-ID=sha256:<64-hex>` entries separated by `; `, or `none`), `Matrix Source Snapshot` over package Markdown plus `must_satisfy` section blocks only, reviewed worktree/ref/commit, and timestamp. See `plugins/super-developer/references/package-verification-report.md` for the full report template, evidence-ref grammar, malformed-binding fail-closed rules, and `context_only_slice_drift` advisory disposition. If proof content, hard-tier source inputs, cited evidence, Test Review Scope inputs, or reviewed implementation state changes after the report, freshness is lost until a new source report/state binding is produced; advisory-only `context_only` drift is non-blocking by default and routed through affected-surface classification.

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
