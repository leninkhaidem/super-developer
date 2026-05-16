# Implement Sub-Agent Contract

Load this reference at implement Step 6 before spawning package or repair agents. The orchestrator remains authoritative for git infrastructure, status transitions, evidence acceptance, and pipeline continuation.

## Package Agent Inputs

Each package agent receives a self-contained assignment with:

- `.tasks/<feature>/SPEC.md`.
- `.tasks/<feature>/tasks.json`.
- Assigned `.tasks/<feature>/proofs/WP<N>.proof.json` path. The orchestrator creates the proof directory/template first when needed and handles artifact handoff because `.tasks/` is ignored by git.
- Assigned work package ID and task IDs.
- Structured acceptance criteria for those tasks, including stable criterion IDs and source refs.
- Required context bundle IDs and bundle content from `tasks.json`.
- Package `primary_paths` to inspect first.
- Package `verification_commands` that the orchestrator has classified as safe to run; unsafe commands require explicit user approval before delegation.
- Package `risk_tags`, targeted-review decision, and risk-class edge-case expectations.
- Assigned worktree path, e.g. `.worktrees/<feature>/wp-WP1/`.
- `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/clean-code-rules.md`.
- Project-level instructions such as CLAUDE.md or AGENTS.md when present.
- Resolved model preference, unless mode is `inherit`.

Do not pass ambient conversation history as hidden context. Agents work from files and the explicit assignment.

## Required Package Agent Behavior

The package agent must:

1. Work exclusively inside the assigned package worktree.
2. Locate its package and tasks in `tasks.json`.
3. Complete internal task dependencies in dependency order.
4. Start exploration with `primary_paths`, then broaden only when imports, tests, or acceptance criteria require it.
5. Read existing files relevant to the assigned package before editing.
6. Read and cite required context bundles; do not infer, mock, or invent external/library/runtime contract shapes defined by a bundle.
7. Follow the Development Quality Contract in `clean-code-rules.md`.
8. Preserve existing contracts unless the accepted plan explicitly changes them.
9. Update affected callsites, tests, docs, generated artifacts, schemas, and contracts within package scope.
10. Commit after completing each task ID so task-level progress is traceable within the package branch.
11. Run package `verification_commands` when safe/provided, plus tests/checks it adds or modifies and the cheapest relevant existing tests/checks for touched paths.
12. Never create worktrees, branches, or perform merge operations.

If a required command is unsafe under the command-safety rule, the agent must not run it. It reports the command and required approval instead.

## Package Proof Expectations

The package agent updates only its assigned `.tasks/<feature>/proofs/WP<N>.proof.json` with one entry per assigned acceptance criterion. Each entry must include:

- criterion ID and source refs;
- state binding: branch/commit/worktree or integrated state observed;
- files/symbols changed or inspected;
- command results or manual evidence with observed output/behavior;
- edge cases covered;
- mock disclosure and justification, if any;
- context-bundle citations when applicable;
- passing evidence for required package `verification_commands` when run in package or integration state;
- status that is not failed, blocked, stale, or manual-required without approval.

Use the generated `taskctl.py proof-template` shape. Proof entry `status` must be one of `verified`, `failed`, `blocked`, or `manual_required`; successful automated work uses `verified`, not `passed`. Proof entry `method` must be one of `unit_test`, `integration_test`, `e2e_test`, `table_driven_test`, `static_inspection`, `manual`, `command`, or `mixed`; do not use invented values such as `automated`.

For `unit_test`, `integration_test`, `e2e_test`, `table_driven_test`, `command`, or `mixed`, `evidence.commands` must contain at least one object with non-empty `cwd`, exact `command`, integer `exit_code` of `0`, and non-empty `observed`. File-only static inspection may use `method: "static_inspection"` with concrete `evidence.files`.

The proof file is the package evidence source. Vague, stale, untied, or missing evidence is rejection-worthy. Do not manually edit the proof `lifecycle` object; the orchestrator accepts or reopens package proofs with `taskctl.py` after integrated validation. The orchestrator records minimal root `targeted_review` evidence when targeted package review is required and passes.

`.tasks/` proof files are task-store artifacts, not package-branch source files. Do not `git add -f .tasks`, do not commit proof files, and do not rely on package branch merges to carry proofs. The orchestrator copies validated proof artifacts into the shared task store.

## Completion Report

The package agent report must include:

- completed task IDs;
- acceptance criteria verified;
- proof entries written/updated;
- Quality Contract Evidence from `clean-code-rules.md`;
- files changed;
- commands run and observed results;
- commits created per task ID;
- context bundles cited;
- mock disclosures;
- unresolved risks, blocked criteria, or scope-expansion requests.

Do not report success for a task whose acceptance criteria are not proven.

## Repair Agent Packet

When integration checkpoint, targeted package review, review-code, or audit rejects package work, the orchestrator delegates a fresh repair/verification agent rather than fixing inline. The repair packet must include:

- original SPEC and tasks files;
- package ID and affected task/criterion IDs;
- current integrated worktree path or package worktree path as appropriate;
- rejection report with exact failed criteria and why evidence was insufficient;
- package diff or relevant changed files;
- current package proof entries and lifecycle state;
- failed command output or observed bad behavior;
- required context bundles and citations expected;
- risk tags and edge-case checklist;
- safe verification commands to run after repair;
- the proof schema contract from `taskctl.py must-prove`;
- instruction to update only package proof entries and report new evidence;
- instruction not to force-add or commit ignored `.tasks` proof artifacts.

Repair scope is limited to making the assigned package criteria true and proven in the current integrated state. Design/product behavior changes, new dependencies/services, scope expansion, or unsafe commands still stop for user approval.
