"""Static guards for repair effort/progress policy and its cold handoffs.

These check explicit policy placement and retired rules, not agent decisions,
live workflow behavior, or optimal repair depth.
"""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def normalized(text: str) -> str:
    return " ".join(text.replace("**", "").split())


def section(text: str, heading: str) -> str:
    found = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if found is None:
        raise AssertionError(f"missing policy section: {heading}")
    return normalized(found.group(1))


class RepairProgressPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = read("references/bounded-attempts.md")

    def has(self, text: str, *terms: str) -> None:
        text = normalized(text)
        for term in terms:
            self.assertIn(term, text)

    def test_rounds_are_not_tool_or_worker_counts(self) -> None:
        rounds = section(self.policy, "Repair Rounds and Progress")
        self.has(rounds, "candidate correction", "required verification", "independent review/closure",
                 "Individual edits, test runs, worker launches, or reviewer handoffs are not rounds",
                 "Normal edit/test/self-review cycles", "A routine failing test is not a reason")

    def test_progress_needs_observations_not_patch_churn(self) -> None:
        rounds = section(self.policy, "Repair Rounds and Progress")
        self.has(rounds, "observed change", "falsifiable cause", "reproduced failure", "verified behavior",
                 "specific evidence gap", "greener unrelated tests", "not progress",
                 "Never weaken the check", "no evidence-backed next check/correction", "non-convergence")

    def test_three_rounds_trigger_reassessment_not_a_new_allowance(self) -> None:
        rounds = section(self.policy, "Repair Rounds and Progress")
        self.has(rounds, "three unsuccessful complete rounds", "reassess the diagnosis", "verification oracle",
                 "internal reassessment trigger", "not an automatic stop", "planning handoff",
                 "fresh-agent requirement", "entitlement to three more rounds", "unchanged allowance")

    def test_task_allowance_is_round_denominated_with_a_disclosed_default(self) -> None:
        allowance = section(self.policy, "One Shared Round Allowance")
        self.has(allowance, "finite repair-round allowance", "six-round default", "not a separate ask",
                 "not an evidence-backed optimal depth", "stricter explicitly approved attempt/round caps",
                 "whole authorized task", "not each package, finding, cluster, round, or worker",
                 "Count every complete round", "one shared pool, not one allowance per worker",
                 "consumed/remaining rounds", "shared remaining count",
                 "code→plan→review never replenish", "Missing/unrecoverable round history stops",
                 "Only explicit user authorization may extend")

    def test_effort_bound_is_rounds_and_defers_runtime_to_command_timeouts(self) -> None:
        """The allowance counts rounds; per-action runtime stays owned by existing timeout rules."""
        allowance = section(self.policy, "One Shared Round Allowance")
        self.has(allowance, "Check the remaining count before dispatch and before opening another round",
                 "existing command/worker timeout, termination, and cleanup rules",
                 "adds no separate runtime limit")

    def test_allowance_cannot_bypass_checks_or_permission(self) -> None:
        allowance = section(self.policy, "One Shared Round Allowance")
        self.has(allowance, "cannot safely run is blocked", "not skipped or truncated into a pass",
                 "Stop new rounds at exhaustion", "independent review/audit gates never become optional",
                 "never overrides an explicit fix gate")
        routing = section(self.policy, "Route the Evidence, Not the Counter")
        self.has(routing, "Advisories are report-only", "observations contradict", "evidenced plan/Acceptance defect",
                 "not because three rounds failed", "authority changes return to the user-facing owner")

    def test_empirical_bound_is_distinct_and_opens_no_separate_allowance(self) -> None:
        empirical = section(self.policy, "Empirical Questions")
        self.has(empirical, "one invocation", "Three total empirical attempts", "no automatic escalation",
                 "runs inside the round that requested it and opens no separate allowance")
        stops = section(self.policy, "Stops and Evidence")
        self.has(stops, "failed hypotheses", "rounds consumed", "never claim completion",
                 "Never overwrite, edit, or delete", "diagnosis/reproducer handback",
                 "No new receipt/registry", "return the same evidence in chat")

    def test_repair_owners_load_the_same_policy(self) -> None:
        for skill in ("implement", "implementation-plan", "review-plan", "review-code", "diagnose-and-fix"):
            with self.subTest(skill=skill):
                self.has(read(f"skills/{skill}/SKILL.md"), "../../references/bounded-attempts.md")

    def test_cold_repair_workers_receive_policy_and_allowance(self) -> None:
        for path in (
            "skills/implement/references/repair-agent-contract.md",
            "skills/implementation-plan/references/planner-agent-contract.md",
            "skills/review-code/references/fix-implementer-contract.md",
            "skills/diagnose-and-fix/references/fix-implementer-contract.md",
        ):
            with self.subTest(path=path):
                self.has(read(path), "bounded-attempts.md", "rounds", "history")
        for path in (
            "skills/implement/references/package-dispatch.md",
            "skills/diagnose-and-fix/references/orchestration-mechanics.md",
        ):
            with self.subTest(path=path):
                self.has(read(path), "remaining", "rounds", "progress")

    def test_verification_review_and_audit_keep_the_shared_allowance(self) -> None:
        for path in (
            "skills/implement/references/package-verification.md",
            "skills/review-code/SKILL.md",
            "skills/review-code/references/pipeline-report.md",
            "skills/review-plan/SKILL.md",
            "skills/review-plan/references/plan-review-rubrics.md",
            "skills/audit/SKILL.md",
            "skills/audit/references/audit-subagent-contract.md",
        ):
            with self.subTest(path=path):
                self.has(read(path), "rounds")
        self.has(read("skills/audit/references/audit-subagent-contract.md"),
                 "incomplete coverage", "never a partial PASS")

    def test_retired_repair_circuits_are_not_still_authoritative(self) -> None:
        retired = ("three-attempt cap", "three-attempt circuit", "one code reclassification",
                   "one exhaustion fallback", "second exhaustion", "ordinal `2|3`",
                   "at most three total repair attempts", "one such escalation",
                   "30-minute", "elapsed repair time", "repair-time allowance",
                   "shared absolute deadline", "remaining time/deadline", "repair budget")
        paths = [ROOT / "references/package-lifecycle.md", ROOT / "references/bounded-attempts.md",
                 ROOT / "README.md"]
        for skill in ("implement", "implementation-plan", "review-plan", "review-code", "diagnose-and-fix"):
            paths.extend((ROOT / "skills" / skill).rglob("*.md"))
        for path in paths:
            with self.subTest(path=str(path.relative_to(ROOT))):
                text = normalized(path.read_text(encoding="utf-8"))
                for rule in retired:
                    self.assertNotIn(rule, text)


if __name__ == "__main__":
    unittest.main()
