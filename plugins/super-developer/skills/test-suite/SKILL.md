---
name: test-suite
description: >
  Orchestrates technology-agnostic feature test authoring and execution with portable proof.
  Use when asked to write or run tests for delivered feature work. Do not use for
  implementation, code review, audit, release, product bug fixing, or mobile app testing.
---

# Test Suite

Scout first, plan second, then delegate feature-test setup, authoring, execution, and proof through
explicit packets. This skill is a strict orchestrator; it proves delivered feature/head code with
portable receipts and never patches product code to make tests pass.

## Always

- Do not assume a language, framework, runner, app shape, CI, tag scheme, or test directory before
  scouting the repository and feature surface.
- Keep feature/head code under test separate from target/base. Tests and proof runs start from the
  delivered feature/head ref, not from target/base alone.
- Never switch the root worktree. Invoke `worktree` for branch/worktree creation, merges, pushes,
  cleanup, or other git lifecycle actions.
- Orchestrate only: do not write tests, shared test configuration, product code, proof receipts,
  dashboard artifacts, worktrees, merges, pushes, tags, or cleanup inline.
- Dependency installs, environment startup, secret/env-file writes, persistence writes, destructive
  reset/seed steps, product-code edits, pushes, force operations, target/base merges, tags, and
  cleanup require exact explicit approval at their own gates.
- Worker authority comes only from an explicit packet plus the referenced worker contract; never from
  hidden chat context, runtime identity, or broad permission implied by the skill invocation.
- Product-code defects found by tests are red-test evidence, not inline fix permission. Do not weaken,
  delete, skip, or rewrite approved tests to hide defects.
- Report discovered mobile app surfaces as unsupported scope; do not translate them into browser/web
  testing mechanics.
- Final success requires every approved plan item green, required category artifacts present, and a
  portable proof receipt. Dashboards may supplement the receipt but cannot replace it.

## Do

1. Classify the request. Continue only for authoring/running tests for delivered feature work; route
   implementation to `implement`, code review to `review-code`, completion audits to `audit`, releases
   to `release`, and product bug fixing to `diagnose-and-fix`.
2. Resolve and record source state before planning: feature/head ref and commit to test, target/base ref
   for later integration, relevant source materials, user constraints, and any existing approval limits.
   If branch/worktree preparation is needed, invoke `worktree`; do not create or switch checkouts inline.
3. Scout the repo before proposing tests. Inspect stack and package/build tooling, CI, existing test
   frameworks, tags/markers, directory conventions, current test commands, feature surfaces, fixtures,
   services, data dependencies, and browser/CLI/API/library boundaries.
4. Derive applicable categories from discovered surfaces and existing conventions. Prefer current
   project patterns; when none exist, propose the smallest conventional structure needed for the plan
   without reorganizing existing tests. Load taxonomy/evidence rules when category detail matters.
5. Present a test plan for explicit approval before workers act. Include plan items, feature surface,
   category, proposed test paths, command candidates, expected artifacts, unsupported mobile scope,
   assumptions, and side effects that will need a Run Contract.
6. Before any side-effectful setup or execution, present a Run Contract and obtain exact approval. The
   approved contract must name install/start commands, env-file paths and secret variable names only,
   persistence writes or seed/reset steps, artifact directories, ownership/teardown, optional dashboard
   tools, and non-authorized actions.
7. Prepare test branches/worktrees only through `worktree`, from the feature/head code ref. Run proof
   commands only on the integrated test branch/worktree that contains delivered feature code plus the
   authored tests/config. Never claim proof from a base-only branch unless the feature code is already
   included and recorded.
8. Dispatch setup, authoring, and run/report work through non-overlapping worker packets. Each packet
   must include goal, contract path, source materials, allowed write scope, feature/head and target/base
   refs, worktree paths, approved commands/checks, expected outputs, stop conditions, and completion
   report requirements.
9. Validate worker reports, git state, commands, artifacts, and proof receipt before final output. Check
   that proof state names the tested branch/ref and commit SHA, maps every approved plan item to tests
   and artifacts, records run ID/environment without secrets, and distinguishes green items from red.
10. If tests are red because delivered feature behavior appears defective, stop with red-test evidence,
    likely cause, affected plan items, commands/output references, and artifact paths. If the user wants
    a fix, route a separate `diagnose-and-fix` workflow with that evidence.
11. Ask for separate final approval before target/base merge, target/base push, feature push if not
    already approved, force operation, tag, cleanup, or teardown beyond the approved Run Contract.
12. Return the final operator-facing result; do not use planned-feature package or staging jargon.

## Load if needed

- Category selection, mobile exclusion, required evidence by category, or proof receipt contents are
  needed → `references/taxonomy-evidence-proof.md`
- Browser/web acceptance flows are planned or discovered → `references/browser-web-evidence.md`
- Dependency, environment, secret, persistence, artifact, dashboard, teardown, or idempotency details
  are needed → `references/run-contract.md`
- Setup, authoring, or run/report worker packet details are needed → `references/worker-contracts.md`

## Stop if

- The request is actually implementation, review, audit, release, product-code bug fixing, or mobile app
  testing rather than a feature test-suite workflow.
- Feature/head ref, target/base ref, testable feature surface, safe worktree path, or required source
  material is missing or ambiguous.
- Scouting cannot identify enough stack/tooling/test-convention information to propose a truthful plan.
- The user has not approved the test plan, the exact Run Contract side effect, or a final git/cleanup
  action that would be required next.
- A dependency install, env startup, secret write, persistence write, global/system change, push, force,
  tag, target/base merge, cleanup, or product-code edit is requested by implication only.
- A required reference for a triggered action point is unavailable or would be replaced by invented detail.
- Safe rerunnable execution cannot be established with available credentials, seed/reset hooks,
  isolation, artifact directories, process ownership, or teardown.
- Tests reveal product-code defects or approved plan items remain red.
- Proceeding would weaken approved tests, hide evidence, rely on stale artifacts, expose secret values,
  switch the root worktree, or prove a delivered feature from target/base alone.

## Output

Return:
- request classification and any routed-away near miss;
- feature/head ref and commit tested, target/base ref recorded, and worktree/branch paths used;
- scouting summary: stack/tooling, CI, existing test conventions, tags/markers, directories, and surfaces;
- approved plan items with category, test files, commands, status, and unsupported mobile scope if any;
- Run Contract approvals used, side effects performed, teardown result, and non-authorized actions left untouched;
- worker packets dispatched and worker report validation result;
- proof receipt path, run ID, command/output references, and artifact paths including browser videos/images when required;
- green proof summary or red-test/blocker summary with affected plan items, evidence, likely cause, and next route;
- pending approvals for merge, push, tag, cleanup, product fixes, or rerun.
