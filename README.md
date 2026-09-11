# Super Developer Marketplace

A marketplace for portable coding-assistant workflow skills, currently packaged for Claude Code.

## Plugins

| Plugin | Description |
|---|---|
| [**super-developer**](plugins/super-developer/) | Full development lifecycle — divergent ideation, evidence-first planning and bug fixing, Slice-first planning, testing workflow strategy and delegated test work, parallel implementation with git worktree isolation, final review-code/audit gates, README polish, release publishing, and standalone interactive walkthroughs. 16 skills. |

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

Includes 16 skills for the development lifecycle and standalone tasks:

```
conceptualize → implementation-plan → review-plan → implement → final review-code + final audit → release
```

`conceptualize` is conversation-first: invocation creates no files or worktrees. It checkpoints settled shared understanding only when durability is useful or necessary, or documentation is explicitly requested. Simple work can finish in chat; a compact Index or focused Slices support longer discussions and durable handoffs.

Clear, bounded, low-risk execution uses its task-appropriate workflow without mandatory planned-feature artifacts. Explicit planning requests and work needing durable coordination or material design/risk decisions use the full pipeline. `implementation-plan` delegates `SPEC.md`, a lightweight `tasks.json`, package Markdown, and result-report declarations. Package IDs are stable; Markdown owns assignments and Acceptance, while result reports hold observed evidence. The draft flows directly into plan review; the reviewed plan requires approval before execution.

Execution approval presents a concise scope/actions/checks/stops summary. Feature-source publication is separately contracted as local-only, per-package, milestone, or final; it is not an unconditional prerequisite for local progress. Final code review discovers production defects, while independent audit reconciles delivery evidence. Both must pass for the same integrated state.

Optional Semgrep validation is disabled by default in the developer-local `.superdeveloper/preferences.yml`. First opt-in names any approved rule-cache clone or `git pull --ff-only`; routine scans stay local and run through the shipped helper, never raw Semgrep commands. Findings are advisory, evidence stays under `.tasks/<feature>/semgrep/`, and final audit remains read-only.

Plus standalone skills: **conceptualize** (conversation-first discovery with need-based durable checkpoints), **perspectives** (divergent problem-solving), **empirical-spike** (bounded caller-neutral evidence when static sources cannot resolve a material behavior), **diagnose-and-fix** (evidence-first issue diagnosis with approval-gated fix routing), **testing** (establishes/updates reusable project testing workflows and routes authoring/execution through approved workflow docs), **review-code** (works independently for PR and local code review), **code-doc** (generate comprehensive codebase documentation via hybrid analysis), **readme-polish** (improve repository README and metadata), **release** (prepare/publish releases with approval gates), and **walk-me-through** (explicitly user-invoked, read-only interactive teaching with ASCII diagrams for practical ownership; not a lifecycle stage).

See the [full documentation](plugins/super-developer/README.md).

## License

MIT
