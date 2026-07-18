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
- `CLEAN` means no confirmed serious review-code findings remain for the reviewed state; it is not audit PASS, proof acceptance, or merge readiness.
- Main agent owns orchestration, state gates, reports, and action routing; semantic review happens through sub-agents.
  Pipeline mode follows `../../references/orchestration-convergence.md` and returns findings to its Delivery Owner;
  it never owns repair or lifecycle continuation. No mutation occurs unless local mode allows it.
- Revalidate reviewed-state metadata before posting, fixing, committing, evidence refresh, or audit-context handoff.

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
- Run one default Code Reviewer sub-agent for each diff or semantic batch.
- Add at most one specialist only when the diff/evidence triggers a sensitive surface: security/privacy/safety;
  data/persistence/change-safety; performance/concurrency; or public-contract/architecture/integration.
- Add Skeptic only for serious findings, risky-clean coverage, cross-batch serious conflicts, or required mode gates. Caps include Skeptic: normal 2, risky 3.
- Resolve reviewer model only when local policy matters: `../../references/model-preferences.md`.
  Pass `../../references/clean-code-rules.md`; do not load it in the orchestrator.
- For changed test-relevant surfaces, use only baseline-only, sampled, or deep scope with rationale and typed evidence; `not-reviewed`/`unreviewed` cannot support clean. Pipeline mode validates each fresh package `### Test Review Scope` receipt against its package-owned reviewed delta, reconciles the union of fresh package receipts against the integrated diff, and separately classifies/reviews integration-only or merge-resolution test-relevant changes. Widen only for canonical triggers/anomalies rather than rereviewing clean package-local tests.
- In pipeline mode, add Slice-first context from the artifact root: package IDs, proof/report paths,
  matrix source IDs/evidence anchors/source bindings, Slice/H3 IDs, verification results/advisories,
  Semgrep evidence when enabled or contracted, risks, deferred concerns, ownership, and the separate integrated code state. Route `context_only_slice_drift` through affected-surface classification as non-blocking by default unless reviewer judgment escalates material risk.
- Pipeline final review is integration-first: trust fresh package-local verification. Reopen local code only for
  a seam, integration-only change, contradiction, stale report, invalidated matrix, or triggered serious risk.

## Coverage Gate

Every discovery reviewer output begins with internal coverage rows; do not render them to the user:

```markdown
DISCOVERY_COVERAGE:
| Lens | Required depth | Result | Evidence | Source |
|---|---|---|---|---|
| <lens> | deep/sniff/not_applicable | deep/sniff/not_applicable | <files/symbols/artifacts/commands or precise N/A reason> | required/reviewer-added |
```

Required lenses come from mode, diff surface, risk notes, changed files, security/privacy/safety sniff, and discovered risks. Pipeline lenses include seams,
Slice/proof contradictions, proof-critical tests, public contracts, data integrity, performance/concurrency, package regressions, report freshness, and audit
boundary.

Before clean: every required lens has concrete evidence; no vague rows (`looks good`, `covered`, bare `N/A`). Give weak rows one focused follow-up. Use
Skeptic/stronger review only for high-risk unresolved coverage.

## Findings, Skeptic, and Suggestions

Severity:

- 🔴 **BLOCKER** — must resolve before merge/commit/audit handoff: correctness, security, privacy, safety, data loss, integrity, or required-evidence failure.
- 🟠 **CRITICAL** — material maintainability, brittleness, operational, regression, completion-confidence,
  or future-modification risk backed by concrete evidence before readiness.
- 🟡 **SUGGESTION** — non-blocking, report-only, actionable, diff-relevant, deduplicated, repo-grounded;
  optional style/taste concerns stay here only when useful, otherwise omit them.

Clean-code findings require material evidence, not taste. Downgrade or exclude preferences that do not show
brittleness, change-cost, caller-contract, safety/security/data, completion-confidence, or future-modification risk.

Internal fields: severity, tags, location, title, evidence, artifact refs, introduced-by-change, planned signal, recommendation, dedupe key, Skeptic verdict,
suggestion actionability, fix status.

Serious candidates require Skeptic verification before reporting or fixing. Skeptic tries to disprove against introduced-change, surrounding code/callers,
framework absorption, reachability, documented intent, test-only scope, reviewed scope, and planned artifacts. Output verdict, decisive check(s), evidence,
reason. Verbose rows are optional.

Documented intent disputes only non-security/privacy/safety findings; real security/privacy/safety risks stay confirmed. Test-only scope disputes serious
findings unless it masks production regression. Planned-requirement claims require artifact evidence; review-code is not final audit.

Only `CONFIRMED` 🔴/🟠 findings are reportable as serious or fixable. `DISPUTED` findings are excluded. `DOWNGRADED` findings may appear only as actionable 🟡
suggestions.

Suggestions are report-only and never start a separate fix loop. Auto-fix at most 1–3 per batch only when bundled with an approved 🔴/🟠 fix, same
file/symbol/root cause, behavior-preserving, no public/API/schema/config/permission/persistence/error/test/user-visible change, no extra surface, and optional
to closing the serious finding.

Promote a user-decision card only when a confirmed serious finding has multiple valid fixes with materially different runtime behavior, blast radius, or public
surface, and choice needs product/architecture authority. Otherwise delegate unambiguous fixes when mode permits. Use `../../references/decision-prompts.md`.

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

Return per dedupe key: `dedupe_key`, `verdict: closed|partially_closed|not_closed|reopened`, evidence, remaining risk, and `next_action: none|same_scope_fix|widened_verification|full_rereview|authority_boundary`. Also include generic affected-surface impact classification, triggers, and readiness: `ready_for_audit`, `needs_fix`, `needs_widened_review`, or `needs_user_authority`.

Classify packages, Slice H3s, validation advisories, artifact-root proof/report/matrix rows, source bindings,
evidence anchors, contracts, integration seams, safety/security/privacy/data surfaces, and whether impact is bounded. Named
triggers: `scope_expansion`, `public_api_or_schema_change`, `sensitive_risk_surface`,
`cross_package_impact`, `proof_invalidation`, `large_delta`, `non_closed_verdict`. Report new issues only
when they are fix-introduced serious regressions or explain a concrete trigger.

Non-closed findings, serious regressions, unresolved triggers, stale state, or dirty pipeline proof/report/matrix evidence block readiness. Do not run full rereview solely because any new commit exists; rerun targeted checks when impact is narrow/bounded and broaden only when affected surfaces cannot be isolated. Do not repeat the same prompt with more tokens; change agent strength, scope split, evidence requirement, specialist lens, or verification seam.

## Stop if

- Mode ambiguity changes side-effect authority.
- PR/local review is asked to satisfy planned-feature proof/report/audit gates, or pipeline review is asked to own full deliverable completeness; switch/stop at the owning gate.
- Reviewed state is stale, broadened, ambiguous, or not bound to the requested action.
- A serious finding lacks Skeptic verdict or required lens coverage is weak.
- A fix requires product/design choice, scope expansion, new dependency/service, unsafe command, credentials, external facts, destructive action, or risk
  acceptance.
- Pipeline caller/return or Delivery Owner context is missing, or artifact-root proof/report/Semgrep evidence,
  package-verification rerun need, validation advisory, or widened verification is stale/contradictory/uncertain.

## Output
Return mode report, verdict, caller/return, classified findings/affected state, owner actions, and blockers. Pipeline states audit readiness only; never final audit PASS or merge readiness.
