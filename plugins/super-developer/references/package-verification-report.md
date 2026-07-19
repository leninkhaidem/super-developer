# Package Verification Report Contract

## Boundary

This is the durable pre-freeze `B[i]` report shape for a package routed `boundary`. Package verification exists
only for a meaningful boundary selected by `assurance-routing.md`; a `final` package has `report_path: null` and no
fabricated report. Verifiers own semantic truth and sufficiency. Helpers own shape and binding only.

## Canonical Source Body

The report starts with this H2 before lifecycle metadata:

```md
## Package Verification: <WP-ID>

### Verdict
PASS | FAIL

### Deliverable Completeness Matrix
| Source ID | Row Type | Deliverable | Evidence Type | Evidence Refs | Exactness / Risk Disposition | Verdict |
|---|---|---|---|---|---|---|
| `<Slice-H3-ID>` | `slice` | <observable deliverable> | `mixed` | `code:plugins/path.py#symbol`; `test:plugins/tests/test_x.py::test_y` | `interface: exact; forbidden-behavior falsified by test:...` | `delivered` |
| `VE-1` | `verification-expectation` | <expectation> | `static` | `static:plugins/ref.md#section` | `expectation covered; no interface` | `delivered` |
| `RISK-lifecycle-1` | `triggered-risk` | <risk scenario> | `command` | `command:proof#Commands Run:targeted` | `triggered because ...; result ...` | `delivered` |

### Triggered Risk Selection Notes
- Applied: `<RISK-ID>` because <scope/Slice/diff/expectation/failure rationale>.
- Not applicable: <nearby high-signal probe> because <concise rationale>.

### Selected Causal Evidence
| Evidence Anchor | Evidence Type | Behavior / Risk Proven | Causal Sufficiency | Substitutes / Fixtures | Fresh Command Result |
|---|---|---|---|---|---|
| `test:plugins/tests/test_x.py::test_y` | `test` | <observable/forbidden behavior or named risk> | <why this forces the actual path and is sufficient, including rows jointly covered> | <mocks, fixtures, hooks, synthetic inputs, or `none`> | `command:proof#Commands Run:targeted` — PASS, <fresh observed result> |

### Slice Closure Review
| Slice ID | Proof status | Evidence sufficient? | Notes |
|---|---|---|---|
| `<Slice ID>` | `PASS` | yes | <concise closure note> |

### Code Review Findings
- None.
```

For failures add `### Blocking Findings` and `### Repair Guidance`. `PASS` requires a clean matrix and a
non-placeholder `### Selected Causal Evidence` section. Slice closure prose alone is insufficient.

## Matrix Rows

Core columns and controlled verdicts are fixed: `delivered`, `missing`, `partial`, `contradicted`, or `unverified`.
Mandatory rows use each exact H3 ID assigned under `Must satisfy` (`slice`), stable package-order `VE-<n>` IDs
(`verification-expectation`), and verifier-selected applicable `RISK-<slug-or-n>` IDs (`triggered-risk`). Verifier
selection is independent: planner seeds do not limit discovery; non-applicable probes must not become checklist noise. Keep a `VE-<n>` row when it
shares decisive evidence with another row and cross-reference rather than inventing another test.

A matrix indexes requirements-first code/test evidence after semantic inspection; it neither defines tests nor
proves its own rows. Every mandatory row must be `delivered` with decisive typed evidence. Interface rows use
`interface: exact; forbidden-behavior falsified by <typed evidence ref>`; ambiguous negative wording fails closed.

## Selected Causal Evidence Contract

Select the smallest credible set under `work-packages.md`. Each row requires:

- a safe typed anchor to the selected test or observation;
- the accepted behavior, forbidden outcome, consumed contract, or triggered risk proven;
- why it forces the actual production path, would fail when the invariant breaks, and is sufficient alone or with
  named companion rows;
- relevant mock, fixture, hook, cache, generated input, synthetic outcome, or other substitute disclosure; and
- a fresh typed command anchor, `PASS`, and concise observed result for package completion.

One anchor may prove multiple related matrix rows. Deeply inspect selected evidence and any changed harness,
fixture, generator, discovery, CI, coverage, build, or test configuration that can affect its trustworthiness.
Concrete false positives, wrong/weakened assertions, hidden skip/focus/xfail, flakiness/inconclusive results,
unsafe side effects, materially unacceptable required runtime, or trust-undermining shared harness/config changes
block. Do not census changed test populations, require exemplars by category, rereview the suite, demand test-code
perfection, or gate/report test count, changed test lines, ratio, coverage, review percentage, or suite volume.
Existing tests are never rejected or removed solely for volume.

## Evidence References

`Evidence Type` is `code`, `test`, `static`, `command`, `manual`, or `mixed`. Semicolon-separated typed anchors are:

- `code:<repo-relative-path>[#symbol-or-lines]`, `test:<repo-relative-path>[::test-or-#lines]`, or
  `static:<repo-relative-path>#section`;
- `command:proof#Commands Run:<label>` or `command:verification-output:<repo-relative-path>#<label>`;
- `manual:scenario=<specific scenario>; observed=<specific result>`.

Reject unsafe, nonexistent, placeholder, fabricated, or structurally vague anchors. Labels, counters, cache hits,
synthetic outcomes, matrix rows, or proof wording alone cannot prove behavior.

## Exact State Binding

Generate this block with `emit-state-binding`, paste it verbatim, and do not hand-compute digests:

```md
## State Binding
- Package: `<WP-ID>`
- Package Markdown: `.tasks/<feature>/packages/<WP-ID>.md`
- Package Markdown Digest: `sha256:<digest>`
- Proof: `.tasks/<feature>/proofs/<WP-ID>.proof.md`
- Proof Digest: `sha256:<digest>`
- Assigned Slices: `<safe sorted paths, or none>`
- Assigned Slice Digests: `path|tier|H3-ID=sha256:<64-hex>; ...` or `none`
- Matrix Source Snapshot: `sha256:<digest>`
- Authorization / Effective Digest: `<authorization-id> | sha256:<digest>`
- Assurance Profile / Verification Mode: `low|standard|high | boundary`
- Worktree: `<absolute reviewed code worktree>`
- Git Ref: `refs/heads/checkpoints/<feature>/<slot>/g<generation>`
- Commit / Tree: `<reviewed commit hash> | <tree hash>`
- Base / Diff Identity: `<base commit> | sha256:<raw-diff-identity digest>`
- Runtime Evidence Digests: `<safe path>=sha256:<digest>; ...` or `none`
- Consumed Contract Digests: `<contract-id>=sha256:<digest>; ...` or `none`
- Verified At: `<ISO-8601 timestamp>`
```

`emit-state-binding` emits all fields from explicit roots/package plus `--authorization-id`, `--effective-digest`,
`--assurance-profile`, `--verification-mode`, `--worktree`, `--git-ref`, `--commit`, `--tree`, `--base-commit`,
`--diff-digest`, repeatable runtime/contract digest flags, and `--verified-at`. Candidate commit/base must be real
commits in the code repository, base must be an ancestor, tree must be the candidate commit's exact tree, and Git
Ref must resolve to that commit in the supplied code repository. In authoritative sidecar mode it is the exact
immutable namespaced checkpoint ref that Lifecycle State bound at immediate completion. Immediate checks require
Worktree to equal the supplied code root with clean HEAD at that candidate. Historical consumer/final validation
uses candidate objects/ref and ancestry to the current checkpoint; the old descriptive Worktree path need not exist.
Diff Identity is exactly `sha256:` plus lowercase SHA-256 of the raw stdout bytes from
`git -C <code-root> diff --raw --no-renames --no-ext-diff --no-textconv --no-abbrev -z <base-commit> <candidate-commit> --`; no text decoding,
path normalization, rename detection, or trailing newline is added. Pass explicit `none` for empty digest sets;
the helper path-checks and sorts them. Assigned Slice Digest
entries separated by `; ` sort by path, then `must_satisfy` before `context_only`, then H3 ID.
Assigned paths must not contain `|`, `=`, or the delimiter sequence `; `; grammar delimiters fail closed before
drift classification. Matrix Source Snapshot covers package Markdown plus must_satisfy section blocks only.
Malformed/current hard-tier, package, proof, selected-evidence, cited-output, profile/mode, consumed-contract, or
reviewed-code drift invalidates `B[i]`. `context_only_slice_drift` is non-blocking by default and receives
affected-surface classification. Binding-only refresh requires identical semantic inputs, claims, method, and
execution evidence. Optional helper-bound Semgrep evidence may follow when enabled.

The helper enforces this conditional grammar and exact binding only; verifier-owned causal and semantic
sufficiency remains outside mechanical validation.
