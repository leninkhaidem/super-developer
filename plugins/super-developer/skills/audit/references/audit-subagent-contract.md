# Audit Sub-Agent Contract

Load this reference only after `audit/SKILL.md` passes the orchestrator readiness gate and is about
to spawn the audit sub-agent. It owns the sub-agent packet, verification procedure, report format,
and PASS/FAIL result contract. The main audit skill owns validator use, review-code audit-readiness,
and non-bypass proof gates.

The sub-agent works read-only from files and receives no conversation history. It must verify the
final integrated state, not package-local assumptions or review summaries.

## Required First Reads

1. `.tasks/<feature>/SPEC.md`
2. `.tasks/<feature>/tasks.json`
3. Every `.tasks/<feature>/proofs/WP<N>.proof.json`
4. `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/clean-code-rules.md`

Package proof lifecycle details are canonical in
`skills/implement/references/package-proof-lifecycle.md`; audit keeps this local invariant: accepted,
fresh package proof evidence is required for every planned-feature audit, including standalone audits
against `.tasks/<feature>/`. Review-code state snapshots, targeted reviews, and self-review summaries
are context only and cannot substitute for accepted package proofs.

## Verification Procedure

Verify every listed requirement and feature-level acceptance criterion against the current codebase
and final integrated state:

- User-visible behavior exists and matches the requirement.
- Constraints are respected.
- Programmatic checks are run when safe and relevant under the command-safety rules from the plan and
  Execution Contract.
- Non-programmatic criteria require durable user-approved manual evidence in the relevant package
  proof; otherwise fail.
- SPEC requirements or ACs not covered by task criteria are reported as `[GAP]`, even if task-level
  criteria pass.
- Every task AC has a package proof entry tied to its criterion ID and source refs.

For every task marked `done` in `tasks.json`:

### Task Acceptance Criteria

- Confirm referenced files, functions, endpoints, commands, behavior, edge cases, and context bundles
  exist and behave as the criterion/evidence claims.
- If testable, run the relevant safe test or command.
- Fail on missing, malformed, stale, failed, blocked, reopened/unaccepted, or unapproved
  `manual_required` proof evidence.
- If a criterion cannot be verified programmatically and lacks complete user-approved manual
  evidence, report `[ISSUE]` and fail.

### Development Quality Contract

Use `clean-code-rules.md` as the governing contract:

- **BLOCKER** for MUST-level violations, missing required verification, fake success states,
  caller-contract failures, unsafe trust boundaries, security/privacy/safety/data-integrity risk,
  incompatible API/contract changes, or unresolved acceptance criteria.
- **CODE-QUALITY** for unjustified SHOULD-level maintainability violations, unclear boundaries,
  harmful duplication, unnecessary coupling, complexity, or spreading legacy-bad patterns.
- **ADVISORY** only for optional, actionable, non-blocking improvements grounded in the diff and local
  conventions.

Do not rely only on legacy file/function-size heuristics. Check discovery, design, implementation,
testing/verification, completion evidence, and audit/review enforcement gates. Non-trivial work must
include compact Quality Contract Evidence or equivalent evidence: inspection outcome, boundary/design
choice, behavior/risk class, affected artifacts, verification run, and rule exceptions. Cite file,
line, severity, and violated clause for each finding.

### Package Proof Check

Missing or non-accepted package proof evidence is a `[PROOF]` failure. For each completed task AC,
confirm the package proof entry has the correct criterion ID, task ID, package ID, source refs,
context bundles, state/commit/worktree, file/symbol or command evidence, observed result,
edge/failure/default/security/privacy/trust-boundary/data-integrity/concurrency/performance/lifecycle
coverage or explicit non-applicability, and mock disclosure.

Fail stale evidence when cited files, symbols, commands, or outputs changed after recorded proof
state. `manual_required` passes only with durable manual evidence including criterion IDs, approval
provenance or supplied artifact, observed result, scope, limits, approval date, and state reference;
a bare approval boolean is never enough.

### Completeness and Integration

- Cross-reference SPEC.md against implementation; report uncovered requirements as `[GAP]`.
- Report skipped or blocked tasks with reasons.
- Search for introduced TODO/FIXME/HACK markers that imply incomplete work.
- Check integration sanity: components connect, imports/references resolve, and safe relevant tests
  pass when available.

## Audit Report

```markdown
## Audit Report: <feature-name>

### Summary
- Tasks completed: X/Y
- Tasks skipped: N (with reasons)
- Tasks blocked: N (with reasons)
- SPEC requirements/acceptance criteria: X/Y verified, N failed, N approved manual
- Task acceptance criteria: X/Y verified, N failed, N approved manual

### Issues Found
1. [BLOCKER] <description> — violated requirement/criterion/contract clause
2. [CODE-QUALITY] <description> — maintainability contract clause
3. [ADVISORY] <description> — optional improvement
4. [SPEC] <description> — SPEC item <REQ/AC ID>
5. [ISSUE] <description> — task <ID>, criterion <N>
6. [GAP] <description> — requirement from SPEC.md not covered
7. [TODO] <file:line> — incomplete work marker found
8. [PROOF] <description> — package proof missing, malformed, stale, unaccepted/reopened, blocked/failed, or unapproved manual evidence

### Passed
- [list of tasks that fully passed verification]

### Verdict
PASS — All tasks completed and verified in the final state, with no [BLOCKER], [CODE-QUALITY], [SPEC], [ISSUE], [GAP], [TODO], or [PROOF] findings. [ADVISORY] findings may be listed without blocking completion.
or
FAIL — Any [BLOCKER], [CODE-QUALITY], [SPEC], [ISSUE], [GAP], [TODO], or [PROOF] finding requires attention before the feature is considered complete. Manual-required criteria are failures unless durable user-approved manual evidence is present and scoped to the criterion.
```
