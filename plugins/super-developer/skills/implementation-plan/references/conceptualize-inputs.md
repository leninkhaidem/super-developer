# Conceptualize Inputs for Implementation Plans

Load this when resolving Conceptualize context for a new `.tasks/<feature-name>/` plan, before drafting `SPEC.md` or `tasks.json`.

Conceptualize files are background evidence only. They may guide planning, but they do not define required outcomes unless the outcome is promoted into `SPEC.md`, task acceptance criteria, design decisions, or context bundles. Slice coverage records are non-authoritative accounting, not a shadow specification.

## Workspace Selection

1. Look for existing `.planning/<concept-slug>/index.md` files whose slug, title, summary, slices, or Planning Handoff plausibly match the requested feature.
2. Use the latest plausible Conceptualize Workspace by default. Prefer a clear recent match over asking the user.
3. Ask one focused question only when multiple plausible workspaces remain genuinely ambiguous after inspecting their indexes.
4. If no plausible workspace exists, auto-create a minimal workspace:
   - derive `<concept-slug>` from the validated feature name unless that would collide, then append a short safe suffix;
   - create `.planning/<concept-slug>/index.md`;
   - create `.planning/<concept-slug>/slices/`, even when no slices exist yet;
   - write only a concise placeholder summary that states no prior Conceptualize session was available.

Do not add readiness, lifecycle, consumed, locked, or draft state.

## Path Boundary

All Conceptualize paths used by implementation planning must stay inside one selected `.planning/<concept-slug>/` workspace.

Before reading, writing, or recording a Conceptualize path:

- require a repo-relative path shaped as `.planning/<concept-slug>/index.md` for the Conceptualize Index or `.planning/<concept-slug>/slices/<slice>.md` for Slices;
- require `<concept-slug>` to be filesystem-safe kebab-case (`^[a-z0-9][a-z0-9-]*$`);
- resolve the repository root first, then require the selected workspace root to resolve under the real repo-local `.planning/<concept-slug>/` path;
- reject symlinked `.planning` directories, symlinked workspace roots, absolute paths, `..` traversal, shell-expanded paths, paths outside the selected workspace, and symlink escapes after resolving the candidate path;
- if a path fails confinement, stop and ask for a safe workspace path rather than reading or recording it.

The validator only enforces deterministic JSON shape; semantic path existence, relevance, and safety checks are planning/review responsibilities.

## SPEC.md Conceptualize Inputs

Add a path-only, non-normative `Conceptualize Inputs` section to `SPEC.md` using the selected Conceptualize Index path.

Rules:

- Include only the index path and a short statement that it is background context.
- Do not copy slice text, research excerpts, design rationale, task decomposition, or hidden requirements into `SPEC.md`.
- Required behavior from Conceptualize material must appear as user-approved requirements or acceptance criteria in the normal SPEC sections.

## Slice Coverage Gate

Before writing `SPEC.md` or `tasks.json`, inventory every Markdown Slice in the selected workspace's `slices/` directory after applying the Path Boundary checks above. Do not limit this inventory to Slices mentioned by the user, listed in the Index, assigned to packages, or flagged under `## Promotion Candidates`.

Block plan writing until one of these states is true:

- every selected-workspace Slice has one coverage/disposition entry in top-level `conceptualize.slice_coverage.entries`; or
- the selected workspace has no Slice Markdown files and `conceptualize.slice_coverage.state` records the explicit zero-Slice empty state with a rationale.

Coverage entries must use a compact disposition vocabulary (`promoted`, `background_only`, `deferred`, `out_of_scope`, `rejected`, or `conflict`) and must not copy Slice prose as requirements. For promoted outcomes, cite authoritative plan artifacts (`SPEC.md` requirement or acceptance IDs, task acceptance criteria, design decisions, or context bundles). For non-promoted outcomes, include a rationale. When a non-promoted disposition reduces behavior the user requested or reasonably expected from the planning conversation, record durable user-approval metadata (approval source, approved-at/provenance, and scope) before writing the plan.

`conflict` dispositions must identify the conflict and either promote the resolved user-approved outcome into authoritative artifacts or block for clarification. The coverage record remains separate from package `conceptualize_slices`: coverage accounts for every workspace Slice, while package assignments identify which Slices a package should read as background.

## tasks.json Conceptualize Metadata

Every new schema version 3 `tasks.json` must include top-level Conceptualize metadata:

```json
"conceptualize": {
  "index": ".planning/<concept-slug>/index.md",
  "slice_coverage": {
    "state": "covered",
    "entries": [
      {
        "path": ".planning/<concept-slug>/slices/<slice-name>.md",
        "disposition": "promoted",
        "promoted_refs": [
          { "type": "spec_req", "id": "REQ-1" }
        ],
        "rationale": "Required behavior was promoted into authoritative plan artifacts."
      }
    ]
  }
}
```

For a workspace with no Slice Markdown files, use the explicit empty state instead of entries:

```json
"conceptualize": {
  "index": ".planning/<concept-slug>/index.md",
  "slice_coverage": {
    "state": "zero_slices",
    "entries": [],
    "rationale": "Selected workspace has no Slice Markdown files."
  }
}
```

Every work package must include `conceptualize_slices`, even when empty:

```json
"conceptualize_slices": [
  {
    "path": ".planning/<concept-slug>/slices/<slice-name>.md",
    "focus": "Optional note scoping this Slice to the package."
  }
]
```

Authoring rules:

- `path` is mandatory and non-empty for each Slice assignment.
- `focus` is optional; use it when a broad Slice needs package-specific scoping.
- Assign only Slices relevant as required background for that work package.
- Do not use Slices as hidden requirements. If implementation must deliver an outcome, promote it into authoritative plan artifacts and cite those artifacts in the full-workspace coverage record.
- Do not treat an empty package `conceptualize_slices` array as zero-Slice workspace coverage; the top-level coverage state is the only full-workspace accounting record.
- Do not generate per-package Conceptualize packet files; later agents read the assigned paths directly as read-only background.
