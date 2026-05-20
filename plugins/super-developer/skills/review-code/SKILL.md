---
name: review-code
description: >
  This skill should be used when the user asks to review a PR, review code changes, review a pull
  request, check code quality, or wants feedback on a diff. Works for both GitHub
  PRs (provide a PR URL or number like "owner/repo#42") and local code changes (staged, unstaged,
  or branch diffs). Triggers on phrases like "review this PR", "review my code", "check these
  changes", "code review", "review", "look over my changes". In the planned-feature pipeline it runs
  after package implementation and before the final internal audit.
---

# Code Review — Multi-Agent Pipeline

A unified code review that uses a bounded reviewer topology: the default Code Reviewer always
reviews the diff, at most one specialist is added only when risk triggers require it, and every
serious finding is verified by a Skeptic Agent before reporting. The shared engine owns discovery
review vocabulary, dynamic lens coverage, finding format, Skeptic verification, and fix-verification
semantics where fixes are allowed; mode-specific references own mutation and side-effect authority.
Works in three modes depending on context.

## Step 1 — Detect Review Mode

Determine the review scope using this priority order:

### Priority 0: Pipeline Context

If a feature was just implemented in this session (feature name and merge worktree path are known
from the implementation step), review the feature branch directly. Worktree path conventions are
defined in the `worktree` skill; invoke it if necessary.

- Work from the merge worktree at `.worktrees/<feature>/merge/`
- Resolve the reviewed base/target ref from implementation context; default to `main` when no stacked-feature target was declared.
- `DIFF_CMD="git diff <target-ref>...feature/<feature>"`
- Collect file list: `git diff <target-ref>...feature/<feature> --stat`
- Scope: complete feature branch diff against `<target-ref>`

Report scope before proceeding:

```text
Review Scope: feature branch `feature/<name>` vs `<target-ref>`
Worktree: .worktrees/<feature>/merge/
Files changed: <count>
Insertions: +<count>  Deletions: -<count>
```

Then skip to Step 2.

### Priority 1: PR Mode

A PR identifier is present (URL like `https://github.com/org/repo/pull/42`, shorthand like
`owner/repo#42`, or just `#42` in a repo context).

Read `references/pr-workflow.md` for PR setup/preflight, reviewed-state metadata capture, hard
stops, and report preview slots. Do not load `references/pr-actions.md` until the user reaches the
gated action phase. Use `references/report-template.md` for the canonical report.

### Priority 2: Local Mode

No PR identifier, no pipeline context. The user wants to review local changes (staged, unstaged, or
a branch diff).

Read `references/local-workflow.md` for scope detection, setup/preflight, reviewed-state metadata
capture, hard stops, and report slots. Do not load `references/local-actions.md` until the user
reaches the gated action phase. Use `references/report-template.md` for the canonical report and
`references/decision-filter.md` only when a local fix may require a design-decision card.

Complete the mode-specific setup and preflight from the workflow reference, then return here for the
shared review pipeline (Steps 2-3). After the shared pipeline, return to the mode workflow reference
for report rendering; load the mode action reference only after the gated action phase begins.

---

## Step 2 — Bounded Reviewer Topology

### Model Selection

Read `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/model-preferences.md` for the canonical schema and
resolution procedure.

Resolve model preferences for these roles:

- **Code Reviewer:** Use the `review-code` key. Hardcoded default: `inherit`.
- **Specialist Reviewer:** Use the `review-code` key. Hardcoded default: `inherit`.
- **Skeptic Agent:** Use the `skeptic-agent` key. Hardcoded default: `inherit`.

**Adaptive interpretation for review-code:** Code Reviewer and specialist use Sonnet for focused
review. Skeptic uses Opus for adversarial reasoning across confirmed serious findings via the
`skeptic-agent` key; when it resolves to `adaptive`, use the strongest available model. `inherit`
uses the orchestrator's model. A specific model name is passed directly.

### Reviewer Caps

Reviewer caps count every delegated reviewer, including the Skeptic Agent.

| Review type | Reviewers | Cap |
|---|---|---|
| Normal review | Code Reviewer + conditional Skeptic | 2 |
| Risky review | Code Reviewer + one selected specialist + conditional Skeptic | 3 |

Run exactly one Code Reviewer for every review or semantic batch. Add at most one specialist reviewer
for the whole review or current semantic batch. Do not create multiple specialist reviewers when
multiple triggers map to the same specialist. Spawn the Skeptic only when there are serious findings,
cross-batch serious-finding conflicts, risky clean coverage that needs targeted challenge, or mode
gates require a final verification pass.

### Specialist Escalation Priority

Classify the diff before delegation. If any named trigger is present, select the first matching
specialist in this deterministic priority order:

| Priority | Trigger | Specialist |
|---|---|---|
| 1 | Security, privacy, or safety-sensitive behavior | Security / Privacy / Safety |
| 2 | Data integrity, financial correctness, migrations, persistence, transactions, schema or storage changes | Data Integrity / Persistence |
| 3 | Performance, scalability, resource bounds, concurrency, latency, or blocking I/O | Performance |
| 4 | Public API, exported types, compatibility, architecture, or cross-module integration | Architecture / Integration |

If several triggers match, choose only the highest-priority specialist. Triggers mapped to the same
specialist still produce one specialist reviewer, not one reviewer per trigger.

### Diff Triage and Package Coverage

Before deep review, create a compact diff triage manifest. Classify changed files as runtime/core
code, public contracts/schemas/generated clients, tests that directly prove changed behavior, test
helpers/fixtures/mocks, snapshots/generated outputs, docs, build/config/tooling, or proof/task/review
artifacts. For changed tests, declare detailed, sampled, or not-reviewed scope with a short rationale.

In planned-feature pipeline context, also consume compact package coverage when available: package
IDs, risk tags, mandatory self-review summaries, targeted package review summaries/receipts,
verification and proof status, deferred concerns, and changed-file manifest. The final review remains
mandatory and integration-first. Its required lenses must cover cross-package and cross-domain seams,
shared contracts, end-to-end behavior, contradictions between packages/proofs/receipts, uncovered
surfaces, deferred concerns, and whole-feature coherence.

Accepted package review receipts stored in the compatibility `targeted_review` proof object count as
package-local coverage only when the receipt evidence is present, specific, fresh for the reviewed
integrated package state, complete for package risk-tag lenses, explicit about test scope, and
consistent with the package risk tags and proof status. Absent concrete contradiction, observed gap,
or serious issue, do not reopen or deeply rereview every work package by default; focus reviewers and
specialists on integration seams, coverage gaps, stale/weak receipts, contradictions, deferred risks,
or uncovered cross-package behavior. Missing, vague, stale, risk-incomplete, test-scope-omitting, or
risk-tag-inconsistent receipts are coverage gaps and must be routed to the narrowest package coverage
follow-up, bounded widening, or proof refresh instead of being trusted blindly.

### Discovery Review Lens Contract

For the initial discovery review, provide reviewers required dynamic risk lenses selected from the
active mode, diff surface, task or package context, package risk tags, changed files, baseline
security/privacy/safety sniff, and any risk signals found while reading the code. In planned-feature
pipeline context, include explicit integration lenses for cross-package seams, shared contracts,
package-proof/receipt contradictions, uncovered surfaces, deferred concerns, and end-to-end feature
coherence. Each required lens has a requested depth of `deep`, `sniff`, or `not_applicable`.
Required lenses cannot be dropped; reviewers may add lenses for newly discovered risks and must
identify them as reviewer-added. Use `references/finding-contract.md` for the compact coverage rows
that keep lens coverage separate from reportable findings.

### Code Reviewer Mandate

The Code Reviewer receives the full diff or current semantic batch diff, diff triage manifest,
change context, codebase path for exploration, reviewed-state metadata, required discovery-review
lenses, available task-awareness and package-coverage context, and
`${SUPER_DEVELOPER_PLUGIN_ROOT}/references/clean-code-rules.md` for the Development Quality Contract.
Use `references/finding-contract.md` for severity taxonomy, canonical finding fields, discovery
coverage output, output format, and suggestion actionability rules.

The Code Reviewer must always perform and report a baseline security/privacy/safety sniff. Blanket
mode cannot skip, silence, or replace this sniff. The sniff is not a substitute for an on-demand
specialist security review when risk triggers require one.

The Code Reviewer must use the Development Quality Contract for maintainability, safety, API
compatibility, caller-contract, error-handling, trust-boundary, dependency, migration, performance,
concurrency, privacy, and dependency findings. Map contract **BLOCKER** issues to 🔴 BLOCKER. Map
significant **CODE-QUALITY** issues to 🟠 CRITICAL when they materially raise operational,
maintenance, or regression risk; otherwise map non-blocking actionable issues to 🟡 SUGGESTION. Use
**ADVISORY** only as 🟡 SUGGESTION. Suggestions are report-only by default across modes: they do not
block readiness, change the verdict, or create a separate review/fix loop. Use
`references/finding-contract.md` for the narrow conditions under which an active mode may bundle a
suggestion with a serious fix.

When task-awareness context is available, the Code Reviewer flags apparent planned requirement or
acceptance-criteria omissions, contradictions, or regressions. These are review-code findings, not
completion proof: the audit skill remains authoritative for proving all planned tasks and acceptance
criteria. In pipeline context, review-code may use accepted package proofs, package self-review, and
targeted package review summaries as task-awareness context, but must not duplicate audit's exhaustive
role or redo package-local review without a coverage gap or integration-level risk.

Detailed review follows behavior-first order: understand intended behavior from SPEC/tasks/proofs and
package reports, review core/runtime functionality first, derive expected test obligations, inspect
corresponding tests as evidence quality, then inspect remaining test-only/generated/config changes as
needed. Tests are in scope as proof quality, but not exhaustively line-reviewed by default. Review
tests in detail when they are proof-cited, the only evidence for behavior, risk-bearing
security/privacy/data/concurrency/failure coverage, changing mocks/fixtures/helpers/snapshots/generated
contracts, using skips/xfails/global/env/import-cache mutation, or themselves the feature/risk surface.

### Specialist Mandate

The optional specialist receives reviewed-state metadata, the trigger that selected that specialist,
required lens rows for that risk domain, relevant package-coverage context, and the relevant
diff/surfaces needed to evaluate the trigger. For small coherent diffs this may be the same diff as
the Code Reviewer; for large, batched, generated, docs, or low-risk surrounding changes, pass a scoped
packet plus repo/worktree access instead of duplicating the full review context. The specialist
focuses only on that risk domain and returns findings using `references/finding-contract.md`.

### Fix Verification Reviewer Mandate (fix modes only)

When an action that the active mode permits has applied a delegated fix batch, use a shared Fix
Verification Reviewer instead of automatically rerunning the full discovery review. Load
`references/fix-verification.md` only at that point. Pipeline mode may reach this path through its
auto-resolve/fix action rules. Local mode may reach it only after the user explicitly chooses `fix`
or blanket-mode authorization applies under `references/local-actions.md`. The Fix Verification
Reviewer checks closure for assigned confirmed findings by dedupe key, runs a serious-regression
sniff over the fix delta and affected surfaces, and reports widening triggers without rediscovering
unrelated issues by default. PR mode remains report-only for code changes and does not create this
fix path.

---

## Step 2A — Big-Diff Batching

If the diff exceeds 2,000 lines or is too broad for one coherent review, use the diff triage
manifest to split only where semantic boundaries improve review confidence. Group low-risk generated,
docs, snapshot, and repetitive test changes with their owning source surface when possible. Do not add
extra reviewer types by default just because a diff is large.

For each batch: preserve mode context and reviewed-state metadata; run the bounded reviewer topology
for that batch; keep the per-batch cap (normal 2, risky 3); assign stable dedupe keys; and carry
confirmed, disputed, downgraded, and suggestion findings into a cross-batch dedupe set.

After all batches, run one final global integration verification pass over the consolidated finding
set and whole reviewed state. This pass verifies cross-batch serious findings, detects conflicts or
duplicates, and confirms that no batch-local recommendation breaks another batch. It does not reopen
the default reviewer fanout.

---

## Step 3 — Finding Contract, Coverage Gate, and Adversarial Verification

Read `references/finding-contract.md` before delegating reviewers. Every reviewer must use its
severity taxonomy, canonical fields, discovery coverage output, output format, and suggestion
actionability rules.

Before treating a discovery review as clean, reconcile `DISCOVERY_COVERAGE` against the required
lens list. Missing required rows, vague evidence, unsupported `not_applicable`, or coverage shallower
than the requested depth make the review incomplete. Ask first for one targeted follow-up on only the
missing or weak lenses; do not rerun the full review by default. Use a stronger reviewer or Skeptic
coverage challenge only when that focused follow-up still leaves a high-risk lens unproven, when the
gap itself is security/privacy/safety/data-integrity critical, or when a mode-specific gate requires
adversarial coverage. If a non-high-risk required lens remains incomplete after the targeted
follow-up, report the exact coverage gap as blocking/incomplete and route to the narrowest missing
evidence or focused reviewer; do not mark the review clean or expand to whole-feature rereview by
default.

Serious findings require Skeptic verification. Spawn a Skeptic Agent using the resolved Step 2 model
for all 🔴 BLOCKER and 🟠 CRITICAL findings, plus cross-batch serious-finding conflicts, risky clean
reviews with weak `NO_FINDING`/`NONE` or coverage rows, or final verification gates. Read
`references/skeptic-checklist.md` for the adversarial procedure, false-positive checklist, coverage
challenge mode, verdict meanings, and Skeptic output format.

The Skeptic's job is to disprove findings. Only Skeptic-confirmed 🔴 BLOCKER and 🟠 CRITICAL findings
are reported. Disputed serious findings are silently excluded. Downgraded serious findings may appear
only as 🟡 SUGGESTION when still actionable, diff-relevant, and deduplicated. Initial reviewers never
set `skeptic_verdict` beyond `not-required`; only the Skeptic may set `confirmed`, `disputed`, or
`downgraded`. A clean discovery result is valid only after every required lens has concrete coverage
and every serious candidate has completed Skeptic confirmation, dispute, or downgrade.

---

## Step 4 — Report & Actions

Read `references/report-template.md` to produce the canonical report. It owns the shared report
structure, universal formatting rules, and the rule that empty reports say `No issues found. ✅`.

Return to the mode-specific workflow:

- **PR Mode** → `references/pr-workflow.md` Phase 4 for report preview. After the user reaches the
  gated action phase, load `references/pr-actions.md` for approve / request-changes / merge / edit /
  abort semantics.
- **Local Mode** → `references/local-workflow.md` Phase 4 for the report. After the user reaches the
  gated action phase, load `references/local-actions.md` for fix / commit / details / abort semantics.
- **Pipeline context** → `references/pipeline-report.md` for pipeline report slots, verdicts, clean-path
  snapshot validation, and stale-state/audit-readiness gates. Load `references/pipeline-actions.md`
  only after **ISSUES FOUND** or an allowed pipeline `fix` action requires fix batching,
  proof-impact/dirty-proof handling, widening, escalation, or Fix Verification Review handoff. Load
  `references/decision-filter.md` only when a pipeline fix may require a design-decision card.

### Pipeline Context Invariants

Pipeline verdict semantics are unchanged:

- **CLEAN** — No 🔴 or 🟠 findings. Pipeline review is ready for final audit; merge approval is only
  appropriate after audit passes.
- **ISSUES FOUND** — One or more 🔴 or 🟠 findings confirmed.

Pipeline side-effect gates stay tied to the reviewed state captured before review. Before any
pipeline fix or readiness action, revalidate that the feature branch head, base branch, diff, and
merge worktree metadata still match the reviewed state. Reject stale or broadened state and instruct
the user to rerun review.

Pipeline fixes load `references/pipeline-actions.md` for the delegated Fix Implementer contract and
mode-specific proof-impact gates, then use the shared Fix Verification Review in
`references/fix-verification.md`; the main agent does not apply substantive
production/test/documentation fixes inline. `commit` is not offered in pipeline context because
feature branch code is already committed. Clean pipeline reviews must not load detailed fix
implementer packets, dirty-proof handling, widening, or escalation text. Do not rerun the full
discovery review after every fix batch by default; widen only when the shared fix-verification
reference reports a concrete trigger and the pipeline action reference routes it.

### Blanket-Mode Boundary

Blanket mode cannot bypass the Code Reviewer's baseline security/privacy/safety sniff, the Skeptic
requirement for serious findings, stale-state gates, delegated fix verification where a mode requires
it, PR merge confirmation, or pipeline final-audit semantics. Blanket mode may only automate actions
that the active mode explicitly permits after those gates pass.

_Designed for multi-agent orchestration. Requires: `git` (always), `gh` CLI (PR mode only)._
