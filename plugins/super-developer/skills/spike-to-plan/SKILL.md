---
name: spike-to-plan
description: >
  Runs a bounded feasibility spike and hands observed evidence to implementation-plan. Use when planning depends
  on unresolved empirical API, integration, performance, concurrency, data, or UX behavior. Do not use for
  routine implementation or code review.
---

# Spike to Plan

Answer the smallest plan-changing empirical question, discard exploratory code, and return observed evidence.
A spike is discovery, never production implementation or a way to inherit protected authority.

## Always

- Prefer repository, tests, docs, and official API evidence before commands or exploratory code.
- Safe disposable discovery is bounded repository inspection, read-only probing, or reversible local experiment in
  a disposable spike worktree. It may not modify production branches, manifests/lockfiles, shared services/data,
  credentials, remote state, or external systems. Record writes and verify cleanup.
- A credentialed/network/live/paid/shared/destructive probe, dependency/manifest/lockfile change, remote write, or
  external effect is a protected discovery action. Stop for one focused authority decision naming exact action,
  side effect, bound, and cleanup. That decision authorizes only this probe, not implementation or later activation.
- Treat spike code/harnesses as disposable evidence. Preserve user work; never stash/reset/overwrite/discard dirty
  changes without exact approval.
- Apply the shared runtime envelope: identity/provenance, cwd/scope, timeout, progress/completion, owned-process
  termination, expected writes, cleanup, and outcome. Timeout or uncertain cleanup is inconclusive evidence.
- If project tests/harnesses/live/browser/shared data are involved, require accepted/current testing workflow,
  routine-safe fallback for one parent-run local command, or exact task-local Testing Authorization. If
  insufficient, invoke `testing` or stop.
- A planning-handoff spike consumes the persisted finite Preauthorization Budget. The owner reserves delegated call,
  spike wave (at most one per empirical cluster), and command units before action; issued usage and absolute
  deadline never reset across retries, replanning, agents, or hosts. Do not create a budget ledger.
- For a Delivery Owner call, load `../../references/orchestration-convergence.md`, preserve caller/return and state,
  and return it to the Delivery
    Owner; never start planning, review, or implementation.

## Do

1. State one empirical assumption, blocked plan decision, success/failure evidence, constraints, non-goals, and
   canonical empirical cluster. Reject bundles of unrelated questions.
2. Inspect existing code/tests/docs and authoritative library/API docs. Stop when static evidence answers it.
3. Before a command, load `../../references/tool-usage.md`; verify caller budget reservation and testing authority.
   Missing workflow alone does not block read-only/static evidence or one proven routine-safe probe.
4. Classify the action as `safe-disposable` or `protected`. For protected action, return
   `protected-discovery-authority-required` before execution unless exact focused authority is present.
5. Use an isolated temporary branch/worktree for code, service, shared-data, or multi-command probes. Current tree
   is allowed only for a small read-only/low-risk probe with clean or explicitly approved state.
6. Define one bounded probe: command identity/provenance, cwd/scope, expected disposable writes and signal, timeout,
   progress/completion, termination/cleanup, approval, and cheapest credible causal evidence. If no narrower probe
   can answer, document why before an explicitly bounded broad-only probe.
7. Run one stage at a time. Do not repeat an unchanged command, inflate timeout to hide absent progress, or hide
   follow-ups in an opaque call. Failure returns control and remains charged.
8. Classify result as `proven-ready`, `known-unavailable`, `protected-activation-required`, `blocked-precondition`,
   `unsafe-needs-approval`, or `inconclusive`. `known-unavailable` required capability becomes planning `blocked`;
   `protected-activation-required` is valid only when feasibility is otherwise established and an exact later
   activation probe/remedy can run after authorization before product writes/fanout.
9. Record observed result, failed/rejected approaches, actual production-path implication, credible observation
   seam, cheapest evidence level, affected broad-regression placement, and prerequisite disposition.
10. Delete throwaway code/harness/worktree/branch after evidence extraction. Verify process/data cleanup; report
    exact residual state and stop if cleanup fails or is uncertain.
11. Return the brief to the caller. Standalone accepted evidence hands off to a fresh `implementation-plan`
    invocation; nested evidence returns to the Delivery Owner. Never draft artifacts inline.

## Stop if

- The question is not material/finite, or budget reservation is missing/exhausted/deadline-expired.
- A command lacks provenance, bound, observable completion, owned termination, or cleanup.
- A protected action lacks exact focused discovery authority; dirty state prevents safe isolation.
- The probe requires invasive production/public-contract changes rather than disposable evidence.
- Timeout/interruption/cleanup leaves uncertainty, or the resulting decision changes product behavior, scope,
  material risk, protected effects, or another Human Authorization Envelope item without user authority.

## Output

Return caller/return; question/cluster/result; safe-vs-protected classification and authority; repository/official
evidence; budget reservation/issued usage/deadline; testing authority; exact commands/writes/cleanup; prerequisite
disposition; production path/seam/broad placement; rejected approaches/risks; and handoff or exact blocker.
