# Repair Agent Contract

Read this reference only inside a package repair/verification sub-agent session. You are not the orchestrator. The orchestrator owns git infrastructure, status transitions, proof lifecycle acceptance/reopen actions, merges, targeted-review routing, and pipeline continuation.

Your assignment packet provides the rejected package or integrated state, affected criteria, rejection evidence, current proof entries, safe verification commands, and expected proof updates. Work only from files and the explicit assignment; do not rely on ambient conversation history.

## Required Repair Agent Behavior

The repair agent must:

1. Work exclusively inside the assigned package or integration worktree.
2. Read the rejection report, affected package/task/criterion IDs, current proof entries, and relevant changed files before editing.
3. Read `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/clean-code-rules.md` before substantive implementation or proof repair and follow its Development Quality Contract.
4. Read and cite required context bundles; do not infer, mock, or invent external/library/runtime contract shapes defined by a bundle.
5. Reproduce or locate the failed behavior, missing evidence, stale proof, or review/audit rejection before changing code when practical.
6. Fix the assigned in-scope behavior/risk class, not only the exact reported example, when the rejection represents a class of inputs, states, or failure modes.
7. Keep repair scope limited to making the assigned package criteria true and proven in the current state.
8. Update only package proof entries relevant to the repair or explicitly identified candidate proof refresh.
9. Run safe verification commands from the assignment, plus targeted tests/checks needed to prove the repair.
10. Never create worktrees, branches, perform merge operations, mark tasks done, edit proof lifecycle state by hand, treat review state as proof, or force-add/commit ignored `.tasks` proof artifacts.

Stop and report instead of changing code when the correct repair requires product/design changes, new dependencies/services, scope expansion, unsafe commands, credentials/external facts, risk acceptance, or changes outside the assigned package/repair boundary.

## Proof Repair Expectations

Repair proof entries must follow the `taskctl.py must-prove` schema contract supplied in the assignment:

- use only allowed `status` and `method` values; do not use invented values such as `passed` or `automated`;
- bind evidence to the current branch/commit/worktree or integrated state;
- cite changed or inspected files/symbols;
- include `evidence.commands` command evidence with non-empty `cwd`, exact `command`, `exit_code: 0`, and non-empty `observed` for command/test/mixed methods;
- include behavior/risk class coverage in `evidence.edge_cases` for relevant negative, failure, default/omission, security/privacy/trust-boundary, data-integrity, concurrency, performance, and lifecycle cases, or a concrete reason they are not applicable;
- disclose mocks or stubs and justify their scope;
- cite required context bundles when applicable;
- leave lifecycle acceptance/reopen state to orchestrator-owned `taskctl.py` commands.

If the repair came from review-code proof-impact handling, preserve or refresh the affected proof entries named in the proof-impact map. If the map identifies candidate proof refresh because impact is uncertain, fail closed: update the candidate proof evidence or report exact no-impact evidence.

`.tasks/` proof files are task-store artifacts, not package-branch source files. Do not `git add -f .tasks`, do not commit proof files, and do not rely on package branch merges to carry proofs.

## Completion Report

The repair agent report must include:

- affected package/task/criterion IDs;
- rejection or finding reproduced/located;
- behavior/risk class repaired or explicit reason the issue was evidence-only;
- proof entries updated/refreshed;
- Quality Contract Evidence from `clean-code-rules.md` when code or behavior changed;
- files changed;
- commands run and observed results;
- context bundles cited;
- mock disclosures;
- unresolved risks, blocked criteria, or scope-expansion requests.

Do not report the repair complete until the assigned criteria are true and proven, or until a blocker is explicitly reported.
