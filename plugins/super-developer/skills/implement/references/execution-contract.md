# Execution Contract
## Boundary
This reference owns the user-facing implement approval template and its approval boundaries.

## Contract
- Derive the contract only from approved plan artifacts, package Markdown, safe assigned Slice content,
  resolved testing authority when execution feasibility is triggered, current git state, and explicit user
  instructions.
- Approval covers only listed actions. List upfront implementation and in-scope test writing,
  focused/runtime execution, evidence collection, bounded reruns, and sidecar/feature pushes as applicable.
- Consolidated no-reask applies only to auto-resolve: do not re-ask while scope and side effects remain within
  those listings; re-ask when either exceeds the contract or a separately protected boundary applies.
  Step-by-step still asks at every contracted major gate as described below.
- Name artifact/code roots, sidecar ref/worktree, and package/integration code worktrees.
- Feature-branch push is covered by default when listed as `git push -u origin feature/<feature>`
  for review/testing; the user may explicitly exclude it.
- Sidecar checkpoint pushes are covered only when listed as `git push -u origin artifacts/<feature>`
  from the artifact worktree at package-delivery or final review/audit gates.
- Target branch merge, target push, force push, tag, release, branch delete, destructive command,
  service install/start, credentialed action, or external side effect always needs separate explicit approval.
- Dependency installs/additions are covered only when exact commands and manifest/lockfile paths are
  derived from approved artifacts or explicit user instruction and listed in this contract; otherwise
  they require separate approval.
- Auto-resolve mode continues through approved implementation gates and the covered feature push only while
  readiness holds and each repair attempt makes material progress. An open execution/repair circuit stops it.
- Step-by-step mode asks before each major gate, package wave, repair loop, feature push, and final handoff.

## Do
1. Validate `.tasks/<feature>/`, package/proof/report/Slice paths, current git refs, and—when execution
   feasibility is triggered—the testing-authority provenance and command/write bounds.
2. Name the exact artifact root, code root, artifact ref/worktree, base ref, feature ref, target ref,
   package refs/worktrees, proof/report paths under the artifact root, sidecar checkpoint command,
   and default-covered feature-push command.
3. For each package, summarize assigned Slice obligations, primary paths, dependencies, approved dependency
   changes, verification expectations/depth, known blockers, and any execution-feasibility profile: authority,
   preconditions/cleanup, cost, bounds, readiness probe, and broad placement or broad-only justification.
4. List exact covered write surfaces, executable verification/evidence actions, bounded rerun rules, and pushes.
   Disclose Semgrep state, local source, helper/evidence flow, advisory policy, and unapproved side effects.
5. List command-safety boundaries and every action not authorized by this contract.
6. Offer exactly three choices: `approve auto-resolve`, `step-by-step`, or `abort`.
7. Stop unless the user approves one choice or prior explicit instruction already selected one.

## Template
```text
Execution Contract for <feature>

Git refs:
  base ref: <base-ref>
  feature ref: feature/<feature>
  artifact ref: artifacts/<feature>
  target ref: <target-ref>

Roots:
  artifact root: .worktrees/<feature>/artifacts (owns .planning/.tasks, proofs, reports, reviews)
  code root: <root or integration/package worktree used for source validation>

Testing authority:
  source: <accepted/current workflow + companions | routine-safe fallback | task-local authorization | not triggered>
  runtime policy: <command budgets, progress/completion, termination, cleanup, shared-resource constraints>

Covered actions:
  writes: <implementation/docs plus exact in-scope test/oracle/harness paths or categories>
  execution/evidence: <focused, runtime, and integrated commands; evidence destinations/redaction>
  bounded reruns: <same-scope rerun conditions/budgets; no unchanged retries or timeout inflation>
  pushes: <sidecar checkpoint and feature push commands listed below, or excluded>

Remote actions:
  feature branch push: git push -u origin feature/<feature> for review/testing (covered by this contract by default; non-force only)
  sidecar checkpoints: git push -u origin artifacts/<feature> from .worktrees/<feature>/artifacts at package/final gates only
  target merge/push: not authorized; requires separate explicit approval for <target-ref>
  force/delete/tag/release actions: not authorized

Worktrees:
  artifact sidecar: .worktrees/<feature>/artifacts on artifacts/<feature>
  integration code: .worktrees/<feature>/merge on feature/<feature>
  packages:
    - <WP-ID>: .worktrees/<feature>/wp-<WP-ID> on wp/<feature>/<WP-ID>

Semgrep:
  state: <disabled | enabled with privacy-mode from .superdeveloper/preferences.yml>
  local rule source/cache: <plugin community cache/index/profile or none>
  helper checks: <none when disabled | retrieve plus python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/semgrep_rules.py" scan ... then summarize/list-findings/show-finding>
  package evidence: .tasks/<feature>/semgrep/<WP-ID>.semgrep.json + .semgrep-summary.json with digests when enabled
  integrated evidence: <not planned | conditional one-shot for named cross-package/shared-surface risk>
  consumption/materiality: summarize -> filtered list-findings -> selected show-finding (target + expected summary digest for excerpts); raw JSON dumps forbidden; Semgrep severity advisory by default
  side effects not authorized here: hidden registry/URL/cloud/telemetry scans, unlisted dependency installs, credentials, service starts/installs, or network clone/pull unless separately listed and approved

Packages:
- <WP-ID>: <title>
  package: <artifact-root>/.tasks/<feature>/packages/<WP-ID>.md
  proof: <artifact-root>/.tasks/<feature>/proofs/<WP-ID>.proof.md
  report: <artifact-root>/.tasks/<feature>/reports/<WP-ID>.package-verification.md
  primary paths: <paths or none>
  assigned Slices/H3 IDs: <slice paths + H3 IDs or none>
  context-only Slices/H3 IDs: <slice paths + H3 IDs or none>
  dependencies: <package IDs or none>
  verification expectations: <safe scoped commands/inspections or none>
  dependency installs/additions: <none or exact approved manifest/lockfile paths and commands>
  package verification: <standard | enhanced + lenses/reasons>
  execution readiness: <omit when clearly non-triggered | triggered sources/bounds/cleanup/probe/broad placement>
  known blockers/deferrals: <none or approved details>

Pipeline:
1. create/resume artifact sidecar plus integration and package code worktrees through the `worktree` skill
2. create proof placeholders in the artifact root with explicit `--artifact-root`/`--code-root` helper flags
3. run conditional contract/fixture/harness preflight and the smallest bounded readiness probe before costly fanout
4. dispatch package agents with artifact-root package/Slice/proof/report paths and package code worktrees
5. require package-agent SELF_REVIEW and artifact-root proof Markdown evidence
6. run root-aware `validate-proof`, package verification with a fresh PASS report, then `validate-package-complete`
7. merge accepted source-only package branches into the integration worktree after gates pass
8. refresh and rerun affected proof/report/verification state after repairs, merge changes, or findings
9. checkpoint sidecar artifacts after package delivery, pushing only `origin artifacts/<feature>`
10. finish repairs; run focused/integrated checks and finalize runtime evidence/cleanup
11. run root-aware final validation; freeze integrated-code/artifact/runtime-evidence inputs
12. invoke `review-code` and `audit` as sibling checks; their outputs are not freeze inputs
13. batch blocking findings, delegate bounded repairs; re-run only the affected checks, then establish a new freeze
14. after clean review-code/audit acceptance, checkpoint artifacts and push the feature branch as covered

Stop conditions:
- unsafe, missing, stale, contradictory, or out-of-scope artifact root, code root, package/proof/report/Slice/worktree path
- unassigned material Slice obligation, unresolved plan defect, unapproved deferral, or weak proof evidence
- failed readiness/verification, missing runtime bounds or cleanup ownership, stale package report,
  artifact-root ambiguity, uncertain termination/cleanup, or ignored proof/report artifact committed to code git
- sidecar checkpoint would push anything except `origin artifacts/<feature>` or merge sidecar artifacts into deliverable code
- product/design change, scope expansion, existing-system contract change not explicitly approved in accepted
  artifacts/this Execution Contract, or risk acceptance needed
- unsafe/destructive/external/credentialed command, service install/start, or unlisted dependency install needed
- feature push remote/ref differs from this contract, remote diverges/non-fast-forwards unexpectedly, or credentials fail
- any target merge/push, force/delete/tag/release action, or branch deletion is requested
- final review-code readiness or audit prerequisites are not fresh and closed

Choices:
  approve auto-resolve — run approved package/verification/repair gates, including the default feature push,
                         while readiness and material-progress circuit rules hold, until completion or stop
  step-by-step        — ask before each package wave, repair loop, push, and final handoff
  abort               — stop before worktree creation or dispatch
```

## Stop if
- Any template field cannot be derived from safe approved artifacts, resolved testing authority, or explicit user
  instruction.
- The user wants the contract to authorize target merge/push, force/delete/tag/release action, destructive command,
  service install/start, credentialed action, or external side effect, or a dependency install not derived from
  approved artifacts/explicit instruction and listed exactly in the contract.
- Package verification depth, Slice obligations, package dependencies, or default feature-push boundary are ambiguous enough to affect execution.

## Output
Return the filled contract, selected choice, testing-authority provenance, feasibility profiles/readiness probes,
covered/excluded actions, progress/circuit boundaries, blockers, and fields needing user clarification.
