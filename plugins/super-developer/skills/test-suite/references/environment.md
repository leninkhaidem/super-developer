# Dev Environment, Persistence, and Dashboard

Load when a planned level needs a live app, or when handling credentials/seed data, persisting setup, or
wiring the results dashboard. The parent skill owns approval and gating.

## When a Live App Is Needed

Only browser e2e and service-integration levels need a running app; unit-only surfaces skip startup. For those
levels, detect the start command and base URL from `package.json` scripts, `Makefile`, `docker-compose`, and
`README`. Present the detected command, URL, and env/seed/auth needs in the Run Contract; start nothing before
that approval. After approval, start the app and health-check the base URL before the run pass, and tear it
down at the end.

## Credentials and Seed Data

Resolve auth and seed data both ways, and stop when unresolved:

- auto-detect seed scripts and a `.env.test`/fixtures convention;
- STOP and ask when auth or seed cannot be resolved — never invent credentials.

## Secrets Safety

Secret values live only in a gitignored env file (for example `.env.test`):

- verify the env file is gitignored before writing any secret; if it is tracked or `.gitignore` lacks it, add
  the ignore rule first (approval-gated) — never write a secret to a tracked file;
- create the env file if it is absent;
- committed docs reference secrets by variable name and env-file path only, never by value.

## Persistence

After a passing gate, persist environment setup (approval-gated, append-only):

- write `docs/testing/test-environment.md`: start command, base URL, env variable names, seed/auth steps, and
  teardown;
- append one lazy-load pointer line to `AGENTS.md` (create it only with approval); never overwrite an existing
  `AGENTS.md` wholesale.

## Dashboard

The default dashboard is Allure — cross-stack, locally served, and it aggregates every level into one report
with history:

- the Allure CLI requires a JRE; STOP and report when Java is absent rather than skipping the dashboard;
- e2e attaches video/screenshot/traces; unit and integration attach their results and logs;
- generate and serve the report from the run+report pass and store it under the gitignored `test-results/<slug>/`.

ReportPortal is an opt-in escape hatch only when the user wants a persistent server and accepts its Docker
stack; do not stand it up by default.
