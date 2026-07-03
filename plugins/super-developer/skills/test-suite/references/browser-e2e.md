# Browser End-to-End Tests

Load when the plan includes a browser end-to-end item, before authoring or running it. The parent skill owns
plan approval, dispatch, and gating; `environment.md` owns live-app startup, secrets, and the dashboard. This
reference owns the browser-e2e mechanism, evidence, and capture rules.

## Target

- Drive a real browser (Playwright by default) against the live app started per `environment.md`.
- Use a real backend; never mock, stub, or fake the backend the flow exercises — proving that path is the
  point of this level.
- If the repo already uses a browser-test framework, conform to it; otherwise add Playwright alongside per the
  conform-vs-add decision.

## Scenarios and Assertions

- One file per user-facing scenario, named by the flow it proves, under the adopted structure.
- Assert observable outcomes a user would see and the resulting backend state — not merely that a page loaded
  or a request returned 200.
- Cover the happy path plus material negative, error, and edge flows for the feature.

## Evidence and Capture

- `acceptance` scenarios (new behavior) must capture both a video and a screenshot of the proven flow.
- `regression` scenarios rely on assertions; capture is optional, since the agent checks the result.
- Enable Playwright video and screenshot capture in the shared config (setup worker), and attach traces on
  failure.

## Dashboard

Attach each scenario's video, screenshot, and trace to the aggregated dashboard (Allure by default; see
`environment.md`), stored under the gitignored `test-results/<slug>/`. A browser-e2e run is complete only when
every planned scenario is green, ran against a real backend, and every `acceptance` scenario has both a video
and a screenshot.
