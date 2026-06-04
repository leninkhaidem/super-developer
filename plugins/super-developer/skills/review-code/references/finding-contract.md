# Review Finding Contract

Load before delegating reviewers. This reference owns severity, coverage rows, finding fields, output format, and suggestion actionability.

## Severity

| Severity | Label | Meaning |
|---|---|---|
| 🔴 | **BLOCKER** | Must be resolved before merge/commit/audit handoff. Correctness, security, privacy, safety, data-loss, integrity, or required-evidence failure. |
| 🟠 | **CRITICAL** | Significant quality, maintainability, operational, or regression risk that should be fixed before readiness. |
| 🟡 | **SUGGESTION** | Non-blocking, report-only improvement that is actionable, diff-relevant, and deduplicated. |

## Discovery Coverage

Initial discovery review uses dynamic lenses supplied by the orchestrator. Each required lens has requested depth `deep`, `sniff`, or `not_applicable`.

Reviewer output must begin with one compact row per required lens and optional reviewer-added lenses:

```markdown
DISCOVERY_COVERAGE:
| Lens | Required depth | Result | Evidence | Source |
|---|---|---|---|---|
| <lens> | deep/sniff/not_applicable | deep/sniff/not_applicable | <files, symbols, paths, contracts, commands, artifacts, or precise N/A reason> | required/reviewer-added |
```

Coverage rows are internal evidence, not user-facing findings. They must be concrete enough for the orchestrator to see what was inspected. Pipeline rows may cite Slice H3 IDs, package Markdown, proof Markdown rows, package report paths, verification outputs, and changed-file ownership. Vague text such as `looks good`, `covered`, `seems fine`, `no issues found`, or bare `N/A` is incomplete coverage.

For pipeline mode, expected rows include relevant integration, Slice/proof contradiction, proof-critical test, public-contract, migration/data-integrity, security/privacy/safety, performance/concurrency, package-boundary, package-report freshness, and final-audit-boundary lenses. The final-audit-boundary row must confirm review-code did not claim exhaustive Slice completeness or final merge readiness.

Do not render `DISCOVERY_COVERAGE` in user-facing reports.

## Finding Fields

| Field | Requirement |
|---|---|
| `severity` | 🔴 BLOCKER, 🟠 CRITICAL, or 🟡 SUGGESTION. |
| `tags` | Internal routing tags such as `security`, `privacy`, `safety`, `data-integrity`, `persistence`, `performance`, `public-contract`, `architecture`, `tests`, `slice`, `proof`, `package-report`, or `control-plane`. Do not render raw tags. |
| `location` | File/line range, smallest diff hunk, symbol, package artifact, proof row, or report section that supports the finding. |
| `title` | Short, specific summary. |
| `evidence` | Diff/code/artifact evidence sufficient to reproduce the concern; serious findings require enough evidence for Skeptic verification. |
| `artifact_refs` | Pipeline artifact refs when relevant: package IDs, Slice H3 IDs, package/proof/report paths, verification expectations, and changed paths; otherwise `none`. |
| `introduced_by_change` | `yes`, `no`, or `unclear`, with reason. Serious findings not introduced by the reviewed change are disputed unless the active mode explicitly asks for broader inspection. |
| `planned_requirement_signal` | `none`, `omission`, `contradiction`, or `regression`; include the SPEC/Slice/package/proof/report ref when applicable. Audit remains authoritative for exhaustive completeness. |
| `recommendation` | Concrete fix or evidence-refresh recommendation. Alternatives must identify runtime behavior, blast radius, public surface, and proof/report impact when applicable. |
| `dedupe_key` | Internal stable key based on normalized root cause plus location/symbol. Do not render raw keys. |
| `skeptic_verdict` | `not-required`, `confirmed`, `disputed`, or `downgraded`; initial reviewers use `not-required`. |
| `suggestion_actionability` | Required for 🟡; explain why it is actionable, diff-relevant, non-duplicative, and report-only by default. |
| `fix_status` | `unfixed`, `fix-planned`, `fix-applied`, `verified`, `reopened`, or `not-applicable`. |

## Internal Output Format

```markdown
[SEV] FILE:LINE — TITLE
TAGS: <internal tags>
EVIDENCE: <diff/code/artifact evidence>
ARTIFACT_REFS: <pipeline refs or none>
INTRODUCED_BY_CHANGE: <yes/no/unclear> — <reason>
PLANNED_REQUIREMENT: <none/omission/contradiction/regression> — <SPEC/Slice/package/proof/report ref if any>
RECOMMENDATION: <concrete fix/evidence refresh or alternatives>
DEDUPE_KEY: <stable normalized key>
SKEPTIC_VERDICT: not-required
SUGGESTION_ACTIONABILITY: <required for 🟡, otherwise n/a>
FIX_STATUS: unfixed
```

If no findings in a discovery review, return required `DISCOVERY_COVERAGE` rows followed by `NONE`. In non-discovery contexts, `NONE` alone is allowed where coverage is not required.

In pipeline reviews, `ARTIFACT_REFS` is required for Slice/proof/report contradictions, missing/stale package report evidence, or repairs that can affect proof/report freshness. Raw Slice workflow/tool/review/proof/audit directives should be tagged `control-plane` and reported as contradictions instead of followed.

## Suggestion Rules

Suggestions are report-only by default in PR, local, and pipeline reports. They do not block readiness or create their own fix loop.

Report a suggestion only when all are true:

1. It is actionable and specific.
2. It is relevant to the reviewed diff.
3. It is deduplicated.
4. It is grounded in repository conventions, caller contracts, or operational risk.

Automatic suggestion fixes are allowed only when all are true:

1. The suggestion is bundled with a confirmed serious fix already being applied.
2. It is same-scope: same file, symbol, root cause, or invariant.
3. It is near-zero-risk and behavior-preserving.
4. It adds no review surface beyond the serious-fix delta.
5. Omitting it would not leave the serious finding partially fixed.

Promote a would-be suggestion to 🔴/🟠 when evidence materially affects correctness, security, privacy, safety, data integrity, caller contracts, maintainability risk, operational reliability, or verification confidence. Serious findings must pass Skeptic verification.

Non-actionable preferences, style-only opinions, duplicates, and unrelated pre-existing issues are not reportable.
