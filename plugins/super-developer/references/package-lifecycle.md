# Package Lifecycle, Candidate, Proof, and Receipt Freshness

## Boundary

This reference owns stabilization, Stable Candidate Identity, proof/receipt freshness, completion, and unlock
mechanics. Shapes live in `slice-first-artifacts.md`; sizing and minimum-sufficient test acceptance in
`work-packages.md`; routing/receipt ownership in `assurance-routing.md`; commands in `tool-usage.md`.

## Status and Proof

Registry status is routing only and proves no correctness. Lifecycle successors are the explicit matrix in
`slice-first-artifacts.md`. Blocked resolution and `invalidated|stabilized|verified → in_progress` repair are legal;
`in_progress|stabilized|verified|done|invalidated → pending` requires a reviewed effective-digest replan.

Each package has one artifact-root proof `.tasks/<feature>/proofs/<WP-ID>.proof.md`. Package agents fill only their
proof and assigned code. `PASS` proof rows are implementer claims, not independent acceptance. Before dispatch use
`sliceproof.py create-proof` with explicit artifact/code roots; existing filled proof is never overwritten without
approved replacement/provenance. When Semgrep is enabled, helper-produced raw/summary evidence under the artifact
root may be cited but never replaces judgment.

A stabilization claim requires every assigned `Must satisfy` H3 and `VE-<n>` expectation closed with concrete
implementation/verification evidence; screened commands/inspections and files recorded; no unresolved
`TODO|OPEN|GAP`, unapproved deferral/N/A, Slice plan defect, context-only misuse, or contradiction; and implementer
completion plus `SELF_REVIEW`. Run `validate-proof`; helper success is necessary, never sufficient.

## Stable Candidate Identity

After behavior, causal evidence, earliest credible affected broad regression, full owned-diff inspection, proof,
and cleanup stabilize, freeze one immutable package candidate. Its identity is authorization/effective digest;
code commit/tree and base/diff identity; package/Slice semantic inputs; proof and runtime-evidence digests;
profile/mode; and consumed-contract digests. Verifier output is excluded. The implementer returns this exact tuple.
Any bound input change invalidates the candidate and affected receipt.

## Mode-Specific Completion

Use `assurance-routing.md` to select exactly one mode:

- **`boundary`**: one independent read-only verifier returns fresh `PASS` B[i] for the meaningful boundary; the
  Delivery Owner persists it at the non-null report path. Require clean matrix, `Selected Causal Evidence`, exact
  candidate/proof/State Binding, and consumed-contract digests. Then run `validate-package-complete`.
- **`final`**: allowed only for a coherent leaf with no dependent or independently consumed material contract and
  no package-bound high-risk lens. `report_path` is null. Do not dispatch package verification or fabricate a
  report; retain valid proof/candidate identity and explicit final-assurance deferral. Final semantic closure is
  owned directly by final assurance.

A boundary package may become `done` only after assignment/proof validation, required commands, `SELF_REVIEW`, no
authority blocker, fresh exact `PASS B[i]`, clean `validate-package-complete`, repair/delta closure, merge
freshness, and checkpoint eligibility. A final package may become implementation-`done` after the same gates except
report/verifier, but feature completion remains blocked until its final assurance owner passes.

The helper branches on mode and parses Selected Causal Evidence; its result is mechanical routing/binding evidence,
not semantic proof. The mode-specific command is:
```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-package-complete \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" \
  ".tasks/<feature>/tasks.json" --package <WP-ID>
```

## Dependency and Material-Contract Unlock

A producer with a dependent routes `boundary`. No dependent dispatch or independently consumed material contract
unlocks until its exact candidate and consumed-contract digests have fresh `PASS B[i]` and clean
`validate-package-complete`; registry `done`, proof rows, `SELF_REVIEW`, helper success alone, merge ancestry, or a
`final` receipt cannot unlock it. This is a pre-freeze input, not a post-freeze substitute.

## Freshness Rules

Classify semantic impact, not file/commit count:

- product/assignment inputs: SPEC, package/Slice obligations, expectations, approval, profile/mode/contracts;
- production/public/generated/integration code;
- selected test/observation, assertion/oracle, harness/helper, fixture/mock, generator, and test configuration;
- proof/report claims including `SELF_REVIEW`, matrix/risk, and Selected Causal Evidence sufficiency;
- command/runtime/Semgrep evidence; or report metadata only.

Metadata-only rebinding requires identical semantic inputs, claims, method, and execution evidence. Evidence-only
change requires verifier inspection of provenance, command/harness, prerequisites, environment, assertions,
cleanup, redaction, and a valid non-contradictory result. Failed/inconclusive evidence blocks. Bounded semantic
changes receive fresh focused verification; material, shared, sensitive, cross-boundary, or uncertain impact
widens. Profile/routing/high-trigger change invalidates affected candidates and requires reviewed promotion.
Keep rationale in existing state/proof/report artifacts—never a new receipt, registry field, or ledger.

For impact, load `orchestration-convergence.md`. Canonical serious-cluster identity includes only the accepted
invariant/contract, failure mechanism, and architectural surface; agent, signature, label, commit, and timeout are
not identity. Keep provisional classification in
orchestrator state and repair/verifier packets, never a registry field or standalone impact receipt. `depends_on` is a sequencing lower
bound, not impact proof. Record package Markdown/digest, assigned Slice source/digest, matrix source snapshot, and
matrix evidence anchors; inspect producing prerequisites, consumers in any lifecycle state, and shared surfaces
not represented by a dependency edge until no new affected surface appears. Failure, commit existence, merge ancestry, or dependency reachability alone does not stale a package; classify uncertainty as unbounded.

After repair, reclassify the actual code diff, invalidate affected receipts, run actual-production-path targeted
and earliest credible affected broad regression before refreshing proof/commands, and reclassify the final
code/proof/command-evidence state until stable. Run `validate-proof`, then fresh focused verification for bounded
impact or widen for material/shared/sensitive/uncertain impact; only afterward run `validate-package-complete`.
Never accept intermediate evidence. Initial independent rejection is strike 1 and its failed closure is strike 2;
do not wait for a “first failed closure” to allow repair or a “second failed closure” to stop.

## Exact Receipt Freshness

`B[i]` binds Stable Candidate Identity, package/proof/Slice and matrix snapshots, selected causal anchors and command
outputs, consumed-contract digests, verifier/time/verdict/findings, and optional Semgrep evidence. Missing, failed,
stale, malformed, dirty, contradicted, or mode-incompatible bindings block. `must_satisfy` drift is hard;
`context_only_slice_drift` is non-blocking by default but requires affected-surface classification.

## Final Readiness

Every included package needs valid assignment/proof, no unresolved markers/plan defect, closed repairs, a clean
integration worktree, and mode-correct completion: fresh exact `B[i]` plus helper result for `boundary`; stable
candidate with null report and explicit direct-final owner for `final`. Run package checks and root-aware
`validate-final` for every included artifact set. For stacked readiness identify the top integrated state and all
base/follow-up task/Slice artifact sets; do not audit only a follow-up when base deliverables are included.

Role ownership is non-duplicative. Package verification inspects Selected Causal Evidence plus only changed
harness/configuration that affects its trustworthiness; it owns one named pre-freeze package/contract lens and cannot
claim final-state coverage. Final review owns concrete integrated correctness, evidence, regression, flakiness,
unsafe/shared-harness, material-runtime, merge/contract risk, and direct semantic coverage for `final`; final
specialists and audit retain distinct named lenses. Audit reconciles accepted outcomes and selectively falsifies
high-value claims without rereviewing the suite.

Freeze exact integrated code, semantic artifacts, runtime evidence, profile/routing, and fresh `B[*]` as `F`.
Dispatch only the serial equation in `assurance-routing.md`: low `F→C→V`, standard `F→R→U→V`, or high
`F→R→S[*]→U→V`. Any frozen-input change invalidates downstream outputs. A review repair must finish and create a
new freeze before review closure; standard/high audit or final specialists start only after `R` PASS for that freeze.
Declare readiness only when all profile-required PASS outputs and `V` bind the same top state.

## Observability

Non-gating traces may show version, timing, commands, cleanup, freshness/rerun reason, and repair identity/progress.
Neither may mutate state, be required as proof, or present mechanics as completion.
