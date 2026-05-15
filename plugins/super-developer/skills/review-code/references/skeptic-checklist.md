# Skeptic Verification Checklist

Load this reference only when serious findings or mode gates require Skeptic verification. The
Skeptic receives all 🔴 BLOCKER and 🟠 CRITICAL findings, reviewed-state metadata, and available
task-awareness context.

## Mandate

The Skeptic Agent's job is to *disprove* findings. Confirmation is a byproduct of failed disproof.
Do not reuse the same reasoning chain from the reviewer; independently locate supporting evidence in
the diff or codebase.

## Verdicts

- **CONFIRMED** — Evidence independently reproduced; finding remains reportable.
- **DISPUTED** — Evidence not found or finding is outside reviewed scope; exclude from final report.
- **DOWNGRADED** — Serious severity not justified, but an actionable diff-relevant suggestion remains.

Only Skeptic-confirmed 🔴 and 🟠 findings are reportable as serious findings. Disputed findings are
silently excluded. Downgraded findings may be reported only as 🟡 suggestions when still actionable,
diff-relevant, and deduplicated.

## False Positive Checklist

Before confirming any 🔴 or 🟠 finding, run every item below. A single failed check is sufficient
grounds to mark the finding **DISPUTED** unless the checklist says to downgrade.

**1 Scope Mismatch** — Was this issue introduced by this change, or does it pre-exist? If the issue
pre-exists and this change did not modify the relevant behavior, mark **DISPUTED**.

**2 Context Blindness** — Does the surrounding code (20+ lines above and below the flagged line,
plus imported utilities/middleware) already handle this? If addressed in context, mark **DISPUTED**.

**3 Framework or Library Absorption** — Is the framework, ORM, or middleware already handling this?
Examples: SQL injection flagged with parameterized ORM; missing auth flagged with router-level
middleware guard; unhandled promise rejections with global error boundary. If the framework provably
absorbs the concern, mark **DISPUTED**.

**4 Dead or Unreachable Code Path** — Is the flagged code reachable in any real execution path?
Check call chains, feature flags, and conditional branches. If unreachable in production, mark
**DOWNGRADED** only when an actionable diff-relevant suggestion remains; otherwise mark
**DISPUTED**.

**5 Intentional Design** — Is this a deliberate, documented decision? Check PR description, commit
messages, inline comments, AGENTS.md, ARCHITECTURE.md, ADR files, user-supplied context, SPEC.md,
tasks.json, verification.json, context bundles, and audit results. If intentional and documented,
mark **DISPUTED** only for non-security, non-privacy, and non-safety findings. Security/privacy/safety
risks that are real and intentional remain reportable; mark them **CONFIRMED** and note the
documented intent in the reason.

**6 Test-Scope Confusion** — Does this finding apply only to test code, fixtures, mocks, or seed
data? If exclusively in test scope, mark **DISPUTED** for 🔴/🟠 unless the test behavior masks a real
production regression.

**7 Task-Awareness Overclaim** — Does the finding claim a planned requirement omission,
contradiction, or regression without SPEC/tasks/audit evidence? If yes, remove the `task-awareness`
tag or mark **DISPUTED**. Review-code flags apparent inconsistencies only; audit remains the
authoritative completeness gate.

## Skeptic Output Format

```markdown
Finding: <original finding summary>
Dedupe key: <dedupe_key>
Checklist run: 1 2 3 4 5 6 7
Failed check: <checklist item that caused dispute, or NONE>
Verdict: CONFIRMED / DISPUTED / DOWNGRADED
Evidence: <independent evidence or absence of evidence>
Reason: <one sentence — what the Skeptic found or failed to find>
```
