"""Return thin detached cuff/shaft label fragments from HeadHair to the body.

The native 1536px pilot uses a five-pixel opening to identify the solid hair
component, then restores its original three-pixel contour neighborhood. Original
RGBA and the complete master remain unchanged; this is ownership correction.
"""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def retained_head(alpha):
    if alpha.shape != (1536, 1536):
        raise ValueError('This ownership profile is calibrated for native 1536px paint')
    opened = cv2.morphologyEx((alpha>32).astype('uint8'), cv2.MORPH_OPEN, np.ones((5, 5), 'uint8'))
    count, labels, stats, _ = cv2.connectedComponentsWithStats(opened, 8)
    if count < 2:
        raise ValueError('Missing solid head component')
    largest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    core = labels == largest
    distance = cv2.distanceTransform((~core).astype('uint8'), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    return (alpha>0) & (distance<=3)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['source', 'masters', 'output']:
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Choose a new ownership output')
    receipt = json.loads((args.source/'receipt.json').read_text())
    roles = ['BodyCostume', 'HeadHair', 'Weapon', 'WeaponHandOccluder']
    args.output.mkdir(parents=True)
    rows = []
    for row in receipt['frames']:
        index = row['index']
        master_path = args.masters/f'{index:03d}.png'
        if sha(master_path) != row['master_sha256']:
            raise ValueError('Proposal master changed')
        master = Image.open(master_path).convert('RGBA')
        pixels = np.array(master)
        arrays = {role: np.array(Image.open(args.source/role/f'{index:03d}.png').convert('RGBA')) for role in roles}
        alpha = arrays['HeadHair'][:, :, 3]
        keep = retained_head(alpha)
        released = (alpha>0) & ~keep
        arrays['HeadHair'][released] = 0
        arrays['BodyCostume'][released] = pixels[released]
        combined = Image.new('RGBA', master.size)
        for role in roles:
            part = Image.fromarray(arrays[role])
            combined.alpha_composite(part)
            folder = args.output/role
            folder.mkdir(exist_ok=True)
            part.save(folder/f'{index:03d}.png')
        if combined.tobytes() != master.tobytes():
            raise ValueError('Ownership transfer changed the master')
        rows.append({**row, 'head_fragment_pixels_reassigned': int(released.sum()),
                     'master_recomposition_changed_pixels': 0})
    (args.output/'renderer-source.py').write_bytes(Path(__file__).read_bytes())
    result = {'status': 'REFINED_VISIBLE_CUTOUTS_REQUIRES_HIDDEN_SURFACE_AND_SWAP_REVIEW',
              'implementation_sha256': sha(__file__), 'source_receipt_sha256': sha(args.source/'receipt.json'),
              'frames': rows, 'painted_rgba_changed': False, 'hidden_anatomy_authored': False,
              'owner_approved': False, 'runtime_admitted': False}
    (args.output/'receipt.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'poses': len(rows), 'master_recomposition_changed_pixels': 0,
                      'reassigned_pixels': sum(row['head_fragment_pixels_reassigned'] for row in rows)}))


if __name__ == '__main__':
    main()
