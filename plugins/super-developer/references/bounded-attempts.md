# Bounded Planned-Feature Attempts

## Boundary

This reference owns empirical-question and plan/code-repair circuits for the planned-feature lifecycle. Load it
before the first attempt or a repair dispatch. Standalone PR/local bugfix authorization remains owned by its
active workflow; this reference does not expand it. Producers return evidence and never choose continuation.

## Identity and Progress

- Give each distinct material empirical question or coherent repair cluster one stable logical ID. A repair
  cluster shares root cause, writable scope, and verification envelope; merging unrelated issues is not a way
  to gain authority or extra attempts.
- Attempt 1 is initial. Attempts 2–3 are fresh invocations with incremented attempt IDs and a named corrected
  packet or changed method, signal, or code delta. Unchanged retries are forbidden.
- Carry the logical ID, prior attempts/outcomes, current ordinal, and any escalation through every worker,
  planning continuation, re-review, and resumed caller packet. Use existing reports/decisions records where
  durability is needed; create no second registry or lifecycle ledger. Unknown history is not permission to
  restart the counter: recover it from retained evidence or stop with the missing history.
- Independent bounded empirical questions may run in parallel. Only accepted evidence may create a sequential
  question. Relabeling/reclustering never resets a circuit; continually emerging or unbounded material questions
  are non-convergence rather than unlimited new attempt-1 work.

## Empirical Evidence

Each attempt is one fresh `empirical-spike` invocation for one material behavior unresolved after bounded
repository/official evidence. Routine work, cost alone, or a statically resolved question needs no probe.
The caller validates identity, provenance, method, authority, bounds, limitations, and cleanup before accepting
`resolved-static`, `supported`, or `rejected`. Evidence cannot approve behavior, scope, architecture, deferral,
or risk. Correct `blocked`, `inconclusive`, or malformed returns only through an authorized materially changed
attempt. Exhaustion at three total attempts stops; empirical questions have no escalation/reset.

## Plan and Code Repair

Classify findings before dispatch: code defect, missing regression evidence, plan defect, proposed requirement,
or advisory. Advisories are report-only. Plan defects go through the planning owner, not a code repair worker;
new requirements/risk/manual exceptions need user authority.

A plan-owned cluster exhausts after three total materially changed attempts. A code cluster also has three
attempts, but on its first exhaustion may be reclassified once as a possible plan defect. Route through
`implementation-plan` continuation and focused `review-plan` only if approved semantics, scope, visible behavior,
risk, and manual exceptions remain fixed. This changes the method, never the authority.

Carry that single escalation on the original cluster ID. After readiness is restored, at most three further
materially changed code-repair attempts may run; the same cluster's second exhaustion stops. Planning repair
itself remains bounded. No renaming, reclustering, new stage, or second escalation earns another budget.
If the first escalation would expand authority, stop immediately instead.

## Stops and Durable Evidence

Under auto-resolve, keep in-contract corrections, replan/re-review, and repairs autonomous. Return to the user
for new semantics/risk/manual exceptions, missing credentials/external facts, protected/out-of-contract actions,
or the exhaustion/unbounded-work conditions above. Initial planning retains its ordinary decision/approval gate.

When implementation stops, write an append-only stop report in the authorized non-root artifact store's existing
reports directory: `.tasks/<feature>/reports/stop-<logical-id>-<event-ordinal>.md`. Include attempts, concrete
outcomes, blocker, current work/refs, and any prior escalation. The event ordinal is new for each stop of that
logical ID. Confirm a safe filename, exact root/write authority, and nonexistence before writing; never overwrite,
edit, or delete an old stop report or obscure user changes. If safe durable writing is unavailable, write nothing
and return the same content in chat with the reason. The user always receives the attempts, blocker, and work state.
