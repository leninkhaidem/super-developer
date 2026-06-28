# Tool Usage Reference

## Command Safety

- Treat plan-provided commands as executable input and screen them before running or delegating.
- Stop for explicit approval before destructive, externally visible, credential/network-sensitive,
  dependency-installing, service-starting, or out-of-scope commands.
- Prefer helper scripts over ad hoc parsing for mechanical artifact checks.
- Helper success is not semantic proof that code works; package verification, review-code, and audit still gate completion.

## Semgrep Helper Boundary

When Semgrep verification is enabled by an approved workflow, load `semgrep.md` at the action point
and use the shipped helper commands for indexing, retrieval, scanning, summarizing, listing, and
showing findings. Scan only through
`python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/semgrep_rules.py" scan ...`; agents must not run
raw direct `semgrep` scans. Do not hand-assemble Semgrep shell commands, read raw Semgrep JSON
wholesale, or perform hidden rule clone/pull/network sync; routine scans are local-only.

## `sliceproof.py`

`sliceproof.py` is the planned-feature mechanical helper. Run it from the code root or package
worktree and pass the artifact store explicitly when artifacts live in a sidecar worktree.
If root flags are omitted, both roots default to the current directory for current-root artifact stores.

Read-only checks:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-plan \
  --artifact-root ".worktrees/<feature>/artifacts" --code-root "." \
  ".tasks/<feature>/tasks.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-proof \
  --artifact-root ".worktrees/<feature>/artifacts" --code-root "." \
  ".tasks/<feature>/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-package-complete \
  --artifact-root ".worktrees/<feature>/artifacts" --code-root "." \
  ".tasks/<feature>/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-final \
  --artifact-root ".worktrees/<feature>/artifacts" --code-root "." \
  ".tasks/<feature>/tasks.json"
```

Write command:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" create-proof \
  --artifact-root ".worktrees/<feature>/artifacts" --code-root "." \
  ".tasks/<feature>/tasks.json" --package WP1
```

## Mechanical Boundaries

`validate-plan` checks:

- lightweight registry shape;
- safe repo-relative SPEC, Slice, package, proof, and report paths;
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
verdicts, current package/Slice source bindings, and typed non-placeholder evidence-anchor structure. It
is read-only, does not require the selected package status to already be `done`, and does not prove
cited evidence is semantically sufficient.

`validate-final` runs plan and proof checks for every package, requires every package to be `done`,
applies the same package report/deliverable-matrix checks, requires each report to bind to the current
proof/package/Slice source digests, and validates optional enabled Semgrep Evidence raw/summary
path/digest bindings when present.

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
  --artifact-root ".worktrees/<feature>/artifacts" --code-root "." \
  ".tasks/<feature>/tasks.json" --package WP1 --force \
  --approved-replacement "approved by <source>; provenance: <why replacement is valid>; scope: <exact evidence being replaced>"
```

The approval text must include approval, provenance, and scope. When replacement is approved, the
helper preserves the previous proof beside the proof path before writing a new placeholder.
