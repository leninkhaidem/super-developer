from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
AUDIT_SKILL = PLUGIN_ROOT / "skills" / "skill-authoring" / "scripts" / "audit-skill.py"


class AuditSkillFixture:
    def __init__(self, name: str = "fixture-skill") -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.skill_dir = self.root / "skills" / name
        self.skill_dir.mkdir(parents=True)
        self.skill_file = self.skill_dir / "SKILL.md"
        self.write_skill()

    def cleanup(self) -> None:
        self.tmp.cleanup()

    def default_frontmatter(self) -> str:
        return textwrap.dedent(
            f"""\
            ---
            name: {self.skill_dir.name}
            description: >
              Audits a focused fixture without relying on external packages.
              Use it only for deterministic validator behavior.
            ---
            """
        )

    def write_skill(self, *, frontmatter: str | None = None, body: str = "# Fixture skill\n") -> None:
        self.skill_file.write_text((frontmatter or self.default_frontmatter()) + body, encoding="utf-8")

    def write_reference(self, name: str, text: str = "# Reference\n") -> Path:
        path = self.skill_dir / "references" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def write_script(self, name: str, text: str = "#!/bin/sh\nexit 0\n") -> Path:
        path = self.skill_dir / "scripts" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def run(self, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(AUDIT_SKILL), *extra, str(self.skill_dir)],
            cwd=self.root,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )


class AuditSkillValidatorTests(unittest.TestCase):
    def fixture(self, name: str = "fixture-skill") -> AuditSkillFixture:
        fixture = AuditSkillFixture(name)
        self.addCleanup(fixture.cleanup)
        return fixture

    def test_default_mode_enforces_skill_and_reference_hard_line_caps(self) -> None:
        skill_fixture = self.fixture("skill-cap")
        skill_fixture.write_skill(body="# Fixture\n" + "\n".join(f"line {index}" for index in range(210)) + "\n")

        result = skill_fixture.run()

        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("SKILL.md exceeds hard cap of 200 lines", result.stdout)
        self.assertIn("HARD LINE CAP ERRORS", result.stdout)

        ref_fixture = self.fixture("reference-cap")
        ref_fixture.write_reference("large.md", "\n".join(f"reference line {index}" for index in range(205)) + "\n")
        ref_fixture.write_skill(body="# Fixture\n\nLoad `references/large.md` when needed.\n")

        result = ref_fixture.run()

        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("reference exceeds hard cap of 200 lines", result.stdout)

    def test_word_budget_warns_and_cannot_be_evaded_by_denser_lines(self) -> None:
        """The word budget warns, and is line-wrapping invariant.

        This is the property a line cap lacks. Identical word content is audited twice, once as
        many short lines and once packed into few long lines; both must report the same word
        budget warning, and neither may fail the audit.
        """
        words = [f"word{index}" for index in range(1900)]

        sparse = self.fixture("word-budget-sparse")
        sparse.write_skill(body="# Fixture\n" + "\n".join(" ".join(words[i : i + 10]) for i in range(0, len(words), 10)) + "\n")
        sparse_result = sparse.run()

        packed = self.fixture("word-budget-packed")
        packed.write_skill(body="# Fixture\n" + "\n".join(" ".join(words[i : i + 200]) for i in range(0, len(words), 200)) + "\n")
        packed_result = packed.run()

        for label, result in (("sparse", sparse_result), ("packed", packed_result)):
            self.assertIn("exceeds word budget of 1800", result.stdout, label)
            self.assertIn("remove obligations rather than compressing prose", result.stdout, label)
            self.assertNotIn("HARD LINE CAP ERRORS", result.stdout)

        # Warning only: an over-budget prompt must still pass the audit.
        self.assertEqual(packed_result.returncode, 0, packed_result.stdout)

    def test_readable_reflowing_below_the_word_budget_passes(self) -> None:
        """De-densifying prose (same words, more/shorter lines) must never fail the audit."""
        words = [f"word{index}" for index in range(700)]
        fixture = self.fixture("reflow-ok")
        fixture.write_skill(body="# Fixture\n" + "\n".join(" ".join(words[i : i + 8]) for i in range(0, len(words), 8)) + "\n")

        result = fixture.run()

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("HARD LINE CAP ERRORS", result.stdout)
        self.assertNotIn("exceeds word budget", result.stdout)

    def test_strict_remains_a_no_op_and_word_targets_remain_warnings(self) -> None:
        fixture = self.fixture()

        default_result = fixture.run()
        strict_result = fixture.run("--strict")
        help_result = subprocess.run(
            [sys.executable, str(AUDIT_SKILL), "--help"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        self.assertEqual(default_result.returncode, 0, default_result.stdout)
        self.assertEqual(strict_result.returncode, 0, strict_result.stdout)
        self.assertIn("words outside target", default_result.stdout)
        self.assertIn("words outside target", strict_result.stdout)
        self.assertIn("backward-compatible no-op", help_result.stdout)
        self.assertIn("word targets only warn", help_result.stdout)

    def test_valid_folded_block_frontmatter_and_relative_shared_path_pass(self) -> None:
        fixture = self.fixture("valid-block")
        shared = fixture.root / "references" / "shared.md"
        shared.parent.mkdir()
        shared.write_text("# Shared contract\n", encoding="utf-8")
        fixture.write_skill(
            frontmatter=textwrap.dedent(
                """\
                ---
                name: valid-block
                description: >-
                  Validates folded frontmatter and a relative shared contract.
                  Keeps the resulting description concise and useful.
                  Remains valid when split across extra content lines.
                  Uses the extra lines as advisory structure only.
                ---
                """
            ),
            body="# Valid block\n\nLoad `../../references/shared.md` when shared behavior matters.\n",
        )

        result = fixture.run()

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("frontmatter description uses 4 content lines", result.stdout)
        self.assertIn("RESULT: PASS", result.stdout)

    def test_invalid_required_frontmatter_values_fail(self) -> None:
        cases = {
            "empty-name": ("empty-name", "name: ''\ndescription: useful description"),
            "empty-description": ("empty-description", "name: empty-description\ndescription: \"\""),
            "non-string-description": ("non-string-description", "name: non-string-description\ndescription: []"),
            "duplicate": ("duplicate", "name: duplicate\nname: duplicate\ndescription: useful description"),
            "overlong": ("overlong", "name: overlong\ndescription: >\n  " + "x" * 281),
            "mismatched": ("actual-directory", "name: other-directory\ndescription: useful description"),
            "not-kebab": ("not-kebab", "name: Not_Kebab\ndescription: useful description"),
        }
        expected = {
            "empty-name": "name must be a non-empty string",
            "empty-description": "description must be a non-empty string",
            "non-string-description": "description value must be a string",
            "duplicate": "duplicate key: name",
            "overlong": "folded description exceeds 280 characters",
            "mismatched": "does not match skill directory `actual-directory`",
            "not-kebab": "name must be kebab-case",
        }

        for case, (directory, fields) in cases.items():
            with self.subTest(case=case):
                fixture = self.fixture(directory)
                fixture.write_skill(frontmatter=f"---\n{fields}\n---\n")
                result = fixture.run()
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn(expected[case], result.stdout)

    def test_broken_markdown_backtick_and_relative_shared_paths_fail(self) -> None:
        fixture = self.fixture("broken-paths")
        fixture.write_skill(
            body=textwrap.dedent(
                """\
                # Broken paths

                Load [the missing reference](references/missing-link.md).
                Run `scripts/missing-tool.py` for validation.
                Load `../../references/missing-shared.md` for shared behavior.

                Ignore [a URL](https://example.invalid/reference.md), [an anchor](#section),
                `references/<topic>.md`, and [a placeholder](references/<topic>.md).
                """
            )
        )

        result = fixture.run()

        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("missing local Markdown link `references/missing-link.md`", result.stdout)
        self.assertIn("missing local backtick `scripts/missing-tool.py`", result.stdout)
        self.assertIn("missing local backtick `../../references/missing-shared.md`", result.stdout)
        self.assertIn("LOCAL LINKS: resolved=0 missing=3", result.stdout)
        self.assertNotIn("example.invalid", result.stdout)
        self.assertNotIn("references/<topic>.md`", result.stdout)

    def test_reference_loading_markdown_is_a_failing_hidden_second_hop(self) -> None:
        fixture = self.fixture("hidden-hop")
        fixture.write_reference(
            "first.md",
            "# First\n\nContinue with [second](second.md).\nRun `scripts/helper.py` if needed.\n",
        )
        fixture.write_reference("second.md")
        fixture.write_script("helper.py", "print('ok')\n")
        fixture.write_skill(
            body=(
                "# Hidden hop\n\n"
                "Load `references/first.md` for the first condition.\n"
                "Load `references/second.md` directly for the second condition.\n"
                "Run `scripts/helper.py` when mechanical validation is needed.\n"
            )
        )

        result = fixture.run()

        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("hidden second-hop Markdown reference `second.md`", result.stdout)
        self.assertNotIn("orphan reference", result.stdout)
        self.assertNotIn("missing local", result.stdout)

    def test_runtime_markdown_artifacts_are_ignored_but_interpreter_prefixed_scripts_are_checked(self) -> None:
        fixture = self.fixture("command-paths")
        fixture.write_reference(
            "workflow.md",
            "# Workflow\n\nUpdate `SPEC.md`, `README.md`, and `CHANGELOG.md` as runtime artifacts.\n",
        )
        fixture.write_skill(
            body=(
                "# Command paths\n\n"
                "Load `references/workflow.md` when workflow artifacts change.\n"
                "Run `python3 scripts/missing-command.py --check` for validation.\n"
            )
        )

        result = fixture.run()

        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("missing local backtick `scripts/missing-command.py`", result.stdout)
        for artifact in ("SPEC.md", "README.md", "CHANGELOG.md"):
            self.assertNotIn(f"hidden second-hop Markdown reference `{artifact}`", result.stdout)
            self.assertNotIn(f"missing local backtick `{artifact}`", result.stdout)

    def test_orphan_reference_fails_and_orphan_script_clearly_warns(self) -> None:
        fixture = self.fixture("orphans")
        fixture.write_reference("orphan.md")
        fixture.write_script("orphan.py")

        result = fixture.run()

        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("orphan reference has no parent SKILL.md load condition", result.stdout)
        self.assertIn("orphan script is not linked from parent SKILL.md", result.stdout)
        self.assertIn("RESULT: FAIL", result.stdout)


if __name__ == "__main__":
    unittest.main()
