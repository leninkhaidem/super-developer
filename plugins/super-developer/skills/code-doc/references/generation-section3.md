# Generation Reference — §3: Update & Merge Logic

Re-analysis workflow for previously documented codebases. Handles three modes based on existing documentation state to preserve human investment while keeping generated docs current.

---

## §3.1 Update Detection

Before generating documentation, detect the existing documentation state:

```
check_doc_state(project_root):
  docs_path = project_root / "docs/"
  
  if not docs_path.exists() or is_empty(docs_path):
    return MODE_A_FRESH
  
  # Check any markdown file for codedoc frontmatter
  for md_file in docs_path.glob("**/*.md"):
    frontmatter = parse_frontmatter(md_file)
    if "codedoc_version" in frontmatter:
      return MODE_B_CODEDOC_OUTPUT
  
  # Docs exist but no codedoc markers
  return MODE_C_HUMAN_WRITTEN
```

**Detection Priority:**
1. If `{project}/docs/` does not exist or is empty → **Mode (a): Fresh Generation**
2. If docs exist with `codedoc_version` in frontmatter → **Mode (b): Existing code-doc Output**
3. If docs exist WITHOUT codedoc frontmatter → **Mode (c): Human-Written Docs**

---

## §3.2 Mode (a): Fresh Generation

**Condition:** No existing `docs/` directory, or `docs/` exists but is empty.

**Workflow:**
1. Run full analysis pipeline (scout → analysts → synthesis)
2. Generate all core documents from templates
3. Generate optional documents based on scout findings
4. Set `codedoc_version: 1` in all generated document frontmatter
5. Write to `{project}/docs/`

**Frontmatter for fresh generation:**
```yaml
---
codedoc_version: 1
generated: 2024-01-15T10:30:00Z
project_hash: abc123  # Hash of analyzed codebase state
---
```

No special handling required — straightforward generation.

---

## §3.3 Mode (b): Existing code-doc Output

**Condition:** `docs/` exists and at least one file contains `codedoc_version` frontmatter.

This mode handles re-documentation of a codebase that was previously documented by code-doc. Human additions must be preserved.

### Step 1: Archive Existing Docs

Create a versioned archive before any modifications:

```
docs/.archive/v{N}/          # N = existing codedoc_version
├── README.md
├── architecture-guide.md
├── developer-guide.md
├── codebase-context.md
└── ...
```

Archive preserves the complete previous state for rollback if needed.

### Step 2: Detect Human Content

Identify human-authored content that must be preserved. Detection in priority order:

**2a. Explicit Markers (highest confidence)**
```markdown
<!-- human -->
This section was written by a developer and contains project-specific
context that cannot be automatically generated.
<!-- /human -->
```

**2b. Non-Template Headers**
Sections with headers not present in the template specification (from §1) are assumed human-authored:

```markdown
## Known Gotchas              <!-- Not in template → preserve -->
## Migration from v1 to v2    <!-- Not in template → preserve -->
## Troubleshooting            <!-- Not in template → preserve -->
```

**2c. Unmarked Substantive Sections**
Entire sections without codedoc markers but with substantive content (>10 lines of prose, not just code blocks):

```markdown
## Deployment Notes
<!-- No markers, but 15 lines of detailed deployment instructions -->
<!-- Preserve as human-authored -->
```

### Step 3: Regenerate Fresh Docs

Run the full analysis pipeline as if Mode (a):
- Scout the codebase
- Run analysts
- Synthesize findings
- Generate fresh documents from templates

### Step 4: Re-insert Human Blocks

After regeneration, merge preserved human content back:

**4a. Matching Header Found:**
Re-insert preserved content AFTER the generated content under the same header:

```markdown
## Configuration

<!-- Generated content -->
The application uses environment variables for configuration...

<!-- human -->
### Legacy Configuration
For deployments before v2.0, the old config.ini format is still supported...
<!-- /human -->
```

**4b. No Matching Header:**
Append at the end of the relevant document with a note:

```markdown
<!-- NOTE: original header was "Database Quirks" -->
<!-- human -->
Our Postgres setup has a non-standard schema for historical reasons...
<!-- /human -->
```

**4c. Wrap All Preserved Content:**
Ensure all preserved blocks have explicit `<!-- human -->` markers for future runs (even if they were detected heuristically this time).

### Step 5: Version Bump

Update frontmatter in all regenerated documents:

```yaml
---
codedoc_version: 3      # Was 2, now 3
generated: 2024-03-20T14:00:00Z
project_hash: def456    # Updated hash
---
```

---

## §3.4 Mode (c): Existing Human-Written Docs

**Condition:** `docs/` exists with content but NO `codedoc_version` frontmatter anywhere.

⚠️ **CRITICAL MODE** — Existing well-written documentation must NOT be destroyed.

### Preservation Rules

**Rule 1: Never Overwrite Comprehensive README**
```
if README.md exists AND (
  line_count > 50 OR
  has_multiple_h2_sections
):
  DO NOT generate a new README.md
```

**Rule 2: Never Overwrite Curated Docs**
Any existing doc that appears manually curated (based on prose quality, custom sections, detailed examples) is preserved entirely.

**Rule 3: Generate Only Gap-Filling Docs**
| Document | Generation Rule |
|----------|-----------------|
| `codebase-context.md` | Always generate — machine metadata, doesn't overlap with human prose |
| `architecture-guide.md` | Only if no equivalent exists (`ARCHITECTURE.md`, `architecture/`, `design/`) |
| `developer-guide.md` | Only if no equivalent exists (`CONTRIBUTING.md`, `DEVELOPMENT.md`, `dev-guide.md`) |

### Augmentation Strategy

Generate code-doc output to a **subdirectory** to avoid conflicts:

```
docs/
├── README.md              # Human — preserved
├── CONTRIBUTING.md        # Human — preserved
├── API.md                 # Human — preserved
└── codedoc/               # Generated — new subdirectory
    ├── INDEX.md           # Links to both human and generated docs
    ├── codebase-context.md
    ├── architecture-guide.md   # Only if gap-filling
    └── diagrams/
        └── architecture.mmd
```

### Create Index Document

Generate `docs/codedoc/INDEX.md` that provides navigation:

```markdown
---
codedoc_version: 1
generated: 2024-01-15T10:30:00Z
---
# Documentation Index

## Existing Documentation
- [README](../README.md) — Project overview and quick start
- [Contributing](../CONTRIBUTING.md) — Contribution guidelines
- [API Reference](../API.md) — API documentation

## Generated Documentation
- [Codebase Context](./codebase-context.md) — Machine-readable project metadata
- [Architecture Guide](./architecture-guide.md) — System architecture overview

*Generated by code-doc. Existing documentation preserved.*
```

### Frontmatter for Mode (c)

Only generated docs receive codedoc frontmatter:
```yaml
---
codedoc_version: 1
generated: 2024-01-15T10:30:00Z
project_hash: abc123
augmentation_mode: true   # Indicates gap-filling only
---
```

Human docs are **never modified** — no frontmatter injection.

---

## §3.5 Edge Cases

| Situation | Detection | Handling |
|-----------|-----------|----------|
| **No existing docs** | `docs/` doesn't exist | Mode (a): fresh run, version 1 |
| **Empty docs folder** | `docs/` exists but contains no `.md` files | Mode (a): treat as no docs |
| **Human docs without frontmatter** | `docs/*.md` exist, none have `codedoc_version` | Mode (c): preserve entirely, generate only to `docs/codedoc/` |
| **Code-doc output without frontmatter** | Docs match code-doc templates but missing frontmatter | Treat as version 0, Mode (b): archive to `v0/` and regenerate |
| **Human block header changed** | Preserved block's original header no longer exists in template | Append with `<!-- NOTE: original header was "X" -->` |
| **Monorepo with mixed doc states** | Different sub-projects have different doc states | Handle each sub-project independently per its own state |
| **Only README.md (no docs/ folder)** | Root `README.md` exists, no `docs/` directory | If README >50 lines: Mode (c), create `docs/codedoc/`. If <50 lines: Mode (a), wrap README content as `<!-- human -->` block in generated README |
| **Partial codedoc output** | Some docs have `codedoc_version`, others don't | Mode (b) for the project, but preserve non-codedoc files as human content |
| **docs/ with only images/assets** | `docs/` contains only non-markdown files | Mode (a): treat as no documentation |
| **Nested docs structure** | `docs/` has subdirectories like `docs/api/`, `docs/guides/` | Scan recursively for frontmatter; preserve nested human structure in Mode (c) |

### Mode Detection Flowchart

```
┌─────────────────────────────────────────────────────────────────┐
│                    Start: Check docs/ state                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   ┌──────────────────┐
                   │ docs/ exists?    │
                   └──────────────────┘
                    │              │
                   No             Yes
                    │              │
                    ▼              ▼
              ┌──────────┐  ┌───────────────────┐
              │ Mode (a) │  │ Has .md files?    │
              │ Fresh    │  └───────────────────┘
              └──────────┘      │           │
                               No          Yes
                                │           │
                                ▼           ▼
                          ┌──────────┐  ┌───────────────────────┐
                          │ Mode (a) │  │ Any codedoc_version?  │
                          │ Fresh    │  └───────────────────────┘
                          └──────────┘      │               │
                                           No              Yes
                                            │               │
                                            ▼               ▼
                                    ┌─────────────┐  ┌─────────────┐
                                    │  Mode (c)   │  │  Mode (b)   │
                                    │ Human Docs  │  │ Code-doc    │
                                    └─────────────┘  └─────────────┘
```

---

## Summary

| Mode | Condition | Action | Output Location |
|------|-----------|--------|-----------------|
| **(a) Fresh** | No docs or empty docs/ | Full generation | `docs/` |
| **(b) Code-doc Output** | `codedoc_version` present | Archive → Regenerate → Merge human blocks | `docs/` (in-place) |
| **(c) Human-Written** | Docs exist, no codedoc markers | Preserve all → Generate gaps only | `docs/codedoc/` |
