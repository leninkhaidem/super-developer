# Browser E2E Stack Setup Reference

Use this only after generic command safety and web discovery when the task asks to propose or set up
a reusable browser E2E stack, evidence toggles, reporting, Playwright, Allure, or when no adequate
browser/reporting convention exists. This reference helps draft an approval plan; it does not
authorize installs, manifest edits, lockfile changes, browser config, CI, or service orchestration.

## Setup Decision

1. Reuse existing project tools if they can provide repeatable browser runs, scenario status,
   screenshots/video when needed, and a reviewable report.
2. If tools exist but lack evidence/reporting, propose the smallest enhancement to that stack.
3. If no adequate stack exists, propose Playwright + Allure as the preferred baseline. If the repo
   has no Node package manager, explicitly ask whether adding a Node-based browser test toolchain is
   acceptable before planning file edits.
4. Keep the approval plan concrete: files to change, packages to add, commands to expose, env vars,
   artifact directories, cleanup behavior, and redaction risks.

## Recommended Convention

Use project-native names when present. Otherwise propose equivalents for these controls:

| Purpose | Example name | Notes |
|---|---|---|
| Browser base URL | `E2E_BASE_URL` or `PLAYWRIGHT_BASE_URL` | Default only to a local/dev URL. Never production. |
| API URL | `E2E_API_URL` | Optional; use for pre-browser setup/cleanup only. |
| Evidence mode | `E2E_MODE=human-review|regression` | Human review is artifact-heavy; regression is lighter. |
| Video | `E2E_VIDEO=off|on|retain-on-failure|hd` | `hd` should use a readable viewport/recording size. |
| Screenshots | `E2E_SCREENSHOTS=off|failures|checkpoints` | Checkpoints are deliberate test attachments. |
| Report | `E2E_REPORT=project-native|allure` | Allure is the fallback dashboard baseline. |
| Web server | `E2E_WEB_SERVER_COMMAND` | Optional; starting servers is approval-gated. |

Artifact directories should be ignored by git, commonly `test-results/`, `playwright-report/`,
`allure-results/`, and `allure-report/`.

## Script Shape

For a Node project, propose scripts like these and adapt names to the package manager:

```json
{
  "test:e2e": "playwright test",
  "test:e2e:review": "E2E_MODE=human-review E2E_VIDEO=hd E2E_SCREENSHOTS=checkpoints playwright test",
  "test:e2e:regression": "E2E_MODE=regression E2E_VIDEO=retain-on-failure E2E_SCREENSHOTS=failures playwright test",
  "test:e2e:report": "sh scripts/e2e-report.sh",
  "test:e2e:review:report": "E2E_MODE=human-review E2E_VIDEO=hd E2E_SCREENSHOTS=checkpoints sh scripts/e2e-report.sh",
  "test:e2e:report:open": "allure open allure-report",
  "test:e2e:codegen": "playwright codegen ${E2E_BASE_URL:-http://localhost:3000}"
}
```

The report helper should run `playwright test "$@"`, store its exit code, generate the dashboard,
and exit with the original test status. If the target shell/package manager cannot run this form,
propose an equivalent checked-in test helper after approval.

## Playwright Config Shape

When approval includes Playwright config, map env vars once in the config and keep test files simple:

```ts
const baseURL = process.env.E2E_BASE_URL ?? process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3000"
const mode = process.env.E2E_MODE ?? "regression"
const videoEnv = process.env.E2E_VIDEO ?? (mode === "human-review" ? "hd" : "retain-on-failure")
const screenshotEnv = process.env.E2E_SCREENSHOTS ?? (mode === "human-review" ? "checkpoints" : "failures")
const hd = { width: 1920, height: 1080 }
const video = videoEnv === "hd" ? { mode: "on", size: hd } : videoEnv === "on" ? "on" : videoEnv === "off" ? "off" : "retain-on-failure"
const screenshot = screenshotEnv === "failures" || screenshotEnv === "checkpoints" ? "only-on-failure" : "off"
```

Use the mapped values in `defineConfig`: `baseURL`, `trace: "retain-on-failure"`, `video`,
`screenshot`, a single browser project unless the plan needs more, and an Allure reporter only when
approved. Add `webServer` only from an existing or approved `E2E_WEB_SERVER_COMMAND`.

## Test Helper Shape

For human-review mode, tests need deliberate attachments, not just global config. Propose helpers:

```ts
export async function checkpoint(page, testInfo, name) {
  if (process.env.E2E_SCREENSHOTS === "checkpoints") {
    await testInfo.attach(`${name}.png`, { body: await page.screenshot(), contentType: "image/png" })
  }
}

export async function reviewPause(page, ms = 500) {
  if (process.env.E2E_MODE === "human-review") await page.waitForTimeout(ms)
}
```

Use role/label/text locators for the visible journey. API setup may happen before the first page so
videos start at meaningful UI, but the recorded flow should use real user actions. Split distinct
journeys into separate tests so each has focused artifacts.

## Documentation to Add

A setup plan should propose docs such as `e2e/README.md` or `docs/testing/browser-e2e.md` covering:

- required env vars, safe defaults, and how to avoid sourcing secret-bearing env files;
- normal, human-review, regression, report, and codegen commands;
- where videos, screenshots, traces, and dashboards are written;
- how scenario names map to artifacts and report entries;
- cleanup limits, owned test data, blocked-precondition outcomes, and redaction rules;
- that generated artifacts stay out of git.

## Approval Boundary

Before approval, only write the plan. After approval, limit edits to agreed test surfaces: E2E test
directory, test helpers, browser test config, test docs, ignore rules for generated artifacts, and
manifest/lockfile changes explicitly named in the plan. Never use this setup to target production,
record secrets, mutate shared unsafe data, or weaken product behavior.
