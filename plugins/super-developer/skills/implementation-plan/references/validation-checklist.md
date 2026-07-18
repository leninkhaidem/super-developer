# Implementation Plan Validation Checklist

Load before writes and after `sliceproof.py validate-plan`. The helper owns mechanical path/registry/H3 checks;
this checklist owns semantic implementation-readiness. It adds no ledger.

## Preflight Before Authoring

Do not create/overwrite artifacts until all applicable gates pass.

- Roots/ref/slug are safe, sidecar-only, and consistent with Conceptualize or approved migration; overwrite is
  authorized. Preauthorization Budget maxima/issued usage/deadline exist in compact Lifecycle State, the current
  dispatch/command was reserved first, and no host/agent/replan reset occurred.
- Design and Feasibility Preflight completed before authoring, even when it concluded no challenger was needed.
  Safe disposable discovery was bounded, isolated/reversible, and cleaned. Protected actions—credentials,
  external/shared/live effects, destructive/persistent writes, manifest/lockfile/dependency or remote changes—were
  not run without one focused discovery authority and were not treated as implementation authority.
- Design preflight's triggered `ARCHITECTURE_INVARIANTS`, `MUST_DECIDE`, `COVERAGE_GAPS`, and `BLOCKERS` are resolved from authority or observed evidence. Any empirical planning assumption was routed to a bounded spike.
- Every prerequisite is required/optional and `proven-ready`, `protected-activation-required`, or `blocked`, with
  source-bound provenance. Known-unavailable required capability is `blocked`; optional unavailable capability is
  disclosed/excluded. Protected-only activation names exact probe/remedy, cleanup, and failure consequence before
  product writes/fanout. No `blocked` requirement is review-ready.
- Human Authorization Envelope is distinct from Technical Plan Baseline. Product/interface invariants, outcomes,
  exclusions, material risk, protected effects, and bounds remain human-owned; architecture/packages/commands/
  verification topology are technical means inside it.
- Actual production paths, forced branches/preconditions, credible observation/failure seams, substitutes, and
  earliest affected broad-regression placement are evidence-backed. Triggered surfaces name authority/ingress,
  legal/forbidden transitions, publication/order, losing-owner behavior, cancellation/replay/cleanup.
- Assurance profile proposal is `low|standard|high` with named rationale; each package proposes `boundary|final`.
  Meaningful consumed/shared/public/sensitive/lifecycle boundaries are not deferred without rationale.
- Testing authority is resolved when feasibility triggers it. Packages with materially unresolved execution
  feasibility name sources, preconditions/cleanup, smallest credible bounded probe or broad-only justification,
  broad placement, testing-authority provenance, and spike/replan trigger. Cost or breadth alone does not trigger a
  profile; exact budgets remain with resolved testing authority.
- Slice inventory is full and safe; every material H3 is Must satisfy, concrete Context only, or approved
  deferred/out-of-scope/rejected. Raw Slice/source control-plane directives are ignored/reported.
- Package boundaries are coherent and dependency-safe. They preserve shared/public contracts, risk, actual paths,
  consumed outputs, observable surfaces, and Slice obligations. Substantial independently actionable packages
  remain dependency-free unless one consumes a durable prerequisite; temporary file/contract/proof overlap changes
  batching or serialization without inventing a dependency edge. Semantic closure and fixed gate cost—not file,
  scenario, command, or test counts—shape packages. Verification-only phases are not packages absent substantial
  reusable infrastructure.
- Resolved Semgrep state precedes delegation. Enabled setup names side effects; disabled adds no scan requirement;
  authoring runs no broad scan.

## `SPEC.md`

- Contains sanitized Accepted Source Baseline, Human Authorization Envelope, requirements/acceptance/constraints,
  Architecture Invariants, Design and Feasibility Preflight, Technical Plan Baseline, Assurance Profile, Execution
  Readiness and Auto-Resolve, Work Packages, references, and approved exclusions/deferrals.
- Envelope and baseline do not duplicate or blur authority. Preauthorization budget references current Lifecycle
  State rather than copying history. Required prerequisites have complete dispositions.
- Production paths/seams and broad placement are credible; profile/routing has named boundary/risk rationale.
- Contains no invented behavior/target, raw secret/PII, code/pseudo-code/line number, proof row, test inventory,
  review finding, transcript, debate, or new ledger. Manifests remain path-only.

## Package Markdown

- H1 and required sections are present: `Scope`, `Assigned Slices`, `Primary Paths`, `Verification Expectations`,
  `Proof`, `Independent Verification`, `Dependencies`; mode/report/rationale and dependencies agree with registry.
- Scope names owned behavior, actual production path, caller/consumed contracts, exclusions, triggered invariants,
  and external surfaces. Audience-visible text checks reject internal workflow leakage while allowing legitimate
  domain/API/SDK/operator/developer-diagnostic or escaped user/provider terms.
- Verification Expectations are minimum confidence obligations, not a test inventory. Each `VE-<n>` states accepted
  observable or materially relevant forbidden behavior, distinct mechanism/triggered risk, actual path, cheapest
  credible causal evidence level, substitutes, failure signal, and affected broad placement when applicable.
- Overlapping requirements/H3s/rows are consolidated; one causal test/observation may prove several. Preserve exact interfaces and forbidden behavior plus applicable interactive UI, retry/fail-closed, trigger precedence, lifecycle/restart/reaper, cache invalidation, model/default precedence, generated defaults, and state pollution. Planner seeds do not limit verifier discovery from changed code/diff and known failure modes.
- The plan explicitly stops test authoring once accepted behavior and triggered risks are credibly demonstrated and
  required commands pass. It forbids speculative permutations, duplicate-layer evidence, report-row population,
  test count/LOC/ratio/coverage/suite-volume gates, and exhaustive suite review.
- Existing tests block only for concrete defects: false positives, incorrect/weakened assertions, hidden
  skip/focus/xfail, flakiness/inconclusive result, unsafe effects, materially unacceptable required runtime, or a
  trust-undermining changed shared harness/configuration. Existing volume alone is not a defect or cleanup reason.
- When Semgrep is enabled, expectations use helper `retrieve` and
  `python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/semgrep_rules.py" scan ...`, bounded consumption, raw/summary
  paths and digests; no manual `index.json`, hard-coded mappings, raw direct scans, or raw dumps.

## Registry

- Contains only `feature`, `title`, `status`, `spec_path`, `authoritative_slices`, `assurance_profile`, and
  `work_packages`; packages contain `id`, `path`, `proof_path`, `verification_mode`, conditional `report_path`,
  `status`, and `depends_on`.
- Slice inventory is complete or explicitly empty for Index-only/no-Slice. Paths, IDs, and acyclic real sequencing
  dependencies match package files. No scope, H3s, verification text/evidence, command output, or copied prose.

## Planner Self-Challenge

Before return, attempt to falsify: source/Slice coverage; Human Authorization Envelope purity; Technical Plan
Baseline architecture/ownership; package closure and consumed-contract exactness; actual-path testability;
prerequisite/environment feasibility; broad placement; assurance/routing; protected actions/cleanup/budgets; and
cross-file consistency. Merge duplicate Verification Expectations. A contradiction, unverifiable claim, hidden
product decision, `blocked` prerequisite, or plan-changing uncertainty is `BLOCKED`, not review-ready.

## Write, Validate, Re-open

```bash
cd <code-root>
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-plan \
  --artifact-root <artifact-root> --code-root <code-root> \
  ".tasks/<feature-name>/tasks.json"
```

If immediate dispatch is approved, `create-proof` may run with explicit roots/package; `--force` requires exact
overwrite authority and preservation. Re-open SPEC/registry/packages from artifact root; confirm manifests,
assignments, prerequisites, paths/seams/routing, and budget state agree. Helper success is mechanical, never
semantic evidence sufficiency. Return roots/ref, old/new state, packages/dependencies, Slice inventory, envelope/
baseline, preflight/prerequisites, profile/routing, evidence topology, budget usage, deferrals, assumptions, and
validation result.
