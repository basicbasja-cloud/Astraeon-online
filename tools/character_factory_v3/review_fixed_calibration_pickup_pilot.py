"""Review one fixed global calibration of a rejected nine-pose paint pilot.

Uses first-frame dark-foreground bounds only to propose a single transform.
No per-frame adjustment, alpha extraction, landmark approval or import.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-male-pickup-sw-000-008-20261029'
SIZE=384

def bbox(im):
 a=np.asarray(im.convert('RGB'));ys,xs=np.where(np.min(a,axis=2)<230)
 if len(xs)==0:raise ValueError('No visible foreground')
 return [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]

def calibration(guide,paint):
 gb=bbox(guide);pb=bbox(paint);scale=(gb[3]-gb[1])/(pb[3]-pb[1])
 if not .4<=scale<=1.5:raise ValueError('Implausible shared calibration')
 tx=(gb[0]+gb[2])/2-scale*(pb[0]+pb[2])/2;ty=gb[3]-scale*pb[3]
 return scale,tx,ty

def fixed_transform(image,scale,tx,ty):
 return image.transform((SIZE,SIZE),Image.Transform.AFFINE,(1/scale,0,-tx/scale,0,1/scale,-ty/scale),resample=Image.Resampling.BICUBIC,fillcolor='white')

def build(out):
 if out.exists() or out.is_symlink():raise ValueError('Choose fresh output')
 paths=[SOURCE/'guide-contact.png',SOURCE/'generated-sheet.png'];sheets=[Image.open(p).convert('RGB').resize((1152,1152),Image.Resampling.LANCZOS) for p in paths]
 def cell(sheet,i):
  x=i%3*SIZE;y=i//3*SIZE;return sheet.crop((x,y,x+SIZE,y+SIZE))
 scale,tx,ty=calibration(cell(sheets[0],0),cell(sheets[1],0));frames=[];rows=[]
 for i in range(9):
  guide=cell(sheets[0],i);paint=cell(sheets[1],i);registered=fixed_transform(paint,scale,tx,ty);g=bbox(guide);r=bbox(registered)
  board=Image.new('RGB',(768,408),'white');board.paste(guide,(0,24));board.paste(registered,(384,24));draw=ImageDraw.Draw(board);draw.text((4,4),f'Guide {i:02}',fill='black');draw.text((388,4),f'One fixed transform {i:02}',fill='black');frames.append(board)
  rows.append({'frame':i,'guide_foreground_bbox':g,'calibrated_foreground_bbox':r,'edge_delta_px':[b-a for a,b in zip(g,r)]})
 out.mkdir(parents=True);frames[0].save(out/'comparison.gif',save_all=True,append_images=frames[1:],duration=[100]*8+[600],loop=0,optimize=False)
 report={'status':'ONE_TRANSFORM_DIAGNOSTIC_NOT_POSE_APPROVAL','scale':scale,'translation_px':[tx,ty],'calibration':'first-frame foreground height, horizontal center, bottom; applied identically to all nine cells','threshold':'minimum RGB <230','rows':rows,'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},'limitations':['Foreground bounds include weapon and costume and are not anatomical landmarks.','White background remains; transformed draft is not a master or cutout.','Nine frames and one view only; no motion, contact or game approval.']}
 (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
