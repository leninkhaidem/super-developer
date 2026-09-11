# Bounded Work and Repair Progress

## Boundary

Owns repair progress, non-convergence, and effort limits for implementation, planning repair, review-owned fixes,
and diagnose-and-fix. Load before authorizing or starting repair and pass it explicitly to cold workers. It grants
no write, command, risk, planning, or delivery authority. Empirical probes retain their separate bounds below.

## Repair Rounds and Progress

- Keep one stable logical ID per coherent repair cluster: shared root cause, writable scope, and verification
  envelope. Carry its evidence and history through continuation, review, reclassification, and resumed sessions.
- A **repair round** takes one candidate correction through implementation, required verification, and independent
  review/closure when reachable. Plan repair uses its applicable validation/re-review. A blocked check ends the
  round without proving closure. Individual edits, test runs, worker launches, or reviewer handoffs are not rounds.
- Normal edit/test/self-review cycles may continue inside a round while scope, budget, and evidence justify them.
  A routine failing test is not a reason to summon the user or restart a worker. Command timeout, unsafe state,
  uncertain termination/cleanup, or authority failure still stops that action; never retry it unchanged.
- Progress needs an observed change: eliminate a falsifiable cause, narrow a reproduced failure, restore verified
  behavior, or resolve a specific evidence gap. A new patch, renamed finding, different agent, greener unrelated
  tests, or a restated hypothesis is not progress. Never weaken the check or hide a regression to claim progress.
- Before another unsuccessful-round follow-up, name the new evidence and next falsifiable strategy. A bounded
  diagnostic check may earn continuation by resolving a concrete uncertainty; do not require a speculative patch.
  If no evidence-backed next check/correction exists, stop for non-convergence rather than spend the whole budget.
- After **three unsuccessful complete rounds**, reassess the diagnosis, verification oracle, scope, and remaining
  effort. This is an internal reassessment trigger, not an automatic stop, planning handoff, fresh-agent requirement,
  or entitlement to three more rounds. Reassess sooner on repeated failure or contradiction; thereafter continue
  only with evidence-backed progress/strategy inside the unchanged budget, reassessing whenever progress stalls.

## One Shared Repair Budget

Before repair, bind a finite elapsed repair-time allowance in the existing Execution Contract, Fix Authorization,
or active task/fix authorization. Use the supplied repair allowance and any tighter remaining task/host limit.
If no repair allowance is supplied,
use a conservative **30-minute repair-time default**, disclosed in that existing authorization—not a separate ask.
This default is a safety backstop, not an evidence-backed optimal duration. Already-approved work may bind this
more restrictive default without gaining action authority. Respect stricter explicitly approved attempt/round caps;
this policy cannot reinterpret them away or silently enlarge a limit.

The allowance belongs to the **whole authorized task**, not each package, finding, cluster, round, or worker:

- Count investigation, editing, tests, planning correction, verification, and review within repair, including failed
  or interrupted work. Initial planned implementation is not a repair round; an initial localized bug fix is.
- Account actual elapsed repair time from a clock. Parallel work shares one elapsed interval, not one allowance per
  worker. Pause accounting only while all repair work is stopped (for example, waiting for the user or doing unrelated
  planned implementation); an active command/reviewer keeps the interval running.
- Carry consumed/remaining time and round/progress history in existing orchestration packets, not a new ledger.
  Each active worker receives the shared absolute deadline for that interval. Resume subtracts consumed time;
  new invocations, renamed clusters, successful intermediate gates, and code→plan→review never replenish it.
- Check remaining time before dispatch, edits, and commands. Bound command/worker timeouts to the shared deadline,
  reserving termination/cleanup time. A required check that cannot safely fit is blocked, not skipped or truncated
  into a pass. Stop new work at exhaustion, safely terminate owned work, preserve evidence, and report the blocker.
- Missing/unrecoverable timing or history stops rather than inventing a fresh allowance. Only explicit user
  authorization may extend an exhausted allowance. Extension preserves history and does not permit unchanged retries.

No count alone proves safety or completion. Required checks and independent review/audit gates never become optional
because the budget is low or a round limit was reached. Budget authority also never overrides an explicit fix gate.

## Route the Evidence, Not the Counter

Classify each blocker: code defect, missing regression evidence, actual plan defect, proposed requirement, or advisory.
Advisories are report-only. Revisit diagnosis when observations contradict the assumed mechanism. Invoke planning
only for an evidenced plan/Acceptance defect or a genuinely broad/risky design decision under the owning workflow's
authority—not because three rounds failed. Same-requirement plan repair preserves the budget and history; scope,
behavior, risk, manual exceptions, or authority changes return to the user-facing owner before action.

## Empirical Questions

A standalone empirical attempt is one invocation for a single material behavior unresolved by bounded repository/
official evidence. Routine work, cost alone, or static resolution does not require a probe.
Attempt 1 is initial; attempts 2 and 3 need incremented IDs and a named material method/packet/
signal change. Never retry unchanged. Carry identity and outcomes across callers; no relabeling resets history.

Accept `resolved-static`, `supported`, or `rejected` only after checking identity, provenance, method, authority, bounds,
limitations, and cleanup. Correct `blocked`, `inconclusive`, or malformed results only through a changed attempt.
Three total empirical attempts exhaust the question; there is no automatic escalation. Independent questions may
run in parallel; sequential questions need accepted evidence. Continually emerging questions are non-convergence,
not unlimited new attempt-1 work. Repair-related probes also consume the shared repair budget. Evidence never
approves product behavior, scope, architecture, deferral, or risk.

## Stops and Evidence

Stop for non-convergence, exhausted effort, unsafe state/actions, scope/risk expansion, or necessary unavailable
facts/access. Return observed progress, failed hypotheses, remaining blocker, budget consumed, work state, and the
smallest useful next step; never claim completion or halt silently. Preserve a useful reproducer when authorized.

For a planned-feature stop, append only within the authorized non-root artifact store's **existing**
`.tasks/<feature>/reports/`: `stop-<logical-id>-<event-ordinal>.md`. Include round/probe history and outcomes, blocker,
budget, and current work/refs. Verify the safe filename, exact write authority, unused ordinal, and file nonexistence.
Never overwrite, edit, or delete an earlier report or obscure user changes. Diagnose-and-fix uses its existing safe
diagnosis/reproducer handback; review-owned work uses its existing report. No new receipt/registry is required.
If safe durable writing is unavailable, write nothing and return the same evidence in chat with the reason.
