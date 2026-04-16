---
name: perspectives
description: >
  This skill should be used when the user asks to "explore approaches", "get multiple perspectives",
  "divergent analysis", "think about this from different angles", "architecture decision",
  "devil's advocate", or faces a complex design decision, architectural problem, or technical
  challenge. Triggers on phrases like "perspectives on", "multiple angles", "explore options",
  "compare approaches". Also appropriate when architecting a new product or facing ambiguous
  cross-cutting problems.
---

# Perspectives: Divergent Problem-Solving

Break out of single-solution thinking by delegating a problem to multiple sub-agents in parallel. Each sub-agent approaches the problem from a distinct angle, independently and without seeing each other's work. A final adversarial agent synthesizes and stress-tests the proposals into a recommendation.

The main agent frames the problem and assigns perspectives. Sub-agents solve independently. The main agent synthesizes at the end.

## Arguments

- `$ARGUMENTS` — Optional problem description or focus area. If omitted, infer from the conversation.

---

## Step 1: Frame the Problem

Review the conversation history and distill the problem into a structured brief. The brief must be self-contained — sub-agents receive no conversation history.

Produce a problem brief containing:

- **Problem statement:** What is happening and what is the impact. Include error messages, metrics, observed behavior where applicable.
- **Current state:** How the system works today. Relevant architecture, components, file paths, technology stack.
- **Constraints:** What cannot change (budget, timeline, backwards compatibility, team size, existing infrastructure).
- **What has been tried or considered:** Solutions already discussed and why they were insufficient. Prevents sub-agents from re-proposing rejected ideas.
- **Success criteria:** What a good solution looks like — performance targets, reliability requirements, acceptable tradeoffs.

## Step 2: Determine Perspectives

Based on the nature of the problem, decide:

1. **How many perspectives** — 2-3 for well-scoped problems with clear boundaries, 4-5 for ambiguous or cross-cutting challenges. Prefer fewer, high-quality perspectives over exhaustive coverage.
2. **What each perspective is.** Each must be a genuinely distinct lens — not a variation of the same approach. The goal is divergence.

Perspective types (inspiration, not a fixed menu):

| Type | Lens |
|---|---|
| Infrastructure / Scaling | Deployment, orchestration, resource allocation |
| Application Architecture | Structural redesign, patterns, decomposition |
| Data / IO | Database, caching, data flow |
| Operational / Pragmatic | Quickest path to stability, minimal changes, buy-vs-build |
| Defensive / Resilience | Fault tolerance, graceful degradation, circuit breaking |
| Root Cause | Challenge the premise — is the stated problem the real problem? **Trigger only when the problem describes symptoms without clear diagnosis** ("it's slow", "crashes occur", "users report errors"). Skip for well-scoped design/architecture decisions. |
| Domain-Specific | Patterns specific to the domain (event sourcing, CQRS, etc.) |
| Unconventional | An approach the team likely hasn't considered |

Announce the perspectives before spawning:

```
Problem: <concise statement>

Spawning N perspectives:
  1. <Name> — <focus areas>
  2. <Name> — <focus areas>
  ...
```

## Step 3: Spawn Sub-Agents in Parallel

Launch one **Opus-class sub-agent per perspective**, each receiving:

- The problem brief from Step 1 (identical for all)
- Their assigned perspective and a directive to solve the problem *only* through that lens
- Access to the project codebase for investigation
- Access to external research tools: WebSearch, WebFetch, and any MCP tools available in the environment (e.g., context7 for library/framework docs). Use whatever is relevant to the problem.

Each sub-agent must:

- **Investigate** the codebase through their assigned lens. Read relevant files, configs, logs.
- **Research externally when the lens demands it.** Pull in current library behavior, API changes, benchmarks, known issues, industry patterns, or prior art. Prefer context7 (or equivalent MCP) for library and framework documentation — training data may lag real releases. Use WebSearch/WebFetch for industry patterns, blog posts, standards, and non-library knowledge.
- **Diagnose** what they believe is happening, from their perspective.
- **Propose a solution** with:
  - Concrete implementation approach (specific changes to specific files — not abstract advice)
  - Tradeoffs: what this approach gains, costs, and risks
  - Effort estimate: 1-hour fix or multi-day refactor?
  - Limitations: what this approach does NOT solve
- **Cite external sources** (URLs, MCP source names) in proposals so the Skeptic can verify.
- **Do not fabricate citations.** If a search is empty or a tool unavailable, say so — no hallucinated sources.
- **Not collaborate** with other sub-agents. Each works independently.

Do not pass conversation history to sub-agents. They work from the problem brief, the codebase, and external research tools.

## Step 4: Collect and Present Proposals

Gather all sub-agent proposals and present them in a structured comparison:

```
## Perspective 1: <Name>
Diagnosis: <what they found>
Proposal: <their solution>
Tradeoffs: <gains vs costs>
Effort: <estimate>

## Perspective 2: <Name>
...
```

Do not editorialize or rank at this stage. Present each proposal on its own merits.

## Step 5: Adversarial Synthesis

Spawn one final **Opus-class sub-agent** — the Skeptic — with the problem brief, all proposals from Step 4, codebase access, and the same external research tools available to perspective sub-agents (WebSearch, WebFetch, MCPs). The Skeptic needs these to verify claims and cited sources in proposals independently.

The Skeptic must:

- **Stress-test each proposal:** What breaks? What edge cases are missed? What assumptions are wrong? **Challenge the premise:** Is the proposal solving the real problem, or just the stated one?
- **Identify complementary elements:** Are there proposals that solve different facets and could be combined?
- **Rank the proposals** by: effectiveness (does it solve the problem?), risk (what could go wrong?), effort (cost to implement), and durability (fix or band-aid?).
- **Produce a final recommendation:** Endorse one proposal, propose a hybrid combining the strongest elements, or recommend a phased approach (quick fix now, proper solution later).

## Step 6: Present Final Recommendation

Present the Skeptic's analysis and recommendation. Include:

- The recommended approach and why
- What was rejected and why
- Open questions or decisions requiring user input
- Suggested next step (continue discussing, or proceed to planning)

All findings remain in the conversation context for downstream skills to consume.

**Optional file output:** If the analysis is substantial (5+ perspectives or very detailed proposals), offer to write the recommendation to `docs/perspectives-<topic>.md` so the plan skill can reference it from disk rather than relying solely on conversation context.

---

## Rules

- **Divergence is the point.** If perspectives produce similar solutions, the perspectives were poorly chosen. Each lens must be meaningfully different.
- **Sub-agents investigate the codebase.** They read code, configs, and infrastructure definitions to ground their proposals in reality — not just theorize.
- **No premature convergence.** State the problem neutrally in the brief. Include what has been tried, but do not indicate a preferred direction.
- **The Skeptic is adversarial, not diplomatic.** Its job is to find flaws, not validate. A proposal that survives the Skeptic has earned its recommendation.
- **This skill does not produce implementation artifacts.** Its output is a recommendation ready to feed into planning.

---

## Pipeline Continuation

If this stage failed or requires user intervention, STOP. Do not invoke the next stage.

State: "Perspectives complete. Ready to convert this into a structured plan when you are — let me know if you have any follow-up questions first."

Wait for user confirmation. Then invoke:

Use the Skill tool with: skill: "implementation-plan"

Do NOT attempt to execute plan logic inline. The Skill tool loads it properly.
