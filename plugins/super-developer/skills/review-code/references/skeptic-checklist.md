# Skeptic Verification Checklist

Load only when serious findings, risky clean coverage, cross-batch conflicts, or mode gates require Skeptic verification. The Skeptic receives serious findings, reviewed-state metadata, available planned-feature context, and any targeted coverage rows being challenged.

## Mandate

Disprove findings. Independently locate supporting or refuting evidence in the diff/codebase/artifacts. In coverage-challenge mode, challenge only named clean claims or weak coverage rows; do not become a second full reviewer by default.

## Verdicts

- **CONFIRMED** — Evidence independently reproduced; finding remains reportable.
- **DISPUTED** — Evidence not found or finding is outside reviewed scope; exclude from final report.
- **DOWNGRADED** — Serious severity not justified, but an actionable diff-relevant suggestion remains.

Only confirmed 🔴/🟠 findings are reportable as serious. Disputed findings are excluded. Downgraded findings may be reported only as 🟡 suggestions when still actionable, diff-relevant, and deduplicated.

## Coverage Challenge Mode

Use only when the orchestrator names a specific weak lens row, risky clean claim, unsupported `not_applicable`, or coverage shallower than requested.

```markdown
Coverage lens: <lens id/name>
Required depth: <deep/sniff/not_applicable>
Challenged evidence: <row or NO_FINDING claim>
Verdict: COVERAGE_ACCEPTED / COVERAGE_INCOMPLETE / SERIOUS_FINDING_CANDIDATE
Evidence: <independent evidence or missing evidence>
Required follow-up: <none, focused reviewer follow-up, or serious-finding verification>
Reason: <one sentence>
```

`COVERAGE_INCOMPLETE` blocks a clean result until focused follow-up supplies concrete evidence. `SERIOUS_FINDING_CANDIDATE` must become a canonical 🔴/🟠 finding and pass serious-finding verification before reporting.

## False-Positive Checklist

Run every item before confirming any 🔴/🟠 finding.

1. **Scope mismatch** — Was this introduced by the reviewed change? If not, dispute unless the mode explicitly requested broader risk discovery.
2. **Context blindness** — Does surrounding code, caller chain, or existing middleware/adapter already handle it? If yes, dispute.
3. **Framework/library absorption** — Does the framework, ORM, runtime, or middleware already enforce the missing property? If yes, dispute.
4. **Dead or unreachable path** — Is the path unreachable in real execution? If unreachable, downgrade only when a useful suggestion remains; otherwise dispute.
5. **Intentional documented behavior** — Is it a deliberate documented choice in PR text, commits, repo docs, SPEC, package Markdown, proof Markdown, package reports, or audit results? Dispute non-sensitive issues when documented; real security/privacy/safety risks remain confirmable.
6. **Test-scope confusion** — Does it apply only to tests/fixtures/mocks/seed data? Dispute serious severity unless test behavior masks a real production regression.
7. **Planned-feature overclaim** — Does it claim a requirement omission, contradiction, or regression without SPEC/Slice/package/proof/report evidence? Remove the planned-feature signal or dispute. Audit is the completeness gate.

## Output

```markdown
Finding: <original finding summary>
Dedupe key: <dedupe_key>
Checklist run: 1 2 3 4 5 6 7
Failed check: <checklist item that caused dispute, or NONE>
Verdict: CONFIRMED / DISPUTED / DOWNGRADED
Evidence: <independent evidence or absence of evidence>
Reason: <one sentence>
```
