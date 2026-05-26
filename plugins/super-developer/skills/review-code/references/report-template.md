# Canonical Review Report Template

All review modes use this template. Substitute `<HEADER>` and `<METADATA>` per the active mode:

- PR mode: values come from `pr-workflow.md`.
- Local mode: values come from `local-workflow.md`.
- Pipeline context: values come from `pipeline-report.md`.

## Posting Strategy

Reviews are posted as a **single structured Markdown body** — no inline diff comments. This
optimizes for AI-agent consumption (single fetch, deterministic parsing) while remaining
human-scannable as rendered Markdown. All finding locations are explicit via `Path:` fields.

````markdown
## <HEADER>

**Verdict:** <APPROVE | REQUEST_CHANGES>
**Findings:** <N> 🔴 | <N> 🟠 | <N> 🟡
**Files reviewed:** <count> | **Lines:** +<insertions> / -<deletions>

<METADATA>

### Discovery Coverage
| Lens | Required depth | Result | Evidence | Source |
|---|---|---|---|---|
| <lens id/name> | <deep/sniff/not_applicable> | <deep/sniff/not_applicable> | <concrete coverage evidence or reason not applicable> | <required/reviewer-added> |

### 🔴 Blockers

#### 1. <title>
- **Path:** `<filename>:<start_line>-<end_line>`
- **Tags:** <comma-separated domain tags>
- **Evidence:** <diff/code evidence sufficient for independent verification>
- **Recommendation:** <concrete fix or alternatives with tradeoffs>
- **Dedupe:** `<stable normalized dedupe key>`

### 🟠 Critical Issues

#### 1. <title>
- **Path:** `<filename>:<start_line>-<end_line>`
- **Tags:** <comma-separated domain tags>
- **Evidence:** <diff/code evidence sufficient for independent verification>
- **Recommendation:** <concrete fix or alternatives with tradeoffs>
- **Dedupe:** `<stable normalized dedupe key>`

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

- **Discovery coverage:** For initial discovery review, include compact lens coverage before
  findings. Coverage is separate from findings and is still required when the finding sections are
  empty. Do not render a clean report until required-lens rows are complete and concrete.
- **Omit empty finding sections.** If all finding sections are empty: `No issues found. ✅`
- **Disputed findings:** Silently excluded. Do not list, count, or mention them.
- **Downgraded findings:** Reclassified from 🔴/🟠 to 🟡 by the Skeptic only when still actionable,
  diff-relevant, and deduplicated.
- **Show only Skeptic-confirmed findings** for 🔴 and 🟠.
- **Suggestions:** Include only actionable, diff-relevant, deduplicated 🟡 findings. They do not
  block readiness or create a separate fix loop. Automatic suggestion fixes are allowed only under
  the bounded same-scope bundle rule in `finding-contract.md`.
- **Decision-card compatibility:** A finding has enough data for a design-decision card when it is
  🔴/🟠, Skeptic-confirmed, and its recommendation lists multiple materially different alternatives.
- **Task-awareness findings:** Present them as consistency signals only. Do not claim review-code has
  proven planned-task or acceptance-criteria completeness; audit owns that proof.
