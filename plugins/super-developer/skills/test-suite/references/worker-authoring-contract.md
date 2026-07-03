# Setup and Authoring Worker Contract

Read this only inside a setup or authoring sub-agent session. You are not the orchestrator: it owns git
infrastructure, test-plan approval, dispatch, gating, merges, and the final summary. Work only from your packet
and the files it names; ignore ambient conversation history.

## Packet Fields

Your packet provides: role (`setup` or `authoring`), base info, your worktree path and branch, the assigned
test group as (level × surface) with items (authoring) or the shared-config scope for the planned levels
(setup), the adopted test-structure map, target test paths, the base URL when the level needs a live app, the
type reference for your group (for example `browser-e2e.md`), and approved deps/commands. Stop and report if a
required field is missing.

## Setup Role

- Install approved test dependencies and write shared config once for every planned level: test-runner configs
  (for example the unit runner and `playwright.config`), Allure wiring for each runner, and shared
  fixtures/helpers.
- Follow the adopted test-structure map; place shared fixtures/config at the tree root.
- Do not author individual tests. Merge first so authoring workers build on a stable base.

## Authoring Role

- Author tests only for your assigned group, in non-overlapping files under the adopted structure — one file
  per logical unit or scenario, named by what it covers.
- Match the level and the type reference named in your packet: run against the target it defines and enable
  the capture it requires; never fake the dependency the level exists to exercise.
- Assertions must prove behavior, not merely that code runs or a page loads.
- Do not edit shared config another worker owns, product code, or other workers' files.

## Both Roles

- Edit only inside your assigned worktree; follow `plugins/super-developer/references/clean-code-rules.md`.
- Do not create worktrees/branches/merges, start or stop the dev app, install unapproved deps, write secrets to
  tracked files, or change product code.
- Before handoff, self-review your diff and fix issues or report an exact blocker.

## Completion Report

Return: role, files created, item→test-file map (authoring) or shared-config summary (setup), deps installed,
capture settings enabled, self-review result, and any blocker. Include this block:

```text
SELF_REVIEW
diff_reviewed: yes
group_covered: <level x surface + item ids, or shared-config>
level_discipline: unit-isolated | integration-real-deps | e2e-real-backend-no-mocks | n/a
capture_enabled: video+screenshot | assertions-only | n/a
issues_found_and_fixed: <list or none>
unresolved_concerns: none or exact blocker
```
