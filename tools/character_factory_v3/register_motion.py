#!/usr/bin/env python3
"""Register an acquired immutable motion file and its reviewed provenance."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from contracts import read_json, repo_path, sha256_file, validate_motion_record, write_json

ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "authoring/characters/factory-v3"


def register(source_arg: str, record_arg: str) -> dict:
    inbox = FACTORY / "motions/inbox"
    source = Path(source_arg)
    if not source.is_absolute():
        source = inbox / source
    source = source.resolve()
    if not source.is_relative_to(inbox.resolve()) or not source.is_file():
        raise ValueError("Motion source must be a file inside authoring/characters/factory-v3/motions/inbox/")
    record_path = Path(record_arg)
    if not record_path.is_absolute():
        record_path = inbox / record_path
    record_path = record_path.resolve()
    if not record_path.is_relative_to(inbox.resolve()) or not record_path.is_file():
        raise ValueError("Provenance JSON must be a file inside the motions inbox")
    record = read_json(record_path)
    motion_id = record.get("id")
    if not motion_id or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for ch in motion_id):
        raise ValueError("Motion id must contain only letters, digits, underscores, and hyphens")
    if record.get("original_filename") != source.name:
        raise ValueError("original_filename must exactly match the acquired source filename")
    actual_hash = sha256_file(source)
    if record.get("file_sha256") != actual_hash:
        raise ValueError(f"Source hash does not match provenance: expected {record.get('file_sha256')}, got {actual_hash}")

    destination = FACTORY / "motions/raw" / motion_id / source.name
    record["local_path"] = str(destination.relative_to(ROOT))
    for evidence in record.get("license_evidence", []):
        evidence_path = repo_path(ROOT, evidence)
        if not evidence_path.is_file():
            raise FileNotFoundError(f"License evidence is missing: {evidence}")
    issues = validate_motion_record(record)
    if issues:
        raise ValueError("Invalid provenance record:\n- " + "\n- ".join(issues))

    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and sha256_file(destination) != actual_hash:
        raise FileExistsError(f"Immutable raw motion destination already contains different bytes: {destination}")
    if not destination.exists():
        shutil.copy2(source, destination)
    if sha256_file(destination) != actual_hash:
        raise RuntimeError("Copied raw motion failed its source digest check")

    registry_path = FACTORY / "motions/candidates.json"
    registry = read_json(registry_path)
    imported = registry.setdefault("imported_motions", [])
    if any(item.get("id") == motion_id for item in imported):
        raise ValueError(f"Motion id is already registered: {motion_id}")
    imported.append(record)
    imported.sort(key=lambda item: item["id"])
    write_json(registry_path, registry)
    return {"registered": True, "id": motion_id, "local_path": record["local_path"], "sha256": actual_hash, "production_status": record["production_status"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Original downloaded file inside the motions inbox")
    parser.add_argument("--record", required=True, help="Completed provenance JSON inside the motions inbox")
    args = parser.parse_args()
    try:
        import json

        print(json.dumps(register(args.source, args.record), indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Motion registration stopped: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
