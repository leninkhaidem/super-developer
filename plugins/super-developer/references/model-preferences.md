# Model Preferences

Controls sub-agent model selection. Any skill that spawns sub-agents reads
`$PROJECT_ROOT/.claude/model-preferences.yml`, resolves each agent role, and applies the
role-specific meaning of the resolved value.

## Local File

Path: `$PROJECT_ROOT/.claude/model-preferences.yml`.

On first run, create the local, gitignored preference file when missing:

```yaml
default-model: inherit
```

This default preserves the orchestrator's currently selected model for delegated sub-agents. Use
`adaptive` only when the local preference file explicitly opts into role-aware model selection.

Ensure `.claude/model-preferences.yml` is ignored; this is local developer preference, not
repository state.

## Schema and Role Keys

```yaml
default-model: inherit       # global default for all agents; omit model parameter
skeptic-agent: adaptive      # optional: adversarial reviewers across skills
implement: adaptive          # optional: implementation sub-agents
review-plan: adaptive        # optional: Plan Reviewer
review-code: inherit         # optional: Code/Specialist reviewers
```

| Key | Controls | Fallback |
|---|---|---|
| `default-model` | Global default | skill hardcoded default |
| `skeptic-agent` | Adversarial agents: review-code Skeptic Agent, review-plan Security/Failure-Mode Reviewer | `default-model` → hardcoded default |
| `implement` | Implementation sub-agents | `default-model` → hardcoded default |
| `review-plan` | review-plan Plan Reviewer | `default-model` → hardcoded default |
| `review-code` | review-code Code Reviewer and optional Specialist Reviewer | `default-model` → hardcoded default |

Per-skill keys control standard agents only. The shared `skeptic-agent` key controls adversarial
agents across skills so users can pair cheaper standard agents with a stronger verifier.

| Skill | Standard agents | Adversarial agent |
|---|---|---|
| `implement` | `implement` key | N/A |
| `review-plan` | `review-plan` key → Plan Reviewer | `skeptic-agent` key → Security/Failure-Mode Reviewer |
| `review-code` | `review-code` key → Code/Specialist Reviewer | `skeptic-agent` key → Skeptic Agent |

## Values

| Value | Meaning |
|---|---|
| `inherit` | Omit the model parameter so the sub-agent inherits the orchestrator model. At `default-model`, this is the default and matches having no preferences file. |
| `adaptive` | Explicitly opt into the invoking skill's built-in role logic. |
| `<model-name>` | Pass the exact model name, such as `claude-opus-4` or `claude-sonnet-4`. |

Adaptive meanings:

| Role | Adaptive behavior |
|---|---|
| `implement` agents | Opus for complex/ambiguous tasks; Sonnet for simple, patterned, unambiguous packages. |
| `review-plan` Plan Reviewer | Sonnet. |
| `review-code` Code/Specialist Reviewer | Sonnet. |
| `skeptic-agent` adversarial roles | Strongest available model, normally Opus. |

## Resolution Procedure

1. Read `.claude/model-preferences.yml`; if missing, create it with `default-model: inherit` and
   ensure it is gitignored.
2. Normalize legacy files: `strategy` is treated as `default-model` only when `default-model` is
   absent; if both exist, `default-model` wins and `strategy` is ignored.
3. Pick the value for the role being spawned:
   - Standard agent: skill-specific key → `default-model` → that skill's hardcoded default.
   - Skeptic/adversarial agent: `skeptic-agent` → `default-model` → that skill's hardcoded default.
4. Interpret the resolved value in the target role's context:
   - `adaptive` applies the role behavior above. An `adaptive` inherited by a skeptic agent through
     `default-model` still means strongest available model/Opus.
   - `inherit` omits the model parameter.
   - Any other value is passed directly as the model parameter.

Hardcoded defaults are the final safety net only when the file exists but both the relevant key and
`default-model` are absent:

| Skill | Hardcoded default |
|---|---|
| `implement` | `inherit` |
| `review-plan` | `inherit` |
| `review-code` | `inherit` |

Load `references/model-preferences-examples.md` only when a user asks for sample configurations or
when illustrating preference combinations would change an action decision.
