# Model Preferences

Controls sub-agent model selection. Any skill that spawns sub-agents reads `$PROJECT_ROOT/.claude/model-preferences.yml`, resolves each agent role, and applies the role-specific meaning of the resolved value.

## Local File

Path: `$PROJECT_ROOT/.claude/model-preferences.yml`.

On first run, create the file when missing:

```yaml
# .claude/model-preferences.yml
# Values: adaptive | inherit | <model-name>
default-model: adaptive
```

This is a local developer preference, not repository state. Ensure `.claude/model-preferences.yml` is ignored, for example:

```bash
grep -qF '.claude/model-preferences.yml' .gitignore 2>/dev/null || echo '.claude/model-preferences.yml' >> .gitignore
```

## Schema and Role Keys

```yaml
default-model: adaptive      # global default for all agents
skeptic-agent: adaptive      # adversarial reviewers across skills
implement: adaptive          # implementation sub-agents
review-plan: adaptive        # Plan Reviewer
review-code: inherit         # Code/Specialist reviewers
```

| Key | Controls | Fallback |
|---|---|---|
| `default-model` | Global default | skill hardcoded default |
| `skeptic-agent` | Adversarial agents: review-code Skeptic Agent, review-plan Security/Failure-Mode Reviewer | `default-model` → hardcoded default |
| `implement` | Implementation sub-agents | `default-model` → hardcoded default |
| `review-plan` | review-plan Plan Reviewer | `default-model` → hardcoded default |
| `review-code` | review-code Code Reviewer and optional Specialist Reviewer | `default-model` → hardcoded default |

Per-skill keys control standard agents only. The `skeptic-agent` key controls adversarial agents across skills so users can pair cheaper standard agents with a stronger verifier.

| Skill | Standard agents | Adversarial agent |
|---|---|---|
| `implement` | `implement` key | N/A |
| `review-plan` | `review-plan` key → Plan Reviewer | `skeptic-agent` key → Security/Failure-Mode Reviewer |
| `review-code` | `review-code` key → Code/Specialist Reviewer | `skeptic-agent` key → Skeptic Agent |

## Values

| Value | Meaning |
|---|---|
| `adaptive` | Use the invoking skill's built-in role logic. |
| `inherit` | Omit the model parameter so the sub-agent inherits the orchestrator model. At `default-model`, this matches having no preferences file. |
| `<model-name>` | Pass the exact model name, such as `claude-opus-4` or `claude-sonnet-4`. |

Adaptive meanings:

| Role | Adaptive behavior |
|---|---|
| `implement` agents | Opus for complex/ambiguous tasks; Sonnet for simple, patterned, unambiguous packages. |
| `review-plan` Plan Reviewer | Sonnet. |
| `review-code` Code/Specialist Reviewer | Sonnet. |
| `skeptic-agent` adversarial roles | Strongest available model, normally Opus. |

## Resolution Procedure

1. Read `.claude/model-preferences.yml`; if missing, create it with `default-model: adaptive`.
2. Normalize legacy files: when `strategy` exists and `default-model` does not, treat `strategy` as `default-model`. If both exist, `default-model` wins and `strategy` is ignored.
3. Pick the value for the role being spawned:
   - Standard agent: skill-specific key → `default-model` → that skill's hardcoded default.
   - Skeptic/adversarial agent: `skeptic-agent` → `default-model` → that skill's hardcoded default.
4. Interpret the resolved value in the target role's context:
   - `adaptive` applies the role behavior above. An `adaptive` inherited by a skeptic agent through `default-model` still means strongest available model/Opus.
   - `inherit` omits the model parameter.
   - Any other value is passed directly as the model parameter.

Hardcoded defaults are the final safety net only when the file exists but both the relevant key and `default-model` are absent:

| Skill | Hardcoded default |
|---|---|
| `implement` | `adaptive` |
| `review-plan` | `adaptive` |
| `review-code` | `inherit` |

## Compact Examples

Default role-aware behavior:

```yaml
default-model: adaptive
```

Strong adversarial reviewers with cheaper standard agents:

```yaml
default-model: claude-sonnet-4
skeptic-agent: claude-opus-4
```

Full control uses the same keys shown in the schema; omitted per-skill keys fall back through `default-model`.
