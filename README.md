# Super Developer Marketplace

A marketplace for portable coding-assistant workflow skills, currently packaged for Claude Code.

## Plugins

| Plugin | Description |
|---|---|
| [**super-developer**](plugins/super-developer/) | Full development lifecycle — divergent ideation, requirements-spec-driven planning, parallel implementation with git worktree isolation, multi-agent adversarial code review, and gated release publishing. 9 skills. |

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

Orchestrates the full development lifecycle with 9 skills:

```
implementation-plan → review-plan → implement → audit → review-code → release
```

The planning stage uses triggered Design Preflight for nontrivial or risky features, then creates `.tasks/<feature>/SPEC.md` for user requirements, feature-level acceptance criteria, constraints, code references, and out-of-scope boundaries, plus `tasks.json` for agent-executable work, work packages, and accepted `design_decisions`.

Plus standalone skills: **perspectives** (divergent problem-solving), **tasks** (status dashboard), **review-code** (works independently for PR and local code review), **code-doc** (generate comprehensive codebase documentation via hybrid analysis), and **release** (prepare/publish releases with approval gates).

See the [full documentation](plugins/super-developer/README.md).

## License

MIT
