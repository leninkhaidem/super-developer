# Execution Contract

## Boundary

This reference owns the user-facing implement approval template and its approval boundaries.

## Contract

- Derive the contract only from approved plan artifacts, package Markdown, safe assigned Slice content, current git state, and explicit user instructions.
- Approval covers only the exact actions listed in the contract.
- Feature-branch push is covered by default when listed as `git push -u origin feature/<feature>`
  for review/testing; the user may explicitly exclude it.
- Target branch merge, target push, force push, tag, release, branch delete, destructive command,
  dependency/service install, credentialed action, or external side effect always needs separate explicit approval.
- Auto-resolve mode continues through approved implementation gates and the covered feature push until
  a stop condition, review-code/audit handoff boundary, or completion.
- Step-by-step mode asks before each major gate, package wave, repair loop, feature push, and final handoff.

## Do

1. Validate `.tasks/<feature>/`, package Markdown, declared proof/report paths, assigned Slice paths/H3 IDs,
   and current git refs before presenting the contract.
2. Name the exact base ref, feature ref, target ref, package refs/worktrees, proof paths, report paths,
   and default-covered feature-push command.
3. For each package, summarize assigned Slice obligations, primary paths, dependencies, verification expectations,
   package verification depth, Semgrep evidence expectations when enabled/contracted, and known blockers.
4. Disclose resolved Semgrep state, privacy/local rule source, helper checks, evidence paths/digests, bounded consumption order, advisory finding policy, and unapproved side effects.
5. List command-safety boundaries and all actions that are not authorized by this contract.
5. Offer exactly three choices: `approve auto-resolve`, `step-by-step`, or `abort`.
6. Stop unless the user approves one choice or prior explicit instruction already selected one.

## Template

```text
Execution Contract for <feature>

Git refs:
  base ref: <base-ref>
  feature ref: feature/<feature>
  target ref: <target-ref>

Remote actions:
  feature branch push: git push -u origin feature/<feature> for review/testing (covered by this contract by default; non-force only)
  target merge/push: not authorized; requires separate explicit approval for <target-ref>
  force/delete/tag/release actions: not authorized

Worktrees:
  integration: .worktrees/<feature>/merge on feature/<feature>
  packages:
    - <WP-ID>: .worktrees/<feature>/wp-<WP-ID> on wp/<feature>/<WP-ID>

Semgrep:
  state: <disabled | enabled with privacy-mode from .superdeveloper/preferences.yml>
  local rule source/cache: <plugin community cache/index/profile or none>
  helper checks: <none when disabled | retrieve/scan/summarize/list-findings/show-finding expectations>
  package evidence: .tasks/<feature>/semgrep/<WP-ID>.semgrep.json + .semgrep-summary.json with digests when enabled
  integrated evidence: <not planned | conditional one-shot for named cross-package/shared-surface risk>
  consumption/materiality: summarize -> filtered list-findings -> selected show-finding; raw JSON dumps forbidden; Semgrep severity advisory by default
  side effects not authorized here: hidden registry/URL/cloud/telemetry scans, dependency installs, credentials, or network clone/pull unless separately listed and approved

Packages:
- <WP-ID>: <title>
  package: .tasks/<feature>/packages/<WP-ID>.md
  proof: .tasks/<feature>/proofs/<WP-ID>.proof.md
  report: .tasks/<feature>/reports/<WP-ID>.package-verification.md
  primary paths: <paths or none>
  assigned Slices/H3 IDs: <slice paths + H3 IDs or none>
  context-only Slices/H3 IDs: <slice paths + H3 IDs or none>
  dependencies: <package IDs or none>
  verification expectations: <safe scoped commands/inspections or none>
  package verification: <standard | enhanced + lenses/reasons>
  known blockers/deferrals: <none or approved details>

Pipeline:
1. create integration and package worktrees through the `worktree` skill
2. dispatch package agents with package Markdown, assigned Slice paths, proof path, and verification expectations
3. require package-agent SELF_REVIEW and proof Markdown evidence
4. run `sliceproof.py validate-proof` and package verification; require fresh PASS report
5. merge accepted package branches into the integration worktree after gates pass
6. refresh proof/report evidence after repairs, merge-impact changes, or verifier findings
7. run final validation and safe integrated checks
8. push the feature branch using the exact feature push above unless the user explicitly excluded it
9. hand off to `review-code` and `audit` through fresh Skill-tool/sub-agent invocations when readiness rules allow

Stop conditions:
- unsafe, missing, stale, contradictory, or out-of-scope plan/package/proof/report/Slice/worktree path
- unassigned material Slice obligation, unresolved plan defect, unapproved deferral, or weak proof evidence
- failed verification, stale package report, or ignored proof/report artifact committed to git
- product/design change, scope expansion, existing-feature contract change, or risk acceptance needed
- unsafe/destructive/external/credentialed command or dependency/service install needed
- feature push remote/ref differs from this contract, remote diverges/non-fast-forwards unexpectedly, or credentials fail
- any target merge/push, force/delete/tag/release action, or branch deletion is requested
- final review-code readiness or audit prerequisites are not fresh and closed

Choices:
  approve auto-resolve — run approved package/verification/repair gates, including the default feature push,
                         until completion or stop condition
  step-by-step        — ask before each package wave, repair loop, push, and final handoff
  abort               — stop before worktree creation or dispatch
```

## Stop if

- Any template field cannot be derived from safe approved artifacts or explicit user instruction.
- The user wants the contract to authorize target merge/push, force/delete/tag/release action, destructive command,
  dependency/service install, credentialed action, or external side effect.
- Package verification depth, Slice obligations, package dependencies, or default feature-push boundary are ambiguous enough to affect execution.

## Output

Return the filled contract, selected choice, explicitly covered actions, explicitly excluded actions, blockers, and any fields needing user clarification.
