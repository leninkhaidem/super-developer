# Bounded Planned-Feature Attempts

## Boundary

This reference is the sole contract for empirical-question and plan/code-repair attempt identity, progress,
limits, escalation, and durable stop evidence in the planned-feature lifecycle. Load it before attempt 1 or repair
dispatch. It does not widen the active workflow's authority; producers return evidence, not continuation decisions.

## Identity and Progress

- Give each empirical question or coherent repair cluster one stable logical ID. A cluster must share root cause,
  writable scope, and verification envelope; do not merge unrelated issues.
- Attempt 1 is the initial invocation. Attempts 2 and 3 must be fresh invocations with incremented attempt IDs and
  a named, material change to the packet, method, signal, or code delta. Never retry unchanged.
- Carry the logical ID, ordinal, prior attempts/outcomes, and escalation through every continuation, re-review, and
  resumed caller packet. Relabeling, reclustering, or crossing a stage never resets history. Recover unknown history
  from retained evidence or stop; do not create another registry or lifecycle ledger.

## Empirical Questions

Probe only one material behavior still unresolved after bounded repository/official evidence. Routine work, cost
alone, and statically resolved questions need no probe. The caller accepts `resolved-static`, `supported`, or
`rejected` only after validating identity, provenance, method, authority, bounds, limitations, and cleanup.
Evidence cannot approve behavior, scope, architecture, deferral, or risk.

Correct `blocked`, `inconclusive`, or malformed results only through a materially changed attempt. Three total
attempts exhaust the question and stop; empirical questions have no escalation. Independent questions may run in
parallel. Only accepted evidence may create a sequential question. Continually emerging or unbounded material
questions are non-convergence, not unlimited new attempt-1 work.

## Plan and Code Repair

Classify findings before dispatch: code defect, missing regression evidence, plan defect, proposed requirement, or
advisory. Advisories are report-only. Plan defects use the planning owner; new requirements, risk, or manual
exceptions require user authority. A plan-owned cluster stops after three materially changed attempts.

A code cluster also receives three attempts. On its first exhaustion only, it may be reclassified once as a possible
plan defect and routed through `implementation-plan` continuation plus focused `review-plan`, but only while approved
semantics, scope, visible behavior, risk, and manual exceptions remain fixed. Preserve the original cluster ID and
history: reclassification changes method, not authority. Planning repair remains bounded. After reviewed readiness
is restored, at most three further materially changed code attempts may run; the cluster's second exhaustion stops.
There is no second escalation. If reclassification would expand authority, stop instead.

## Stops and Durable Evidence

Auto-resolve in-contract work; return new semantics/risk/manual exceptions, missing external facts or credentials,
protected/out-of-contract actions, exhaustion, or unbounded work to the user-facing owner. Initial planning keeps
its ordinary decisions and approval.

When implementation stops, append a new report only in the authorized non-root artifact store's **existing**
`.tasks/<feature>/reports/` directory:
`stop-<logical-id>-<event-ordinal>.md`. Include attempt history and outcomes, blocker, current work/refs, and prior
escalation. Verify the safe filename, exact root/write authority, unused event ordinal, and file nonexistence.
Never overwrite, edit, or delete an earlier report or obscure user changes. If safe durable writing is unavailable,
write nothing and return the same content in chat with the reason. The user always receives attempts, blocker, and
work state.
