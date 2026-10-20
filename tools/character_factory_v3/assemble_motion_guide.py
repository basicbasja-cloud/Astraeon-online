#!/usr/bin/env python3
"""Assemble Blender motion-guide views into an authoring sheet and preview GIF."""
from __future__ import annotations

import argparse
import hashlib
import json
from statistics import mean
from pathlib import Path

from PIL import Image, ImageChops


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--timeline", required=True, type=Path)
    parser.add_argument("--sheet", required=True, type=Path)
    parser.add_argument("--gif", required=True, type=Path)
    args = parser.parse_args()

    manifest_path = args.manifest.resolve()
    timeline_path = args.timeline.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    directions = manifest["directions"]
    frames = manifest["frames"]
    timeline_frames = timeline["frames"]
    if len(frames) != len(timeline_frames) or not frames:
        raise ValueError("Rendered frame count must match the timeline")
    if [int(row["sample_index"]) for row in frames] != [
        int(row["frame_index"]) for row in timeline_frames
    ]:
        raise ValueError("Rendered frame indexes do not match the timeline")

    first_record = frames[0]["directions"][0]
    first_path = manifest_path.parent / first_record["file"]
    with Image.open(first_path) as source:
        cell_size = source.size
    sheet = Image.new("RGBA", (cell_size[0] * len(directions), cell_size[1] * len(frames)), (0, 0, 0, 0))
    gif_frames: list[Image.Image] = []
    durations: list[int] = []
    views = {direction: [] for direction in directions}

    for row_index, (rendered, timed) in enumerate(zip(frames, timeline_frames, strict=True)):
        by_direction = {row["direction"]: row for row in rendered["directions"]}
        if set(by_direction) != set(directions):
            raise ValueError(f"Direction mismatch in rendered sample {row_index}")
        row_canvas = Image.new("RGBA", (cell_size[0] * len(directions), cell_size[1]), (0, 0, 0, 0))
        for col_index, direction in enumerate(directions):
            image_path = manifest_path.parent / by_direction[direction]["file"]
            with Image.open(image_path) as source:
                image = source.convert("RGBA")
            if image.size != cell_size:
                raise ValueError(f"Unexpected size in {image_path}: {image.size}")
            views[direction].append(image.copy())
            x, y = col_index * cell_size[0], row_index * cell_size[1]
            sheet.alpha_composite(image, (x, y))
            row_canvas.alpha_composite(image, (col_index * cell_size[0], 0))
        gif_frames.append(row_canvas.convert("P", palette=Image.Palette.ADAPTIVE, colors=255))
        durations.append(max(10, int(timed["duration_ms"])))

    args.sheet.parent.mkdir(parents=True, exist_ok=True)
    args.gif.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.sheet)
    gif_durations: list[int] = []
    elapsed_ms = 0
    previous_boundary_ms = 0
    for duration_ms in durations:
        elapsed_ms += duration_ms
        boundary_ms = ((elapsed_ms + 5) // 10) * 10
        gif_durations.append(max(10, boundary_ms - previous_boundary_ms))
        previous_boundary_ms = boundary_ms
    save_options = {
        "save_all": True,
        "append_images": gif_frames[1:],
        "duration": gif_durations,
        "optimize": False,
        "disposal": 2,
    }
    if timeline.get("loop"):
        save_options["loop"] = 0
    gif_frames[0].save(args.gif, **save_options)

    def alpha_iou(first: Image.Image, second: Image.Image) -> float:
        first_alpha = first.getchannel("A").point(lambda value: 255 if value else 0).convert("1")
        second_alpha = second.getchannel("A").point(lambda value: 255 if value else 0).convert("1")
        intersection_area = ImageChops.logical_and(first_alpha, second_alpha).histogram()[-1]
        union_area = ImageChops.logical_or(first_alpha, second_alpha).histogram()[-1]
        return intersection_area / union_area if union_area else 1.0

    continuity: dict[str, dict[str, float]] = {}
    all_adjacent: list[float] = []
    for direction, direction_frames in views.items():
        adjacent = [alpha_iou(left, right) for left, right in zip(direction_frames, direction_frames[1:])]
        all_adjacent.extend(adjacent)
        report = {"mean": round(mean(adjacent), 4), "minimum": round(min(adjacent), 4)} if adjacent else {}
        if timeline.get("loop"):
            report["last_to_first"] = round(alpha_iou(direction_frames[-1], direction_frames[0]), 4)
        continuity[direction] = report
    loop_values = [item["last_to_first"] for item in continuity.values() if "last_to_first" in item]

    provenance = {
        "role": "POSE_GUIDE_ONLY_NOT_PAINTED_ART",
        "sheet": str(args.sheet.resolve()),
        "sheet_sha256": sha256(args.sheet),
        "gif": str(args.gif.resolve()),
        "gif_sha256": sha256(args.gif),
        "layout": {
            "width_px": sheet.width,
            "height_px": sheet.height,
            "cell_px": list(cell_size),
            "columns": directions,
            "rows": len(frames),
        },
        "source_scene": manifest["source_scene"],
        "source_scene_sha256": sha256(Path(manifest["source_scene"])),
        "timeline": str(timeline_path),
        "timeline_sha256": sha256(timeline_path),
        "renderer_manifest": str(manifest_path),
        "renderer_manifest_sha256": sha256(manifest_path),
        "renderer": "Blender Cycles CPU, 160x160 per pose, 1 render sample; pose reference only",
        "loop": bool(timeline.get("loop")),
        "timeline_duration_ms": sum(durations),
        "gif_duration_ms": sum(gif_durations),
        "gif_timing_quantization_ms": 10,
        "rendered_silhouette_continuity_diagnostic": {
            "method": "binary alpha IoU between adjacent pose-guide frames; includes last-to-first only for loop clips",
            "per_direction": continuity,
            "mean_adjacent": round(mean(all_adjacent), 4) if all_adjacent else None,
            "minimum_adjacent": round(min(all_adjacent), 4) if all_adjacent else None,
            "mean_last_to_first": round(mean(loop_values), 4) if loop_values else None,
            "interpretation": "Pose-guide silhouette diagnostic only; it does not rate painted-art quality or human motion naturalness.",
        },
        "frame_phases": [
            {
                "frame_index": int(row["frame_index"]),
                "phase": float(row["phase"]),
                "duration_ms": int(row["duration_ms"]),
                "retarget_frame": int(row["retarget_frame"]),
            }
            for row in timeline_frames
        ],
    }
    provenance_path = args.sheet.with_suffix(".provenance.json")
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sheet": str(args.sheet), "gif": str(args.gif), "provenance": str(provenance_path)}))


if __name__ == "__main__":
    main()
