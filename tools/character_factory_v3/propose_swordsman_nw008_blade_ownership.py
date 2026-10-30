"""Propose transfer of only the unoccluded blade tip in NW BasicAttack 008."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/basic-attack-simple/NW'
ORDER = ('WeaponLightBack', 'BodyCostume', 'WeaponLightFront', 'HeadHair', 'Weapon', 'WeaponHandOccluder')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def compose(parts):
    out = Image.new('RGBA', (512, 512))
    for role in ORDER:
        out.alpha_composite(parts[role])
    return out

def build(out):
    if out.exists() or out.is_symlink():
        raise ValueError('choose a fresh output')
    parts = {}
    for role in ORDER:
        with Image.open(SOURCE / role / '008.png') as im:
            parts[role] = im.convert('RGBA')
    before = compose(parts)
    # Strictly visible blade segment, excluding the ambiguous scarf overlap below.
    stencil = Image.new('1', (512, 512))
    ImageDraw.Draw(stencil).polygon([(279, 226), (281, 226), (281, 240), (276, 240), (276, 233)], fill=1)
    select = np.array(stencil, dtype=bool)
    body = np.array(parts['BodyCostume']); weapon = np.array(parts['Weapon'])
    select &= body[:, :, 3] > 0
    if np.any(weapon[:, :, 3][select] != 0):
        raise ValueError('existing weapon overlaps proposed transfer')
    if any(np.any(np.asarray(parts[role])[:, :, 3][select] != 0) for role in ('HeadHair', 'WeaponHandOccluder', 'WeaponLightBack', 'WeaponLightFront')):
        raise ValueError('another role overlaps transfer')
    weapon[select] = body[select]
    body[select] = [0, 0, 0, 0]
    parts['Weapon'] = Image.fromarray(weapon, 'RGBA')
    parts['BodyCostume'] = Image.fromarray(body, 'RGBA')
    after = compose(parts)
    if not np.array_equal(np.asarray(before), np.asarray(after)):
        raise ValueError('composite changed')
    out.mkdir(parents=True)
    parts['Weapon'].save(out / 'Weapon.png'); parts['BodyCostume'].save(out / 'BodyCostume.png')
    Image.fromarray((select * 255).astype('uint8'), 'L').save(out / 'transfer-mask.png')
    before.save(out / 'recomposed.png')
    report = {'status':'PARTIAL_VISIBLE_BLADE_OWNERSHIP_PROPOSAL_NOT_APPROVED',
              'source_hashes':{role:sha(SOURCE / role / '008.png') for role in ORDER},
              'implementation_sha256':sha(Path(__file__)), 'transferred_nontransparent_pixels':int(select.sum()),
              'composite_exact_rgba':True,
              'limitations':['Only the clearly exposed tip is transferred; the lower blade/scarf seam and occluded blade are not resolved.', 'No underpainting of the concealed blade or costume is supplied; this is not a usable weapon swap.', 'Grip and other frames/directions remain unverified.']}
    (out / 'receipt.json').write_text(json.dumps(report, indent=2) + '\n')
    return report

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    print(json.dumps(build(p.parse_args().output)))
