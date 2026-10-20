#!/usr/bin/env python3
"""Normalize painted Rokoko keyframes to one fixed floor root and body height.

This is a review/export helper for frame-by-frame painted cutouts. It does not
retarget or alter the pose. A small red-key cleanup removes generator markup
contamination before premultiplied-alpha resizing.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage


CELL_SIZE = 320
BACKGROUND = (232, 232, 232)


def parse_source_frame(path: Path) -> float:
    match = re.fullmatch(r"swordsman_([0-9]+(?:p[0-9]+)?)", path.stem)
    if not match:
        raise ValueError(f"unexpected keyframe filename: {path.name}")
    return float(match.group(1).replace("p", "."))


def largest_component(mask: np.ndarray, min_area: int) -> tuple[int, tuple[slice, slice]]:
    labels, _ = ndimage.label(mask, structure=np.ones((3, 3), dtype=np.uint8))
    best: tuple[int, tuple[slice, slice]] | None = None
    for label, sl in enumerate(ndimage.find_objects(labels), start=1):
        if sl is None:
            continue
        area = int(np.count_nonzero(labels[sl] == label))
        if area >= min_area and (best is None or area > best[0]):
            best = (area, sl)
    if best is None:
        raise ValueError("could not locate a stable hair-color region")
    return best


def detect_anchors(rgba: np.ndarray, support_foot_screen: str = "average") -> dict[str, object]:
    height, width = rgba.shape[:2]
    rgb = rgba[:, :, :3].astype(np.int16)
    alpha = rgba[:, :, 3].astype(np.int16)
    red, green, blue = (rgb[:, :, i] for i in range(3))
    yy, xx = np.indices((height, width))

    hair_mask = (
        (alpha > 20)
        & (yy < height * 0.64)
        & (xx > width * 0.18)
        & (xx < width * 0.84)
        & (red > 80)
        & (green > 55)
        & (blue > 75)
        & (np.abs(red - blue) < 100)
        & (red > green * 1.03)
        & (blue > green * 0.90)
    )
    hair_area, hair_slice = largest_component(hair_mask, min_area=150)
    hair_top = int(hair_slice[0].start)

    boot_mask = (
        (alpha > 30)
        & (yy > height * 0.70)
        & (red > green * 1.08)
        & (green > blue * 1.10)
        & (red < 220)
        & (green < 180)
        & (blue < 145)
    )
    labels, _ = ndimage.label(boot_mask, structure=np.ones((3, 3), dtype=np.uint8))
    boots: list[dict[str, float]] = []
    for label, sl in enumerate(ndimage.find_objects(labels), start=1):
        if sl is None:
            continue
        local = labels[sl] == label
        if int(local.sum()) < 600:
            continue
        local_y, local_x = np.where(local)
        local_y = local_y + int(sl[0].start)
        local_x = local_x + int(sl[1].start)
        bottom = int(local_y.max())
        sole = local_y >= bottom - 20
        boots.append({
            "area": float(local.sum()),
            "sole_x": float(local_x[sole].mean()),
            "sole_y": float(bottom),
        })
    boots.sort(key=lambda item: item["area"], reverse=True)
    if len(boots) < 2:
        raise ValueError(f"expected two boot regions, detected {len(boots)}")
    boots = boots[:2]
    if support_foot_screen == "left":
        root_boot = min(boots, key=lambda boot: boot["sole_x"])
    elif support_foot_screen == "right":
        root_boot = max(boots, key=lambda boot: boot["sole_x"])
    else:
        root_boot = None
    root_x = (float(root_boot["sole_x"]) if root_boot is not None
              else float(np.mean([boot["sole_x"] for boot in boots])))
    root_y = (float(root_boot["sole_y"]) if root_boot is not None
              else float(np.mean([boot["sole_y"] for boot in boots])))
    body_height = root_y - hair_top
    if body_height < 500:
        raise ValueError(f"implausible head-to-floor height: {body_height:.1f}px")
    return {
        "hair_top_y": hair_top,
        "hair_region_area": hair_area,
        "boot_regions": boots,
        "source_floor_root_xy": [root_x, root_y],
        "support_foot_screen": support_foot_screen,
        "source_head_to_floor_px": body_height,
    }


def gif_delays_ms(source_frames: list[float], fps: float, hold_ms: int) -> list[int]:
    exact = [(source_frames[i + 1] - source_frames[i]) * 1000.0 / fps
             for i in range(len(source_frames) - 1)]
    exact.append(float(hold_ms))
    target_units = round(sum(exact) / 10.0)
    units = [max(1, math.floor(value / 10.0)) for value in exact]
    fractions = [value / 10.0 - math.floor(value / 10.0) for value in exact]
    while sum(units) < target_units:
        index = max(range(len(units)), key=lambda i: fractions[i])
        units[index] += 1
        fractions[index] = -1.0
    while sum(units) > target_units:
        choices = [i for i, value in enumerate(units) if value > 1]
        if not choices:
            break
        index = min(choices, key=lambda i: fractions[i])
        units[index] -= 1
        fractions[index] = 2.0
    return [value * 10 for value in units]


def save_contact(frames: list[Image.Image], source_frames: list[float], path: Path) -> None:
    columns = 4
    rows = math.ceil(len(frames) / columns)
    cell_h = CELL_SIZE + 24
    sheet = Image.new("RGB", (columns * CELL_SIZE, rows * cell_h), BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    for index, (frame, source_frame) in enumerate(zip(frames, source_frames)):
        preview = frame.resize((CELL_SIZE, CELL_SIZE), Image.Resampling.LANCZOS)
        x = (index % columns) * CELL_SIZE
        y = (index // columns) * cell_h
        sheet.paste(preview, (x, y), preview)
        draw.text((x + 4, y + CELL_SIZE + 4), f"{index:02d} / {source_frame:g}", fill=(20, 20, 20))
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path, optimize=True)


def save_guide_comparison(frames: list[Image.Image], source_frames: list[float],
                          guide_root: Path, guide_manifest: dict[str, object], path: Path,
                          audit_frames: list[dict[str, object]], root_xy: tuple[float, float],
                          frame_size: int) -> None:
    by_source = {float(frame["source_frame"]): frame for frame in guide_manifest["frames"]}
    audit_by_source = {float(frame["source_frame"]): frame for frame in audit_frames}
    columns = 4
    rows = math.ceil(len(frames) / columns)
    panel_size = CELL_SIZE
    cell_width = panel_size * 2
    row_height = panel_size + 24
    sheet = Image.new("RGB", (cell_width * columns, rows * row_height), BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    for index, (painted, source_frame) in enumerate(zip(frames, source_frames)):
        guide_info = by_source[source_frame]
        guide_rgb = np.asarray(Image.open(guide_root / guide_info["guide_png"]).convert("RGB"))
        guide_values = guide_rgb.astype(np.int16)
        neutral = ((guide_values.max(axis=2) - guide_values.min(axis=2) <= 40)
                   & (guide_values.min(axis=2) >= 200))
        edge = np.zeros(neutral.shape, dtype=bool)
        edge[[0, -1], :] = neutral[[0, -1], :]
        edge[:, [0, -1]] = neutral[:, [0, -1]]
        backdrop = ndimage.binary_propagation(
            edge, mask=neutral, structure=np.ones((3, 3), dtype=bool)
        )
        guide = Image.fromarray(
            np.dstack((guide_rgb, np.where(backdrop, 0, 255).astype(np.uint8))), "RGBA"
        )
        body = guide_info["body_landmarks_xy_px"]
        feet = [body["foot_R"], body["foot_L"]]
        source_root_x = float(np.mean([point[0] for point in feet]))
        source_root_y = float(np.mean([point[1] for point in feet]))
        frame_audit = audit_by_source[source_frame]
        effective_ratio = (
            float(frame_audit["scale"]) * float(frame_audit["source_head_to_floor_px"])
            / float(frame_audit["guide_head_to_floor_px"])
        )
        scaled_size = (round(guide.width * effective_ratio), round(guide.height * effective_ratio))
        resized = guide.convert("RGBa").resize(scaled_size, Image.Resampling.LANCZOS).convert("RGBA")
        dx = round(root_xy[0] - source_root_x * effective_ratio)
        dy = round(root_xy[1] - source_root_y * effective_ratio)
        guide_canvas = Image.new("RGBA", (frame_size, frame_size), (0, 0, 0, 0))
        left, top = max(0, dx), max(0, dy)
        right, bottom = min(frame_size, dx + resized.width), min(frame_size, dy + resized.height)
        if right > left and bottom > top:
            crop = resized.crop((left - dx, top - dy, right - dx, bottom - dy))
            guide_canvas.alpha_composite(crop, (left, top))
        guide_preview = guide_canvas.resize((panel_size, panel_size), Image.Resampling.LANCZOS)
        painted_preview = painted.resize((panel_size, panel_size), Image.Resampling.LANCZOS)
        x = (index % columns) * cell_width
        y = (index // columns) * row_height
        sheet.paste(guide_preview, (x, y), guide_preview)
        sheet.paste(painted_preview, (x + panel_size, y), painted_preview)
        draw.text((x + 4, y + panel_size + 4), f"{source_frame:g}: guide | paint", fill=(20, 20, 20))
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path, optimize=True)


def save_gif(frames: list[Image.Image], delays: list[int], path: Path,
             output_size: int = 768) -> int:
    canvases = []
    for frame in frames:
        canvas = Image.new("RGBA", frame.size, (*BACKGROUND, 255))
        canvas.alpha_composite(frame)
        canvases.append(canvas.resize((output_size, output_size), Image.Resampling.LANCZOS).convert("RGB"))
    palette_source = Image.new("RGB", (output_size, output_size * len(canvases)))
    for index, canvas in enumerate(canvases):
        palette_source.paste(canvas, (0, index * output_size))
    palette = palette_source.convert("P", palette=Image.Palette.ADAPTIVE, colors=255)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in canvases]
    path.parent.mkdir(parents=True, exist_ok=True)
    indexed[0].save(path, save_all=True, append_images=indexed[1:],
                    duration=delays, disposal=2, optimize=False)
    return sum(delays)


def save_comparison_gif(frames: list[Image.Image], source_frames: list[float], delays: list[int],
                        guide_root: Path, guide_manifest: dict[str, object], path: Path) -> None:
    by_source = {float(frame["source_frame"]): frame for frame in guide_manifest["frames"]}
    canvases = []
    for painted, source_frame in zip(frames, source_frames):
        guide = Image.open(guide_root / by_source[source_frame]["guide_png"]).convert("RGBA")
        guide = guide.resize((512, 512), Image.Resampling.LANCZOS)
        paint = painted.resize((512, 512), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (1024, 512), (*BACKGROUND, 255))
        canvas.alpha_composite(guide, (0, 0))
        canvas.alpha_composite(paint, (512, 0))
        canvases.append(canvas.convert("RGB"))
    palette_source = Image.new("RGB", (1024, 512 * len(canvases)))
    for index, canvas in enumerate(canvases):
        palette_source.paste(canvas, (0, index * 512))
    palette = palette_source.convert("P", palette=Image.Palette.ADAPTIVE, colors=255)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in canvases]
    path.parent.mkdir(parents=True, exist_ok=True)
    indexed[0].save(path, save_all=True, append_images=indexed[1:],
                    duration=delays, disposal=2, optimize=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-frames", required=True, type=Path)
    parser.add_argument("--guide-root", required=True, type=Path)
    parser.add_argument("--guide-manifest", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--target-height", type=float, default=600.0)
    parser.add_argument(
        "--fixed-scale", type=float,
        help=("use one pixel scale for every pose; this preserves natural height "
              "changes from crouching and avoids frame-by-frame camera zoom"),
    )
    parser.add_argument(
        "--guide-height-ratio", type=float,
        help=("scale each painted cutout so its detected head-to-floor height "
              "tracks this multiple of the matching Rokoko guide height"),
    )
    parser.add_argument("--root-x", type=float, default=512.0)
    parser.add_argument("--root-y", type=float, default=940.0)
    parser.add_argument(
        "--support-foot-screen", choices=("average", "left", "right"), default="average",
        help=("anchor the root to the leftmost or rightmost detected shoe in every frame; "
              "use only after confirming that shoe is the continuously planted support foot"),
    )
    parser.add_argument("--canvas-size", type=int, default=1024,
                        help="square transparent frame size; increase it to preserve scale around long weapons")
    parser.add_argument("--canvas-margin", type=int, default=16)
    parser.add_argument("--review-gif-size", type=int, default=768)
    parser.add_argument("--recovery-hold-ms", type=int, default=300)
    args = parser.parse_args()

    if args.fixed_scale is not None and args.guide_height_ratio is not None:
        parser.error("--fixed-scale and --guide-height-ratio cannot be used together")
    if args.canvas_size < 512:
        parser.error("--canvas-size must be at least 512 pixels")

    guide_manifest = json.loads(args.guide_manifest.read_text(encoding="utf-8"))
    guide_by_source = {float(frame["source_frame"]): frame for frame in guide_manifest["frames"]}
    raw_files = sorted(args.raw_frames.glob("swordsman_*.png"), key=parse_source_frame)
    if len(raw_files) < 16:
        parser.error("at least 16 individually painted poses are required")

    source_frames = [parse_source_frame(path) for path in raw_files]
    if any(source_frames[i] >= source_frames[i + 1] for i in range(len(source_frames) - 1)):
        parser.error("source-frame filenames must be strictly increasing")
    missing = [frame for frame in source_frames if frame not in guide_by_source]
    if missing:
        parser.error(f"no Blender guide frame for source frames: {missing}")

    frame_root = args.output_root / "master/frames"
    frame_root.mkdir(parents=True, exist_ok=True)
    timeline_frames = []
    normalized: list[Image.Image] = []
    audit_frames = []
    for index, (raw_path, source_frame) in enumerate(zip(raw_files, source_frames)):
        original = Image.open(raw_path).convert("RGBA")
        rgba = np.array(original, dtype=np.uint8)
        r, g, b, alpha = (rgba[:, :, i].astype(np.int16) for i in range(4))
        near_transparent = alpha <= 5
        red_markup = (alpha > 0) & (r > 150) & (g < 75) & (b < 95) & (r > g * 1.8)
        removed_red = int(red_markup.sum())
        rgba[near_transparent | red_markup, 3] = 0
        rgba[near_transparent | red_markup, :3] = 0
        anchors = detect_anchors(rgba, args.support_foot_screen)
        guide_info = guide_by_source[source_frame]
        guide_landmarks = guide_info["body_landmarks_xy_px"]
        guide_head_floor = max(
            float(guide_landmarks["foot_R"][1]),
            float(guide_landmarks["foot_L"][1]),
        ) - float(guide_landmarks["head"][1])
        if args.fixed_scale is not None:
            scale = args.fixed_scale
            scale_mode = "fixed_clip_scale"
        elif args.guide_height_ratio is not None:
            scale = (guide_head_floor * args.guide_height_ratio
                     / float(anchors["source_head_to_floor_px"]))
            scale_mode = "guide_relative_head_to_floor"
        else:
            scale = args.target_height / float(anchors["source_head_to_floor_px"])
            scale_mode = "per_frame_head_to_floor"
        requested_scale = scale
        source_bbox = Image.fromarray(rgba, "RGBA").getchannel("A").getbbox()
        if source_bbox is None:
            parser.error(f"frame {source_frame:g} has no visible pixels after cleanup")
        root_source_x, root_source_y = anchors["source_floor_root_xy"]
        x0, y0, x1, y1 = map(float, source_bbox)
        margin = max(0, int(args.canvas_margin))
        scale_caps: list[tuple[str, float]] = []
        if root_source_x > x0:
            scale_caps.append(("left", (args.root_x - margin) / (root_source_x - x0)))
        if x1 > root_source_x:
            scale_caps.append(("right", (args.canvas_size - margin - args.root_x) / (x1 - root_source_x)))
        if root_source_y > y0:
            scale_caps.append(("top", (args.root_y - margin) / (root_source_y - y0)))
        if y1 > root_source_y:
            scale_caps.append(("bottom", (args.canvas_size - margin - args.root_y) / (y1 - root_source_y)))
        max_canvas_scale = min(value for _, value in scale_caps)
        limiting_axis, _ = min(scale_caps, key=lambda item: item[1])
        scale = min(scale, max_canvas_scale)
        if not 0.40 <= scale <= 0.90:
            parser.error(f"frame {source_frame:g}: implausible canvas-fitted scale {scale:.3f}")
        if not 0.40 <= scale <= 0.90:
            parser.error(f"frame {source_frame:g}: implausible normalization scale {scale:.3f}")
        resized = Image.fromarray(rgba, "RGBA").convert("RGBa").resize(
            (round(original.width * scale), round(original.height * scale)), Image.Resampling.LANCZOS
        ).convert("RGBA")
        dx = round(args.root_x - float(root_source_x) * scale)
        dy = round(args.root_y - float(root_source_y) * scale)
        source_alpha_bbox = resized.getchannel("A").getbbox() or (0, 0, 0, 0)
        placed_alpha_bbox = (
            source_alpha_bbox[0] + dx,
            source_alpha_bbox[1] + dy,
            source_alpha_bbox[2] + dx,
            source_alpha_bbox[3] + dy,
        )
        if (placed_alpha_bbox[0] < 0 or placed_alpha_bbox[1] < 0
                or placed_alpha_bbox[2] > args.canvas_size or placed_alpha_bbox[3] > args.canvas_size):
            parser.error(
                f"frame {source_frame:g} would be clipped by the shared canvas: "
                f"{placed_alpha_bbox}; increase canvas margins before exporting"
            )
        frame = Image.new("RGBA", (args.canvas_size, args.canvas_size), (0, 0, 0, 0))
        frame.alpha_composite(resized, (dx, dy))
        output_array = np.array(frame)
        output_array[output_array[:, :, 3] <= 1, :3] = 0
        output_array[output_array[:, :, 3] <= 1, 3] = 0
        frame = Image.fromarray(output_array, "RGBA")
        out_path = frame_root / f"basicattack_se_{index:02d}.png"
        frame.save(out_path, optimize=True)
        normalized.append(frame)

        interval_ms = ((source_frames[index + 1] - source_frame) * 1000 / guide_manifest["source_fps"]
                       if index + 1 < len(source_frames) else args.recovery_hold_ms)
        timeline_frames.append({
            "sprite_frame": index,
            "source_frame": source_frame,
            "source_time_seconds": source_frame / guide_manifest["source_fps"],
            "guide_png": guide_info["guide_png"],
            "duration_ms_exact": round(interval_ms, 4),
        })
        audit_frames.append({
            "sprite_frame": index,
            "source_frame": source_frame,
            "raw_png": raw_path.name,
            "scale": round(scale, 6),
            "requested_scale": round(requested_scale, 6),
            "canvas_scale_cap": round(max_canvas_scale, 6),
            "canvas_scale_limited": scale < requested_scale,
            "canvas_scale_limiting_axis": limiting_axis if scale < requested_scale else None,
            "scale_mode": scale_mode,
            "guide_head_to_floor_px": round(guide_head_floor, 3),
            "target_root_xy": [args.root_x, args.root_y],
            "source_root_xy": [round(float(root_source_x), 3), round(float(root_source_y), 3)],
            "support_foot_screen": anchors["support_foot_screen"],
            "source_head_to_floor_px": round(float(anchors["source_head_to_floor_px"]), 3),
            "hair_top_y": anchors["hair_top_y"],
            "boot_regions": anchors["boot_regions"],
            "removed_saturated_red_pixels": removed_red,
            "translation_xy": [dx, dy],
            "unclipped_output_alpha_bbox": list(placed_alpha_bbox),
            "output_alpha_bbox": list(frame.getchannel("A").getbbox() or ()),
        })

    delays = gif_delays_ms(source_frames, float(guide_manifest["source_fps"]), args.recovery_hold_ms)
    review = args.output_root / "review"
    save_contact(normalized, source_frames, review / "basicattack-se-normalized-contact.png")
    save_guide_comparison(normalized, source_frames, args.guide_root, guide_manifest,
                          review / "basicattack-se-guide-comparison.png", audit_frames,
                          (args.root_x, args.root_y), args.canvas_size)
    total_ms = save_gif(normalized, delays, review / "basicattack-se-one-shot.gif",
                        args.review_gif_size)
    (args.output_root / "master/motion-timeline.json").write_text(
        json.dumps({
            "status": "REVIEW_ONLY_NOT_APPROVED",
            "motion": "Rokoko SwordFight_mixamo.fbx, Blender fixed-camera guide",
            "source_fps": guide_manifest["source_fps"],
            "frame_count": len(normalized),
            "one_shot": True,
            "final_recovery_hold_ms": args.recovery_hold_ms,
            "frames": timeline_frames,
            "gif_delays_ms": delays,
            "gif_total_ms": total_ms,
        }, indent=2) + "\n", encoding="utf-8")
    (args.output_root / "review/normalization-audit.json").write_text(
        json.dumps({
            "status": "REVIEW_ONLY_NOT_APPROVED",
            "root_xy_px": [args.root_x, args.root_y],
            "canvas_size_px": [args.canvas_size, args.canvas_size],
            "target_head_to_floor_px": args.target_height,
            "scale_is_frame_specific": args.fixed_scale is None,
            "scale_mode": (
                "fixed_clip_scale" if args.fixed_scale is not None else
                "guide_relative_head_to_floor" if args.guide_height_ratio is not None else
                "per_frame_head_to_floor"
            ),
            "fixed_clip_scale": args.fixed_scale,
            "guide_height_ratio": args.guide_height_ratio,
            "support_foot_screen": args.support_foot_screen,
            "root_and_scale_source": (
                "detected shoe anchors; one fixed scale for the full clip"
                if args.fixed_scale is not None else
                "matching Rokoko head-to-floor projection and detected painted head/boot anchors; "
                "support foot selected by screen side"
                if args.guide_height_ratio is not None else
                "detected hair-top and lower-boot regions in each painted cutout"
            ),
            "alpha_resize": "premultiplied RGBA, Lanczos; alpha <= 5 and saturated red markup removed",
            "frames": audit_frames,
        }, indent=2) + "\n", encoding="utf-8")
    save_comparison_gif(normalized, source_frames, delays, args.guide_root, guide_manifest,
                        review / "rokoko-vs-painted-one-shot.gif")
    print(json.dumps({
        "frames": len(normalized),
        "source_range": [source_frames[0], source_frames[-1]],
        "gif_duration_ms": total_ms,
        "median_scale": float(np.median([item["scale"] for item in audit_frames])),
        "review_contact": str(review / "basicattack-se-normalized-contact.png"),
        "review_gif": str(review / "basicattack-se-one-shot.gif"),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
