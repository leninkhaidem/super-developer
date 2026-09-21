# Repair Progress and Execution Limits

## Boundary

Owns repair progress, non-convergence, and applicable effort limits for implementation, planning repair,
review-owned fixes, and diagnose-and-fix. Load before authorizing or starting repair and pass it explicitly to cold
workers. It grants no write, command, risk, planning, or delivery authority. Empirical probes retain their separate
bounds below.

## Repair Rounds and Progress

- Keep one stable logical ID per coherent repair cluster: shared root cause, writable scope, and verification
  envelope. Carry its evidence and history through continuation, review, reclassification, and resumed sessions.
- A **repair round** takes one candidate correction through implementation, required verification, and independent
  review/closure when reachable. Plan repair uses its applicable validation/re-review. A blocked check ends the
  round without proving closure. Individual edits, test runs, worker launches, or reviewer handoffs are not rounds.
- Normal edit/test/self-review cycles may continue inside a round while scope, evidence, and applicable limits
  justify them. A routine failing test is not a reason to summon the user or restart a worker. Command timeout,
  unsafe state, uncertain termination/cleanup, or authority failure still stops that action; never retry it unchanged.
- Progress needs an observed change: eliminate a falsifiable cause, narrow a reproduced failure, restore verified
  behavior, or resolve a specific evidence gap. A new patch, renamed finding, different agent, greener unrelated
  tests, or a restated hypothesis is not progress. Never weaken the check or hide a regression to claim progress.
- Before a failed correction's follow-up, use task-relevant observations to justify the next falsifiable strategy.
  A plausible strategy alone is not evidence. A bounded diagnostic check may earn continuation by resolving a
  concrete uncertainty; name the uncertainty and distinguishing signal, not a speculative patch. If no
  evidence-backed next check/correction exists, stop for non-convergence.
- Reassess the diagnosis, verification oracle, and scope when observations contradict the hypothesis or progress
  stalls, including recurring failures and oscillating regressions. Apply this rule after meaningful diagnostic or
  verification results inside a long round too; do not hide repeated ineffective work inside one invocation.
  This is not a new stage, per-command form, or automatic planning/fresh-agent handoff.
- Repeatedly spawning or renaming problems without advancing the agreed obligations is non-convergence. Several
  independently verified corrections are not, by their number alone, non-convergence or a change in approved scope.

## Applicable Limits

There is no default repair-round quota or count-triggered reassessment. Do not invent a replacement timer or require
consumed/remaining counters when no applicable count limit exists. Use existing authorizations and handoffs, not a
new budget framework, progress score, or ledger.

Honor explicit user limits, already-approved caps, and actual host-enforced limits within their stated scope. The
orchestrator preserves task-wide limits across parallel workers, continuation, reclassification, and resumed sessions;
a new worker, cluster, successful gate, or code→plan→review transition cannot reset them. Do not give each worker a
fresh copy of a task-wide allowance. Carry only the limit state needed to honor those constraints, alongside repair
evidence/history. If a binding limit's remaining capacity cannot be established, stop the governed work rather than
guess or reset it. Only explicit user authorization may extend a user-imposed limit; it does not bypass host limits.

For an explicit repair-round cap, count a started round once, including failed or interrupted work; interruption
never proves completion or creates a free retry. Initial planned implementation is not a repair round; an initial
localized bug fix is. A differently defined explicit limit retains its own counting semantics. An exhausted round
start-count forbids another round, not completion of already-authorized checks in the current round; deadlines and
other action limits retain their own stop conditions.

Existing command/worker timeout, termination, and cleanup rules still govern each action. These prompt instructions
do not enforce an aggregate runtime, cost, or turn ceiling; per-command timeouts do not bound the whole task.
Without an external task-level guard, overall effort control remains best-effort. A required check that cannot safely
run is blocked, not skipped or truncated into a pass. Required checks and independent review/audit gates never become
optional because effort is high or a limit is reached. This policy never overrides an explicit fix gate.

## Route the Evidence, Not the Counter

Classify each blocker: code defect, missing regression evidence, actual plan defect, proposed requirement, or advisory.
Advisories are report-only. Revisit diagnosis when observations contradict the assumed mechanism. Invoke planning
only for an evidenced plan/Acceptance defect or a genuinely broad/risky design decision under the owning workflow's
authority—not because repairs took several rounds. Same-requirement plan repair preserves evidence/history and
applicable limits; scope, behavior, risk, manual exceptions, or authority changes return to the user-facing owner
before action. Recover missing repair context from authorized evidence; if safe continuation cannot be established,
stop with the missing facts rather than invent history or repeat failed approaches.

## Empirical Questions

A standalone empirical attempt is one invocation for a single material behavior unresolved by bounded repository/
official evidence. Routine work, cost alone, or static resolution does not require a probe.
Attempt 1 is initial; attempts 2 and 3 need incremented IDs and a named material method/packet/
signal change. Never retry unchanged. Carry identity and outcomes across callers; no relabeling resets history.

Accept `resolved-static`, `supported`, or `rejected` only after checking identity, provenance, method, authority, bounds,
limitations, and cleanup. Correct `blocked`, `inconclusive`, or malformed results only through a changed attempt.
Three total empirical attempts exhaust the question; there is no automatic escalation. Independent questions may
run in parallel; sequential questions need accepted evidence. Continually emerging questions are non-convergence,
not unlimited new attempt-1 work. A repair-related probe remains part of its originating repair and inherits applicable
task limits as well as this separate empirical cap. Evidence never approves product behavior, scope, architecture,
deferral, or risk.

## Stops and Evidence

Stop for non-convergence, a limit blocking required work, unsafe state/actions, scope/risk expansion, or necessary
unavailable facts/access. Safely terminate owned work when required. Return observed progress, failed hypotheses,
remaining blocker, applicable limit state, work state, and the smallest useful next step; never claim completion or
halt silently. Preserve a reproducer when authorized.

For a planned-feature stop, append only within the authorized non-root artifact store's **existing**
`.tasks/<feature>/reports/`: `stop-<logical-id>-<event-ordinal>.md`. Include repair/probe history and outcomes, blocker,
applicable limits, and current work/refs. Verify the safe filename, exact write authority, unused ordinal, and
nonexistence. Never overwrite, edit, or delete an earlier report or obscure user changes. Diagnose-and-fix uses its
existing safe diagnosis/reproducer handback; review-owned work uses its existing report. No new receipt/registry is
required. If safe durable writing is unavailable, write nothing and return the same evidence in chat with the reason.
