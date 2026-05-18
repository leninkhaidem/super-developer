# Update Mode — Archive and Regenerate

On re-invocation when `{project}/docs/` already exists.

---

## Mode Detection

| Condition | Mode | Action |
|-----------|------|--------|
| No `docs/` directory, or empty | **Fresh** | Full generation, `codedoc_version: 1` |
| Docs exist with `codedoc_version` frontmatter | **Regenerate** | Archive → regenerate → merge human blocks |
| Docs exist WITHOUT `codedoc_version` frontmatter | **Augment** | Preserve all human docs, generate only to `docs/codedoc/` |

---

## Mode A: Fresh Generation

Straightforward — run full pipeline, write to `{project}/docs/`, set `codedoc_version: 1`.
For `README.md`, still apply README protection: write it only if missing, tiny/template-like,
already code-doc-generated, or explicitly approved. Preserve short but meaningful human READMEs.

---

## Mode B: Regenerate (Existing code-doc Output)

### Archive

1. Create `{project}/.docs-archive/v{N}/` (N = existing `codedoc_version` from frontmatter)
2. Copy all existing docs into archive directory
3. Preserve directory structure

### Archive Handoff Policy

`.docs-archive/` is a rollback and merge-audit aid, not a default documentation deliverable.
Keep it available through review and handoff, but exclude it from the proposed commit unless the
user explicitly approves committing the archive. If the user declines to keep it, remove it only
after generated docs have passed review and the user has accepted the regenerated output.

### Human Content Preservation

Two detection methods, applied in priority order:

**1. Explicit Markers** (highest priority):
```markdown
<!-- human -->
This section was written by a developer.
<!-- /human -->
```

**2. Non-Template Headers**: Sections under headers not present in the standard code-doc output
for that doc type are assumed human-authored. Extract all detected human blocks with their parent
header. Store in memory for re-insertion after generation.

### Regenerate

1. Run full analysis pipeline (scout → analysts → synthesis → doc writers)
2. Generate fresh docs from analysis
3. Re-insert preserved human blocks under matching headers
4. If no matching header exists, append human block at end of relevant doc with original header intact
5. Wrap re-inserted blocks with explicit `<!-- human -->` markers for future runs
6. Set `codedoc_version = N + 1`

---

## Mode C: Augment (Existing Human-Written Docs)

**Never overwrite comprehensive human documentation.**

### Preservation Rules

- Never blindly overwrite README.md. Generate/rewrite it only if missing, tiny/template-like, already code-doc-generated, or explicitly approved by the user.
- If README is human-authored, preserve it and propose (do not apply) an optional link section pointing to generated supporting docs.
- Never overwrite any doc that appears manually curated (prose quality, custom sections, detailed examples)
- `codebase-context.md` always generated — machine metadata, doesn't overlap with human prose

### Augmentation Strategy

Generate code-doc output to a subdirectory to avoid conflicts:

```
docs/
├── README.md              # Human — preserved
├── CONTRIBUTING.md        # Human — preserved
└── codedoc/               # Generated — new subdirectory
    ├── INDEX.md           # Links to both human and generated docs
    ├── codebase-context.md
    └── architecture-guide.md   # Only if no equivalent exists
```

Generated docs include `augmentation_mode: true` in frontmatter. Human docs are never modified without explicit user approval.

---

## Frontmatter

Every generated doc carries:

```yaml
---
codedoc_version: {int}
generated: {ISO-8601}
project_hash: {short git SHA, or "uncommitted"/"no-git" when unavailable}
---
```

On fresh run: `codedoc_version: 1`. On re-invocation: increment by 1.

---

## Edge Cases

| Situation | Handling |
|-----------|----------|
| No existing docs | Fresh run — `codedoc_version: 1` |
| Empty `docs/` folder (no `.md` files) | Fresh run |
| Existing docs without frontmatter | Mode C (augment) |
| Code-doc output without frontmatter | Treat as version 0, Mode B |
| Human block header changed in new version | Append at end with `<!-- NOTE: original header was "X" -->` |
| Monorepo with mixed doc states | Handle each sub-project independently |
| Only `README.md` (no `docs/` folder) | Apply README protection criteria, not line count: preserve if human-authored/meaningful; generate or rewrite only if missing, tiny/template-like, already code-doc-generated, or explicitly approved |
