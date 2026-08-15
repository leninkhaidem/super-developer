# Execution Contract
## Boundary
This reference owns the user-facing implement approval template and its approval boundaries.
## Contract
- Derive the contract only from approved plan artifacts, package Markdown, safe assigned Slice content,
  resolved testing authority when execution feasibility is triggered, current git state, and explicit user
  instructions.
- Approval covers only listed actions. For auto-resolve list in-scope code/test writes, bounded empirical-spike
  dispatch, disposable local harness/temp/probe-worktree writes and cleanup, evidence, changed follow-ups,
  same-requirement plan repair/focused re-review, ordinary repairs/review/audit, and pushes.
- Auto-resolve never re-asks while scope/side effects stay within those listings; it stops when they exceed the
  contract or reach a protected boundary. Step-by-step still asks at each contracted major gate.
- Name fixed worktrees and one bounded dynamic envelope: exact feature namespace/path/ref patterns, probe base refs
  plus caller/contract-supplied expected base SHAs, package bases/prerequisites, bindings, manifests, and prohibitions.
- A probe receipt binds `BASE_REF`, `EXPECTED_BASE_SHA`, full direct `REF`, clean initial HEAD/index/worktree,
  non-writing `git hash-object --no-filters` `INDEX_DIGEST`, exact NUL owned tracked/untracked/ignored/symlink/process/
  data manifests, and `remote_action=none`; it forbids index writes, commit/merge/push/force/reset/stash/clean.
- Continuation may create—but never remove—focused-reviewed package IDs. Each package artifact/contract supplies
  `BASE_KIND`, exact `BASE_REF`, focused-reviewed `REVIEWED_BASE_SHA`, and prerequisite ref/SHAs. Independent uses
  approved original base; dependent integration `HEAD` equals that SHA with every prerequisite SHA its ancestor.
- Autonomous envelope cleanup is probe-only after exact owned-delta restoration and clean proofs. It checks local
  upstream/tracking absence, performs no network/credential check or remote action, and leaves remote refs untouched.
- Normal feature execution requires the exact non-force `feature/<feature>` checkpoint after every accepted
  package merge with remote-SHA verification; auto-resolve covers all repetitions. Planned-hotfix push is separate.
- Sidecar pushes require their own exact listed command/ref; source/target publication never implies them or vice
  versa. One approval may list both. When excluded, valid local artifacts remain usable but unpublished.
- Target merge/push, force push, tag, release, remote deletion, local ref deletion outside owned probe/final package
  cleanup, destructive command, service install/start, credentialed action, or external effect needs approval.
- Dependency installs/additions are covered only when exact commands and manifest/lockfile paths are
  derived from approved artifacts or explicit user instruction and listed in this contract; otherwise
  they require separate approval.
- Accept `resolved-static`, `supported`, or `rejected` only after validating report identity, provenance, method,
  authority, bounds, limitations, and cleanup. Auto-resolve corrects in-contract `blocked`/`inconclusive`; protected/
  out-of-contract needs return at a Stop condition. Each logical empirical question has at most three total attempts:
  attempt 1 is initial; attempts 2–3 are each a fresh invocation with stable ID and named corrected packet or changed method/signal.
  Exhaustion of an empirical question stops, with no escalation; unchanged work is forbidden and no other counter
  exists for it. Code repair clusters use the separate circuit in pipeline step 13.
- Step-by-step mode asks before each major gate, package wave, repair loop, source push, and final handoff.
## Do
1. Validate `.tasks/<feature>/`, package/report/Slice paths, current git refs, and—when execution
   feasibility is triggered—the testing-authority provenance and command/write bounds.
2. Name delivery context, roots/refs, fixed worktrees, probe receipts, continuation `BASE_KIND`/exact `BASE_REF`/
   `REVIEWED_BASE_SHA`/prerequisites, optional sidecar command, and context-applicable source command: repeated feature checkpoints only for `feature`,
   or separately contracted `hotfix/<name>` publication.
3. For each package, summarize assigned Slice obligations, primary paths, dependencies, approved dependency
   changes, verification expectations/depth, known blockers, and any execution-feasibility profile: authority,
   preconditions/cleanup, cost, bounds, readiness probe, and broad placement or broad-only justification.
4. List covered production/test/plan/temp writes, empirical and verification actions, logical question/attempt
   ledger, cleanup, changed follow-ups, same-requirement focused re-review, pushes, Semgrep flow, and exclusions.
5. List command-safety boundaries and every action not authorized by this contract.
6. Offer exactly three choices: `approve auto-resolve`, `step-by-step`, or `abort`.
7. Stop unless the user approves one choice or prior explicit instruction already selected one.
## Template
```text
Execution Contract for <feature>
Delivery context: feature | planned-hotfix
Git refs:
  base ref: <base-ref>
  integration ref: feature/<feature> | hotfix/<name> (planned-hotfix; no implicit feature ref)
  artifact ref: artifacts/<feature>
  target ref: <target-ref>
Roots:
  artifact root: .worktrees/<feature>/artifacts (owns .planning/.tasks, reports, reviews)
  code root: <root or integration/package worktree used for source validation>
Testing authority:
  source: <accepted/current workflow + companions | routine-safe fallback | task-local authorization | not triggered>
  runtime policy: <command budgets, progress/completion, termination, cleanup, shared-resource constraints>
Covered actions:
  writes: <implementation/test plus disposable local harness/temp/worktree and same-requirement plan-artifact writes>
  execution/evidence: <bounded empirical-spike, test/review/audit commands; evidence destinations and cleanup>
  follow-up/replan: <stable logical-question ID; attempts 1–3; corrected packet or changed method/signal;
                     plan repair with empirical report set or none + focused re-review; no unchanged attempt>
  pushes: <required normal-feature checkpoints and each optional planned-hotfix/sidecar action below>
Remote actions:
  source checkpoints: <normal feature: repeated non-force post-package push + remote-SHA verification | planned hotfix: exact push or excluded>
  sidecar checkpoints: <exact push of artifacts/<feature> from its worktree at eligible gates, or excluded/local-only>
  target merge/push: not authorized; requires separate explicit approval for <target-ref>
  force/remote-delete/tag/release actions: not authorized; probe cleanup records remote_action=none
Worktree authority envelope:
  namespace: .worktrees/<feature>/...; refs probe/<feature>/... and wp/<feature>/... only
  probe: exact allowed BASE_REF + supplied EXPECTED_BASE_SHA; require equality before/after creation; receipt stores full REF
  probe state: clean HEAD/index/worktree + INDEX_DIGEST and exact NUL tracked/deleted/untracked/ignored/symlink/process/data manifests
  probe limits: no stage/index write/commit/merge/push/reset/stash/force/git-clean/broad delete
  probe cleanup: restore/remove exact owned only; prove expected base/full ref/index/status; normal remove/direct full-ref CAS
  local-only: no upstream/tracking config; remote_action=none; no network lookup or remote ref mutation
  continuation package: create only; reviewed ID + BASE_KIND + exact BASE_REF + REVIEWED_BASE_SHA + prerequisite ref/SHAs
  package creation: base ref equals reviewed SHA before/after add; dependent clean integration HEAD equals it and contains prerequisites
  retention: active/retired package worktrees/refs remain through final whole-feature cleanup
Fixed worktrees:
  artifact sidecar: .worktrees/<feature>/artifacts on artifacts/<feature>
  integration code: <non-root path> on feature/<feature> | hotfix/<name>
  planned packages: <exact WP-ID path/ref list>
Semgrep:
  state/source: <disabled | enabled privacy mode + local cache/index/profile>
  helper/evidence: <none | wrapper scan, bounded summarize/list/show, package/integration paths + digests>
  limits: no raw scan/JSON; advisory by default; no hidden cloud/network/setup/credentials/service side effects
Packages:
- <WP-ID>: <title>
  package: <artifact-root>/.tasks/<feature>/packages/<WP-ID>.md
  report: <artifact-root>/.tasks/<feature>/reports/<WP-ID>.package-verification.md
  primary paths: <paths or none>
  assigned Slices/H3 IDs: <slice paths + H3 IDs or none>
  context-only Slices/H3 IDs: <slice paths + H3 IDs or none>
  dependencies: <package IDs or none>; continuation creation: <BASE_KIND; exact BASE_REF; REVIEWED_BASE_SHA; prerequisite ref/SHAs | n/a>
  verification expectations: <safe scoped commands/inspections or none>
  dependency installs/additions: <none or exact approved manifest/lockfile paths and commands>
  package verification: <standard | enhanced + lenses/reasons>
  execution readiness: <omit when clearly non-triggered | triggered sources/bounds/cleanup/probe/broad placement>
  known blockers/deferrals: <none or approved details>
Pipeline:
1. create fixed worktrees; create probes/continuation packages only under their exact runtime-validated envelope
2. declare each package `report_path`; create no undeclared artifact files
3. run attempt-ledger probes; NUL-classify/restore owned dirty state before normal local cleanup, never force/network
4. dispatch package agents with artifact-root package/Slice/report paths and package code worktrees
5. require package-agent SELF_REVIEW; after return, re-run every executable frozen AC item into the result file
6. treat a failed re-run as automatic FAIL with no LLM; then run root-aware `validate-package-complete`
7. merge each accepted source-only package branch into the integration worktree after its gates pass
8. refresh affected evidence/seams; only for delivery context `feature`, checkpoint and require remote feature SHA = integration `HEAD` before downstream progression; retain all safety nets on failure/divergence
9. planned-hotfix has no feature ref/SHA or package-boundary source push; run its separately listed `hotfix/<name>` publication only at its source-push gate; publish sidecar only when listed
10. route any plan-owned defect (reports or none) through continuation/focused review; repair code separately
11. run root-aware final validation; freeze integrated-code/artifact/runtime-evidence inputs
12. invoke `review-code` and `audit` as sibling checks; their outputs are not freeze inputs
13. preserve logical question/finding identity and the existing three-total-attempt circuit; never retry unchanged;
    empirical questions and plan-owned clusters stop on that exhaustion, while a code repair cluster is instead
    re-classified once as a possible plan defect and routed through step 10 when that preserves approved semantics,
    scope, user-visible behavior, risk, and manual exceptions — otherwise that routing is new semantic authority and
    stops; at most one such escalation per cluster identity, relabeling or reclustering earns no second one, and the
    same cluster's second attempt-3 exhaustion stops
14. stabilize repairs; deduplicate commands only for equivalent state/cwd/environment/isolation/evidence mappings; establish a new freeze and require focused review-code closure plus a fresh cold complete same-freeze audit PASS
15. retain all package safety nets to final cleanup; then run only independently listed sidecar/source pushes
Stop conditions:
- unsafe, contradictory, out-of-contract, uncertain, or unowned artifact/code/package/report/Slice/worktree state
- genuine requirement/scope/user-visible behavior/Slice semantic/manual-exception change or risk acceptance
- missing credentials/external facts, or command/write authority absent from this Execution Contract
- destructive/external/service/dependency action not explicitly listed and approved
- sidecar action would escape `origin artifacts/<feature>` or merge artifact-only state into deliverable code
- feature/hotfix checkpoint diverges, non-fast-forwards, or fails protected remote/credential checks
- target delivery, force/remote-delete/tag/release, or local ref deletion outside probe/final-package cleanup
- attempt-3 exhaustion of an empirical question or plan-owned cluster, a code repair cluster's second attempt-3
  exhaustion after its one allowed re-classification, unbounded questions, or other true bounded non-convergence
Choices:
  approve auto-resolve — run covered code/probes/tests/replan/re-review/repairs/review/audit and, for `feature`,
                         listed checkpoints while scope, authority, and material-progress rules hold, until stop
  step-by-step        — ask before each package wave, repair loop, push, and final handoff
  abort               — stop before worktree creation or dispatch
```
## Stop if
- Any template field cannot be derived from safe approved artifacts, resolved testing authority, or explicit user
  instruction.
- The user wants target merge/push, force/remote-delete/tag/release, destructive action, or early package cleanup,
  service install/start, credentialed action, or external side effect, or a dependency install not derived from
  approved artifacts/explicit instruction and listed exactly in the contract.
- Package verification depth, Slice obligations, package dependencies, delivery context, or source-push boundary is ambiguous enough to affect execution.
## Output
Return the filled contract, selected choice, testing-authority provenance, feasibility profiles/readiness probes,
covered/excluded actions, progress/circuit boundaries, blockers, and fields needing user clarification.
