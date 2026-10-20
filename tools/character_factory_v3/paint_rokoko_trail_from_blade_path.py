#!/usr/bin/env python3
"""Paint an original thick WeaponLight trail from the transformed Rokoko blade path."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


CELL = 320
GRID = 4
SUPERSAMPLE = 4
BACKGROUND = (235, 235, 235)


def catmull_rom(points: list[tuple[float, float]], steps_per_segment: int = 32) -> list[tuple[float, float]]:
    if len(points) < 2:
        return points
    samples: list[tuple[float, float]] = []
    p = [np.asarray(x, dtype=np.float64) for x in points]
    for index in range(len(p) - 1):
        p0 = p[index - 1] if index > 0 else p[index] * 2 - p[index + 1]
        p1, p2 = p[index], p[index + 1]
        p3 = p[index + 2] if index + 2 < len(p) else p[index + 1] * 2 - p[index]
        for step in range(steps_per_segment):
            t = step / steps_per_segment
            t2, t3 = t * t, t * t * t
            value = 0.5 * ((2 * p1) + (-p0 + p2) * t
                           + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                           + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
            samples.append((float(value[0]), float(value[1])))
    samples.append((float(p[-1][0]), float(p[-1][1])))
    return samples


def ribbon_mask(points: list[tuple[float, float]], max_width: float) -> Image.Image:
    path = catmull_rom(points)
    scale = SUPERSAMPLE
    mask = Image.new("L", (CELL * scale, CELL * scale), 0)
    if len(path) < 2:
        return mask
    left: list[tuple[float, float]] = []
    right: list[tuple[float, float]] = []
    count = len(path)
    for index, (x, y) in enumerate(path):
        before = path[max(0, index - 1)]
        after = path[min(count - 1, index + 1)]
        dx, dy = after[0] - before[0], after[1] - before[1]
        length = max(math.hypot(dx, dy), 1e-6)
        nx, ny = -dy / length, dx / length
        t = index / max(1, count - 1)
        envelope = max(0.0, math.sin(math.pi * t)) ** 0.72
        half = max_width * envelope / 2
        left.append(((x + nx * half) * scale, (y + ny * half) * scale))
        right.append(((x - nx * half) * scale, (y - ny * half) * scale))
    ImageDraw.Draw(mask).polygon(left + list(reversed(right)), fill=255)
    return mask.resize((CELL, CELL), Image.Resampling.LANCZOS)


def fill_mask(color: tuple[int, int, int], opacity: float, mask: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", (CELL, CELL), (*color, 0))
    layer.putalpha(mask.point(lambda value: round(value * opacity)))
    return layer


def trail_frame(points: list[tuple[float, float]], profile: tuple[float, float] | None) -> Image.Image:
    frame = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    if profile is None or len(points) < 2:
        return frame
    opacity, width = profile
    outer = ribbon_mask(points, width + 8.0)
    body = ribbon_mask(points, width * 0.72)
    core = ribbon_mask(points, max(2.0, width * 0.20))
    frame.alpha_composite(fill_mask((105, 96, 127), opacity * 0.70, outer))
    frame.alpha_composite(fill_mask((178, 174, 210), opacity * 0.84, body))
    frame.alpha_composite(fill_mask((255, 244, 222), opacity * 0.90, core))
    return frame


def blade_sweep(previous: dict[str, object], current: dict[str, object]) -> list[tuple[float, float]]:
    """Sample the sword blade's actual rotational sweep around its moving grip."""
    pivot0 = np.asarray(previous["pivot_xy"], dtype=np.float64)
    pivot1 = np.asarray(current["pivot_xy"], dtype=np.float64)
    angle0 = math.radians(float(previous["blade_angle_degrees"]))
    angle1 = math.radians(float(current["blade_angle_degrees"]))
    tip0 = np.asarray(previous["blade_tip_xy"], dtype=np.float64)
    tip1 = np.asarray(current["blade_tip_xy"], dtype=np.float64)
    length0 = float(np.linalg.norm(tip0 - pivot0))
    length1 = float(np.linalg.norm(tip1 - pivot1))
    steps = max(12, int(math.ceil(abs(angle1 - angle0) / math.radians(3.0))))
    result = []
    for step in range(steps + 1):
        t = step / steps
        pivot = pivot0 * (1.0 - t) + pivot1 * t
        angle = angle0 * (1.0 - t) + angle1 * t
        length = length0 * (1.0 - t) + length1 * t
        point = pivot + length * np.asarray([math.cos(angle), math.sin(angle)])
        result.append((float(point[0]), float(point[1])))
    return result


def keep_trail_behind_head(effect: Image.Image, head_xy: list[float]) -> Image.Image:
    alpha = np.asarray(effect.getchannel("A"), dtype=np.uint8).copy()
    y, x = np.mgrid[:CELL, :CELL]
    hx, hy = map(float, head_xy)
    head_depth_mask = ((x - hx) / 42.0) ** 2 + ((y - hy) / 50.0) ** 2 <= 1.0
    alpha[head_depth_mask] = 0
    output = effect.copy()
    output.putalpha(Image.fromarray(alpha))
    return output


def contact(frames: list[Image.Image], path: Path, behind: list[Image.Image] | None = None) -> None:
    values = behind if behind is not None else frames
    rows = math.ceil(len(values) / GRID)
    sheet = Image.new("RGBA", (CELL * GRID, CELL * rows), (*BACKGROUND, 255))
    for index, frame in enumerate(values):
        sheet.alpha_composite(frame, ((index % GRID) * CELL, (index // GRID) * CELL))
    sheet.convert("RGB").save(path, quality=96)


def gif(frames: list[Image.Image], durations: list[int], path: Path,
        final_hold_ms: int, scale: int = 3) -> int:
    held = list(durations)
    held[-1] = max(held[-1], final_hold_ms)
    total_units = round(sum(held) / 10)
    units = [duration // 10 for duration in held]
    rest = total_units - sum(units)
    order = sorted(range(len(held)), key=lambda i: (-(held[i] % 10), i))
    for index in order[:rest]:
        units[index] += 1
    delays = [unit * 10 for unit in units]
    canvases: list[Image.Image] = []
    for frame in frames:
        canvas = Image.new("RGBA", (CELL, CELL), (*BACKGROUND, 255))
        canvas.alpha_composite(frame)
        canvases.append(canvas.resize((CELL * scale, CELL * scale), Image.Resampling.LANCZOS).convert("RGB"))
    palette_source = Image.new("RGB", (CELL * scale, CELL * scale * len(canvases)))
    for index, canvas in enumerate(canvases):
        palette_source.paste(canvas, (0, index * CELL * scale))
    palette = palette_source.convert("P", palette=Image.Palette.ADAPTIVE, colors=255)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in canvases]
    indexed[0].save(path, save_all=True, append_images=indexed[1:], duration=delays,
                    disposal=2, optimize=False)
    return sum(delays)


def source_frame_number(value: object) -> int | float:
    frame = round(float(value), 4)
    return int(frame) if frame.is_integer() else frame


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master-frames", required=True, type=Path)
    parser.add_argument("--layers-root", type=Path,
                        help="Optional modular layer directory; defaults beside master/frames")
    parser.add_argument("--timeline", required=True, type=Path)
    parser.add_argument("--pose-audit", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--max-width-px", type=float, default=28.0,
                        help="maximum ribbon thickness in the 320px runtime cell")
    parser.add_argument("--early-frames", type=int, default=1,
                        help="begin this many sampled frames before the measured high-speed sweep")
    args = parser.parse_args()
    if args.max_width_px < 8 or args.early_frames < 0:
        parser.error("--max-width-px must be at least 8 and --early-frames cannot be negative")
    layers_root = args.layers_root or args.master_frames.parent.parent / "layers"
    timeline = json.loads(args.timeline.read_text(encoding="utf-8"))
    audit = json.loads(args.pose_audit.read_text(encoding="utf-8"))
    frame_data = audit.get("frames", [])
    frame_count = len(timeline.get("frames", []))
    if frame_count < 2 or len(frame_data) != frame_count:
        parser.error("timeline and transformed blade path must have matching frame counts")
    if any(not math.isclose(float(frame_data[i]["source_frame"]),
                            float(timeline["frames"][i]["source_frame"]), abs_tol=1e-5)
           for i in range(frame_count)):
        parser.error("transformed blade path source frames do not match the motion timeline")

    weapon_states = [frame["weapon_path"] for frame in frame_data]
    durations = [int(frame["duration_ms"]) for frame in timeline["frames"]]
    candidate_events = []
    for index in range(1, frame_count):
        previous, current = weapon_states[index - 1], weapon_states[index]
        angle_delta = float(current["blade_angle_degrees"]) - float(previous["blade_angle_degrees"])
        sweep = blade_sweep(previous, current)
        travel = sum(math.dist(sweep[k - 1], sweep[k]) for k in range(1, len(sweep)))
        if abs(angle_delta) >= 45.0 and travel >= 24.0:
            candidate_events.append({
                "frame": index,
                "angle_delta_degrees": round(angle_delta, 3),
                "sweep_travel_cell_px": round(travel, 3),
            })
    if not candidate_events:
        parser.error("no decisive blade-sweep event found in the transformed motion")

    # Subframe sampling can split one fast stroke across adjacent 60 fps samples.
    # Merge consecutive high-speed segments into one impact ribbon so the effect
    # grows into contact instead of restarting as separate crescents.
    event_groups: list[list[dict[str, object]]] = []
    for candidate in candidate_events:
        if event_groups and int(candidate["frame"]) == int(event_groups[-1][-1]["frame"]) + 1:
            event_groups[-1].append(candidate)
        else:
            event_groups.append([candidate])
    impact_events = []
    for group in event_groups:
        start_frame = int(group[0]["frame"])
        impact_frame = int(group[-1]["frame"])
        combined_path: list[tuple[float, float]] = []
        for segment_index in range(start_frame, impact_frame + 1):
            segment = blade_sweep(weapon_states[segment_index - 1], weapon_states[segment_index])
            combined_path.extend(segment if not combined_path else segment[1:])
        travel = sum(math.dist(combined_path[k - 1], combined_path[k])
                     for k in range(1, len(combined_path)))
        impact_events.append({
            "start_frame": start_frame,
            "trail_start_frame": max(0, start_frame - args.early_frames),
            "frame": impact_frame,
            "angle_delta_degrees": round(sum(float(item["angle_delta_degrees"]) for item in group), 3),
            "sweep_travel_cell_px": round(travel, 3),
        })

    effect_frames: list[Image.Image] = []
    effect_root = args.output_root / "layers/WeaponLight/frames"
    review_root = args.output_root / "review"
    effect_root.mkdir(parents=True, exist_ok=True)
    review_root.mkdir(parents=True, exist_ok=True)
    reports = []
    for index in range(frame_count):
        effect = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
        sweeps = []
        active_event = None
        for event in impact_events:
            event_frame = int(event["frame"])
            start_frame = int(event["start_frame"])
            trail_start_frame = int(event["trail_start_frame"])
            if index < trail_start_frame:
                continue
            if index < start_frame:
                # Add a short, faint lead-in on the first actual strike frame.
                # Its centerline comes from the next measured blade segment.
                lead = blade_sweep(weapon_states[start_frame - 1], weapon_states[start_frame])
                fraction = (index - trail_start_frame + 1) / (start_frame - trail_start_frame + 1)
                last = max(2, min(len(lead), round((len(lead) - 1) * fraction) + 1))
                sweep = lead[:last]
                age_ms = 0
                opacity = 0.52
                width = args.max_width_px * 0.66
            elif index <= event_frame:
                age_ms = 0
                progress = (1.0 if event_frame == start_frame else
                            (index - start_frame) / (event_frame - start_frame))
                opacity = 0.62 + 0.32 * progress
                width = args.max_width_px * (0.68 + 0.32 * progress)
                sweep = []
                for segment_index in range(start_frame, index + 1):
                    segment = blade_sweep(weapon_states[segment_index - 1],
                                          weapon_states[segment_index])
                    sweep.extend(segment if not sweep else segment[1:])
            else:
                age_ms = sum(durations[event_frame:index])
                if age_ms > 198:
                    continue
                fade = max(0.0, 1.0 - age_ms / 220.0) ** 1.35
                opacity = 0.94 * fade
                width = args.max_width_px * (0.52 + 0.48 * fade)
                sweep = []
                for segment_index in range(start_frame, event_frame + 1):
                    segment = blade_sweep(weapon_states[segment_index - 1],
                                          weapon_states[segment_index])
                    sweep.extend(segment if not sweep else segment[1:])
            effect.alpha_composite(trail_frame(sweep, (opacity, width)))
            active_event = event
            sweeps.append({
                "from_frame": trail_start_frame,
                "to_frame": event_frame,
                "age_ms": age_ms,
                "opacity": round(opacity, 3),
                "maximum_width_cell_px": round(width, 2),
                "centerline_xy": [[round(x, 3), round(y, 3)] for x, y in sweep],
            })
        effect.save(effect_root / f"weaponlight_se_{index:02d}.png")
        effect_frames.append(effect)
        reports.append({
            "sprite_frame": index,
            "source_frame": source_frame_number(frame_data[index]["source_frame"]),
            "active": bool(sweeps),
            "impact_event": active_event,
            "sweep_segments": sweeps,
            "opacity": sweeps[-1]["opacity"] if sweeps else 0.0,
            "maximum_width_cell_px": sweeps[-1]["maximum_width_cell_px"] if sweeps else 0.0,
            "alpha_bounds_xyxy": list(effect.getchannel("A").getbbox() or []),
        })

    master_frames: list[Image.Image] = []
    behind: list[Image.Image] = []
    over: list[Image.Image] = []
    layered: list[Image.Image] = []
    for index, effect in enumerate(effect_frames):
        path = args.master_frames / f"se_{index:02d}.png"
        master = Image.open(path).convert("RGBA")
        if master.size != (CELL, CELL):
            parser.error(f"master frame must be {CELL}x{CELL}: {path}")
        master_frames.append(master)
        behind_frame = effect.copy()
        behind_frame.alpha_composite(master)
        behind.append(behind_frame)
        over_frame = master.copy()
        over_frame.alpha_composite(effect)
        over.append(over_frame)

        if layers_root.is_dir():
            effect_stack = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
            for name in ["BackAccessory", "BaseBody", "Outfit"]:
                layer_path = layers_root / name / "frames" / f"se_{index:02d}.png"
                if layer_path.is_file():
                    effect_stack.alpha_composite(Image.open(layer_path).convert("RGBA"))
            head_xy = frame_data[index]["landmarks_xy"]["head"]
            root_adjust = int(frame_data[index].get("pixel_root_correction_y", 0))
            head_xy = [float(head_xy[0]), float(head_xy[1]) + root_adjust]
            effect_stack.alpha_composite(keep_trail_behind_head(effect, head_xy))
            hair_path = layers_root / "Hair" / "frames" / f"se_{index:02d}.png"
            if hair_path.is_file():
                effect_stack.alpha_composite(Image.open(hair_path).convert("RGBA"))
            weapon_path = layers_root / "Weapon" / "frames" / f"se_{index:02d}.png"
            if weapon_path.is_file():
                effect_stack.alpha_composite(Image.open(weapon_path).convert("RGBA"))
            else:
                effect_stack.alpha_composite(master)
            headgear_path = layers_root / "Headgear" / "frames" / f"se_{index:02d}.png"
            if headgear_path.is_file():
                effect_stack.alpha_composite(Image.open(headgear_path).convert("RGBA"))
            layered.append(effect_stack)
        else:
            layered.append(over_frame)

    rows = math.ceil(len(effect_frames) / GRID)
    layer_sheet = Image.new("RGBA", (CELL * GRID, CELL * rows), (0, 0, 0, 0))
    for index, effect in enumerate(effect_frames):
        layer_sheet.alpha_composite(effect, ((index % GRID) * CELL, (index // GRID) * CELL))
    layer_sheet.save(args.output_root / f"layers/WeaponLight/weaponlight-se-{GRID}x{rows}.png")
    contact(effect_frames, review_root / f"weaponlight-path-contact-{GRID}x{rows}.jpg")
    contact(behind, review_root / f"basicattack-se-with-path-trail-behind-{GRID}x{rows}.jpg")
    contact(over, review_root / f"basicattack-se-with-path-trail-over-{GRID}x{rows}.jpg")
    contact(layered, review_root / f"basicattack-se-with-path-trail-layered-{GRID}x{rows}.jpg")
    gif_duration = gif(layered, durations,
                       review_root / "basicattack-se-rokoko-research-surface-with-trail-one-shot.gif",
                       int(timeline.get("recovery_hold_ms", 300)))
    payload = {
        "status": "REVIEW_ONLY_ORIGINAL_WEAPONLIGHT_PATH_DERIVED; OWNER_REVIEW_PENDING",
        "art_direction": "Original thick plum-gray, lavender-silver, warm-ivory tapered ribbon; not copied RO pixels.",
        "registration_method": "Consecutive high-angular-speed source segments are grouped into one thick tapered ribbon; a faint short lead-in begins one sampled frame before the measured sweep, the ribbon reaches full width at contact, then fades for 198 ms.",
        "trail_profile": {
            "max_width_cell_px": args.max_width_px,
            "early_frames_before_measured_sweep": args.early_frames,
            "event_onset_policy": "a faint lead-in follows the first measured strike segment; the ribbon reaches full width at contact",
        },
        "layers": "WeaponLight remains separate; the review composites body, WeaponLight, hair/head, then sword so the effect reads over the body while staying behind the face and blade.",
        "playback": {
            "frame_count": frame_count,
            "source_duration_ms": sum(durations),
            "gif_duration_ms_with_recovery_hold": gif_duration,
            "gif_loop_extension": False,
            "source_frame_range": [source_frame_number(frame_data[0]["source_frame"]),
                                   source_frame_number(frame_data[-1]["source_frame"])],
        },
        "impact_events": impact_events,
        "frames": reports,
        "limitations": [
            "The base sprite remains an internal research-template pose study and is not owner-approved production art.",
            "This is one SE view; other directions and semantic cape reconstruction are not included.",
        ],
    }
    (review_root / "weaponlight-path-provenance.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "active_frames": [index for index, report in enumerate(reports) if report["active"]],
        "impact_events": impact_events,
        "gif_duration_ms": gif_duration,
        "behind_contact": str((review_root / f"basicattack-se-with-path-trail-behind-{GRID}x{rows}.jpg").resolve()),
        "layered_contact": str((review_root / f"basicattack-se-with-path-trail-layered-{GRID}x{rows}.jpg").resolve()),
        "gif": str((review_root / "basicattack-se-rokoko-research-surface-with-trail-one-shot.gif").resolve()),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
