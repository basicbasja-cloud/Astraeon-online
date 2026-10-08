#!/usr/bin/env python3
"""Validate modular JSON schema, shared runtime contracts and lossless RGBA atlases.
Uses the project's existing jsonschema/Pillow authoring stack, with no npm install.
"""
import argparse
import json
import subprocess
from pathlib import Path
import jsonschema
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]

def unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result: raise ValueError(f'Duplicate metadata/frame ID: {key}')
        result[key]=value
    return result

def read_json(path):
    return json.loads(path.read_text(),object_pairs_hook=unique_object)

def validate_file(file,root,schema):
    d=read_json(file)
    jsonschema.Draft202012Validator(schema).validate(d)
    if file.parent.name!=d['characterId']: raise ValueError('Metadata directory differs from characterId')
    images={};alphas={}
    try:
        for atlas_id,atlas in d['atlases'].items():
            path=root/atlas['file']
            if not path.resolve().is_relative_to((root/'assets/characters').resolve()):
                raise ValueError(f'Atlas outside character asset namespace: {atlas_id}')
            image=Image.open(path);images[atlas_id]=image;image.load()
            if image.format!='PNG' or image.mode!='RGBA' or image.size!=(atlas['width'],atlas['height']):
                raise ValueError(f'Atlas image dimensions/format mismatch: {atlas_id}')
            alphas[atlas_id]=image.getchannel('A')
            if alphas[atlas_id].getextrema()[0]!=0: raise ValueError(f'Atlas lacks transparency: {atlas_id}')
        rectangles={}
        w,h=d['canvas']['frameWidth'],d['canvas']['frameHeight']
        for part_id,part in d['parts'].items():
            for frame_id,ref in part['frames'].items():
                image=images[ref['atlasId']];x,y,rw,rh=ref['rect']
                if rw!=w or rh!=h or x<0 or y<0 or x+rw>image.width or y+rh>image.height:
                    raise ValueError(f'Invalid canonical canvas: {frame_id}')
                # Untrimmed cells require at least one empty pixel around every frame.
                if x<1 or y<1 or x+rw>=image.width or y+rh>=image.height:
                    raise ValueError(f'Missing atlas gutter: {frame_id}')
                alpha=alphas[ref['atlasId']]
                if alpha.crop((x,y,x+rw,y+rh)).getextrema()[0]!=0:
                    raise ValueError(f'Frame lacks transparent background: {frame_id}')
                for box in [(x-1,y-1,x+rw+1,y),(x-1,y+rh,x+rw+1,y+rh+1),
                            (x-1,y,x,y+rh),(x+rw,y,x+rw+1,y+rh)]:
                    if alpha.crop(box).getextrema()[1]!=0: raise ValueError(f'Atlas bleed in gutter: {frame_id}')
                rectangles.setdefault(ref['atlasId'],set()).add(tuple(ref['rect']))
        # Sharing exactly the same frame is allowed; partially overlapping cells are not.
        for atlas_id,rects in rectangles.items():
            ordered=sorted(rects,key=lambda r:(r[1],r[0]))
            for i,(x,y,w,h) in enumerate(ordered):
                for xx,yy,ww,hh in ordered[i+1:]:
                    if yy>=y+h: break
                    if xx<x+w and xx+ww>x and yy<y+h: raise ValueError(f'Overlapping atlas frames: {atlas_id}')
    finally:
        for image in images.values():image.close()
    return len(d['atlases']),sum(len(p['frames']) for p in d['parts'].values())

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('definitions',nargs='*',type=Path)
    parser.add_argument('--repository',type=Path,default=ROOT)
    args=parser.parse_args();root=args.repository.resolve()
    schema=read_json(root/'assets/characters/schemas/sprite-definition.schema.json')
    jsonschema.Draft202012Validator.check_schema(schema)
    files=[file.resolve() for file in args.definitions] or sorted((root/'assets/characters').glob('*/sprite.json'))
    if not files: raise SystemExit('FAIL No sprite definitions')
    failures=[];atlas_count=frame_count=0
    for file in files:
        try:
            a,f=validate_file(file,root,schema);atlas_count+=a;frame_count+=f
            print('PASS schema, RGBA dimensions, transparency and gutters',file.relative_to(root),flush=True)
        except (ValueError,OSError,KeyError,jsonschema.ValidationError) as error:
            failures.append(f'{file}: {error}');print('FAIL',failures[-1],flush=True)
    result=subprocess.run(['node',str(root/'tools/validate-modular-metadata.cjs'),*[str(p) for p in files]],cwd=root)
    if failures or result.returncode:raise SystemExit(1)
    print(f'PASS {len(files)} definitions / {atlas_count} atlases / {frame_count} modular frame references')
