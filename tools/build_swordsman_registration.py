#!/usr/bin/env python3
"""Owner-authorized salvage: preserve dressed-body/face pixels, register attachments.

No generation, redrawing, rescaling of body strips, or RO image input. Original
atlases remain immutable. All corrections are baked into authored metadata.
"""
import copy,hashlib,json,math
from pathlib import Path
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw
from build_painted_swordsman import head_box
R=Path(__file__).resolve().parents[1]
OLD=R/'authoring/characters/appearance/swordsman-male-painted/appearance-pack.json'
OUT=R/'authoring/characters/appearance/swordsman-bodywithoutfit/appearance-pack.json'
BUILD=R/'authoring/characters/builds/swordsman-registration-v1'
AS=R/'assets/characters/swordsman-bodywithoutfit-v1'
REVIEW=R/'docs/review/character-bodywithoutfit-registration-v1'
D=['S','SW','W','NW','N','NE','E','SE']
def read(p):return json.loads(p.read_text())
def write(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tr(x=0,y=0,rotation=0,scale=1):return dict(x=round(float(x),5),y=round(float(y),5),rotation=round(float(rotation),7),scale=round(float(scale),7))
def relative(a,b):
 dx=(b['x']-a['x'])/a['scale'];dy=(b['y']-a['y'])/a['scale'];c=math.cos(a['rotation']);s=math.sin(a['rotation'])
 return tr(c*dx+s*dy,-s*dx+c*dy,b['rotation']-a['rotation'],b['scale']/a['scale'])
def trimref(ref,pivot,sourceSize,offset,**kw):return {**ref,'pivot':[round(float(x),4) for x in pivot],'trim':{'sourceSize':sourceSize,'offset':offset},**kw}
def build():
 AS.mkdir(parents=True,exist_ok=True);BUILD.mkdir(parents=True,exist_ok=True);REVIEW.mkdir(parents=True,exist_ok=True)
 old=read(OLD);motionfile=R/'authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json';t=read(motionfile)
 ims={k:Image.open(R/a['file']).convert('RGBA') for k,a in old['atlases'].items()}
 p=copy.deepcopy(old);p.update(schemaVersion='1.1',packId='swordsman-bodywithoutfit-registration-v1',status='REQUIRES_OWNER_VISUAL_REVIEW')
 p['source'].update(method='Owner-authorized pixel-preserving head extraction and dressed-body salvage; measured socket/pivot registration',baselineCommit='db2959b97a77b3f9b54c22d5e732fe2b2345a529')
 p['bodyContract']={'contractId':'swordsman-male-dressed-body-v1','model':'BodyWithOutfit+Head','registration':copy.deepcopy(t['registration']),'directions':D,'actions':list(t['actions']),'timeline':{a:{d:[f['durationMs'] for f in v['directions'][d]['frames']] for d in D} for a,v in t['actions'].items()},'sockets':['head','mainHand','offHand','back','waist','fxOrigin'],'presentationSelector':'costumeBodyId; independent of gameplay equipment','internalLayerEquivalent':{'BodyWithOutfit':'Body','Head':'HeadBase'}}
 p['slots'].pop('Body');p['slots']['BodyWithOutfit']={'layers':['Body'],'required':True};p['slots']['Head']={'layers':['HeadBase'],'required':True}
 p['defaultParts'].pop('Body');p['defaultParts'].update(BodyWithOutfit='swordsman-body-default',Head='swordsman-head')
 p['parts'].pop('body-swordsman')
 for id in ['swordsman-body-default','swordsman-body-royal-proof']:
  p['parts'][id]={'slot':'BodyWithOutfit','mode':'BODY_SYNC','space':'canvas','contractId':p['bodyContract']['contractId'],'timelines':{}}
 p['parts']['swordsman-body-royal-proof']['status']='DEV_ONLY';p['parts']['swordsman-body-royal-proof']['purpose']='Controlled navy/teal recolour of the complete dressed-body pixels; costume-swap proof only'
 p['parts']['swordsman-head']={'slot':'Head','mode':'BODY_SYNC','space':'attachment','anchor':'head','defaultRegistration':tr(),'timelines':{}}
 samples={};receipt=[];headrows={};bodyrows={};handrows={}
 atlas={}
 def saveatlas(id,rows,tile):
  im=Image.new('RGBA',(max(map(len,rows))*tile[0],len(rows)*tile[1]));refs=[]
  for y,row in enumerate(rows):
   refs.append([])
   for x,c in enumerate(row):im.alpha_composite(c,(x*tile[0],y*tile[1]));refs[-1].append({'atlasId':id,'rect':[x*tile[0],y*tile[1],*tile]})
  path=AS/(id+'.png');im.save(path);p['atlases'][id]={'file':path.relative_to(R).as_posix(),'width':im.width,'height':im.height};atlas[id]=sha(path);return refs
 # Exact complementary split: reassembling Head at its neck pivot recreates
 # every original RGBA pixel. No facial repaint or resized identity is allowed.
 for a,action in t['actions'].items():
  heads=[];bodies=[];royals=[];hands=[]
  for j,d in enumerate(D):
   hr=[];br=[];rr=[];gr=[]
   for i,f in enumerate(action['directions'][d]['frames']):
    ref=old['parts']['body-swordsman']['timelines'][a][d]['frames'][i]['layers']['Body'];x,y,w,h=ref['rect'];im=ims[ref['atlasId']].crop((x,y,x+w,y+h));arr=np.asarray(im).copy();hb=head_box(im)
    l=max(0,hb[0]-3);top=max(0,hb[1]-2);right=min(320,hb[2]+3);bottom=hb[3]+1
    mask=np.zeros((320,320),bool);mask[top:bottom,l:right]=True
    headarr=arr.copy();headarr[~mask]=0;bodyarr=arr.copy();bodyarr[mask]=0
    head=Image.fromarray(headarr);body=Image.fromarray(bodyarr);restored=Image.alpha_composite(body,head)
    assert np.array_equal(np.asarray(restored),arr),(a,d,i,'identity changed')
    neck=[(hb[0]+hb[2])/2,bottom-1];crop=head.crop((l,top,right,bottom));cell=Image.new('RGBA',(96,96));cx=(96-crop.width)//2;cy=(96-crop.height)//2;cell.alpha_composite(crop,(cx,cy))
    pivot=[cx+neck[0]-l,cy+neck[1]-top]
    # Skull measurements use only the upper half, excluding collar/neck/ears.
    skin=(arr[:,:,0]>130)&(arr[:,:,1]>85)&(arr[:,:,2]>55)&(arr[:,:,0]>arr[:,:,1]*1.035)&(arr[:,:,3]>200)
    upper=skin[max(0,hb[1]):hb[1]+max(8,(hb[3]-hb[1])//2),l:right];uy,ux=np.where(upper)
    skullx=float(np.median(ux)+l);skullw=int(ux.max()-ux.min()+1);skully=hb[1]+15
    topys,topxs=np.where(skin[hb[1]:hb[1]+10,l:right]);lowys,lowxs=np.where(skin[hb[1]+18:min(hb[3],hb[1]+30),l:right])
    tilt=math.atan2(float(np.median(topxs)-np.median(lowxs)),20) if len(topxs) and len(lowxs) else 0
    tilt=max(-.32,min(.32,tilt));hairscale=(skullw+6)/48
    sockets={'hair':tr(skullx-neck[0],skully-neck[1],tilt,hairscale),'headgear':tr(skullx-neck[0],skully+8-neck[1],tilt,hairscale)}
    # Glove prior is measured on original sources. Search the actual dark
    # glove, with explicit reviewed overrides for difficult occlusions below.
    yy,xx=np.mgrid[:320,:320];glove=(arr[:,:,0]>28)&(arr[:,:,0]<128)&(arr[:,:,1]>18)&(arr[:,:,1]<88)&(arr[:,:,2]>10)&(arr[:,:,2]<64)&(arr[:,:,0]>arr[:,:,1]*1.08)&(arr[:,:,3]>220)
    density=ndimage.uniform_filter(glove.astype(float),size=7)
    grips={}
    for name in ['mainHand','offHand']:
     prior=f['anchors'][name];dist=(xx-prior['x'])**2+(yy-prior['y'])**2
     radius=42 if a=='BasicAttack' and i<10 else 18
     score=density-dist/(5000 if a=='BasicAttack' and i<10 else 1100);score[dist>radius**2]=-100;score[arr[:,:,3]<220]=-100
     # Do not select the face or neck as a glove.
     score[top:bottom,l:right]=-100
     gy,gx=np.unravel_index(score.argmax(),score.shape);grips[name]=[int(gx),int(gy)]
    # Shoulder attachment follows measured neck and upper torso, not a head
    # centre offset. Directional cape registration is calibrated separately.
    back=[neck[0],neck[1]+9]
    samples[a,d,i]={'neck':neck,'hairSockets':sockets,'headRect':[l,top,right,bottom],'headPivot':pivot,'headCanvasOffset':[l-cx,top-cy],'mainHand':grips['mainHand'],'offHand':grips['offHand'],'back':back,'tilt':tilt,'headBox':hb}
    hr.append(cell);br.append(body)
    # Proof B changes all complete clothing/armour pixels, preserving gloves
    # and boots. It cannot alter the now-independent Head source.
    royal=bodyarr.copy();warm=(royal[:,:,0]>royal[:,:,2]*1.4)&(royal[:,:,1]>royal[:,:,2]*1.25)&(royal[:,:,0]>95)&(royal[:,:,3]>0)
    royal[:,:,0][warm]=(royal[:,:,0][warm]*.43).astype('uint8');royal[:,:,1][warm]=(royal[:,:,1][warm]*.88).astype('uint8');royal[:,:,2][warm]=np.minimum(255,royal[:,:,2][warm]*1.8+55).astype('uint8');rr.append(Image.fromarray(royal))
    receipt.append({'action':a,'direction':d,'frame':i,'sourceAtlas':ref['atlasId'],'sourceRect':ref['rect'],'sourceRGBA':hashlib.sha256(arr.tobytes()).hexdigest(),'headRect':[l,top,right,bottom],'headPivot':pivot,'losslessReassembly':True})
   heads.append(hr);bodies.append(br);royals.append(rr)
  hrefs=saveatlas('head-'+a.lower(),heads,(96,96));brefs=saveatlas('body-'+a.lower(),bodies,(320,320));rrefs=saveatlas('royal-'+a.lower(),royals,(320,320))
  p['parts']['swordsman-head']['timelines'][a]={};p['parts']['swordsman-body-default']['timelines'][a]={};p['parts']['swordsman-body-royal-proof']['timelines'][a]={}
  for j,d in enumerate(D):
   hf=[]
   for i,f in enumerate(action['directions'][d]['frames']):
    s=samples[a,d,i];target=tr(*s['neck']);registration=relative(f['anchors']['head'],target)
    hf.append({'layers':{'HeadBase':trimref(hrefs[j][i],s['headPivot'],[320,320],s['headCanvasOffset'],localTransform=registration,sockets=s['hairSockets'],pivotSemantic='neck/head-base',sourceExtraction=s['headRect'])}})
   p['parts']['swordsman-head']['timelines'][a][d]={'frames':hf}
   for id,refs in [('swordsman-body-default',brefs),('swordsman-body-royal-proof',rrefs)]:p['parts'][id]['timelines'][a][d]={'frames':[{'layers':{'Body':r}} for r in refs[j]]}
 # Hair images are retained byte-for-byte. Their transform inherits the actual
 # selected Head socket, with no independent body-space bob/quarter-cycle lag.
 for id in ['hair-a','hair-b']:
  part=p['parts'][id];part.update(mode='BODY_SYNC',parentLayer='HeadBase',anchor='hair',defaultRegistration=tr());part['timelines']={}
  for a,action in t['actions'].items():
   part['timelines'][a]={}
   for j,d in enumerate(D):
    oldref=old['parts'][id]['timelines']['*'][d]['phases'][0]['layers']['HairFront'];r=oldref['rect'];tile=ims[id].crop((r[0],r[1],r[0]+r[2],r[1]+r[3]));bb=tile.getbbox();pivot=[(bb[0]+bb[2])/2,bb[1]+18]
    ref=trimref({'atlasId':id,'rect':r},pivot,[80,80],[0,0],pivotSemantic='skull',localTransform=tr(0,-2))
    part['timelines'][a][d]={'frames':[{'layers':{'HairFront':copy.deepcopy(ref)}} for f in action['directions'][d]['frames']]}
 # Minimal directional phase perspectives reuse the same authored blade art.
 # Grip annotation is measured within the handle rather than .86 bbox height.
 overrides=read(BUILD/'socket-overrides.json') if (BUILD/'socket-overrides.json').exists() else {}
 for id in ['weapon-a','weapon-b','offhand','headgear','garment']:
  part=p['parts'][id];part['mode']='BODY_SYNC';part['timelines']={};part['defaultRegistration']=tr()
  if id=='headgear':part.update(parentLayer='HeadBase',anchor='headgear')
  for a,action in t['actions'].items():
   part['timelines'][a]={}
   for j,d in enumerate(D):
    frames=[]
    for i,f in enumerate(action['directions'][d]['frames']):
     s=samples[a,d,i];ov=overrides.get(a+'/'+d,{}).get(str(i),{})
     if id.startswith('weapon'):
      base=old['parts'][id]['timelines']['*'][d]['views'][0]['layers']['MainHand'];r=base['rect'];tile=ims[id].crop((r[0],r[1],r[0]+48,r[1]+128));bb=tile.getbbox()
      # Each original raster is annotated at its visible grip segment.
      pivot=[(bb[0]+bb[2])/2,bb[3]-16];layer='MainHand';point=ov.get('mainHand',s['mainHand']);rotation=f['anchors']['mainHand']['rotation']
      if 'weaponRotation' in ov:rotation=ov['weaponRotation']
      target=tr(*point,rotation);local=relative(f['anchors']['mainHand'],target);sourceSize=[48,128]
     elif id=='offhand':
      base=old['parts'][id]['timelines']['*'][d]['views'][0]['layers']['OffHand'];pivot=base['pivot'];layer='OffHand';point=ov.get('offHand',s['offHand']);local=relative(f['anchors']['offHand'],tr(*point));sourceSize=[80,80]
     elif id=='headgear':
      base=old['parts'][id]['timelines']['*'][d]['views'][0]['layers']['HeadgearTop'];pivot=base['pivot'];layer='HeadgearTop';local=tr();sourceSize=[80,80]
     else:
      base=old['parts'][id]['timelines']['*'][d]['phases'][0]['layers']['GarmentBack'];pivot=base['pivot'];layer='GarmentBack';sourceSize=[160,144]
      point=ov.get('back',s['back']);rotation=s['tilt']*.65
      # Rear cape collar is seated below the extracted jaw; front/profile
      # cloth is behind shoulders, with its neckline occluded by the body.
      target=tr(*point,rotation,.94);local=relative(f['anchors']['back'],target)
     ref=trimref({'atlasId':base['atlasId'],'rect':base['rect']},pivot,sourceSize,[0,0],localTransform=local,pivotSemantic={'MainHand':'grip','OffHand':'handle','HeadgearTop':'head-local','GarmentBack':'upper-back'}[layer])
     frames.append({'layers':{layer:ref}})
    part['timelines'][a][d]={'frames':frames}
 # Perspective masks are supplied by frame/direction profiles, not class logic.
 layers=list(t['drawProfiles']['front']);front=layers.copy();rear=layers.copy();rear.remove('GarmentBack');rear.insert(rear.index('Body')+1,'GarmentBack')
 p['drawProfiles']={'front':front,'rear':rear};p['frameDrawProfiles']={a:{d:['rear' if d in ['NW','N','NE'] else 'front']*len(v['directions'][d]['frames']) for d in D} for a,v in t['actions'].items()}
 # Remove unreferenced old body/reuse atlases; preserved outside this new pack.
 used={r['atlasId'] for part in p['parts'].values() for dirs in part['timelines'].values() for seq in dirs.values() for e in seq.get('frames',seq.get('views',seq.get('phases',[]))) for r in e['layers'].values()}
 p['atlases']={k:v for k,v in p['atlases'].items() if k in used}
 write(OUT,p);write(BUILD/'salvage-receipt.json',{'baselineAppearanceSHA256':sha(OLD),'motionTemplateSHA256':sha(motionfile),'sourceAtlases':{k:sha(R/v['file']) for k,v in old['atlases'].items()},'runtimeAtlases':{k:sha(R/v['file']) for k,v in p['atlases'].items()},'frameCount':len(receipt),'faceRedrawn':False,'bodyRescaled':False,'frames':receipt,'ownerVisualApproval':'PENDING'})
 write(BUILD/'measured-sockets.json',{'/'.join(map(str,k)):v for k,v in samples.items()})
 print('Saved strict BodyWithOutfit + independent Head pack; 328 lossless salvaged frames')
if __name__=='__main__':build()
