# Slice-First Planned-Feature Artifacts
## Boundary
This reference owns artifact roles and file shapes. `artifact-store.md` owns sidecar authority, roots, migration,
permission, and checkpoint order. Slice authority lives in `conceptualize-slice-authority.md`; sizing/test
acceptance in `work-packages.md`; profile/routing in `assurance-routing.md`; completion/freshness in
`package-lifecycle.md`; commands in `tool-usage.md`. Pass
`plugins/super-developer/references/package-verification-report.md` only to a `boundary` verifier.
## Artifact Set
All paths are relative to the distinct namespaced artifact root; source/test paths resolve under the code root.
Equal/current roots fail closed for planned authority; legacy copies are migration input only.

- `.planning/<feature>/slices/*.md` — authoritative product/design Slices when present.
- `.tasks/<feature>/SPEC.md` — accepted requirements, constraints, and verification summary.
- `.tasks/<feature>/tasks.json` — lightweight registry only.
- `.tasks/<feature>/packages/<WP-ID>.md` — assignment; `proofs/<WP-ID>.proof.md` — closure evidence.
- `.tasks/<feature>/reports/<WP-ID>.package-verification.md` — pre-freeze `B[i]` only for `boundary`; absent for `final`.
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
`artifact_commit`, `artifact_tree`, and `base_commit`, plus SHA-256 `clean_status`, `dependencies`
(dependency/prerequisite snapshot), `routing`, `actions`, `budget_authority`, and `amendment_policy`. It contains
digests, not copied plan/action text. `initial_digest` equals canonical sorted-key compact UTF-8 JSON SHA-256 of
exactly `inputs`; initial `effective_digest` equals it. The helper requires `artifact_commit` to be an exact commit
in the artifact root with tree `artifact_tree`; at initial authorization it equals the artifact checkpoint and exact
reviewed predecessor (`last_verified.artifact_sha`/`--previous-commit`). It also verifies the exact base commit,
initial routing against required `assurance_profile` plus complete `package_modes`, and fixed budget authority.
`routing` digests those lifecycle values. `budget_authority` digests each budget's `maxima`, `started_at`,
`deadline_at`, plus control-plane `maximum`; mutable issued/reservation usage is excluded. ID, inputs, and initial
digest are immutable; amendments retain them while `amendment_link` advances the artifact checkpoint.

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
commands, findings, or task bodies. Required top-level fields are `feature`, `title`, `status`, `spec_path`,
`authoritative_slices`, `assurance_profile` (`low|standard|high`), and non-empty `work_packages`. Every package
requires `id`, `path`, `proof_path`, `verification_mode` (`boundary|final`), `report_path`, `status`, and
`depends_on`. `report_path` is a safe artifact-root-relative report path for `boundary` and exactly `null` for
`final`; substitutes are invalid. Paths are safe artifact-root-relative POSIX paths; IDs are contiguous `WP<N>`,
dependencies declared/acyclic, and statuses controlled. `authoritative_slices` may be empty only for Index-only
plans. B2 adds strict helper parsing; B1 authors must follow this shape and must not fabricate final reports.

## Package Markdown and Proof

Package Markdown is a cold-readable assignment with `## Scope`, `## Assigned Slices`, `## Primary Paths`,
`## Verification Expectations`, `## Proof`, `## Independent Verification`, and `## Dependencies`:

```md
## Independent Verification
- Mode: `boundary | final`
- Report: `<safe path> | None — final assurance`
- Rationale: <named boundary/risk reason>
```

Mode/report must equal registry values. Assigned Slice H3s split into `Must satisfy` closure rows and required-
reading `Context only`; context alone creates no proof row unless another package owns it.

Proof Markdown requires package/slice scope, Slice and expectation closure tables, commands, files, gaps/deviations,
and completion statement. Closure values are `PASS`, `DEFERRED`, or `N/A`; `OPEN`, `GAP`, placeholders,
missing/duplicate/unexpected rows, or unapproved deferral/N/A/gap text fail closed. Deferral/N/A/gap metadata
requires explicit approval, provenance, and scope; N/A also requires rationale.

## Package Verification Report

Only a `boundary` package has a report and deliverable completeness matrix. It starts `## Package Verification: <WP-ID>` with ordered `### Verdict`,
`### Deliverable Completeness Matrix`, `### Triggered Risk Selection Notes`, `### Selected Causal Evidence`,
`### Slice Closure Review`, and `### Code Review Findings`; FAIL adds findings/guidance. The matrix keeps canonical
columns and delivered mandatory Slice/`VE-<n>`/triggered `RISK-<...>` rows with typed anchors. Selected Causal
Evidence records typed selected anchors, behavior/risk, sufficiency, substitutes, and fresh command result—never a
changed-population census or volume gate.

Append helper-emitted `## State Binding` with package/proof paths and digests, Assigned Slices, section-scoped
`Assigned Slice Digests` (`path|tier|H3-ID=sha256:<64-hex>` separated by `; `), Matrix Source Snapshot, Worktree,
Git Ref, Commit, and Verified At. It must preserve exact Stable Candidate Identity, profile/mode, evidence, and
consumed-contract bindings. Hard-tier/current candidate drift loses freshness. `context_only_slice_drift` is
non-blocking by default and receives affected-surface classification. Helpers validate grammar/bindings, not
semantic truth or sufficiency; B2 implements the new conditional grammar.

## Review-Code Governance State
`.tasks/<feature>/reviews/review-code-state.json` is compact readiness only: feature, pipeline mode/state/time;
exact refs/commit/diff/file-list/worktree; SPEC/registry/package/proof/report/Slice context and freshness; completed
lenses; `findings.open_serious: []`; and closure flags for no serious regression, widening, fresh evidence, and
audit readiness. It is not proof, transcript, history, or lifecycle authority; stale/missing/uncertain readiness
fails audit handoff.
