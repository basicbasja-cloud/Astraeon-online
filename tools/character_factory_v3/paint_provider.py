"""Provider-neutral paint-over stage with a deterministic manual handoff."""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from contracts import read_json, sha256_file, write_json
from qa import validate_production_guide_manifest


class PaintProvider(ABC):
    provider_id = "abstract"

    @abstractmethod
    def prepare(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def paint(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def refine(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def validate(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError


class ManualHandoffProvider(PaintProvider):
    provider_id = "manual_handoff"

    def prepare(self, *, repo_root: Path, config_path: Path, guide_manifest_path: Path, output_root: Path) -> dict[str, Any]:
        config = read_json(config_path)
        manifest = read_json(guide_manifest_path)
        gate = validate_production_guide_manifest(guide_manifest_path, config["required_actions"])
        if not gate["passed"]:
            return {
                "passed": False,
                "provider": self.provider_id,
                "blocked": "Production paint handoff requires a complete animated guide set.",
                "qa": gate,
            }
        identity_path = repo_root / config["identity"]
        if not identity_path.is_file():
            raise FileNotFoundError(f"Identity authority is missing: {identity_path}")
        identity = read_json(identity_path)
        job_seed = {
            "character_id": config["id"],
            "provider": self.provider_id,
            "guide_manifest_sha256": sha256_file(guide_manifest_path),
            "identity_manifest_sha256": sha256_file(identity_path),
            "required_actions": config["required_actions"],
            "directions": config["render"]["directions"],
            "layers": config["paint"]["layers"],
            "identity_locks": identity["locks"],
            "palette_lock": identity["locks"]["palette"],
            "event_names": config["semantic_events"],
            "actions": manifest["actions"],
            "events_by_action": config.get("events_by_action", {}),
            "source_motion_provenance": manifest.get("motion_provenance", {}),
            "motion_guide_license_policy": identity["paint_consistency"]["provider_policy"],
        }
        # Include source pass hashes in the stable job key, never mutable timestamps.
        job_seed["guide_pass_hashes"] = [
            entry["sha256"]
            for frame in manifest.get("frames", [])
            for _, entry in sorted(frame.get("passes", {}).items())
        ]
        key = sha256_bytes(json.dumps(job_seed, sort_keys=True, separators=(",", ":")).encode("utf-8"))[:24]
        target = output_root / key
        target.mkdir(parents=True, exist_ok=True)
        job = {
            "schema_version": 1,
            "job_id": key,
            **job_seed,
            "status": "GUIDES_READY_FOR_MANUAL_REVIEW",
            "painted_outputs": [],
            "owner_visual_approval": False,
            "created_by": "character_factory_v3",
            "source_guides": str(guide_manifest_path.relative_to(repo_root)),
        }
        write_json(target / "job.json", job)
        return {"passed": True, "provider": self.provider_id, "job_id": key, "job_file": str(target / "job.json"), "status": job["status"]}

    def paint(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return {"passed": False, "provider": self.provider_id, "blocked": "Manual artist work is required; this provider does not synthesize pixels."}

    def refine(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return {"passed": False, "provider": self.provider_id, "blocked": "Refinement requires a reviewed painted submission."}

    def validate(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return {"passed": False, "provider": self.provider_id, "blocked": "Paint validation requires painted outputs."}


class DisabledPaintProvider(PaintProvider):
    provider_id = "disabled"

    def prepare(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return {"passed": False, "provider": self.provider_id, "blocked": "Paint provider is disabled."}

    def paint(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self.prepare()

    def refine(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self.prepare()

    def validate(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self.prepare()


def sha256_bytes(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()
