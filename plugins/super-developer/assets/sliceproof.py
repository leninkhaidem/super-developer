#!/usr/bin/env python3
"""Mechanical helper for Slice-first planned-feature artifacts.

The helper performs deterministic structure, path-safety, proof-closure, and
report-binding checks. It does not judge semantic proof quality, run tests,
mutate package status, write review readiness, or replace review/audit gates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

FEATURE_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
PACKAGE_ID_RE = re.compile(r"^WP[1-9]\d*$")
SLICE_ID_RE = re.compile(r"^[A-Z][A-Z0-9-]*-[0-9]{3}$")
H3_ID_RE = re.compile(r"^\s*###\s+`?([A-Z][A-Z0-9-]*-[0-9]{3})`?(?:\s+(?:—|-)\s*(.*?))?\s*$")
COMMIT_RE = re.compile(r"^[0-9a-fA-F]{7,64}$")
STATUS_VALUES = {"pending", "in_progress", "done", "blocked"}
FEATURE_STATUS_VALUES = {"planned", "reviewed", "in_progress", "completed", "blocked", "on_hold"}
REGISTRY_KEYS = {"feature", "title", "status", "spec_path", "authoritative_slices", "work_packages"}
REGISTRY_PACKAGE_KEYS = {"id", "path", "proof_path", "report_path", "status", "depends_on"}
REQUIRED_PACKAGE_SECTIONS = {
    "Scope",
    "Assigned Slices",
    "Primary Paths",
    "Verification Expectations",
    "Proof",
    "Package Verification Report",
    "Dependencies",
}
REQUIRED_PROOF_SECTIONS = {
    "Package Scope",
    "Assigned Slice Scope",
    "Slice Closure Table",
    "Acceptance / Verification Closure",
    "Commands Run",
    "Files Changed / Inspected",
    "Gaps, Deviations, or Deferred Items",
    "Package Agent Completion Statement",
}
REQUIRED_REPORT_SECTIONS = {"State Binding", "Verification Result", "Checks", "Open Findings"}
PROOF_STATUS_VALUES = {"PASS", "GAP", "DEFERRED", "N/A", "OPEN"}
PASS_REPORT_VALUES = {"passed", "pass", "verified"}
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


class SliceproofError(Exception):
    def __init__(self, errors: list[str]) -> None:
        super().__init__("\n".join(errors))
        self.errors = errors


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
    proof_path: str
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


@dataclass(frozen=True)
class Registry:
    path: Path
    root: Path
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
    proof_path: Path
    report_path: Path


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except SliceproofError as exc:
        write_json(sys.stderr, {"ok": False, "command": args.command, "errors": exc.errors})
        return 1
    except (OSError, UnicodeError) as exc:
        write_json(sys.stderr, {"ok": False, "command": args.command, "errors": [f"{args.command}: I/O error: {exc}"]})
        return 1
    write_json(sys.stdout, {"ok": True, "command": args.command, **result})
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Mechanical Slice-first planned-feature helper. Validation commands are read-only; "
            "create-proof only writes the declared package proof Markdown placeholder."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_plan = subparsers.add_parser(
        "validate-plan",
        help="Validate a lightweight registry plus package Markdown and Slice H3 references.",
    )
    validate_plan.add_argument("tasks", type=Path, help="Path to .tasks/<feature>/tasks.json.")
    validate_plan.set_defaults(func=cmd_validate_plan)

    create_proof = subparsers.add_parser(
        "create-proof",
        help="Create a package proof Markdown placeholder from work-package Markdown.",
    )
    create_proof.add_argument("tasks", type=Path, help="Path to .tasks/<feature>/tasks.json.")
    create_proof.add_argument("--package", required=True, help="Work package id, for example WP1.")
    create_proof.add_argument(
        "--force",
        action="store_true",
        help="Replace edited or filled proof content only with explicit approved replacement metadata.",
    )
    create_proof.add_argument(
        "--approved-replacement",
        help="Approval text containing explicit approved-by source, provenance, and scope for replacing edited or filled proof evidence.",
    )
    create_proof.set_defaults(func=cmd_create_proof)

    validate_proof = subparsers.add_parser(
        "validate-proof",
        help="Validate one package proof Markdown file mechanically.",
    )
    validate_proof.add_argument("tasks", type=Path, help="Path to .tasks/<feature>/tasks.json.")
    validate_proof.add_argument("--package", required=True, help="Work package id, for example WP1.")
    validate_proof.set_defaults(func=cmd_validate_proof)

    validate_final = subparsers.add_parser(
        "validate-final",
        help="Validate all packages, proof Markdown, and package verification report bindings.",
    )
    validate_final.add_argument("tasks", type=Path, help="Path to .tasks/<feature>/tasks.json.")
    validate_final.set_defaults(func=cmd_validate_final)
    return parser


def cmd_validate_plan(args: argparse.Namespace) -> dict[str, Any]:
    registry, packages = load_and_validate_plan(args.tasks)
    return {
        "tasks": str(args.tasks),
        "feature": registry.feature,
        "packages": [package.package_id for package in registry.packages],
        "validated_package_markdown": sorted(packages),
        "validated_slices": sorted(registry.authoritative_slices),
    }


def cmd_create_proof(args: argparse.Namespace) -> dict[str, Any]:
    if args.approved_replacement and not args.force:
        raise SliceproofError(["create-proof: --approved-replacement requires --force"])
    if args.approved_replacement is not None and not has_approval_provenance_scope(args.approved_replacement):
        raise SliceproofError(
            ["create-proof: --approved-replacement must include positive approval, provenance, and scope"]
        )

    registry, packages = load_and_validate_plan(args.tasks)
    package = require_package(registry, args.package)
    package_md = packages[package.package_id]
    proof_path = resolve_safe_path(
        registry.root,
        package.proof_path,
        f"work_packages[{package.package_id}].proof_path",
        expected_suffix=".proof.md",
    )
    proof_text = render_proof_template(registry, package_md)
    backup_path: Path | None = None

    existed_before = proof_path.exists() or proof_path.is_symlink()
    if existed_before:
        if proof_path.is_symlink():
            raise SliceproofError([f"create-proof: refusing to write through symlink proof path: {package.proof_path}"])
        existing = read_text_file(proof_path, f"create-proof: existing proof {package.proof_path}")
        if is_generated_placeholder(existing, proof_text):
            return {
                "package": package.package_id,
                "proof_path": package.proof_path,
                "created": False,
                "already_existed": True,
                "required_slice_rows": package_md.must_satisfy_ids,
            }
        if not args.force:
            raise SliceproofError(
                [f"create-proof: {package.proof_path} already exists and is not the current empty placeholder; refusing overwrite"]
            )
        if not args.approved_replacement:
            raise SliceproofError(
                [
                    f"create-proof: {package.proof_path} contains edited or filled proof content; refusing --force "
                    "without approved replacement metadata and preservation safeguards"
                ]
            )
        backup_path = preserve_existing_proof(proof_path, existing)

    ensure_directory(proof_path.parent, f"create-proof: proof directory for {package.proof_path}")
    atomic_write_text(proof_path, proof_text)
    result: dict[str, Any] = {
        "package": package.package_id,
        "proof_path": package.proof_path,
        "created": True,
        "already_existed": False,
        "replaced_existing": existed_before,
        "required_slice_rows": package_md.must_satisfy_ids,
    }
    if backup_path is not None:
        result["preserved_existing_proof"] = str(backup_path.relative_to(registry.root))
        result["approved_replacement"] = args.approved_replacement.strip()
    return result


def cmd_validate_proof(args: argparse.Namespace) -> dict[str, Any]:
    state = load_package_state(args.tasks, args.package)
    errors = validate_proof_markdown(state.proof_path, state.package_md)
    if errors:
        raise SliceproofError(errors)
    return {
        "package": state.package.package_id,
        "proof_path": state.package.proof_path,
        "required_slice_rows": state.package_md.must_satisfy_ids,
        "verification_expectations": state.package_md.verification_expectations,
    }


def cmd_validate_final(args: argparse.Namespace) -> dict[str, Any]:
    registry, packages = load_and_validate_plan(args.tasks)
    errors: list[str] = []
    validated_reports: list[str] = []
    for package in registry.packages:
        package_md = packages[package.package_id]
        if package.status != "done":
            errors.append(f"work_packages[{package.package_id}].status: expected 'done' for validate-final, got {package.status!r}")
        proof_path = resolve_safe_path(
            registry.root,
            package.proof_path,
            f"work_packages[{package.package_id}].proof_path",
            expected_suffix=".proof.md",
        )
        report_path = resolve_safe_path(
            registry.root,
            package.report_path,
            f"work_packages[{package.package_id}].report_path",
            expected_suffix=".package-verification.md",
        )
        errors.extend(validate_proof_markdown(proof_path, package_md))
        report_errors = validate_report_markdown(report_path, package, package_md, proof_path)
        if not report_errors:
            validated_reports.append(package.report_path)
        errors.extend(report_errors)
    if errors:
        raise SliceproofError(errors)
    return {
        "feature": registry.feature,
        "packages": [package.package_id for package in registry.packages],
        "proofs_validated": [package.proof_path for package in registry.packages],
        "reports_validated": validated_reports,
    }


def load_package_state(tasks_path: Path, package_id: str) -> PackageState:
    registry, packages = load_and_validate_plan(tasks_path)
    package = require_package(registry, package_id)
    package_md = packages[package.package_id]
    proof_path = resolve_safe_path(
        registry.root,
        package.proof_path,
        f"work_packages[{package.package_id}].proof_path",
        expected_suffix=".proof.md",
    )
    report_path = resolve_safe_path(
        registry.root,
        package.report_path,
        f"work_packages[{package.package_id}].report_path",
        expected_suffix=".package-verification.md",
    )
    return PackageState(registry, package, package_md, proof_path, report_path)


def load_and_validate_plan(tasks_path: Path) -> tuple[Registry, dict[str, PackageMarkdown]]:
    registry = load_registry(tasks_path)
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


def load_registry(tasks_path: Path) -> Registry:
    root = Path.cwd().resolve(strict=False)
    tasks_resolved = resolve_tasks_argument(root, tasks_path)
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
        data=data,
        feature=feature,
        authoritative_slices=[path for path in authoritative_slices if isinstance(path, str)],
        packages=packages,
    )


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
            resolve_safe_path(registry.root, spec_path, "spec_path", expected_suffix=".md", must_exist_file=True)
        except SliceproofError as exc:
            errors.extend(exc.errors)

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
                resolve_safe_path(registry.root, path, f"authoritative_slices[{index}]", expected_suffix=".md", must_exist_file=True)
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
        for key in sorted(set(item) - REGISTRY_PACKAGE_KEYS):
            errors.append(f"{prefix}.{key}: unsupported package registry field")
        package_id = item.get("id")
        if not isinstance(package_id, str) or not PACKAGE_ID_RE.fullmatch(package_id):
            errors.append(f"{prefix}.id: expected WP<N> package id")
        else:
            if package_id in seen_ids:
                errors.append(f"work_packages: duplicate package id {package_id}")
            seen_ids.add(package_id)
            package_ids.add(package_id)
        path_suffixes = {"path": ".md", "proof_path": ".proof.md", "report_path": ".package-verification.md"}
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
    proof_paths = parse_bullets(sections["Proof"], unwrap_path=True)
    report_paths = parse_bullets(sections["Package Verification Report"], unwrap_path=True)
    dependencies = parse_dependencies(sections["Dependencies"])

    if not primary_paths:
        errors.append(f"{path}: ## Primary Paths must list at least one path")
    if not verification_expectations:
        errors.append(f"{path}: ## Verification Expectations must list at least one expectation")
    if len(proof_paths) != 1:
        errors.append(f"{path}: ## Proof must list exactly one proof path")
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
        proof_path=proof_paths[0],
        report_path=report_paths[0],
        dependencies=dependencies,
    )


def validate_package_markdown(registry: Registry, package: RegistryPackage, package_md: PackageMarkdown) -> list[str]:
    errors: list[str] = []
    if package_md.proof_path != package.proof_path:
        errors.append(f"{package.path}: ## Proof path {package_md.proof_path!r} does not match registry proof_path {package.proof_path!r}")
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

    for key, value, suffix in (
        ("proof path", package_md.proof_path, ".proof.md"),
        ("report path", package_md.report_path, ".package-verification.md"),
    ):
        try:
            resolve_safe_path(registry.root, value, f"{package.path}: {key}", expected_suffix=suffix)
        except SliceproofError as exc:
            errors.extend(exc.errors)
    for path in package_md.primary_paths:
        try:
            resolve_safe_path(registry.root, path, f"{package.path}: primary path {path!r}")
        except SliceproofError as exc:
            errors.extend(exc.errors)

    slice_titles_cache: dict[str, dict[str, str]] = {}
    seen_required_ids: set[str] = set()
    for ref in package_md.slice_refs:
        try:
            resolved = resolve_safe_path(registry.root, ref.path, f"{package.path}: assigned Slice {ref.path!r}", expected_suffix=".md", must_exist_file=True)
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
                    errors.append(f"{package.path}: {kind} ID {slice_id!r} not found as H3 in {ref.path}")
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


def split_h2_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    in_fence = False
    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")
        stripped = line.strip()
        if is_fence(stripped):
            in_fence = not in_fence
            if current is not None:
                sections[current].append(line)
            continue
        if not in_fence and line.startswith("## ") and not line.startswith("### "):
            current = line[3:].strip()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


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


def render_proof_template(registry: Registry, package_md: PackageMarkdown) -> str:
    slice_titles = load_titles_for_package(registry.root, package_md)
    lines: list[str] = [
        f"# Package Proof: {package_md.package_id} — {package_md.title}",
        "",
        "## Package Scope",
        package_md.scope,
        "",
        "## Assigned Slice Scope",
    ]
    if package_md.slice_refs:
        for ref in package_md.slice_refs:
            lines.append(f"- `{ref.path}`")
            for slice_id in ref.must_satisfy:
                title = slice_titles.get(ref.path, {}).get(slice_id, "")
                lines.append(f"  - Must satisfy: `{slice_id}`{format_title(title)}")
            for slice_id in ref.context_only:
                title = slice_titles.get(ref.path, {}).get(slice_id, "")
                lines.append(f"  - Context only: `{slice_id}`{format_title(title)}")
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Slice Closure Table",
            "",
            "| Slice ID | Required understanding | Implementation evidence | Verification evidence | Status |",
            "|---|---|---|---|---|",
        ]
    )
    for ref in package_md.slice_refs:
        for slice_id in ref.must_satisfy:
            title = slice_titles.get(ref.path, {}).get(slice_id, "")
            lines.append(f"| `{slice_id}` | {escape_table_cell(title or slice_id)} | TODO | TODO | OPEN |")
    lines.extend(
        [
            "",
            "## Acceptance / Verification Closure",
            "",
            "| Expectation | Evidence | Status |",
            "|---|---|---|",
        ]
    )
    for expectation in package_md.verification_expectations:
        lines.append(f"| {escape_table_cell(expectation)} | TODO | OPEN |")
    lines.extend(
        [
            "",
            "## Commands Run",
            "- TODO",
            "",
            "## Files Changed / Inspected",
            "- TODO",
            "",
            "## Gaps, Deviations, or Deferred Items",
            "- None.",
            "",
            "## Package Agent Completion Statement",
            "- TODO",
            "",
        ]
    )
    return "\n".join(lines)


def validate_proof_markdown(proof_path: Path, package_md: PackageMarkdown) -> list[str]:
    if not proof_path.is_file():
        return [f"proof: file not found: {proof_path}"]
    text = read_text_file(proof_path, f"proof {proof_path}")
    errors: list[str] = []
    sections = split_h2_sections(text)
    for section in sorted(REQUIRED_PROOF_SECTIONS):
        if section not in sections:
            errors.append(f"{proof_path}: missing required section ## {section}")
    if errors:
        return errors

    slice_rows = parse_table(sections["Slice Closure Table"])
    expectation_rows = parse_table(sections["Acceptance / Verification Closure"])
    errors.extend(validate_slice_rows(proof_path, package_md, slice_rows, sections))
    errors.extend(validate_expectation_rows(proof_path, package_md, expectation_rows, sections))
    for section in ("Commands Run", "Files Changed / Inspected", "Package Agent Completion Statement"):
        body = sections[section]
        if not body.strip() or is_placeholder_text(body):
            errors.append(f"{proof_path}: ## {section} must contain non-placeholder evidence")
        if BLOCKING_MARKER_RE.search(body):
            errors.append(f"{proof_path}: ## {section} contains unresolved TODO/OPEN/GAP marker")
    gaps_body = sections["Gaps, Deviations, or Deferred Items"]
    if UNRESOLVED_MARKER_RE.search(gaps_body):
        errors.append(f"{proof_path}: ## Gaps, Deviations, or Deferred Items contains unresolved TODO/OPEN marker")
    if not is_empty_gaps_deviations_section(gaps_body) and not has_approval_provenance_scope(gaps_body):
        errors.append(
            f"{proof_path}: ## Gaps, Deviations, or Deferred Items contains gap/deviation text without approval, provenance, and scope"
        )
    return errors


def validate_slice_rows(
    proof_path: Path,
    package_md: PackageMarkdown,
    rows: list[ProofRow],
    sections: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    required_columns = {"Slice ID", "Required understanding", "Implementation evidence", "Verification evidence", "Status"}
    required_ids = set(package_md.must_satisfy_ids)
    if rows and not required_columns.issubset(rows[0].cells):
        errors.append(f"{proof_path}: ## Slice Closure Table missing columns {sorted(required_columns - set(rows[0].cells))}")
        return errors
    rows_by_id: dict[str, ProofRow] = {}
    for index, row in enumerate(rows, start=1):
        slice_id = clean_cell_id(row.cells.get("Slice ID", ""))
        row_label = slice_id or f"Slice Closure Table row {index}"
        if slice_id:
            if slice_id in rows_by_id:
                errors.append(f"{proof_path}: duplicate Slice Closure Table row for {slice_id}")
            else:
                rows_by_id[slice_id] = row
            if slice_id not in required_ids:
                errors.append(f"{proof_path}: unexpected Slice Closure Table row for {slice_id}")
        errors.extend(validate_slice_row_status(proof_path, row, row_label, sections))
    for slice_id in package_md.must_satisfy_ids:
        if slice_id not in rows_by_id:
            errors.append(f"{proof_path}: Slice Closure Table missing required row for {slice_id}")
    return errors


def validate_expectation_rows(
    proof_path: Path,
    package_md: PackageMarkdown,
    rows: list[ProofRow],
    sections: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    required_columns = {"Expectation", "Evidence", "Status"}
    if rows and not required_columns.issubset(rows[0].cells):
        errors.append(f"{proof_path}: ## Acceptance / Verification Closure missing columns {sorted(required_columns - set(rows[0].cells))}")
        return errors
    rows_by_expectation: dict[str, ProofRow] = {}
    display_by_expectation: dict[str, str] = {}
    required_expectations = {normalize_text(expectation) for expectation in package_md.verification_expectations}
    for index, row in enumerate(rows, start=1):
        expectation = row.cells.get("Expectation", "")
        normalized = normalize_text(expectation)
        row_label = f"expectation {expectation!r}" if normalized else f"Acceptance / Verification Closure row {index}"
        if normalized:
            if normalized in rows_by_expectation:
                errors.append(f"{proof_path}: duplicate Acceptance / Verification Closure row for {display_by_expectation[normalized]!r}")
            else:
                rows_by_expectation[normalized] = row
                display_by_expectation[normalized] = expectation
            if normalized not in required_expectations:
                errors.append(f"{proof_path}: unexpected Acceptance / Verification Closure row for {expectation!r}")
        errors.extend(validate_expectation_row_status(proof_path, row, row_label, sections))
    for expectation in package_md.verification_expectations:
        row = rows_by_expectation.get(normalize_text(expectation))
        if row is None:
            errors.append(f"{proof_path}: Acceptance / Verification Closure missing expectation {expectation!r}")
    return errors


def validate_slice_row_status(proof_path: Path, row: ProofRow, row_label: str, sections: dict[str, str]) -> list[str]:
    if not any(normalize_text(value) for value in row.cells.values()):
        return []
    errors: list[str] = []
    implementation = row.cells.get("Implementation evidence", "")
    verification = row.cells.get("Verification evidence", "")
    status = normalize_status(row.cells.get("Status", ""))
    row_text = " ".join(row.cells.values()) + " " + sections["Gaps, Deviations, or Deferred Items"]
    if status not in PROOF_STATUS_VALUES:
        errors.append(f"{proof_path}: {row_label} status {status!r} is not supported")
    elif status == "PASS":
        if is_placeholder_text(implementation):
            errors.append(f"{proof_path}: {row_label} implementation evidence is missing or placeholder")
        if is_placeholder_text(verification):
            errors.append(f"{proof_path}: {row_label} verification evidence is missing or placeholder")
    elif status in {"OPEN", "GAP"}:
        errors.append(f"{proof_path}: {row_label} status {status} blocks proof validation")
    elif status == "DEFERRED":
        if not has_approval_provenance_scope(row_text):
            errors.append(f"{proof_path}: {row_label} DEFERRED requires approval, provenance, and scope metadata")
    elif status == "N/A":
        if not has_approval_provenance_scope(row_text) or "rationale" not in row_text.lower():
            errors.append(f"{proof_path}: {row_label} N/A requires rationale plus approval, provenance, and scope metadata")
    if BLOCKING_MARKER_RE.search(row.raw):
        errors.append(f"{proof_path}: {row_label} row contains unresolved TODO/OPEN/GAP marker")
    return errors


def validate_expectation_row_status(proof_path: Path, row: ProofRow, row_label: str, sections: dict[str, str]) -> list[str]:
    if not any(normalize_text(value) for value in row.cells.values()):
        return []
    errors: list[str] = []
    evidence = row.cells.get("Evidence", "")
    status = normalize_status(row.cells.get("Status", ""))
    row_text = " ".join(row.cells.values()) + " " + sections["Gaps, Deviations, or Deferred Items"]
    if status not in PROOF_STATUS_VALUES:
        errors.append(f"{proof_path}: {row_label} status {status!r} is not supported")
    elif status == "PASS":
        if is_placeholder_text(evidence):
            errors.append(f"{proof_path}: {row_label} evidence is missing or placeholder")
    elif status in {"OPEN", "GAP"}:
        errors.append(f"{proof_path}: {row_label} status {status} blocks proof validation")
    elif status == "DEFERRED" and not has_approval_provenance_scope(row_text):
        errors.append(f"{proof_path}: {row_label} DEFERRED requires approval, provenance, and scope metadata")
    elif status == "N/A" and (not has_approval_provenance_scope(row_text) or "rationale" not in row_text.lower()):
        errors.append(f"{proof_path}: {row_label} N/A requires rationale plus approval, provenance, and scope metadata")
    if BLOCKING_MARKER_RE.search(row.raw):
        errors.append(f"{proof_path}: {row_label} row contains unresolved TODO/OPEN/GAP marker")
    return errors


def validate_report_markdown(
    report_path: Path,
    package: RegistryPackage,
    package_md: PackageMarkdown,
    proof_path: Path,
) -> list[str]:
    if not report_path.is_file():
        return [f"report: file not found: {report_path}"]
    text = read_text_file(report_path, f"package verification report {report_path}")
    errors: list[str] = []
    h1_match = re.search(r"^#\s+Package Verification Report:\s+(WP[1-9]\d*)\s*(?:—|-)?\s*(.*?)\s*$", text, flags=re.MULTILINE)
    if not h1_match:
        errors.append(f"{report_path}: expected H1 '# Package Verification Report: {package.package_id} — <title>'")
    elif h1_match.group(1) != package.package_id:
        errors.append(f"{report_path}: H1 package id {h1_match.group(1)!r} does not match registry id {package.package_id!r}")

    sections = split_h2_sections(text)
    for section in sorted(REQUIRED_REPORT_SECTIONS):
        if section not in sections:
            errors.append(f"{report_path}: missing required section ## {section}")
    if errors:
        return errors

    binding = parse_key_values(sections["State Binding"])
    result = parse_key_values(sections["Verification Result"])
    required_binding = {"Package", "Proof", "Proof Digest", "Worktree", "Git Ref", "Commit", "Verified At"}
    required_result = {"Result", "Reviewer", "Scope"}
    for field in sorted(required_binding - set(binding)):
        errors.append(f"{report_path}: ## State Binding missing {field!r}")
    for field in sorted(required_result - set(result)):
        errors.append(f"{report_path}: ## Verification Result missing {field!r}")
    if errors:
        return errors

    if clean_cell_id(binding["Package"]) != package.package_id:
        errors.append(f"{report_path}: State Binding Package must be {package.package_id}")
    if normalize_path_value(binding["Proof"]) != package.proof_path:
        errors.append(f"{report_path}: State Binding Proof must be {package.proof_path}")
    actual_digest = digest_text(read_text_file(proof_path, f"proof {proof_path}"))
    if clean_cell_id(binding["Proof Digest"]) != actual_digest:
        errors.append(f"{report_path}: State Binding Proof Digest does not match current proof content")
    if not normalize_text(binding["Worktree"]):
        errors.append(f"{report_path}: State Binding Worktree must be non-empty")
    if not normalize_text(binding["Git Ref"]):
        errors.append(f"{report_path}: State Binding Git Ref must be non-empty")
    commit = clean_cell_id(binding["Commit"])
    if not COMMIT_RE.fullmatch(commit):
        errors.append(f"{report_path}: State Binding Commit must look like a git commit")
    if not is_iso8601(clean_cell_id(binding["Verified At"])):
        errors.append(f"{report_path}: State Binding Verified At must be ISO-8601")
    if clean_cell_id(result["Result"]).lower() not in PASS_REPORT_VALUES:
        errors.append(f"{report_path}: Verification Result must be passed")
    if is_placeholder_text(result["Reviewer"]):
        errors.append(f"{report_path}: Verification Result Reviewer must be non-placeholder")
    if is_placeholder_text(result["Scope"]):
        errors.append(f"{report_path}: Verification Result Scope must be non-placeholder")
    if not sections["Checks"].strip() or is_placeholder_text(sections["Checks"]):
        errors.append(f"{report_path}: ## Checks must contain non-placeholder verification notes")
    if UNRESOLVED_MARKER_RE.search(sections["Open Findings"]):
        errors.append(f"{report_path}: ## Open Findings contains unresolved TODO/OPEN marker")
    if not is_empty_gaps_deviations_section(sections["Open Findings"]):
        errors.append(f"{report_path}: ## Open Findings must be '- None.' for final validation")
    _ = package_md  # keep signature explicit: report validation is package-assignment scoped.
    return errors


def parse_key_values(body: str) -> dict[str, str]:
    values: dict[str, str] = {}
    in_fence = False
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if is_fence(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = re.sub(r"^(?:[-*]|\d+\.)\s+", "", line)
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key:
            values[key] = value.strip()
    return values


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


def resolve_tasks_argument(root: Path, value: Path) -> Path:
    candidate = value if value.is_absolute() else root / value
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError:
        raise SliceproofError([f"tasks.json: path escapes repository root: {value}"])
    return resolved


def resolve_safe_path(
    root: Path,
    value: str,
    label: str,
    *,
    expected_suffix: str | None = None,
    must_exist_file: bool = False,
) -> Path:
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
    resolved = (root / path).resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError:
        raise SliceproofError([f"{label}: path escapes repository root"])
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


def is_generated_placeholder(existing: str, generated: str) -> bool:
    return normalize_generated_placeholder(existing) == normalize_generated_placeholder(generated)


def normalize_generated_placeholder(value: str) -> str:
    return value.replace("\r\n", "\n").rstrip("\n")


def preserve_existing_proof(proof_path: Path, existing: str) -> Path:
    digest = hashlib.sha256(existing.encode("utf-8")).hexdigest()[:12]
    backup_path = proof_path.with_name(f"{proof_path.name}.preserved.{digest}.bak")
    if backup_path.is_symlink():
        raise SliceproofError([f"create-proof: preservation backup path is a symlink: {backup_path}"])
    write_text_exclusive_no_follow(backup_path, existing, "create-proof: preservation backup")
    return backup_path


def read_text_file(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SliceproofError([f"{label}: file not found: {path}"])
    except UnicodeError as exc:
        raise SliceproofError([f"{label}: unable to decode UTF-8 text from {path}: {exc}"])
    except OSError as exc:
        raise SliceproofError([f"{label}: unable to read {path}: {exc}"])


def ensure_directory(path: Path, label: str) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise SliceproofError([f"{label}: unable to create directory {path}: {exc}"])


def write_text_exclusive_no_follow(path: Path, content: str, label: str) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd: int | None = None
    try:
        fd = os.open(path, flags, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            fd = None
            handle.write(content)
    except FileExistsError:
        raise SliceproofError([f"{label} already exists: {path}"])
    except OSError as exc:
        raise SliceproofError([f"{label}: unable to create {path}: {exc}"])
    finally:
        if fd is not None:
            os.close(fd)


def atomic_write_text(path: Path, content: str) -> None:
    tmp_fd: int | None = None
    tmp_name: str | None = None
    try:
        tmp_fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as handle:
            tmp_fd = None
            handle.write(content)
        os.replace(tmp_name, path)
        tmp_name = None
    except OSError as exc:
        raise SliceproofError([f"unable to write {path}: {exc}"])
    finally:
        if tmp_fd is not None:
            os.close(tmp_fd)
        if tmp_name is not None:
            try:
                os.unlink(tmp_name)
            except FileNotFoundError:
                pass


def load_titles_for_package(root: Path, package_md: PackageMarkdown) -> dict[str, dict[str, str]]:
    titles: dict[str, dict[str, str]] = {}
    for ref in package_md.slice_refs:
        titles[ref.path] = extract_slice_h3_titles(resolve_safe_path(root, ref.path, f"assigned Slice {ref.path!r}", expected_suffix=".md", must_exist_file=True))
    return titles


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


def normalize_path_value(value: str) -> str:
    return clean_cell_id(value).strip()


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
        if not re.fullmatch(r"(?:[-*]\s+|\d+\.\s+)?None\.?", stripped, flags=re.IGNORECASE):
            return False
    return True


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
    normalized = normalize_text(value).strip(" -*`'\".:?!").lower()
    return not normalized or APPROVAL_PLACEHOLDER_TOKEN_RE.search(normalized) is not None


def digest_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def is_iso8601(value: str) -> bool:
    if not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def format_title(title: str) -> str:
    return f" — {title}" if title else ""


def escape_table_cell(value: str) -> str:
    return value.replace("|", "\\|")


def is_fence(line: str) -> bool:
    return line.startswith("```") or line.startswith("~~~")


def write_json(stream: Any, data: dict[str, Any]) -> None:
    json.dump(data, stream, indent=2, sort_keys=True)
    stream.write("\n")


if __name__ == "__main__":
    raise SystemExit(main())
