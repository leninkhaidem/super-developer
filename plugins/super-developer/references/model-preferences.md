# Model Preferences

Controls how skills select models for sub-agents. Each skill that spawns sub-agents reads `.claude/model-preferences.yml` from the project root and resolves a model for each agent role.

---

## File Location and Lifecycle

**Path:** `$PROJECT_ROOT/.claude/model-preferences.yml`

**First run:** If the file does not exist, the skill auto-creates it with:

```yaml
# .claude/model-preferences.yml
# Controls model selection for sub-agents across all skills.
# Values: adaptive | inherit | <model-name> (e.g., claude-opus-4)
default-model: adaptive
```

**Gitignore:** This is a local developer preference — not committed. Ensure `.claude/model-preferences.yml` is in `.gitignore`:

```bash
grep -qF '.claude/model-preferences.yml' .gitignore 2>/dev/null || echo '.claude/model-preferences.yml' >> .gitignore
```

---

## Schema

```yaml
# Global default — applies to all agents unless overridden
default-model: adaptive

# Adversarial/skeptic agents across all skills
skeptic-agent: adaptive

# Per-skill overrides for standard agents (optional — omit to use default-model)
implement: adaptive
review-plan: adaptive
review-code: inherit
```

### Keys

| Key | Controls | Fallback |
|---|---|---|
| `default-model` | Global default for all agents | Skill's hardcoded default |
| `skeptic-agent` | Adversarial reviewers: review-code Skeptic, review-plan Plan Review Challengers | `default-model` → hardcoded default |
| `implement` | Implementation sub-agents (delegated tasks) | `default-model` → hardcoded default |
| `review-plan` | Review-plan Plan Quality Reviewer | `default-model` → hardcoded default |
| `review-code` | Review-code specialist agents (security, logic, performance, architecture) | `default-model` → hardcoded default |

### Role-to-Key Mapping

Per-skill keys control **standard agents only**. The `skeptic-agent` key controls **adversarial agents across all skills**. This split allows users to run cheap specialists with a strong adversarial reviewer.

| Skill | Standard Agents | Adversarial Agent |
|---|---|---|
| `implement` | `implement` key | N/A (no adversarial role) |
| `review-plan` | `review-plan` key → Plan Quality Reviewer | `skeptic-agent` key → selected Plan Review Challengers |
| `review-code` | `review-code` key → 4 specialists | `skeptic-agent` key → Skeptic Agent |

---

## Values

| Value | Meaning |
|---|---|
| `adaptive` | Skill uses its built-in model selection logic. Each SKILL.md defines what this means for its roles. For `skeptic-agent`, this means "strongest available model (Opus)" since it's cross-cutting with no SKILL.md. |
| `inherit` | No model override — sub-agents use the orchestrator's model. At the `default-model` level, this is equivalent to not having a preferences file at all. |
| `<model-name>` | Use that exact model (e.g., `claude-opus-4`, `claude-sonnet-4`). Passed directly as the model parameter to sub-agents. |

### Per-Skill Adaptive Interpretations

When a skill resolves `adaptive`, it applies its own role-based logic:

| Skill | Adaptive Behavior |
|---|---|
| `implement` | Opus for complex/ambiguous tasks, Sonnet for simple/patterned ones |
| `review-code` | Sonnet for specialists, Opus for Skeptic (via `skeptic-agent`) |
| `review-plan` | Sonnet for Plan Quality Reviewer, selected Plan Review Challengers governed by `skeptic-agent` key |

---

## Resolution Procedure

When a skill needs to determine the model for a sub-agent, follow this procedure:

### For Standard Agents

1. Read `.claude/model-preferences.yml`. If missing, auto-create with `default-model: adaptive`.
2. Check the **skill-specific key** (e.g., `review-code` for review-code specialists). If present, use its value.
3. If absent, check `default-model`. If present, use its value.
4. If absent, use the skill's **hardcoded default**.

### For Skeptic/Adversarial Agents

1. Read `.claude/model-preferences.yml`. If missing, auto-create with `default-model: adaptive`.
2. Check the `skeptic-agent` key. If present, use its value.
3. If absent, check `default-model`. If present, use its value.
4. If absent, use the skill's **hardcoded default**.

### Interpreting the Resolved Value

- `adaptive` → Apply the skill's built-in logic (see Per-Skill Adaptive Interpretations above). For `skeptic-agent`, use strongest available model (Opus).
- `inherit` → Do not pass a `model` parameter. The sub-agent inherits the orchestrator's model.
- Any other value → Pass it directly as the `model` parameter to the sub-agent.

**Value interpretation is role-context-dependent regardless of which fallback level provided it.** An `adaptive` value that reaches a skeptic agent via the `default-model` fallback is still interpreted in the skeptic context ("strongest model"), not the generic context.

### Hardcoded Defaults (Safety Net)

These are only reached when the file exists but both the relevant key and `default-model` are absent:

| Skill | Hardcoded Default |
|---|---|
| `implement` | `adaptive` |
| `review-plan` | `adaptive` |
| `review-code` | `inherit` |

---

## Backward Compatibility

The previous schema used a single `strategy` field:

```yaml
# Legacy format
strategy: adaptive
```

When the file contains a `strategy` key but no `default-model` key, treat `strategy` as `default-model`:

```yaml
# This legacy file...
strategy: adaptive

# ...is interpreted as:
default-model: adaptive
```

When both `strategy` and `default-model` coexist, `default-model` takes precedence. The `strategy` key is ignored.

---

## Example Configurations

### 1. Default — Role-Appropriate Selection

```yaml
# All skills use their built-in logic for role-appropriate model selection.
# Specialists get Sonnet, adversarial reviewers get Opus, complex tasks get Opus.
default-model: adaptive
```

### 2. Strong Skeptic, Cheap Everything Else

```yaml
# Standard agents use Sonnet across all skills.
# Adversarial agents (review-code Skeptic, review-plan Plan Review Challengers) use Opus.
default-model: claude-sonnet-4
skeptic-agent: claude-opus-4
```

### 3. Uniform Model with Per-Skill Override

```yaml
# Everything uses the orchestrator's model by default.
# But implementation tasks get Opus for complex work.
default-model: inherit
implement: adaptive
# Note: review-code specialists will inherit the orchestrator's model.
#       review-code Skeptic will also inherit (skeptic-agent falls back to default-model).
```

### 4. Full Control

```yaml
# Explicit model for every role.
default-model: claude-sonnet-4
skeptic-agent: claude-opus-4
implement: claude-opus-4
review-plan: claude-sonnet-4
review-code: claude-sonnet-4
# Result:
#   implement sub-agents → claude-opus-4
#   review-plan Plan Quality Reviewer → claude-sonnet-4, Plan Review Challengers → claude-opus-4
#   review-code specialists → claude-sonnet-4, Skeptic → claude-opus-4
```
