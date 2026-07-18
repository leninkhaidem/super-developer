---
name: spike-to-plan
description: >
  Runs a bounded feasibility spike and hands observed evidence to implementation-plan. Use when planning depends
  on unresolved empirical API, integration, performance, concurrency, data, or UX behavior. Do not use for
  routine implementation or code review.
---

# Spike to Plan

Answer the smallest empirical question needed for a reliable Slice-first planned-feature plan, discard
exploratory code, and return observed evidence without turning the spike into implementation.

## Always

- Treat spike code and temporary harnesses as disposable evidence, not production implementation.
- Prefer repository, documentation, and official API evidence before exploratory code or commands.
- Keep work isolated, bounded, reversible, and focused on one material planning assumption.
- Preserve user work; never stash, reset, overwrite, or discard dirty changes without approval.
- Apply the shared command runtime envelope to every command: identity, provenance, scope, timeout, progress,
  completion, owned-process termination, cleanup, and outcome.
- When a probe uses project tests, harnesses, live/browser services, or shared data, require testing authority:
  accepted/current workflow for high-risk/reusable work, routine-safe fallback for a bounded local command, or
  task-local Testing Authorization for exact focused approval. If insufficient, invoke `testing` or stop.
- Timeout, uncertain termination, or uncertain cleanup is inconclusive evidence, never a successful observation.
- Do not persist exploratory code as planned-feature artifacts. Persist accepted planning outcomes later through
  normal specification, package, Slice approval/deferral, or registry ownership.
- When called by a planned-feature Delivery Owner, load `../../references/orchestration-convergence.md`, preserve
  caller/return state, and return evidence; never start planning, review, or implementation on the caller's behalf.

## Do

1. State one planning assumption, the decision it blocks, success/failure evidence, constraints, and non-goals.
2. Inspect existing code, tests, repository docs, and authoritative library/API docs before probing.
3. Stop the spike when static evidence resolves the assumption; report that evidence directly.
4. Before any command, load `../../references/tool-usage.md`. If project testing/harness policy applies, resolve
   testing authority. Missing workflow alone does not block read-only/static evidence or a routine-safe probe. If
   authority is missing, stale, conflicting, or insufficient, invoke `testing` and stop command execution.
5. Select an isolated temporary branch/worktree for code, service, shared-data, or multi-command probes. Use the
   current tree only for a small read-only or low-risk probe with clean or explicitly approved state.
6. Define the probe contract: command identity/provenance, cwd/scope, expected writes and signal, explicit timeout,
   progress/completion, termination/cleanup, approval state, and the smallest credible bounded evidence path.
   If no narrower probe can answer the assumption, document why before an explicitly bounded broad-only probe.
7. Run one bounded stage at a time and return control after failure. Do not repeat an unchanged command, enlarge a
   timeout to mask missing progress, or hide iterative follow-ups inside one opaque command/tool call.
8. Record observed results and failed/rejected approaches. Distinguish passed observation, rejected assumption,
   blocked precondition, unsafe-needs-approval, and inconclusive/cleanup-uncertain outcomes.
9. Delete throwaway code, harnesses, branches, and worktrees after extracting evidence. Verify owned-process and
   data cleanup; stop with the exact residual state when cleanup fails or is uncertain.
10. Return a concise spike brief with its caller/return disposition. For a nested call, return it to the Delivery
    Owner for amendment routing. For a standalone planning request, hand it to a fresh `implementation-plan`
    invocation. Do not draft planned-feature artifacts inline or treat exploratory code as implementation.

## Load if needed

- Command safety, bounds, termination, or cleanup → `../../references/tool-usage.md`
- Official library/API evidence → only when repository evidence does not resolve the assumption
- Project test/harness/live/browser authority is missing or stale → invoke `testing`
- Temporary branch/worktree isolation → invoke `worktree`
- Nested caller/return or continuation semantics → `../../references/orchestration-convergence.md`
- Durable feature artifacts after standalone evidence acceptance → invoke `implementation-plan`

## Stop if

- The assumption is not material to a planning decision or several unrelated questions remain bundled.
- A required command lacks authoritative provenance, an explicit bound, observable completion, termination, or
  cleanup ownership.
- Evidence needs external access, credentials, production data, paid services, or an unsafe/unapproved action.
- The probe requires invasive production changes, broad refactoring, dependency upgrades, or public-contract
  changes rather than disposable isolation.
- Dirty state prevents safe isolation and the user has not approved the exact current-tree probe.
- Timeout, interruption, or failed cleanup leaves process/data/environment state uncertain.
- The resulting decision changes behavior, scope, risk acceptance, or a locked commitment without user approval.

## Output

Return caller/return disposition; planning question and result; repository/official evidence; testing-authority
provenance; bounded command and cleanup outcomes; rejected approaches; remaining risks and verification
implications; and either the nested Delivery Owner evidence handback, standalone `implementation-plan` handoff,
or exact blocker.
