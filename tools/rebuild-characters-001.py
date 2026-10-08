#!/usr/bin/env python3
"""Original painted 0.0.1 characters. Shared anatomy; offline, synchronized 2D parts.

Reference pixels are never imported. Generated masters are registered once, then
every costume/hair surface follows the same authored pose. No per-frame fitting.
Run --masters to inspect source registration before baking animation.
"""
import argparse, copy, hashlib, importlib.util, json, math, shutil, time
from functools import lru_cache
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'authoring/characters/patch-001'
OLD=ROOT/'authoring/characters/swordsman-production'
DIRECTIONS=['S','SW','W','NW','N','NE','E','SE']
LAYERS=['BaseBody','Outfit','Hair','Weapon','Headgear','BackAccessory']
NAMES=['head','neck','waist','shoulder_R','elbow_R','hand_R','shoulder_L','elbow_L','hand_L','hip_R','knee_R','foot_R','hip_L','knee_L','foot_L']
ORDER=['BackAccessory','BaseBody','Outfit','Hair','Weapon','Headgear']
PARTS={'BaseBody':'body-default','Outfit':'outfit-default','Hair':'hair-default','Weapon':'weapon-default','Headgear':'headgear-none','BackAccessory':'back-none'}
ANATOMY={'canvas':[320,320],'root':[160,264],'standingHeight':176,'headEnvelope':[48,50],
         'headToBodyRatio':50/176,'rigScale':.70,'pixelsPerMetre':320/2.65*.70,
         'directions':DIRECTIONS,'handedness':'anatomical-right','mirroring':'none'}
CLIPS={
 'Idle':([225]*8,True), 'Walk':([70]*16,True), 'Run':([60]*12,True),
 'Sprint':([48]*12,True), 'BasicAttack':([40,40,45,45,45,35,30,25,25,35,40,45,50,55,60,65],False),
 'SkillAction':([55,55,55,60,60,50,35,35,45,50,55,65,65,65],False),
 'CastChannel':([90]*12,True), 'CastRelease':([35,35,40,30,30,40,50,65,65,70],False),
 'Guard':([75]*10,True), 'Dash':([25,25,30,35,35,40,40,40,40,45],False),
 'Blink':([25,25,30,35,35,40,40,40,40,45],False), 'Hit':([25,25,35,40,45,50,50,50],False),
 'Death':([45,45,50,55,60,60,65,65,75,90,120,160],False),
 'Interact':([65]*8,False), 'Pickup':([60]*8,False), 'ItemUse':([65]*8,False),
 'Sit':([75]*8,False), 'Respawn':([75]*10,False),
}

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
painter=module('painted_authoring_001',ROOT/'tools/build-swordsman-production.py')
walk=module('walk_001',ROOT/'tools/swordsman-walk-cycle.py')
run=module('run_001',ROOT/'tools/swordsman-run-cycle.py')
actions=module('actions_001',ROOT/'tools/swordsman-action-poses.py')
GUIDES=json.loads((OLD/'male/pose-guides.json').read_text())['guides']
Y,X=np.mgrid[:320,:320]

@lru_cache(maxsize=64)
def warp_coordinates(source_key,target_key):
 """Rasterize the fixed source topology once, shared by cosmetic surfaces."""
 source=np.array(source_key);target=np.array(target_key)
 mx=np.full((320,320),-1.,dtype=np.float32);my=mx.copy()
 for indices in painter.Delaunay(source).simplices:
  original=source[indices];posed=target[indices]
  x0,y0=np.maximum(0,np.floor(posed.min(axis=0))).astype(int);x1,y1=np.minimum(319,np.ceil(posed.max(axis=0))).astype(int)
  if x1<x0 or y1<y0:continue
  matrix=np.vstack((posed.T,np.ones(3)))
  if abs(np.linalg.det(matrix))<1e-7:continue
  yy,xx=np.mgrid[y0:y1+1,x0:x1+1];bary=(np.linalg.inv(matrix)@np.vstack((xx.ravel(),yy.ravel(),np.ones(xx.size)))).T
  inside=(bary>=-1e-7).all(axis=1);coordinates=bary[inside]@original
  mx[yy.ravel()[inside],xx.ravel()[inside]]=coordinates[:,0];my[yy.ravel()[inside],xx.ravel()[inside]]=coordinates[:,1]
 return my,mx

def shared_warp(image,source,target):
 """Premultiplied RGBA, no alpha-bound fitting or runtime deformation."""
 keys=lambda values:tuple(tuple(float(v) for v in p) for p in values)
 my,mx=warp_coordinates(keys(source),keys(target))
 a=np.asarray(image).astype(np.float32)/255;a[:,:,:3]*=a[:,:,3:4]
 out=np.stack([ndimage.map_coordinates(a[:,:,c],[my,mx],order=1,mode='constant',cval=0,prefilter=False) for c in range(4)],axis=2)
 out[:,:,:3]=np.divide(out[:,:,:3],out[:,:,3:4],out=np.zeros_like(out[:,:,:3]),where=out[:,:,3:4]>0)
 return Image.fromarray(np.clip(np.rint(out*255),0,255).astype('uint8'))
painter.warp=shared_warp

def save_json(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2)+'\n')

def rgba(path):return Image.open(path).convert('RGBA')
def mask(im,selection):return painter.masked(im,selection)
def smooth(t):return walk.smooth(float(np.clip(t,0,1)))
def shift(im,old,new,angle=0):return painter.rigid_weapon(im,old,new,angle)

def normalize_sheet(path,body,kind):
 """One measured scale for each entire generated sheet, never alpha-fit frames."""
 sheet=rgba(path);cols=4;rows=4 if kind=='mage' else 2
 cw,ch=sheet.width/cols,sheet.height/rows
 scale=.53 if kind=='female' else .61 if kind=='mage' else .52
 result={}
 for row,d in enumerate(DIRECTIONS):
  offset=2 if kind=='mage' and body=='female' else 0
  cx,cy=(row%4)*cw,(row//4+offset)*ch
  cell=sheet.crop((round(cx),round(cy),round(cx+cw),round(cy+ch)))
  a=np.asarray(cell);yy,xx=np.mgrid[:cell.height,:cell.width];rgb=a[:,:,:3].astype(float)
  if kind=='mage':hair=(rgb[:,:,0]>rgb[:,:,1]*1.35)&(rgb[:,:,1]>rgb[:,:,2]*1.16)&(yy<ch*.24)&(a[:,:,3]>128)
  else:hair=(rgb[:,:,2]>rgb[:,:,1]*.94)&(rgb[:,:,2]>rgb[:,:,0]*.78)&(yy<ch*.45)&(a[:,:,3]>128)
  labels,n=ndimage.label(hair);sizes=np.bincount(labels.ravel());sizes[0]=0;hair=labels==sizes.argmax()
  points=np.argwhere(hair)
  if len(points)<20:raise ValueError('Missing directional head '+d)
  hx,hy=float(np.median(points[:,1])),float(np.median(points[:,0]))
  # Feet are in the lower anatomical band. Exclude transparent fringe.
  feet=np.argwhere((a[:,:,3]>128)&(yy>ch*.72)&(abs(xx-hx)<cw*.19))
  gy=float(feet[:,0].max())
  g=GUIDES[d];ox=hx-(g['head'][0]-160)/scale
  image=cell.transform((320,320),Image.Transform.AFFINE,(1/scale,0,ox-160/scale,0,1/scale,gy-264/scale),Image.Resampling.BICUBIC)
  # Register head paint to the SAME physical 48x50 envelope in every class.
  ar=np.asarray(image);rgb=ar[:,:,:3].astype(float)
  if kind=='mage':hm=(rgb[:,:,0]>rgb[:,:,1]*1.35)&(rgb[:,:,1]>rgb[:,:,2]*1.16)&(Y<134)&(abs(X-g['head'][0])<30)&(ar[:,:,3]>64)
  else:hm=(rgb[:,:,2]>rgb[:,:,1]*.94)&(rgb[:,:,2]>rgb[:,:,0]*.78)&(Y<148)&(ar[:,:,3]>64)
  labels,n=ndimage.label(hm);sizes=np.bincount(labels.ravel());sizes[0]=0;hm=labels==sizes.argmax()
  py,px=np.where(hm)
  sourceCenter=[(px.min()+px.max())/2,(py.min()+py.max())/2+4]
  # One authoring normalization, shared by head/face/hair and all later poses.
  halfWidth=max(px.max()-px.min()+1,1)/2;halfHeight=halfWidth*50/48
  corners=[[0,0],[319,0],[319,319],[0,319]]
  old=[[sourceCenter[0]+sx*halfWidth,sourceCenter[1]+sy*halfHeight] for sx,sy in [(-1,-1),(1,-1),(-1,1),(1,1)]]
  new=[[g['head'][0]+sx*24,g['head'][1]+sy*25] for sx,sy in [(-1,-1),(1,-1),(-1,1),(1,1)]]
  collar=[[g['head'][0]-36,g['neck'][1]+7],[g['head'][0]+36,g['neck'][1]+7],[g['waist'][0],g['waist'][1]]]
  # One continuous source mesh preserves the neckline; separate cutouts can
  # leave a transparent horizontal join when skull normalization changes size.
  result[d]=painter.warp(image,corners+old+collar,corners+new+collar)
 return result

def hair_mask(im,g,kind):
 a=np.asarray(im);r,gc,b=a[:,:,:3].astype(float).transpose(2,0,1)
 color=(r>gc*1.30)&(gc>b*1.16) if kind=='mage' else (b>gc*.94)&(b>r*.78)
 selection=color&(Y<g['neck'][1]+5)&(abs(X-g['head'][0])<30)&(a[:,:,3]>0)
 labels,n=ndimage.label(selection)
 if n:
  sizes=np.bincount(labels.ravel());sizes[0]=0;selection=labels==sizes.argmax()
 return ndimage.binary_fill_holes(selection)

def make_masters():
 SOURCE.mkdir(parents=True,exist_ok=True);save_json(SOURCE/'anatomy.json',ANATOMY)
 sources=SOURCE/'generated';sources.mkdir(exist_ok=True)
 incoming={'female-swordsman.png':'exec-89af3ab2-03c7-4cf1-969f-bad01b76da8a.png',
           'mage-bodies.png':'exec-9c212ef3-5541-40ab-a272-03b43913a946.png',
           'hair-bob.png':'exec-2e490e97-fc36-4590-b5f6-714a453a8406.png',
           'astral-court.png':'exec-4130c99d-8837-42cd-ab32-ecb5bed4d9d0.png'}
 for target,origin in incoming.items():
  if not (sources/target).exists():shutil.copy2(ROOT.parent/'generated_images'/origin,sources/target)
 bob=normalize_sheet(sources/'hair-bob.png','male','bob')
 court=normalize_sheet(sources/'astral-court.png','male','court')
 for cls in ['swordsman','mage']:
  for body in ['male','female']:
   character=f'{cls}-{body}-001';out=SOURCE/character/'masters';out.mkdir(parents=True,exist_ok=True)
   masters=None if cls=='swordsman' and body=='male' else normalize_sheet(sources/('mage-bodies.png' if cls=='mage' else 'female-swordsman.png'),body,'mage' if cls=='mage' else 'female')
   sheet=Image.new('RGBA',(320*4,320*2));layersheet=Image.new('RGBA',(320*6,320*8))
   for row,d in enumerate(DIRECTIONS):
    g=GUIDES[d];base=rgba(OLD/'male/modular-masters'/d/'BaseBody.png')
    if masters is None:layers={layer:rgba(OLD/'male/modular-masters'/d/(layer+'.png')) for layer in LAYERS}
    else:
     im=masters[d];a=np.asarray(im);rgb=a[:,:,:3].astype(float)
     hair=hair_mask(im,g,cls)
     face=(Y<g['neck'][1]-1)&(abs(X-g['head'][0])<28)&~hair&(a[:,:,3]>0)
     warm=(rgb[:,:,0]>rgb[:,:,1]*1.18)&(rgb[:,:,1]>rgb[:,:,2]*1.14)&(rgb[:,:,0]>110)&~hair
     hands=((X-g['hand_R'][0])**2+(Y-g['hand_R'][1])**2<9**2)|((X-g['hand_L'][0])**2+(Y-g['hand_L'][1])**2<9**2)
     skin=face|(hands&warm)
     base=mask(base,Y>=g['neck'][1]-2);base.alpha_composite(mask(im,skin))
     # A neutral scalp is supplied by the original underlying anatomy.
     if cls=='swordsman':weapon=painter.poly(g['weaponPolygon'])&(a[:,:,3]>0)&~skin
     else:
      # The staff's gold/jade silhouette is distinct from its robe surface.
      zone=X<g['head'][0]-14 if d in ['S','SW','W','NW'] else X>g['head'][0]+10
      gold=(rgb[:,:,0]>rgb[:,:,2]*1.7)&(rgb[:,:,0]>rgb[:,:,1]*1.06)
      jade=(rgb[:,:,1]>rgb[:,:,0]*1.12)&(rgb[:,:,2]>rgb[:,:,0]*1.10)
      weapon=zone&(gold|jade)&(Y>g['head'][1]-2)&(Y<264)&(a[:,:,3]>0)&~skin&~hair
      weapon=ndimage.binary_closing(weapon,iterations=1)&(a[:,:,3]>0)&~skin
     outfit=(a[:,:,3]>0)&~hair&~skin&~weapon
     layers={'BaseBody':base,'Outfit':mask(im,outfit),'Hair':mask(im,hair),'Weapon':mask(im,weapon),'Headgear':Image.new('RGBA',(320,320)),'BackAccessory':Image.new('RGBA',(320,320))}
    # Face is exposed anatomy; the old hairstyle must not remain underneath.
    altHair=mask(bob[d],hair_mask(bob[d],g,'swordsman'))
    layers['HairBob']=altHair
    ci=court[d];ca=np.asarray(ci);crgb=ca[:,:,:3].astype(float)
    ch=hair_mask(ci,g,'swordsman');cw=painter.poly(g['weaponPolygon']);cf=(Y<g['neck'][1]-1)&(abs(X-g['head'][0])<28)
    warm=(crgb[:,:,0]>crgb[:,:,1]*1.18)&(crgb[:,:,1]>crgb[:,:,2]*1.14)&(crgb[:,:,0]>110)
    hands=((X-g['hand_R'][0])**2+(Y-g['hand_R'][1])**2<8**2)|((X-g['hand_L'][0])**2+(Y-g['hand_L'][1])**2<8**2)
    layers['OutfitCourt']=mask(ci,~ch&~cw&~cf&~(hands&warm))
    cell=Image.new('RGBA',(320,320))
    for layer in ORDER:cell.alpha_composite(layers[layer])
    for col,layer in enumerate(LAYERS):
     path=out/d/(layer+'.png');path.parent.mkdir(exist_ok=True);layers[layer].save(path)
     layersheet.paste(layers[layer],(col*320,row*320))
    altHair.save(out/d/'HairBob.png');layers['OutfitCourt'].save(out/d/'OutfitCourt.png');cell.save(out/d/'composite.png');sheet.paste(cell,(row%4*320,row//4*320))
   sheet.save(out/'directions.png');layersheet.save(out/'layers.png');save_json(out/'registration.json',{'anatomy':ANATOMY,'guides':GUIDES,'status':'REVIEW_CANDIDATE','sourceScale':'One transform per source master sheet; no animation frame fitting'})
   print('MASTERS',character,flush=True)

def pose(clip,index,count,d,cls):
 """One original shared pose, then projected to eight cameras; no mirroring."""
 g=GUIDES[d];phase=index/count if CLIPS[clip][1] else index/(count-1);az=-DIRECTIONS.index(d)*math.pi/4;px=ANATOMY['pixelsPerMetre']
 def project(v):
  x,y,z=np.asarray(v,float);return np.array([px*(-math.cos(az)*x+math.sin(az)*y),px/math.sqrt(2)*(math.sin(az)*x+math.cos(az)*y-z)])
 target={n:np.array(g[n],float) for n in NAMES};footdata=None;angle=0.;wholeAngle=0.;headAngle=0.
 if clip in ['Walk','Run','Sprint']:
  cycle=walk if clip=='Walk' else run;p=cycle.pose(phase);ref=cycle.pose(.25);footdata=p['feet']
  pelvisShift=project(p['pelvis']-[0,0,1.035])
  for n in NAMES:
   if not n.startswith(('hip','knee','foot')):target[n]+=pelvisShift
  for side in ['R','L']:
   for n in ['hip','knee']:target[n+'_'+side]=np.array([160.,264.])+project(p['feet'][side][n])
   target['foot_'+side]=np.array([160.,264.])+project(p['feet'][side]['sole'])
   for n,bone,end in [('shoulder','upperarm',0),('elbow','upperarm',1),('hand','forearm',1)]:target[n+'_'+side]+=project(np.asarray(p['bones'][side+'-'+bone][end])-np.asarray(ref['bones'][side+'-'+bone][end]))*(.55 if clip=='Walk' else 1.)
  if clip in ['Run','Sprint']:
   for n in NAMES:
    if not n.startswith(('foot','knee','hip')):target[n]+=project([0,.13*np.clip((g['waist'][1]-g[n][1])/75,0,1)*(1.2 if clip=='Sprint' else 1),0])
 elif clip in ['BasicAttack','SkillAction','Hit'] and cls=='swordsman':
  return painter.pose(clip,index,count,d,g)+({'wholeAngle':0.,'headAngle':0.,'phase':phase},)
 else:
  activity=math.sin(math.pi*phase)
  if clip=='Idle':
   for n in NAMES:
    if not n.startswith(('hip','knee','foot')):target[n]+=[0,-.7*math.sin(math.tau*phase)]
  elif clip in ['BasicAttack','SkillAction','CastChannel','CastRelease','Guard','ItemUse','Interact']:
   lift=activity if clip not in ['Guard','CastChannel'] else .85+.05*math.sin(math.tau*phase)
   if clip in ['BasicAttack','SkillAction','CastRelease']:
    lift=smooth(phase/.32) if phase<.32 else 1-smooth((phase-.48)/.52)
   if clip=='ItemUse':lift=activity*.75
   if clip=='Interact':lift=activity*.50
   for side,sign in [('R',1),('L',-1)]:
    target['hand_'+side]+=project([-sign*.09,.12,.38])*lift
    target['elbow_'+side]+=project([-sign*.025,.025,.17])*lift
   angle=0. if cls=='mage' else -40*lift
  elif clip=='Hit':
   for n in ['head','neck','waist','shoulder_R','shoulder_L','elbow_R','elbow_L','hand_R','hand_L']:target[n]+=project([0,-.10*activity,-.025*activity])
  elif clip in ['Pickup','Sit']:
   down=activity if clip=='Pickup' else smooth(phase/.6)
   for n in ['head','neck','waist','shoulder_R','shoulder_L','elbow_R','elbow_L','hand_R','hand_L']:target[n]+=project([0,.09*down,-.35*down])
   for side in ['R','L']:target['knee_'+side]+=project([0,.1*down,0])
  elif clip in ['Dash','Blink']:
   for n in NAMES:
    if not n.startswith(('foot','knee','hip')):target[n]+=project([0,.17*activity,-.12*activity])
  elif clip in ['Death','Respawn']:
   fall=smooth((phase-.1)/.78) if clip=='Death' else 1-smooth(phase/.9)
   # Fall is authored into all layers, with one ground pivot. No runtime squash.
   wholeAngle=(78 if d in ['S','SW','W','NW'] else -78)*fall
   headAngle=0
 corners=[[0,0],[319,0],[319,319],[0,319]];support=[[g['head'][0]+dx,g['head'][1]+dy] for dx,dy in [(-30,-28),(30,-28),(-30,16),(30,16)]]
 headShift=target['head']-g['head'];src=corners+[g[n] for n in NAMES]+support;dst=corners+[target[n].tolist() for n in NAMES]+[(np.array(p)+headShift).tolist() for p in support]
 sockets={'root':[160,264],'head':target['head'].tolist(),'hand_R':target['hand_R'].tolist(),'hand_L':target['hand_L'].tolist(),'back':target['neck'].tolist(),'waist':target['waist'].tolist(),'foot_R':target['foot_R'].tolist(),'foot_L':target['foot_L'].tolist()}
 for side in ['R','L']:
  sockets['ankle_'+side]=(np.array([160.,264.])+project(footdata[side]['ankle']) if footdata else target['foot_'+side]+[0,-12]).tolist()
  if footdata:
   for n in ['heel','toe']:sockets[n+'_'+side]=(np.array([160.,264.])+project(footdata[side][n])).tolist()
 if wholeAngle:
  a=math.radians(wholeAngle);c,s=math.cos(a),math.sin(a);pivot=np.array([160.,200.]);fall=abs(wholeAngle)/78
  for n,v in list(sockets.items()):
   if n=='root':continue
   x,y=np.array(v)-pivot;sockets[n]=[160+c*x-s*y,200+60*fall+s*x+c*y]
 return src,dst,sockets,angle,{'wholeAngle':wholeAngle,'headAngle':headAngle,'phase':phase}

def bake(character,only=None):
 cls,body,_=character.split('-');directory=SOURCE/character;out=directory/'normalized';guides=GUIDES
 definition={'version':'0.1','characterId':character,'classId':'Swordsman' if cls=='swordsman' else 'Mage','bodyVariant':body,'directions':DIRECTIONS,'mirroring':'none',
  'tags':['DEV_ONLY','PLACEHOLDER','NOT_FINAL_ART','PATCH_001_FULL_MOTION_REVIEW'],
  'source':{'status':'DEV_ONLY','reference':str((directory/'masters/directions.png').relative_to(ROOT)),'approvedBy':None,'camera':'Shared original painted 45 degree elevated camera','handedness':'right','normalization':{'sourceFrameWidth':320,'sourceFrameHeight':320,'sourceRootAnchor':[160,264],'scale':1},'designLocks':['shared 176 pixel body height','shared 48x50 head envelope','shared anatomical rig','right-hand weapons','separate hair and outfit','no runtime mirroring']},
  'canvas':{'frameWidth':320,'frameHeight':320,'rootAnchorX':160,'rootAnchorY':264,'referenceHeight':176},'slots':{n:n for n in LAYERS},'defaultParts':PARTS,'drawOrder':ORDER,'clips':{},'parts':{part:{'slot':slot,'cosmeticId':{'Hair':'hair-native','Outfit':cls+'-traveler'}.get(slot,part),'frames':{}} for slot,part in PARTS.items()},'atlases':{}}
 definition['parts']['hair-bob']={'slot':'Hair','cosmeticId':'silver-bob','frames':{}}
 definition['parts']['outfit-court']={'slot':'Outfit','cosmeticId':'astral-court','frames':{}}
 review=directory/'review';review.mkdir(exist_ok=True)
 for clip,(durations,loop) in CLIPS.items():
  if only and clip not in only:continue
  count=len(durations);strips={n:Image.new('RGBA',(320*count,320*8)) for n in [*LAYERS,'HairBob','OutfitCourt']};directions={};film=Image.new('RGBA',(320*count,320*8));st=time.time()
  for row,d in enumerate(DIRECTIONS):
   g=guides[d];masters={n:rgba(directory/'masters'/d/(n+'.png')) for n in strips};frames=[]
   for index in range(count):
    src,dst,sockets,angle,extra=pose(clip,index,count,d,cls);fall=extra['wholeAngle']
    if fall:
     # Pre-fall sockets are used once for source baking; then all parts rotate
     # together. Their final sockets receive the identical transform above.
     _,_,local,_,_=pose('Idle',0,8,d,cls)
     target=dst
    else:local=sockets
    layers={}
    for layer,master in masters.items():
     if layer=='Weapon':image=shift(master,g['hand_R'],local['hand_R'],angle)
     elif layer in ['Hair','HairBob']:image=shift(master,g['head'],local['head'],extra['headAngle'])
     elif layer in ['Headgear','BackAccessory']:image=master
     elif cls=='swordsman':image=painter.painted_body_motion(master,src,dst,g,local,d,'Outfit' if layer=='OutfitCourt' else layer,articulateArms=clip in ['BasicAttack','SkillAction','Guard','CastChannel','CastRelease','Interact','ItemUse'],armBehind=d in ['W','NW','N','NE'])
     else:image=painter.warp(master,src,dst)
     if fall:image=shift(image,[160,200],[160,200+60*abs(fall)/78],fall)
     layers[layer]=image;strips[layer].paste(image,(index*320,row*320))
    order=['BackAccessory','Weapon','BaseBody','Outfit','Hair','Headgear'] if d in ['NW','N','NE'] and clip in ['BasicAttack','Guard'] else ORDER
    composite=Image.new('RGBA',(320,320))
    for n in order:composite.alpha_composite(layers[n])
    film.paste(composite,(index*320,row*320));frames.append({'frameIndex':index,'sockets':sockets,'drawOrder':order})
   directions[d]={'frames':frames}
  for layer,strip in strips.items():
   part={'HairBob':'hair-bob','OutfitCourt':'outfit-court'}.get(layer,PARTS.get(layer));path=out/'parts'/part/clip/'strip.png';path.parent.mkdir(parents=True,exist_ok=True);strip.save(path)
  film.save(review/(clip+'-strip.png'))
  # Review at actual game size, with all directions and every frame visible.
  small=Image.new('RGB',(count*112,8*126),(27,42,49));dr=ImageDraw.Draw(small)
  for row,d in enumerate(DIRECTIONS):
   for index in range(count):
    cell=film.crop((index*320,row*320,(index+1)*320,(row+1)*320)).resize((112,112),Image.Resampling.LANCZOS);small.paste(cell,(index*112,row*126),cell);dr.text((index*112+4,row*126+112),f'{d} {index:02d}',fill='#d7c58e')
  small.save(review/(clip+'-frames.png'))
  entry={'loop':loop,'durations':durations,'directions':directions,'tags':['PRODUCED','REQUIRES_OWNER_VISUAL_REVIEW']}
  if clip in ['Walk','Run','Sprint']:
   cycle=walk if clip=='Walk' else run;entry['cycleDistance']=cycle.CYCLE_DISTANCE*ANATOMY['pixelsPerMetre']/(49.497/(70*(92/76)/176))
  definition['clips'][clip]=entry
  print('BAKED',character,clip,count*8,'poses',round(time.time()-st,1),'seconds',flush=True)
 save_json(directory/'definition.json',definition)
 save_json(directory/'provenance.json',{'status':'PRODUCED_REVIEW_CANDIDATE','ownerApproval':None,'baseCommit':'1b8b1c70be8b018bd5a4a5a857730b71e0740a70','anatomy':ANATOMY,'clips':{k:len(v['durations'])*8 for k,v in definition['clips'].items()},'method':'Registered original painted masters, original shared articulated walk/run and authored action poses; whole strips baked offline; no RO pixels','sourceHash':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
 return directory/'definition.json',out

def pack_runtime(character):
 """One shared 1/2 scale for every whole strip, canvas, anchor and socket.

 Keep the 320px authoring sheets intact. The 160px runtime canvas still exceeds
 the game's normal character display size, while using 1/4 the decoded RAM.
 No trimming, frame fitting, part offsets or direction mirroring is introduced.
 """
 directory=SOURCE/character;definition=json.loads((directory/'definition.json').read_text())
 canvas=definition['canvas']
 for key in ['frameWidth','frameHeight','rootAnchorX','rootAnchorY','referenceHeight']:canvas[key]=round(canvas[key]/2)
 definition['source']['normalization']={'sourceFrameWidth':320,'sourceFrameHeight':320,'sourceRootAnchor':[160,264],'scale':.5}
 definition['source']['designLocks'].append('uniform 0.5 runtime scale for all classes, frames and layers')
 for clip in definition['clips'].values():
  for direction in clip['directions'].values():
   for frame in direction['frames']:
    frame['sockets']={key:[v/2 for v in values] for key,values in frame['sockets'].items()}
 normalized=directory/'runtime-160'
 for part in definition['parts']:
  for clip in definition['clips']:
   source=directory/'normalized/parts'/part/clip/'strip.png';target=normalized/'parts'/part/clip/'strip.png';target.parent.mkdir(parents=True,exist_ok=True)
   with Image.open(source) as strip:strip.resize((strip.width//2,strip.height//2),Image.Resampling.LANCZOS).save(target)
 packer=module('runtime_packer_001',ROOT/'tools/pack-modular-sprites.py')
 result=packer.pack(definition,normalized,ROOT,deduplicate=True)
 print('PACKED_RUNTIME',result,flush=True);return result

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--masters',action='store_true');parser.add_argument('--character',action='append');parser.add_argument('--clip',action='append');parser.add_argument('--pack',action='store_true');parser.add_argument('--pack-existing',action='append',help='Pack already-baked complete character at the shared runtime scale');args=parser.parse_args()
 if args.masters:make_masters()
 if args.character:
  packer=module('packer_001',ROOT/'tools/pack-modular-sprites.py')
  for character in args.character:
   definition,normalized=bake(character,args.clip)
   if args.pack:pack_runtime(character)
 for character in args.pack_existing or []:pack_runtime(character)
