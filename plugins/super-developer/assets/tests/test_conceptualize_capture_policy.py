"""Static prompt-contract guards for Conceptualize capture/routing policy.

These checks do not execute an agent or prove runtime behavior. They guard policy structure:
conversation-first startup, gated/delayed artifact writes, optional Index/Slice
handoffs, route selection at handoff time, and planner handling of chat-only or
Index-only inputs.
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

    def test_durability_gate_precedes_any_artifact_resolution(self) -> None:
        skill = read("skills/conceptualize/SKILL.md")
        do = section(skill, "Do")
        gate = do.index("Durability Gate")
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
