#!/usr/bin/env python3
"""Offline Semgrep helper for Super Developer.

The helper owns local community-rule inventory, stack-to-config retrieval,
privacy-preserving scan argv construction, and bounded Semgrep JSON
consumption. It deliberately does not clone, pull, fetch registry configs, or
interpret Semgrep severities as Super Developer blocker status.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Iterable

try:  # Optional at runtime; JSON fallback keeps this asset importable.
    import yaml  # type: ignore
except Exception:  # pragma: no cover - exercised only where PyYAML is absent.
    yaml = None  # type: ignore


VERSION = 1
MAX_RAW_BYTES = 5 * 1024 * 1024
MAX_RESULTS = 5000
MAX_STRING = 1000
MAX_MESSAGE = 240
MAX_CONTEXT_LINES = 10
SUMMARY_TOP_N = 10
LIST_LIMIT_MAX = 100
LOCAL_RULES_RELATIVE = Path(".superdeveloper/semgrep/local-rules.yml")
RULE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,255}$")
SAFE_STACK_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.+:-]{0,80}$")
EVIDENCE_BASE_RE = re.compile(r"^(integration|WP[A-Za-z0-9_-]+)$")
CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]+")
SUMMARY_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
REGISTRY_PREFIXES = ("p/", "r/", "http://", "https://")
SHELL_SEPARATORS = ("\x00", "\n", "\r", ";", "&&", "||", "`", "$(", "|", ">", "<")


class HelperError(RuntimeError):
    """User-facing helper failure with a concise message."""


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def _sanitize_string(value: Any, limit: int = MAX_STRING) -> str:
    text = str(value) if value is not None else ""
    text = CONTROL_CHARS_RE.sub(" ", text).replace("\r", " ").replace("\n", " ")
    text = " ".join(text.split())
    if len(text) > limit:
        return text[: limit - 15].rstrip() + "...<truncated>"
    return text


def _first_line(value: Any, limit: int = MAX_MESSAGE) -> str:
    text = str(value) if value is not None else ""
    first = text.splitlines()[0] if text.splitlines() else text
    return _sanitize_string(first, limit=limit)


def _json_dump(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def _canonical_json(data: Any) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path, *, max_bytes: int | None = None) -> Any:
    if max_bytes is not None and path.stat().st_size > max_bytes:
        raise HelperError(f"Refusing oversized JSON file: {path.name}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HelperError(f"Invalid JSON in {path.name}: {exc.msg}") from exc


def _load_yaml(path: Path, *, label: str) -> Any:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise HelperError(f"Cannot read {label}: {path.name}: {exc.strerror}") from exc
    if not text.strip():
        return {}
    if yaml is not None:
        try:
            data = yaml.safe_load(text)
        except Exception as exc:  # PyYAML exception classes differ by version.
            raise HelperError(f"Invalid {label} YAML: {path.name}: {exc}") from exc
        return {} if data is None else data
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:  # pragma: no cover - fallback path.
        raise HelperError(f"Invalid {label} YAML: {path.name}; PyYAML is unavailable") from exc


def _write_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if yaml is not None:
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    else:  # pragma: no cover - fallback path.
        path.write_text(_json_dump(data), encoding="utf-8")


def _repo_root_from_arg(value: str | None) -> Path:
    root = Path(value or os.getcwd()).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise HelperError("Repository root must be an existing directory")
    return root


def _expected_plugin_root() -> Path:
    configured = os.environ.get("SUPER_DEVELOPER_PLUGIN_ROOT")
    root = Path(configured).expanduser() if configured and configured.strip() else Path(__file__).resolve().parents[1]
    return root.resolve(strict=False)


def _expected_rules_root() -> Path:
    return (_expected_plugin_root() / ".cache" / "semgrep-rules" / "community").resolve(strict=False)


def _expected_index_path() -> Path:
    return (_expected_plugin_root() / ".cache" / "semgrep-rules" / "index.json").resolve(strict=False)


def _reject_path_traversal(path: Path, label: str) -> None:
    if any(part == ".." for part in path.parts):
        raise HelperError(f"{label} must not contain '..' traversal")


def _reject_shellish(value: str, label: str) -> None:
    if any(separator in value for separator in SHELL_SEPARATORS):
        raise HelperError(f"{label} contains a shell-like separator")


def _reject_registry_config(value: str, label: str = "config") -> None:
    text = value.strip()
    lowered = text.lower()
    if lowered == "auto" or lowered.startswith(REGISTRY_PREFIXES) or "://" in lowered:
        raise HelperError(f"{label} must be a local filesystem path, not registry/URL config: {_sanitize_string(text, 120)}")
    if text.startswith("-"):
        raise HelperError(f"{label} must not look like a command-line flag")
    _reject_shellish(text, label)


def _resolve_existing_path(value: str, *, repo_root: Path | None, label: str) -> Path:
    _reject_registry_config(value, label)
    raw = Path(value).expanduser()
    _reject_path_traversal(raw, label)
    path = raw if raw.is_absolute() else (repo_root or Path.cwd()) / raw
    try:
        resolved = path.resolve(strict=True)
    except FileNotFoundError as exc:
        raise HelperError(f"{label} does not exist: {raw.name if raw.name else raw}") from exc
    return resolved


def _resolve_optional_project_path(value: str, *, repo_root: Path, label: str) -> Path:
    raw = Path(value).expanduser()
    _reject_path_traversal(raw, label)
    path = raw if raw.is_absolute() else repo_root / raw
    resolved = path.resolve(strict=False)
    if not is_relative_to(resolved, repo_root):
        raise HelperError(f"{label} must stay under the repository/worktree root")
    return resolved


def _validate_profile_path(value: str, *, repo_root: Path) -> Path:
    path = _resolve_optional_project_path(value, repo_root=repo_root, label="stack profile")
    if path.exists() and path.is_symlink():
        raise HelperError("stack profile must not be a symlink")
    if path.exists() and not path.is_file():
        raise HelperError("stack profile must be a file")
    return path


def _validate_target(value: str, *, repo_root: Path) -> Path:
    raw = Path(value).expanduser()
    if str(value).strip().startswith("-"):
        raise HelperError("target must not look like a command-line flag")
    _reject_path_traversal(raw, "target")
    _reject_shellish(str(value), "target")
    path = raw if raw.is_absolute() else repo_root / raw
    try:
        resolved = path.resolve(strict=True)
    except FileNotFoundError as exc:
        raise HelperError("target path does not exist") from exc
    if not is_relative_to(resolved, repo_root):
        raise HelperError("target path must stay under the repository/worktree root")
    return resolved


def _validate_evidence_path(value: str, *, repo_root: Path, kind: str, must_exist: bool) -> Path:
    raw = Path(value).expanduser()
    _reject_path_traversal(raw, kind)
    _reject_shellish(str(value), kind)
    path = raw if raw.is_absolute() else repo_root / raw
    if path.is_symlink():
        raise HelperError(f"{kind} path must not be a symlink")
    resolved = path.resolve(strict=False)
    if not is_relative_to(resolved, repo_root):
        raise HelperError(f"{kind} path must stay under the repository/worktree root")
    rel = resolved.relative_to(repo_root)
    parts = rel.parts
    if len(parts) != 4 or parts[0] != ".tasks" or parts[2] != "semgrep":
        raise HelperError(f"{kind} path must be under .tasks/<feature>/semgrep/")
    name = parts[3]
    if kind == "raw output":
        if not name.endswith(".semgrep.json") or name.endswith(".semgrep-summary.json"):
            raise HelperError("raw output must be named <WP-ID>.semgrep.json or integration.semgrep.json")
        base = name[: -len(".semgrep.json")]
    elif kind == "summary output":
        if not name.endswith(".semgrep-summary.json"):
            raise HelperError("summary output must be named <WP-ID>.semgrep-summary.json or integration.semgrep-summary.json")
        base = name[: -len(".semgrep-summary.json")]
    else:
        base = Path(name).stem
    if not EVIDENCE_BASE_RE.match(base):
        raise HelperError(f"{kind} path must use a package WP-ID or integration evidence stem")
    if resolved.exists() and resolved.is_symlink():
        raise HelperError(f"{kind} path must not be a symlink")
    if must_exist and not resolved.is_file():
        raise HelperError(f"{kind} file does not exist: {name}")
    return resolved


def _validate_evidence_pair(raw_value: str, summary_value: str, *, repo_root: Path, must_exist: bool) -> tuple[Path, Path]:
    raw_path = _validate_evidence_path(raw_value, repo_root=repo_root, kind="raw output", must_exist=must_exist)
    summary_path = _validate_evidence_path(summary_value, repo_root=repo_root, kind="summary output", must_exist=False)
    raw_rel = raw_path.relative_to(repo_root).parts
    summary_rel = summary_path.relative_to(repo_root).parts
    raw_base = raw_rel[3][: -len(".semgrep.json")]
    summary_base = summary_rel[3][: -len(".semgrep-summary.json")]
    if raw_rel[1] != summary_rel[1] or raw_base != summary_base:
        raise HelperError("raw and summary evidence paths must share feature and stem")
    summary_parent = summary_path.parent.resolve(strict=False)
    if not is_relative_to(summary_parent, repo_root):
        raise HelperError("summary output parent must stay under the repository/worktree root")
    return raw_path, summary_path


def _default_summary_path(raw_path: Path) -> Path:
    name = raw_path.name[: -len(".semgrep.json")] + ".semgrep-summary.json"
    return raw_path.with_name(name)


def _git_dir_for_worktree(path: Path) -> Path | None:
    dotgit = path / ".git"
    if dotgit.is_dir():
        return dotgit
    if dotgit.is_file():
        text = dotgit.read_text(encoding="utf-8", errors="replace").strip()
        if text.startswith("gitdir:"):
            gitdir = Path(text.split(":", 1)[1].strip())
            return (path / gitdir).resolve() if not gitdir.is_absolute() else gitdir.resolve()
    return None


def _read_git_commit(path: Path) -> str | None:
    gitdir = _git_dir_for_worktree(path)
    if gitdir is None:
        return None
    head = gitdir / "HEAD"
    if not head.is_file():
        return None
    text = head.read_text(encoding="utf-8", errors="replace").strip()
    if re.fullmatch(r"[0-9a-fA-F]{40}", text):
        return text.lower()
    if text.startswith("ref:"):
        ref = text.split(":", 1)[1].strip()
        ref_path = gitdir / ref
        if ref_path.is_file():
            value = ref_path.read_text(encoding="utf-8", errors="replace").strip()
            if re.fullmatch(r"[0-9a-fA-F]{40}", value):
                return value.lower()
        packed_refs = gitdir / "packed-refs"
        if packed_refs.is_file():
            for line in packed_refs.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.startswith("#") or not line.strip():
                    continue
                pieces = line.split()
                if len(pieces) == 2 and pieces[1] == ref and re.fullmatch(r"[0-9a-fA-F]{40}", pieces[0]):
                    return pieces[0].lower()
    return None


def _rule_files(rules_root: Path) -> list[Path]:
    files = [path for path in rules_root.rglob("*") if path.is_file() and path.suffix.lower() in {".yml", ".yaml"}]
    return sorted(files, key=lambda item: item.relative_to(rules_root).as_posix())


def _content_fingerprint(rules_root: Path, files: Iterable[Path] | None = None) -> str:
    digest = hashlib.sha256()
    selected = list(files) if files is not None else _rule_files(rules_root)
    for path in selected:
        rel = path.relative_to(rules_root).as_posix().encode("utf-8")
        digest.update(rel)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _fingerprint_source(rules_root: Path, files: Iterable[Path] | None = None) -> dict[str, str | None]:
    commit = _read_git_commit(rules_root)
    fingerprint = _content_fingerprint(rules_root, files)
    return {
        "community_rules_commit": commit,
        "content_fingerprint": fingerprint,
        "source": "git-commit" if commit else "content-fingerprint",
    }


def _flatten_metadata_terms(value: Any) -> set[str]:
    terms: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            terms.add(str(key))
            terms.update(_flatten_metadata_terms(item))
    elif isinstance(value, list):
        for item in value:
            terms.update(_flatten_metadata_terms(item))
    elif value is not None:
        terms.add(str(value))
    return terms


def _normalize_term(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def _path_terms(path: Path) -> set[str]:
    terms: set[str] = set()
    for part in path.parts:
        for token in re.split(r"[^A-Za-z0-9]+", part):
            if token:
                terms.add(token)
        terms.add(part)
    return terms


def _extract_rule_file_entry(path: Path, rules_root: Path) -> dict[str, Any]:
    rel = path.relative_to(rules_root)
    data = _load_yaml(path, label="Semgrep rule")
    if not isinstance(data, dict):
        raise HelperError(f"Semgrep rule file must contain a mapping: {rel.as_posix()}")
    rules = data.get("rules")
    if rules is None:
        return {
            "path": rel.as_posix(),
            "absolute_path": str(path.resolve()),
            "config_path": str(path.parent.resolve()),
            "languages": [],
            "rule_ids": [],
            "metadata_terms": sorted(_path_terms(rel)),
            "rules_count": 0,
        }
    if not isinstance(rules, list):
        raise HelperError(f"Semgrep rule file has non-list rules: {rel.as_posix()}")
    languages: set[str] = set()
    ids: list[str] = []
    metadata_terms: set[str] = set(_path_terms(rel))
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        rule_id = rule.get("id")
        if rule_id is not None:
            ids.append(_sanitize_string(rule_id, 256))
            metadata_terms.add(str(rule_id))
        rule_languages = rule.get("languages", [])
        if isinstance(rule_languages, str):
            rule_languages = [rule_languages]
        if isinstance(rule_languages, list):
            for language in rule_languages:
                if language is not None:
                    text = _sanitize_string(language, 80).lower()
                    languages.add(text)
                    metadata_terms.add(text)
        metadata = rule.get("metadata")
        metadata_terms.update(_flatten_metadata_terms(metadata))
    return {
        "path": rel.as_posix(),
        "absolute_path": str(path.resolve()),
        "config_path": str(path.parent.resolve()),
        "languages": sorted(languages),
        "rule_ids": ids[:200],
        "metadata_terms": sorted({_sanitize_string(term, 120) for term in metadata_terms if str(term).strip()}),
        "rules_count": len(rules),
    }


def _build_index(rules_root: Path) -> dict[str, Any]:
    files = _rule_files(rules_root)
    freshness = _fingerprint_source(rules_root, files)
    entries = [_extract_rule_file_entry(path, rules_root) for path in files]
    return {
        "version": VERSION,
        "rules_root": str(rules_root.resolve()),
        "freshness": freshness,
        "files": entries,
    }


def _load_index(index_path: Path) -> dict[str, Any]:
    if not index_path.is_file():
        raise HelperError("Semgrep rules index is missing; run the helper index command first")
    data = _load_json(index_path)
    if not isinstance(data, dict) or data.get("version") != VERSION:
        raise HelperError("Semgrep rules index has an unsupported format")
    if not isinstance(data.get("files"), list):
        raise HelperError("Semgrep rules index is missing file entries")
    return data


def _validate_index_current(index: dict[str, Any], rules_root: Path) -> None:
    indexed_root = Path(str(index.get("rules_root", ""))).resolve(strict=False)
    if indexed_root != rules_root.resolve(strict=True):
        raise HelperError("Semgrep rules index was built for a different rules root; rerun index")
    current = _fingerprint_source(rules_root)
    stored = index.get("freshness") if isinstance(index.get("freshness"), dict) else {}
    if stored.get("community_rules_commit") != current.get("community_rules_commit"):
        raise HelperError("Semgrep rules index commit is stale; rerun index")
    if stored.get("content_fingerprint") != current.get("content_fingerprint"):
        raise HelperError("Semgrep rules index content fingerprint is stale; rerun index")


def _match_stack(entry: dict[str, Any], stack: str) -> bool:
    query = _normalize_term(stack)
    if not query:
        return False
    terms: set[str] = set()
    for key in ("languages", "rule_ids", "metadata_terms"):
        values = entry.get(key, [])
        if isinstance(values, list):
            for value in values:
                normalized = _normalize_term(value)
                if normalized:
                    terms.add(normalized)
    path = entry.get("path")
    if isinstance(path, str):
        terms.update({_normalize_term(part) for part in Path(path).parts})
    return query in terms or any(query and query == term for term in terms)


def _profile_from_matches(index_path: Path, index: dict[str, Any], stacks: list[str], matches: dict[str, list[str]]) -> dict[str, Any]:
    freshness = index.get("freshness") if isinstance(index.get("freshness"), dict) else {}
    return {
        "version": VERSION,
        "rules-index": {
            "community-rules-commit": freshness.get("community_rules_commit"),
            "content-fingerprint": freshness.get("content_fingerprint"),
            "fingerprint-source": freshness.get("source"),
            "index-path": str(index_path.resolve()),
            "rules-root": str(index.get("rules_root", "")),
        },
        "stacks": {stack: {"semgrep-configs": matches.get(stack, [])} for stack in stacks},
    }


def _load_stack_profile(path: Path) -> dict[str, Any]:
    data = _load_yaml(path, label="stack profile")
    if not isinstance(data, dict) or data.get("version") != VERSION:
        raise HelperError("stack profile must be a version: 1 mapping")
    stacks = data.get("stacks")
    if not isinstance(stacks, dict) or not stacks:
        raise HelperError("stack profile must contain stacks with semgrep-configs")
    return data


def _profile_configs(profile: dict[str, Any]) -> list[str]:
    configs: list[str] = []
    stacks = profile.get("stacks") if isinstance(profile.get("stacks"), dict) else {}
    for stack_name in sorted(stacks):
        stack = stacks[stack_name]
        if not isinstance(stack, dict):
            raise HelperError(f"stack profile entry is malformed: {_sanitize_string(stack_name, 80)}")
        values = stack.get("semgrep-configs")
        if not isinstance(values, list) or not values:
            raise HelperError(f"stack profile entry has no semgrep-configs: {_sanitize_string(stack_name, 80)}")
        for value in values:
            if not isinstance(value, str):
                raise HelperError("stack profile config paths must be strings")
            configs.append(value)
    deduped: list[str] = []
    seen: set[str] = set()
    for config in configs:
        if config not in seen:
            deduped.append(config)
            seen.add(config)
    return deduped


def _allowed_index_config_paths(index: dict[str, Any], rules_root: Path) -> set[Path]:
    rules_root = rules_root.resolve(strict=True)
    allowed: set[Path] = set()
    files = index.get("files")
    if not isinstance(files, list):
        raise HelperError("Semgrep rules index is missing file entries")
    for entry in files:
        if not isinstance(entry, dict):
            continue
        config = entry.get("config_path")
        if not isinstance(config, str) or not config.strip():
            continue
        _reject_registry_config(config, "indexed config")
        raw = Path(config).expanduser()
        _reject_path_traversal(raw, "indexed config")
        if not raw.is_absolute():
            raise HelperError("indexed config paths must be absolute local paths")
        try:
            resolved = raw.resolve(strict=True)
        except FileNotFoundError as exc:
            raise HelperError("indexed config path does not exist; rerun index") from exc
        if not is_relative_to(resolved, rules_root):
            raise HelperError("indexed config path escapes the bound rules root; rerun index")
        if not (resolved.is_file() or resolved.is_dir()):
            raise HelperError("indexed config path must be a file or directory")
        allowed.add(resolved)
    return allowed


def _validate_profile_freshness(profile: dict[str, Any]) -> set[Path]:
    rules_index = profile.get("rules-index")
    if not isinstance(rules_index, dict):
        raise HelperError("stack profile is missing rules-index binding")
    index_path_text = rules_index.get("index-path")
    rules_root_text = rules_index.get("rules-root")
    if not isinstance(index_path_text, str) or not index_path_text:
        raise HelperError("stack profile is missing rules-index.index-path")
    if not isinstance(rules_root_text, str) or not rules_root_text:
        raise HelperError("stack profile is missing rules-index.rules-root")
    expected_root = _expected_rules_root()
    expected_index = _expected_index_path()
    index_path = Path(index_path_text).expanduser().resolve(strict=False)
    rules_root = Path(rules_root_text).expanduser().resolve(strict=False)
    if rules_root != expected_root:
        raise HelperError("stack profile rules root must match the shared plugin Semgrep rules cache")
    if index_path != expected_index:
        raise HelperError("stack profile index path must match the shared plugin Semgrep rules cache")
    if not index_path.is_file():
        raise HelperError("stack profile points at a missing rules index")
    try:
        rules_root = rules_root.resolve(strict=True)
    except FileNotFoundError as exc:
        raise HelperError("stack profile points at a missing shared plugin rules root") from exc
    index = _load_index(index_path)
    _validate_index_current(index, rules_root)
    stored = index.get("freshness") if isinstance(index.get("freshness"), dict) else {}
    if rules_index.get("community-rules-commit") != stored.get("community_rules_commit"):
        raise HelperError("stack profile commit binding is stale; rerun retrieve")
    if rules_index.get("content-fingerprint") != stored.get("content_fingerprint"):
        raise HelperError("stack profile fingerprint binding is stale; rerun retrieve")
    return _allowed_index_config_paths(index, rules_root)


def _validate_local_config(value: str, *, repo_root: Path, label: str, require_absolute: bool) -> Path:
    _reject_registry_config(value, label)
    raw = Path(value).expanduser()
    _reject_path_traversal(raw, label)
    if require_absolute and not raw.is_absolute():
        raise HelperError(f"{label} must be an absolute local path")
    path = raw if raw.is_absolute() else repo_root / raw
    try:
        resolved = path.resolve(strict=True)
    except FileNotFoundError as exc:
        raise HelperError(f"{label} does not exist: {raw.name if raw.name else raw}") from exc
    if not (resolved.is_file() or resolved.is_dir()):
        raise HelperError(f"{label} must be a file or directory")
    return resolved


def _load_excluded_rules(path: Path | None) -> list[str]:
    if path is None or not path.exists():
        return []
    if path.is_symlink():
        raise HelperError("excluded rules file must not be a symlink")
    data = _load_yaml(path, label="excluded rules")
    if not isinstance(data, dict):
        raise HelperError("excluded rules YAML must be a mapping")
    entries = data.get("excluded-rules", [])
    if entries is None:
        return []
    if not isinstance(entries, list):
        raise HelperError("excluded-rules must be a list")
    ids: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise HelperError("each excluded-rules item must be a mapping")
        rule_id = entry.get("id")
        if not isinstance(rule_id, str) or not rule_id.strip():
            raise HelperError("each excluded-rules item must contain an id")
        _validate_rule_id(rule_id)
        ids.append(rule_id.strip())
    return ids


def _validate_rule_id(rule_id: str) -> None:
    text = rule_id.strip()
    lowered = text.lower()
    if lowered.startswith(REGISTRY_PREFIXES) or "://" in lowered:
        raise HelperError("excluded rule id must not be a registry or URL value")
    if any(separator in text for separator in SHELL_SEPARATORS):
        raise HelperError(f"unsafe excluded rule id: {_sanitize_string(text, 120)}")
    if not RULE_ID_RE.fullmatch(text):
        raise HelperError(f"unsafe excluded rule id: {_sanitize_string(text, 120)}")


def _validate_local_rules_path(path: Path | None, *, repo_root: Path) -> Path | None:
    if path is None:
        return None
    allowed = (repo_root / LOCAL_RULES_RELATIVE).resolve(strict=False)
    if path.resolve(strict=False) != allowed:
        raise HelperError("local rules must use .superdeveloper/semgrep/local-rules.yml")
    return path


def _validate_local_rules(path: Path | None) -> Path | None:
    if path is None or not path.exists():
        return None
    if path.is_symlink():
        raise HelperError("local rules file must not be a symlink")
    data = _load_yaml(path, label="local rules")
    if not isinstance(data, dict):
        raise HelperError("local rules YAML must be a mapping")
    rules = data.get("rules")
    if rules is not None and not isinstance(rules, list):
        raise HelperError("local rules YAML has non-list rules")
    return path.resolve(strict=True)


def _semgrep_executable(value: str) -> str:
    if " ci" in value or value.strip().endswith("/ci"):
        raise HelperError("semgrep ci mode is not supported by this offline helper")
    _reject_shellish(value, "semgrep executable")
    candidate = Path(value)
    if candidate.is_absolute() or os.sep in value:
        if not candidate.exists():
            raise HelperError("semgrep executable is missing")
        return str(candidate)
    resolved = shutil.which(value)
    if resolved is None:
        raise HelperError("semgrep executable is missing")
    return resolved


def _scan_argv(*, semgrep_bin: str, configs: list[Path], excluded_rule_ids: list[str], raw_output: Path, target: Path) -> list[str]:
    argv = [semgrep_bin, "scan", "--metrics=off", "--disable-version-check"]
    for config in configs:
        argv.extend(["--config", str(config)])
    for rule_id in excluded_rule_ids:
        argv.extend(["--exclude-rule", rule_id])
    argv.extend(["--json", "--output", str(raw_output), str(target)])
    return argv


def _narrow_metadata(metadata: Any) -> dict[str, Any]:
    if not isinstance(metadata, dict):
        return {}
    selected: dict[str, Any] = {}
    for key in ("cwe", "owasp", "category", "technology", "confidence", "impact", "likelihood"):
        if key not in metadata:
            continue
        value = metadata.get(key)
        if isinstance(value, (str, int, float, bool)) or value is None:
            selected[key] = _sanitize_string(value, 240)
        elif isinstance(value, list):
            selected[key] = [_sanitize_string(item, 160) for item in value[:20]]
        elif isinstance(value, dict):
            selected[key] = {
                _sanitize_string(k, 80): _sanitize_string(v, 160)
                for k, v in list(value.items())[:20]
                if isinstance(k, (str, int, float, bool))
            }
    return selected


def _finding_fingerprint(result: dict[str, Any], extra: dict[str, Any]) -> str:
    for container in (extra, result):
        for key in ("fingerprint", "match_based_id", "syntactic_id"):
            value = container.get(key)
            if isinstance(value, str) and value.strip():
                return _sanitize_string(value, 256)
    return ""


def _extract_findings(raw_data: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_data, dict):
        raise HelperError("Semgrep JSON must be a mapping")
    results = raw_data.get("results", [])
    if results is None:
        results = []
    if not isinstance(results, list):
        raise HelperError("Semgrep JSON results must be a list")
    if len(results) > MAX_RESULTS:
        raise HelperError(f"Refusing oversized Semgrep result set: {len(results)} results")
    findings: list[dict[str, Any]] = []
    for index, result in enumerate(results, start=1):
        if not isinstance(result, dict):
            continue
        extra = result.get("extra") if isinstance(result.get("extra"), dict) else {}
        start = result.get("start") if isinstance(result.get("start"), dict) else {}
        line = start.get("line", 0)
        col = start.get("col", 0)
        try:
            line_int = max(0, int(line))
        except (TypeError, ValueError):
            line_int = 0
        try:
            col_int = max(0, int(col))
        except (TypeError, ValueError):
            col_int = 0
        metadata = _narrow_metadata(extra.get("metadata"))
        findings.append(
            {
                "ref": f"F{index:03d}",
                "severity": _sanitize_string(extra.get("severity") or result.get("severity") or "UNKNOWN", 40).upper() or "UNKNOWN",
                "rule_id": _sanitize_string(result.get("check_id") or extra.get("check_id") or "unknown", 256),
                "path": _sanitize_string(result.get("path") or "", 500),
                "line": line_int,
                "col": col_int,
                "message": _first_line(extra.get("message") or result.get("message") or "", MAX_MESSAGE),
                "fingerprint": _finding_fingerprint(result, extra),
                "metadata": metadata,
            }
        )
    return findings


def _extract_scan_errors(raw_data: Any, exit_code: int | None = None) -> list[str]:
    errors: list[str] = []
    if isinstance(raw_data, dict):
        raw_errors = raw_data.get("errors", [])
        if isinstance(raw_errors, list):
            for error in raw_errors[:20]:
                if isinstance(error, dict):
                    errors.append(_first_line(error.get("message") or error.get("code") or error, 240))
                else:
                    errors.append(_first_line(error, 240))
    if exit_code not in (None, 0):
        errors.insert(0, f"semgrep exited with code {exit_code}")
    return [error for error in errors if error]


def _build_summary(raw_path: Path, raw_data: Any, *, scan_target: Path | None = None, semgrep_exit_code: int | None = None) -> dict[str, Any]:
    findings = _extract_findings(raw_data)
    raw_digest = _sha256_file(raw_path)
    severity_counts = Counter(finding["severity"] for finding in findings)
    rule_counts = Counter(finding["rule_id"] for finding in findings)
    path_counts = Counter(finding["path"] for finding in findings)
    group_counts = Counter(Path(finding["path"]).parts[0] if finding["path"] else "<unknown>" for finding in findings)
    summary: dict[str, Any] = {
        "version": VERSION,
        "raw_path": str(raw_path),
        "raw_digest": raw_digest,
        "result_count": len(findings),
        "scan_errors": _extract_scan_errors(raw_data, semgrep_exit_code),
        "severity_counts": dict(sorted(severity_counts.items())),
        "top_rules": [{"rule_id": key, "count": count} for key, count in rule_counts.most_common(SUMMARY_TOP_N)],
        "top_paths": [{"path": key, "count": count} for key, count in path_counts.most_common(SUMMARY_TOP_N)],
        "top_path_groups": [{"path_group": key, "count": count} for key, count in group_counts.most_common(SUMMARY_TOP_N)],
        "findings_index": [
            {
                "ref": finding["ref"],
                "severity": finding["severity"],
                "rule_id": finding["rule_id"],
                "location": f"{finding['path']}:{finding['line']}",
                "message": finding["message"],
                "fingerprint": finding["fingerprint"],
            }
            for finding in findings[: min(100, MAX_RESULTS)]
        ],
        "semgrep_severity_is_advisory": True,
    }
    if scan_target is not None:
        summary["scan_target"] = str(scan_target)
    summary["summary_digest"] = _sha256_bytes(_canonical_json(summary))
    return summary


def _write_summary(summary_path: Path, summary: dict[str, Any]) -> dict[str, Any]:
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(_json_dump(summary), encoding="utf-8")
    return summary


def _load_raw_for_consumption(raw_path: Path) -> tuple[Any, str]:
    raw_data = _load_json(raw_path, max_bytes=MAX_RAW_BYTES)
    digest = _sha256_file(raw_path)
    _extract_findings(raw_data)  # schema/count validation at trust boundary
    return raw_data, digest


def _computed_summary_digest(summary: dict[str, Any]) -> str:
    clone = copy.deepcopy(summary)
    clone.pop("summary_digest", None)
    return _sha256_bytes(_canonical_json(clone))


def _validate_summary_binding(raw_path: Path, summary_path: Path | None, expected_digest: str) -> dict[str, Any] | None:
    if summary_path is None or not summary_path.exists():
        return None
    data = _load_json(summary_path, max_bytes=MAX_RAW_BYTES)
    if not isinstance(data, dict):
        raise HelperError("summary JSON must be a mapping")
    if data.get("raw_digest") != expected_digest:
        raise HelperError("summary/raw digest mismatch; rerun summarize")
    stored_summary_digest = data.get("summary_digest")
    if isinstance(stored_summary_digest, str) and stored_summary_digest != _computed_summary_digest(data):
        raise HelperError("summary digest mismatch; rerun summarize")
    return data


def _summary_path_for_consumption(raw_path: Path, summary_value: str | None, *, repo_root: Path) -> Path | None:
    if summary_value:
        summary_path = _validate_evidence_path(summary_value, repo_root=repo_root, kind="summary output", must_exist=False)
        raw_rel = raw_path.relative_to(repo_root).parts
        summary_rel = summary_path.relative_to(repo_root).parts
        if raw_rel[1] != summary_rel[1] or raw_rel[3][: -len(".semgrep.json")] != summary_rel[3][: -len(".semgrep-summary.json")]:
            raise HelperError("raw and summary evidence paths must share feature and stem")
        return summary_path
    default = _default_summary_path(raw_path)
    return default if default.exists() else None


def _print_json(data: Any) -> None:
    print(_json_dump(data), end="")


def command_index(args: argparse.Namespace) -> int:
    rules_root = _resolve_existing_path(args.rules_root, repo_root=None, label="rules root")
    if not rules_root.is_dir():
        raise HelperError("rules root must be an existing local directory")
    index_path = Path(args.index).expanduser()
    _reject_path_traversal(index_path, "index")
    index_path = index_path.resolve(strict=False)
    index = _build_index(rules_root)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(_json_dump(index), encoding="utf-8")
    _print_json(
        {
            "index": str(index_path),
            "rules_root": str(rules_root),
            "rule_files": len(index["files"]),
            "freshness": index["freshness"],
        }
    )
    return 0


def command_retrieve(args: argparse.Namespace) -> int:
    repo_root = _repo_root_from_arg(args.repo_root)
    rules_root = _resolve_existing_path(args.rules_root, repo_root=None, label="rules root")
    if not rules_root.is_dir():
        raise HelperError("rules root must be an existing local directory")
    index_raw = Path(args.index).expanduser()
    _reject_path_traversal(index_raw, "index")
    index_path = index_raw.resolve(strict=False)
    index = _load_index(index_path)
    _validate_index_current(index, rules_root)
    stacks = list(args.stack or [])
    if not stacks:
        raise HelperError("retrieve requires at least one --stack")
    for stack in stacks:
        if not SAFE_STACK_RE.fullmatch(stack):
            raise HelperError(f"unsafe stack name: {_sanitize_string(stack, 80)}")
    matches: dict[str, list[str]] = {}
    for stack in stacks:
        config_paths: set[str] = set()
        for entry in index["files"]:
            if isinstance(entry, dict) and _match_stack(entry, stack):
                config = entry.get("config_path")
                if isinstance(config, str):
                    resolved = _validate_local_config(config, repo_root=repo_root, label="indexed config", require_absolute=True)
                    config_paths.add(str(resolved))
        matches[stack] = sorted(config_paths)
    profile = _profile_from_matches(index_path, index, stacks, matches)
    if args.write_profile:
        profile_path = _validate_profile_path(args.write_profile, repo_root=repo_root)
        _write_yaml(profile_path, profile)
    _print_json(profile)
    return 0


def command_scan(args: argparse.Namespace, *, runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run) -> int:
    repo_root = _repo_root_from_arg(args.repo_root)
    profile_path = _resolve_existing_path(args.profile, repo_root=repo_root, label="stack profile")
    profile = _load_stack_profile(profile_path)
    allowed_profile_configs = _validate_profile_freshness(profile)
    target = _validate_target(args.target, repo_root=repo_root)
    raw_path, summary_path = _validate_evidence_pair(args.json_output, args.summary_output, repo_root=repo_root, must_exist=False)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    configs = []
    for config in _profile_configs(profile):
        resolved_config = _validate_local_config(config, repo_root=repo_root, label="profile config", require_absolute=True)
        if resolved_config not in allowed_profile_configs:
            raise HelperError("profile config is not in the current rules index; rerun retrieve")
        configs.append(resolved_config)
    local_rules_path = _resolve_optional_project_path(args.local_rules, repo_root=repo_root, label="local rules") if args.local_rules else None
    local_rules_path = _validate_local_rules_path(local_rules_path, repo_root=repo_root)
    local_rules = _validate_local_rules(local_rules_path)
    if local_rules is not None:
        configs.append(local_rules)
    excluded_path = _resolve_optional_project_path(args.excluded_rules, repo_root=repo_root, label="excluded rules") if args.excluded_rules else None
    excluded_rule_ids = _load_excluded_rules(excluded_path)
    semgrep_bin = _semgrep_executable(args.semgrep_bin)
    argv = _scan_argv(semgrep_bin=semgrep_bin, configs=configs, excluded_rule_ids=excluded_rule_ids, raw_output=raw_path, target=target)
    try:
        result = runner(
            argv,
            cwd=str(repo_root),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            shell=False,
        )
    except FileNotFoundError as exc:
        raise HelperError("semgrep executable is missing") from exc
    if not raw_path.is_file():
        stderr = _first_line(getattr(result, "stderr", ""), 300)
        raise HelperError(f"semgrep did not write raw JSON output{': ' + stderr if stderr else ''}")
    raw_data = _load_json(raw_path, max_bytes=MAX_RAW_BYTES)
    summary = _build_summary(raw_path, raw_data, scan_target=target, semgrep_exit_code=result.returncode)
    _write_summary(summary_path, summary)
    if result.returncode != 0:
        stderr = _first_line(getattr(result, "stderr", ""), 300)
        raise HelperError(f"semgrep scan failed with exit code {result.returncode}{': ' + stderr if stderr else ''}")
    print(
        f"Semgrep scan complete: findings={summary['result_count']} errors={len(summary['scan_errors'])} "
        f"raw_digest={summary['raw_digest']} summary_digest={summary['summary_digest']}"
    )
    return 0


def command_summarize(args: argparse.Namespace) -> int:
    repo_root = _repo_root_from_arg(args.repo_root)
    raw_path = _validate_evidence_path(args.json_output, repo_root=repo_root, kind="raw output", must_exist=True)
    summary_value = args.summary_output or str(_default_summary_path(raw_path))
    raw_path, summary_path = _validate_evidence_pair(str(raw_path), summary_value, repo_root=repo_root, must_exist=True)
    raw_data = _load_json(raw_path, max_bytes=MAX_RAW_BYTES)
    target = _validate_target(args.target, repo_root=repo_root) if args.target else None
    summary = _build_summary(raw_path, raw_data, scan_target=target)
    _write_summary(summary_path, summary)
    _print_json(summary)
    return 0


def _filtered_findings(findings: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    selected = findings
    if args.severity:
        allowed = {severity.upper() for severity in args.severity}
        selected = [finding for finding in selected if finding["severity"].upper() in allowed]
    if args.rule_id:
        selected = [finding for finding in selected if finding["rule_id"] == args.rule_id]
    if args.path_contains:
        needle = args.path_contains.lower()
        selected = [finding for finding in selected if needle in finding["path"].lower()]
    return selected


def command_list_findings(args: argparse.Namespace) -> int:
    repo_root = _repo_root_from_arg(args.repo_root)
    raw_path = _validate_evidence_path(args.json_output, repo_root=repo_root, kind="raw output", must_exist=True)
    raw_data, raw_digest = _load_raw_for_consumption(raw_path)
    summary_path = _summary_path_for_consumption(raw_path, args.summary_output, repo_root=repo_root)
    _validate_summary_binding(raw_path, summary_path, raw_digest)
    findings = _filtered_findings(_extract_findings(raw_data), args)
    limit = min(max(1, args.limit), LIST_LIMIT_MAX)
    rows = [
        {
            "ref": finding["ref"],
            "severity": finding["severity"],
            "rule_id": finding["rule_id"],
            "location": f"{finding['path']}:{finding['line']}",
            "message": finding["message"],
            "fingerprint": finding["fingerprint"],
        }
        for finding in findings[:limit]
    ]
    _print_json({"raw_digest": raw_digest, "total_matching": len(findings), "limit": limit, "findings": rows})
    return 0


def _resolve_context_file(finding_path: str, *, repo_root: Path, target: Path) -> Path:
    if not finding_path:
        raise HelperError("finding path is empty; cannot read context")
    raw = Path(finding_path)
    _reject_path_traversal(raw, "finding path")
    candidates = [raw] if raw.is_absolute() else [repo_root / raw, target / raw]
    saw_escape = False
    saw_non_file = False
    for candidate in candidates:
        try:
            resolved = candidate.resolve(strict=True)
        except FileNotFoundError:
            continue
        if not is_relative_to(resolved, target):
            saw_escape = True
            continue
        if not resolved.is_file():
            saw_non_file = True
            continue
        if resolved.stat().st_size > MAX_RAW_BYTES:
            raise HelperError("finding context file is too large")
        return resolved
    if saw_escape:
        raise HelperError("finding context path escapes the scan target")
    if saw_non_file:
        raise HelperError("finding context path is not a file")
    raise HelperError("finding context path does not exist under the scan target")


def _context_excerpt(finding: dict[str, Any], *, repo_root: Path, target: Path, context_lines: int) -> list[dict[str, Any]]:
    if context_lines <= 0:
        return []
    context_lines = min(context_lines, MAX_CONTEXT_LINES)
    source = _resolve_context_file(finding["path"], repo_root=repo_root, target=target)
    lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    line_no = max(1, int(finding.get("line") or 1))
    start = max(1, line_no - context_lines)
    end = min(len(lines), line_no + context_lines)
    return [
        {"line": number, "text": _sanitize_string(lines[number - 1], 240)}
        for number in range(start, end + 1)
    ]


def _validate_expected_summary_digest(value: str | None) -> str:
    if not isinstance(value, str) or not value.strip():
        raise HelperError("show-finding context requires --expected-summary-digest")
    digest = value.strip().lower()
    if not SUMMARY_DIGEST_RE.fullmatch(digest):
        raise HelperError("expected summary digest must be a 64-character sha256 hex digest")
    return digest


def _target_for_show(args: argparse.Namespace, *, repo_root: Path, summary: dict[str, Any] | None) -> Path:
    if not args.target:
        raise HelperError("show-finding context requires explicit --target")
    if summary is None:
        raise HelperError("show-finding context requires a valid summary file")
    if summary.get("version") != VERSION:
        raise HelperError("show-finding context requires a current summary binding; rerun summarize")
    expected_digest = _validate_expected_summary_digest(args.expected_summary_digest)
    current_digest = summary.get("summary_digest")
    if not isinstance(current_digest, str):
        raise HelperError("show-finding context requires a digest-bound summary; rerun summarize")
    if current_digest.lower() != expected_digest:
        raise HelperError("summary digest does not match --expected-summary-digest")
    scan_target = summary.get("scan_target")
    if not isinstance(scan_target, str) or not scan_target.strip():
        raise HelperError("show-finding context requires a summary scan_target binding")
    explicit_target = _validate_target(args.target, repo_root=repo_root)
    summary_target = _validate_target(scan_target, repo_root=repo_root)
    if explicit_target != summary_target:
        raise HelperError("--target must match the summary scan_target; refusing widened context")
    return explicit_target


def command_show_finding(args: argparse.Namespace) -> int:
    repo_root = _repo_root_from_arg(args.repo_root)
    raw_path = _validate_evidence_path(args.json_output, repo_root=repo_root, kind="raw output", must_exist=True)
    raw_data, raw_digest = _load_raw_for_consumption(raw_path)
    summary_path = _summary_path_for_consumption(raw_path, args.summary_output, repo_root=repo_root)
    summary = _validate_summary_binding(raw_path, summary_path, raw_digest)
    findings = _extract_findings(raw_data)
    selected = [finding for finding in findings if finding["ref"] == args.finding or (finding["fingerprint"] and finding["fingerprint"] == args.finding)]
    if len(selected) != 1:
        raise HelperError(f"finding selector must match exactly one finding; matched {len(selected)}")
    finding = selected[0]
    # No-context detail is safe without target binding; context reads must not fall back to repo root.
    context: list[dict[str, Any]] = []
    if args.context_lines > 0:
        target = _target_for_show(args, repo_root=repo_root, summary=summary)
        context = _context_excerpt(finding, repo_root=repo_root, target=target, context_lines=args.context_lines)
    elif args.target:
        _validate_target(args.target, repo_root=repo_root)
    detail = {
        "raw_digest": raw_digest,
        "finding": {
            "ref": finding["ref"],
            "severity": finding["severity"],
            "rule_id": finding["rule_id"],
            "location": f"{finding['path']}:{finding['line']}:{finding['col']}",
            "message": finding["message"],
            "fingerprint": finding["fingerprint"],
            "metadata": finding["metadata"],
            "context": context,
        },
        "semgrep_severity_is_advisory": True,
    }
    _print_json(detail)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Super Developer offline Semgrep helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    index = subparsers.add_parser("index", help="index already-local community Semgrep rules")
    index.add_argument("--rules-root", required=True)
    index.add_argument("--index", required=True)
    index.set_defaults(func=command_index)

    retrieve = subparsers.add_parser("retrieve", help="retrieve local configs for detected stacks")
    retrieve.add_argument("--index", required=True)
    retrieve.add_argument("--rules-root", required=True)
    retrieve.add_argument("--stack", action="append", required=True)
    retrieve.add_argument("--write-profile")
    retrieve.add_argument("--repo-root")
    retrieve.set_defaults(func=command_retrieve)

    scan = subparsers.add_parser("scan", help="run privacy-preserving local Semgrep scan")
    scan.add_argument("--profile", required=True)
    scan.add_argument("--excluded-rules")
    scan.add_argument("--local-rules", default=".superdeveloper/semgrep/local-rules.yml")
    scan.add_argument("--target", required=True)
    scan.add_argument("--json-output", required=True)
    scan.add_argument("--summary-output", required=True)
    scan.add_argument("--semgrep-bin", default=os.environ.get("SEMGREP_BIN", "semgrep"))
    scan.add_argument("--repo-root")
    scan.set_defaults(func=command_scan)

    summarize = subparsers.add_parser("summarize", help="write bounded summary JSON for raw Semgrep output")
    summarize.add_argument("--json-output", required=True)
    summarize.add_argument("--summary-output")
    summarize.add_argument("--target")
    summarize.add_argument("--repo-root")
    summarize.set_defaults(func=command_summarize)

    list_findings = subparsers.add_parser("list-findings", help="list bounded Semgrep findings")
    list_findings.add_argument("--json-output", required=True)
    list_findings.add_argument("--summary-output")
    list_findings.add_argument("--severity", action="append")
    list_findings.add_argument("--rule-id")
    list_findings.add_argument("--path-contains")
    list_findings.add_argument("--limit", type=int, default=20)
    list_findings.add_argument("--repo-root")
    list_findings.set_defaults(func=command_list_findings)

    show = subparsers.add_parser("show-finding", help="show one bounded finding detail")
    show.add_argument("--json-output", required=True)
    show.add_argument("--summary-output")
    show.add_argument("--finding", required=True)
    show.add_argument("--context-lines", type=int, default=0)
    show.add_argument("--target")
    show.add_argument("--expected-summary-digest", help="required with --context-lines > 0; must match the trusted summary_digest")
    show.add_argument("--repo-root")
    show.set_defaults(func=command_show_finding)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args) or 0)
    except HelperError as exc:
        eprint(f"error: {exc}")
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
