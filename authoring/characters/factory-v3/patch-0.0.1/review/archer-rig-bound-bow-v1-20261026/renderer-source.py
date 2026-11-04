"""Paint a reusable bow/arrow profile over captured rig geometry, not body art.

Complete front/back weapon layers share the native canvas and source grips.
The reference-body occlusion split still needs painted-hand boundary review.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


PALETTE={'outline':'#332218','wood':'#8d572b','light':'#bd8b49','shine':'#e2bb77','leather':'#634027','gold':'#c6a05a','string':'#dfd2b1','shaft':'#93663c','steel0':'#d5ddd8','steel1':'#78868c','feather':'#eee4d0'}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def runs(points):
    result=[];current=[];previous=None
    for first,last in zip(points,points[1:]):
        owner='WeaponBack'if first['behind_body']or last['behind_body']else'Weapon'
        if owner!=previous:
            if len(current)>1:result.append((previous,current))
            current=[first];previous=owner
        current.append(last)
    if len(current)>1:result.append((previous,current))
    return result


def ribbon(points,widths,offsets=None):
    points=np.array(points,float);delta=np.gradient(points,axis=0);length=np.linalg.norm(delta,axis=1);normal=np.column_stack([-delta[:,1],delta[:,0]])/np.maximum(length[:,None],1e-6)
    offsets=np.zeros(len(points))if offsets is None else np.asarray(offsets)
    center=points+normal*offsets[:,None];widths=np.asarray(widths)
    return [tuple(p)for p in np.vstack([center+normal*widths[:,None]/2,(center-normal*widths[:,None]/2)[::-1]])]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--geometry',type=Path,required=True);p.add_argument('--style-reference',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--aa',type=int,default=3)
    a=p.parse_args()
    if a.output.exists():raise ValueError('Choose a fresh sprite profile')
    if not 2<=a.aa<=4:raise ValueError('Use 2–4x antialiasing')
    geometry=json.loads(a.geometry.read_text());size=geometry['canvas'];a.output.mkdir(parents=True);records=[];aa=a.aa
    for frame in geometry['frames']:
        layers={name:Image.new('RGBA',(size[0]*aa,size[1]*aa))for name in ['WeaponBack','Weapon']};draw={name:ImageDraw.Draw(im)for name,im in layers.items()};ppm=size[0]/frame['camera']['ortho_scale']
        for path in frame['paths']:
            material=path['material']
            for owner,part in runs(path['points']):
                coords=np.array([p['xy']for p in part],float)*aa;d=draw[owner]
                if material=='wood':
                    t=np.array([p['parameter']for p in part]);width=.036*ppm*(.45+.55*(1-np.abs(t)**1.5))*aa
                    d.polygon(ribbon(coords,width+1.7*aa),fill=PALETTE['outline']);d.polygon(ribbon(coords,width),fill=PALETTE['wood'])
                    d.polygon(ribbon(coords,width*.46,-width*.17),fill=PALETTE['light']);d.polygon(ribbon(coords,np.maximum(.55*aa,width*.11),-width*.36),fill=PALETTE['shine'])
                    for sign in [-1,1]:
                        grain=coords.copy();delta=np.gradient(coords,axis=0);normal=np.column_stack([-delta[:,1],delta[:,0]])/np.maximum(np.linalg.norm(delta,axis=1)[:,None],1e-6);grain+=normal*(width*(.17*sign+.035*np.sin(t*17)))[:,None]
                        d.line([tuple(p)for p in grain],fill='#754824',width=max(1,round(.45*aa)))
                    selected=np.where(abs(t)<=.12)[0]
                    if len(selected)>1:
                        q=coords[selected];w=width[selected]*1.05;d.polygon(ribbon(q,w),fill=PALETTE['leather']);d.polygon(ribbon(q,w*.2,-w*.27),fill='#956c40')
                    for mark in [-.13,.13]:
                        selected=np.where(abs(t-mark)<.018)[0]
                        if len(selected)>1:d.polygon(ribbon(coords[selected],width[selected]*1.08),fill=PALETTE['gold'])
                else:
                    width=(1.15 if material=='string' else 1.8)*aa;color=PALETTE[material]
                    d.line([tuple(p)for p in coords],fill=PALETTE['outline'],width=max(1,round(width+aa*.7)),joint='curve')
                    d.line([tuple(p)for p in coords],fill=color,width=max(1,round(width)),joint='curve')
        for poly in sorted(frame['polygons'],key=lambda x:x['camera_depth'],reverse=True):
            owner='WeaponBack'if poly['behind_body']else'Weapon';coords=[tuple(np.array(p['xy'])*aa)for p in poly['points']];d=draw[owner]
            d.polygon(coords,fill=PALETTE[poly['material']]);d.line(coords+[coords[0]],fill=PALETTE['outline'],width=max(1,round(.5*aa)))
        exported={}
        for name,image in layers.items():
            image=image.convert('RGBa').resize(tuple(size),Image.Resampling.LANCZOS).convert('RGBA');arr=np.array(image);arr[arr[:,:,3]==0]=0;image=Image.fromarray(arr);folder=a.output/frame['direction']/name;folder.mkdir(parents=True,exist_ok=True);path=folder/f'{frame["index"]:03d}.png';image.save(path);exported[name]=image
        master=Image.alpha_composite(exported['WeaponBack'],exported['Weapon']);folder=a.output/frame['direction']/'Master';folder.mkdir(exist_ok=True);path=folder/f'{frame["index"]:03d}.png';master.save(path)
        records.append({'direction':frame['direction'],'index':frame['index'],'arrow_visible':frame['arrow_visible'],'source_bow_grip_world':frame['bow_grip_world'],'source_nock_world':frame['right_nock_world'],'master_sha256':sha(path),'parts_sha256':{name:sha(a.output/frame['direction']/name/f'{frame["index"]:03d}.png')for name in exported},'visible_front_pixels':int((np.array(exported['Weapon'])[:,:,3]>0).sum()),'visible_back_pixels':int((np.array(exported['WeaponBack'])[:,:,3]>0).sum())})
        print('RIG_BOUND_WEAPON_SPRITE',frame['direction'],frame['index'],flush=True)
    (a.output/'receipt.json').write_text(json.dumps({'status':'RIG_BOUND_WEAPON_STYLE_CANDIDATE_REQUIRES_PAINTED_GRIP_REVIEW','profile':'oak-gold-v1','palette':PALETTE,'frames':records,'source_geometry_sha256':sha(a.geometry),'style_reference_sha256':sha(a.style_reference),'implementation_sha256':sha(Path(__file__)),'native_canvas':size,'arrow_length_m':geometry['arrow_length_m'],'per_frame_image_generation':False,'hand_or_body_pixels_generated':False,'camera_changed':False,'runtime_admitted':False},indent=2)+'\n');(a.output/'renderer-source.py').write_bytes(Path(__file__).read_bytes())


if __name__=='__main__':main()
