# Feature Source Publication

## Boundary

This shared reference owns planned-feature source publication cadence. It does not authorize package commits,
artifact-sidecar publication, target publication, planned-hotfix publication, release, deployment, or cleanup. Load it
at policy selection and at each scheduled feature-source push; callers carry the selected packet instead of restating
cadence rules elsewhere.

## Cadence Contract

Record exactly one policy for `feature/<feature>`. The user selects any remote cadence; never choose one for them. A
generic publish request without a cadence needs a focused choice before execution approval.

- `local-only` — default unless the user explicitly authorized remote source publication. Perform no fetch,
  `ls-remote`, or push. Local commits, retained refs/worktrees, verification, and downstream readiness continue.
- `per-package` — publish after each accepted package is merged and post-merge freshness closes.
- `milestone` — before execution, list precise named triggers, such as integration of specified stable package IDs.
  Triggers need not partition or cover every package. Each checkpoint is due once its trigger is satisfied and prior
  scheduled gates have closed. The push publishes the whole approved integration state then, including
  same-requirement focused-reviewed continuation packages, not a cherry-picked subset. New package IDs alone do not
  change authorization; changed feature scope, destination, or checkpoint timing does.
- `final` — publish only from the exact final freeze with sibling `review-code` `CLEAN` and `audit` `PASS`.

A remote policy is valid only when the user's approval names remote `origin`, destination
`refs/heads/feature/<feature>`, the exact command below, the selected cadence, milestone triggers when applicable,
and the final catch-up below. Plan approval does not approve execution or publication. Execution approval includes
publication only when this complete remote scope is visible in the approval request. Never infer publication from a
feature ref, package merge, prior checkpoint, target delivery, or sidecar policy.

For every remote cadence, visibly include final catch-up authorization: after same-freeze `CLEAN` + `PASS`, push the
accepted final state only if its SHA differs from the last successful source checkpoint. This covers integrated
repairs and work after the last milestone without ad hoc repair pushes. `final` performs its normal single final push;
`local-only` never gains a network action. Preserve the last successful checkpoint in existing status, not a new
ledger; recover uncertain history before any scheduled action. Do not infer new permission at final time.

A non-due gate performs no network action and never blocks locally verified integration or downstream readiness. At a
due remote gate, push, credential, network, non-fast-forward, missing remote result, or SHA mismatch failure stops that
gate and later progression; preserve all local commits, package refs/worktrees, integration, and artifact safety nets.
Never force.

## Scheduled Feature Push

Run only from the clean integration worktree after the selected gate is due:

```bash
set -euo pipefail
cd "$PROJECT_ROOT/.worktrees/<feature>/merge"
test "$(git symbolic-ref --short HEAD)" = "feature/<feature>"
test -z "$(git status --porcelain)"
LOCAL_SHA="$(git rev-parse HEAD)"
git push origin "HEAD:refs/heads/feature/<feature>"
REMOTE_LINE="$(git ls-remote --heads origin refs/heads/feature/<feature>)"
test -n "$REMOTE_LINE"
REMOTE_SHA="${REMOTE_LINE%%$'\t'*}"
test "$REMOTE_SHA" = "$LOCAL_SHA"
```

The gate succeeds only after remote SHA equals the exact local SHA. Record local and verified remote SHA in existing
execution status/report output; do not create another ledger or receipt.

## Independent Boundaries

- Package branches remain local safety nets; publication pushes only `feature/<feature>`.
- Target merge/push requires separate exact approval and is never implied by feature-source publication.
- `artifacts/<feature>` is a separate sidecar action/ref with separate approval.
- Planned production hotfixes create no feature ref and use only the separately approved non-force `hotfix/<name>`
  source gate from their Execution Contract.

## Stop if

- More than one cadence is selected, remote publication was requested without a user-selected cadence, a remote
  cadence lacks explicit authorization, or a milestone trigger/checkpoint is incomplete or ambiguous.
- The integration checkout/ref/state does not match the due gate, or `final` lacks same-freeze `CLEAN` and `PASS`.
- Any scheduled remote operation fails or cannot verify remote SHA; retain all safety nets and never silently
  downgrade to `local-only`.
