#!/usr/bin/env python3
"""Normalize coherent painted strips and independent components; never invent body poses.

One scale per strip; translation registers the support baseline. RO imagery is
only read by the separate acquisition tool and never by this asset compiler.
"""
import copy
import hashlib
import json
import math
import subprocess
from pathlib import Path
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
AP = ROOT/'authoring/characters/appearance'
BD = AP/'bodies/swordsman-male-default/generated'
MD = ROOT/'authoring/characters/motion-templates/ro1-swordsman-male'
BUILD = ROOT/'authoring/characters/builds/swordsman-male'
ASSETS = ROOT/'assets/characters/swordsman-ro1-painted-v1'
REVIEW = ROOT/'docs/review/character-ro1-animated-v1'
DIRECTIONS = ['S','SW','W','NW','N','NE','E','SE']
REG = dict(canvas=[320,320],root=dict(x=160,y=264,rotation=0,scale=1),referenceHeight=176,mirroring='none')
LAYERS = ['Shadow','GarmentBack','Body','HeadBase','HairBack','HairFront','HeadgearLower','HeadgearMiddle','HeadgearTop','MainHand','WeaponSlash','OffHand','GarmentFront','BackAccessory','CosmeticFX']

def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2)+'\n')

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def tr(x,y,rotation=0,scale=1): return dict(x=round(float(x),3),y=round(float(y),3),rotation=round(float(rotation),5),scale=round(float(scale),5))

def clean(im):
    a=np.array(im.convert('RGBA')).copy()
    a[:,:,3][a[:,:,3]<18]=0
    a[:,:,3][a[:,:,3]>240]=255
    # Remove isolated specks, including generated transparent-matte debris.
    labels,n=ndimage.label(a[:,:,3]>0)
    sizes=np.bincount(labels.ravel()); keep=sizes>=max(20,sizes.max()*.001)
    keep[0]=False; a[:,:,3][~keep[labels]]=0
    a[a[:,:,3]==0,:3]=0
    return Image.fromarray(a)

def grid(path,cols,rows,primary=False):
    im=Image.open(path).convert('RGBA');w,h=im.size
    cells=[clean(im.crop((round(i%cols*w/cols),round(i//cols*h/rows),round((i%cols+1)*w/cols),round((i//cols+1)*h/rows)))) for i in range(cols*rows)]
    if primary:
        for i,c in enumerate(cells):
            a=np.array(c);labels,n=ndimage.label(a[:,:,3]>0);sizes=np.bincount(labels.ravel());sizes[0]=0
            a[labels!=sizes.argmax()]=0;cells[i]=Image.fromarray(a)
    return cells

def head_box(im):
    a=np.array(im).astype(float);h,w=a.shape[:2]
    # Include the brightly lit scalp, not only the darker face/cheek. The old
    # red/green threshold discarded pale forehead pixels in leaning attacks.
    mask=(a[:,:,0]>130)&(a[:,:,1]>85)&(a[:,:,2]>55)&(a[:,:,0]>a[:,:,1]*1.035)&(a[:,:,1]>a[:,:,2]*1.02)&(a[:,:,2]>a[:,:,0]*.52)&(a[:,:,3]>200)
    # Leaning side/rear poses move the whole scalp away from cell center.
    # Clipping to a central band measured only half the head and broke hair
    # coverage and chunk scale. Gloves are darker than this skin threshold.
    mask[int(h*.55):]=False
    mask=ndimage.binary_closing(mask,iterations=2)
    labels,n=ndimage.label(mask);sizes=np.bincount(labels.ravel());sizes[0]=0
    if not n or sizes.max()<30: raise ValueError('Cannot locate painted bald head')
    yy,xx=np.where(labels==sizes.argmax())
    return (int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1))

def normalize(cells,action,direction,fixed_scale=None):
    # A crouch must not become larger: scale comes from the same ready/key pose.
    heights=[c.getbbox()[3]-head_box(c)[1] for c in cells]
    scale=fixed_scale or 170/(heights[0] if action=='BasicAttack' else np.median(heights))
    frames=[];anchors=[];transforms=[]
    for i,c in enumerate(cells):
        hb=head_box(c);bb=c.getbbox()
        resized=c.resize((round(c.width*scale),round(c.height*scale)),Image.Resampling.LANCZOS)
        # Shared support plane, rather than centering each bounding rectangle.
        dx=160-round((hb[0]+hb[2])/2*scale)
        dy=264-round(bb[3]*scale)
        canvas=Image.new('RGBA',(320,320));canvas.alpha_composite(resized,(dx,dy))
        head=tr((hb[0]+hb[2])/2*scale+dx,(hb[1]+hb[3])/2*scale+dy,0,((hb[2]-hb[0])*scale+8)/48)
        transforms.append(dict(scale=scale,translation=[dx,dy],sourceHeadBox=hb,sourceBounds=bb))
        frames.append(clean(canvas));anchors.append({'head':head})
    return frames,anchors,transforms

def idle_breath(base,index):
    # The RO source has one standing pose. Painted raster breathing is explicitly
    # ASTRAEON refinement. Feet remain untouched; no runtime puppet or bone rig.
    phase=index/8; amount=(1-math.cos(phase*math.tau))*.55
    a=np.asarray(base); h,w=a.shape[:2]; yy,xx=np.mgrid[:h,:w].astype(float)
    taper=np.clip((235-yy)/90,0,1)
    sy=yy+amount*taper
    # Bounded torso expansion, with no independent limb deformation.
    sx=160+(xx-160)/(1+.005*math.sin(phase*math.tau)**2*taper)
    out=np.empty_like(a)
    for k in range(4):out[:,:,k]=ndimage.map_coordinates(a[:,:,k],[sy,sx],order=1,mode='constant',cval=0)
    return clean(Image.fromarray(out))

def build():
    ASSETS.mkdir(parents=True,exist_ok=True);REVIEW.mkdir(parents=True,exist_ok=True)
    body_frames={}; anchor_data={}; normalization={}
    idle=grid(BD/'idle-raw.png',4,2,primary=True)
    for j,d in enumerate(DIRECTIONS):
        base,a,n=normalize([idle[j]],'Idle',d)
        body_frames['Idle',d]=[idle_breath(base[0],i) for i in range(9)]
        anchor_data['Idle',d]=[copy.deepcopy(a[0]) for i in range(9)]
        normalization['Idle/'+d]=n
        for action,file in [('Walk','walk'),('BasicAttack','attack')]:
            original=grid(BD/f'{file}-{d}-raw.png',4,4,primary=True)
            if action=='BasicAttack':
                # The renderer's key4 is still a loaded, raised sword arm.
                # The generator cut early in slot5. Retarget that landmark to
                # the coherent strip's loaded slot4, and use old slot5 as its
                # acceleration in-between. Never label an early cut RO key4.
                early_cut=original[5].copy();original[5]=original[4].copy();original[6]=early_cut
            f,a,n=normalize(original,action,d)
            if action=='BasicAttack':
                n[5]['paintedSourceFrame']=4;n[6]['paintedSourceFrame']=5
            if action=='BasicAttack' and (BD/f'recovery-{d}-raw.png').exists():
                chunk=grid(BD/f'recovery-{d}-raw.png',4,2,primary=True)
                # Convert the chunk's source-pixel units into the locked action
                # units once, using its two overlapping head-size landmarks.
                widths=lambda cells:[head_box(c)[2]-head_box(c)[0] for c in cells]
                ratio=float(np.median(widths(original[8:10]))/np.median(widths(chunk[:2])))
                cf,ca,cn=normalize(chunk,action,d,n[0]['scale']*ratio)
                f[10:]=cf[2:];a[10:]=ca[2:];n[10:]=cn[2:]
                for item in n[10:]:item['sourceChunk']='recovery-'+d+'-raw.png';item['lockedBoundaryFrames']=[8,9];item['chunkUnitConversion']=ratio
            body_frames[action,d]=f;anchor_data[action,d]=a;normalization[action+'/'+d]=n
    write(BUILD/'normalization.json',{'method':'one shared scale per strip; painted head center and support baseline registration; no per-frame scaling','sequences':normalization})

    # Hand grip annotations are authoring metadata, not ACT-extracted sockets.
    # Values measured on the normalized painted poses; repair overrides live in
    # attachment-calibration.json so anatomy and provenance remain reviewable.
    restR=[(-34,61),(-22,65),(-4,64),(27,61),(35,58),(20,62),(-10,64),(-26,58)]
    restL=[(34,62),(32,54),(21,51),(-23,49),(-35,58),(-27,60),(24,57),(23,48)]
    raised=[(-26,-13),(-22,-9),(-25,-3),(28,-12),(29,-13),(27,-5),(-28,-3),(-34,-9)]
    contact=[(0,69),(-15,63),(-13,61),(-23,59),(38,53),(43,47),(31,62),(12,74)]
    follow=[(33,58),(26,67),(19,65),(-48,52),(47,45),(50,40),(38,46),(27,62)]
    return_grip=[(-30,14),(-27,4),(-29,8),(28,-8),(29,-8),(28,-4),(-28,-3),(-33,-5)]
    rot_rest=[-2.63,-2.82,-3.03,2.87,2.57,2.35,2.8,-2.35]
    rot_attack=[2.65,2.72,2.85,2.96,2.7,2.65,2.6,2.62]
    calibration=json.loads((BUILD/'attachment-calibration.json').read_text()) if (BUILD/'attachment-calibration.json').exists() else {}
    source_calibration=json.loads((BUILD/'attachment-source-calibration.json').read_text()) if (BUILD/'attachment-source-calibration.json').exists() else {}
    for (action,d),frames in body_frames.items():
        j=DIRECTIONS.index(d)
        for i,f in enumerate(frames):
            h=anchor_data[action,d][i]['head'];hx,hy=h['x'],h['y']
            r=restR[j];l=restL[j];rotation=rot_rest[j]
            if action=='BasicAttack':
                milestones=[(0,raised[j]),(3,raised[j]),(5,(raised[j][0]*.7,raised[j][1]+15)),(7,contact[j]),(10,follow[j]),(12,return_grip[j]),(15,raised[j])]
                for (a,p),(b,q) in zip(milestones,milestones[1:]):
                    if a<=i<=b:
                        t=(i-a)/(b-a);r=(p[0]+(q[0]-p[0])*t,p[1]+(q[1]-p[1])*t);break
                # Shortest continuous clockwise sweep and readable recovery.
                angles=np.interp(i,[0,3,5,7,10,12,15],[rot_attack[j],rot_attack[j]-.4,1.0,-1.7,-2.4,-3.1,-3.63])
                rotation=float(angles)
                if i>=10:
                    # Actual finish remains across the torso, then settles into
                    # inspected Ready at waist. No invented overhead reset.
                    finish=follow[j];ready=restR[j]
                    fraction=max(0,min(1,(i-12)/3))
                    r=(finish[0]+(ready[0]-finish[0])*fraction,finish[1]+(ready[1]-finish[1])*fraction)
                    rotation=float(np.interp(i,[10,12,15],[-2.4,-2.6,[-.6,-.9,-1.15,-1.5,.6,.9,1.15,.3][j]]))
            anchors={'root':copy.deepcopy(REG['root']),'head':h,'mainHand':tr(hx+r[0],hy+r[1],rotation),
                     'offHand':tr(hx+l[0],hy+l[1]),'back':tr(hx,hy+28),'waist':tr(hx,hy+86),
                     'footL':tr(146,259),'footR':tr(174,259)}
            source_index=normalization[action+'/'+d][i].get('paintedSourceFrame',i) if action!='Idle' else i
            source_points=source_calibration.get(action+'/'+d,{}).get(str(source_index),{})
            norm=normalization[action+'/'+d][0 if action=='Idle' else i]
            for name,(sx,sy,rot,size) in source_points.items():
                anchors[name]=tr(sx*norm['scale']+norm['translation'][0],sy*norm['scale']+norm['translation'][1],rot,size)
            if action=='Idle':
                breath=(1-math.cos(i/8*math.tau))*.55
                for name in ['head','mainHand','offHand','back']: anchors[name]['y']=round(anchors[name]['y']-breath,3)
            if action in ['Idle','Walk'] or (action=='BasicAttack' and i>=10):
                # A small authored search window registers the grip to the
                # actual dark painted glove. It does not synthesize body motion.
                pixels=np.asarray(f).astype(float);yy,xx=np.mgrid[:320,:320]
                glove=(pixels[:,:,0]>50)&(pixels[:,:,0]<168)&(pixels[:,:,1]>30)&(pixels[:,:,1]<118)&(pixels[:,:,2]>18)&(pixels[:,:,2]<83)&(pixels[:,:,0]>pixels[:,:,1]*1.12)&(pixels[:,:,1]>pixels[:,:,2]*1.1)&(pixels[:,:,3]>220)
                density=ndimage.uniform_filter(glove.astype(float),size=7)
                for name in ['mainHand','offHand']:
                    p=anchors[name];px,py=p['x'],p['y']+(0 if action=='BasicAttack' else 8)
                    dist=(xx-px)**2+(yy-py)**2;score=density-dist/500
                    score[dist>18**2]=-100;score[pixels[:,:,3]<220]=-100
                    gy,gx=np.unravel_index(score.argmax(),score.shape)
                    anchors[name]['x']=int(gx);anchors[name]['y']=int(gy)
            overrides=calibration.get(action+'/'+d,{}).get(str(i),{})
            for name,value in overrides.items(): anchors[name]=tr(*value) if isinstance(value,list) else value
            # Sole guides are derived from the painted lower silhouette. Side
            # views can occlude one sole; keep the required finite guide when
            # two distinct components cannot be identified. No gameplay feet.
            pixels=np.asarray(f);yy,xx=np.mgrid[:320,:320]
            labels,n=ndimage.label((pixels[:,:,3]>200)&(yy>235))
            sizes=np.bincount(labels.ravel());sizes[0]=0
            ids=[k for k in np.argsort(sizes)[::-1][:2] if sizes[k]>12]
            soles=[]
            for k in ids:
                fy,fx=np.where(labels==k);soles.append(((float(fx.min())+float(fx.max()))/2,float(fy.max())))
            if len(soles)==2:
                soles.sort();left,right=soles
                if d in ['S','SW','W','SE']:left,right=right,left
                anchors['footL']=tr(*left);anchors['footR']=tr(*right)
            grip_rotation=anchors['mainHand']['rotation']
            anchors['weaponTip']=tr(anchors['mainHand']['x']+83*math.sin(grip_rotation),anchors['mainHand']['y']-83*math.cos(grip_rotation))
            anchors['fxOrigin']=copy.deepcopy(anchors['mainHand'])
            anchor_data[action,d][i]=anchors

    atlas_meta={};hashes={};parts={}
    def atlas(name,rows,tile):
        image=Image.new('RGBA',(max(map(len,rows))*tile[0],len(rows)*tile[1]));refs=[]
        for y,row in enumerate(rows):
            rr=[]
            for x,c in enumerate(row):
                assert c.size==tile
                image.alpha_composite(c,(x*tile[0],y*tile[1]));rr.append(dict(atlasId=name,rect=[x*tile[0],y*tile[1],*tile]))
            refs.append(rr)
        path=ASSETS/(name+'.png');image.save(path)
        atlas_meta[name]=dict(file=path.relative_to(ROOT).as_posix(),width=image.width,height=image.height);hashes[name]=digest(path)
        return refs
    timelines={}
    for action in ['Idle','Walk','BasicAttack']:
        refs=atlas('body-'+action.lower(),[body_frames[action,d] for d in DIRECTIONS],(320,320))
        timelines[action]={d:{'frames':[{'layers':{'Body':r}} for r in refs[i]]} for i,d in enumerate(DIRECTIONS)}
    parts['body-swordsman']={'slot':'Body','mode':'BODY_SYNC','space':'canvas','timelines':timelines}
    # Shadow is a non-character raster, not painted anatomy.
    shadow=Image.new('RGBA',(320,320));draw=ImageDraw.Draw(shadow);draw.ellipse((122,251,198,273),fill=(10,18,27,65));shadow=shadow.filter(ImageFilter.GaussianBlur(3))
    shrefs=atlas('shadow',[[shadow] for d in DIRECTIONS],(320,320))
    parts['shadow']={'slot':'Shadow','mode':'ANCHOR_HOLD','space':'canvas','timelines':{'*':{d:{'views':[{'at':0,'layers':{'Shadow':shrefs[i][0]}}]} for i,d in enumerate(DIRECTIONS)}}}

    def component(im,tile,size,pivot_fraction=(.5,.5)):
        crop=im.crop(im.getbbox());target=crop.resize(size,Image.Resampling.LANCZOS);out=Image.new('RGBA',tile)
        x=(tile[0]-size[0])//2;y=(tile[1]-size[1])//2;out.alpha_composite(target,(x,y))
        return clean(out),[x+size[0]*pivot_fraction[0],y+size[1]*pivot_fraction[1]]

    haircells=grid(AP/'hair/silver-tousled/generated/hair-A-B-raw.png',4,4,primary=True)
    for k,name in enumerate(['hair-a','hair-b']):
        rows=[];pivots=[]
        for j,d in enumerate(DIRECTIONS):
            c=haircells[k*8+j];bb=c.getbbox();ratio=(bb[3]-bb[1])/(bb[2]-bb[0]);width=48 if k==0 else 49
            tile,pivot=component(c,(80,80),(width,min(54,round(width*ratio))),(.5,.58));rows.append([tile]);pivots.append(pivot)
        refs=atlas(name,rows,(80,80))
        parts[name]={'slot':'Hair','mode':'PHASE_SYNC','space':'attachment','anchor':'head','timelines':{'*':{d:{'phases':[{'at':at,'layers':{'HairFront':{**refs[j][0],'pivot':pivots[j],'localTransform':tr(0,-3+dy,rot,1)}}} for at,dy,rot in [(0,0,0),(.25,-.35,.012),(.5,.1,0),(.75,.35,-.012)]]} for j,d in enumerate(DIRECTIONS)}}}

    # The generated weapons sheet returned6columns and4rows (24views); select
    # eight distinct authored views from each coherent12-view variant group.
    weapons=grid(AP/'weapons/swordsman-sword/generated/weapons-raw.png',6,4,primary=True)
    for k,name in enumerate(['weapon-a','weapon-b']):
        rows=[];pivots=[]
        for j,d in enumerate(DIRECTIONS):
            view=[0,1,2,3,6,10,9,11][j]
            c=weapons[k*12+view];bb=c.getbbox();ratio=(bb[2]-bb[0])/(bb[3]-bb[1]);height=101
            tile,pivot=component(c,(48,128),(max(7,round(height*ratio*.58)),height),(.5,.86));rows.append([tile]);pivots.append(pivot)
        refs=atlas(name,rows,(48,128))
        parts[name]={'slot':'MainHand','mode':'ANCHOR_HOLD','space':'attachment','anchor':'mainHand','timelines':{'*':{d:{'views':[{'at':0,'layers':{'MainHand':{**refs[j][0],'pivot':pivots[j]}}}]} for j,d in enumerate(DIRECTIONS)}}}
    gear=grid(AP/'offhand/shield-proof/generated/shield-headgear-raw.png',4,4,primary=True)
    for k,name,slot,layer,anchor in [(0,'offhand','OffHand','OffHand','offHand'),(1,'headgear','Headgear','HeadgearTop','head')]:
        rows=[];pivots=[]
        for j,d in enumerate(DIRECTIONS):
            c=gear[k*8+j];bb=c.getbbox();ratio=(bb[2]-bb[0])/(bb[3]-bb[1])
            size=(max(6,round(39*ratio)),39) if k==0 else (44,max(5,round(44/ratio)))
            tile,pivot=component(c,(80,80),size,(.5,.5 if k==0 else .5));rows.append([tile]);pivots.append(pivot)
        refs=atlas(name,rows,(80,80))
        parts[name]={'slot':slot,'mode':'ANCHOR_HOLD','space':'attachment','anchor':anchor,'timelines':{'*':{d:{'views':[{'at':0,'layers':{layer:{**refs[j][0],'pivot':pivots[j],'localTransform':tr(0,0 if k==0 else -2)}}}]} for j,d in enumerate(DIRECTIONS)}}}
    cape=grid(AP/'garments/swordsman-cape/generated/cape-raw.png',4,4,primary=True)
    rows=[];pivots=[]
    for j,d in enumerate(DIRECTIONS):
        row=[];pv=[]
        for k in range(2):
            c=cape[k*8+j];bb=c.getbbox();height=112; width=min(133,round(height*(bb[2]-bb[0])/(bb[3]-bb[1])))
            tile,pivot=component(c,(160,144),(width,height),(.5,.10));row.append(tile);pv.append(pivot)
        rows.append(row);pivots.append(pv)
    refs=atlas('cape',rows,(160,144))
    parts['garment']={'slot':'Garment','mode':'PHASE_SYNC','space':'attachment','anchor':'back','timelines':{'*':{d:{'phases':[{'at':at,'layers':{'GarmentBack':{**refs[j][k],'pivot':pivots[j][k],'localTransform':tr(0,-5,rot,1)}}} for at,k,rot in [(0,0,0),(.25,1,.012),(.5,0,0),(.75,1,-.012)]]} for j,d in enumerate(DIRECTIONS)}}}

    # Source-derived phase keys + explicit time-budgeted refinements.
    reference=json.loads((MD/'rendered-reference.json').read_text())
    records={(r['action'],r['direction']):r for r in reference['records']}
    profiles={'front':LAYERS.copy()}
    rear=LAYERS.copy();rear.remove('MainHand');rear.insert(rear.index('Body'),'MainHand');rear.remove('OffHand');rear.insert(rear.index('Body'),'OffHand');rear.remove('GarmentBack');rear.insert(rear.index('Body')+1,'GarmentBack');profiles['rear']=rear
    loaded=LAYERS.copy();loaded.remove('MainHand');loaded.insert(loaded.index('Body'),'MainHand');profiles['loaded']=loaded
    t={'schemaVersion':'1.0','motionTemplateId':'ro1-swordsman-male-v1','status':'REQUIRES_OWNER_VISUAL_REVIEW','directions':DIRECTIONS,'registration':REG,
       'transformConvention':'canvas pixels; clockwise radians; uniform positive scale','provenance':{'kind':'RO1_DERIVED','referenceManifestSHA256':digest(MD/'rendered-reference.json'),'evidenceClass':'RENDERED_REFERENCE','exactACTTiming':False,'rawACTInspected':False,'attachmentCoordinates':'ASTRAEON painted-pose calibration; not exact ACT offsets'},'drawProfiles':profiles,'defaultDrawProfile':'front','actions':{}}
    for action in ['Idle','Walk','BasicAttack']:
        dirs={}
        for j,d in enumerate(DIRECTIONS):
            if action=='Idle':key_indices=[0,8];durations=[2400,600];phases=['stand','standSettled'];src_action='idle';src_frames=[0,0]
            elif action=='Walk':key_indices=list(range(0,16,2));durations=[75]*8;phases=reference['phaseLabels']['walk'];src_action='walk';src_frames=list(range(8))
            else:key_indices=[0,1,2,3,5,7,9,10,12,15];durations=[20,20,20,20,90,50,30,30,90,80];phases=reference['phaseLabels']['attack']+['readyReturn'];src_action='attack';src_frames=list(range(9))+[0]
            keys=[]
            for ki,(index,duration,phase,sourceframe) in enumerate(zip(key_indices,durations,phases,src_frames)):
                r=records[('ready' if action=='BasicAttack' and ki==9 else src_action,d)]
                events=[]
                if action=='BasicAttack' and ki in [0,5,7]:events=[dict(name={0:'attackAnticipation',5:'attackContact',7:'attackRecovery'}[ki],authority='presentation')]
                frame={'id':f'{action}/{d}/key{ki}','durationMs':duration,'role':'referenceKey','evidenceClass':'RENDERED_REFERENCE','referencePhase':phase,'root':copy.deepcopy(REG['root']),'anchors':copy.deepcopy(anchor_data[action,d][index]),'events':events,
                       'source':{'kind':'RENDERED_REFERENCE','sourceImageSHA256':r['sha256'],'url':r['url'],'actionId':r['actionId'],'frameIndex':sourceframe,'direction':d,'confidence':'HIGH' if action!='BasicAttack' else 'MEDIUM','rawACTInspected':False},
                       'poseIntent':{'bodyOrientation':d+' elevated camera; independently painted','limbPhase':phase,'footContact':phase if action=='Walk' else 'support stance retained','attackPhase':phase if action=='BasicAttack' else 'none','silhouette':'RO rendered pose landmark retargeted to ASTRAEON outfit and anatomical right hand'}}
                if action=='BasicAttack' and ki<4:frame['drawProfile']='loaded'
                keys.append(frame)
            frames=[]
            for ki,key in enumerate(keys):
                index=key_indices[ki];end=key_indices[ki+1] if ki+1<len(keys) else len(body_frames[action,d])
                count=end-index;budget=key['durationMs'];offsets=[round(budget*n/count) for n in range(count+1)]
                frames.append({**copy.deepcopy(key),'durationMs':offsets[1]})
                for n in range(1,count):
                    right=keys[(ki+1)%len(keys)]
                    frames.append(dict(id=f'{action}/{d}/between{index+n}',durationMs=offsets[n+1]-offsets[n],role='astraeonInbetween',evidenceClass='ASTRAEON_INBETWEEN',referencePhase=None,between=[key['id'],right['id']],fraction=n/count,root=copy.deepcopy(REG['root']),anchors=anchor_data[action,d][index+n],events=[]))
            dirs[d]={'totalDurationMs':sum(durations),'referenceKeys':keys,'frames':frames,'drawProfile':'rear' if d in ['NW','N','NE'] else 'front'}
        t['actions'][action]={'loop':action!='BasicAttack','directions':dirs}
    write(MD/'motion-template.json',t)
    slots={'Body':dict(layers=['Body'],required=True),'Shadow':dict(layers=['Shadow'],required=False),'Hair':dict(layers=['HairFront'],required=False),'MainHand':dict(layers=['MainHand'],required=False),'OffHand':dict(layers=['OffHand'],required=False),'Headgear':dict(layers=['HeadgearTop'],required=False),'Garment':dict(layers=['GarmentBack'],required=False)}
    pack={'schemaVersion':'1.0','packId':'swordsman-ro1-painted-v1','status':'REQUIRES_OWNER_VISUAL_REVIEW','source':{'reference':'authoring/characters/gait-rig-v50/approved-warrior-seed.png','method':'coherent generated painted strips, independent components; owner approval required for new art'},'compatibleMotionTemplates':[t['motionTemplateId']],'registration':REG,'mirroring':'none','slots':slots,'defaultParts':{'Body':'body-swordsman','Shadow':'shadow','Hair':'hair-a','MainHand':'weapon-a','OffHand':None,'Headgear':None,'Garment':'garment'},'parts':parts,'atlases':atlas_meta}
    write(AP/'swordsman-male-painted/appearance-pack.json',pack)
    # A second deliberately non-production appearance uses this SAME rendered
    # MotionTemplate. Flat first-party silhouettes prove reuse without class
    # branches or treating a debug body as an approved catalogue character.
    dummy=copy.deepcopy(pack);dummy['packId']='ro1-reuse-dummy-v1';dummy['status']='DEV_ONLY';dummy['source']={'reference':'tools/build_painted_swordsman.py','purpose':'Reusable-motion calibration; flat blue first-party alpha silhouettes, never production'}
    dummy_timelines={}
    for action in t['actions']:
        rows=[]
        for d in DIRECTIONS:
            row=[]
            for body in body_frames[action,d]:
                cell=Image.new('RGBA',(320,320),(61,140,226,0));cell.putalpha(body.getchannel('A'));row.append(cell)
            rows.append(row)
        refs=atlas('reuse-body-'+action.lower(),rows,(320,320))
        dummy_timelines[action]={d:{'frames':[{'layers':{'Body':r}} for r in refs[j]]} for j,d in enumerate(DIRECTIONS)}
    dummy['parts']['body-debug']={'slot':'Body','mode':'BODY_SYNC','space':'canvas','timelines':dummy_timelines};del dummy['parts']['body-swordsman']
    dummy['defaultParts'].update(Body='body-debug',Hair='hair-b',MainHand='weapon-b');dummy['atlases']=copy.deepcopy(atlas_meta)
    write(AP/'ro1-reuse-dummy/appearance-pack.json',dummy)
    write(BUILD/'build-manifest.json',{'status':'ANIMATED_ART_PROOF_CREATED','ownerVisualApproval':'PENDING','motionTemplate':str((MD/'motion-template.json').relative_to(ROOT)),'appearancePack':'authoring/characters/appearance/swordsman-male-painted/appearance-pack.json','registration':REG,'runtimeAtlases':hashes,'actions':{a:{'framesPerDirection':len(t['actions'][a]['directions']['S']['frames']),'durationMs':t['actions'][a]['directions']['S']['totalDurationMs'],'referenceKeys':len(t['actions'][a]['directions']['S']['referenceKeys']),'inbetweens':len(t['actions'][a]['directions']['S']['frames'])-len(t['actions'][a]['directions']['S']['referenceKeys'])} for a in t['actions']},'rawROPixelsInProduction':False})
    # Painted-body-only sheets with numerical hand attachment overlays for QA.
    for action in t['actions']:
        sheet=Image.new('RGB',(320*4,350*8),'#263547');draw=ImageDraw.Draw(sheet)
        for j,d in enumerate(DIRECTIONS):
            for col,index in enumerate([0,3,7,12] if action!='Idle' else [0,2,4,6]):
                im=body_frames[action,d][index];x=col*320;y=j*350;sheet.paste(im,(x,y),im)
                a=anchor_data[action,d][index]
                for name,color in [('head','#d19df3'),('mainHand','#ff788a'),('offHand','#f9de81')]:
                    p=a[name];px=x+p['x'];py=y+p['y'];draw.line((px-5,py,px+5,py),fill=color,width=2);draw.line((px,py-5,px,py+5),fill=color,width=2)
                draw.text((x+8,y+305),f'{action} {d} frame {index}',fill='white')
        sheet.save(REVIEW/(action.lower()+'-attachment-calibration.png'))
    subprocess.run(['node','-e',"const fs=require('fs'),m=require('./character-motion-template.js'),a=require('./character-assembly.js');const t=JSON.parse(fs.readFileSync('authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json')); const p=JSON.parse(fs.readFileSync('authoring/characters/appearance/swordsman-male-painted/appearance-pack.json')); a.compileAssembly(t,p); console.log('Painted motion and appearance validate');"],cwd=ROOT,check=True)
    print('Baked painted raster body, independent hair/sword/shield/circlet/cape; no raw RO imagery consumed')

if __name__=='__main__': build()
