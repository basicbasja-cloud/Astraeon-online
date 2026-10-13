"""Reproduce closed receiver assets after extract-parts.py.
Select the largest connected alpha component of each asset panel; discard detached
atlas background specks/neighbor fragments, never paint or alter retained pixels.
This normalization changes a shared asset once, not individual motion frames.
"""
from pathlib import Path
import hashlib,json
import cv2,numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return str(p.relative_to(ROOT))
data=json.loads((P/'parts.json').read_text());raw=P/'limbs-raw.png';im=Image.open(raw).convert('RGBA')
closed=[
 ('right.upperarm',[0,0,384,504],[245,137],[160,403],.18),
 ('right.forearm',[384,0,768,504],[618,112],[535,344],.18),
 ('left.upperarm',[768,0,1152,504],[974,143],[1035,414],.18),
 ('left.forearm',[1152,0,1536,590],[1379,120],[1372,361],.18),
 ('right.shin',[0,504,384,1024],[184,611],[191,842],.22),
 ('left.shin',[384,504,768,1024],[539,624],[584,844],.22),
 ('right.foot',[768,590,1152,1024],[977,760],None,.30),
 ('left.foot',[1152,590,1536,1024],[1374,760],None,.29)]
for name,box,a,b,width in closed:
 row=next(r for r in data['parts'] if r['name']==name)
 file=P/'parts'/('closed-'+name+'.png');im.crop(box).save(file)
 row.update(file=rel(file),source_atlas=rel(raw),atlas_box=box,pivot=[a[0]-box[0],a[1]-box[1]],end=[b[0]-box[0],b[1]-box[1]] if b else None,width_scale=width,source_role='imagegen-authored closed/filled hinge receiving surfaces; no hollow socket glyph')
 if name.endswith('.foot'):row['hinge_definition']='authored ankle-cuff center; filled receiving shaft extends above it'
torso=next(r for r in data['parts'] if r['name']=='torso');torso.update(file=rel(P/'torso-raw.png'),source_atlas=rel(P/'torso-raw.png'),atlas_box=[0,0,1081,1455],pivot=[490,370],end=[496,1150],width_scale=.145,source_role='imagegen repair removes embedded shoulder armor to prevent doubled articulated pauldrons')
receipts=[]
for row in data['parts']:
 path=ROOT/row['file'];path=path if path.is_absolute() else ROOT/path
 # Leave torso raw unmodified. All atlas-panel assets have one authored piece.
 if row['name']!='torso':
  a=np.array(Image.open(path).convert('RGBA'));n,labels,stats,_=cv2.connectedComponentsWithStats((a[:,:,3]>0).astype('uint8'),8)
  chosen=1+int(np.argmax(stats[1:,cv2.CC_STAT_AREA]));keep=labels==chosen;discard=int(((a[:,:,3]>0)&~keep).sum())
  a[~keep]=0;Image.fromarray(a).save(path)
  receipts.append({'name':row['name'],'discarded_detached_alpha_pixels':discard,'retained_rgba_unchanged':True,'policy':'largest connected alpha component; no per-frame cleanup'})
 row['file']=rel(path);row['sha256']=sha(path)
 if 'source_atlas' not in row:row['source_atlas']=rel(P/'atlas-raw.png')
data['atlas_file']=rel(P/'atlas-raw.png');data['scope']='16 authored part slots, one facing/one action. Head+hair combined. Asset-bind hinges are not automatic anatomical detections.'
(P/'parts.json').write_text(json.dumps(data,indent=2)+'\n');(P/'normalization-receipt.json').write_text(json.dumps(receipts,indent=2)+'\n')
print('REPAIRED_PART_BANK',len(data['parts']))
