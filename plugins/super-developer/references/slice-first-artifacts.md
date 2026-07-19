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
              "control_plane_reserve": {"maximum": 1, "issued": 0, "reservation": null}},
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
Budget `maxima`/`issued` use identical non-empty safe counter keys: finite preauthorization planning/correction/
spike/command and implementation `repair_waves`, delegated-call, command, and cost totals. Values are non-negative;
issued never decreases or exceeds fixed maxima/times. Each budget has absolute timezone-aware `started_at`/
`deadline_at`; an active reservation names owner/budget/generation and positive units already charged. Repair-wave
maximum is low ≤1, standard ≤2, and an explicit finite integer for high. The separate fixed control reserve is 0/1.
Its optional one-unit `reservation{id,generation,operation,reason,expected_parent,checkpoint_digest,conflict_digest}`
is only `safe-checkpoint|last-verified` for budget exhaustion or ownership/CAS loss, cannot coexist with semantic work,
and never authorizes calls, commands, repair, tests, evidence, mutation, or takeover.
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
Thus blocked resolution and explicit repair progression remain legal; resetting a progressed state to `pending`
additionally requires a reviewed effective-digest change. `last_verified` is null only at generation 1 and later binds the exact
quiescent prior commit/state digest/generation. Authorized state requires `assurance_profile` plus package-complete
`package_modes` (`boundary|final`); routing/membership change requires an effective-digest transition.
Each serious cluster stores canonical identity text `accepted_invariant`, `root_mechanism`, `architectural_surface`;
`id` is the canonical JSON digest of exactly those fields. It separately stores append-only `observed_signatures`,
all observed classes, any selected observed class at the strongest precedence rank, its route, strike 1–2,
disposition, and at most one immutable `repair{root_cause_digest,affected_surface_digest}` plus matching
`closure{verdict,affected_surface_digest,evidence_digest}`. Eligible clusters start strike 1; PASS closes at 1,
FAIL opens the circuit at 2, and terminal lineage is immutable.
`freeze` is null or `{id,path,digest}` at `.tasks/<feature>/assurance/<freeze-id>/freeze.json`. Canonical F binds
schema/kind/id, authorization ID/effective digest, code checkpoint ref/commit/tree/base/raw-diff/clean-status,
exact typed semantic manifest, runtime and command-result path/digests, profile/modes, exact boundary `B[*]`, sorted
zero-or-more high specialist lenses, cluster digest, and `frozen_at`. The semantic manifest is exactly SPEC, registry,
packages, proofs, boundary reports, and Slices—never Lifecycle State or `C/R/S/U/V`.
Receipt pointers are `{role,lens,path,digest,freeze_digest}`. Canonical same-freeze JSON paths are `combined.json`,
`review.json`, `specialists/<lens>.json`, `audit.json`, and `verification-summary.json`; files bind authorization/F,
exact predecessor pointers, `recorded_at`, and role verdict(s). V has only deviations/limitations, never semantic
PASS. Existing freeze files are append-only; same-freeze pointers cannot mutate. Lifecycle `artifact_checkpoint`
SHA/tree remains the effective-authorization semantic checkpoint, exposed as `lifecycle_artifact_checkpoint`;
mutable artifact ref/HEAD carries self-containing V and is verified as `verification_summary_checkpoint`. A4 keeps
shape/transition semantics; B3/B4 own read-only completion validation with explicit roots/feature/profile equation.
## Lightweight Registry
`tasks.json` remains bookkeeping only: no scope prose, assignment detail, proof/report body, lifecycle/history,
commands, findings, or task bodies. Required top-level fields are `feature`, `title`, `status`, `spec_path`,
`authoritative_slices`, `assurance_profile` (`low|standard|high`), and non-empty `work_packages`. Every package
requires `id`, `path`, `proof_path`, `verification_mode` (`boundary|final`), `report_path`, `status`, and
`depends_on`. `report_path` is a safe artifact-root-relative report path for `boundary` and exactly `null` for
`final`; substitutes are invalid. Paths are safe artifact-root-relative POSIX paths; IDs are contiguous `WP<N>`,
dependencies declared/acyclic, and statuses controlled. `authoritative_slices` may be empty only for Index-only
plans. The helper parses this shape strictly and rejects final report substitutes.
## Package Markdown and Proof
Package Markdown is a cold-readable assignment with `## Scope`, `## Assigned Slices`, `## Primary Paths`,
`## Verification Expectations`, `## Proof`, `## Independent Verification`, and `## Dependencies`:

```md
## Independent Verification
- Mode: `boundary | final`
- Report: `<safe path> | None — final assurance`
- Rationale: <named boundary/risk reason>
```

Mode/report must equal registry values. Rationale names the boundary/risk for `boundary`; `final` explicitly says
semantic verification is deferred to final assurance and uses `Owner: <direct-final role>` (plus `lens: <risk>` for
high). Assigned H3s split into `Must satisfy` closure rows and required-reading `Context only`.

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

Append helper-emitted `## State Binding` with existing package/proof/Slice/matrix fields plus authorization/
effective digest, profile/mode, worktree/ref, commit/tree, base/diff, runtime-evidence and consumed-contract
digests, and verified-at. Slice digest entries use `path|tier|H3-ID=sha256:<64-hex>` separated by `; `. Hard-tier/
candidate drift loses freshness; `context_only_slice_drift` is non-blocking by default and receives affected-surface classification. Helpers validate bindings, not
semantic truth or sufficiency.
## Review-Code Governance State
`.tasks/<feature>/reviews/review-code-state.json` is compact readiness only: feature, pipeline mode/state/time;
exact refs/commit/diff/file-list/worktree; SPEC/registry/package/proof/report/Slice context and freshness; completed
lenses; `findings.open_serious: []`; and closure flags for no serious regression, widening, fresh evidence, and
audit readiness. It is not proof, transcript, history, or lifecycle authority; stale/missing/uncertain readiness
fails audit handoff.
