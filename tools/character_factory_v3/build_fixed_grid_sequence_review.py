"""Slice a sheet uniformly and build review GIFs without per-frame fitting.

This is a diagnostic artifact builder, not an animation acceptance gate.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage


def frames_from_sheet(path, output, size=768):
    source = Image.open(path).convert('RGBA')
    if source.width!=source.height:raise ValueError('A 4x4 square-cell sheet must be square; do not stretch rectangular cells')
    output.mkdir(parents=True, exist_ok=True)
    frames, records = [], []
    for index in range(16):
        col, row = index % 4, index // 4
        box = (col*source.width/4,row*source.height/4,(col+1)*source.width/4,(row+1)*source.height/4)
        # Fractional boundaries retain ONE scale even for 1254px / 4 cells.
        cell = source.convert('RGBa').transform((size,size),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC).convert('RGBA')
        a = np.array(cell)
        # Preserve real alpha. Only remove border-connected near-white for opaque inputs.
        if a[:,:,3].min() == 255:
            candidate = a[:,:,:3].min(axis=2) >= 242
            border = np.zeros(candidate.shape, bool)
            border[[0,-1],:] = candidate[[0,-1],:]
            border[:,[0,-1]] = candidate[:,[0,-1]]
            bg = ndimage.binary_propagation(border,mask=candidate)
            a[bg] = 0
        a[a[:,:,3]==0] = 0
        cell = Image.fromarray(a)
        cell.save(output/f'{index:03d}.png')
        alpha = np.array(cell)[:,:,3] > 16
        ys,xs = np.where(alpha)
        bbox = [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None
        records.append({'index':index,'source_box':box,'alpha_bbox':bbox,'touches_edge':bool(alpha[0].any() or alpha[-1].any() or alpha[:,0].any() or alpha[:,-1].any())})
        frames.append(cell)
    return frames,records,source.size


def gif(frames,path,durations):
    # One shared palette prevents independent per-frame color quantization flicker.
    backgrounds=[]
    for im in frames:
        bg=Image.new('RGBA',im.size,'#e8e8e8');bg.alpha_composite(im);backgrounds.append(bg.convert('RGB'))
    montage=Image.new('RGB',(frames[0].width*4,frames[0].height*4))
    for i,im in enumerate(backgrounds):montage.paste(im,((i%4)*im.width,(i//4)*im.height))
    palette=montage.quantize(colors=255)
    indexed=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in backgrounds]
    indexed[0].save(path,save_all=True,append_images=indexed[1:],duration=durations,loop=0,disposal=2,optimize=False)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sheet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--before',type=Path);a=p.parse_args()
    frames,records,source_size=frames_from_sheet(a.sheet,a.output/'frames')
    durations=[90]*4+[75]*2+[85]*2+[110]*2+[65]*2+[95]*4
    gif(frames,a.output/'normal.gif',durations);gif(frames,a.output/'slow.gif',[d*3 for d in durations])
    if a.before:
        old,_,_=frames_from_sheet(a.before,a.output/'before-frames');comp=[]
        for before,after in zip(old,frames):
            pair=Image.new('RGBA',(1536,800),'#e8e8e8');pair.alpha_composite(before,(0,32));pair.alpha_composite(after,(768,32));d=ImageDraw.Draw(pair);d.text((20,10),'BEFORE',fill='black');d.text((788,10),'REPAIR CANDIDATE - NOT APPROVED',fill='black');comp.append(pair)
        gif(comp,a.output/'before-after.gif',durations)
    report={'status':'REQUIRES_VISUAL_REVIEW','source':str(a.sheet),'source_sha256':hashlib.sha256(a.sheet.read_bytes()).hexdigest(),'source_size':source_size,'frames':records,'shared_cell_canvas':[768,768],'per_frame_scale_or_translation':False,'source_pose_registered':False,'durations_ms':durations,'timing_status':'preview cadence only; not runtime event metadata','owner_approved':False,'runtime_admitted':False,'limitations':['Uniform grid slicing cannot correct generation drift.','Bounding boxes describe visible pixels, not a skeleton root.','A looping preview does not establish a seamless action-to-idle transition.']}
    (a.output/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'output':str(a.output),'edge_frames':[r['index'] for r in records if r['touches_edge']]}))

if __name__=='__main__':main()
