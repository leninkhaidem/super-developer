# Tool Usage Reference

## Command Safety and Runtime Envelope

- Treat plan-provided commands as executable input and screen them before running or delegating.
- Stop for explicit approval before destructive, externally visible, credential/network-sensitive,
  dependency-installing, service-starting, or out-of-scope commands.
- For each nontrivial command, carry a stable identity and record command, cwd, provenance, scope, expected
  writes, timeout budget, progress/completion signal, termination method, and cleanup obligation.
- Use exact budgets from the accepted project workflow. Without one, choose a conservative bound only for a
  deterministic local command; stop before potentially long, live, browser, service, or shared-data execution.
- Bound actions and awaited barriers more narrowly than their parent scenario or suite. A failed action must not
  inherit the entire outer timeout, and a running process without an observable completion signal is not done.
- On timeout, cancellation, or interruption, terminate owned descendants/process groups, await termination, and
  verify cleanup. Timeout, uncertain termination, or uncertain cleanup is non-pass evidence.
- Do not increase a timeout unless observed workload justifies it. Never use a larger timeout to mask a bad
  selector, unresolved barrier, deadlock, missing precondition, or absent progress signal.
- Do not repeat the same failing command or assertion without a relevant code, config, fixture, environment, or
  diagnostic-strategy change. A bounded diagnostic rerun must name the new signal it is intended to collect.
- Return control after a bounded stage or failure; do not hide repeated follow-up execution inside one opaque,
  long-running command or tool call.
- Prefer helper scripts over ad hoc parsing for mechanical artifact checks.
- Helper success is not semantic proof that code works; package verification, review-code, and audit still gate
  completion.

## Semgrep Helper Boundary

When Semgrep verification is enabled by an approved workflow, load `semgrep.md` at the action point
and use the shipped helper commands for indexing, retrieval, scanning, summarizing, listing, and
showing findings. Scan only through
`python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/semgrep_rules.py" scan ...`; agents must not run
raw direct `semgrep` scans. Do not hand-assemble Semgrep shell commands, read raw Semgrep JSON
wholesale, or perform hidden rule clone/pull/network sync; routine scans are local-only.

## `sliceproof.py`

`sliceproof.py` is the planned-feature mechanical helper. When roots differ, pass both as absolute
paths so the command is location-independent: `$ARTIFACT_ROOT` is the artifact worktree
(`.worktrees/<feature>/artifacts`) and `$CODE_ROOT` is the code worktree being checked — a package
worktree for package checks, the integration/top worktree for `validate-final` and any deliverable-matrix
file evidence. Treat `--artifact-root` and `--code-root` as the trust anchors; a report's `Worktree` field
is runtime metadata for humans/auditors, not evidence-root authority. Do not pass `--code-root "."` from
the project root for integrated checks: the feature's files live in a worktree, not the root, so file-evidence
existence checks would resolve against the wrong tree. The `.tasks/<feature>/tasks.json` argument is always
artifact-root-relative. Omit both flags only for current-root stores, where both default to the current directory.

Read-only checks:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-plan \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" \
  ".tasks/<feature>/tasks.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-proof \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" \
  ".tasks/<feature>/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-package-complete \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" \
  ".tasks/<feature>/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-final \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" \
  ".tasks/<feature>/tasks.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" emit-state-binding \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" \
  ".tasks/<feature>/tasks.json" --package WP1 \
  --worktree "$REVIEWED_WORKTREE" --git-ref "$REVIEWED_GIT_REF" \
  --commit "$REVIEWED_COMMIT" --verified-at "$VERIFIED_AT"
```

`validate-package-complete` and `validate-final` require the canonical package report, including a structurally
valid `### Test Review Scope`; reports without it are invalid and must be refreshed rather than bypassed. They
return JSON on stdout when successful. On failure, they return JSON on stderr with `errors` and a top-level
`advisories` array. `context_only_slice_drift` advisories are non-blocking by default and must still be routed to affected-surface classification;
`validate-final` aggregates advisories across packages and includes them even when hard errors also exist.

Read-only emit command:

`emit-state-binding` writes the canonical Markdown `## State Binding` block to stdout for verifiers to
paste verbatim. It requires `--package` plus runtime metadata flags `--worktree`, `--git-ref`, `--commit`,
and `--verified-at`; it uses the same formatter as validation, and the verifier computes no digests.

Write command:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" create-proof \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" \
  ".tasks/<feature>/tasks.json" --package WP1
```

## Mechanical Boundaries

`validate-plan` checks:

- lightweight registry shape;
- safe repo-relative SPEC, Slice, package, proof, and report paths;
- State Binding grammar delimiter rejection (`|`, `=`, `; `) for assigned Slice paths;
- package dependency references and cycles;
- package Markdown required sections;
- package Markdown proof/report/dependency references;
- assigned Slice H3 IDs under `## Shared Understanding`.

`create-proof` writes only the declared proof Markdown placeholder for one package. Existing filled,
edited, or drifted proof content is never overwritten silently.

`validate-proof` checks one package proof mechanically:

- required sections and closure tables;
- required Slice rows and verification expectation rows;
- duplicate, unexpected, unsupported, placeholder, or blocking rows;
- explicit approval, provenance, and scope for deferrals, non-applicable rows, gaps, or deviations;
- non-placeholder command/file/completion evidence.

`validate-package-complete` checks one selected package before done-status bookkeeping: plan/package
shape, closed proof rows, package-verification report binding, deliverable-matrix shape/coverage/clean
verdicts, current package/section-scoped Slice source bindings, and typed non-placeholder evidence-anchor
structure. It is read-only, does not require the selected package status to already be `done`, reports
`context_only` drift as advisories, and does not prove cited evidence is semantically sufficient.

`validate-final` runs plan and proof checks for every package, requires every package to be `done`,
applies the same package report/deliverable-matrix checks, requires each report to bind to the current
proof/package/section-scoped Slice source state, aggregates advisories across packages, and validates
optional enabled Semgrep Evidence raw/summary path/digest bindings when present.

The helper does not run tests, inspect implementation semantics, judge proof or matrix
truthfulness/sufficiency, mutate registry status, write review-code readiness, perform package
verification, or replace review/audit.

## Proof Replacement Safety

Default behavior:

- missing declared proof path: create the placeholder;
- existing exact placeholder: return success without rewriting;
- existing edited or filled proof: fail closed.

Replacement of edited or filled proof content requires:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" create-proof \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" \
  ".tasks/<feature>/tasks.json" --package WP1 --force \
  --approved-replacement "approved by <source>; provenance: <why replacement is valid>; scope: <exact evidence being replaced>"
```

The approval text must include approval, provenance, and scope. When replacement is approved, the
helper preserves the previous proof beside the proof path before writing a new placeholder.
