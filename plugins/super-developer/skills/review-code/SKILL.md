---
name: review-code
description: >
  Reviews code changes with bounded multi-agent analysis. Use for PRs, local diffs, or planned-feature final
  integrated review. Do not use for final planned-feature audit or PR/local repairs unless the selected mode
  explicitly permits fixes.
---

# Review Code

Run bounded review; route report/actions by mode.

## Always

- Select exactly one mode: PR, local, or planned-feature pipeline.
- Keep PR/local review separate from Slice/proof/report/audit obligations unless pipeline artifacts are in scope.
- Pipeline review first establishes accepted obligations and frozen production paths, then causal test/runtime evidence;
  deliverable matrices are context only for freshness, seams, contradictions, and proof/report invalidation, not a third deliverable-completeness gate.
- In PR/local mode, `CLEAN` means no confirmed serious findings for the reviewed state; it is not proof acceptance
  or merge readiness. Pipeline mode returns freeze-scoped `C` or `R`, never audit/completion readiness.
- PR/local mode may use its bounded review engine. In pipeline mode the Delivery Owner directly dispatches one cold,
  read-only, return-only role under `../../references/orchestration-convergence.md`; it never owns repair or lifecycle continuation
  and never mutates, dispatches, freezes, advances, checkpoints, or notifies.
- Revalidate reviewed-state metadata before posting, fixing, committing, evidence refresh, or pipeline return.

## Mode Routing

1. PR mode: PR URL, `owner/repo#N`, or `#N` in repo context → load `references/pr-workflow.md`. PR mode is review-only for code changes.
2. Local mode: no pipeline context and no PR identifier → load `references/local-workflow.md`.
3. Pipeline mode: feature context plus artifact root, SPEC, registry, package/proof/report artifacts, and
   integrated code worktree state → load `references/pipeline-report.md`. Load and pass
   `../../references/package-verification-report.md`. Pass `../../references/package-lifecycle.md` as a labeled
   path, but load it only when proof/report freshness or non-bypass routing is disputed.
4. Before reviewer dispatch, capture immutable refs/SHAs, worktree or PR identity, diff checksum or saved
   diff, file list/status, artifact root, code root, and mode artifact context.

## Review Engine and Big Diffs

- Build a compact manifest: core/runtime, public contracts, generated/schema/config, proof-critical tests, fixtures/snapshots, docs/tooling.
- Use semantic batching when the diff is about 2,000+ lines, many files, mixed domains, generated churn, or too broad for one coherent review.
- Split by package, module, seam, or risk surface; never by arbitrary line chunks.
- Keep source and tests that prove the same behavior together when practical.
- For low-risk generated/docs/snapshots/repetitive fixtures, verify provenance or sample with the owning surface.
- Per batch: preserve mode metadata, run bounded topology, assign stable dedupe keys, and merge all verdict types into one cross-batch set.
- After batches, run one global integration pass for duplicates, conflicting recommendations, cross-batch serious risks, and seam issues.
- Reopen reviewer fanout only when batch boundaries cannot preserve confidence.
- In PR/local mode, run one default Code Reviewer sub-agent per diff/batch; add at most one triggered specialist and
  Skeptic only for serious/risky-clean/conflicting coverage (caps: normal 2, risky 3).
- Pipeline mode does not use this fanout: low dispatches one Combined Low Verifier; standard/high dispatches one Code
  Reviewer. High final specialists are separate Delivery-Owner calls only after `R` PASS and never part of review-code.
- Resolve reviewer model only when local policy matters: `../../references/model-preferences.md`.
  Pass `../../references/clean-code-rules.md`; do not load it in the orchestrator.
- Pipeline code-risk review inspects tests only for concrete production/evidence correctness, regression,
  flakiness, unsafe/shared harness changes, or materially harmful required runtime. Consume package Selected Causal
  Evidence and trust fresh package verification unless a seam, contradiction, stale binding, or one of those risks
  requires focused inspection; never census or rereview the suite.
- In pipeline mode, add Slice-first context from the artifact root: package IDs, proof/report paths,
  matrix source IDs/evidence anchors/source bindings, Slice/H3 IDs, verification results/advisories,
  Semgrep evidence when enabled or contracted, risks, deferred concerns, ownership, and the separate integrated code state. Route `context_only_slice_drift` through affected-surface classification as non-blocking by default unless reviewer judgment escalates material risk.
- Pipeline final review is integration-first: trust fresh package-local verification. Reopen local code only for
  a seam, integration-only change, contradiction, stale report, invalidated matrix, or triggered serious risk.

## Coverage Gate

Every PR/local discovery output begins with internal coverage rows; do not render them to the user. Pipeline uses
its single named lens and the receipt format in `references/pipeline-report.md` instead:

```markdown
DISCOVERY_COVERAGE:
| Lens | Required depth | Result | Evidence | Source |
|---|---|---|---|---|
| <lens> | deep/sniff/not_applicable | deep/sniff/not_applicable | <files/symbols/artifacts/commands or precise N/A reason> | required/reviewer-added |
```

Required PR/local lenses come from mode, diff, risks, files, sensitive-surface sniff, and discoveries. Before clean,
each has concrete evidence; give weak rows one focused follow-up and use Skeptic only for high-risk uncertainty.

## Findings, Skeptic, and Suggestions
Severity:
- 🔴 **BLOCKER** — must resolve before merge/commit/final-assurance handoff: correctness, security, privacy, safety,
  data loss, integrity, or required-evidence failure.
- 🟠 **CRITICAL** — evidenced material maintainability, operational, regression, completion-confidence, brittleness,
  or future-modification risk.
- 🟡 **SUGGESTION** — useful, actionable, diff-relevant, report-only preference; otherwise omit it.
Clean-code findings require material evidence, not taste. Internal fields include severity, location, evidence,
artifact refs, introduced-by-change, recommendation, dedupe key, Skeptic verdict, and fix status.
PR/local serious candidates require Skeptic disproof against introduced-change, callers, framework absorption,
reachability, intent, test-only/reviewed scope, and artifacts. Pipeline performs that disproof inside its one role,
without dispatch. Documented intent disputes only non-sensitive findings; test-only
scope disputes seriousness unless it masks regression. Planned-requirement claims require artifact evidence.
Only `CONFIRMED` 🔴/🟠 findings are serious/fixable; exclude `DISPUTED`, and render `DOWNGRADED` only as 🟡.
Suggestions never start a loop; bundle at most 1–3 only with an approved same-root serious local fix when strictly
behavior-preserving. Use `../../references/decision-prompts.md` only for materially different authorized choices.

## Report Template

Render one Markdown body, not inline diff comments: header, optional verdict, finding counts, file/line counts, metadata, then 🔴/🟠/🟡 sections. Each finding
needs title, `Path`, evidence, and recommendation/tradeoffs. Omit empty sections; if all empty, render `No issues found. ✅`.

Footer states bounded review and Skeptic verification for serious findings, plus mode footer. Never
render coverage rows, raw tags, dedupe keys, state/lifecycle fields, or tracking IDs. Pipeline
findings are consistency/evidence signals.

## Fix Verification Gate

Every review-owned local repair passes `references/fix-implementer-contract.md` to a fresh Fix Implementer; PR
mode has no fix path. Pipeline mode returns classified findings, affected state, and suggested verification to the
Delivery Owner without dispatching a fix. A caller-owned local repair contract takes precedence.

After a delegated local fix batch, run Fix Verification as a fresh closure role, not second discovery. Inputs:
original findings, Fix Implementer report, pre/post metadata, boundaries, constraints, target paths, and code.

Return per dedupe key: `dedupe_key`, `verdict: closed|partially_closed|not_closed|reopened`, evidence, remaining risk,
and `next_action: none|same_scope_fix|widened_verification|full_rereview|authority_boundary`. Also include generic
affected-surface impact classification, triggers, and state: `review_pass`, `needs_fix`, `needs_widened_review`, or
`needs_user_authority`.

Classify packages, Slice H3s, validation advisories, artifact-root proof/report/matrix rows, source bindings,
evidence anchors, contracts, integration seams, safety/security/privacy/data surfaces, and whether impact is bounded. Named
triggers: `scope_expansion`, `public_api_or_schema_change`, `sensitive_risk_surface`,
`cross_package_impact`, `proof_invalidation`, `large_delta`, `non_closed_verdict`. Report new issues only
when they are fix-introduced serious regressions or explain a concrete trigger.

Non-closed findings, serious regressions, unresolved triggers, stale state, or dirty pipeline evidence block PASS.
Do not run full rereview solely because any new commit exists; target bounded impact and broaden only when isolation
fails. Do not repeat the same prompt with more tokens; change scope, evidence requirement, or verification seam.

## Stop if

- Mode ambiguity changes side-effect authority.
- PR/local review is asked to satisfy planned-feature proof/report/final-assurance gates, or pipeline review is asked
  to own full deliverable completeness; switch/stop at the owning gate.
- Reviewed state is stale, broadened, ambiguous, or not bound to the requested action.
- A serious finding lacks Skeptic verdict or required lens coverage is weak.
- A fix requires product/design choice, scope expansion, new dependency/service, unsafe command, credentials, external facts, destructive action, or risk
  acceptance.
- Pipeline caller/return, profile, named lens, exact `F`, or Delivery Owner context is missing; a low call includes
  separate reviewer/auditor/specialist roles; a standard/high call tries to start later assurance before `R` PASS;
  or artifact proof/report/Semgrep evidence or required widening is stale, contradictory, or uncertain.

## Output
Return mode report, caller/return, classified findings/affected state, and blockers. Pipeline returns only `C` with
explicit code-risk/completion verdicts (low) or `R` PASS/FAIL (standard/high), bound to `F`; never `U`, `V`, repair,
or merge readiness.
