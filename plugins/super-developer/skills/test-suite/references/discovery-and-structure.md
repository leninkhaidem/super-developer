# Project Scouting, Test-Plan Discovery, Routing, and Structure

Load when scouting the project, discovering the test plan, classifying surfaces and levels, or deciding where
authored tests live. The parent skill owns approval, dispatch, and gating; this reference owns scouting, the
test-plan contract, surface→level routing, generic level-target discipline, and the test-structure map.
Type-specific mechanics (for example browser end-to-end) live in their own reference.

## Scout the Project First

Before proposing any plan, learn what the project is:

- language/stack and build tooling, from manifests, lockfiles, and CI config;
- any existing test framework, runner, and directory convention;
- existing test tags/markers and naming patterns already in use;
- the feature's surfaces: backend service, web frontend, CLI, library, or a new one.

Plan from what you find, never from an assumed stack. Report the scouting result as part of the plan.

## Test-Plan Discovery

Identify the feature's surfaces, then derive candidate tests from the first available source and confirm:

1. Plan Slices under `.planning/<concept-slug>/slices/` when present — enumerate the behaviors and user-facing
   flows the feature adds or changes.
2. Else the git diff against base and the changed surface — map touched modules, handlers, routes, commands, or
   components to the behaviors and flows they need.
3. Else ask the user to name the feature, its surfaces, and expected behaviors/flows.

Cover happy paths plus material negative, error, and edge cases at each level.

## Surface to Level Routing

Each surface picks the levels it needs; coverage is project-dependent, so propose it and let the user adjust.
Routing names which levels apply — each level's mechanism is defined below or in the type reference:

- backend service → unit + integration;
- web frontend → unit + browser end-to-end (mechanism in `browser-e2e.md`);
- CLI tool → unit + end-to-end that spawns the built binary and asserts stdout, exit code, and side effects;
- library/SDK → unit + integration; browser e2e is usually N/A — say so.

Mobile app surfaces are out of scope; report them instead of substituting a browser.

## Level Target Discipline

Each level runs against a specific target; no level fakes the dependency it exists to exercise:

- unit → isolated; mocks/stubs allowed; no live app;
- integration/component → real dependencies (real requests against the running service, real DB/adapters);
- system/end-to-end → the live app with a real backend; never mock the thing under proof.

## Test-Plan Contract

Present the derived plan as groups of (level × surface) plus named scenarios, and get explicit approval. The
approved plan is the completion contract:

- every planned test needs authoring and a passing run before completion;
- never silently drop, merge, or narrow an approved item — one that cannot pass is reported, not removed;
- tag each item `acceptance` (new behavior) or `regression` (retained). Per-type evidence rules live in the
  type reference.

## Test Taxonomy

Organize tests on two open axes plus one tag, so categories are generated rather than fixed:

- level: `unit` → `integration/component` → `e2e/system`;
- surface: `backend-service`, `frontend-browser`, `cli`, `library`, or a new surface as needed;
- purpose tag: `acceptance` vs `regression` — a tag, not a folder.

The four common categories fall out of this: backend `unit`, backend `integration` (often tagged
`regression`), frontend `unit`, and frontend-browser `e2e`.

## Directory and Structure Map

Never reorganize existing tests.

- Detect an existing convention (co-located `*_test.go`, `tests/` in Python, `e2e/` in JS, etc.) → adopt it as
  the binding structure.
- None found → establish the canonical layout: `tests/<level>/<surface>/<feature>/`, one file per logical unit
  or scenario named by what it covers, with shared fixtures/config at the tree root.

Publish the adopted structure (approval-gated, append-only) to `docs/testing/test-structure.md` with a
lazy-load pointer in `AGENTS.md`. Every test later authored via this skill conforms to that map — the existing
convention when present, else the canonical layout.
