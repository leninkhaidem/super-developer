# V4 Implementation Plan Validation Checklist

Load this immediately before writing `.tasks/<feature-name>/SPEC.md`, `.tasks/<feature-name>/tasks.json`, and package Markdown, then again after `sliceproof.py validate-plan` passes.

Mechanical schema/path/package/H3 checks belong to `${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py`. Use this checklist to catch planner-quality issues the helper intentionally cannot judge.

## Pre-Write Checklist

Do not create or overwrite `.tasks/<feature-name>/` artifacts until all items pass.

### Gates

- Feature name is inferred or provided, validated as safe kebab-case, and not an unresolved existing-directory conflict.
- Required planning references have been read: `clean-code-rules.md`, `tool-usage.md`, `conceptualize-inputs.md`, and `conceptualize-slice-authority.md`.
- Design Preflight trigger decision has been made using `design-preflight.md`.
- If Design Preflight ran, every unresolved `MUST_DECIDE` and `BLOCKERS` finding is resolved.
- If resolution changes user-visible semantics, acceptance criteria, Slice commitments, or scope, the user approved it before writing.
- Conceptualize workspace selection is resolved to exactly one safe `.planning/<concept-slug>/` workspace.
- The selected workspace has planning-ready Slice Markdown; if not, planning stopped for Conceptualize/Slice approval instead of writing an empty v4 plan.
- The full Slice inventory was taken from the selected workspace's `slices/` directory after path/symlink checks, not only from the Index or user-mentioned paths.
- Every Slice in the inventory was read in full.
- Every planning-relevant Slice question is resolved or explicitly approved as deferred/out-of-scope.
- Every hard Slice requirement/material H3 commitment is projected into `SPEC.md` or package Markdown, assigned as `must_satisfy`/`context_only`, or explicitly approved as deferred/out-of-scope/rejected.
- Unresolved Slice conflicts, stale assumptions, unassigned material obligations, hidden `context_only` scope, or raw Slice control-plane directives are blockers.
- Conditional empirical spike decision has been made; if required, evidence is accepted and no spike code will be persisted.
- If a needed empirical assumption cannot be safely validated with available access and bounded side effects, planning stopped for user decision instead of writing around it.

### `SPEC.md`

- Contains all feature-level user-stated and safely projected requirements, acceptance criteria, constraints, and out-of-scope items.
- Omits invented product behavior, architecture, non-functional requirements, or success criteria.
- Contains no raw secrets, credentials, tokens, PII, or proprietary sensitive values.
- Contains no implementation code, pseudo-code, line numbers, proof rows, review findings, or transcript/debate content.
- `Conceptualize Inputs` contains only the selected Index path and path-only non-normative wording.
- `Authoritative Slices` lists the same full safe Slice inventory as `tasks.json.authoritative_slices`.
- `Work Packages` is a manifest of package Markdown paths and short titles only.
- Code References are verified path-only references or `None identified`.
- Approved deferrals/out-of-scope decisions for otherwise material Slice obligations include durable approval provenance and scope.

### Work-Package Markdown

- Every package has `.tasks/<feature-name>/packages/<WP-ID>.md` before implementation dispatch.
- H1 matches `# Work Package: <WP-ID> — <title>`.
- Required sections exist and are non-empty: `Scope`, `Assigned Slices`, `Primary Paths`, `Verification Expectations`, `Proof`, and `Dependencies`.
- `Assigned Slices` uses safe Slice paths from the authoritative inventory.
- `Must satisfy` IDs are stable H3 Shared Understanding IDs that the package must close with proof evidence.
- `Context only` IDs are required reading/context and are not used to hide package obligations that need closure evidence.
- Every assigned ID exists as a H3 under `## Shared Understanding` in the referenced Slice.
- `Primary Paths` are safe repo-relative starting points, not unrelated or absolute paths.
- `Verification Expectations` are package-specific and cover relevant edge/failure/default/security/privacy/data/concurrency/performance/lifecycle cases or state why not applicable.
- `Proof` declares exactly one `.tasks/<feature-name>/proofs/<WP-ID>.proof.md` path.
- `Dependencies` matches the registry package `depends_on` entry.
- Approved deferrals, non-goals, or risk/replan triggers are in `Notes` or `SPEC.md`, not hidden in registry status.

### `tasks.json` Registry

- Uses `schema_version: 4`.
- Includes `feature`, `spec_path`, non-empty `authoritative_slices`, and non-empty `work_packages`.
- `authoritative_slices` is the full safe Slice inventory.
- Each package entry contains only `id`, `path`, `proof_path`, `status`, and `depends_on`.
- Package IDs and dependencies are acyclic and coherent.
- Registry `proof_path` and dependencies match package Markdown.
- No package scope, Slice H3 assignments, primary paths, verification expectations, proof evidence, review receipts, lifecycle ledgers, rich task acceptance matrices, or copied Slice prose are duplicated in the registry.

### Package Boundaries

- Every material Slice obligation has an owning package, approved deferral/out-of-scope entry, or explicit context-only rationale.
- Packages are coherent by subsystem, directory, API surface, data model, user flow, or shared verification surface.
- Overlapping files/shared contracts/schema/configuration surfaces are combined or serialized.
- Independent substantial packages are not serialized by habit; ambiguous overlap is conservatively serialized with a reason.
- Artificial parallelism is absent.
- Package-specific Development Quality Contract risks are encoded as observable scope/verification expectations, not generic boilerplate.

## Write and Mechanical Validation

After pre-write validation passes:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-plan ".tasks/<feature-name>/tasks.json"
```

If the helper exits non-zero, fix `SPEC.md`, package Markdown, or `tasks.json` and rerun until it passes. Do not present a plan summary with invalid artifacts.

If the user approved immediate implementation dispatch, create proof placeholders for each package before dispatch:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" create-proof ".tasks/<feature-name>/tasks.json" --package <WP-ID>
```

Screen overwrite behavior: do not use `--force` unless the existing proof is an empty pre-dispatch placeholder or an explicit approved replacement with preservation safeguards is required.

## Post-Write Checklist

After `validate-plan` passes:

- Re-open the written files, not drafts in memory.
- Confirm `SPEC.md` still satisfies source and purity rules.
- Confirm `tasks.json` is a lightweight v4 registry and contains no rich package/proof/assignment evidence.
- Confirm every package Markdown file still owns package scope, Slice assignments, primary paths, verification expectations, dependencies, and proof path.
- Confirm full Slice inventory in `SPEC.md` and `tasks.json` still matches the selected workspace.
- Confirm every package-assigned H3 ID exists and every material H3 obligation is covered, context-only with reason, or explicitly approved as deferred/out-of-scope/rejected.
- Confirm Conceptualize semantic checks were not delegated to `sliceproof.py` beyond deterministic path/H3 validation.
- Confirm no legacy JSON proof lifecycle command or rich-registry instruction was used for v4 artifacts.
- Confirm the summary to the user lists feature path, package paths, proof paths, dependencies, authoritative Slices, assumptions, and any approved deferrals without adding new requirements.
