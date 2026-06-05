# Local Code Review Workflow

Local mode owns offline diff setup, report, local fix, commit, details, and abort gates. It does not impose planned-feature Slice/proof/report/audit obligations or refresh package evidence; switch to pipeline mode for governed planned-feature fixes.

Requirement: `git` installed and inside a Git repository.

If the user provides intent, constraints, known tradeoffs, or focus areas, pass them to reviewers and fix agents to reduce false positives.

## Scope and Setup

Detect review scope in priority order:

```bash
STAGED=$(git diff --cached --stat)
UNSTAGED=$(git diff --stat)

if [ -n "$STAGED" ]; then
  SCOPE="staged"
  DIFF_CMD="git diff --cached"
elif [ -n "$UNSTAGED" ]; then
  SCOPE="uncommitted"
  DIFF_CMD="git diff HEAD"
else
  DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
  SCOPE="branch"
  DIFF_CMD="git diff origin/${DEFAULT_BRANCH}...HEAD"
fi
```

Preflight:

```bash
git rev-parse --is-inside-work-tree
$DIFF_CMD
$DIFF_CMD --stat
git branch --show-current
git log --oneline -10
```

Hard stops: not a Git repo or empty diff.

Capture reviewed-state metadata: current branch, `HEAD` SHA, base ref/SHA for branch diff, scope, reviewed file list/status, diff checksum or saved diff, and staged checksum when reviewing staged changes.

Report scope before reviewer dispatch:

```text
Review Scope: <staged | uncommitted | branch diff against origin/<branch>>
Files changed: <count>
Insertions: +<count>  Deletions: -<count>
```

After setup, return to the main skill for reviewer dispatch.

## Review Report

Mode values for the main report template:

- Header: `Local Code Review`.
- Metadata: `**Branch:** <current branch> | **Scope:** <scope> | **Files:** <count> changed`.
- Verdict line: none in the body; state the verdict after the report.
- Footer: none.

Verdicts:

- `CLEAN` — no confirmed 🔴/🟠 findings.
- `ISSUES FOUND` — one or more confirmed 🔴/🟠 findings.

Full stop after report. Await one explicit action keyword.

## Action Keywords

| Keyword | Action |
|---|---|
| `fix` | Delegate confirmed 🔴/🟠 fixes, then run the main skill's Fix Verification Gate. |
| `commit` | Stage/commit reviewed state as-is only when no confirmed 🔴/🟠 issues remain and Local State Gate passes. |
| `details <N>` | Expand finding N without mutating state. |
| `abort` | No action. |

Any other response requires clarification. Never treat ambiguity, silence, or partial confirmation as approval.

## Local State Gate

Before mutating files, staging, committing, or claiming post-fix readiness, revalidate captured metadata:

- branch and `HEAD` SHA still match, except approved local fix commits from this flow;
- reviewed file list and diff checksum still match unchanged findings;
- staged content still matches when `SCOPE="staged"`;
- no new unreviewed files or broadened diff appeared;
- base ref/SHA still match for branch-diff reviews.

Reject stale or broadened state and instruct the user to rerun review.

## Fix Action

The main agent does not implement substantive code/test/docs fixes inline. Delegate a Fix Implementer with:

- confirmed findings with dedupe keys, Skeptic verdicts, evidence, recommendations, and approved decision-card outcomes;
- reviewed-state metadata, target paths, exact local scope, user/repo/mode constraints;
- instruction to avoid unrelated cleanup, broad rewrites, or files outside target paths unless required to close the finding.

The Fix Implementer must reproduce or locate each finding, state the bug class/equivalence class, add or adjust targeted regression evidence when applicable, run targeted checks, and report unresolved blockers.

After fixes, run the main skill's Fix Verification Gate. Local post-fix commit/readiness requires all assigned findings closed, regression sniff pass, no unresolved widening trigger, and Local State Gate pass. After one widened verification pass, stop instead of widening recursively if more scope is still needed or no bounded seam remains.

## Commit, Details, Abort, Blanket Mode

`commit` is allowed only when no confirmed 🔴/🟠 issues remain and Local State Gate passes:

```bash
if [ "$SCOPE" != "staged" ]; then
  $DIFF_CMD --name-only | xargs git add --
fi
git commit -m "<concise summary of changes>"
```

Do not use `git add -A`. If serious issues exist, refuse and offer `fix` or rerun after manual repairs.

`details <N>` expands finding N with code snippet, evidence, Skeptic summary for serious findings, and recommendation. Do not expose internal coverage rows, raw tags, dedupe keys, or state/fix metadata unless requested for diagnostics.

`abort` closes cleanly without mutating files, staging area, commits, proof/report files, or review metadata.

Blanket mode may delegate unambiguous serious fixes after Local State Gate passes. Product/architecture choices still require the main skill's decision-card rule. Blanket mode never bypasses security/privacy/safety sniff, Skeptic verification, Local State Gate, Fix Verification Gate, blocker commit refusal, or repeated-widening stop.
