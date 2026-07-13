# Package Verification Report Contract

Boundary: shared durable report, test-review receipt, and deliverable-matrix shape for package verifiers,
package completion helpers, final auditors, and freshness checks. Reports live under the artifact root; `Worktree` in state
binding is the reviewed code worktree. Verifiers and final auditors own semantic truthfulness and sufficiency.

## Canonical Source Body

The report at `.tasks/<feature>/reports/<WP-ID>.package-verification.md` starts with this H2 before lifecycle metadata:

```md
## Package Verification: <WP-ID>

### Verdict
PASS | FAIL

### Deliverable Completeness Matrix
| Source ID | Row Type | Deliverable | Evidence Type | Evidence Refs | Exactness / Risk Disposition | Verdict |
|---|---|---|---|---|---|---|
| `<Slice-H3-ID>` | `slice` | <observable deliverable> | `mixed` | `code:plugins/path.py#symbol`; `test:plugins/tests/test_x.py::test_y` | `interface: exact; forbidden-behavior falsified by test:...` | `delivered` |
| `VE-1` | `verification-expectation` | <package expectation from Markdown order> | `static` | `static:plugins/ref.md#section` | `expectation covered; no interface` | `delivered` |
| `RISK-lifecycle-1` | `triggered-risk` | <applicable risk scenario> | `command` | `command:proof#Commands Run:pytest-targeted` | `triggered because ...; result ...` | `delivered` |

### Triggered Risk Selection Notes
- Applied: `<RISK-ID>` because <scope/slice/diff/expectation/failure-mode rationale>.
- Not applicable: <nearby high-signal probe> because <concise rationale>.

### Test Review Scope
| Surface | Changed Population | Review Depth | Baseline Review | Deep Triggers | Selected Exemplars | Sampling Rationale | Generator / Input / Provenance | Evidence Refs |
|---|---|---|---|---|---|---|---|---|
| `tests` | `count: 12; scope: parser success and malformed-receipt cases` | `sampled` | `complete: assertions, paths, state effects, and fresh commands checked; no skip changes found` | `none: package-local parser cases are not sensitive or sole evidence` | `selected: valid, malformed, and unsupported receipt cases` | `strategy: semantic behavior and oracle-shape strata` | `not-applicable: hand-authored tests contain no generated output` | `test:plugins/tests/test_x.py::test_y` |

### Slice Closure Review
| Slice ID | Proof status | Evidence sufficient? | Notes |
|---|---|---|---|
| `<Slice ID>` | `PASS` | yes | <concise closure note> |

### Code Review Findings
- None.
```

For failures, add `### Blocking Findings` and `### Repair Guidance` under the same H2. A `PASS` requires a present, clean `### Deliverable Completeness Matrix` and valid `### Test Review Scope`; `### Slice Closure Review` and proof prose alone are insufficient.

## Matrix Row Contract

Core columns are fixed exactly as shown: `Source ID`, `Row Type`, `Deliverable`, `Evidence Type`, `Evidence Refs`, `Exactness / Risk Disposition`, and `Verdict`.

Controlled verdicts are `delivered`, `missing`, `partial`, `contradicted`, and `unverified`. Clean package verification requires every mandatory row to be present, `delivered`, and supported by structurally valid non-placeholder evidence references. Any `missing`, `partial`, `contradicted`, or `unverified` row blocks completion even if other report sections look coherent.

Mandatory rows come from:

1. Assigned package `Must satisfy` Slice H3 IDs, using each exact H3 ID as `Source ID` and row type `slice`.
2. Package Markdown `## Verification Expectations`, using stable `VE-<n>` IDs in listed order and row type `verification-expectation`. If an expectation is materially proven by a Slice row, keep the `VE-<n>` row and cross-reference that evidence rather than omitting it.
3. Triggered risk rows are verifier-selected, using explicit `RISK-<slug-or-n>` IDs and row type `triggered-risk` with rationale/disposition. Selection comes from package scope, assigned Slices, changed code/diff/tests, verification expectations, and known failure modes; planner seeds do not limit discovery, and non-applicable probes must not become checklist noise.

## Test Review Scope Receipt

The package verifier records one row per changed category in the package-owned reviewed delta: `tests`, `harnesses/helpers`, `mocks/fixtures`, `generators/snapshots`, or `test-discovery/CI/coverage/build-config`.
Group by semantic population and account for every package-owned changed path. Clean depths are only `baseline-only`, `sampled`, and `deep`; `not-reviewed` and `unreviewed` are invalid.

Every ordinary row uses this exact field grammar (whitespace and harmless punctuation normalization may vary; prefixes and semantics may not):

- `Changed Population`: `count: <positive integer>; scope: <specific non-placeholder description>`.
- `Baseline Review`: `complete: <specific non-placeholder checks/results>`.
- `Deep Triggers`: for `deep`, `triggered: <specific non-placeholder trigger>`; for `baseline-only` or `sampled`, `none: <specific reason>`.
- `Selected Exemplars`: for `sampled`, `selected: <specific exemplars>`; otherwise, `not-applicable: <specific reason>`.
- `Sampling Rationale`: for `sampled`, `strategy: <specific semantic selection rationale>`; otherwise, `not-applicable: <specific reason>`.
- `Generator / Input / Provenance`: `generators/snapshots` requires `generator: <specific>; inputs: <specific>; provenance: <specific>`; other surfaces allow that triple or `not-applicable: <specific reason>`.
- `Evidence Refs`: one or more typed anchors from the evidence-reference grammar below.

Baseline checks/results cover assertion weakening/deletion, skip/focus/xfail changes, broad tolerances or matchers, path execution/discrimination, mock/fixture/global-state effects, fresh commands/evidence, and generated provenance where applicable.
`deep` is required for proof-critical or sole evidence; security/privacy/safety/data/migration/concurrency/public-contract seams; shared harness/helper/config; weakened assertions or skips; missing provenance; contradictions or stale evidence; cross-package seams; and tests-as-deliverable.

Sampling is semantic, never percentage-based: partition by behavior/contract, oracle shape, helper/mock stack, and generator provenance/risk.
Generated output is sampleable only after its generator, inputs, and provenance are reviewed. Budget exhaustion causes semantic batching or
widening, never reduced rigor or fixed-percentage quotas.

Only the constrained whole-receipt absence is allowed. For no applicable surface, use exactly one row with `Surface`, `Changed Population`, and `Selected Exemplars` set to `none`, `Review Depth` set to `no-applicable-surface`, every other narrative field set to `not-applicable: <specific reason>`, and typed classification evidence.
It cannot coexist with another row. Explicit `not-reviewed`/`unreviewed` and unresolved marker forms anywhere in the section are invalid.

Mechanical validation owns the exact grammar, positive count, controlled surface/depth values, non-placeholder payloads, strict table shape (exactly one unfenced contiguous Markdown table with a matching-width delimiter, exact-arity rows, and no extra pipe fragments/tables), and typed-reference safety.
It does not infer semantic truth from arbitrary prose or decide whether a claim is honest, contradictory, or sufficient. Thus `Review status: baseline review was not performed` fails the required `complete:` grammar, while a syntactically valid but dishonest `complete:` claim is for the verifier/reviewer/auditor to reject; legitimate negative results inside `complete:` remain valid.

Final pipeline review validates each fresh receipt against its package-owned reviewed delta and reconciles the union of fresh package receipts against the integrated diff. It separately reviews integration-only or merge-resolution test-relevant changes at a canonical depth, then widens for triggers/anomalies.
Audit follows the same partition and selectively falsifies rather than rereviewing every test. Reports without the receipt are invalid and must be refreshed; there is no silent format bypass.

## Evidence Reference Rules

`Evidence Type` is one of `code`, `test`, `static`, `command`, `manual`, or `mixed`. `Evidence Refs` are semicolon-separated typed anchors:

- `code:<repo-relative-path>[#symbol-or-lines]`, `test:<repo-relative-path>[::test-or-#lines]`, and `static:<repo-relative-path>#section` point to safe existing repo paths; no absolute paths, traversal, fabricated files, or vague-only anchors.
- `command:proof#Commands Run:<label>` or `command:verification-output:<repo-relative-path>#<label>` links to proof command rows or durable verifier output records.
- `manual:scenario=<specific scenario>; observed=<specific result>` records manual evidence without pretending it is mechanically executable.

Mechanical helpers may reject unsafe, nonexistent, placeholder, fabricated, or structurally vague anchors. They do not decide whether the cited evidence truly proves the deliverable.

## Exactness and Risk Disposition

Interface-bearing Slice rows must record an exactness verdict and forbidden-behavior falsification in `Exactness / Risk Disposition`. Use exactness values `exact`, `ambiguous`, `partial`, `contradicted`, or `over-broad`; only `exact` plus falsified forbidden behaviors can support a clean `delivered` interface row. Triggered-risk rows record why the probe was triggered, what was checked, and its disposition.

## State Binding

Append lifecycle metadata after the source body so helpers and final auditors can consume it without hidden
chat context. Generate the block with `emit-state-binding`, paste it verbatim, and do not hand-compute
digests. Paths below are artifact-root-relative except `Worktree`, which is an absolute code worktree.
`Worktree` records where review happened for human/audit context; mechanical file-evidence resolution uses
the orchestrator-supplied `--code-root`, not this field, so the two must stay consistent.

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" emit-state-binding \
  --artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT" \
  ".tasks/<feature>/tasks.json" --package <WP-ID> \
  --worktree "<absolute reviewed worktree root>" --git-ref "<reviewed branch/ref/commit>" \
  --commit "<reviewed commit hash>" --verified-at "<ISO-8601 timestamp>"
```

```md
## State Binding
- Package: `<WP-ID>`
- Package Markdown: `.tasks/<feature>/packages/<WP-ID>.md`
- Package Markdown Digest: `sha256:<digest>`
- Proof: `.tasks/<feature>/proofs/<WP-ID>.proof.md`
- Proof Digest: `sha256:<digest>`
- Assigned Slices: `<comma-separated repo-relative Slice paths in lexicographic order, or none>`
- Assigned Slice Digests: `path|tier|H3-ID=sha256:<64-hex>; ...` or `none`
- Matrix Source Snapshot: `sha256:<digest over package Markdown plus must_satisfy section blocks only>`
- Worktree: `<absolute reviewed worktree root>`
- Git Ref: `<reviewed branch/ref/commit>`
- Commit: `<reviewed commit hash>`
- Verified At: `<ISO-8601 timestamp>`
```

`Assigned Slice Digests` is one parser-safe line of `path|tier|H3-ID=sha256:<64-hex>` entries separated
by `; `, sorted by Slice path, then `must_satisfy` before `context_only`, then H3 ID. Assigned Slice paths
used in this grammar must not contain `|`, `=`, or the delimiter sequence `; `; helper validation fails
closed before emitting or accepting a binding when an assigned path contains those grammar delimiters.
`Matrix Source Snapshot` covers package Markdown plus `must_satisfy` section blocks only; `context_only`
sections live only in `Assigned Slice Digests`. Missing, extra, duplicate, malformed, unknown-path/H3, invalid-tier,
invalid-digest, or encoded-tier-mismatch entries fail closed before drift classification. Valid
`context_only` digest drift emits a non-blocking `context_only_slice_drift` advisory; `must_satisfy`
drift remains a hard freshness error.

Changing package Markdown verification expectations, assigned `must_satisfy` section content, proof
content, cited verification output, Test Review Scope inputs/receipt, artifact root selection, or reviewed
code invalidates the report until refreshed. `context_only` section drift is routed as an advisory for
affected-surface classification unless
reviewer/auditor judgment escalates material risk. Optional `## Semgrep Evidence` may follow when
enabled/contracted, with helper-produced artifact-root raw/summary paths, digests, scan scope, and bounded
summary.
