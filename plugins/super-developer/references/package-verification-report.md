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
PASS | FAIL | PENDING_VERIFICATION

## Acceptance Checklist Result
| Item | Result | Evidence |
|---|---|---|
| `AC-1` | pass | pointer: `test:path::test_name` — observed: exit 0; bounded output |
| `AC-2` | pass | pointer: manual (approved) — observed: <result> |

## Blocking findings
- none

## Advisory notes
- <non-blocking observation>, or none

## Plan gaps
- none

## Reviewed state
- Worktree/ref/commit of the code verified: `<worktree>` `<ref>` `<commit>`

## Gaps
- none
```

## Rules

- **PASS** requires every Acceptance Checklist item marked `pass` with a pointer plus orchestrator-observed
  output (exit/status and bounded output) and no open blocking finding. Missing, skipped, or failed observed
  output is automatic FAIL. Any `fail` item or open blocking finding is **FAIL**.
- **PENDING_VERIFICATION** is the drafting-stage value only: the package agent finished implementing and the
  orchestrator has not yet re-run the frozen checklist. It states an honest unverified position instead of
  claiming a verdict no one observed. The helper treats it as not complete, and it never satisfies a completion
  gate; the orchestrator replaces it with `PASS` or `FAIL` from its own re-run.
- **Severity bar:** only correctness / security / data-loss / contract-break go under `## Blocking findings`.
  Everything else is an `## Advisory note` — it never changes the verdict.
- **Warrant:** every blocking finding carries `warrant: AC-<id>`, `warrant: regression:<ref>`, or
  `warrant: override:<class>`. An unwarranted finding is not blocking: it becomes an advisory note, or a
  `## Plan gaps` entry (`warrant: plan-gap`) when it names a real obligation the frozen checklist omits.
  A plan gap never changes the verdict and never starts a code repair loop, but it is a plan defect, not an
  advisory: while it stays open `validate-package-complete` and `validate-final` fail, the package does not become
  `done`, and dependents do not unlock. The orchestrator routes it to planning continuation, so a missing
  requirement is neither forced in by a verifier nor lost.
- **Closing a plan gap never means deleting it.** Every real entry starts at column zero with exact
  `- warrant: plan-gap`, occupies a single physical line, and carries its disposition on that same physical line.
  The two dispositions remain a substantive `closed:` note or durable out-of-scope approval with non-placeholder
  approval, provenance, and scope. Blank separator lines and trailing whitespace are allowed. Leading indentation,
  wrapping, nesting, alternate markers, comments, fences, prose, malformed warrants, and mixed `- none` are not.
  The empty disposition is sole exact lowercase `- none`. Enforcement is immediate for new runs, with no
  compatibility path, fallback, migration, adapter, flag, or hidden mode. The helper validates this mechanical
  shape and disposition presence only; verifiers and auditors retain semantic truthfulness and sufficiency judgment.
- **Evidence authenticity:** a pointer plus observed output must resolve to real output (a test id + result, a
  command + observed result, or a `manual (approved)` observation). A PASS row with a hollow non-path claim is
  not a semantic done signal. The helper only checks presence, non-placeholder, and safe path existence when the
  pointer looks like a path.
- **Executable-by-default:** a `manual` result is acceptable only for an item the plan froze as a human-approved
  `manual (approved)` exception at the plan gate. The orchestrator does not re-run manual items.
- **Gaps** must be `none` or carry approval, provenance, and scope. The helper checks that metadata presence only.
- **`## Plan gaps` is required and uses only the flat grammar above.** Finding nothing is the sole exact written
  claim `- none`, never an omission. Every other nonblank physical line must be a canonical real entry; the helper
  does not interpret Markdown ownership or silently discard unknown content. Copy the template above and the section
  is already valid.
- Mechanical `sliceproof.py` output is structural fail-closed, never semantic authenticity. Helper ok alone is
  not done.

## Re-verification after repair

Classify semantic impact rather than following dependency descendants. Re-check only affected package-local
checklist/result evidence plus fresh-for-the-stabilized-state affected build/lint/test evidence; retain
unaffected results. Focused seam closure remains exclusively with final `review-code` Fix Verification. Unknown or
unbounded consumers/invariants widen conservatively. Rewrite each affected report for the repaired state; the
verifier remains separate from the implementer.

For one stabilized state, run or reuse the deduplicated minimum union only when code/artifact state, cwd,
environment/data, isolation/order assumptions, and evidence mapping are equivalent. Fresh-for-that-state evidence
may use authentic exact-state reused output; distinct package, isolation, cleanup, or nondeterministic checks still
run.
