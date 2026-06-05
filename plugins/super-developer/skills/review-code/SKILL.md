---
name: review-code
description: >
  Review code changes with bounded multi-agent review. Use for PR review, local diff review, or the
  planned-feature final integrated code-review sibling to final audit. Do not use as final
  planned-feature completion audit or as a PR/local code-fix tool unless the selected mode explicitly
  permits fixes.
---

# Review Code

Run bounded code-risk review, then route report/actions by mode.

## Always

- Select exactly one mode: PR, local, or planned-feature pipeline.
- Keep PR/local reviews isolated from Slice/proof/report/audit obligations unless pipeline artifacts are explicitly in scope.
- Pipeline review is the final integrated code/evidence-risk gate; final audit remains the Slice/package/proof completeness gate.
- `CLEAN` means no confirmed serious review-code findings remain for the reviewed state; it is not audit PASS or merge readiness.
- The main agent orchestrates review, state gates, reports, and allowed action routing. Do not mutate code, GitHub state, lifecycle state, proof Markdown, package reports, or commits until the selected mode allows it.
- Revalidate immutable reviewed-state metadata before posting, fixing, committing, package evidence refresh, or audit-context handoff.

## Mode Routing

1. PR mode: PR URL, `owner/repo#N`, or `#N` in repo context → load `references/pr-workflow.md` for setup, preview, posting, approval, merge, and cleanup gates. PR mode is review-only for code changes.
2. Local mode: no pipeline context and no PR identifier → load `references/local-workflow.md` for scope detection, report, local fix/commit/details/abort gates.
3. Pipeline mode: explicit or inherited feature context plus `.tasks/<feature>/SPEC.md`, `tasks.json`, package/proof/report artifacts, and integrated worktree state → load `references/pipeline-report.md` for artifact gates, final review report, fix loop, and audit handoff.
4. Capture immutable reviewed-state metadata in the mode reference before reviewer dispatch: refs/SHAs, worktree or PR identity, diff checksum or saved diff, file list/status, and mode-specific artifact context.

## Review Engine

- Run one default Code Reviewer for the reviewed diff or semantic batch.
- Add at most one specialist for the whole review/batch, chosen by first triggered risk: security/privacy/safety; data integrity/persistence/migrations/destructive data; performance/concurrency/resource bounds; public contracts/exported types/architecture/cross-module integration.
- Add Skeptic only for serious findings, risky-clean coverage challenge, cross-batch serious conflicts, or mode gates that require adversarial verification. Reviewer caps include Skeptic: normal cap 2, risky cap 3.
- Resolve reviewer model only when local policy is relevant: `../../references/model-preferences.md`; pass `../../references/clean-code-rules.md` as a reviewer quality reference path instead of loading it in the orchestrator.
- Build a compact manifest before review: runtime/core code; public contracts/generated/schema/config; proof-critical tests; helpers/fixtures/mocks/snapshots/generated output; docs/build/tooling; pipeline artifacts when active.
- For changed tests, declare deep, sampled, or not-reviewed scope with rationale. Deep-review tests that are proof-critical, sensitive/data/concurrency/public-contract related, mutate globals/import state, use mocks/skips/snapshots, or prove changed behavior.
- In pipeline mode, add Slice-first context: package IDs, package/proof/report paths, assigned Slice/H3 IDs, verification expectations/results, risk notes, self-review summaries, report freshness, deferred concerns, and changed-file ownership.
- Pipeline final review is integration-first: cross-package seams, shared contracts, e2e behavior, Slice/proof/report contradictions, uncovered surfaces, evidence quality, report freshness, and whole-feature coherence. Do not deep-rereview package-local implementation unless a seam, gap, contradiction, stale report, or serious risk triggers it.

## Coverage Gate

Every discovery reviewer output begins with internal coverage rows; do not render them to the user:

```markdown
DISCOVERY_COVERAGE:
| Lens | Required depth | Result | Evidence | Source |
|---|---|---|---|---|
| <lens> | deep/sniff/not_applicable | deep/sniff/not_applicable | <files/symbols/contracts/artifacts/commands or precise N/A reason> | required/reviewer-added |
```

Required lenses come from mode, diff surface, risk notes, changed files, baseline `security-privacy-safety-sniff`, and discovered risks. Pipeline lenses commonly include `integration-seams`, `slice-proof-contradictions`, `proof-critical-tests`, `public-contracts`, `migration-data-integrity`, `performance-concurrency`, `package-boundary-regressions`, `package-report-freshness`, and `final-audit-boundary`.

Before a clean result: every required lens has concrete evidence at requested depth; no row is vague (`looks good`, `covered`, bare `N/A`); weak rows get one focused follow-up. Use Skeptic coverage challenge or stronger review only for high-risk unresolved coverage.

## Findings and Skeptic

Severity:

- 🔴 **BLOCKER** — must resolve before merge/commit/audit handoff: correctness, security, privacy, safety, data-loss, integrity, or required-evidence failure.
- 🟠 **CRITICAL** — significant quality, maintainability, operational, or regression risk that should be fixed before readiness.
- 🟡 **SUGGESTION** — non-blocking, report-only improvement that is actionable, diff-relevant, deduplicated, and grounded in repo conventions/contracts/risk.

Internal finding fields: `severity`, internal `tags`, `location`, `title`, `evidence`, `artifact_refs` or `none`, `introduced_by_change`, `planned_requirement_signal`, `recommendation`, `dedupe_key`, `skeptic_verdict`, `suggestion_actionability`, `fix_status`.

Serious candidates require Skeptic verification before reporting or fixing. Skeptic tries to disprove the finding against surrounding code, caller chains, frameworks, reachability, documented intent, test-only scope, reviewed-change scope, and planned-feature artifact evidence. Verdicts: `CONFIRMED`, `DISPUTED`, `DOWNGRADED`. Only confirmed 🔴/🟠 findings are reportable as serious; disputed findings are excluded; downgraded findings may appear only as actionable 🟡 suggestions.

Promote a user-decision card only when a Skeptic-confirmed serious finding has two or more valid fix approaches with materially different runtime behavior, blast radius, or public surface, and choosing among them is product/architecture authority. Otherwise delegate unambiguous fixes when the active mode permits. Use `../../references/decision-prompts.md` for card display.

## Report Template

Render one structured Markdown body, not inline diff comments:

```markdown
## <HEADER>
<OPTIONAL_VERDICT_LINE>
**Findings:** <N> 🔴 | <N> 🟠 | <N> 🟡
**Files reviewed:** <count> | **Lines:** +<insertions> / -<deletions>
<METADATA>

### 🔴 Blockers
#### 1. <title>
- **Path:** `<file>:<line-range>`
- **Evidence:** <independently verifiable evidence>
- **Recommendation:** <concrete fix or alternatives with tradeoffs>

### 🟠 Critical Issues
...

### 🟡 Suggestions _(non-blocking)_
...

---
_Review generated via bounded multi-agent analysis. Reported blockers and critical issues were independently verified by the Skeptic Agent._
<OPTIONAL_MODE_FOOTER>
```

Omit empty sections; if all are empty, render `No issues found. ✅`. Never render coverage rows, raw tags, dedupe keys, state fields, lifecycle fields, or tracking IDs. Pipeline findings must be consistency/evidence signals and must not claim exhaustive Slice/package/proof completion.

## Fix Verification Gate

Local and pipeline fixes are delegated; PR mode has no code-fix path. The main agent may apply only trivial behavior-preserving mechanical edits and must say why.

After a delegated fix batch, run Fix Verification Review as a closure gate, not a second discovery review. Inputs: original confirmed findings, Fix Implementer report, pre/post state metadata, batch boundaries, mode constraints, target paths, affected package/proof/report context when pipeline evidence may be stale, and enough surrounding context to verify the fix delta.

Required verdict per assigned dedupe key: `closed`, `partially_closed`, `not_closed`, or `reopened`, with evidence and next action. Also include regression sniff for affected security/privacy/safety/data/public-contract/concurrency/performance surfaces, widening triggers, and readiness: `ready_for_audit`, `needs_fix`, `needs_widened_review`, or `needs_user_authority`.

Non-closed findings, serious regressions, unresolved widening triggers, stale state, or dirty pipeline proof/report evidence block readiness. Do not repeat the same fix prompt with more tokens; change agent strength, scope split, evidence requirement, specialist lens, or verification seam. Reserve full rereview for deltas whose affected surfaces cannot be isolated.

## Stop if

- Mode ambiguity changes side-effect authority.
- PR/local review is asked to satisfy planned-feature proof/report/audit gates; switch to pipeline mode.
- Reviewed state is stale, broadened, ambiguous, or not bound to the requested action.
- A serious finding lacks Skeptic verdict or required lens coverage is weak.
- A fix requires product/design choice, scope expansion, new dependency/service, unsafe command, credentials, external facts, destructive action, or risk acceptance.
- Pipeline package proof/report freshness, review-code state, package verification rerun need, or widened verification is missing, stale, contradictory, or uncertain.

## Output

Return the mode-specific report, verdict, allowed next actions, and blocked readiness reason. In pipeline mode, state whether review-code is audit-ready; never state final audit PASS or merge readiness.
