# Implementation Authorization Content
## Boundary
This path owns execution-readiness and covered-action content for the sole Implementation Authorization.
`review-plan` presents it after cold review; `implement` consumes the checkpointed receipt and never presents
another decision surface.

## Source and Decision Rule
Derive fields from reviewed artifacts, resolved testing authority, readiness, Git state, budgets, and instructions.
Unknown fields or blocked required prerequisites prevent the decision.

Only initial clean `review-plan` offers **Approve and auto-resolve**, **Request changes**, and **Abort**. Approval
begins delivery after the exact checkpoint and covers listed routine actions without later prompts. Nested-amendment
review returns a cold receipt to the existing Delivery Owner; it never offers choices, creates an ID, or re-enters
gate readiness. No per-stage or downstream implementation choice is added.
## Canonical Decision Surface

```text
Implementation Authorization for <feature>

Human Authorization Envelope:
  outcomes and observable behavior: <exact accepted summary/requirement anchors>
  product/interface invariants: <exact anchors>
  scope and exclusions: <exact included/excluded behavior>
  accepted material risks and protected effects: <exact list or none>
  spending/command/time bounds: <finite user-owned bounds>

Reviewed Technical Plan Baseline:
  baseline identity: <digest/version>
  architecture invariants and package/consumed-contract order: <exact anchors/topology>
  assurance profile/routing and receipt topology: <profile, package modes, lenses>
  verification/evidence/cleanup strategy: <reviewed minimum sufficient checks>
  allowed amendment policy: <envelope-preserving technical corrections + affected cold re-review only>

Exact state and Authorization Digest inputs:
  distinct artifact/code roots; artifact ref/candidate commit+tree; base commit: <exact verified objects>
  immutable inputs snapshot: <artifact_tree, base_commit, clean_status, dependencies, routing, actions,
    budget_authority, amendment_policy; last six are canonical digests>
  initial digest: <canonical JSON digest of exactly inputs>; initial effective digest: <equal value>
  Lifecycle State path/generation/digest/last-verified predecessor: <derived path + exact values>
  packages, worktrees, proof/report paths and expected deterministic mutations: <exact safe values>
  one configured push endpoint and exact refs per relevant root: <authorized exact values>

Execution readiness:
  mechanical plan/sidecar validation: <fresh result>
  tools and non-protected environments: <proven-ready results>
  safe baseline/readiness probes: <bounded command/result>
  package dependencies/integration order: <coherent result>
  prerequisites:
    - <name>: <proven-ready | protected-activation-required>
      provenance/snapshot: <source-bound identity>
      activation probe/remedy/failure consequence: <exact covered values or n/a>
  blocked/optional capability: <none, or optional disclosed and excluded; required blocked prevents this surface>

Testing authority:
  source: <accepted/current workflow + companions | routine-safe fallback | task-local authorization | not triggered>
  triggered profile: <omit when clearly non-triggered>
  command identity/preconditions/cleanup/progress/termination: <exact values>
  broad placement or broad-only justification: <reviewed value>

Covered writes and actions:
  production/docs: <exact paths/categories>
  tests/oracles/fixtures/harness/config: <exact paths/categories>
  artifacts/evidence/lifecycle receipts: <exact paths/categories>
  commands/tests/runtime observations: <exact commands/categories and safety bounds>
  package waves/eligible repairs: <scope; one logical owner; batched root causes>
  reruns/evidence refresh/cleanup: <affected-only rules, widening triggers, exact cleanup>
  checkpoints: <code-before-sidecar refs, Lifecycle State path, expected parents, CAS boundaries>
  listed pushes: <one exact configured endpoint per root + exact non-force sidecar/code/feature argv or none>

Finite autonomous budgets:
  delegated calls by role: <maxima>
  repair waves and canonical-cluster closure: <finite maxima; initial rejection + one repair + closure>
  command/cost units: <finite maxima>
  started_at/deadline_at: <fixed values>
  no-reset rule: <agent/host/model/commit/timeout cannot reset issued usage or deadline>

Auto-resolve boundary:
  Includes listed implementation, tests, stabilization, repairs, reruns, evidence refresh, cleanup,
  cold technical amendment/re-review, checkpoints, and pushes.
  Stops for envelope/scope/risk/budget or protected action/endpoint change, unlisted action, blocked activation,
  exact-state/ownership loss, no credible envelope-preserving design, open circuit, or exhausted budget.

Excluded/protected actions:
  initial Sidecar Portability Authorization: separate planning-only authority; not inherited here
  target/main merge or push: not authorized
  force/delete/tag/release/deploy/branch cleanup: not authorized
  destructive, credentialed, shared-service, or external effect not exactly listed: not authorized
  new dependency/service/permission or dependency manifest/lockfile change: not authorized
  existing-system contract change not explicitly approved by the Human Authorization Envelope: not authorized

Choices:
  Approve and auto-resolve
  Request changes
  Abort
```

## Covered-Action Rules

- New dependencies/services and dependency manifest/lockfile changes are outside auto-resolve and require their
  own focused authority; reviewed plan text alone never authorizes them.
- Delivery checkpoint authority is separate from Sidecar Portability Authorization. For each relevant root,
  require one configured push endpoint, bind it in covered actions, capture it once, reject zero/multiple/change,
  and use that exact argv for `ls-remote`, `push`, `fetch`, and post-check. A distinct fetch URL proves nothing.
  Publish immutable checkpoint refs before expected-parent-bound sidecar CAS; all operations are non-force.
- Feature push is covered only when its exact non-force ref/command appears. Target merge/push and release remain
  separate even when feature delivery is complete.
- Semgrep stays advisory and local under reviewed policy. When enabled, list evidence paths and use only
  `python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/semgrep_rules.py" scan ...`; no hidden cloud/telemetry, network,
  install, credential, or service action is implied.
- Covered local implementation/test failures, eligible repairs, bounded reruns, evidence refresh, and checkpoint
  retries proceed without user input only while they make material progress and remain inside all listed bounds.

## Pipeline:

1. validate Lifecycle State/predecessor plus canonical immutable inputs, objects/tree, authorization checkpoint,
   cheap freshness guard, then covered protected activation
2. create/resume authorized worktrees and dispatch ready package owners
3. stabilize production behavior and actual-path causal tests before proof conclusions
4. run focused and affected broad regression before proof/report refresh
5. perform package verification, completion validation, merge, and code-before-sidecar checkpoints
6. finish integrated checks/evidence and run root-aware final validation; freeze exact inputs
7. invoke `review-code` and `audit` only as return-only independent checks against that freeze
8. for amendment invoke nested `review-plan`, validate its cold receipt/effective digest, checkpoint; then batch findings, delegate repairs
   only for eligible clusters, rerun affected checks, and establish a new freeze
9. after clean review-code/audit acceptance, run listed final checkpoint and push the feature branch if covered

## Stop conditions:

Stop before the decision when required inputs/readiness are missing or blocked. After authorization, stop only at
the listed Human Authorization Envelope, protected-action, freshness/ownership, activation, circuit, or budget
boundaries; routine in-scope failure is returned to the Delivery Owner for bounded auto-resolution.

## Lifecycle Helper Boundary
Run `sliceproof.py validate-lifecycle-state` with distinct roots, derived `--feature`, and full `--previous-commit`
after generation 1. It validates generation-1 null topology, local objects/tree/digests, immutable authorization,
artifact ancestry on exact sidecar lineage, monotonic state, and predecessor. Exact-endpoint remote reachability/CAS
stays in the worktree contract; the helper never reserves, transitions, dispatches, pushes, or proves completion.

## Activation Guard

Immediately before product writes/fanout, compare exact authorization ID/digest, artifact commit/tree, base
commit/status digest, dependency/prerequisite snapshot, profile/routing, covered actions, and expected deterministic
mutations. This is a cheap activation guard, not a new decision surface. Unlisted drift returns to affected cold
technical review; only Human Authorization Envelope change returns to the user.

## Output

Before authorization, return filled content or blockers. Afterward, `implement` returns authorization/effective
digest, readiness/freshness/activation, budgets, covered/excluded actions, and any precise escalation—never a new
delivery decision.
