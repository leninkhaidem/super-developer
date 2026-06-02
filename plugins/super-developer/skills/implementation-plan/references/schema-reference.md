# tasks.json Schema Reference

Load this when you need a human-readable map of `tasks.json`. The machine source of truth is `${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py`; if this reference and the validator disagree, the validator wins. Work-package semantics, risk metadata, mandatory package review, and review-depth rules are owned by `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/work-packages.md` plus the validator.

## Top-Level Object

- `schema_version`: number. New plans use `3`; legacy `2` plans are accepted for compatibility. Current accepted versions are owned by the validator.
- `feature`: kebab-case feature name matching the `.tasks/<feature>/` directory.
- `title`: human-readable feature title.
- `description`: one-line feature summary.
- `created_at`: ISO 8601 timestamp.
- `status`: feature lifecycle status. Use the validator for accepted values.
- `conceptualize`: mandatory in schema version 3; object with mandatory `index` path to the selected Conceptualize Index. Optional in legacy schema version 2, but shape-validated when present.
- `design_decisions`: array; include `[]` when none.
- `context_bundles`: array; include `[]` when none.
- `work_packages`: array; required for every generated plan.
- `phases`: ordered array of phase objects.

## Conceptualize

Mandatory top-level object for every new schema version 3 plan. Legacy schema version 2 plans may omit it; if present, the validator still checks its deterministic shape. Legacy schema version 2 plans that already record `conceptualize.index` may omit `slice_coverage` for compatibility; new/current schema version 3 plans must not.

Fields:
- `index`: non-empty repo-relative path to the selected `.planning/<concept-slug>/index.md` Conceptualize Index.
- `slice_coverage`: mandatory in schema version 3; full-workspace, non-authoritative Slice accounting. Use `state: "covered"` with non-empty `entries`, or `state: "zero_slices"` with `entries: []` and a rationale.

Coverage entry fields:
- `path`: non-empty Slice path string.
- `disposition`: compact validator-owned value: `promoted`, `background_only`, `deferred`, `out_of_scope`, `rejected`, or `conflict`.
- `promoted_refs`: required non-empty array when `disposition` is `promoted`; refs point to existing authoritative artifacts using `type`/`id` (`spec_req`, `spec_ac`, `task_ac`, `design_decision`, or `context_bundle`).
- `rationale`: required for non-promoted dispositions; optional but non-empty when present for promoted entries.
- `approval`: required for inherently scope-reducing `deferred`, `out_of_scope`, and `rejected` entries. It records durable user approval metadata: `source`, `approved_at`, `provenance`, `scope`, and optional validated `refs` using the same coverage-ref shape.

The index path, Slice paths, and coverage entries are background accounting, not requirements sources. The validator checks deterministic shape, accepted values, duplicate coverage paths, and reference targets only. Semantic path existence, workspace confinement, Slice relevance, hidden requirements, and whether a `background_only` or `conflict` entry also needs user approval are planning/review/audit responsibilities.

## Design Decisions

Each decision records an accepted planning choice that materially affects implementation or verification.

Fields:
- `id`: sequential `DD-*` identifier with no gaps.
- `decision`: concise accepted decision.
- `rationale`: why this choice satisfies the requirements and constraints.
- `alternatives_considered`: array, possibly empty for simple planner decisions.
- `source`: accepted source value from the validator.

Do not store the full Preflight Brief, debate, or raw spike notes.

## Context Bundles

Use bundles for durable ground truth that future agents must not infer or mock.

Fields:
- `id`: sequential `CTX-*` identifier with no gaps.
- `title`: short contract title.
- `required_for`: work package IDs or task IDs that must read and cite the bundle.
- `sources`: source objects with a validator-accepted `type`, `path_or_url`, and concrete `claims`.
- `verification_required`: proof obligations tied to the bundle.

## Work Packages

Work packages are implementation delegation units. See `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/work-packages.md` for semantics and sizing.

Fields:
- `id`: sequential `WP*` identifier with no gaps.
- `title`, `description`, `rationale`: human package metadata; rationale is especially important for one-task packages.
- `task_ids`: task IDs included in the package; every task appears exactly once across packages.
- `depends_on`: other work package IDs that must be integrated first.
- `parallel_safe_with`: symmetric list of package IDs safe to run in the same implementation batch.
- `primary_paths`: likely files/directories to inspect first; starting points, not hard boundaries.
- `verification_commands`: scoped, known-safe commands, or `[]` when unknown.
- `risk_tags`: controlled tags owned by the validator; they select package-review depth/lenses, not whether review runs.
- `required_context_bundles`: context bundle IDs package agents must read and cite.
- `targeted_review_required`: compatibility boolean for the existing `targeted_review.required` receipt field. Author new packages with `true` for every work package; the mandatory package review gate applies regardless of risk tags.
- `conceptualize_slices`: mandatory in schema version 3; array of Slice assignment objects. Use `[]` when no Slice is relevant. Each object has mandatory non-empty `path` and optional `focus` string. Optional in legacy schema version 2, but shape-validated when present.

Conceptualize Slices are required background context, not hidden requirements. Promote required outcomes into `SPEC.md`, task acceptance criteria, design decisions, or context bundles.

Do not duplicate the long risk-tag or review-depth taxonomy here. Use the validator and `work-packages.md`.

## Phases and Tasks

Phase fields:
- `id`: sequential `P*` identifier.
- `name`: short phase name.
- `description`: what the phase accomplishes as a unit.
- `order`: sequential order with no gaps.
- `tasks`: task objects.

Task fields:
- `id`: phase-qualified task ID.
- `title`: short task title.
- `description`: WHAT to build plus non-discoverable constraints; not exact implementation steps.
- `status`: task lifecycle status. Use the validator for accepted values.
- `dependencies`: task IDs within this feature.
- `acceptance_criteria`: non-empty array of criterion objects.
- `required_context_bundles`: bundle IDs needed for this task; use `[]` or omit when none if accepted by validator.
- `context`: WHY this task exists and which requirement/acceptance outcome motivated it.
- `completed_at` and `blocked_reason`: status-dependent fields added later by execution/status workflows when required.

Task acceptance criterion fields:
- `id`: stable criterion ID derived from the task ID.
- `criterion`: observable, verifiable outcome.
- `source_refs`: non-empty typed references to SPEC requirements, SPEC acceptance criteria, design decisions, or context bundles.
- `verification_hint`: proof hint when verification depends on an edge case, command, manual evidence, performance bound, library/runtime behavior, or no-mocks constraint.

## Validator-Owned Details

Do not maintain competing copies of these details in skills or plans:
- accepted feature/task statuses;
- exact ID regexes and sequential/no-gap checks;
- accepted source-ref and context-bundle source types;
- risk-tag taxonomy and enhanced review-trigger set;
- final package proof schema and stale-evidence checks.

For those details, inspect `${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py`; for package meaning and review expectations, inspect `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/work-packages.md`.
