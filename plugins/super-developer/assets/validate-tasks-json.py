#!/usr/bin/env python3
"""Validate super-developer tasks.json, package proofs, and historical verification ledgers."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

FEATURE_STATUSES = {"planned", "reviewed", "in-progress", "completed", "on-hold"}
TASK_STATUSES = {"pending", "in-progress", "done", "blocked", "skipped"}
DESIGN_DECISION_SOURCES = {"design-preflight", "planner"}
PHASE_ID_RE = re.compile(r"P[1-9]\d*")
TASK_ID_RE = re.compile(r"(P[1-9]\d*)-T\d{3}")
TASK_AC_ID_RE = re.compile(r"(P[1-9]\d*-T\d{3})-AC[1-9]\d*")
WORK_PACKAGE_ID_RE = re.compile(r"WP[1-9]\d*")
DESIGN_DECISION_ID_RE = re.compile(r"DD-[1-9]\d*")
CONTEXT_BUNDLE_ID_RE = re.compile(r"CTX-[1-9]\d*")
SPEC_REQ_RE = re.compile(r"^\s*-\s*(REQ-[1-9]\d*)\s*:")
SPEC_AC_RE = re.compile(r"^\s*-\s*(AC-[1-9]\d*)\s*:")

SOURCE_REF_TYPES = {"spec_req", "spec_ac", "design_decision", "context_bundle"}
SLICE_COVERAGE_STATES = {"covered", "zero_slices"}
SLICE_COVERAGE_DISPOSITIONS = {
    "projected",
    "informational",
    "deferred",
    "out_of_scope",
    "rejected",
    "conflict",
}
SLICE_COVERAGE_REF_TYPES = SOURCE_REF_TYPES | {"task_ac"}
SLICE_COVERAGE_SCOPE_REDUCING_DISPOSITIONS = {"deferred", "out_of_scope", "rejected"}
BUNDLE_SOURCE_TYPES = {"docs", "code", "spec", "external", "repo"}
LEDGER_STATUSES = {"verified", "failed", "blocked", "manual_required"}
LEDGER_METHODS = {
    "unit_test",
    "integration_test",
    "e2e_test",
    "table_driven_test",
    "static_inspection",
    "manual",
    "command",
    "mixed",
}
COMMAND_EVIDENCE_METHODS = {
    "unit_test",
    "integration_test",
    "e2e_test",
    "table_driven_test",
    "command",
    "mixed",
}
TASK_PLAN_SCHEMA_VERSION_LEGACY = 2
TASK_PLAN_SCHEMA_VERSION_CURRENT = 3
TASK_PLAN_SCHEMA_VERSIONS = {TASK_PLAN_SCHEMA_VERSION_LEGACY, TASK_PLAN_SCHEMA_VERSION_CURRENT}
TASK_PLAN_CONCEPTUALIZE_SCHEMA_VERSION = 3
PACKAGE_PROOF_SCHEMA_VERSION = 1
PACKAGE_LIFECYCLE_FIELD = "lifecycle"
PACKAGE_LIFECYCLE_STATES = {"accepted", "reopened"}
PACKAGE_LIFECYCLE_WRITER_SCHEMA_VERSION = 1
PACKAGE_LIFECYCLE_WRITER_TOOL = "taskctl.py"
PACKAGE_PROOF_DIGEST_RE = re.compile(r"^sha256:[0-9a-fA-F]{64}$")
PACKAGE_LIFECYCLE_TRANSITIONS = {
    "none": {"accepted"},
    "accepted": {"reopened"},
    "reopened": {"accepted"},
}
PACKAGE_LIFECYCLE_FORBIDDEN_ROOT_FIELDS = {
    "event_log",
    "events",
    "finalization",
    "finalized_at",
    "generated_checklist",
    "generated_checklists",
    "history",
    "lifecycle_history",
    "proof_history",
    "targeted_review_state",
    "workflow_engine_state",
    "workflow_state",
}
VAGUE_MANUAL_VALUES = {
    "approved",
    "approval",
    "done",
    "good",
    "looks good",
    "manual approval",
    "n/a",
    "na",
    "none",
    "ok",
    "passed",
    "verified",
    "yes",
}
STATE_REFERENCE_MARKERS = (
    "/",
    ":",
    ".json",
    ".md",
    ".py",
    "artifact",
    "command",
    "commit",
    "evidence",
    "file",
    "ledger",
    "proof",
    "test",
    "verification",
)
TARGETED_REVIEW_EVIDENCE_SUMMARY = (
    "compact state-bound receipt: reviewed integrated commit/range, review depth/lenses, "
    "explicit test scope, baseline security/privacy/safety sniff, serious finding "
    "count/closure, and repair/delta-verification closure when applicable"
)
TARGETED_REVIEW_EVIDENCE_MAX_CHARS = 800
TARGETED_REVIEW_STALE_MARKERS = (
    "stale",
    "pre-repair",
    "pre repair",
    "before repair",
    "unverified repair",
    "open repair",
    "open finding",
)
TARGETED_REVIEW_EVIDENCE_CLAUSE_RE = re.compile(r"[.;,]+")
TARGETED_REVIEW_SERIOUS_FINDING_TRAILING_SECTION_RE = re.compile(
    r"\b(?:repairs?|delta(?:[- ]verification)?)\b"
)
TARGETED_REVIEW_SERIOUS_FINDING_UNCLOSED_RE = re.compile(
    r"\b(?:"
    r"pending|open|unresolved|unclosed|unverified|"
    r"not[- ]closed|not[- ]verified|not[- ]resolved"
    r")\b"
)
TARGETED_REVIEW_SERIOUS_FINDING_ABSENCE_RE = re.compile(r"\b(?:0|zero|none|no)\b")
TARGETED_REVIEW_SERIOUS_FINDING_COUNT_RE = re.compile(r"\b\d+\b")
TARGETED_REVIEW_SERIOUS_FINDING_CLOSURE_RE = re.compile(r"\b(?:closed|closure|verified)\b")
TARGETED_REVIEW_UNCLOSED_REPAIR_DELTA_RE = re.compile(
    r"\b(?:"
    r"(?:repairs?|delta(?:[- ]verification)?)\b[^.;,]*\b"
    r"(?:pending|not closed|not verified|unverified|unresolved|not resolved|open)\b"
    r"|(?:pending|not closed|not verified|unverified|unresolved|not resolved|open)\b"
    r"[^.;,]*\b(?:repairs?|delta(?:[- ]verification)?)\b"
    r")"
)
TARGETED_REVIEW_REPAIR_CLOSURE_PHRASES = (
    "repairs none",
    "repair none",
    "no repairs",
    "repairs closed",
    "repair closed",
)
TARGETED_REVIEW_DELTA_CLOSURE_PHRASES = (
    "delta verification verified",
    "delta-verification verified",
    "delta verification not applicable",
    "delta-verification not applicable",
    "delta verification n/a",
    "delta-verification n/a",
)

RISK_TAGS = {
    "security",
    "privacy",
    "safety",
    "persistence",
    "data-integrity",
    "migration",
    "runtime-contract",
    "library-contract",
    "public-api",
    "exported-types",
    "concurrency",
    "idempotency",
    "replay",
    "performance",
    "resource-bounds",
    "cross-package-integration",
    "schema",
    "traceability",
    "validation",
    "orchestration",
    "git-state",
    "integration",
    "subagent-contract",
    "review",
    "audit",
    "fix-loop",
    "quality-contract",
    "documentation",
    "consistency",
    "validation-samples",
    "docs",
}

TARGETED_REVIEW_RISK_TAGS = {
    "security",
    "privacy",
    "safety",
    "persistence",
    "data-integrity",
    "migration",
    "runtime-contract",
    "library-contract",
    "public-api",
    "exported-types",
    "concurrency",
    "idempotency",
    "replay",
    "performance",
    "resource-bounds",
    "cross-package-integration",
    "schema",
    "traceability",
    "validation",
    "orchestration",
    "git-state",
    "integration",
    "subagent-contract",
    "review",
    "audit",
    "fix-loop",
    "quality-contract",
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate super-developer task plans and optional package proof final gates."
    )
    parser.add_argument("path", help="Path to .tasks/<feature>/tasks.json")
    parser.add_argument(
        "--final",
        action="store_true",
        help="Also validate accepted package proofs as a final/audit gate.",
    )
    parser.add_argument(
        "--worktree",
        help="Worktree used for stale-evidence checks (defaults to current directory).",
    )
    args = parser.parse_args()

    tasks_path = Path(args.path)
    try:
        with tasks_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: file not found: {tasks_path}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}", file=sys.stderr)
        return 2
    except (OSError, UnicodeDecodeError) as exc:
        print(f"ERROR: unable to read tasks.json: {exc}", file=sys.stderr)
        return 2

    spec_path = tasks_path.with_name("SPEC.md")
    errors, plan_index = validate_tasks_json(data, tasks_path=tasks_path, spec_path=spec_path)

    if args.final:
        errors.extend(validate_final_task_lifecycle(data, plan_index))
        errors.extend(
            validate_final_package_proofs(
                tasks_path,
                plan_index,
                worktree=Path(args.worktree) if args.worktree else Path.cwd(),
            )
        )

    if errors:
        print(f"ERROR: tasks.json validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"  - {error}")
        return 1

    if args.final:
        print("OK: tasks.json and package proofs are valid")
    else:
        print("OK: tasks.json is valid")
    return 0


def validate_tasks_json(
    data: Any, *, tasks_path: Path | None = None, spec_path: Path | None = None
) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    plan_index: dict[str, Any] = {
        "feature": None,
        "schema_version": TASK_PLAN_SCHEMA_VERSION_CURRENT,
        "feature_status": None,
        "task_ids": set(),
        "task_ac_ids": set(),
        "task_ac_sources": {},
        "task_statuses": {},
        "task_required_context_bundles": {},
        "task_to_package": {},
        "package_ids": set(),
        "package_required_context_bundles": {},
        "package_to_tasks": {},
        "package_targeted_review_required": {},
        "package_verification_commands": {},
        "context_bundle_ids": set(),
    }
    if not isinstance(data, dict):
        return ["root: expected JSON object"], plan_index

    schema_version = validate_schema_version(data, errors)
    plan_index["schema_version"] = schema_version
    plan_index["feature"] = data.get("feature")
    plan_index["feature_status"] = data.get("status")

    validate_top_level(data, errors, schema_version=schema_version)
    if "context_bundles" not in data:
        errors.append("context_bundles: expected array")
    context_bundle_ids = validate_context_bundles(
        data.get("context_bundles", []), errors, required=True
    )
    plan_index["context_bundle_ids"] = context_bundle_ids

    phases = data.get("phases")
    work_packages = data.get("work_packages")

    task_ids: set[str] = set()
    task_dependencies: dict[str, list[str]] = {}
    task_phase_order: dict[str, int] = {}
    task_statuses: dict[str, str] = {}
    task_ac_ids: set[str] = set()
    task_ac_sources: dict[str, list[dict[str, str]]] = {}
    task_required_context_bundles: dict[str, set[str]] = {}

    design_decision_ids = collect_design_decision_ids(data.get("design_decisions"))

    if isinstance(phases, list):
        validate_phases(
            phases,
            errors,
            task_ids,
            task_dependencies,
            task_phase_order,
            task_statuses,
            task_ac_ids=task_ac_ids,
            task_ac_sources=task_ac_sources,
            task_required_context_bundles=task_required_context_bundles,
            design_decision_ids=design_decision_ids,
            context_bundle_ids=context_bundle_ids,
        )
    else:
        errors.append("phases: expected array")

    if isinstance(work_packages, list):
        task_to_package = validate_work_packages(
            work_packages,
            errors,
            task_ids,
            task_dependencies,
            context_bundle_ids=context_bundle_ids,
            schema_version=schema_version,
        )
        plan_index["task_to_package"] = task_to_package
        index_work_packages(work_packages, plan_index)
    else:
        errors.append("work_packages: expected array")

    validate_task_dependencies(task_dependencies, task_ids, task_phase_order, errors)

    spec_ids = parse_spec_ids(spec_path, errors) if spec_path else {"spec_req": set(), "spec_ac": set()}
    validate_source_ref_targets(
        task_ac_sources,
        errors,
        spec_ids=spec_ids,
        design_decision_ids=design_decision_ids,
        context_bundle_ids=context_bundle_ids,
    )
    validate_slice_coverage_ref_targets(
        data.get("conceptualize"),
        errors,
        spec_ids=spec_ids,
        task_ac_ids=task_ac_ids,
        design_decision_ids=design_decision_ids,
        context_bundle_ids=context_bundle_ids,
    )
    validate_spec_coverage(task_ac_sources, spec_ids, errors)
    if isinstance(work_packages, list):
        validate_context_bundle_consumers(
            data.get("context_bundles", []),
            work_packages,
            phases if isinstance(phases, list) else [],
            task_ids,
            errors,
            task_ac_sources,
        )

    plan_index["task_ids"] = task_ids
    plan_index["task_statuses"] = task_statuses
    plan_index["task_ac_ids"] = task_ac_ids
    plan_index["task_ac_sources"] = task_ac_sources
    plan_index["task_required_context_bundles"] = task_required_context_bundles
    return errors, plan_index


def validate_schema_version(data: dict[str, Any], errors: list[str]) -> int:
    value = data.get("schema_version")
    if isinstance(value, bool) or not isinstance(value, int):
        errors.append("schema_version: expected integer 2 or 3")
        return TASK_PLAN_SCHEMA_VERSION_CURRENT
    if value not in TASK_PLAN_SCHEMA_VERSIONS:
        expected = sorted(TASK_PLAN_SCHEMA_VERSIONS)
        errors.append(f"schema_version: expected one of {expected}, got {value!r}")
        return TASK_PLAN_SCHEMA_VERSION_CURRENT
    return value


def validate_top_level(
    data: dict[str, Any], errors: list[str], *, schema_version: int
) -> None:
    for field in ("feature", "title", "description", "created_at", "status"):
        require_non_empty_string(data, field, field, errors)

    status = data.get("status")
    if isinstance(status, str) and status not in FEATURE_STATUSES:
        errors.append(
            f"status: expected one of {sorted(FEATURE_STATUSES)}, got {status!r}"
        )

    created_at = data.get("created_at")
    if isinstance(created_at, str) and created_at.strip():
        validate_iso_datetime(created_at, "created_at", errors)

    if schema_version >= TASK_PLAN_CONCEPTUALIZE_SCHEMA_VERSION or "conceptualize" in data:
        validate_conceptualize(
            data.get("conceptualize"),
            "conceptualize",
            errors,
            schema_version=schema_version,
        )

    if "design_decisions" not in data:
        errors.append("design_decisions: expected array")
        return

    design_decisions = data["design_decisions"]
    if not isinstance(design_decisions, list):
        errors.append("design_decisions: expected array")
        return
    validate_design_decisions(design_decisions, errors)


def validate_conceptualize(
    value: Any, path: str, errors: list[str], *, schema_version: int
) -> None:
    if not isinstance(value, dict):
        errors.append(f"{path}: expected object")
        return
    require_non_empty_string(value, "index", f"{path}.index", errors)
    if schema_version >= TASK_PLAN_CONCEPTUALIZE_SCHEMA_VERSION:
        validate_slice_coverage(
            value.get("slice_coverage"), f"{path}.slice_coverage", errors, required=True
        )
    elif "slice_coverage" in value:
        validate_slice_coverage(
            value.get("slice_coverage"), f"{path}.slice_coverage", errors, required=False
        )


def validate_slice_coverage(
    value: Any, path: str, errors: list[str], *, required: bool
) -> None:
    if value is None and not required:
        return
    if not isinstance(value, dict):
        errors.append(f"{path}: expected object")
        return

    state = value.get("state")
    if not isinstance(state, str) or state not in SLICE_COVERAGE_STATES:
        errors.append(
            f"{path}.state: expected one of {sorted(SLICE_COVERAGE_STATES)}, got {state!r}"
        )

    entries = value.get("entries")
    if not isinstance(entries, list):
        errors.append(f"{path}.entries: expected array")
        entries = []

    rationale = value.get("rationale")
    if state == "zero_slices":
        if entries:
            errors.append(f"{path}.entries: expected empty array when state is 'zero_slices'")
        require_non_empty_string(value, "rationale", f"{path}.rationale", errors)
    elif state == "covered":
        if not entries:
            errors.append(f"{path}.entries: expected at least one item when state is 'covered'")
        if rationale is not None and (not isinstance(rationale, str) or not rationale.strip()):
            errors.append(f"{path}.rationale: expected non-empty string when present")
    elif rationale is not None and (not isinstance(rationale, str) or not rationale.strip()):
        errors.append(f"{path}.rationale: expected non-empty string when present")

    entry_paths: list[str] = []
    for index, entry in enumerate(entries):
        entry_path = f"{path}.entries[{index}]"
        slice_path = validate_slice_coverage_entry(entry, entry_path, errors)
        if slice_path is not None:
            entry_paths.append(slice_path)
    add_duplicate_errors(entry_paths, "Slice coverage path", f"{path}.entries", errors)


def validate_slice_coverage_entry(entry: Any, path: str, errors: list[str]) -> str | None:
    if not isinstance(entry, dict):
        errors.append(f"{path}: expected object")
        return None

    slice_path: str | None = None
    if require_non_empty_string(entry, "path", f"{path}.path", errors):
        slice_path = entry["path"]

    disposition = entry.get("disposition")
    if not isinstance(disposition, str) or disposition not in SLICE_COVERAGE_DISPOSITIONS:
        errors.append(
            f"{path}.disposition: expected one of {sorted(SLICE_COVERAGE_DISPOSITIONS)}, got {disposition!r}"
        )
        disposition = None

    rationale = entry.get("rationale")
    if "promoted_refs" in entry:
        errors.append(
            f"{path}.promoted_refs: legacy PR-only field is not accepted; use projected_refs"
        )

    if disposition == "projected":
        if rationale is not None and (not isinstance(rationale, str) or not rationale.strip()):
            errors.append(f"{path}.rationale: expected non-empty string when present")
        validate_slice_coverage_ref_array(
            entry.get("projected_refs"),
            f"{path}.projected_refs",
            errors,
            required=True,
        )
    else:
        require_non_empty_string(entry, "rationale", f"{path}.rationale", errors)
        if "projected_refs" in entry:
            validate_slice_coverage_ref_array(
                entry.get("projected_refs"),
                f"{path}.projected_refs",
                errors,
                required=False,
            )

    approval_required = disposition in SLICE_COVERAGE_SCOPE_REDUCING_DISPOSITIONS
    if approval_required or "approval" in entry:
        validate_slice_coverage_approval(
            entry.get("approval"),
            f"{path}.approval",
            errors,
            required=approval_required,
        )

    return slice_path


def validate_slice_coverage_approval(
    value: Any, path: str, errors: list[str], *, required: bool
) -> None:
    if value is None and not required:
        return
    if not isinstance(value, dict):
        errors.append(f"{path}: expected object")
        return
    for field in ("source", "approved_at", "provenance", "scope"):
        require_non_empty_string(value, field, f"{path}.{field}", errors)
    approved_at = value.get("approved_at")
    if isinstance(approved_at, str) and approved_at.strip():
        validate_iso_datetime(approved_at, f"{path}.approved_at", errors)
    if "refs" in value:
        validate_slice_coverage_ref_array(
            value.get("refs"), f"{path}.refs", errors, required=False
        )


def validate_slice_coverage_ref_array(
    refs: Any, path: str, errors: list[str], *, required: bool
) -> None:
    if refs is None and not required:
        return
    if not isinstance(refs, list):
        errors.append(f"{path}: expected array")
        return
    if not refs:
        errors.append(f"{path}: expected at least one item")
        return
    for index, ref in enumerate(refs):
        validate_slice_coverage_ref(ref, f"{path}[{index}]", errors)


def validate_slice_coverage_ref(ref: Any, path: str, errors: list[str]) -> dict[str, str] | None:
    if not isinstance(ref, dict):
        errors.append(f"{path}: expected object")
        return None
    ref_type = ref.get("type")
    ref_id = ref.get("id")
    if not isinstance(ref_type, str) or ref_type not in SLICE_COVERAGE_REF_TYPES:
        errors.append(
            f"{path}.type: expected one of {sorted(SLICE_COVERAGE_REF_TYPES)}, got {ref_type!r}"
        )
        return None
    if not isinstance(ref_id, str) or not ref_id.strip():
        errors.append(f"{path}.id: expected non-empty string")
        return None
    return {"type": ref_type, "id": ref_id}


def collect_design_decision_ids(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    ids: set[str] = set()
    for decision in value:
        if isinstance(decision, dict) and isinstance(decision.get("id"), str):
            ids.add(decision["id"])
    return ids


def validate_design_decisions(
    design_decisions: list[Any], errors: list[str]
) -> None:
    decision_ids: list[str] = []
    for index, decision in enumerate(design_decisions):
        path = f"design_decisions[{index}]"
        if not isinstance(decision, dict):
            errors.append(f"{path}: expected object")
            continue

        for field in ("id", "decision", "rationale", "source"):
            require_non_empty_string(decision, field, f"{path}.{field}", errors)

        decision_id = decision.get("id")
        if isinstance(decision_id, str) and decision_id.strip():
            if not DESIGN_DECISION_ID_RE.fullmatch(decision_id):
                errors.append(f"{path}.id: expected DD-<N>, got {decision_id!r}")
            decision_ids.append(decision_id)

        source = decision.get("source")
        if isinstance(source, str) and source not in DESIGN_DECISION_SOURCES:
            errors.append(
                f"{path}.source: expected one of {sorted(DESIGN_DECISION_SOURCES)}, got {source!r}"
            )

        alternatives = decision.get("alternatives_considered")
        if not isinstance(alternatives, list):
            errors.append(f"{path}.alternatives_considered: expected array")
        elif not all(isinstance(item, str) for item in alternatives):
            errors.append(f"{path}.alternatives_considered: expected string array")

    add_duplicate_errors(decision_ids, "design decision id", "design_decisions", errors)
    validate_sequential_ids(decision_ids, "DD-", "design_decisions", errors)


def validate_context_bundles(value: Any, errors: list[str], *, required: bool) -> set[str]:
    if value is None and not required:
        return set()
    if not isinstance(value, list):
        if required:
            errors.append("context_bundles: expected array")
        return set()

    bundle_ids: list[str] = []
    for index, bundle in enumerate(value):
        path = f"context_bundles[{index}]"
        if not isinstance(bundle, dict):
            errors.append(f"{path}: expected object")
            continue
        for field in ("id", "title"):
            require_non_empty_string(bundle, field, f"{path}.{field}", errors)
        bundle_id = bundle.get("id")
        if isinstance(bundle_id, str) and bundle_id.strip():
            if not CONTEXT_BUNDLE_ID_RE.fullmatch(bundle_id):
                errors.append(f"{path}.id: expected CTX-<N>, got {bundle_id!r}")
            bundle_ids.append(bundle_id)

        required_for = require_string_list(
            bundle, "required_for", f"{path}.required_for", errors
        )
        for ref in required_for:
            if not (WORK_PACKAGE_ID_RE.fullmatch(ref) or TASK_ID_RE.fullmatch(ref)):
                errors.append(
                    f"{path}.required_for: expected WP<N> or task id, got {ref!r}"
                )

        sources = bundle.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{path}.sources: expected non-empty array")
        else:
            for source_index, source in enumerate(sources):
                source_path = f"{path}.sources[{source_index}]"
                if not isinstance(source, dict):
                    errors.append(f"{source_path}: expected object")
                    continue
                source_type = source.get("type")
                if not isinstance(source_type, str) or source_type not in BUNDLE_SOURCE_TYPES:
                    errors.append(
                        f"{source_path}.type: expected one of {sorted(BUNDLE_SOURCE_TYPES)}, got {source_type!r}"
                    )
                require_non_empty_string(
                    source, "path_or_url", f"{source_path}.path_or_url", errors
                )
                claims = require_string_list(
                    source, "claims", f"{source_path}.claims", errors
                )
                if not claims:
                    errors.append(f"{source_path}.claims: expected at least one item")

        verification_required = require_string_list(
            bundle,
            "verification_required",
            f"{path}.verification_required",
            errors,
        )
        if not verification_required:
            errors.append(f"{path}.verification_required: expected at least one item")

    add_duplicate_errors(bundle_ids, "context bundle id", "context_bundles", errors)
    validate_sequential_ids(bundle_ids, "CTX-", "context_bundles", errors)
    return set(bundle_ids)

def validate_context_bundle_consumers(
    bundles: Any,
    work_packages: list[Any],
    phases: list[Any],
    task_ids: set[str],
    errors: list[str],
    task_ac_sources: dict[str, list[dict[str, str]]],
) -> None:
    if not isinstance(bundles, list):
        return

    def string_set(value: Any) -> set[str]:
        if not isinstance(value, list):
            return set()
        return {item for item in value if isinstance(item, str)}

    package_ids = {
        package.get("id")
        for package in work_packages
        if isinstance(package, dict) and isinstance(package.get("id"), str)
    }
    package_tasks = {
        package["id"]: string_set(package.get("task_ids"))
        for package in work_packages
        if isinstance(package, dict) and isinstance(package.get("id"), str)
    }
    task_to_package = {
        task_id: package_id
        for package_id, package_task_ids in package_tasks.items()
        for task_id in package_task_ids
    }
    package_bundle_refs = {
        package["id"]: string_set(package.get("required_context_bundles"))
        for package in work_packages
        if isinstance(package, dict) and isinstance(package.get("id"), str)
    }
    task_bundle_refs: dict[str, set[str]] = {}
    for phase in phases:
        if not isinstance(phase, dict) or not isinstance(phase.get("tasks"), list):
            continue
        for task in phase["tasks"]:
            if isinstance(task, dict) and isinstance(task.get("id"), str):
                task_bundle_refs[task["id"]] = string_set(task.get("required_context_bundles"))
    bundle_required_for: dict[str, set[str]] = {}
    for index, bundle in enumerate(bundles):
        if not isinstance(bundle, dict) or not isinstance(bundle.get("id"), str):
            continue
        refs = string_set(bundle.get("required_for"))
        bundle_required_for[bundle["id"]] = refs
        for ref in refs:
            if ref not in package_ids and ref not in task_ids:
                errors.append(
                    f"context_bundles[{index}].required_for: unknown package/task reference {ref!r}"
                )
            elif ref in package_ids and bundle["id"] not in package_bundle_refs.get(ref, set()):
                errors.append(
                    f"context_bundles[{index}].required_for: package {ref!r} must include {bundle['id']!r} in required_context_bundles"
                )
            elif ref in task_ids:
                containing_package = task_to_package.get(ref)
                if (
                    bundle["id"] not in task_bundle_refs.get(ref, set())
                    and bundle["id"] not in package_bundle_refs.get(containing_package, set())
                ):
                    errors.append(
                        f"context_bundles[{index}].required_for: task {ref!r} or containing package must include {bundle['id']!r} in required_context_bundles"
                    )

    for ac_id, refs in task_ac_sources.items():
        task_id = ac_id.rsplit("-AC", 1)[0]
        containing_package = task_to_package.get(task_id)
        for ref in refs:
            if ref.get("type") != "context_bundle":
                continue
            bundle_id = ref.get("id")
            if not isinstance(bundle_id, str):
                continue
            if (
                bundle_id not in task_bundle_refs.get(task_id, set())
                and bundle_id not in package_bundle_refs.get(containing_package, set())
            ):
                errors.append(
                    f"acceptance criterion {ac_id}: context_bundle source_ref {bundle_id!r} must be listed in the task or containing package required_context_bundles"
                )
            required_for = bundle_required_for.get(bundle_id, set())
            if task_id not in required_for and containing_package not in required_for:
                errors.append(
                    f"acceptance criterion {ac_id}: context_bundle source_ref {bundle_id!r} must list {task_id!r} or containing package in context_bundles[].required_for"
                )

    for package in work_packages:
        if not isinstance(package, dict) or not isinstance(package.get("id"), str):
            continue
        package_id = package["id"]
        package_task_ids = package_tasks.get(package_id, set())
        bundle_refs = string_set(package.get("required_context_bundles"))
        for bundle_ref in bundle_refs:
            refs = bundle_required_for.get(bundle_ref, set())
            if package_id not in refs and not (package_task_ids & refs):
                errors.append(
                    f"work package {package_id}: required_context_bundles {bundle_ref!r} must list {package_id!r} or one contained task in context_bundles[].required_for"
                )

    for phase in phases:
        if not isinstance(phase, dict) or not isinstance(phase.get("tasks"), list):
            continue
        for task in phase["tasks"]:
            if not isinstance(task, dict) or not isinstance(task.get("id"), str):
                continue
            task_id = task["id"]
            bundle_refs = string_set(task.get("required_context_bundles"))
            for bundle_ref in bundle_refs:
                refs = bundle_required_for.get(bundle_ref, set())
                if task_id not in refs and task_to_package.get(task_id) not in refs:
                    errors.append(
                        f"task {task_id}: required_context_bundles {bundle_ref!r} must list {task_id!r} or containing package in context_bundles[].required_for"
                    )


def validate_phases(
    phases: list[Any],
    errors: list[str],
    task_ids: set[str],
    task_dependencies: dict[str, list[str]],
    task_phase_order: dict[str, int],
    task_statuses: dict[str, str],
    task_ac_ids: set[str],
    task_ac_sources: dict[str, list[dict[str, str]]],
    task_required_context_bundles: dict[str, set[str]],
    design_decision_ids: set[str],
    context_bundle_ids: set[str],
) -> None:
    phase_ids: list[str] = []
    phase_orders: list[int] = []

    for phase_index, phase in enumerate(phases):
        phase_path = f"phases[{phase_index}]"
        if not isinstance(phase, dict):
            errors.append(f"{phase_path}: expected object")
            continue

        for field in ("id", "name", "description"):
            require_non_empty_string(phase, field, f"{phase_path}.{field}", errors)

        phase_id = phase.get("id")
        if isinstance(phase_id, str) and phase_id.strip():
            if not PHASE_ID_RE.fullmatch(phase_id):
                errors.append(f"{phase_path}.id: expected P<N>, got {phase_id!r}")
            phase_ids.append(phase_id)

        order = phase.get("order")
        if isinstance(order, bool) or not isinstance(order, int):
            errors.append(f"{phase_path}.order: expected integer")
        else:
            phase_orders.append(order)

        tasks = phase.get("tasks")
        if not isinstance(tasks, list):
            errors.append(f"{phase_path}.tasks: expected array")
            continue

        for task_index, task in enumerate(tasks):
            validate_task(
                task,
                f"{phase_path}.tasks[{task_index}]",
                phase_id if isinstance(phase_id, str) else None,
                order if isinstance(order, int) else phase_index + 1,
                errors,
                task_ids,
                task_dependencies,
                task_phase_order,
                task_statuses,
                task_ac_ids=task_ac_ids,
                task_ac_sources=task_ac_sources,
                task_required_context_bundles=task_required_context_bundles,
                design_decision_ids=design_decision_ids,
                context_bundle_ids=context_bundle_ids,
            )

    add_duplicate_errors(phase_ids, "phase id", "phases", errors)
    validate_sequential_ids(phase_ids, "P", "phases", errors)
    validate_sequential_orders(phase_orders, "phases[].order", errors)


def validate_task(
    task: Any,
    task_path: str,
    phase_id: str | None,
    phase_order: int,
    errors: list[str],
    task_ids: set[str],
    task_dependencies: dict[str, list[str]],
    task_phase_order: dict[str, int],
    task_statuses: dict[str, str],
    task_ac_ids: set[str],
    task_ac_sources: dict[str, list[dict[str, str]]],
    task_required_context_bundles: dict[str, set[str]],
    design_decision_ids: set[str],
    context_bundle_ids: set[str],
) -> None:
    if not isinstance(task, dict):
        errors.append(f"{task_path}: expected object")
        return

    for field in ("id", "title", "description", "status", "context"):
        require_non_empty_string(task, field, f"{task_path}.{field}", errors)

    task_id = task.get("id")
    if isinstance(task_id, str) and task_id.strip():
        match = TASK_ID_RE.fullmatch(task_id)
        if not match:
            errors.append(f"{task_path}.id: expected <PhaseID>-T<NNN>, got {task_id!r}")
        elif phase_id is not None and match.group(1) != phase_id:
            errors.append(
                f"{task_path}.id: task id phase {match.group(1)!r} does not match {phase_id!r}"
            )

        if task_id in task_ids:
            errors.append(f"{task_path}.id: duplicate task id {task_id!r}")
        task_ids.add(task_id)
        task_phase_order[task_id] = phase_order

    status = task.get("status")
    if isinstance(status, str) and status not in TASK_STATUSES:
        errors.append(
            f"{task_path}.status: expected one of {sorted(TASK_STATUSES)}, got {status!r}"
        )
    if isinstance(task_id, str) and task_id.strip() and isinstance(status, str):
        task_statuses[task_id] = status
    if status == "done":
        if require_non_empty_string(
            task, "completed_at", f"{task_path}.completed_at", errors
        ):
            validate_iso_datetime(task["completed_at"], f"{task_path}.completed_at", errors)
    if status == "blocked":
        require_non_empty_string(
            task, "blocked_reason", f"{task_path}.blocked_reason", errors
        )

    dependencies = require_string_list(
        task, "dependencies", f"{task_path}.dependencies", errors
    )
    if isinstance(task_id, str) and task_id.strip():
        task_dependencies[task_id] = dependencies

    validate_structured_acceptance_criteria(
        task,
        task_path,
        task_id if isinstance(task_id, str) else None,
        errors,
        task_ac_ids,
        task_ac_sources,
    )
    bundle_refs = require_string_list(
        task,
        "required_context_bundles",
        f"{task_path}.required_context_bundles",
        errors,
        required=False,
    )
    for bundle_ref in bundle_refs:
        if bundle_ref not in context_bundle_ids:
            errors.append(
                f"{task_path}.required_context_bundles: unknown context bundle {bundle_ref!r}"
            )
    if isinstance(task_id, str) and task_id.strip():
        task_required_context_bundles[task_id] = set(bundle_refs)

def validate_structured_acceptance_criteria(
    task: dict[str, Any],
    task_path: str,
    task_id: str | None,
    errors: list[str],
    task_ac_ids: set[str],
    task_ac_sources: dict[str, list[dict[str, str]]],
) -> None:
    criteria = task.get("acceptance_criteria")
    if not isinstance(criteria, list):
        errors.append(f"{task_path}.acceptance_criteria: expected array")
        return
    if not criteria:
        errors.append(f"{task_path}.acceptance_criteria: expected at least one item")

    for index, criterion in enumerate(criteria):
        path = f"{task_path}.acceptance_criteria[{index}]"
        if not isinstance(criterion, dict):
            errors.append(f"{path}: expected object")
            continue
        for field in ("id", "criterion", "source_refs"):
            if field == "source_refs":
                continue
            require_non_empty_string(criterion, field, f"{path}.{field}", errors)

        ac_id = criterion.get("id")
        if isinstance(ac_id, str) and ac_id.strip():
            match = TASK_AC_ID_RE.fullmatch(ac_id)
            if not match:
                errors.append(f"{path}.id: expected <TaskID>-AC<N>, got {ac_id!r}")
            elif task_id is not None and match.group(1) != task_id:
                errors.append(
                    f"{path}.id: criterion id task {match.group(1)!r} does not match {task_id!r}"
                )
            if ac_id in task_ac_ids:
                errors.append(f"{path}.id: duplicate acceptance criterion id {ac_id!r}")
            task_ac_ids.add(ac_id)

        refs = criterion.get("source_refs")
        if not isinstance(refs, list) or not refs:
            errors.append(f"{path}.source_refs: expected non-empty array")
            parsed_refs: list[dict[str, str]] = []
        else:
            parsed_refs = []
            for ref_index, ref in enumerate(refs):
                parsed = validate_source_ref(ref, f"{path}.source_refs[{ref_index}]", errors)
                if parsed is not None:
                    parsed_refs.append(parsed)
        if isinstance(ac_id, str) and ac_id.strip():
            task_ac_sources[ac_id] = parsed_refs

        hint = criterion.get("verification_hint")
        if hint is not None and (not isinstance(hint, str) or not hint.strip()):
            errors.append(f"{path}.verification_hint: expected non-empty string when present")


def validate_source_ref(ref: Any, path: str, errors: list[str]) -> dict[str, str] | None:
    if not isinstance(ref, dict):
        errors.append(f"{path}: expected object")
        return None
    ref_type = ref.get("type")
    ref_id = ref.get("id")
    if not isinstance(ref_type, str) or ref_type not in SOURCE_REF_TYPES:
        errors.append(
            f"{path}.type: expected one of {sorted(SOURCE_REF_TYPES)}, got {ref_type!r}"
        )
        return None
    if not isinstance(ref_id, str) or not ref_id.strip():
        errors.append(f"{path}.id: expected non-empty string")
        return None
    return {"type": ref_type, "id": ref_id}


def parse_spec_ids(spec_path: Path | None, errors: list[str]) -> dict[str, set[str]]:
    ids = {"spec_req": set(), "spec_ac": set()}
    if spec_path is None:
        errors.append("SPEC.md: path unavailable for traceability validation")
        return ids
    if not spec_path.exists():
        errors.append(f"SPEC.md: expected sibling file at {spec_path}")
        return ids

    req_ids: list[str] = []
    ac_ids: list[str] = []
    try:
        spec_lines = spec_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"SPEC.md: unable to read {spec_path}: {exc}")
        return ids
    for line in spec_lines:
        req_match = SPEC_REQ_RE.match(line)
        if req_match:
            req_ids.append(req_match.group(1))
        ac_match = SPEC_AC_RE.match(line)
        if ac_match:
            ac_ids.append(ac_match.group(1))

    add_duplicate_errors(req_ids, "SPEC requirement id", "SPEC.md Requirements", errors)
    add_duplicate_errors(ac_ids, "SPEC acceptance criterion id", "SPEC.md Acceptance Criteria", errors)
    ids["spec_req"] = set(req_ids)
    ids["spec_ac"] = set(ac_ids)
    if not req_ids:
        errors.append("SPEC.md Requirements: expected at least one REQ-<N> id")
    if not ac_ids:
        errors.append("SPEC.md Acceptance Criteria: expected at least one AC-<N> id")
    return ids


def validate_source_ref_targets(
    task_ac_sources: dict[str, list[dict[str, str]]],
    errors: list[str],
    *,
    spec_ids: dict[str, set[str]],
    design_decision_ids: set[str],
    context_bundle_ids: set[str],
) -> None:
    for ac_id, refs in task_ac_sources.items():
        for ref in refs:
            ref_type = ref["type"]
            ref_id = ref["id"]
            if ref_type == "spec_req" and ref_id not in spec_ids["spec_req"]:
                errors.append(f"acceptance criterion {ac_id}: unknown SPEC requirement {ref_id!r}")
            elif ref_type == "spec_ac" and ref_id not in spec_ids["spec_ac"]:
                errors.append(f"acceptance criterion {ac_id}: unknown SPEC acceptance criterion {ref_id!r}")
            elif ref_type == "design_decision" and ref_id not in design_decision_ids:
                errors.append(f"acceptance criterion {ac_id}: unknown design decision {ref_id!r}")
            elif ref_type == "context_bundle" and ref_id not in context_bundle_ids:
                errors.append(f"acceptance criterion {ac_id}: unknown context bundle {ref_id!r}")


def validate_slice_coverage_ref_targets(
    conceptualize: Any,
    errors: list[str],
    *,
    spec_ids: dict[str, set[str]],
    task_ac_ids: set[str],
    design_decision_ids: set[str],
    context_bundle_ids: set[str],
) -> None:
    if not isinstance(conceptualize, dict):
        return
    coverage = conceptualize.get("slice_coverage")
    if not isinstance(coverage, dict):
        return
    entries = coverage.get("entries")
    if not isinstance(entries, list):
        return

    for entry_index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        entry_path = f"conceptualize.slice_coverage.entries[{entry_index}]"
        projected_refs = entry.get("projected_refs")
        if isinstance(projected_refs, list):
            for ref_index, ref in enumerate(projected_refs):
                parsed = normalized_slice_coverage_ref(ref)
                if parsed is not None:
                    validate_slice_coverage_ref_target(
                        parsed,
                        f"{entry_path}.projected_refs[{ref_index}]",
                        errors,
                        spec_ids=spec_ids,
                        task_ac_ids=task_ac_ids,
                        design_decision_ids=design_decision_ids,
                        context_bundle_ids=context_bundle_ids,
                    )
        approval = entry.get("approval")
        if not isinstance(approval, dict):
            continue
        approval_refs = approval.get("refs")
        if not isinstance(approval_refs, list):
            continue
        for ref_index, ref in enumerate(approval_refs):
            parsed = normalized_slice_coverage_ref(ref)
            if parsed is not None:
                validate_slice_coverage_ref_target(
                    parsed,
                    f"{entry_path}.approval.refs[{ref_index}]",
                    errors,
                    spec_ids=spec_ids,
                    task_ac_ids=task_ac_ids,
                    design_decision_ids=design_decision_ids,
                    context_bundle_ids=context_bundle_ids,
                )


def normalized_slice_coverage_ref(ref: Any) -> dict[str, str] | None:
    if not isinstance(ref, dict):
        return None
    ref_type = ref.get("type")
    ref_id = ref.get("id")
    if (
        isinstance(ref_type, str)
        and ref_type in SLICE_COVERAGE_REF_TYPES
        and isinstance(ref_id, str)
        and ref_id.strip()
    ):
        return {"type": ref_type, "id": ref_id}
    return None


def validate_slice_coverage_ref_target(
    ref: dict[str, str],
    path: str,
    errors: list[str],
    *,
    spec_ids: dict[str, set[str]],
    task_ac_ids: set[str],
    design_decision_ids: set[str],
    context_bundle_ids: set[str],
) -> None:
    ref_type = ref["type"]
    ref_id = ref["id"]
    if ref_type == "spec_req" and ref_id not in spec_ids["spec_req"]:
        errors.append(f"{path}: unknown SPEC requirement {ref_id!r}")
    elif ref_type == "spec_ac" and ref_id not in spec_ids["spec_ac"]:
        errors.append(f"{path}: unknown SPEC acceptance criterion {ref_id!r}")
    elif ref_type == "task_ac" and ref_id not in task_ac_ids:
        errors.append(f"{path}: unknown task acceptance criterion {ref_id!r}")
    elif ref_type == "design_decision" and ref_id not in design_decision_ids:
        errors.append(f"{path}: unknown design decision {ref_id!r}")
    elif ref_type == "context_bundle" and ref_id not in context_bundle_ids:
        errors.append(f"{path}: unknown context bundle {ref_id!r}")


def validate_spec_coverage(
    task_ac_sources: dict[str, list[dict[str, str]]],
    spec_ids: dict[str, set[str]],
    errors: list[str],
) -> None:
    covered_req = {
        ref["id"]
        for refs in task_ac_sources.values()
        for ref in refs
        if ref["type"] == "spec_req"
    }
    covered_ac = {
        ref["id"]
        for refs in task_ac_sources.values()
        for ref in refs
        if ref["type"] == "spec_ac"
    }
    for req_id in sorted(spec_ids["spec_req"] - covered_req):
        errors.append(f"SPEC requirement {req_id}: not covered by any task acceptance criterion")
    for ac_id in sorted(spec_ids["spec_ac"] - covered_ac):
        errors.append(f"SPEC acceptance criterion {ac_id}: not covered by any task acceptance criterion")


def validate_task_dependencies(
    task_dependencies: dict[str, list[str]],
    task_ids: set[str],
    task_phase_order: dict[str, int],
    errors: list[str],
) -> None:
    for task_id, dependencies in task_dependencies.items():
        for duplicate in duplicates(dependencies):
            errors.append(f"task {task_id}: duplicate dependency {duplicate!r}")
        for dependency in dependencies:
            if dependency == task_id:
                errors.append(f"task {task_id}: must not depend on itself")
            elif dependency not in task_ids:
                errors.append(f"task {task_id}: unknown dependency {dependency!r}")
            elif task_phase_order.get(dependency, 0) > task_phase_order.get(task_id, 0):
                errors.append(
                    f"task {task_id}: depends on future-phase task {dependency!r}"
                )

    cycle = find_cycle(task_dependencies)
    if cycle:
        errors.append(f"task dependencies contain cycle: {' -> '.join(cycle)}")


def validate_work_packages(
    work_packages: list[Any],
    errors: list[str],
    task_ids: set[str],
    task_dependencies: dict[str, list[str]],
    context_bundle_ids: set[str],
    *,
    schema_version: int,
) -> dict[str, str]:
    package_ids: list[str] = []
    package_task_refs: dict[str, list[str]] = {}
    package_dependencies: dict[str, list[str]] = {}
    package_parallel: dict[str, list[str]] = {}

    for package_index, package in enumerate(work_packages):
        package_path = f"work_packages[{package_index}]"
        if not isinstance(package, dict):
            errors.append(f"{package_path}: expected object")
            continue

        for field in ("id", "title", "description", "rationale"):
            require_non_empty_string(package, field, f"{package_path}.{field}", errors)

        package_id = package.get("id")
        if isinstance(package_id, str) and package_id.strip():
            if not WORK_PACKAGE_ID_RE.fullmatch(package_id):
                errors.append(
                    f"{package_path}.id: expected WP<N>, got {package_id!r}"
                )
            package_ids.append(package_id)

        task_refs = require_string_list(
            package, "task_ids", f"{package_path}.task_ids", errors
        )
        depends_on = require_string_list(
            package, "depends_on", f"{package_path}.depends_on", errors
        )
        parallel_safe_with = require_string_list(
            package,
            "parallel_safe_with",
            f"{package_path}.parallel_safe_with",
            errors,
        )
        require_string_list(
            package, "primary_paths", f"{package_path}.primary_paths", errors
        )
        require_string_list(
            package,
            "verification_commands",
            f"{package_path}.verification_commands",
            errors,
        )

        validate_package_v2_fields(
            package,
            package_path,
            errors,
            context_bundle_ids=context_bundle_ids,
        )
        if (
            schema_version >= TASK_PLAN_CONCEPTUALIZE_SCHEMA_VERSION
            or "conceptualize_slices" in package
        ):
            validate_conceptualize_slices(
                package.get("conceptualize_slices"),
                f"{package_path}.conceptualize_slices",
                errors,
            )

        if isinstance(package_id, str) and package_id.strip():
            package_task_refs[package_id] = task_refs
            package_dependencies[package_id] = depends_on
            package_parallel[package_id] = parallel_safe_with

        if not task_refs:
            errors.append(f"{package_path}.task_ids: expected at least one task id")
        if len(task_refs) == 1:
            require_non_empty_string(
                package, "rationale", f"{package_path}.rationale", errors
            )
        for duplicate in duplicates(task_refs):
            errors.append(f"{package_path}.task_ids: duplicate task id {duplicate!r}")
        for duplicate in duplicates(depends_on):
            errors.append(f"{package_path}.depends_on: duplicate package id {duplicate!r}")
        for duplicate in duplicates(parallel_safe_with):
            errors.append(
                f"{package_path}.parallel_safe_with: duplicate package id {duplicate!r}"
            )

    add_duplicate_errors(package_ids, "work package id", "work_packages", errors)
    validate_sequential_ids(package_ids, "WP", "work_packages", errors)
    task_to_package = validate_package_task_coverage(package_task_refs, task_ids, errors)
    validate_package_dependency_fields(package_dependencies, package_parallel, errors)
    validate_package_dependency_graph(package_dependencies, errors)
    validate_parallel_symmetry(package_parallel, errors)
    validate_cross_package_task_dependencies(
        package_task_refs, package_dependencies, task_dependencies, errors
    )
    return task_to_package


def index_work_packages(work_packages: list[Any], plan_index: dict[str, Any]) -> None:
    package_ids: set[str] = set()
    package_to_tasks: dict[str, list[str]] = {}
    package_required_context_bundles: dict[str, set[str]] = {}
    package_targeted_review_required: dict[str, bool] = {}
    package_verification_commands: dict[str, list[str]] = {}
    for package in work_packages:
        if not isinstance(package, dict) or not isinstance(package.get("id"), str):
            continue
        package_id = package["id"]
        package_ids.add(package_id)
        task_ids = package.get("task_ids")
        if isinstance(task_ids, list):
            package_to_tasks[package_id] = [
                task_id for task_id in task_ids if isinstance(task_id, str)
            ]
        bundle_refs = package.get("required_context_bundles")
        if isinstance(bundle_refs, list):
            package_required_context_bundles[package_id] = {
                bundle_ref for bundle_ref in bundle_refs if isinstance(bundle_ref, str)
            }
        targeted = package.get("targeted_review_required")
        if isinstance(targeted, bool):
            package_targeted_review_required[package_id] = targeted
        commands = package.get("verification_commands")
        if isinstance(commands, list):
            package_verification_commands[package_id] = [
                command for command in commands if isinstance(command, str)
            ]
    plan_index["package_ids"] = package_ids
    plan_index["package_to_tasks"] = package_to_tasks
    plan_index["package_required_context_bundles"] = package_required_context_bundles
    plan_index["package_targeted_review_required"] = package_targeted_review_required
    plan_index["package_verification_commands"] = package_verification_commands


def validate_package_v2_fields(
    package: dict[str, Any],
    package_path: str,
    errors: list[str],
    *,
    context_bundle_ids: set[str],
) -> None:
    risk_tags = require_string_list(package, "risk_tags", f"{package_path}.risk_tags", errors)
    for tag in risk_tags:
        if tag not in RISK_TAGS:
            errors.append(
                f"{package_path}.risk_tags: unknown risk tag {tag!r}; expected one of {sorted(RISK_TAGS)}"
            )

    bundle_refs = require_string_list(
        package,
        "required_context_bundles",
        f"{package_path}.required_context_bundles",
        errors,
    )
    for bundle_ref in bundle_refs:
        if bundle_ref not in context_bundle_ids:
            errors.append(
                f"{package_path}.required_context_bundles: unknown context bundle {bundle_ref!r}"
            )

    targeted = package.get("targeted_review_required")
    if not isinstance(targeted, bool):
        errors.append(f"{package_path}.targeted_review_required: expected boolean")
        return
    triggering_tags = sorted(set(risk_tags) & TARGETED_REVIEW_RISK_TAGS)
    if triggering_tags and not targeted:
        errors.append(
            f"{package_path}.targeted_review_required: must be true for compatibility metadata because risk_tags include enhanced package-review trigger(s) {triggering_tags}"
        )


def validate_conceptualize_slices(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{path}: expected array")
        return

    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_path}: expected object")
            continue
        require_non_empty_string(item, "path", f"{item_path}.path", errors)
        focus = item.get("focus")
        if focus is not None and not isinstance(focus, str):
            errors.append(f"{item_path}.focus: expected string when present")


def validate_package_task_coverage(
    package_task_refs: dict[str, list[str]], task_ids: set[str], errors: list[str]
) -> dict[str, str]:
    task_to_packages: dict[str, list[str]] = defaultdict(list)
    for package_id, refs in package_task_refs.items():
        for task_id in refs:
            if task_id not in task_ids:
                errors.append(
                    f"work package {package_id}: unknown task id {task_id!r} in task_ids"
                )
            else:
                task_to_packages[task_id].append(package_id)

    task_to_package: dict[str, str] = {}
    for task_id in sorted(task_ids):
        packages = task_to_packages.get(task_id, [])
        if not packages:
            errors.append(f"task {task_id}: not assigned to any work package")
        elif len(packages) > 1:
            errors.append(
                f"task {task_id}: assigned to multiple work packages {sorted(packages)}"
            )
        else:
            task_to_package[task_id] = packages[0]
    return task_to_package


def validate_package_dependency_fields(
    package_dependencies: dict[str, list[str]],
    package_parallel: dict[str, list[str]],
    errors: list[str],
) -> None:
    package_ids = set(package_dependencies) | set(package_parallel)
    for package_id in sorted(package_ids):
        for dependency in package_dependencies.get(package_id, []):
            if dependency == package_id:
                errors.append(f"work package {package_id}: must not depend on itself")
            elif dependency not in package_ids:
                errors.append(
                    f"work package {package_id}: unknown package dependency {dependency!r}"
                )
            if dependency in package_parallel.get(package_id, []):
                errors.append(
                    f"work package {package_id}: {dependency!r} cannot be both a dependency and parallel-safe"
                )
        for parallel_id in package_parallel.get(package_id, []):
            if parallel_id == package_id:
                errors.append(
                    f"work package {package_id}: must not list itself in parallel_safe_with"
                )
            elif parallel_id not in package_ids:
                errors.append(
                    f"work package {package_id}: unknown parallel_safe_with package {parallel_id!r}"
                )


def validate_package_dependency_graph(
    package_dependencies: dict[str, list[str]], errors: list[str]
) -> None:
    cycle = find_cycle(package_dependencies)
    if cycle:
        errors.append(f"work package dependencies contain cycle: {' -> '.join(cycle)}")


def validate_parallel_symmetry(
    package_parallel: dict[str, list[str]], errors: list[str]
) -> None:
    for package_id, parallel_ids in package_parallel.items():
        for parallel_id in parallel_ids:
            if parallel_id not in package_parallel:
                continue
            if package_id not in package_parallel[parallel_id]:
                errors.append(
                    f"work package {package_id}: parallel_safe_with {parallel_id!r} is not symmetric"
                )


def validate_cross_package_task_dependencies(
    package_task_refs: dict[str, list[str]],
    package_dependencies: dict[str, list[str]],
    task_dependencies: dict[str, list[str]],
    errors: list[str],
) -> None:
    task_to_package: dict[str, str] = {}
    for package_id, task_refs in package_task_refs.items():
        for task_id in task_refs:
            if task_id not in task_to_package:
                task_to_package[task_id] = package_id

    for task_id, dependencies in task_dependencies.items():
        package_id = task_to_package.get(task_id)
        if package_id is None:
            continue
        for dependency in dependencies:
            dependency_package = task_to_package.get(dependency)
            if dependency_package is None or dependency_package == package_id:
                continue
            if dependency_package not in package_dependencies.get(package_id, []):
                errors.append(
                    f"work package {package_id}: missing depends_on {dependency_package!r} "
                    f"because task {task_id} depends on {dependency}"
                )


def expected_package_proof_path(tasks_path: Path, package_id: str) -> Path:
    return tasks_path.with_name("proofs") / f"{package_id}.proof.json"


def validate_package_proof_json_file(
    proof_path: Path,
    plan_index: dict[str, Any],
    *,
    worktree: Path,
    tasks_path: Path | None = None,
) -> list[str]:
    errors: list[str] = []
    if tasks_path is None:
        return ["package proof path: tasks_path is required for file validation"]

    try:
        with proof_path.open("r", encoding="utf-8") as f:
            proof = json.load(f)
    except FileNotFoundError:
        return [f"package proof: file not found at {proof_path}"]
    except json.JSONDecodeError as exc:
        return [f"package proof: invalid JSON: {exc}"]
    except (OSError, UnicodeDecodeError) as exc:
        return [f"package proof: unable to read {proof_path}: {exc}"]

    errors.extend(
        validate_package_proof_json(
            proof,
            plan_index,
            worktree=worktree,
            proof_path=proof_path,
            tasks_path=tasks_path,
        )
    )
    return errors


def validate_final_package_proofs(
    tasks_path: Path, plan_index: dict[str, Any], *, worktree: Path
) -> list[str]:
    errors: list[str] = []
    package_ids = sorted(plan_index.get("package_ids", set()), key=package_id_sort_key)
    expected_paths = {
        expected_package_proof_path(tasks_path, package_id) for package_id in package_ids
    }
    proofs_dir = tasks_path.with_name("proofs")
    existing_paths = set(proofs_dir.glob("*.proof.json")) if proofs_dir.exists() else set()
    for extra_path in sorted(existing_paths - expected_paths):
        errors.append(f"package proof: unexpected proof file at {extra_path}")

    for package_id in package_ids:
        proof_path = expected_package_proof_path(tasks_path, package_id)
        try:
            with proof_path.open("r", encoding="utf-8") as f:
                proof = json.load(f)
        except FileNotFoundError:
            errors.append(f"{package_id}: package proof: file not found at {proof_path}")
            continue
        except json.JSONDecodeError as exc:
            errors.append(f"{package_id}: package proof: invalid JSON: {exc}")
            continue
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"{package_id}: package proof: unable to read {proof_path}: {exc}")
            continue

        proof_errors = validate_package_proof_json(
            proof,
            plan_index,
            worktree=worktree,
            proof_path=proof_path,
            tasks_path=tasks_path,
        )
        errors.extend(f"{package_id}: {error}" for error in proof_errors)
        if isinstance(proof, dict):
            lifecycle_state = package_lifecycle_state_name(proof)
            if lifecycle_state != "accepted":
                errors.append(
                    f"{package_id}: package proof.lifecycle.state: "
                    f"expected 'accepted' for final validation, got {lifecycle_state!r}"
                )
    return errors


def validate_final_task_lifecycle(data: Any, plan_index: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return errors
    status = data.get("status")
    if status != "completed":
        errors.append(
            f"feature.status: expected 'completed' for final validation, got {status!r}"
        )
    task_statuses = plan_index.get("task_statuses", {})
    if isinstance(task_statuses, dict):
        for task_id, task_status in sorted(task_statuses.items()):
            if task_status != "done":
                errors.append(
                    f"task {task_id}.status: expected 'done' for final validation, got {task_status!r}"
                )
    return errors


def package_id_sort_key(package_id: str) -> tuple[int, str]:
    match = WORK_PACKAGE_ID_RE.fullmatch(package_id)
    if match:
        return (int(package_id[2:]), package_id)
    return (0, package_id)


def normalized_existing_or_candidate_path(path: Path) -> Path:
    try:
        return path.resolve(strict=False)
    except OSError:
        return path.absolute()


def validate_package_proof_json(
    proof: Any,
    plan_index: dict[str, Any],
    *,
    worktree: Path,
    proof_path: Path | None = None,
    tasks_path: Path | None = None,
    enforce_entry_freshness: bool = True,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(proof, dict):
        return ["package proof root: expected object"]

    for field in sorted(PACKAGE_LIFECYCLE_FORBIDDEN_ROOT_FIELDS & set(proof)):
        errors.append(f"package proof.{field}: forbidden Release 2 lifecycle persistence field")

    schema_version = proof.get("schema_version")
    if (
        isinstance(schema_version, bool)
        or not isinstance(schema_version, int)
        or schema_version != PACKAGE_PROOF_SCHEMA_VERSION
    ):
        errors.append(
            f"package proof.schema_version: expected integer {PACKAGE_PROOF_SCHEMA_VERSION}, got {schema_version!r}"
        )

    feature = proof.get("feature")
    if feature != plan_index.get("feature"):
        errors.append(
            f"package proof.feature: expected {plan_index.get('feature')!r}, got {feature!r}"
        )

    package_id = proof.get("package_id")
    if not isinstance(package_id, str) or not package_id.strip():
        errors.append("package proof.package_id: expected non-empty string")
        package_id = None
    elif package_id not in plan_index.get("package_ids", set()):
        errors.append(f"package proof.package_id: unknown work package {package_id!r}")

    if proof_path is not None and isinstance(package_id, str):
        if tasks_path is not None:
            expected_path = expected_package_proof_path(tasks_path, package_id)
            if normalized_existing_or_candidate_path(
                proof_path
            ) != normalized_existing_or_candidate_path(expected_path):
                errors.append(
                    f"package proof path: expected {expected_path}, got {proof_path}"
                )
        else:
            errors.append("package proof path: tasks_path is required for file validation")

    entries = proof.get("entries")
    if not isinstance(entries, list):
        errors.append("package proof.entries: expected array")
        return errors

    expected_ac_ids = (
        package_acceptance_criteria(plan_index, package_id)
        if isinstance(package_id, str)
        else set()
    )
    seen_ac_ids: set[str] = set()
    entry_ac_ids: list[str] = []
    for index, entry in enumerate(entries):
        entry_path = f"package proof.entries[{index}]"
        validate_package_proof_entry(
            entry,
            entry_path,
            errors,
            plan_index,
            worktree,
            package_id=package_id if isinstance(package_id, str) else None,
            enforce_entry_freshness=enforce_entry_freshness,
        )
        if isinstance(entry, dict) and isinstance(entry.get("criterion_id"), str):
            criterion_id = entry["criterion_id"]
            seen_ac_ids.add(criterion_id)
            entry_ac_ids.append(criterion_id)

    for ac_id in sorted(expected_ac_ids - seen_ac_ids):
        errors.append(f"package proof.entries: missing proof entry for acceptance criterion {ac_id}")
    for ac_id in sorted(seen_ac_ids - expected_ac_ids):
        errors.append(
            f"package proof.entries: acceptance criterion {ac_id!r} is not owned by package {package_id!r}"
        )
    for duplicate in duplicates(entry_ac_ids):
        errors.append(f"package proof.entries: duplicate criterion_id {duplicate!r}")

    validate_package_lifecycle_state(
        proof,
        "package proof.lifecycle",
        errors,
        plan_index,
        worktree,
        package_id=package_id if isinstance(package_id, str) else None,
        proof_path=proof_path,
        tasks_path=tasks_path,
    )
    required_reviews = plan_index.get("package_targeted_review_required", {})
    lifecycle_state = package_lifecycle_state_name(proof)
    if lifecycle_state != "accepted":
        validate_package_targeted_review(
            proof.get("targeted_review"),
            "package proof.targeted_review",
            errors,
            required_by_plan=bool(required_reviews.get(package_id))
            if isinstance(package_id, str)
            else False,
            require_presence=False,
        )
    if isinstance(package_id, str) and lifecycle_state == "accepted":
        validate_package_acceptance_gates(
            proof,
            "package proof",
            errors,
            plan_index,
            package_id,
        )

    return errors


def validate_package_acceptance_gates(
    proof: dict[str, Any],
    path: str,
    errors: list[str],
    plan_index: dict[str, Any],
    package_id: str,
) -> None:
    required_commands = plan_index.get("package_verification_commands", {}).get(package_id, [])
    validate_package_verification_command_evidence(
        proof,
        required_commands if isinstance(required_commands, list) else [],
        f"{path}.verification_commands",
        errors,
    )
    required_reviews = plan_index.get("package_targeted_review_required", {})
    validate_package_targeted_review(
        proof.get("targeted_review"),
        f"{path}.targeted_review",
        errors,
        required_by_plan=bool(required_reviews.get(package_id)),
        require_presence=True,
    )


def validate_package_verification_command_evidence(
    proof: dict[str, Any],
    required_commands: list[str],
    path: str,
    errors: list[str],
) -> None:
    if not required_commands:
        return
    passing_commands: set[str] = set()
    entries = proof.get("entries")
    if isinstance(entries, list):
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            evidence = entry.get("evidence")
            if not isinstance(evidence, dict):
                continue
            commands = evidence.get("commands")
            if not isinstance(commands, list):
                continue
            for command in commands:
                if not isinstance(command, dict):
                    continue
                command_text = command.get("command")
                if isinstance(command_text, str) and command.get("exit_code") == 0:
                    passing_commands.add(command_text)
    for required_command in required_commands:
        if required_command not in passing_commands:
            errors.append(
                f"{path}: missing passing proof evidence for verification_commands entry {required_command!r}"
            )


def validate_package_targeted_review(
    review: Any,
    path: str,
    errors: list[str],
    *,
    required_by_plan: bool,
    require_presence: bool = True,
) -> None:
    if review is None:
        if require_presence:
            errors.append(f"{path}: required for mandatory package review receipt")
        return
    if not isinstance(review, dict):
        errors.append(f"{path}: expected object")
        return
    expected_fields = {"required", "performed", "reviewer", "result", "evidence", "reviewed_at"}
    actual_fields = set(review)
    for missing in sorted(expected_fields - actual_fields):
        errors.append(f"{path}.{missing}: expected field")
    for extra in sorted(actual_fields - expected_fields):
        errors.append(f"{path}.{extra}: unexpected field")
    if review.get("required") is not required_by_plan:
        errors.append(
            f"{path}.required: expected {required_by_plan!r}, got {review.get('required')!r}"
        )
    if review.get("performed") is not True:
        errors.append(f"{path}.performed: expected True")
    if review.get("result") != "passed":
        errors.append(f"{path}.result: expected 'passed', got {review.get('result')!r}")
    for field in ("reviewer", "evidence", "reviewed_at"):
        require_non_empty_string(review, field, f"{path}.{field}", errors)
    validate_targeted_review_evidence_quality(review.get("evidence"), f"{path}.evidence", errors)
    reviewed_at = review.get("reviewed_at")
    if isinstance(reviewed_at, str) and reviewed_at.strip():
        validate_iso_datetime(reviewed_at, f"{path}.reviewed_at", errors)


def validate_targeted_review_evidence_quality(
    value: Any, path: str, errors: list[str]
) -> None:
    if not isinstance(value, str) or not value.strip():
        return
    stripped = value.strip()
    normalized = " ".join(stripped.lower().split())
    if normalized in VAGUE_MANUAL_VALUES or len(normalized.split()) < 12:
        errors.append(
            f"{path}: expected {TARGETED_REVIEW_EVIDENCE_SUMMARY}, not approval-only or flag-only text"
        )
        return
    if len(stripped) > TARGETED_REVIEW_EVIDENCE_MAX_CHARS or "\n" in stripped:
        errors.append(
            f"{path}: expected compact single-receipt evidence, not a transcript or long report"
        )
    for marker in TARGETED_REVIEW_STALE_MARKERS:
        if marker in normalized:
            errors.append(
                f"{path}: expected current post-repair integrated review evidence, not stale/open-review text"
            )
            break

    missing: list[str] = []
    if not (
        text_has_any(normalized, ("integrated", "integration", "merge worktree"))
        and text_has_any(normalized, ("commit", "range", "head"))
    ):
        missing.append("reviewed integrated commit/range")
    if not text_has_any(
        normalized,
        ("depth", "lens", "lenses", "standard", "enhanced", "baseline"),
    ):
        missing.append("review depth/lenses")
    if not text_has_any(
        normalized,
        ("test scope", "test-scope", "sampled", "deep", "not applicable"),
    ):
        missing.append("explicit test scope")
    if not text_has_any(normalized, ("security", "privacy", "safety", "sniff")):
        missing.append("baseline security/privacy/safety sniff")
    if not has_closed_serious_finding_evidence(normalized):
        missing.append("serious finding count/closure")
    if TARGETED_REVIEW_UNCLOSED_REPAIR_DELTA_RE.search(normalized):
        missing.append("repair/delta-verification closure")
    elif not (
        text_has_any(normalized, TARGETED_REVIEW_REPAIR_CLOSURE_PHRASES)
        and text_has_any(normalized, TARGETED_REVIEW_DELTA_CLOSURE_PHRASES)
    ):
        missing.append("repair/delta-verification closure")
    if missing:
        errors.append(
            f"{path}: expected {TARGETED_REVIEW_EVIDENCE_SUMMARY}; missing {', '.join(missing)}"
        )


def has_closed_serious_finding_evidence(normalized: str) -> bool:
    serious_clauses: list[str] = []
    has_unclosed_serious_phrase = False
    for raw_clause in TARGETED_REVIEW_EVIDENCE_CLAUSE_RE.split(normalized):
        if not ("serious" in raw_clause and "finding" in raw_clause):
            continue
        if TARGETED_REVIEW_SERIOUS_FINDING_UNCLOSED_RE.search(raw_clause):
            has_unclosed_serious_phrase = True
        serious_index = raw_clause.find("serious")
        scoped_clause = raw_clause[serious_index:]
        trailing_section = TARGETED_REVIEW_SERIOUS_FINDING_TRAILING_SECTION_RE.search(
            scoped_clause, 1
        )
        if trailing_section:
            scoped_clause = scoped_clause[: trailing_section.start()]
        if re.search(r"\bno\s*$", raw_clause[:serious_index]):
            scoped_clause = f"no {scoped_clause}"
        serious_clauses.append(scoped_clause.strip())

    if not serious_clauses:
        return False
    if has_unclosed_serious_phrase:
        return False
    return any(
        TARGETED_REVIEW_SERIOUS_FINDING_ABSENCE_RE.search(clause)
        or (
            TARGETED_REVIEW_SERIOUS_FINDING_COUNT_RE.search(clause)
            and TARGETED_REVIEW_SERIOUS_FINDING_CLOSURE_RE.search(clause)
        )
        for clause in serious_clauses
    )


def text_has_any(value: str, markers: tuple[str, ...]) -> bool:
    return any(marker in value for marker in markers)


def package_proof_digest(proof: dict[str, Any]) -> str:
    digestible = {
        key: value
        for key, value in proof.items()
        if key != PACKAGE_LIFECYCLE_FIELD
    }
    canonical = json.dumps(
        digestible,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def package_lifecycle_state_name(proof: dict[str, Any]) -> str:
    lifecycle = proof.get(PACKAGE_LIFECYCLE_FIELD)
    if lifecycle is None:
        return "none"
    if isinstance(lifecycle, dict) and isinstance(lifecycle.get("state"), str):
        return lifecycle["state"]
    return "invalid"


def package_lifecycle_transition_errors(
    proof: dict[str, Any],
    target_state: str,
) -> list[str]:
    current_state = package_lifecycle_state_name(proof)
    if target_state not in PACKAGE_LIFECYCLE_STATES:
        return [f"package lifecycle transition: unknown target state {target_state!r}"]
    if current_state == "invalid":
        return ["package lifecycle transition: current lifecycle state is invalid"]

    if current_state == "accepted" and target_state == "accepted":
        lifecycle = proof.get(PACKAGE_LIFECYCLE_FIELD)
        if (
            isinstance(lifecycle, dict)
            and lifecycle.get("proof_digest") == package_proof_digest(proof)
            and isinstance(lifecycle.get("state_binding"), dict)
            and lifecycle["state_binding"].get("state") == "accepted"
        ):
            return []
        return [
            "package lifecycle transition: accepted -> accepted is only allowed "
            "as an idempotent rerun for the same proof_digest and accepted state"
        ]

    allowed_targets = PACKAGE_LIFECYCLE_TRANSITIONS.get(current_state, set())
    if target_state not in allowed_targets:
        return [
            f"package lifecycle transition: {current_state} -> {target_state} is not allowed"
        ]
    return []


def validate_package_lifecycle_state(
    proof: dict[str, Any],
    path: str,
    errors: list[str],
    plan_index: dict[str, Any],
    worktree: Path,
    *,
    package_id: str | None,
    proof_path: Path | None,
    tasks_path: Path | None,
) -> None:
    lifecycle = proof.get(PACKAGE_LIFECYCLE_FIELD)
    if lifecycle is None:
        return
    if not isinstance(lifecycle, dict):
        errors.append(f"{path}: expected object")
        return

    state = lifecycle.get("state")
    if not isinstance(state, str) or state not in PACKAGE_LIFECYCLE_STATES:
        errors.append(f"{path}.state: expected one of {sorted(PACKAGE_LIFECYCLE_STATES)}, got {state!r}")
        return
    validate_lifecycle_exact_fields(lifecycle, path, errors, state)
    validate_lifecycle_binding(
        lifecycle,
        path,
        errors,
        proof,
        worktree,
        package_id=package_id,
        proof_path=proof_path,
        tasks_path=tasks_path,
    )
    validate_lifecycle_writer(lifecycle.get("writer"), f"{path}.writer", errors, state)
    validate_lifecycle_state_binding(
        lifecycle.get("state_binding"),
        f"{path}.state_binding",
        errors,
        state,
        proof,
        worktree,
    )


def validate_package_lifecycle_state_for_replacement(
    proof: dict[str, Any],
    path: str,
    errors: list[str],
    plan_index: dict[str, Any],
    worktree: Path,
    *,
    package_id: str | None,
    proof_path: Path | None,
    tasks_path: Path | None,
) -> None:
    lifecycle = proof.get(PACKAGE_LIFECYCLE_FIELD)
    if lifecycle is None:
        return
    if not isinstance(lifecycle, dict):
        errors.append(f"{path}: expected object")
        return

    state = lifecycle.get("state")
    if not isinstance(state, str) or state not in PACKAGE_LIFECYCLE_STATES:
        errors.append(f"{path}.state: expected one of {sorted(PACKAGE_LIFECYCLE_STATES)}, got {state!r}")
        return
    validate_lifecycle_exact_fields(lifecycle, path, errors, state)
    validate_lifecycle_binding(
        lifecycle,
        path,
        errors,
        proof,
        worktree,
        package_id=package_id,
        proof_path=proof_path,
        tasks_path=tasks_path,
        enforce_digest=False,
        enforce_accepted_freshness=False,
    )
    validate_lifecycle_writer(lifecycle.get("writer"), f"{path}.writer", errors, state)
    validate_lifecycle_state_binding(
        lifecycle.get("state_binding"),
        f"{path}.state_binding",
        errors,
        state,
        proof,
        worktree,
        enforce_freshness=False,
        enforce_worktree=False,
    )


def validate_lifecycle_exact_fields(
    lifecycle: dict[str, Any], path: str, errors: list[str], state: str
) -> None:
    timestamp_field = f"{state}_at"
    expected_fields = {
        "state",
        "package_id",
        "proof_path",
        "proof_digest",
        timestamp_field,
        "writer",
        "state_binding",
    }
    actual_fields = set(lifecycle)
    for missing in sorted(expected_fields - actual_fields):
        errors.append(f"{path}.{missing}: expected field for {state!r} lifecycle state")
    for extra in sorted(actual_fields - expected_fields):
        errors.append(f"{path}.{extra}: unexpected field for Release 2 lifecycle state")
    timestamp = lifecycle.get(timestamp_field)
    if isinstance(timestamp, str) and timestamp.strip():
        validate_iso_datetime(timestamp, f"{path}.{timestamp_field}", errors)
    else:
        errors.append(f"{path}.{timestamp_field}: expected non-empty string")


def validate_lifecycle_binding(
    lifecycle: dict[str, Any],
    path: str,
    errors: list[str],
    proof: dict[str, Any],
    worktree: Path,
    *,
    package_id: str | None,
    proof_path: Path | None,
    tasks_path: Path | None,
    enforce_digest: bool = True,
    enforce_accepted_freshness: bool = True,
) -> None:
    stored_package_id = lifecycle.get("package_id")
    if stored_package_id != package_id:
        errors.append(
            f"{path}.package_id: expected package proof package_id {package_id!r}, got {stored_package_id!r}"
        )

    stored_digest = lifecycle.get("proof_digest")
    expected_digest = package_proof_digest(proof)
    if enforce_digest and stored_digest != expected_digest:
        errors.append(
            f"{path}.proof_digest: expected {expected_digest!r} for current proof content, got {stored_digest!r}"
        )
    elif not enforce_digest and (
        not isinstance(stored_digest, str)
        or PACKAGE_PROOF_DIGEST_RE.fullmatch(stored_digest) is None
    ):
        errors.append(f"{path}.proof_digest: expected sha256 digest string")

    stored_path = lifecycle.get("proof_path")
    expected_path = None
    if tasks_path is not None and package_id is not None:
        expected_path = expected_package_proof_path(tasks_path, package_id)
    elif proof_path is not None:
        expected_path = proof_path
    if expected_path is None:
        errors.append(f"{path}.proof_path: tasks_path or proof_path is required for lifecycle binding")
    elif stored_path != str(normalized_existing_or_candidate_path(expected_path)):
        errors.append(
            f"{path}.proof_path: expected {str(normalized_existing_or_candidate_path(expected_path))!r}, got {stored_path!r}"
        )

    if enforce_accepted_freshness and lifecycle.get("state") == "accepted":
        validate_accepted_lifecycle_freshness(
            proof,
            f"{path}.state_binding",
            errors,
            worktree,
        )


def validate_lifecycle_writer(
    writer: Any, path: str, errors: list[str], state: str
) -> None:
    if not isinstance(writer, dict):
        errors.append(f"{path}: expected object")
        return
    expected_command = "accept-package" if state == "accepted" else "reopen-package"
    expected = {
        "tool": PACKAGE_LIFECYCLE_WRITER_TOOL,
        "command": expected_command,
        "schema_version": PACKAGE_LIFECYCLE_WRITER_SCHEMA_VERSION,
    }
    if set(writer) != set(expected):
        missing = sorted(set(expected) - set(writer))
        extra = sorted(set(writer) - set(expected))
        if missing:
            errors.append(f"{path}: missing writer field(s) {missing}")
        if extra:
            errors.append(f"{path}: unexpected writer field(s) {extra}")
    for field, expected_value in expected.items():
        if writer.get(field) != expected_value:
            errors.append(f"{path}.{field}: expected {expected_value!r}, got {writer.get(field)!r}")


def validate_lifecycle_state_binding(
    binding: Any,
    path: str,
    errors: list[str],
    expected_state: str,
    proof: dict[str, Any],
    worktree: Path,
    *,
    enforce_freshness: bool = True,
    enforce_worktree: bool = True,
) -> None:
    if not isinstance(binding, dict):
        errors.append(f"{path}: expected object")
        return
    expected_fields = {"state", "worktree", "git_ref", "commit"}
    actual_fields = set(binding)
    for missing in sorted(expected_fields - actual_fields):
        errors.append(f"{path}.{missing}: expected field")
    for extra in sorted(actual_fields - expected_fields):
        errors.append(f"{path}.{extra}: unexpected field")
    if binding.get("state") != expected_state:
        errors.append(f"{path}.state: expected {expected_state!r}, got {binding.get('state')!r}")
    for field in ("worktree", "git_ref", "commit"):
        require_non_empty_string(binding, field, f"{path}.{field}", errors)

    stored_worktree = binding.get("worktree")
    expected_worktree = str(normalized_existing_or_candidate_path(worktree))
    if (
        enforce_worktree
        and isinstance(stored_worktree, str)
        and stored_worktree != expected_worktree
    ):
        errors.append(f"{path}.worktree: expected {expected_worktree!r}, got {stored_worktree!r}")

    commit = binding.get("commit")
    evidence_files = proof_lifecycle_evidence_paths(proof)
    if (
        enforce_freshness
        and expected_state == "accepted"
        and isinstance(commit, str)
        and commit.strip()
        and evidence_files
    ):
        stale = evidence_paths_changed_since(commit, evidence_files, worktree)
        if stale is True:
            errors.append(
                f"{path}.commit: stale accepted proof state; cited files changed after {commit!r}"
            )
        elif stale is None:
            errors.append(
                f"{path}.commit: unable to verify accepted proof freshness for {commit!r} in {worktree}"
            )


def validate_accepted_lifecycle_freshness(
    proof: dict[str, Any], path: str, errors: list[str], worktree: Path
) -> None:
    entries = proof.get("entries")
    if not isinstance(entries, list):
        return
    for index, entry in enumerate(entries):
        entry_path = f"package proof.entries[{index}]"
        if not isinstance(entry, dict):
            continue
        if entry.get("status") == "manual_required" or entry.get("method") == "manual":
            errors.append(
                f"{entry_path}: accepted lifecycle requires git-tracked file evidence, not manual evidence"
            )
        evidence_paths = extract_evidence_paths(entry.get("evidence"))
        if not evidence_paths:
            errors.append(
                f"{entry_path}.evidence.files: accepted lifecycle requires path-scoped file evidence"
            )


def proof_lifecycle_evidence_paths(proof: dict[str, Any]) -> list[str]:
    entries = proof.get("entries")
    if not isinstance(entries, list):
        return []
    paths: list[str] = []
    for entry in entries:
        if isinstance(entry, dict):
            paths.extend(extract_evidence_paths(entry.get("evidence")))
    return paths


def validate_package_proof_entry(
    entry: Any,
    path: str,
    errors: list[str],
    plan_index: dict[str, Any],
    worktree: Path,
    *,
    package_id: str | None,
    enforce_entry_freshness: bool = True,
) -> None:
    before_count = len(errors)
    validate_ledger_entry(
        entry,
        path,
        errors,
        plan_index,
        worktree,
        enforce_state_freshness=enforce_entry_freshness,
    )
    if not isinstance(entry, dict):
        return

    entry_package_id = entry.get("package_id")
    if (
        package_id is not None
        and isinstance(entry_package_id, str)
        and entry_package_id != package_id
    ):
        errors.append(
            f"{path}.package_id: expected package proof package_id {package_id!r}, got {entry_package_id!r}"
        )

    validate_required_context_bundle_citations(
        entry,
        path,
        errors,
        plan_index,
        proof_package_id=package_id,
    )
    if len(errors) == before_count and entry.get("status") in {"failed", "blocked"}:
        errors.append(f"{path}.status: package proof cannot contain {entry.get('status')!r} entry")


def package_acceptance_criteria(plan_index: dict[str, Any], package_id: str | None) -> set[str]:
    if package_id is None:
        return set()
    task_ids = set(plan_index.get("package_to_tasks", {}).get(package_id, []))
    return {
        ac_id
        for ac_id in plan_index.get("task_ac_ids", set())
        if ac_id.rsplit("-AC", 1)[0] in task_ids
    }


def required_context_bundles_for_entry(
    entry: dict[str, Any],
    plan_index: dict[str, Any],
    *,
    proof_package_id: str | None,
) -> set[str]:
    criterion_id = entry.get("criterion_id")
    task_id = entry.get("task_id")
    if not isinstance(task_id, str) and isinstance(criterion_id, str):
        match = TASK_AC_ID_RE.fullmatch(criterion_id)
        if match:
            task_id = match.group(1)
    package_id = proof_package_id
    if package_id is None and isinstance(task_id, str):
        package_id = plan_index.get("task_to_package", {}).get(task_id)

    required = set()
    if package_id is not None:
        required.update(
            plan_index.get("package_required_context_bundles", {}).get(package_id, set())
        )
    if isinstance(task_id, str):
        required.update(
            plan_index.get("task_required_context_bundles", {}).get(task_id, set())
        )
    if isinstance(criterion_id, str):
        for ref in plan_index.get("task_ac_sources", {}).get(criterion_id, []):
            if ref.get("type") == "context_bundle":
                required.add(ref["id"])
    return required


def validate_required_context_bundle_citations(
    entry: dict[str, Any],
    path: str,
    errors: list[str],
    plan_index: dict[str, Any],
    *,
    proof_package_id: str | None,
) -> None:
    evidence = entry.get("evidence")
    if not isinstance(evidence, dict):
        return
    required = required_context_bundles_for_entry(
        entry, plan_index, proof_package_id=proof_package_id
    )
    cited = evidence.get("context_bundles")
    if cited is None:
        cited_set: set[str] = set()
    elif isinstance(cited, list):
        cited_set = {item for item in cited if isinstance(item, str)}
    else:
        cited_set = set()

    for bundle_id in sorted(required - cited_set):
        errors.append(
            f"{path}.evidence.context_bundles: missing required context bundle citation {bundle_id!r}"
        )


def validate_verification_json_file(
    verification_path: Path, plan_index: dict[str, Any], *, worktree: Path
) -> list[str]:
    errors: list[str] = []
    try:
        with verification_path.open("r", encoding="utf-8") as f:
            ledger = json.load(f)
    except FileNotFoundError:
        return [f"verification.json: file not found at {verification_path}"]
    except json.JSONDecodeError as exc:
        return [f"verification.json: invalid JSON: {exc}"]
    except (OSError, UnicodeDecodeError) as exc:
        return [f"verification.json: unable to read {verification_path}: {exc}"]

    errors.extend(validate_verification_json(ledger, plan_index, worktree=worktree))
    return errors


def validate_verification_json(
    ledger: Any, plan_index: dict[str, Any], *, worktree: Path
) -> list[str]:
    errors: list[str] = []
    if not isinstance(ledger, dict):
        return ["verification.json root: expected object"]

    schema_version = ledger.get("schema_version")
    if (
        isinstance(schema_version, bool)
        or not isinstance(schema_version, int)
        or schema_version != 1
    ):
        errors.append(f"verification.schema_version: expected integer 1, got {schema_version!r}")

    feature = ledger.get("feature")
    if feature != plan_index.get("feature"):
        errors.append(
            f"verification.feature: expected {plan_index.get('feature')!r}, got {feature!r}"
        )

    entries = ledger.get("entries")
    if not isinstance(entries, list):
        errors.append("verification.entries: expected array")
        return errors

    task_ac_ids: set[str] = set(plan_index.get("task_ac_ids", set()))
    seen_ac_ids: set[str] = set()
    for index, entry in enumerate(entries):
        validate_ledger_entry(entry, f"verification.entries[{index}]", errors, plan_index, worktree)
        if isinstance(entry, dict) and isinstance(entry.get("criterion_id"), str):
            seen_ac_ids.add(entry["criterion_id"])

    for ac_id in sorted(task_ac_ids - seen_ac_ids):
        errors.append(f"verification.entries: missing ledger entry for acceptance criterion {ac_id}")
    for ac_id in sorted(seen_ac_ids - task_ac_ids):
        errors.append(f"verification.entries: unknown acceptance criterion {ac_id!r}")
    for duplicate in duplicates(
        [
            entry["criterion_id"]
            for entry in entries
            if isinstance(entry, dict) and isinstance(entry.get("criterion_id"), str)
        ]
    ):
        errors.append(f"verification.entries: duplicate criterion_id {duplicate!r}")

    return errors


def validate_ledger_entry(
    entry: Any,
    path: str,
    errors: list[str],
    plan_index: dict[str, Any],
    worktree: Path,
    *,
    enforce_state_freshness: bool = True,
) -> None:
    if not isinstance(entry, dict):
        errors.append(f"{path}: expected object")
        return

    criterion_id = entry.get("criterion_id")
    task_id = entry.get("task_id")
    package_id = entry.get("package_id")
    status = entry.get("status")
    method = entry.get("method")

    for field in ("criterion_id", "task_id", "package_id", "status", "method"):
        require_non_empty_string(entry, field, f"{path}.{field}", errors)

    if isinstance(criterion_id, str):
        match = TASK_AC_ID_RE.fullmatch(criterion_id)
        if not match:
            errors.append(f"{path}.criterion_id: expected <TaskID>-AC<N>, got {criterion_id!r}")
        elif isinstance(task_id, str) and match.group(1) != task_id:
            errors.append(
                f"{path}.task_id: expected {match.group(1)!r} from criterion_id, got {task_id!r}"
            )
    if isinstance(task_id, str):
        if task_id not in plan_index.get("task_ids", set()):
            errors.append(f"{path}.task_id: unknown task id {task_id!r}")
        expected_package = plan_index.get("task_to_package", {}).get(task_id)
        if expected_package and isinstance(package_id, str) and package_id != expected_package:
            errors.append(
                f"{path}.package_id: expected {expected_package!r} for task {task_id}, got {package_id!r}"
            )

    if isinstance(status, str) and status not in LEDGER_STATUSES:
        errors.append(f"{path}.status: expected one of {sorted(LEDGER_STATUSES)}, got {status!r}")
    if status in {"failed", "blocked"}:
        errors.append(f"{path}.status: final evidence cannot contain {status!r} entry")
    if isinstance(method, str) and method not in LEDGER_METHODS:
        errors.append(f"{path}.method: expected one of {sorted(LEDGER_METHODS)}, got {method!r}")

    validate_ledger_source_refs(entry, path, errors, plan_index)
    validate_ledger_state(
        entry.get("state"),
        f"{path}.state",
        errors,
        worktree,
        entry,
        enforce_freshness=enforce_state_freshness,
    )
    validate_ledger_evidence(
        entry.get("evidence"), f"{path}.evidence", errors, method=method
    )

    if status == "manual_required" or method == "manual":
        validate_manual_evidence(
            entry.get("manual_evidence"),
            f"{path}.manual_evidence",
            errors,
            criterion_id=criterion_id if isinstance(criterion_id, str) else None,
            known_criteria=set(plan_index.get("task_ac_ids", set())),
        )


def validate_ledger_source_refs(
    entry: dict[str, Any], path: str, errors: list[str], plan_index: dict[str, Any]
) -> None:
    criterion_id = entry.get("criterion_id")
    refs = entry.get("source_refs")
    if not isinstance(refs, list) or not refs:
        errors.append(f"{path}.source_refs: expected non-empty array")
        return
    parsed_refs: list[dict[str, str]] = []
    for index, ref in enumerate(refs):
        parsed = validate_source_ref(ref, f"{path}.source_refs[{index}]", errors)
        if parsed is not None:
            parsed_refs.append(parsed)
    expected = (
        plan_index.get("task_ac_sources", {}).get(criterion_id)
        if isinstance(criterion_id, str)
        else None
    )
    if expected is not None and sorted(parsed_refs, key=ref_sort_key) != sorted(expected, key=ref_sort_key):
        errors.append(f"{path}.source_refs: does not match task acceptance criterion source_refs")


def ref_sort_key(ref: dict[str, str]) -> tuple[str, str]:
    return (ref["type"], ref["id"])


def validate_ledger_state(
    state: Any,
    path: str,
    errors: list[str],
    worktree: Path,
    entry: dict[str, Any],
    *,
    enforce_freshness: bool = True,
) -> None:
    if not isinstance(state, dict):
        errors.append(f"{path}: expected object")
        return
    for field in ("git_ref", "commit", "worktree", "captured_at"):
        require_non_empty_string(state, field, f"{path}.{field}", errors)
    captured_at = state.get("captured_at")
    if isinstance(captured_at, str) and captured_at.strip():
        validate_iso_datetime(captured_at, f"{path}.captured_at", errors)

    commit = state.get("commit")
    evidence = entry.get("evidence")
    evidence_files = extract_evidence_paths(evidence)
    if enforce_freshness and isinstance(commit, str) and commit.strip() and evidence_files:
        stale = evidence_paths_changed_since(commit, evidence_files, worktree)
        if stale is True:
            errors.append(
                f"{path}.commit: stale evidence; cited files changed after {commit!r}"
            )
        elif stale is None:
            errors.append(
                f"{path}.commit: unable to verify evidence freshness for {commit!r} in {worktree}"
            )


def validate_ledger_evidence(
    evidence: Any, path: str, errors: list[str], *, method: Any
) -> None:
    if not isinstance(evidence, dict):
        errors.append(f"{path}: expected object")
        return

    files = require_string_list(evidence, "files", f"{path}.files", errors)
    commands = evidence.get("commands")
    if not isinstance(commands, list):
        errors.append(f"{path}.commands: expected array")
        commands = []
    if not files and not commands:
        errors.append(f"{path}: expected file/symbol evidence or command evidence")
    if method in COMMAND_EVIDENCE_METHODS and not commands:
        errors.append(f"{path}.commands: expected at least one command for command evidence")

    for index, command in enumerate(commands):
        command_path = f"{path}.commands[{index}]"
        if not isinstance(command, dict):
            errors.append(f"{command_path}: expected object")
            continue
        for field in ("cwd", "command", "observed"):
            require_non_empty_string(command, field, f"{command_path}.{field}", errors)
        exit_code = command.get("exit_code")
        if isinstance(exit_code, bool) or not isinstance(exit_code, int):
            errors.append(f"{command_path}.exit_code: expected integer")
        elif exit_code != 0:
            errors.append(f"{command_path}.exit_code: final evidence command must pass, got {exit_code}")

    require_string_list(evidence, "edge_cases", f"{path}.edge_cases", errors, required=False)
    require_string_list(evidence, "context_bundles", f"{path}.context_bundles", errors, required=False)
    mocks = evidence.get("mocks")
    if mocks is not None and (not isinstance(mocks, str) or not mocks.strip()):
        errors.append(f"{path}.mocks: expected non-empty string when present")


def validate_manual_evidence(
    evidence: Any,
    path: str,
    errors: list[str],
    *,
    criterion_id: str | None,
    known_criteria: set[str],
) -> None:
    if not isinstance(evidence, dict):
        errors.append(f"{path}: expected object for manual_required entry")
        return
    required_fields = (
        "criterion_ids",
        "approval_provenance",
        "observed_result",
        "scope",
        "limits",
        "state_reference",
        "approved_at",
    )
    for field in required_fields:
        if field == "criterion_ids":
            values = require_string_list(evidence, field, f"{path}.{field}", errors)
            if not values:
                errors.append(f"{path}.{field}: expected at least one criterion id")
            for manual_criterion_id in values:
                if manual_criterion_id not in known_criteria:
                    errors.append(
                        f"{path}.{field}: unknown acceptance criterion {manual_criterion_id!r}"
                    )
            if criterion_id is not None and criterion_id not in values:
                errors.append(
                    f"{path}.{field}: must include entry criterion_id {criterion_id!r}"
                )
        else:
            require_non_empty_string(evidence, field, f"{path}.{field}", errors)
    approved_at = evidence.get("approved_at")
    if isinstance(approved_at, str) and approved_at.strip():
        validate_iso_datetime(approved_at, f"{path}.approved_at", errors)
    approved = evidence.get("approved")
    if approved is not True:
        errors.append(f"{path}.approved: expected true for approved manual evidence")
    validate_manual_evidence_quality(evidence, path, errors)


def validate_manual_evidence_quality(
    evidence: dict[str, Any], path: str, errors: list[str]
) -> None:
    require_substantive_manual_text(
        evidence.get("observed_result"),
        f"{path}.observed_result",
        errors,
        minimum_words=5,
    )
    require_substantive_manual_text(
        evidence.get("scope"),
        f"{path}.scope",
        errors,
        minimum_words=3,
    )
    require_artifact_state_reference(
        evidence.get("state_reference"),
        f"{path}.state_reference",
        errors,
    )


def require_substantive_manual_text(
    value: Any, path: str, errors: list[str], *, minimum_words: int
) -> None:
    if not isinstance(value, str) or not value.strip():
        return
    normalized = " ".join(value.lower().split())
    if normalized in VAGUE_MANUAL_VALUES or len(normalized.split()) < minimum_words:
        errors.append(
            f"{path}: expected verifiable observed behavior, not approval-only or vague text"
        )


def require_artifact_state_reference(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        return
    normalized = value.lower()
    if " ".join(normalized.split()) in VAGUE_MANUAL_VALUES:
        errors.append(f"{path}: expected artifact context, not approval-only or vague text")
        return
    if not any(marker in normalized for marker in STATE_REFERENCE_MARKERS):
        errors.append(
            f"{path}: expected artifact context such as file, command, commit, or proof reference"
        )


def extract_evidence_paths(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return []
    raw_files = evidence.get("files")
    if not isinstance(raw_files, list):
        return []
    paths: list[str] = []
    for item in raw_files:
        if not isinstance(item, str):
            continue
        stripped = item.strip()
        if stripped.startswith(("http://", "https://")):
            continue
        path = stripped.split(":", 1)[0].strip()
        if path:
            paths.append(path)
    return paths


def evidence_paths_changed_since(commit: str, paths: list[str], worktree: Path) -> bool | None:
    try:
        subprocess.run(
            ["git", "rev-parse", "--verify", f"{commit}^{{commit}}"],
            cwd=worktree,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        tracked_result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", *paths],
            cwd=worktree,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        committed_result = subprocess.run(
            ["git", "diff", "--quiet", f"{commit}..HEAD", "--", *paths],
            cwd=worktree,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        worktree_result = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", *paths],
            cwd=worktree,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if tracked_result.returncode != 0:
        return True
    if committed_result.returncode not in (0, 1) or worktree_result.returncode not in (0, 1):
        return None
    return committed_result.returncode == 1 or worktree_result.returncode == 1


def require_non_empty_string(
    obj: dict[str, Any], field: str, path: str, errors: list[str]
) -> bool:
    value = obj.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}: expected non-empty string")
        return False
    return True


def require_string_list(
    obj: dict[str, Any],
    field: str,
    path: str,
    errors: list[str],
    *,
    required: bool = True,
) -> list[str]:
    if field not in obj and not required:
        return []
    value = obj.get(field)
    if not isinstance(value, list):
        errors.append(f"{path}: expected string array")
        return []
    strings = [item for item in value if isinstance(item, str) and item.strip()]
    if len(strings) != len(value):
        errors.append(f"{path}: expected non-empty string array")
    return strings


def validate_iso_datetime(value: str, path: str, errors: list[str]) -> None:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{path}: expected ISO 8601 datetime string")


def validate_sequential_orders(values: list[int], path: str, errors: list[str]) -> None:
    if not values:
        return
    expected = list(range(1, len(values) + 1))
    if sorted(values) != expected:
        errors.append(f"{path}: expected sequential values {expected}, got {sorted(values)}")


def validate_sequential_ids(
    values: list[str], prefix: str, path: str, errors: list[str]
) -> None:
    valid_numbers = sorted(
        int(value.removeprefix(prefix))
        for value in values
        if value.startswith(prefix) and value.removeprefix(prefix).isdigit()
    )
    if not valid_numbers:
        return
    expected_numbers = list(range(1, len(valid_numbers) + 1))
    if valid_numbers != expected_numbers:
        expected_ids = [f"{prefix}{number}" for number in expected_numbers]
        actual_ids = [f"{prefix}{number}" for number in valid_numbers]
        errors.append(f"{path}: expected sequential ids {expected_ids}, got {actual_ids}")


def add_duplicate_errors(
    values: list[str], label: str, path: str, errors: list[str]
) -> None:
    for value in duplicates(values):
        errors.append(f"{path}: duplicate {label} {value!r}")


def duplicates(values: list[Any]) -> list[Any]:
    return sorted(
        (value for value, count in Counter(values).items() if count > 1),
        key=lambda item: repr(item),
    )


def find_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    state: dict[str, str] = {}
    path: list[str] = []

    def visit(node: str) -> list[str] | None:
        marker = state.get(node)
        if marker == "visiting":
            start = path.index(node)
            return path[start:] + [node]
        if marker == "visited":
            return None

        state[node] = "visiting"
        path.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in graph:
                continue
            cycle = visit(neighbor)
            if cycle:
                return cycle
        path.pop()
        state[node] = "visited"
        return None

    for node in graph:
        cycle = visit(node)
        if cycle:
            return cycle
    return None


if __name__ == "__main__":
    raise SystemExit(main())
