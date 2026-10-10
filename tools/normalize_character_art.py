"""Normalize explicitly mapped original art cells without fitting or deforming limbs.

One source scale applies to the entire sheet; authored direction origins may correct
source-sheet row placement and remain fixed across every frame in that direction.
Every target direction/frame
must be declared, including an explanation for repeated source cells. Outputs are
lossless RGBA atlases and a provenance/layout receipt, not visual approval.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
from PIL import Image

DIRECTIONS = ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE']


def normalize(plan, repository, output):
    repository, output = Path(repository).resolve(), Path(output).resolve()
    if plan.get('schemaVersion') != '1.0' or plan.get('directions') != DIRECTIONS:
        raise ValueError('Expected normalization v1 and canonical directions')
    if plan.get('action') not in ['Idle', 'Walk', 'BasicAttack']:
        raise ValueError('Unsupported action')
    config = plan['source']
    source = (repository / config['file']).resolve()
    if not source.is_relative_to(repository) or 'private-ro-reference' in source.parts or '.git' in source.parts or '.private' in source.parts:
        raise ValueError('Only original repository artwork may enter production normalization')
    w, h = plan['canvas']
    sw, sh = config['cell']
    if any(type(n) is not int or n <= 0 for n in [w, h, sw, sh]):
        raise ValueError('Invalid cell dimensions')
    scale = config['scale']
    if type(scale) not in [int, float] or not math.isfinite(scale) or scale <= 0:
        raise ValueError('Invalid shared scale')
    for p in [plan['root'], config['root']]:
        if len(p) != 2 or any(type(n) not in [int, float] or not math.isfinite(n) for n in p):
            raise ValueError('Invalid registration root')
    direction_roots = config.get('directionRoots', {d: config['root'] for d in DIRECTIONS})
    if set(direction_roots) != set(DIRECTIONS):
        raise ValueError('Every authored direction origin is required')
    for p in direction_roots.values():
        if not isinstance(p, list) or len(p) != 2 or any(type(n) not in [int, float] or not math.isfinite(n) for n in p):
            raise ValueError('Invalid authored direction origin')
    count = plan['frameCount']
    if type(count) is not int or count <= 0:
        raise ValueError('Invalid frame count')
    if set(plan['frames']) != set(DIRECTIONS):
        raise ValueError('Every direction is required')
    with Image.open(source) as opened:
        opened.load()
        if opened.mode != 'RGBA' or opened.getchannel('A').getextrema()[0] != 0:
            raise ValueError('Original art must be RGBA with transparency')
        source_image = opened.copy()
    dx = round(plan['root'][0] - config['root'][0] * scale)
    dy = round(plan['root'][1] - config['root'][1] * scale)
    size = (round(sw * scale), round(sh * scale))
    if min(size) < 1:
        raise ValueError('Scale collapses source pixels')
    atlas = Image.new('RGBA', (w * count, h * 8))
    records = []
    for row, direction in enumerate(DIRECTIONS):
        source_root = direction_roots[direction]
        dx = round(plan['root'][0] - source_root[0] * scale)
        dy = round(plan['root'][1] - source_root[1] * scale)
        cells = plan['frames'][direction]
        if len(cells) != count:
            raise ValueError(f'Missing frames: {direction}')
        seen = set()
        for index, entry in enumerate(cells):
            if set(entry) - {'column', 'row', 'reuseReason'}:
                raise ValueError('Per-frame transforms and deformations are prohibited')
            column, source_row = entry['column'], entry['row']
            if any(type(n) is not int or n < 0 for n in [column, source_row]):
                raise ValueError('Invalid source grid location')
            cell_key = (column, source_row)
            if cell_key in seen and not str(entry.get('reuseReason', '')).strip():
                raise ValueError(f'Unexplained frame reuse: {direction}/{index}')
            seen.add(cell_key)
            bounds = (column * sw, source_row * sh, (column + 1) * sw, (source_row + 1) * sh)
            if bounds[2] > source_image.width or bounds[3] > source_image.height:
                raise ValueError('Source frame exceeds source image')
            raw_cell = source_image.crop(bounds)
            alpha = raw_cell.getchannel('A')
            borders = [(0,0,sw,1),(0,sh-1,sw,sh),(0,0,1,sh),(sw-1,0,sw,sh)]
            if any(alpha.crop(border).getextrema()[1] > 16 for border in borders):
                raise ValueError(f'Source art touches cell boundary: {direction}/{index}; do not silently crop a limb or blade')
            cell = raw_cell.resize(size, Image.Resampling.LANCZOS)
            painted = cell.getchannel('A').getbbox()
            if painted and (painted[0] + dx < 0 or painted[1] + dy < 0 or painted[2] + dx > w or painted[3] + dy > h):
                raise ValueError(f'Clipped painted pixels: {direction}/{index}; change shared registration or repair source art')
            normalized = Image.new('RGBA', (w, h))
            normalized.paste(cell, (dx, dy))
            atlas.paste(normalized, (index * w, row * h))
            records.append(dict(direction=direction, frame=index, sourceRect=list(bounds),
                                rect=[index * w, row * h, w, h],
                                sourceRoot=source_root, translation=[dx, dy],
                                pixelSHA256=hashlib.sha256(normalized.tobytes()).hexdigest(),
                                reuseReason=entry.get('reuseReason')))
    receipt = dict(schemaVersion='1.0', action=plan['action'], source=config['file'],
                   sourceSHA256=hashlib.sha256(source.read_bytes()).hexdigest(),
                   canvas=[w, h], root=plan['root'], sharedScale=scale,
                   translation=[round(plan['root'][0]-config['root'][0]*scale),round(plan['root'][1]-config['root'][1]*scale)],
                   directionOrigins=direction_roots,
                   frames=records, visualApproval=False)
    # Validate every cell before producing files.
    if source == output / 'atlas.png':
        raise ValueError('Output cannot overwrite the authoritative source sheet')
    output.mkdir(parents=True, exist_ok=True)
    atlas.save(output / 'atlas.png', compress_level=9)
    (output / 'layout.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', required=True, type=Path)
    parser.add_argument('--repository', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = normalize(json.loads(args.plan.read_text(encoding='utf8')), args.repository, args.output)
    print(f"Normalized {len(result['frames'])} explicit frames; visual approval remains pending")
