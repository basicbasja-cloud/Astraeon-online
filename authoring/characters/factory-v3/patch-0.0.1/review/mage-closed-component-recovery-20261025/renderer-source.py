"""Recover complete separated figures that straddle a generated sheet grid.

The generator may change the sheet's lattice spacing. A single explicit lattice
and one uniform transform are shared by all frames. Components select ownership
only: their bounding boxes never determine scale or per-frame positioning.
This produces research candidates, not native-pose or semantic approval.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage


def components(image, grid, pitch, minimum_area=1500):
    pixels = np.array(image.convert('RGBA'))
    labels, count = ndimage.label(pixels[:,:,3]>64,structure=np.ones((3,3)))
    area = np.bincount(labels.ravel())
    objects = ndimage.find_objects(labels)
    found = {}
    for label, box in enumerate(objects,1):
        if area[label] < minimum_area:
            continue
        y,x = box
        column = int(np.floor((x.start+x.stop)/2/pitch[0]))
        row = int(np.floor((y.start+y.stop)/2/pitch[1]))
        if not 0 <= column < grid[0] or not 0 <= row < grid[1]:
            raise ValueError('Figure outside explicit sheet lattice')
        index = row*grid[0]+column
        if index in found:
            raise ValueError('Multiple large components in one lattice slot')
        if x.start==0 or y.start==0 or x.stop==image.width or y.stop==image.height:
            raise ValueError('Figure touches the outer sheet edge')
        found[index] = {'label':label,'area':int(area[label]),
                        'box':[x.start,y.start,x.stop,y.stop]}
    if sorted(found)!=list(range(grid[0]*grid[1])):
        raise ValueError('Expected one complete independent component per pose')
    # Nearest labeled opaque figure owns only its nearby antialiasing band.
    main = np.isin(labels,[v['label'] for v in found.values()])
    distance, nearest = ndimage.distance_transform_edt(~main,return_indices=True)
    owners = labels[nearest[0],nearest[1]]
    owners[distance>3] = 0
    return pixels, owners, found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sheet',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--grid',type=int,nargs=2,required=True)
    parser.add_argument('--pitch',type=float,nargs=2,required=True)
    parser.add_argument('--scale',type=float,required=True)
    parser.add_argument('--offset',type=float,nargs=2,required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Choose a new research output')
    if min(*args.grid,*args.pitch,args.scale)<=0:
        raise ValueError('Positive layout dimensions required')
    image = Image.open(args.sheet).convert('RGBA')
    pixels, owners, found = components(image,args.grid,args.pitch)
    args.output.mkdir(parents=True)
    records,preview = [],[]
    for index in sorted(found):
        part = np.zeros_like(pixels)
        selected = owners==found[index]['label']
        part[selected] = pixels[selected]
        part[part[:,:,3]==0] = 0
        x = index%args.grid[0]*args.pitch[0]
        y = index//args.grid[0]*args.pitch[1]
        s = args.scale
        matrix = (1/s,0,x-args.offset[0]/s,0,1/s,y-args.offset[1]/s)
        frame = Image.fromarray(part).convert('RGBa').transform((1536,1536),Image.Transform.AFFINE,matrix,Image.Resampling.BILINEAR).convert('RGBA')
        path = args.output/f'{index:03d}.png'
        frame.save(path)
        background = Image.new('RGBA',frame.size,'#eee')
        background.alpha_composite(frame)
        preview.append(background.convert('RGB').resize((768,768),Image.Resampling.LANCZOS))
        records.append({'index':index,'raw_component':found[index],
                        'raw_owned_visible_pixels':int(np.count_nonzero(part[:,:,3])),
                        'source_lattice_origin':[x,y],'inverse_affine':matrix,
                        'output_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    # No endpoint cloning: expose the actual painted seam for review.
    preview[0].save(args.output/'component-cycle-diagnostic.gif',save_all=True,append_images=preview[1:],loop=0,duration=80)
    report = {'status':'COMPLETE_COMPONENTS_SHARED_LATTICE_RESEARCH_ONLY',
              'sheet_sha256':hashlib.sha256(args.sheet.read_bytes()).hexdigest(),
              'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'grid':args.grid,'pitch':args.pitch,'scale':s,'offset':args.offset,
              'per_frame_bounding_box_fit':False,'endpoint_cloning':False,
              'paint_alignment_approved':False,'runtime_admitted':False,'frames':records}
    (args.output/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    (args.output/'renderer-source.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'complete_components':len(records),'per_frame_fit':False,'runtime_admitted':False}))


if __name__ == '__main__':
    main()
