# Testing Workflow Contract Reference

Use this reference when a repository's reusable testing workflow is missing, stale, ambiguous, being
updated, or needed before test authoring/execution. It defines how to discover, initialize, update,
and apply project workflow documentation. It is not a stack methodology and does not authorize test
writes, test runs, installs, browser use, network access, live services, or config/CI changes.

## Authority and Canonical Interface

Authority order for testing work:

1. System, developer, current user, and current skill safety rules.
2. Approved project workflow docs for this repository.
3. Optional skill-local references, used only as proposal/adaptation aids.

The canonical project interface is root-relative:

- `AGENTS.md`: a short lazy-loading pointer for testing work. It should tell future agents to consult
  `docs/testing/workflow.md` when a task involves test strategy, authoring, alteration, or execution.
  If the file already exists, preserve unrelated content and add/update only the testing pointer.
- `docs/testing/workflow.md`: the reusable testing workflow entry point. It summarizes authority,
  scope, strategy, workflow state, approval gates, delegation rules, evidence/reporting, redaction,
  stale/conflict handling, and update procedure.
- `docs/testing/*`: optional companion docs loaded lazily when the entry point links them, such as
  stack details, fixture/data rules, live-service rules, browser E2E strategy, or reporting formats.

Do not silently choose alternate canonical paths. Lowercase `agents.md` and existing testing docs may
be candidates, but candidates are source material only: they govern test work only after
`docs/testing/workflow.md` exists, is accepted/current, and incorporates or references them through an
approved adopt, migrate, link, or initialize decision.

## Workflow State Routing

Classify workflow state before edits or commands:

- `approved/current`: `docs/testing/workflow.md` exists, has been accepted for the repository, is
  relevant to the task, and does not conflict with higher-priority instructions or clear repo
  evidence. Load linked companion docs as needed. Explicit initialize, update, adopt, migrate,
  link, or revise requests still route to the strategy interview; existing docs are source material.
- `missing`: no canonical entry point exists, including greenfield repositories with no/minimal tests or no documented testing strategy. Run candidate discovery and ask the user whether to adopt,
  migrate, link, or initialize through `docs/testing/workflow.md` before test edits, command runs, or delegation.
- `stale/ambiguous/conflicting`: a workflow exists but its commands, paths, stack assumptions,
  approval gates, safety stance, or acceptance/currentness conflict with repo evidence or the
  request. Recommend an update to the canonical entry and ask for approval before proceeding.
- `unsafe/refused`: the workflow or user decision would require unsafe, secret-bearing, production,
  or unapproved side effects, or the user refuses canonical workflow creation/update/adoption/linking.
  Stop or offer a safer documentation/update path.

## Missing-Workflow Candidate Discovery

Discovery is bounded, read-only, path-safe, symlink-safe, and secret-aware:

1. Check `docs/testing/workflow.md` first.
2. Inspect only project-owned candidate locations, including:
   - root `AGENTS.md`;
   - lowercase root `agents.md` as non-canonical candidate only;
   - `docs/testing/`, `docs/tests/`, and `docs/qa/`;
   - testing sections in root `README*` and other root project docs;
   - `README*` files under test, tests, spec, specs, e2e, integration, or similar test directories.
3. Avoid vendor/generated/dump/cache/build/dependency directories such as `node_modules`, `.git`,
   `dist`, `build`, `coverage`, reports, snapshots, binary artifact folders, and large dumps.
4. Do not follow symlinks outside the repository root. Treat unclear symlinks as blockers.
5. Summarize only relevant, sanitized facts: candidate path, why it looks like testing workflow
   material, scope/stack signals, known commands without secrets, and gaps/risks. Do not paste raw
   secrets, env files, tokens, proprietary data, screenshots, or large logs.
6. Present candidates as source material and ask the user to choose one canonical-file outcome:
   - **adopt** an existing canonical-quality doc as the basis for `docs/testing/workflow.md`;
   - **migrate** useful content into the canonical workflow entry point;
   - **link** from `docs/testing/workflow.md` to an existing curated companion doc;
   - **initialize** a new workflow from repo evidence and focused recommendations.

Candidate choice alone is not enough to proceed. First write or update `docs/testing/workflow.md` so
it incorporates or references the approved candidate and is accepted/current for the task. If the user
refuses all canonical-file options, stop. Do not perform one-off test edits, command execution, or
delegation.

## Recommendation-Led Initialization or Update

Start with repo evidence, not a broad questionnaire. Inspect relevant project files read-only, such
as manifests, scripts, test directories, fixtures, existing docs, app entry points, dev-server hints,
CI/config files, known report/artifact locations, and risk-sensitive data/auth boundaries. Use the
smallest useful evidence set; avoid large generated or secret-bearing files.

For greenfield/no-strategy repositories and explicit initialize, update, adopt, migrate, link, or revise requests, load `references/strategy-interview.md` and run the strategy interview before
accepted workflow-doc writes. Existing workflows, absent/minimal tests, candidates, and companion docs inform the recommendation but do not skip the interview. Ordinary author/alter/execute may use an accepted/current workflow only when adequate; missing, stale, ambiguous, conflicting,
unsafe, or insufficient workflows fail closed to this update path.

Interview one focused question at a time after the evidence summary. Start the user-facing strategy
branch with confidence goals, using optional examples only when helpful rather than a mandatory visible
menu. Resolve core domains or user deferrals: stack/surfaces, folders, plan policy, execution choices
and approvals, evidence/reporting, data/setup/cleanup, legacy stance, and stale/conflict updates.
Activate browser/web domains only when repo evidence, user scope, or selected strategy makes them material.

Then present a recommendation:

- name the recommended strategy and why repo evidence supports it;
- list what the workflow entry point and companion docs should contain;
- identify approval-gated actions and side effects that the strategy will not perform now;
- ask one focused confirmation or risk-boundary question when evidence is insufficient;
- adapt optional references only when they fit the repo and the user accepts the direction.

For missing browser E2E strategy, inspect the web stack, existing scripts/tests, app entry points,
dev-server assumptions, auth/data risks, and docs. If no adequate convention exists, the recommended
strategy may adapt the optional browser E2E reference for this project, but strategy establishment
still stops at a documentation proposal. It does not install dependencies, create browser config,
write tests, run browsers, start services, use recordings, touch secrets, access the network, edit
config/CI/orchestration, or execute tests.

## Draft and Approval Gate

Before writing root `AGENTS.md` or any `docs/testing/*` file, present a draft summary and proposed
file changes. The approval request should name:

- the `AGENTS.md` lazy pointer text or surgical update;
- `docs/testing/workflow.md` sections to create/update;
- companion docs under `docs/testing/` to create/update/link;
- methodology decisions and unresolved choices that will be persisted;
- accepted interview decisions for confidence goals, plan/test/report paths, coverage-index stance,
  execution choices, active conditional domains, reliability/cleanup, legacy stance, and explicit deferrals;
- approval-gated actions that remain outside the documentation update;
- redaction/privacy handling and stale/conflict update procedure.

Write workflow docs only after explicit current-task approval, including adopt/migrate/link updates
that create or change `docs/testing/workflow.md`. Persist accepted interview decisions in
`docs/testing/workflow.md` or linked `docs/testing/*` companions; a standalone questionnaire or
checklist is optional, not the default. If approval is not granted, continue focused discovery or
stop with the draft. Do not leave partial docs or candidate-only choices as accepted workflow.

## Minimal Workflow Entry Template

A project workflow entry point should be concise and reusable:

- purpose, authority, scope, and how this doc relates to `AGENTS.md`;
- confidence goals, strategy summary by relevant test levels, risk boundaries, and active conditional domains;
- links to companion docs and when to load them;
- safe discovery/update process for missing or stale conventions;
- folder/taxonomy and central feature test index or coverage-index stance (used, linked, or
  not used) for new plans, tests, evidence, reports, plus legacy stay-put or migration stance;
- feature/domain plan policy, approved plan path/version expectations, and plan-before-work gates;
- delegation rules for authoring, alteration, and execution;
- user-friendly execution choices, selected-choice reporting, and current-task approval gates for
  writes, commands, browser/live/network/dependency/config/CI/orchestration actions, and other side
  effects;
- evidence/reporting expectations, outcomes, skipped/not-run handling, cleanup, product-failure
  routing, redaction rules, and strict non-pass treatment for flaky or inconclusive results;
- procedure for updating the workflow when repo evidence changes.
