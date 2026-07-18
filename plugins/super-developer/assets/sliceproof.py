#!/usr/bin/env python3
"""Mechanical helper for Slice-first planned-feature artifacts.

The helper performs deterministic structure, path-safety, proof-closure,
report-binding, and local lifecycle/predecessor checks. It does not judge
semantic quality, run tests, mutate lifecycle/package state, dispatch work,
perform remote Git effects, or replace review/audit gates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
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
EXACT_GIT_SHA_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
SAFE_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
ACTION_RE = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
COUNTER_RE = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
WAVE_ID_RE = re.compile(r"^wave-[a-z0-9][a-z0-9-]*$")
SEMGREP_DIGEST_RE = re.compile(r"^(?:sha256:)?([0-9a-fA-F]{64})$")
STATUS_VALUES = {"pending", "in_progress", "done", "blocked"}
FEATURE_STATUS_VALUES = {"planned", "reviewed", "in_progress", "completed", "blocked", "on_hold"}
ASSURANCE_PROFILES = {"low", "standard", "high"}
PACKAGE_VERIFICATION_MODES = {"boundary", "final"}
REGISTRY_KEYS = {
    "feature", "title", "status", "spec_path", "authoritative_slices", "work_packages", "assurance_profile"
}
REGISTRY_PACKAGE_KEYS = {
    "id", "path", "proof_path", "report_path", "status", "depends_on", "verification_mode"
}
PREAUTH_LIFECYCLE_STAGES = {
    "conceptualization", "conceptualization-checkpoint", "preflight", "planning", "plan-review",
    "execution-readiness", "authorization-pending",
}
AUTHORIZED_LIFECYCLE_STAGES = {
    "authorized", "activation", "package-wave", "package-wave-quiescent", "integration",
    "technical-reassessment", "technical-plan-review", "final-assurance", "completed",
}
NEUTRAL_LIFECYCLE_STAGES = {"blocked", "needs-decision"}
LIFECYCLE_STAGES = PREAUTH_LIFECYCLE_STAGES | AUTHORIZED_LIFECYCLE_STAGES | NEUTRAL_LIFECYCLE_STAGES
PREAUTH_BUDGET_STAGES = PREAUTH_LIFECYCLE_STAGES - {"conceptualization", "conceptualization-checkpoint"}
OWNER_DISPOSITIONS = {"unassigned", "active", "stopped", "released"}
PACKAGE_LIFECYCLE_STATES = {"pending", "in_progress", "stabilized", "verified", "done", "blocked", "invalidated"}
PACKAGE_STATE_TRANSITIONS = {
    "pending": {"pending", "in_progress", "blocked", "invalidated"},
    "in_progress": {"in_progress", "stabilized", "blocked", "invalidated"},
    "stabilized": {"stabilized", "verified", "in_progress", "blocked", "invalidated"},
    "verified": {"verified", "done", "in_progress", "blocked", "invalidated"},
    "done": {"done", "invalidated"},
    "blocked": {"blocked", "pending", "in_progress", "invalidated"},
    "invalidated": {"invalidated", "in_progress", "blocked"},
}
REPLAN_RESET_STATES = {"in_progress", "stabilized", "verified", "done", "invalidated"}
WAVE_STATES = {"reserved", "active", "quiescent", "completed", "blocked"}
CLUSTER_DISPOSITIONS = {"repair-eligible", "closed", "circuit-open"}
PREAUTH_REQUIRED_COUNTERS = {"delegated_calls", "planner_correction_waves", "spike_waves", "command_units"}
IMPLEMENTATION_REQUIRED_COUNTERS = {"repair_waves", "delegated_calls", "command_units", "cost_units"}
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
REQUIRED_SOURCE_REPORT_H3 = {
    "Verdict",
    "Deliverable Completeness Matrix",
    "Triggered Risk Selection Notes",
    "Test Review Scope",
    "Slice Closure Review",
    "Code Review Findings",
}
FAILURE_SOURCE_REPORT_H3 = {"Blocking Findings", "Repair Guidance"}
MATRIX_COLUMNS = [
    "Source ID",
    "Row Type",
    "Deliverable",
    "Evidence Type",
    "Evidence Refs",
    "Exactness / Risk Disposition",
    "Verdict",
]
MATRIX_ROW_TYPES = {"slice", "verification-expectation", "triggered-risk"}
MATRIX_EVIDENCE_TYPES = {"code", "test", "static", "command", "manual", "mixed"}
MATRIX_VERDICTS = {"delivered", "missing", "partial", "contradicted", "unverified"}
MATRIX_CLEAN_VERDICT = "delivered"
TEST_REVIEW_SCOPE_COLUMNS = [
    "Surface",
    "Changed Population",
    "Review Depth",
    "Baseline Review",
    "Deep Triggers",
    "Selected Exemplars",
    "Sampling Rationale",
    "Generator / Input / Provenance",
    "Evidence Refs",
]
TEST_REVIEW_SURFACES = {
    "tests",
    "harnesses/helpers",
    "mocks/fixtures",
    "generators/snapshots",
    "test-discovery/ci/coverage/build-config",
    "other-test-relevant",
}
TEST_REVIEW_DEPTHS = {"baseline-only", "sampled", "deep"}
NO_APPLICABLE_TEST_SURFACE_DEPTH = "no-applicable-surface"
TEST_REVIEW_UNRESOLVED_MARKER_RE = re.compile(
    r"(?i:\btodo\b)|\b(?:OPEN|GAP)\b|"
    r"(?i:(?:^|[|;(\[])\s*(?:open|gap)\s*(?=[:;,\])|]|$)|"
    r"\b(?:open|gap)\s+(?:marker|item|remains?|pending|unresolved)\b|"
    r"\b(?:unresolved|pending)\s+(?:open|gap)\b)",
    re.MULTILINE,
)
TEST_REVIEW_FORBIDDEN_STATUS_RE = re.compile(r"\b(?:not[- ]reviewed|unreviewed)\b", re.IGNORECASE)
RISK_SOURCE_ID_RE = re.compile(r"^RISK-[A-Za-z0-9][A-Za-z0-9_-]*$")
FALSIFICATION_TERM = r"falsif(?:y|ies|ied|ication|ications)"
FORBIDDEN_BEHAVIOR_TERM = r"forbidden[-\s]+behaviou?rs?"
AFFIRMATIVE_FORBIDDEN_FALSIFICATION_RE = re.compile(
    rf"(?:\b{FORBIDDEN_BEHAVIOR_TERM}\b.{{0,160}}\b{FALSIFICATION_TERM}\b|"
    rf"\b{FALSIFICATION_TERM}\b.{{0,160}}\b{FORBIDDEN_BEHAVIOR_TERM}\b)",
    re.IGNORECASE,
)
NEGATED_FORBIDDEN_FALSIFICATION_RE = re.compile(
    rf"(?:\b(?:not|never|without|unfalsified)\b.{{0,80}}\b{FALSIFICATION_TERM}\b|"
    rf"\b(?:did|does|do|was|were|is|are|has|have|had)\s+not\s+(?:\w+\s+){{0,3}}{FALSIFICATION_TERM}\b|"
    rf"\bno\b.{{0,80}}\b{FALSIFICATION_TERM}\b|"
    rf"\b(?:fail(?:ed|s)?|unable|cannot|can't)\s+(?:to\s+)?{FALSIFICATION_TERM}\b|"
    rf"\b{FALSIFICATION_TERM}\b\s+(?:(?:was|were|is|are|has|have|had)\s+)?"
    rf"(?:not|never|missing|absent|unverified)\b)",
    re.IGNORECASE,
)
TRIGGERED_RISK_RATIONALE_RE = re.compile(
    r"\btriggered\s+(?:because|by|due\s+to|from)\s+(?P<rationale>[^;|.]+)",
    re.IGNORECASE,
)
TRIGGERED_RISK_GENERIC_TOKENS = {
    "a",
    "an",
    "and",
    "are",
    "because",
    "by",
    "disposition",
    "due",
    "for",
    "from",
    "in",
    "is",
    "of",
    "or",
    "result",
    "risk",
    "row",
    "rows",
    "the",
    "to",
    "triggered",
    "was",
    "were",
    "with",
}
EVIDENCE_REF_PREFIX_RE = re.compile(r"(?:^|;\s*)(code|test|static|command|manual):")
STATE_BINDING_FIELD_ORDER = [
    "Package",
    "Package Markdown",
    "Package Markdown Digest",
    "Proof",
    "Proof Digest",
    "Assigned Slices",
    "Assigned Slice Digests",
    "Matrix Source Snapshot",
    "Worktree",
    "Git Ref",
    "Commit",
    "Verified At",
]
REQUIRED_STATE_BINDING_FIELDS = set(STATE_BINDING_FIELD_ORDER)
SLICE_DIGEST_TIERS = ("must_satisfy", "context_only")
SLICE_DIGEST_TIER_ORDER = {tier: index for index, tier in enumerate(SLICE_DIGEST_TIERS)}
SLICE_DIGEST_ADVISORY_TYPE = "context_only_slice_drift"
STATE_BINDING_ASSIGNED_SLICE_PATH_DELIMITERS = ("|", "=", "; ")
SEMGREP_EVIDENCE_FIELDS = {"Status", "Raw Path", "Raw Digest", "Summary Path", "Summary Digest", "Scan Scope", "Bounded Summary"}
SEMGREP_ENABLED_STATUSES = {"enabled", "contracted"}
SEMGREP_DISABLED_STATUSES = {"disabled", "not-contracted", "not contracted"}
PROOF_STATUS_VALUES = {"PASS", "GAP", "DEFERRED", "N/A", "OPEN"}
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
REPORT_BINDING_PLACEHOLDER_VALUES = {
    "",
    "none",
    "no",
    "n a",
    "na",
    "tbd",
    "to be determined",
    "todo",
    "open",
    "gap",
    "unknown",
    "unconfirmed",
    "missing",
    "absent",
    "pending",
    "requested",
    "awaiting",
    "not set",
    "unset",
    "not provided",
    "not supplied",
}
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
class SliceDigestEntry:
    path: str
    tier: str
    h3_id: str
    digest: str


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
    verification_mode: str | None = None


@dataclass(frozen=True)
class Registry:
    path: Path
    root: Path
    code_root: Path
    data: dict[str, Any]
    feature: str
    authoritative_slices: list[str]
    packages: list[RegistryPackage]
    assurance_profile: str | None = None

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
            "create-proof only writes the declared package proof Markdown placeholder."
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

    create_proof = subparsers.add_parser(
        "create-proof",
        parents=[root_options],
        help="Create a package proof Markdown placeholder from work-package Markdown.",
    )
    create_proof.add_argument("tasks", type=Path, help="Path to .tasks/<feature>/tasks.json under the artifact root.")
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
        parents=[root_options],
        help="Validate one package proof Markdown file mechanically.",
    )
    validate_proof.add_argument("tasks", type=Path, help="Path to .tasks/<feature>/tasks.json under the artifact root.")
    validate_proof.add_argument("--package", required=True, help="Work package id, for example WP1.")
    validate_proof.set_defaults(func=cmd_validate_proof)

    validate_package_complete = subparsers.add_parser(
        "validate-package-complete",
        parents=[root_options],
        help="Validate one package proof plus verification report and deliverable matrix before marking done.",
    )
    validate_package_complete.add_argument("tasks", type=Path, help="Path to .tasks/<feature>/tasks.json under the artifact root.")
    validate_package_complete.add_argument("--package", required=True, help="Work package id, for example WP1.")
    validate_package_complete.set_defaults(func=cmd_validate_package_complete)

    validate_final = subparsers.add_parser(
        "validate-final",
        parents=[root_options],
        help="Validate all packages, proof Markdown, and package verification report bindings.",
    )
    validate_final.add_argument("tasks", type=Path, help="Path to .tasks/<feature>/tasks.json under the artifact root.")
    validate_final.set_defaults(func=cmd_validate_final)

    emit_state_binding = subparsers.add_parser(
        "emit-state-binding",
        parents=[root_options],
        help="Emit the canonical State Binding block for a package verification report.",
    )
    emit_state_binding.add_argument("tasks", type=Path, help="Path to .tasks/<feature>/tasks.json under the artifact root.")
    emit_state_binding.add_argument("--package", required=True, help="Work package id, for example WP1.")
    emit_state_binding.add_argument("--worktree", required=True, help="Absolute reviewed worktree path to write into the binding.")
    emit_state_binding.add_argument("--git-ref", required=True, help="Reviewed git ref to write into the binding.")
    emit_state_binding.add_argument("--commit", required=True, help="Reviewed commit SHA to write into the binding.")
    emit_state_binding.add_argument("--verified-at", required=True, help="ISO-8601 verification timestamp to write into the binding.")
    emit_state_binding.set_defaults(func=cmd_emit_state_binding)

    validate_lifecycle = subparsers.add_parser(
        "validate-lifecycle-state",
        parents=[root_options],
        help="Validate the derived portable Lifecycle State and, after generation one, its exact committed predecessor.",
    )
    validate_lifecycle.add_argument("--feature", required=True, help="Feature slug used to derive .tasks/<feature>/lifecycle-state.json.")
    validate_lifecycle.add_argument(
        "--previous-commit",
        help="Exact full artifact-sidecar commit containing the predecessor Lifecycle State; required after generation one.",
    )
    validate_lifecycle.set_defaults(func=cmd_validate_lifecycle_state)
    return parser


def add_root_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--artifact-root",
        type=Path,
        help="Root for .planning/.tasks artifacts; compatibility default is cwd, but lifecycle validation requires it.",
    )
    parser.add_argument(
        "--code-root",
        type=Path,
        help="Root for source/test evidence; compatibility default is cwd, but lifecycle validation requires it.",
    )


def cmd_validate_lifecycle_state(args: argparse.Namespace) -> dict[str, Any]:
    if args.artifact_root is None or args.code_root is None:
        raise SliceproofError([
            "validate-lifecycle-state: --artifact-root and --code-root are required for planned-feature authority"
        ])
    if not FEATURE_RE.fullmatch(args.feature):
        raise SliceproofError(["--feature: expected lowercase slug with letters, digits, and hyphens"])

    cwd = Path.cwd().resolve(strict=False)
    artifact_root = resolve_cli_root(args.artifact_root, cwd, "--artifact-root")
    code_root = resolve_cli_root(args.code_root, cwd, "--code-root")
    if artifact_root == code_root:
        raise SliceproofError(["validate-lifecycle-state: artifact root and code root must be distinct"])
    require_exact_git_root(artifact_root, "artifact root")
    require_exact_git_root(code_root, "code root")

    relative_path = f".tasks/{args.feature}/lifecycle-state.json"
    state = load_strict_json_file(resolve_authority_file(artifact_root, relative_path, "Lifecycle State"), "Lifecycle State")
    errors = validate_lifecycle_state_data(
        state,
        artifact_root=artifact_root,
        code_root=code_root,
        feature=args.feature,
        verify_files=True,
        verify_git_objects=True,
    )
    if errors:
        raise SliceproofError(errors)

    head = git_head_or_none(artifact_root)
    lineage_errors = validate_artifact_checkpoint_lineage(
        artifact_root,
        state["artifact_checkpoint"]["sha"],
        head,
        "lifecycle-state.json.artifact_checkpoint.sha",
    )
    if lineage_errors:
        raise SliceproofError(lineage_errors)

    generation = state["generation"]
    previous_digest: str | None = None
    if generation == 1:
        if args.previous_commit is not None:
            raise SliceproofError(["validate-lifecycle-state: generation 1 must not name --previous-commit"])
        validate_generation_one_topology(artifact_root, relative_path, state)
    else:
        if args.previous_commit is None:
            raise SliceproofError(["validate-lifecycle-state: --previous-commit is required after generation 1"])
        if args.previous_commit != state["last_verified"]["artifact_sha"]:
            raise SliceproofError([
                "validate-lifecycle-state: --previous-commit does not match last_verified.artifact_sha"
            ])
        previous = load_committed_lifecycle_state(
            artifact_root, relative_path, args.previous_commit, current_state=state
        )
        prior_errors = validate_lifecycle_state_data(
            previous,
            artifact_root=artifact_root,
            code_root=code_root,
            feature=args.feature,
            verify_files=False,
            verify_git_objects=False,
        )
        if prior_errors:
            raise SliceproofError([f"prior snapshot: {error}" for error in prior_errors])
        prior_artifact = previous["artifact_checkpoint"]
        if prior_artifact["sha"] is not None:
            prior_object_errors: list[str] = []
            prior_tree = git_commit_tree(
                artifact_root,
                prior_artifact["sha"],
                "prior snapshot: artifact_checkpoint.sha",
                prior_object_errors,
            )
            if prior_tree is not None and prior_tree != prior_artifact["tree"]:
                prior_object_errors.append(
                    "prior snapshot: artifact_checkpoint.tree does not match checkpoint commit tree"
                )
            if prior_object_errors:
                raise SliceproofError(prior_object_errors)
        if previous["quiescent"] is not True:
            raise SliceproofError(["prior snapshot: last_verified fallback must be quiescent"])
        prior_lineage_errors = validate_artifact_checkpoint_lineage(
            artifact_root,
            previous["artifact_checkpoint"]["sha"],
            args.previous_commit,
            "prior snapshot: artifact_checkpoint.sha",
        )
        if prior_lineage_errors:
            raise SliceproofError(prior_lineage_errors)
        previous_digest = canonical_json_digest(previous)
        if state["last_verified"]["state_digest"] != previous_digest:
            raise SliceproofError([
                "lifecycle-state.json.last_verified.state_digest: does not match the committed predecessor state"
            ])
        transition_errors = compare_lifecycle_states(previous, state)
        transition_errors.extend(validate_artifact_checkpoint_ancestry(artifact_root, previous, state))
        if transition_errors:
            raise SliceproofError(transition_errors)

    return {
        "artifact_root": str(artifact_root),
        "code_root": str(code_root),
        "state_path": relative_path,
        "feature": args.feature,
        "schema_version": state["schema_version"],
        "generation": generation,
        "stage": state["stage"],
        "quiescent": state["quiescent"],
        "state_digest": canonical_json_digest(state),
        "previous_commit": args.previous_commit,
        "previous_state_digest": previous_digest,
    }


def load_strict_json_file(path: Path, label: str) -> Any:
    return load_strict_json_text(read_text_file(path, label), label)


def load_strict_json_text(text: str, label: str) -> Any:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate key {key!r}")
            result[key] = value
        return result

    try:
        return json.loads(text, object_pairs_hook=reject_duplicates)
    except json.JSONDecodeError as exc:
        raise SliceproofError([f"{label}: invalid JSON at line {exc.lineno} column {exc.colno}: {exc.msg}"])
    except ValueError as exc:
        raise SliceproofError([f"{label}: invalid JSON: {exc}"])


# Compact shape grammar: mappings are exact (`?` marks optional); tuple tags cover nullable/pattern/enum/rule/list/map.
TOKEN_SCHEMA = ("pattern", SAFE_TOKEN_RE, "safe token")
DIGEST_SCHEMA = ("pattern", DIGEST_RE, "lowercase sha256:<64-hex> digest")
SHA_SCHEMA = ("pattern", EXACT_GIT_SHA_RE, "exact lowercase 40- or 64-hex Git object id")
ACTION_SCHEMA = ("pattern", ACTION_RE, "safe action token")
COUNTER_SCHEMA = ("pattern", COUNTER_RE, "safe counter token")
PACKAGE_ID_SCHEMA = ("pattern", PACKAGE_ID_RE, "WP<N> package id")
WAVE_ID_SCHEMA = ("pattern", WAVE_ID_RE, "wave-<slug>")
POSITIVE_INT_SCHEMA = ("rule", lambda value: type(value) is int and value > 0, "positive integer")
NONNEGATIVE_INT_SCHEMA = ("rule", lambda value: type(value) is int and value >= 0, "non-negative integer")
NULLABLE_TOKEN_SCHEMA = ("nullable", TOKEN_SCHEMA)
NULLABLE_DIGEST_SCHEMA = ("nullable", DIGEST_SCHEMA)
NULLABLE_SHA_SCHEMA = ("nullable", SHA_SCHEMA)
AUTHORIZATION_INPUTS_SCHEMA = {
    "artifact_tree": SHA_SCHEMA,
    "base_commit": SHA_SCHEMA,
    "clean_status": DIGEST_SCHEMA,
    "dependencies": DIGEST_SCHEMA,
    "routing": DIGEST_SCHEMA,
    "actions": DIGEST_SCHEMA,
    "budget_authority": DIGEST_SCHEMA,
    "amendment_policy": DIGEST_SCHEMA,
}
BUDGET_SCHEMA = ("nullable", {
    "maxima": ("map", COUNTER_SCHEMA, NONNEGATIVE_INT_SCHEMA),
    "issued": ("map", COUNTER_SCHEMA, NONNEGATIVE_INT_SCHEMA),
    "started_at": str,
    "deadline_at": str,
})
LIFECYCLE_JSON_SCHEMA = {
    "schema_version": ("rule", lambda value: type(value) is int and value == 1, "1"),
    "generation": POSITIVE_INT_SCHEMA,
    "feature": str,
    "stage": ("enum", LIFECYCLE_STAGES),
    "quiescent": bool,
    "next_legal_actions": ("list", ACTION_SCHEMA),
    "owner": {
        "token": NULLABLE_TOKEN_SCHEMA,
        "host": NULLABLE_TOKEN_SCHEMA,
        "disposition": ("enum", OWNER_DISPOSITIONS),
        "takeover": ("nullable", {
            "previous_token": TOKEN_SCHEMA,
            "previous_host": TOKEN_SCHEMA,
            "previous_generation": POSITIVE_INT_SCHEMA,
            "evidence_digest": DIGEST_SCHEMA,
        }),
    },
    "artifact_checkpoint": {"ref": str, "sha": NULLABLE_SHA_SCHEMA, "tree": NULLABLE_SHA_SCHEMA},
    "code_checkpoint": ("nullable", {"ref": str, "sha": SHA_SCHEMA}),
    "authorization": {
        "id": NULLABLE_TOKEN_SCHEMA,
        "initial_digest": NULLABLE_DIGEST_SCHEMA,
        "effective_digest": NULLABLE_DIGEST_SCHEMA,
        "inputs": ("nullable", AUTHORIZATION_INPUTS_SCHEMA),
        "amendment_link": ("nullable", {
            "parent_effective_digest": DIGEST_SCHEMA,
            "amendment_digest": DIGEST_SCHEMA,
            "artifact_sha": SHA_SCHEMA,
        }),
    },
    "budgets": {
        "preauthorization": BUDGET_SCHEMA,
        "implementation": BUDGET_SCHEMA,
        "active_reservation": ("nullable", {
            "id": TOKEN_SCHEMA,
            "owner_token": TOKEN_SCHEMA,
            "budget": ("enum", {"preauthorization", "implementation"}),
            "generation": POSITIVE_INT_SCHEMA,
            "units": ("map", COUNTER_SCHEMA, POSITIVE_INT_SCHEMA),
        }),
        "control_plane_reserve": {"maximum": NONNEGATIVE_INT_SCHEMA, "issued": NONNEGATIVE_INT_SCHEMA},
    },
    "packages": ("map", PACKAGE_ID_SCHEMA, {
        "state": ("enum", PACKAGE_LIFECYCLE_STATES), "wave": ("nullable", WAVE_ID_SCHEMA),
    }),
    "wave": ("nullable", {
        "id": WAVE_ID_SCHEMA,
        "generation": POSITIVE_INT_SCHEMA,
        "state": ("enum", WAVE_STATES),
        "packages": ("list", PACKAGE_ID_SCHEMA),
    }),
    "serious_clusters": ("list", {
        "id": DIGEST_SCHEMA,
        "strikes": ("enum", {1, 2}),
        "disposition": ("enum", CLUSTER_DISPOSITIONS),
    }),
    "freeze": ("nullable", {"id": TOKEN_SCHEMA, "digest": DIGEST_SCHEMA}),
    "receipts": ("list", {
        "role": ACTION_SCHEMA, "path": str, "digest": DIGEST_SCHEMA, "freeze_digest?": NULLABLE_DIGEST_SCHEMA,
    }),
    "last_verified": ("nullable", {
        "artifact_ref": str,
        "artifact_sha": SHA_SCHEMA,
        "state_digest": DIGEST_SCHEMA,
        "generation": POSITIVE_INT_SCHEMA,
    }),
    "portability_authorization": str,
    "assurance_profile?": ("enum", ASSURANCE_PROFILES),
    "package_modes?": ("map", PACKAGE_ID_SCHEMA, ("enum", PACKAGE_VERIFICATION_MODES)),
}


def validate_json_shape(value: Any, schema: Any, label: str, errors: list[str]) -> None:
    if isinstance(schema, dict):
        if not isinstance(value, dict):
            errors.append(f"{label}: expected object")
            return
        fields = {key.removesuffix("?"): item for key, item in schema.items()}
        required = {key for key in schema if not key.endswith("?")}
        for key in sorted(required - set(value)):
            errors.append(f"{label}: missing required field {key!r}")
        for key in sorted(set(value) - set(fields)):
            errors.append(f"{label}.{key}: unsupported field")
        for key in sorted(set(value) & set(fields)):
            validate_json_shape(value[key], fields[key], f"{label}.{key}", errors)
        return
    if schema is str or schema is bool:
        if type(value) is not schema:
            errors.append(f"{label}: expected {schema.__name__}")
        return
    kind = schema[0]
    if kind == "nullable":
        if value is not None:
            validate_json_shape(value, schema[1], label, errors)
    elif kind == "pattern":
        if not isinstance(value, str) or not schema[1].fullmatch(value):
            errors.append(f"{label}: expected {schema[2]}")
    elif kind == "enum":
        allowed_types = {type(item) for item in schema[1]}
        if type(value) not in allowed_types or value not in schema[1]:
            errors.append(f"{label}: expected one of {sorted(schema[1])}")
    elif kind == "rule":
        if not schema[1](value):
            errors.append(f"{label}: expected {schema[2]}")
    elif kind == "list":
        if not isinstance(value, list):
            errors.append(f"{label}: expected array")
        else:
            for index, item in enumerate(value):
                validate_json_shape(item, schema[1], f"{label}[{index}]", errors)
    elif kind == "map":
        if not isinstance(value, dict):
            errors.append(f"{label}: expected object")
        else:
            for key in sorted(value):
                validate_json_shape(key, schema[1], f"{label} key", errors)
                validate_json_shape(value[key], schema[2], f"{label}.{key}", errors)


def validate_lifecycle_state_data(
    state: Any,
    *,
    artifact_root: Path,
    code_root: Path,
    feature: str,
    verify_files: bool,
    verify_git_objects: bool,
) -> list[str]:
    label = "lifecycle-state.json"
    errors: list[str] = []
    validate_json_shape(state, LIFECYCLE_JSON_SCHEMA, label, errors)
    if errors:
        return errors

    generation, stage = state["generation"], state["stage"]
    if state["feature"] != feature:
        errors.append(f"{label}.feature: expected {feature!r}")
    actions = state["next_legal_actions"]
    if len(actions) != len(set(actions)) or len(actions) > 8:
        errors.append(f"{label}.next_legal_actions: actions must be unique and bounded to eight")
    if not actions and stage != "completed":
        errors.append(f"{label}.next_legal_actions: non-completed state requires at least one action")
    portability = state["portability_authorization"]
    if not portability.strip() or len(portability) > 512:
        errors.append(f"{label}.portability_authorization: expected concise non-empty source text")

    owner = state["owner"]
    if owner["disposition"] == "unassigned" and (owner["token"] is not None or owner["host"] is not None):
        errors.append(f"{label}.owner: unassigned owner must have null token and host")
    if owner["disposition"] != "unassigned" and (owner["token"] is None or owner["host"] is None):
        errors.append(f"{label}.owner: {owner['disposition']} owner requires token and host")
    takeover = owner["takeover"]
    if takeover is not None and takeover["previous_generation"] >= generation:
        errors.append(f"{label}.owner.takeover.previous_generation: must be below current generation")

    artifact = state["artifact_checkpoint"]
    expected_artifact_ref = f"refs/heads/artifacts/{feature}"
    if artifact["ref"] != expected_artifact_ref:
        errors.append(f"{label}.artifact_checkpoint.ref: expected {expected_artifact_ref!r}")
    if (artifact["sha"] is None) != (artifact["tree"] is None):
        errors.append(f"{label}.artifact_checkpoint: sha and tree must both be null or exact object IDs")
    elif artifact["sha"] is not None and verify_git_objects:
        actual_tree = git_commit_tree(artifact_root, artifact["sha"], f"{label}.artifact_checkpoint.sha", errors)
        if actual_tree is not None and actual_tree != artifact["tree"]:
            errors.append(f"{label}.artifact_checkpoint.tree: does not match checkpoint commit tree")

    code = state["code_checkpoint"]
    if code is not None:
        match = re.fullmatch(
            rf"refs/heads/checkpoints/{re.escape(feature)}/[A-Za-z0-9][A-Za-z0-9-]*/g([1-9]\d*)",
            code["ref"],
        )
        if match is None:
            errors.append(
                f"{label}.code_checkpoint.ref: expected immutable refs/heads/checkpoints/{feature}/<slot>/g<generation>"
            )
        elif int(match.group(1)) > generation:
            errors.append(f"{label}.code_checkpoint.ref: checkpoint generation exceeds Lifecycle State generation")
        if verify_git_objects:
            require_git_commit(code_root, code["sha"], f"{label}.code_checkpoint.sha", errors)

    authorization = state["authorization"]
    auth_fields = ("id", "initial_digest", "effective_digest", "inputs")
    auth_values = [authorization[field] for field in auth_fields]
    authorization_complete = all(value is not None for value in auth_values)
    if any(value is not None for value in auth_values) and not authorization_complete:
        errors.append(
            f"{label}.authorization: id, initial_digest, effective_digest, and inputs must be all null or all set"
        )
    if stage in PREAUTH_LIFECYCLE_STAGES and authorization_complete:
        errors.append(f"{label}.authorization: must be empty before authorization")
    if stage in AUTHORIZED_LIFECYCLE_STAGES and not authorization_complete:
        errors.append(f"{label}.authorization: complete lineage is required at stage {stage!r}")
    if authorization_complete and artifact["sha"] is None:
        errors.append(f"{label}.artifact_checkpoint: authorized state requires exact commit and tree")
    if code is not None and not authorization_complete:
        errors.append(f"{label}.code_checkpoint: complete implementation authorization is required")

    amendment = authorization["amendment_link"]
    if amendment is not None and not authorization_complete:
        errors.append(f"{label}.authorization.amendment_link: requires complete authorization fields")
    if amendment is not None:
        computed = technical_amendment_effective_digest(
            amendment["parent_effective_digest"], amendment["amendment_digest"], amendment["artifact_sha"]
        )
        if authorization["effective_digest"] != computed:
            errors.append(f"{label}.authorization.effective_digest: does not match current amendment link")
        if amendment["artifact_sha"] != artifact["sha"]:
            errors.append(f"{label}.authorization.amendment_link.artifact_sha: must match artifact checkpoint sha")
        if generation == 1:
            errors.append(f"{label}.authorization.amendment_link: generation 1 has no predecessor to amend")
        if verify_git_objects:
            require_git_commit(
                artifact_root, amendment["artifact_sha"], f"{label}.authorization.amendment_link.artifact_sha", errors
            )

    validate_lifecycle_budget_invariants(state, authorization_complete, errors)

    packages, wave = state["packages"], state["wave"]
    if authorization_complete:
        inputs = authorization["inputs"]
        if authorization["initial_digest"] != canonical_json_digest(inputs):
            errors.append(f"{label}.authorization.initial_digest: must equal the canonical inputs digest")
        if verify_git_objects:
            require_git_tree(artifact_root, inputs["artifact_tree"], f"{label}.authorization.inputs.artifact_tree", errors)
            require_git_commit(code_root, inputs["base_commit"], f"{label}.authorization.inputs.base_commit", errors)
        profile = state.get("assurance_profile")
        modes = state.get("package_modes")
        if profile is None:
            errors.append(f"{label}.assurance_profile: required after authorization")
        if not isinstance(modes, dict) or not modes or set(modes) != set(packages):
            errors.append(f"{label}.package_modes: authorized state must bind every lifecycle package exactly")
        if not packages:
            errors.append(f"{label}.packages: authorized state requires at least one package")
        if authorization["effective_digest"] == authorization["initial_digest"]:
            if inputs["artifact_tree"] != artifact["tree"]:
                errors.append(
                    f"{label}.authorization.inputs.artifact_tree: must match the initial artifact checkpoint tree"
                )
            if profile is not None and isinstance(modes, dict):
                routing = canonical_json_digest({"assurance_profile": profile, "package_modes": modes})
                if inputs["routing"] != routing:
                    errors.append(f"{label}.authorization.inputs.routing: does not match initial lifecycle routing")
        expected_budget_authority = authorization_budget_authority_digest(state["budgets"])
        if inputs["budget_authority"] != expected_budget_authority:
            errors.append(f"{label}.authorization.inputs.budget_authority: does not match finite budget authority")

    if generation == 1:
        future_state = {
            "artifact_checkpoint": artifact["sha"] is not None or artifact["tree"] is not None,
            "code_checkpoint": code is not None,
            "authorization": any(value is not None for value in auth_values) or amendment is not None,
            "packages": bool(packages),
            "wave": wave is not None,
            "serious_clusters": bool(state["serious_clusters"]),
            "freeze": state["freeze"] is not None,
            "receipts": bool(state["receipts"]),
        }
        populated = sorted(name for name, present in future_state.items() if present)
        if populated:
            errors.append(f"{label}: generation 1 requires initial null/empty topology; found {populated}")
    if wave is None and any(package["wave"] is not None for package in packages.values()):
        errors.append(f"{label}.wave: package wave pointers require a current wave")
    if wave is not None:
        if wave["generation"] > generation:
            errors.append(f"{label}.wave.generation: cannot exceed Lifecycle State generation")
        if not wave["packages"] or len(wave["packages"]) != len(set(wave["packages"])):
            errors.append(f"{label}.wave.packages: expected non-empty unique package ids")
        for package_id in wave["packages"]:
            if package_id not in packages or packages[package_id]["wave"] != wave["id"]:
                errors.append(f"{label}.wave.packages: {package_id!r} must name a package pointing to current wave")
        for package_id, package in packages.items():
            if package["wave"] is not None and package["wave"] != wave["id"]:
                errors.append(f"{label}.packages.{package_id}.wave: does not match current wave")
            elif package["wave"] == wave["id"] and package_id not in wave["packages"]:
                errors.append(f"{label}.wave.packages: missing package {package_id!r} that points to current wave")

    cluster_ids = [cluster["id"] for cluster in state["serious_clusters"]]
    if len(cluster_ids) != len(set(cluster_ids)):
        errors.append(f"{label}.serious_clusters: duplicate cluster id")
    for package_id in state.get("package_modes", {}):
        if package_id not in packages:
            errors.append(f"{label}.package_modes.{package_id}: package is not present in lifecycle packages")

    validate_receipt_pointers(state["receipts"], artifact_root, feature, errors, verify_files)
    verified = state["last_verified"]
    if generation == 1 and verified is not None:
        errors.append(f"{label}.last_verified: generation 1 must use null")
    elif generation > 1:
        if verified is None:
            errors.append(f"{label}.last_verified: required after generation 1")
        else:
            if verified["artifact_ref"] != expected_artifact_ref:
                errors.append(f"{label}.last_verified.artifact_ref: expected {expected_artifact_ref!r}")
            if verified["generation"] >= generation:
                errors.append(f"{label}.last_verified.generation: must be below current generation")
    return errors


def validate_lifecycle_budget_invariants(
    state: dict[str, Any], authorization_complete: bool, errors: list[str]
) -> None:
    label = "lifecycle-state.json.budgets"
    budgets = state["budgets"]
    for name in ("preauthorization", "implementation"):
        budget = budgets[name]
        if budget is None:
            continue
        maxima, issued = budget["maxima"], budget["issued"]
        if not maxima or set(maxima) != set(issued):
            errors.append(f"{label}.{name}: maxima and issued require the same non-empty counters")
        required = PREAUTH_REQUIRED_COUNTERS if name == "preauthorization" else IMPLEMENTATION_REQUIRED_COUNTERS
        missing = required - set(maxima)
        if missing:
            errors.append(f"{label}.{name}: missing required counters {sorted(missing)}")
        for counter in sorted(set(maxima) & set(issued)):
            if issued[counter] > maxima[counter]:
                errors.append(f"{label}.{name}.issued.{counter}: issued usage exceeds maximum")
        started = parse_aware_iso8601(budget["started_at"], f"{label}.{name}.started_at", errors)
        deadline = parse_aware_iso8601(budget["deadline_at"], f"{label}.{name}.deadline_at", errors)
        if started is not None and deadline is not None and deadline <= started:
            errors.append(f"{label}.{name}.deadline_at: must be later than started_at")
    if state["stage"] in PREAUTH_BUDGET_STAGES and budgets["preauthorization"] is None:
        errors.append(f"{label}.preauthorization: required at stage {state['stage']!r}")
    if authorization_complete and (budgets["preauthorization"] is None or budgets["implementation"] is None):
        errors.append(f"{label}: authorized state requires preauthorization and implementation budgets")
    if not authorization_complete and budgets["implementation"] is not None:
        errors.append(f"{label}.implementation: must be null before authorization")
    control = budgets["control_plane_reserve"]
    if control["maximum"] != 1 or control["issued"] > 1:
        errors.append(f"{label}.control_plane_reserve: expected fixed maximum 1 and issued 0 or 1")

    reservation = budgets["active_reservation"]
    if reservation is None:
        return
    owner = state["owner"]
    if owner["disposition"] != "active" or reservation["owner_token"] != owner["token"]:
        errors.append(f"{label}.active_reservation: requires and must match active owner")
    if reservation["generation"] != state["generation"]:
        errors.append(f"{label}.active_reservation.generation: must equal Lifecycle State generation")
    selected = budgets[reservation["budget"]]
    if selected is None:
        errors.append(f"{label}.active_reservation.budget: selected budget is not active")
        return
    if not reservation["units"]:
        errors.append(f"{label}.active_reservation.units: expected non-empty counter object")
    for counter, amount in reservation["units"].items():
        if counter not in selected["issued"]:
            errors.append(f"{label}.active_reservation.units.{counter}: unsupported budget counter")
        elif amount > selected["issued"][counter]:
            errors.append(f"{label}.active_reservation.units.{counter}: reservation is not already charged")


def validate_receipt_pointers(
    receipts: list[dict[str, Any]],
    artifact_root: Path,
    feature: str,
    errors: list[str],
    verify_files: bool,
) -> None:
    label = "lifecycle-state.json.receipts"
    seen: set[tuple[str, str]] = set()
    for index, receipt in enumerate(receipts):
        item_label = f"{label}[{index}]"
        try:
            path = repo_relative_path(receipt["path"], f"{item_label}.path")
        except SliceproofError as exc:
            errors.extend(exc.errors)
            continue
        if len(path.parts) < 3 or path.parts[:2] != (".tasks", feature):
            errors.append(f"{item_label}.path: must remain under .tasks/{feature}/")
            continue
        key = (receipt["role"], receipt["path"])
        if key in seen:
            errors.append(f"{label}: duplicate role/path pointer {key!r}")
        seen.add(key)
        if verify_files:
            try:
                receipt_path = resolve_authority_file(artifact_root, receipt["path"], f"{item_label}.path")
            except SliceproofError as exc:
                errors.extend(exc.errors)
            else:
                if digest_bytes(receipt_path.read_bytes()) != receipt["digest"]:
                    errors.append(f"{item_label}.digest: does not match current receipt file")


def technical_amendment_effective_digest(parent: str, amendment: str, artifact_sha: str) -> str:
    return canonical_json_digest({
        "artifact_sha": artifact_sha,
        "parent_effective_digest": parent,
        "technical_amendment_digest": amendment,
    })


def authorization_budget_authority_digest(budgets: dict[str, Any]) -> str:
    def fixed_budget(name: str) -> dict[str, Any] | None:
        budget = budgets[name]
        if budget is None:
            return None
        return {
            "maxima": budget["maxima"],
            "started_at": budget["started_at"],
            "deadline_at": budget["deadline_at"],
        }

    return canonical_json_digest({
        "preauthorization": fixed_budget("preauthorization"),
        "implementation": fixed_budget("implementation"),
        "control_plane_maximum": budgets["control_plane_reserve"]["maximum"],
    })


def validate_generation_one_topology(artifact_root: Path, relative_path: str, state: dict[str, Any]) -> None:
    head = git_head_or_none(artifact_root)
    if head is None:
        return
    try:
        committed = git_output(
            artifact_root, ["show", f"{head}:{relative_path}"], "validate-lifecycle-state: committed generation 1 state"
        )
    except SliceproofError:
        raise SliceproofError(["validate-lifecycle-state: generation 1 cannot reset committed lifecycle history"])
    parents = git_output(
        artifact_root, ["rev-list", "--parents", "-n", "1", head], "validate-lifecycle-state: generation 1 ancestry"
    ).split()
    if len(parents) != 1 or canonical_json_digest(load_strict_json_text(committed, "committed generation 1 Lifecycle State")) != canonical_json_digest(state):
        raise SliceproofError(["validate-lifecycle-state: generation 1 cannot reset committed lifecycle history"])


def load_committed_lifecycle_state(
    artifact_root: Path,
    relative_path: str,
    commit: str,
    *,
    current_state: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    if not require_exact_git_sha(commit, "validate-lifecycle-state: --previous-commit", errors):
        raise SliceproofError(errors)
    require_git_commit(artifact_root, commit, "validate-lifecycle-state: --previous-commit", errors)
    if errors:
        raise SliceproofError(errors)
    tree_line = git_output(
        artifact_root, ["ls-tree", commit, "--", relative_path], "validate-lifecycle-state: committed predecessor path"
    ).strip()
    fields = tree_line.split(None, 3)
    if len(fields) != 4 or fields[0] not in {"100644", "100755"} or fields[1] != "blob" or fields[3] != relative_path:
        raise SliceproofError([
            "validate-lifecycle-state: predecessor Lifecycle State must be a regular committed blob at the derived path"
        ])
    previous = load_strict_json_text(
        git_output(
            artifact_root, ["show", f"{commit}:{relative_path}"], "validate-lifecycle-state: predecessor Lifecycle State"
        ),
        "predecessor Lifecycle State",
    )
    if not isinstance(previous, dict):
        raise SliceproofError(["predecessor Lifecycle State: root must be an object"])
    validate_predecessor_topology(artifact_root, relative_path, commit, current_state)
    return previous


def validate_predecessor_topology(
    artifact_root: Path,
    relative_path: str,
    previous_commit: str,
    current_state: dict[str, Any],
) -> None:
    head = git_output(artifact_root, ["rev-parse", "HEAD"], "validate-lifecycle-state: artifact HEAD").strip()
    if head == previous_commit:
        return
    committed_current = load_strict_json_text(
        git_output(
            artifact_root, ["show", f"{head}:{relative_path}"], "validate-lifecycle-state: committed current Lifecycle State"
        ),
        "committed current Lifecycle State",
    )
    if canonical_json_digest(committed_current) != canonical_json_digest(current_state):
        raise SliceproofError([
            "validate-lifecycle-state: current working state is not based on the named predecessor snapshot"
        ])
    parents = git_output(
        artifact_root, ["rev-list", "--parents", "-n", "1", head], "validate-lifecycle-state: artifact checkpoint ancestry"
    ).split()
    if len(parents) != 2 or parents[1] != previous_commit:
        raise SliceproofError([
            "validate-lifecycle-state: committed current state must have the named predecessor as its sole parent"
        ])


def compare_lifecycle_states(previous: dict[str, Any], current: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if current["generation"] != previous["generation"] + 1:
        errors.append("lifecycle transition: generation must advance exactly once from committed predecessor")
    if current["last_verified"]["generation"] != previous["generation"]:
        errors.append("lifecycle transition: last_verified.generation must equal predecessor generation")

    previous_owner, current_owner = previous["owner"], current["owner"]
    if current_owner["token"] == previous_owner["token"]:
        if current_owner["host"] != previous_owner["host"]:
            errors.append("lifecycle transition: owner host cannot reset while owner token is unchanged")
        if current_owner.get("takeover") != previous_owner.get("takeover"):
            errors.append("lifecycle transition: takeover provenance is immutable for the same owner")
        if previous_owner["disposition"] == "released" and current_owner["disposition"] != "released":
            errors.append("lifecycle transition: released owner disposition is terminal")
    elif previous_owner["token"] is None:
        if current_owner.get("takeover") is not None or (
            current_owner.get("token") is not None and current_owner.get("disposition") != "active"
        ):
            errors.append("lifecycle transition: initial owner acquisition must become active without takeover provenance")
    else:
        takeover = current_owner.get("takeover")
        valid_takeover = (
            previous_owner["disposition"] in {"stopped", "released"}
            and current_owner["disposition"] == "active"
            and isinstance(takeover, dict)
            and takeover.get("previous_token") == previous_owner["token"]
            and takeover.get("previous_host") == previous_owner["host"]
            and takeover.get("previous_generation") == previous["generation"]
        )
        if not valid_takeover:
            errors.append("lifecycle transition: owner/host change requires exact stopped-owner takeover provenance")

    if previous["artifact_checkpoint"]["ref"] != current["artifact_checkpoint"]["ref"]:
        errors.append("lifecycle transition: artifact checkpoint ref is immutable")
    if previous["artifact_checkpoint"]["sha"] is not None and current["artifact_checkpoint"]["sha"] is None:
        errors.append("lifecycle transition: artifact checkpoint cannot reset to null")
    if previous["portability_authorization"] != current["portability_authorization"]:
        errors.append("lifecycle transition: portability authorization source is immutable")
    previous_code, current_code = previous.get("code_checkpoint"), current.get("code_checkpoint")
    if previous_code and current_code is None:
        errors.append("lifecycle transition: code checkpoint cannot reset to null")
    elif previous_code and current_code:
        if previous_code["ref"] == current_code["ref"] and previous_code["sha"] != current_code["sha"]:
            errors.append("lifecycle transition: immutable code checkpoint ref cannot change sha")
        elif previous_code["ref"] != current_code["ref"] and checkpoint_ref_generation(current_code["ref"]) <= checkpoint_ref_generation(previous_code["ref"]):
            errors.append("lifecycle transition: code checkpoint generation must advance when ref changes")

    previous_auth, current_auth = previous["authorization"], current["authorization"]
    previous_authorized = previous_auth["id"] is not None
    current_authorized = current_auth["id"] is not None
    authorization_changed = False
    if previous_authorized:
        if not current_authorized:
            errors.append("lifecycle transition: authorization cannot reset")
        else:
            for field in ("id", "initial_digest", "inputs"):
                if current_auth[field] != previous_auth[field]:
                    errors.append(f"lifecycle transition: authorization {field} is immutable")
            authorization_changed = current_auth["effective_digest"] != previous_auth["effective_digest"]
            link = current_auth.get("amendment_link")
            old_artifact = previous["artifact_checkpoint"]["sha"]
            new_artifact = current["artifact_checkpoint"]["sha"]
            if authorization_changed:
                if not isinstance(link, dict) or link.get("parent_effective_digest") != previous_auth["effective_digest"]:
                    errors.append("lifecycle transition: effective authorization digest requires an exact amendment link")
                if new_artifact == old_artifact:
                    errors.append("lifecycle transition: effective authorization digest requires a distinct artifact checkpoint")
                if not isinstance(link, dict) or link.get("artifact_sha") != new_artifact:
                    errors.append("lifecycle transition: amendment link must name the exact new artifact checkpoint")
            elif link is not None:
                errors.append("lifecycle transition: amendment_link is allowed only for this generation's effective-digest change")
            if new_artifact != old_artifact and not authorization_changed:
                errors.append("lifecycle transition: authorized artifact checkpoint changed without technical amendment")
            if not authorization_changed:
                for field in ("assurance_profile", "package_modes"):
                    if current.get(field) != previous.get(field):
                        errors.append(f"lifecycle transition: authorized {field} changed without technical amendment")
    elif current_authorized and (
        current_auth["effective_digest"] != current_auth["initial_digest"] or current_auth.get("amendment_link") is not None
    ):
        errors.append("lifecycle transition: initial authorization must start at its initial digest without amendment history")

    errors.extend(compare_lifecycle_budgets(previous["budgets"], current["budgets"]))
    previous_packages, current_packages = previous["packages"], current["packages"]
    if previous_authorized and not authorization_changed and set(previous_packages) != set(current_packages):
        errors.append("lifecycle transition: authorized package membership changed without technical amendment")
    errors.extend(compare_package_states(previous_packages, current_packages, authorization_changed))

    previous_wave, current_wave = previous["wave"], current["wave"]
    if previous_wave is not None:
        if current_wave is None or current_wave["id"] != previous_wave["id"]:
            if previous_wave["state"] not in {"completed", "blocked"}:
                errors.append("lifecycle transition: current wave cannot disappear or change before terminal disposition")
        else:
            if current_wave["generation"] != previous_wave["generation"]:
                errors.append("lifecycle transition: current wave generation is immutable")
            if current_wave["packages"] != previous_wave["packages"]:
                errors.append("lifecycle transition: current wave package membership is immutable")
            if previous_wave["state"] in {"completed", "blocked"} and current_wave["state"] != previous_wave["state"]:
                errors.append("lifecycle transition: terminal wave disposition is immutable")
            if previous_wave["state"] == "active" and current_wave["state"] == "reserved":
                errors.append("lifecycle transition: active wave cannot reset to reserved")

    previous_clusters = {item["id"]: item for item in previous["serious_clusters"]}
    current_clusters = {item["id"]: item for item in current["serious_clusters"]}
    for cluster_id, old in previous_clusters.items():
        new = current_clusters.get(cluster_id)
        if new is None:
            errors.append(f"lifecycle transition: serious cluster {cluster_id} cannot disappear")
            continue
        if new["strikes"] < old["strikes"]:
            errors.append(f"lifecycle transition: serious cluster {cluster_id} strikes cannot decrease")
        if old["disposition"] in {"closed", "circuit-open"} and new["disposition"] != old["disposition"]:
            errors.append(f"lifecycle transition: serious cluster {cluster_id} terminal disposition is immutable")

    if previous["freeze"] == current["freeze"]:
        old_receipts = {(item["role"], item["path"]): item for item in previous["receipts"]}
        new_receipts = {(item["role"], item["path"]): item for item in current["receipts"]}
        for key, old in old_receipts.items():
            if new_receipts.get(key) != old:
                errors.append(f"lifecycle transition: receipt pointer {key!r} cannot mutate under the same freeze")
    return errors


def compare_package_states(
    previous: dict[str, dict[str, Any]],
    current: dict[str, dict[str, Any]],
    authorization_changed: bool,
) -> list[str]:
    errors: list[str] = []
    for package_id in sorted(set(previous) & set(current)):
        old_state = previous[package_id]["state"]
        new_state = current[package_id]["state"]
        reviewed_replan_reset = (
            authorization_changed and old_state in REPLAN_RESET_STATES and new_state == "pending"
        )
        if new_state not in PACKAGE_STATE_TRANSITIONS[old_state] and not reviewed_replan_reset:
            suffix = "; pending replan reset requires a reviewed effective-digest change" if new_state == "pending" else ""
            errors.append(
                f"lifecycle transition: package {package_id} cannot move from {old_state} to {new_state}{suffix}"
            )
    return errors


def validate_artifact_checkpoint_lineage(
    artifact_root: Path,
    checkpoint_sha: str | None,
    lineage_tip: str | None,
    label: str,
) -> list[str]:
    if checkpoint_sha is None:
        return []
    if lineage_tip is None:
        return [f"{label}: cannot exist before the sidecar has an exact HEAD lineage"]
    result = git_process(
        artifact_root,
        ["merge-base", "--is-ancestor", checkpoint_sha, lineage_tip],
        label,
    )
    if result.returncode == 0:
        return []
    if result.returncode == 1:
        return [f"{label}: must be an ancestor of the exact sidecar HEAD/predecessor lineage"]
    detail = result.stderr.strip() or f"exit {result.returncode}"
    return [f"{label}: unable to verify exact sidecar lineage: {detail}"]


def validate_artifact_checkpoint_ancestry(
    artifact_root: Path,
    previous: dict[str, Any],
    current: dict[str, Any],
) -> list[str]:
    old_sha = previous["artifact_checkpoint"].get("sha")
    new_sha = current["artifact_checkpoint"].get("sha")
    if old_sha is None or new_sha is None or old_sha == new_sha:
        return []
    result = git_process(artifact_root, ["merge-base", "--is-ancestor", old_sha, new_sha], "lifecycle transition")
    if result.returncode == 0:
        return []
    if result.returncode == 1:
        return ["lifecycle transition: artifact checkpoint cannot move to a non-descendant commit"]
    detail = result.stderr.strip() or f"exit {result.returncode}"
    return [f"lifecycle transition: unable to verify artifact checkpoint ancestry: {detail}"]


def checkpoint_ref_generation(ref: str) -> int:
    return int(ref.rsplit("/g", 1)[1])


def compare_lifecycle_budgets(previous: dict[str, Any], current: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for budget_name in ("preauthorization", "implementation"):
        old, new = previous.get(budget_name), current.get(budget_name)
        if old is not None and new is None:
            errors.append(f"lifecycle transition: {budget_name} budget cannot reset to null")
            continue
        if old is None or new is None:
            continue
        if new["maxima"] != old["maxima"]:
            errors.append(f"lifecycle transition: {budget_name} maxima are fixed")
        for field in ("started_at", "deadline_at"):
            if new[field] != old[field]:
                errors.append(f"lifecycle transition: {budget_name} {field} is fixed")
        for counter, old_usage in old["issued"].items():
            if new["issued"].get(counter, -1) < old_usage:
                errors.append(f"lifecycle transition: {budget_name} issued {counter} cannot decrease")

    old_control, new_control = previous["control_plane_reserve"], current["control_plane_reserve"]
    if new_control["maximum"] != old_control["maximum"]:
        errors.append("lifecycle transition: control-plane reserve maximum is fixed")
    if new_control["issued"] < old_control["issued"]:
        errors.append("lifecycle transition: control-plane reserve issued usage cannot decrease")

    old_reservation, new_reservation = previous.get("active_reservation"), current.get("active_reservation")
    if old_reservation and new_reservation and old_reservation["id"] == new_reservation["id"]:
        if old_reservation != new_reservation:
            errors.append("lifecycle transition: active reservation cannot mutate under the same id")
    elif new_reservation is not None:
        budget_name = new_reservation["budget"]
        old_budget, new_budget = previous.get(budget_name), current.get(budget_name)
        old_issued = old_budget["issued"] if old_budget is not None else {}
        if new_budget is not None:
            for counter, amount in new_reservation["units"].items():
                if new_budget["issued"][counter] - old_issued.get(counter, 0) < amount:
                    errors.append(
                        f"lifecycle transition: reservation {counter} must be charged by this generation's issued delta"
                    )
    return errors


def resolve_authority_file(root: Path, value: str, label: str) -> Path:
    path = repo_relative_path(value, label)
    current = root
    for part in path.parts:
        current /= part
        if current.is_symlink():
            raise SliceproofError([f"{label}: authority path must not contain symlinks: {value}"])
    resolved = current.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError:
        raise SliceproofError([f"{label}: path escapes artifact root"])
    if not resolved.is_file():
        raise SliceproofError([f"{label}: file not found: {value}"])
    return resolved


def git_process(root: Path, args: list[str], label: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError as exc:
        raise SliceproofError([f"{label}: unable to invoke local git: {exc}"])


def git_output(root: Path, args: list[str], label: str) -> str:
    result = git_process(root, args, label)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise SliceproofError([f"{label}: local git inspection failed: {detail}"])
    return result.stdout


def git_head_or_none(root: Path) -> str | None:
    result = git_process(root, ["rev-parse", "--verify", "HEAD"], "validate-lifecycle-state")
    if result.returncode == 0:
        return result.stdout.strip()
    if result.returncode == 128 and "needed a single revision" in result.stderr.lower():
        return None
    raise SliceproofError([
        f"validate-lifecycle-state: unable to inspect artifact HEAD: {result.stderr.strip()}"
    ])


def require_exact_git_root(root: Path, label: str) -> None:
    top = git_output(root, ["rev-parse", "--show-toplevel"], f"validate-lifecycle-state: {label}").strip()
    if Path(top).resolve(strict=False) != root:
        raise SliceproofError([f"validate-lifecycle-state: {label} must be an exact Git worktree root"])


def require_git_commit(root: Path, sha: str, label: str, errors: list[str]) -> None:
    try:
        actual = git_output(root, ["rev-parse", f"{sha}^{{commit}}"], label).strip()
    except SliceproofError as exc:
        errors.extend(exc.errors)
        return
    if actual != sha:
        errors.append(f"{label}: does not resolve to the exact named commit")


def git_commit_tree(root: Path, sha: str, label: str, errors: list[str]) -> str | None:
    before = len(errors)
    require_git_commit(root, sha, label, errors)
    if len(errors) != before:
        return None
    try:
        return git_output(root, ["rev-parse", f"{sha}^{{tree}}"], label).strip()
    except SliceproofError as exc:
        errors.extend(exc.errors)
        return None


def require_git_tree(root: Path, sha: str, label: str, errors: list[str]) -> None:
    try:
        actual_type = git_output(root, ["cat-file", "-t", sha], label).strip()
    except SliceproofError as exc:
        errors.extend(exc.errors)
        return
    if actual_type != "tree":
        errors.append(f"{label}: does not resolve to the exact named tree")


def require_exact_git_sha(value: Any, label: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or not EXACT_GIT_SHA_RE.fullmatch(value):
        errors.append(f"{label}: expected exact lowercase 40- or 64-hex Git object id")
        return False
    return True


def parse_aware_iso8601(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str):
        errors.append(f"{label}: expected timezone-aware ISO-8601 timestamp")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label}: expected timezone-aware ISO-8601 timestamp")
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        errors.append(f"{label}: expected timezone-aware ISO-8601 timestamp")
        return None
    return parsed


def canonical_json_digest(value: Any) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def cmd_validate_plan(args: argparse.Namespace) -> dict[str, Any]:
    registry, packages = load_and_validate_plan(args.tasks, artifact_root=args.artifact_root, code_root=args.code_root)
    return {
        "tasks": str(args.tasks),
        "artifact_root": str(registry.root),
        "code_root": str(registry.code_root),
        "feature": registry.feature,
        "assurance_profile": registry.assurance_profile,
        "package_modes": {
            package.package_id: package.verification_mode
            for package in registry.packages
            if package.verification_mode is not None
        },
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

    preflight_registry = load_registry(args.tasks, artifact_root=args.artifact_root, code_root=args.code_root)
    preflight_package = preflight_registry.package(args.package)
    if preflight_package is not None and preflight_package.proof_path:
        reject_existing_symlink_at_unresolved_path(
            preflight_registry.root,
            preflight_package.proof_path,
            f"work_packages[{args.package}].proof_path",
            expected_suffix=".proof.md",
            error_message=f"create-proof: refusing to write through symlink proof path: {preflight_package.proof_path}",
        )

    registry, packages = load_and_validate_plan(args.tasks, artifact_root=args.artifact_root, code_root=args.code_root)
    package = require_package(registry, args.package)
    package_md = packages[package.package_id]
    proof_path = resolve_safe_path(
        registry.root,
        package.proof_path,
        f"work_packages[{package.package_id}].proof_path",
        expected_suffix=".proof.md",
        root_label="artifact root",
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
    state = load_package_state(args.tasks, args.package, artifact_root=args.artifact_root, code_root=args.code_root)
    errors = validate_proof_markdown(state.proof_path, state.package_md)
    if errors:
        raise SliceproofError(errors)
    return {
        "package": state.package.package_id,
        "proof_path": state.package.proof_path,
        "required_slice_rows": state.package_md.must_satisfy_ids,
        "verification_expectations": state.package_md.verification_expectations,
    }


def cmd_validate_package_complete(args: argparse.Namespace) -> dict[str, Any]:
    state = load_package_state(args.tasks, args.package, artifact_root=args.artifact_root, code_root=args.code_root)
    errors = validate_proof_markdown(state.proof_path, state.package_md)
    report_result = validate_report_markdown(
        state.report_path,
        state.package,
        state.package_md,
        state.proof_path,
        state.registry.root,
        state.registry.code_root,
        state.registry.feature,
    )
    errors.extend(report_result.errors)
    if errors:
        raise SliceproofError(errors, report_result.advisories)
    return {
        "package": state.package.package_id,
        "package_status": state.package.status,
        "proof_path": state.package.proof_path,
        "report_path": state.package.report_path,
        "required_slice_rows": state.package_md.must_satisfy_ids,
        "verification_expectation_rows": [f"VE-{index}" for index in range(1, len(state.package_md.verification_expectations) + 1)],
        "advisories": report_result.advisories,
    }


def cmd_emit_state_binding(args: argparse.Namespace) -> RawText:
    state = load_package_state(args.tasks, args.package, artifact_root=args.artifact_root, code_root=args.code_root)
    runtime_errors = validate_state_binding_runtime_metadata(
        "emit-state-binding",
        args.worktree,
        args.git_ref,
        args.commit,
        args.verified_at,
    )
    if runtime_errors:
        raise SliceproofError(runtime_errors)
    values = state_binding_values(
        state.registry.root,
        state.package,
        state.package_md,
        state.proof_path,
        worktree=args.worktree,
        git_ref=args.git_ref,
        commit=args.commit,
        verified_at=args.verified_at,
    )
    return RawText(render_state_binding_block(values))


def cmd_validate_final(args: argparse.Namespace) -> dict[str, Any]:
    registry, packages = load_and_validate_plan(args.tasks, artifact_root=args.artifact_root, code_root=args.code_root)
    errors: list[str] = []
    advisories: list[dict[str, Any]] = []
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
            root_label="artifact root",
        )
        report_path = resolve_safe_path(
            registry.root,
            package.report_path,
            f"work_packages[{package.package_id}].report_path",
            expected_suffix=".package-verification.md",
            root_label="artifact root",
        )
        errors.extend(validate_proof_markdown(proof_path, package_md))
        report_result = validate_report_markdown(
            report_path,
            package,
            package_md,
            proof_path,
            registry.root,
            registry.code_root,
            registry.feature,
        )
        advisories.extend(report_result.advisories)
        if not report_result.errors:
            validated_reports.append(package.report_path)
        errors.extend(report_result.errors)
    if errors:
        raise SliceproofError(errors, advisories)
    return {
        "feature": registry.feature,
        "packages": [package.package_id for package in registry.packages],
        "proofs_validated": [package.proof_path for package in registry.packages],
        "reports_validated": validated_reports,
        "advisories": advisories,
    }


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
    proof_path = resolve_safe_path(
        registry.root,
        package.proof_path,
        f"work_packages[{package.package_id}].proof_path",
        expected_suffix=".proof.md",
        root_label="artifact root",
    )
    report_path = resolve_safe_path(
        registry.root,
        package.report_path,
        f"work_packages[{package.package_id}].report_path",
        expected_suffix=".package-verification.md",
        root_label="artifact root",
    )
    return PackageState(registry, package, package_md, proof_path, report_path)


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
                verification_mode=(
                    item.get("verification_mode") if isinstance(item.get("verification_mode"), str) else None
                ),
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
        assurance_profile=(
            data.get("assurance_profile") if isinstance(data.get("assurance_profile"), str) else None
        ),
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
    assurance_profile = data.get("assurance_profile")
    if assurance_profile is not None and (
        not isinstance(assurance_profile, str) or assurance_profile not in ASSURANCE_PROFILES
    ):
        errors.append(f"assurance_profile: expected one of {sorted(ASSURANCE_PROFILES)} when present")

    spec_path = data.get("spec_path")
    if not isinstance(spec_path, str) or not spec_path.strip():
        errors.append("spec_path: expected non-empty string")
    else:
        try:
            resolve_safe_path(registry.root, spec_path, "spec_path", expected_suffix=".md", must_exist_file=True, root_label="artifact root")
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
                    root_label="artifact root",
                )
            except SliceproofError as exc:
                errors.extend(exc.errors)
        status = item.get("status")
        if not isinstance(status, str) or status not in STATUS_VALUES:
            errors.append(f"{prefix}.status: expected one of {sorted(STATUS_VALUES)}")
        verification_mode = item.get("verification_mode")
        if verification_mode is not None and (
            not isinstance(verification_mode, str) or verification_mode not in PACKAGE_VERIFICATION_MODES
        ):
            errors.append(
                f"{prefix}.verification_mode: expected one of {sorted(PACKAGE_VERIFICATION_MODES)} when present"
            )
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
            resolve_safe_path(registry.root, value, f"{package.path}: {key}", expected_suffix=suffix, root_label="artifact root")
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
        delimiter_error = state_binding_assigned_slice_path_error(ref.path, f"{package.path}: assigned Slice {ref.path!r}")
        if delimiter_error:
            errors.append(delimiter_error)
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


def h2_order(text: str) -> list[str]:
    names: list[str] = []
    in_fence = False
    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")
        stripped = line.strip()
        if is_fence(stripped):
            in_fence = not in_fence
            continue
        if not in_fence and line.startswith("## ") and not line.startswith("### "):
            names.append(line[3:].strip())
    return names


def split_h3_sections(text: str) -> dict[str, str]:
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
        if not in_fence and line.startswith("### ") and not line.startswith("#### "):
            current = line[4:].strip()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def h3_order(text: str) -> list[str]:
    names: list[str] = []
    in_fence = False
    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")
        stripped = line.strip()
        if is_fence(stripped):
            in_fence = not in_fence
            continue
        if not in_fence and line.startswith("### ") and not line.startswith("#### "):
            names.append(line[4:].strip())
    return names


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
    row_text = "\n".join([implementation, verification, sections["Gaps, Deviations, or Deferred Items"]])
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
    row_text = "\n".join([evidence, sections["Gaps, Deviations, or Deferred Items"]])
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
    root: Path,
    code_root: Path,
    feature: str,
) -> ReportValidationResult:
    if not report_path.is_file():
        return ReportValidationResult([f"report: file not found: {report_path}"], [])
    text = read_text_file(report_path, f"package verification report {report_path}")
    errors: list[str] = []
    sections = split_h2_sections(text)
    section_order = h2_order(text)
    source_section = f"Package Verification: {package.package_id}"
    if section_order and section_order[0] != source_section:
        errors.append(f"{report_path}: first report section must be ## {source_section}")
    if source_section in sections and "State Binding" in sections:
        source_index = section_order.index(source_section)
        state_index = section_order.index("State Binding")
        if state_index < source_index:
            errors.append(f"{report_path}: ## State Binding must appear after ## {source_section}")
    if source_section not in sections:
        found_source_sections = sorted(section for section in sections if section.startswith("Package Verification:"))
        if found_source_sections:
            errors.append(f"{report_path}: source report section must be ## {source_section}")
        else:
            errors.append(f"{report_path}: missing required section ## {source_section}")
    if "State Binding" not in sections:
        errors.append(f"{report_path}: missing required section ## State Binding")
    if source_section not in sections or "State Binding" not in sections:
        return ReportValidationResult(errors, [])

    source_h3 = split_h3_sections(sections[source_section])
    source_h3_names = h3_order(sections[source_section])
    canonical_h3_order = [
        "Verdict",
        "Deliverable Completeness Matrix",
        "Triggered Risk Selection Notes",
        "Test Review Scope",
        "Slice Closure Review",
        "Code Review Findings",
        "Blocking Findings",
        "Repair Guidance",
    ]
    present_canonical_h3 = [name for name in source_h3_names if name in canonical_h3_order]
    expected_h3_order = [name for name in canonical_h3_order if name in source_h3]
    if present_canonical_h3 != expected_h3_order:
        errors.append(
            f"{report_path}: source report sections must appear in order: "
            "### Verdict, ### Deliverable Completeness Matrix, ### Triggered Risk Selection Notes, "
            "### Test Review Scope, ### Slice Closure Review, ### Code Review Findings, "
            "### Blocking Findings, ### Repair Guidance"
        )
    for section in sorted(REQUIRED_SOURCE_REPORT_H3):
        if section not in source_h3:
            errors.append(f"{report_path}: missing required source section ### {section}")

    evidence_root = code_root.resolve(strict=False)

    verdict = ""
    if "Verdict" in source_h3:
        verdict = source_report_verdict(source_h3["Verdict"])
        if verdict not in {"PASS", "FAIL"}:
            errors.append(f"{report_path}: ### Verdict must be PASS or FAIL")
        elif verdict != "PASS":
            errors.append(f"{report_path}: ### Verdict must be PASS for final validation")
        if verdict == "FAIL":
            for section in sorted(FAILURE_SOURCE_REPORT_H3):
                if section not in source_h3:
                    errors.append(f"{report_path}: FAIL report missing required source section ### {section}")

    if "Deliverable Completeness Matrix" in source_h3:
        errors.extend(
            validate_deliverable_completeness_matrix(
                report_path,
                root,
                evidence_root,
                proof_path,
                package_md,
                source_h3["Deliverable Completeness Matrix"],
            )
        )
    if "Triggered Risk Selection Notes" in source_h3:
        errors.extend(validate_triggered_risk_selection_notes(report_path, source_h3["Triggered Risk Selection Notes"]))
    if "Test Review Scope" in source_h3:
        errors.extend(
            validate_test_review_scope(
                report_path,
                root,
                evidence_root,
                proof_path,
                source_h3["Test Review Scope"],
            )
        )
    if "Slice Closure Review" in source_h3:
        errors.extend(validate_report_slice_closure_review(report_path, package_md, source_h3["Slice Closure Review"]))
    if "Code Review Findings" in source_h3:
        errors.extend(validate_report_code_review_findings(report_path, source_h3["Code Review Findings"]))
    if "Blocking Findings" in source_h3 and not is_empty_gaps_deviations_section(source_h3["Blocking Findings"]):
        errors.append(f"{report_path}: ### Blocking Findings must be empty or None for final validation")
    if "Open Findings" in sections:
        open_findings = sections["Open Findings"]
        if UNRESOLVED_MARKER_RE.search(open_findings):
            errors.append(f"{report_path}: ## Open Findings contains unresolved TODO/OPEN marker")
        if not is_empty_gaps_deviations_section(open_findings):
            errors.append(f"{report_path}: ## Open Findings must be '- None.' for final validation")

    state_result = validate_report_state_binding(report_path, root, package, package_md, proof_path, sections["State Binding"])
    errors.extend(state_result.errors)
    if "Semgrep Evidence" in sections:
        errors.extend(validate_semgrep_evidence_binding(report_path, root, feature, package, sections["Semgrep Evidence"]))
    return ReportValidationResult(errors, state_result.advisories)


def source_report_verdict(body: str) -> str:
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"^(?:[-*]|\d+\.)\s+", "", line)
        return clean_cell_id(line).upper()
    return ""


def validate_deliverable_completeness_matrix(
    report_path: Path,
    root: Path,
    evidence_root: Path,
    proof_path: Path,
    package_md: PackageMarkdown,
    body: str,
) -> list[str]:
    errors: list[str] = []
    if is_report_section_placeholder_body(body):
        return [f"{report_path}: ### Deliverable Completeness Matrix must contain a non-placeholder matrix"]

    headers = extract_first_table_headers(body)
    if headers != MATRIX_COLUMNS:
        errors.append(f"{report_path}: ### Deliverable Completeness Matrix columns must be exactly {MATRIX_COLUMNS}")
    rows = parse_table(body)
    if not rows:
        errors.append(f"{report_path}: ### Deliverable Completeness Matrix must include deliverable rows")
        return errors

    try:
        proof_sections = split_h2_sections(read_text_file(proof_path, f"proof {proof_path}"))
    except SliceproofError as exc:
        errors.extend(exc.errors)
        proof_commands = ""
    else:
        proof_commands = proof_sections.get("Commands Run", "")

    required_sources: dict[str, str] = {slice_id: "slice" for slice_id in package_md.must_satisfy_ids}
    for index, _expectation in enumerate(package_md.verification_expectations, start=1):
        required_sources[f"VE-{index}"] = "verification-expectation"
    interface_ids = interface_bearing_slice_ids(root, package_md)

    rows_by_source: dict[str, ProofRow] = {}
    for index, row in enumerate(rows, start=1):
        source_id = clean_cell_id(row.cells.get("Source ID", ""))
        row_type = clean_cell_id(row.cells.get("Row Type", "")).lower()
        evidence_type = clean_cell_id(row.cells.get("Evidence Type", "")).lower()
        verdict = clean_cell_id(row.cells.get("Verdict", "")).lower()
        row_label = source_id or f"Deliverable Completeness Matrix row {index}"

        for column in MATRIX_COLUMNS:
            if is_report_section_placeholder_body(row.cells.get(column, "")):
                errors.append(f"{report_path}: {row_label} {column} must be non-placeholder")

        if source_id:
            if source_id in rows_by_source:
                errors.append(f"{report_path}: duplicate Deliverable Completeness Matrix row for {source_id}")
            else:
                rows_by_source[source_id] = row

        if row_type not in MATRIX_ROW_TYPES:
            errors.append(f"{report_path}: {row_label} Row Type {row_type!r} is not supported")
        if evidence_type not in MATRIX_EVIDENCE_TYPES:
            errors.append(f"{report_path}: {row_label} Evidence Type {evidence_type!r} is not supported")
        if verdict not in MATRIX_VERDICTS:
            errors.append(f"{report_path}: {row_label} Verdict {verdict!r} is not supported")
        elif verdict != MATRIX_CLEAN_VERDICT:
            errors.append(f"{report_path}: {row_label} Verdict must be delivered for package completion")

        expected_type = required_sources.get(source_id)
        if expected_type is not None and row_type and row_type != expected_type:
            errors.append(f"{report_path}: {source_id} Row Type must be {expected_type}")
        elif expected_type is None and row_type == "slice":
            errors.append(f"{report_path}: unexpected Deliverable Completeness Matrix slice row for {source_id}")
        elif expected_type is None and row_type == "verification-expectation":
            errors.append(f"{report_path}: unexpected Deliverable Completeness Matrix verification expectation row for {source_id}")
        elif row_type == "triggered-risk" and (not source_id or not RISK_SOURCE_ID_RE.fullmatch(source_id)):
            errors.append(f"{report_path}: {row_label} triggered-risk Source ID must match RISK-<slug-or-n>")

        errors.extend(
            validate_matrix_evidence_refs(
                report_path,
                root,
                evidence_root,
                proof_commands,
                row_label,
                evidence_type,
                row.cells.get("Evidence Refs", ""),
            )
        )
        if source_id in interface_ids and row_type == "slice":
            errors.extend(validate_interface_matrix_row(report_path, row_label, row.cells.get("Exactness / Risk Disposition", "")))
        if row_type == "triggered-risk":
            errors.extend(validate_triggered_risk_matrix_row(report_path, row_label, row.cells.get("Exactness / Risk Disposition", "")))

    for source_id, row_type in required_sources.items():
        if source_id not in rows_by_source:
            errors.append(f"{report_path}: ### Deliverable Completeness Matrix missing required {row_type} row for {source_id}")
    return errors


def extract_first_table_headers(body: str) -> list[str]:
    for raw_line in body.splitlines():
        cells = split_markdown_table_row(raw_line.strip())
        if cells is not None:
            return cells
    return []


def parse_test_review_scope_table(report_path: Path, body: str) -> tuple[list[ProofRow], list[str]]:
    label = f"{report_path}: ### Test Review Scope"
    numbered_lines = [
        (line_number, raw_line.strip())
        for line_number, raw_line in enumerate(body.splitlines(), start=1)
        if raw_line.strip()
    ]
    if any(is_fence(line) for _line_number, line in numbered_lines):
        return [], [f"{label} must not contain fenced content"]
    if not numbered_lines:
        return [], [f"{label} must include at least one surface row"]

    table_lines: list[tuple[int, list[str], str]] = []
    for line_number, line in numbered_lines:
        cells = split_markdown_table_row(line)
        if cells is None:
            return [], [
                f"{label} must contain exactly one contiguous Markdown table with no prose or ignored pipe fragments"
            ]
        table_lines.append((line_number, cells, line))

    line_numbers = [line_number for line_number, _cells, _line in table_lines]
    if line_numbers != list(range(line_numbers[0], line_numbers[0] + len(line_numbers))):
        return [], [
            f"{label} must contain exactly one contiguous Markdown table with no prose or ignored pipe fragments"
        ]

    headers = table_lines[0][1]
    errors: list[str] = []
    if headers != TEST_REVIEW_SCOPE_COLUMNS:
        errors.append(f"{label} columns must be exactly {TEST_REVIEW_SCOPE_COLUMNS}")
    expected_width = len(TEST_REVIEW_SCOPE_COLUMNS)
    if len(table_lines) < 2 or not is_markdown_table_delimiter(table_lines[1][1], expected_width):
        errors.append(
            f"{label} must place a matching-width Markdown delimiter immediately after the header"
        )
    if len(table_lines) < 3:
        errors.append(f"{label} must include at least one surface row")

    proof_rows: list[ProofRow] = []
    for table_index, (_line_number, cells, raw_line) in enumerate(table_lines[2:], start=3):
        if is_markdown_table_delimiter(cells, len(cells)):
            errors.append(f"{label} must contain exactly one contiguous Markdown table")
            continue
        if len(cells) != expected_width:
            errors.append(
                f"{report_path}: Test Review Scope table row {table_index} must contain exactly "
                f"{expected_width} cells"
            )
            continue
        proof_rows.append(ProofRow(dict(zip(TEST_REVIEW_SCOPE_COLUMNS, cells)), raw_line))

    if errors:
        return [], errors
    return proof_rows, []


def is_markdown_table_delimiter(cells: list[str], expected_width: int) -> bool:
    return len(cells) == expected_width and all(
        re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) is not None for cell in cells
    )


def validate_triggered_risk_selection_notes(report_path: Path, body: str) -> list[str]:
    if is_report_section_placeholder_body(body):
        return [f"{report_path}: ### Triggered Risk Selection Notes must contain non-placeholder risk selection notes"]
    if BLOCKING_MARKER_RE.search(body):
        return [f"{report_path}: ### Triggered Risk Selection Notes contains unresolved TODO/OPEN/GAP marker"]
    return []


def validate_test_review_scope(
    report_path: Path,
    root: Path,
    evidence_root: Path,
    proof_path: Path,
    body: str,
) -> list[str]:
    errors: list[str] = []
    if is_report_section_placeholder_body(body):
        return [f"{report_path}: ### Test Review Scope must contain a non-placeholder receipt"]
    if TEST_REVIEW_UNRESOLVED_MARKER_RE.search(body):
        errors.append(f"{report_path}: ### Test Review Scope contains unresolved TODO/OPEN/GAP marker")
    if TEST_REVIEW_FORBIDDEN_STATUS_RE.search(body):
        errors.append(f"{report_path}: ### Test Review Scope contains forbidden not-reviewed/unreviewed status")

    rows, table_errors = parse_test_review_scope_table(report_path, body)
    errors.extend(table_errors)
    if table_errors:
        return errors

    try:
        proof_sections = split_h2_sections(read_text_file(proof_path, f"proof {proof_path}"))
    except SliceproofError as exc:
        errors.extend(exc.errors)
        proof_commands = ""
    else:
        proof_commands = proof_sections.get("Commands Run", "")

    no_applicable_rows = [
        row
        for row in rows
        if normalize_test_review_value(row.cells.get("Review Depth", "")) == NO_APPLICABLE_TEST_SURFACE_DEPTH
    ]
    if no_applicable_rows:
        if len(rows) != 1 or not is_canonical_no_applicable_test_surface_row(no_applicable_rows[0]):
            errors.append(
                f"{report_path}: no-applicable-surface receipt must contain exactly one canonical none row"
            )
        errors.extend(
            validate_matrix_evidence_refs(
                report_path,
                root,
                evidence_root,
                proof_commands,
                "Test Review Scope no-applicable-surface row",
                "mixed",
                no_applicable_rows[0].cells.get("Evidence Refs", ""),
            )
        )
        return errors

    seen_surfaces: set[str] = set()
    for index, row in enumerate(rows, start=1):
        surface = normalize_test_review_value(row.cells.get("Surface", ""))
        depth = normalize_test_review_value(row.cells.get("Review Depth", ""))
        row_label = f"Test Review Scope {surface or f'row {index}'}"

        if surface not in TEST_REVIEW_SURFACES:
            errors.append(f"{report_path}: {row_label} Surface {surface!r} is not supported")
        elif surface in seen_surfaces:
            errors.append(f"{report_path}: duplicate Test Review Scope row for {surface}")
        else:
            seen_surfaces.add(surface)

        population = parse_test_review_components(row.cells.get("Changed Population", ""), ("count", "scope"))
        if population is None:
            errors.append(
                f"{report_path}: {row_label} Changed Population must use "
                "'count: <positive integer>; scope: <specific non-placeholder description>'"
            )
        else:
            count, scope = population
            if not count.isascii() or not count.isdecimal() or int(count) < 1:
                errors.append(f"{report_path}: {row_label} Changed Population count must be a positive integer")
            if not is_specific_test_review_payload(scope):
                errors.append(f"{report_path}: {row_label} Changed Population scope must be non-placeholder")

        if not has_test_review_grammar(row.cells.get("Baseline Review", ""), ("complete",)):
            errors.append(
                f"{report_path}: {row_label} Baseline Review must use "
                "'complete: <specific non-placeholder checks/results>'"
            )

        if surface == "other-test-relevant" and depth in TEST_REVIEW_DEPTHS and depth != "deep":
            errors.append(
                f"{report_path}: {row_label} Review Depth must be deep for other-test-relevant"
            )

        if depth not in TEST_REVIEW_DEPTHS:
            errors.append(f"{report_path}: {row_label} Review Depth {depth!r} is not supported")
        elif depth == "sampled":
            if not has_test_review_grammar(row.cells.get("Selected Exemplars", ""), ("selected",)):
                errors.append(
                    f"{report_path}: {row_label} sampled Selected Exemplars must use "
                    "'selected: <specific exemplars>'"
                )
            if not has_test_review_grammar(row.cells.get("Sampling Rationale", ""), ("strategy",)):
                errors.append(
                    f"{report_path}: {row_label} sampled Sampling Rationale must use "
                    "'strategy: <specific semantic selection rationale>'"
                )
        else:
            for column in ("Selected Exemplars", "Sampling Rationale"):
                if not has_test_review_grammar(row.cells.get(column, ""), ("not-applicable",)):
                    errors.append(
                        f"{report_path}: {row_label} {column} must use "
                        f"'not-applicable: <specific reason>' when depth is {depth}"
                    )

        if depth == "deep":
            if not has_test_review_grammar(row.cells.get("Deep Triggers", ""), ("triggered",)):
                errors.append(
                    f"{report_path}: {row_label} deep Deep Triggers must use "
                    "'triggered: <specific non-placeholder trigger>'"
                )
        elif depth in {"baseline-only", "sampled"} and not has_test_review_grammar(
            row.cells.get("Deep Triggers", ""), ("none",)
        ):
            errors.append(
                f"{report_path}: {row_label} {depth} Deep Triggers must use 'none: <specific reason>'"
            )

        provenance = row.cells.get("Generator / Input / Provenance", "")
        has_provenance = has_test_review_grammar(provenance, ("generator", "inputs", "provenance"))
        if surface == "generators/snapshots":
            if not has_provenance:
                errors.append(
                    f"{report_path}: {row_label} Generator / Input / Provenance must use "
                    "'generator: <specific>; inputs: <specific>; provenance: <specific>'"
                )
        elif not (has_provenance or has_test_review_grammar(provenance, ("not-applicable",))):
            errors.append(
                f"{report_path}: {row_label} Generator / Input / Provenance must use the structured "
                "generator/inputs/provenance triple or 'not-applicable: <specific reason>'"
            )

        errors.extend(
            validate_matrix_evidence_refs(
                report_path,
                root,
                evidence_root,
                proof_commands,
                row_label,
                "mixed",
                row.cells.get("Evidence Refs", ""),
            )
        )
    return errors


def normalize_test_review_value(value: str) -> str:
    return normalize_text(value).strip("`").lower()


def parse_test_review_components(value: str, keys: tuple[str, ...]) -> tuple[str, ...] | None:
    text = normalize_text(value).strip("`")
    segments = [text] if len(keys) == 1 else text.split(";")
    if len(segments) != len(keys):
        return None
    values: list[str] = []
    for segment, expected_key in zip(segments, keys):
        key, separator, payload = segment.partition(":")
        if not separator or normalize_text(key).lower() != expected_key:
            return None
        values.append(payload.strip())
    return tuple(values)


def has_test_review_grammar(value: str, keys: tuple[str, ...]) -> bool:
    components = parse_test_review_components(value, keys)
    return components is not None and all(is_specific_test_review_payload(item) for item in components)


def is_specific_test_review_payload(value: str) -> bool:
    normalized = normalize_text(value).strip("`").strip()
    placeholder = normalize_report_binding_placeholder_value(normalized)
    return (
        any(character.isalnum() for character in normalized)
        and placeholder not in REPORT_BINDING_PLACEHOLDER_VALUES | {"not applicable"}
        and not (normalized.startswith("<") and normalized.endswith(">"))
    )


def is_canonical_no_applicable_test_surface_row(row: ProofRow) -> bool:
    exact_none_fields = ("Surface", "Changed Population", "Selected Exemplars")
    rationale_fields = (
        "Baseline Review",
        "Deep Triggers",
        "Sampling Rationale",
        "Generator / Input / Provenance",
    )
    return (
        all(normalize_test_review_value(row.cells.get(field, "")) == "none" for field in exact_none_fields)
        and normalize_test_review_value(row.cells.get("Review Depth", "")) == NO_APPLICABLE_TEST_SURFACE_DEPTH
        and all(has_test_review_grammar(row.cells.get(field, ""), ("not-applicable",)) for field in rationale_fields)
    )


def validate_matrix_evidence_refs(
    report_path: Path,
    root: Path,
    evidence_root: Path,
    proof_commands: str,
    row_label: str,
    evidence_type: str,
    refs_text: str,
) -> list[str]:
    errors: list[str] = []
    refs = split_evidence_refs(refs_text)
    if not refs:
        return [f"{report_path}: {row_label} Evidence Refs must use typed evidence anchors"]
    for ref in refs:
        ref_type, _separator, payload = ref.partition(":")
        ref_type = ref_type.strip().lower()
        if ref_type not in MATRIX_EVIDENCE_TYPES - {"mixed"}:
            errors.append(f"{report_path}: {row_label} Evidence Refs anchor {ref!r} has unsupported evidence type")
            continue
        if evidence_type in MATRIX_EVIDENCE_TYPES - {"mixed"} and ref_type != evidence_type:
            errors.append(f"{report_path}: {row_label} Evidence Type {evidence_type!r} does not match {ref_type!r} anchor")
        if is_report_section_placeholder_body(payload):
            errors.append(f"{report_path}: {row_label} Evidence Refs anchor {ref!r} must be non-placeholder")
            continue
        if ref_type in {"code", "test", "static"}:
            errors.extend(validate_path_evidence_ref(report_path, evidence_root, row_label, ref_type, payload))
        elif ref_type == "command":
            errors.extend(validate_command_evidence_ref(report_path, root, proof_commands, row_label, payload))
        elif ref_type == "manual":
            errors.extend(validate_manual_evidence_ref(report_path, row_label, payload))
    return errors


def split_evidence_refs(value: str) -> list[str]:
    cleaned = value.replace("`", "").strip()
    matches = list(EVIDENCE_REF_PREFIX_RE.finditer(cleaned))
    refs: list[str] = []
    for index, match in enumerate(matches):
        start = match.start()
        if cleaned[start] == ";":
            start += 1
        end = matches[index + 1].start() if index + 1 < len(matches) else len(cleaned)
        ref = cleaned[start:end].strip().rstrip(";").strip()
        if ref:
            refs.append(ref)
    return refs


def validate_path_evidence_ref(report_path: Path, root: Path, row_label: str, ref_type: str, payload: str) -> list[str]:
    errors: list[str] = []
    path_value = payload
    anchor = ""
    if ref_type == "test" and "::" in payload:
        path_value, anchor = payload.split("::", 1)
    elif "#" in payload:
        path_value, anchor = payload.split("#", 1)
    if not path_value or is_report_section_placeholder_body(path_value):
        return [f"{report_path}: {row_label} {ref_type} evidence path must be non-placeholder"]
    if ref_type in {"code", "test", "static"} and not anchor:
        errors.append(f"{report_path}: {row_label} {ref_type} evidence ref must include a concrete anchor")
    elif is_report_section_placeholder_body(anchor):
        errors.append(f"{report_path}: {row_label} {ref_type} evidence anchor must be non-placeholder")
    try:
        resolve_safe_path(
            root,
            path_value,
            f"{report_path}: {row_label} {ref_type} evidence path",
            must_exist_file=True,
            root_label="code root",
        )
    except SliceproofError as exc:
        errors.extend(exc.errors)
    return errors


def validate_command_evidence_ref(
    report_path: Path,
    root: Path,
    proof_commands: str,
    row_label: str,
    payload: str,
) -> list[str]:
    if payload.startswith("proof#Commands Run:"):
        label = payload.removeprefix("proof#Commands Run:").strip()
        if is_report_section_placeholder_body(label):
            return [f"{report_path}: {row_label} command proof label must be non-placeholder"]
        normalized_label = normalize_command_ref_text(label)
        normalized_commands = normalize_command_ref_text(proof_commands)
        if normalized_label not in normalized_commands:
            return [f"{report_path}: {row_label} command proof label {label!r} was not found in proof ## Commands Run"]
        return []
    if payload.startswith("verification-output:"):
        target = payload.removeprefix("verification-output:").strip()
        if "#" not in target:
            return [f"{report_path}: {row_label} verification-output command ref must include #<label>"]
        path_value, label = target.split("#", 1)
        errors: list[str] = []
        if is_report_section_placeholder_body(label):
            errors.append(f"{report_path}: {row_label} verification-output label must be non-placeholder")
        evidence_path: Path | None = None
        try:
            evidence_path = resolve_safe_path(
                root,
                path_value,
                f"{report_path}: {row_label} verification-output evidence path",
                must_exist_file=True,
                root_label="artifact root",
            )
        except SliceproofError as exc:
            errors.extend(exc.errors)
        if evidence_path is not None and not is_report_section_placeholder_body(label):
            try:
                evidence_text = read_text_file(evidence_path, f"{report_path}: {row_label} verification-output evidence file")
            except SliceproofError as exc:
                errors.extend(exc.errors)
            else:
                if not verification_output_contains_label(evidence_text, label):
                    errors.append(
                        f"{report_path}: {row_label} verification-output label {label!r} "
                        f"was not found in evidence file {path_value}"
                    )
        return errors
    return [f"{report_path}: {row_label} command evidence must reference proof#Commands Run or verification-output"]


def verification_output_contains_label(content: str, label: str) -> bool:
    normalized_label = normalize_command_ref_text(label)
    label_slug = markdown_anchor_slug(label)
    if not normalized_label and not label_slug:
        return False
    for raw_line in content.splitlines():
        normalized_line = normalize_command_ref_text(raw_line)
        if normalized_label and normalized_label in normalized_line:
            return True
        if label_slug and label_slug in markdown_anchor_slugs(raw_line):
            return True
    return False


def markdown_anchor_slugs(line: str) -> set[str]:
    anchors: set[str] = set()
    stripped = line.strip()
    heading = re.match(r"^#{1,6}\s+(.+?)\s*$", stripped)
    if heading:
        heading_text = re.sub(r"\s+\{#[^}]+\}\s*$", "", heading.group(1)).strip()
        slug = markdown_anchor_slug(heading_text)
        if slug:
            anchors.add(slug)
    for custom_anchor in re.findall(r"\{#([A-Za-z0-9][A-Za-z0-9_.:-]*)\}", stripped):
        anchors.add(custom_anchor.lower())
    for html_anchor in re.findall(r"<a\s+[^>]*(?:id|name)=[\"']([^\"']+)[\"']", stripped, flags=re.IGNORECASE):
        anchors.add(html_anchor.lower())
    return anchors


def markdown_anchor_slug(value: str) -> str:
    normalized = normalize_command_ref_text(value)
    return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")


def validate_manual_evidence_ref(report_path: Path, row_label: str, payload: str) -> list[str]:
    fields: dict[str, str] = {}
    for part in payload.split(";"):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        fields[key.strip().lower()] = value.strip()
    errors: list[str] = []
    for field in ("scenario", "observed"):
        value = fields.get(field, "")
        if is_report_section_placeholder_body(value):
            errors.append(f"{report_path}: {row_label} manual evidence must include non-placeholder {field}=...")
    return errors


def validate_interface_matrix_row(report_path: Path, row_label: str, disposition: str) -> list[str]:
    text = normalize_text(disposition).lower()
    errors: list[str] = []
    if not has_exact_interface_disposition(text):
        errors.append(f"{report_path}: {row_label} interface row must record exact interface fulfillment")
    dirty_exactness = {
        "ambiguous",
        "partial",
        "contradicted",
        "over-broad",
        "over broad",
        "missing",
        "unverified",
        "inexact",
        "not exact",
        "not-exact",
        "non-exact",
        "non exact",
    }
    if any(token in text for token in dirty_exactness):
        errors.append(f"{report_path}: {row_label} interface row contains non-exact interface disposition")
    if has_negated_forbidden_falsification(text):
        errors.append(f"{report_path}: {row_label} interface row must not negate forbidden-behavior falsification")
    if not has_affirmative_forbidden_falsification(text):
        errors.append(
            f"{report_path}: {row_label} interface row must record forbidden-behavior falsification with affirmative wording"
        )
    return errors


def has_exact_interface_disposition(text: str) -> bool:
    negated_exactness = re.compile(r"\b(?:inexact|not[-\s]+exact|non[-\s]+exact)\b")
    for clause in split_matrix_disposition_clauses(text):
        if "interface" not in clause:
            continue
        if negated_exactness.search(clause):
            continue
        if re.search(r"\bexact\b", clause):
            return True
    return False


def has_negated_forbidden_falsification(text: str) -> bool:
    return any(
        AFFIRMATIVE_FORBIDDEN_FALSIFICATION_RE.search(clause) and NEGATED_FORBIDDEN_FALSIFICATION_RE.search(clause)
        for clause in split_matrix_disposition_clauses(text)
    )


def has_affirmative_forbidden_falsification(text: str) -> bool:
    return any(
        AFFIRMATIVE_FORBIDDEN_FALSIFICATION_RE.search(clause) and not NEGATED_FORBIDDEN_FALSIFICATION_RE.search(clause)
        for clause in split_matrix_disposition_clauses(text)
    )


def validate_triggered_risk_matrix_row(report_path: Path, row_label: str, disposition: str) -> list[str]:
    text = normalize_text(disposition).lower()
    rationale_match = TRIGGERED_RISK_RATIONALE_RE.search(text)
    rationale_ok = bool(rationale_match and is_concrete_risk_phrase(rationale_match.group("rationale")))
    result_ok = has_triggered_risk_result_clause(text)
    if not rationale_ok or not result_ok:
        return [
            f"{report_path}: {row_label} triggered-risk row must record rationale/disposition as "
            "'triggered because ...; disposition/result ...'"
        ]
    return []


def has_triggered_risk_result_clause(text: str) -> bool:
    clauses = split_matrix_disposition_clauses(text)
    for index, clause in enumerate(clauses):
        if TRIGGERED_RISK_RATIONALE_RE.search(clause):
            return any(is_concrete_risk_phrase(candidate) for candidate in clauses[index + 1 :])
    return False


def is_concrete_risk_phrase(value: str) -> bool:
    if is_report_section_placeholder_body(value):
        return False
    tokens = re.findall(r"[a-z0-9][a-z0-9_-]*", value.lower())
    meaningful_tokens = [token for token in tokens if token not in TRIGGERED_RISK_GENERIC_TOKENS]
    return len(meaningful_tokens) >= 2


def split_matrix_disposition_clauses(value: str) -> list[str]:
    clauses: list[str] = []
    for part in re.split(r"[;|\n]+", value):
        clause = normalize_text(part).lower().strip(" :-")
        if clause:
            clauses.append(clause)
    return clauses


def interface_bearing_slice_ids(root: Path, package_md: PackageMarkdown) -> set[str]:
    interface_ids: set[str] = set()
    for ref in package_md.slice_refs:
        try:
            slice_path = resolve_safe_path(root, ref.path, f"assigned Slice {ref.path!r}", expected_suffix=".md", must_exist_file=True)
        except SliceproofError:
            continue
        blocks = extract_slice_h3_blocks(slice_path)
        for slice_id in ref.must_satisfy:
            if re.search(r"\bInterface contract\b", blocks.get(slice_id, ""), flags=re.IGNORECASE):
                interface_ids.add(slice_id)
    return interface_ids


def extract_slice_h3_blocks(path: Path) -> dict[str, str]:
    blocks: dict[str, list[str]] = {}
    current_id: str | None = None
    in_fence = False
    in_shared_understanding = False
    for raw_line in read_text_file(path, f"Slice {path}").splitlines():
        line = raw_line.strip()
        if is_fence(line):
            in_fence = not in_fence
            if current_id is not None:
                blocks[current_id].append(raw_line)
            continue
        if not in_fence and raw_line.startswith("## ") and not raw_line.startswith("### "):
            in_shared_understanding = raw_line[3:].strip().lower() == "shared understanding"
            current_id = None
            continue
        if not in_shared_understanding:
            continue
        if not in_fence:
            match = H3_ID_RE.match(raw_line)
            if match:
                current_id = match.group(1)
                blocks.setdefault(current_id, [])
                continue
        if current_id is not None:
            blocks[current_id].append(raw_line)
    return {slice_id: "\n".join(lines).strip() for slice_id, lines in blocks.items()}


def validate_report_slice_closure_review(report_path: Path, package_md: PackageMarkdown, body: str) -> list[str]:
    errors: list[str] = []
    if is_report_section_placeholder_body(body):
        return [f"{report_path}: ### Slice Closure Review must contain non-placeholder review evidence"]
    if BLOCKING_MARKER_RE.search(body):
        errors.append(f"{report_path}: ### Slice Closure Review contains unresolved TODO/OPEN/GAP marker")
    rows = parse_table(body)
    if not rows:
        if package_md.must_satisfy_ids:
            errors.append(f"{report_path}: ### Slice Closure Review must include a table row for each required Slice ID")
        return errors

    required_columns = {"Slice ID", "Proof status", "Evidence sufficient?", "Notes"}
    if not required_columns.issubset(rows[0].cells):
        errors.append(f"{report_path}: ### Slice Closure Review missing columns {sorted(required_columns - set(rows[0].cells))}")
        return errors

    required_ids = set(package_md.must_satisfy_ids)
    rows_by_id: dict[str, ProofRow] = {}
    for index, row in enumerate(rows, start=1):
        slice_id = clean_cell_id(row.cells.get("Slice ID", ""))
        row_label = slice_id or f"Slice Closure Review row {index}"
        if not slice_id:
            errors.append(f"{report_path}: {row_label} Slice ID must be non-placeholder")
            continue
        if slice_id in rows_by_id:
            errors.append(f"{report_path}: duplicate Slice Closure Review row for {slice_id}")
        else:
            rows_by_id[slice_id] = row
        for field in sorted(required_columns):
            value = row.cells.get(field, "")
            if is_report_section_placeholder_body(value):
                errors.append(f"{report_path}: {row_label} {field} must be non-placeholder")
        if slice_id in required_ids:
            proof_status = normalize_status(row.cells.get("Proof status", ""))
            if proof_status != "PASS":
                errors.append(f"{report_path}: {slice_id} Proof status must be PASS")
            evidence_sufficient = normalize_text(row.cells.get("Evidence sufficient?", "")).strip("`").lower()
            if evidence_sufficient not in {"yes", "y", "true"}:
                errors.append(f"{report_path}: {slice_id} Evidence sufficient? must be yes")
    for slice_id in package_md.must_satisfy_ids:
        if slice_id not in rows_by_id:
            errors.append(f"{report_path}: ### Slice Closure Review missing required row for {slice_id}")
    return errors


def validate_report_code_review_findings(report_path: Path, body: str) -> list[str]:
    if is_report_section_placeholder_body(body):
        return [f"{report_path}: ### Code Review Findings must contain non-placeholder review evidence"]
    if BLOCKING_MARKER_RE.search(body):
        return [f"{report_path}: ### Code Review Findings contains unresolved TODO/OPEN/GAP marker"]
    return []



def validate_semgrep_evidence_binding(
    report_path: Path,
    root: Path,
    feature: str,
    package: RegistryPackage,
    body: str,
) -> list[str]:
    errors: list[str] = []
    binding = parse_key_values(body)
    status = normalize_text(clean_cell_id(binding.get("Status", ""))).lower()
    if not status:
        return [f"{report_path}: ## Semgrep Evidence missing 'Status'"]
    if status not in SEMGREP_ENABLED_STATUSES | SEMGREP_DISABLED_STATUSES:
        errors.append(f"{report_path}: ## Semgrep Evidence Status must be enabled, contracted, disabled, or not-contracted")

    evidence_fields_present = any(
        field in binding and not is_report_binding_placeholder_text(clean_cell_id(binding[field]))
        for field in SEMGREP_EVIDENCE_FIELDS
        if field != "Status"
    )
    if status not in SEMGREP_ENABLED_STATUSES and evidence_fields_present:
        errors.append(f"{report_path}: ## Semgrep Evidence raw/summary fields require Status enabled or contracted")
    if status not in SEMGREP_ENABLED_STATUSES:
        return errors

    for field in sorted(SEMGREP_EVIDENCE_FIELDS - set(binding)):
        errors.append(f"{report_path}: ## Semgrep Evidence missing {field!r}")
    if errors:
        return errors

    for field in sorted(SEMGREP_EVIDENCE_FIELDS):
        value = clean_cell_id(binding[field])
        if is_report_binding_placeholder_text(value):
            errors.append(f"{report_path}: Semgrep Evidence {field} must be non-placeholder")
    if errors:
        return errors

    try:
        raw_path = resolve_semgrep_evidence_path(
            root,
            feature,
            normalize_path_value(binding["Raw Path"]),
            f"{report_path}: Semgrep Evidence Raw Path",
            expected_suffix=".semgrep.json",
        )
        summary_path = resolve_semgrep_evidence_path(
            root,
            feature,
            normalize_path_value(binding["Summary Path"]),
            f"{report_path}: Semgrep Evidence Summary Path",
            expected_suffix=".semgrep-summary.json",
        )
    except SliceproofError as exc:
        return [*errors, *exc.errors]

    raw_value = normalize_path_value(binding["Raw Path"])
    summary_value = normalize_path_value(binding["Summary Path"])
    raw_stem = Path(raw_value).name[: -len(".semgrep.json")]
    summary_stem = Path(summary_value).name[: -len(".semgrep-summary.json")]
    if raw_stem != package.package_id:
        errors.append(f"{report_path}: Semgrep Evidence Raw Path must use package stem {package.package_id}.semgrep.json")
    if summary_stem != package.package_id:
        errors.append(f"{report_path}: Semgrep Evidence Summary Path must use package stem {package.package_id}.semgrep-summary.json")
    if raw_stem != summary_stem:
        errors.append(f"{report_path}: Semgrep Evidence raw and summary paths must have paired stems")

    raw_digest = file_digest_hex(raw_path)
    expected_raw_digest = normalize_semgrep_digest(binding["Raw Digest"], f"{report_path}: Semgrep Evidence Raw Digest", errors)
    if expected_raw_digest and expected_raw_digest != raw_digest:
        errors.append(f"{report_path}: Semgrep Evidence Raw Digest does not match current raw output")

    summary_data = load_semgrep_summary_json(summary_path, report_path, errors)
    if isinstance(summary_data, dict):
        summary_raw_digest = normalize_semgrep_digest(str(summary_data.get("raw_digest", "")), f"{report_path}: Semgrep summary raw_digest", errors)
        if summary_raw_digest and summary_raw_digest != raw_digest:
            errors.append(f"{report_path}: Semgrep summary raw_digest does not match current raw output")
        actual_summary_digest = normalize_semgrep_digest(str(summary_data.get("summary_digest", "")), f"{report_path}: Semgrep summary summary_digest", errors)
        computed_summary_digest = digest_semgrep_summary(summary_data)
        if actual_summary_digest and actual_summary_digest != computed_summary_digest:
            errors.append(f"{report_path}: Semgrep summary_digest does not match summary content")
        expected_summary_digest = normalize_semgrep_digest(binding["Summary Digest"], f"{report_path}: Semgrep Evidence Summary Digest", errors)
        if expected_summary_digest and expected_summary_digest != computed_summary_digest:
            errors.append(f"{report_path}: Semgrep Evidence Summary Digest does not match current summary output")
    return errors


def resolve_semgrep_evidence_path(root: Path, feature: str, value: str, label: str, *, expected_suffix: str) -> Path:
    path = repo_relative_path(value, label, expected_suffix=expected_suffix)
    parts = path.parts
    if len(parts) != 4 or parts[0] != ".tasks" or parts[1] != feature or parts[2] != "semgrep":
        raise SliceproofError([f"{label}: path must be under .tasks/{feature}/semgrep/"])
    current = root
    for part in parts:
        current = current / part
        try:
            if current.is_symlink():
                raise SliceproofError([f"{label}: path must not contain symlinks: {value}"])
        except OSError as exc:
            raise SliceproofError([f"{label}: unable to inspect path {value}: {exc}"])
    resolved = (root / path).resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError:
        raise SliceproofError([f"{label}: path escapes artifact root"])
    semgrep_root = (root / ".tasks" / feature / "semgrep").resolve(strict=False)
    try:
        resolved.relative_to(semgrep_root)
    except ValueError:
        raise SliceproofError([f"{label}: path must resolve under .tasks/{feature}/semgrep/"])
    if not resolved.is_file():
        raise SliceproofError([f"{label}: file not found: {value}"])
    return resolved


def normalize_semgrep_digest(value: str, label: str, errors: list[str]) -> str:
    cleaned = clean_cell_id(value).strip()
    match = SEMGREP_DIGEST_RE.fullmatch(cleaned)
    if not match:
        errors.append(f"{label}: expected 64 hex digest or sha256:<digest>")
        return ""
    return match.group(1).lower()


def file_digest_hex(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_semgrep_summary_json(path: Path, report_path: Path, errors: list[str]) -> Any:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{report_path}: Semgrep summary JSON is invalid at line {exc.lineno} column {exc.colno}: {exc.msg}")
        return None
    except (OSError, UnicodeError) as exc:
        errors.append(f"{report_path}: unable to read Semgrep summary JSON: {exc}")
        return None
    if not isinstance(data, dict):
        errors.append(f"{report_path}: Semgrep summary JSON must be a mapping")
    return data


def digest_semgrep_summary(summary: dict[str, Any]) -> str:
    clone = dict(summary)
    clone.pop("summary_digest", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def validate_report_state_binding(
    report_path: Path,
    root: Path,
    package: RegistryPackage,
    package_md: PackageMarkdown,
    proof_path: Path,
    body: str,
) -> ReportValidationResult:
    errors: list[str] = []
    advisories: list[dict[str, Any]] = []
    binding = parse_key_values(body)
    for field in sorted(REQUIRED_STATE_BINDING_FIELDS - set(binding)):
        errors.append(f"{report_path}: ## State Binding missing {field!r}")
    if errors:
        return ReportValidationResult(errors, advisories)

    expected_values = state_binding_values(
        root,
        package,
        package_md,
        proof_path,
        worktree=clean_cell_id(binding["Worktree"]),
        git_ref=clean_cell_id(binding["Git Ref"]),
        commit=clean_cell_id(binding["Commit"]),
        verified_at=clean_cell_id(binding["Verified At"]),
    )
    for field in STATE_BINDING_FIELD_ORDER:
        value = clean_cell_id(binding[field])
        if field in {"Assigned Slices", "Assigned Slice Digests"} and expected_values[field] == "none" and value == "none":
            continue
        if is_report_binding_placeholder_text(value):
            errors.append(f"{report_path}: State Binding {field} must be non-placeholder")

    if clean_cell_id(binding["Package"]) != expected_values["Package"]:
        errors.append(f"{report_path}: State Binding Package must be {package.package_id}")
    if normalize_path_value(binding["Package Markdown"]) != expected_values["Package Markdown"]:
        errors.append(f"{report_path}: State Binding Package Markdown must be {package.path}")
    if clean_cell_id(binding["Package Markdown Digest"]) != expected_values["Package Markdown Digest"]:
        errors.append(f"{report_path}: State Binding Package Markdown Digest does not match current package Markdown content")
    if normalize_path_value(binding["Proof"]) != expected_values["Proof"]:
        errors.append(f"{report_path}: State Binding Proof must be {package.proof_path}")
    if clean_cell_id(binding["Proof Digest"]) != expected_values["Proof Digest"]:
        errors.append(f"{report_path}: State Binding Proof Digest does not match current proof content")
    if clean_cell_id(binding["Assigned Slices"]) != expected_values["Assigned Slices"]:
        errors.append(f"{report_path}: State Binding Assigned Slices must be {expected_values['Assigned Slices']}")

    digest_result = validate_assigned_slice_digest_binding(
        report_path,
        package.package_id,
        clean_cell_id(binding["Assigned Slice Digests"]),
        root,
        package_md,
    )
    errors.extend(digest_result.errors)
    advisories.extend(digest_result.advisories)

    if clean_cell_id(binding["Matrix Source Snapshot"]) != expected_values["Matrix Source Snapshot"]:
        errors.append(f"{report_path}: State Binding Matrix Source Snapshot does not match current package/Slice source content")
    worktree = clean_cell_id(binding["Worktree"])
    if not Path(worktree).is_absolute():
        errors.append(f"{report_path}: State Binding Worktree must be an absolute reviewed worktree path")
    commit = clean_cell_id(binding["Commit"])
    if not COMMIT_RE.fullmatch(commit):
        errors.append(f"{report_path}: State Binding Commit must look like a git commit")
    if not is_iso8601(clean_cell_id(binding["Verified At"])):
        errors.append(f"{report_path}: State Binding Verified At must be ISO-8601")
    return ReportValidationResult(errors, advisories)


def state_binding_values(
    root: Path,
    package: RegistryPackage,
    package_md: PackageMarkdown,
    proof_path: Path,
    *,
    worktree: str,
    git_ref: str,
    commit: str,
    verified_at: str,
) -> dict[str, str]:
    package_path = resolve_safe_path(root, package.path, f"work_packages[{package.package_id}].path", expected_suffix=".md", must_exist_file=True)
    package_text = read_text_file(package_path, f"package Markdown {package_path}")
    proof_text = read_text_file(proof_path, f"proof {proof_path}")
    return {
        "Package": package.package_id,
        "Package Markdown": package.path,
        "Package Markdown Digest": digest_text(package_text),
        "Proof": package.proof_path,
        "Proof Digest": digest_text(proof_text),
        "Assigned Slices": assigned_slices_binding(package_md),
        "Assigned Slice Digests": assigned_slice_digests_binding(root, package_md),
        "Matrix Source Snapshot": matrix_source_snapshot_binding(root, package, package_md),
        "Worktree": worktree,
        "Git Ref": git_ref,
        "Commit": commit,
        "Verified At": verified_at,
    }


def render_state_binding_block(values: dict[str, str]) -> str:
    lines = [
        "## State Binding",
        "Helper/package-lifecycle metadata; the source report body above remains canonical.",
    ]
    for field in STATE_BINDING_FIELD_ORDER:
        lines.append(f"- {field}: `{values[field]}`")
    return "\n".join(lines) + "\n"


def validate_state_binding_runtime_metadata(
    command: str,
    worktree: str,
    git_ref: str,
    commit: str,
    verified_at: str,
) -> list[str]:
    errors: list[str] = []
    if not Path(worktree).is_absolute():
        errors.append(f"{command}: --worktree must be an absolute reviewed worktree path")
    if is_report_binding_placeholder_text(git_ref):
        errors.append(f"{command}: --git-ref must be non-placeholder")
    if not COMMIT_RE.fullmatch(commit):
        errors.append(f"{command}: --commit must look like a git commit")
    if not is_iso8601(verified_at):
        errors.append(f"{command}: --verified-at must be ISO-8601")
    return errors


def is_report_section_placeholder_body(body: str) -> bool:
    return not body.strip() or is_placeholder_text(body)


def state_binding_assigned_slice_path_error(path_value: str, label: str) -> str | None:
    if any(delimiter in path_value for delimiter in STATE_BINDING_ASSIGNED_SLICE_PATH_DELIMITERS):
        return (
            f"{label}: State Binding Assigned Slice path must not contain '|', '=', or '; ' because "
            "Assigned Slice Digests uses path|tier|H3-ID=sha256:<64-hex> entries separated by '; '"
        )
    return None


def enforce_state_binding_assigned_slice_paths(package_md: PackageMarkdown) -> None:
    errors = [
        error
        for ref in package_md.slice_refs
        if (error := state_binding_assigned_slice_path_error(ref.path, f"assigned Slice {ref.path!r}"))
    ]
    if errors:
        raise SliceproofError(errors)


def assigned_slices_binding(package_md: PackageMarkdown) -> str:
    if not package_md.slice_refs:
        return "none"
    enforce_state_binding_assigned_slice_paths(package_md)
    return ", ".join(sorted(ref.path for ref in package_md.slice_refs))


def assigned_slice_digests_binding(root: Path, package_md: PackageMarkdown) -> str:
    return format_assigned_slice_digest_entries(assigned_slice_digest_entries(root, package_md))


def format_assigned_slice_digest_entries(entries: list[SliceDigestEntry]) -> str:
    if not entries:
        return "none"
    return "; ".join(f"{entry.path}|{entry.tier}|{entry.h3_id}={entry.digest}" for entry in entries)


def assigned_slice_digest_entries(
    root: Path,
    package_md: PackageMarkdown,
    *,
    tiers: tuple[str, ...] = SLICE_DIGEST_TIERS,
) -> list[SliceDigestEntry]:
    enforce_state_binding_assigned_slice_paths(package_md)
    assignments = assigned_slice_h3_assignments(package_md)
    if not assignments:
        return []
    entries: list[SliceDigestEntry] = []
    errors: list[str] = []
    for path_value in sorted(assignments):
        slice_path = resolve_safe_path(root, path_value, f"assigned Slice {path_value!r}", expected_suffix=".md", must_exist_file=True)
        blocks = extract_slice_h3_blocks(slice_path)
        for tier in tiers:
            for h3_id in sorted(assignments[path_value][tier]):
                block = blocks.get(h3_id)
                if block is None:
                    errors.append(f"assigned H3 '{h3_id}' not found in Slice '{path_value}'")
                    continue
                entries.append(SliceDigestEntry(path_value, tier, h3_id, digest_text(block)))
    if errors:
        raise SliceproofError(errors)
    return entries


def assigned_slice_h3_assignments(package_md: PackageMarkdown) -> dict[str, dict[str, set[str]]]:
    assignments: dict[str, dict[str, set[str]]] = {}
    for ref in package_md.slice_refs:
        path_assignments = assignments.setdefault(ref.path, {tier: set() for tier in SLICE_DIGEST_TIERS})
        path_assignments["must_satisfy"].update(ref.must_satisfy)
        path_assignments["context_only"].update(ref.context_only)
    return assignments


def validate_assigned_slice_digest_binding(
    report_path: Path,
    package_id: str,
    actual_value: str,
    root: Path,
    package_md: PackageMarkdown,
) -> ReportValidationResult:
    expected_entries = assigned_slice_digest_entries(root, package_md)
    if not expected_entries:
        if actual_value == "none":
            return ReportValidationResult([], [])
        return ReportValidationResult([f"{report_path}: State Binding Assigned Slice Digests must be none"], [])

    expected_by_key = {(entry.path, entry.tier, entry.h3_id): entry.digest for entry in expected_entries}
    expected_keys = set(expected_by_key)
    parsed_entries, structural_errors = parse_assigned_slice_digest_entries(report_path, actual_value, package_md)
    if structural_errors:
        return ReportValidationResult(structural_errors, [])

    actual_keys = [(entry.path, entry.tier, entry.h3_id) for entry in parsed_entries]
    missing = sorted(expected_keys - set(actual_keys), key=slice_digest_key_sort)
    extra = sorted(set(actual_keys) - expected_keys, key=slice_digest_key_sort)
    for path_value, tier, h3_id in missing:
        structural_errors.append(f"{report_path}: State Binding Assigned Slice Digests missing entry for {path_value}|{tier}|{h3_id}")
    for path_value, tier, h3_id in extra:
        structural_errors.append(f"{report_path}: State Binding Assigned Slice Digests extra entry for {path_value}|{tier}|{h3_id}")
    if actual_keys != sorted(actual_keys, key=slice_digest_key_sort):
        structural_errors.append(f"{report_path}: State Binding Assigned Slice Digests entries must be sorted by Slice path, tier, and H3 ID")
    if structural_errors:
        return ReportValidationResult(structural_errors, [])

    errors: list[str] = []
    drifted_context: dict[str, list[str]] = {}
    for entry in parsed_entries:
        expected_digest = expected_by_key[(entry.path, entry.tier, entry.h3_id)]
        if entry.digest == expected_digest:
            continue
        if entry.tier == "must_satisfy":
            errors.append(
                f"{report_path}: State Binding must_satisfy Slice section drift for {entry.h3_id} in {entry.path}"
            )
        else:
            drifted_context.setdefault(entry.path, []).append(entry.h3_id)
    advisories = [
        context_only_slice_drift_advisory(package_id, path_value, sorted(h3_ids))
        for path_value, h3_ids in sorted(drifted_context.items())
    ]
    return ReportValidationResult(errors, advisories)


def parse_assigned_slice_digest_entries(
    report_path: Path,
    value: str,
    package_md: PackageMarkdown,
) -> tuple[list[SliceDigestEntry], list[str]]:
    assignments = assigned_slice_h3_assignments(package_md)
    assigned_paths = set(assignments)
    h3_tier_by_path: dict[str, dict[str, str]] = {}
    for path_value, tiers in assignments.items():
        h3_tier_by_path[path_value] = {}
        for tier in SLICE_DIGEST_TIERS:
            for h3_id in tiers[tier]:
                h3_tier_by_path[path_value][h3_id] = tier

    entries: list[SliceDigestEntry] = []
    errors: list[str] = []
    seen: set[tuple[str, str, str]] = set()
    if value == "none":
        return entries, [f"{report_path}: State Binding Assigned Slice Digests missing section-scoped entries"]
    for raw_entry in value.split("; "):
        if not raw_entry:
            errors.append(f"{report_path}: State Binding Assigned Slice Digests contains an empty entry")
            continue
        if "=" not in raw_entry:
            errors.append(f"{report_path}: State Binding Assigned Slice Digests malformed entry {raw_entry!r}")
            continue
        left, digest = raw_entry.split("=", 1)
        parts = left.split("|")
        if len(parts) != 3 or not all(parts):
            errors.append(f"{report_path}: State Binding Assigned Slice Digests malformed entry {raw_entry!r}")
            continue
        path_value, tier, h3_id = parts
        digest_valid = bool(re.fullmatch(r"sha256:[0-9a-f]{64}", digest))
        if not digest_valid:
            errors.append(f"{report_path}: State Binding Assigned Slice Digests invalid digest for {path_value}|{tier}|{h3_id}")
        if path_value not in assigned_paths:
            errors.append(f"{report_path}: State Binding Assigned Slice Digests unknown path {path_value!r}")
        if tier not in SLICE_DIGEST_TIERS:
            errors.append(f"{report_path}: State Binding Assigned Slice Digests invalid tier {tier!r} for {path_value}|{h3_id}")
        elif path_value in assigned_paths:
            expected_tier = h3_tier_by_path[path_value].get(h3_id)
            if expected_tier is None:
                errors.append(f"{report_path}: State Binding Assigned Slice Digests unknown H3 {h3_id!r} for {path_value}")
            elif expected_tier != tier:
                errors.append(
                    f"{report_path}: State Binding Assigned Slice Digests encoded tier mismatch for {path_value}|{h3_id}: "
                    f"binding uses {tier}, package Markdown assigns {expected_tier}"
                )
        key = (path_value, tier, h3_id)
        if key in seen:
            errors.append(f"{report_path}: State Binding Assigned Slice Digests duplicate entry for {path_value}|{tier}|{h3_id}")
        seen.add(key)
        if digest_valid:
            entries.append(SliceDigestEntry(path_value, tier, h3_id, digest))
    return entries, errors


def slice_digest_key_sort(key: tuple[str, str, str]) -> tuple[str, int, str]:
    path_value, tier, h3_id = key
    return (path_value, SLICE_DIGEST_TIER_ORDER.get(tier, len(SLICE_DIGEST_TIER_ORDER)), h3_id)


def context_only_slice_drift_advisory(package_id: str, path_value: str, h3_ids: list[str]) -> dict[str, Any]:
    joined_ids = ", ".join(h3_ids)
    return {
        "type": SLICE_DIGEST_ADVISORY_TYPE,
        "severity": "advisory",
        "package": package_id,
        "slice_path": path_value,
        "tier": "context_only",
        "h3_ids": h3_ids,
        "message": f"context_only Slice section drift detected for {joined_ids} in {path_value}; review whether package evidence still applies.",
    }


def matrix_source_snapshot_binding(root: Path, package: RegistryPackage, package_md: PackageMarkdown) -> str:
    package_path = resolve_safe_path(root, package.path, f"work_packages[{package.package_id}].path", expected_suffix=".md", must_exist_file=True)
    parts = [snapshot_part(package.path, read_text_file(package_path, f"package Markdown {package_path}"))]
    for entry in assigned_slice_digest_entries(root, package_md, tiers=("must_satisfy",)):
        slice_path = resolve_safe_path(root, entry.path, f"assigned Slice {entry.path!r}", expected_suffix=".md", must_exist_file=True)
        blocks = extract_slice_h3_blocks(slice_path)
        block = blocks.get(entry.h3_id)
        if block is None:
            raise SliceproofError([f"assigned H3 '{entry.h3_id}' not found in Slice '{entry.path}'"])
        parts.append(snapshot_part(f"{entry.path}|{entry.tier}|{entry.h3_id}", block))
    return digest_text("".join(parts))


def snapshot_part(path_value: str, content: str) -> str:
    return f"{path_value}\0{content}\0"


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


def normalize_command_ref_text(value: str) -> str:
    return normalize_text(value).replace("`", "").lower()


def is_placeholder_text(value: str) -> bool:
    stripped = normalize_text(value).lower().strip("-* \t")
    if stripped in PLACEHOLDER_VALUES:
        return True
    return bool(BLOCKING_MARKER_RE.fullmatch(stripped))


def is_report_binding_placeholder_text(value: str) -> bool:
    normalized = normalize_report_binding_placeholder_value(value)
    return normalized in REPORT_BINDING_PLACEHOLDER_VALUES


def normalize_report_binding_placeholder_value(value: str) -> str:
    normalized = normalize_text(value).lower()
    return re.sub(r"[^a-z0-9]+", " ", normalized).strip()


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
    normalized = normalize_approval_placeholder_value(value)
    return not normalized or APPROVAL_PLACEHOLDER_TOKEN_RE.search(normalized) is not None


def normalize_approval_placeholder_value(value: str) -> str:
    normalized = normalize_text(value).strip(" -*`'\".:?!").lower()
    return re.sub(r"[\s_-]+", " ", normalized)


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
