#!/usr/bin/env python3
"""Audit skill prompt structure, complexity budgets, and local reference links.

Usage:
  audit-skill.py path/to/skills/<skill-name>
  audit-skill.py --strict path/to/skills/<skill-name>/SKILL.md

The audit always fails invalid frontmatter, broken local links, hidden Markdown-reference hops,
and hard budget violations (words and a loose line backstop). Word *targets* and long-line
density remain warnings. ``--strict`` is accepted as a backward-compatible no-op because
budgets are always enforced.

Words, not lines, are the enforced complexity ceiling. See the constants below for why.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

LONG_LINE_LIMIT = 120

# Line caps are a loose *formatting* backstop, not the complexity budget. A tight line cap
# is gameable and actively harmful: prose compressed into fewer, denser lines passes it,
# so the cap ends up rewarding the unreadable density it was meant to prevent. Keep these
# generous enough that plain, readable prose never has to be compressed to fit.
SKILL_LINE_MAX = 220
REF_LINE_MAX = 220

# Words are the real complexity ceiling: line-wrapping invariant, so unlike a line cap this
# cannot be satisfied by reflowing the same obligations into denser text. Adding meaningful
# new behaviour to a prompt must cost budget; reformatting it for clarity must not.
SKILL_WORD_MAX = 1800
REF_WORD_MAX = 1800
SKILL_WORD_TARGET = (600, 1500)
REF_WORD_TARGET = (300, 1200)
DESCRIPTION_CHAR_MAX = 280
DESCRIPTION_CONTENT_LINE_TARGET = 3

FRONTMATTER_START_RE = re.compile(r"\A---[ \t]*\r?\n")
FRONTMATTER_END_RE = re.compile(r"^---[ \t]*(?:\r?\n|\Z)", re.MULTILINE)
KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:(.*)$")
BLOCK_SCALAR_RE = re.compile(r"^([>|])([+-])?$")
KEBAB_CASE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
BACKTICK_RE = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
PRIVATE_REF_RE = re.compile(r"skills/([^/\s`]+)/references/")
URL_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
NUMBER_RE = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?$")


@dataclass
class Metrics:
    path: Path
    lines: int
    words: int
    chars: int
    max_line: int
    long_lines: list[tuple[int, int]]


@dataclass(frozen=True)
class LocalPathReference:
    source: Path
    display: str
    target: Path
    is_markdown: bool
    kind: str


@dataclass
class FrontmatterValidation:
    errors: list[str]
    warnings: list[str]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def metrics(path: Path) -> Metrics:
    text = read_text(path)
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
    text = read_text(skill_file)
    opening = FRONTMATTER_START_RE.match(text)
    if opening is None:
        raise ValueError("missing opening frontmatter marker")
    closing = FRONTMATTER_END_RE.search(text, opening.end())
    if closing is None:
        raise ValueError("missing closing frontmatter marker")
    return text[opening.end() : closing.start()], closing.end()


def strip_inline_comment(value: str) -> str:
    """Remove a simple YAML comment while preserving hashes inside quoted scalars."""
    quote: str | None = None
    escaped = False
    for index, char in enumerate(value):
        if quote == '"' and char == "\\" and not escaped:
            escaped = True
            continue
        if char in {"'", '"'} and not escaped:
            if quote is None:
                quote = char
            elif quote == char:
                quote = None
        if char == "#" and quote is None and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
        escaped = False
    return value.strip()


def parse_inline_string(value: str) -> tuple[str | None, str | None]:
    """Parse the small scalar subset needed by skill frontmatter."""
    value = strip_inline_comment(value).strip()
    if not value:
        return None, None
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            return None, "unterminated single-quoted string"
        return value[1:-1].replace("''", "'"), None
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return None, "invalid double-quoted string"
        return (parsed, None) if isinstance(parsed, str) else (None, "value must be a string")

    lowered = value.lower()
    non_strings = {"null", "~", "true", "false", "yes", "no", "on", "off"}
    if lowered in non_strings or NUMBER_RE.fullmatch(value) or value.startswith(("[", "{", "&", "*", "!")):
        return None, "value must be a string"
    return value, None


def parse_block_string(lines: list[str], style: str) -> tuple[str, int, list[str]]:
    errors: list[str] = []
    nonblank = [line for line in lines if line.strip()]
    if any("\t" in line[: len(line) - len(line.lstrip())] for line in nonblank):
        errors.append("block scalar indentation must use spaces")
    if any(not line.startswith(" ") for line in nonblank):
        errors.append("block scalar content must be indented")

    indents = [len(line) - len(line.lstrip(" ")) for line in nonblank if line.startswith(" ")]
    indent = min(indents, default=0)
    content = [line[indent:] if line.strip() else "" for line in lines]
    content_lines = sum(bool(line.strip()) for line in content)

    if style == "|":
        return "\n".join(content).strip(), content_lines, errors

    folded: list[str] = []
    blank_lines = 0
    for line in content:
        if not line.strip():
            blank_lines += 1
            continue
        if blank_lines:
            folded.append("\n" * blank_lines)
            blank_lines = 0
        elif folded:
            folded.append(" ")
        folded.append(line.strip())
    return "".join(folded).strip(), content_lines, errors


def validate_frontmatter(skill_file: Path) -> FrontmatterValidation:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        frontmatter, _ = extract_frontmatter(skill_file)
    except ValueError as exc:
        return FrontmatterValidation([str(exc)], [])

    entries: dict[str, tuple[str | None, int]] = {}
    description_content_lines: int | None = None
    lines = frontmatter.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        lineno = index + 2
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if line.startswith((" ", "\t")):
            errors.append(f"frontmatter line {lineno}: unexpected indented content")
            index += 1
            continue

        match = KEY_RE.match(line)
        if match is None:
            errors.append(f"frontmatter line {lineno}: unindented line is not a key/value pair")
            index += 1
            continue
        key, raw_value = match.groups()
        duplicate = key in entries
        if duplicate:
            errors.append(f"frontmatter line {lineno}: duplicate key: {key}")

        cleaned_value = strip_inline_comment(raw_value).strip()
        block_match = BLOCK_SCALAR_RE.fullmatch(cleaned_value)
        if block_match:
            block_lines: list[str] = []
            next_index = index + 1
            while next_index < len(lines) and (
                not lines[next_index].strip() or lines[next_index].startswith((" ", "\t"))
            ):
                block_lines.append(lines[next_index])
                next_index += 1
            value, content_line_count, block_errors = parse_block_string(block_lines, block_match.group(1))
            errors.extend(f"frontmatter line {lineno}: {message}" for message in block_errors)
            if key == "description" and not duplicate:
                description_content_lines = content_line_count
            index = next_index
        else:
            value, scalar_error = parse_inline_string(raw_value)
            if scalar_error:
                errors.append(f"frontmatter line {lineno}: {key} {scalar_error}")
            index += 1

        if not duplicate:
            entries[key] = (value, lineno)

    for required in ("name", "description"):
        if required not in entries:
            errors.append(f"frontmatter missing required key: {required}")
            continue
        value, lineno = entries[required]
        if not isinstance(value, str):
            errors.append(f"frontmatter line {lineno}: {required} must be a non-empty string")
        elif not value.strip():
            errors.append(f"frontmatter line {lineno}: {required} must be a non-empty string")

    name_entry = entries.get("name")
    if name_entry and isinstance(name_entry[0], str) and name_entry[0].strip():
        name = name_entry[0].strip()
        if KEBAB_CASE_RE.fullmatch(name) is None:
            errors.append(f"frontmatter line {name_entry[1]}: name must be kebab-case")
        if name != skill_file.parent.name:
            errors.append(
                f"frontmatter line {name_entry[1]}: name `{name}` does not match "
                f"skill directory `{skill_file.parent.name}`"
            )

    description_entry = entries.get("description")
    if description_entry and isinstance(description_entry[0], str):
        description = description_entry[0].strip()
        if len(description) > DESCRIPTION_CHAR_MAX:
            errors.append(
                f"frontmatter line {description_entry[1]}: folded description exceeds "
                f"{DESCRIPTION_CHAR_MAX} characters ({len(description)})"
            )
    if description_content_lines is not None and description_content_lines > DESCRIPTION_CONTENT_LINE_TARGET:
        warnings.append(
            f"frontmatter description uses {description_content_lines} content lines; "
            f"target is at most {DESCRIPTION_CONTENT_LINE_TARGET}"
        )

    return FrontmatterValidation(errors, warnings)


def markdown_destination(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<"):
        closing = raw.find(">")
        if closing != -1:
            return raw[1:closing].strip()
    return raw.split(maxsplit=1)[0] if raw else ""


def is_placeholder_path(value: str) -> bool:
    return bool(
        not value
        or "$" in value
        or re.search(r"<[^>]+>|\{[^}]+\}|\[[^]]+\]|(?:^|/)\.\.\.(?:/|$)|[*?]", value)
    )


def normalize_local_path(value: str) -> str | None:
    value = unquote(value.strip()).replace("\\ ", " ")
    if not value or value.startswith(("#", "//", "/")) or URL_SCHEME_RE.match(value):
        return None
    value = value.split("#", 1)[0].split("?", 1)[0].rstrip(".,;:")
    if is_placeholder_path(value):
        return None
    return value or None


def looks_like_backticked_path(value: str) -> bool:
    return value == "SKILL.md" or value.startswith(("./", "../", "references/", "scripts/"))


def local_path_references(skill_dir: Path, files: list[Path]) -> list[LocalPathReference]:
    links: list[LocalPathReference] = []
    for source in files:
        text = read_text(source)
        for raw in BACKTICK_RE.findall(text):
            try:
                tokens = shlex.split(raw)
            except ValueError:
                tokens = raw.split()
            for display in tokens:
                rel = normalize_local_path(display)
                if rel is None or not looks_like_backticked_path(rel):
                    continue
                base = skill_dir if rel == "SKILL.md" or rel.startswith(("references/", "scripts/")) else source.parent
                target = (base / rel).resolve()
                links.append(
                    LocalPathReference(source, display, target, Path(rel).suffix.lower() == ".md", "backtick")
                )

        for raw in MARKDOWN_LINK_RE.findall(text):
            display = markdown_destination(raw)
            rel = normalize_local_path(display)
            if rel is None:
                continue
            target = (source.parent / rel).resolve()
            links.append(
                LocalPathReference(source, display, target, Path(rel).suffix.lower() == ".md", "Markdown link")
            )

    return list(dict.fromkeys(links))


def referenced_local_files(
    links: list[LocalPathReference],
) -> tuple[list[Path], list[LocalPathReference]]:
    found = sorted({link.target for link in links if link.target.exists()})
    missing = [link for link in links if not link.target.exists()]
    return found, missing


def private_reference_links(skill_dir: Path, files: list[Path]) -> list[tuple[Path, str]]:
    skill_name = skill_dir.name
    hits: list[tuple[Path, str]] = []
    for path in files:
        for linked_skill in PRIVATE_REF_RE.findall(read_text(path)):
            if linked_skill != skill_name and "<" not in linked_skill and ">" not in linked_skill:
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
    # Retain the argument for callers that used the old opt-in mode. It intentionally changes nothing.
    _ = strict
    skill_file = skill_dir / "SKILL.md"
    ref_dir = skill_dir / "references"
    script_dir = skill_dir / "scripts"
    refs = sorted(ref_dir.rglob("*.md")) if ref_dir.exists() else []
    scripts = (
        sorted(p for p in script_dir.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
        if script_dir.exists()
        else []
    )
    files = [skill_file, *refs]

    errors: list[str] = []
    warnings: list[str] = []
    line_cap_errors: list[str] = []

    frontmatter = validate_frontmatter(skill_file)
    errors.extend(f"{skill_file}: {message}" for message in frontmatter.errors)
    warnings.extend(f"{skill_file}: {message}" for message in frontmatter.warnings)

    skill_metrics = metrics(skill_file)
    ref_metrics = [metrics(path) for path in refs]
    print_metric("SKILL", skill_metrics)
    if skill_metrics.lines > SKILL_LINE_MAX:
        line_cap_errors.append(f"{skill_file}: SKILL.md exceeds hard cap of {SKILL_LINE_MAX} lines")
    if skill_metrics.words > SKILL_WORD_MAX:
        line_cap_errors.append(
            f"{skill_file}: SKILL.md exceeds hard budget of {SKILL_WORD_MAX} words "
            f"({skill_metrics.words}); remove obligations rather than compressing prose"
        )
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
            line_cap_errors.append(f"{item.path}: reference exceeds hard cap of {REF_LINE_MAX} lines")
        if item.words > REF_WORD_MAX:
            line_cap_errors.append(
                f"{item.path}: reference exceeds hard budget of {REF_WORD_MAX} words "
                f"({item.words}); remove obligations rather than compressing prose"
            )
        if not (REF_WORD_TARGET[0] <= item.words <= REF_WORD_TARGET[1]):
            warnings.append(f"{item.path}: words outside target {REF_WORD_TARGET[0]}-{REF_WORD_TARGET[1]}")
        if item.long_lines:
            warnings.append(f"{item.path}: has lines over {LONG_LINE_LIMIT} chars")

    local_links = local_path_references(skill_dir, files)
    linked, missing = referenced_local_files(local_links)
    for link in missing:
        errors.append(f"{link.source}: missing local {link.kind} `{link.display}`")
    for path, linked_skill in private_reference_links(skill_dir, files):
        errors.append(f"{path}: deep-links private references for skill `{linked_skill}`")

    parent_targets = {link.target for link in local_links if link.source == skill_file}
    for ref in refs:
        if ref.resolve() not in parent_targets:
            errors.append(f"{ref}: orphan reference has no parent SKILL.md load condition")
    for script in scripts:
        if script.resolve() not in parent_targets:
            warnings.append(f"{script}: orphan script is not linked from parent SKILL.md")

    ref_set = set(refs)
    for link in local_links:
        if link.source not in ref_set:
            continue
        if link.is_markdown and link.target != skill_file.resolve():
            errors.append(f"{link.source}: hidden second-hop Markdown reference `{link.display}`")
        elif link.target != skill_file.resolve():
            warnings.append(
                f"{link.source}: reference mentions local link `{link.display}`; keep script loading parent-owned"
            )

    errors.extend(line_cap_errors)
    print(
        f"REFERENCES: count={len(refs)} total_lines={total_ref_lines} "
        f"total_words={total_ref_words} total_chars={total_ref_chars}"
    )
    print(f"LOCAL LINKS: resolved={len(linked)} missing={len(missing)}")
    print(f"SCRIPTS: count={len(scripts)}")

    if line_cap_errors:
        print("\nHARD LINE CAP ERRORS:")
        for error in line_cap_errors:
            print(f"- {error}")
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
    parser.add_argument(
        "--strict",
        action="store_true",
        help="backward-compatible no-op; hard word/line budgets are always enforced and word targets only warn",
    )
    args = parser.parse_args(argv)
    return audit(find_skill_dir(args.path), strict=args.strict)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
