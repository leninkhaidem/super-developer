"""Focused empirical-spike and auto-resolve contract scenario checks.

The generic prompt suite stays content-agnostic. These tests protect the routed-name
migration, producer/caller attempt boundary, plan-defect route, and worktree envelope.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
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


def markdown_section(text: str, heading: str, next_level: str = "##") -> str:
    start = text.index(heading)
    separator = f"\n{next_level} " if next_level.startswith(("#", "-")) else f"\n{next_level}"
    end = text.find(separator, start + len(heading))
    return text[start:] if end < 0 else text[start:end]


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("–", "-")).strip().lower()


def fenced_commands(text: str) -> str:
    return "\n".join(re.findall(r"```bash\n(.*?)```", text, re.DOTALL))


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
        self.assertRegex(self.skill, r"(?is)Never.{0,100}invoke `implementation-plan`")
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
        def load(*parts: str) -> str:
            return (SKILLS_ROOT.joinpath(*parts)).read_text(encoding="utf-8")

        cls.empirical = load(NEW_SKILL, "SKILL.md")
        cls.implement = load("implement", "SKILL.md")
        cls.execution = load("implement", "references", "execution-contract.md")
        cls.dispatch = load("implement", "references", "package-dispatch.md")
        cls.integration = load("implement", "references", "package-integration-gates.md")
        cls.repair = load("implement", "references", "repair-agent-contract.md")
        cls.plan = load("implementation-plan", "SKILL.md")
        cls.planner = load("implementation-plan", "references", "planner-agent-contract.md")
        cls.validation = load("implementation-plan", "references", "validation-checklist.md")
        cls.review = load("review-plan", "SKILL.md")
        cls.resolution = load("review-plan", "references", "plan-review-resolution.md")
        cls.worktree = load("worktree", "SKILL.md")
        cls.feature_worktrees = load("worktree", "references", "feature-package-workflow.md")
        cls.probe_worktrees = load("worktree", "references", "bugfix-hotfix-workflow.md")
        cls.probe_cleanup = load("worktree", "references", "probe-cleanup.md")
        cls.cleanup = load("worktree", "references", "cleanup-safety.md")
        cls.public_docs = (PLUGIN_ROOT / "README.md").read_text(encoding="utf-8")

    def test_logical_question_uses_one_run_per_invocation_and_three_total_attempts(self) -> None:
        callers = (self.implement, self.plan, self.review, self.execution)
        for caller in callers:
            contract = normalized(caller)
            self.assertIn("logical-question", contract)
            self.assertIn("attempt 1", contract)
            self.assertRegex(contract, r"attempts? 2-3")
            self.assertIn("fresh invocation", contract)
            self.assertIn("corrected packet", contract)
            self.assertIn("changed method/signal", contract)
            self.assertIn("unchanged", contract)
            self.assertRegex(contract, r"three total|at most three")

        producer = normalized(self.empirical)
        self.assertIn("one material question per run", producer)
        self.assertLess(producer.index("attempt 1"), producer.index("attempts 2-3"))
        self.assertIn("never hide multiple attempts in one run", producer)

        workflow = normalized("\n".join(callers + (self.public_docs,)))
        self.assertNotRegex(workflow, r"one fresh `empirical-spike` per (?:distinct )?question")
        self.assertNotRegex(workflow, r"one invocation per (?:logical )?question")

    def test_non_empirical_plan_defect_routes_through_planning_then_focused_review(self) -> None:
        route = normalized(markdown_section(self.implement, "- **Plan-defect route.**", "-"))
        for stage in ("readiness", "package-agent", "verifier", "integration", "final review", "audit"):
            self.assertIn(stage, route)
        planning = route.index("`implementation-plan` `implementation-continuation`")
        focused_review = route.index("`review-plan` `implementation-continuation-focused`")
        restored = route.index("restore readiness")
        self.assertLess(planning, focused_review)
        self.assertLess(focused_review, restored)
        self.assertIn("explicit `none`", route)
        self.assertIn("never send it to a code repair worker", route)

        planner_packet = normalized(markdown_section(self.planner, "## Required Packet"))
        self.assertIn("non-empirical plan defect", planner_packet)
        self.assertIn("explicit `none`", planner_packet)

        for downstream in (self.dispatch, self.integration):
            routing = normalized(downstream)
            self.assertIn("`implementation-plan` `implementation-continuation`", routing)
            self.assertIn("focused", routing)
            self.assertRegex(routing, r"explicit (?:report set )?`none`|reports or explicit `none`")
            self.assertRegex(
                routing,
                r"never .*code repair|only code defects trigger ordinary repair|dispatch only a blocking code defect",
            )
        repair_worker = normalized(self.repair)
        self.assertIn("make no repair for it", repair_worker)
        self.assertIn("never mix it into a code-repair cluster", repair_worker)

    def test_dirty_probe_cleanup_uses_bound_manifests_and_exact_local_restoration(self) -> None:
        envelope = normalized(markdown_section(self.execution, "Worktree authority envelope:", "Fixed worktrees:"))
        for required in (
            "clean head/index/worktree",
            "index checksum",
            "exact nul tracked/deleted/untracked/ignored/symlink/process/data",
            "no stage/index write",
            "remote_action=none",
            "normal remove/cas",
        ):
            self.assertIn(required, envelope)

        producer = normalized(self.empirical)
        self.assertIn("never stage or write the index", producer)
        self.assertIn("nul-safely classify every delta", producer)
        self.assertIn("restoring exact owned tracked paths from the bound base sha", producer)
        self.assertLess(
            producer.index("remove exact owned untracked/ignored leaves"),
            producer.index("restoring exact owned tracked paths"),
        )

        creation = normalized(markdown_section(self.probe_worktrees, "Auto-resolve probe", "Active-feature"))
        for required in ("base_ref", "base_sha", "index_sha256", "initial_status_nul", "initial_ignored_nul"):
            self.assertIn(required, creation)
        self.assertIn("git worktree add --no-track -b", creation)
        self.assertLess(creation.index("git worktree add --no-track -b"), creation.index("for-each-ref"))
        self.assertLess(creation.index("for-each-ref"), creation.index("index_sha256"))
        self.assertLess(creation.index("index_sha256"), creation.index("before any probe write"))

        cleanup = normalized(self.probe_cleanup)
        for required in (
            "obs_tracked",
            "obs_deleted",
            "obs_untracked",
            "obs_ignored",
            "base/current symlink",
            "process identities",
            "external data",
            "--literal-pathspecs",
            "--source=\"$base_sha\" --worktree",
            "rm -- \"$wt/$path\"",
            "rmdir --",
            "regenerated nul index digest unchanged",
            "head`/direct ref = base sha",
            "git worktree remove \"$wt\"",
            "update-ref --no-deref -d \"$ref\" \"$base_sha\"",
        ):
            self.assertIn(required, cleanup)
        self.assertLess(cleanup.index("classify before mutation"), cleanup.index("restore exact owned state"))
        leaf_removal = cleanup.index("for every nul record in `obs_untracked` and `obs_ignored`")
        dir_removal = cleanup.index("after all leaves are gone")
        tracked_restore = cleanup.index("only after owned leaves/directories are removed")
        self.assertLess(leaf_removal, dir_removal)
        self.assertLess(dir_removal, tracked_restore)
        self.assertLess(tracked_restore, cleanup.index("git worktree remove \"$wt\""))
        self.assertIn("immediately revalidate", cleanup)
        self.assertIn("any extra", cleanup)
        self.assertIn("unowned, or uncertain record stops", cleanup)

        boundary = markdown_section(self.cleanup, "## Envelope Probe Boundary", "## Package Cleanup")
        commands = normalized(fenced_commands(self.probe_cleanup) + fenced_commands(boundary))
        self.assertNotRegex(commands, r"\bgit\s+(?:ls-remote|fetch|push|clean|reset)\b")
        self.assertNotRegex(commands, r"\bgit\s+worktree\s+remove\s+--force\b|\brm\s+-r")
        for required in ("for-each-ref --format='%(upstream)'", "branch.$branch.remote", "remote_action"):
            self.assertIn(required, cleanup)
        local_boundary = normalized(boundary)
        self.assertIn("perform no network/credential check", local_boundary)
        self.assertIn("coincidental remote ref is out of scope and untouched", local_boundary)

    def test_continuation_package_creation_uses_reviewed_base_and_prerequisite_ancestry(self) -> None:
        for prompt in (self.plan, self.planner, self.validation, self.review, self.dispatch, self.execution):
            contract = normalized(prompt)
            self.assertIn("approved original base", contract)
            for field in ("base_kind", "base_ref", "reviewed_base_sha"):
                self.assertIn(field, contract)
            self.assertRegex(contract, r"prerequisite.{0,100}(?:ref/)?sha")
            self.assertRegex(contract, r"ancestor|ancestry")

        package = normalized(markdown_section(self.feature_worktrees, "### 2. Create package worktrees", "### 3."))
        for required in ("base_kind", "base_ref", "reviewed_base_sha", "prereq_refs", "prereq_shas"):
            self.assertIn(required, package)
        self.assertIn("test \"$base_ref\" = \"$original_base_ref\"", package)
        self.assertIn("test \"$base_ref\" = \"feature/<feature>\"", package)
        self.assertIn("merge-base --is-ancestor", package)
        add = package.index("git worktree add --no-track -b")
        base_checks = [m.start() for m in re.finditer(r'test "\$\(git rev-parse "\$base_ref"\)" = "\$reviewed_base_sha"', package)]
        self.assertEqual(len(base_checks), 2)
        self.assertLess(base_checks[0], add)
        self.assertGreater(base_checks[1], add)
        self.assertLess(package.index("merge-base --is-ancestor"), add)
        self.assertIn("integration\" rev-parse head)\" = \"$reviewed_base_sha", package)
        self.assertNotIn("base_sha=\"$(git rev-parse", package)
        self.assertLess(add, package.index("for-each-ref"))
        self.assertIn("branch.$ref.remote", package)
        self.assertIn("no arbitrary allowed-base selection is valid", package)

    def test_continuation_packages_are_retained_until_safe_final_cleanup(self) -> None:
        for prompt in (self.execution, self.worktree, self.feature_worktrees):
            contract = normalized(prompt)
            self.assertRegex(contract, r"active.{0,40}retired|active/retired")
            self.assertRegex(contract, r"remain|retain")
            self.assertRegex(contract, r"final (?:whole-feature )?(?:gates|cleanup)")
        workflow = normalized(self.feature_worktrees)
        self.assertIn("retirement alone never authorizes cleanup", workflow)
        self.assertNotIn("cleanup early", workflow)

        final_cleanup = normalized(markdown_section(self.cleanup, "## Package Cleanup", "## Normal Feature"))
        self.assertIn("no active or retired package cleanup", final_cleanup)
        self.assertIn("merge-base --is-ancestor \"$tip\" \"$final\"", final_cleanup)
        self.assertIn("$kind\" = continuation", final_cleanup)
        self.assertIn("$tip\" = \"$base", final_cleanup)
        self.assertIn("preserve: unique unmerged package commits", final_cleanup)
        self.assertLess(final_cleanup.index("merge-base --is-ancestor"), final_cleanup.index("git worktree remove"))

    def test_continuation_has_no_generic_design_decision_user_prompt(self) -> None:
        decision = normalized(markdown_section(self.resolution, "### design decision", "###"))
        self.assertIn("in initial mode, ask the user", decision)
        self.assertIn("in continuation-focused mode", decision)
        self.assertIn("return to `implement` only if", decision)
        self.assertNotIn("ask the user unless", decision)

        for sentence in re.split(r"(?<=[.!?])\s+", normalized(self.resolution)):
            if "ask the user" in sentence:
                self.assertIn("initial mode", sentence)
        continuation = normalized(self.review)
        self.assertIn("decision-prompts.md` only for structured decisions in initial mode", continuation)

    def test_protected_stops_survive_autonomous_routing_and_cleanup(self) -> None:
        implement_stops = normalized(markdown_section(self.implement, "## Stop if"))
        for protected in (
            "new semantic authority",
            "manual exception",
            "missing credentials or external facts",
            "protected or out-of-contract action",
            "target delivery boundary",
            "non-convergence",
        ):
            self.assertIn(protected, implement_stops)

        execution_stops = normalized(markdown_section(self.execution, "Stop conditions:", "Choices:"))
        for protected in (
            "risk acceptance",
            "missing credentials/external facts",
            "destructive/external/service/dependency action",
            "target delivery",
            "force/remote-delete/tag/release",
            "uncertain",
        ):
            self.assertIn(protected, execution_stops)

        worktree_stops = normalized(markdown_section(self.worktree, "## Stop if"))
        for protected in ("root checkout", "another namespace", "remote", "target merge", "forced deletion"):
            self.assertIn(protected, worktree_stops)

    def test_initial_gates_remain_distinct_from_autonomous_continuation(self) -> None:
        self.assertRegex(normalized(self.plan), r"initial.{0,120}retain every existing.{0,100}gate")
        review_contract = normalized(self.review)
        self.assertIn("in `initial` mode, one blocking plan-approval gate", review_contract)
        self.assertIn("continuation-focused mode does not reopen this gate", review_contract)
        self.assertIn("present no gate", review_contract)

    def test_planner_worker_remains_evidence_consumer_not_spike_orchestrator(self) -> None:
        self.assertIn("planner worker, not the orchestrator", self.planner)
        self.assertIn("BLOCKED: empirical_evidence_needed", self.planner)
        self.assertIn("Do not invoke `empirical-spike`", self.planner)
        self.assertIn("confirm no artifacts were written", self.planner)
        self.assertRegex(self.plan, r"(?is)never recursively invoke\s+`implementation-plan`")


class GitEnvelopeSimulationTests(unittest.TestCase):
    def init_repo(self, root: Path) -> None:
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "Contract Test"], check=True)
        (root / "seed").write_text("seed\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "seed"], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", "seed"], check=True)

    def test_removal_precedes_restore_for_tracked_file_to_directory_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            self.init_repo(repo)
            slot = repo / "slot"
            slot.write_text("base\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "slot"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "tracked slot"], check=True)
            paths = Path(temp) / "paths.nul"
            paths.write_bytes(b"slot\0")

            def replace_with_owned_leaf() -> Path:
                slot.unlink()
                slot.mkdir()
                leaf = slot / "owned.tmp"
                leaf.write_text("owned\n", encoding="utf-8")
                return leaf

            leaf = replace_with_owned_leaf()
            restore = [
                "git", "--literal-pathspecs", "-C", str(repo), "restore", "--source=HEAD", "--worktree",
                f"--pathspec-from-file={paths}", "--pathspec-file-nul",
            ]
            subprocess.run(restore, check=True)
            self.assertFalse(leaf.exists(), "Git restore demonstrates the owned-leaf deletion hazard")

            leaf = replace_with_owned_leaf()
            leaf.unlink()
            slot.rmdir()
            subprocess.run(restore, check=True)
            self.assertEqual(slot.read_text(encoding="utf-8"), "base\n")

    def test_no_track_defeats_auto_setup_merge_always(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            worktree = Path(temp) / "probe"
            self.init_repo(repo)
            subprocess.run(["git", "-C", str(repo), "branch", "base"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "branch.autoSetupMerge", "always"], check=True)
            subprocess.run(
                ["git", "-C", str(repo), "worktree", "add", "-q", "--no-track", "-b", "probe/f/q/a1", str(worktree), "base"],
                check=True,
            )
            upstream = subprocess.check_output(
                ["git", "-C", str(repo), "for-each-ref", "--format=%(upstream)", "refs/heads/probe/f/q/a1"], text=True
            ).strip()
            self.assertEqual(upstream, "")
            for key in ("remote", "merge", "pushRemote"):
                result = subprocess.run(
                    ["git", "-C", str(repo), "config", "--get", f"branch.probe/f/q/a1.{key}"],
                    check=False,
                    stdout=subprocess.PIPE,
                    text=True,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")

    def test_moved_reviewed_base_is_rejected_before_worktree_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            worktree = Path(temp) / "wp-WP2"
            self.init_repo(repo)
            subprocess.run(["git", "-C", str(repo), "branch", "feature/demo"], check=True)
            reviewed = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "feature/demo"], text=True).strip()
            (repo / "seed").write_text("moved\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "commit", "-qam", "move base"], check=True)
            subprocess.run(["git", "-C", str(repo), "branch", "-f", "feature/demo", "HEAD"], check=True)
            script = 'test "$(git rev-parse feature/demo)" = "$REVIEWED_BASE_SHA" && git worktree add --no-track -b wp/demo/WP2 "$WT" "$REVIEWED_BASE_SHA"'
            result = subprocess.run(
                ["bash", "-c", script], cwd=repo, check=False,
                env={**os.environ, "REVIEWED_BASE_SHA": reviewed, "WT": str(worktree)},
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(worktree.exists())
            branch = subprocess.run(
                ["git", "-C", str(repo), "show-ref", "--verify", "--quiet", "refs/heads/wp/demo/WP2"], check=False
            )
            self.assertNotEqual(branch.returncode, 0)


if __name__ == "__main__":
    unittest.main()
