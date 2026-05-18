# Implement Delegation Dispatch

Load this reference at implement Step 6 before spawning package or repair agents. This file is orchestrator-facing only: it defines what to put in delegated prompts and which role-specific contracts to pass. It intentionally does not repeat package-agent or repair-agent behavior.

## Context Boundary

The orchestrator MUST keep its context focused on plan state, git/worktree infrastructure, package selection, proof handoff, integration validation, targeted review, and pipeline continuation.

By default, the orchestrator MUST NOT load these sub-agent-facing references into main context:

- `plugins/super-developer/skills/implement/references/package-agent-contract.md`
- `plugins/super-developer/skills/implement/references/repair-agent-contract.md`
- `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/clean-code-rules.md`

Pass those paths to the assigned sub-agent and instruct the sub-agent to read the relevant contract. Load them in the orchestrator only when debugging or changing the plugin instructions themselves, or when a returned report is ambiguous and targeted contract inspection is needed.

Do not pass ambient conversation history as hidden context. Agents work from files and the explicit assignment.

## Package Agent Dispatch Packet

Each package-agent prompt must include:

- Role: package implementation agent.
- Required first read: `plugins/super-developer/skills/implement/references/package-agent-contract.md`.
- Required quality reference for the package agent to read: `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/clean-code-rules.md`.
- `.tasks/<feature>/SPEC.md`.
- `.tasks/<feature>/tasks.json`.
- Assigned `.tasks/<feature>/proofs/WP<N>.proof.json` path. The orchestrator creates the proof directory/template first when needed and handles artifact handoff because `.tasks/` is ignored by git.
- Assigned work package ID and task IDs.
- Structured acceptance criteria for those tasks, including stable criterion IDs and source refs.
- Required context bundle IDs and bundle content from `tasks.json`.
- Package `primary_paths` to inspect first.
- Package `verification_commands` that the orchestrator has classified as safe to run; unsafe commands require explicit user approval before delegation.
- Package `risk_tags`, targeted-review decision, and risk-class edge-case expectations.
- Output from `taskctl.py must-prove --package <WP-ID>` when available.
- Assigned worktree path, e.g. `.worktrees/<feature>/wp-WP1/`.
- Project-level instructions such as CLAUDE.md or AGENTS.md when present.
- Resolved model preference, unless mode is `inherit`.

The prompt must remind the package agent not to create worktrees, branches, or merges, and not to force-add or commit ignored `.tasks` proof artifacts.

## Repair Agent Dispatch Packet

Each repair-agent prompt must include:

- Role: package repair/verification agent.
- Required first read: `plugins/super-developer/skills/implement/references/repair-agent-contract.md`.
- Required quality reference for the repair agent to read when touching implementation or proof evidence: `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/clean-code-rules.md`.
- Original SPEC and tasks files.
- Package ID and affected task/criterion IDs.
- Current integrated worktree path or package worktree path as appropriate.
- Rejection report with exact failed criteria and why evidence was insufficient.
- Package diff or relevant changed files.
- Current package proof entries and lifecycle state.
- Review-code proof-impact map when the repair came from pipeline review-code, including affected or candidate package IDs, task/criterion IDs, proof entries, and any explicit no-impact evidence the orchestrator expects the repair to preserve or refresh.
- Failed command output or observed bad behavior.
- Required context bundles and citations expected.
- Risk tags and edge-case checklist.
- Safe verification commands to run after repair.
- The proof schema contract from `taskctl.py must-prove`.
- Instruction to update only package proof entries relevant to the repair or explicitly identified candidate proof refresh, and report new state-bound evidence.
- Instruction not to edit proof lifecycle state by hand, mark tasks done, treat review state as proof, or force-add/commit ignored `.tasks` proof artifacts.

Repair scope is limited to making the assigned package criteria true and proven in the current integrated state. Product/design changes, new dependencies/services, scope expansion, unsafe commands, credentials/external facts, or risk acceptance still stop for user approval.

## Orchestrator Edit Boundary

Direct orchestrator edits are limited to workflow metadata (`tasks.json`, package proof artifact handoff/validation/acceptance bookkeeping), mechanical merge-conflict/status artifacts, and explicit user-approved plan/status changes.

The orchestrator does not perform substantive production/test/documentation implementation or fixes inline. If package work is incomplete or rejected, delegate a fresh package or repair agent with the relevant packet above.
