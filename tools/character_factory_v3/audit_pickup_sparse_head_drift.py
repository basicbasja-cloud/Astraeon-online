"""Compare provisional head-mask motion with the locked SW guide, not an acceptance test."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / 'authoring/characters/factory-v3/patch-0.0.1/research'
GUIDE = ROOT / 'docs/character-factory/review/patch001-swordsman-pickup-35frame-20261029/manifest.json'
OFFSETS = {2: 4, 4: 20, 6: 13, 8: 0}

def audit():
 frames = json.loads(GUIDE.read_text())['views']['SW']['frames']
 results = []
 for mask_id in (0, 2):
  for repaired in (False, True):
   previous = None
   for index, extra_y in OFFSETS.items():
    if index == 8:
     masks = RESEARCH / 'swordsman-pickup-sw08-sam-20261029/head/masks'
    else:
     suffix = '006-bounded' if index == 6 and repaired else f'{index:03}'
     masks = RESEARCH / 'swordsman-pickup-sw-sparse-sam-20261029' / suffix / 'masks'
    pixels = np.asarray(Image.open(masks / f'{mask_id}.png').convert('L')) > 0
    y, x = np.where(pixels)
    if not x.size: raise ValueError(f'Empty head proposal: {masks}/{mask_id}.png')
    center = np.array([x.mean() * 384 / 1254, y.mean() * 384 / 1254 + 17 + extra_y])
    guide = np.array(frames[index]['landmarks']['head'])
    if previous is not None:
     residual = np.linalg.norm(((center - previous[0]) - (guide - previous[1])) * 240 / 768)
     results.append({'mask': mask_id, 'bounded_repair': repaired, 'from_frame': previous[2],
                     'to_frame': index, 'residual_runtime_px': round(float(residual), 3),
                     'mask_pixels': int(x.size)})
    previous = center, guide, index
 return {'status': 'RESEARCH_NOT_APPROVED', 'comparisons': results,
         'limitations': ['Masks can include clothing or omit face; centroids are not anatomical landmarks.',
          'Frames are nonadjacent and proposed foot registration is unverified.',
          'No visual quality, animation, cutout or runtime acceptance is implied.']}

if __name__ == '__main__':
 p = argparse.ArgumentParser(description=__doc__)
 p.add_argument('--output', type=Path, required=True)
 args = p.parse_args()
 result = audit()
 args.output.write_text(json.dumps(result, indent=2) + '\n')
 print(json.dumps(result))
