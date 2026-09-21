"""Static guards for repair progress policy and its cold handoffs.

These check explicit policy placement and retired rules, not agent decisions,
live workflow behavior, resource enforcement, or improved repair performance.
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
                 "Never weaken the check", "evidence-backed next check/correction", "non-convergence",
                 "A plausible strategy alone is not evidence", "concrete uncertainty", "distinguishing signal")

    def test_reassessment_follows_evidence_including_inner_loops(self) -> None:
        rounds = section(self.policy, "Repair Rounds and Progress")
        self.has(rounds, "observations contradict", "progress stalls", "oscillating regressions",
                 "inside a long round", "not a new stage, per-command form",
                 "Several independently verified corrections", "not, by their number alone")

    def test_no_default_quota_or_unconditional_counter_bookkeeping(self) -> None:
        limits = section(self.policy, "Applicable Limits")
        self.has(limits, "no default repair-round quota", "count-triggered reassessment",
                 "when no applicable count limit exists", "existing authorizations and handoffs",
                 "not a new budget framework", "progress score", "ledger")

    def test_binding_limits_keep_their_scope_and_continuity(self) -> None:
        limits = section(self.policy, "Applicable Limits")
        self.has(limits, "explicit user limits", "already-approved caps", "actual host-enforced limits",
                 "within their stated scope", "task-wide limits across parallel workers",
                 "resumed sessions", "cannot reset", "Do not give each worker a fresh copy",
                 "remaining capacity cannot be established", "Only explicit user authorization may extend",
                 "count a started round once", "failed or interrupted work", "own counting semantics",
                 "not completion of already-authorized checks")

    def test_runtime_and_completion_claims_stay_honest(self) -> None:
        limits = section(self.policy, "Applicable Limits")
        self.has(limits, "command/worker timeout, termination, and cleanup rules",
                 "do not enforce an aggregate runtime, cost, or turn ceiling",
                 "per-command timeouts do not bound the whole task", "best-effort",
                 "cannot safely run is blocked", "not skipped or truncated into a pass",
                 "independent review/audit gates never become optional", "never overrides an explicit fix gate")
        routing = section(self.policy, "Route the Evidence, Not the Counter")
        self.has(routing, "Advisories are report-only", "evidenced plan/Acceptance defect",
                 "authority changes return to the user-facing owner", "Recover missing repair context",
                 "if safe continuation cannot be established", "rather than invent history")

    def test_empirical_cap_and_existing_stop_handoff_are_preserved(self) -> None:
        empirical = section(self.policy, "Empirical Questions")
        self.has(empirical, "one invocation", "Three total empirical attempts", "no automatic escalation",
                 "inherits applicable task limits as well as this separate empirical cap")
        stops = section(self.policy, "Stops and Evidence")
        self.has(stops, "failed hypotheses", "applicable limit state", "never claim completion",
                 "Never overwrite, edit, or delete", "diagnosis/reproducer handback",
                 "No new receipt/registry", "return the same evidence in chat")

    def test_repair_owners_load_the_same_policy(self) -> None:
        for skill in ("implement", "implementation-plan", "review-plan", "review-code", "diagnose-and-fix"):
            with self.subTest(skill=skill):
                self.has(read(f"skills/{skill}/SKILL.md"), "../../references/bounded-attempts.md")

    def test_cold_repair_handoffs_keep_policy_and_evidence_history(self) -> None:
        for path in (
            "skills/implement/references/repair-agent-contract.md",
            "skills/implementation-plan/references/planner-agent-contract.md",
            "skills/review-code/references/fix-implementer-contract.md",
            "skills/diagnose-and-fix/references/fix-implementer-contract.md",
        ):
            with self.subTest(path=path):
                self.has(read(path), "bounded-attempts.md", "history")
        for path in (
            "skills/implement/references/package-dispatch.md",
            "skills/diagnose-and-fix/references/orchestration-mechanics.md",
        ):
            with self.subTest(path=path):
                self.has(read(path), "history", "progress")

    def test_verification_review_and_audit_keep_applicable_limits(self) -> None:
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
                self.has(read(path), "limits")
        self.has(read("skills/audit/references/audit-subagent-contract.md"),
                 "incomplete coverage", "never a partial PASS")

    def test_retired_repair_circuits_are_not_still_authoritative(self) -> None:
        retired = ("three-attempt cap", "three-attempt circuit", "one code reclassification",
                   "one exhaustion fallback", "second exhaustion", "ordinal `2|3`",
                   "at most three total repair attempts", "one such escalation",
                   "30-minute", "elapsed repair time", "repair-time allowance",
                   "shared absolute deadline", "remaining time/deadline", "repair budget",
                   "six-round default", "three unsuccessful complete rounds", "One Shared Round Allowance")
        paths = [ROOT / "references/package-lifecycle.md", ROOT / "references/bounded-attempts.md",
                 ROOT / "README.md"]
        for skill in ("implement", "implementation-plan", "review-plan", "review-code", "diagnose-and-fix", "audit"):
            paths.extend((ROOT / "skills" / skill).rglob("*.md"))
        for path in paths:
            with self.subTest(path=str(path.relative_to(ROOT))):
                text = normalized(path.read_text(encoding="utf-8"))
                for rule in retired:
                    self.assertNotIn(rule, text)


if __name__ == "__main__":
    unittest.main()
