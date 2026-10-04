"""Read original cutout alpha for native ray-bake sampling; no image edits."""
import argparse,base64,json,zlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
world=json.loads((ROOT/'world/v3/wayfarer-spatial.json').read_text());cache={}
for material in world['materials'].values():
    spec=material.get('texture',{})
    if not spec.get('alphaCutoff') or not spec['file'].endswith(('.png','.webp')):continue
    with Image.open(ROOT/spec['file']) as image:
        alpha=image.getchannel('A');cache[spec['file']]={'size':image.size,'alpha':base64.b64encode(zlib.compress(alpha.tobytes())).decode()}
args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(cache))
print('Read original alpha for native cutout casts:',list(cache))
