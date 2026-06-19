from __future__ import annotations

import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PLUGIN_ROOT.parents[1]


def read_repo(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def prompt_surface_paths() -> list[Path]:
    paths = [REPO_ROOT / "README.md", PLUGIN_ROOT / "README.md"]
    paths.extend(sorted((PLUGIN_ROOT / "references").glob("*.md")))
    paths.extend(sorted((PLUGIN_ROOT / "skills").glob("**/*.md")))
    return paths


def context_window(text: str, needle: str, radius: int = 120) -> str:
    index = text.find(needle)
    if index < 0:
        return ""
    start = max(0, index - radius)
    end = min(len(text), index + len(needle) + radius)
    return text[start:end].lower()


class SkillPromptSurfaceTests(unittest.TestCase):
    def test_readmes_document_optional_local_semgrep_lifecycle(self) -> None:
        required = [
            ".superdeveloper/preferences.yml",
            ".superdeveloper/model-preferences.yml",
            ".superdeveloper/semgrep/excluded-rules.yml",
            ".superdeveloper/semgrep/local-rules.yml",
            ".superdeveloper/semgrep/stack-profile.yml",
            "${SUPER_DEVELOPER_PLUGIN_ROOT}/.cache/semgrep-rules/community",
            "clone",
            "git pull --ff-only",
            "disabled by default",
            "summarize",
            "list-findings",
            "show-finding",
            ".tasks/<feature>/semgrep/<WP-ID>.semgrep.json",
            ".tasks/<feature>/semgrep/<WP-ID>.semgrep-summary.json",
            ".tasks/<feature>/semgrep/integration.semgrep.json",
            ".tasks/<feature>/semgrep/integration.semgrep-summary.json",
            "raw digest",
            "summary digest",
            "advisory",
            "read-only",
        ]
        for rel in ["README.md", "plugins/super-developer/README.md"]:
            with self.subTest(readme=rel):
                text = read_repo(rel)
                for needle in required:
                    self.assertIn(needle, text)
                self.assertRegex(text, r"old `\.superdeveloper/model-preferences\.yml`[^.]+ignored/deprecated")
                self.assertRegex(text.lower(), r"routine scans? (must |never|do not|must not|no hidden|never hide)")
                self.assertNotRegex(text, r"semgrep scan\s+\\")
                self.assertNotIn("--config auto", text)

    def test_obsolete_or_unsafe_terms_are_only_negative_guidance(self) -> None:
        for path in prompt_surface_paths():
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(REPO_ROOT)
            if ".superdeveloper/model-preferences.yml" in text:
                window = context_window(text, ".superdeveloper/model-preferences.yml")
                self.assertIn("deprecated", window, rel)
                self.assertRegex(window, r"ignor(?:e|ed)", rel)
                if any(word in window for word in ["read", "copy", "translate", "preserve", "migrate", "bridge"]):
                    self.assertRegex(window, r"\b(do not|does not|never|no migration|never migrated|ignored:)\b", rel)
            for token in [".superdeveloper/semgrep-policy.yml", "local-rule-files", "local-rules-path"]:
                if token in text:
                    window = context_window(text, token)
                    self.assertRegex(window, r"\b(do not|no|without|reject|forbid|forbidden|never)\b", f"{rel}: {token}")
            if path.name != "semgrep.md":
                self.assertNotIn("--config auto", text, rel)
                self.assertNotRegex(text, r"(?m)^\s*semgrep\s+scan\b", rel)
            for line in text.splitlines():
                lowered = line.lower()
                if "semgrep" in lowered and "fix-all" in lowered:
                    self.assertRegex(lowered, r"\b(not|no|without|unless|advisory|bounded)\b", f"{rel}: {line}")
                if "semgrep" in lowered and "automatic" in lowered and "blocker" in lowered:
                    self.assertRegex(lowered, r"\b(not|no|without|unless)\b", f"{rel}: {line}")

    def test_semgrep_prompt_detail_stays_progressively_disclosed(self) -> None:
        skill_paths = [
            PLUGIN_ROOT / "skills" / "conceptualize" / "SKILL.md",
            PLUGIN_ROOT / "skills" / "implementation-plan" / "SKILL.md",
            PLUGIN_ROOT / "skills" / "implement" / "SKILL.md",
            PLUGIN_ROOT / "skills" / "review-code" / "SKILL.md",
            PLUGIN_ROOT / "skills" / "audit" / "SKILL.md",
            PLUGIN_ROOT / "skills" / "skill-authoring" / "SKILL.md",
        ]
        eager_forbidden = [
            "semgrep-rules.git",
            ".cache/semgrep-rules/community",
            ".tasks/<feature>/semgrep/<WP-ID>.semgrep.json",
            "show-finding --",
            "list-findings --",
            "semgrep scan",
        ]
        for path in skill_paths:
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(REPO_ROOT)
            self.assertLessEqual(len(text.splitlines()), 150, rel)
            for token in eager_forbidden:
                self.assertNotIn(token, text, rel)

        semgrep_reference = PLUGIN_ROOT / "references" / "semgrep.md"
        text = semgrep_reference.read_text(encoding="utf-8")
        self.assertLessEqual(len(text.splitlines()), 150)
        self.assertLessEqual(len(text.split()), 900)
        self.assertIn("Load it only when resolving Semgrep state", text)
        self.assertNotIn("rules inventory", text.lower().replace("rule inventory", ""))

    def test_helper_user_facing_summaries_are_bounded_and_not_workflow_jargon(self) -> None:
        source = (PLUGIN_ROOT / "assets" / "semgrep_rules.py").read_text(encoding="utf-8")
        self.assertIn("Semgrep scan complete: findings=", source)
        self.assertIn("SUMMARY_TOP_N", source)
        self.assertIn("LIST_LIMIT_MAX", source)
        self.assertIn("semgrep_severity_is_advisory", source)
        summary_region = source[source.index("def _build_summary") : source.index("def _write_summary")]
        for workflow_word in ["proof", "package verification", "Slice", "planning", "staging"]:
            self.assertNotIn(workflow_word, summary_region)


if __name__ == "__main__":
    unittest.main()
