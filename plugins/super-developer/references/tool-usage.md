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

`sliceproof.py` is the planned-feature mechanical helper. Always pass both roots as resolved absolute paths:
`$ARTIFACT_ROOT` is the distinct sidecar (`.worktrees/<feature>/artifacts`) and `$CODE_ROOT` is the code worktree
being checked—a package worktree for package checks and the integration/top worktree for `validate-final` and file
evidence. Treat roots as trust anchors. A report's `Worktree` cannot select roots, but its candidate binding must
resolve to an exact worktree in the same Git repository. Omitted defaults are compatibility, never planned authority.
Reject equal/current roots; migrate `.planning`/`.tasks` through `artifact-store.md`. The tasks path remains
artifact-root-relative.

Git publication is not a helper function. At action time use the parent-supplied artifact-store and worktree
contracts: exact namespaced non-force CAS, immutable code checkpoint refs, verified code-before-sidecar ordering,
and path-specific finalized staging. Sidecar Portability Authorization cannot authorize code, target, release,
force, or deletion operations.

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
  --authorization-id "$AUTHORIZATION_ID" --effective-digest "$EFFECTIVE_DIGEST" \
  --assurance-profile "$PROFILE" --verification-mode boundary \
  --worktree "$REVIEWED_WORKTREE" --git-ref "$REVIEWED_GIT_REF" \
  --commit "$REVIEWED_COMMIT" --tree "$REVIEWED_TREE" --base-commit "$BASE_COMMIT" \
  --diff-digest "$DIFF_DIGEST" --runtime-evidence-digest none \
  --consumed-contract-digest none --verified-at "$VERIFIED_AT"
```
For `boundary`, completion requires fresh PASS, clean matrix, exact six-column `### Selected Causal Evidence`, and
exact State Binding. For `final`, it requires null report, stable closed proof, explicit direct-final owner/deferral,
and no dependent boundary. Distinct roots require transition-valid authorization and exact checkpoint ref/SHA;
immediate completion requires `stabilized|verified|done` plus a clean exact candidate code-root HEAD. Consumer
completion revalidates each direct producer's `done` state and exact historical `B[i]`. `validate-final` requires
lifecycle `done` and a clean integration checkpoint while accepting exact prior `B[i]`. Same-root is non-authoritative.
Commands return JSON on success and JSON `errors` plus `advisories` on failure. `context_only_slice_drift` remains
non-blocking by default, routes to affected-surface classification, and is aggregated by `validate-final` even with hard errors.

`emit-state-binding` is read-only and boundary-only. It writes canonical Markdown to stdout from the explicit
candidate flags above. Repeat artifact-relative `--runtime-evidence-digest PATH=sha256:<digest>` and safe
`--consumed-contract-digest ID=sha256:<digest>` as needed; pass each flag exactly once with `none` for an empty set.
Inputs are validated/sorted, current runtime files are digested, and verifiers never hand-compute the block.

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
- package Markdown `Independent Verification` mode/report/rationale and dependency references;
- assigned Slice H3 IDs under `## Shared Understanding`.

`create-proof` writes only the declared proof Markdown placeholder for one package. Existing filled,
edited, or drifted proof content is never overwritten silently.

`validate-proof` checks one package proof mechanically:

- required sections and closure tables;
- required Slice rows and verification expectation rows;
- duplicate, unexpected, unsupported, placeholder, or blocking rows;
- explicit approval, provenance, and scope for deferrals, non-applicable rows, gaps, or deviations;
- non-placeholder command/file/completion evidence.

`validate-package-complete` branches mechanically: `boundary` validates PASS report, matrix, Selected Causal
Evidence, exact candidate/contract binding, and optional Semgrep evidence; `final` validates proof/assignment,
null/absent report, direct-final deferral, and leaf routing. It accepts pre-`done` status and judges no semantics.

`validate-final` requires every package `done` and validates only the selected pre-freeze equation: fresh `B[i]`
for boundary packages and stable direct-final deferral for final packages. It aggregates advisories and explicitly
does not claim post-freeze final assurance ran.

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
