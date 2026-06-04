# Canonical Review Report Template

All review modes use this template. Substitute `<HEADER>` and `<METADATA>` per the active mode:

- PR mode: values come from `pr-workflow.md`.
- Local mode: values come from `local-workflow.md`.
- Pipeline mode: values come from `pipeline-report.md`.

Rendered reports are developer-facing. Internal reviewer metadata such as `DISCOVERY_COVERAGE`, tags, dedupe keys, state fields, and fix metadata stays internal.

## Posting Strategy

Reviews are posted or shown as one structured Markdown body, not inline diff comments.

````markdown
## <HEADER>

<OPTIONAL_VERDICT_LINE>
**Findings:** <N> 🔴 | <N> 🟠 | <N> 🟡
**Files reviewed:** <count> | **Lines:** +<insertions> / -<deletions>

<METADATA>

### 🔴 Blockers

#### 1. <title>
- **Path:** `<filename>:<start_line>-<end_line>`
- **Evidence:** <diff/code/artifact evidence sufficient for independent verification>
- **Recommendation:** <concrete fix or alternatives with tradeoffs>

### 🟠 Critical Issues

#### 1. <title>
- **Path:** `<filename>:<start_line>-<end_line>`
- **Evidence:** <diff/code/artifact evidence sufficient for independent verification>
- **Recommendation:** <concrete fix or alternatives with tradeoffs>

### 🟡 Suggestions _(non-blocking)_

#### 1. <title>
- **Path:** `<filename>:<line>`
- **Action:** <specific, diff-relevant improvement>

---
_Review generated via bounded multi-agent analysis. Reported blockers and critical issues were independently verified by the Skeptic Agent. Planned-feature findings are consistency signals only; audit remains authoritative for Slice/package/proof completeness._
````

## Universal Formatting Rules

- Mode references own verdict placement. Render `**Verdict:** ...` only when the active mode supplies `<OPTIONAL_VERDICT_LINE>`.
- Initial discovery reviews must still produce `DISCOVERY_COVERAGE`; the orchestrator validates it but does not render it.
- Do not render internal tags, dedupe keys, state fields, lifecycle fields, or tracking IDs.
- Omit empty finding sections. If all finding sections are empty: `No issues found. ✅`.
- Silently exclude disputed findings.
- Downgraded findings appear only as actionable, diff-relevant suggestions.
- Show only Skeptic-confirmed 🔴/🟠 findings.
- Suggestions do not block readiness or create a separate fix loop.
- A finding has enough data for a user-decision card when it is serious, Skeptic-confirmed, and its recommendation lists multiple materially different alternatives.
- Planned-feature findings must be presented as consistency/evidence signals. Do not claim review-code has proven full Slice, package, proof, or final completion.
