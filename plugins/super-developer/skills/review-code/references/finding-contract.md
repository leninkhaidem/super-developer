# Review Finding Contract

Load this reference before delegating the Code Reviewer or specialist reviewer. It is the canonical
shared contract for severity, finding fields, reviewer output, and suggestion actionability.

## Severity Taxonomy

Every finding must be classified — no exceptions:

| Severity | Label | Meaning |
|---|---|---|
| 🔴 | **BLOCKER** | Must be resolved before merge/commit. Correctness, security, privacy, safety, data-loss, or integrity risk. |
| 🟠 | **CRITICAL** | Strongly recommended fix. Significant quality, maintainability, operational, or regression risk. |
| 🟡 | **SUGGESTION** | Non-blocking improvement that is actionable, diff-relevant, and deduplicated. |

## Discovery Review Lenses and Coverage Output

Initial discovery review uses dynamic risk lenses instead of a fixed exhaustive checklist. The
orchestrator supplies required lenses from the active review mode, diff surface, task or package
context, package risk tags, changed files, baseline security/privacy/safety sniff, and known
risk signals. Reviewers must keep every required lens and may add reviewer-discovered lenses when
reading the diff reveals a new risk signal.

Each lens has a requested depth:

- `deep` — trace the relevant changed behavior through nearby callers, contracts, and verification
  evidence needed to support or reject findings in that risk domain.
- `sniff` — perform a bounded check for obvious risk in that domain, including the mandatory
  security/privacy/safety baseline sniff.
- `not_applicable` — use only when the reviewer can name why the lens does not intersect the diff,
  task context, or changed files.

Reviewer output must include `DISCOVERY_COVERAGE` before findings, with one compact row per
required lens and optional rows for reviewer-added lenses:

```markdown
DISCOVERY_COVERAGE:
| Lens | Required depth | Result | Evidence | Source |
|---|---|---|---|---|
| <lens id/name> | deep/sniff/not_applicable | deep/sniff/not_applicable | <concrete files, symbols, paths, contracts, or reason N/A applies> | required/reviewer-added |
```

Coverage rows are evidence, not findings. They must be concrete enough for the orchestrator to see
what was inspected: cite files, symbols, call paths, task/package evidence, or the specific reason a
lens is not applicable. Vague boilerplate such as `looks good`, `no issues found`, `covered`,
`seems fine`, or bare `N/A` is not valid coverage evidence. Missing or vague required-lens rows are
incomplete coverage, not a clean review. A clean discovery review still returns the coverage table,
followed by `NONE` when there are no reportable findings.

## Canonical Finding Fields

Each reviewer returns findings that can drive the report, decision cards, blanket-mode behavior, and
fix workflows without hidden fields later.

| Field | Requirement |
|---|---|
| `severity` | 🔴 BLOCKER, 🟠 CRITICAL, or 🟡 SUGGESTION. |
| `tags` | Domain tags such as `security`, `privacy`, `safety`, `data-integrity`, `migration`, `persistence`, `performance`, `public-api`, `architecture`, `cross-module`, `tests`, `docs`, or `task-awareness`. |
| `location` | File and line range when available; otherwise the smallest diff hunk, symbol, or module that supports the finding. |
| `title` | Short, specific summary. |
| `evidence` | Diff/code evidence sufficient for a reviewer to reproduce the concern. Serious findings require enough evidence for independent Skeptic verification. |
| `introduced_by_change` | `yes`, `no`, or `unclear`, with the reason. Findings not introduced by the reviewed change are disputed for 🔴/🟠 unless the mode explicitly asks for broader audit. |
| `task_awareness_signal` | `none`, `omission`, `contradiction`, or `regression`; include the referenced planned requirement or acceptance criterion when available. Audit remains authoritative for completeness. |
| `recommendation` | Concrete fix recommendation, or alternatives when materially different approaches exist. Alternatives must identify runtime behavior, blast radius, and public-surface tradeoffs. |
| `dedupe_key` | Stable key based on normalized root cause plus location/symbol, used across reviewers and big-diff batches. |
| `skeptic_verdict` | `not-required`, `confirmed`, `disputed`, or `downgraded`. Reviewers initialize this as `not-required`; the Skeptic updates 🔴/🟠 findings before reporting. |
| `suggestion_actionability` | For 🟡 only: explain why the suggestion is actionable, diff-relevant, and non-duplicative; otherwise do not report it. |
| `fix_status` | `unfixed`, `fix-proposed`, `fix-applied`, `verified`, `reopened`, or `not-applicable`. |

## Reviewer Output Format

```markdown
[SEV] FILE:LINE — TITLE
TAGS: <comma-separated tags>
EVIDENCE: <diff/code evidence; include repro reasoning for serious findings>
INTRODUCED_BY_CHANGE: <yes/no/unclear> — <reason>
TASK_AWARENESS: <none/omission/contradiction/regression> — <requirement or acceptance criterion if any>
RECOMMENDATION: <concrete fix, or alternatives with tradeoffs>
DEDUPE_KEY: <stable normalized key>
SKEPTIC_VERDICT: not-required
SUGGESTION_ACTIONABILITY: <required for 🟡, otherwise n/a>
FIX_STATUS: unfixed
```

If no findings, respond with exactly `NONE`. Do not append `NONE` after findings.

Reviewers must include `SKEPTIC_VERDICT: not-required` on initial output. The Skeptic is the only
actor that changes this field, setting it to `confirmed`, `disputed`, or `downgraded` for 🔴/🟠
findings during adversarial verification. This keeps the finding lifecycle explicit in the record
rather than relying on hidden orchestration state.

## Suggestion Actionability Rules

Suggestions are reportable only when all are true:

1. The recommendation is actionable and specific enough for a maintainer to implement.
2. The issue is relevant to the reviewed diff, not a pre-existing unrelated concern.
3. The suggestion is deduplicated by root cause and location/symbol.
4. The recommendation is grounded in repository conventions, caller contracts, or operational risk;
   it is not a style-only preference.

Non-actionable preferences, style-only opinions without repository grounding, duplicated comments,
and pre-existing unrelated issues are not reportable suggestions.
