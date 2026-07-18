# Slice-First Planned-Feature Artifacts

## Boundary

This reference owns artifact roles and file shapes. `artifact-store.md` owns sidecar authority, roots, migration,
permission, and checkpoint order. Slice authority lives in `conceptualize-slice-authority.md`; sizing in
`work-packages.md`; completion/freshness in `package-lifecycle.md`; commands in `tool-usage.md`. Pass
`plugins/super-developer/references/package-verification-report.md` directly to package verifiers.

## Artifact Set

All paths are relative to the distinct namespaced artifact root; source/test paths resolve under the code root.
Equal/current roots fail closed for planned authority; legacy copies are migration input only.

- `.planning/<feature>/slices/*.md` — authoritative product/design Slices when present.
- `.tasks/<feature>/SPEC.md` — accepted requirements, constraints, and verification summary.
- `.tasks/<feature>/tasks.json` — lightweight registry only.
- `.tasks/<feature>/packages/<WP-ID>.md` — assignment; `proofs/<WP-ID>.proof.md` — closure evidence.
- `.tasks/<feature>/reports/<WP-ID>.package-verification.md` — independent package receipt and deliverable completeness matrix.
- `.tasks/<feature>/semgrep/*.{semgrep.json,semgrep-summary.json}` — optional local package/integration evidence.
- `.tasks/<feature>/reviews/review-code-state.json` — governance readiness for audit handoff.
- `.tasks/<feature>/lifecycle-state.json` — subordinate mechanical CAS continuation snapshot, never product authority,
  semantic proof, an event log, or permission to perform its named next action.

## Compact Lifecycle State — Schema 1

The helper derives the path from `--feature`; no state path field or CLI path is accepted. Required top-level keys:

```json
{
  "schema_version": 1, "generation": 1, "feature": "feature-slug",
  "stage": "conceptualization-checkpoint", "quiescent": true, "next_legal_actions": ["preflight"],
  "owner": {"token": "owner-token", "host": "host-token", "disposition": "active", "takeover": null},
  "artifact_checkpoint": {"ref": "refs/heads/artifacts/feature-slug", "sha": null, "tree": null},
  "code_checkpoint": null,
  "authorization": {"id": null, "initial_digest": null, "effective_digest": null,
                    "inputs": null, "amendment_link": null},
  "budgets": {"preauthorization": null, "implementation": null, "active_reservation": null,
              "control_plane_reserve": {"maximum": 1, "issued": 0}},
  "packages": {}, "wave": null, "serious_clusters": [], "freeze": null, "receipts": [],
  "last_verified": null, "portability_authorization": "explicit instruction or durable preference"
}
```

Controlled stages cover conceptualization/checkpoint, preflight, planning/review/readiness/authorization-pending,
authorized/activation/package-wave/quiescent/integration, technical reassessment/review, final assurance,
completed, blocked, and needs-decision. Generation 1 is initial topology: artifact SHA/tree, code, all
authorization fields including `inputs`/amendment, freeze, and last-verified are null; packages, wave, clusters, and
receipts are empty. Initial publication with a code ref is invalid. Later code checkpoints require complete
Implementation Authorization.

Authorization is all null before authorization and complete afterward. Its one immutable `inputs` object has exact
`artifact_tree` and `base_commit`, plus SHA-256 `clean_status`, `dependencies` (dependency/prerequisite snapshot),
`routing`, `actions`, `budget_authority`, and `amendment_policy`. It contains digests, not copied plan/action text.
`initial_digest` equals canonical sorted-key compact UTF-8 JSON SHA-256 of exactly `inputs`; initial
`effective_digest` equals it. The helper verifies exact base/artifact objects, the initial tree/checkpoint relation,
initial routing against required `assurance_profile` plus complete `package_modes`, and fixed budget authority.
`routing` digests exactly those two lifecycle values. `budget_authority` digests each budget's `maxima`, `started_at`,
`deadline_at`, plus control-plane `maximum`; mutable issued/reservation usage is excluded. ID, inputs, and initial
digest are immutable.

`amendment_link` is non-null only in the snapshot whose effective digest changes; it contains
`parent_effective_digest`, cold-reviewed `amendment_digest`, and exact current `artifact_sha`. The artifact must be
a distinct reviewed descendant checkpoint on the exact sidecar lineage. Effective digest is canonical SHA-256 over
those values (key `technical_amendment_digest`). The next unchanged snapshot clears the link; Git preserves prior
links and no sequence/history array is allowed. Canonical state/prior digests use the same JSON rule.

Budget `maxima`/`issued` use the same non-empty safe counter keys, including finite preauthorization planning,
correction, spike, and command categories plus implementation repair/call-by-role/command/cost categories as
applicable. Values are non-negative and issued cannot exceed maxima. Each budget has timezone-aware
`started_at`/`deadline_at`; an active reservation names owner, budget, generation, and positive units already
charged to issued usage. Across the exact predecessor, maxima/times stay fixed and issued usage never decreases;
the control-plane reserve is fixed and monotonic.

`packages` maps `WP<N>` to current `state`/`wave`; `wave` names current id/generation/state/package ids. Allowed
same-effective-digest package successors are explicit:

| From | Allowed next state (including self) |
|---|---|
| `pending` | `pending`, `in_progress`, `blocked`, `invalidated` |
| `in_progress` | `in_progress`, `stabilized`, `blocked`, `invalidated` |
| `stabilized` | `stabilized`, `verified`, `in_progress`, `blocked`, `invalidated` |
| `verified` | `verified`, `done`, `in_progress`, `blocked`, `invalidated` |
| `done` | `done`, `invalidated` |
| `blocked` | `blocked`, `pending`, `in_progress`, `invalidated` |
| `invalidated` | `invalidated`, `in_progress`, `blocked` |

Thus blocked resolution and explicit repair progression remain legal. Resetting `in_progress`, `stabilized`,
`verified`, `done`, or `invalidated` to `pending` is a replan and additionally requires a reviewed effective-digest
change. `serious_clusters` contains canonical SHA-256 ids, strikes 1–2, and disposition. `freeze` is optional;
receipt pointers contain role, safe path, digest, and optional freeze digest. `last_verified` is null only at
generation 1; later it binds an exact quiescent prior commit/state digest/generation. After authorization,
`assurance_profile` and exact package-complete `package_modes` (`boundary|final`) are required; changing routing or
package membership requires an effective-digest transition.

Schema 1 validates only current mechanical shapes and A4 transitions. It does not interpret receipt roles,
predecessors, verdicts, freeze equations, Verification Summary, or `completed` semantics; B3/B4 own those rules.

## Lightweight Registry

`tasks.json` remains bookkeeping only: no scope prose, assignment detail, proof/report body, lifecycle/history,
commands, findings, or task bodies. Required fields are `feature`, `title`, `status`, `spec_path`,
`authoritative_slices`, and non-empty `work_packages`; package entries require `id`, `path`, `proof_path`,
`report_path`, `status`, and `depends_on`. Paths are safe artifact-root-relative POSIX paths; package IDs are
contiguous `WP<N>`, dependencies declared/acyclic, and statuses retain their controlled values.
`authoritative_slices` may be empty only for an Index-only plan with no independent Slice obligation.
`assurance_profile` and package `verification_mode` are optional forward-compatible fields in this slice;
unknown values fail.

## Package Markdown and Proof

Package Markdown is a cold-readable assignment with `## Scope`, `## Assigned Slices`, `## Primary Paths`,
`## Verification Expectations`, `## Proof`, `## Package Verification Report`, and `## Dependencies`. Assigned Slice
H3s split into `Must satisfy` closure rows and required-reading `Context only` rows; context alone creates no proof
row unless another package owns it.

Proof Markdown requires package/slice scope, Slice and expectation closure tables, commands, files, gaps/deviations,
and completion statement. Closure values are `PASS`, `DEFERRED`, or `N/A`; `OPEN`, `GAP`, placeholders,
missing/duplicate/unexpected rows, or unapproved deferral/N/A/gap text fail closed. Deferral/N/A/gap metadata
requires explicit approval, provenance, and scope; N/A also requires rationale.

## Package Verification Report

The canonical report starts `## Package Verification: <WP-ID>` and includes ordered `### Verdict`,
`### Deliverable Completeness Matrix`, `### Triggered Risk Selection Notes`, `### Test Review Scope`,
`### Slice Closure Review`, and `### Code Review Findings`; FAIL adds findings/guidance. Matrix columns remain
`Source ID`, `Row Type`, `Deliverable`, `Evidence Type`, `Evidence Refs`, `Exactness / Risk Disposition`, `Verdict`;
clean completion requires delivered mandatory Slice/`VE-<n>` rows, verifier-selected `RISK-<...>` rows when any,
and typed non-placeholder code/test/static/command/manual anchors. `missing`, `partial`, `contradicted`, or
`unverified` blocks; proof prose or Slice Closure Review alone is insufficient.

Append helper-emitted `## State Binding` with package/proof paths and digests, Assigned Slices, section-scoped
`Assigned Slice Digests` (`path|tier|H3-ID=sha256:<64-hex>` separated by `; `), Matrix Source Snapshot over package
Markdown plus must-satisfy blocks, Worktree, Git Ref, Commit, and Verified At. Hard-tier/current proof/package/code
or cited-evidence drift loses freshness. `context_only_slice_drift` is non-blocking by default and receives
affected-surface classification. Helpers validate grammar/bindings, not semantic truth or sufficiency.

## Review-Code Governance State

`.tasks/<feature>/reviews/review-code-state.json` is compact readiness only: feature, pipeline mode/state/time;
exact refs/commit/diff/file-list/worktree; SPEC/registry/package/proof/report/Slice context and freshness; completed
lenses; `findings.open_serious: []`; and closure flags for no serious regression, widening, fresh evidence, and
audit readiness. It is not proof, transcript, history, or lifecycle authority; stale/missing/uncertain readiness
fails audit handoff.
