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

Classify semantic impact rather than following dependency descendants. Re-check only affected checklist/proof/
report evidence plus focused seam closure and a fresh affected build/lint/test run; retain unaffected results.
Unknown or unbounded consumers/invariants widen conservatively. Rewrite each affected report for the repaired
state; the verifier remains separate from the implementer.

For one stabilized state, run or reuse the deduplicated minimum union only when code/artifact state, cwd,
environment/data, isolation/order assumptions, and evidence mapping are equivalent. Reuse authentic exact-state
output; distinct package, isolation, cleanup, or nondeterministic checks still run.
