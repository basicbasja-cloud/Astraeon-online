#!/usr/bin/env python3
"""Pack normalized whole motion strips into untrimmed, padded, lossless RGBA atlases.
Input: <sources>/parts/<partId>/<AnimationId>/strip.png, S SW W NW N NE E SE rows.
No resize, mirror, root fitting, or individual part offsets happen during packing.
"""
import argparse
import json
import re
from pathlib import Path
from PIL import Image

DIRECTIONS = ['S','SW','W','NW','N','NE','E','SE']

def pack(definition, sources, repository, padding=2):
    if definition['directions'] != DIRECTIONS:
        raise ValueError('Noncanonical directions')
    if not isinstance(padding, int) or padding < 1 or padding > 16:
        raise ValueError('Padding must be an integer in 1..16')
    character = definition['characterId']
    if not re.fullmatch(r'[a-z][a-z0-9-]*', character):
        raise ValueError('Invalid characterId')
    width = definition['canvas']['frameWidth']
    height = definition['canvas']['frameHeight']
    definition['atlases'] = {}
    pending = []
    for part_id, part in definition['parts'].items():
        if not re.fullmatch(r'[a-z][a-z0-9-]*', part_id):
            raise ValueError('Invalid partId')
        part['frames'] = {}
        for animation, clip in definition['clips'].items():
            if not re.fullmatch(r'[A-Z][A-Za-z0-9]*', animation):
                raise ValueError('Invalid animationId')
            count = len(clip['durations'])
            path = sources / 'parts' / part_id / animation / 'strip.png'
            with Image.open(path) as source:
                source.load()
                if source.mode != 'RGBA' or source.size != (width*count, height*8):
                    raise ValueError(f'Invalid RGBA strip dimensions: {path}')
                if source.getchannel('A').getextrema()[0] != 0:
                    raise ValueError(f'Strip lacks transparent pixels: {path}')
                cell_w, cell_h = width+padding*2, height+padding*2
                size = (cell_w*count, cell_h*8)
                if max(size) > 4096:
                    raise ValueError(f'Atlas exceeds 4096; split clip into pages before publishing: {path}')
                atlas = Image.new('RGBA', size, (0,0,0,0))
                atlas_id = f'{part_id}-{animation.lower()}'
                if atlas_id in definition['atlases']:
                    raise ValueError(f'Duplicate atlas ID: {atlas_id}')
                file = f'assets/characters/{character}/atlases/{atlas_id}.png'
                definition['atlases'][atlas_id] = {'file':file, 'width':size[0], 'height':size[1]}
                for row, direction in enumerate(DIRECTIONS):
                    for index in range(count):
                        frame = source.crop((index*width,row*height,(index+1)*width,(row+1)*height))
                        if frame.getchannel('A').getextrema()[0] != 0:
                            raise ValueError(f'Frame lacks transparent background: {part_id}/{animation}/{direction}/{index}')
                        x,y = index*cell_w+padding,row*cell_h+padding
                        atlas.paste(frame,(x,y))
                        frame_id = f'{character}_{part_id}_{animation}_{direction}_{index:02d}'
                        part['frames'][frame_id] = {'atlasId':atlas_id,'rect':[x,y,width,height]}
                pending.append((repository/file,atlas))
    # Check every input before writing any output. Source strips remain authoritative.
    for path, atlas in pending:
        path.parent.mkdir(parents=True, exist_ok=True)
        atlas.save(path, format='PNG', optimize=False, compress_level=9)
    target = repository / 'assets' / 'characters' / character / 'sprite.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(definition, indent=2)+'\n')
    return target

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--definition', required=True, type=Path)
    parser.add_argument('--sources', required=True, type=Path)
    parser.add_argument('--repository', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    definition = json.loads(args.definition.read_text())
    print(pack(definition, args.sources, args.repository))
