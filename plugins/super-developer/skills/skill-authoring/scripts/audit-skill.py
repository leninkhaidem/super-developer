#!/usr/bin/env python3
"""Audit skill prompt structure, budgets, and local reference links.

Usage:
  audit-skill.py path/to/skills/<skill-name>
  audit-skill.py --strict path/to/skills/<skill-name>/SKILL.md

The script is intentionally mechanical. It fails on invalid frontmatter and broken local links.
Use --strict to fail on budget caps while authoring or revising a skill.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

LONG_LINE_LIMIT = 160
SKILL_LINE_MAX = 150
REF_LINE_MAX = 150
SKILL_WORD_TARGET = (600, 1200)
REF_WORD_TARGET = (300, 900)

LOCAL_LINK_RE = re.compile(r"`((?:references|scripts)/[^`\s]+)`")
PRIVATE_REF_RE = re.compile(r"skills/([^/\s`]+)/references/")
KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*\s*:")


@dataclass
class Metrics:
    path: Path
    lines: int
    words: int
    chars: int
    max_line: int
    long_lines: list[tuple[int, int]]


def metrics(path: Path) -> Metrics:
    text = path.read_text()
    lines = text.splitlines()
    return Metrics(
        path=path,
        lines=len(lines),
        words=len(text.split()),
        chars=len(text),
        max_line=max((len(line) for line in lines), default=0),
        long_lines=[(i, len(line)) for i, line in enumerate(lines, 1) if len(line) > LONG_LINE_LIMIT],
    )


def find_skill_dir(path: Path) -> Path:
    path = path.resolve()
    if path.name == "SKILL.md":
        return path.parent
    if (path / "SKILL.md").exists():
        return path
    raise SystemExit(f"not a skill directory or SKILL.md: {path}")


def extract_frontmatter(skill_file: Path) -> tuple[str, int]:
    text = skill_file.read_text()
    if not text.startswith("---\n"):
        raise ValueError("missing opening frontmatter marker")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("missing closing frontmatter marker")
    return text[4:end], end + 5


def validate_frontmatter(skill_file: Path) -> list[str]:
    errors: list[str] = []
    try:
        fm, _ = extract_frontmatter(skill_file)
    except ValueError as exc:
        return [str(exc)]

    seen: set[str] = set()
    block_key = False
    for lineno, line in enumerate(fm.splitlines(), 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            if not seen:
                errors.append(f"frontmatter line {lineno}: indented content before any key")
            continue
        if not KEY_RE.match(line):
            errors.append(f"frontmatter line {lineno}: unindented line is not a key/value pair")
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        seen.add(key)
        block_key = value.strip() in {">", "|", ">-", "|-", ">+", "|+"}
        _ = block_key

    for required in ("name", "description"):
        if required not in seen:
            errors.append(f"frontmatter missing required key: {required}")
    return errors


def referenced_local_files(skill_dir: Path, files: list[Path]) -> tuple[list[Path], list[tuple[Path, str]]]:
    found: list[Path] = []
    missing: list[tuple[Path, str]] = []
    for path in files:
        for rel in LOCAL_LINK_RE.findall(path.read_text()):
            if "<" in rel or ">" in rel:
                continue
            target = skill_dir / rel
            if target.exists():
                found.append(target)
            else:
                missing.append((path, rel))
    return sorted(set(found)), missing


def private_reference_links(skill_dir: Path, files: list[Path]) -> list[tuple[Path, str]]:
    skill_name = skill_dir.name
    hits: list[tuple[Path, str]] = []
    for path in files:
        for linked_skill in PRIVATE_REF_RE.findall(path.read_text()):
            if linked_skill != skill_name:
                hits.append((path, linked_skill))
    return hits


def print_metric(prefix: str, item: Metrics) -> None:
    print(
        f"{prefix}: {item.path} lines={item.lines} words={item.words} "
        f"chars={item.chars} max_line={item.max_line} >{LONG_LINE_LIMIT}={len(item.long_lines)}"
    )
    for lineno, length in item.long_lines:
        print(f"  long line: {lineno} chars={length}")


def audit(skill_dir: Path, *, strict: bool = False) -> int:
    # Keep the public signature/CLI stable, but always enforce strict checks internally.
    strict = True
    skill_file = skill_dir / "SKILL.md"
    ref_dir = skill_dir / "references"
    script_dir = skill_dir / "scripts"
    refs = sorted(ref_dir.rglob("*.md")) if ref_dir.exists() else []
    scripts = sorted(p for p in script_dir.glob("*") if p.is_file()) if script_dir.exists() else []
    files = [skill_file, *refs]

    errors: list[str] = []
    warnings: list[str] = []
    budget_errors: list[str] = []

    errors.extend(f"{skill_file}: {msg}" for msg in validate_frontmatter(skill_file))

    skill_metrics = metrics(skill_file)
    ref_metrics = [metrics(path) for path in refs]
    print_metric("SKILL", skill_metrics)
    if skill_metrics.lines > SKILL_LINE_MAX:
        budget_errors.append(f"{skill_file}: SKILL.md exceeds {SKILL_LINE_MAX} lines")
    if not (SKILL_WORD_TARGET[0] <= skill_metrics.words <= SKILL_WORD_TARGET[1]):
        warnings.append(f"{skill_file}: words outside target {SKILL_WORD_TARGET[0]}-{SKILL_WORD_TARGET[1]}")
    if skill_metrics.long_lines:
        warnings.append(f"{skill_file}: has lines over {LONG_LINE_LIMIT} chars")

    total_ref_lines = total_ref_words = total_ref_chars = 0
    for item in ref_metrics:
        print_metric("REF", item)
        total_ref_lines += item.lines
        total_ref_words += item.words
        total_ref_chars += item.chars
        if item.lines > REF_LINE_MAX:
            budget_errors.append(f"{item.path}: reference exceeds {REF_LINE_MAX} lines")
        if not (REF_WORD_TARGET[0] <= item.words <= REF_WORD_TARGET[1]):
            warnings.append(f"{item.path}: words outside target {REF_WORD_TARGET[0]}-{REF_WORD_TARGET[1]}")
        if item.long_lines:
            warnings.append(f"{item.path}: has lines over {LONG_LINE_LIMIT} chars")

    linked, missing = referenced_local_files(skill_dir, files)
    for path, rel in missing:
        errors.append(f"{path}: missing local linked file `{rel}`")
    for path, linked_skill in private_reference_links(skill_dir, files):
        errors.append(f"{path}: deep-links private references for skill `{linked_skill}`")

    hidden_second_hops = []
    for ref in refs:
        for rel in LOCAL_LINK_RE.findall(ref.read_text()):
            if "<" in rel or ">" in rel:
                continue
            hidden_second_hops.append((ref, rel))
    for ref, rel in hidden_second_hops:
        warnings.append(f"{ref}: reference mentions local link `{rel}`; ensure parent skill owns load condition")

    print(
        f"REFERENCES: count={len(refs)} total_lines={total_ref_lines} "
        f"total_words={total_ref_words} total_chars={total_ref_chars}"
    )
    print(f"LOCAL LINKS: resolved={len(linked)} missing={len(missing)}")
    print(f"SCRIPTS: count={len(scripts)}")

    if budget_errors:
        heading = "STRICT BUDGET ERRORS" if strict else "BUDGET WARNINGS"
        print(f"\n{heading}:")
        for warning in budget_errors:
            print(f"- {warning}")
        if strict:
            errors.extend(budget_errors)
    if warnings:
        print("\nWARNINGS:")
        for warning in warnings:
            print(f"- {warning}")
    if errors:
        print("\nERRORS:")
        for error in errors:
            print(f"- {error}")
        print("\nRESULT: FAIL")
        return 1
    print("\nRESULT: PASS")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="skill directory or SKILL.md to audit")
    parser.add_argument("--strict", action="store_true", help="fail on line/word/reference budget cap violations")
    args = parser.parse_args(argv)
    return audit(find_skill_dir(args.path), strict=args.strict)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
