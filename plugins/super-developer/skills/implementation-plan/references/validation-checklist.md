# Implementation Plan Validation Checklist

Load this immediately before writing `.tasks/<feature-name>/SPEC.md` and `.tasks/<feature-name>/tasks.json`, then again after the shared validator passes.

Validator-owned schema, ID, status, risk-tag, targeted-review, and ledger details belong to `${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py`. Work-package semantics belong to `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/work-packages.md`. Use this checklist to catch planner-quality issues those sources cannot fully judge.

## Pre-Write Checklist

Do not create `.tasks/<feature-name>/` or write files until all items pass.

### Gates

- Feature name is inferred or provided, validated as safe kebab-case, and not an unresolved existing-directory conflict.
- Required planning references have been read: `work-packages.md` and `clean-code-rules.md`.
- Design Preflight trigger decision has been made using `design-preflight.md`.
- If Design Preflight ran, every unresolved `MUST_DECIDE` and `BLOCKERS` finding is resolved.
- If resolution changes user-visible semantics, acceptance criteria, or scope, the user approved it before writing.
- Conceptualize Workspace selection is resolved: latest plausible workspace chosen, real ambiguity asked once, or a minimal `.planning/<concept-slug>/index.md` plus `slices/` auto-created.
- The Conceptualize Slice gate from `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/conceptualize-slice-authority.md` has passed: safe selected workspace, full Markdown Slice inventory, complete coverage or explicit zero-Slice state, projection of every hard requirement/material commitment, durable approval for scope reductions, no unresolved conflicts, and no transcript/every-sentence capture.
- Conditional empirical spike decision has been made.
- If a spike was required, accepted evidence is ready to record as `tasks.json.design_decisions` and no spike code will be persisted.
- If the needed empirical assumption cannot be safely validated with available access and bounded side effects, stop and ask the user instead of writing around it.

### SPEC.md

- Contains all user-stated requirements, acceptance criteria, constraints, and out-of-scope items.
- Omits invented product behavior, architecture, non-functional requirements, or success criteria.
- Contains no raw secrets, credentials, tokens, PII, or proprietary sensitive values.
- Contains no implementation details, code snippets, pseudo-code, line numbers, task breakdowns, or implementation sequencing.
- Conceptualize Inputs contains only the selected Conceptualize Index path and path-only non-normative wording.
- Code References are verified path-only references or `None identified`.
- Architecture rationale and design decisions are absent unless the user explicitly made them product requirements.
- Stable `REQ-*` and `AC-*` IDs are present where needed for traceability.

### tasks.json Content

- New plans use schema version 3 with top-level `conceptualize`, `design_decisions`, `context_bundles`, `work_packages`, and `phases` present. Legacy schema version 2 remains compatibility-only for existing plans.
- Accepted preflight, spike, and planner decisions that affect implementation or verification are persisted as concise `design_decisions`.
- Any execution constraints or replan triggers are feature-specific, encoded in existing schema fields, and absent when not materially needed.
- No Preflight Brief, reviewer debate, discarded comments, or raw spike notes are persisted.
- For schema version 3, top-level `conceptualize.index` points to the selected Conceptualize Index, top-level `conceptualize.slice_coverage` records full-workspace coverage or `zero_slices`, and every work package has `conceptualize_slices` as an array of Slice objects with `path` and optional `focus`.
- Conceptualize Slices assigned to packages are read lists only; all hard Slice requirements and material commitments are projected into SPEC requirements, task acceptance criteria, design decisions, or context bundles and cited from `projected` coverage entries.
- The full-workspace coverage matrix remains separate from package-specific `conceptualize_slices`; empty package assignments do not prove zero-Slice workspace coverage.
- No unnecessary verbatim duplication of SPEC sections; tasks trace to SPEC IDs and add task-level verification detail.
- Every task has at least one acceptance criterion object with stable ID, observable criterion, non-empty typed `source_refs`, and a useful verification hint when proof is non-obvious.
- Every SPEC `REQ-*` and `AC-*` is covered by at least one task acceptance criterion.
- Every task passes the independence test: a reviewer can verify its acceptance criteria without seeing another task.
- Every task description states intent plus constraints, not a code tutorial.
- Dependencies are acyclic and point only to valid task IDs.
- Phase order and task IDs are coherent.
- Context bundle references point to valid bundles, and bundle `required_for` fields mention the packages or tasks that need them.

### Work Packages

Use `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/work-packages.md` for source-of-truth semantics.

- Every task appears in exactly one work package.
- Package IDs are coherent and sequential.
- Every package task reference points to a valid task.
- `depends_on` and `parallel_safe_with` point to valid package IDs.
- `parallel_safe_with` is symmetric and conservative based on likely file/module/contract impact.
- The plan includes an explicit safe-parallelism pass: substantial packages that can proceed together without dependency, file, subsystem, or shared-contract overlap are marked as a safe useful wave rather than serialized by habit.
- Any substantial, independent, non-overlapping packages left serialized have a concrete dependency, file-impact, shared-contract, or subsystem-safety reason.
- Artificial parallelism is absent: packages are not split merely to maximize sub-agent count, and ambiguous overlap/shared files/shared contracts/unsafe subsystem impact are combined or serialized.
- A package does not list itself as dependent or parallel-safe.
- Package dependencies do not contradict task dependencies.
- One-task work packages have a rationale explaining why the task is substantial, risky, or naturally isolated.
- `primary_paths` are filled when relevant paths are known.
- `verification_commands` are scoped, known-safe commands or `[]`; do not invent commands.
- Feature-specific Development Quality Contract risks are encoded as observable task criteria, verification commands, package boundaries, context bundles, or design decisions. Generic quality rules are not copied into every task.
- `risk_tags` and `targeted_review_required` follow `validate-tasks-json.py` and `work-packages.md`; do not rely on a copied taxonomy.
- `conceptualize_slices` is present on every package and uses `[]` when no Slice is relevant.

## Write and Machine Validate

After pre-write validation passes:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py" ".tasks/<feature-name>/tasks.json"
```

If the validator exits non-zero, fix `tasks.json` and rerun the same command until it passes. Do not present a plan summary with invalid JSON or validator failures.

## Post-Write Checklist

After the validator passes:

- Re-open the written files, not drafts in memory.
- Confirm `SPEC.md` still satisfies the source and purity rules, including path-only non-normative Conceptualize Inputs.
- Confirm `tasks.json` still matches the intended plan after any validator-driven corrections.
- Confirm all SPEC `REQ-*` and `AC-*` IDs are traced by task acceptance criteria.
- Confirm work-package grouping still reflects the plan after any edits: coherent packages, preferred safe useful parallel waves, conservative serialization for ambiguity or shared contracts, safe commands, and correct targeted-review metadata.
- Confirm no machine-owned long taxonomy was copied into the plan or references when a pointer to `validate-tasks-json.py` or `work-packages.md` is the correct source.
- Confirm Conceptualize semantic checks were not delegated to the validator beyond deterministic shape.
- Confirm Conceptualize semantic checks still match `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/conceptualize-slice-authority.md`: full Slice coverage or explicit zero-Slice state, valid projected refs/approval metadata where required, no unresolved conflicts, and no `informational` entry hiding a hard requirement.
- Confirm the summary to the user lists feature path, phase-by-phase tasks, dependencies, and assumptions without adding new requirements.
