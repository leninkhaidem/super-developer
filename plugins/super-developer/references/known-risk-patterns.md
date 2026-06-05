# Known Risk Patterns

## Boundary

This is a probe library only; do not persist these prompts as registry fields or generic checklists.

## Probes

- **Optional boundary fields and defaults** — When payloads, requests, configs, commands, events, or serialized records cross a boundary, verify which fields may be omitted, which defaults apply, and whether omission differs from explicit empty/null/false values.
- **Generated contract defaults** — When code consumes generated clients, schemas, types, CLIs, fixtures, or docs, verify generated defaults and compatibility at the generated boundary instead of inferring behavior from handwritten wrappers.
- **Global, import, environment, and test pollution** — When tests or runtime code mutate import caches, module registries, environment variables, globals, monkeypatches, singleton caches, or shared process state, run pollution-sensitive ordering checks or document why the trigger does not apply.
- **Cache invalidation** — For memoized state, caches, registries, generated artifacts, or retained handles, verify invalidation on write/update/delete/reset paths and across process, request, tenant, user, and configuration boundaries that matter.
- **Lifecycle/reaper partial outcomes** — For cleanup, reapers, retries, migrations, queues, finalizers, or background work, verify partial success, partial failure, idempotent reruns, interruption, stale ownership, and observability of skipped or failed items.
- **Model/default precedence** — When multiple defaults or overrides can apply, verify deterministic precedence between user input, config files, environment, generated defaults, stored state, CLI flags, model preferences, and hardcoded fallbacks.
- **Pure boundary contract construction** — When constructing boundary payloads, requests, configs, command descriptors, or similar contracts, prefer small pure builders and tests that assert the observable contract instead of scattered ad hoc construction.
- **Proof/report freshness** — When repairs, merge resolutions, or artifact edits touch proof-cited files, verification output, assigned Slice scope, package reports, or review readiness, verify freshness was restored rather than assuming the previous report still applies.

## Use

Scan the probes against the package scope, assigned Slices, verification expectations, changed files, and runtime observations. Add only applicable probes to package evidence, review findings, or audit reasoning. Omit non-applicable probes instead of creating durable checklist noise.
