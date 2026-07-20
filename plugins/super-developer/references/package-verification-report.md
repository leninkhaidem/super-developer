# Package Verification Report Contract

Boundary: the shared shape of the durable package verification report, consumed by package verifiers, the
package-completion helper, and final audit. Reports live under the artifact root. Verifiers and auditors own
semantic truthfulness; this contract only fixes the lightweight structure.

## The report is a lightweight result

A report records that a package was verified against its **frozen `## Acceptance Checklist`** (in the package
Markdown) and passed with authentic evidence. It is not a deliverable-completeness matrix, a test-review
receipt, or a digest state-binding block — those are removed. Keep it short.

Canonical path: `.tasks/<feature>/reports/<WP-ID>.package-verification.md`.

```md
## Package Verification: <WP-ID>

### Verdict
PASS | FAIL

## Acceptance Checklist Result
| Item | Result | Evidence |
|---|---|---|
| `AC-1` | pass | `test:path::test_name` (or command + observed result) |
| `AC-2` | pass | manual (approved): observed <result> |

## Blocking findings
- none

## Advisory notes
- <non-blocking observation>, or none

## Reviewed state
- Worktree/ref/commit of the code verified: `<worktree>` `<ref>` `<commit>`
```

## Rules

- **PASS** requires every Acceptance Checklist item marked `pass` with a resolvable evidence pointer and no open
  blocking finding. Any `fail` item or open blocking finding is **FAIL**.
- **Severity bar:** only correctness / security / data-loss / contract-break go under `## Blocking findings`.
  Everything else is an `## Advisory note` — it never changes the verdict.
- **Evidence authenticity:** an evidence pointer must resolve to real output (a test id + result, a command +
  observed result, or a `manual (approved)` observation). Fabricated, skipped-without-approval, or hollow
  evidence makes the item `fail`.
- **Executable-by-default:** a `manual` result is acceptable only for an item the plan froze as a human-approved
  `manual (approved)` exception at the plan gate.
- Mechanical `sliceproof.py` output is advisory diagnostics, never a reason to FAIL a package whose checklist
  passes. Note shape issues under Advisory; do not loop on paperwork.

## Re-verification after repair

Re-check only the checklist items whose evidence the repair diff touched, plus a fresh build/lint/test run, and
rewrite this report for the repaired state. A repair does not invalidate items its diff did not touch.
