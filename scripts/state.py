#!/usr/bin/env python3
"""Validate, resume, and atomically checkpoint an Electrical Engineering KB state."""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import os
from pathlib import Path
import sqlite3
import sys
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment diagnostic
    raise SystemExit("PyYAML is required; run with the workspace Python environment") from exc


STATE_REL = Path("00_System/runtime/CURRENT_STATE.yaml")
PREVIOUS_REL = Path("00_System/runtime/CURRENT_STATE.previous.yaml")
LOG_REL = Path("00_System/runtime/SESSION_LOG.md")
MODES = {"focus", "review", "solve", "reflect", "maintenance", "idle"}
REVIEW_WORKFLOWS = {"review", "candidate-review", "knowledge-pack"}
REVIEW_REFERENCE_KEYS = {
    "candidate_id", "review_path", "knowledge_pack_path", "pack_id",
    "review_object_id", "review_object_ids",
}
REQUIRED = {
    "schema_version", "state_revision", "workspace_id", "workspace_version", "skill",
    "active_session", "current_mode", "active_source", "active_chapter", "active_topic",
    "current_pdf_page", "active_workflow", "workflow_stage", "pending_candidates",
    "pending_review", "deferred_items", "last_completed_action", "last_canonical_object",
    "next_action", "dirty_index", "stale_reading_notes", "last_validation_status", "updated_at",
}


class StateError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def envelope(ok: bool, op: str, data: Any = None, warnings: list[Any] | None = None,
             error: dict[str, Any] | None = None) -> None:
    print(json.dumps({"api_version": "1", "ok": ok, "op": op, "data": data,
                      "warnings": warnings or [], "error": error}, ensure_ascii=False))


def workspace_path(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    if not (root / "AGENTS.md").is_file():
        raise StateError("NOT_A_WORKSPACE", "workspace root must contain AGENTS.md", {"path": str(root)})
    return root


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise StateError("STATE_MISSING", "CURRENT_STATE.yaml is missing", {"path": str(path)}) from exc
    except (OSError, yaml.YAMLError) as exc:
        raise StateError("STATE_UNREADABLE", "CURRENT_STATE.yaml cannot be parsed", {"reason": str(exc)}) from exc
    if not isinstance(data, dict):
        raise StateError("STATE_INVALID", "CURRENT_STATE.yaml must contain a mapping")
    return data


def validate_state(data: dict[str, Any]) -> None:
    missing = sorted(REQUIRED - set(data))
    if missing:
        raise StateError("STATE_INVALID", "required state fields are missing", {"missing": missing})
    if data["schema_version"] != 1:
        raise StateError("STATE_INVALID", "unsupported state schema_version")
    if not isinstance(data["state_revision"], int) or data["state_revision"] < 1:
        raise StateError("STATE_INVALID", "state_revision must be a positive integer")
    if not isinstance(data["workspace_id"], str) or not data["workspace_id"]:
        raise StateError("STATE_INVALID", "workspace_id must be a non-empty string")
    skill = data["skill"]
    if not isinstance(skill, dict) or skill.get("name") != "electrical-learning-assistant":
        raise StateError("STATE_INVALID", "skill.name must be electrical-learning-assistant")
    if data["current_mode"] not in MODES:
        raise StateError("STATE_INVALID", "current_mode is invalid", {"allowed": sorted(MODES)})
    for key in ("pending_candidates", "deferred_items", "stale_reading_notes"):
        if not isinstance(data[key], list):
            raise StateError("STATE_INVALID", f"{key} must be a list")
    dirty = data["dirty_index"]
    if not isinstance(dirty, dict) or not isinstance(dirty.get("dirty"), bool):
        raise StateError("STATE_INVALID", "dirty_index.dirty must be boolean")

    def review_workflow(value: Any) -> bool:
        return isinstance(value, str) and value.casefold().replace("_", "-") in REVIEW_WORKFLOWS

    candidate_ids: list[str] = []
    for position, item in enumerate(data["pending_candidates"]):
        identity = item.get("candidate_id") if isinstance(item, dict) else None
        if not isinstance(identity, str) or not identity.strip():
            raise StateError("PENDING_CANDIDATE_ID_INVALID",
                             "each pending candidate must have a non-empty candidate_id",
                             {"position": position})
        candidate_ids.append(identity)
    duplicates = sorted({identity for identity in candidate_ids if candidate_ids.count(identity) > 1})
    if duplicates:
        raise StateError("PENDING_CANDIDATE_ID_DUPLICATE", "pending candidate IDs must be unique",
                         {"candidate_ids": duplicates})

    next_action = data["next_action"]
    if next_action is not None and not isinstance(next_action, dict):
        raise StateError("NEXT_ACTION_INVALID", "next_action must be a mapping or null")
    next_action = next_action or {}
    workflow = next_action.get("workflow")
    active_workflow = data.get("active_workflow")
    review_context = review_workflow(workflow) or review_workflow(active_workflow)
    references = sorted(REVIEW_REFERENCE_KEYS & set(next_action))
    if references and not review_context:
        raise StateError("NEXT_ACTION_REVIEW_REFERENCE_OUTSIDE_REVIEW",
                         "only Review or Knowledge Pack may carry pending review references",
                         {"workflow": workflow, "fields": references})

    pending_review = data["pending_review"]
    if pending_review is not None and not isinstance(pending_review, dict):
        raise StateError("PENDING_REVIEW_INVALID", "pending_review must be a mapping or null")
    if isinstance(pending_review, dict) and not review_context:
        raise StateError("PENDING_REVIEW_OUTSIDE_REVIEW",
                         "pending_review is allowed only during Review or Knowledge Pack",
                         {"active_workflow": active_workflow, "next_action_workflow": workflow})

    if "candidate_id" in next_action:
        identity = next_action.get("candidate_id")
        if not isinstance(identity, str) or not identity.strip():
            raise StateError("NEXT_ACTION_CANDIDATE_ID_INVALID",
                             "next_action.candidate_id must be a non-empty string")
        if not candidate_ids:
            raise StateError("NEXT_ACTION_CANDIDATE_WITH_EMPTY_QUEUE",
                             "next_action cannot carry candidate_id when pending_candidates is empty",
                             {"candidate_id": identity})
        if identity not in candidate_ids:
            raise StateError("NEXT_ACTION_CANDIDATE_NOT_PENDING",
                             "next_action.candidate_id must reference a current pending candidate",
                             {"candidate_id": identity, "pending_candidate_ids": sorted(candidate_ids)})

    formal_references = sorted((REVIEW_REFERENCE_KEYS - {"candidate_id"}) & set(next_action))
    if formal_references and not isinstance(pending_review, dict):
        raise StateError("NEXT_ACTION_REVIEW_REFERENCE_WITHOUT_PENDING_REVIEW",
                         "Review, pack and reviewed-object references require pending_review",
                         {"fields": formal_references})

    def check_strings(value: Any, location: str = "state") -> None:
        if isinstance(value, str) and len(value) > 1200:
            raise StateError("STATE_CONTAINS_LARGE_TEXT",
                             "runtime state must contain references and short summaries, not knowledge prose",
                             {"field": location, "length": len(value)})
        if isinstance(value, dict):
            for key, item in value.items():
                check_strings(item, f"{location}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                check_strings(item, f"{location}[{index}]")
    check_strings(data)


def frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    value = yaml.safe_load(text[4:end])
    return value if isinstance(value, dict) else {}


def reading_status(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    stale: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    reading_root = root / "10_Reading"
    if not reading_root.is_dir():
        return stale, issues
    for note in sorted(reading_root.rglob("*.md")):
        meta = frontmatter(note)
        if meta.get("reading_view") is not True:
            continue
        object_id = meta.get("source_object_id")
        reading_revision = meta.get("source_revision")
        rel = str(note.relative_to(root))
        if not isinstance(object_id, str) or not isinstance(reading_revision, int):
            issues.append({"code": "READING_METADATA_INVALID", "path": rel, "severity": "error"})
            continue
        source = root / "objects" / f"{object_id}.md"
        if not source.is_file():
            issues.append({"code": "READING_SOURCE_MISSING", "path": rel, "source_object_id": object_id,
                           "severity": "error"})
            continue
        canonical_revision = frontmatter(source).get("revision")
        if not isinstance(canonical_revision, int) or canonical_revision < reading_revision:
            issues.append({"code": "READING_REVISION_INCONSISTENT", "path": rel,
                           "reading_revision": reading_revision, "canonical_revision": canonical_revision,
                           "severity": "error"})
        elif canonical_revision > reading_revision:
            stale.append({"path": rel, "source_object_id": object_id,
                          "source_revision": reading_revision, "canonical_revision": canonical_revision})
    return stale, issues


def inspect(root: Path, state: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    source_result: dict[str, Any] | None = None
    active_source = state.get("active_source")
    if isinstance(active_source, dict):
        source_id = active_source.get("source_id")
        checksum = active_source.get("version_sha256")
        registry_path = root / "sources" / "registry" / f"{source_id}.json"
        source_result = {"source_id": source_id, "registry": str(registry_path.relative_to(root)),
                         "version_sha256": checksum, "available_locations": []}
        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            versions = [item for item in registry.get("versions", []) if item.get("sha256") == checksum]
            if len(versions) != 1:
                issues.append({"code": "ACTIVE_SOURCE_VERSION_MISSING", "severity": "error",
                               "source_id": source_id})
            else:
                for location in versions[0].get("locations", []):
                    raw = location.get("path") if isinstance(location, dict) else None
                    if (isinstance(location, dict) and location.get("base") == "kb_root"
                            and isinstance(raw, str) and not Path(raw).is_absolute()):
                        candidate = (root / raw).resolve()
                        if candidate.is_file():
                            source_result["available_locations"].append(str(candidate))
                if not source_result["available_locations"]:
                    issues.append({"code": "ACTIVE_SOURCE_UNAVAILABLE", "severity": "warning",
                                   "source_id": source_id,
                                   "action": "rebind the matching PDF through rebind_source.py"})
        except (OSError, json.JSONDecodeError, AttributeError) as exc:
            issues.append({"code": "ACTIVE_SOURCE_REGISTRY_INVALID", "severity": "error",
                           "source_id": source_id, "reason": str(exc)})

    for item in state.get("pending_candidates", []):
        path = item.get("record_path") if isinstance(item, dict) else None
        if not isinstance(path, str) or Path(path).is_absolute() or not (root / path).is_file():
            issues.append({"code": "PENDING_CANDIDATE_RECORD_MISSING", "severity": "error",
                           "candidate_id": item.get("candidate_id") if isinstance(item, dict) else None,
                           "path": path})
    pending_review = state.get("pending_review")
    if isinstance(pending_review, dict):
        path = pending_review.get("review_path")
        if not isinstance(path, str) or Path(path).is_absolute() or not (root / path).is_file():
            issues.append({"code": "PENDING_REVIEW_MISSING", "severity": "error", "path": path})

    index_state: dict[str, Any] = {"exists": False, "dirty": state["dirty_index"]["dirty"]}
    database = root / "runtime" / "index.sqlite3"
    if database.is_file():
        index_state["exists"] = True
        try:
            with sqlite3.connect(database) as connection:
                rows = dict(connection.execute("select key, value from index_state"))
            current_snapshot = json.loads(rows.get("snapshot_sha256", "null"))
            index_state["snapshot_sha256"] = current_snapshot
            expected = state["dirty_index"].get("snapshot_sha256")
            index_state["state_snapshot_matches"] = expected == current_snapshot
            if not state["dirty_index"]["dirty"] and expected and expected != current_snapshot:
                issues.append({"code": "INDEX_STATE_MISMATCH", "severity": "warning",
                               "expected": expected, "actual": current_snapshot})
        except (sqlite3.Error, json.JSONDecodeError) as exc:
            issues.append({"code": "INDEX_UNREADABLE", "severity": "warning", "reason": str(exc)})
    else:
        issues.append({"code": "INDEX_MISSING", "severity": "warning", "action": "rebuild from Markdown"})
    if state["dirty_index"]["dirty"]:
        issues.append({"code": "INDEX_DIRTY", "severity": "warning",
                       "reason": state["dirty_index"].get("reason")})

    stale, reading_issues = reading_status(root)
    issues.extend(reading_issues)
    if stale:
        issues.append({"code": "READING_NOTES_STALE", "severity": "warning", "count": len(stale)})
    return {"active_source": source_result, "index": index_state, "stale_reading_notes": stale,
            "issues": issues}


def deep_merge(base: Any, patch: Any) -> Any:
    if isinstance(base, dict) and isinstance(patch, dict):
        merged = copy.deepcopy(base)
        for key, value in patch.items():
            merged[key] = deep_merge(merged.get(key), value) if key in merged else copy.deepcopy(value)
        return merged
    return copy.deepcopy(patch)


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def yaml_text(data: dict[str, Any]) -> str:
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000)


def append_log(root: Path, state: dict[str, Any], event: str, summary: str) -> None:
    path = root / LOG_REL
    existing = path.read_text(encoding="utf-8") if path.is_file() else "# Session Log\n\n"
    source = state.get("active_source") or {}
    source_label = source.get("title") or "—"
    topic = state.get("active_topic") or state.get("active_chapter") or "—"
    objects = (state.get("last_completed_action") or {}).get("object_ids") or []
    next_summary = (state.get("next_action") or {}).get("summary") or "—"
    entry = (f"## {state['updated_at']} — {event}\n\n"
             f"- Session: `{state.get('active_session') or '—'}`\n"
             f"- Source / topic: {source_label} / {topic}\n"
             f"- Summary: {summary}\n"
             f"- Objects: {', '.join(objects) if objects else '—'}\n"
             f"- Next: {next_summary}\n\n")
    atomic_write(path, existing + entry)


def command_resume(root: Path) -> int:
    state = load_yaml(root / STATE_REL)
    validate_state(state)
    checks = inspect(root, state)
    errors = [item for item in checks["issues"] if item.get("severity") == "error"]
    warnings = [item for item in checks["issues"] if item.get("severity") == "warning"]
    data = {
        "workspace_id": state["workspace_id"],
        "state_revision": state["state_revision"],
        "active_session": state["active_session"],
        "current_mode": state["current_mode"],
        "active_source": state["active_source"],
        "active_chapter": state["active_chapter"],
        "active_topic": state["active_topic"],
        "current_pdf_page": state["current_pdf_page"],
        "active_workflow": state["active_workflow"],
        "workflow_stage": state["workflow_stage"],
        "pending_candidates": state["pending_candidates"],
        "pending_review": state["pending_review"],
        "deferred_items": state["deferred_items"],
        "last_completed_action": state["last_completed_action"],
        "last_canonical_object": state["last_canonical_object"],
        "next_action": state["next_action"],
        "last_validation_status": state["last_validation_status"],
        "checks": checks,
        "ready_to_continue": not errors and not any(item["code"] == "ACTIVE_SOURCE_UNAVAILABLE" for item in warnings),
    }
    envelope(True, "state.resume", data, warnings)
    return 0


def command_validate(root: Path) -> int:
    state = load_yaml(root / STATE_REL)
    validate_state(state)
    checks = inspect(root, state)
    errors = [item for item in checks["issues"] if item.get("severity") == "error"]
    warnings = [item for item in checks["issues"] if item.get("severity") == "warning"]
    envelope(not errors, "state.validate",
             {"valid": not errors, "state_revision": state["state_revision"], "checks": checks},
             warnings, None if not errors else {"code": "STATE_REFERENCE_ERRORS",
                                                "message": "runtime state has invalid references",
                                                "details": {"count": len(errors)}})
    return 0 if not errors else 2


def command_checkpoint(root: Path, patch_path: Path, event: str, summary: str) -> int:
    state_path = root / STATE_REL
    current = load_yaml(state_path)
    validate_state(current)
    patch = load_yaml(patch_path)
    updated = deep_merge(current, patch)
    updated["schema_version"] = 1
    updated["state_revision"] = current["state_revision"] + 1
    updated["updated_at"] = utc_now()
    stale, reading_issues = reading_status(root)
    if reading_issues:
        raise StateError("READING_STATE_INVALID", "cannot checkpoint with invalid Reading Note references",
                         {"issues": reading_issues})
    updated["stale_reading_notes"] = stale
    validate_state(updated)
    inspection = inspect(root, updated)
    errors = [item for item in inspection["issues"] if item.get("severity") == "error"]
    if errors:
        raise StateError("CHECKPOINT_REFERENCE_ERRORS", "checkpoint contains invalid workspace references",
                         {"issues": errors})
    atomic_write(root / PREVIOUS_REL, state_path.read_text(encoding="utf-8"))
    atomic_write(state_path, yaml_text(updated))
    append_log(root, updated, event, summary)
    envelope(True, "state.checkpoint", {"state_revision": updated["state_revision"],
                                         "updated_at": updated["updated_at"],
                                         "event": event,
                                         "state_path": str(STATE_REL),
                                         "previous_path": str(PREVIOUS_REL),
                                         "log_path": str(LOG_REL),
                                         "stale_reading_notes": stale},
             [item for item in inspection["issues"] if item.get("severity") == "warning"])
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    for name in ("resume", "validate"):
        command = sub.add_parser(name)
        command.add_argument("--workspace", required=True)
    checkpoint = sub.add_parser("checkpoint")
    checkpoint.add_argument("--workspace", required=True)
    checkpoint.add_argument("--patch", required=True)
    checkpoint.add_argument("--event", required=True)
    checkpoint.add_argument("--summary", required=True)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        root = workspace_path(args.workspace)
        if args.command == "resume":
            return command_resume(root)
        if args.command == "validate":
            return command_validate(root)
        return command_checkpoint(root, Path(args.patch).expanduser().resolve(), args.event, args.summary)
    except StateError as exc:
        envelope(False, f"state.{args.command}", error={"code": exc.code, "message": exc.message,
                                                            "details": exc.details})
        return 2


if __name__ == "__main__":
    sys.exit(main())
