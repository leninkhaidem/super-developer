# Test Plan and Taxonomy

Boundary: load after source-state resolution when scouting a repository, routing feature surfaces to
test categories, or explaining unsupported mobile scope. This reference defines plan content; proof
receipts and browser artifact mechanics are separate action-point contracts.

## Scouting Contract

Scout before proposing test work. Do not assume language, framework, runner, app shape, service
layout, or test directory names from the request alone.

Discover and record:
- stack, manifests, lockfiles, package/build tools, scripts, and local runner commands;
- CI workflows, existing test jobs, report/artifact paths, and environment setup hints;
- existing test frameworks, helpers, fixtures, tags/markers, naming, and directory conventions;
- changed feature surfaces: public APIs, UI flows, CLI commands, library entrypoints, data/storage,
  adapters, background jobs, services, and compatibility boundaries;
- required local services, credentials by variable name, seed/reset hooks, generated assets, and
  stateful side effects that will need a Run Contract.

Prefer existing project conventions. If none exist, propose the smallest conventional structure that
can prove the approved behavior without reorganizing existing tests.

## Plan Item Shape

Each proposed item names the feature surface, category, purpose tag, target, candidate test path,
expected command, required artifacts, and any side effect that requires approval. A category applies
only when scouting shows the feature surface or project convention needs it. Never run every category
unconditionally.

Report native mobile app surfaces as unsupported scope. Do not substitute browser/web tests for native
or hybrid mobile app validation. Responsive web running in a browser may still use browser/web e2e.

## Core Categories

- Static/type/lint checks
  - Applicability: repo exposes relevant static, type, lint, formatting, schema, or generated checks.
  - Target: existing project commands, preferably narrowed to changed surfaces when supported.
  - Authoring expectation: reuse commands/config; add config only when approved and conventional.
  - Evidence: command, cwd, exit code, and output/report reference.
- Unit tests
  - Applicability: behavior can be isolated at code-level boundaries.
  - Target: unit under proof through the repo's unit framework.
  - Authoring expectation: assert success, failure, invalid/default input, and edge behavior; mocks or
    stubs may replace dependencies outside the behavior under proof, not the behavior itself.
  - Evidence: test file, assertions/fixtures summary, command, cwd, exit code, and output reference.
- Component/integration tests
  - Applicability: behavior crosses modules, adapters, filesystem, database, queue, service, or runtime
    lifecycle boundaries.
  - Target: real or realistic local dependencies according to established project convention.
  - Authoring expectation: set up fixtures, seed/reset state, and verify interaction outcomes.
  - Evidence: command proof, logs/output, fixture or data references, and seed/reset method.
- API/contract tests
  - Applicability: HTTP, RPC, event, schema, public API, SDK contract, or compatibility behavior matters.
  - Target: real handler/service, local app, or established contract runner.
  - Authoring expectation: cover request/response, schema, errors, compatibility, and auth boundary as
    applicable without leaking secret values.
  - Evidence: test file or contract artifact, request/response or schema reference, command proof.
- CLI tests
  - Applicability: command behavior, flags, stdin/stdout/stderr, exit code, files, or side effects matter.
  - Target: built/local binary or command entrypoint in the repo's normal execution mode.
  - Authoring expectation: assert argv, cwd behavior, exit codes, output, error paths, and approved side
    effects with isolated state.
  - Evidence: argv, cwd, stdout/stderr refs, exit code, and side-effect proof.
- Browser/web end-to-end tests
  - Applicability: user-facing browser flow or frontend/backend integration proves the feature.
  - Target: real browser against a live app and the real backend/service dependencies required by flow.
  - Authoring expectation: map acceptance scenarios to stable user-visible actions and assertions.
  - Evidence: command proof plus video and screenshot/image artifacts mapped to scenarios.
- Smoke/regression tests
  - Applicability: high-value existing behavior or release confidence should remain intact.
  - Target: smallest meaningful real path using existing smoke/regression convention.
  - Authoring expectation: keep small, deterministic, and tied to the changed risk surface.
  - Evidence: scenario mapping, command proof, and output or artifact references.

## Conditional Categories

Performance/load, accessibility, visual regression, and security-focused checks are discover-and-propose
categories. Include them only when the feature risk, existing project convention, user request,
or changed surface warrants them. State the target, cost, environment needs, evidence, and approvals
needed; otherwise record why they were not selected.

## Stop If

Stop rather than inventing structure when scouting cannot identify enough tooling or surfaces for a
truthful plan, when safe category execution would need unapproved dependencies or environment setup,
or when the only requested scope is unsupported mobile app testing.
