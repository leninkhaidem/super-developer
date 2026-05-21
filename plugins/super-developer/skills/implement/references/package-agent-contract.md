# Package Agent Contract

Read this reference only inside a package implementation sub-agent session. You are not the orchestrator. The orchestrator owns git infrastructure, package selection, status transitions, evidence acceptance, merges, targeted-review routing, and pipeline continuation.

Your assignment packet provides the feature/task files, package ID, task IDs, acceptance criteria, context bundles, proof path, worktree path, safe verification commands, risk tags, and any project instructions. Work only from files and the explicit assignment; do not rely on ambient conversation history.

## Required Package Agent Behavior

Treat assigned acceptance criteria as minimum proof obligations, not as the maximum useful implementation. "Go the extra mile" means depth and completeness inside the assigned package boundary: solve the behavior/risk class implied by the package, cover relevant security, privacy, reliability, edge-case, and failure-mode concerns, and update affected artifacts. It does not permit speculative features, unrelated cleanup, broad refactors, new dependencies/services, or product/design changes without approval.

The package agent must:

1. Work exclusively inside the assigned package worktree.
2. Locate its package and tasks in `tasks.json`.
3. Read `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/clean-code-rules.md` before substantive implementation and follow its Development Quality Contract.
4. Complete internal task dependencies in dependency order.
5. Start exploration with `primary_paths`, then broaden only when imports, tests, or acceptance criteria require it.
6. Read existing files relevant to the assigned package before editing.
7. Read and cite required context bundles; do not infer, mock, or invent external/library/runtime contract shapes defined by a bundle.
8. Before substantive edits for non-trivial package work, form a compact implementation strategy and reflect it in completion evidence. The strategy must identify the caller contract and failure/partial/invalid-input behavior, trust boundaries and security/privacy/data/performance/concurrency implications, applicable risk tags and known-risk probes, affected artifacts, the natural implementation seam/methodology, and verification mapped to acceptance criteria plus relevant edge/failure cases.
9. Implement the complete in-scope behavior/risk class implied by the assigned criteria, risk tags, context bundles, and existing contracts; do not patch only the literal happy path or example input when adjacent in-scope states should share the same invariant.
10. Preserve existing contracts unless the accepted plan explicitly changes them.
11. Update affected callsites, tests, docs, generated artifacts, schemas, and contracts within package scope.
12. Stop and report when the correct implementation requires scope expansion, a product/design decision, new dependency/service, unsafe command, credentials/external facts, or changes outside the package boundary.
13. Commit after completing each task ID so task-level progress is traceable within the package branch.
14. Run package `verification_commands` when safe/provided, plus tests/checks it adds or modifies and the cheapest relevant existing tests/checks for touched paths. Prefer targeted checks that prove assigned criteria and touched behavior; do not run broad expensive suites by default unless they are assigned, cheap by project convention, or the only credible proof for the package's risk surface.
15. Before handoff, perform the mandatory package self-review below and fix self-found issues or report an exact blocker.
16. Never create worktrees, branches, or perform merge operations.

If a required command is unsafe under the command-safety rule, do not run it. Report the command and required approval instead.

## Package Self-Review

Before returning, review your own package diff in behavior-first order:

1. Re-read the assigned acceptance criteria, risk tags, context bundles, and proof obligations.
2. Review the core/runtime behavior you changed before reviewing tests.
3. Derive which tests, commands, static inspections, or manual observations should prove the behavior and risk cases.
4. Review corresponding tests/proofs as evidence quality: assertions, negative/failure/security/privacy/data/concurrency cases, mocks, skips, generated snapshots/contracts, and pollution-sensitive setup.
5. Review remaining test-only/generated/config/docs changes only as needed for package scope and risk.

If self-review finds an issue, fix it before handoff and rerun the relevant targeted checks, or report the exact blocker when the fix requires scope expansion, unsafe commands, external facts, credentials, or a product/design decision. Self-review is a compact report block, not a new proof artifact or schema field.

Include this exact block in the completion report:

```text
SELF_REVIEW
diff_reviewed: yes
criteria_checked: <AC IDs>
risk_lenses_checked: <risk tags/lenses or none-applicable>
tests_reviewed_as_evidence: <test files/commands or none>
issues_found_and_fixed: <short list or none>
tests_and_proofs_consistent: yes/no + reason
unresolved_concerns: none or exact blocker
```

## Package Proof Expectations

Update only the assigned `.tasks/<feature>/proofs/WP<N>.proof.json` with one entry per assigned acceptance criterion. Each entry must include:

- criterion ID and source refs;
- state binding: branch/commit/worktree or integrated state observed;
- files/symbols changed or inspected;
- command results or manual evidence with observed output/behavior;
- edge cases covered in `evidence.edge_cases`, including behavior/risk class coverage for relevant negative, failure, default/omission, security/privacy/trust-boundary, data-integrity, concurrency, and performance cases, or a concrete reason they are not applicable;
- mock disclosure and justification, if any;
- context-bundle citations when applicable;
- passing evidence for required package `verification_commands` when run in package or integration state;
- status that is not failed, blocked, stale, or manual-required without approval.

Use the generated `taskctl.py proof-template` shape. Proof entry `status` must be one of `verified`, `failed`, `blocked`, or `manual_required`; successful automated work uses `verified`, not `passed`. Proof entry `method` must be one of `unit_test`, `integration_test`, `e2e_test`, `table_driven_test`, `static_inspection`, `manual`, `command`, or `mixed`; do not use invented values such as `automated`.

For `unit_test`, `integration_test`, `e2e_test`, `table_driven_test`, `command`, or `mixed`, `evidence.commands` must contain at least one object with non-empty `cwd`, exact `command`, integer `exit_code` of `0`, and non-empty `observed`. File-only static inspection may use `method: "static_inspection"` with concrete `evidence.files`.

The proof file is the package evidence source. Vague, stale, untied, or missing evidence is rejection-worthy. Do not manually edit the proof `lifecycle` object; the orchestrator accepts or reopens package proofs with `taskctl.py` after integrated validation. The orchestrator records minimal root `targeted_review` evidence only after the mandatory targeted package review passes and any required repairs or delta verification close.

`.tasks/` proof files are task-store artifacts, not package-branch source files. Do not `git add -f .tasks`, do not commit proof files, and do not rely on package branch merges to carry proofs. The orchestrator copies validated proof artifacts into the shared task store.

## Completion Report

The package agent report must include:

- completed task IDs;
- acceptance criteria verified;
- proof entries written/updated;
- Quality Contract Evidence from `clean-code-rules.md`;
- depth-within-scope strategy and behavior/risk class coverage, including any applicable security, privacy, failure-mode, edge-case, or methodology decisions;
- files changed;
- commands run and concise observed results or relevant excerpts; also list safe targeted commands that were not run and why;
- commits created per task ID;
- context bundles cited;
- mock disclosures;
- the required `SELF_REVIEW` block;
- unresolved risks, blocked criteria, or scope-expansion requests.

Do not report success for a task whose acceptance criteria are not proven.
