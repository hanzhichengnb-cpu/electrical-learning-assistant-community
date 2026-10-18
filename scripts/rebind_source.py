#!/usr/bin/env python3
"""Safely add a workspace-relative PDF location to an existing Source version."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any


class RebindError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


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


def envelope(ok: bool, data: Any = None, error: dict[str, Any] | None = None) -> None:
    print(json.dumps({"api_version": "1", "ok": ok, "op": "source.rebind", "data": data,
                      "warnings": [], "error": error}, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--pdf", required=True)
    args = parser.parse_args()
    try:
        root = Path(args.workspace).expanduser().resolve()
        pdf = Path(args.pdf).expanduser().resolve()
        if not (root / "AGENTS.md").is_file():
            raise RebindError("NOT_A_WORKSPACE", "workspace root must contain AGENTS.md")
        if not pdf.is_file() or pdf.suffix.lower() != ".pdf":
            raise RebindError("PDF_UNAVAILABLE", "selected source must be an existing PDF", {"path": str(pdf)})
        registry_path = root / "sources" / "registry" / f"{args.source_id}.json"
        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RebindError("SOURCE_REGISTRY_INVALID", "Source Registry cannot be read",
                              {"path": str(registry_path), "reason": str(exc)}) from exc
        actual = digest(pdf)
        matches = [version for version in registry.get("versions", [])
                   if isinstance(version, dict) and version.get("sha256") == actual]
        if len(matches) != 1:
            raise RebindError("SOURCE_VERSION_MISMATCH",
                              "PDF hash does not match exactly one registered Source version",
                              {"source_id": args.source_id, "pdf_sha256": actual})
        relative = Path(os.path.relpath(pdf, root)).as_posix()
        if Path(relative).is_absolute():
            raise RebindError("NON_PORTABLE_LOCATION", "rebinding must produce a relative workspace location")
        locations = matches[0].setdefault("locations", [])
        entry = {"base": "kb_root", "path": relative}
        changed = entry not in locations
        previous = (root / "00_System" / "runtime" / "source-registry-backups"
                    / f"{args.source_id}.previous.json")
        if changed:
            locations.append(entry)
            atomic_write(previous, registry_path.read_text(encoding="utf-8"))
            atomic_write(registry_path, json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
        envelope(True, {"source_id": args.source_id, "pdf_sha256": actual,
                        "location": entry, "changed": changed,
                        "registry": str(registry_path.relative_to(root)),
                        "previous": str(previous.relative_to(root)) if changed else None})
        return 0
    except RebindError as exc:
        envelope(False, error={"code": exc.code, "message": exc.message, "details": exc.details})
        return 2


if __name__ == "__main__":
    sys.exit(main())
