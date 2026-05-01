---
name: review-code
description: >
  This skill should be used when the user asks to review a PR, review code changes, review a pull
  request, check code quality, or wants feedback on a diff. Works for both GitHub
  PRs (provide a PR URL or number like "owner/repo#42") and local code changes (staged, unstaged,
  or branch diffs). Triggers on phrases like "review this PR", "review my code", "check these
  changes", "code review", "review", "look over my changes". Also activates as the final step
  in the development pipeline after implementation.
---

# Code Review — Multi-Agent Pipeline

A unified code review that uses a bounded reviewer topology: the default Code Reviewer always
reviews the diff, one specialist is added only when risk triggers require it, and serious findings
are verified by a Skeptic Agent before reporting. Works in three modes depending on context.

## Step 1 — Detect Review Mode

Determine the review scope using this priority order:

### Priority 0: Pipeline Context

If a feature was just implemented in this session (feature name and merge worktree path are
known from the implementation step), review the feature branch directly.
Worktree path conventions are defined in the `worktree` skill. Invoke it if necessary

- Work from the merge worktree at `.worktrees/<feature>/merge/`
- `DIFF_CMD="git diff main...feature/<feature>"`
- Collect file list: `git diff main...feature/<feature> --stat`
- Scope: complete feature branch diff against main

Report scope before proceeding:

```
Review Scope: feature branch `feature/<name>` vs main
Worktree: .worktrees/<feature>/merge/
Files changed: <count>
Insertions: +<count>  Deletions: -<count>
```

Then skip to Step 2 (shared pipeline).

### Priority 1: PR Mode

A PR identifier is present (URL like `https://github.com/org/repo/pull/42`, shorthand like
`owner/repo#42`, or just `#42` in a repo context).

Read `references/pr-workflow.md` for setup, report format, and post-review actions.

### Priority 2: Local Mode

No PR identifier, no pipeline context. The user wants to review local changes (staged, unstaged,
or a branch diff).

Read `references/local-workflow.md` for **scope detection (Phase 0), setup (Phase 1)**,
report format, and actions.

Complete the mode-specific **setup and preflight** from the reference file, then return here for
the shared review pipeline (Steps 2-3). After the shared pipeline, go back to the reference file
for the **report format** and **gated actions**.

---

## Step 2 — Bounded Reviewer Topology

### Model Selection

Read `${CLAUDE_PLUGIN_ROOT}/references/model-preferences.md` for the canonical schema and resolution procedure.

Resolve model preferences for these roles:

- **Code Reviewer:** Use the `review-code` key. Hardcoded default: `inherit`.
- **Specialist Reviewer:** Use the `review-code` key. Hardcoded default: `inherit`.
- **Skeptic Agent:** Use the `skeptic-agent` key. Hardcoded default: `inherit`.

**Adaptive interpretation for review-code:** The Code Reviewer and any selected specialist use
Sonnet for focused review. Skeptic uses Opus for adversarial reasoning across confirmed serious
findings (via `skeptic-agent` key — when it resolves to `adaptive`, use the strongest available
model). When the resolved value is `inherit`, all agents use the orchestrator's model. When the
resolved value is a specific model name, pass it directly.

### Reviewer Caps

Reviewer caps count every delegated reviewer, including the Skeptic Agent.

| Review type | Reviewers | Cap |
|---|---|---|
| Normal review | Code Reviewer + conditional Skeptic | 2 |
| Risky review | Code Reviewer + one selected specialist + conditional Skeptic | 3 |

Run exactly one Code Reviewer for every batch. Add at most one specialist reviewer for the whole
review or current semantic batch. Do not create multiple specialist reviewers when multiple triggers
map to the same specialist. Spawn the Skeptic only when there are serious findings, cross-batch
serious-finding conflicts, or mode gates require a final verification pass.

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

### Code Reviewer Mandate

The Code Reviewer receives:

- The full diff, or the current semantic batch diff if big-diff batching is active
- Change context: PR description and title, commit messages, user-supplied context, or feature context
- Codebase path for file exploration: the review worktree path (`.worktrees/pr-review/<number>/`
  for PR mode, `.worktrees/<feature>/merge/` for pipeline mode, or the project root for local mode)
- When available: `SPEC.md`, `tasks.json`, and audit results as task-awareness context

The Code Reviewer must always perform and report a baseline security/privacy/safety sniff. Blanket
mode cannot skip, silence, or replace this sniff. The sniff is not a substitute for an on-demand
specialist security review when risk triggers require one.

When task-awareness context is available, the Code Reviewer flags apparent planned requirement or
acceptance-criteria omissions, contradictions, or regressions. These are review-code findings, not
completion proof: the audit skill remains the authoritative completeness gate for proving all
planned tasks and acceptance criteria.

### Specialist Mandate

The optional specialist receives the same inputs as the Code Reviewer plus the trigger that selected
that specialist. The specialist focuses only on that risk domain and returns findings using the
canonical finding contract below.

---

## Step 2A — Big-Diff Batching

If the diff exceeds 2,000 lines or is too broad for one coherent review, split it into semantic
batches by related files, module boundaries, ownership boundaries, or feature areas. Do not add extra
reviewer types by default just because a diff is large.

For each batch:

1. Preserve mode context and reviewed-state metadata.
2. Run the bounded reviewer topology for that batch.
3. Keep the per-batch reviewer cap: normal batches cap at 2 reviewers; risky batches cap at 3.
4. Assign stable dedupe keys to every finding.
5. Carry confirmed, disputed, downgraded, and suggestion findings into a cross-batch dedupe set.

After all batches, run one final global integration verification pass over the consolidated finding
set and the whole reviewed state. This pass verifies cross-batch serious findings, detects conflicts
or duplicates across batches, and confirms that no batch-local recommendation breaks another batch.
It does not reopen the default reviewer fanout.

---

## Step 3 — Finding Contract and Adversarial Verification

### Severity Taxonomy

Every finding must be classified — no exceptions:

| Severity | Label | Meaning |
|---|---|---|
| 🔴 | **BLOCKER** | Must be resolved before merge/commit. Correctness, security, privacy, safety, data-loss, or integrity risk. |
| 🟠 | **CRITICAL** | Strongly recommended fix. Significant quality, maintainability, operational, or regression risk. |
| 🟡 | **SUGGESTION** | Non-blocking improvement that is actionable, diff-relevant, and deduplicated. |

### Canonical Finding Contract

Each reviewer returns findings that can drive the report, decision cards, blanket-mode behavior, and
fix workflows without adding hidden fields later. Each finding must include:

| Field | Requirement |
|---|---|
| `severity` | 🔴 BLOCKER, 🟠 CRITICAL, or 🟡 SUGGESTION. |
| `tags` | Domain tags such as `security`, `privacy`, `safety`, `data-integrity`, `migration`, `persistence`, `performance`, `public-api`, `architecture`, `cross-module`, `tests`, `docs`, or `task-awareness`. |
| `location` | File and line range when available; otherwise the smallest diff hunk, symbol, or module that supports the finding. |
| `title` | Short, specific summary. |
| `evidence` | Diff/code evidence sufficient for a maintainer to reproduce the concern. Serious findings require enough evidence for independent Skeptic verification. |
| `introduced_by_change` | `yes`, `no`, or `unclear`, with the reason. Findings not introduced by the reviewed change are disputed for 🔴/🟠 unless the mode explicitly asks for broader audit. |
| `task_awareness_signal` | `none`, `omission`, `contradiction`, or `regression`; include the referenced planned requirement or acceptance criterion when available. Audit remains authoritative for completeness. |
| `recommendation` | Concrete fix recommendation, or alternatives when materially different approaches exist. Alternatives must identify runtime behavior, blast radius, and public-surface tradeoffs. |
| `dedupe_key` | Stable key based on normalized root cause plus location/symbol, used across reviewers and big-diff batches. |
| `skeptic_verdict` | `not-required`, `confirmed`, `disputed`, or `downgraded`. 🔴/🟠 findings cannot be reported until the Skeptic sets this. |
| `suggestion_actionability` | For 🟡 only: explain why the suggestion is actionable, diff-relevant, and non-duplicative; otherwise do not report it. |
| `fix_status` | `unfixed`, `fix-proposed`, `fix-applied`, `verified`, `reopened`, or `not-applicable`. |

Reviewer output format:

```markdown
[SEV] FILE:LINE — TITLE
TAGS: <comma-separated tags>
EVIDENCE: <diff/code evidence; include repro reasoning for serious findings>
INTRODUCED_BY_CHANGE: <yes/no/unclear> — <reason>
TASK_AWARENESS: <none/omission/contradiction/regression> — <requirement or acceptance criterion if any>
RECOMMENDATION: <concrete fix, or alternatives with tradeoffs>
DEDUPE_KEY: <stable normalized key>
SUGGESTION_ACTIONABILITY: <required for 🟡, otherwise n/a>
FIX_STATUS: unfixed
```

If no findings, respond with exactly `NONE`. Do not append `NONE` after findings.

Suggestions are reportable only when they are actionable, relevant to the reviewed diff, and
deduplicated. Non-actionable preferences, style-only opinions without repository grounding, and
pre-existing unrelated issues are not reportable suggestions.

### Adversarial Verification (Skeptic Agent)

Spawn a Skeptic Agent (model per resolved preference from Step 2) that receives all 🔴 BLOCKER and
🟠 CRITICAL findings, the reviewed-state metadata, and any task-awareness context. The Skeptic
independently locates supporting evidence in the diff or codebase.

The Skeptic Agent's job is to *disprove* findings. Confirmation is a byproduct of failed disproof.
Do not reuse the same reasoning chain from the reviewer — that defeats the purpose.

Verdicts:

- **CONFIRMED** — Evidence independently reproduced; finding remains reportable.
- **DISPUTED** — Evidence not found or finding is outside reviewed scope; exclude from final report.
- **DOWNGRADED** — Serious severity not justified, but an actionable diff-relevant suggestion remains.

### False Positive Checklist

Before confirming any 🔴 or 🟠 finding, run every item below. A single failed check is sufficient
grounds to mark the finding **DISPUTED** unless the checklist says to downgrade.

**1 Scope Mismatch** — Was this issue introduced by this change, or does it pre-exist? If the issue
pre-exists and this change did not modify the relevant behavior, mark **DISPUTED**.

**2 Context Blindness** — Does the surrounding code (20+ lines above and below the flagged line,
plus imported utilities/middleware) already handle this? If addressed in context, mark **DISPUTED**.

**3 Framework or Library Absorption** — Is the framework, ORM, or middleware already handling this?
(SQL injection flagged with parameterized ORM; missing auth flagged with router-level middleware
guard; unhandled promise rejections with global error boundary.) If the framework provably absorbs
the concern, mark **DISPUTED**.

**4 Dead or Unreachable Code Path** — Is the flagged code reachable in any real execution path?
Check call chains, feature flags, conditional branches. If unreachable in production, mark
**DOWNGRADED** only when an actionable diff-relevant suggestion remains; otherwise mark
**DISPUTED**.

**5 Intentional Design** — Is this a deliberate, documented decision? Check PR description, commit
messages, inline comments, AGENTS.md, ARCHITECTURE.md, ADR files, user-supplied context, SPEC.md,
tasks.json, and audit results. If intentional and documented, mark **DISPUTED** only for
non-security, non-privacy, and non-safety findings. Security/privacy/safety risks that are real and
intentional remain reportable; mark them **CONFIRMED** and note the documented intent in the reason.

**6 Test-Scope Confusion** — Does this finding apply only to test code, fixtures, mocks, or seed
data? If exclusively in test scope, mark **DISPUTED** for 🔴/🟠 unless the test behavior masks a
real production regression.

**7 Task-Awareness Overclaim** — Does the finding claim a planned requirement omission,
contradiction, or regression without SPEC/tasks/audit evidence? If yes, remove the
`task-awareness` tag or mark **DISPUTED**. Review-code flags apparent inconsistencies only; audit
remains the authoritative completeness gate.

Skeptic output format:

```markdown
Finding: <original finding summary>
Dedupe key: <dedupe_key>
Checklist run: 1 2 3 4 5 6 7
Failed check: <checklist item that caused dispute, or NONE>
Verdict: CONFIRMED / DISPUTED / DOWNGRADED
Evidence: <independent evidence or absence of evidence>
Reason: <one sentence — what the Skeptic found or failed to find>
```

---

## Report Template

All modes use this canonical report structure. Substitute `<HEADER>` and `<METADATA>` per mode.

````markdown
## <HEADER>

<METADATA>

### 🔴 Blockers
1. [Finding] — `<filename>`, Line <line>
   <explanation>
   Evidence: <evidence>
   Recommendation: <fix or alternatives>

### 🟠 Critical Issues
1. [Finding] — `<filename>`, Line <line>
   <explanation>
   Evidence: <evidence>
   Recommendation: <fix or alternatives>

### 🟡 Suggestions _(non-blocking)_
1. [Finding] — `<filename>`, Line <line>
   Action: <specific, diff-relevant improvement>

---
_Review generated via bounded multi-agent analysis. All reported blockers and critical issues were
independently verified by the Skeptic Agent. Task-awareness findings are consistency signals only;
audit remains authoritative for planned-task and acceptance-criteria completeness._
````

**Universal format rules:**

- **Omit empty sections.** If all sections are empty: "No issues found. ✅"
- **Disputed findings:** Silently excluded. Do not list, count, or mention them.
- **Downgraded findings:** Reclassified from 🔴/🟠 to 🟡 by the Skeptic only when still actionable,
  diff-relevant, and deduplicated.
- **Show only Skeptic-confirmed findings** for 🔴 and 🟠.
- **Suggestions:** Include only actionable, diff-relevant, deduplicated 🟡 findings.
- **Decision-card compatibility:** A finding has enough data for a design-decision card when it is
  🔴/🟠, Skeptic-confirmed, and its recommendation lists multiple materially different alternatives.

---

## Step 4 — Report & Actions

Return to the mode-specific workflow:

- **PR Mode** → `references/pr-workflow.md` — Phase 4 (report preview) and Phase 5
  (approve / request-changes / edit / abort)
- **Local Mode** → `references/local-workflow.md` — Phase 4 (report) and Phase 5
  (fix / commit / details / abort)
- **Pipeline context** → Use the canonical report template above with these slot values,
  then pipeline-specific gated actions below.

### Design-Decision Filter

When applying fixes under blanket mode, a finding is **promoted to a decision card** only when
**all three** conditions hold:

1. Severity is `[BLOCKER]` or `[CRITICAL]`.
2. The finding is Skeptic-confirmed and tied to the immutable reviewed state.
3. The reviewer surfaced two or more valid fix approaches with different runtime behavior, blast
   radius, or public surface area, and choosing among them is a product or architecture decision.

Examples that prompt:

- "SQL injection — parameterize the query (status quo) OR migrate to ORM (3 callers affected, behavior preserved)"
- "Auth bypass — fix at middleware (centralized) OR per-route guard (explicit but verbose)"
- "Race condition — pessimistic lock (slower) OR optimistic retry (more code, faster happy path)"

Examples that do **not** prompt (fixed silently only when a mode permits fixing):

- "SQL injection — switch to parameterized query" (only one approach)
- "Off-by-one — change `<` to `<=`" (only one approach)
- "Missing null check — add guard" (only one approach)
- Any test-only fix, regardless of approach count, since it does not change shipped runtime behavior

Outside blanket mode, the mode-specific gated-action semantics continue to apply. Blanket mode never
bypasses the Code Reviewer's baseline security/privacy/safety sniff, the Skeptic requirement for
serious findings, or stale-state gates.

### Pipeline Context — Report & Actions

Use the canonical report template with:

- **HEADER:** ``Feature Branch Review — `feature/<name>` vs `main` ``
- **METADATA:** ``**Worktree:** `.worktrees/<feature>/merge/` | **Files:** <count> changed``

**Verdict:**

- **CLEAN** — No 🔴 or 🟠 findings. Feature branch is ready for merge approval.
- **ISSUES FOUND** — One or more 🔴 or 🟠 findings confirmed.

**Pipeline Gated Actions:**

| Keyword | Action |
|---|---|
| `fix` | Pipeline-context only: fix confirmed 🔴 and 🟠 findings in the merge worktree, then commit fixes to the feature branch. Under blanket mode, design-decision findings (see Design-Decision Filter above) are presented as decision cards via `${CLAUDE_PLUGIN_ROOT}/references/decision-prompts.md`; unambiguous non-design fixes may apply silently. Outside blanket mode, present each proposed fix with its finding evidence and ask `yes`/`skip` before applying that fix. PR mode has no code-fix path. |
| `details <N>` | Expand finding N with full context and recommended fix. Return to gated actions. |
| `abort` | No changes. Close review. |

Pipeline side-effect gates stay tied to the reviewed state captured before the review. Before any
pipeline fix or readiness action, revalidate that the feature branch head, base branch, diff, and
merge worktree metadata still match the reviewed state. Reject stale or broadened state and instruct
the user to rerun review. Pipeline mode does not use delegated local Fix Verification Review in this
redesign.

> `commit` is not offered — feature branch code is already committed. Use `fix` to apply
> corrections, which are committed to the feature branch in the merge worktree.

_Designed for multi-agent orchestration. Requires: `git` (always), `gh` CLI (PR mode only)._
