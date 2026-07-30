# Bounded Attempts

One shared rule for bounding retries, so a loop cannot spin forever and cannot be
reset by relabeling. `implement`, `review-plan`, and `empirical-spike` all bind to
this rule; each owns only its role-specific additions.

## The rule

Track every retryable unit under one **stable logical ID**. A retryable unit is a
single material empirical question, or a coherent repair cluster.

- **Attempt 1** is the initial run.
- **Attempts 2 and 3** must each be a fresh run that is *materially changed*: same
  logical ID, incremented attempt ID, plus a named corrected packet, changed
  method, changed signal, or changed code delta.
- **Three total attempts exhaust the circuit.** There is no fourth attempt.

## What cannot reset a circuit

The cap is per logical unit, not per invocation. None of the following start a new
circuit or return an exhausted one to attempt 1:

- retrying unchanged work, or rerunning with only cosmetic differences;
- renaming or relabeling the question, cluster, or IDs;
- reclustering — splitting one unit into several, or merging several into one, to
  obtain fresh attempt counts;
- a new sub-agent, worker, or fresh context performing the same attempt.

If a genuinely distinct material question emerges from accepted evidence, it is a
new unit with its own new logical ID and its own circuit. Deriving a new question
requires new evidence, not a new framing of the same unresolved one.

## Ordering and parallelism

Parallelize independent units. Sequence only when accepted evidence from one unit
creates the next question. Retain context across attempts within a unit so a later
attempt can name what changed.

Reject out-of-order attempts, attempts over the cap, and unchanged follow-ups.
Never hide multiple attempts inside one run.

## On exhaustion

Exhausting a circuit is a reportable outcome, not a failure to retry harder. Report
the logical ID, all attempts with what materially changed in each, and the residual
unknown. The owning skill decides where that goes: `empirical-spike` returns it to
its caller and never routes or prompts; `implement` and `review-plan` treat
non-convergence as their named stop condition.

Never report unresolved work as resolved, and never silently continue past an
exhausted circuit.
