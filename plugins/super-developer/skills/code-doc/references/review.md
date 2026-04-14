# Review Protocol

This document defines the quality assurance pipeline for generated documentation. Three Sonnet-class reviewers run in parallel, each with explicit checklists. Findings are merged, deduplicated, and fixed by severity.

---

## §1 Three Parallel Reviewers

All reviewers are spawned via `task(agent_type='explore')` and receive:
- **Generated docs**: all `.md` files produced by the generation phase
- **Project source path**: the root of the target codebase
- **Native extractor output**: JSON/Markdown from TypeDoc, Sphinx, Godoc, etc. (ground truth for names/signatures)

Reviewers run in parallel. Their findings are merged by the orchestrator.

---

### §1.1 Accuracy Reviewer

**Purpose**: Verify all factual claims in documentation match the source code.

#### Checklist

| # | Check | Verification Method |
|---|-------|---------------------|
| 1 | Every function/method name mentioned exists in source | `grep -r "function_name"` in source |
| 2 | Every file path mentioned exists on filesystem | `test -f <path>` or glob match |
| 3 | Every module description matches actual code behavior | Read source, compare semantics |
| 4 | Code snippets are syntactically correct | Language-specific syntax check |
| 5 | Mermaid diagrams match actual module relationships | Verify edges against `import`/`require`/`from` statements |
| 6 | Dependency lists match package manifest | Cross-check `package.json`, `requirements.txt`, `go.mod`, etc. |
| 7 | API signatures match native extractor output | Extractor JSON is ground truth |
| 8 | Version numbers, URLs, config values are current | Check package.json version, validate URLs exist |

#### Prompt Template

```markdown
# Accuracy Review Task

You are reviewing generated documentation for factual accuracy.

## Inputs
- **Docs directory**: {{docs_path}}
- **Source directory**: {{source_path}}
- **Native extractor output**: {{extractor_output_path}} (ground truth for function names, signatures, types)

## Your Checklist
For each generated doc, verify:

1. **Function/method names**: Every function mentioned must exist. Use `grep -rn "def function_name\|function function_name\|func function_name"` to verify.

2. **File paths**: Every path like `src/utils/helpers.ts` must exist. Use `test -f {{source_path}}/path` or glob.

3. **Module descriptions**: Read the actual source file. Does the description match what the code does?

4. **Code snippets**: Check syntax. A Python snippet with `def foo():` followed by unindented code is wrong.

5. **Mermaid diagrams**: For each arrow `A --> B`, verify A actually imports/calls B. Check import statements.

6. **Dependencies**: Compare listed deps against:
   - `package.json` (JS/TS)
   - `requirements.txt` / `pyproject.toml` (Python)
   - `go.mod` (Go)
   - `pom.xml` / `build.gradle` (Java)

7. **Native extractor cross-check**: If extractor says `getUserById(id: string): User`, docs must not say `getUserById(userId: number)`.

8. **URLs/versions**: Ping URLs (or note if unreachable). Check version in package manifest.

## Output Format
```
## Accuracy Review

### 🔴 Blockers
- **[doc-name.md, line ~N]:** [specific wrong reference] — actual: [correct value from source]

### 🟡 Warnings
- **[doc-name.md, section]:** [issue description]

### ℹ️ Info
- **[doc-name.md]:** [suggestion]

### Verdict: PASS | BLOCK
```

A single 🔴 Blocker means Verdict: BLOCK.
```

---

### §1.2 Completeness Reviewer

**Purpose**: Ensure documentation covers all significant parts of the codebase with no gaps.

#### Checklist

| # | Check | Verification Method |
|---|-------|---------------------|
| 1 | Every entry point has a section | Entry points from scout → check architecture/developer guide |
| 2 | All modules with >10 files are mentioned | `find` + count → grep in architecture guide |
| 3 | All public API endpoints documented | Route definitions → api-reference.md coverage |
| 4 | External dependencies listed | Package manifest → developer guide deps section |
| 5 | File inventory matches filesystem | `codebase-context.md` count vs `glob **/*` count |
| 6 | No empty/placeholder sections | Grep for "TODO", "TBD", "Coming soon", empty headers |
| 7 | Build/test/run commands documented | Developer guide has setup, build, test, run sections |
| 8 | All Mermaid diagrams referenced exist | Every `See [diagram-name]` has corresponding ```mermaid block |

#### Prompt Template

```markdown
# Completeness Review Task

You are reviewing generated documentation for coverage gaps.

## Inputs
- **Docs directory**: {{docs_path}}
- **Source directory**: {{source_path}}
- **Native extractor output**: {{extractor_output_path}}
- **Scout report**: {{scout_report_path}} (detected entry points, modules, frameworks)

## Your Checklist

1. **Entry point coverage**: Scout identified entry points (e.g., `src/index.ts`, `main.py`, `cmd/server/main.go`). Each must appear in architecture-guide.md or developer-guide.md.

2. **Large module coverage**: Find directories with >10 source files:
   ```bash
   find {{source_path}} -type d -exec sh -c 'count=$(find "$1" -maxdepth 1 -name "*.ts" -o -name "*.py" -o -name "*.go" | wc -l); [ $count -gt 10 ] && echo "$1: $count files"' _ {} \;
   ```
   Each should be mentioned in architecture-guide.md.

3. **API endpoint coverage**: If scout detected routes (Express, FastAPI, etc.), every route should be in api-reference.md. Cross-check:
   - Express: `grep -r "app\.\(get\|post\|put\|delete\)" {{source_path}}`
   - FastAPI: `grep -r "@app\.\(get\|post\|put\|delete\)" {{source_path}}`

4. **Dependency completeness**: Every non-dev dependency in package manifest should appear in developer-guide.md or architecture-guide.md.

5. **File inventory accuracy**: Compare codebase-context.md file list against:
   ```bash
   find {{source_path}} -type f \( -name "*.ts" -o -name "*.py" -o -name "*.go" \) | wc -l
   ```
   Allow ±5% variance. Flag if >10% mismatch.

6. **No placeholders**: Search for incomplete sections:
   ```bash
   grep -rn "TODO\|TBD\|FIXME\|Coming soon\|^\s*$" {{docs_path}}/*.md
   ```
   Empty sections under headers = blocker.

7. **Developer guide commands**: Must have:
   - Prerequisites/setup section
   - Build command
   - Test command
   - Run/start command

8. **Diagram references**: Every "See Figure X" or "See [X diagram]" must have a corresponding ```mermaid block.

## Output Format
```
## Completeness Review

### 🔴 Blockers
- **[doc-name.md, line ~N]:** [missing coverage] — expected: [what should be there]

### 🟡 Warnings
- **[doc-name.md, section]:** [issue description]

### ℹ️ Info
- **[doc-name.md]:** [suggestion]

### Verdict: PASS | BLOCK
```

Missing entry point or major module = 🔴 Blocker.
```

---

### §1.3 Clarity Reviewer

**Purpose**: Ensure documentation is clear, consistent, and usable by developers new to the codebase.

#### Checklist

| # | Check | Verification Method |
|---|-------|---------------------|
| 1 | Developer guide: self-sufficient setup | Follow steps without external knowledge |
| 2 | Architecture guide: 10-minute comprehension | Read through, assess cognitive load |
| 3 | README: 30-second project understanding | First 3 paragraphs convey purpose + quickstart |
| 4 | No contradictions between docs | Compare setup steps, terminology across docs |
| 5 | Consistent terminology | Same component = same name everywhere |
| 6 | Appropriate detail level | Not too verbose (>50 lines for simple concept), not too terse (<5 lines for complex) |
| 7 | Acronyms defined on first use | Every acronym has expansion on first occurrence |
| 8 | Logical section ordering | Prerequisites before steps, concepts before details |

#### Prompt Template

```markdown
# Clarity Review Task

You are reviewing generated documentation for clarity and usability.

## Inputs
- **Docs directory**: {{docs_path}}
- **Source directory**: {{source_path}} (for context on project complexity)

## Your Checklist

1. **Developer guide self-sufficiency**: Mentally walk through as a new developer:
   - Are all prerequisites listed (Node version, Python version, etc.)?
   - Are environment variables documented?
   - Can you run the project with ONLY these instructions?
   - Flag any step that requires "tribal knowledge" not in the doc.

2. **Architecture guide comprehension**: Read architecture-guide.md:
   - After 10 minutes, can you explain the system to someone else?
   - Is the high-level structure clear before diving into details?
   - Are relationships between components explained, not just listed?

3. **README effectiveness**: First 3 paragraphs must answer:
   - What does this project do?
   - Who is it for?
   - How do I get started (quickstart link or 3-line snippet)?

4. **Cross-document consistency**: Check for contradictions:
   - Setup steps in README vs developer-guide.md
   - Module names in architecture-guide.md vs codebase-context.md
   - Config file paths mentioned in multiple places

5. **Terminology consistency**: Track key terms:
   - Is `UserService` also called "user handler" somewhere? Flag it.
   - Is the database called "PostgreSQL" in one place and "Postgres" in another? Standardize.

6. **Detail calibration**:
   - Simple utility function: 2-5 lines description is fine
   - Core business logic module: needs more depth
   - Flag sections that are walls of text (>50 lines without headers)
   - Flag sections that are suspiciously brief for complex topics

7. **Acronym definitions**: First occurrence of each acronym must expand it:
   - Good: "Object-Relational Mapping (ORM)"
   - Bad: "Uses the ORM to query..." (ORM never defined)

8. **Logical ordering**:
   - Prerequisites before installation steps
   - Concepts/overview before detailed API
   - Common tasks before advanced configuration

## Output Format
```
## Clarity Review

### 🔴 Blockers
- **[doc-name.md, line ~N]:** [clarity issue blocking comprehension]

### 🟡 Warnings
- **[doc-name.md, section]:** [issue description]

### ℹ️ Info
- **[doc-name.md]:** [suggestion]

### Verdict: PASS | BLOCK
```

Developer guide that cannot be followed independently = 🔴 Blocker.
Contradictions between docs = 🔴 Blocker.
```

---

## §2 Finding Severity

| Severity | Icon | Definition | Examples | Action |
|----------|------|------------|----------|--------|
| **BLOCKER** | 🔴 | Factually wrong code reference OR missing major module/entry point | Wrong function name (`getUser` → actual is `fetchUser`), non-existent file path (`src/auth.ts` doesn't exist), entry point `main.go` not documented | Must fix before writing. Triggers re-review. |
| **WARNING** | 🟡 | Minor inaccuracy, unclear wording, incomplete detail | Typo in config path, unclear sentence, missing optional parameter in signature | Fix inline. No re-review. |
| **INFO** | ℹ️ | Style suggestion, formatting, nice-to-have | "Consider adding example", "Could reorder sections", "Diagram would help here" | Fix if time permits. |

### Severity Decision Tree

```
Is it factually wrong about code? (wrong name, wrong path, wrong signature)
├─ Yes → 🔴 BLOCKER
└─ No
   Is a major component/entry point missing from docs?
   ├─ Yes → 🔴 BLOCKER
   └─ No
      Does it contradict another document?
      ├─ Yes → 🔴 BLOCKER (clarity)
      └─ No
         Is it unclear, incomplete, or has minor inaccuracy?
         ├─ Yes → 🟡 WARNING
         └─ No → ℹ️ INFO
```

---

## §3 Fix Loop

The orchestrator manages the fix loop after collecting findings from all 3 reviewers.

### Algorithm

```
iteration = 0
MAX_ITERATIONS = 2

while iteration < MAX_ITERATIONS:
    findings = merge_and_deduplicate(
        accuracy_reviewer.findings,
        completeness_reviewer.findings,
        clarity_reviewer.findings
    )
    
    blockers = [f for f in findings if f.severity == 'BLOCKER']
    warnings = [f for f in findings if f.severity == 'WARNING']
    infos = [f for f in findings if f.severity == 'INFO']
    
    if not blockers:
        # Fix warnings inline, skip re-review
        fix_inline(warnings)
        fix_if_quick(infos)
        break
    
    # Fix all blockers
    fix_all(blockers)
    iteration += 1
    
    if iteration < MAX_ITERATIONS:
        # Re-run all 3 reviewers
        re_review()

if iteration == MAX_ITERATIONS and blockers:
    # Append Known Issues section to README
    append_known_issues(blockers)
```

### Fix Loop Rules

1. **Blockers exist**: Fix all blockers, re-run all 3 reviewers
2. **Only warnings**: Fix inline without re-review
3. **Max 2 iterations**: If blockers remain after 2 iterations, proceed with `## Known Issues`
4. **INFO findings**: Fix only if they don't require regeneration; otherwise skip

### Known Issues Section Format

If blockers remain after 2 iterations, append to README.md:

```markdown
## Known Issues

The following documentation issues were identified but could not be automatically resolved:

| Issue | Document | Description |
|-------|----------|-------------|
| Unverified function reference | architecture-guide.md | `processPayment()` mentioned but could not verify in source |
| Missing module coverage | architecture-guide.md | `internal/legacy/` module not fully documented |

These issues may be resolved manually or in a future documentation update.
```

---

## §4 Why No Skeptic Agent

### Cost/Benefit Analysis for Documentation

| Factor | Code Review | Documentation Review |
|--------|-------------|---------------------|
| **Error impact** | Bug ships to production | Developer reads source, self-corrects |
| **Recovery cost** | Hotfix, rollback, incident | Mental model correction in seconds |
| **Verification difficulty** | Logic, state, concurrency | String matching, file existence |
| **Opus-class value** | High (catches subtle bugs) | Low (simple verification suffices) |

### Rationale

Documentation errors are **low-stakes** compared to code bugs:

- **Wrong function name in docs** → Developer looks at source, sees correct name, corrects mental model in seconds. Minor friction, no production impact.
  
- **Wrong function name in code review** → Bug ships to production. Customer-facing error. Incident response. Postmortem.

The verification needed for documentation is primarily **mechanical**:
- Does this string exist in source? (grep)
- Does this file exist? (test -f)
- Does this signature match? (diff against extractor output)

An Opus-class Skeptic agent excels at **subtle logical reasoning**, which is rarely needed for documentation verification. Three Sonnet-class reviewers with **explicit checklists** provide sufficient coverage at ~1/10th the cost.

### When Skeptic WOULD Be Justified

- Documentation that affects security (API authentication flows)
- Documentation that affects financial outcomes (billing integration guides)
- Regulated industries requiring audit-ready documentation

For general codebase documentation, the three-reviewer model is appropriate.

---

## §5 Review Output Format

### Individual Reviewer Output

Each reviewer produces:

```markdown
## [Accuracy/Completeness/Clarity] Review

**Reviewed documents**: README.md, architecture-guide.md, developer-guide.md, codebase-context.md
**Source path**: /path/to/project
**Extractor output**: /path/to/extractor-output.json (if applicable)

### 🔴 Blockers
- **[architecture-guide.md, line ~42]:** References `AuthController.validateToken()` — actual: `AuthService.verifyToken()` per source
- **[developer-guide.md, line ~15]:** Path `src/config/database.ts` does not exist — actual: `src/db/config.ts`

### 🟡 Warnings
- **[README.md, Quick Start]:** Missing `npm install` step before `npm run dev`
- **[architecture-guide.md, Data Flow]:** Diagram shows `API → DB` but actual flow is `API → Cache → DB`

### ℹ️ Info
- **[codebase-context.md]:** Consider grouping files by module instead of flat list
- **[architecture-guide.md]:** A sequence diagram would clarify the auth flow

### Verdict: BLOCK

**Blocker count**: 2
**Warning count**: 2
**Info count**: 2
```

### Merged Orchestrator Report

The orchestrator merges all 3 reports:

```markdown
# Documentation Review Summary

**Review iteration**: 1 of 2
**Timestamp**: 2024-01-15T10:30:00Z

## Findings by Severity

### 🔴 Blockers (3) — Must fix, will re-review

| # | Document | Line | Issue | Source | Reviewer |
|---|----------|------|-------|--------|----------|
| 1 | architecture-guide.md | ~42 | Wrong method name: `AuthController.validateToken()` | Actual: `AuthService.verifyToken()` | Accuracy |
| 2 | developer-guide.md | ~15 | Non-existent path: `src/config/database.ts` | Actual: `src/db/config.ts` | Accuracy |
| 3 | architecture-guide.md | — | Missing `payment/` module (47 files) | Entry point: `payment/processor.ts` | Completeness |

### 🟡 Warnings (4) — Fix inline

| # | Document | Section | Issue | Reviewer |
|---|----------|---------|-------|----------|
| 1 | README.md | Quick Start | Missing `npm install` step | Completeness |
| 2 | architecture-guide.md | Data Flow | Diagram missing cache layer | Accuracy |
| 3 | developer-guide.md | Setup | Env vars not fully documented | Clarity |
| 4 | codebase-context.md | — | File count off by 12% | Completeness |

### ℹ️ Info (2) — Fix if time permits

| # | Document | Suggestion | Reviewer |
|---|----------|------------|----------|
| 1 | codebase-context.md | Group files by module | Completeness |
| 2 | architecture-guide.md | Add auth sequence diagram | Clarity |

## Verdicts

| Reviewer | Verdict |
|----------|---------|
| Accuracy | BLOCK |
| Completeness | BLOCK |
| Clarity | PASS |

## Action Plan

1. **Fix blockers 1-3** (estimated: 3 edits)
2. **Re-run all 3 reviewers** (iteration 2)
3. **If pass**: fix warnings inline, commit
4. **If still blocked**: fix, append Known Issues, commit
```

---

## §6 Integration with Generation Phase

### Handoff from Generation

Generation phase produces:
- `docs/` directory with all generated Markdown files
- `extractor-output/` directory with native tool outputs (if `--with-build` was used)
- `scout-report.md` with detected entry points, modules, frameworks

### Reviewer Invocation

```python
# Orchestrator spawns 3 reviewers in parallel
accuracy_task = task(
    agent_type='explore',
    prompt=ACCURACY_PROMPT.format(
        docs_path='docs/',
        source_path=project_root,
        extractor_output_path='extractor-output/'
    )
)

completeness_task = task(
    agent_type='explore',
    prompt=COMPLETENESS_PROMPT.format(
        docs_path='docs/',
        source_path=project_root,
        extractor_output_path='extractor-output/',
        scout_report_path='scout-report.md'
    )
)

clarity_task = task(
    agent_type='explore',
    prompt=CLARITY_PROMPT.format(
        docs_path='docs/',
        source_path=project_root
    )
)

# Wait for all, merge findings
findings = merge_findings(
    accuracy_task.result,
    completeness_task.result,
    clarity_task.result
)
```

### Handoff to Write Phase

After review passes (or max iterations reached):
- All `.md` files in `docs/` are finalized
- Orchestrator commits with appropriate message
- If Known Issues appended, commit message notes it

---

## Summary

| Component | Specification |
|-----------|---------------|
| **Reviewers** | 3 Sonnet-class (Accuracy, Completeness, Clarity) |
| **Execution** | Parallel via `task(agent_type='explore')` |
| **Checklists** | Explicit, verifiable checks per reviewer |
| **Ground truth** | Native extractor output for names/signatures |
| **Severity levels** | 🔴 BLOCKER, 🟡 WARNING, ℹ️ INFO |
| **Fix loop** | Max 2 iterations, then Known Issues fallback |
| **Skeptic agent** | Not used (cost/benefit inappropriate for docs) |
| **Output format** | Structured Markdown with tables |
