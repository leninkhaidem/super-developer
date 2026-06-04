# Package Lifecycle, Proof, and Report Freshness

Load when implementing, repairing, reviewing, displaying, or auditing planned-feature package state.

## Boundary

This reference owns package completion semantics and freshness. Artifact shapes live in `slice-first-artifacts.md`; command shapes live in `tool-usage.md`; workflow runbooks decide when to act.

## Package Status Signals

Registry package status is a routing signal only:

- `pending`: package has not started.
- `in_progress`: package work or repair is underway.
- `blocked`: package needs an authority-boundary decision before continuing.
- `done`: package passed the completion gate below.

Status does not prove implementation correctness. A dashboard may show status, dependency readiness, proof/report paths, and helper results, but must label them as mechanical signals.

## Completion Gate

A package may become `done` only after all of these are true:

1. Package Markdown assignment validates mechanically.
2. Proof Markdown validates mechanically and closes every required Slice row and verification expectation.
3. Required commands or inspections from the package assignment are recorded in the proof.
4. The package implementer completion statement and `SELF_REVIEW` evidence are present in the handoff/reporting channel required by the workflow.
5. Independent package verification has produced a package verification report bound to the proof digest and verified worktree state.
6. Required repairs and delta verification are closed.
7. No unresolved Slice plan defect, unapproved gap/deviation, or authority-boundary blocker remains.

Do not mark a package complete from registry status, helper success, proof table `PASS` rows, or package assignment text alone.

## Freshness Rules

Freshness is lost when any package-owned implementation, test, documentation, assignment, proof, or verification artifact changes after proof/report capture.

When freshness is lost:

- proof evidence affected by the change must be refreshed or rewritten;
- package verification must rerun for the affected scope;
- the package verification report must be replaced with a new proof digest and state binding;
- review-code readiness must be refreshed when the change occurs after review-code reached readiness;
- audit must treat the package as not final-ready until proof, report, and review-code readiness are fresh again.

Mechanical helper success is necessary but not sufficient: it checks structure, closure rows, and report binding, not semantic sufficiency.

## Non-Bypass Semantics

Package completion, review-code readiness, and audit are separate gates:

- Package completion requires valid proof Markdown plus a fresh package verification report.
- Review-code readiness requires the review/fix loop to close serious findings and confirm package proof/report freshness after repairs.
- Audit requires final artifact validation, fresh package reports, review-code readiness, and material Slice obligation closure.

A later gate may reject an earlier gate's output. Do not downgrade, hide, or override missing proof rows, failed reports, stale bindings, unresolved findings, or unapproved deferrals through dashboard edits or registry status changes.

## Dashboard Rule

Dashboards are read-only. They may surface:

- registry status and dependency readiness;
- package/proof/report file paths;
- proof Markdown mechanical validation state;
- package verification report presence and binding state;
- review-code readiness state when present.

Dashboards must not mutate lifecycle state or present mechanical signals as semantic proof.
