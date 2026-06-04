# Model Preferences

Load before a skill spawns sub-agents and needs local model selection.

## Boundary

This reference owns local model preference keys and resolution. Each skill owns what its roles do after a value resolves.

## Local File

Path: `$PROJECT_ROOT/.claude/model-preferences.yml`

Create the local, gitignored file when missing:

```yaml
default-model: inherit
```

Ensure `.claude/model-preferences.yml` is ignored; it is developer-local preference, not repository state.

## Keys

```yaml
default-model: inherit
skeptic-agent: adaptive
implement: adaptive
review-plan: adaptive
review-code: inherit
```

| Key | Controls | Fallback |
|---|---|---|
| `default-model` | Global default | skill hardcoded default |
| `skeptic-agent` | Adversarial reviewers across skills | `default-model` → hardcoded default |
| `implement` | Implementation sub-agents | `default-model` → hardcoded default |
| `review-plan` | Plan-review standard reviewers | `default-model` → hardcoded default |
| `review-code` | Code and specialist reviewers | `default-model` → hardcoded default |

## Values

| Value | Meaning |
|---|---|
| `inherit` | Omit the model parameter so the sub-agent inherits the orchestrator model. |
| `adaptive` | Use the invoking skill's role-aware selection. |
| `<model-name>` | Pass the exact model name. |

Adaptive meanings:

| Role | Adaptive behavior |
|---|---|
| `implement` agents | Opus for complex/ambiguous packages; Sonnet for simple, patterned, unambiguous packages. |
| `review-plan` standard reviewers | Sonnet. |
| `review-code` code/specialist reviewers | Sonnet. |
| `skeptic-agent` adversarial reviewers | Strongest available model, normally Opus. |

## Resolution

1. Read `.claude/model-preferences.yml`; create it with `default-model: inherit` when missing.
2. Pick the value for the spawned role:
   - standard agent: skill-specific key → `default-model` → skill hardcoded default;
   - adversarial agent: `skeptic-agent` → `default-model` → skill hardcoded default.
3. Interpret the value in the role context:
   - `inherit`: omit the model parameter;
   - `adaptive`: apply the role behavior above;
   - any other value: pass it directly as the model parameter.

Hardcoded defaults are the final safety net when no relevant value exists:

| Skill | Hardcoded default |
|---|---|
| `implement` | `inherit` |
| `review-plan` | `inherit` |
| `review-code` | `inherit` |

## Examples

Default inherit behavior:

```yaml
default-model: inherit
```

Role-aware behavior:

```yaml
default-model: adaptive
```

Strong adversarial reviewers with cheaper standard agents:

```yaml
default-model: claude-sonnet-4
skeptic-agent: claude-opus-4
```
