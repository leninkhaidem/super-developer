# Review-Code Fix Implementer Contract

Boundary: governs only review-owned local or pipeline repairs. A caller-owned local `repair_owner` and
`repair_contract_path` take precedence; review-code returns that repair packet instead of using this contract.
The review parent owns authorization, packet construction, state validation, git/delivery, and user interaction.

## Role and Authority

Authority comes only from a complete explicit fix packet plus this contract, never hidden chat, a finding alone,
blanket wording, or runtime identity. The worker may reproduce confirmed findings, edit exact permitted paths, add
bounded regression evidence, verify, and self-review. It may not expand authority or perform delivery.

Before any repository command or write, read the whole packet and this contract at the exact supplied path. Missing,
stale, unsafe, ambiguous, or conflicting input means no repository action and `BLOCKED` with field/evidence.

## Required Packet

The parent supplies:

- packet ID, contract path, `mode: local|pipeline`, and recorded explicit fix authorization;
- confirmed finding keys, evidence, Skeptic verdicts, decisions, expected behavior, and repair goal;
- exact repository/worktree, branch/ref, base ref/SHA, HEAD SHA, and complete starting-state binding;
- separate category manifests/content checksums plus complete checksum; untracked records include file type,
  Git mode (`100644|100755|120000`), symlink target, and content digest/binary provenance;
- exact writable file paths, new-file name rules, non-goals, and all other paths read-only;
- reproduction, minimal strategy, regression requirement, and expected failure mechanism;
- bounded verification commands and supplied tool-usage/testing-authority contract paths when applicable;
- forbidden actions, stop/scope-expansion route, and required report fields;
- local context: caller constraints and reviewed snapshot; or
- pipeline context: artifact/code roots, feature/package/Slice IDs, proof/report paths, dirty-evidence map,
  source bindings, verification state, and freshness handback owner;
- for cross-package repair, every affected package, writable path, and finding under one coherent seam authority
  and verification envelope; otherwise the parent must split the packet.

Normally the parent supplies a clean isolated worktree. Before action and immediately before the first write,
recapture HEAD and all four state categories and compare every checksum. Any drift is `BLOCKED`; never absorb it.

## Write and Side-Effect Boundary

Write only exact packet paths inside the named worktree. New regression files need an approved parent, name rule,
and purpose. No unrelated cleanup, formatting, refactor, dependency, config, CI, generated output, or artifact edit.

Never create/remove worktrees or refs; switch branches; stage; commit; merge; rebase; push/fetch/pull; reset; stash;
clean; discard changes; force operations; install dependencies; access the network; start live services; use
credentials; mutate shared/production data; or run destructive commands. Return required expansion to the parent.

## Ordered Workflow

1. **Preflight:** read packet/contract, validate mode authority and paths, recapture complete starting state, and
   return no-action `BLOCKED` on mismatch. Load supplied command/testing contracts only at their action point.
2. **Reproduce:** locate and reproduce each confirmed finding with the smallest safe bounded inspection/command.
   Stop if the observed mechanism differs, cannot be reached, or needs forbidden/unapproved action.
3. **Repair:** apply the minimal change for the confirmed mechanism inside exact write scope. Do not repair
   suggestions separately or broaden behavior/contracts.
4. **Regression:** add or adjust targeted evidence that fails for the original mechanism and passes with repair
   when practical. If no bounded seam exists, return `BLOCKED: scope_expansion`.
5. **Verify:** run the regression, original repro, smallest affected existing slice, and packet checks. Record cwd,
   bound, result, termination, and cleanup. Timeout, flaky output, or uncertain cleanup is not pass.
6. **Self-review:** inspect complete delta and untracked provenance; confirm scope, behavior, secrets, residue,
   and regression relevance. Apply the complete shared codebase-design model and every smell to changed behavior
   and directly affected Interfaces, Seams, Adapters, callers, tests, and evidence; fix material in-scope risk,
   justify harmless shapes, and exclude unrelated legacy cleanup. Do not stage or commit.
7. **Hand back:** leave state intact and return only the bounded report.

## Pipeline Freshness Handback

Pipeline workers never claim proof/report/Semgrep freshness, Fix Verification, or audit readiness. Return each
affected package, checklist/proof/report row, seam, Slice H3, evidence anchor, Semgrep evidence, and verification
output as `no_impact|refresh_required|candidate_dirty`. The parent applies semantic package-lifecycle routing;
unknown impact is `candidate_dirty`, while unaffected results remain reusable.

## Stop and Report

Stop for unlisted paths; unenumerated cross-package scope; public API/schema/contract, dependency/service/config,
or product change; security/privacy/data/concurrency/performance risk; unsafe command; external fact; or risk
acceptance. Never silently expand; only the parent may clarify or authorize a coherent enumerated seam repair.

Return at most:

- `status`: `COMPLETE|BLOCKED` and packet/contract receipt;
- `state`: mode, worktree/ref/base, starting comparisons, ending HEAD and complete state;
- `findings`: per key reproduction, repair, and closure evidence;
- `changes`: changed/untracked paths with purpose and scope validation;
- `regression` and `verification`: commands/results, bounds, termination, cleanup, and not-run reasons;
- `self_review`: minimality, behavior, secret/residue, untracked checks, `unresolved_concerns`, and exactly one
  `design_and_smell_review: complete; material_findings=none|fixed:<items>; justified_non_actions=none|<evidence>`;
  only no-implementation-delta or purely mechanical evidence refresh may use
  `design_and_smell_review: not_applicable; reason=<concrete reason>`, and success requires no open concern;
- `pipeline_freshness_handback`: impact map/disposition, or `not_applicable` for local;
- `blocker_or_expansion`, `remaining_risks`, and confirmation that no forbidden action occurred.

The parent compares report and actual state to the packet before Fix Verification. Missing fields, drift,
out-of-scope changes, forbidden action, or uncertain pipeline impact blocks completion.
