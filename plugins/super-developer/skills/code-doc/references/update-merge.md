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

---

## Mode B: Regenerate (Existing code-doc Output)

### Archive

1. Create `{project}/.docs-archive/v{N}/` (N = existing `codedoc_version` from frontmatter)
2. Copy all existing docs into archive directory
3. Preserve directory structure

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

- Never overwrite README.md if it has >50 lines or multiple H2 sections
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

Generated docs include `augmentation_mode: true` in frontmatter. Human docs are never modified.

---

## Frontmatter

Every generated doc carries:

```yaml
---
codedoc_version: {int}
generated: {ISO-8601}
project_hash: {git SHA or "uncommitted"}
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
| Only `README.md` (no `docs/` folder) | If >50 lines: Mode C. If <50 lines: Mode A, wrap as `<!-- human -->` block |
