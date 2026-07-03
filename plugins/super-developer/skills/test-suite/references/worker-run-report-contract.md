# Run and Report Worker Contract

Read this only inside the single run+report sub-agent session. You are not the orchestrator: it owns dispatch,
gating, and merges. Work from your packet and the files it names only; ignore ambient conversation history.

## Packet Fields

Your packet provides: the integrated test branch/worktree, the approved test plan (level × surface groups plus
e2e scenarios with `acceptance`/`regression` tags), the base URL of the running app when the plan needs one,
the type references for the planned test types (for example `browser-e2e.md`), the dashboard choice (Allure
default), and the artifact and proof paths. Stop and report if a required field is
missing or a required live app is not reachable.

## Workflow

1. Run every planned level against the target its type reference defines: lower levels isolated, higher levels
   against real dependencies, and system/browser levels against the live app with a real backend — never mock
   the dependency under proof. Use each runner's own parallelism; do not spawn agents.
2. Capture the evidence each test type requires (for browser e2e see `browser-e2e.md`: `acceptance` scenarios
   produce both a video and a screenshot); other levels and `regression` items rely on assertions.
3. Generate the unified dashboard (Allure by default; requires a JRE) aggregating all levels, and store the
   report plus e2e videos/screenshots under the gitignored `test-results/<slug>/`.
4. Do not modify product code, test logic, or config to force a pass. A failing test is reported red with its
   evidence.

## Proof Receipt

Write a committed `test-proof.md` mapping each planned item to: level, surface, test file, pass/fail, the
target used (isolated / real-deps / live-app), and artifact paths (video/screenshot for e2e acceptance). Mark
the run complete only when every planned test is green, e2e used a real backend, and every e2e `acceptance`
scenario has both artifacts.

## Completion Report

Return: the pass/fail matrix by level and surface, the dashboard path, artifact paths, the `test-proof.md`
path, any red tests with evidence and likely cause, and whether the gate conditions are met. Do not report
success when any planned test is red or missing required evidence.
