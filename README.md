# Super Developer Marketplace

A marketplace for portable coding-assistant workflow skills, currently packaged for Claude Code.

## Plugins

| Plugin | Description |
|---|---|
| [**super-developer**](plugins/super-developer/) | Full development lifecycle — divergent ideation, evidence-first planning and bug fixing, Slice-first planning, parallel implementation with git worktree isolation, final review-code/audit gates, and release publishing. 13 skills. |

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

Orchestrates the full development lifecycle with 13 skills:

```
conceptualize → implementation-plan → review-plan → implement → final review-code + final audit → release
```

The optional `conceptualize` stage maintains a minimal planning index and writes focused Slices only when useful. `implementation-plan` delegates artifact authoring to planner agents that create `.tasks/<feature>/SPEC.md`, a lightweight `tasks.json` registry, package Markdown, declared proof paths, and package verification report paths. `tasks.json` is bookkeeping only; package Markdown owns work-package scope, Slice assignments, dependencies, verification expectations, proof paths, and report paths.

Optional Semgrep validation is disabled by default in the developer-local `.superdeveloper/preferences.yml`. First opt-in names any approved rule-cache clone or `git pull --ff-only`; routine scans stay local and run through the shipped helper, never raw Semgrep commands. Findings are advisory, evidence stays under `.tasks/<feature>/semgrep/`, and final audit remains read-only.

Plus standalone skills: **conceptualize** (minimal pre-planning index with optional handoff slices), **perspectives** (divergent problem-solving), **spike-to-plan** (empirical feature spikes before implementation planning), **spike-and-fix** (evidence-first bug diagnosis with isolated spike validation), **review-code** (works independently for PR and local code review), **code-doc** (generate comprehensive codebase documentation via hybrid analysis), and **release** (prepare/publish releases with approval gates).

See the [full documentation](plugins/super-developer/README.md).

## License

MIT
