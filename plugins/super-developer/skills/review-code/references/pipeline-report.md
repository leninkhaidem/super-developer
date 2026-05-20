# Pipeline Review Report and Clean-Path Gate

Load this reference in planned-feature pipeline context after the shared review pipeline, before any
pipeline verdict or action decision. It owns report slots, verdict selection, the clean-path stale
state/audit-readiness gate, and the handoff to fix actions only when confirmed serious issues exist.

## Pipeline Report Slots

Use `report-template.md` with:

- **HEADER:** ``Feature Branch Review — `feature/<name>` vs `<target-ref>` ``
- **METADATA:** ``**Worktree:** `.worktrees/<feature>/merge/` | **Files:** <count> changed``

## Verdicts

- **CLEAN** — No Skeptic-confirmed 🔴 or 🟠 findings. Pipeline review may proceed to final audit
  readiness checks; merge approval is only appropriate after audit passes.
- **ISSUES FOUND** — One or more 🔴 or 🟠 findings were confirmed by the Skeptic.

There is no third option. Suggestions alone do not change a clean verdict.

## Package Coverage Input

When planned-feature package coverage exists, final review-code consumes it as compact context, not as
a second proof ledger: package IDs, risk tags, self-review summaries, targeted package review
summaries/receipts, verification/proof status, deferred concerns, and changed-file manifest. Accepted
package review receipts stored in the existing `targeted_review` proof object count as package-local
coverage absent concrete contradiction, observed gap, or serious issue. Final review still performs a
baseline security/privacy/safety sniff plus cross-package/cross-domain integration review, uncovered
surface checks, contradiction checks, deferred-concern checks, and whole-feature coherence review.

Receipt trust is conditional. Treat package-local coverage as valid only when the receipt is present,
specific about reviewed integrated state, fresh for the current package state, complete for the
package's risk-tag lenses, explicit about test scope, and consistent with proof status and risk tags.
Missing, vague, stale, risk-incomplete, test-scope-omitting, or contradictory receipts are coverage
gaps. Route those gaps to the narrowest package coverage follow-up, bounded widening, or proof refresh;
do not mark the final review clean from weak receipt evidence and do not deeply rereview every work
package by default. A final reviewer may report a concrete observed package-local serious issue found
while checking an integration seam, contradiction, uncovered surface, or receipt gap, but must not
actively hunt package internals without that trigger.

## Clean-Path State Snapshot

For pipeline reviews, refresh the orchestrator-owned lightweight snapshot at:

```text
.tasks/<feature>/reviews/review-code-state.json
```

The snapshot is governance state only. It is not proof, audit evidence, task lifecycle, package proof
content, a review transcript, an event stream, or a second acceptance ledger.

For a **CLEAN** verdict, the snapshot must bind the reviewed state and readiness decision with:

- `schema_version`, `feature`, `mode: "pipeline"`, `updated_at`.
- `reviewed_state`: feature ref/head, base ref/SHA, target ref, reviewed diff or checksum, reviewed
  file list/status checksum, and merge worktree metadata.
- `lenses`: one compact row per required discovery lens, including the baseline
  security/privacy/safety sniff, with requested depth, completion status, and concrete coverage
  pointer/summary.
- `findings`: no confirmed serious finding keys; suggestions may be omitted or linked from the report.
- `closure_status`: `ready_for_audit` true only when snapshot validation passes and no confirmed
  serious finding, serious regression, widening trigger, or dirty-proof blocker is open.

Before marking the pipeline ready for audit, validate that the snapshot is present, parseable, for the
same feature/mode, has required fields/enums, has no duplicate or unreferenced dedupe keys, records
completed required lenses, and binds to the Stale-State Gate below. Fail closed if the snapshot is
missing, malformed, stale, contradictory, or for the wrong feature/mode/state.

## Stale-State Gate for Clean Readiness

Before a clean verdict can hand off to final audit readiness, revalidate that the current state still
matches the discovery reviewed state:

- Feature branch head.
- Base branch and base SHA/ref.
- Reviewed diff checksum or exact saved diff.
- Reviewed file list and status.
- Merge worktree metadata.

Reject stale, broadened, ambiguous, or missing state and instruct the user to rerun review. Clean
review-code output is not package proof and does not bypass accepted-proof or final-audit gates.

## Issues Handoff

If the verdict is **ISSUES FOUND**, load `pipeline-actions.md` before planning or performing any
pipeline fix, proof-impact handling, widening, escalation, or fix-verification handoff. Integration-
triggered package coverage invalidation, proof-impact concerns, or observed package-local serious
issues must be handed off as bounded affected-seam/package work, not default full-feature or
full-package rereview. Do not load fix implementer packets, dirty-proof handling, widening rules, or
escalation rules on the clean path.
