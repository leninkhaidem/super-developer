#!/usr/bin/env python3
"""Mechanical helper for Slice-first planned-feature artifacts.

The helper performs deterministic structure, path-safety, checklist-coverage,
and cheap pointer-resolve checks. It does not judge semantic evidence quality,
run tests, mutate package status, write the result file, or replace review/audit.
A registry package is new-shape iff it omits proof_path; new-shape PASS is never
applied to a package that still declares that field.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

FEATURE_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
PACKAGE_ID_RE = re.compile(r"^WP[1-9]\d*$")
SLICE_ID_RE = re.compile(r"^[A-Z][A-Z0-9-]*-[0-9]{3}$")
H3_ID_RE = re.compile(r"^\s*###\s+`?([A-Z][A-Z0-9-]*-[0-9]{3})`?(?:\s+(?:—|-)\s*(.*?))?\s*$")
STATUS_VALUES = {"pending", "in_progress", "done", "blocked"}
FEATURE_STATUS_VALUES = {"planned", "reviewed", "in_progress", "completed", "blocked", "on_hold"}
REGISTRY_KEYS = {"feature", "title", "status", "spec_path", "authoritative_slices", "work_packages"}
REGISTRY_PACKAGE_KEYS = {"id", "path", "report_path", "status", "depends_on"}
LEGACY_PACKAGE_KEYS = {"proof_path"}
REQUIRED_PACKAGE_SECTIONS = {
    "Scope",
    "Assigned Slices",
    "Primary Paths",
    "Verification Expectations",
    "Acceptance Checklist",
    "Package Verification Report",
    "Dependencies",
}
# ``Plan gaps`` is required so that finding nothing is an affirmative ``- none`` an auditor can read, not a silent
# absence. Reports are gitignored, so a deleted section leaves no diff: only a written claim can be audited.
REQUIRED_REPORT_SECTIONS = {
    "Acceptance Checklist Result",
    "Blocking findings",
    "Advisory notes",
    "Plan gaps",
    "Reviewed state",
    "Gaps",
}
# semantic_done is always False by design. It is not a failure signal and not a lifecycle state: this helper
# checks structure only, so orchestrator checklist re-run, report evidence, and review/audit own completion.
SEMANTIC_DONE_NOTE = (
    "structural check only; orchestrator checklist re-run, report evidence, and review/audit own semantic completion"
)
BLOCKING_MARKER_RE = re.compile(r"\b(?:TODO|OPEN|GAP)\b", re.IGNORECASE)
UNRESOLVED_MARKER_RE = re.compile(r"\b(?:TODO|OPEN)\b", re.IGNORECASE)
NEGATED_APPROVAL_RE = re.compile(
    r"\b(?:unapproved|not\s+(?:explicitly\s+)?(?:user[-\s]?)?approved|no\s+(?:user[-\s]?)?approval|"
    r"without\s+(?:user[-\s]?)?approval|(?:pending|requested|awaiting)\s+approval|approval\s+(?:pending|requested|awaiting)|"
    r"approval\s*(?::|is\s+|was\s+)?\s*(?:missing|absent|denied|rejected|not\s+granted|none|no|tbd|to\s+be\s+determined|unknown|unconfirmed)|"
    r"approval\s+not\s+(?:granted|given|provided|confirmed))\b",
    re.IGNORECASE,
)
APPROVAL_SOURCE_RE = re.compile(
    r"\b(?:approved\s+by|approval\s+(?:granted|given|provided|confirmed)\s+by)\s+(?P<source>[^;\n|]+)",
    re.IGNORECASE,
)
USER_APPROVED_SOURCE_RE = re.compile(
    r"\buser[-\s]?approved\s*(?::|by)\s*(?P<source>[^;\n|]+)",
    re.IGNORECASE,
)
APPROVAL_METADATA_VALUE_RE = re.compile(
    r"\b(?P<field>provenance|scope)\s*:\s*(?P<value>[^;\n|]+)",
    re.IGNORECASE,
)
PLAN_GAP_CLOSURE_RE = re.compile(r"\bclosed\s*:\s*(?P<value>[^;\n|]+)", re.IGNORECASE)
PLAN_GAP_PREFIX = "- warrant: plan-gap"
# A plan-gap closure is free text and is accepted as written. Only a bare non-answer is rejected, so an accurate
# short closure such as "repaired by WP1b" costs nothing while "yes" or "TBD" records nothing. "false" denies the
# closure outright and "null" is the same non-answer as "nil".
CONTENTLESS_CLOSURE_VALUES = frozenset(
    {
        "yes", "no", "ok", "n/a", "na", "none", "nil", "null", "false",
        "done", "fixed", "closed", "resolved", "complete", "completed",
        "tbd", "to be determined", "todo", "pending",
    }
)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
# Zero-width and format characters render nothing, so they cannot carry a written disposition.
INVISIBLE_CHAR_RE = re.compile(r"[\u00ad\u200b-\u200f\u2028\u2029\u202a-\u202e\u2060-\u2064\ufeff]")
APPROVAL_PLACEHOLDER_TOKEN_RE = re.compile(
    r"(?:^|[^a-z0-9])"
    r"(?:none|no|n/a|na|tbd|to\s+be\s+determined|todo|open|gap|unknown|unconfirmed|missing|absent|"
    r"pending|requested|awaiting|not\s+(?:provided|supplied|given|specified|available|set|known|confirmed|applicable|relevant))"
    r"(?:$|[^a-z0-9])",
    re.IGNORECASE,
)
PLACEHOLDER_VALUES = {"", "todo", "open", "gap", "tbd", "n/a", "na"}
FORBIDDEN_REGISTRY_KEYS = {
    "phases",
    "tasks",
    "acceptance_criteria",
    "design_decisions",
    "context_bundles",
    "proofs",
    "proof_entries",
    "verification_commands",
    "lifecycle",
}
TEST_ID_RE = re.compile(r"(?:^test:|::)", re.IGNORECASE)
FILE_SUFFIX_RE = re.compile(r"\.[A-Za-z0-9]{1,8}$")
COMMAND_INVOCATION_RE = re.compile(
    r"(?:^|[`$'\"(])\s*(?:python3?|py|pytest|npm|pnpm|yarn|make|cargo|go|node|bash|sh|zsh)\b|"
    r"\s(?:-[A-Za-z]|--[A-Za-z0-9-]+)\b|\s\|\s|&&|;",
    re.IGNORECASE,
)


class SliceproofError(Exception):
    def __init__(self, errors: list[str], advisories: list[dict[str, Any]] | None = None) -> None:
        super().__init__("\n".join(errors))
        self.errors = errors
        self.advisories = advisories or []


@dataclass(frozen=True)
class RawText:
    text: str


@dataclass(frozen=True)
class ReportValidationResult:
    errors: list[str]
    advisories: list[dict[str, Any]]


@dataclass(frozen=True)
class SliceRef:
    path: str
    must_satisfy: list[str]
    context_only: list[str]


@dataclass(frozen=True)
class PackageMarkdown:
    package_id: str
    title: str
    scope: str
    slice_refs: list[SliceRef]
    primary_paths: list[str]
    verification_expectations: list[str]
    acceptance_checklist: list[str]
    report_path: str
    dependencies: list[str]

    @property
    def must_satisfy_ids(self) -> list[str]:
        ids: list[str] = []
        for ref in self.slice_refs:
            ids.extend(ref.must_satisfy)
        return ids


@dataclass(frozen=True)
class RegistryPackage:
    package_id: str
    path: str
    proof_path: str
    report_path: str
    status: str
    depends_on: list[str]

    @property
    def is_new_shape(self) -> bool:
        return not self.proof_path.strip()


@dataclass(frozen=True)
class Registry:
    path: Path
    root: Path
    code_root: Path
    data: dict[str, Any]
    feature: str
    authoritative_slices: list[str]
    packages: list[RegistryPackage]

    def package(self, package_id: str) -> RegistryPackage | None:
        for package in self.packages:
            if package.package_id == package_id:
                return package
        return None


@dataclass(frozen=True)
class ProofRow:
    cells: dict[str, str]
    raw: str


@dataclass(frozen=True)
class PackageState:
    registry: Registry
    package: RegistryPackage
    package_md: PackageMarkdown
    report_path: Path


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except SliceproofError as exc:
        payload: dict[str, Any] = {"ok": False, "command": args.command, "errors": exc.errors}
        if args.command in {"validate-package-complete", "validate-final"} or exc.advisories:
            payload["advisories"] = exc.advisories
        write_json(sys.stderr, payload)
        return 1
    except (OSError, UnicodeError) as exc:
        payload = {"ok": False, "command": args.command, "errors": [f"{args.command}: I/O error: {exc}"]}
        if args.command in {"validate-package-complete", "validate-final"}:
            payload["advisories"] = []
        write_json(sys.stderr, payload)
        return 1
    if isinstance(result, RawText):
        sys.stdout.write(result.text)
        if not result.text.endswith("\n"):
            sys.stdout.write("\n")
        return 0
    write_json(sys.stdout, {"ok": True, "command": args.command, **result})
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Mechanical Slice-first planned-feature helper. Validation commands are read-only; "
            "only the orchestrator or agent writes the package result file."
        )
    )
    root_options = argparse.ArgumentParser(add_help=False)
    add_root_options(root_options)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_plan = subparsers.add_parser(
        "validate-plan",
        parents=[root_options],
        help="Validate a lightweight registry plus package Markdown and Slice H3 references.",
    )
    validate_plan.add_argument("tasks", type=Path, help="Path to .tasks/<feature>/tasks.json under the artifact root.")
    validate_plan.set_defaults(func=cmd_validate_plan)

    validate_package_complete = subparsers.add_parser(
        "validate-package-complete",
        parents=[root_options],
        help="Read-only check of one package result: checklist coverage and cheap pointer resolve.",
    )
    validate_package_complete.add_argument("tasks", type=Path, help="Path to .tasks/<feature>/tasks.json under the artifact root.")
    validate_package_complete.add_argument("--package", required=True, help="Work package id, for example WP1.")
    validate_package_complete.set_defaults(func=cmd_validate_package_complete)

    validate_final = subparsers.add_parser(
        "validate-final",
        parents=[root_options],
        help="Validate all packages are done and each new-shape result file is structurally complete.",
    )
    validate_final.add_argument("tasks", type=Path, help="Path to .tasks/<feature>/tasks.json under the artifact root.")
    validate_final.set_defaults(func=cmd_validate_final)
    return parser


def add_root_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--artifact-root",
        type=Path,
        help="Root for .planning/.tasks artifacts; defaults to the current directory.",
    )
    parser.add_argument(
        "--code-root",
        type=Path,
        help="Root for source, test, and static evidence paths; defaults to the current directory.",
    )


def cmd_validate_plan(args: argparse.Namespace) -> dict[str, Any]:
    registry, packages = load_and_validate_plan(args.tasks, artifact_root=args.artifact_root, code_root=args.code_root)
    return {
        "tasks": str(args.tasks),
        "artifact_root": str(registry.root),
        "code_root": str(registry.code_root),
        "feature": registry.feature,
        "packages": [package.package_id for package in registry.packages],
        "validated_package_markdown": sorted(packages),
        "validated_slices": sorted(registry.authoritative_slices),
        "mechanical_only": True,
        "semantic_done": False,
        "semantic_done_note": SEMANTIC_DONE_NOTE,
        "advisories": [],
    }


def cmd_validate_package_complete(args: argparse.Namespace) -> dict[str, Any]:
    state = load_package_state(args.tasks, args.package, artifact_root=args.artifact_root, code_root=args.code_root)
    errors = reject_non_new_shape(state.package)
    report_result = validate_report_markdown(state.report_path, state.package, state.package_md, state.registry)
    errors.extend(report_result.errors)
    if errors:
        raise SliceproofError(errors, report_result.advisories)
    return {
        "package": state.package.package_id,
        "package_status": state.package.status,
        "report_path": state.package.report_path,
        "new_shape": True,
        "mechanical_only": True,
        "semantic_done": False,
        "semantic_done_note": SEMANTIC_DONE_NOTE,
        "acceptance_checklist_items": state.package_md.acceptance_checklist,
        "advisories": report_result.advisories,
    }


def cmd_validate_final(args: argparse.Namespace) -> dict[str, Any]:
    registry, packages = load_and_validate_plan(args.tasks, artifact_root=args.artifact_root, code_root=args.code_root)
    errors: list[str] = []
    advisories: list[dict[str, Any]] = []
    validated_reports: list[str] = []
    for package in registry.packages:
        package_md = packages[package.package_id]
        if package.status != "done":
            errors.append(f"work_packages[{package.package_id}].status: expected 'done' for validate-final, got {package.status!r}")
        errors.extend(reject_non_new_shape(package))
        report_path = resolve_safe_path(
            registry.root,
            package.report_path,
            f"work_packages[{package.package_id}].report_path",
            expected_suffix=".package-verification.md",
            root_label="artifact root",
        )
        report_result = validate_report_markdown(report_path, package, package_md, registry)
        advisories.extend(report_result.advisories)
        if not report_result.errors:
            validated_reports.append(package.report_path)
        errors.extend(report_result.errors)
    if errors:
        raise SliceproofError(errors, advisories)
    return {
        "feature": registry.feature,
        "packages": [package.package_id for package in registry.packages],
        "reports_validated": validated_reports,
        "mechanical_only": True,
        "semantic_done": False,
        "semantic_done_note": SEMANTIC_DONE_NOTE,
        "advisories": advisories,
    }


def reject_non_new_shape(package: RegistryPackage) -> list[str]:
    if package.is_new_shape:
        return []
    return [
        f"work_packages[{package.package_id}]: cannot apply new-shape PASS while proof_path is declared"
    ]


def load_package_state(
    tasks_path: Path,
    package_id: str,
    *,
    artifact_root: Path | None = None,
    code_root: Path | None = None,
) -> PackageState:
    registry, packages = load_and_validate_plan(tasks_path, artifact_root=artifact_root, code_root=code_root)
    package = require_package(registry, package_id)
    package_md = packages[package.package_id]
    report_path = resolve_safe_path(
        registry.root,
        package.report_path,
        f"work_packages[{package.package_id}].report_path",
        expected_suffix=".package-verification.md",
        root_label="artifact root",
    )
    return PackageState(registry, package, package_md, report_path)


def load_and_validate_plan(
    tasks_path: Path,
    *,
    artifact_root: Path | None = None,
    code_root: Path | None = None,
) -> tuple[Registry, dict[str, PackageMarkdown]]:
    registry = load_registry(tasks_path, artifact_root=artifact_root, code_root=code_root)
    errors = validate_registry(registry)
    packages: dict[str, PackageMarkdown] = {}
    if not errors:
        for package in registry.packages:
            package_path = resolve_safe_path(
                registry.root,
                package.path,
                f"work_packages[{package.package_id}].path",
                expected_suffix=".md",
                must_exist_file=True,
                root_label="artifact root",
            )
            try:
                package_md = parse_package_markdown(package_path, package.package_id)
            except SliceproofError as exc:
                errors.extend(exc.errors)
                continue
            packages[package.package_id] = package_md
            errors.extend(validate_package_markdown(registry, package, package_md))
    if errors:
        raise SliceproofError(errors)
    return registry, packages


def load_registry(
    tasks_path: Path,
    *,
    artifact_root: Path | None = None,
    code_root: Path | None = None,
) -> Registry:
    cwd = Path.cwd().resolve(strict=False)
    root = resolve_cli_root(artifact_root, cwd, "--artifact-root")
    source_root = resolve_cli_root(code_root, cwd, "--code-root")
    tasks_resolved = resolve_tasks_argument(root, tasks_path, root_label="artifact root")
    try:
        data = json.loads(read_text_file(tasks_resolved, "tasks.json"))
    except json.JSONDecodeError as exc:
        raise SliceproofError([f"tasks.json: invalid JSON at line {exc.lineno} column {exc.colno}: {exc.msg}"])
    if not isinstance(data, dict):
        raise SliceproofError(["tasks.json: root must be an object"])

    feature = data.get("feature") if isinstance(data.get("feature"), str) else ""
    authoritative_slices = data.get("authoritative_slices") if isinstance(data.get("authoritative_slices"), list) else []
    packages_data = data.get("work_packages") if isinstance(data.get("work_packages"), list) else []
    packages: list[RegistryPackage] = []
    for item in packages_data:
        if not isinstance(item, dict):
            continue
        packages.append(
            RegistryPackage(
                package_id=item.get("id") if isinstance(item.get("id"), str) else "",
                path=item.get("path") if isinstance(item.get("path"), str) else "",
                proof_path=item.get("proof_path") if isinstance(item.get("proof_path"), str) else "",
                report_path=item.get("report_path") if isinstance(item.get("report_path"), str) else "",
                status=item.get("status") if isinstance(item.get("status"), str) else "",
                depends_on=item.get("depends_on") if isinstance(item.get("depends_on"), list) else [],
            )
        )
    return Registry(
        path=tasks_resolved,
        root=root,
        code_root=source_root,
        data=data,
        feature=feature,
        authoritative_slices=[path for path in authoritative_slices if isinstance(path, str)],
        packages=packages,
    )


ACCEPTANCE_ID_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*)\s*:")
ACCEPTANCE_PLACEHOLDER_LEADING_RE = re.compile(
    r"^(?:todo|tbd|to(?:[\s_-]+)be(?:[\s_-]+)determined)\b",
    flags=re.IGNORECASE,
)


def acceptance_item_id(item: str) -> str | None:
    match = ACCEPTANCE_ID_RE.match(item.strip())
    return match.group(1) if match else None


def is_manual_approved_item(item: str) -> bool:
    return re.search(r"(?i)\bmanual\s*\(approved\)", item) is not None


def is_executable_acceptance_item(item: str) -> bool:
    check_match = re.search(r"(?i)\bcheck\s*:", item)
    if check_match is None:
        return False
    payload = item[check_match.end():].strip()
    payload = re.split(
        r"(?:^|\s+)(?:—|–)\s*(?:expected|verify)\s*:",
        payload,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0].strip()
    if is_placeholder_text(payload):
        return False
    if re.match(r"(?i)manual\s*\(approved\)", payload):
        return False
    return True


def validate_acceptance_items(items: list[str], label: str, *, require_executable: bool = False) -> list[str]:
    """Right-sized checks on a frozen Acceptance list: real IDs, unique, not placeholders,
    and each item names an executable check or an approved manual exception. It does not (and
    cannot) prove a check actually runs — the verifier/orchestrator owns that."""
    errors: list[str] = []
    seen: set[str] = set()
    executable = 0
    for index, item in enumerate(items, 1):
        text = item.strip()
        if is_placeholder_text(text):
            errors.append(f"{label}: item {index} is a placeholder ({text!r}); write a concrete acceptance check")
            continue
        id_match = ACCEPTANCE_ID_RE.match(text)
        if id_match is None:
            errors.append(f"{label}: item {index} must start with a stable ID like 'AC-1:' ({text!r})")
            continue
        item_id = id_match.group(1)
        if item_id in seen:
            errors.append(f"{label}: duplicate acceptance item ID {item_id!r}")
        seen.add(item_id)

        body = text[id_match.end():].strip()
        check_match = re.search(r"(?i)\bcheck\s*:", body)
        manual_match = re.search(r"(?i)\bmanual\s*\(approved\)", body)
        marker_starts = [match.start() for match in (check_match, manual_match) if match is not None]
        description = body[:min(marker_starts)].strip(" \t—–-:") if marker_starts else body
        if is_placeholder_text(description) or ACCEPTANCE_PLACEHOLDER_LEADING_RE.match(description):
            errors.append(f"{label}: item {item_id} requirement description is missing or placeholder")

        if check_match is None and manual_match is None:
            errors.append(
                f"{label}: item {item_id} must name an executable 'check:' or a 'manual (approved)' exception"
            )
        elif manual_match is not None and check_match is None:
            manual_description = body[manual_match.end():].strip()
            manual_description = re.sub(
                r"(?i)^(?:—|–|-)?\s*verify\s*:", "", manual_description
            ).strip(" \t—–-:")
            if is_placeholder_text(manual_description):
                errors.append(
                    f"{label}: item {item_id} 'manual (approved)' exception must include a non-empty description"
                )
        elif check_match is not None:
            check_payload = body[check_match.end():].strip()
            check_payload = re.split(
                r"(?:^|\s+)(?:—|–)\s*(?:expected|verify)\s*:",
                check_payload,
                maxsplit=1,
                flags=re.IGNORECASE,
            )[0].strip()
            if is_placeholder_text(check_payload):
                errors.append(f"{label}: item {item_id} must include a non-empty 'check:' payload")
            elif re.match(r"(?i)manual\s*\(approved\)", check_payload):
                manual_description = re.sub(
                    r"(?i)^manual\s*\(approved\)\s*", "", check_payload
                ).strip(" \t—–-:")
                if is_placeholder_text(manual_description) and not re.search(r"(?i)\bverify\s*:", body):
                    errors.append(
                        f"{label}: item {item_id} 'manual (approved)' exception must include a non-empty description"
                    )
            else:
                executable += 1
    if require_executable and executable == 0 and not errors:
        errors.append(f"{label}: must include at least one independently confirmable executable check")
    elif require_executable and executable == 0:
        errors.append(f"{label}: must include at least one independently confirmable executable check")
    return errors


def validate_spec_acceptance(spec_path: Path) -> list[str]:
    try:
        text = read_text_file(spec_path, f"SPEC {spec_path}")
    except SliceproofError as exc:
        return exc.errors
    sections = split_h2_sections(text)
    if "Acceptance" not in sections:
        return [f"{spec_path}: missing required section ## Acceptance"]
    items = parse_bullets(sections["Acceptance"], unwrap_path=False)
    if not items:
        return [f"{spec_path}: ## Acceptance must list at least one feature-level acceptance item"]
    return validate_acceptance_items(items, f"{spec_path}: ## Acceptance", require_executable=False)


def validate_registry(registry: Registry) -> list[str]:
    data = registry.data
    errors: list[str] = []
    unknown_keys = sorted(set(data) - REGISTRY_KEYS - FORBIDDEN_REGISTRY_KEYS)
    for key in sorted(set(data) & FORBIDDEN_REGISTRY_KEYS):
        errors.append(f"tasks.json.{key}: not part of the lightweight registry")
    for key in unknown_keys:
        errors.append(f"tasks.json.{key}: unsupported registry field")
    for key in ("feature", "title", "status", "spec_path", "authoritative_slices", "work_packages"):
        if key not in data:
            errors.append(f"{key}: expected field in lightweight registry")

    if not registry.feature or not FEATURE_RE.fullmatch(registry.feature):
        errors.append("feature: expected lowercase slug with letters, digits, and hyphens")
    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        errors.append("title: expected non-empty string")
    status = data.get("status")
    if not isinstance(status, str) or status not in FEATURE_STATUS_VALUES:
        errors.append(f"status: expected one of {sorted(FEATURE_STATUS_VALUES)}")

    spec_path = data.get("spec_path")
    if not isinstance(spec_path, str) or not spec_path.strip():
        errors.append("spec_path: expected non-empty string")
    else:
        try:
            spec_resolved = resolve_safe_path(registry.root, spec_path, "spec_path", expected_suffix=".md", must_exist_file=True, root_label="artifact root")
        except SliceproofError as exc:
            errors.extend(exc.errors)
        else:
            errors.extend(validate_spec_acceptance(spec_resolved))

    authoritative = data.get("authoritative_slices")
    if not isinstance(authoritative, list):
        errors.append("authoritative_slices: expected array")
    else:
        seen_slices: set[str] = set()
        for index, path in enumerate(authoritative):
            if not isinstance(path, str) or not path.strip():
                errors.append(f"authoritative_slices[{index}]: expected non-empty string")
                continue
            if path in seen_slices:
                errors.append(f"authoritative_slices[{index}]: duplicate path {path!r}")
            seen_slices.add(path)
            try:
                resolve_safe_path(registry.root, path, f"authoritative_slices[{index}]", expected_suffix=".md", must_exist_file=True, root_label="artifact root")
            except SliceproofError as exc:
                errors.extend(exc.errors)

    packages_data = data.get("work_packages")
    if not isinstance(packages_data, list) or not packages_data:
        errors.append("work_packages: expected non-empty array")
        return errors

    seen_ids: set[str] = set()
    package_ids: set[str] = set()
    for index, item in enumerate(packages_data):
        prefix = f"work_packages[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: expected object")
            continue
        allowed = REGISTRY_PACKAGE_KEYS | LEGACY_PACKAGE_KEYS
        for key in sorted(set(item) - allowed):
            errors.append(f"{prefix}.{key}: unsupported package registry field")
        package_id = item.get("id")
        if not isinstance(package_id, str) or not PACKAGE_ID_RE.fullmatch(package_id):
            errors.append(f"{prefix}.id: expected WP<N> package id")
        else:
            if package_id in seen_ids:
                errors.append(f"work_packages: duplicate package id {package_id}")
            seen_ids.add(package_id)
            package_ids.add(package_id)
        path_suffixes = {"path": ".md", "report_path": ".package-verification.md"}
        for key, suffix in path_suffixes.items():
            path = item.get(key)
            if not isinstance(path, str) or not path.strip():
                errors.append(f"{prefix}.{key}: expected non-empty string")
                continue
            try:
                resolve_safe_path(
                    registry.root,
                    path,
                    f"{prefix}.{key}",
                    expected_suffix=suffix,
                    must_exist_file=key == "path",
                    root_label="artifact root",
                )
            except SliceproofError as exc:
                errors.extend(exc.errors)
        proof_path = item.get("proof_path")
        if proof_path is not None:
            if not isinstance(proof_path, str) or not proof_path.strip():
                errors.append(f"{prefix}.proof_path: expected non-empty string when declared")
            else:
                try:
                    resolve_safe_path(
                        registry.root,
                        proof_path,
                        f"{prefix}.proof_path",
                        expected_suffix=".proof.md",
                        root_label="artifact root",
                    )
                except SliceproofError as exc:
                    errors.extend(exc.errors)
        status = item.get("status")
        if not isinstance(status, str) or status not in STATUS_VALUES:
            errors.append(f"{prefix}.status: expected one of {sorted(STATUS_VALUES)}")
        depends_on = item.get("depends_on")
        if not isinstance(depends_on, list):
            errors.append(f"{prefix}.depends_on: expected array")
        else:
            seen_deps: set[str] = set()
            for dep_index, dependency in enumerate(depends_on):
                if not isinstance(dependency, str) or not PACKAGE_ID_RE.fullmatch(dependency):
                    errors.append(f"{prefix}.depends_on[{dep_index}]: expected WP<N> package id")
                    continue
                if dependency == package_id:
                    errors.append(f"{prefix}.depends_on[{dep_index}]: package cannot depend on itself")
                if dependency in seen_deps:
                    errors.append(f"{prefix}.depends_on[{dep_index}]: duplicate dependency {dependency}")
                seen_deps.add(dependency)
    for index, item in enumerate(packages_data):
        if not isinstance(item, dict) or not isinstance(item.get("depends_on"), list):
            continue
        for dependency in item["depends_on"]:
            if isinstance(dependency, str) and PACKAGE_ID_RE.fullmatch(dependency) and dependency not in package_ids:
                errors.append(f"work_packages[{index}].depends_on: unknown package id {dependency}")
    errors.extend(validate_dependency_cycles(packages_data))
    return errors


def validate_dependency_cycles(packages_data: list[Any]) -> list[str]:
    graph: dict[str, list[str]] = {}
    for item in packages_data:
        if isinstance(item, dict) and isinstance(item.get("id"), str) and isinstance(item.get("depends_on"), list):
            graph[item["id"]] = [dep for dep in item["depends_on"] if isinstance(dep, str)]
    errors: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(package_id: str, stack: list[str]) -> None:
        if package_id in visiting:
            cycle_start = stack.index(package_id) if package_id in stack else 0
            cycle = stack[cycle_start:] + [package_id]
            errors.append(f"work_packages.depends_on: dependency cycle detected: {' -> '.join(cycle)}")
            return
        if package_id in visited:
            return
        visiting.add(package_id)
        for dependency in graph.get(package_id, []):
            if dependency in graph:
                visit(dependency, [*stack, dependency])
        visiting.remove(package_id)
        visited.add(package_id)

    for package_id in sorted(graph):
        visit(package_id, [package_id])
    return errors


def parse_package_markdown(path: Path, package_id: str) -> PackageMarkdown:
    text = read_text_file(path, f"package Markdown {path}")
    errors: list[str] = []
    title = package_id
    h1_match = re.search(r"^#\s+Work Package:\s+(WP[1-9]\d*)\s*(?:—|-)?\s*(.*?)\s*$", text, flags=re.MULTILINE)
    if h1_match:
        found_id = h1_match.group(1)
        if found_id != package_id:
            errors.append(f"{path}: H1 package id {found_id!r} does not match registry id {package_id!r}")
        title = h1_match.group(2).strip() or found_id
    else:
        errors.append(f"{path}: expected H1 '# Work Package: {package_id} — <title>'")

    sections = split_h2_sections(text)
    for section in sorted(REQUIRED_PACKAGE_SECTIONS):
        if section not in sections:
            errors.append(f"{path}: missing required section ## {section}")

    if errors:
        raise SliceproofError(errors)

    scope = sections["Scope"].strip()
    if not scope:
        errors.append(f"{path}: ## Scope must be non-empty")
    slice_refs = parse_assigned_slices(sections["Assigned Slices"])
    primary_paths = parse_bullets(sections["Primary Paths"], unwrap_path=True)
    verification_expectations = parse_bullets(sections["Verification Expectations"], unwrap_path=False)
    acceptance_checklist = parse_bullets(sections["Acceptance Checklist"], unwrap_path=False)
    report_paths = parse_bullets(sections["Package Verification Report"], unwrap_path=True)
    dependencies = parse_dependencies(sections["Dependencies"])

    if not primary_paths:
        errors.append(f"{path}: ## Primary Paths must list at least one path")
    if not verification_expectations:
        errors.append(f"{path}: ## Verification Expectations must list at least one expectation")
    if not acceptance_checklist:
        errors.append(f"{path}: ## Acceptance Checklist must list at least one checklist item")
    else:
        errors.extend(
            validate_acceptance_items(
                acceptance_checklist,
                f"{path}: ## Acceptance Checklist",
                require_executable=True,
            )
        )
    if len(report_paths) != 1:
        errors.append(f"{path}: ## Package Verification Report must list exactly one report path")
    if errors:
        raise SliceproofError(errors)
    return PackageMarkdown(
        package_id=package_id,
        title=title,
        scope=scope,
        slice_refs=slice_refs,
        primary_paths=primary_paths,
        verification_expectations=verification_expectations,
        acceptance_checklist=acceptance_checklist,
        report_path=report_paths[0],
        dependencies=dependencies,
    )


def validate_package_markdown(registry: Registry, package: RegistryPackage, package_md: PackageMarkdown) -> list[str]:
    errors: list[str] = []
    if package_md.report_path != package.report_path:
        errors.append(
            f"{package.path}: ## Package Verification Report path {package_md.report_path!r} does not match registry report_path {package.report_path!r}"
        )
    if package_md.dependencies != package.depends_on:
        errors.append(f"{package.path}: ## Dependencies {package_md.dependencies!r} do not match registry depends_on {package.depends_on!r}")

    authoritative = set(registry.authoritative_slices)
    if authoritative and not package_md.slice_refs:
        errors.append(f"{package.path}: ## Assigned Slices must list at least one Slice when authoritative_slices is non-empty")
    if not authoritative and package_md.slice_refs:
        errors.append(f"{package.path}: assigned Slice references require authoritative_slices registry entries")

    try:
        resolve_safe_path(
            registry.root,
            package_md.report_path,
            f"{package.path}: report path",
            expected_suffix=".package-verification.md",
            root_label="artifact root",
        )
    except SliceproofError as exc:
        errors.extend(exc.errors)
    for path in package_md.primary_paths:
        try:
            resolve_safe_path(registry.code_root, path, f"{package.path}: primary path {path!r}", root_label="code root")
        except SliceproofError as exc:
            errors.extend(exc.errors)

    slice_titles_cache: dict[str, dict[str, str]] = {}
    seen_required_ids: set[str] = set()
    for ref in package_md.slice_refs:
        try:
            resolved = resolve_safe_path(
                registry.root,
                ref.path,
                f"{package.path}: assigned Slice {ref.path!r}",
                expected_suffix=".md",
                must_exist_file=True,
                root_label="artifact root",
            )
        except SliceproofError as exc:
            errors.extend(exc.errors)
            continue
        if ref.path not in authoritative:
            errors.append(f"{package.path}: assigned Slice {ref.path!r} is not listed in authoritative_slices")
        slice_titles_cache[ref.path] = extract_slice_h3_titles(resolved)
        if not ref.must_satisfy and not ref.context_only:
            errors.append(f"{package.path}: assigned Slice {ref.path!r} has no must_satisfy or context_only IDs")
        overlap = set(ref.must_satisfy) & set(ref.context_only)
        for slice_id in sorted(overlap):
            errors.append(f"{package.path}: Slice ID {slice_id!r} cannot be both must_satisfy and context_only")
        for kind, ids in (("must_satisfy", ref.must_satisfy), ("context_only", ref.context_only)):
            seen: set[str] = set()
            for slice_id in ids:
                if not SLICE_ID_RE.fullmatch(slice_id):
                    errors.append(f"{package.path}: {kind} ID {slice_id!r} has unsupported shape")
                    continue
                if slice_id in seen:
                    errors.append(f"{package.path}: duplicate {kind} ID {slice_id!r} for Slice {ref.path!r}")
                seen.add(slice_id)
                if kind == "must_satisfy":
                    if slice_id in seen_required_ids:
                        errors.append(f"{package.path}: duplicate required Slice ID {slice_id!r} across assignment")
                    seen_required_ids.add(slice_id)
                if slice_id not in slice_titles_cache[ref.path]:
                    errors.append(
                        f"{package.path}: {kind} assigned H3 '{slice_id}' not found in Slice '{ref.path}' (not found as H3)"
                    )
    return errors


def parse_assigned_slices(body: str) -> list[SliceRef]:
    refs: list[SliceRef] = []
    current_path: str | None = None
    current_must: list[str] = []
    current_context: list[str] = []
    mode: str | None = None
    in_fence = False

    def flush() -> None:
        nonlocal current_path, current_must, current_context
        if current_path is not None:
            refs.append(SliceRef(current_path, current_must, current_context))
        current_path = None
        current_must = []
        current_context = []

    for raw_line in body.splitlines():
        line = raw_line.strip()
        if is_fence(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.startswith("### "):
            flush()
            current_path = extract_backticked_or_text(line[4:].strip())
            mode = None
            continue
        if re.fullmatch(r"Must satisfy\s*:", line, flags=re.IGNORECASE):
            mode = "must"
            continue
        if re.fullmatch(r"Context only\s*:", line, flags=re.IGNORECASE):
            mode = "context"
            continue
        bullet_match = re.match(r"^[-*](?:\s+(.*))?$", line)
        if bullet_match and mode and current_path:
            item = (bullet_match.group(1) or "").strip()
            slice_id = extract_assigned_slice_id_token(item)
            if mode == "must":
                current_must.append(slice_id)
            else:
                current_context.append(slice_id)
    flush()
    return refs


def parse_dependencies(body: str) -> list[str]:
    if re.search(r"^\s*(?:-|\*)?\s*None\.\s*$", body, flags=re.IGNORECASE | re.MULTILINE):
        return []
    dependencies: list[str] = []
    for item in parse_bullets(body, unwrap_path=False):
        dependency = extract_work_package_id(item) or item.strip("`")
        if dependency:
            dependencies.append(dependency)
    return dependencies


def parse_bullets(body: str, *, unwrap_path: bool) -> list[str]:
    values: list[str] = []
    in_fence = False
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if is_fence(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.startswith(("- ", "* ")):
            item = line[2:].strip()
            values.append(extract_backticked_or_text(item) if unwrap_path else item)
        elif re.match(r"^\d+\.\s+", line):
            item = re.sub(r"^\d+\.\s+", "", line).strip()
            values.append(extract_backticked_or_text(item) if unwrap_path else item)
    return [value for value in values if value]


def iter_markdown_lines(text: str) -> Iterator[tuple[str, str, bool]]:
    """Yield ``(raw_line, visible_line, fenced)`` for Markdown that may contain HTML comments.

    ``visible_line`` has comments removed while keeping the line count, so a comment spanning two lines cannot
    splice them together. A fence counts only when both texts show one: a marker written inside a comment renders
    as nothing, and a marker that appears only once a comment is removed was never written. Reading a fence that
    is not really there silently swallows everything after it, so both callers share this one implementation.
    """
    visible_text = HTML_COMMENT_RE.sub(lambda match: "\n" * match.group(0).count("\n"), text)
    active_fence: tuple[str, int] | None = None
    for raw_line, visible_line in zip(text.splitlines(), visible_text.splitlines()):
        was_in_fence = active_fence is not None
        next_fence, is_fence_marker = advance_markdown_fence(raw_line, active_fence)
        if is_fence_marker and not advance_markdown_fence(visible_line, active_fence)[1]:
            next_fence, is_fence_marker = active_fence, False
        active_fence = next_fence
        yield raw_line, visible_line, was_in_fence or is_fence_marker


def split_h2_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for raw_line, visible_line, fenced in iter_markdown_lines(text):
        line = raw_line.rstrip("\n")
        if fenced:
            if current is not None:
                sections[current].append(line)
            continue
        # A section heading must be wholly visible. Reading raw headings from inside or partly inside an HTML
        # comment lets invisible required sections satisfy report validation.
        if raw_line == visible_line and line.startswith("## ") and not line.startswith("### "):
            current = line[3:].strip()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    # Remove section-separator newlines only. Leading spaces and tabs are report grammar,
    # so callers that validate physical lines must receive them unchanged.
    return {name: "\n".join(lines).strip("\n") for name, lines in sections.items()}


def extract_slice_h3_titles(path: Path) -> dict[str, str]:
    titles: dict[str, str] = {}
    in_fence = False
    in_shared_understanding = False
    for raw_line in read_text_file(path, f"Slice {path}").splitlines():
        line = raw_line.strip()
        if is_fence(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if raw_line.startswith("## ") and not raw_line.startswith("### "):
            in_shared_understanding = raw_line[3:].strip().lower() == "shared understanding"
            continue
        if not in_shared_understanding:
            continue
        match = H3_ID_RE.match(raw_line)
        if match:
            titles[match.group(1)] = (match.group(2) or "").strip()
    return titles


def strip_fenced_blocks(text: str) -> str:
    """Drop fenced code blocks so example Markdown cannot be read as a real declaration."""
    unfenced_lines: list[str] = []
    active_fence: tuple[str, int] | None = None
    for line in text.splitlines():
        was_in_fence = active_fence is not None
        active_fence, is_fence_marker = advance_markdown_fence(line, active_fence)
        if not was_in_fence and not is_fence_marker:
            unfenced_lines.append(line)
    return "\n".join(unfenced_lines)


def report_verdicts(text: str) -> list[str]:
    unfenced_text = strip_fenced_blocks(text)
    return [
        match.group(1).upper()
        for match in re.finditer(r"(?im)^#{2,4}\s*Verdict\s*$\s*\n+\s*([A-Za-z_]+)", unfenced_text)
    ]


def parse_report_checklist_results(section_body: str) -> dict[str, tuple[str, str]]:
    """Accept either a Markdown table (Item|Result|Evidence) or a bullet list
    (`- AC-1: pass — evidence: ...`). Lenient on shape; strict only on the outcome."""
    results: dict[str, tuple[str, str]] = {}
    for row in parse_table(section_body):
        item_cell = extract_backticked_or_text(row.cells.get("Item", "").strip())
        item_id = acceptance_item_id(item_cell) or item_cell
        if item_id and item_id not in results:
            evidence = row.cells.get("Evidence", "").strip() or row.cells.get("Pointer", "").strip()
            results[item_id] = (row.cells.get("Result", "").strip(), evidence)
    for bullet in parse_bullets(section_body, unwrap_path=False):
        item_id = acceptance_item_id(bullet)
        if not item_id or item_id in results:
            continue
        rest = bullet[bullet.index(":") + 1:].strip()
        match = re.match(r"(?i)(pass|fail)\b(.*)", rest)
        if match:
            results[item_id] = (match.group(1), match.group(2).strip(" \u2014-:"))
        else:
            results[item_id] = (rest, "")
    return results


def extract_pointer_text(evidence: str) -> str:
    cleaned = re.sub(r"(?i)^(?:evidence|pointer|observed)\s*:\s*", "", evidence).strip(" \t—–-")
    if not cleaned:
        return ""
    backticked = re.search(r"`([^`]+)`", cleaned)
    if backticked:
        return backticked.group(1).strip()
    first = re.split(r"\s+[—–-]\s+|\s+\((?:exit|status|observed)\b", cleaned, maxsplit=1)[0]
    return first.strip()


def is_test_id_pointer(value: str) -> bool:
    return bool(TEST_ID_RE.search(value.strip()))


def is_command_invocation(value: str) -> bool:
    text = value.strip().strip("`")
    if not text:
        return False
    if is_test_id_pointer(text):
        return False
    if COMMAND_INVOCATION_RE.search(text):
        return True
    return bool(re.search(r"\s", text)) and not looks_like_relative_path(text)


def looks_like_relative_path(value: str) -> bool:
    text = value.strip().strip("`")
    if not text or "\\" in text or "\x00" in text:
        return False
    if text.startswith(("/", "~")) or ":" in text.split("/", 1)[0]:
        return False
    return "/" in text or bool(FILE_SUFFIX_RE.search(Path(text).name))


def looks_like_path_pointer(value: str) -> bool:
    text = value.strip().strip("`")
    if not text or is_test_id_pointer(text) or is_command_invocation(text):
        return False
    if text.startswith(("/", "~")) or "\\" in text:
        return True
    return looks_like_relative_path(text)


def pointer_root_for(registry: Registry, pointer: str) -> tuple[Path, str]:
    if pointer.startswith((".tasks/", ".planning/")):
        return registry.root, "artifact root"
    return registry.code_root, "code root"


def resolve_result_pointer(registry: Registry, pointer: str, label: str) -> None:
    root, root_label = pointer_root_for(registry, pointer)
    reject_existing_symlink_at_unresolved_path(
        root,
        pointer,
        label,
        error_message=f"{label}: refusing symlink-escaped pointer: {pointer}",
    )
    resolve_safe_path(root, pointer, label, must_exist_file=True, root_label=root_label)


def validate_plan_gaps_section(report_path: Path, plan_gaps_body: str) -> list[str]:
    """Validate the strict flat physical-line grammar and require closed entries."""
    lines = [raw_line.rstrip() for raw_line in plan_gaps_body.splitlines() if raw_line.rstrip()]
    if lines == ["- none"]:
        return []
    if not lines or any(
        not line.startswith(PLAN_GAP_PREFIX)
        or (
            line[len(PLAN_GAP_PREFIX) : len(PLAN_GAP_PREFIX) + 1]
            and line[len(PLAN_GAP_PREFIX)] not in " \t—–-:;,.!?([{"
        )
        or "<!--" in line
        or "-->" in line
        or "```" in line
        or "~~~" in line
        for line in lines
    ):
        return [
            f"{report_path}: ## Plan gaps must contain sole exact `- none` or one or more column-zero, "
            f"single-line entries beginning exactly `{PLAN_GAP_PREFIX}`; blank separator lines and trailing "
            f"whitespace are allowed, but every other physical line is noncanonical."
        ]

    errors: list[str] = []
    for entry in lines:
        if has_plan_gap_closure(entry) or has_approval_provenance_scope(entry):
            continue
        errors.append(
            f"{report_path}: ## Plan gaps entry is still open; close it on the same physical line with a "
            f"substantive 'closed:' note, or with non-placeholder approval, provenance, and scope: {entry}"
        )
    return errors


def validate_gaps_section(report_path: Path, gaps_body: str) -> list[str]:
    if is_empty_gaps_deviations_section(gaps_body):
        return []
    if UNRESOLVED_MARKER_RE.search(gaps_body):
        return [f"{report_path}: ## Gaps contains unresolved TODO/OPEN marker"]
    if not has_approval_provenance_scope(gaps_body):
        return [f"{report_path}: ## Gaps must be none or carry approval, provenance, and scope"]
    return []


def validate_report_markdown(
    report_path: Path,
    package: RegistryPackage,
    package_md: PackageMarkdown,
    registry: Registry,
) -> ReportValidationResult:
    """Confirm the result file records checklist coverage and cheap pointers.

    The helper is not authenticity: it checks presence, non-placeholder text, and
    safe path existence when a pointer looks like a path. It does not run tests
    or judge semantic done.
    """
    if not report_path.is_file():
        return ReportValidationResult([f"report: file not found: {report_path}"], [])
    text = read_text_file(report_path, f"package verification report {report_path}")
    errors: list[str] = []
    if not text.strip():
        errors.append(f"{report_path}: package verification report must be non-empty")
        return ReportValidationResult(errors, [])

    verdicts = report_verdicts(text)
    if len(verdicts) != 1:
        errors.append(
            f"{report_path}: report must contain exactly one canonical Verdict heading/value "
            f"(found {len(verdicts)})"
        )
    elif verdicts[0] != "PASS":
        errors.append(f"{report_path}: report Verdict must be PASS (found {verdicts[0]})")

    sections = split_h2_sections(text)
    for section in sorted(REQUIRED_REPORT_SECTIONS):
        if section not in sections:
            errors.append(f"{report_path}: missing ## {section} section")

    blocking_body = sections.get("Blocking findings")
    if blocking_body is not None:
        open_blockers = [b for b in parse_bullets(blocking_body, unwrap_path=False) if b.strip().lower() != "none"]
        if open_blockers:
            errors.append(f"{report_path}: report has open blocking findings: {open_blockers}")

    gaps_body = sections.get("Gaps")
    if gaps_body is not None:
        errors.extend(validate_gaps_section(report_path, gaps_body))

    result_body = sections.get("Acceptance Checklist Result")
    if result_body is not None:
        results = parse_report_checklist_results(result_body)
        for item in package_md.acceptance_checklist:
            item_id = acceptance_item_id(item)
            if item_id is None:
                continue
            if item_id not in results:
                errors.append(f"{report_path}: Acceptance Checklist Result is missing frozen item {item_id}")
                continue
            result_value, evidence = results[item_id]
            if result_value.lower() != "pass":
                errors.append(f"{report_path}: checklist item {item_id} result must be pass (found {result_value!r})")
                continue
            pointer = extract_pointer_text(evidence)
            if is_placeholder_text(evidence) or is_placeholder_text(pointer):
                errors.append(f"{report_path}: checklist item {item_id} is marked pass without evidence")
                continue
            if looks_like_path_pointer(pointer):
                try:
                    resolve_result_pointer(registry, pointer, f"{report_path}: checklist item {item_id} pointer")
                except SliceproofError as exc:
                    errors.extend(exc.errors)

    reviewed_body = sections.get("Reviewed state")
    if reviewed_body is not None and not reviewed_body.strip():
        errors.append(f"{report_path}: missing or empty ## Reviewed state section")
    elif "Reviewed state" not in sections:
        pass

    # An open plan gap is a completion blocker, not a note: the package is not done until it is routed through
    # planning continuation and closed. It is an error rather than an advisory so this command's success signal
    # cannot say "structurally complete" while a known obligation is missing.
    #
    # Closure must never mean erasure. An entry closes in place by recording how it closed, so the audit trail of
    # the omitted requirement survives into the report. The section is required and its dispositions are bullets,
    # so the cheapest escape is writing `- none` -- a falsehood an auditor can read -- not an invisible deletion.
    plan_gaps_body = sections.get("Plan gaps")
    if plan_gaps_body is not None:  # absence is already reported by the required-section check above
        errors.extend(validate_plan_gaps_section(report_path, plan_gaps_body))

    return ReportValidationResult(errors, [])


def parse_table(body: str) -> list[ProofRow]:
    rows: list[tuple[list[str], str]] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        cells = split_markdown_table_row(line)
        if cells is None:
            continue
        if cells and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells):
            continue
        rows.append((cells, raw_line))
    if len(rows) < 2:
        return []
    headers = rows[0][0]
    proof_rows: list[ProofRow] = []
    for cells, raw_line in rows[1:]:
        mapped = {header: cells[index] if index < len(cells) else "" for index, header in enumerate(headers)}
        proof_rows.append(ProofRow(mapped, raw_line))
    return proof_rows


def split_markdown_table_row(line: str) -> list[str] | None:
    if not line.startswith("|") or not line.endswith("|"):
        return None
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for char in line[1:-1]:
        if escaped:
            if char == "|":
                current.append("|")
            else:
                current.append("\\")
                current.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if escaped:
        current.append("\\")
    cells.append("".join(current).strip())
    return cells


def resolve_cli_root(value: Path | None, cwd: Path, label: str) -> Path:
    candidate = cwd if value is None else value if value.is_absolute() else cwd / value
    resolved = candidate.resolve(strict=False)
    if not resolved.is_dir():
        display = str(value) if value is not None else str(cwd)
        raise SliceproofError([f"{label}: directory not found: {display}"])
    return resolved


def resolve_tasks_argument(root: Path, value: Path, *, root_label: str = "root") -> Path:
    candidate = value if value.is_absolute() else root / value
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError:
        raise SliceproofError([f"tasks.json: path escapes {root_label}: {value}"])
    return resolved


def repo_relative_path(value: str, label: str, *, expected_suffix: str | None = None) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise SliceproofError([f"{label}: expected non-empty repo-relative path"])
    if "\x00" in value or "\\" in value:
        raise SliceproofError([f"{label}: path must use safe repo-relative POSIX syntax"])
    path = Path(value)
    if path.is_absolute() or value.startswith("~") or ":" in value:
        raise SliceproofError([f"{label}: path must be repo-relative, not absolute/home/drive-qualified"])
    if any(part in {"", ".", ".."} for part in path.parts):
        raise SliceproofError([f"{label}: path must not contain empty, '.', or '..' segments"])
    if expected_suffix is not None and not value.endswith(expected_suffix):
        raise SliceproofError([f"{label}: path must end with {expected_suffix}"])
    return path


def unresolved_safe_path(root: Path, value: str, label: str, *, expected_suffix: str | None = None) -> Path:
    return root / repo_relative_path(value, label, expected_suffix=expected_suffix)


def reject_existing_symlink_at_unresolved_path(
    root: Path,
    value: str,
    label: str,
    *,
    expected_suffix: str | None = None,
    error_message: str | None = None,
) -> None:
    unresolved = unresolved_safe_path(root, value, label, expected_suffix=expected_suffix)
    try:
        is_symlink = unresolved.is_symlink()
    except OSError as exc:
        raise SliceproofError([f"{label}: unable to inspect unresolved path {value}: {exc}"])
    if is_symlink:
        raise SliceproofError([error_message or f"{label}: existing path is a symlink: {value}"])


def resolve_safe_path(
    root: Path,
    value: str,
    label: str,
    *,
    expected_suffix: str | None = None,
    must_exist_file: bool = False,
    root_label: str = "root",
) -> Path:
    path = repo_relative_path(value, label, expected_suffix=expected_suffix)
    resolved = (root / path).resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError:
        raise SliceproofError([f"{label}: path escapes {root_label}"])
    if must_exist_file and not resolved.is_file():
        raise SliceproofError([f"{label}: file not found: {value}"])
    return resolved


def require_package(registry: Registry, package_id: str) -> RegistryPackage:
    if not PACKAGE_ID_RE.fullmatch(package_id):
        raise SliceproofError([f"--package: expected WP<N> package id, got {package_id!r}"])
    package = registry.package(package_id)
    if package is None:
        raise SliceproofError([f"--package: unknown package id {package_id}"])
    return package


def read_text_file(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SliceproofError([f"{label}: file not found: {path}"])
    except UnicodeError as exc:
        raise SliceproofError([f"{label}: unable to decode UTF-8 text from {path}: {exc}"])
    except OSError as exc:
        raise SliceproofError([f"{label}: unable to read {path}: {exc}"])


def extract_backticked_or_text(value: str) -> str:
    match = re.search(r"`([^`]+)`", value)
    if match:
        return match.group(1).strip()
    return re.split(r"\s+(?:—|-)\s+", value, maxsplit=1)[0].strip()


def extract_assigned_slice_id_token(value: str) -> str:
    backticked = re.search(r"`([^`]*)`", value)
    if backticked:
        return backticked.group(1).strip()
    return extract_backticked_or_text(value)


def extract_work_package_id(value: str) -> str | None:
    backticked = re.search(r"`(WP[1-9]\d*)`", value)
    if backticked:
        return backticked.group(1)
    plain = re.search(r"\b(WP[1-9]\d*)\b", value)
    return plain.group(1) if plain else None


def clean_cell_id(value: str) -> str:
    return value.strip().strip("`")


def normalize_status(value: str) -> str:
    return value.strip().strip("`").upper()


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().strip("`"))


def is_placeholder_text(value: str) -> bool:
    stripped = normalize_text(value).lower().strip("-* \t")
    if stripped in PLACEHOLDER_VALUES:
        return True
    return bool(BLOCKING_MARKER_RE.fullmatch(stripped))


def is_empty_gaps_deviations_section(value: str) -> bool:
    for line in value.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if not re.fullmatch(r"(?:[-*+]\s+|\d+[.)]\s+)?None\.?", stripped, flags=re.IGNORECASE):
            return False
    return True


def has_plan_gap_closure(value: str) -> bool:
    """True when a plan-gap entry records a substantive ``closed:`` route.

    Closure text is free prose and is taken as written: describing a gap accurately must never cost anything.
    Only a closure that says nothing is rejected. The unresolved-marker scan is deliberately scoped to the
    closure value, so a gap whose *description* names "the open-file limit" or "the TODO scanner" stays closable.
    """
    closures = [match.group("value") for match in PLAN_GAP_CLOSURE_RE.finditer(value)]
    return bool(closures) and all(is_substantive_closure(closure) for closure in closures)


def is_substantive_closure(value: str) -> bool:
    # Text that renders nothing records nothing, so a comment or zero-width run is dropped before the value is
    # weighed. This is scoped to the closure rather than folded into the shared normalizer, where removing an
    # invisible separator would instead *hide* a placeholder word from the approval detector.
    visible = INVISIBLE_CHAR_RE.sub("", HTML_COMMENT_RE.sub("", value))
    # normalize_approval_placeholder_value is reused for case/punctuation folding only; the approval placeholder
    # detector itself is not applied here, because it searches free text for words a real closure may contain.
    normalized = normalize_approval_placeholder_value(visible)
    if not normalized or normalized in CONTENTLESS_CLOSURE_VALUES:
        return False
    return UNRESOLVED_MARKER_RE.search(value) is None


def has_approval_provenance_scope(value: str) -> bool:
    return (
        has_positive_approval(value)
        and has_non_placeholder_metadata(value, "provenance")
        and has_non_placeholder_metadata(value, "scope")
    )


def has_positive_approval(value: str) -> bool:
    if NEGATED_APPROVAL_RE.search(value):
        return False
    approval_sources = [match.group("source") for match in APPROVAL_SOURCE_RE.finditer(value)]
    approval_sources.extend(match.group("source") for match in USER_APPROVED_SOURCE_RE.finditer(value))
    return bool(approval_sources) and all(
        not is_approval_placeholder_value(source) for source in approval_sources
    )


def has_non_placeholder_metadata(value: str, field: str) -> bool:
    metadata_values = [
        match.group("value")
        for match in APPROVAL_METADATA_VALUE_RE.finditer(value)
        if match.group("field").lower() == field
    ]
    return bool(metadata_values) and all(not is_approval_placeholder_value(metadata) for metadata in metadata_values)


def is_approval_placeholder_value(value: str) -> bool:
    normalized = normalize_approval_placeholder_value(value)
    return not normalized or APPROVAL_PLACEHOLDER_TOKEN_RE.search(normalized) is not None


def normalize_approval_placeholder_value(value: str) -> str:
    normalized = normalize_text(value).strip(" -*`'\".:?!").lower()
    return re.sub(r"[\s_-]+", " ", normalized)


def advance_markdown_fence(
    line: str, active_fence: tuple[str, int] | None
) -> tuple[tuple[str, int] | None, bool]:
    match = re.match(r"^(`{3,}|~{3,})(.*)$", line.strip())
    if match is None:
        return active_fence, False

    marker, suffix = match.groups()
    if active_fence is None:
        return (marker[0], len(marker)), True

    delimiter, opening_length = active_fence
    if marker[0] == delimiter and len(marker) >= opening_length and not suffix.strip():
        return None, True
    return active_fence, False


def is_fence(line: str) -> bool:
    return line.startswith("```") or line.startswith("~~~")


def write_json(stream: Any, data: dict[str, Any]) -> None:
    json.dump(data, stream, indent=2, sort_keys=True)
    stream.write("\n")


if __name__ == "__main__":
    raise SystemExit(main())
