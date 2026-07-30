"""Generic contract-integrity checks for skill/reference prompt files.

These tests are intentionally *content-agnostic*. They do not assert that
particular sentences or design vocabulary appear in the markdown — that style of
"string-presence" test is a brittle change-detector that couples every wording
change to a test edit and provides little real assurance.

Instead they guard the things that break silently and actually matter:

- every SKILL.md has valid front-matter (name/description) and name matches its dir;
- every relative doc path a prompt references resolves to a real file (no dead cross-refs);
- internal markdown links resolve;
- no prompt file grows into an unreviewable wall (anti-bloat line cap);
- a small safety negative-guard list (e.g. Semgrep scans must go through the wrapper).

Real behavioral tests live in test_sliceproof.py / test_audit_skill.py.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PLUGIN_ROOT.parents[1]

# Loose formatting backstop for skill/reference prompts (matches audit-skill.py SKILL_LINE_MAX).
# A poor proxy for complexity, since a line cap is satisfied by compressing the same obligations
# into denser text; audit-skill.py reports words as the better signal, as a warning.
MD_LINE_CAP = 200

# Files that already exceeded the cap; tracked as pre-existing debt rather than silently allowed
# by a loose global cap. New/changed files must meet the cap.
# perspectives (156 lines) came into compliance when the backstop moved to 200.
PREEXISTING_OVER_CAP = {
    "plugins/super-developer/skills/code-doc/SKILL.md",
}

# Placeholder / non-file markers: paths containing these are runtime templates, not
# repository files, and must not be checked for existence.
PLACEHOLDER_CHARS = set("<>*$")
RUNTIME_PREFIXES = (".tasks/", ".planning/", ".worktrees/", ".superdeveloper/", "docs/testing/")


def prompt_files() -> list[Path]:
    paths = [PLUGIN_ROOT / "README.md"]
    paths += sorted((PLUGIN_ROOT / "references").glob("*.md"))
    paths += sorted((PLUGIN_ROOT / "skills").glob("**/*.md"))
    return [p for p in paths if p.exists()]


def skill_files() -> list[Path]:
    return sorted((PLUGIN_ROOT / "skills").glob("*/SKILL.md"))


def is_runtime_or_placeholder(candidate: str) -> bool:
    if any(ch in candidate for ch in PLACEHOLDER_CHARS):
        return True
    if candidate.startswith(("http://", "https://", "#", "mailto:")):
        return True
    if candidate.startswith(RUNTIME_PREFIXES):
        return True
    return False


def looks_like_plugin_doc(candidate: str) -> bool:
    """Only enforce existence for paths that clearly point at skill/reference docs."""
    return candidate.endswith(".md") and (
        "references/" in candidate
        or candidate.endswith("SKILL.md")
        or "skills/" in candidate
        or candidate.startswith("plugins/super-developer/")
    )


# Backtick code-span paths and markdown-link targets.
BACKTICK_PATH_RE = re.compile(r"`([^`\n]+?\.md)`")
MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def referenced_doc_paths(text: str) -> list[str]:
    raw: list[str] = []
    for m in BACKTICK_PATH_RE.finditer(text):
        raw.append(m.group(1).strip())
    for m in MD_LINK_RE.finditer(text):
        raw.append(m.group(1).split()[0].strip())
    found: list[str] = []
    for candidate in raw:
        # Unwrap `key=value` spans (e.g. `repair_contract_path=references/x.md`).
        if "=" in candidate:
            candidate = candidate.rsplit("=", 1)[-1].strip()
        # Skip bare filenames with no directory component (too generic to resolve).
        if "/" not in candidate:
            continue
        found.append(candidate)
    return found


def resolve_candidate(source: Path, candidate: str) -> Path | None:
    """Resolve a referenced path relative to the source file, its skill dir, or repo root."""
    candidate = candidate.split("#", 1)[0]
    if not candidate:
        return None
    bases = [source.parent, REPO_ROOT, PLUGIN_ROOT / "skills"]
    # Also allow resolution relative to the skill root (…/skills/<name>/) for `references/x.md`.
    for parent in source.parents:
        if parent.parent.name == "skills":
            bases.append(parent)
            break
    for base in bases:
        resolved = (base / candidate)
        if resolved.exists():
            return resolved
    return None


class FrontMatterTests(unittest.TestCase):
    def test_every_skill_has_valid_frontmatter(self) -> None:
        for skill in skill_files():
            text = skill.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), f"{skill}: missing front-matter")
            end = text.find("\n---", 4)
            self.assertGreater(end, 0, f"{skill}: unterminated front-matter")
            fm = text[4:end]
            name_match = re.search(r"^name:\s*(\S+)", fm, re.MULTILINE)
            self.assertIsNotNone(name_match, f"{skill}: front-matter missing name")
            self.assertIn("description:", fm, f"{skill}: front-matter missing description")
            self.assertEqual(
                name_match.group(1).strip(),  # type: ignore[union-attr]
                skill.parent.name,
                f"{skill}: front-matter name must match skill directory",
            )


class CrossReferenceTests(unittest.TestCase):
    def test_referenced_doc_paths_resolve(self) -> None:
        missing: list[str] = []
        for source in prompt_files():
            text = source.read_text(encoding="utf-8")
            for candidate in referenced_doc_paths(text):
                if is_runtime_or_placeholder(candidate) or not looks_like_plugin_doc(candidate):
                    continue
                if resolve_candidate(source, candidate) is None:
                    missing.append(f"{source.relative_to(REPO_ROOT)} -> {candidate}")
        self.assertEqual(missing, [], "dead doc cross-references:\n" + "\n".join(missing))


class BudgetTests(unittest.TestCase):
    def test_no_prompt_file_exceeds_line_cap(self) -> None:
        oversized: list[str] = []
        for source in prompt_files():
            rel = str(source.relative_to(REPO_ROOT))
            # The line cap governs skill/reference prompts, not README docs (matches audit-skill.py).
            if source.name == "README.md" or rel in PREEXISTING_OVER_CAP:
                continue
            n = len(source.read_text(encoding="utf-8").splitlines())
            if n > MD_LINE_CAP:
                oversized.append(f"{rel}: {n} lines")
        self.assertEqual(oversized, [], f"prompt files over {MD_LINE_CAP} lines:\n" + "\n".join(oversized))


class SafetyGuardTests(unittest.TestCase):
    def test_semgrep_scans_go_through_the_wrapper(self) -> None:
        # If a prompt invokes a Semgrep scan, it must use the local wrapper, never a raw
        # `semgrep scan`/`semgrep --config …` that could hit the registry/network.
        raw = re.compile(r"`[^`]*\bsemgrep\s+(?:scan\b|--)")
        offenders: list[str] = []
        for source in prompt_files():
            text = source.read_text(encoding="utf-8")
            for m in raw.finditer(text):
                span = m.group(0)
                if "semgrep_rules.py" not in span:
                    offenders.append(f"{source.relative_to(REPO_ROOT)}: {span}")
        self.assertEqual(offenders, [], "raw semgrep scan invocation found:\n" + "\n".join(offenders))

    def test_sliceproof_python_invocations_use_plugin_root(self) -> None:
        expected = '${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py'
        offenders: list[str] = []
        for source in prompt_files():
            for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
                if "python3 " in line and "sliceproof.py" in line and expected not in line:
                    offenders.append(f"{source.relative_to(REPO_ROOT)}:{line_number}: {line.strip()}")
        self.assertEqual(offenders, [], "non-portable sliceproof invocation found:\n" + "\n".join(offenders))


if __name__ == "__main__":
    unittest.main()
