"""Prepare an unclipped fixed-camera paint plate for any current source job.

Fit ONE viewport to the union of ALL source poses, even for a key-pose selection.
Generated art maps directly to the canonical authoring canvas in one resample.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image
from source_capture_identity import seal_source_reference


def source_union_viewport(frames,margin,author_size):
    if type(author_size)is not int or author_size<1:raise ValueError('A positive integer authoring size is required')
    if not frames or any(im.size!=frames[0].size for im in frames):raise ValueError('Source canvases differ or are empty')
    size=frames[0].width
    if frames[0].height!=size or size%author_size:raise ValueError('Source must be an integer multiple of the square authoring canvas')
    if type(margin)is not int or margin<1:raise ValueError('A positive fixed source margin is required')
    boxes=[]
    for im in frames:
        alpha=np.array(im.getchannel('A'))>0
        if not alpha.any():raise ValueError('Empty source pose')
        if alpha[0].any()or alpha[-1].any()or alpha[:,0].any()or alpha[:,-1].any():raise ValueError('Source render itself touches its canvas edge')
        y,x=np.where(alpha);boxes.append((x.min(),y.min(),x.max()+1,y.max()+1))
    factor=size//author_size
    left=max(0,math.floor((min(b[0]for b in boxes)-margin)/factor)*factor)
    top=max(0,math.floor((min(b[1]for b in boxes)-margin)/factor)*factor)
    right=min(size,math.ceil((max(b[2]for b in boxes)+margin)/factor)*factor)
    bottom=min(size,math.ceil((max(b[3]for b in boxes)+margin)/factor)*factor)
    return [left,top,right,bottom],factor


def prepare(guide,direction,indices,columns,margin,author_size,output):
    if output.exists():raise ValueError('Preserve previous paint plates; choose a fresh output')
    manifest_path=guide/'manifest.json';manifest=json.loads(manifest_path.read_text())
    if direction not in manifest['views']:raise ValueError('Direction was not captured')
    count=manifest['frame_count'];indices=list(range(count))if indices is None else indices
    if not indices or len(set(indices))!=len(indices)or any(type(i)is not int or not 0<=i<count for i in indices):raise ValueError('Invalid selected source poses')
    if type(columns)is not int or columns<1 or len(indices)%columns:raise ValueError('Use a complete rectangular source grid')
    frames=[];inputs=[]
    for i in range(count):
        path=guide/direction/f'{i:03d}.png'
        frames.append(Image.open(path).convert('RGBA'));inputs.append({'index':i,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    viewport,factor=source_union_viewport(frames,margin,author_size)
    left,top,right,bottom=viewport;width=right-left;height=bottom-top;rows=len(indices)//columns
    plate=Image.new('RGBA',(width*columns,height*rows),'white')
    for slot,index in enumerate(indices):plate.alpha_composite(frames[index].crop(tuple(viewport)),((slot%columns)*width,(slot//columns)*height))
    output.mkdir(parents=True);plate.convert('RGB').save(output/'source-plate.png')
    root=manifest['views'][direction]['frames'][0]['landmarks']['root']
    recipe={'grid':[columns,rows],'source_size':[author_size,author_size],
            'viewport':[v//factor for v in viewport],'source_pose_indices':indices,
            'frame_space':'canonical-authoring','canonical_root':[v/factor for v in root],
            'native_guide_viewport':viewport,'native_cell_size':[width,height],
            'guide_job':manifest['job']['id'],'guide_manifest_sha256':hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            'direction':direction,'all_source_frame_inputs':inputs,'fixed_margin_native_pixels':margin,
            'source_union_uses_all_frames_not_only_selected_keys':True,
            'per_frame_figure_fitting':False,'runtime_admitted':False}
    recipe_path=output/'viewport.json'
    recipe_path.write_text(json.dumps(recipe,indent=2)+'\n')
    seal_source_reference(recipe_path,guide)
    return recipe


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--guide',type=Path,required=True)
    p.add_argument('--direction',required=True);p.add_argument('--indices',type=int,nargs='+')
    p.add_argument('--columns',type=int,default=4);p.add_argument('--margin',type=int,default=96)
    p.add_argument('--author-size',type=int,default=768);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=prepare(a.guide,a.direction,a.indices,a.columns,a.margin,a.author_size,a.output)
    print(json.dumps({'guide_job':r['guide_job'],'source_viewport':r['native_guide_viewport'],'frame_space':r['frame_space'],'canonical_root':r['canonical_root']}))
