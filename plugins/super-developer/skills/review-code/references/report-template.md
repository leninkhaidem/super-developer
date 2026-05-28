# Canonical Review Report Template

All review modes use this template. Substitute `<HEADER>` and `<METADATA>` per the active mode:

- PR mode: values come from `pr-workflow.md`.
- Local mode: values come from `local-workflow.md`.
- Pipeline context: values come from `pipeline-report.md`.

Rendered review reports are developer-facing. Internal reviewer metadata such as
`DISCOVERY_COVERAGE`, `tags`, and `dedupe_key` remains available to the orchestrator for coverage
validation, routing, deduplication, state snapshots, and fix verification, but is not shown in the
user-facing report.

## Posting Strategy

Reviews are posted as a **single structured Markdown body** — no inline diff comments. This
optimizes for AI-agent consumption (single fetch, deterministic parsing) while remaining
human-scannable as rendered Markdown. All finding locations are explicit via `Path:` fields.

````markdown
## <HEADER>

<OPTIONAL_VERDICT_LINE>
**Findings:** <N> 🔴 | <N> 🟠 | <N> 🟡
**Files reviewed:** <count> | **Lines:** +<insertions> / -<deletions>

<METADATA>

### 🔴 Blockers

#### 1. <title>
- **Path:** `<filename>:<start_line>-<end_line>`
- **Evidence:** <diff/code evidence sufficient for independent verification>
- **Recommendation:** <concrete fix or alternatives with tradeoffs>

### 🟠 Critical Issues

#### 1. <title>
- **Path:** `<filename>:<start_line>-<end_line>`
- **Evidence:** <diff/code evidence sufficient for independent verification>
- **Recommendation:** <concrete fix or alternatives with tradeoffs>

### 🟡 Suggestions _(non-blocking)_

#### 1. <title>
- **Path:** `<filename>:<line>`
- **Action:** <specific, diff-relevant improvement>

---
_Review generated via bounded multi-agent analysis. All reported blockers and critical issues were
independently verified by the Skeptic Agent. Task-awareness findings are consistency signals only;
audit remains authoritative for planned-task and acceptance-criteria completeness._
````

## Universal Formatting Rules

- **Verdict placement:** Mode-specific workflow references own verdict placement. Render a
  `**Verdict:** ...` line only when the active mode explicitly supplies `<OPTIONAL_VERDICT_LINE>`;
  otherwise omit it from the report body and present the verdict where the mode workflow requires.
- **Internal coverage:** Initial discovery reviews must still produce `DISCOVERY_COVERAGE`, and the
  orchestrator must validate required-lens rows before declaring a clean review. Do not render the
  coverage table in user-facing reports.
- **Internal tags and tracking:** Keep `tags` and `dedupe_key` in internal finding records and
  state/fix workflows. Do not render `Tags`, `Dedupe`, `dedupe_key`, or tracking-ID fields in
  user-facing reports. If a domain classification matters to a developer, express it naturally in the
  title, evidence, or recommendation instead of exposing raw tags.
- **Omit empty finding sections.** If all finding sections are empty: `No issues found. ✅`
- **Disputed findings:** Silently excluded. Do not list, count, or mention them.
- **Downgraded findings:** Reclassified from 🔴/🟠 to 🟡 by the Skeptic only when still actionable,
  diff-relevant, and non-duplicative.
- **Show only Skeptic-confirmed findings** for 🔴 and 🟠.
- **Suggestions:** Include only actionable, diff-relevant, non-duplicative 🟡 findings. They do not
  block readiness or create a separate fix loop. Automatic suggestion fixes are allowed only under
  the bounded same-scope bundle rule in `finding-contract.md`.
- **Decision-card compatibility:** A finding has enough data for a design-decision card when it is
  🔴/🟠, Skeptic-confirmed, and its recommendation lists multiple materially different alternatives.
- **Task-awareness findings:** Present them as consistency signals only. Do not claim review-code has
  proven planned-task or acceptance-criteria completeness; audit owns that proof.
