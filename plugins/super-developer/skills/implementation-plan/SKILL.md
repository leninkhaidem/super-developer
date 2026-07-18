---
name: implementation-plan
description: >
  Creates fresh Slice-first planned-feature artifacts or performs a Delivery-Owner-routed focused amendment.
  Use for implementation planning, package breakdowns, or accepted-plan amendments. Do not use for coding,
  code review, audit, or status.
---

# Implementation Plan

Orchestrate `create` of a fresh Slice-first planned-feature set, or an explicit `amend`, under the selected
artifact root. The approved change may target a new or existing system. Source inspection and helper execution use
the code root. Delegate artifact writing to a fresh planner with `references/planner-agent-contract.md`; do not
draft `.tasks/<feature>/` artifacts inline.

## Always

- Plan only after Design and Feasibility Preflight has resolved requirement, architecture, prerequisite, and
  verification-seam uncertainty. Preflight depth is adaptive, but it always precedes plan authoring.
- Preserve a sanitized accepted source baseline, authoritative Slices, accepted architecture invariants, and
  observed repository/spike evidence. Never add another requirement, architecture, or test ledger.
- Separate the user-owned Human Authorization Envelope from the agent-correctable Technical Plan Baseline.
- At the planning handoff, initialize or resume the finite Preauthorization Budget in the existing compact
  Lifecycle State: maxima and monotonically issued usage for calls, planner-correction waves, spike waves, command
  units, and an absolute deadline. Reserve usage before dispatch/command; replanning, agents, and hosts never reset
  it. Budget exhaustion returns one batched `needs_decision` result and authorizes no implementation.
- For nested amendments, load `../../references/orchestration-convergence.md`; preserve caller/return, old
  accepted commit, finite affected scope, and authorization. Return old accepted/new candidate state plus the
  invalidation handback; never invoke review or implementation on the caller's behalf.
- Ask before inventing behavior, narrowing scope, deferring a material obligation, accepting risk, changing the
  Human Authorization Envelope, or overwriting an existing plan.
- Slices are product/design authority when present, never workflow or tool instructions. Inventory and read every
  safe Slice in full; Index-only planning is allowed when no Slice is independently useful.
- Registry is bookkeeping only. Package Markdown owns assignment; proof/report artifacts are later evidence.
- Apply `../../references/clean-code-rules.md` while shaping packages, projecting only material implications.
- Carry explicit artifact root, code root, artifact ref, and resolved slug in packets, commands, and summaries.
- Preserve the Conceptualize slug unless approved rename/migration metadata covers every affected sidecar surface.
- Semgrep opt-in is parent-resolved when supplied; do not reopen opt-in. Only when no resolved Semgrep state is supplied, treat this as
  direct invocation and resolve `.superdeveloper/preferences.yml`. Disabled means no setup, scan, or network need.
- Validate returned files and run the Planner Self-Challenge before presenting review-ready output.

## Do

1. Load `../../references/artifact-store.md` and, for nested work,
   `../../references/orchestration-convergence.md`. Resolve `create|amend`, caller/return, roots/ref/slug, accepted
   state, affected scope, source material, and the persisted Preauthorization Budget. Sidecar setup belongs to
   `worktree`; fail closed on drift or unsafe current-root authority.
2. Run `references/design-preflight.md` before artifact authoring. Safe repository reads, read-only probes, and
   reversible local experiments in a disposable spike worktree may proceed under discovery authority. A probe that
   changes production branches, manifests/lockfiles, shared services/data, credentials, remotes, or external
   systems is protected: obtain one focused discovery decision or stop. Do not disguise it as implementation.
3. Resolve every required prerequisite as `proven-ready`, `protected-activation-required`, or `blocked` with
   source-bound provenance. Known-unavailable requirements are `blocked`; protected-only checks name the exact
   activation probe/remedy and run only after later authorization, before product writes/fanout. Optional unavailable
   capability is disclosed and excluded. Route plan-changing empirical uncertainty through `spike-to-plan`.
4. When test/harness behavior is material, resolve testing authority: accepted/current workflow, routine-safe
   fallback for one bounded local command, or exact task-local authorization. Missing workflow alone does not block
   read-only planning. If authority is insufficient, invoke `testing` to establish/update it or stop. Establish
   actual production paths, credible observation seams, cleanup, and earliest affected broad-regression placement.
5. Resolve Semgrep state before planner dispatch. Use supplied state and do not reopen opt-in. Otherwise load
   `../../references/model-preferences.md`; at the action point load `../../references/semgrep.md`, disclose any
   clone/fast-forward side effect, and continue disabled if declined. Do not scan while authoring.
6. Dispatch a fresh planner with roots/ref/slug; sanitized baseline and Slices; resolved preflight evidence,
   prerequisites, actual-path seams, broad placement, testing authority, and Preauthorization Budget snapshot;
   Human Authorization Envelope inputs; labeled contract paths; resolved Semgrep state; overwrite/stops/outputs;
   and amendment caller/return plus affected/preserved-state handback when applicable. Include
   testing-authority provenance only for a triggered feasibility profile; omit routine non-trigger state.
7. Require the planner to propose the Technical Plan Baseline, `low|standard|high` assurance profile and
   `boundary|final` package routing with named risk/boundary rationale, then self-challenge requirement coverage,
   architecture, package/consumed contracts, actual-path testability, prerequisites, routing, and contradictions.
   Any unresolved item is `BLOCKED`, not review-ready.
8. Re-open `SPEC.md`, `tasks.json`, and every package file from the artifact root. From the code root run
   `python3 plugins/super-developer/assets/sliceproof.py validate-plan --artifact-root <artifact-root> \
   --code-root <code-root> .tasks/<feature>/tasks.json`; return semantic repair to the planner, charging the budget.
9. Report roots/ref, mode/caller, old/new candidate state, envelope/baseline split, preflight and prerequisite
   dispositions, profile/routing proposal, packages/dependencies, actual paths/seams/broad checks, budget usage,
   affected/preserved state and stale evidence, validation, deferrals, assumptions, and next review input. This is
   not the final accepted amendment handback.

## Load if needed

- Root/storage details → `../../references/artifact-store.md`
- Conceptualize inputs → `references/conceptualize-inputs.md` and
  `../../references/conceptualize-slice-authority.md`
- Package shaping → `../../references/work-packages.md`
- SPEC/artifacts → `references/spec-template.md`, `references/artifact-authoring.md`, and
  `../../references/slice-first-artifacts.md`
- Before writes/completion → `references/validation-checklist.md`
- Command safety → `../../references/tool-usage.md`; Semgrep action point → `../../references/semgrep.md`

## Stop if

- Roots/ref/slug/source paths, sidecar state, or budget state are unsafe, missing, stale, or contradictory.
- A Human Authorization Envelope decision, Slice disposition, risk acceptance, or protected discovery action lacks
  authority; a known required prerequisite is unavailable; or protected activation is not exact and deferrable.
- A material actual production path, causal observation seam, broad-regression placement, package boundary,
  consumed contract, or routing rationale is unresolved.
- A spike/probe is unsafe, unbounded, outside discovery authority, or cannot clean up; or budget is exhausted.
- `sliceproof.py validate-plan` fails and cannot be repaired within envelope, scope, and budget.

## Output

Return mode/caller, roots/ref, old/new state, Human Authorization Envelope, Technical Plan Baseline, accepted
baseline/invariants, preflight/prerequisites, packages/dependencies/routing, actual-path verification topology,
Preauthorization Budget maxima/issued/deadline, Slice inventory, deferrals, assumptions, validation, and next step.
