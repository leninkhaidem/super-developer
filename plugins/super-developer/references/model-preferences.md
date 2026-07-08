# Local Preferences

## Boundary

This reference governs developer-local preference resolution before a skill delegates or spawns
agents. Model resolution never authorizes inline execution; callers must still dispatch the
resolved role/skill as a fresh sub-agent or Skill-tool invocation.

## Local File

Path: `$PROJECT_ROOT/.superdeveloper/preferences.yml`

Create the parent directory and file when missing with the full first-run defaults:

```yaml
models:
  default-model: inherit
  implementation-plan: inherit
  design-preflight: adaptive
  implement: adaptive
  review-plan: adaptive
  review-code: inherit
  skeptic-agent: adaptive

semgrep:
  enabled: false
  privacy-mode: true
  rules-provider: plugin-community-cache
  project-policy-gate: skeptic
```

Keep `.superdeveloper/preferences.yml` gitignored; it is developer-local preference, not
repository state. It is the only supported preferences file.

## Model Keys

Model preferences live under `models:`:

- `default-model` — fallback for every role.
- `implementation-plan` — delegated planning artifact writer.
- `design-preflight` — Design Preflight challenger sub-agents.
- `implement` — package implementation agents.
- `review-plan` — plan-review standard reviewers.
- `review-code` — code and specialist reviewers.
- `skeptic-agent` — adversarial reviewers across skills.

## Values

- `inherit` — omit model so the sub-agent inherits the orchestrator model.
- `adaptive` — use role-aware selection.
- `<model-name>` — pass the exact model name.

Adaptive defaults:

- `implementation-plan`: inherit unless local policy overrides.
- `design-preflight`: planning/challenge-aware selection, stronger for high-risk challenger lenses.
- `implement`: stronger model for complex/ambiguous packages; standard model for simple, patterned packages.
- `review-plan`: standard model.
- `review-code`: standard model.
- `skeptic-agent`: strongest available model.

## Resolution

1. Read `.superdeveloper/preferences.yml`; create it with the full defaults above when missing.
2. Resolve role value from `models.<role>` (including `models.design-preflight`) → `models.default-model` → hardcoded `inherit`.
3. Interpret value: `inherit` omits model, `adaptive` applies role behavior, any other value is
   passed directly.

For Semgrep key meanings, local policy files, and cache/network boundaries, load `semgrep.md` only
at the Semgrep action point.
