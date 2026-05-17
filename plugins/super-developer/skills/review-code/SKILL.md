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
serious finding is verified by a Skeptic Agent before reporting. Works in three modes depending on
context.

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

### Discovery Review Lens Contract

For the initial discovery review, provide reviewers required dynamic risk lenses selected from the
active mode, diff surface, task or package context, package risk tags, changed files, baseline
security/privacy/safety sniff, and any risk signals found while reading the code. Each required
lens has a requested depth of `deep`, `sniff`, or `not_applicable`. Required lenses cannot be
dropped; reviewers may add lenses for newly discovered risks and must identify them as
reviewer-added. Use `references/finding-contract.md` for the compact coverage rows that keep
lens coverage separate from reportable findings.

### Code Reviewer Mandate

The Code Reviewer receives the full diff or current semantic batch diff, change context, codebase
path for exploration, reviewed-state metadata, required discovery-review lenses, available
task-awareness context, and `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/clean-code-rules.md` for the
Development Quality Contract. Use `references/finding-contract.md` for severity taxonomy,
canonical finding fields, discovery coverage output, output format, and suggestion actionability
rules.

The Code Reviewer must always perform and report a baseline security/privacy/safety sniff. Blanket
mode cannot skip, silence, or replace this sniff. The sniff is not a substitute for an on-demand
specialist security review when risk triggers require one.

The Code Reviewer must use the Development Quality Contract for maintainability, safety, API
compatibility, caller-contract, error-handling, trust-boundary, dependency, migration, performance,
concurrency, privacy, and dependency findings. Map contract **BLOCKER** issues to 🔴 BLOCKER. Map
significant **CODE-QUALITY** issues to 🟠 CRITICAL when they materially raise operational,
maintenance, or regression risk; otherwise map non-blocking actionable issues to 🟡 SUGGESTION. Use
**ADVISORY** only as 🟡 SUGGESTION.

When task-awareness context is available, the Code Reviewer flags apparent planned requirement or
acceptance-criteria omissions, contradictions, or regressions. These are review-code findings, not
completion proof: the audit skill remains authoritative for proving all planned tasks and acceptance
criteria. In pipeline context, review-code may use accepted package proofs as task-awareness context,
but must not duplicate audit's exhaustive role.

### Specialist Mandate

The optional specialist receives the same inputs as the Code Reviewer plus the trigger that selected
that specialist. The specialist focuses only on that risk domain and returns findings using
`references/finding-contract.md`.

---

## Step 2A — Big-Diff Batching

If the diff exceeds 2,000 lines or is too broad for one coherent review, split it into semantic
batches by related files, module boundaries, ownership boundaries, or feature areas. Do not add extra
reviewer types by default just because a diff is large.

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
than the requested depth make the review incomplete. Ask first for targeted follow-up on only the
missing or weak lenses; do not rerun the full review by default. Use a stronger reviewer or Skeptic
coverage challenge only after repeated weak coverage or when the gap is high-risk.

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
- **Pipeline context** → `references/pipeline-actions.md` for pipeline report slots, verdicts,
  fix implementer packet, and stale-state gate; load `references/decision-filter.md` only when a pipeline fix may require a design-decision card.

### Pipeline Context Invariants

Pipeline verdict semantics are unchanged:

- **CLEAN** — No 🔴 or 🟠 findings. Pipeline review is ready for final audit; merge approval is only
  appropriate after audit passes.
- **ISSUES FOUND** — One or more 🔴 or 🟠 findings confirmed.

Pipeline side-effect gates stay tied to the reviewed state captured before review. Before any
pipeline fix or readiness action, revalidate that the feature branch head, base branch, diff, and
merge worktree metadata still match the reviewed state. Reject stale or broadened state and instruct
the user to rerun review.

Pipeline fixes use the delegated Fix Implementer contract in `references/pipeline-actions.md`; the
main agent does not apply substantive production/test/documentation fixes inline. `commit` is not
offered in pipeline context because feature branch code is already committed.

### Blanket-Mode Boundary

Blanket mode cannot bypass the Code Reviewer's baseline security/privacy/safety sniff, the Skeptic
requirement for serious findings, stale-state gates, delegated fix verification where a mode requires
it, PR merge confirmation, or pipeline final-audit semantics. Blanket mode may only automate actions
that the active mode explicitly permits after those gates pass.

_Designed for multi-agent orchestration. Requires: `git` (always), `gh` CLI (PR mode only)._
