# Super Developer Marketplace

A collection of Claude Code plugins for software development.

## Plugins

| Plugin | Description |
|---|---|
| [**super-developer**](plugins/super-developer/) | Full development lifecycle — divergent ideation, requirements-spec-driven planning, parallel implementation with git worktree isolation, and multi-agent adversarial code review. 8 skills. |

More plugins coming soon: GitHub issue management, and others.

## Installation

```bash
# 1. Add the marketplace (one-time)
/plugin marketplace add leninkhaidem/super-developer

# 2. Install any plugin
/plugin install super-developer@super-developer-marketplace
```

### Available Commands

```bash
# List what's available
/plugin marketplace list

# Install a plugin
/plugin install <plugin-name>@super-developer-marketplace

# Update a plugin
/plugin update <plugin-name>@super-developer-marketplace

# Update all plugins in this marketplace
/plugin marketplace update super-developer-marketplace

# Reload after install/update
/reload-plugins
```

## Plugin Details

### super-developer

Orchestrates the full development lifecycle with 8 skills:

```
implementation-plan → review-plan → implement → audit → review-code
```

The planning stage creates `.tasks/<feature>/SPEC.md` for user requirements, feature-level acceptance criteria, constraints, code references, and out-of-scope boundaries, plus `tasks.json` for agent-executable work.

Plus standalone skills: **perspectives** (divergent problem-solving), **tasks** (status dashboard), **review-code** (works independently for PR and local code review), and **code-doc** (generate comprehensive codebase documentation via hybrid analysis).

See the [full documentation](plugins/super-developer/README.md).

## License

MIT
