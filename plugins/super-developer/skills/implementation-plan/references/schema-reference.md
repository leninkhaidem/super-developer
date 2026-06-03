# V4 Slice-First Artifact Schema Reference

Load this when you need a compact human map of the implementation-plan v4 artifact set. The mechanical source of truth is `${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py`; if this reference and the helper disagree, the helper wins for deterministic validation.

## Artifact Set

New Slice-first plans create these files before implementation dispatch:

```text
.tasks/<feature>/SPEC.md
.tasks/<feature>/tasks.json
.tasks/<feature>/packages/<WP-ID>.md
.tasks/<feature>/proofs/<WP-ID>.proof.md   # path declared during planning; placeholder created before package dispatch
```

Authoritative product/design context stays in Markdown Slices under one selected `.planning/<concept-slug>/slices/` workspace.

## `tasks.json` Registry

Top-level fields for schema-version-4 registries:

| Field | Meaning |
|---|---|
| `schema_version` | Must be `4` for new Slice-first plans. |
| `feature` | Safe kebab-case feature slug matching `.tasks/<feature>/`. |
| `title` | Optional non-empty human title. |
| `status` | Optional feature bookkeeping state. |
| `spec_path` | Path to `.tasks/<feature>/SPEC.md`; must exist for validation. |
| `authoritative_slices` | Non-empty full inventory of safe Slice Markdown paths in the selected workspace. |
| `work_packages` | Non-empty package registry entries. |

Package registry entry fields:

| Field | Meaning |
|---|---|
| `id` | `WP<N>` package ID. |
| `path` | `.tasks/<feature>/packages/<WP-ID>.md` assignment file; must exist. |
| `proof_path` | `.tasks/<feature>/proofs/<WP-ID>.proof.md` declared proof path. |
| `status` | Package bookkeeping state: `pending`, `in_progress`, `done`, or `blocked`. |
| `depends_on` | Package dependency IDs; acyclic and known. |

The registry intentionally omits package scope, assigned H3 IDs, primary paths, verification expectations, proof evidence, review receipts, rich task matrices, and lifecycle ledgers.

## Work-Package Markdown

Required package Markdown shape:

```md
# Work Package: WP1 — <title>

## Scope
...

## Assigned Slices

### `.planning/<concept-slug>/slices/<slice>.md`

Must satisfy:
- `<H3-ID>` — <title>

Context only:
- `<H3-ID>` — <title/reason>

## Primary Paths
- `path/to/file-or-dir`

## Verification Expectations
- <expectation>

## Proof
- `.tasks/<feature>/proofs/WP1.proof.md`

## Dependencies
- None.
```

`sliceproof.py validate-plan` checks required sections, proof-path/dependency consistency with the registry, safe paths, assigned Slice existence, and H3 ID existence under `## Shared Understanding`. It does not decide whether assignment is semantically complete.

## Slice H3 References

Material Slice obligations are Heading 3 Shared Understanding blocks in Markdown Slices. Recommended ID shape is `PREFIX-NNN`, for example:

```md
### DB-SESSION-TIMEOUT-001 — Organization stores timeout in minutes
```

Work-package Markdown references the ID. The full H3 content remains the obligation to understand and satisfy; the title is not a substitute.

## Proof Markdown

The package proof path is declared in both the registry and package Markdown. Before package dispatch, generate the placeholder with:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" create-proof ".tasks/<feature>/tasks.json" --package WP1
```

The generated proof contains required rows for `must_satisfy` IDs only and includes `context_only` IDs as assigned-scope context. Implementation agents fill evidence; `validate-proof` checks mechanical completion markers and required rows only.

## Mechanical Helper Boundary

Use `sliceproof.py` for v4:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-plan ".tasks/<feature>/tasks.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" create-proof ".tasks/<feature>/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-proof ".tasks/<feature>/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-final ".tasks/<feature>/tasks.json"
```

The helper validates structure, paths, package sections, H3 existence, proof rows, and unresolved markers. It does not inspect git freshness, run tests, mutate status, judge semantic evidence sufficiency, accept/reopen proofs, or replace review/audit.

Legacy schema-version-2/3 helpers (`validate-tasks-json.py`, `taskctl.py`) are compatibility tools for old plans and are not the v4 artifact source of truth.
