# Assurance Routing

## Boundary

This is the single owner of planned-feature assurance profiles, package routing, receipt ownership, and the
pre-/post-freeze boundary. Work-package acceptance owns test sufficiency; package lifecycle owns candidate
freshness and unlock mechanics; artifact references own file shapes. File, call, test, and evidence volume never
select or lower assurance.

## Feature Profiles

Precedence is `high > standard > low`. `standard` is the default whenever strict low eligibility is not proven and
no high trigger applies.

- **Low** is eligible only for one coherent `final` package with no dependency, independently consumed or material
  contract, boundary, sensitive/shared/public/lifecycle surface, specialist need, or triggered high risk. Every
  condition must be evidenced; uncertainty selects `standard`.
- **Standard** covers ordinary multi-surface work and meaningful internal boundaries. A coherent leaf package may
  route `final`; a package whose output unlocks a dependent or independently consumed material contract routes
  `boundary`.
- **High** applies when any named trigger is material: security, privacy, or safety; persistence, data integrity,
  migration, or rollback; public/external contract or integration; concurrency, idempotency, replay,
  cancellation, or cleanup; or operational/performance/resource behavior whose failure has material impact.
  Every meaningful consumed/shared/public/sensitive/lifecycle boundary routes `boundary`, with enhanced verification
  and any named specialist lens. A coherent high-risk leaf may remain `final` only when its lens is explicitly
  final-assurance-owned and nothing consumes it before freeze. One high trigger wins regardless of lower signals.

Runtime discovery never bypasses this order. A higher trigger invalidates the affected Stable Candidate Identity,
profile/routing, and receipt graph. The Delivery Owner promotes the Technical Plan Baseline, obtains affected cold
review, advances the Effective Authorization Digest and checkpoint, and rebuilds affected candidates/receipts.
Proceed without the user only while envelope, protected effects, covered actions, and budgets remain authorized.
A verifier seeing a higher trigger returns `PROFILE_INVALID`, never `PASS`. Downgrade requires a newly reviewed
baseline and Effective Authorization Digest; ask the user only if envelope, material-risk acceptance, protected
effects, covered actions, or budgets change.

## Package Modes and Unlock

Each package has exactly one mode:

- **`boundary`** — independent package verification produces pre-freeze `B[i]` because the package exposes a
  meaningful dependency, independently consumed material contract, or package-bound high-risk lens.
- **`final`** — semantic verification is owned by final assurance. This is valid only for a coherent leaf with no
  output or risk requiring pre-consumption trust. It has `report_path: null`; never fabricate a package report or
  run package verification merely to satisfy a universal gate.

A dependent dispatch or independently consumed material-contract unlock requires a fresh `PASS B[i]` for the
producer. `B[i]` binds the exact producer candidate and exact consumed-contract digests. Registry `done`, proof,
`SELF_REVIEW`, helper success, merge ancestry, or an unrelated/final receipt cannot unlock it. Package verification
exists only for meaningful `boundary` packages.

## Stable Candidate and Binding

Independent assurance begins only after owner stabilization. **Stable Candidate Identity** is the immutable tuple
of authorization/effective digest; package code commit/tree and base/diff identity; semantic package/Slice inputs;
proof and selected runtime-evidence digests; profile/mode; and consumed-contract digests. Verifier outputs are not
candidate inputs.

`B[i]` preserves the canonical State Binding fields and adds no substitute identity: its package/proof/Slice,
matrix-source, worktree/ref/commit, evidence, profile/mode, and consumed-contract bindings must resolve to that
same candidate. Any bound-input change invalidates the receipt; binding-only refresh is allowed only when semantic
inputs, claims, method, and evidence are identical. Pre-freeze receipts become inputs to the Final Freeze `F`.
Post-freeze outputs never redefine or retroactively validate a candidate.

## One Owner, Lens, and Side of Freeze

Every assurance assignment names exactly one owner, one non-overlapping lens, and one side of `F`:

| Owner / receipt | Lens | Side |
|---|---|---|
| package verifier or package-bound specialist / `B[i]` | package behavior, Selected Causal Evidence, and named consumed contract/risk | pre-freeze |
| combined low verifier / `C` | explicit code-risk and completion verdicts | post-freeze |
| code reviewer / `R` | integrated implementation, merge/contracts/regression, plus direct coverage of `final` packages | post-freeze |
| final specialist / `S[j]` | one named integrated high-risk lens absent from package/code-review ownership | post-freeze, after `R` |
| completion auditor / `U` | accepted-outcome/envelope reconciliation over clean predecessors | post-freeze |
| Delivery Owner | classification, routing, repair, checkpointing, lifecycle | no semantic verdict |

A package specialist assigned to `B[i]` is pre-freeze only and cannot claim final-state coverage. A final specialist
is post-freeze only. Audit does not repeat package, code-review, or specialist lenses. Verification Summary `V`
indexes freeze-scoped outputs and proves nothing independently.

## Serial Final Equations

After the Delivery Owner freezes final inputs as `F`, it dispatches exactly the selected equation:

- **Low:** `F → C(code-risk PASS, completion PASS) → V`. One cold combined read-only verifier owns the named
  `combined-low-assurance` lens and returns both explicit verdicts in `C`; do not dispatch a separate reviewer,
  auditor, or specialist.
- **Standard:** `F → R(PASS/closure) → U(PASS, F, R) → V`. `U` cannot start until `R` is PASS for `F`.
- **High:** `F → R(PASS/closure) → S[*] (each PASS, F, R) → U(PASS, F, R, S[*]) → V`. Each `S[j]` owns one
  named non-overlapping integrated lens and starts only after `R` PASS.

All verifiers, reviewers, auditors, and specialists are cold, read-only, return-only roles. They do not dispatch,
repair, freeze, transition, checkpoint, notify, or invoke a successor. Only the Delivery Owner does those things.
A code-review repair invalidates `R` and `F`; the Delivery Owner finishes repair and required checks, creates a new
`F`, and obtains `R` PASS/closure before any standard/high `S[j]` or `U` starts. Review and audit never run concurrently.
Returned `C/R/S/U` and `V` bind one freeze. Persist them through existing sidecar paths and Lifecycle State only;
do not add a receipt registry, ledger, or orchestration platform.

## Mechanical Enforcement Boundary

The helper requires profile/mode and conditional report paths, parses Selected Causal Evidence, binds boundary
receipts to explicit candidate/contract inputs, and validates the selected pre-freeze package equation. It rejects
final substitutes and controlled Lifecycle State routing mismatch. Helper acceptance never establishes semantic
sufficiency or validates the post-freeze DAG; B4 owns executable final receipt validation.
