# Tool Usage Reference

## Command Safety and Runtime Envelope

- Treat plan-provided commands as executable input and screen them before running or delegating.
- Stop for explicit approval before destructive, externally visible, credential/network-sensitive,
  dependency-installing, service-starting, or out-of-scope commands.
- For each nontrivial command, carry a stable identity and record command, cwd, provenance, scope, expected
  writes, timeout budget, progress/completion signal, termination method, and cleanup obligation.
- Use exact budgets from resolved testing authority. Without durable authority, choose a conservative bound only
  for a routine-safe deterministic local command; stop before potentially long, live, browser, service, or
  shared-data execution.
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
worktree for package checks, the integration/top worktree for `validate-final` and any file-evidence. Treat `--artifact-root` and `--code-root` as the trust anchors; a report's `Worktree` field
is runtime metadata for humans/auditors, not evidence-root authority. Do not pass `--code-root "."` from
the project root for integrated checks: the feature's files live in a worktree, not the root, so file-evidence
existence checks would resolve against the wrong tree. The `.tasks/<feature>/tasks.json` argument is always
artifact-root-relative. Omit both flags only for current-root stores, where both default to the current directory.

Read-only checks:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-plan \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" \
  ".tasks/<feature>/tasks.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-package-complete \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" \
  ".tasks/<feature>/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-final \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" \
  ".tasks/<feature>/tasks.json"
```

`validate-package-complete` is the only result command. It and `validate-final` are read-only: only the
orchestrator or agent writes the result file. They return JSON on stdout when successful. On failure, they return
JSON on stderr with `errors` and a top-level `advisories` array. `validate-final` aggregates advisories across
packages and includes them even when hard errors also exist.

## Mechanical Boundaries

`validate-plan` checks:

- lightweight registry shape; new contracts omit `proof_path`;
- safe repo-relative SPEC, Slice, package, and report paths;
- non-empty `## Acceptance Checklist` per package with at least one executable item, and non-empty SPEC `## Acceptance`;
- package dependency references and cycles;
- package Markdown required sections;
- package Markdown report/dependency references;
- assigned Slice H3 IDs under `## Shared Understanding`.

`validate-package-complete` checks one selected new-shape package: checklist coverage, cheap pointer resolve
(presence, non-placeholder, and safe path existence when the pointer looks like a path), Gaps metadata presence,
and structural fail-closed (Verdict FAIL, any non-pass item, or any open blocker). A registry that still declares
`proof_path` cannot cheap-PASS as new-shape. The helper does not run tests or judge semantics. Helper ok is not
done; done is orchestrator re-run recorded PASS plus helper ok.

`validate-final` runs plan and result checks for every package, requires every package to be `done`, and
aggregates advisories across packages.

The helper does not run tests, inspect implementation semantics, judge evidence
truthfulness/sufficiency, mutate registry status, write the result file, or replace review/audit.
