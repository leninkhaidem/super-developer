# Model Preference Examples

Optional examples for `model-preferences.md`; do not load this file for routine role resolution.

Default inherit behavior:

```yaml
default-model: inherit
```

Explicit role-aware behavior:

```yaml
default-model: adaptive
```

Strong adversarial reviewers with cheaper standard agents:

```yaml
default-model: claude-sonnet-4
skeptic-agent: claude-opus-4
```

Full control uses the same keys shown in `model-preferences.md`; omitted per-skill keys fall back
through `default-model`.
