---
name: empirical-spike
description: >
  Produces bounded evidence for one unresolved empirical behavior. Use directly or when planning, plan review,
  or implementation depends on observed behavior after static evidence is insufficient. Do not use to perform
  implementation, code/plan review, or routine testing.
---

# Empirical Spike

Answer one caller-supplied empirical question with bounded, reproducible evidence. Return a caller-neutral report;
the caller retains its context, interprets the evidence, and owns every downstream decision or workflow.

## Always

- Prefer existing code, tests, repository documentation, standards, and current official API/library documentation.
  Do not run a probe when those sources resolve the question.
- Treat every probe, harness, fixture, branch, and worktree as disposable evidence only. Never stage or write the
  index, commit, merge, push, promote, copy, refactor, or continue it as implementation or a planned-feature artifact.
- Never prompt the user, acquire authority, invoke `implementation-plan`, write `.planning/` or `.tasks/`
  artifacts, make product/architecture/risk decisions, or select/recommend/invoke a downstream workflow. Return
  missing authority to the caller as `blocked` with the exact need.
- Keep one material question per run. Under auto-resolve, one logical question has at most three total attempts:
  attempt 1 is the initial run; attempts 2–3 are fresh invocations with the same logical-question ID, an incremented
  attempt ID, and a named corrected packet or changed method/signal. Reject out-of-order, over-cap, or unchanged
  follow-ups; never hide multiple attempts in one run.
- Bound scope, stages, commands, runtime, writes, repetitions, resources, processes, data, side effects, and cleanup
  before execution.
- Apply only a bounded methodological/correctness check to disposable code: prove the probe measures the stated
  question, uses a credible oracle/control or comparison when needed, can discriminate the relevant outcomes,
  and does not materially distort the behavior being observed. Record representativeness and sampling limits.
- Assess security only at the execution boundary: credentials/secrets, sensitive/production/shared data, network,
  permissions, destructive or externally visible effects, isolation, termination, and cleanup. Stop when any
  boundary lacks authority or containment.
- Do not production-harden disposable probe code or perform production-grade security review of it. Solely for
  that code, never dispatch a dedicated security reviewer, `review-code`, or `audit`. An unsafe boundary is a stop,
  not a reason to overengineer or review throwaway code as production.
- Preserve user work. Never stash, reset, force-remove, run `git clean`, or overwrite/remove unowned state.
  Probe cleanup restores/removes only receipt-owned exact paths; uncertainty makes evidence `inconclusive`.

## Do

1. Normalize the input into one falsifiable question or proposition, its stable logical-question/attempt IDs,
   the material decision, support/reject outcomes, constraints, non-goals, supplied authority, and—after attempt
   1—the named packet/method/signal change. Return `blocked` without probing if identity/sequence is invalid,
   unrelated questions are bundled, or no material decision exists.
2. Inspect bounded repository sources first, then current official/primary documentation when repository evidence
   is insufficient. Record path or URL, version/revision/date, relevant passage or observed fact, and freshness.
3. Return `resolved-static` immediately when repository or official evidence answers the question. State why no
   command was needed and retain limitations; do not probe merely for confirmation.
4. Before commands, load `../../references/tool-usage.md`. Resolve testing authority from an accepted/current
   workflow for high-risk, reusable, delegated, browser, live-service, or shared-data work; a routine-safe fallback
   for one bounded deterministic local command; or exact task-local Testing Authorization. If authority is missing,
   stale, conflicting, or too narrow, return `blocked` and name the approval needed; do not select another workflow.
5. Screen the execution boundary named in Always. Use a clean temporary directory for contained local probes. For
   a worktree probe, require a creation receipt binding base ref and caller/contract-supplied expected base SHA,
   full direct ref, clean initial HEAD/index/worktree, unchanged index digest, exact NUL-delimited owned
   path/symlink/process/data manifests, and `remote_action=none`.
6. Write the probe contract before execution: question mapping and signals; environment/limits; command identity,
   cwd, exact allowed writes, timeout/progress, resources, termination, cleanup, and authority. Choose the smallest
   credible discriminator. Never use production targets or sensitive/shared data as a realism shortcut.
7. Run one bounded stage at a time. Return control after failure. Never hide follow-ups in an opaque command,
   repeat an unchanged failure, inflate a timeout to mask missing progress, or broaden scope without authority.
8. Compare observations with the predeclared outcomes. Use `supported` only when the bounded observation supports
   the proposition, `rejected` when it contradicts it, `blocked` when execution/preconditions lack authority, and
   `inconclusive` when the method or outcome cannot discriminate. Do not generalize beyond observed bounds.
9. For a dirty worktree, use `worktree`'s receipt procedure: NUL-safely classify every delta, stop on anything
   unowned, remove exact owned untracked/ignored leaves and empty directories before restoring exact owned tracked
   paths from the bound base SHA, then prove processes/data gone, index unchanged, HEAD/base/ref restored, and
   status clean before normal removal/CAS.
   Never force, reset, stash, broad-delete, or run `git clean`; uncertain cleanup is `inconclusive`.
10. Return the bounded report and stop. The report may inform its caller but is not authority for requirements,
    implementation, security acceptance, planning artifacts, or workflow selection.

## Load if needed

- Command provenance, runtime bounds, termination, or cleanup → `../../references/tool-usage.md`
- Approved disposable git isolation/cleanup mechanics → use `worktree` without delegating downstream decisions
- Project testing policy → read the accepted workflow named by the caller or repository at command time
- Official/primary documentation → only after bounded repository evidence is insufficient

## Stop if

- The question is routine, immaterial, already resolved statically, not falsifiable within bounds, or bundles
  unrelated uncertainties.
- Required credentials, network, permissions, external access, paid services, production/sensitive/shared data,
  destructive effects, isolation, termination, cleanup, or testing authority is absent or unapproved.
- A credible measurement requires production changes, broad refactoring, public-contract changes, dependency or
  service adoption, or treating exploratory code as an implementation head start.
- The stated method cannot distinguish outcomes, its instrumentation invalidates the observation, or its required
  breadth cannot be bounded and justified.
- Dirty/unowned state prevents safe isolation or cleanup, or interruption/timeout leaves residual state uncertain.

## Output

Return exactly one status — `resolved-static`, `supported`, `rejected`, `blocked`, or `inconclusive` — plus the
logical-question/attempt IDs and named follow-up change or `initial`; question/proposition and informed decision;
evidence provenance/freshness; method check; probe-receipt identity/manifest digests when used; testing and command
authority; commands with cwd, bounds, signals, termination, cleanup, and outcomes; observations and
rejected approaches; broad-only justification if applicable; limitations and non-authoritative decision
implications; cleanup result and residual state; and exact approval needed or `none`. Do not include a next-skill
invocation or planned-feature handoff.
