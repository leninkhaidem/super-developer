"""Focused migration, routing, and ownership checks for empirical-spike.

The generic prompt suite stays content-agnostic. These tests protect the breaking
routed-name migration and the empirical producer/orchestrator boundary.
"""

from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PLUGIN_ROOT.parents[1]
SKILLS_ROOT = PLUGIN_ROOT / "skills"
DEPRECATED_SKILL = "spike" + "-to-plan"
NEW_SKILL = "empirical-spike"
AUDIT_SKILL = SKILLS_ROOT / "skill-authoring" / "scripts" / "audit-skill.py"
DEPRECATED_NAME_ALLOWLIST = {REPO_ROOT / "CHANGELOG.md"}


def relevant_markdown_json() -> list[Path]:
    return sorted(
        path
        for path in REPO_ROOT.rglob("*")
        if path.is_file()
        and path.suffix in {".md", ".json"}
        and ".git" not in path.relative_to(REPO_ROOT).parts
    )


def folded_description(skill_text: str) -> str:
    frontmatter = skill_text.split("---", 2)[1]
    match = re.search(r"(?m)^description:\s*>[-+]?\s*\n((?:  .*\n?)+)", frontmatter)
    if not match:
        raise AssertionError("expected folded description")
    return " ".join(line.strip() for line in match.group(1).splitlines())


class EmpiricalSpikeMigrationTests(unittest.TestCase):
    def test_catalog_keeps_15_skills_and_rename_is_complete(self) -> None:
        skill_dirs = sorted(path.name for path in SKILLS_ROOT.iterdir() if path.is_dir())
        self.assertEqual(len(skill_dirs), 15)
        self.assertIn(NEW_SKILL, skill_dirs)
        self.assertNotIn(DEPRECATED_SKILL, skill_dirs)

        skill_text = (SKILLS_ROOT / NEW_SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertRegex(skill_text, rf"(?m)^name:\s*{re.escape(NEW_SKILL)}$")
        self.assertIn("# Empirical Spike", skill_text)

    def test_deprecated_name_is_absent_from_live_markdown_and_json(self) -> None:
        offenders = {
            path
            for path in relevant_markdown_json()
            if DEPRECATED_SKILL in path.read_text(encoding="utf-8")
        }
        self.assertEqual(offenders, DEPRECATED_NAME_ALLOWLIST)

    def test_unreleased_changelog_records_breaking_rename(self) -> None:
        changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        unreleased = changelog.split("## [Unreleased]", 1)[1].split("\n## [", 1)[0]
        self.assertIn("Breaking", unreleased)
        self.assertIn(DEPRECATED_SKILL, unreleased)
        self.assertIn(NEW_SKILL, unreleased)

    def test_renamed_skill_passes_frontmatter_link_and_budget_audit(self) -> None:
        result = subprocess.run(
            [sys.executable, str(AUDIT_SKILL), str(SKILLS_ROOT / NEW_SKILL)],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("RESULT: PASS", result.stdout)


class EmpiricalSpikeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = (SKILLS_ROOT / NEW_SKILL / "SKILL.md").read_text(encoding="utf-8")

    def test_frontmatter_routes_conditional_pipeline_calls_without_performing_the_stage(self) -> None:
        description = folded_description(self.skill)
        routing, near_miss = description.split("Do not use", 1)

        self.assertLessEqual(len(description), 280)
        for caller_stage in ("planning", "plan review", "implementation"):
            self.assertIn(caller_stage, routing.lower())
        self.assertIn("to perform", near_miss.lower())
        for performed_work in ("implementation", "code/plan review", "routine testing"):
            self.assertIn(performed_work, near_miss.lower())

    def test_report_statuses_and_standalone_boundary_are_explicit(self) -> None:
        for status in ("resolved-static", "supported", "rejected", "blocked", "inconclusive"):
            self.assertIn(f"`{status}`", self.skill)
        self.assertIn("Never invoke `implementation-plan`", self.skill)
        self.assertIn("planned-feature artifact", self.skill)
        self.assertIn("Do not include a next-skill", self.skill)
        self.assertIn("non-authoritative decision", self.skill)
        self.assertRegex(self.skill, r"(?i)one (?:material|falsifiable) question per (?:run|invocation)")

    def test_probe_review_is_bounded_to_method_and_execution_boundary(self) -> None:
        for required in (
            "methodological/correctness check",
            "credentials/secrets",
            "sensitive/production/shared data",
            "network",
            "permissions",
            "destructive or externally visible effects",
            "isolation",
            "termination",
            "cleanup",
            "dedicated security reviewer",
            "`review-code`",
            "`audit`",
        ):
            self.assertIn(required, self.skill)
        self.assertNotIn("`security-review`", self.skill)


class OrchestratorOwnershipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = (SKILLS_ROOT / "implementation-plan" / "SKILL.md").read_text(encoding="utf-8")
        cls.review = (SKILLS_ROOT / "review-plan" / "SKILL.md").read_text(encoding="utf-8")
        cls.implement = (SKILLS_ROOT / "implement" / "SKILL.md").read_text(encoding="utf-8")
        cls.planner = (
            SKILLS_ROOT / "implementation-plan" / "references" / "planner-agent-contract.md"
        ).read_text(encoding="utf-8")
        cls.validation = (
            SKILLS_ROOT / "implementation-plan" / "references" / "validation-checklist.md"
        ).read_text(encoding="utf-8")
        cls.resolution = (
            SKILLS_ROOT / "review-plan" / "references" / "plan-review-resolution.md"
        ).read_text(encoding="utf-8")
        cls.public_docs = (PLUGIN_ROOT / "README.md").read_text(encoding="utf-8")

    def test_orchestrators_support_bounded_multi_question_evidence_sets(self) -> None:
        for prompt in (self.plan, self.review, self.implement):
            self.assertRegex(prompt, r"(?is)bounded set of distinct.{0,120}questions")
            self.assertRegex(prompt, r"(?is)one fresh `empirical-spike` per.{0,80}question")
            self.assertRegex(prompt, r"(?is)parallel.{0,180}(?:sequential|sequence).{0,120}evidence creates")
            self.assertRegex(prompt, r"(?is)repeated\s+unchanged.{0,180}(?:emerging|unbounded)")

    def test_global_resume_cap_ceremony_does_not_return(self) -> None:
        workflow = "\n".join(
            (
                self.plan,
                self.review,
                self.implement,
                self.planner,
                self.validation,
                self.resolution,
                self.public_docs,
            )
        )
        forbidden = (
            r"resume (?:is )?spent",
            r"at most once",
            r"single-(?:resume|replan|plan-routing)",
            r"one empirical resume",
            r"single bounded resume",
            r"second empirical question",
            r"chain spikes",
            r"`implementation-plan` exactly once",
        )
        for pattern in forbidden:
            self.assertNotRegex(workflow, rf"(?i){pattern}")

    def test_planning_continuation_is_caller_owned_for_report_set_not_spike_cap(self) -> None:
        for prompt in (self.review, self.implement):
            self.assertRegex(prompt, r"(?is)one\s+caller-owned.{0,80}`implementation-plan` continuation")
            self.assertRegex(prompt, r"(?is)continuation.{0,160}(?:does not|not a) cap.{0,80}spike")
        self.assertIn("never recursively invoke\n  `implementation-plan`", self.plan)

    def test_planner_worker_uses_reports_without_counter_and_returns_exact_blocker(self) -> None:
        self.assertIn("planner worker, not the orchestrator", self.planner)
        self.assertRegex(self.planner, r"accepted empirical reports.*(?:\n.*){0,2}explicit `none`")
        self.assertNotRegex(self.planner, r"(?i)resume.{0,40}(?:spent|counter)")
        self.assertIn("BLOCKED: empirical_evidence_needed", self.planner)
        self.assertIn("Do not invoke `empirical-spike`", self.planner)
        self.assertIn("confirm no artifacts were written", self.planner)
        self.assertIn("new distinct bounded blocker", self.plan)
        self.assertIn("redispatch", self.plan)


if __name__ == "__main__":
    unittest.main()
