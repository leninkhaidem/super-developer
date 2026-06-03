#!/usr/bin/env python3
"""Mechanical helper for schema-version-4 Slice-first planned-feature artifacts.

The helper intentionally performs shallow deterministic checks only.  It validates
registry/package/Slice/proof Markdown structure and can create package proof
placeholders.  It does not judge semantic proof quality, mutate package status,
run tests, inspect git freshness, or maintain JSON lifecycle state.
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
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 4
FEATURE_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
PACKAGE_ID_RE = re.compile(r"^WP[1-9]\d*$")
SLICE_ID_RE = re.compile(r"^[A-Z][A-Z0-9-]*-[0-9]{3}$")
H3_ID_RE = re.compile(r"^\s*###\s+`?([A-Z][A-Z0-9-]*-[0-9]{3})`?(?:\s+(?:—|-)\s*(.*?))?\s*$")
STATUS_VALUES = {"pending", "in_progress", "done", "blocked"}
FEATURE_STATUS_VALUES = {"planned", "reviewed", "in_progress", "in-progress", "completed", "on_hold", "on-hold"}
REQUIRED_PACKAGE_SECTIONS = {
    "Scope",
    "Assigned Slices",
    "Primary Paths",
    "Verification Expectations",
    "Proof",
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
PROOF_STATUS_VALUES = {"PASS", "GAP", "DEFERRED", "N/A", "OPEN"}
BLOCKING_MARKER_RE = re.compile(r"\b(?:TODO|OPEN|GAP)\b", re.IGNORECASE)
PLACEHOLDER_VALUES = {"", "todo", "open", "gap", "tbd", "n/a", "na"}


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


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except SliceproofError as exc:
        write_json(sys.stderr, {"ok": False, "command": args.command, "errors": exc.errors})
        return 1
    write_json(sys.stdout, {"ok": True, "command": args.command, **result})
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Mechanical schema-v4 Slice-first helper. Validation commands are read-only; "
            "create-proof only writes the declared package proof Markdown placeholder."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_plan = subparsers.add_parser(
        "validate-plan",
        help="Validate a v4 registry plus package Markdown and Slice H3 references.",
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
        help=(
            "Regenerate only an empty pre-dispatch placeholder. Filled proof evidence is refused "
            "unless --approved-replacement is also supplied."
        ),
    )
    create_proof.add_argument(
        "--approved-replacement",
        help=(
            "Explicit approval/provenance for replacing filled proof evidence. Requires --force; "
            "the existing proof is preserved next to the proof file before replacement."
        ),
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
        help="Validate all package Markdown and package proof Markdown files for final readiness.",
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
    if args.approved_replacement is not None and not args.approved_replacement.strip():
        raise SliceproofError(["create-proof: --approved-replacement must be non-empty when provided"])

    registry, packages = load_and_validate_plan(args.tasks)
    package = require_package(registry, args.package)
    package_md = packages[package.package_id]
    proof_path = resolve_safe_path(registry.root, package.proof_path, f"work_packages[{package.package_id}].proof_path")
    proof_text = render_proof_template(registry, package_md)
    backup_path: Path | None = None

    existed_before = proof_path.exists()
    if existed_before:
        existing = proof_path.read_text(encoding="utf-8")
        if not args.force:
            raise SliceproofError([f"create-proof: {package.proof_path} already exists; use --force only after overwrite screening"])
        if is_empty_placeholder(existing, package_md):
            pass
        elif args.approved_replacement:
            backup_path = preserve_existing_proof(proof_path, existing)
        else:
            raise SliceproofError(
                [
                    f"create-proof: {package.proof_path} contains filled proof evidence; refusing --force without "
                    "explicit approved replacement and preservation safeguards"
                ]
            )

    proof_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(proof_path, proof_text)
    result: dict[str, Any] = {
        "package": package.package_id,
        "proof_path": package.proof_path,
        "created": True,
        "replaced_existing": existed_before,
        "required_slice_rows": package_md.must_satisfy_ids,
    }
    if backup_path is not None:
        result["preserved_existing_proof"] = str(backup_path.relative_to(registry.root))
        result["approved_replacement"] = args.approved_replacement.strip()
    return result


def cmd_validate_proof(args: argparse.Namespace) -> dict[str, Any]:
    registry, packages = load_and_validate_plan(args.tasks)
    package = require_package(registry, args.package)
    package_md = packages[package.package_id]
    proof_path = resolve_safe_path(registry.root, package.proof_path, f"work_packages[{package.package_id}].proof_path")
    errors = validate_proof_markdown(proof_path, package_md)
    if errors:
        raise SliceproofError(errors)
    return {
        "package": package.package_id,
        "proof_path": package.proof_path,
        "required_slice_rows": package_md.must_satisfy_ids,
        "verification_expectations": package_md.verification_expectations,
    }


def cmd_validate_final(args: argparse.Namespace) -> dict[str, Any]:
    registry, packages = load_and_validate_plan(args.tasks)
    errors: list[str] = []
    for package in registry.packages:
        if package.status != "done":
            errors.append(f"work_packages[{package.package_id}].status: expected 'done' for validate-final, got {package.status!r}")
        proof_path = resolve_safe_path(registry.root, package.proof_path, f"work_packages[{package.package_id}].proof_path")
        errors.extend(validate_proof_markdown(proof_path, packages[package.package_id]))
    if errors:
        raise SliceproofError(errors)
    return {
        "feature": registry.feature,
        "packages": [package.package_id for package in registry.packages],
        "proofs_validated": [package.proof_path for package in registry.packages],
    }


def load_and_validate_plan(tasks_path: Path) -> tuple[Registry, dict[str, PackageMarkdown]]:
    registry = load_registry(tasks_path)
    errors = validate_registry(registry)
    packages: dict[str, PackageMarkdown] = {}
    if not errors:
        for package in registry.packages:
            package_path = resolve_safe_path(registry.root, package.path, f"work_packages[{package.package_id}].path")
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
    try:
        data = json.loads(tasks_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SliceproofError([f"tasks.json: file not found: {tasks_path}"])
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
                status=item.get("status") if isinstance(item.get("status"), str) else "",
                depends_on=item.get("depends_on") if isinstance(item.get("depends_on"), list) else [],
            )
        )
    return Registry(
        path=tasks_path,
        root=root,
        data=data,
        feature=feature,
        authoritative_slices=[path for path in authoritative_slices if isinstance(path, str)],
        packages=packages,
    )


def validate_registry(registry: Registry) -> list[str]:
    data = registry.data
    errors: list[str] = []
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version: expected {SCHEMA_VERSION}")
    if not registry.feature or not FEATURE_RE.fullmatch(registry.feature):
        errors.append("feature: expected lowercase slug with letters, digits, and hyphens")
    title = data.get("title")
    if title is not None and (not isinstance(title, str) or not title.strip()):
        errors.append("title: expected non-empty string when present")
    status = data.get("status")
    if status is not None and (not isinstance(status, str) or status not in FEATURE_STATUS_VALUES):
        errors.append(f"status: expected one of {sorted(FEATURE_STATUS_VALUES)} when present")

    spec_path = data.get("spec_path")
    if spec_path is not None:
        if not isinstance(spec_path, str) or not spec_path.strip():
            errors.append("spec_path: expected non-empty string when present")
        else:
            try:
                resolved_spec = resolve_safe_path(registry.root, spec_path, "spec_path")
                if not resolved_spec.is_file():
                    errors.append(f"spec_path: file not found: {spec_path}")
            except SliceproofError as exc:
                errors.extend(exc.errors)

    authoritative = data.get("authoritative_slices")
    if not isinstance(authoritative, list) or not authoritative:
        errors.append("authoritative_slices: expected non-empty array")
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
                resolved = resolve_safe_path(registry.root, path, f"authoritative_slices[{index}]")
                if not resolved.is_file():
                    errors.append(f"authoritative_slices[{index}]: file not found: {path}")
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
        package_id = item.get("id")
        if not isinstance(package_id, str) or not PACKAGE_ID_RE.fullmatch(package_id):
            errors.append(f"{prefix}.id: expected WP<N> package id")
        else:
            if package_id in seen_ids:
                errors.append(f"work_packages: duplicate package id {package_id}")
            seen_ids.add(package_id)
            package_ids.add(package_id)
        for key in ("path", "proof_path"):
            path = item.get(key)
            if not isinstance(path, str) or not path.strip():
                errors.append(f"{prefix}.{key}: expected non-empty string")
                continue
            try:
                resolved = resolve_safe_path(registry.root, path, f"{prefix}.{key}")
                if key == "path" and not resolved.is_file():
                    errors.append(f"{prefix}.path: file not found: {path}")
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
            cycle = stack[stack.index(package_id) :] + [package_id]
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
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    title = package_id
    h1_match = re.search(r"^#\s+Work Package:\s+([A-Z0-9]+)\s*(?:—|-)?\s*(.*?)\s*$", text, flags=re.MULTILINE)
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
    slice_refs = parse_assigned_slices(sections["Assigned Slices"], path)
    primary_paths = parse_bullets(sections["Primary Paths"], unwrap_path=True)
    verification_expectations = parse_bullets(sections["Verification Expectations"], unwrap_path=False)
    proof_paths = parse_bullets(sections["Proof"], unwrap_path=True)
    dependencies = parse_dependencies(sections["Dependencies"])

    if not slice_refs:
        errors.append(f"{path}: ## Assigned Slices must list at least one Slice")
    if not primary_paths:
        errors.append(f"{path}: ## Primary Paths must list at least one path")
    if not verification_expectations:
        errors.append(f"{path}: ## Verification Expectations must list at least one expectation")
    if len(proof_paths) != 1:
        errors.append(f"{path}: ## Proof must list exactly one proof path")
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
        dependencies=dependencies,
    )


def validate_package_markdown(registry: Registry, package: RegistryPackage, package_md: PackageMarkdown) -> list[str]:
    errors: list[str] = []
    if package_md.proof_path != package.proof_path:
        errors.append(
            f"{package.path}: ## Proof path {package_md.proof_path!r} does not match registry proof_path {package.proof_path!r}"
        )
    if package_md.dependencies != package.depends_on:
        errors.append(
            f"{package.path}: ## Dependencies {package_md.dependencies!r} do not match registry depends_on {package.depends_on!r}"
        )

    authoritative = set(registry.authoritative_slices)
    slice_titles_cache: dict[str, dict[str, str]] = {}
    for path in package_md.primary_paths:
        try:
            resolve_safe_path(registry.root, path, f"{package.path}: primary path {path!r}")
        except SliceproofError as exc:
            errors.extend(exc.errors)
    for ref in package_md.slice_refs:
        try:
            resolved = resolve_safe_path(registry.root, ref.path, f"{package.path}: assigned Slice {ref.path!r}")
            if not resolved.is_file():
                errors.append(f"{package.path}: assigned Slice file not found: {ref.path}")
                continue
        except SliceproofError as exc:
            errors.extend(exc.errors)
            continue
        if ref.path not in authoritative:
            errors.append(f"{package.path}: assigned Slice {ref.path!r} is not listed in authoritative_slices")
        slice_titles_cache[ref.path] = extract_slice_h3_titles(resolved)
        if not ref.must_satisfy and not ref.context_only:
            errors.append(f"{package.path}: assigned Slice {ref.path!r} has no must_satisfy or context_only IDs")
        for kind, ids in (("must_satisfy", ref.must_satisfy), ("context_only", ref.context_only)):
            seen: set[str] = set()
            for slice_id in ids:
                if not SLICE_ID_RE.fullmatch(slice_id):
                    errors.append(f"{package.path}: {kind} ID {slice_id!r} has unsupported shape")
                    continue
                if slice_id in seen:
                    errors.append(f"{package.path}: duplicate {kind} ID {slice_id!r} for Slice {ref.path!r}")
                seen.add(slice_id)
                if slice_id not in slice_titles_cache[ref.path]:
                    errors.append(f"{package.path}: {kind} ID {slice_id!r} not found as H3 in {ref.path}")
    return errors


def parse_assigned_slices(body: str, package_path: Path) -> list[SliceRef]:
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
        if line.startswith(("- ", "* ")) and mode and current_path:
            item = line[2:].strip()
            slice_id = extract_id(item)
            if slice_id:
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
        dependency = extract_id(item) or item.strip("`")
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
    for raw_line in path.read_text(encoding="utf-8").splitlines():
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
    for ref in package_md.slice_refs:
        lines.append(f"- `{ref.path}`")
        for slice_id in ref.must_satisfy:
            title = slice_titles.get(ref.path, {}).get(slice_id, "")
            lines.append(f"  - Must satisfy: `{slice_id}`{format_title(title)}")
        for slice_id in ref.context_only:
            title = slice_titles.get(ref.path, {}).get(slice_id, "")
            lines.append(f"  - Context only: `{slice_id}`{format_title(title)}")
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
    text = proof_path.read_text(encoding="utf-8")
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
    if BLOCKING_MARKER_RE.search(gaps_body):
        errors.append(f"{proof_path}: ## Gaps, Deviations, or Deferred Items contains unresolved TODO/OPEN/GAP marker")
    if re.search(r"\bDEFERRED\b", gaps_body, flags=re.IGNORECASE) and not contains_approval_scope(gaps_body):
        errors.append(f"{proof_path}: deferred gap/deviation requires explicit approved deferral/scope metadata")
    return errors


def validate_slice_rows(
    proof_path: Path,
    package_md: PackageMarkdown,
    rows: list[ProofRow],
    sections: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    required_columns = {"Slice ID", "Required understanding", "Implementation evidence", "Verification evidence", "Status"}
    if rows and not required_columns.issubset(rows[0].cells):
        errors.append(f"{proof_path}: ## Slice Closure Table missing columns {sorted(required_columns - set(rows[0].cells))}")
        return errors
    rows_by_id: dict[str, ProofRow] = {}
    for row in rows:
        slice_id = clean_cell_id(row.cells.get("Slice ID", ""))
        if slice_id:
            rows_by_id[slice_id] = row
    for slice_id in package_md.must_satisfy_ids:
        row = rows_by_id.get(slice_id)
        if row is None:
            errors.append(f"{proof_path}: Slice Closure Table missing required row for {slice_id}")
            continue
        implementation = row.cells.get("Implementation evidence", "")
        verification = row.cells.get("Verification evidence", "")
        status = normalize_status(row.cells.get("Status", ""))
        row_text = " ".join(row.cells.values()) + " " + sections["Gaps, Deviations, or Deferred Items"]
        if status not in PROOF_STATUS_VALUES:
            errors.append(f"{proof_path}: {slice_id} status {status!r} is not supported")
            continue
        if status == "PASS":
            if is_placeholder_text(implementation):
                errors.append(f"{proof_path}: {slice_id} implementation evidence is missing or placeholder")
            if is_placeholder_text(verification):
                errors.append(f"{proof_path}: {slice_id} verification evidence is missing or placeholder")
        elif status in {"OPEN", "GAP"}:
            errors.append(f"{proof_path}: {slice_id} status {status} blocks proof validation")
        elif status == "DEFERRED":
            if not contains_approval_scope(row_text):
                errors.append(f"{proof_path}: {slice_id} DEFERRED requires explicit approved deferral/scope metadata")
        elif status == "N/A":
            if not contains_na_approval_scope(row_text):
                errors.append(f"{proof_path}: {slice_id} N/A requires explicit rationale and approval/scope metadata")
        if BLOCKING_MARKER_RE.search(row.raw):
            errors.append(f"{proof_path}: {slice_id} row contains unresolved TODO/OPEN/GAP marker")
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
        errors.append(
            f"{proof_path}: ## Acceptance / Verification Closure missing columns {sorted(required_columns - set(rows[0].cells))}"
        )
        return errors
    rows_by_expectation = {normalize_text(row.cells.get("Expectation", "")): row for row in rows}
    for expectation in package_md.verification_expectations:
        row = rows_by_expectation.get(normalize_text(expectation))
        if row is None:
            errors.append(f"{proof_path}: Acceptance / Verification Closure missing expectation {expectation!r}")
            continue
        evidence = row.cells.get("Evidence", "")
        status = normalize_status(row.cells.get("Status", ""))
        row_text = " ".join(row.cells.values()) + " " + sections["Gaps, Deviations, or Deferred Items"]
        if status not in PROOF_STATUS_VALUES:
            errors.append(f"{proof_path}: expectation {expectation!r} status {status!r} is not supported")
            continue
        if status == "PASS":
            if is_placeholder_text(evidence):
                errors.append(f"{proof_path}: expectation {expectation!r} evidence is missing or placeholder")
        elif status in {"OPEN", "GAP"}:
            errors.append(f"{proof_path}: expectation {expectation!r} status {status} blocks proof validation")
        elif status == "DEFERRED" and not contains_approval_scope(row_text):
            errors.append(f"{proof_path}: expectation {expectation!r} DEFERRED requires explicit approved deferral/scope metadata")
        elif status == "N/A" and not contains_na_approval_scope(row_text):
            errors.append(f"{proof_path}: expectation {expectation!r} N/A requires explicit rationale and approval/scope metadata")
        if BLOCKING_MARKER_RE.search(row.raw):
            errors.append(f"{proof_path}: expectation {expectation!r} row contains unresolved TODO/OPEN/GAP marker")
    return errors


def parse_table(body: str) -> list[ProofRow]:
    rows: list[list[str]] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line.startswith("|") or not line.endswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells):
            continue
        rows.append(cells)
    if len(rows) < 2:
        return []
    headers = rows[0]
    proof_rows: list[ProofRow] = []
    for cells in rows[1:]:
        mapped = {header: cells[index] if index < len(cells) else "" for index, header in enumerate(headers)}
        proof_rows.append(ProofRow(mapped, " | ".join(cells)))
    return proof_rows


def is_empty_placeholder(text: str, package_md: PackageMarkdown) -> bool:
    sections = split_h2_sections(text)
    if not REQUIRED_PROOF_SECTIONS.issubset(sections):
        return False
    rows = parse_table(sections["Slice Closure Table"])
    expectation_rows = parse_table(sections["Acceptance / Verification Closure"])
    rows_by_id = {clean_cell_id(row.cells.get("Slice ID", "")): row for row in rows}
    expectation_by_text = {normalize_text(row.cells.get("Expectation", "")): row for row in expectation_rows}
    for slice_id in package_md.must_satisfy_ids:
        row = rows_by_id.get(slice_id)
        if row is None:
            return False
        if normalize_status(row.cells.get("Status", "")) == "PASS":
            return False
        for column in ("Implementation evidence", "Verification evidence"):
            if not is_placeholder_text(row.cells.get(column, "")):
                return False
    for expectation in package_md.verification_expectations:
        row = expectation_by_text.get(normalize_text(expectation))
        if row is None:
            return False
        if normalize_status(row.cells.get("Status", "")) == "PASS":
            return False
        if not is_placeholder_text(row.cells.get("Evidence", "")):
            return False
    for section in ("Commands Run", "Files Changed / Inspected", "Package Agent Completion Statement"):
        if not is_placeholder_text(sections.get(section, "")):
            return False
    return True


def preserve_existing_proof(proof_path: Path, existing: str) -> Path:
    digest = hashlib.sha256(existing.encode("utf-8")).hexdigest()[:12]
    backup_path = proof_path.with_name(f"{proof_path.name}.preserved.{digest}.bak")
    if backup_path.exists():
        raise SliceproofError([f"create-proof: preservation backup already exists: {backup_path}"])
    backup_path.write_text(existing, encoding="utf-8")
    return backup_path


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


def require_package(registry: Registry, package_id: str) -> RegistryPackage:
    if not PACKAGE_ID_RE.fullmatch(package_id):
        raise SliceproofError([f"--package: expected WP<N> package id, got {package_id!r}"])
    package = registry.package(package_id)
    if package is None:
        raise SliceproofError([f"--package: unknown package id {package_id}"])
    return package


def resolve_safe_path(root: Path, value: str, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise SliceproofError([f"{label}: expected non-empty repo-relative path"])
    if "\x00" in value or "\\" in value:
        raise SliceproofError([f"{label}: path must use safe repo-relative POSIX syntax"])
    path = Path(value)
    if path.is_absolute() or value.startswith("~") or ":" in value:
        raise SliceproofError([f"{label}: path must be repo-relative, not absolute/home/drive-qualified"])
    if any(part in {"", ".", ".."} for part in path.parts):
        raise SliceproofError([f"{label}: path must not contain empty, '.', or '..' segments"])
    resolved = (root / path).resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError:
        raise SliceproofError([f"{label}: path escapes repository root"])
    return resolved


def load_titles_for_package(root: Path, package_md: PackageMarkdown) -> dict[str, dict[str, str]]:
    titles: dict[str, dict[str, str]] = {}
    for ref in package_md.slice_refs:
        titles[ref.path] = extract_slice_h3_titles(resolve_safe_path(root, ref.path, f"assigned Slice {ref.path!r}"))
    return titles


def extract_backticked_or_text(value: str) -> str:
    match = re.search(r"`([^`]+)`", value)
    if match:
        return match.group(1).strip()
    return re.split(r"\s+(?:—|-)\s+", value, maxsplit=1)[0].strip()


def extract_id(value: str) -> str | None:
    backticked = re.search(r"`([A-Z][A-Z0-9-]*-[0-9]{3})`", value)
    if backticked:
        return backticked.group(1)
    plain = re.search(r"\b([A-Z][A-Z0-9-]*-[0-9]{3})\b", value)
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


def contains_approval_scope(value: str) -> bool:
    lowered = value.lower()
    return "approved" in lowered and ("scope" in lowered or "deferral" in lowered or "approval" in lowered)


def contains_na_approval_scope(value: str) -> bool:
    lowered = value.lower()
    return "approved" in lowered and "scope" in lowered and ("rationale" in lowered or "no longer applies" in lowered)


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
