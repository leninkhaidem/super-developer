# Run Contract

Boundary: load when presenting the start approval or the final review-and-merge approval. This reference owns
the start and final approval gates; everything between them runs frictionless.

## Contract

- Derive the contract only from detected repo state, the approved test-plan contract, and explicit user
  instruction.
- Approval covers only the listed actions. Any push, force, tag, or merge to a branch other than base always
  needs separate explicit approval.
- Dependency installs (test runners, Playwright, Allure, JRE) and starting a dev app are covered only when
  named here.
- Auto-resolve continues through authoring, run, and gating until a stop condition or the final review gate.
  Step-by-step asks before each dispatch wave and the run pass.

## Start Template

```text
Test Suite Run Contract for <feature>

Refs:
  base ref: <base-ref>
  test branch: feature/<slug>-tests (off base)
Test plan:
  <level x surface groups + named scenarios, each tagged acceptance|regression>
Environment (only for levels needing a live app):
  start command: <cmd or none>    base URL: <url or none>
  seed/auth: <steps or none>
Deps to install: <runners/playwright/allure/jre list or none>
Dashboard: allure (local serve) | reportportal (opt-in)
Artifacts: test-results/<slug>/ (gitignored); proof: test-proof.md (committed)
Worktrees: setup + authoring (wp-style) + integration under .worktrees/<slug>-tests/
Not authorized: any push, target/main merge, force, tag, or product code changes
Choices: approve auto-resolve | step-by-step | abort
```

## Final Review Gate

Present the proof receipt, dashboard path, and each test type's required evidence before any merge. On explicit approval,
merge the test branch into base locally through the `worktree` skill and clean up the branch/worktrees. Never
auto-push; a remote push is always a separate explicit request.

## Stop if

- Any field cannot be derived from detected state or explicit instruction.
- The user asks the contract to authorize a push, force, tag, target/main merge, or product code change.
- A required live app cannot start or the JRE for Allure is absent.
