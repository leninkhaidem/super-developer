# Model Preferences

## Boundary

This reference governs local model preference keys and resolution before a skill delegates or
spawns agents. Model resolution never authorizes inline execution; callers must still dispatch the
resolved role/skill as a fresh sub-agent or Skill-tool invocation. Each skill owns role behavior
after a value resolves.

## Local File

Path: `$PROJECT_ROOT/.claude/model-preferences.yml`

Create it when missing:

```yaml
default-model: inherit
```

Keep `.claude/model-preferences.yml` gitignored; it is developer-local preference, not repository state.

## Keys

```yaml
default-model: inherit
implementation-plan: inherit
implement: adaptive
review-plan: adaptive
review-code: inherit
skeptic-agent: adaptive
```

- `default-model` — fallback for every role.
- `implementation-plan` — delegated planning artifact writer.
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
- `implement`: stronger model for complex/ambiguous packages; standard model for simple, patterned packages.
- `review-plan`: standard model.
- `review-code`: standard model.
- `skeptic-agent`: strongest available model.

## Resolution

1. Read `.claude/model-preferences.yml`; create it with `default-model: inherit` when missing.
2. Resolve role value: role key → `default-model` → hardcoded `inherit`.
3. Interpret value: `inherit` omits model, `adaptive` applies role behavior, any other value is passed directly.
