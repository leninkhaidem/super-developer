# Package Lifecycle, Proof, and Report Freshness

## Boundary

This reference owns package completion, proof creation/refresh, verification reports, freshness, and non-bypass semantics. Artifact shapes live in `slice-first-artifacts.md`; package sizing lives in `work-packages.md`; command shapes live in `tool-usage.md`.

## Status Signals

Registry package status is routing only:

- `pending`: package has not started.
- `in_progress`: package work or repair is underway.
- `blocked`: an authority-boundary decision is needed.
- `done`: the package passed the completion gate below.

Status does not prove implementation correctness. Dashboards may show status, dependency readiness, proof/report paths, and helper results only as mechanical signals.

## Proof Ownership

Each package has one proof Markdown file declared in the registry and package Markdown:

```text
.tasks/<feature>/proofs/<WP-ID>.proof.md
```

Package agents fill or refresh only their assigned proof file and package commits. They do not mark packages done, finalize features, edit unrelated proof files, or reconcile a central evidence ledger.

Proof Markdown owns package evidence for assigned `Must satisfy` H3 IDs and package verification expectations. `PASS` in a proof row is a package-agent claim, not package acceptance.

When Semgrep is enabled or contracted for a package, raw and summary outputs live under
`.tasks/<feature>/semgrep/` and proofs/reports cite paths and digests. These files are local task
store evidence, not lifecycle state or a replacement for proof/report judgment.

## Pre-Dispatch Proof Creation

Before dispatching a package, create the declared proof placeholder:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" create-proof ".tasks/<feature>/tasks.json" --package WP1
```

`create-proof` generates closure rows for assigned `Must satisfy` H3 IDs and records `Context only` IDs as scope context without closure rows.

Overwrite safety:

- existing exact placeholder: idempotent success;
- missing proof: create placeholder;
- edited or filled proof: fail closed unless `--force --approved-replacement` includes approval, provenance, and scope and preserves the prior content as described in `tool-usage.md`.

Filled evidence must never be silently erased.

## Package Agent Closure

A package agent cannot claim completion until proof Markdown shows:

- every assigned `Must satisfy` H3 ID in `## Slice Closure Table`;
- concrete implementation evidence for every required row;
- concrete verification evidence for every required row;
- `PASS` for every required row, or explicitly approved `DEFERRED`/`N/A` where allowed;
- every package verification expectation covered in `## Acceptance / Verification Closure`;
- exact command/static/manual evidence in `## Commands Run` and `## Files Changed / Inspected`;
- no unresolved `TODO`, `OPEN`, or `GAP` markers;
- no unresolved Slice plan defect, context-only misuse, or contradiction with assigned Slices.

## Mechanical Validation

When a package agent returns, run:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-proof ".tasks/<feature>/tasks.json" --package WP1
```

Reject proof handoff when validation reports missing sections, missing rows, duplicate rows, missing implementation/verification evidence, unresolved markers, unsupported statuses, missing verification expectation closure, unsafe paths, or missing proof files.

Mechanical validation is necessary, never sufficient. Package verification decides evidence sufficiency.

## Completion Gate

A package may become `done` only after all are true:

1. package Markdown assignment validates mechanically;
2. proof Markdown validates mechanically and closes every required Slice row and verification expectation;
3. required commands or inspections are recorded in proof evidence;
4. the package implementer supplied the required completion statement and `SELF_REVIEW` evidence;
5. no unresolved Slice plan defect, unapproved gap/deviation, or authority-boundary blocker remains;
6. independent package verification returned `PASS` and wrote the report bound to proof digest and verified worktree state, preferably after the package branch was committed/stabilized so the PASS binds directly to an exact commit/ref;
7. repairs and delta verification are closed;
8. post-merge or integration changes did not stale the proof/report, or freshness was restored.

Do not mark a package complete from registry status, helper success, proof rows, self-review, or package assignment text alone.

## Freshness Rules

Freshness is lost when any package-owned implementation, test, documentation, assignment, Slice approval metadata, proof, verification output, Semgrep evidence cited by proof/report, merge-resolution edit, or semantic report body changes after proof/report capture.

When freshness is lost:

- refresh affected proof rows and command/file evidence;
- rerun `sliceproof.py validate-proof` for every dirty package;
- rerun focused or full package verification as required by the changed surface;
- replace the report with a new proof digest and state binding;
- rerun affected review-code checks and refresh review-code readiness when the change occurs after review-code reached readiness;
- treat the package as not final-ready until proof, report, review-code readiness, and required audit reruns are fresh again.

Narrow binding-only refresh: if package verification already semantically reviewed identical code tree/diff, proof content/digest, package Markdown, assigned Slice set, implementer report/`SELF_REVIEW`, and verification output, and the only change is updating `## State Binding` from uncommitted/moving state to exact commit/ref metadata, update binding/report metadata without rerunning semantic package verification or code review.

The carve-out is invalid unless the source report body is unchanged, proof digest is unchanged, assigned Slice set is unchanged, package Markdown is unchanged, implementer report/`SELF_REVIEW` is unchanged, verification output is unchanged, reviewed code tree/diff is unchanged, and there were no repairs, merge-resolution edits, proof-evidence changes, or package/Slice/output changes. Uncertain impact fails closed by marking candidate package proofs/reports dirty or recording explicit no-impact evidence and rerunning focused/full package verification as required.

## Repair Handling

Before delegating repair, map each confirmed finding or fix batch to affected packages, Slice H3 IDs, proof rows, verification expectations, and proof-cited files/commands when identifiable.

After repair:

1. run relevant commands or inspections;
2. refresh affected proof rows and evidence sections;
3. rerun mechanical proof validation;
4. rerun package verification focused on failed findings and changed surfaces;
5. rerun affected final code-review checks when changed code or risk surfaces were already reviewed;
6. rerun focused audit checks for bounded Slice/package/global repair, or full final audit when scope is broad or assignment/completeness assumptions changed;
7. require full package re-verification when repair widens scope, changes package contracts, invalidates coverage/mock/Slice disclosures, touches new risk surfaces, or repeatedly fails to close.

Do not refresh proof evidence for failed or partial intermediate attempts as accepted evidence.

## Report Freshness

A package verification report must bind to package ID, package Markdown path, proof path, proof digest, assigned Slice paths (or explicit `none`), worktree, git ref/commit, reviewed verification output, verifier, timestamp, verdict, and open findings.

Reports block completion when missing, failed, stale, contradicted by code/proof/Slice content, bound to pre-repair evidence, or missing state binding.

## Final Readiness

Before final review-code or audit, every package must have:

- valid package Markdown;
- mechanically valid proof Markdown;
- no unresolved `GAP`, `OPEN`, `TODO`, unapproved `DEFERRED`, or unsupported `N/A`;
- a fresh `PASS` package verification report;
- closed repair/delta verification;
- no unresolved Slice plan defect.

Run:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-final ".tasks/<feature>/tasks.json"
```

This package-final readiness allows dispatching final review-code and final audit. Merge/readiness still requires review-code readiness and final audit PASS clean for the same integrated state. Helper success, registry mutation, manual proof edits, or dashboard output cannot bypass those gates.

## End-to-End Final Loop

1. Complete all packages through the package completion gate and run final package validation.
2. Run final review-code and final audit as sibling checks against the same integrated state when practical. Audit receives review-code state/report when already available, or explicit `none`; review-code readiness is not required before audit dispatch.
3. Batch compatible final review-code and final audit findings when possible, delegate repair, refresh affected proof Markdown/package reports, rerun `sliceproof.py validate-proof`/package verification, and rerun affected final code-review plus focused/full audit checks as scope requires.
4. If either final check was not run, is stale, or is affected by repair, run or rerun it before readiness.
5. Declare readiness only when package evidence, review-code readiness, and final audit PASS are clean for the same integrated state.

## Dashboard Rule

Dashboards are read-only. They may surface:

- registry status and dependency readiness;
- package/proof/report file paths;
- proof mechanical validation state;
- report presence and binding state;
- review-code readiness state when present.

Dashboards must not mutate lifecycle state or present mechanical signals as semantic proof.
