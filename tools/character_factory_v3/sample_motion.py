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
    source_range = clip.get("source_frame_range", [clip.get("frame_start", 0), clip.get("frame_end", 0)])
    output_range = clip.get("output_frame_range", [clip.get("frame_start", 0), clip.get("frame_end", 0)])
    if len(source_range) != 2 or len(output_range) != 2:
        raise ValueError("clip report requires two-element source and retarget frame ranges")
    source_start, source_end = map(float, source_range)
    output_start, output_end = map(float, output_range)
    output_fps = float(clip.get("output_fps", source_fps))
    if not all(math.isfinite(value) for value in (source_fps, source_start, source_end, output_start, output_end, output_fps)) or source_fps <= 0 or output_fps <= 0 or source_end <= source_start or output_end <= output_start:
        raise ValueError("clip report requires positive frame rates and increasing source/retarget frame ranges")
    selected_range = action_config.get("retarget_frame_range", [output_start, output_end])
    if len(selected_range) != 2:
        raise ValueError("retarget_frame_range must contain start and end frames")
    selected_start, selected_end = map(float, selected_range)
    if selected_start < output_start or selected_end > output_end or selected_end <= selected_start:
        raise ValueError("retarget_frame_range must be an increasing subrange of the retargeted action")
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
            split_index = max(
                range(len(phases) - 1),
                key=lambda index: phases[index + 1] - phases[index],
            )
            phase = (phases[split_index] + phases[split_index + 1]) * 0.5
            phases.append(phase)
            phases.sort()
        if len(phases) > count:
            raise ValueError(f"BasicAttack has {len(phases)} required phase/end points but only {count} configured samples")
    else:
        if count <= len(default_samples):
            phases = [default_samples[round(i * (len(default_samples) - 1) / (count - 1))] for i in range(count)]
        elif loop:
            # Keep the endpoint out of a loop: phase 1 is phase 0 again. More
            # samples are evenly spaced over [0, 1) so the wrap gap is one
            # normal frame instead of a shortened or duplicated endpoint.
            phases = [i / count for i in range(count)]
        else:
            phases = [i / (count - 1) for i in range(count)]
    retarget_exact = [selected_start + phase * (selected_end - selected_start) for phase in phases]
    retarget_frames = [int(round(value)) for value in retarget_exact]
    if len(set(retarget_frames)) != len(retarget_frames):
        raise ValueError("Sampling phases collapse onto duplicate source frames; increase source duration or reduce sample_count")
    source_frames = [
        int(round(source_start + ((value - output_start) / (output_end - output_start)) * (source_end - source_start)))
        for value in retarget_exact
    ]
    sampled_span_seconds = (selected_end - selected_start) / output_fps
    terminal_hold_seconds = 0.0 if loop else 1.0 / output_fps
    requested_duration_ms = clip.get("duration_ms")
    if requested_duration_ms is not None:
        if not isinstance(requested_duration_ms, (int, float)) or not math.isfinite(requested_duration_ms) or requested_duration_ms <= 0:
            raise ValueError("duration_ms must be a positive finite value when supplied")
        requested_span_seconds = requested_duration_ms / 1000.0 - terminal_hold_seconds
        if requested_span_seconds <= 0:
            raise ValueError("duration_ms is too short for the selected clip and terminal hold")
        sampled_span_seconds = requested_span_seconds
    clip_duration_seconds = sampled_span_seconds + terminal_hold_seconds
    if clip_duration_seconds <= 0:
        raise ValueError("Selected retarget range has no positive duration")
    frame_records = []
    durations_seconds: list[float] = []
    for index, (phase, source_frame, retarget_frame) in enumerate(zip(phases, source_frames, retarget_frames)):
        next_phase = phases[index + 1] if index + 1 < len(phases) else 1.0
        if not loop and index == len(phases) - 1 and phase >= 1.0:
            # An endpoint sample is held for one output frame instead of
            # receiving a meaningless 1 ms duration.
            duration_seconds = terminal_hold_seconds
        else:
            duration_seconds = max(0.0, next_phase - phase) * sampled_span_seconds
            if not loop and index == len(phases) - 1:
                # If there is no explicit endpoint sample, keep the last pose
                # through the end and its one-frame terminal hold.
                duration_seconds += terminal_hold_seconds
        durations_seconds.append(duration_seconds)
        frame_records.append({
            "frame_index": index,
            "source_frame": source_frame,
            "retarget_frame": retarget_frame,
            "phase": round(phase, 6),
        })
    # Round cumulative boundaries rather than each duration independently so
    # the integer frame holds sum to the source clip duration without drift.
    elapsed_seconds = 0.0
    previous_boundary_ms = 0
    for item, duration_seconds in zip(frame_records, durations_seconds):
        elapsed_seconds += duration_seconds
        boundary_ms = int(round(elapsed_seconds * 1000.0))
        item["duration_ms"] = max(1, boundary_ms - previous_boundary_ms)
        previous_boundary_ms = boundary_ms
    duration_total = previous_boundary_ms
    events = []
    for event in clip.get("semantic_events", []):
        name = event.get("name")
        phase = float(event.get("phase", -1))
        if name not in (
            "footstep", "leftFootstep", "rightFootstep", "anticipationStart", "attackStart",
            "contact", "recoveryStart", "impact", "groundContact", "complete",
            "castRelease", "itemUse", "animationComplete",
        ):
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
        "output_fps": output_fps,
        "source_frame_range": [source_start, source_end],
        "retarget_frame_range": [selected_start, selected_end],
        "loop": loop,
        "frame_count": len(frame_records),
        "duration_ms": duration_total,
        "semantic_phases": markers,
        "events": events,
        "frames": frame_records,
    }


def validate_sample_timeline(timeline: dict[str, Any]) -> list[str]:
    """Check sampled frame timing and semantic event positions before rendering."""
    errors: list[str] = []
    frames = timeline.get("frames", [])
    if not frames:
        errors.append("Sample timeline contains no frames")
    if [item.get("frame_index") for item in frames] != list(range(len(frames))):
        errors.append("Sample frame indices must be contiguous from zero")
    durations = [item.get("duration_ms") for item in frames]
    if any(not isinstance(value, (int, float)) or value <= 0 for value in durations):
        errors.append("Every sampled frame needs a positive duration_ms")
    duration_total = sum(value for value in durations if isinstance(value, (int, float)))
    for event in timeline.get("events", []):
        phase = event.get("phase")
        time_ms = event.get("time_ms")
        frame_index = event.get("frame_index")
        if not isinstance(phase, (int, float)) or not 0 <= phase <= 1:
            errors.append(f"Semantic event {event.get('name')} phase is outside [0,1]")
        if not isinstance(time_ms, (int, float)) or not 0 <= time_ms <= duration_total:
            errors.append(f"Semantic event {event.get('name')} time_ms is outside the sampled clip")
        if not isinstance(frame_index, int) or not 0 <= frame_index < len(frames):
            errors.append(f"Semantic event {event.get('name')} refers to an invalid sample frame")
    return errors


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
