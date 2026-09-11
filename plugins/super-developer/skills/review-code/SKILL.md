---
name: review-code
description: >
  Reviews code changes with bounded multi-agent analysis. Use for PRs, local diffs, or planned-feature final
  integrated review. Do not use for final planned-feature audit or PR/local repairs unless the selected mode
  explicitly permits fixes.
---

# Review Code

Run bounded review; route the report and any allowed action by mode.

## Always

- Select exactly one mode: PR, local, or planned-feature pipeline.
- Keep PR/local review separate from Slice/result/audit obligations unless pipeline artifacts are in scope.
- Pipeline `review-code` is the primary defect-discovery gate for integrated production correctness: cross-package
  seams plus production deltas from standard packages that had no independent package verifier. It requires minimal
  evidence-sufficiency coverage for those standard production changes; it is not a whole-feature completeness gate.
- Pipeline review also checks shared/public contracts, caller/callee behavior, coherence, integration-only changes,
  and triggered security/privacy/data/concurrency/lifecycle risk. It trusts fresh package-local verification where
  that evidence is independent and relevant; it is not a second package-test review.
- `CLEAN` means no open blocking finding remains for the reviewed state; it is not audit PASS or merge readiness.
  Final delivery requires an independently produced same-freeze review `CLEAN` and audit `PASS`.
- Review-code and audit are sibling final checks. Each may run once its own inputs are ready; audit has no false
  ordering prerequisite. If review context is supplied to audit, it must bind the same state; explicit `none` is
  valid. A prior or cross-freeze result never satisfies the final same-freeze pair.
- Main agent owns orchestration, state gates, reports, and action routing; semantic review/role work happen through
  dispatched sub-agents. No mutation until the active mode allows it.
- For pipeline retry/fix routing, the parent loads `../../references/bounded-attempts.md` and supplies its exact
  path/contents and current attempt binding in the packet before dispatch; pipeline references do not load it through
  a second hop. PR/local repair behavior remains governed by its own workflow.
- Revalidate reviewed-state metadata before posting, fixing, committing, evidence refresh, or audit-context handoff.

## Mode Routing

1. PR mode: PR URL, `owner/repo#N`, or `#N` in repo context → load `references/pr-workflow.md`. PR mode is
   review-only for code changes.
2. Local mode: no pipeline context and no PR identifier → load `references/local-workflow.md`.
3. Pipeline mode: feature context plus artifact root, SPEC (including `## Acceptance`), registry, package Markdown
   with Acceptance Checklists, package result reports, and integrated code worktree state → load
   `references/pipeline-report.md`.
4. Before reviewer dispatch, capture immutable refs/SHAs, worktree or PR identity, diff checksum or saved diff,
   file list/status, artifact root, code root, and mode artifact context.

## Review Engine and Big Diffs

- Build a compact manifest: core/runtime, public contracts, generated/schema/config, proof-critical tests,
  fixtures/snapshots, docs/tooling.
- Use semantic batching when the diff is about 2,000+ lines, many files, mixed domains, generated churn, or too
  broad for one coherent review. Split by package, module, seam, or risk surface, never arbitrary line chunks;
  keep source and tests proving the same behavior together when practical.
- For low-risk generated/docs/snapshots/repetitive fixtures, verify provenance or sample with the owning surface.
- Per batch preserve mode metadata, run bounded topology, assign stable dedupe keys, and merge verdicts into one
  cross-batch set. After batches, run one global integration pass for duplicates, conflicting recommendations,
  cross-batch serious risks, and seam issues; reopen fanout only when batch boundaries cannot preserve confidence.
- Run one default Code Reviewer sub-agent per diff/batch; add at most one specialist only when the diff/evidence
  triggers a sensitive surface: security/privacy/safety; data/persistence/change-safety; performance/concurrency;
  or public-contract/architecture/integration. Add Skeptic only for serious findings, risky-clean coverage,
  cross-batch serious conflicts, or required mode gates. Caps include Skeptic: normal 2, risky 3.
- Resolve reviewer model only when local policy matters (`../../references/model-preferences.md`); pass
  `../../references/clean-code-rules.md` without loading it in the orchestrator.
- For changed test-relevant surfaces, confirm coverage by a check that actually ran; do not impose receipt-grammar
  ceremony. In pipeline mode, do not routinely inspect the full test diff, line-review already verified
  package-local tests/fixtures/snapshots, or rerun package-local checks. Follow the bounded widening gate in
  `references/pipeline-report.md` and inspect only the minimum evidence needed.
- In pipeline mode, add Slice-first artifact-root context (package IDs, result report paths, Slice/H3 IDs,
  Acceptance Checklist results, standard/enhanced classification, integrated code state) and stay integration-first
  for production behavior. Route product/design Slice drift as advisory unless it is a real integration
  contradiction. Package result/report evidence is context for freshness, seams, and contradictions only; review-code
  does not own completeness.

## Coverage Gate

Every discovery reviewer output begins with internal coverage rows; do not render them to the user:

```markdown
DISCOVERY_COVERAGE:
| Lens | Depth | Result | Evidence | Source |
|---|---|---|---|---|
| <lens> | deep/sniff/not_applicable | deep/sniff/not_applicable | <concrete evidence> | required/reviewer-added |
```

Required lenses come from mode, diff surface, risk notes, changed files, security/privacy/safety sniff, and
discovered risks. Pipeline lenses additionally include every cross-package seam, each changed production delta
from a standard package without an independent verifier, shared/public contracts, and triggered risk surfaces.
Each standard-production-delta row names the exact changed path/symbol, behavior or invariant checked, concrete
code/result/check evidence, and its sufficiency result. Combine rows only when they prove the same behavior. This
is minimal production-evidence coverage, not a replay of every Acceptance Checklist item or a whole-feature audit.

Before clean: every required lens has concrete evidence; no vague rows (`looks good`, `covered`, bare `N/A`). Give
weak rows one focused follow-up. Use Skeptic/stronger review only for high-risk unresolved coverage.

## Findings, Skeptic, and Suggestions

Severity (two tiers — the bar):

- 🔴 **BLOCKING** — must resolve before merge/commit/audit handoff: correctness, security, privacy, safety,
  data loss, integrity, or a broken stated contract. Only these trigger a fix loop.
- 🟡 **ADVISORY** — everything else: maintainability opinions, brittleness, style, taste, non-blocking
  regressions with no evidence of a real defect. Report-only; never blocks, never starts a fix loop.

A finding is blocking only when it makes the software wrong, unsafe, lose data, or break a stated contract.
Do not manufacture blockers from taste or speculative completeness.

**Over-engineering lens:** flag complexity not traced to an accepted requirement or the `## Acceptance` criteria
— speculative abstraction, unused extensibility, needless layers/config/flags, or premature optimization. Report
it as 🟡 **ADVISORY** by default; escalate to 🔴 **BLOCKING** only when the excess creates a real
correctness/security/data/contract risk. Do not demand rewrites of working, right-sized code, and do not treat
simplicity itself as a defect — under-engineering (missing validation, error handling, or tests) is a separate
finding.

Internal fields: severity, tags, location, title, evidence, artifact refs, introduced-by-change, planned signal,
recommendation, dedupe key, Skeptic verdict, suggestion actionability, fix status.

Serious candidates require Skeptic verification before reporting or fixing. Skeptic tries to disprove against
introduced-change, surrounding code/callers, framework absorption, reachability, documented intent, test-only scope,
reviewed scope, and planned artifacts. Output verdict, decisive check(s), evidence, reason. Verbose rows are optional.

Documented intent disputes only non-security/privacy/safety findings; real security/privacy/safety risks stay
confirmed. Test-only scope disputes serious findings unless it masks production regression. Planned-requirement claims
require artifact evidence; review-code is not final audit.

Only `CONFIRMED` 🔴 blocking findings are reportable as blocking or fixable. `DISPUTED` findings are excluded.
`DOWNGRADED` findings may appear only as 🟡 advisory suggestions.

Suggestions are report-only and never start a separate fix loop. Auto-fix at most 1–3 per batch only when bundled
with an approved 🔴 fix, same file/symbol/root cause, behavior-preserving, no public/API/schema/config/permission/
persistence/error/test/user-visible change, no extra surface, and optional to closing the serious finding.

Promote a user-decision card only when a confirmed serious finding has multiple valid fixes with materially different
runtime behavior, blast radius, or public surface, and choice needs product/architecture authority. Otherwise
delegate unambiguous fixes when mode permits. Use `../../references/decision-prompts.md`.

## Report Template

Render one Markdown body, not inline diff comments: header, optional verdict, finding counts, file/line counts,
metadata, then 🔴/🟡 sections. Each finding needs title, `Path`, evidence, and recommendation/tradeoffs. Omit empty
sections; if all empty, render `No issues found. ✅`.

Footer states bounded review and Skeptic verification for serious findings, plus mode footer. Never render coverage
rows, raw tags, dedupe keys, state/lifecycle fields, or tracking IDs. Pipeline findings are consistency/evidence
signals.

## Fix Verification Gate

Every review-owned local/pipeline repair passes `references/fix-implementer-contract.md` to a fresh Fix
Implementer; PR mode has no fix path. For caller-owned local repair, review-code returns only an untrusted repair
proposal—and, in explicit mode, its accepted-fix receipt—to the owner; the owner validates it and constructs
bound-contract authoritative control. Review-code/Main never builds a caller packet or edits caller-owned repair.
Only for review-owned repair may Main apply a trivial behavior-preserving mechanical edit, with rationale.

After a delegated fix cluster, run focused Fix Verification as a fresh closure gate, not second discovery. Cluster
only shared root cause, writable scope, and verification envelope; preserve logical cluster identity and the
three-attempt cap. Review-owned cross-package repair is allowed only when every affected package, path, and finding
is explicitly enumerated under one coherent seam authority/verification envelope; otherwise split or stop.

Refresh **only affected package evidence and focused seams**, plus feature Acceptance. Return per finding:
`verdict: closed|not_closed|reopened`, evidence, and `next_action: none|same_scope_fix|authority_boundary`.
Unaffected results remain reusable. `CLEAN` may be restored for the new freeze, but cannot substitute for the
fresh cold auditor's complete same-freeze PASS. Keep Fix Implementer, Fix Verification, and auditor separate.

## Stop if

- Mode ambiguity changes side-effect authority.
- PR/local review is asked to satisfy planned-feature audit gates, or pipeline review is asked to own whole-feature
  completeness; switch/stop at the owning gate.
- Reviewed state is stale, broadened, ambiguous, or not bound to the requested action.
- A blocking finding lacks Skeptic verdict or required lens coverage is weak.
- A fix requires product/design choice, scope expansion, new dependency/service, unsafe command, credentials,
  external facts, destructive action, or risk acceptance.
- A blocking seam finding will not converge within 3 attempts.

## Output

Return the mode report, verdict, allowed next actions, and blocked readiness reason. In pipeline mode, state whether
review-code is audit-ready; never state final audit PASS or merge readiness.
