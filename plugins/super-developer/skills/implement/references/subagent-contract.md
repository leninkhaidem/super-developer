# Implement Sub-Agent Contract Index

This compatibility index replaces the former mixed package/repair/orchestrator contract. Do not pass this file as the primary contract for new delegated work.

Use the role-specific references instead:

- Orchestrator dispatch packet construction: `plugins/super-developer/skills/implement/references/delegation-dispatch.md`
- Package implementation agents: `plugins/super-developer/skills/implement/references/package-agent-contract.md`
- Package repair agents: `plugins/super-developer/skills/implement/references/repair-agent-contract.md`
- Holistic package verification reviewers: `plugins/super-developer/skills/implement/references/package-verification.md`

The orchestrator should load `delegation-dispatch.md` only. It should pass the appropriate role-specific contract path to each sub-agent and should not load package/repair/verifier contracts or `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/clean-code-rules.md` into main context by default.
