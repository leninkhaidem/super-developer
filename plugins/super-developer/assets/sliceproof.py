#!/usr/bin/env python3
"""Mechanical helper for Slice-first planned-feature artifacts.

The helper performs deterministic structure, path-safety, proof-closure,
report-binding, lifecycle/predecessor, and freeze-receipt completion checks.
It does not judge semantic quality, run tests, mutate lifecycle/package state, dispatch work,
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
EXACT_GIT_SHA_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
SAFE_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
SAFE_GIT_REF_RE = re.compile(r"^(?!/)(?!.*(?:\.\.|//|@\{|[\\ ~^:?*\[]))[A-Za-z0-9._/-]{1,256}(?<![/.])$")
ACTION_RE = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
COUNTER_RE = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
WAVE_ID_RE = re.compile(r"^wave-[a-z0-9][a-z0-9-]*$")
FREEZE_ID_RE = re.compile(r"^freeze-[a-z0-9][a-z0-9-]{0,63}$")
LENS_RE = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
SEMGREP_DIGEST_RE = re.compile(r"^(?:sha256:)?([0-9a-fA-F]{64})$")
STATUS_VALUES = {"pending", "in_progress", "done", "blocked"}
FEATURE_STATUS_VALUES = {"planned", "reviewed", "in_progress", "completed", "blocked", "on_hold"}
ASSURANCE_PROFILES = {"low", "standard", "high"}
ASSURANCE_PROFILE_RANK = {"low": 0, "standard": 1, "high": 2}
PACKAGE_VERIFICATION_MODES = {"boundary", "final"}
FINAL_REPORT_MARKER = "None — final assurance"
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
NEUTRAL_LIFECYCLE_STAGES = {"blocked", "needs-decision", "parked", "cancelled", "superseded"}
LIFECYCLE_STAGES = PREAUTH_LIFECYCLE_STAGES | AUTHORIZED_LIFECYCLE_STAGES | NEUTRAL_LIFECYCLE_STAGES
RESUMABLE_LIFECYCLE_STAGES = LIFECYCLE_STAGES - {"completed", "parked", "cancelled", "superseded"}
LIFECYCLE_DISPOSITIONS = {"active", "parked", "cancelled", "superseded", "completed"}
PARKED_NEXT_ACTIONS = ("resume", "cancel", "supersede")
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
ROUTING_CANDIDATE_STATES = {"in_progress", "stabilized", "verified", "done"}
WAVE_STATES = {"reserved", "active", "quiescent", "completed", "blocked"}
CLUSTER_CLASSES = {
    "requirement-gap",
    "architecture-invalidation",
    "implementation-defect",
    "integration-regression",
    "test-fidelity-gap",
    "evidence-stale-or-contradicted",
    "confidence-enhancement",
}
CLUSTER_CLASS_PRECEDENCE_RANK = {
    "requirement-gap": 0,
    "architecture-invalidation": 1,
    "implementation-defect": 2,
    "integration-regression": 2,
    "test-fidelity-gap": 3,
    "evidence-stale-or-contradicted": 3,
    "confidence-enhancement": 4,
}
CLUSTER_ROUTES = {
    "requirement-gap": "human-envelope",
    "architecture-invalidation": "technical-reassessment",
    "implementation-defect": "closure-repair",
    "integration-regression": "closure-repair",
    "test-fidelity-gap": "closure-repair",
    "evidence-stale-or-contradicted": "evidence-refresh",
    "confidence-enhancement": "report-only",
}
CLUSTER_DISPOSITIONS = {"repair-eligible", "closure-pending", "routed", "closed", "circuit-open"}
ASSURANCE_RECEIPT_ROLES = {"C", "R", "S", "U", "V"}
FIXED_RECEIPT_LENSES = {
    "C": "combined-low-assurance",
    "R": "integrated-code-risk",
    "U": "accepted-outcome-reconciliation",
    "V": "verification-summary",
}
ASSURANCE_ASSIGNMENT_OWNERS = {"package-verifier", "package-specialist", "C", "R", "S"}
ASSURANCE_ASSIGNMENT_SIDES = {"pre-freeze", "post-freeze"}
CONTROL_PLANE_OPERATIONS = {"safe-checkpoint", "last-verified"}
CONTROL_PLANE_REASONS = {"budget-exhausted", "ownership-unavailable", "cas-unavailable"}
PREAUTH_REQUIRED_COUNTERS = {"delegated_calls", "planner_correction_waves", "spike_waves", "command_units"}
FINAL_ASSURANCE_CALL_COUNTERS = {
    "C": "combined_low_calls",
    "R": "code_review_calls",
    "S": "final_specialist_calls",
    "U": "completion_audit_calls",
}
PROFILE_FINAL_EQUATION_ROLES = {
    "low": ("C",),
    "standard": ("R", "U"),
    "high": ("R", "S", "U"),
}
PROFILE_REQUIRED_FINAL_ROLES = {
    "low": ("C",),
    "standard": ("R", "U"),
    "high": ("R", "U"),
}
ROLE_SCOPED_CALL_COUNTERS = tuple(FINAL_ASSURANCE_CALL_COUNTERS.values())
IMPLEMENTATION_REQUIRED_COUNTERS = {
    "repair_waves",
    "delegated_calls",
    "combined_low_calls",
    "code_review_calls",
    "final_specialist_calls",
    "completion_audit_calls",
    "command_units",
    "cost_units",
}
REQUIRED_PACKAGE_SECTIONS = {
    "Scope",
    "Assigned Slices",
    "Primary Paths",
    "Verification Expectations",
    "Proof",
    "Independent Verification",
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
    "Selected Causal Evidence",
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
SELECTED_CAUSAL_EVIDENCE_COLUMNS = [
    "Evidence Anchor",
    "Evidence Type",
    "Behavior / Risk Proven",
    "Causal Sufficiency",
    "Substitutes / Fixtures",
    "Fresh Command Result",
]
EVIDENCE_UNRESOLVED_MARKER_RE = re.compile(
    r"(?i)(?:^|[;|])\s*(?:TODO|OPEN|GAP)(?:\s*[:;]|\s*$)"
)
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
    "Authorization / Effective Digest",
    "Assurance Profile / Verification Mode",
    "Worktree",
    "Git Ref",
    "Commit / Tree",
    "Base / Diff Identity",
    "Runtime Evidence Digests",
    "Consumed Contract Digests",
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
class AssuranceAssignment:
    owner: str
    lens: str
    side: str
    reason: str


@dataclass(frozen=True)
class PackageMarkdown:
    package_id: str
    title: str
    scope: str
    slice_refs: list[SliceRef]
    primary_paths: list[str]
    verification_expectations: list[str]
    proof_path: str
    verification_mode: str
    report_path: str | None
    verification_rationale: str
    assurance_assignment: AssuranceAssignment
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
    report_path: str | None
    status: str
    depends_on: list[str]
    verification_mode: str


@dataclass(frozen=True)
class Registry:
    path: Path
    root: Path
    code_root: Path
    data: dict[str, Any]
    feature: str
    authoritative_slices: list[str]
    packages: list[RegistryPackage]
    assurance_profile: str
    planned_sidecar: bool

    def package(self, package_id: str) -> RegistryPackage | None:
        for package in self.packages:
            if package.package_id == package_id:
                return package
        return None

    def dependents(self, package_id: str) -> list[str]:
        return [
            package.package_id
            for package in self.packages
            if package_id in package.depends_on
        ]


@dataclass(frozen=True)
class CandidateBinding:
    authorization_id: str
    effective_digest: str
    assurance_profile: str
    verification_mode: str
    commit: str
    tree: str
    base_commit: str
    diff_digest: str
    runtime_evidence_digests: tuple[tuple[str, str], ...]
    consumed_contract_digests: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class ControlledRouting:
    authorization_id: str
    effective_digest: str
    assurance_profile: str
    package_modes: dict[str, str]
    package_assignments: list[dict[str, str]]
    package_states: dict[str, str]
    code_checkpoint_ref: str | None
    code_checkpoint_sha: str | None


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
    report_path: Path | None
    package_markdowns: dict[str, PackageMarkdown]


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except SliceproofError as exc:
        payload: dict[str, Any] = {"ok": False, "command": args.command, "errors": exc.errors}
        if args.command in {"validate-package-complete", "validate-final", "validate-agentic-completion"} or exc.advisories:
            payload["advisories"] = exc.advisories
        write_json(sys.stderr, payload)
        return 1
    except (OSError, UnicodeError) as exc:
        payload = {"ok": False, "command": args.command, "errors": [f"{args.command}: I/O error: {exc}"]}
        if args.command in {"validate-package-complete", "validate-final", "validate-agentic-completion"}:
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

    validate_completion = subparsers.add_parser(
        "validate-agentic-completion",
        parents=[root_options],
        help="Validate a checkpointed, freeze-scoped final receipt graph without mutating state.",
    )
    validate_completion.add_argument(
        "--feature",
        required=True,
        help="Feature slug used to derive Lifecycle State, freeze, and receipt paths.",
    )
    validate_completion.set_defaults(func=cmd_validate_agentic_completion)

    emit_state_binding = subparsers.add_parser(
        "emit-state-binding",
        parents=[root_options],
        help="Emit the canonical State Binding block for a package verification report.",
    )
    emit_state_binding.add_argument("tasks", type=Path, help="Path to .tasks/<feature>/tasks.json under the artifact root.")
    emit_state_binding.add_argument("--package", required=True, help="Work package id, for example WP1.")
    emit_state_binding.add_argument("--authorization-id", required=True, help="Stable authorization identifier.")
    emit_state_binding.add_argument("--effective-digest", required=True, help="Effective Authorization sha256 digest.")
    emit_state_binding.add_argument("--assurance-profile", required=True, help="Candidate assurance profile.")
    emit_state_binding.add_argument("--verification-mode", required=True, help="Candidate package verification mode.")
    emit_state_binding.add_argument("--worktree", required=True, help="Absolute reviewed worktree path to write into the binding.")
    emit_state_binding.add_argument("--git-ref", required=True, help="Reviewed git ref to write into the binding.")
    emit_state_binding.add_argument("--commit", required=True, help="Exact reviewed commit object id.")
    emit_state_binding.add_argument("--tree", required=True, help="Exact reviewed tree object id.")
    emit_state_binding.add_argument("--base-commit", required=True, help="Exact base commit object id.")
    emit_state_binding.add_argument("--diff-digest", required=True, help="Canonical candidate diff sha256 digest.")
    emit_state_binding.add_argument(
        "--runtime-evidence-digest",
        action="append",
        required=True,
        help="Repeat artifact-relative PATH=sha256:<digest>, or pass exactly 'none'.",
    )
    emit_state_binding.add_argument(
        "--consumed-contract-digest",
        action="append",
        required=True,
        help="Repeat CONTRACT-ID=sha256:<digest>, or pass exactly 'none'.",
    )
    emit_state_binding.add_argument("--verified-at", required=True, help="Timezone-aware ISO-8601 verification timestamp.")
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
        help="Required absolute distinct sidecar root for .planning/.tasks planned-feature artifacts.",
    )
    parser.add_argument(
        "--code-root",
        type=Path,
        help="Required absolute distinct code worktree root for source/test evidence.",
    )


def require_planned_cli_roots(args: argparse.Namespace) -> tuple[Path, Path]:
    command = args.command
    missing = [flag for flag, value in (
        ("--artifact-root", args.artifact_root),
        ("--code-root", args.code_root),
    ) if value is None]
    if missing:
        raise SliceproofError([
            f"{command}: explicit absolute --artifact-root and --code-root are required; missing {', '.join(missing)}"
        ])
    if not args.artifact_root.is_absolute() or not args.code_root.is_absolute():
        raise SliceproofError([
            f"{command}: --artifact-root and --code-root must both be absolute paths"
        ])
    cwd = Path.cwd().resolve(strict=False)
    artifact_root = resolve_cli_root(args.artifact_root, cwd, "--artifact-root")
    code_root = resolve_cli_root(args.code_root, cwd, "--code-root")
    if artifact_root == code_root:
        raise SliceproofError([
            f"{command}: artifact root and code root must be distinct; same-root files are migration input only"
        ])
    require_exact_git_root(artifact_root, "artifact root", command=command)
    require_exact_git_root(code_root, "code root", command=command)
    args.artifact_root = artifact_root
    args.code_root = code_root
    return artifact_root, code_root


def cmd_validate_lifecycle_state(args: argparse.Namespace) -> dict[str, Any]:
    artifact_root, code_root = require_planned_cli_roots(args)
    if not FEATURE_RE.fullmatch(args.feature):
        raise SliceproofError(["--feature: expected lowercase slug with letters, digits, and hyphens"])

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

    generation, previous_commit, previous_digest = validate_lifecycle_transition_authority(
        state,
        artifact_root=artifact_root,
        code_root=code_root,
        feature=args.feature,
        relative_path=relative_path,
        previous_commit=args.previous_commit,
        infer_previous=False,
        state_data_already_validated=True,
    )

    return {
        "artifact_root": str(artifact_root),
        "code_root": str(code_root),
        "state_path": relative_path,
        "feature": args.feature,
        "schema_version": state["schema_version"],
        "generation": generation,
        "stage": state["stage"],
        "quiescent": state["quiescent"],
        "disposition": state["disposition"],
        "next_legal_actions": state["next_legal_actions"],
        "resume": state["resume"],
        "supersession": state["supersession"],
        "state_digest": canonical_json_digest(state),
        "previous_commit": previous_commit,
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
FREEZE_ID_SCHEMA = ("pattern", FREEZE_ID_RE, "freeze-<slug>")
LENS_SCHEMA = ("pattern", LENS_RE, "lowercase path-safe lens")
FEATURE_SCHEMA = ("pattern", FEATURE_RE, "lowercase feature slug")
POSITIVE_INT_SCHEMA = ("rule", lambda value: type(value) is int and value > 0, "positive integer")
NONNEGATIVE_INT_SCHEMA = ("rule", lambda value: type(value) is int and value >= 0, "non-negative integer")
NULLABLE_TOKEN_SCHEMA = ("nullable", TOKEN_SCHEMA)
NULLABLE_DIGEST_SCHEMA = ("nullable", DIGEST_SCHEMA)
NULLABLE_SHA_SCHEMA = ("nullable", SHA_SCHEMA)
AUTHORIZATION_INPUTS_SCHEMA = {
    "artifact_commit": SHA_SCHEMA,
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
ROLE_CALL_CONSUMPTION_SCHEMA = {
    role: NONNEGATIVE_INT_SCHEMA for role in FINAL_ASSURANCE_CALL_COUNTERS
}
ARTIFACT_DIGEST_ENTRY_SCHEMA = {"path": str, "digest": DIGEST_SCHEMA}
SEMANTIC_ARTIFACT_ENTRY_SCHEMA = {
    "kind": ("enum", {"spec", "registry", "package", "proof", "boundary-report", "slice"}),
    "path": str,
    "digest": DIGEST_SCHEMA,
}
BOUNDARY_RECEIPT_SCHEMA = {
    "package": PACKAGE_ID_SCHEMA,
    "path": str,
    "digest": DIGEST_SCHEMA,
}
PACKAGE_ASSURANCE_ASSIGNMENT_SCHEMA = {
    "package": PACKAGE_ID_SCHEMA,
    "mode": ("enum", PACKAGE_VERIFICATION_MODES),
    "owner": ("enum", ASSURANCE_ASSIGNMENT_OWNERS),
    "lens": LENS_SCHEMA,
    "side": ("enum", ASSURANCE_ASSIGNMENT_SIDES),
}
FREEZE_FILE_SCHEMA = {
    "schema_version": ("rule", lambda value: type(value) is int and value == 1, "1"),
    "kind": ("enum", {"agentic-freeze"}),
    "id": FREEZE_ID_SCHEMA,
    "authorization": {"id": TOKEN_SCHEMA, "effective_digest": DIGEST_SCHEMA},
    "code": {
        "checkpoint_ref": str,
        "commit": SHA_SCHEMA,
        "tree": SHA_SCHEMA,
        "base_commit": SHA_SCHEMA,
        "raw_diff_digest": DIGEST_SCHEMA,
        "clean_status_digest": DIGEST_SCHEMA,
    },
    "semantic_artifacts": ("list", SEMANTIC_ARTIFACT_ENTRY_SCHEMA),
    "runtime_evidence": ("list", ARTIFACT_DIGEST_ENTRY_SCHEMA),
    "assurance": {
        "profile": ("enum", ASSURANCE_PROFILES),
        "package_modes": ("map", PACKAGE_ID_SCHEMA, ("enum", PACKAGE_VERIFICATION_MODES)),
        "package_assignments": ("list", PACKAGE_ASSURANCE_ASSIGNMENT_SCHEMA),
        "required_boundary_receipts": ("list", BOUNDARY_RECEIPT_SCHEMA),
        "specialist_lenses": ("list", LENS_SCHEMA),
    },
    "serious_clusters_digest": DIGEST_SCHEMA,
    "command_results": ("list", ARTIFACT_DIGEST_ENTRY_SCHEMA),
    "frozen_at": str,
}
PREDECESSOR_POINTER_SCHEMA = {
    "role": ("enum", {"F", "C", "R", "S", "U"}),
    "lens": LENS_SCHEMA,
    "path": str,
    "digest": DIGEST_SCHEMA,
}

LIFECYCLE_JSON_SCHEMA = {
    "schema_version": ("rule", lambda value: type(value) is int and value == 1, "1"),
    "generation": POSITIVE_INT_SCHEMA,
    "feature": str,
    "stage": ("enum", LIFECYCLE_STAGES),
    "quiescent": bool,
    "next_legal_actions": ("list", ACTION_SCHEMA),
    "disposition": ("enum", LIFECYCLE_DISPOSITIONS),
    "resume": ("nullable", {
        "stage": ("enum", RESUMABLE_LIFECYCLE_STAGES),
        "next_legal_actions": ("list", ACTION_SCHEMA),
    }),
    "supersession": ("nullable", {
        "feature": FEATURE_SCHEMA,
        "baseline": {
            "artifact": {"ref": str, "sha": SHA_SCHEMA, "tree": SHA_SCHEMA},
            "code": ("nullable", {"ref": str, "sha": SHA_SCHEMA}),
        },
        "package_map": ("list", {"source": PACKAGE_ID_SCHEMA, "target": PACKAGE_ID_SCHEMA}),
    }),
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
        "role_call_consumption": ROLE_CALL_CONSUMPTION_SCHEMA,
        "active_reservation": ("nullable", {
            "id": TOKEN_SCHEMA,
            "owner_token": TOKEN_SCHEMA,
            "budget": ("enum", {"preauthorization", "implementation"}),
            "generation": POSITIVE_INT_SCHEMA,
            "units": ("map", COUNTER_SCHEMA, POSITIVE_INT_SCHEMA),
        }),
        "control_plane_reserve": {
            "maximum": NONNEGATIVE_INT_SCHEMA,
            "issued": NONNEGATIVE_INT_SCHEMA,
            "reservation": ("nullable", {
                "id": TOKEN_SCHEMA,
                "generation": POSITIVE_INT_SCHEMA,
                "operation": ("enum", CONTROL_PLANE_OPERATIONS),
                "reason": ("enum", CONTROL_PLANE_REASONS),
                "expected_parent": SHA_SCHEMA,
                "checkpoint_digest": NULLABLE_DIGEST_SCHEMA,
                "conflict_digest": NULLABLE_DIGEST_SCHEMA,
            }),
        },
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
        "accepted_invariant": str,
        "root_mechanism": str,
        "architectural_surface": str,
        "observed_signatures": ("list", DIGEST_SCHEMA),
        "observed_classes": ("list", ("enum", CLUSTER_CLASSES)),
        "class": ("enum", CLUSTER_CLASSES),
        "route": ("enum", set(CLUSTER_ROUTES.values())),
        "strikes": ("enum", {1, 2}),
        "disposition": ("enum", CLUSTER_DISPOSITIONS),
        "repair": ("nullable", {
            "root_cause_digest": DIGEST_SCHEMA,
            "affected_surface_digest": DIGEST_SCHEMA,
        }),
        "closure": ("nullable", {
            "verdict": ("enum", {"PASS", "FAIL"}),
            "affected_surface_digest": DIGEST_SCHEMA,
            "evidence_digest": DIGEST_SCHEMA,
        }),
    }),
    "freeze": ("nullable", {
        "id": FREEZE_ID_SCHEMA, "path": str, "digest": DIGEST_SCHEMA,
    }),
    "receipts": ("list", {
        "role": ("enum", ASSURANCE_RECEIPT_ROLES),
        "lens": LENS_SCHEMA,
        "path": str,
        "digest": DIGEST_SCHEMA,
        "freeze_digest": DIGEST_SCHEMA,
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
    "package_assignments": ("list", PACKAGE_ASSURANCE_ASSIGNMENT_SCHEMA),
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


def validate_lifecycle_disposition_state(
    state: dict[str, Any],
    *,
    artifact_root: Path,
    code_root: Path,
    feature: str,
    verify_git_objects: bool,
    errors: list[str],
) -> None:
    label = "lifecycle-state.json"
    disposition = state["disposition"]
    stage = state["stage"]
    actions = state["next_legal_actions"]
    resume = state["resume"]
    supersession = state["supersession"]

    if resume is not None:
        resume_actions = resume["next_legal_actions"]
        if not resume_actions or len(resume_actions) != len(set(resume_actions)) or len(resume_actions) > 8:
            errors.append(
                f"{label}.resume.next_legal_actions: expected a non-empty ordered unique list bounded to eight"
            )
        if "resume" in resume_actions:
            errors.append(f"{label}.resume.next_legal_actions: an active resume point cannot name resume")

    if disposition == "active":
        if stage not in RESUMABLE_LIFECYCLE_STAGES:
            errors.append(f"{label}: active disposition requires a resumable active stage")
        if not actions:
            errors.append(f"{label}.next_legal_actions: active state requires at least one action")
        if "resume" in actions:
            errors.append(f"{label}.next_legal_actions: resume is legal only while parked")
        if resume is not None or supersession is not None:
            errors.append(f"{label}: active state cannot retain resume or supersession metadata")
    elif disposition == "parked":
        if stage != "parked" or state["quiescent"] is not True:
            errors.append(f"{label}: parked disposition requires parked stage and quiescent true")
        if state["owner"]["disposition"] != "stopped":
            errors.append(f"{label}.owner.disposition: parked state requires a stopped logical owner")
        expected_actions = list(PARKED_NEXT_ACTIONS)
        if state["authorization"]["id"] is None:
            expected_actions.remove("supersede")
        if actions != expected_actions:
            errors.append(
                f"{label}.next_legal_actions: parked state requires ordered legal actions {expected_actions!r}"
            )
        if resume is None:
            errors.append(f"{label}.resume: parked state requires the exact prior stage and actions")
        if supersession is not None:
            errors.append(f"{label}.supersession: parked state cannot already name a replacement")
    elif disposition == "cancelled":
        if stage != "cancelled" or state["quiescent"] is not True or actions:
            errors.append(f"{label}: cancelled disposition requires cancelled quiescent terminal state with no action")
        if supersession is not None:
            errors.append(f"{label}.supersession: cancelled state cannot name a replacement")
    elif disposition == "superseded":
        if stage != "superseded" or state["quiescent"] is not True or actions:
            errors.append(f"{label}: superseded disposition requires superseded quiescent terminal state with no action")
        if supersession is None:
            errors.append(f"{label}.supersession: superseded state requires replacement provenance and package map")
    elif disposition == "completed":
        if stage != "completed" or state["quiescent"] is not True or actions:
            errors.append(f"{label}: completed disposition requires completed quiescent terminal state with no action")
        if resume is not None or supersession is not None:
            errors.append(f"{label}: completed state cannot retain resume or supersession metadata")

    if disposition in {"parked", "cancelled", "superseded"}:
        if state["budgets"]["active_reservation"] is not None:
            errors.append(f"{label}: quiescent continuity disposition cannot retain an active reservation")
        if state["budgets"]["control_plane_reserve"]["reservation"] is not None:
            errors.append(f"{label}: quiescent continuity disposition cannot retain a control-plane reservation")
        wave = state["wave"]
        if wave is not None and wave["state"] in {"reserved", "active"}:
            errors.append(f"{label}.wave: quiescent continuity disposition cannot retain reserved or active work")

    if supersession is None:
        return
    replacement_feature = supersession["feature"]
    if replacement_feature == feature:
        errors.append(f"{label}.supersession.feature: replacement feature must differ from the superseded feature")
    baseline = supersession["baseline"]
    baseline_artifact = baseline["artifact"]
    expected_artifact_ref = f"refs/heads/artifacts/{replacement_feature}"
    if baseline_artifact["ref"] != expected_artifact_ref:
        errors.append(
            f"{label}.supersession.baseline.artifact.ref: expected {expected_artifact_ref!r}"
        )
    elif verify_git_objects:
        tree = git_commit_tree(
            artifact_root,
            baseline_artifact["sha"],
            f"{label}.supersession.baseline.artifact.sha",
            errors,
        )
        if tree is not None and tree != baseline_artifact["tree"]:
            errors.append(f"{label}.supersession.baseline.artifact.tree: does not match baseline commit tree")
        require_git_ref_at_commit(
            artifact_root,
            baseline_artifact["ref"],
            baseline_artifact["sha"],
            f"{label}.supersession.baseline.artifact.ref",
            errors,
        )

    baseline_code = baseline["code"]
    if baseline_code is not None:
        if immutable_checkpoint_ref_generation(baseline_code["ref"], replacement_feature) is None:
            errors.append(
                f"{label}.supersession.baseline.code.ref: expected immutable replacement checkpoint ref"
            )
        elif verify_git_objects:
            require_git_ref_at_commit(
                code_root,
                baseline_code["ref"],
                baseline_code["sha"],
                f"{label}.supersession.baseline.code.ref",
                errors,
            )

    package_map = supersession["package_map"]
    if not package_map:
        errors.append(f"{label}.supersession.package_map: expected at least one old-to-new package edge")
        return
    ordered = sorted(
        package_map,
        key=lambda edge: (package_id_order(edge["source"]), package_id_order(edge["target"])),
    )
    if package_map != ordered:
        errors.append(f"{label}.supersession.package_map: edges must use canonical package-id order")
    targets = [edge["target"] for edge in package_map]
    if len(targets) != len(set(targets)):
        errors.append(f"{label}.supersession.package_map: each target must have exactly one source")
    package_ids = set(state["packages"])
    adjacency: dict[str, set[str]] = {}
    for edge in package_map:
        source, target = edge["source"], edge["target"]
        if source not in package_ids or target not in package_ids:
            errors.append(f"{label}.supersession.package_map: every source and target must exist in packages")
            continue
        if source == target:
            errors.append(f"{label}.supersession.package_map: source and target must differ")
        adjacency.setdefault(source, set()).add(target)
        if state["packages"][source]["state"] != "invalidated":
            errors.append(f"{label}.packages.{source}.state: mapped old package must be invalidated")
        target_state = state["packages"][target]
        if target_state != {"state": "pending", "wave": None}:
            errors.append(f"{label}.packages.{target}: replacement package must append as pending with no wave")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(package_id: str) -> bool:
        if package_id in visiting:
            return False
        if package_id in visited:
            return True
        visiting.add(package_id)
        if any(not visit(target) for target in adjacency.get(package_id, set())):
            return False
        visiting.remove(package_id)
        visited.add(package_id)
        return True

    if any(not visit(package_id) for package_id in adjacency):
        errors.append(f"{label}.supersession.package_map: replacement mapping must be acyclic")

    if verify_git_objects and baseline_artifact["ref"] == expected_artifact_ref:
        validate_replacement_baseline_lifecycle(
            state,
            artifact_root=artifact_root,
            code_root=code_root,
            replacement_feature=replacement_feature,
            baseline_artifact=baseline_artifact,
            mapped_targets=set(targets),
            errors=errors,
        )


def load_regular_committed_json_blob(
    root: Path,
    commit: str,
    path: str,
    label: str,
    errors: list[str],
) -> dict[str, Any] | None:
    try:
        tree_line = git_output(root, ["ls-tree", commit, "--", path], label).strip()
    except SliceproofError as exc:
        errors.extend(exc.errors)
        return None
    fields = tree_line.split(None, 3)
    if len(fields) != 4 or fields[0] not in {"100644", "100755"} or fields[1] != "blob" or fields[3] != path:
        errors.append(f"{label}: expected a regular committed JSON blob at {path!r}")
        return None
    try:
        value = load_strict_json_text(
            git_output(root, ["show", f"{commit}:{path}"], label),
            label,
        )
    except SliceproofError as exc:
        errors.extend(exc.errors)
        return None
    if not isinstance(value, dict):
        errors.append(f"{label}: root must be an object")
        return None
    return value


def validate_replacement_baseline_lifecycle(
    superseded_state: dict[str, Any],
    *,
    artifact_root: Path,
    code_root: Path,
    replacement_feature: str,
    baseline_artifact: dict[str, str],
    mapped_targets: set[str],
    errors: list[str],
) -> None:
    label = "lifecycle-state.json.supersession.baseline.artifact"
    old_commits = {superseded_state["artifact_checkpoint"]["sha"]}
    verified = superseded_state.get("last_verified")
    if isinstance(verified, dict):
        old_commits.add(verified.get("artifact_sha"))
    if baseline_artifact["sha"] in old_commits:
        errors.append(
            f"{label}.sha: replacement baseline must be a distinct replacement commit, not the old feature commit"
        )
        return

    path = f".tasks/{replacement_feature}/lifecycle-state.json"
    replacement = load_regular_committed_json_blob(
        artifact_root,
        baseline_artifact["sha"],
        path,
        f"{label}: replacement Lifecycle State",
        errors,
    )
    if replacement is None:
        return
    replacement_errors = validate_lifecycle_state_data(
        replacement,
        artifact_root=artifact_root,
        code_root=code_root,
        feature=replacement_feature,
        verify_files=False,
        verify_git_objects=False,
    )
    errors.extend(f"{label}: replacement snapshot: {error}" for error in replacement_errors)
    if replacement_errors:
        return
    if replacement["disposition"] != "active" or replacement["supersession"] is not None:
        errors.append(f"{label}: replacement baseline must be active with null supersession")
        return
    object_errors = validate_lifecycle_state_data(
        replacement,
        artifact_root=artifact_root,
        code_root=code_root,
        feature=replacement_feature,
        verify_files=False,
        verify_git_objects=True,
    )
    errors.extend(f"{label}: replacement object snapshot: {error}" for error in object_errors)
    if object_errors:
        return
    replacement_generation = replacement["generation"]
    if replacement_generation == 1 and mapped_targets:
        errors.append(f"{label}: mapped targets require a committed post-generation-1 replacement transition")
    if replacement_generation == 1:
        return
    replacement_code = replacement["code_checkpoint"]
    baseline_code = superseded_state["supersession"]["baseline"]["code"]
    if replacement_code != baseline_code:
        errors.append(f"{label}: replacement code checkpoint must exactly equal baseline code provenance")

    transition_label = f"{label}: replacement transition"
    verified = replacement["last_verified"]
    try:
        parents = git_output(
            artifact_root,
            ["rev-list", "--parents", "-n", "1", baseline_artifact["sha"]],
            transition_label,
        ).split()
    except SliceproofError as exc:
        errors.extend(exc.errors)
        return
    if len(parents) != 2 or parents[1] != verified["artifact_sha"]:
        errors.append(
            f"{transition_label}: baseline commit must have last_verified.artifact_sha as its sole parent"
        )
        return

    predecessor = load_regular_committed_json_blob(
        artifact_root,
        verified["artifact_sha"],
        path,
        f"{transition_label}: predecessor Lifecycle State",
        errors,
    )
    if predecessor is None:
        return
    predecessor_errors = validate_lifecycle_state_data(
        predecessor,
        artifact_root=artifact_root,
        code_root=code_root,
        feature=replacement_feature,
        verify_files=False,
        verify_git_objects=False,
    )
    errors.extend(f"{transition_label}: predecessor snapshot: {error}" for error in predecessor_errors)
    if predecessor_errors:
        return
    predecessor_artifact = predecessor["artifact_checkpoint"]
    if predecessor_artifact["sha"] is not None:
        predecessor_tree = git_commit_tree(
            artifact_root,
            predecessor_artifact["sha"],
            f"{transition_label}: predecessor artifact_checkpoint.sha",
            errors,
        )
        if predecessor_tree is not None and predecessor_tree != predecessor_artifact["tree"]:
            errors.append(f"{transition_label}: predecessor artifact checkpoint tree does not match its commit")
    if predecessor["quiescent"] is not True:
        errors.append(f"{transition_label}: predecessor must be quiescent")
    if verified["state_digest"] != canonical_json_digest(predecessor):
        errors.append(f"{transition_label}: last_verified.state_digest does not match the predecessor blob")
    errors.extend(f"{transition_label}: {error}" for error in compare_lifecycle_states(predecessor, replacement))
    errors.extend(
        f"{transition_label}: {error}"
        for error in validate_artifact_checkpoint_ancestry(artifact_root, predecessor, replacement)
    )
    errors.extend(
        f"{transition_label}: {error}"
        for error in validate_artifact_checkpoint_lineage(
            artifact_root,
            predecessor["artifact_checkpoint"]["sha"],
            verified["artifact_sha"],
            "predecessor artifact checkpoint",
        )
    )
    errors.extend(
        f"{transition_label}: {error}"
        for error in validate_artifact_checkpoint_lineage(
            artifact_root,
            replacement["artifact_checkpoint"]["sha"],
            baseline_artifact["sha"],
            "replacement artifact checkpoint",
        )
    )

    replacement_packages = replacement["packages"]
    missing_targets = sorted(mapped_targets - set(replacement_packages), key=package_id_order)
    non_pending_targets = sorted(
        target for target in mapped_targets & set(replacement_packages)
        if replacement_packages[target] != {"state": "pending", "wave": None}
    )
    if missing_targets:
        errors.append(f"{label}: replacement Lifecycle State is missing mapped pending targets {missing_targets}")
    if non_pending_targets:
        errors.append(
            f"{label}: replacement Lifecycle State must bind mapped targets pending with no wave; got {non_pending_targets}"
        )

    old_authorization = superseded_state["authorization"]
    replacement_authorization = replacement["authorization"]
    inherited = [
        field for field in ("id", "initial_digest", "effective_digest")
        if old_authorization[field] is not None
        and replacement_authorization[field] == old_authorization[field]
    ]
    if inherited:
        errors.append(f"{label}: replacement Lifecycle State inherits old authorization fields {inherited}")
    if replacement["freeze"] is not None or replacement["receipts"]:
        errors.append(f"{label}: replacement baseline cannot inherit freeze or final-assurance receipts")
    completed_packages = sorted(
        package_id for package_id, package in replacement_packages.items()
        if package["state"] in {"verified", "done"}
    )
    if completed_packages:
        errors.append(f"{label}: replacement baseline cannot inherit package completion {completed_packages}")


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
    validate_lifecycle_disposition_state(
        state,
        artifact_root=artifact_root,
        code_root=code_root,
        feature=feature,
        verify_git_objects=verify_git_objects,
        errors=errors,
    )
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
            require_git_ref_at_commit(
                code_root,
                code["ref"],
                code["sha"],
                f"{label}.code_checkpoint.ref",
                errors,
            )

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
    resume = state["resume"]
    if resume is not None:
        if resume["stage"] in PREAUTH_LIFECYCLE_STAGES and authorization_complete:
            errors.append(f"{label}.resume.stage: preauthorization resume point cannot carry implementation authority")
        if resume["stage"] in AUTHORIZED_LIFECYCLE_STAGES and not authorization_complete:
            errors.append(f"{label}.resume.stage: authorized resume point requires complete authorization")
    if state["disposition"] == "superseded" and not authorization_complete:
        errors.append(f"{label}.authorization: supersession requires complete reviewed authorization lineage")
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
    assignments = state["package_assignments"]
    if not authorization_complete and assignments != []:
        errors.append(f"{label}.package_assignments: must be empty before authorization")
    if authorization_complete:
        inputs = authorization["inputs"]
        if authorization["initial_digest"] != canonical_json_digest(inputs):
            errors.append(f"{label}.authorization.initial_digest: must equal the canonical inputs digest")
        if verify_git_objects:
            artifact_input_tree = git_commit_tree(
                artifact_root,
                inputs["artifact_commit"],
                f"{label}.authorization.inputs.artifact_commit",
                errors,
            )
            require_git_tree(artifact_root, inputs["artifact_tree"], f"{label}.authorization.inputs.artifact_tree", errors)
            if artifact_input_tree is not None and artifact_input_tree != inputs["artifact_tree"]:
                errors.append(
                    f"{label}.authorization.inputs.artifact_tree: does not match authorization artifact commit tree"
                )
            require_git_commit(code_root, inputs["base_commit"], f"{label}.authorization.inputs.base_commit", errors)
        profile = state.get("assurance_profile")
        modes = state.get("package_modes")
        if profile is None:
            errors.append(f"{label}.assurance_profile: required after authorization")
        if not isinstance(modes, dict) or not modes or set(modes) != set(packages):
            errors.append(f"{label}.package_modes: authorized state must bind every lifecycle package exactly")
        if profile in ASSURANCE_PROFILES and isinstance(modes, dict):
            errors.extend(validate_assurance_assignment_values(
                assignments,
                profile=profile,
                package_modes=modes,
                label=f"{label}.package_assignments",
            ))
        if not packages:
            errors.append(f"{label}.packages: authorized state requires at least one package")
        if profile == "low" and isinstance(modes, dict) and (
            len(modes) != 1 or set(modes.values()) != {"final"}
        ):
            errors.append(f"{label}: low assurance requires exactly one final package mode")
        if authorization["effective_digest"] == authorization["initial_digest"]:
            if inputs["artifact_commit"] != artifact["sha"]:
                errors.append(
                    f"{label}.authorization.inputs.artifact_commit: must match the initial artifact checkpoint commit"
                )
            if inputs["artifact_tree"] != artifact["tree"]:
                errors.append(
                    f"{label}.authorization.inputs.artifact_tree: must match the initial artifact checkpoint tree"
                )
            if profile is not None and isinstance(modes, dict):
                routing = assurance_routing_digest(profile, modes, assignments)
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
            "continuity": (
                state["disposition"] != "active"
                or state["resume"] is not None
                or state["supersession"] is not None
            ),
            "role_call_consumption": any(state["budgets"]["role_call_consumption"].values()),
            "packages": bool(packages),
            "package_assignments": bool(assignments),
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

    validate_serious_clusters(state["serious_clusters"], errors)
    for package_id in state.get("package_modes", {}):
        if package_id not in packages:
            errors.append(f"{label}.package_modes.{package_id}: package is not present in lifecycle packages")

    validate_receipt_pointers(
        state["freeze"], state["receipts"], artifact_root, feature, errors, verify_files
    )
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


def validate_lifecycle_transition_authority(
    state: dict[str, Any],
    *,
    artifact_root: Path,
    code_root: Path,
    feature: str,
    relative_path: str,
    previous_commit: str | None,
    infer_previous: bool,
    state_data_already_validated: bool = False,
) -> tuple[int, str | None, str | None]:
    """Validate the exact committed predecessor and one-generation transition.

    The standalone command supplies ``previous_commit`` explicitly. Distinct-root
    consumers infer that same exact value from ``last_verified`` so schema-valid
    snapshots cannot become controlled authority without transition proof.
    """
    if not state_data_already_validated:
        errors = validate_lifecycle_state_data(
            state,
            artifact_root=artifact_root,
            code_root=code_root,
            feature=feature,
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
        if previous_commit is not None:
            raise SliceproofError(["validate-lifecycle-state: generation 1 must not name --previous-commit"])
        validate_generation_one_topology(artifact_root, relative_path, state)
        return generation, None, None

    verified = state["last_verified"]
    inferred_previous = verified["artifact_sha"] if infer_previous else previous_commit
    if inferred_previous is None:
        raise SliceproofError(["validate-lifecycle-state: --previous-commit is required after generation 1"])
    if inferred_previous != verified["artifact_sha"]:
        raise SliceproofError([
            "validate-lifecycle-state: --previous-commit does not match last_verified.artifact_sha"
        ])

    previous = load_committed_lifecycle_state(
        artifact_root, relative_path, inferred_previous, current_state=state
    )
    prior_errors = validate_lifecycle_state_data(
        previous,
        artifact_root=artifact_root,
        code_root=code_root,
        feature=feature,
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
        inferred_previous,
        "prior snapshot: artifact_checkpoint.sha",
    )
    if prior_lineage_errors:
        raise SliceproofError(prior_lineage_errors)
    previous_digest = canonical_json_digest(previous)
    if verified["state_digest"] != previous_digest:
        raise SliceproofError([
            "lifecycle-state.json.last_verified.state_digest: does not match the committed predecessor state"
        ])
    transition_errors = compare_lifecycle_states(previous, state)
    transition_errors.extend(validate_control_only_transition_paths(
        artifact_root,
        code_root,
        inferred_previous,
        relative_path,
        state,
    ))
    transition_errors.extend(validate_continuity_transition_paths(
        artifact_root,
        code_root,
        inferred_previous,
        relative_path,
        previous,
        state,
    ))
    transition_errors.extend(validate_artifact_checkpoint_ancestry(artifact_root, previous, state))
    transition_errors.extend(validate_assurance_paths_append_only(artifact_root, feature, inferred_previous))
    transition_errors.extend(validate_new_assurance_pointer_paths(
        artifact_root, inferred_previous, previous, state
    ))
    if transition_errors:
        raise SliceproofError(transition_errors)
    return generation, inferred_previous, previous_digest


def canonical_serious_cluster_id(cluster: dict[str, Any]) -> str:
    return canonical_json_digest({
        "accepted_invariant": cluster["accepted_invariant"],
        "architectural_surface": cluster["architectural_surface"],
        "root_mechanism": cluster["root_mechanism"],
    })


def validate_serious_clusters(clusters: list[dict[str, Any]], errors: list[str]) -> None:
    label = "lifecycle-state.json.serious_clusters"
    ids = [cluster["id"] for cluster in clusters]
    if len(ids) != len(set(ids)):
        errors.append(f"{label}: duplicate canonical cluster id")
    for index, cluster in enumerate(clusters):
        item_label = f"{label}[{index}]"
        for field in ("accepted_invariant", "root_mechanism", "architectural_surface"):
            value = cluster[field]
            if not value or value != value.strip() or len(value) > 512:
                errors.append(f"{item_label}.{field}: expected concise canonical non-blank text")
        if cluster["id"] != canonical_serious_cluster_id(cluster):
            errors.append(
                f"{item_label}.id: must derive only from accepted_invariant, root_mechanism, and architectural_surface"
            )
        signatures = cluster["observed_signatures"]
        if not signatures or len(signatures) != len(set(signatures)):
            errors.append(f"{item_label}.observed_signatures: expected non-empty unique observations")
        observed_classes = cluster["observed_classes"]
        if not observed_classes or len(observed_classes) != len(set(observed_classes)):
            errors.append(f"{item_label}.observed_classes: expected non-empty unique classes")
        else:
            strongest_rank = min(CLUSTER_CLASS_PRECEDENCE_RANK[name] for name in observed_classes)
            selected = cluster["class"]
            if selected not in observed_classes or CLUSTER_CLASS_PRECEDENCE_RANK[selected] != strongest_rank:
                errors.append(f"{item_label}.class: must be an observed class at the strongest precedence rank")
        expected_route = CLUSTER_ROUTES[cluster["class"]]
        if cluster["route"] != expected_route:
            errors.append(f"{item_label}.route: class {cluster['class']!r} requires {expected_route!r}")

        strikes = cluster["strikes"]
        disposition = cluster["disposition"]
        repair = cluster["repair"]
        closure = cluster["closure"]
        if closure is not None and repair is not None and (
            closure["affected_surface_digest"] != repair["affected_surface_digest"]
        ):
            errors.append(f"{item_label}.closure: must bind the repair's exact affected surface")
        if expected_route == "closure-repair":
            valid_phase = (
                (strikes, disposition, repair is None, closure is None) == (1, "repair-eligible", True, True)
                or (strikes, disposition, repair is not None, closure is None)
                == (1, "closure-pending", True, True)
                or (
                    strikes == 1
                    and disposition == "closed"
                    and repair is not None
                    and closure is not None
                    and closure["verdict"] == "PASS"
                )
                or (
                    strikes == 2
                    and disposition == "circuit-open"
                    and repair is not None
                    and closure is not None
                    and closure["verdict"] == "FAIL"
                )
            )
            if not valid_phase:
                errors.append(
                    f"{item_label}: closure repair permits one strike-1 repair/PASS closure or strike-2 circuit-open"
                )
        else:
            valid_phase = (
                strikes == 1
                and repair is None
                and (
                    (disposition == "routed" and closure is None)
                    or (
                        disposition == "closed"
                        and (
                            (expected_route == "report-only" and closure is None)
                            or (closure is not None and closure["verdict"] == "PASS")
                        )
                    )
                )
            )
            if not valid_phase:
                errors.append(f"{item_label}: non-repair route cannot consume a repair or closure strike")


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
    control_reservation = control["reservation"]
    if control_reservation is not None:
        if control["issued"] != 1:
            errors.append(f"{label}.control_plane_reserve.reservation: must consume the one control unit")
        if control_reservation["generation"] != state["generation"]:
            errors.append(f"{label}.control_plane_reserve.reservation.generation: must equal Lifecycle State generation")
        if state["stage"] not in {"blocked", "needs-decision"}:
            errors.append(f"{label}.control_plane_reserve.reservation: escalation requires blocked or needs-decision")
        if state["budgets"]["active_reservation"] is not None:
            errors.append(f"{label}.control_plane_reserve.reservation: cannot coexist with a semantic reservation")
        if state["last_verified"] is None:
            errors.append(f"{label}.control_plane_reserve.reservation: requires exact last_verified fallback")
        elif control_reservation["expected_parent"] != state["last_verified"]["artifact_sha"]:
            errors.append(f"{label}.control_plane_reserve.reservation.expected_parent: must equal last_verified artifact sha")
        operation = control_reservation["operation"]
        checkpoint = control_reservation["checkpoint_digest"]
        conflict = control_reservation["conflict_digest"]
        if operation == "safe-checkpoint":
            if checkpoint is None or conflict is not None or state["owner"]["disposition"] != "active":
                errors.append(
                    f"{label}.control_plane_reserve.reservation: safe-checkpoint requires active ownership, checkpoint digest, and no conflict"
                )
        elif checkpoint is not None or conflict is None:
            errors.append(
                f"{label}.control_plane_reserve.reservation: last-verified requires conflict digest and no checkpoint mutation"
            )
        if control_reservation["reason"] in {"ownership-unavailable", "cas-unavailable"} and operation != "last-verified":
            errors.append(
                f"{label}.control_plane_reserve.reservation: ownership/CAS loss must use last-verified without takeover"
            )
        if control_reservation["reason"] == "budget-exhausted":
            implementation = budgets["implementation"]
            exhausted = implementation is not None and any(
                maximum > 0 and implementation["issued"][counter] == maximum
                for counter, maximum in implementation["maxima"].items()
            )
            if not exhausted:
                errors.append(f"{label}.control_plane_reserve.reservation: budget-exhausted requires an exhausted counter")

    implementation = budgets["implementation"]
    profile = state.get("assurance_profile")
    if implementation is not None and authorization_complete:
        maxima = implementation["maxima"]
        issued = implementation["issued"]
        issued_role_calls = sum(issued.get(counter, 0) for counter in ROLE_SCOPED_CALL_COUNTERS)
        if issued.get("delegated_calls", 0) < issued_role_calls:
            errors.append(
                f"{label}.implementation.issued.delegated_calls: must cover the sum of issued "
                f"role-scoped calls ({issued.get('delegated_calls', 0)} < {issued_role_calls})"
            )
        if profile in PROFILE_FINAL_EQUATION_ROLES:
            for role in PROFILE_REQUIRED_FINAL_ROLES[profile]:
                counter = FINAL_ASSURANCE_CALL_COUNTERS[role]
                if maxima.get(counter, 0) < 1:
                    errors.append(
                        f"{label}.implementation.maxima.{counter}: {profile} final equation requires at least 1"
                    )
            equation_counters = [
                FINAL_ASSURANCE_CALL_COUNTERS[role]
                for role in PROFILE_FINAL_EQUATION_ROLES[profile]
            ]
            equation_maximum = sum(maxima.get(counter, 0) for counter in equation_counters)
            if maxima.get("delegated_calls", 0) < equation_maximum:
                errors.append(
                    f"{label}.implementation.maxima.delegated_calls: must cover the selected {profile} "
                    f"final-equation role maxima ({maxima.get('delegated_calls', 0)} < {equation_maximum})"
                )
    if implementation is not None and profile in ASSURANCE_PROFILES:
        repair_maximum = implementation["maxima"].get("repair_waves")
        if profile == "low" and repair_maximum is not None and repair_maximum > 1:
            errors.append(f"{label}.implementation.maxima.repair_waves: low profile maximum is 1")
        if profile == "standard" and repair_maximum is not None and repair_maximum > 2:
            errors.append(f"{label}.implementation.maxima.repair_waves: standard profile maximum is 2")
        has_root_cause_repair = any(cluster["repair"] is not None for cluster in state["serious_clusters"])
        if has_root_cause_repair and implementation["issued"].get("repair_waves", 0) < 1:
            errors.append(f"{label}.implementation.issued.repair_waves: cluster repair must consume a wave")

    consumption = budgets["role_call_consumption"]
    current_receipt_counts = {
        role: sum(receipt["role"] == role for receipt in state["receipts"])
        for role in FINAL_ASSURANCE_CALL_COUNTERS
    }
    for role, counter in FINAL_ASSURANCE_CALL_COUNTERS.items():
        consumed = consumption[role]
        issued = 0 if implementation is None else implementation["issued"].get(counter, 0)
        if consumed > issued:
            errors.append(
                f"{label}.role_call_consumption.{role}: consumed calls exceed issued {counter} "
                f"({consumed} > {issued})"
            )
        if current_receipt_counts[role] > consumed:
            errors.append(
                f"{label}.role_call_consumption.{role}: current receipt graph requires at least "
                f"{current_receipt_counts[role]} consumed calls"
            )

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
    reserved_role_calls = sum(
        reservation["units"].get(counter, 0) for counter in ROLE_SCOPED_CALL_COUNTERS
    )
    if reserved_role_calls and reservation["units"].get("delegated_calls", 0) < reserved_role_calls:
        errors.append(
            f"{label}.active_reservation.units.delegated_calls: must cover the sum of reserved "
            f"role-scoped calls ({reservation['units'].get('delegated_calls', 0)} < {reserved_role_calls})"
        )
    for counter, amount in reservation["units"].items():
        if counter not in selected["issued"]:
            errors.append(f"{label}.active_reservation.units.{counter}: unsupported budget counter")
        elif amount > selected["issued"][counter]:
            errors.append(f"{label}.active_reservation.units.{counter}: reservation is not already charged")


def canonical_freeze_directory(feature: str, freeze_id: str) -> str:
    return f".tasks/{feature}/assurance/{freeze_id}"


def canonical_freeze_path(feature: str, freeze_id: str) -> str:
    return f"{canonical_freeze_directory(feature, freeze_id)}/freeze.json"


def canonical_receipt_path(feature: str, freeze_id: str, role: str, lens: str) -> str:
    base = canonical_freeze_directory(feature, freeze_id)
    if role == "C":
        return f"{base}/combined.json"
    if role == "R":
        return f"{base}/review.json"
    if role == "S":
        return f"{base}/specialists/{lens}.json"
    if role == "U":
        return f"{base}/audit.json"
    if role == "V":
        return f"{base}/verification-summary.json"
    raise ValueError(f"unsupported assurance receipt role {role!r}")


def validate_receipt_pointers(
    freeze: dict[str, Any] | None,
    receipts: list[dict[str, Any]],
    artifact_root: Path,
    feature: str,
    errors: list[str],
    verify_files: bool,
) -> None:
    label = "lifecycle-state.json"
    if freeze is None:
        if receipts:
            errors.append(f"{label}.receipts: receipt pointers require a freeze")
        return
    expected_freeze_path = canonical_freeze_path(feature, freeze["id"])
    try:
        repo_relative_path(freeze["path"], f"{label}.freeze.path")
    except SliceproofError as exc:
        errors.extend(exc.errors)
    if freeze["path"] != expected_freeze_path:
        errors.append(f"{label}.freeze.path: expected canonical path {expected_freeze_path!r}")
    elif verify_files:
        validate_pointer_file(artifact_root, freeze["path"], freeze["digest"], f"{label}.freeze", errors)

    seen_roles: set[str] = set()
    seen_lenses: set[str] = set()
    for index, receipt in enumerate(receipts):
        item_label = f"{label}.receipts[{index}]"
        role, lens = receipt["role"], receipt["lens"]
        if role in seen_roles and role != "S":
            errors.append(f"{label}.receipts: duplicate singleton role {role}")
        seen_roles.add(role)
        if lens in seen_lenses:
            errors.append(f"{label}.receipts: duplicate receipt lens {lens!r}")
        seen_lenses.add(lens)
        fixed_lens = FIXED_RECEIPT_LENSES.get(role)
        if fixed_lens is not None and lens != fixed_lens:
            errors.append(f"{item_label}.lens: role {role} requires {fixed_lens!r}")
        if role == "S" and lens in set(FIXED_RECEIPT_LENSES.values()):
            errors.append(f"{item_label}.lens: specialist cannot reuse a canonical final-role lens")
        expected_path = canonical_receipt_path(feature, freeze["id"], role, lens)
        try:
            repo_relative_path(receipt["path"], f"{item_label}.path")
        except SliceproofError as exc:
            errors.extend(exc.errors)
        if receipt["path"] != expected_path:
            errors.append(f"{item_label}.path: expected canonical path {expected_path!r}")
        elif verify_files:
            validate_pointer_file(artifact_root, receipt["path"], receipt["digest"], item_label, errors)
        if receipt["freeze_digest"] != freeze["digest"]:
            errors.append(f"{item_label}.freeze_digest: must match the active freeze")


def validate_pointer_file(
    artifact_root: Path,
    path: str,
    expected_digest: str,
    label: str,
    errors: list[str],
) -> None:
    try:
        pointer_path = resolve_authority_file(artifact_root, path, f"{label}.path")
    except SliceproofError as exc:
        errors.extend(exc.errors)
        return
    if digest_bytes(pointer_path.read_bytes()) != expected_digest:
        errors.append(f"{label}.digest: does not match current file")


def technical_amendment_effective_digest(parent: str, amendment: str, artifact_sha: str) -> str:
    return canonical_json_digest({
        "artifact_sha": artifact_sha,
        "parent_effective_digest": parent,
        "technical_amendment_digest": amendment,
    })


def assurance_routing_digest(
    profile: str,
    package_modes: dict[str, str],
    package_assignments: list[dict[str, str]],
) -> str:
    return canonical_json_digest({
        "assurance_profile": profile,
        "package_modes": package_modes,
        "package_assignments": package_assignments,
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


CONTINUITY_PRESERVED_FIELDS = (
    "artifact_checkpoint",
    "code_checkpoint",
    "authorization",
    "budgets",
    "packages",
    "wave",
    "serious_clusters",
    "freeze",
    "receipts",
    "portability_authorization",
    "assurance_profile",
    "package_modes",
    "package_assignments",
)


def compare_preserved_lifecycle_fields(
    previous: dict[str, Any],
    current: dict[str, Any],
    fields: tuple[str, ...],
    transition: str,
) -> list[str]:
    errors: list[str] = []
    for field in fields:
        if field == "authorization":
            keys = ("id", "initial_digest", "effective_digest", "inputs")
            changed = any(previous[field][key] != current[field][key] for key in keys)
        else:
            changed = previous.get(field) != current.get(field)
        if changed:
            preserved = "authorization ID/inputs/digests" if field == "authorization" else field
            errors.append(f"lifecycle transition: {transition} must preserve {preserved} exactly")
    return errors


def continuity_predecessor_errors(previous: dict[str, Any], transition: str) -> list[str]:
    errors: list[str] = []
    if previous["quiescent"] is not True:
        errors.append(f"lifecycle transition: {transition} requires a quiescent predecessor checkpoint")
    if previous["budgets"]["active_reservation"] is not None:
        errors.append(f"lifecycle transition: {transition} cannot abandon an active reservation")
    if previous["budgets"]["control_plane_reserve"]["reservation"] is not None:
        errors.append(f"lifecycle transition: {transition} cannot abandon a control-plane reservation")
    wave = previous["wave"]
    if wave is not None and wave["state"] in {"reserved", "active"}:
        errors.append(f"lifecycle transition: {transition} cannot abandon reserved or active wave work")
    return errors


def compare_lifecycle_dispositions(
    previous: dict[str, Any],
    current: dict[str, Any],
    authorization_changed: bool,
) -> list[str]:
    errors: list[str] = []
    old = previous["disposition"]
    new = current["disposition"]
    if old in {"cancelled", "superseded", "completed"}:
        return [f"lifecycle transition: {old} lifecycle disposition is terminal and immutable"]
    if old == new == "active":
        return errors
    if old == "active" and new == "parked":
        errors.extend(continuity_predecessor_errors(previous, "park"))
        expected_resume = {
            "stage": previous["stage"],
            "next_legal_actions": previous["next_legal_actions"],
        }
        if current["resume"] != expected_resume:
            errors.append("lifecycle transition: park must record the exact prior resume stage and ordered actions")
        old_owner, parked_owner = previous["owner"], current["owner"]
        if (
            parked_owner["token"] != old_owner["token"]
            or parked_owner["host"] != old_owner["host"]
            or parked_owner["takeover"] != old_owner["takeover"]
            or parked_owner["disposition"] != "stopped"
        ):
            errors.append(
                "lifecycle transition: park must preserve owner token/host/takeover and stop the logical owner"
            )
        errors.extend(compare_preserved_lifecycle_fields(
            previous, current, CONTINUITY_PRESERVED_FIELDS, "park"
        ))
        return errors
    if old == "parked" and new == "active":
        expected = previous["resume"]
        if expected is None or (
            current["stage"], current["next_legal_actions"]
        ) != (expected["stage"], expected["next_legal_actions"]):
            errors.append("lifecycle transition: resume must restore only the parked stage and ordered actions")
        if current["quiescent"] is not True:
            errors.append("lifecycle transition: resume starts from the verified quiescent checkpoint")
        old_owner, resumed_owner = previous["owner"], current["owner"]
        if old_owner["disposition"] != "stopped" or resumed_owner["disposition"] != "active":
            errors.append("lifecycle transition: resume requires a stopped owner to become active")
        if resumed_owner["token"] == old_owner["token"] and (
            resumed_owner["host"] != old_owner["host"]
            or resumed_owner["takeover"] != old_owner["takeover"]
        ):
            errors.append(
                "lifecycle transition: same-owner resume must preserve exact host and prior takeover provenance"
            )
        errors.extend(compare_preserved_lifecycle_fields(
            previous, current, CONTINUITY_PRESERVED_FIELDS, "resume"
        ))
        return errors
    if new == "cancelled" and old in {"active", "parked"}:
        errors.extend(continuity_predecessor_errors(previous, "cancel"))
        if current["resume"] != previous["resume"]:
            errors.append("lifecycle transition: cancel cannot mutate the parked resume point")
        errors.extend(compare_preserved_lifecycle_fields(
            previous, current, ("owner", *CONTINUITY_PRESERVED_FIELDS), "cancel"
        ))
        return errors
    if new == "superseded" and old in {"active", "parked"}:
        errors.extend(continuity_predecessor_errors(previous, "supersede"))
        if current["resume"] != previous["resume"]:
            errors.append("lifecycle transition: supersede cannot mutate the parked resume point")
        if not authorization_changed:
            errors.append(
                "lifecycle transition: supersession mapping requires a reviewed effective-digest amendment"
            )
        preserved = (
            "owner",
            "code_checkpoint",
            "budgets",
            "wave",
            "serious_clusters",
            "freeze",
            "receipts",
            "portability_authorization",
            "assurance_profile",
        )
        errors.extend(compare_preserved_lifecycle_fields(previous, current, preserved, "supersede"))
        errors.extend(compare_supersession_packages(previous, current))
        return errors
    if old == "active" and new == "completed":
        return errors
    errors.append(f"lifecycle transition: impossible disposition change {old!r} to {new!r}")
    return errors


def compare_supersession_packages(
    previous: dict[str, Any], current: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    supersession = current["supersession"]
    if supersession is None:
        return ["lifecycle transition: supersede requires durable replacement provenance"]
    old_packages = previous["packages"]
    new_packages = current["packages"]
    old_ids = set(old_packages)
    appended_ids = set(new_packages) - old_ids
    mapping = supersession["package_map"]
    sources = {edge["source"] for edge in mapping}
    targets = {edge["target"] for edge in mapping}
    if not old_ids or not appended_ids:
        errors.append("lifecycle transition: supersede requires existing old packages and appended replacements")
    if any(source not in old_ids for source in sources):
        errors.append("lifecycle transition: replacement mapping sources must be existing old package IDs")
    if targets != appended_ids:
        errors.append("lifecycle transition: replacement mapping targets must be exactly the appended package IDs")
    for package_id in sorted(old_ids, key=package_id_order):
        old_package = old_packages[package_id]
        new_package = new_packages.get(package_id)
        if new_package is None:
            continue
        if package_id in sources:
            if new_package["state"] != "invalidated" or new_package["wave"] != old_package["wave"]:
                errors.append(
                    f"lifecycle transition: mapped old package {package_id} must remain present and become invalidated"
                )
        elif new_package != old_package:
            errors.append(f"lifecycle transition: unmapped old package {package_id} must remain unchanged")
    for package_id in sorted(appended_ids, key=package_id_order):
        if new_packages[package_id] != {"state": "pending", "wave": None}:
            errors.append(
                f"lifecycle transition: appended replacement {package_id} must start pending without completion inference"
            )
    old_modes = previous.get("package_modes", {})
    new_modes = current.get("package_modes", {})
    if any(new_modes.get(package_id) != mode for package_id, mode in old_modes.items()):
        errors.append("lifecycle transition: supersede cannot rewrite old package routing")
    old_assignments = {
        item["package"]: item for item in previous.get("package_assignments", [])
    }
    new_assignments = {
        item["package"]: item for item in current.get("package_assignments", [])
    }
    if any(new_assignments.get(package_id) != assignment for package_id, assignment in old_assignments.items()):
        errors.append("lifecycle transition: supersede cannot rewrite old package assignments")
    return errors


def compare_immutable_package_ids(
    previous: dict[str, Any],
    current: dict[str, Any],
    previous_authorized: bool,
    authorization_changed: bool,
) -> list[str]:
    old_ids = set(previous["packages"])
    new_ids = set(current["packages"])
    errors: list[str] = []
    removed = sorted(old_ids - new_ids, key=package_id_order)
    if removed:
        errors.append(f"lifecycle transition: immutable package IDs cannot be removed or renumbered; missing {removed}")
    appended = sorted(new_ids - old_ids, key=package_id_order)
    if appended:
        if previous_authorized and not authorization_changed:
            errors.append("lifecycle transition: package append requires a reviewed effective-digest amendment")
        start = max((package_id_order(package_id) for package_id in old_ids), default=0) + 1
        expected = [f"WP{number}" for number in range(start, start + len(appended))]
        if appended != expected:
            errors.append(
                f"lifecycle transition: new package IDs must append contiguously above prior IDs; expected {expected}"
            )
        if any(current["packages"][package_id]["state"] != "pending" for package_id in appended):
            errors.append("lifecycle transition: appended package IDs must start pending without completion inference")
    old_map = (
        previous["supersession"]["package_map"]
        if previous.get("supersession") is not None else []
    )
    new_map = (
        current["supersession"]["package_map"]
        if current.get("supersession") is not None else []
    )
    if old_map and new_map[:len(old_map)] != old_map:
        errors.append("lifecycle transition: replacement mapping is monotonic and cannot mutate or reset")
    if old_map != new_map and previous_authorized and not authorization_changed:
        errors.append("lifecycle transition: replacement mapping change requires a reviewed effective-digest amendment")
    return errors


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
            and takeover.get("evidence_digest") == canonical_json_digest(previous)
        )
        if not valid_takeover:
            errors.append(
                "lifecycle transition: owner/host change requires exact stopped-owner takeover provenance "
                "bound to the predecessor evidence digest"
            )

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
    elif current_authorized:
        if (
            current_auth["effective_digest"] != current_auth["initial_digest"]
            or current_auth.get("amendment_link") is not None
        ):
            errors.append("lifecycle transition: initial authorization must start at its initial digest without amendment history")
        if current_auth["inputs"]["artifact_commit"] != current["last_verified"]["artifact_sha"]:
            errors.append(
                "lifecycle transition: initial authorization artifact_commit must match the exact reviewed predecessor candidate"
            )
        introduced_non_pending = sorted(
            package_id
            for package_id, package_state in current["packages"].items()
            if package_state["state"] != "pending"
        )
        if introduced_non_pending:
            errors.append(
                "lifecycle transition: initial authorization must introduce every package in pending state; "
                f"got non-pending packages {introduced_non_pending}"
            )

    errors.extend(compare_lifecycle_dispositions(previous, current, authorization_changed))
    errors.extend(compare_lifecycle_budgets(previous["budgets"], current["budgets"]))
    previous_packages, current_packages = previous["packages"], current["packages"]
    errors.extend(compare_immutable_package_ids(
        previous, current, previous_authorized, authorization_changed
    ))
    if previous_authorized and not authorization_changed and set(previous_packages) != set(current_packages):
        errors.append("lifecycle transition: authorized package membership changed without technical amendment")
    errors.extend(compare_package_states(previous_packages, current_packages, authorization_changed))
    errors.extend(compare_assurance_routing(previous, current, previous_authorized, authorization_changed))

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
    for cluster_id in sorted(set(current_clusters) - set(previous_clusters)):
        new_cluster = current_clusters[cluster_id]
        if new_cluster["strikes"] != 1:
            errors.append(f"lifecycle transition: new serious cluster {cluster_id} must start at strike 1")
        if new_cluster["route"] == "closure-repair" and (
            new_cluster["disposition"] != "repair-eligible"
            or new_cluster["repair"] is not None
            or new_cluster["closure"] is not None
        ):
            errors.append(
                f"lifecycle transition: new eligible serious cluster {cluster_id} starts with exactly one repair authorization"
            )
    for cluster_id, old in previous_clusters.items():
        new = current_clusters.get(cluster_id)
        if new is None:
            errors.append(f"lifecycle transition: serious cluster {cluster_id} cannot disappear")
            continue
        for field in ("accepted_invariant", "root_mechanism", "architectural_surface"):
            if new[field] != old[field]:
                errors.append(f"lifecycle transition: serious cluster {cluster_id} canonical identity is immutable")
        if new["observed_signatures"][:len(old["observed_signatures"])] != old["observed_signatures"]:
            errors.append(f"lifecycle transition: serious cluster {cluster_id} observed signatures are append-only")
        if new["observed_classes"][:len(old["observed_classes"])] != old["observed_classes"]:
            errors.append(f"lifecycle transition: serious cluster {cluster_id} observed classes are append-only")
        if new["strikes"] < old["strikes"]:
            errors.append(f"lifecycle transition: serious cluster {cluster_id} strikes cannot decrease")
        if old["repair"] is not None and new["repair"] != old["repair"]:
            errors.append(f"lifecycle transition: serious cluster {cluster_id} has exactly one immutable repair")
        if old["closure"] is not None and new["closure"] != old["closure"]:
            errors.append(f"lifecycle transition: serious cluster {cluster_id} has exactly one immutable closure")
        if old["disposition"] in {"closed", "circuit-open"} and new != old:
            errors.append(
                f"lifecycle transition: serious cluster {cluster_id} terminal disposition is immutable; terminal lineage cannot change"
            )

    old_freeze, new_freeze = previous["freeze"], current["freeze"]
    if old_freeze is not None and new_freeze is None:
        errors.append("lifecycle transition: freeze pointer cannot disappear")
    elif old_freeze is not None and new_freeze is not None and old_freeze["id"] == new_freeze["id"]:
        if old_freeze != new_freeze:
            errors.append("lifecycle transition: same-freeze pointer cannot mutate")
        old_receipts = {(item["role"], item["lens"]): item for item in previous["receipts"]}
        new_receipts = {(item["role"], item["lens"]): item for item in current["receipts"]}
        for key, old in old_receipts.items():
            if new_receipts.get(key) != old:
                errors.append(f"lifecycle transition: receipt pointer {key!r} cannot mutate under the same freeze")
    elif old_freeze is not None and new_freeze is not None and old_freeze["path"] == new_freeze["path"]:
        errors.append("lifecycle transition: a new freeze requires a new canonical path")

    errors.extend(validate_role_call_consumption_transition(previous, current))

    control_reservation = current["budgets"]["control_plane_reserve"]["reservation"]
    if control_reservation is not None:
        operation = control_reservation["operation"]
        preserved_fields = (
            "artifact_checkpoint", "code_checkpoint", "authorization", "packages", "wave",
            "serious_clusters", "freeze", "receipts", "assurance_profile", "package_modes",
            "package_assignments",
        )
        if any(current.get(field) != previous.get(field) for field in preserved_fields):
            errors.append(
                f"lifecycle transition: {operation} control-only escalation cannot mutate semantic/checkpoint state"
            )
        if (
            any(
                current["budgets"][name] != previous["budgets"][name]
                for name in ("preauthorization", "implementation")
            )
            or current["budgets"]["role_call_consumption"]
            != previous["budgets"]["role_call_consumption"]
        ):
            errors.append(
                f"lifecycle transition: {operation} control-only escalation cannot issue or mutate semantic budgets"
            )
        if operation == "safe-checkpoint":
            if current["owner"] != previous["owner"] or current["owner"]["disposition"] != "active":
                errors.append(
                    "lifecycle transition: safe-checkpoint escalation must preserve the exact active owner"
                )
        elif current["owner"] != previous["owner"]:
            errors.append("lifecycle transition: last-verified escalation cannot mutate ownership or take over")
        if (
            control_reservation["reason"] in {"ownership-unavailable", "cas-unavailable"}
            and current["owner"] != previous["owner"]
        ):
            errors.append(
                "lifecycle transition: ownership/CAS-unavailable escalation cannot take over ownership"
            )
    return errors


def compare_assurance_routing(
    previous: dict[str, Any],
    current: dict[str, Any],
    previous_authorized: bool,
    authorization_changed: bool,
) -> list[str]:
    if not previous_authorized:
        return []
    old_profile = previous.get("assurance_profile")
    new_profile = current.get("assurance_profile")
    old_modes = previous.get("package_modes", {})
    new_modes = current.get("package_modes", {})
    old_assignments = {
        item["package"]: item for item in previous.get("package_assignments", [])
    }
    new_assignments = {
        item["package"]: item for item in current.get("package_assignments", [])
    }
    profile_changed = old_profile != new_profile
    changed_mode_ids = {
        package_id
        for package_id in set(old_modes) | set(new_modes)
        if old_modes.get(package_id) != new_modes.get(package_id)
    }
    changed_assignment_ids = {
        package_id
        for package_id in set(old_assignments) | set(new_assignments)
        if old_assignments.get(package_id) != new_assignments.get(package_id)
    }
    if not profile_changed and not changed_mode_ids and not changed_assignment_ids:
        return []

    errors: list[str] = []
    if (
        profile_changed
        and old_profile in ASSURANCE_PROFILE_RANK
        and new_profile in ASSURANCE_PROFILE_RANK
        and ASSURANCE_PROFILE_RANK[new_profile] < ASSURANCE_PROFILE_RANK[old_profile]
    ):
        errors.append(
            "lifecycle transition: assurance profile downgrade is forbidden under the existing authorization "
            "lineage; it requires a fresh reviewed baseline and new user authorization"
        )
    if not authorization_changed:
        if profile_changed:
            direction = "changed"
            if old_profile in ASSURANCE_PROFILE_RANK and new_profile in ASSURANCE_PROFILE_RANK:
                direction = (
                    "promotion"
                    if ASSURANCE_PROFILE_RANK[new_profile] > ASSURANCE_PROFILE_RANK[old_profile]
                    else "downgrade"
                )
            errors.append(
                f"lifecycle transition: assurance profile {direction} requires a reviewed effective-digest amendment"
            )
        if changed_mode_ids:
            errors.append(
                "lifecycle transition: package verification mode change requires a reviewed effective-digest amendment"
            )
        if changed_assignment_ids:
            errors.append(
                "lifecycle transition: package assurance assignment change requires a reviewed "
                "effective-digest amendment"
            )
        return errors

    affected = (
        set(previous.get("packages", {}))
        if profile_changed
        else changed_mode_ids | changed_assignment_ids
    )
    for package_id in sorted(affected & set(previous.get("packages", {})) & set(current.get("packages", {}))):
        old_state = previous["packages"][package_id]["state"]
        new_state = current["packages"][package_id]["state"]
        if old_state in ROUTING_CANDIDATE_STATES and new_state != "invalidated":
            errors.append(
                f"lifecycle transition: routing change must invalidate existing candidate for {package_id}; "
                f"got {old_state} to {new_state}"
            )
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


def validate_continuity_transition_paths(
    artifact_root: Path,
    code_root: Path,
    previous_commit: str,
    lifecycle_path: str,
    previous: dict[str, Any],
    current: dict[str, Any],
) -> list[str]:
    old, new = previous["disposition"], current["disposition"]
    transition = None
    if old == "active" and new == "parked":
        transition = "park"
    elif old == "parked" and new == "active":
        transition = "resume"
    elif old in {"active", "parked"} and new == "cancelled":
        transition = "cancel"
    if transition is None:
        return []

    label = f"lifecycle transition: {transition} continuity checkpoint"
    errors: list[str] = []
    try:
        changed_output = git_output(
            artifact_root,
            ["diff", "--name-only", "--no-renames", previous_commit, "--"],
            label,
        )
        untracked_output = git_output(
            artifact_root,
            ["ls-files", "--others", "--exclude-standard"],
            label,
        )
    except SliceproofError as exc:
        return exc.errors
    changed = {path for path in changed_output.splitlines() if path}
    changed.update(path for path in untracked_output.splitlines() if path)
    if changed != {lifecycle_path}:
        errors.append(
            f"{label} may change only {lifecycle_path}; observed paths {sorted(changed)}"
        )
    try:
        status = git_output(
            code_root,
            ["status", "--porcelain=v1", "--untracked-files=all"],
            label,
        )
    except SliceproofError as exc:
        errors.extend(exc.errors)
    else:
        if status:
            errors.append(f"{label} requires a clean code root; later local files are untrusted")
    checkpoint = current["code_checkpoint"]
    if checkpoint is not None:
        errors.extend(validate_worktree_head_and_clean(
            code_root,
            checkpoint["sha"],
            f"{label}: exact referenced code checkpoint",
        ))
    return errors


def validate_control_only_transition_paths(
    artifact_root: Path,
    code_root: Path,
    previous_commit: str,
    lifecycle_path: str,
    state: dict[str, Any],
) -> list[str]:
    reservation = state["budgets"]["control_plane_reserve"]["reservation"]
    if reservation is None:
        return []
    label = f"lifecycle transition: {reservation['operation']} control-only escalation"
    errors: list[str] = []
    try:
        changed_output = git_output(
            artifact_root,
            ["diff", "--name-only", "--no-renames", previous_commit, "--"],
            label,
        )
        untracked_output = git_output(
            artifact_root,
            ["ls-files", "--others"],
            label,
        )
    except SliceproofError as exc:
        return exc.errors
    changed = {path for path in changed_output.splitlines() if path}
    changed.update(path for path in untracked_output.splitlines() if path)
    unexpected = sorted(changed - {lifecycle_path})
    if unexpected:
        errors.append(
            f"{label} may change only {lifecycle_path}; unexpected changed paths {unexpected}"
        )
    if lifecycle_path not in changed:
        errors.append(f"{label} must change only the derived Lifecycle State path")

    try:
        code_status = git_output(
            code_root,
            ["status", "--porcelain=v1", "--untracked-files=all"],
            label,
        )
    except SliceproofError as exc:
        errors.extend(exc.errors)
    else:
        if code_status:
            errors.append(f"{label} cannot progress code or code-root evidence")
    checkpoint = state.get("code_checkpoint")
    if checkpoint is not None:
        errors.extend(validate_worktree_head_and_clean(
            code_root,
            checkpoint["sha"],
            f"{label}: code checkpoint",
        ))
    return errors


def validate_assurance_paths_append_only(
    artifact_root: Path, feature: str, previous_commit: str
) -> list[str]:
    pathspec = f".tasks/{feature}/assurance"
    try:
        changed = git_output(
            artifact_root,
            ["diff", "--name-status", "--no-renames", previous_commit, "--", pathspec],
            "lifecycle transition: freeze-scoped paths",
        )
    except SliceproofError as exc:
        return exc.errors
    errors: list[str] = []
    for line in changed.splitlines():
        fields = line.split("\t", 1)
        if len(fields) != 2 or fields[0] != "A":
            errors.append(
                "lifecycle transition: freeze-scoped files are append-only across freezes; "
                f"observed {line!r}"
            )
    return errors


def validate_new_assurance_pointer_paths(
    artifact_root: Path,
    previous_commit: str,
    previous: dict[str, Any],
    current: dict[str, Any],
) -> list[str]:
    candidates: list[str] = []
    old_freeze, new_freeze = previous["freeze"], current["freeze"]
    if new_freeze is not None and (old_freeze is None or new_freeze["id"] != old_freeze["id"]):
        candidates.append(new_freeze["path"])
    old_nodes = {
        (item["role"], item["lens"]): item["path"] for item in previous["receipts"]
    }
    candidates.extend(
        item["path"] for item in current["receipts"]
        if old_nodes.get((item["role"], item["lens"])) != item["path"]
    )
    errors: list[str] = []
    for path in sorted(set(candidates)):
        try:
            existing = git_output(
                artifact_root,
                ["ls-tree", previous_commit, "--", path],
                "lifecycle transition: new freeze-scoped path",
            ).strip()
        except SliceproofError as exc:
            errors.extend(exc.errors)
            continue
        if existing:
            errors.append(
                f"lifecycle transition: new freeze/receipt pointer cannot reuse prior path {path!r}"
            )
    return errors


def validate_role_call_consumption_transition(
    previous: dict[str, Any],
    current: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    previous_consumption = previous["budgets"]["role_call_consumption"]
    current_consumption = current["budgets"]["role_call_consumption"]
    previous_implementation = previous["budgets"].get("implementation")
    previous_issued = (
        previous_implementation["issued"] if previous_implementation is not None else {}
    )

    previous_freeze = previous["freeze"]
    current_freeze = current["freeze"]
    same_freeze = (
        previous_freeze is not None
        and current_freeze is not None
        and previous_freeze["id"] == current_freeze["id"]
    )
    previous_nodes = (
        {(receipt["role"], receipt["lens"]) for receipt in previous["receipts"]}
        if same_freeze
        else set()
    )
    added_receipts = {role: 0 for role in FINAL_ASSURANCE_CALL_COUNTERS}
    for receipt in current["receipts"]:
        role = receipt["role"]
        if role in added_receipts and (role, receipt["lens"]) not in previous_nodes:
            added_receipts[role] += 1

    for role, counter in FINAL_ASSURANCE_CALL_COUNTERS.items():
        old_consumed = previous_consumption[role]
        new_consumed = current_consumption[role]
        if new_consumed < old_consumed:
            errors.append(
                f"lifecycle transition: role_call_consumption.{role} cannot decrease"
            )
            continue
        consumed_delta = new_consumed - old_consumed
        if consumed_delta and new_consumed > previous_issued.get(counter, 0):
            errors.append(
                f"lifecycle transition: role_call_consumption.{role}={new_consumed} exceeds "
                f"predecessor-issued {counter}={previous_issued.get(counter, 0)}"
            )
        if added_receipts[role] > consumed_delta:
            errors.append(
                f"lifecycle transition: {added_receipts[role]} new {role} receipt(s) require matching "
                f"new role-call consumption after predecessor issuance; delta is {consumed_delta}"
            )
    return errors


def checkpoint_ref_generation(ref: str) -> int:
    return int(ref.rsplit("/g", 1)[1])


def immutable_checkpoint_ref_generation(ref: str, feature: str) -> int | None:
    match = re.fullmatch(
        rf"refs/heads/checkpoints/{re.escape(feature)}/[A-Za-z0-9][A-Za-z0-9-]*/g([1-9]\d*)",
        ref,
    )
    return None if match is None else int(match.group(1))


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
    old_control_reservation = old_control.get("reservation")
    new_control_reservation = new_control.get("reservation")
    if (
        old_control_reservation is not None
        and new_control_reservation is not None
        and old_control_reservation["id"] == new_control_reservation["id"]
        and old_control_reservation != new_control_reservation
    ):
        errors.append("lifecycle transition: control-plane reservation cannot mutate under the same id")
    if old_control_reservation is None and new_control_reservation is not None:
        if new_control["issued"] - old_control["issued"] != 1:
            errors.append("lifecycle transition: control-plane reservation must consume the one issued unit")

    old_reservation, new_reservation = previous.get("active_reservation"), current.get("active_reservation")
    new_reservation_created = new_reservation is not None and (
        old_reservation is None or old_reservation["id"] != new_reservation["id"]
    )
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

    old_implementation = previous.get("implementation")
    new_implementation = current.get("implementation")
    old_role_issued = old_implementation["issued"] if old_implementation is not None else {}
    new_role_issued = new_implementation["issued"] if new_implementation is not None else {}
    role_deltas = {
        counter: new_role_issued.get(counter, 0) - old_role_issued.get(counter, 0)
        for counter in ROLE_SCOPED_CALL_COUNTERS
    }
    positive_role_deltas = {
        counter: delta for counter, delta in role_deltas.items() if delta > 0
    }
    if positive_role_deltas:
        matching_reservation = (
            new_reservation_created
            and new_reservation is not None
            and new_reservation["budget"] == "implementation"
        )
        if not matching_reservation:
            errors.append(
                "lifecycle transition: positive role-call issued delta requires a newly created "
                "matching implementation reservation"
            )
        else:
            units = new_reservation["units"]
            for counter, delta in positive_role_deltas.items():
                if units.get(counter, 0) != delta:
                    errors.append(
                        f"lifecycle transition: new reservation {counter} units must exactly match "
                        f"issued delta {delta}"
                    )
            role_delta_total = sum(positive_role_deltas.values())
            if units.get("delegated_calls", 0) < role_delta_total:
                errors.append(
                    "lifecycle transition: new role-call reservation must charge delegated_calls "
                    "by at least the role delta sum"
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


def git_output_bytes(root: Path, args: list[str], label: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError as exc:
        raise SliceproofError([f"{label}: unable to invoke local git: {exc}"])
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).decode("utf-8", errors="replace").strip()
        raise SliceproofError([f"{label}: local git inspection failed: {detail or f'exit {result.returncode}'}"])
    return result.stdout


def raw_git_diff_identity(root: Path, base_commit: str, candidate_commit: str, label: str) -> str:
    raw = git_output_bytes(
        root,
        [
            "diff", "--raw", "--no-renames", "--no-ext-diff", "--no-textconv", "--no-abbrev", "-z",
            base_commit, candidate_commit, "--",
        ],
        label,
    )
    return digest_bytes(raw)


def git_head_or_none(root: Path) -> str | None:
    result = git_process(root, ["rev-parse", "--verify", "HEAD"], "validate-lifecycle-state")
    if result.returncode == 0:
        return result.stdout.strip()
    if result.returncode == 128 and "needed a single revision" in result.stderr.lower():
        return None
    raise SliceproofError([
        f"validate-lifecycle-state: unable to inspect artifact HEAD: {result.stderr.strip()}"
    ])


def require_exact_git_root(
    root: Path,
    label: str,
    *,
    command: str = "validate-lifecycle-state",
) -> None:
    top = git_output(root, ["rev-parse", "--show-toplevel"], f"{command}: {label}").strip()
    if Path(top).resolve(strict=False) != root:
        raise SliceproofError([f"{command}: {label} must equal its own exact Git worktree root"])


def git_common_dir(root: Path, label: str) -> Path:
    value = git_output(root, ["rev-parse", "--path-format=absolute", "--git-common-dir"], label).strip()
    return Path(value).resolve(strict=False)


def require_git_commit(root: Path, sha: str, label: str, errors: list[str]) -> None:
    try:
        actual = git_output(root, ["rev-parse", f"{sha}^{{commit}}"], label).strip()
    except SliceproofError as exc:
        errors.extend(exc.errors)
        return
    if actual != sha:
        errors.append(f"{label}: does not resolve to the exact named commit")


def require_git_ref_at_commit(
    root: Path,
    ref: str,
    sha: str,
    label: str,
    errors: list[str],
) -> None:
    symbolic = git_process(root, ["symbolic-ref", "-q", ref], label)
    if symbolic.returncode == 0:
        errors.append(f"{label}: must be a direct ref; symbolic refs are forbidden")
    elif symbolic.returncode != 1:
        detail = symbolic.stderr.strip() or symbolic.stdout.strip() or f"exit {symbolic.returncode}"
        errors.append(f"{label}: direct-ref inspection failed: {detail}")

    direct = git_process(root, ["show-ref", "--verify", "--hash", ref], label)
    if direct.returncode != 0:
        detail = direct.stderr.strip() or direct.stdout.strip() or f"exit {direct.returncode}"
        errors.append(f"{label}: exact direct ref is missing or unreadable: {detail}")
    elif direct.stdout.strip() != sha:
        errors.append(f"{label}: must resolve locally to the exact checkpoint sha as a direct ref")

    require_git_commit(root, sha, f"{label}: bound sha", errors)


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


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"\n"


def canonical_json_digest(value: Any) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def cmd_validate_plan(args: argparse.Namespace) -> dict[str, Any]:
    require_planned_cli_roots(args)
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
        },
        "packages": [package.package_id for package in registry.packages],
        "validated_package_markdown": sorted(packages),
        "validated_slices": sorted(registry.authoritative_slices),
    }


def cmd_create_proof(args: argparse.Namespace) -> dict[str, Any]:
    require_planned_cli_roots(args)
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
    require_planned_cli_roots(args)
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
    require_planned_cli_roots(args)
    state = load_package_state(args.tasks, args.package, artifact_root=args.artifact_root, code_root=args.code_root)
    errors = validate_proof_markdown(state.proof_path, state.package_md)
    dependency_result = validate_direct_dependency_unlocks(state)
    errors.extend(dependency_result.errors)
    advisories = list(dependency_result.advisories)
    report_result = ReportValidationResult([], [])
    if state.package.verification_mode == "boundary":
        if state.report_path is None:
            errors.append(f"work_packages[{state.package.package_id}].report_path: boundary report is required")
        else:
            report_result = validate_report_markdown(
                state.report_path,
                state.registry,
                state.package,
                state.package_md,
                state.proof_path,
            )
            errors.extend(report_result.errors)
            advisories.extend(report_result.advisories)
    else:
        errors.extend(validate_final_report_absence(state.registry, state.package))
        errors.extend(validate_controlled_stable_candidate(
            state.registry,
            state.package,
            candidate_commit=None,
            label="validate-package-complete",
        ))
    if errors:
        raise SliceproofError(errors, advisories)
    return {
        "package": state.package.package_id,
        "package_status": state.package.status,
        "assurance_profile": state.registry.assurance_profile,
        "verification_mode": state.package.verification_mode,
        "proof_path": state.package.proof_path,
        "report_path": state.package.report_path,
        "boundary_receipt_validated": state.package.verification_mode == "boundary",
        "direct_final_deferral_validated": state.package.verification_mode == "final",
        "post_freeze_assurance_validated": False,
        "required_slice_rows": state.package_md.must_satisfy_ids,
        "verification_expectation_rows": [f"VE-{index}" for index in range(1, len(state.package_md.verification_expectations) + 1)],
        "advisories": advisories,
    }


def cmd_emit_state_binding(args: argparse.Namespace) -> RawText:
    require_planned_cli_roots(args)
    state = load_package_state(args.tasks, args.package, artifact_root=args.artifact_root, code_root=args.code_root)
    if state.package.verification_mode != "boundary":
        raise SliceproofError([
            "emit-state-binding: final packages have no package report; substitute State Binding is invalid"
        ])
    candidate, candidate_errors = candidate_binding_from_cli(state.registry, state.package, args)
    runtime_errors = validate_state_binding_runtime_metadata(
        "emit-state-binding",
        args.worktree,
        args.git_ref,
        args.verified_at,
    )
    errors = [*candidate_errors, *runtime_errors]
    if errors or candidate is None:
        raise SliceproofError(errors or ["emit-state-binding: invalid candidate binding inputs"])
    values = state_binding_values(
        state.registry.root,
        state.package,
        state.package_md,
        state.proof_path,
        candidate=candidate,
        worktree=args.worktree,
        git_ref=args.git_ref,
        verified_at=args.verified_at,
    )
    return RawText(render_state_binding_block(values))


def cmd_validate_final(args: argparse.Namespace) -> dict[str, Any]:
    require_planned_cli_roots(args)
    registry, packages = load_and_validate_plan(args.tasks, artifact_root=args.artifact_root, code_root=args.code_root)
    errors: list[str] = validate_controlled_integration_checkpoint(registry, "validate-final")
    advisories: list[dict[str, Any]] = []
    validated_reports: list[str] = []
    final_deferrals: list[str] = []
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
        errors.extend(validate_proof_markdown(proof_path, package_md))
        if package.verification_mode == "boundary":
            if package.report_path is None:
                errors.append(f"work_packages[{package.package_id}].report_path: boundary report is required")
                continue
            report_path = resolve_safe_path(
                registry.root,
                package.report_path,
                f"work_packages[{package.package_id}].report_path",
                expected_suffix=".package-verification.md",
                root_label="artifact root",
            )
            report_result = validate_report_markdown(
                report_path,
                registry,
                package,
                package_md,
                proof_path,
                final_validation=True,
            )
            advisories.extend(report_result.advisories)
            if not report_result.errors:
                validated_reports.append(package.report_path)
            errors.extend(report_result.errors)
        else:
            final_errors = validate_final_report_absence(registry, package)
            final_errors.extend(validate_controlled_stable_candidate(
                registry,
                package,
                candidate_commit=None,
                label="validate-final",
                require_done=True,
            ))
            if not final_errors:
                final_deferrals.append(package.package_id)
            errors.extend(final_errors)
    if errors:
        raise SliceproofError(errors, advisories)
    return {
        "feature": registry.feature,
        "assurance_profile": registry.assurance_profile,
        "packages": [package.package_id for package in registry.packages],
        "proofs_validated": [package.proof_path for package in registry.packages],
        "boundary_reports_validated": validated_reports,
        "final_deferrals_validated": final_deferrals,
        "pre_freeze_package_equation_validated": True,
        "post_freeze_assurance_validated": False,
        "advisories": advisories,
    }


def cmd_validate_agentic_completion(args: argparse.Namespace) -> dict[str, Any]:
    artifact_root, code_root = require_planned_cli_roots(args)
    if not FEATURE_RE.fullmatch(args.feature):
        raise SliceproofError(["--feature: expected lowercase slug with letters, digits, and hyphens"])
    state_relative = f".tasks/{args.feature}/lifecycle-state.json"
    state_path = resolve_authority_file(artifact_root, state_relative, "Lifecycle State")
    state = load_strict_json_file(state_path, "Lifecycle State")
    if not isinstance(state, dict):
        raise SliceproofError(["Lifecycle State: root must be an object"])
    generation, previous_commit, _previous_digest = validate_lifecycle_transition_authority(
        state,
        artifact_root=artifact_root,
        code_root=code_root,
        feature=args.feature,
        relative_path=state_relative,
        previous_commit=None,
        infer_previous=True,
    )

    prefreeze = cmd_validate_final(argparse.Namespace(
        command="validate-final",
        tasks=Path(f".tasks/{args.feature}/tasks.json"),
        artifact_root=artifact_root,
        code_root=code_root,
    ))
    registry, package_markdowns = load_and_validate_plan(
        Path(f".tasks/{args.feature}/tasks.json"),
        artifact_root=artifact_root,
        code_root=code_root,
    )
    errors, result = validate_agentic_completion_data(
        state,
        registry=registry,
        artifact_root=artifact_root,
        code_root=code_root,
        state_relative=state_relative,
        package_markdowns=package_markdowns,
    )
    if errors:
        raise SliceproofError(errors, prefreeze.get("advisories", []))
    return {
        "artifact_root": str(artifact_root),
        "code_root": str(code_root),
        "feature": args.feature,
        "schema_version": state["schema_version"],
        "generation": generation,
        "previous_commit": previous_commit,
        "profile": state["assurance_profile"],
        "freeze": result["freeze"],
        "lifecycle_artifact_checkpoint": result["lifecycle_artifact_checkpoint"],
        "verification_summary_checkpoint": result["verification_summary_checkpoint"],
        "code_checkpoint": result["code_checkpoint"],
        "receipts": result["receipts"],
        "completion_timestamp": result["completion_timestamp"],
        "semantic_artifact_count": result["semantic_artifact_count"],
        "pre_freeze_package_equation_validated": True,
        "post_freeze_assurance_validated": True,
        "advisories": prefreeze.get("advisories", []),
    }


def validate_agentic_completion_data(
    state: dict[str, Any],
    *,
    registry: Registry,
    artifact_root: Path,
    code_root: Path,
    state_relative: str,
    package_markdowns: dict[str, PackageMarkdown],
) -> tuple[list[str], dict[str, Any]]:
    label = "validate-agentic-completion"
    errors: list[str] = []
    if state["stage"] != "completed" or state["disposition"] != "completed":
        errors.append(f"{label}: Lifecycle State stage/disposition must be 'completed'")
    if state["quiescent"] is not True:
        errors.append(f"{label}: completed state must be quiescent")
    if state["next_legal_actions"]:
        errors.append(f"{label}: completed state cannot name a next lifecycle action")
    if state["budgets"]["active_reservation"] is not None:
        errors.append(f"{label}: completion cannot retain an active semantic reservation")
    if state["budgets"]["control_plane_reserve"]["reservation"] is not None:
        errors.append(f"{label}: completion cannot be an escalation reservation")
    if state["wave"] is not None and state["wave"]["state"] != "completed":
        errors.append(f"{label}: completion cannot retain an active or blocked wave")
    incomplete = sorted(
        package_id for package_id, package in state["packages"].items()
        if package["state"] != "done"
    )
    if incomplete:
        errors.append(f"{label}: all lifecycle packages must be done; incomplete {incomplete}")
    open_clusters = sorted(
        cluster["id"] for cluster in state["serious_clusters"]
        if cluster["disposition"] != "closed"
    )
    if open_clusters:
        errors.append(f"{label}: serious clusters must be closed with no open circuit; open {open_clusters}")

    freeze_pointer = state["freeze"]
    if freeze_pointer is None:
        errors.append(f"{label}: completed state requires an immutable freeze pointer")
        return errors, {}
    freeze = load_canonical_assurance_json(
        artifact_root, freeze_pointer["path"], "freeze F", errors
    )
    if freeze is None:
        return errors, {}
    validate_json_shape(freeze, FREEZE_FILE_SCHEMA, "freeze F", errors)
    if errors:
        return errors, {}
    if freeze_pointer["digest"] != digest_bytes(canonical_json_bytes(freeze)):
        errors.append(f"{label}: Lifecycle State freeze digest does not bind canonical F")
    if freeze["id"] != freeze_pointer["id"]:
        errors.append(f"{label}: freeze id does not match Lifecycle State pointer")

    authorization = state["authorization"]
    if freeze["authorization"] != {
        "id": authorization["id"], "effective_digest": authorization["effective_digest"]
    }:
        errors.append(f"{label}: freeze authorization lineage does not match Lifecycle State")
    assurance = freeze["assurance"]
    if assurance["profile"] != state["assurance_profile"]:
        errors.append(f"{label}: freeze profile does not match Lifecycle State")
    if assurance["package_modes"] != state["package_modes"]:
        errors.append(f"{label}: freeze package modes do not match Lifecycle State")
    markdown_assignments = expected_package_assurance_assignments(registry, package_markdowns)
    controlled_assignments = state["package_assignments"]
    if markdown_assignments != controlled_assignments:
        errors.append(
            f"{label}: current package Markdown assignments do not match controlled Lifecycle State"
        )
    if assurance["package_assignments"] != controlled_assignments:
        errors.append(
            f"{label}: freeze package assignments must exactly match controlled Lifecycle State"
        )
    boundary_lenses = {
        item["lens"] for item in controlled_assignments if item["side"] == "pre-freeze"
    }
    planned_specialist_lenses = planned_final_specialist_lenses(controlled_assignments)
    if assurance["specialist_lenses"] != planned_specialist_lenses:
        errors.append(
            f"{label}: final specialist lenses must exactly equal planned high final owner S assignments"
        )
    post_freeze_lenses = set(FIXED_RECEIPT_LENSES.values()) | set(assurance["specialist_lenses"])
    overlap = sorted(boundary_lenses & post_freeze_lenses)
    if overlap:
        errors.append(f"{label}: assurance lens cannot appear on both sides of F: {overlap}")

    manifest, manifest_errors = expected_semantic_artifact_manifest(registry)
    errors.extend(manifest_errors)
    if freeze["semantic_artifacts"] != manifest:
        errors.append(
            f"{label}: freeze semantic artifact manifest must exactly bind SPEC/registry/packages/proofs/"
            "boundary reports/Slices and exclude Lifecycle State/post-freeze outputs"
        )
    boundary_receipts = expected_boundary_receipts(registry, errors)
    if assurance["required_boundary_receipts"] != boundary_receipts:
        errors.append(f"{label}: freeze required B[*] pointers do not match boundary package routing")
    post_paths = {receipt["path"] for receipt in state["receipts"]}
    if any(item["path"] in post_paths for item in assurance["required_boundary_receipts"]):
        errors.append(f"{label}: a receipt role cannot appear on both sides of F")

    validate_freeze_artifact_digests(
        artifact_root,
        freeze["runtime_evidence"],
        "freeze F.runtime_evidence",
        errors,
        require_nonempty=False,
    )
    validate_freeze_artifact_digests(
        artifact_root,
        freeze["command_results"],
        "freeze F.command_results",
        errors,
        require_nonempty=True,
    )
    evidence_paths = [item["path"] for item in freeze["runtime_evidence"]]
    command_paths = [item["path"] for item in freeze["command_results"]]
    semantic_paths = {item["path"] for item in freeze["semantic_artifacts"]}
    if set(evidence_paths) & set(command_paths):
        errors.append(f"{label}: runtime evidence and command-result paths must have one canonical owner")
    if semantic_paths & (set(evidence_paths) | set(command_paths)):
        errors.append(f"{label}: semantic artifacts and execution outputs must have distinct manifest roles")
    if freeze["serious_clusters_digest"] != canonical_json_digest(state["serious_clusters"]):
        errors.append(f"{label}: freeze serious cluster digest does not match terminal cluster state")

    code = freeze["code"]
    validate_completion_code_identity(state, code, code_root, errors)
    frozen_at = parse_aware_iso8601(freeze["frozen_at"], "freeze F.frozen_at", errors)
    graph, completion_at = validate_completion_receipt_graph(
        state,
        freeze,
        artifact_root,
        frozen_at,
        errors,
    )
    implementation_budget = state["budgets"]["implementation"]
    if implementation_budget is None:
        errors.append(f"{label}: finite implementation budget is required")
    else:
        issued = implementation_budget["issued"]
        if freeze["command_results"] and issued["command_units"] < 1:
            errors.append(f"{label}: bound command results must consume finite implementation command units")
        exact_graph_calls = {
            counter: sum(item["role"] == role for item in state["receipts"])
            for role, counter in FINAL_ASSURANCE_CALL_COUNTERS.items()
        }
        for counter, required_calls in exact_graph_calls.items():
            if issued[counter] < required_calls:
                errors.append(
                    f"{label}: implementation issued {counter} must cover the exact final receipt graph "
                    f"({issued[counter]} issued, {required_calls} required)"
                )
        role_calls_issued = sum(issued[counter] for counter in exact_graph_calls)
        if issued["delegated_calls"] < role_calls_issued:
            errors.append(
                f"{label}: total delegated_calls must cover all issued role-scoped assurance calls; "
                "one call cannot authorize multiple C/R/S/U roles"
            )
    if implementation_budget is not None and completion_at is not None:
        started_at = parse_aware_iso8601(
            implementation_budget["started_at"],
            "lifecycle-state.json.budgets.implementation.started_at",
            errors,
        )
        deadline_at = parse_aware_iso8601(
            implementation_budget["deadline_at"],
            "lifecycle-state.json.budgets.implementation.deadline_at",
            errors,
        )
        if started_at is not None and frozen_at is not None and frozen_at < started_at:
            errors.append(f"{label}: F timestamp predates implementation authorization")
        if started_at is not None and completion_at < started_at:
            errors.append(f"{label}: V completion timestamp predates implementation authorization")
        if deadline_at is not None and completion_at > deadline_at:
            errors.append(f"{label}: V completion timestamp exceeds the fixed authorized deadline")

    validate_verification_summary_checkpoint(
        state,
        artifact_root,
        state_relative,
        freeze_pointer,
        freeze,
        graph,
        errors,
    )
    artifact_head = git_output(
        artifact_root, ["rev-parse", "HEAD^{commit}"], "validate-agentic-completion: artifact HEAD"
    ).strip()
    artifact_tree = git_output(
        artifact_root, ["rev-parse", "HEAD^{tree}"], "validate-agentic-completion: artifact tree"
    ).strip()
    return errors, {
        "freeze": freeze_pointer,
        "lifecycle_artifact_checkpoint": state["artifact_checkpoint"],
        "verification_summary_checkpoint": {
            "ref": state["artifact_checkpoint"]["ref"],
            "commit": artifact_head,
            "tree": artifact_tree,
        },
        "code_checkpoint": freeze["code"],
        "receipts": [
            {"role": item["role"], "lens": item["lens"], "path": item["path"], "digest": item["digest"]}
            for item in state["receipts"]
        ],
        "completion_timestamp": None if completion_at is None else completion_at.isoformat(),
        "semantic_artifact_count": len(manifest),
    }


def expected_semantic_artifact_manifest(registry: Registry) -> tuple[list[dict[str, str]], list[str]]:
    entries: list[tuple[str, str]] = [
        ("spec", registry.data["spec_path"]),
        ("registry", f".tasks/{registry.feature}/tasks.json"),
    ]
    entries.extend(("slice", path) for path in registry.authoritative_slices)
    for package in registry.packages:
        entries.extend((("package", package.path), ("proof", package.proof_path)))
        if package.verification_mode == "boundary" and package.report_path is not None:
            entries.append(("boundary-report", package.report_path))
    result: list[dict[str, str]] = []
    errors: list[str] = []
    for kind, path in sorted(entries, key=lambda item: (item[0], item[1])):
        try:
            artifact = resolve_authority_file(registry.root, path, f"semantic artifact {path}")
        except SliceproofError as exc:
            errors.extend(exc.errors)
            continue
        result.append({"kind": kind, "path": path, "digest": digest_bytes(artifact.read_bytes())})
    return result, errors


def expected_boundary_receipts(registry: Registry, errors: list[str]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for package in registry.packages:
        if package.verification_mode != "boundary" or package.report_path is None:
            continue
        try:
            report = resolve_authority_file(
                registry.root, package.report_path, f"boundary receipt {package.package_id}"
            )
        except SliceproofError as exc:
            errors.extend(exc.errors)
            continue
        result.append({
            "package": package.package_id,
            "path": package.report_path,
            "digest": digest_bytes(report.read_bytes()),
        })
    return sorted(result, key=lambda item: item["package"])


def validate_freeze_artifact_digests(
    artifact_root: Path,
    entries: list[dict[str, str]],
    label: str,
    errors: list[str],
    *,
    require_nonempty: bool,
) -> None:
    if require_nonempty and not entries:
        errors.append(f"{label}: expected at least one bound command result")
    paths = [item["path"] for item in entries]
    if paths != sorted(paths) or len(paths) != len(set(paths)):
        errors.append(f"{label}: paths must be unique and canonically sorted")
    for index, item in enumerate(entries):
        item_label = f"{label}[{index}]"
        if item["path"].endswith("/lifecycle-state.json") or "/assurance/" in item["path"]:
            errors.append(f"{item_label}.path: Lifecycle State and post-freeze outputs are excluded")
            continue
        validate_pointer_file(artifact_root, item["path"], item["digest"], item_label, errors)


def validate_completion_code_identity(
    state: dict[str, Any], code: dict[str, str], code_root: Path, errors: list[str]
) -> None:
    label = "validate-agentic-completion: freeze code"
    checkpoint = state["code_checkpoint"]
    if checkpoint is None or (
        code["checkpoint_ref"] != checkpoint["ref"] or code["commit"] != checkpoint["sha"]
    ):
        errors.append(f"{label}: must equal the exact Lifecycle State code checkpoint/ref")
    require_git_commit(code_root, code["commit"], f"{label}.commit", errors)
    require_git_commit(code_root, code["base_commit"], f"{label}.base_commit", errors)
    require_git_tree(code_root, code["tree"], f"{label}.tree", errors)
    actual_tree = git_commit_tree(code_root, code["commit"], f"{label}.commit", errors)
    if actual_tree is not None and actual_tree != code["tree"]:
        errors.append(f"{label}.tree: does not match exact code commit")
    require_git_ref_at_commit(
        code_root, code["checkpoint_ref"], code["commit"], f"{label}.checkpoint_ref", errors
    )
    errors.extend(validate_worktree_head_and_clean(code_root, code["commit"], label))
    try:
        clean = git_output_bytes(
            code_root,
            ["status", "--porcelain=v1", "-z", "--untracked-files=all"],
            label,
        )
        if clean:
            errors.append(f"{label}: exact clean-status identity is not clean")
        if digest_bytes(clean) != code["clean_status_digest"]:
            errors.append(f"{label}.clean_status_digest: does not match current exact status")
        if raw_git_diff_identity(
            code_root, code["base_commit"], code["commit"], f"{label}.raw_diff_digest"
        ) != code["raw_diff_digest"]:
            errors.append(f"{label}.raw_diff_digest: does not match exact base-to-commit raw diff")
        ancestry = git_process(
            code_root, ["merge-base", "--is-ancestor", code["base_commit"], code["commit"]], label
        )
        if ancestry.returncode != 0:
            errors.append(f"{label}.base_commit: must be an ancestor of the frozen commit")
    except SliceproofError as exc:
        errors.extend(exc.errors)


def load_canonical_assurance_json(
    artifact_root: Path, path: str, label: str, errors: list[str]
) -> dict[str, Any] | None:
    try:
        resolved = resolve_authority_file(artifact_root, path, label)
        raw = resolved.read_bytes()
        data = load_strict_json_text(raw.decode("utf-8"), label)
    except (SliceproofError, UnicodeError) as exc:
        if isinstance(exc, SliceproofError):
            errors.extend(exc.errors)
        else:
            errors.append(f"{label}: expected UTF-8 canonical JSON")
        return None
    if not isinstance(data, dict):
        errors.append(f"{label}: root must be an object")
        return None
    if raw != canonical_json_bytes(data):
        errors.append(f"{label}: file must use canonical sorted-key compact JSON with one trailing newline")
    return data


def predecessor_pointer(role: str, lens: str, path: str, digest: str) -> dict[str, str]:
    return {"role": role, "lens": lens, "path": path, "digest": digest}


def validate_completion_receipt_graph(
    state: dict[str, Any],
    freeze: dict[str, Any],
    artifact_root: Path,
    frozen_at: datetime | None,
    errors: list[str],
) -> tuple[list[dict[str, Any]], datetime | None]:
    label = "validate-agentic-completion: receipt graph"
    profile = freeze["assurance"]["profile"]
    lenses = freeze["assurance"]["specialist_lenses"]
    if lenses != sorted(lenses) or len(lenses) != len(set(lenses)):
        errors.append(f"{label}: specialist lenses must be unique and canonically sorted")
    if any(lens in set(FIXED_RECEIPT_LENSES.values()) for lens in lenses):
        errors.append(f"{label}: specialist lenses cannot overlap canonical C/R/U/V ownership")
    if profile != "high" and lenses:
        errors.append(f"{label}: only high profile may own final specialist lenses")

    expected_nodes: list[tuple[str, str]]
    if profile == "low":
        expected_nodes = [("C", FIXED_RECEIPT_LENSES["C"]), ("V", FIXED_RECEIPT_LENSES["V"])]
    elif profile == "standard":
        expected_nodes = [
            ("R", FIXED_RECEIPT_LENSES["R"]),
            ("U", FIXED_RECEIPT_LENSES["U"]),
            ("V", FIXED_RECEIPT_LENSES["V"]),
        ]
    else:
        expected_nodes = [
            ("R", FIXED_RECEIPT_LENSES["R"]),
            *(("S", lens) for lens in lenses),
            ("U", FIXED_RECEIPT_LENSES["U"]),
            ("V", FIXED_RECEIPT_LENSES["V"]),
        ]
    actual_nodes = [(item["role"], item["lens"]) for item in state["receipts"]]
    if actual_nodes != expected_nodes:
        errors.append(
            f"{label}: {profile} profile requires exact roles/lenses {expected_nodes!r}; got {actual_nodes!r}"
        )

    freeze_pointer = predecessor_pointer(
        "F", "freeze", state["freeze"]["path"], state["freeze"]["digest"]
    )
    pointer_by_node = {
        (item["role"], item["lens"]): predecessor_pointer(
            item["role"], item["lens"], item["path"], item["digest"]
        )
        for item in state["receipts"]
    }
    receipt_data: dict[tuple[str, str], dict[str, Any]] = {}
    receipt_times: dict[tuple[str, str], datetime] = {}
    graph: list[dict[str, Any]] = []
    for pointer in state["receipts"]:
        node = (pointer["role"], pointer["lens"])
        data = load_canonical_assurance_json(artifact_root, pointer["path"], f"receipt {node}", errors)
        if data is None:
            continue
        if digest_bytes(canonical_json_bytes(data)) != pointer["digest"]:
            errors.append(f"receipt {node}: pointer digest does not match canonical receipt")
        schema = receipt_file_schema(pointer["role"])
        before_shape = len(errors)
        validate_json_shape(data, schema, f"receipt {node}", errors)
        if len(errors) != before_shape:
            continue
        if data["role"] != pointer["role"] or data["lens"] != pointer["lens"]:
            errors.append(f"receipt {node}: file role/lens does not match Lifecycle State pointer")
        if data["freeze_id"] != freeze["id"] or data["freeze_digest"] != state["freeze"]["digest"]:
            errors.append(f"receipt {node}: cross-freeze binding is forbidden")
        if data["authorization"] != freeze["authorization"]:
            errors.append(f"receipt {node}: authorization lineage does not match F")
        recorded = parse_aware_iso8601(data["recorded_at"], f"receipt {node}.recorded_at", errors)
        if recorded is not None:
            receipt_times[node] = recorded
        receipt_data[node] = data
        graph.append(data)

    def pointer(role: str, lens: str) -> dict[str, str] | None:
        value = pointer_by_node.get((role, lens))
        if value is None:
            errors.append(f"{label}: missing predecessor pointer {(role, lens)!r}")
        return value

    expected_predecessors: dict[tuple[str, str], list[dict[str, str] | None]] = {}
    if profile == "low":
        expected_predecessors[("C", FIXED_RECEIPT_LENSES["C"])] = [freeze_pointer]
        expected_predecessors[("V", FIXED_RECEIPT_LENSES["V"])] = [
            freeze_pointer, pointer("C", FIXED_RECEIPT_LENSES["C"])
        ]
    else:
        review = pointer("R", FIXED_RECEIPT_LENSES["R"])
        expected_predecessors[("R", FIXED_RECEIPT_LENSES["R"])] = [freeze_pointer]
        specialist_pointers = [pointer("S", lens) for lens in lenses]
        for lens in lenses:
            expected_predecessors[("S", lens)] = [freeze_pointer, review]
        audit_predecessors = [freeze_pointer, review, *specialist_pointers]
        expected_predecessors[("U", FIXED_RECEIPT_LENSES["U"])] = audit_predecessors
        expected_predecessors[("V", FIXED_RECEIPT_LENSES["V"])] = [
            *audit_predecessors, pointer("U", FIXED_RECEIPT_LENSES["U"])
        ]

    for node, data in receipt_data.items():
        expected = expected_predecessors.get(node)
        if expected is None or any(item is None for item in expected) or data["predecessors"] != expected:
            errors.append(
                f"receipt {node}.predecessors: must name exact acyclic same-freeze predecessors; "
                "circular/postdecessor/summary substitution is forbidden"
            )
        if node[0] == "C":
            if data["verdicts"] != {"code_risk": "PASS", "completion": "PASS"}:
                errors.append(f"receipt {node}: low C requires two explicit PASS verdicts")
        elif node[0] in {"R", "S", "U"} and data["verdict"] != "PASS":
            errors.append(f"receipt {node}: semantic predecessor must be PASS")
        recorded = receipt_times.get(node)
        if recorded is not None and frozen_at is not None and recorded < frozen_at:
            errors.append(f"receipt {node}.recorded_at: cannot predate F")
        if recorded is not None and expected is not None:
            for predecessor in expected:
                if predecessor is None or predecessor["role"] == "F":
                    continue
                predecessor_time = receipt_times.get((predecessor["role"], predecessor["lens"]))
                if predecessor_time is not None and recorded < predecessor_time:
                    errors.append(f"receipt {node}.recorded_at: cannot predate a required predecessor")
        if node[0] == "V":
            for field in ("deviations", "limitations"):
                if any(not item.strip() or len(item) > 512 for item in data[field]):
                    errors.append(f"receipt {node}.{field}: expected concise non-blank index entries")

    summary_node = ("V", FIXED_RECEIPT_LENSES["V"])
    return graph, receipt_times.get(summary_node)


def receipt_file_schema(role: str) -> dict[str, Any]:
    schema: dict[str, Any] = {
        "schema_version": ("rule", lambda value: type(value) is int and value == 1, "1"),
        "role": ("enum", {role}),
        "lens": LENS_SCHEMA,
        "freeze_id": FREEZE_ID_SCHEMA,
        "freeze_digest": DIGEST_SCHEMA,
        "authorization": {"id": TOKEN_SCHEMA, "effective_digest": DIGEST_SCHEMA},
        "predecessors": ("list", PREDECESSOR_POINTER_SCHEMA),
        "recorded_at": str,
    }
    if role == "C":
        schema["verdicts"] = {
            "code_risk": ("enum", {"PASS", "FAIL", "PROFILE_INVALID"}),
            "completion": ("enum", {"PASS", "FAIL", "PROFILE_INVALID"}),
        }
    elif role in {"R", "S", "U"}:
        schema["verdict"] = ("enum", {"PASS", "FAIL"})
    elif role == "V":
        schema["deviations"] = ("list", str)
        schema["limitations"] = ("list", str)
    return schema


def validate_verification_summary_checkpoint(
    state: dict[str, Any],
    artifact_root: Path,
    state_relative: str,
    freeze_pointer: dict[str, str],
    freeze: dict[str, Any],
    graph: list[dict[str, Any]],
    errors: list[str],
) -> None:
    label = "validate-agentic-completion: artifact V checkpoint"
    try:
        head = git_output(artifact_root, ["rev-parse", "HEAD^{commit}"], label).strip()
    except SliceproofError as exc:
        errors.extend(exc.errors)
        return
    errors.extend(validate_worktree_head_and_clean(artifact_root, head, label))
    require_git_ref_at_commit(
        artifact_root,
        state["artifact_checkpoint"]["ref"],
        head,
        f"{label}.artifact_ref",
        errors,
    )
    paths = [
        state_relative,
        freeze_pointer["path"],
        *(item["path"] for item in state["receipts"]),
        *(item["path"] for item in freeze["semantic_artifacts"]),
        *(item["path"] for item in freeze["runtime_evidence"]),
        *(item["path"] for item in freeze["command_results"]),
    ]
    for path in paths:
        try:
            current = resolve_authority_file(artifact_root, path, f"{label}: {path}").read_bytes()
            committed = git_output_bytes(
                artifact_root, ["show", f"{head}:{path}"], f"{label}: committed {path}"
            )
        except SliceproofError as exc:
            errors.extend(exc.errors)
            continue
        if current != committed:
            errors.append(f"{label}: current {path} must equal its exact committed V-checkpoint file")
    if not any(item.get("role") == "V" for item in graph):
        errors.append(f"{label}: checkpoint must contain the index-only V receipt before notification")


def validate_final_report_absence(registry: Registry, package: RegistryPackage) -> list[str]:
    errors: list[str] = []
    if package.report_path is not None:
        errors.append(
            f"work_packages[{package.package_id}].report_path: final mode requires null; substitute report is invalid"
        )
    dependents = registry.dependents(package.package_id)
    if dependents:
        errors.append(
            f"assurance routing: final package {package.package_id} cannot unlock dependents {dependents}"
        )
    canonical_relative = f".tasks/{registry.feature}/reports/{package.package_id}.package-verification.md"
    canonical_path = registry.root / canonical_relative
    if canonical_path.exists() or canonical_path.is_symlink():
        errors.append(
            f"assurance routing: final package {package.package_id} must not use fabricated or substitute report "
            f"{canonical_relative}"
        )
    return errors


def validate_direct_dependency_unlocks(state: PackageState) -> ReportValidationResult:
    """Validate direct producer receipts without recursively completing producers."""
    registry = state.registry
    if not registry.planned_sidecar or not state.package.depends_on:
        return ReportValidationResult([], [])

    errors: list[str] = []
    advisories: list[dict[str, Any]] = []
    controlled, controlled_errors = load_controlled_routing(registry)
    errors.extend(controlled_errors)
    if controlled is None:
        if not controlled_errors:
            errors.append(
                "dependency unlock: distinct-root planned mode requires controlled authorized Lifecycle State"
            )
        return ReportValidationResult(errors, advisories)

    for dependency_id in state.package.depends_on:
        producer = registry.package(dependency_id)
        if producer is None:
            errors.append(f"dependency unlock: unknown direct producer {dependency_id}")
            continue
        if producer.verification_mode != "boundary":
            errors.append(f"dependency unlock: producer {dependency_id} must use boundary verification mode")
        if controlled.package_states.get(dependency_id) != "done":
            errors.append(f"dependency unlock: controlled producer {dependency_id} must be done")

        producer_md = state.package_markdowns[dependency_id]
        try:
            proof_path = resolve_safe_path(
                registry.root,
                producer.proof_path,
                f"dependency unlock: producer {dependency_id} proof_path",
                expected_suffix=".proof.md",
                must_exist_file=True,
                root_label="artifact root",
            )
        except SliceproofError as exc:
            errors.extend(exc.errors)
            proof_path = None
        if proof_path is not None:
            errors.extend(validate_proof_markdown(proof_path, producer_md))

        if producer.report_path is None:
            errors.append(f"dependency unlock: producer {dependency_id} boundary report is required")
            continue
        try:
            report_path = resolve_safe_path(
                registry.root,
                producer.report_path,
                f"dependency unlock: producer {dependency_id} report_path",
                expected_suffix=".package-verification.md",
                must_exist_file=True,
                root_label="artifact root",
            )
        except SliceproofError as exc:
            errors.extend(exc.errors)
            continue
        if proof_path is None:
            continue
        result = validate_report_markdown(
            report_path,
            registry,
            producer,
            producer_md,
            proof_path,
            final_validation=True,
        )
        errors.extend(result.errors)
        advisories.extend(result.advisories)
    return ReportValidationResult(errors, advisories)


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
    report_path: Path | None = None
    if package.report_path is not None:
        report_path = resolve_safe_path(
            registry.root,
            package.report_path,
            f"work_packages[{package.package_id}].report_path",
            expected_suffix=".package-verification.md",
            root_label="artifact root",
        )
    return PackageState(registry, package, package_md, proof_path, report_path, packages)


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
        if len(packages) == len(registry.packages):
            errors.extend(validate_package_assurance_assignments(registry, packages))
            controlled, controlled_errors = load_controlled_routing(registry)
            errors.extend(controlled_errors)
            if controlled is not None and (
                expected_package_assurance_assignments(registry, packages)
                != controlled.package_assignments
            ):
                errors.append(
                    "assurance routing: package Markdown assignments do not match controlled Lifecycle State"
                )
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
    data = load_strict_json_file(tasks_resolved, "tasks.json")
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
                report_path=item.get("report_path") if isinstance(item.get("report_path"), str) else None,
                status=item.get("status") if isinstance(item.get("status"), str) else "",
                depends_on=item.get("depends_on") if isinstance(item.get("depends_on"), list) else [],
                verification_mode=(
                    item.get("verification_mode") if isinstance(item.get("verification_mode"), str) else ""
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
            data.get("assurance_profile") if isinstance(data.get("assurance_profile"), str) else ""
        ),
        planned_sidecar=(
            artifact_root is not None
            and code_root is not None
            and root != source_root
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
    for key in (
        "feature",
        "title",
        "status",
        "spec_path",
        "authoritative_slices",
        "assurance_profile",
        "work_packages",
    ):
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
    if not isinstance(assurance_profile, str) or assurance_profile not in ASSURANCE_PROFILES:
        errors.append(f"assurance_profile: required and expected one of {sorted(ASSURANCE_PROFILES)}")

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
        for key in sorted(REGISTRY_PACKAGE_KEYS - set(item)):
            errors.append(f"{prefix}.{key}: expected field in package registry entry")
        package_id = item.get("id")
        if not isinstance(package_id, str) or not PACKAGE_ID_RE.fullmatch(package_id):
            errors.append(f"{prefix}.id: expected WP<N> package id")
        else:
            if package_id in seen_ids:
                errors.append(f"work_packages: duplicate package id {package_id}")
            seen_ids.add(package_id)
            package_ids.add(package_id)
        for key, suffix in (("path", ".md"), ("proof_path", ".proof.md")):
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
        if not isinstance(verification_mode, str) or verification_mode not in PACKAGE_VERIFICATION_MODES:
            errors.append(
                f"{prefix}.verification_mode: required and expected one of {sorted(PACKAGE_VERIFICATION_MODES)}"
            )
        report_path = item.get("report_path")
        if verification_mode == "boundary":
            if not isinstance(report_path, str) or not report_path.strip():
                errors.append(f"{prefix}.report_path: boundary mode requires a non-empty safe report path string")
            else:
                try:
                    resolve_safe_path(
                        registry.root,
                        report_path,
                        f"{prefix}.report_path",
                        expected_suffix=".package-verification.md",
                        root_label="artifact root",
                    )
                except SliceproofError as exc:
                    errors.extend(exc.errors)
        elif verification_mode == "final" and report_path is not None:
            errors.append(f"{prefix}.report_path: final mode requires exactly null; substitute reports are invalid")
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
    if assurance_profile == "low":
        low_shape = (
            len(packages_data) == 1
            and isinstance(packages_data[0], dict)
            and packages_data[0].get("verification_mode") == "final"
            and packages_data[0].get("depends_on") == []
        )
        if not low_shape:
            errors.append("assurance routing: low profile requires exactly one coherent final package with no dependencies")
    mode_by_id = {
        item.get("id"): item.get("verification_mode")
        for item in packages_data
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    for consumer in packages_data:
        if not isinstance(consumer, dict) or not isinstance(consumer.get("depends_on"), list):
            continue
        for producer_id in consumer["depends_on"]:
            if mode_by_id.get(producer_id) == "final":
                errors.append(
                    f"assurance routing: producer {producer_id} has dependent {consumer.get('id')}; "
                    "dependent producers must use boundary mode"
                )
    if registry.feature and FEATURE_RE.fullmatch(registry.feature):
        _controlled, lifecycle_errors = load_controlled_routing(registry)
        errors.extend(lifecycle_errors)
    return errors


def load_controlled_routing(registry: Registry) -> tuple[ControlledRouting | None, list[str]]:
    """Load authority only from an explicit distinct-root planned sidecar."""
    if not registry.planned_sidecar:
        return None, []

    relative_path = f".tasks/{registry.feature}/lifecycle-state.json"
    unresolved = registry.root / relative_path
    if not unresolved.exists() and not unresolved.is_symlink():
        return None, []
    try:
        state_path = resolve_authority_file(registry.root, relative_path, "Lifecycle State routing")
        state = load_strict_json_file(state_path, "Lifecycle State routing")
    except SliceproofError as exc:
        return None, exc.errors
    if not isinstance(state, dict):
        return None, ["Lifecycle State routing: root must be an object"]
    try:
        validate_lifecycle_transition_authority(
            state,
            artifact_root=registry.root,
            code_root=registry.code_root,
            feature=registry.feature,
            relative_path=relative_path,
            previous_commit=None,
            infer_previous=True,
        )
    except SliceproofError as exc:
        return None, exc.errors

    authorization = state["authorization"]
    if authorization["id"] is None:
        return None, []

    errors: list[str] = []
    authorization_id = authorization["id"]
    effective_digest = authorization["effective_digest"]
    profile = state["assurance_profile"]
    modes = state["package_modes"]
    assignments = state["package_assignments"]
    package_states = {
        package_id: package_state["state"]
        for package_id, package_state in state["packages"].items()
    }
    code_checkpoint = state["code_checkpoint"]
    code_checkpoint_ref = code_checkpoint["ref"] if code_checkpoint is not None else None
    code_checkpoint_sha = code_checkpoint["sha"] if code_checkpoint is not None else None
    if is_report_binding_placeholder_text(authorization_id):
        errors.append("Lifecycle State routing: controlled authorization id must be a safe non-placeholder token")
    if errors:
        return None, errors

    expected_modes = {package.package_id: package.verification_mode for package in registry.packages}
    if profile != registry.assurance_profile:
        errors.append(
            "assurance routing: registry assurance_profile does not match controlled Lifecycle State"
        )
    if modes != expected_modes:
        errors.append(
            "assurance routing: registry verification_mode values do not match controlled Lifecycle State package_modes"
        )
    return ControlledRouting(
        authorization_id=authorization_id,
        effective_digest=effective_digest,
        assurance_profile=profile,
        package_modes=modes,
        package_assignments=assignments,
        package_states=package_states,
        code_checkpoint_ref=code_checkpoint_ref,
        code_checkpoint_sha=code_checkpoint_sha,
    ), errors


def validate_worktree_head_and_clean(root: Path, expected_commit: str, label: str) -> list[str]:
    errors: list[str] = []
    try:
        head = git_output(root, ["rev-parse", "--verify", "HEAD^{commit}"], label).strip()
        if head != expected_commit:
            errors.append(f"{label}: HEAD must equal the exact bound candidate commit")
        status = git_output(
            root,
            ["status", "--porcelain=v1", "--untracked-files=all"],
            label,
        )
        if status:
            errors.append(f"{label}: worktree must be clean, including tracked and untracked files")
    except SliceproofError as exc:
        errors.extend(exc.errors)
    return errors


def validate_controlled_integration_checkpoint(registry: Registry, label: str) -> list[str]:
    if not registry.planned_sidecar:
        return []
    controlled, errors = load_controlled_routing(registry)
    if errors:
        return errors
    if controlled is None:
        return [f"{label}: distinct-root planned mode requires controlled authorized Lifecycle State"]
    if controlled.code_checkpoint_sha is None:
        return [f"{label}: controlled code checkpoint is required for the integration candidate"]
    errors.extend(validate_worktree_head_and_clean(
        registry.code_root,
        controlled.code_checkpoint_sha,
        f"{label}: integration code root",
    ))
    return errors


def validate_controlled_stable_candidate(
    registry: Registry,
    package: RegistryPackage,
    *,
    candidate_commit: str | None,
    candidate_ref: str | None = None,
    label: str,
    require_done: bool = False,
    require_current_candidate: bool = True,
) -> list[str]:
    if not registry.planned_sidecar:
        return []
    controlled, errors = load_controlled_routing(registry)
    if errors:
        return errors
    if controlled is None:
        return [f"{label}: distinct-root planned mode requires controlled authorized Lifecycle State"]

    package_state = controlled.package_states.get(package.package_id)
    allowed_states = {"done"} if require_done else {"stabilized", "verified", "done"}
    if package_state not in allowed_states:
        required_state = "done" if require_done else "stabilized, verified, or done"
        errors.append(
            f"{label}: controlled package {package.package_id} must be {required_state}"
        )
    if controlled.code_checkpoint_sha is None or controlled.code_checkpoint_ref is None:
        errors.append(f"{label}: controlled code checkpoint is required for a stable package candidate")
        return errors

    require_git_commit(
        registry.code_root,
        controlled.code_checkpoint_sha,
        f"{label}: controlled code checkpoint sha",
        errors,
    )
    if candidate_commit is not None:
        ancestry = git_process(
            registry.code_root,
            ["merge-base", "--is-ancestor", candidate_commit, controlled.code_checkpoint_sha],
            f"{label}: boundary candidate ancestry",
        )
        if ancestry.returncode == 1:
            errors.append(
                f"{label}: boundary candidate commit must be an ancestor of the current consumer/integration checkpoint"
            )
        elif ancestry.returncode != 0:
            detail = ancestry.stderr.strip() or ancestry.stdout.strip() or f"exit {ancestry.returncode}"
            errors.append(f"{label}: unable to verify boundary candidate ancestry: {detail}")
    if require_current_candidate:
        if candidate_commit is not None and candidate_commit != controlled.code_checkpoint_sha:
            errors.append(f"{label}: boundary report commit must match the controlled code checkpoint")
        if candidate_ref is not None and candidate_ref != controlled.code_checkpoint_ref:
            errors.append(
                f"{label}: boundary report Git Ref must match the exact controlled immutable code checkpoint ref"
            )
        errors.extend(validate_worktree_head_and_clean(
            registry.code_root,
            controlled.code_checkpoint_sha,
            f"{label}: controlled code root/package worktree",
        ))
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
    section_names = h2_order(text)
    for section in sorted(REQUIRED_PACKAGE_SECTIONS):
        count = section_names.count(section)
        if count == 0:
            errors.append(f"{path}: missing required section ## {section}")
        elif count > 1:
            errors.append(f"{path}: duplicate required section ## {section}")

    if errors:
        raise SliceproofError(errors)

    scope = sections["Scope"].strip()
    if not scope:
        errors.append(f"{path}: ## Scope must be non-empty")
    slice_refs = parse_assigned_slices(sections["Assigned Slices"])
    primary_paths = parse_bullets(sections["Primary Paths"], unwrap_path=True)
    verification_expectations = parse_bullets(sections["Verification Expectations"], unwrap_path=False)
    proof_paths = parse_bullets(sections["Proof"], unwrap_path=True)
    verification_mode, report_path, verification_rationale, assurance_assignment, verification_errors = (
        parse_independent_verification(path, sections["Independent Verification"])
    )
    errors.extend(verification_errors)
    dependencies = parse_dependencies(sections["Dependencies"])

    if "Package Verification Report" in sections:
        errors.append(
            f"{path}: obsolete ## Package Verification Report is a substitute; use ## Independent Verification"
        )
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
        verification_mode=verification_mode,
        report_path=report_path,
        verification_rationale=verification_rationale,
        assurance_assignment=assurance_assignment,
        dependencies=dependencies,
    )


def parse_independent_verification(
    path: Path,
    body: str,
) -> tuple[str, str | None, str, AssuranceAssignment, list[str]]:
    label = f"{path}: ## Independent Verification"
    expected_fields = ["Mode", "Report", "Rationale"]
    fields: dict[str, str] = {}
    order: list[str] = []
    errors: list[str] = []
    in_fence = False
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if is_fence(line):
            in_fence = not in_fence
            errors.append(f"{label} must not contain fenced content")
            continue
        if in_fence:
            continue
        match = re.fullmatch(r"[-*]\s+([^:]+):\s*(.+)", line)
        if match is None:
            errors.append(f"{label} must contain only Mode, Report, and Rationale bullet fields")
            continue
        field, value = match.group(1).strip(), match.group(2).strip()
        if field not in expected_fields:
            errors.append(f"{label} contains unsupported field {field!r}")
            continue
        if field in fields:
            errors.append(f"{label} contains duplicate field {field!r}")
            continue
        fields[field] = value
        order.append(field)
    for field in expected_fields:
        if field not in fields:
            errors.append(f"{label} missing {field!r}")
    if order and order != [field for field in expected_fields if field in fields]:
        errors.append(f"{label} fields must appear in Mode, Report, Rationale order")

    mode = normalize_markdown_scalar(fields.get("Mode", ""))
    if mode not in PACKAGE_VERIFICATION_MODES:
        errors.append(f"{label} Mode must be boundary or final")
    raw_report = fields.get("Report", "")
    report_value = normalize_markdown_scalar(raw_report)
    report_path: str | None = report_value
    if mode == "final":
        final_value = normalize_text(raw_report.replace("`", ""))
        if final_value != FINAL_REPORT_MARKER:
            errors.append(f"{label} final Report must be exactly {FINAL_REPORT_MARKER!r}")
            report_path = report_value or None
        else:
            report_path = None
    elif mode == "boundary":
        if normalize_text(raw_report.replace("`", "")) == FINAL_REPORT_MARKER:
            errors.append(f"{label} boundary Report requires a safe package verification report path")
            report_path = None
        elif not report_value:
            errors.append(f"{label} boundary Report requires a safe package verification report path")

    rationale = normalize_markdown_scalar(fields.get("Rationale", ""))
    assignment, assignment_errors = parse_assurance_assignment(rationale, f"{label} Rationale")
    errors.extend(assignment_errors)
    if assignment is None:
        assignment = AssuranceAssignment("", "", "", "")
    return mode, report_path, rationale, assignment, errors


def parse_assurance_assignment(
    rationale: str,
    label: str,
) -> tuple[AssuranceAssignment | None, list[str]]:
    match = re.fullmatch(
        r"Owner: (?P<owner>package-verifier|package-specialist|C|R|S); "
        r"Lens: (?P<lens>[a-z][a-z0-9-]{0,63}); "
        r"Side: (?P<side>pre-freeze|post-freeze); Reason: (?P<reason>.+)",
        rationale,
    )
    if match is None:
        return None, [
            f"{label} must use 'Owner: <package-verifier|package-specialist|C|R|S>; "
            "Lens: <lowercase-token>; Side: <pre-freeze|post-freeze>; Reason: <specific reason>'"
        ]
    reason = match.group("reason").strip()
    if not is_specific_evidence_payload(reason, allow_none=False):
        return None, [f"{label} Reason must be a specific non-placeholder value"]
    return AssuranceAssignment(
        owner=match.group("owner"),
        lens=match.group("lens"),
        side=match.group("side"),
        reason=reason,
    ), []


def validate_independent_verification_rationale(
    registry: Registry,
    package: RegistryPackage,
    package_md: PackageMarkdown,
) -> list[str]:
    label = f"{package.path}: ## Independent Verification Rationale"
    assignment = package_md.assurance_assignment
    reason = assignment.reason.lower()
    errors: list[str] = []
    if package.verification_mode == "boundary":
        if assignment.owner not in {"package-verifier", "package-specialist"}:
            errors.append(f"{label} boundary assignment owner must be package-verifier or package-specialist")
        if assignment.side != "pre-freeze":
            errors.append(f"{label} boundary assignment side must be pre-freeze")
        if assignment.lens in set(FIXED_RECEIPT_LENSES.values()):
            errors.append(f"{label} boundary lens cannot reuse a controlled post-freeze lens")
        if not re.search(
            r"\b(?:boundary|depend(?:ent|ency)?|consum(?:e|ed|er|ption)|contract|risk|specialist|"
            r"shared|public|sensitive|lifecycle)\b",
            reason,
        ):
            errors.append(f"{label} Reason must name the consumed boundary, contract, or package-bound risk")
        return errors

    if assignment.side != "post-freeze":
        errors.append(f"{label} final assignment side must be post-freeze")
    if "final assurance" not in reason or re.search(r"\bdefer(?:red|ral|s|ring)?\b", reason) is None:
        errors.append(f"{label} Reason must explicitly defer semantic verification to final assurance")
    expected: set[tuple[str, str]]
    if registry.assurance_profile == "low":
        expected = {("C", FIXED_RECEIPT_LENSES["C"])}
    elif registry.assurance_profile == "standard":
        expected = {("R", FIXED_RECEIPT_LENSES["R"])}
    else:
        expected = {("R", FIXED_RECEIPT_LENSES["R"]), ("S", assignment.lens)}
    if (assignment.owner, assignment.lens) not in expected:
        if registry.assurance_profile == "high" and assignment.owner == "S":
            errors.append(f"{label} high final-specialist lens requires exact owner S and its named lens")
        else:
            allowed = "C/combined-low-assurance" if registry.assurance_profile == "low" else (
                "R/integrated-code-risk" if registry.assurance_profile == "standard" else
                "R/integrated-code-risk or S/<planned-lens>"
            )
            errors.append(
                f"{label} {registry.assurance_profile} final assignment requires controlled owner/lens {allowed}"
            )
    if assignment.owner == "S" and registry.assurance_profile != "high":
        errors.append(f"{label} final-specialist owner S requires high assurance")
    if assignment.owner == "S" and assignment.lens in set(FIXED_RECEIPT_LENSES.values()):
        errors.append(f"{label} final-specialist lens cannot reuse a canonical final-role lens")
    return errors


def package_id_order(package_id: str) -> int:
    return int(package_id.removeprefix("WP"))


def validate_assignment_lens_reuse(
    assignments: list[dict[str, str]],
    label: str,
) -> list[str]:
    errors: list[str] = []
    lens_owners: dict[str, tuple[str, str, str]] = {}
    for assignment in assignments:
        identity = (assignment["owner"], assignment["lens"], assignment["side"])
        previous = lens_owners.get(assignment["lens"])
        if previous is None:
            lens_owners[assignment["lens"]] = (
                assignment["package"], assignment["owner"], assignment["side"]
            )
            continue
        previous_package, previous_owner, previous_side = previous
        same_post_freeze_assignment = (
            assignment["side"] == "post-freeze"
            and (previous_owner, assignment["lens"], previous_side) == identity
        )
        if not same_post_freeze_assignment:
            errors.append(
                f"{label}: lens {assignment['lens']!r} is assigned to both "
                f"{previous_package} ({previous_side}) and {assignment['package']} ({assignment['side']})"
            )
    return errors


def validate_assurance_assignment_values(
    assignments: list[dict[str, str]],
    *,
    profile: str,
    package_modes: dict[str, str],
    label: str,
) -> list[str]:
    errors: list[str] = []
    expected_packages = sorted(package_modes, key=package_id_order)
    actual_packages = [item["package"] for item in assignments]
    if actual_packages != expected_packages:
        errors.append(f"{label}: must be a canonical package-complete list ordered by package id")
    for index, item in enumerate(assignments):
        item_label = f"{label}[{index}]"
        mode = package_modes.get(item["package"])
        if item["mode"] != mode:
            errors.append(f"{item_label}.mode: must match controlled package mode")
        owner, lens, side = item["owner"], item["lens"], item["side"]
        if mode == "boundary":
            if owner not in {"package-verifier", "package-specialist"} or side != "pre-freeze":
                errors.append(f"{item_label}: boundary requires a package verifier/specialist on pre-freeze")
            if lens in set(FIXED_RECEIPT_LENSES.values()):
                errors.append(f"{item_label}.lens: boundary cannot reuse a controlled post-freeze lens")
        elif mode == "final":
            allowed = {("R", FIXED_RECEIPT_LENSES["R"])}
            if profile == "low":
                allowed = {("C", FIXED_RECEIPT_LENSES["C"])}
            elif profile == "high":
                allowed.add(("S", lens))
            if side != "post-freeze" or (owner, lens) not in allowed:
                errors.append(f"{item_label}: final owner/lens/side does not match {profile} routing")
            if owner == "S" and lens in set(FIXED_RECEIPT_LENSES.values()):
                errors.append(f"{item_label}.lens: final specialist cannot reuse a canonical role lens")
    errors.extend(validate_assignment_lens_reuse(assignments, label))
    return errors


def validate_package_assurance_assignments(
    registry: Registry,
    packages: dict[str, PackageMarkdown],
) -> list[str]:
    assignments = expected_package_assurance_assignments(registry, packages)
    return validate_assignment_lens_reuse(assignments, "assurance assignments")


def package_assurance_assignment_value(
    package: RegistryPackage,
    package_md: PackageMarkdown,
) -> dict[str, str]:
    assignment = package_md.assurance_assignment
    return {
        "package": package.package_id,
        "mode": package.verification_mode,
        "owner": assignment.owner,
        "lens": assignment.lens,
        "side": assignment.side,
    }


def expected_package_assurance_assignments(
    registry: Registry,
    packages: dict[str, PackageMarkdown],
) -> list[dict[str, str]]:
    return [
        package_assurance_assignment_value(package, packages[package.package_id])
        for package in sorted(registry.packages, key=lambda item: package_id_order(item.package_id))
    ]


def planned_final_specialist_lenses(assignments: list[dict[str, str]]) -> list[str]:
    return sorted({
        item["lens"] for item in assignments
        if item["mode"] == "final" and item["owner"] == "S" and item["side"] == "post-freeze"
    })


def validate_package_markdown(registry: Registry, package: RegistryPackage, package_md: PackageMarkdown) -> list[str]:
    errors: list[str] = []
    if package_md.proof_path != package.proof_path:
        errors.append(f"{package.path}: ## Proof path {package_md.proof_path!r} does not match registry proof_path {package.proof_path!r}")
    if package_md.verification_mode != package.verification_mode:
        errors.append(
            f"{package.path}: ## Independent Verification Mode {package_md.verification_mode!r} "
            f"does not match registry verification_mode {package.verification_mode!r}"
        )
    if package_md.report_path != package.report_path:
        errors.append(
            f"{package.path}: ## Independent Verification Report {package_md.report_path!r} "
            f"does not match registry report_path {package.report_path!r}"
        )
    errors.extend(validate_independent_verification_rationale(registry, package, package_md))
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
            package_md.proof_path,
            f"{package.path}: proof path",
            expected_suffix=".proof.md",
            root_label="artifact root",
        )
    except SliceproofError as exc:
        errors.extend(exc.errors)
    if package_md.verification_mode == "boundary" and package_md.report_path is not None:
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


def bound_candidate_commit(state_binding_body: str) -> str | None:
    binding = parse_key_values(state_binding_body)
    value = clean_cell_id(binding.get("Commit / Tree", ""))
    parts = value.split(" | ")
    if len(parts) == 2 and EXACT_GIT_SHA_RE.fullmatch(parts[0]):
        return parts[0]
    return None


def validate_candidate_tracked_evidence_path(
    root: Path,
    candidate_commit: str,
    path_value: str,
    label: str,
) -> list[str]:
    result = git_process(root, ["ls-tree", candidate_commit, "--", path_value], label)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        return [f"{label}: unable to inspect bound candidate tree: {detail}"]
    fields = result.stdout.strip().split(None, 3)
    if (
        len(fields) != 4
        or fields[0] not in {"100644", "100755"}
        or fields[1] != "blob"
        or fields[3] != path_value
    ):
        return [f"{label}: must be a regular Git-tracked file in the bound candidate commit"]
    return []


def validate_report_markdown(
    report_path: Path,
    registry: Registry,
    package: RegistryPackage,
    package_md: PackageMarkdown,
    proof_path: Path,
    *,
    final_validation: bool = False,
) -> ReportValidationResult:
    if package.verification_mode != "boundary" or package.report_path is None:
        return ReportValidationResult([
            f"{package.package_id}: package verification report is valid only for boundary mode"
        ], [])
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
        "Selected Causal Evidence",
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
            "### Selected Causal Evidence, ### Slice Closure Review, ### Code Review Findings, "
            "### Blocking Findings, ### Repair Guidance"
        )
    for section in sorted(REQUIRED_SOURCE_REPORT_H3):
        if section not in source_h3:
            errors.append(f"{report_path}: missing required source section ### {section}")

    root = registry.root
    evidence_root = registry.code_root.resolve(strict=False)
    evidence_candidate_commit = (
        bound_candidate_commit(sections["State Binding"])
        if registry.planned_sidecar
        else None
    )

    verdict = ""
    if "Verdict" in source_h3:
        verdict = source_report_verdict(source_h3["Verdict"])
        if verdict not in {"PASS", "FAIL"}:
            errors.append(f"{report_path}: ### Verdict must be PASS or FAIL")
        elif verdict != "PASS":
            errors.append(f"{report_path}: ### Verdict must be PASS for boundary package completion")
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
                candidate_commit=evidence_candidate_commit,
            )
        )
    if "Triggered Risk Selection Notes" in source_h3:
        errors.extend(validate_triggered_risk_selection_notes(report_path, source_h3["Triggered Risk Selection Notes"]))
    if "Test Review Scope" in source_h3:
        errors.append(f"{report_path}: obsolete ### Test Review Scope receipt is not supported")
    if "Selected Causal Evidence" in source_h3:
        errors.extend(
            validate_selected_causal_evidence(
                report_path,
                root,
                evidence_root,
                proof_path,
                source_h3["Selected Causal Evidence"],
                candidate_commit=evidence_candidate_commit,
            )
        )
    if "Slice Closure Review" in source_h3:
        errors.extend(validate_report_slice_closure_review(report_path, package_md, source_h3["Slice Closure Review"]))
    if "Code Review Findings" in source_h3:
        errors.extend(validate_report_code_review_findings(report_path, source_h3["Code Review Findings"]))
    if "Blocking Findings" in source_h3 and not is_empty_gaps_deviations_section(source_h3["Blocking Findings"]):
        errors.append(f"{report_path}: ### Blocking Findings must be empty or None for boundary completion")
    if "Open Findings" in sections:
        open_findings = sections["Open Findings"]
        if UNRESOLVED_MARKER_RE.search(open_findings):
            errors.append(f"{report_path}: ## Open Findings contains unresolved TODO/OPEN marker")
        if not is_empty_gaps_deviations_section(open_findings):
            errors.append(f"{report_path}: ## Open Findings must be '- None.' for boundary completion")

    state_result = validate_report_state_binding(
        report_path,
        registry,
        package,
        package_md,
        proof_path,
        sections["State Binding"],
        final_validation=final_validation,
    )
    errors.extend(state_result.errors)
    if "Semgrep Evidence" in sections:
        errors.extend(
            validate_semgrep_evidence_binding(
                report_path,
                root,
                registry.feature,
                package,
                sections["Semgrep Evidence"],
            )
        )
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
    *,
    candidate_commit: str | None = None,
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
                candidate_commit=candidate_commit,
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


def parse_strict_report_table(
    report_path: Path,
    section: str,
    body: str,
    columns: list[str],
) -> tuple[list[ProofRow], list[str]]:
    label = f"{report_path}: ### {section}"
    numbered_lines = [
        (line_number, raw_line.strip())
        for line_number, raw_line in enumerate(body.splitlines(), start=1)
        if raw_line.strip()
    ]
    if any(is_fence(line) for _line_number, line in numbered_lines):
        return [], [f"{label} must not contain fenced content"]
    if not numbered_lines:
        return [], [f"{label} must include at least one evidence row"]

    table_lines: list[tuple[int, list[str], str]] = []
    for line_number, line in numbered_lines:
        cells = split_markdown_table_row(line)
        if cells is None:
            return [], [
                f"{label} must contain exactly one contiguous Markdown table with no prose"
            ]
        table_lines.append((line_number, cells, line))
    line_numbers = [line_number for line_number, _cells, _line in table_lines]
    if line_numbers != list(range(line_numbers[0], line_numbers[0] + len(line_numbers))):
        return [], [f"{label} must contain exactly one contiguous Markdown table with no prose"]

    errors: list[str] = []
    if table_lines[0][1] != columns:
        errors.append(f"{label} columns must be exactly {columns}")
    expected_width = len(columns)
    if len(table_lines) < 2 or not is_markdown_table_delimiter(table_lines[1][1], expected_width):
        errors.append(f"{label} must place a matching-width Markdown delimiter after the header")
    if len(table_lines) < 3:
        errors.append(f"{label} must include at least one evidence row")

    rows: list[ProofRow] = []
    for table_index, (_line_number, cells, raw_line) in enumerate(table_lines[2:], start=3):
        if is_markdown_table_delimiter(cells, len(cells)):
            errors.append(f"{label} must contain exactly one contiguous Markdown table")
            continue
        if len(cells) != expected_width:
            errors.append(f"{label} row {table_index} must contain exactly {expected_width} cells")
            continue
        rows.append(ProofRow(dict(zip(columns, cells)), raw_line))
    return ([], errors) if errors else (rows, [])


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


def validate_selected_causal_evidence(
    report_path: Path,
    root: Path,
    evidence_root: Path,
    proof_path: Path,
    body: str,
    *,
    candidate_commit: str | None = None,
) -> list[str]:
    if is_report_section_placeholder_body(body):
        return [f"{report_path}: ### Selected Causal Evidence must contain a non-placeholder table"]
    rows, errors = parse_strict_report_table(
        report_path,
        "Selected Causal Evidence",
        body,
        SELECTED_CAUSAL_EVIDENCE_COLUMNS,
    )
    if errors:
        return errors
    try:
        proof_sections = split_h2_sections(read_text_file(proof_path, f"proof {proof_path}"))
    except SliceproofError as exc:
        errors.extend(exc.errors)
        proof_commands = ""
    else:
        proof_commands = proof_sections.get("Commands Run", "")

    for index, row in enumerate(rows, start=1):
        row_label = f"Selected Causal Evidence row {index}"
        for column in SELECTED_CAUSAL_EVIDENCE_COLUMNS:
            value = row.cells.get(column, "")
            allow_none = column == "Substitutes / Fixtures"
            if not is_specific_evidence_payload(value, allow_none=allow_none):
                errors.append(f"{report_path}: {row_label} {column} must be a specific non-placeholder value")
            elif EVIDENCE_UNRESOLVED_MARKER_RE.search(value):
                errors.append(f"{report_path}: {row_label} {column} contains an unresolved marker")
        evidence_type = clean_cell_id(row.cells.get("Evidence Type", "")).lower()
        if evidence_type not in MATRIX_EVIDENCE_TYPES:
            errors.append(f"{report_path}: {row_label} Evidence Type {evidence_type!r} is not supported")
        else:
            errors.extend(
                validate_matrix_evidence_refs(
                    report_path,
                    root,
                    evidence_root,
                    proof_commands,
                    row_label,
                    evidence_type,
                    row.cells.get("Evidence Anchor", ""),
                    field_name="Evidence Anchor",
                    candidate_commit=candidate_commit,
                )
            )
        errors.extend(
            validate_fresh_command_result(
                report_path,
                root,
                proof_commands,
                row_label,
                row.cells.get("Fresh Command Result", ""),
            )
        )
    return errors


def validate_fresh_command_result(
    report_path: Path,
    root: Path,
    proof_commands: str,
    row_label: str,
    value: str,
) -> list[str]:
    cleaned = value.replace("`", "").strip()
    match = re.fullmatch(
        r"(?P<anchor>command:.+?)\s+(?:—|-)\s+PASS(?:\s*[,;:]\s*|\s+)(?P<observed>.+)",
        cleaned,
    )
    if match is None:
        return [
            f"{report_path}: {row_label} Fresh Command Result must use "
            "'command:<typed anchor> — PASS, <fresh observed result>'"
        ]
    observed = match.group("observed").strip()
    if not is_specific_evidence_payload(observed, allow_none=False):
        return [f"{report_path}: {row_label} Fresh Command Result must include a specific observed result"]
    anchor = match.group("anchor").strip()
    ref_type, separator, payload = anchor.partition(":")
    if ref_type != "command" or not separator:
        return [f"{report_path}: {row_label} Fresh Command Result requires one typed command anchor"]
    return validate_command_evidence_ref(report_path, root, proof_commands, row_label, payload)


def validate_matrix_evidence_refs(
    report_path: Path,
    root: Path,
    evidence_root: Path,
    proof_commands: str,
    row_label: str,
    evidence_type: str,
    refs_text: str,
    *,
    field_name: str = "Evidence Refs",
    candidate_commit: str | None = None,
) -> list[str]:
    errors: list[str] = []
    cleaned_refs = refs_text.replace("`", "").strip()
    if not re.match(r"^(?:code|test|static|command|manual):", cleaned_refs):
        return [f"{report_path}: {row_label} {field_name} must start with a typed evidence anchor"]
    refs = split_evidence_refs(refs_text)
    if not refs:
        return [f"{report_path}: {row_label} {field_name} must use typed evidence anchors"]
    for ref in refs:
        ref_type, _separator, payload = ref.partition(":")
        ref_type = ref_type.strip().lower()
        if ref_type not in MATRIX_EVIDENCE_TYPES - {"mixed"}:
            errors.append(f"{report_path}: {row_label} {field_name} anchor {ref!r} has unsupported evidence type")
            continue
        if evidence_type in MATRIX_EVIDENCE_TYPES - {"mixed"} and ref_type != evidence_type:
            errors.append(f"{report_path}: {row_label} Evidence Type {evidence_type!r} does not match {ref_type!r} anchor")
        if is_report_section_placeholder_body(payload):
            errors.append(f"{report_path}: {row_label} {field_name} anchor {ref!r} must be non-placeholder")
            continue
        if ref_type in {"code", "test", "static"}:
            errors.extend(validate_path_evidence_ref(
                report_path,
                evidence_root,
                row_label,
                ref_type,
                payload,
                candidate_commit=candidate_commit,
            ))
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


def validate_path_evidence_ref(
    report_path: Path,
    root: Path,
    row_label: str,
    ref_type: str,
    payload: str,
    *,
    candidate_commit: str | None = None,
) -> list[str]:
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
        if candidate_commit is None:
            resolve_safe_path(
                root,
                path_value,
                f"{report_path}: {row_label} {ref_type} evidence path",
                must_exist_file=True,
                root_label="code root",
            )
        else:
            repo_relative_path(
                path_value,
                f"{report_path}: {row_label} {ref_type} evidence path",
            )
    except SliceproofError as exc:
        errors.extend(exc.errors)
    else:
        if candidate_commit is not None:
            errors.extend(validate_candidate_tracked_evidence_path(
                root,
                candidate_commit,
                path_value,
                f"{report_path}: {row_label} {ref_type} evidence path",
            ))
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


def candidate_binding_from_cli(
    registry: Registry,
    package: RegistryPackage,
    args: argparse.Namespace,
) -> tuple[CandidateBinding | None, list[str]]:
    runtime_entries, runtime_errors = parse_digest_entries(
        args.runtime_evidence_digest,
        "emit-state-binding: --runtime-evidence-digest",
        key_kind="path",
        root=registry.root,
    )
    contract_entries, contract_errors = parse_digest_entries(
        args.consumed_contract_digest,
        "emit-state-binding: --consumed-contract-digest",
        key_kind="token",
    )
    errors = [*runtime_errors, *contract_errors]
    candidate = CandidateBinding(
        authorization_id=args.authorization_id,
        effective_digest=args.effective_digest,
        assurance_profile=args.assurance_profile,
        verification_mode=args.verification_mode,
        commit=args.commit,
        tree=args.tree,
        base_commit=args.base_commit,
        diff_digest=args.diff_digest,
        runtime_evidence_digests=runtime_entries,
        consumed_contract_digests=contract_entries,
    )
    errors.extend(validate_candidate_binding(
        registry,
        package,
        candidate,
        "emit-state-binding",
        worktree=args.worktree,
        git_ref=args.git_ref,
    ))
    return (None, errors) if errors else (candidate, [])


def candidate_binding_from_report(
    report_path: Path,
    registry: Registry,
    package: RegistryPackage,
    binding: dict[str, str],
    *,
    final_validation: bool = False,
) -> tuple[CandidateBinding | None, list[str]]:
    label = f"{report_path}: State Binding"
    authorization, authorization_errors = parse_binding_pair(
        clean_cell_id(binding["Authorization / Effective Digest"]),
        f"{label} Authorization / Effective Digest",
    )
    profile_mode, profile_errors = parse_binding_pair(
        clean_cell_id(binding["Assurance Profile / Verification Mode"]),
        f"{label} Assurance Profile / Verification Mode",
    )
    commit_tree, commit_errors = parse_binding_pair(
        clean_cell_id(binding["Commit / Tree"]),
        f"{label} Commit / Tree",
    )
    base_diff, base_errors = parse_binding_pair(
        clean_cell_id(binding["Base / Diff Identity"]),
        f"{label} Base / Diff Identity",
    )
    runtime_entries, runtime_errors = parse_digest_binding_text(
        clean_cell_id(binding["Runtime Evidence Digests"]),
        f"{label} Runtime Evidence Digests",
        key_kind="path",
        root=registry.root,
    )
    contract_entries, contract_errors = parse_digest_binding_text(
        clean_cell_id(binding["Consumed Contract Digests"]),
        f"{label} Consumed Contract Digests",
        key_kind="token",
    )
    errors = [
        *authorization_errors,
        *profile_errors,
        *commit_errors,
        *base_errors,
        *runtime_errors,
        *contract_errors,
    ]
    if errors:
        return None, errors
    candidate = CandidateBinding(
        authorization_id=authorization[0],
        effective_digest=authorization[1],
        assurance_profile=profile_mode[0],
        verification_mode=profile_mode[1],
        commit=commit_tree[0],
        tree=commit_tree[1],
        base_commit=base_diff[0],
        diff_digest=base_diff[1],
        runtime_evidence_digests=runtime_entries,
        consumed_contract_digests=contract_entries,
    )
    errors.extend(validate_candidate_binding(
        registry,
        package,
        candidate,
        label,
        worktree=clean_cell_id(binding["Worktree"]),
        git_ref=clean_cell_id(binding["Git Ref"]),
        final_validation=final_validation,
    ))
    return (None, errors) if errors else (candidate, [])


def parse_binding_pair(value: str, label: str) -> tuple[tuple[str, str], list[str]]:
    parts = value.split(" | ")
    if len(parts) != 2 or not all(parts):
        return ("", ""), [f"{label} must contain exactly two values separated by ' | '"]
    return (parts[0], parts[1]), []


def parse_digest_binding_text(
    value: str,
    label: str,
    *,
    key_kind: str,
    root: Path | None = None,
) -> tuple[tuple[tuple[str, str], ...], list[str]]:
    values = ["none"] if value == "none" else value.split("; ")
    entries, errors = parse_digest_entries(values, label, key_kind=key_kind, root=root)
    if not errors and format_digest_entries(entries) != value:
        errors.append(f"{label} entries must be unique and sorted by key")
    return entries, errors


def parse_digest_entries(
    values: list[str],
    label: str,
    *,
    key_kind: str,
    root: Path | None = None,
) -> tuple[tuple[tuple[str, str], ...], list[str]]:
    if values == ["none"]:
        return (), []
    errors: list[str] = []
    if not values or "none" in values:
        return (), [f"{label} must be exactly 'none' or one or more digest entries"]
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    for raw_entry in values:
        if raw_entry.count("=") != 1 or "; " in raw_entry:
            errors.append(f"{label}: malformed digest entry {raw_entry!r}")
            continue
        key, digest = raw_entry.split("=", 1)
        if key in seen:
            errors.append(f"{label}: duplicate digest key {key!r}")
        seen.add(key)
        if key_kind == "path":
            try:
                repo_relative_path(key, f"{label} path")
            except SliceproofError as exc:
                errors.extend(exc.errors)
            if any(delimiter in key for delimiter in ("=", "; ")):
                errors.append(f"{label} path must not contain binding delimiters")
            if root is not None:
                try:
                    evidence_path = resolve_authority_file(root, key, f"{label} path")
                except SliceproofError as exc:
                    errors.extend(exc.errors)
                else:
                    if DIGEST_RE.fullmatch(digest) and digest_bytes(evidence_path.read_bytes()) != digest:
                        errors.append(f"{label}: digest does not match current runtime evidence file {key}")
        elif key_kind == "token":
            if not SAFE_TOKEN_RE.fullmatch(key) or is_report_binding_placeholder_text(key):
                errors.append(f"{label}: contract id {key!r} must be a safe non-placeholder token")
        else:
            errors.append(f"{label}: unsupported digest key kind")
        if not DIGEST_RE.fullmatch(digest):
            errors.append(f"{label}: digest for {key!r} must be lowercase sha256:<64-hex>")
        entries.append((key, digest))
    return tuple(sorted(entries)), errors


def format_digest_entries(entries: tuple[tuple[str, str], ...]) -> str:
    if not entries:
        return "none"
    return "; ".join(f"{key}={digest}" for key, digest in entries)


def validate_candidate_git_identity(
    registry: Registry,
    candidate: CandidateBinding,
    *,
    worktree: str,
    git_ref: str,
    label: str,
    historical_candidate: bool = False,
) -> list[str]:
    errors: list[str] = []
    if not all(EXACT_GIT_SHA_RE.fullmatch(value) for value in (
        candidate.commit,
        candidate.tree,
        candidate.base_commit,
    )) or not DIGEST_RE.fullmatch(candidate.diff_digest):
        return errors
    if (
        not Path(worktree).is_absolute()
        or "\x00" in worktree
        or not SAFE_GIT_REF_RE.fullmatch(git_ref)
        or is_report_binding_placeholder_text(git_ref)
    ):
        return errors

    reviewed_worktree: Path | None = None
    try:
        code_top = Path(git_output(
            registry.code_root,
            ["rev-parse", "--show-toplevel"],
            f"{label}: code repository",
        ).strip()).resolve(strict=False)
        if code_top != registry.code_root:
            errors.append(f"{label}: code root must be an exact Git worktree root")
        if not historical_candidate:
            unresolved_worktree = Path(worktree)
            try:
                reviewed_worktree = unresolved_worktree.resolve(strict=True)
            except OSError as exc:
                errors.append(f"{label}: Worktree must be an existing exact Git worktree root: {exc}")
            else:
                if reviewed_worktree != unresolved_worktree or not reviewed_worktree.is_dir():
                    errors.append(f"{label}: Worktree must be an existing exact Git worktree root")
                else:
                    worktree_top = Path(git_output(
                        reviewed_worktree,
                        ["rev-parse", "--show-toplevel"],
                        f"{label}: Worktree",
                    ).strip()).resolve(strict=False)
                    if worktree_top != reviewed_worktree:
                        errors.append(f"{label}: Worktree must be an existing exact Git worktree root")
                    if registry.planned_sidecar and reviewed_worktree != registry.code_root:
                        errors.append(f"{label}: Worktree must equal the exact supplied code root/package worktree")
                    if git_common_dir(registry.code_root, f"{label}: code repository") != git_common_dir(
                        reviewed_worktree,
                        f"{label}: Worktree",
                    ):
                        errors.append(f"{label}: Worktree must belong to the code repository")
    except SliceproofError as exc:
        errors.extend(exc.errors)
    if errors:
        return errors

    commit_errors_before = len(errors)
    require_git_commit(registry.code_root, candidate.commit, f"{label}: Commit", errors)
    require_git_commit(registry.code_root, candidate.base_commit, f"{label}: Base commit", errors)
    if len(errors) != commit_errors_before:
        return errors

    actual_tree = git_commit_tree(registry.code_root, candidate.commit, f"{label}: Commit", errors)
    if actual_tree is not None and actual_tree != candidate.tree:
        errors.append(f"{label}: Tree must equal the exact candidate commit tree")

    ancestry = git_process(
        registry.code_root,
        ["merge-base", "--is-ancestor", candidate.base_commit, candidate.commit],
        f"{label}: candidate ancestry",
    )
    if ancestry.returncode == 1:
        errors.append(f"{label}: Base commit must be an ancestor of Commit")
    elif ancestry.returncode != 0:
        detail = ancestry.stderr.strip() or ancestry.stdout.strip() or f"exit {ancestry.returncode}"
        errors.append(f"{label}: candidate ancestry local git inspection failed: {detail}")

    require_git_ref_at_commit(
        registry.code_root,
        git_ref,
        candidate.commit,
        f"{label}: Git Ref",
        errors,
    )
    try:
        expected_diff = raw_git_diff_identity(
            registry.code_root,
            candidate.base_commit,
            candidate.commit,
            f"{label}: Diff Identity",
        )
        if candidate.diff_digest != expected_diff:
            errors.append(
                f"{label}: Diff Identity must equal sha256 of the canonical raw no-renames Git diff identity"
            )
    except SliceproofError as exc:
        errors.extend(exc.errors)
    if registry.planned_sidecar and not historical_candidate and reviewed_worktree is not None:
        errors.extend(validate_worktree_head_and_clean(
            reviewed_worktree,
            candidate.commit,
            f"{label}: reviewed package worktree",
        ))
    return errors


def validate_candidate_binding(
    registry: Registry,
    package: RegistryPackage,
    candidate: CandidateBinding,
    label: str,
    *,
    worktree: str,
    git_ref: str,
    final_validation: bool = False,
) -> list[str]:
    errors: list[str] = []
    if not SAFE_TOKEN_RE.fullmatch(candidate.authorization_id) or is_report_binding_placeholder_text(
        candidate.authorization_id
    ):
        errors.append(f"{label}: Authorization id must be a safe non-placeholder token")
    if not DIGEST_RE.fullmatch(candidate.effective_digest):
        errors.append(f"{label}: Effective Authorization Digest must be lowercase sha256:<64-hex>")
    if candidate.assurance_profile not in ASSURANCE_PROFILES:
        errors.append(f"{label}: Assurance Profile is unknown")
    elif candidate.assurance_profile != registry.assurance_profile:
        errors.append(f"{label}: Assurance Profile does not match registry assurance_profile")
    if candidate.verification_mode not in PACKAGE_VERIFICATION_MODES:
        errors.append(f"{label}: Verification Mode is unknown")
    elif candidate.verification_mode != package.verification_mode:
        errors.append(f"{label}: Verification Mode does not match registry verification_mode")
    if package.verification_mode != "boundary":
        errors.append(f"{label}: State Binding is a boundary receipt only; final mode cannot substitute it")
    if is_report_binding_placeholder_text(git_ref):
        errors.append(f"{label} Git Ref must be non-placeholder")
    elif not SAFE_GIT_REF_RE.fullmatch(git_ref):
        errors.append(f"{label}: Git Ref must use safe Git ref syntax")
    elif registry.planned_sidecar and immutable_checkpoint_ref_generation(git_ref, registry.feature) is None:
        errors.append(
            f"{label}: Git Ref must be an immutable namespaced checkpoint ref under "
            f"refs/heads/checkpoints/{registry.feature}/<slot>/g<generation>"
        )
    for field, value in (
        ("Commit", candidate.commit),
        ("Tree", candidate.tree),
        ("Base commit", candidate.base_commit),
    ):
        if not EXACT_GIT_SHA_RE.fullmatch(value):
            errors.append(f"{label}: {field} must be an exact lowercase 40- or 64-hex Git object id")
    if not DIGEST_RE.fullmatch(candidate.diff_digest):
        errors.append(f"{label}: Diff Identity must be lowercase sha256:<64-hex>")
    verifier_output_prefix = f".tasks/{registry.feature}/reports/"
    for path_value, _digest in candidate.runtime_evidence_digests:
        if path_value.startswith(verifier_output_prefix):
            errors.append(f"{label}: verifier report output cannot be a runtime-evidence candidate input")
    if registry.dependents(package.package_id) and not candidate.consumed_contract_digests:
        errors.append(
            f"{label}: dependent producer {package.package_id} requires at least one consumed-contract digest"
        )
    controlled, controlled_errors = load_controlled_routing(registry)
    errors.extend(controlled_errors)
    if controlled is not None:
        if candidate.authorization_id != controlled.authorization_id:
            errors.append(f"{label}: Authorization id does not match controlled Lifecycle State")
        if candidate.effective_digest != controlled.effective_digest:
            errors.append(f"{label}: Effective Authorization Digest does not match controlled Lifecycle State")
    errors.extend(validate_candidate_git_identity(
        registry,
        candidate,
        worktree=worktree,
        git_ref=git_ref,
        label=label,
        historical_candidate=final_validation,
    ))
    errors.extend(validate_controlled_stable_candidate(
        registry,
        package,
        candidate_commit=candidate.commit,
        candidate_ref=git_ref,
        label=label,
        require_done=final_validation,
        require_current_candidate=not final_validation,
    ))
    return errors


def validate_report_state_binding(
    report_path: Path,
    registry: Registry,
    package: RegistryPackage,
    package_md: PackageMarkdown,
    proof_path: Path,
    body: str,
    *,
    final_validation: bool = False,
) -> ReportValidationResult:
    errors: list[str] = []
    advisories: list[dict[str, Any]] = []
    binding, binding_errors = parse_key_values_strict(body, REQUIRED_STATE_BINDING_FIELDS)
    errors.extend(f"{report_path}: ## State Binding {error}" for error in binding_errors)
    for field in sorted(REQUIRED_STATE_BINDING_FIELDS - set(binding)):
        errors.append(f"{report_path}: ## State Binding missing {field!r}")
    if errors:
        return ReportValidationResult(errors, advisories)

    digest_result = validate_assigned_slice_digest_binding(
        report_path,
        package.package_id,
        clean_cell_id(binding["Assigned Slice Digests"]),
        registry.root,
        package_md,
    )
    errors.extend(digest_result.errors)
    advisories.extend(digest_result.advisories)
    candidate, candidate_errors = candidate_binding_from_report(
        report_path,
        registry,
        package,
        binding,
        final_validation=final_validation,
    )
    errors.extend(candidate_errors)
    if candidate is None:
        return ReportValidationResult(errors, advisories)
    expected_values = state_binding_values(
        registry.root,
        package,
        package_md,
        proof_path,
        candidate=candidate,
        worktree=clean_cell_id(binding["Worktree"]),
        git_ref=clean_cell_id(binding["Git Ref"]),
        verified_at=clean_cell_id(binding["Verified At"]),
    )
    none_allowed = {
        "Assigned Slices",
        "Assigned Slice Digests",
        "Runtime Evidence Digests",
        "Consumed Contract Digests",
    }
    for field in STATE_BINDING_FIELD_ORDER:
        value = clean_cell_id(binding[field])
        if field in none_allowed and expected_values[field] == "none" and value == "none":
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

    if clean_cell_id(binding["Matrix Source Snapshot"]) != expected_values["Matrix Source Snapshot"]:
        errors.append(f"{report_path}: State Binding Matrix Source Snapshot does not match current package/Slice source content")

    for field in (
        "Authorization / Effective Digest",
        "Assurance Profile / Verification Mode",
        "Commit / Tree",
        "Base / Diff Identity",
        "Runtime Evidence Digests",
        "Consumed Contract Digests",
    ):
        if clean_cell_id(binding[field]) != expected_values[field]:
            errors.append(f"{report_path}: State Binding {field} is not in canonical candidate form")
    errors.extend(
        validate_state_binding_runtime_metadata(
            f"{report_path}: State Binding",
            clean_cell_id(binding["Worktree"]),
            clean_cell_id(binding["Git Ref"]),
            clean_cell_id(binding["Verified At"]),
        )
    )
    return ReportValidationResult(errors, advisories)


def state_binding_values(
    root: Path,
    package: RegistryPackage,
    package_md: PackageMarkdown,
    proof_path: Path,
    *,
    candidate: CandidateBinding,
    worktree: str,
    git_ref: str,
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
        "Authorization / Effective Digest": f"{candidate.authorization_id} | {candidate.effective_digest}",
        "Assurance Profile / Verification Mode": (
            f"{candidate.assurance_profile} | {candidate.verification_mode}"
        ),
        "Worktree": worktree,
        "Git Ref": git_ref,
        "Commit / Tree": f"{candidate.commit} | {candidate.tree}",
        "Base / Diff Identity": f"{candidate.base_commit} | {candidate.diff_digest}",
        "Runtime Evidence Digests": format_digest_entries(candidate.runtime_evidence_digests),
        "Consumed Contract Digests": format_digest_entries(candidate.consumed_contract_digests),
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
    verified_at: str,
) -> list[str]:
    errors: list[str] = []
    if not Path(worktree).is_absolute() or "\x00" in worktree:
        errors.append(f"{command}: --worktree must be an absolute reviewed worktree path")
    if not SAFE_GIT_REF_RE.fullmatch(git_ref) or is_report_binding_placeholder_text(git_ref):
        errors.append(f"{command}: --git-ref must be a safe non-placeholder reviewed ref")
    parse_aware_iso8601(verified_at, f"{command}: --verified-at", errors)
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


def parse_key_values_strict(body: str, allowed_fields: set[str]) -> tuple[dict[str, str], list[str]]:
    values: dict[str, str] = {}
    errors: list[str] = []
    in_fence = False
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if is_fence(line):
            in_fence = not in_fence
            errors.append("must not contain fenced content")
            continue
        if in_fence or not line:
            continue
        bullet = re.match(r"^(?:[-*]|\d+\.)\s+(.+)$", line)
        if bullet is None:
            continue
        item = bullet.group(1)
        if ":" not in item:
            errors.append(f"malformed field line {line!r}")
            continue
        key, value = item.split(":", 1)
        key = key.strip()
        if key not in allowed_fields:
            errors.append(f"contains unsupported field {key!r}")
            continue
        if key in values:
            errors.append(f"contains duplicate field {key!r}")
            continue
        values[key] = value.strip()
    return values, errors


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


def normalize_markdown_scalar(value: str) -> str:
    stripped = value.strip()
    if len(stripped) >= 2 and stripped.startswith("`") and stripped.endswith("`"):
        stripped = stripped[1:-1]
    return normalize_text(stripped)


def is_specific_evidence_payload(value: str, *, allow_none: bool) -> bool:
    normalized = normalize_text(value).strip("`").strip()
    lowered = normalize_report_binding_placeholder_value(normalized)
    if allow_none and lowered in {
        "none",
        "none disclosed",
        "no substitutes",
        "no fixtures or substitutes",
    }:
        return True
    return (
        any(character.isalnum() for character in normalized)
        and lowered not in REPORT_BINDING_PLACEHOLDER_VALUES | {"not applicable"}
        and not (normalized.startswith("<") and normalized.endswith(">"))
    )


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
