# Evidence and Proof

Boundary: load when defining required evidence, browser/web acceptance proof, dashboards, red-test
handling, or the final portable proof receipt. This reference describes proof content, not worker
packet authority or environment approval.

## Portable Proof Receipt

Every completed run produces a durable proof receipt that can be reviewed without a dashboard. Store it
with stable relative or absolute artifact paths plus enough metadata to rerun or audit the result.

The receipt records:
- run ID or timestamp and run-specific artifact directory;
- tested feature/head branch or ref, tested commit SHA, target/base ref recorded separately, and the
  branch or worktree where proof commands ran;
- approved plan item to test file/config mapping;
- category, feature surface, and purpose tag for every item;
- exact commands, cwd, exit code, runner/report/output references, and relevant command ordering;
- environment summary without secret values: tool versions when relevant, service URLs, ports,
  variable names, seed/auth method, state reset method, and teardown result;
- artifact paths for logs, reports, fixtures, snapshots, generated outputs, traces, videos, and images;
- red-test evidence with affected plan items, failing command/output refs, missing artifacts, and likely
  cause classification such as product behavior, test defect, environment, data, or authorization.

Success is allowed only when every approved plan item is green and every category-required artifact
exists for the same run ID and tested commit. If an approved item is red, skipped without approval, or
missing evidence, return a red/blocker summary instead of success. Do not delete, weaken, skip, or
rewrite approved tests to hide product defects.

Dashboards, HTML reports, coverage views, traces, and hosted artifacts may supplement the receipt, but
no dashboard replaces it. The receipt must remain useful if dashboard access expires or the product is
unavailable.

## Browser/Web Evidence

Browser/web acceptance scenarios require proof from a real browser against a live app. The app must use
the real backend or service dependencies required by the flow. Do not mock the dependency under proof,
replace it with component snapshots, static screenshots, request stubs, or a non-browser renderer and
still claim browser/web e2e proof. Headless mode is acceptable only when it uses a real browser engine
and captures the required artifacts.

For each new behavior acceptance scenario, capture and map:
- video artifact path;
- screenshot or image artifact path at a meaningful state;
- command, cwd, exit code, output/report reference, and run ID;
- base URL, browser/engine, relevant viewport/device emulation if used, and health-check/start refs;
- traces, console logs, network logs, or server logs when useful as supporting evidence.

A single video or image can cover multiple planned scenarios only when the mapping is explicit and the
artifact visibly includes each scenario. If required video or screenshot/image evidence is absent,
malformed, stale, or from a different commit/run, the browser item is not complete.

Protect secrets and private data in proof. Use test accounts, masked values, or non-sensitive fixtures;
if a screenshot, video, log, or dashboard would expose a secret value or private data beyond approved
scope, stop and report instead of publishing it.

## Red-Test and Defect Routing

Red tests are valid evidence, not failure to perform the skill. Report the exact failing plan items,
commands, output refs, artifacts present/missing, likely cause, and whether rerun is safe. Product-code
defects route to a separate bug-fix workflow with this evidence; test-suite work does not patch product
code or change feature behavior to force green proof.

## Stop If

Stop when proof would rely on target/base without the delivered feature code, stale artifacts, ambient
manual state, dashboard-only evidence, missing required browser artifacts, or secret-bearing evidence
that cannot be safely excluded.
