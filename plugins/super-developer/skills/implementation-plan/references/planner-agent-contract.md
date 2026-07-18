# Planner Agent Contract

Use only when an `implementation-plan` orchestrator delegates artifact writing. You are the fresh planner agent.
Read the packet and files, write/validate artifacts, self-challenge them, and return. Do not rely on hidden chat.

## Required Packet

The packet must provide:

- artifact root, code root, artifact ref, feature/artifact slug, and approved rename/migration metadata if any;
- sanitized accepted source baseline, requirements, Conceptualize Index/Slices, and full safe Slice paths;
- resolved Design and Feasibility Preflight: accepted architecture invariants, actual production paths,
  verification seams, affected broad-regression placement, and every prerequisite disposition;
- Human Authorization Envelope inputs and boundaries for agent-owned Technical Plan Baseline choices;
- persisted Preauthorization Budget maxima/issued usage/deadline and reservation identity;
- testing-authority provenance for triggered feasibility; omit when clearly non-triggered;
- overwrite state, resolved Semgrep state, labeled supporting-contract paths, output fields, and stops.

Return `BLOCKED` when a required field or labeled contract is missing. Do not dispatch another agent, run an
unreserved command, or repair the packet from hidden assumptions.

## Supporting Contracts

Load only the parent-labeled contract needed at the action point: artifact storage for roots/ref/slug; Slice and
Conceptualize authority for inventory/projection; preflight evidence before shaping; SPEC template before SPEC;
clean-code/work-package contracts for boundaries and minimum-sufficient acceptance; canonical assurance routing;
artifact/authoring contracts before registry/package files; validation before writes/claims; testing authority for
triggered feasibility; tool safety for command ambiguity; Semgrep policy only when enabled. Do not discover
supporting references through this worker contract.

## Workflow

1. Validate roots/ref/slug, artifact/source/Slice paths, sidecar state, and the budget reservation. If
   Conceptualize applies, inventory/read every safe Slice; use its slug unless migration is approved.
2. Reconcile the accepted source baseline, Slices, and preflight. Ask/stop rather than inventing behavior,
   accepting risk, narrowing scope, deferring material obligations, or changing the Human Authorization Envelope.
   Project accepted invariants through existing SPEC/package/Slice surfaces; never create an architecture,
   prerequisite, requirement, or test ledger.
3. Draft `SPEC.md` with an explicit **Human Authorization Envelope** (outcomes, exclusions, product/interface
   invariants, accepted risks, protected effects, bounds) and versionable **Technical Plan Baseline** (architecture,
   packages, commands, verification topology, prerequisites, cleanup, routing). Technical choices must remain
   envelope-preserving.
4. Shape coherent packages using semantic closure complexity and fixed gate cost, not numeric thresholds. Name
   owned behavior, actual production path, consumed contracts, integration owner, primary paths, dependencies,
   prerequisite activation, cleanup, and earliest credible affected broad regression.
5. Apply the canonical assurance contract once: `standard` by default, strict evidence for `low`, and high-trigger
   precedence. Runtime discovery promotes. Write required top-level `assurance_profile`; for every package write
   `verification_mode: boundary|final` and a safe `report_path` only for `boundary` (`null` for `final`). Package
   Markdown uses `## Independent Verification` with Mode, Report, and named Rationale. Route every producer with a
   dependent or independently consumed material contract to `boundary`; name its contract-digest source, `B[i]`
   owner/lens, and pre-consumption unlock. A coherent leaf may use `final` without a fabricated report. Assign each
   assurance lens to exactly one owner and one side of freeze. This canonical shape supersedes pre-B2
   unconditional-report examples; do not invent a routing ledger.
6. Write Verification Expectations as minimum confidence obligations, not test inventories. Each states accepted
   observable or materially relevant forbidden behavior, the distinct failure mechanism/triggered risk, actual
   production-path seam, cheapest credible causal evidence level, substitutes/disclosures, and failure signal.
   Consolidate overlaps: one causal test/observation may prove several requirements, Slice rows, or `VE-<n>` rows.
   Rows index obligations and never require one test each. Include affected broad-regression placement only where
   shared/public/lifecycle risk makes it credible.
7. Seed obvious exact interface and forbidden behavior plus applicable interactive UI, retry/fail-closed, trigger precedence, lifecycle/restart/reaper, cache invalidation, model/default precedence, generated defaults, and state pollution risk. State that planner seeds do not limit verifier discovery from changed code/diff and known failure modes. Do not prescribe speculative permutations or duplicate evidence layers.
8. When material execution feasibility remains unresolved, record sources/cleanup, smallest credible bounded probe
   or broad-only reason, testing-authority provenance, and spike trigger; route empirical assumptions to a spike.
   Every required prerequisite must be `proven-ready`, `protected-activation-required`, or `blocked`; known
   unavailable is `blocked`, while protected-only activation names its exact post-authorization probe/remedy.
9. If Semgrep is disabled, require no setup/scans. If enabled, use helper `index`/`retrieve`; expectations use
   `python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/semgrep_rules.py" scan ...` with local configs and bounded
   summary consumption. Never run broad or raw direct scans during authoring.
10. Keep `tasks.json` lightweight; package Markdown owns assignment and Verification Expectations. Write only after
    validation gates pass. Re-open files and run `sliceproof.py validate-plan` from code root with explicit roots;
    repair only within packet scope and reserved budget. Proof placeholders require approved dispatch.
11. Perform the Planner Self-Challenge before returning. Attempt to falsify requirement/Slice coverage, envelope
    separation, architecture/ownership, package closure and consumed-contract exactness, actual-path testability,
    prerequisites/environment, broad placement, profile/routing, protected actions/cleanup/budgets, and internal
    consistency. Consolidate duplicate expectations. Any contradiction, unverifiable claim, `blocked` prerequisite,
    or plan-changing uncertainty returns `BLOCKED`, never review-ready.

## Minimum-Sufficient Test Rule

`work-packages.md` is canonical. Apply its smallest-causal-set obligations and stop rule; do not restate them in
SPEC/package prose. Verification Expectations name behavior/risk, distinct mechanism, actual path, cheapest
credible evidence, substitutes, failure signal, and broad placement. One causal test may prove multiple rows.
Never gate on count, changed test lines, test-to-production ratio, coverage, review percentage, or suite volume;
never demand exhaustive suite review or reject/clean up existing tests solely for volume.

## Output

Return roots/ref/slug; SPEC/registry/package/proof/report paths; Human Authorization Envelope and Technical Plan
Baseline summary; preflight/prerequisite dispositions; production paths/seams/broad placement; assurance/routing
proposal; Slice inventory; Semgrep and testing authority; Preauthorization Budget usage; self-challenge result;
deferrals/assumptions; validation; blockers; and next gate.
