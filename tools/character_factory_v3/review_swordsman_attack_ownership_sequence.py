"""Review all preserved BasicAttack poses without changing artwork or fitting frames.

Exact recomposition is checked separately from semantic ownership. The weapon-off
view keeps the original hand occluder, as an equipment toggle actually would.
Neither the measurements nor these previews imply art or gameplay approval.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/basic-attack-simple'
DIRECTIONS = ('SW', 'NW', 'NE', 'SE')
ROLES = ('BodyCostume', 'HeadHair', 'Weapon', 'WeaponHandOccluder')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def composite(parts, roles):
    result = Image.new('RGBA', (512, 512))
    for role in roles:
        result.alpha_composite(parts[role])
    return result


def background(image, color):
    result = Image.new('RGBA', image.size, color)
    result.alpha_composite(image)
    return result.convert('RGB')


def build(output):
    if output.exists() or output.is_symlink():
        raise ValueError('Choose a fresh output; preserve previous reviews')
    timing_path = SOURCE / 'assembly-audit.json'
    timing = json.loads(timing_path.read_text())['durations_ms']
    if len(timing) != 16:
        raise ValueError('Unexpected retained sequence length')
    hashes = {str(timing_path.relative_to(ROOT)): sha(timing_path)}
    sequences = {}
    records = []
    for direction in DIRECTIONS:
        frames = []
        for index in range(16):
            paths = {r: SOURCE / direction / r / f'{index:03}.png'
                     for r in ('Master', *ROLES)}
            images = {}
            for role, path in paths.items():
                with Image.open(path) as image:
                    if image.mode != 'RGBA' or image.size != (512, 512):
                        raise ValueError(f'Unexpected source canvas: {path}')
                    images[role] = image.copy()
                hashes[str(path.relative_to(ROOT))] = sha(path)
            core = composite(images, ('BodyCostume', 'HeadHair', 'Weapon'))
            original = np.asarray(images['Master'])
            reconstructed = np.asarray(core)
            visible = (original[:, :, 3] > 0) | (reconstructed[:, :, 3] > 0)
            mismatch = int(np.any(original != reconstructed, axis=2)[visible].sum())
            if mismatch:
                raise ValueError(f'Core recomposition changed: {direction}/{index}')
            equipped = composite(images, ROLES)
            hidden = composite(images, ('BodyCostume', 'HeadHair', 'WeaponHandOccluder'))
            weapon = composite(images, ('Weapon',))
            hand = np.asarray(images['WeaponHandOccluder'])
            records.append({
                'direction': direction, 'index': index,
                'core_visible_rgba_mismatch_pixels': mismatch,
                'hand_overlay_changes_master_pixels': int(np.any(np.asarray(equipped) != original, axis=2).sum()),
                'weapon_nontransparent_pixels': int((np.asarray(weapon)[:, :, 3] > 0).sum()),
                'hand_nontransparent_pixels': int((hand[:, :, 3] > 0).sum()),
                'semantic_status': 'REQUIRES_VISUAL_REVIEW',
            })
            frames.append((images['Master'], hidden, weapon))
        sequences[direction] = frames
    # Validate all input frames before creating any output; no per-frame fitting.
    output.mkdir(parents=True)
    labels = ('PRESERVED MASTER', 'WEAPON OFF / HAND KEPT', 'WEAPON ONLY')
    for direction, frames in sequences.items():
        for start in range(0, 16, 4):
            board = Image.new('RGB', (1536, 4 * 544), '#303038')
            draw = ImageDraw.Draw(board)
            for row, index in enumerate(range(start, start + 4)):
                for col, image in enumerate(frames[index]):
                    x, y = col * 512, row * 544
                    board.paste(background(image, '#303038'), (x, y + 32))
                    draw.text((x + 8, y + 8), f'{direction}/{index:03} {labels[col]} - REVIEW ONLY', fill='white')
            board.save(output / f'{direction}-{start:02}-{start + 3:02}.png')
        # Full canvas, retained timing, single playback; no forced cyclic attack.
        for name, multiplier, color in (('normal', 1, '#303038'), ('slow-light', 3, '#eeeeee')):
            animation = []
            for index, triplet in enumerate(frames):
                panel = Image.new('RGB', (1536, 544), color)
                draw = ImageDraw.Draw(panel)
                for col, image in enumerate(triplet):
                    panel.paste(background(image, color), (col * 512, 32))
                    draw.text((col * 512 + 8, 8), f'{direction}/{index:03} {labels[col]} - REVIEW ONLY', fill='red')
                animation.append(panel)
            animation[0].save(output / f'{direction}-{name}.gif', save_all=True,
                              append_images=animation[1:], duration=[t * multiplier for t in timing],
                              optimize=False, disposal=2)
    if any(sha(ROOT / path) != digest for path, digest in hashes.items()):
        raise ValueError('A source changed during review')
    receipt = {
        'status': 'FULL_SEQUENCE_OWNERSHIP_DIAGNOSTIC_NOT_APPROVAL',
        'frames_reviewable': len(records), 'directions': list(DIRECTIONS),
        'source_sha256': hashes, 'implementation_sha256': sha(Path(__file__)),
        'duration_ms': timing, 'attack_gifs_loop_extension': False,
        'source_art_changed': False, 'runtime_admitted': False,
        'frames': records,
        'limitations': [
            'Recomposition does not validate ownership, hidden surfaces, grip or alpha edges.',
            'Weapon off retains the hand layer, which may itself contain weapon or costume pixels.',
            'No shape/contact/guide alignment metric or accepted action is implied.',
            'Retained timing includes the historical 250ms terminal preview hold; no game transition is shown.',
        ],
    }
    (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    result = build(parser.parse_args().output)
    print(json.dumps({k: result[k] for k in ('status', 'frames_reviewable', 'source_art_changed', 'runtime_admitted')}))
