"""Static prompt-contract guards for Conceptualize capture/routing policy.

These checks do not execute an agent or prove runtime behavior. They guard policy structure:
conversation-first startup, readiness-driven questions, read-only resume,
uncertainty recovery, gated/delayed artifact writes, lossless Index/Slice handoffs,
route selection at handoff time, and planner handling of chat-only or Index-only
inputs.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (PLUGIN_ROOT / rel).read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)", text, re.M | re.S)
    if match is None:
        raise AssertionError(f"missing section: {heading}")
    return match.group("body")


def assert_has_all(test: unittest.TestCase, text: str, needles: list[str]) -> None:
    lowered = " ".join(text.lower().replace("**", "").split())
    missing = [needle for needle in needles if " ".join(needle.lower().split()) not in lowered]
    test.assertEqual(missing, [])


class ConceptualizeCapturePolicyTests(unittest.TestCase):
    def test_startup_is_conversation_first_and_write_free(self) -> None:
        skill = read("skills/conceptualize/SKILL.md")
        introduction = skill.split("## Always", 1)[0]
        assert_has_all(
            self, introduction, ["Invocation alone", "creates no files, slug", "artifact root", "worktree"]
        )
        first_step = re.search(r"^1\. (?P<body>.*?)(?=^2\. )", section(skill, "Do"), re.M | re.S)
        self.assertIsNotNone(first_step)
        assert_has_all(
            self,
            first_step.group("body"),  # type: ignore[union-attr]
            ["Start in chat", "do not", "artifact paths", "set up git"],
        )
        self.assertNotIn("Create and maintain at least one Slice before any successful handoff", skill)

    def test_settled_context_can_skip_questions(self) -> None:
        skill = read("skills/conceptualize/SKILL.md")
        always = section(skill, "Always")
        do = section(skill, "Do")
        readiness = do.index("Check next-step readiness")
        question = do.index("Otherwise ask one focused question")
        self.assertLess(readiness, question)
        assert_has_all(self, always, ["at most one focused question", "skip questions"])
        assert_has_all(
            self,
            do[readiness:question],
            ["before the first question", "after each answer", "approved context is sufficient",
             "ask no further questions", "Durability Gate"],
        )
        self.assertNotIn("Ask exactly one focused question", skill)

    def test_intent_discovery_does_not_require_premature_recommendations(self) -> None:
        always = section(read("skills/conceptualize/SKILL.md"), "Always")
        assert_has_all(
            self,
            always,
            ["Discover unclear intent", "open-ended questions", "recommendation only when",
             "evidence and the user's goals", "do not guess the audience, problem, or desired outcome"],
        )
        self.assertNotIn("For each material question, give your recommended answer", always)

    def test_unknown_answers_have_bounded_recovery_without_assumed_approval(self) -> None:
        do = section(read("skills/conceptualize/SKILL.md"), "Do")
        recovery = do[do.index("If the user cannot answer:"):do.index("Apply the **Durability Gate**")]
        assert_has_all(
            self,
            recovery,
            ["unclear intent", "concrete scenario", "unknown fact", "bounded read-only evidence",
             "uncertain preference", "without choosing for the user", "Keep hypotheses unapproved",
             "next useful action instead of repeating prompts or claiming readiness"],
        )

    def test_resume_reads_existing_context_before_questioning_without_a_checkpoint(self) -> None:
        do = section(read("skills/conceptualize/SKILL.md"), "Do")
        resume_start = do.index("When resuming an existing workspace")
        readiness = do.index("Check next-step readiness")
        gate = do.index("Apply the **Durability Gate**")
        self.assertLess(resume_start, readiness)
        self.assertLess(resume_start, gate)
        resume = do[resume_start:do.index("Gather bounded repository/research evidence")]
        assert_has_all(
            self,
            resume,
            ["artifact-store.md", "workspace-index.md", "safely resolve", "read the Index",
             "conceptualize-slice-authority.md", "inventory and read every safe Slice",
             "in full before selecting a question", "Reuse approved decisions",
             "Read-only recovery needs no new checkpoint or worktree", "missing context is a blocker"],
        )
        boundary = section(read("skills/conceptualize/references/workspace-index.md"), "Boundary")
        assert_has_all(self, boundary, ["Resuming is read-only recovery", "before selecting the next question"])
        self.assertNotIn("Create or resume it only after the Durability Gate", boundary)

    def test_index_to_slice_transition_preserves_existing_commitments(self) -> None:
        index = read("skills/conceptualize/references/workspace-index.md")
        transition = section(index, "Lossless Index-to-Slice Transition")
        assert_has_all(
            self,
            transition,
            ["Inventory every approved implementation-shaping Index commitment", "stable H3 blocks",
             "scope, rationale", "accepted tradeoffs, non-goals, verification expectations",
             "user-decision provenance", "do not invent missing details or narrow commitments",
             "open questions explicitly unresolved", "not as approved", "H3 commitments",
             "Verify every original commitment", "before replacing detailed Index entries",
             "one authoritative home", "not fresh product approval or permission to drop scope"],
        )
        self.assertLess(transition.index("Carry each commitment"), transition.index("replacing detailed Index entries"))
        assert_has_all(self, section(index, "Stop"), ["leave a material commitment only in the Index"])
        do = section(read("skills/conceptualize/SKILL.md"), "Do")
        self.assertIn("apply the lossless transition in", do)

    def test_durability_gate_precedes_new_workspace_resolution_and_writes(self) -> None:
        skill = read("skills/conceptualize/SKILL.md")
        do = section(skill, "Do")
        gate = do.index("Apply the **Durability Gate**")
        first_write = do.index("Only for a needed write")
        self.assertLess(gate, first_write)
        assert_has_all(
            self,
            do[gate:first_write],
            ["no settled understanding", "simple settled work", "durable need", "smallest sufficient",
             "documentation request"],
        )
        assert_has_all(self, do[first_write:], ["artifact-store.md", "workspace-index.md", "worktree"])

    def test_handoff_route_loads_change_routing_at_route_choice(self) -> None:
        skill = read("skills/conceptualize/SKILL.md")
        route_step = re.search(r"At handoff.*?change-routing\.md", section(skill, "Do"), re.S)
        self.assertIsNotNone(route_step)
        assert_has_all(
            self,
            skill,
            ["direct task", "planning", "verification expectations", "never backfill Slices"],
        )

    def test_durable_references_allow_chat_index_or_slice_handoffs(self) -> None:
        skill = read("skills/conceptualize/SKILL.md")
        index = read("skills/conceptualize/references/workspace-index.md")
        template = read("skills/conceptualize/references/slice-template.md")
        authority = read("references/conceptualize-slice-authority.md")
        assert_has_all(self, skill, ["chat-only", "Index-only", "smallest durable record"])
        assert_has_all(self, index, ["Index-only handoff is valid", "no Slice is independently useful"])
        assert_has_all(self, template, ["Durability Gate", "independently useful", "Batch updates"])
        assert_has_all(self, authority, ["Chat-only", "Index-only", "Once any Slice exists", "full safe inventory"])

    def test_documentation_handoff_can_expose_questions_without_readiness_claim(self) -> None:
        skill = read("skills/conceptualize/SKILL.md")
        skill_stops = section(skill, "Stop if")
        assert_has_all(self, section(skill, "Do"), ["continued-discovery", "open questions", "without claiming"])
        assert_has_all(self, skill_stops, ["readiness", "continued-discovery", "open questions", "blocked"])

    def test_canonical_registry_and_authoring_allow_the_same_no_slice_modes(self) -> None:
        for path in (
            "references/slice-first-artifacts.md",
            "skills/implementation-plan/references/artifact-authoring.md",
        ):
            with self.subTest(path=path):
                text = read(path)
                rule = re.search(r"^- `authoritative_slices`.*?(?=^- |^## |\Z)", text, re.M | re.S)
                self.assertIsNotNone(rule)
                assert_has_all(self, rule.group(0), [
                    "full safe existing Slice inventory", "empty only", "chat-only", "Index-only",
                    "no-Slice", "no authoritative Slice file",
                ])
                self.assertNotIn("empty only for Index-only", rule.group(0))

    def test_implementation_plan_accepts_complete_non_slice_inputs(self) -> None:
        inputs = read("skills/implementation-plan/references/conceptualize-inputs.md")
        assert_has_all(
            self,
            inputs,
            [
                "chat-only approved context",
                "Index-only planning is valid",
                "no authoritative Slice",
                "inventory",
                "If any Slice exists",
                "read",
                "each file in full",
                "hidden conversation context",
            ],
        )


if __name__ == "__main__":
    unittest.main()
