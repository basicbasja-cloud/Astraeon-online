#!/usr/bin/env python3
"""Prototype a narrow WeaponLight trail from sword-tip motion in a 4x4 master."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_blade_tip(cell: Image.Image) -> tuple[float, float]:
    """Find the long, bright, low-saturation blade component in one frame."""
    rgba = np.asarray(cell.convert("RGBA"), dtype=np.uint8)
    rgb = rgba[:, :, :3].astype(np.float32) / 255
    maximum = rgb.max(axis=2)
    minimum = rgb.min(axis=2)
    saturation = np.where(maximum > 0, (maximum - minimum) / np.maximum(maximum, 1e-5), 0)
    height, width = rgba.shape[:2]
    mask = ((saturation < 0.33) & (maximum > 0.40) &
            (np.arange(height)[:, None] > height * 0.30) & (rgba[:, :, 3] > 120))
    mask = ndimage.binary_closing(mask, iterations=2)
    labels, count = ndimage.label(mask)
    candidates: list[tuple[float, np.ndarray]] = []
    for label in range(1, count + 1):
        if int(np.sum(labels == label)) < 100:
            continue
        yy, xx = np.nonzero(labels == label)
        coordinates = np.column_stack((xx, yy)).astype(np.float64)
        values, vectors = np.linalg.eigh(np.cov(coordinates.T))
        elongation = float(values[-1] / max(values[0], 0.01))
        if elongation < 3:
            continue
        candidates.append((elongation * float(np.sqrt(len(coordinates))), coordinates))
    if not candidates:
        raise ValueError("Could not detect the sword blade in a source frame")
    _, coordinates = max(candidates, key=lambda item: item[0])
    values, vectors = np.linalg.eigh(np.cov(coordinates.T))
    axis = vectors[:, int(np.argmax(values))]
    center = coordinates.mean(axis=0)
    projection = (coordinates - center) @ axis
    ends = [center + float(projection.min()) * axis,
            center + float(projection.max()) * axis]
    torso = np.asarray([width * 0.50, height * 0.64])
    tip = max(ends, key=lambda point: float(np.linalg.norm(point - torso)))
    return float(tip[0]), float(tip[1])


def tapered_trail(start: tuple[float, float], end: tuple[float, float],
                  cell_size: int = 160) -> Image.Image:
    """Draw a short, tapered, softly curved line on a transparent cell."""
    supersample = 4
    size = cell_size * supersample
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    sx, sy = start
    ex, ey = end
    dx, dy = ex - sx, ey - sy
    length = float(np.hypot(dx, dy))
    if length < 2:
        return canvas.resize((cell_size, cell_size), Image.Resampling.LANCZOS)
    nx, ny = -dy / length, dx / length
    # Bend the trail away from the actor's center while keeping it close to the
    # actual swept tip path. This is a short motion mark, not a crescent.
    center = np.asarray([(sx + ex) / 2, (sy + ey) / 2])
    outward = center - np.asarray([80.0, 90.0])
    if nx * outward[0] + ny * outward[1] < 0:
        nx, ny = -nx, -ny
    bend = min(3.2, length * 0.18)
    control = ((sx + ex) / 2 + nx * bend, (sy + ey) / 2 + ny * bend)
    points: list[tuple[float, float]] = []
    widths: list[float] = []
    alphas: list[int] = []
    for step in range(17):
        t = step / 16
        u = 1 - t
        px = u * u * sx + 2 * u * t * control[0] + t * t * ex
        py = u * u * sy + 2 * u * t * control[1] + t * t * ey
        points.append((px * supersample, py * supersample))
        widths.append((0.65 + 2.45 * t) * supersample)
        alphas.append(round(72 + 168 * t))
    # Layer small tapered segments to keep the tail transparent and the contact
    # end bright without a thick aura.
    for index in range(len(points) - 1):
        alpha = alphas[index]
        width = max(1, round(widths[index]))
        draw.line((points[index], points[index + 1]), fill=(255, 181, 54, alpha),
                  width=width)
        if index >= 5:
            draw.line((points[index], points[index + 1]),
                      fill=(255, 242, 201, round(alpha * 0.92)), width=max(1, width // 2))
    return canvas.resize((cell_size, cell_size), Image.Resampling.LANCZOS)


def gif_durations(durations: list[int]) -> list[int]:
    output: list[int] = []
    elapsed = boundary = 0
    for duration in durations:
        elapsed += duration
        next_boundary = ((elapsed + 5) // 10) * 10
        output.append(max(10, next_boundary - boundary))
        boundary = next_boundary
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master", required=True, type=Path)
    parser.add_argument("--timeline", required=True, type=Path)
    parser.add_argument("--normalizer-provenance", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--preview-scale", type=int, default=2)
    args = parser.parse_args()

    master_path = args.master.resolve()
    timeline_path = args.timeline.resolve()
    normalizer_path = args.normalizer_provenance.resolve()
    output_root = args.output_root.resolve()
    master = Image.open(master_path).convert("RGBA")
    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    normalization = json.loads(normalizer_path.read_text(encoding="utf-8"))
    if len(timeline.get("frames", [])) != 16 or master.width == 0:
        raise ValueError("Expected a 16-frame BasicAttack master and timeline")
    if not 1 <= args.preview_scale <= 4:
        raise ValueError("Preview scale must be from 1 to 4")
    if int(normalization.get("frame_count", 0)) != 16:
        raise ValueError("Normalizer provenance must describe 16 frames")
    width, height = master.size
    x_edges = [round(index * width / 4) for index in range(5)]
    y_edges = [round(index * height / 4) for index in range(5)]
    tips: list[tuple[float, float]] = []
    for index in range(16):
        row, col = divmod(index, 4)
        cell = master.crop((x_edges[col], y_edges[row], x_edges[col + 1], y_edges[row + 1]))
        raw_x, raw_y = find_blade_tip(cell)
        record = normalization["frames"][index]
        scale = float(normalization["shared_scale"])
        left, top = map(float, record["normalized_translation_px"])
        tips.append((left + raw_x * scale, top + raw_y * scale))

    output_root.mkdir(parents=True, exist_ok=True)
    frames_dir = output_root / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    effects: list[Image.Image] = []
    records = []
    for index in range(16):
        layer = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
        active = 5 <= index <= 11  # frames 6-12; contact marker is frame 8.
        if active:
            previous = np.asarray(tips[index - 1], dtype=np.float64)
            current = np.asarray(tips[index], dtype=np.float64)
            movement = current - previous
            distance = float(np.linalg.norm(movement))
            direction = movement / max(distance, 1e-5)
            visible_length = min(24.0, max(12.0, distance))
            start = current - direction * visible_length
            end = current - direction * min(1.8, visible_length * 0.15)
            layer = tapered_trail(tuple(start), tuple(end))
            if index == 7:
                glint = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
                glow = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
                gd = ImageDraw.Draw(glow)
                cx, cy = map(round, current)
                gd.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=(255, 189, 66, 150))
                glint.alpha_composite(glow.filter(ImageFilter.GaussianBlur(1.2)))
                ImageDraw.Draw(glint).polygon([(cx, cy - 3), (cx + 2, cy),
                                               (cx, cy + 3), (cx - 2, cy)],
                                              fill=(255, 250, 225, 250))
                layer.alpha_composite(glint)
        frame_path = frames_dir / f"weaponlight_se_{index:02d}.png"
        layer.save(frame_path)
        effects.append(layer)
        records.append({"frame_index": index, "active": active,
                        "blade_tip_normalized_px": [round(v, 3) for v in tips[index]],
                        "effect_bounds": list(layer.getchannel("A").getbbox() or [])})

    vertical = Image.new("RGBA", (160, 2560), (0, 0, 0, 0))
    contact = Image.new("RGBA", (640, 640), (0, 0, 0, 0))
    over_master = Image.new("RGBA", (640, 640), (232, 232, 232, 255))
    behind_master = Image.new("RGBA", (640, 640), (232, 232, 232, 255))
    normalized_dir = normalizer_path.parent / "frames"
    for index, effect in enumerate(effects):
        row, col = divmod(index, 4)
        vertical.alpha_composite(effect, (0, index * 160))
        contact.alpha_composite(effect, (col * 160, row * 160))
        character = Image.open(normalized_dir / f"se_{index:02d}.png").convert("RGBA")
        over = Image.new("RGBA", (160, 160), (232, 232, 232, 255))
        over.alpha_composite(character)
        over.alpha_composite(effect)
        behind = Image.new("RGBA", (160, 160), (232, 232, 232, 255))
        behind.alpha_composite(effect)
        behind.alpha_composite(character)
        position = (col * 160, row * 160)
        over_master.alpha_composite(over, position)
        behind_master.alpha_composite(behind, position)
    vertical.save(output_root / "weaponlight-se-16.png")
    contact.save(output_root / "weaponlight-contact-4x4.png")
    over_master.save(output_root / "weaponlight-over-master-4x4.png")
    behind_master.save(output_root / "weaponlight-behind-master-4x4.png")

    durations = gif_durations([int(item["duration_ms"]) for item in timeline["frames"]])
    gif_frames = []
    for index, effect in enumerate(effects):
        base = Image.new("RGBA", (160, 160), (232, 232, 232, 255))
        character = Image.open(normalized_dir / f"se_{index:02d}.png").convert("RGBA")
        base.alpha_composite(effect)
        base.alpha_composite(character)
        if args.preview_scale > 1:
            size = (160 * args.preview_scale, 160 * args.preview_scale)
            base = base.resize(size, Image.Resampling.LANCZOS)
        gif_frames.append(base.convert("P", palette=Image.Palette.ADAPTIVE, colors=255))
    gif_path = output_root / "basicattack-se-weaponlight-loop.gif"
    gif_frames[0].save(gif_path, save_all=True, append_images=gif_frames[1:],
                       duration=durations, loop=0, optimize=False, disposal=2)
    provenance = {
        "status": "WEAPONLIGHT_TRAIL_PROTOTYPE_REQUIRES_VISUAL_REVIEW",
        "master": str(master_path), "master_sha256": sha256(master_path),
        "timeline": str(timeline_path), "timeline_sha256": sha256(timeline_path),
        "normalizer_provenance": str(normalizer_path),
        "normalizer_provenance_sha256": sha256(normalizer_path),
        "method": "bright low-saturation blade component; PCA tip; short tapered motion-vector trail",
        "active_frames_1_based": [6, 12], "contact_glint_frame_1_based": 8,
        "gif_preview_scale": args.preview_scale,
        "gif_preview_loop": True,
        "production_basicattack_loop": False,
        "frames": records,
        "files": {"effect_sheet": str((output_root / "weaponlight-se-16.png")),
                  "over_master_contact": str((output_root / "weaponlight-over-master-4x4.png")),
                  "behind_master_contact": str((output_root / "weaponlight-behind-master-4x4.png")),
                  "gif": str(gif_path)},
        "limitations": ["Single SE facing only.",
                        "Base full master has clipped sword pixels in frames 9-10.",
                        "Effect is a procedural prototype, not approved production art."],
    }
    (output_root / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n",
                                                   encoding="utf-8")
    print(json.dumps({"effect_sheet": str(output_root / "weaponlight-se-16.png"),
                      "contact": str(output_root / "weaponlight-over-master-4x4.png"),
                      "gif": str(gif_path), "provenance": str(output_root / "provenance.json")}))


if __name__ == "__main__":
    from PIL import ImageFilter
    main()
