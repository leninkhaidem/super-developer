# Known Risk Patterns

## Boundary

This is a probe library only; do not persist these prompts as registry fields or generic checklists.

## Probes

- **Optional boundary fields and defaults** — When payloads, requests, configs, commands, events, or serialized
  records cross a boundary, verify permitted omission, applicable defaults, and whether omission differs from
  explicit empty, null, or false values.
- **Generated contract defaults** — When code consumes generated clients, schemas, types, CLIs, fixtures, or docs,
  verify generated defaults and compatibility at that boundary instead of inferring from handwritten wrappers.
- **Global, import, environment, and test pollution** — When tests or runtime code mutate caches, registries,
  environment, globals, monkeypatches, or singletons, run ordering checks or explain why the trigger is irrelevant.
- **Cache invalidation** — For memoized state, caches, registries, generated artifacts, or retained handles, verify
  invalidation across write/update/delete/reset and relevant process, request, tenant, user, or config boundaries.
- **Lifecycle/reaper partial outcomes** — For cleanup, retries, migrations, queues, finalizers, or background work,
  verify partial outcomes, idempotent reruns, interruption, stale ownership, and observable skipped/failed items.
- **Model/default precedence** — When several defaults or overrides apply, verify deterministic precedence among
  user input, config, environment, generated/stored defaults, flags, model preferences, and hardcoded fallbacks.
- **Pure boundary contract construction** — For payload, request, config, or command contracts, prefer small pure
  builders and tests of the observable contract over scattered ad hoc construction.
- **Harness discovery and readiness** — For a changed, shared, costly, or unproven harness, verify discovery,
  environment/data preconditions, isolation, bounded completion, and teardown before broad execution.
- **Fixture-contract fidelity** — When fixtures, mocks, generated inputs, clients, schemas, or runtime config cross
  a boundary, verify authoritative constraints, omission/null/default semantics, consumer compatibility, and
  resource/rate/concurrency budgets before treating them as executable evidence.
- **Asynchronous settlement and process ownership** — For barriers, routes, deferred work, subprocesses, servers,
  queues, or callbacks, verify every path settles or cancels, descendants terminate, progress is observable, and
  cleanup survives timeout or interruption.
- **Timeout and fail-fast amplification** — When an action can inherit an outer timeout or one failure can suppress
  later evidence, verify action-level bounds, failure isolation, progress, and targeted execution before breadth.
- **Result freshness** — When repairs, merge resolutions, or artifact edits touch result-cited files,
  verification output, assigned Slice scope, package reports, or review readiness, restore freshness explicitly.

## Use

Scan probes against package scope, assigned Slices, verification expectations, changed code/diff/tests, and
runtime observations. Verifiers raise only applicable probes that reveal a real blocking finding
(correctness/security/data-loss/contract-break) or a missed Acceptance Checklist obligation; everything else is
an advisory note. Mention nearby high-signal non-applicable probes concisely; omit the rest instead of creating
durable noise.
