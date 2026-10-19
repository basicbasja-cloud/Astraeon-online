#!/usr/bin/env python3
"""Sample meaningful source frames and produce explicit sprite timings."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

from contracts import read_json, write_json

ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "authoring/characters/factory-v3"


def sample_clip(action_name: str, action_config: dict[str, Any], clip: dict[str, Any], default_samples: list[float]) -> dict[str, Any]:
    source_fps = float(clip.get("source_fps", 0))
    start = float(clip.get("frame_start", 0))
    end = float(clip.get("frame_end", 0))
    if not math.isfinite(source_fps) or source_fps <= 0 or not math.isfinite(start + end) or end <= start:
        raise ValueError("clip report requires a positive source_fps and frame_end greater than frame_start")
    count = int(action_config["sample_count"])
    if count < 2:
        raise ValueError(f"{action_name} needs at least two meaningful frames")
    loop = bool(action_config["loop"])
    markers = clip.get("semantic_phases", {})
    if action_name == "BasicAttack":
        required_phases = ("anticipation", "wind_up", "contact", "follow_through", "recovery")
        missing = [name for name in required_phases if name not in markers]
        if missing:
            raise ValueError("BasicAttack needs reviewed semantic phase markers: " + ", ".join(missing))
        anchors = [float(markers[name]) for name in required_phases]
        if any(not 0.0 <= phase <= 1.0 for phase in anchors) or anchors != sorted(anchors):
            raise ValueError("BasicAttack semantic phase markers must be ordered in the [0,1] clip range")
        phases = sorted(set([0.0, 1.0, *anchors]))
        while len(phases) < count:
            phase = max((a + b) * 0.5 for a, b in zip(phases, phases[1:]))
            phases.append(phase)
            phases.sort()
        if len(phases) > count:
            raise ValueError(f"BasicAttack has {len(phases)} required phase/end points but only {count} configured samples")
    else:
        if count <= len(default_samples):
            phases = [default_samples[round(i * (len(default_samples) - 1) / (count - 1))] for i in range(count)]
        else:
            phases = [i / (count - 1) for i in range(count)]
    source_frames = [int(round(start + phase * (end - start))) for phase in phases]
    if len(set(source_frames)) != len(source_frames):
        raise ValueError("Sampling phases collapse onto duplicate source frames; increase source duration or reduce sample_count")
    clip_frame_count = max(1.0, end - start + 1.0)
    frame_records = []
    for index, (phase, source_frame) in enumerate(zip(phases, source_frames)):
        next_frame = source_frames[index + 1] if index + 1 < len(source_frames) else (source_frames[0] + clip_frame_count if loop else source_frame + 1.0)
        duration_ms = max(1, int(round((next_frame - source_frame) * 1000.0 / source_fps)))
        frame_records.append({
            "frame_index": index,
            "source_frame": source_frame,
            "phase": round(phase, 6),
            "duration_ms": duration_ms,
        })
    duration_total = sum(item["duration_ms"] for item in frame_records)
    events = []
    for event in clip.get("semantic_events", []):
        name = event.get("name")
        phase = float(event.get("phase", -1))
        if name not in ("footstep", "attackStart", "contact", "recoveryStart", "castRelease", "itemUse", "animationComplete"):
            raise ValueError(f"Unsupported semantic event name: {name}")
        if not 0.0 <= phase <= 1.0:
            raise ValueError(f"Semantic event {name} must have a phase in [0,1]")
        time_ms = int(round(phase * duration_total))
        nearest = min(frame_records, key=lambda item: abs(item["phase"] - phase))
        events.append({"name": name, "phase": round(phase, 6), "time_ms": time_ms, "frame_index": nearest["frame_index"]})
    return {
        "action": action_name,
        "motion_id": action_config["motion_id"],
        "source_action": clip.get("source_action"),
        "source_fps": source_fps,
        "loop": loop,
        "frame_count": len(frame_records),
        "duration_ms": duration_total,
        "semantic_phases": markers,
        "events": events,
        "frames": frame_records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character", default="swordsman_male_v3")
    parser.add_argument("--action", required=True, choices=("Idle", "Walk", "Run", "BasicAttack", "Hit", "Death"))
    parser.add_argument("--clip-report", required=True, help="Reviewed JSON inventory for one imported source clip")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        config = read_json(FACTORY / "configs" / f"{args.character}.json")
        clip = read_json(Path(args.clip_report))
        result = sample_clip(args.action, config["actions"][args.action], clip, config["sampling"]["default_phase_samples"])
        result["character_id"] = config["id"]
        result["directions"] = config["render"]["directions"]
        result["frame_size"] = [config["render"]["width"], config["render"]["height"]]
        result["status"] = "SAMPLED_REQUIRES_MOTION_QA_AND_RENDER_REVIEW"
        write_json(Path(args.output), result)
        print(json.dumps({"passed": True, "action": args.action, "frame_count": result["frame_count"], "duration_ms": result["duration_ms"], "output": args.output}, indent=2))
        return 0
    except Exception as exc:
        print(f"Motion sampling blocked: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
