# Local Gated Actions

Load only after local setup/review/report is complete and the user reaches the gated action phase. This reference owns local fix, verification, commit, details, and abort behavior.

Local mode is ordinary code review. It does not impose planned-feature Slice/proof/report/audit obligations and does not refresh planned-feature package evidence. If the user wants governed planned-feature fix/proof/report handling, switch to pipeline mode.

## Actions

Only proceed when the user responds with one keyword:

| Keyword | Action |
|---|---|
| `fix` | Delegate confirmed 🔴/🟠 fixes, then run Fix Verification Review. |
| `commit` | Stage/commit reviewed state as-is only when no 🔴/🟠 issues remain and state revalidation passes. |
| `details <N>` | Expand finding N without mutating state. |
| `abort` | No action. |

Any other response requires clarification. Never treat ambiguity, silence, or partial confirmation as approval.

## Local State Gate

Before mutating files, staging, committing, or reporting post-fix readiness, revalidate metadata captured in `local-workflow.md`:

- current branch and `HEAD` SHA still match, except approved local fix commits from this flow;
- reviewed file list and diff checksum still match unchanged findings;
- staged content still matches when `SCOPE="staged"`;
- no new unreviewed files or broadened diff appeared;
- base ref/SHA still match for branch-diff reviews.

Reject stale or broadened state and instruct the user to rerun review.

## Workflow A — `fix`

Use two delegated roles:

- Fix Implementer: applies bounded fixes for confirmed findings.
- Fix Verification Reviewer: uses `fix-verification.md` to verify closure and serious-regression sniff.

The main agent does not implement substantive code, test, or documentation fixes inline. It may apply only trivial mechanical typo/formatting fixes and must report why they were behavior-preserving.

Pass the Fix Implementer:

- confirmed 🔴/🟠 findings with dedupe keys, Skeptic verdicts, evidence, and recommendations;
- reviewed-state metadata;
- target paths and exact local scope;
- user/repository/mode constraints;
- any approved user-decision card outcomes;
- instruction to avoid unrelated cleanup, broad rewrites, or touching files outside target paths unless required to close the finding.

The Fix Implementer must reproduce or locate each finding, state the bug class/equivalence class, add or adjust targeted regression evidence where applicable, run targeted checks, and report unresolved blockers.

After fixes, load `fix-verification.md`. Post-fix commit/readiness requires all assigned findings `closed`, regression sniff `pass`, no unresolved widening trigger, and a passing Local State Gate.

After one widened verification pass, stop instead of widening recursively if more scope is still needed or no bounded seam remains. Report unresolved findings and exact unreviewed scope.

## Workflow B — `commit`

Allowed only when no 🔴/🟠 issues remain. Run the Local State Gate immediately before staging or committing.

```bash
# Only stage files from the reviewed diff. Do not use git add -A.
if [ "$SCOPE" != "staged" ]; then
  $DIFF_CMD --name-only | xargs git add --
fi

git commit -m "<concise summary of changes>"
```

If serious issues exist, refuse and report: `Blockers detected. Resolve before committing. Run review again after fixing, or respond fix to attempt delegated fixes.`

## Workflow C — `details <N>`

Expand finding N with developer-facing context, code snippet, evidence, Skeptic confirmation summary for serious findings, and recommendation. Do not expose internal coverage rows, raw tags, dedupe keys, or state/fix metadata unless the user explicitly asks for diagnostics. Do not mutate files or state.

## Workflow D — `abort`

Close cleanly without mutating files, staging area, commits, proof/report files, or review metadata.

## Blanket Mode

When the user has authorized blanket mode, unambiguous serious fixes may be delegated silently after the Local State Gate passes. Product/architecture choices still require a user-decision card through `decision-filter.md` and `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/decision-prompts.md`.

Blanket mode does not bypass the baseline security/privacy/safety sniff, Skeptic verification, Local State Gate, delegated Fix Verification Review, blocker commit refusal, or repeated-widening stop.
