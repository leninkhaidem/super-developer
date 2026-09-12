---
name: review-code
description: >
  Reviews PRs, local diffs, or integrated planned features with bounded independent analysis.
  Use for code review. Do not use as final completion audit or perform repairs unless the selected mode permits them.
---

# Review Code

Review one bound state, report actionable findings, and route allowed actions by mode. The main agent orchestrates;
fresh sub-agents perform semantic review. Do not mutate until the active mode authorizes it.

## Always

- Select PR, local, or pipeline mode; ordinary PR/local work does not inherit planned-feature artifacts or audit.
- Pipeline review is integration-first production-defect discovery, including standard-package production changes
  without independent verification. It is not whole-feature completeness; that belongs to audit.
- `CLEAN` means no open blocking finding for the reviewed state, not audit PASS or merge permission. Pipeline
  delivery needs independent same-freeze CLEAN + PASS; generated gate reports are not freeze inputs.
- Revalidate the bound state before posting, fixing, committing, refreshing evidence, or handing off audit context.
- Before authorizing review-owned repair, load `../../references/bounded-attempts.md` and bind its shared repair
  allowance in the existing fix approval. Supply its path, round/progress history, and remaining rounds to fix workers.
  During any caller-owned repair, all review/closure workers inherit the caller's remaining rounds; never
  restart its allowance or infer fix permission. PR remains review-only; local explicit gates remain unchanged.

## Mode Routing

1. PR URL, `owner/repo#N`, or `#N` in repository context → load `references/pr-workflow.md`; code is review-only.
2. No PR identifier or pipeline context → load `references/local-workflow.md`.
3. Feature artifacts plus integrated code state → load `references/pipeline-report.md` for required inputs,
   production coverage, bounded evidence widening, and pipeline handback.
4. Capture immutable refs/SHAs, worktree/PR identity, diff checksum or saved diff, changed files/status, roots, and
   mode artifact context before dispatch. Ambiguity that changes authority stops selection.

## Review Engine

- Build a compact manifest of runtime, public contracts, generated/schema/config, proof-critical tests, fixtures,
  and docs/tooling. Batch a large/mixed diff (roughly 2,000+ lines or too broad for one coherent review) by module,
  seam, package, or risk—not arbitrary line chunks. Keep production and its proving tests together where practical.
- Low-risk generated/repetitive content may use provenance checks or sampling with its owning surface.
- Run one Code Reviewer per batch. Add at most one specialist for triggered security/privacy/safety, data/change
  safety, performance/concurrency, or public-contract/integration risk. Add Skeptic for serious candidates,
  risky-clean coverage, serious cross-batch conflicts, or required mode gates. Caps including Skeptic: normal 2,
  risky 3. Resolve models through `../../references/model-preferences.md` when local policy applies; pass
  `../../references/clean-code-rules.md` to reviewers without loading it into the orchestrator.
- Preserve state metadata and stable dedupe keys across batches; consolidate findings once. Do one global pass
  for conflicting recommendations, cross-batch risks, and seams; reopen fanout only for a concrete coverage gap.
- Changed test-relevant behavior needs evidence from a check that actually ran. Do not invent receipt grammar or
  routinely rerun/line-review verified package tests; pipeline widening follows its loaded mode contract.

## Coverage Gate

Each reviewer returns internal coverage rows, not a user-facing worksheet:

```markdown
DISCOVERY_COVERAGE:
| Lens | Depth | Result | Evidence | Source |
|---|---|---|---|---|
| <lens> | deep/sniff/not_applicable | <result> | <concrete evidence or precise N/A reason> | required/reviewer-added |
```

Required lenses follow the mode contract, changed surfaces, and discovered risks. Before CLEAN, every required
lens has concrete coverage; `looks good`, `covered`, or bare `N/A` is insufficient. Give weak coverage one focused
follow-up, escalating to stronger/Skeptic review only for high-risk unresolved coverage.

## Findings and Skeptic

Severity has two tiers:
- 🔴 **BLOCKING:** demonstrated correctness, security/privacy/safety, data/integrity, or stated-contract failure.
- 🟡 **ADVISORY:** style, taste, speculative completeness, or maintainability concerns without such a defect.
  Report only; never block delivery or start a fix loop.

Challenge overengineering not traced to accepted requirements, Acceptance, or evidenced risk: unused extension
points, unnecessary layers/configuration, and premature optimization. It stays advisory unless it causes a real
blocking defect. Do not demand rewrites of working right-sized code; missing validation/error handling/tests are
separate evidence-based concerns.

For each serious candidate, Skeptic attempts to disprove it using introduced-change scope, surrounding callers,
reachability, framework handling, documented intent, test-only scope, and planned artifacts. Return verdict,
decisive checks, evidence, and reason. Intent cannot excuse actual security/privacy/safety defects; test-only
findings block only when they mask production regression. Requirement claims need artifact evidence.

Only `CONFIRMED` findings may be blocking/fixable. Exclude `DISPUTED`; show `DOWNGRADED` only as advisory.
Retain location, evidence, artifact refs, introduced-by-change, recommendation/tradeoff, dedupe key, Skeptic result,
and fix/actionability state internally; do not surface tracking noise.

Suggestions never start another loop. Bundle at most 1–3 with an approved blocking fix only for the same
file/symbol/root cause, behavior-preserving and optional to closure, with no new surface or API/schema/config/
permission/persistence/error/test/user-visible change. Ask a decision card via `../../references/decision-prompts.md`
only when valid fixes materially differ in behavior/blast radius/public surface and need product authority.
Otherwise delegate an unambiguous fix when the mode permits it.

## Fix Verification Gate

Every review-owned local/pipeline repair passes `references/fix-implementer-contract.md` to a fresh Fix
Implementer; PR mode has no fix path. For caller-owned local repair, review-code returns only an untrusted repair
proposal—and, in explicit mode, its accepted-fix receipt—to the owner; the owner validates it and constructs
bound-contract authoritative control. Review-code/Main never builds a caller packet or edits caller-owned repair.
Only for review-owned repair may Main apply a trivial behavior-preserving mechanical edit, with rationale.

Cluster only shared root cause, writable scope, and verification envelope; preserve round/progress history and the
shared task allowance. Reassess failed rounds under the loaded policy; planning requires an actual plan defect.
Cross-package repair requires every affected package/path/finding explicitly within one coherent seam envelope;
otherwise split or stop. Fresh Fix Verification checks closure, not second discovery, returning per finding
`verdict: closed|not_closed|reopened`, evidence, and `next_action: none|same_scope_fix|authority_boundary`.

Refresh only affected package evidence/seams plus feature Acceptance. Reuse unaffected evidence; pipeline CLEAN
for a new freeze still needs a separate fresh cold auditor's complete same-freeze PASS. Keep implementer,
package verifier, Fix Verification, and auditor separate.

## Stop if

- Requested action/mode is ambiguous, the bound state is stale or broadened, or side-effect authority is missing.
- A blocking candidate lacks Skeptic confirmation, or required coverage remains weak after its bounded follow-up.
- A fix requires scope/product/risk/manual authority, new dependencies/services, credentials/external facts,
  unsafe/destructive commands, or repair reaches non-convergence/exhausted effort. Required review that cannot fit
  the remaining allowance is incomplete, never CLEAN by omission.
- Pipeline review is asked to replace audit, or PR/local review is asked to satisfy unscoped pipeline gates.

## Output

Return one Markdown report with mode/state, verdict, finding counts, and nonempty blocking/advisory sections.
Each finding needs title, path, evidence, and recommendation/tradeoff. If empty: `No issues found. ✅`.
The footer states bounded review/Skeptic verification and mode-allowed next actions. Do not render internal
coverage/tracking fields. Pipeline output states audit readiness, never final audit PASS or merge permission.
