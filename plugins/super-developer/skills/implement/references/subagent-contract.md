# Implement Sub-Agent Contract Index

Use role-specific references for delegated planned-feature work:

- Orchestrator dispatch packet construction: `plugins/super-developer/skills/implement/references/delegation-dispatch.md`
- Package implementation agents: `plugins/super-developer/skills/implement/references/package-agent-contract.md`
- Package repair agents: `plugins/super-developer/skills/implement/references/repair-agent-contract.md`
- Holistic package verification reviewers: `plugins/super-developer/skills/implement/references/package-verification.md`

The orchestrator should load `delegation-dispatch.md` only at dispatch/repair/verifier action points. It should pass the appropriate role-specific contract path to each sub-agent and should not load package/repair/verifier contracts or `plugins/super-developer/references/clean-code-rules.md` into main context by default.
