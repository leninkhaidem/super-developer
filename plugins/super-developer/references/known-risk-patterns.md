# Known Risk Patterns

Generic prompt source for planning, implementation, review, and must-prove checklists. This is not a schema, risk-tag taxonomy, or persistent checklist. Use it to sharpen probes, then record feature-specific proof in acceptance criteria, verification hints, context bundles, package proof files, reviews, or audit output.

## Required Probes

- **Optional boundary fields and defaults** — When payloads, requests, configs, commands, events, or serialized records cross a boundary, prove which fields may be omitted, which defaults are applied, and whether omission differs from an explicit empty/null/false value.
- **Generated contract defaults** — When code consumes generated clients, schemas, types, CLIs, fixtures, or docs, verify generated defaults and compatibility at the generated boundary; do not infer behavior from handwritten wrappers alone.
- **Global, import, environment, and test pollution** — When tests or runtime code mutate import caches, module registries, environment variables, globals, monkeypatches, singleton caches, or equivalent shared process state, run pollution-sensitive ordering checks: test alone, test before and after likely consumers, and the combined affected suite, or document why the trigger does not apply.
- **Cache invalidation** — For memoized state, caches, registries, singletons, generated artifacts, or retained handles, prove invalidation on write/update/delete/reset paths and across process, request, tenant, user, and configuration boundaries that matter to the feature.
- **Lifecycle/reaper partial outcomes** — For cleanup, reapers, retries, migrations, queues, finalizers, or background work, prove partial success, partial failure, idempotent reruns, interruption, stale ownership, and observability of skipped or failed items.
- **Model/default precedence** — When multiple defaults or overrides can apply, prove deterministic precedence between user input, config files, environment, generated defaults, stored state, CLI flags, model preferences, and hardcoded fallbacks.
- **Pure boundary contract construction** — When constructing boundary payloads, requests, configs, command descriptors, or similar contracts with optional/default/contract-drift risk, prefer small pure builders and tests that assert the observable contract instead of scattering ad hoc construction through orchestration or UI code.

## Use

Before coding or reviewing a risky package, scan the probes above against the work package's acceptance criteria, risk tags, context bundles, and verification hints. Add only the applicable probes to the package's must-prove reasoning. Do not add durable checklist fields or new validator risk tags for these prompts.
