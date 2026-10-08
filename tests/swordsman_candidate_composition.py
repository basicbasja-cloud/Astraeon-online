"""Verify packed independent layers reproduce the reviewed full painted strip."""
import argparse
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('clip')
parser.add_argument('candidate')
parser.add_argument('--body', default='male')
args = parser.parse_args()
definition = json.loads((ROOT/f'assets/characters/swordsman-{args.body}-candidate/sprite.json').read_text())
review = ROOT/f'authoring/characters/swordsman-production/{args.body}/motion-candidates/{args.clip}/{args.candidate}/composite-strip.png'
intended = Image.open(review).convert('RGBA')
clip = definition['clips'][args.clip]; count = len(clip['durations'])
assert intended.size == (320*count, 320*8)
atlases = {}; checked = 0
for row, direction in enumerate(definition['directions']):
    sequence = clip['directions'][direction]
    for index, frame in enumerate(sequence['frames']):
        output = Image.new('RGBA', (320,320))
        order = frame.get('drawOrder', sequence.get('drawOrder', definition['drawOrder']))
        for slot in order:
            part_id = definition['defaultParts'][slot]
            frame_id = f'{definition["characterId"]}_{part_id}_{args.clip}_{direction}_{index:02d}'
            ref = definition['parts'][part_id]['frames'][frame_id]
            atlas_id = ref['atlasId']
            if atlas_id not in atlases:
                atlases[atlas_id] = Image.open(ROOT/definition['atlases'][atlas_id]['file']).convert('RGBA')
            x,y,w,h = ref['rect']
            assert (w,h)==(320,320)
            output.alpha_composite(atlases[atlas_id].crop((x,y,x+w,y+h)))
        expected = intended.crop((index*320,row*320,(index+1)*320,(row+1)*320))
        assert output.tobytes()==expected.tobytes(), f'Packed composite differs: {direction}/{index}'
        checked += 1
print(f'PASS {args.body} {args.clip}: {checked} packed composites reproduce the full painted review strip exactly')
