---
name: test-suite
description: >
  Authors and runs a feature's test suite across whatever levels apply and proves it works. Use when
  asked to test a feature, write its tests, add unit/integration/e2e coverage, or verify it end-to-end. Do
  not use for code review, audit, release, or package implementation.
---

# Test Suite

Orchestrate proof that a delivered feature works: scout the project, derive an approved test plan across
whatever levels and surfaces apply, stand up any environment the plan needs, delegate isolated test authoring
plus one run+report pass, and gate on a green run with each test type's required evidence before the user
reviews and merges.

## Always

- The orchestrator orchestrates only: scout, derive the plan, confirm, set up worktrees and any environment,
  dispatch, validate, merge, gate, and present. It never writes test or product code inline — authoring and
  run work are delegated to sub-agents.
- Scout before planning: detect the language/stack, any existing test framework, convention, and tags, and the
  feature's surfaces. Derive the plan from what the project actually is, never from an assumed stack.
- Derive the plan from the feature's surfaces: each surface picks the levels it needs. Coverage is
  project-dependent — propose it, but let the user adjust which levels apply.
- Type-specific mechanics live in references, not here: before authoring or running any planned test type, load
  its reference to bind the target, evidence, and capture rules for that type.
- The approved test plan is the completion contract: every planned test needs authoring and a passing run
  before completion; never silently drop, merge, or narrow a planned item.
- Level discipline is generic here: each level runs against the target its reference defines — lower levels
  isolated, higher levels against progressively realer dependencies, system levels against the live app. No
  level fakes the dependency it exists to exercise.
- Each test type emits the evidence its reference requires; all levels report into one aggregated dashboard.
- A red test blocks completion. Report it honestly with evidence; never patch product code to force green —
  product changes route to user approval or the `diagnose-and-fix` skill.
- Never reorganize existing tests. Conform to an existing test convention when present; otherwise establish the
  canonical taxonomy. Every test authored by this skill follows the adopted structure.
- Secrets live only in a gitignored env file; verify it is gitignored before writing any secret, and reference
  secrets by variable name and path in committed docs, never by value.
- Git actions are orchestrator-owned through the `worktree` skill; the root worktree is never switched. Merge
  to base is local only — never auto-push. The primary human gates are the test-plan contract, the Run
  Contract, and the final review-and-merge; auto-resolve between them still stops only for the conform-vs-add
  decision, secret/gitignore safety, and persistence writes.

## Do

1. Resolve the base ref and feature slug, then scout and plan: load `references/discovery-and-structure.md`,
   detect the stack, any existing test convention and tags, and the feature's surfaces; derive the level
   coverage per surface, and seed items from plan Slices if present, else the git diff / changed surface, else
   ask. Present the plan (groups by level × surface plus named scenarios) and get approval — it is the
   completion contract.
2. Detect any existing test stack/convention; when one exists, STOP and ask whether to conform to it or add the
   missing runners alongside.
3. For each planned test type, load its reference to bind mechanism, target, and evidence: browser end-to-end →
   `references/browser-e2e.md`; any level needing a live app, credentials, or dashboard wiring →
   `references/environment.md`. Other levels follow the target discipline in
   `references/discovery-and-structure.md`.
4. Load `references/run-contract.md`; present the Run Contract (base ref, test branch, plan, deps to install,
   start command + URL when needed, seed/auth, dashboard, artifact paths, stop conditions, auto-resolve vs
   step-by-step) and get one approval.
5. After approval, use the `worktree` skill to create `feature/<slug>-tests` off base plus the setup,
   authoring, and integration worktrees without switching the root worktree; then start any needed environment
   and health-check it per `references/environment.md`.
6. Dispatch the setup sub-agent with `references/worker-authoring-contract.md`: it installs approved test
   dependencies and writes shared config (runners + dashboard wiring) for every planned level and hands off;
   the orchestrator merges its branch first through the `worktree` skill to establish the base.
7. Fan out authoring workers by logical group (level × surface) with `references/worker-authoring-contract.md`,
   each packet naming the type reference for its group; each owns non-overlapping test files and returns an
   item→test-file map and `SELF_REVIEW`. The orchestrator merges each returned branch into the test branch
   through the `worktree` skill without a per-merge approval.
8. Dispatch one run+report sub-agent with `references/worker-run-report-contract.md`: run every planned level
   against the target its type reference defines, generate the unified dashboard, collect each type's required
   evidence, and return the pass/fail matrix and the committed `test-proof.md`.
9. Gate: confirm every planned test is green and each test type produced its required evidence. On any red or
   missing evidence, STOP and report honestly. On pass, persist env setup and the test-structure map per
   `references/environment.md` and `references/discovery-and-structure.md` (approval-gated, append-only).
10. Present the proof receipt, dashboard path, and artifacts for user review; on approval, use the `worktree`
    skill to merge the test branch into base locally and clean up the branch/worktrees. Never auto-push.

## Load if needed

- A failing test requires a product/design fix → invoke the `diagnose-and-fix` skill.
- Risk probes for a complex authoring or run+report packet → `../../references/known-risk-patterns.md`
- A local model-preference override is intentionally resolved → `../../references/model-preferences.md`

## Stop if

- Feature surfaces, level coverage, base ref, or test branch cannot be safely derived, or the test-plan
  contract is unapproved.
- A level needs a live app or dashboard prerequisite that cannot be started or health-checked, or auth/seed
  cannot be resolved.
- An existing test stack/convention is detected but the conform-vs-add decision is unapproved.
- A secret would be written to a tracked (non-gitignored) file, or `.gitignore` cannot be safely updated first.
- The Run Contract is unapproved, or a requested git/remote action differs from it (any push, force, tag, or
  merge to a branch other than base).
- A planned test cannot pass, required evidence for a test type is missing, or passing would require a
  product/design change, scope expansion, unsafe command, or external credentials.
- The root worktree would need a branch switch, or the final merge-to-base/cleanup lacks explicit approval.

## Output

Return the approved test plan with per-test pass/fail by level and surface, the dashboard and artifact paths,
the `test-proof.md` path, the dev-env start summary (when used), branches/worktrees created and merged,
persistence writes (`AGENTS.md`, `docs/testing/`), blockers or red tests, and the next gate.
