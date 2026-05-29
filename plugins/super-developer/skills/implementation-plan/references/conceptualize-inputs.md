# Conceptualize Inputs for Implementation Plans

Load this when resolving Conceptualize context for a new `.tasks/<feature-name>/` plan, before drafting `SPEC.md` or `tasks.json`.

Conceptualize files are background evidence only. They may guide planning, but they do not define required outcomes unless the outcome is promoted into `SPEC.md`, task acceptance criteria, design decisions, or context bundles.

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

## tasks.json Conceptualize Metadata

Every new schema version 3 `tasks.json` must include top-level Conceptualize metadata:

```json
"conceptualize": {
  "index": ".planning/<concept-slug>/index.md"
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
- Do not use Slices as hidden requirements. If implementation must deliver an outcome, promote it into authoritative plan artifacts.
- Do not generate per-package Conceptualize packet files; later agents read the assigned paths directly as read-only background.
