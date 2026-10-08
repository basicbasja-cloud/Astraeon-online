#!/usr/bin/env python3
"""Offline painted authoring: fixed master registration, semantic extraction, shared pose deformation.
Not a skeletal renderer. Source PNGs remain authoritative; runtime gets full-canvas 2D parts.
"""
import argparse,json,math,datetime
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from scipy import ndimage
from scipy.spatial import Delaunay
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'authoring/characters/swordsman-production'
DIRECTIONS=['S','SW','W','NW','N','NE','E','SE']
LAYERS=['BaseBody','Hair','Outfit','Weapon','Headgear','BackAccessory']

def poly(points):
    im=Image.new('L',(320,320));ImageDraw.Draw(im).polygon([tuple(p) for p in points],fill=255) if points else None
    return np.array(im)>0

def bone_distance(x,y,start,end):
    start=np.array(start,float);delta=np.array(end,float)-start
    along=np.clip(((x-start[0])*delta[0]+(y-start[1])*delta[1])/max(delta@delta,1e-8),0,1)
    return np.hypot(x-start[0]-along*delta[0],y-start[1]-along*delta[1])

def masked(image,mask):
    a=np.array(image).copy();a[:,:,3]=np.where(mask,a[:,:,3],0);a[a[:,:,3]==0,:3]=0
    return Image.fromarray(a)

def painted_skin(image,start,end,newStart,newEnd,r0,r1,surface='skin'):
    """Complete a neutral anatomical surface from its own painted skin texture.

    Occluded master legs do not supply closed anatomy. Fill the pose surface
    from nearest same-view skin samples, retaining painted light/color texture.
    This is offline source completion; no additional runtime limb slots exist.
    """
    a=np.array(image);y,x=np.mgrid[:320,:320]
    skin=(a[:,:,3]>50)&(a[:,:,0].astype(float)>a[:,:,1]*1.15)&(a[:,:,1].astype(float)>a[:,:,2]*1.12)
    if surface=='trouser':
        rgb=a[:,:,:3].astype(float)
        skin=(a[:,:,3]>50)&(rgb[:,:,0]>100)&(rgb[:,:,1]>90)&(rgb[:,:,0]<rgb[:,:,1]*1.38)&(rgb[:,:,2]>rgb[:,:,1]*.65)
    if not skin.any():raise ValueError('No painted neutral skin source')
    _,nearest=ndimage.distance_transform_edt(~skin,return_indices=True)
    texture=a[:,:,:3][nearest[0],nearest[1]]
    start,end,newStart,newEnd=map(lambda p:np.array(p,float),[start,end,newStart,newEnd]);v=newEnd-newStart;length=np.linalg.norm(v)
    # Foreshortened ankle/foot segments can project almost to a point. Keep
    # an orthonormal basis; a clamped denominator made oversized skin blobs.
    old=end-start;oldUnit=old/max(np.linalg.norm(old),1e-8)
    u=v/length if length>1e-6 else oldUnit
    along=((x-newStart[0])*u[0]+(y-newStart[1])*u[1]);t=np.clip(along/max(length,1e-8),0,1)
    perpendicular=(x-newStart[0])*(-u[1])+(y-newStart[1])*u[0]
    radius=r0+(r1-r0)*t;distance=np.hypot(perpendicular,np.maximum(0,np.maximum(-along,along-length)))
    sx=start[0]+old[0]*t-oldUnit[1]*perpendicular;sy=start[1]+old[1]*t+oldUnit[0]*perpendicular
    rgb=np.stack([ndimage.map_coordinates(texture[:,:,c].astype(float),[sy,sx],order=1,mode='nearest') for c in range(3)],axis=2)
    pixels=np.zeros((320,320,4),dtype='uint8');pixels[:,:,:3]=np.clip(rgb,0,255).astype('uint8');pixels[:,:,3]=np.clip((radius+.5-distance)*255,0,255).astype('uint8');pixels[pixels[:,:,3]==0,:3]=0
    return Image.fromarray(pixels)

def warp(image,source,target):
    """Forward-rasterized fixed source topology in premultiplied RGBA.

    Re-triangulating destination joints can invert source skin surfaces when
    projected knees/hands cross. Preserve the painted mesh topology instead.
    """
    source=np.asarray(source,float);target=np.asarray(target,float)
    triangles=Delaunay(source)
    a=np.array(image).astype(float)/255;a[:,:,:3]*=a[:,:,3:4]
    out=np.zeros((320,320,4))
    for indices in triangles.simplices:
        original=source[indices];posed=target[indices]
        x0,y0=np.maximum(0,np.floor(posed.min(axis=0))).astype(int);x1,y1=np.minimum(319,np.ceil(posed.max(axis=0))).astype(int)
        if x1<x0 or y1<y0:continue
        matrix=np.vstack((posed.T,np.ones(3)))
        if abs(np.linalg.det(matrix))<1e-7:continue
        yy,xx=np.mgrid[y0:y1+1,x0:x1+1];pixels=np.vstack((xx.ravel(),yy.ravel(),np.ones(xx.size)))
        bary=np.linalg.solve(matrix,pixels).T;inside=(bary>=-1e-7).all(axis=1)
        if not inside.any():continue
        coordinates=bary[inside]@original;colors=np.column_stack([ndimage.map_coordinates(a[:,:,channel],coordinates[:,::-1].T,order=1,mode='constant',cval=0) for channel in range(4)])
        ix=xx.ravel()[inside];iy=yy.ravel()[inside];old=out[iy,ix];out[iy,ix]=colors+old*(1-colors[:,3:4])
    out[:,:,:3]=np.divide(out[:,:,:3],out[:,:,3:4],out=np.zeros_like(out[:,:,:3]),where=out[:,:,3:4]>0)
    return Image.fromarray(np.clip(np.rint(out*255),0,255).astype('uint8'))

def extract():
    registration=json.loads((SOURCE/'male/pose-guides.json').read_text());guides=registration['guides']
    raw=Image.open(SOURCE/'candidates/body-01/generated-body.png')
    grounds=[(225,455),(615,465),(990,480),(1380,465),(220,943),(620,945),(1000,959),(1370,960)]
    sheet=Image.new('RGBA',(320*6,320*8))
    for row,d in enumerate(DIRECTIONS):
        master=Image.open(SOURCE/'masters'/f'{d}.png');a=np.array(master);g=guides[d];y,x=np.mgrid[:320,:320]
        # Hair is lavender/grey, face is warm. Restrict classification to measured head zone.
        hair=(y<g['hairBottom'])&(y<g['head'][1]+23)&(abs(x-g['head'][0])<35)&(a[:,:,2].astype(float)>a[:,:,1]*.96)&(a[:,:,2].astype(float)>a[:,:,0]*.79)&(a[:,:,3]>0)
        hair=ndimage.binary_fill_holes(hair)
        # Explicit sword silhouettes, excluding skin at the grip.
        weapon=poly(g['weaponPolygon'])&(a[:,:,3]>0)
        grip=np.array(g['hand_R']);blade=np.array(g['weapon_tip'])-grip
        along=((x-grip[0])*blade[0]+(y-grip[1])*blade[1])/(blade@blade)
        distance=abs((x-grip[0])*blade[1]-(y-grip[1])*blade[0])/np.linalg.norm(blade)
        weapon|=(along>.32)&(along<1.12)&(distance<8)&(a[:,:,3]>0)
        face=poly(g['facePolygon'])&~hair&(a[:,:,3]>0)
        skin=face.copy()
        visibleHands=['hand_R','hand_L'] if d in ['S','SW','W','SE','E'] else ['hand_R']
        for hand in visibleHands:
            hx,hy=g[hand];zone=(x-hx)**2+(y-hy)**2<6**2
            warm=(a[:,:,0].astype(float)>a[:,:,1]*1.18)&(a[:,:,1].astype(float)>a[:,:,2]*1.16)&(a[:,:,0]>110)&((a[:,:,0].astype(float)-a[:,:,2])<a[:,:,0]*.65)
            skin|=zone&warm&(a[:,:,3]>0)
        weapon&=~skin;outfit=(a[:,:,3]>0)&~hair&~weapon&~skin
        # Neutral construction texture: never use its generated face/scalp.
        cell=(row%4*384,row//4*512,(row%4+1)*384,(row//4+1)*512)
        bodySource=Image.new('RGBA',raw.size);bodySource.paste(raw.crop(cell),cell[:2]);rx,ry=grounds[row];scale=.4
        body=bodySource.transform((320,320),Image.Transform.AFFINE,(1/scale,0,rx-160/scale,0,1/scale,ry-264/scale),Image.Resampling.BICUBIC)
        neutral=registration['neutralSourceGuides'][d];names=[n for n in neutral if not (d=='E' and n in ['shoulder_L','elbow_L','hand_L'])];corners=[[0,0],[319,0],[319,319],[0,319]]
        if d=='E':
            # Side-view depth order crosses the two feet. A continuous mesh folds
            # at that crossing, so register the neutral painted legs separately
            # offline, far leg first, instead of distorting the torso.
            far=masked(body,(y>=193)&(x<143));near=masked(body,(y>=193)&(x>=136));torso=masked(body,y<203)
            old=np.array([130,238])-np.array([134,197]);new=np.array([159,253])-np.array([165,196]);length=np.linalg.norm(new)/np.linalg.norm(old)
            angle=math.atan2(new[1],new[0])-math.atan2(old[1],old[0]);c,s=math.cos(angle)/length,math.sin(angle)/length;px,py=134,197;nx,ny=165,196
            far=far.transform((320,320),Image.Transform.AFFINE,(c,s,px-c*nx-s*ny,-s,c,py+s*nx-c*ny),Image.Resampling.BICUBIC)
            near=near.transform((320,320),Image.Transform.AFFINE,(1,0,0,0,1,-2),Image.Resampling.BICUBIC)
            torso=torso.transform((320,320),Image.Transform.AFFINE,(1,0,-4,0,1,0),Image.Resampling.BICUBIC)
            body=Image.new('RGBA',(320,320));body.alpha_composite(far);body.alpha_composite(near);body.alpha_composite(torso)
        else:body=warp(body,corners+[neutral[n] for n in names],corners+[g[n] for n in names])
        # Keep neutral scalp underneath hair, and the exact source-painted exposed face.
        # Clear the generated facial features; they have no identity authority.
        faceBand=(y>g['head'][1]+9)&(y<g['neck'][1]+4)&(abs(x-g['head'][0])<27)
        interior=ndimage.binary_erosion((a[:,:,3]>235),iterations=2)
        blurred=body.filter(ImageFilter.GaussianBlur(4));pixels=np.array(body).copy();pixels[faceBand,:3]=np.array(blurred)[faceBand,:3];body=Image.fromarray(pixels)
        body=masked(body,interior)
        # Register underlying anatomy inside the approved clothing proportions.
        # The generated fists/calves are wider than the source glove/greave;
        # copying them through the cape silhouette creates stray skin surfaces.
        head=((x-g['head'][0])/23)**2+((y-g['head'][1])/25)**2<=1
        torso=poly([g[n] for n in ['shoulder_R','shoulder_L','hip_L','hip_R']])
        anatomy=head|torso
        for side in ['R','L']:
            anatomy|=bone_distance(x,y,g['shoulder_'+side],g['elbow_'+side])<=7
            anatomy|=bone_distance(x,y,g['elbow_'+side],g['hand_'+side])<=4.5
            anatomy|=bone_distance(x,y,g['hip_'+side],g['knee_'+side])<=6
            anatomy|=bone_distance(x,y,g['knee_'+side],g['foot_'+side])<=5
        body=masked(body,anatomy)
        closed=Image.new('RGBA',(320,320))
        clavicle=(np.array(g['shoulder_R'])+g['shoulder_L'])/2
        closed.alpha_composite(painted_skin(body,clavicle,np.array(g['head'])+[0,18],clavicle,np.array(g['head'])+[0,18],4,5))
        for side in ['R','L']:
            hip,knee,foot=[np.array(g[n+'_'+side]) for n in ['hip','knee','foot']];ankle=foot+[0,-12]
            closed.alpha_composite(painted_skin(body,hip,knee,hip,knee,4.5,4))
            closed.alpha_composite(painted_skin(body,knee,ankle,knee,ankle,3,2.5))
            closed.alpha_composite(painted_skin(body,ankle,foot+[0,-6],ankle,foot+[0,-6],2.5,3))
        closed.alpha_composite(body);body=closed
        body.alpha_composite(masked(master,skin))
        src,dst,sockets,_=pose('Idle',0,8,d,g)
        body=painted_body_motion(body,src,dst,g,sockets,d,'BaseBody')
        clothing=painted_body_motion(masked(master,outfit),src,dst,g,sockets,d,'Outfit')
        layers={'BaseBody':body,'Hair':masked(master,hair),'Outfit':clothing,'Weapon':masked(master,weapon),'Headgear':Image.new('RGBA',(320,320)),'BackAccessory':Image.new('RGBA',(320,320))}
        target=SOURCE/'male/modular-masters'/d;target.mkdir(parents=True,exist_ok=True)
        composite=Image.new('RGBA',(320,320))
        for col,layer in enumerate(LAYERS):
            layers[layer].save(target/f'{layer}.png');sheet.paste(layers[layer],(col*320,row*320));composite.alpha_composite(layers[layer])
        composite.save(target/'composite.png')
        # Compare visible modular result against authoritative master, not isolated layers.
        delta=np.abs(np.array(composite).astype(int)-a.astype(int));visible=a[:,:,3]>0
        print(d,'composite max/mean RGBA error',delta[visible].max(),round(float(delta[visible].mean()),4),'weapon alpha pixels',int((np.array(layers['Weapon'])[:,:,3]>0).sum()))
    sheet.save(SOURCE/'male/modular-layer-preview.png')
    bg=Image.new('RGBA',sheet.size,(31,48,60,255));bg.alpha_composite(sheet);bg.resize((1152,1536)).convert('RGB').save('/tmp/swordsman-modular-layers.jpg')

ORDER=['BackAccessory','BaseBody','Outfit','Hair','Weapon','Headgear']
PARTS={'BaseBody':'body-default','Hair':'hair-default','Outfit':'swordsman-default','Weapon':'sword-default','Headgear':'headgear-none','BackAccessory':'back-none'}
CLIPS=['Idle','Walk','Run','BasicAttack','SkillAction','Hit','Death','Guard','Dash']

def pose(animation,index,count,d,g):
    phase=index/count;wave=math.sin(phase*2*math.pi)
    names=['head','neck','waist','shoulder_R','elbow_R','hand_R','shoulder_L','elbow_L','hand_L','hip_R','knee_R','foot_R','hip_L','knee_L','foot_L']
    source=[g[n] for n in names];target={n:np.array(g[n],float) for n in names};ankles={}
    if animation=='Idle':
        for n in names:
            if not n.startswith(('foot','knee','hip')):target[n]+=[0,-.7*wave]
        for side,sign in [('R',-1),('L',1)]:target['shoulder_'+side]+=[sign*.45*wave,0]
    elif animation in ['Walk','Run']:
        # Consume the inspected, immutable articulated authoring cycle. The
        # earlier independent projected leg guide is deliberately removed.
        import importlib.util, hashlib
        rigPath=SOURCE/'rig-walk/candidate-03'
        gate=json.loads((rigPath/'rig-quality-report.json').read_text())
        if gate['status']!='INTERNAL_PASS':raise ValueError('Articulated rig visual gate has not passed')
        shared=json.loads((rigPath/'shared-cycle.json').read_text())
        rigSource=rigPath/'cycle-source.py'
        provenance=json.loads((rigPath/'provenance.json').read_text())
        if hashlib.sha256(rigSource.read_bytes()).hexdigest()!=provenance['rigSourceSHA256']:
            raise ValueError('Shared authoring cycle changed after inspection')
        if animation=='Run':rigSource=ROOT/'tools/swordsman-run-cycle.py'
        spec=importlib.util.spec_from_file_location('authoring_cycle',rigSource)
        motion=importlib.util.module_from_spec(spec);spec.loader.exec_module(motion)
        p=motion.pose(phase)
        # One anthropometric scale for the entire leg chain, all directions
        # and parts. Keep the locked painted head/torso proportions; a neutral
        # human proxy is not a new Swordsman design. Never fit individual frames.
        bodyScale=.70; pixels=320/2.65*bodyScale
        azimuth=-DIRECTIONS.index(d)*math.pi/4
        def project(v):
            x,y,z=np.asarray(v,float)
            return np.array([pixels*(-math.cos(azimuth)*x+math.sin(azimuth)*y),
                             pixels/math.sqrt(2)*(math.sin(azimuth)*x+math.cos(azimuth)*y-z)])
        neutralPelvis=np.array([0.,0.,1.035])
        pelvisShift=project(p['pelvis']-neutralPelvis)
        for n in names:
            if not n.startswith(('hip','knee','foot')):
                target[n]+=pelvisShift
                if animation=='Run':
                    commitment=np.clip((g['waist'][1]-g[n][1])/75,0,1)*.13
                    target[n]+=project([0,commitment,0])
        for side in ['R','L']:
            f=p['feet'][side]
            for n in ['hip','knee']:
                target[n+'_'+side]=np.array([160.,264.])+project(f[n])
            ankles[side]=np.array([160.,264.])+project(f['ankle'])
            target['foot_'+side]=np.array([160.,264.])+project(f['sole'])
            # Rigid sword carried with restrained arm counter-motion. Limb
            # guides and every rendered part derive from this same cycle.
            reference=motion.pose(.25)
            for n,bone,end in [('shoulder','upperarm',0),('elbow','upperarm',1),('hand','forearm',1)]:
                displacement=project(np.asarray(p['bones'][side+'-'+bone][end])-np.asarray(reference['bones'][side+'-'+bone][end]))
                target[n+'_'+side]+=displacement*(.55 if animation=='Walk' else 1.)
    corners=[[0,0],[319,0],[319,319],[0,319]]
    # Head support points preserve the painted face/hair as a rigid texture.
    support=[[g['head'][0]+dx,g['head'][1]+dy] for dx,dy in [(-30,-28),(30,-28),(-30,16),(30,16)]]
    headShift=target['head']-g['head'];targetSupport=[(np.array(p)+headShift).tolist() for p in support]
    src=corners+source+support;dst=corners+[target[n].tolist() for n in names]+targetSupport
    sockets={'root':[160,264],'head':target['head'].tolist(),'hand_R':target['hand_R'].tolist(),'hand_L':target['hand_L'].tolist(),'back':target['neck'].tolist(),'waist':target['waist'].tolist(),'foot_R':target['foot_R'].tolist(),'foot_L':target['foot_L'].tolist()}
    for side in ['R','L']:sockets['ankle_'+side]=ankles.get(side,target['foot_'+side]+[0,-12]).tolist()
    if animation in ['Walk','Run']:
        for side in ['R','L']:
            for key in ['heel','toe']:sockets[key+'_'+side]=(np.array([160.,264.])+project(p['feet'][side][key])).tolist()
    return src,dst,sockets,0

def rigid_weapon(image,pivot,newPivot,angle):
    radians=math.radians(angle);c,s=math.cos(radians),math.sin(radians);px,py=pivot;nx,ny=newPivot
    # Inverse transform around the anatomical hand, without changing dimensions.
    return image.transform((320,320),Image.Transform.AFFINE,(c,s,px-c*nx-s*ny,-s,c,py+s*nx-c*ny),Image.Resampling.BICUBIC)

def bone_patch(image,start,end,newStart,newEnd):
    """Pose a painted bone surface without a global triangulation field."""
    start,end,newStart,newEnd=map(lambda p:np.array(p,float),[start,end,newStart,newEnd])
    old=end-start;new=newEnd-newStart;oldLength=np.linalg.norm(old);newLength=max(np.linalg.norm(new),1)
    u=old/oldLength;v=new/newLength
    original=np.column_stack((u,[-u[1],u[0]]));posed=np.column_stack((v,[-v[1],v[0]]))
    matrix=original@np.diag([oldLength/newLength,1])@posed.T;offset=start-matrix@newStart
    return image.transform((320,320),Image.Transform.AFFINE,(matrix[0,0],matrix[0,1],offset[0],matrix[1,0],matrix[1,1],offset[1]),Image.Resampling.BICUBIC)

def smooth_painted_leg(image,hip,knee,ankle,newHip,newKnee,newAnkle,bootCut,bootAngle):
    """One continuous painted UV surface; no cut-and-rotated knee seams.

    Full-canvas output uses the inspected projected articulated chain. The
    source grid is fixed for each directional texture. Weight bands connect
    thigh/calf and upper boot; the sole remains wholly rigid to the ankle.
    This deformation happens offline and creates no runtime skeletal parts.
    """
    alpha=np.array(image)[:,:,3];yy,xx=np.where(alpha>0)
    if not len(xx):return Image.new('RGBA',(320,320))
    xs=list(range(max(0,int(xx.min())-2),min(319,int(xx.max())+2)+1,4))
    ys=list(range(max(0,int(yy.min())-2),min(319,int(yy.max())+2)+1,4))
    xs.append(min(319,int(xx.max())+2));ys.append(min(319,int(yy.max())+2))
    ys+=list(map(float,[knee[1]-5,knee[1],knee[1]+5,bootCut-4,bootCut+4,ankle[1]]))
    nodes=np.array([(x,y) for y in sorted(set(ys)) for x in sorted(set(xs))])
    def transformed(a,b,c,d):
        a,b,c,d=map(lambda p:np.array(p,float),[a,b,c,d])
        u=(b-a)/np.linalg.norm(b-a);v=(d-c)/np.linalg.norm(d-c)
        original=np.column_stack((u,[-u[1],u[0]]));posed=np.column_stack((v,[-v[1],v[0]]))
        matrix=posed@np.diag([np.linalg.norm(d-c)/np.linalg.norm(b-a),1])@original.T
        return (nodes-a)@matrix.T+c
    thigh=transformed(hip,knee,newHip,newKnee)
    calf=transformed(knee,ankle,newKnee,newAnkle)
    angle=math.radians(bootAngle);rotation=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
    boot=(nodes-np.array(ankle))@rotation.T+np.array(newAnkle)
    def weight(y,start,end):
        t=np.clip((y-start)/(end-start),0,1);return (t*t*(3-2*t))[:,None]
    shinWeight=weight(nodes[:,1],knee[1]-5,knee[1]+5)
    bootWeight=weight(nodes[:,1],bootCut-4,bootCut+4)
    target=(thigh*(1-shinWeight)+calf*shinWeight)*(1-bootWeight)+boot*bootWeight
    return warp(image,nodes,target)

def painted_body_motion(image,source,target,g,sockets,d,layer):
    """Offline depth-aware leg painting: logical runtime layer stays whole."""
    a=np.array(image);y,x=np.mgrid[:320,:320];cut={'S':220,'SW':216,'W':228,'NW':228,'N':231,'NE':230,'E':230,'SE':220}[d]
    originalNames=['head','neck','waist','shoulder_R','elbow_R','hand_R','shoulder_L','elbow_L','hand_L','hip_R','knee_R','foot_R','hip_L','knee_L','foot_L']
    if layer=='BaseBody':
        posed={name:np.array(target[4+originalNames.index(name)]) for name in originalNames}
        core=masked(image,poly([np.array(g['neck'])+[-10,0],g['shoulder_R'],g['hip_R'],g['hip_L'],g['shoulder_L'],np.array(g['neck'])+[10,0]]))
        hip=(np.array(g['hip_R'])+g['hip_L'])/2;newHip=(posed['hip_R']+posed['hip_L'])/2
        core=bone_patch(core,g['neck'],hip,posed['neck'],newHip)
        result=Image.new('RGBA',(320,320))
        for side in sorted(['R','L'],key=lambda s:sockets['foot_'+s][1]):
            oldHip,knee,foot=[np.array(g[n+'_'+side]) for n in ['hip','knee','foot']];ankle=foot+[0,-12];newFoot=posed['foot_'+side];newAnkle=np.array(sockets['ankle_'+side])
            for oldA,oldB,newA,newB,r0,r1 in [(oldHip,knee,posed['hip_'+side],posed['knee_'+side],4.5,4),(knee,ankle,posed['knee_'+side],newAnkle,3,2.5),(ankle,foot+[0,-6],newAnkle,newFoot+[0,-6],2.5,3)]:result.alpha_composite(painted_skin(image,oldA,oldB,newA,newB,r0,r1))
            for n1,n2,r0,r1 in [('shoulder','elbow',4,3),('elbow','hand',3,2.5)]:result.alpha_composite(painted_skin(image,g[n1+'_'+side],g[n2+'_'+side],posed[n1+'_'+side],posed[n2+'_'+side],r0,r1))
            hand=masked(image,(x-g['hand_'+side][0])**2+(y-g['hand_'+side][1])**2<3**2)
            result.alpha_composite(rigid_weapon(hand,g['hand_'+side],posed['hand_'+side],0))
        result.alpha_composite(core)
        clavicle=(np.array(g['shoulder_R'])+g['shoulder_L'])/2;newClavicle=(posed['shoulder_R']+posed['shoulder_L'])/2
        result.alpha_composite(painted_skin(image,clavicle,np.array(g['head'])+[0,18],newClavicle,posed['head']+[0,18],4,5))
        head=masked(image,y<g['neck'][1]-3);result.alpha_composite(rigid_weapon(head,g['head'],posed['head'],0));return result
    if layer=='BaseBody':cut=g['waist'][1]+14
    legZone=(y>=cut)&(a[:,:,3]>0)
    if layer=='Outfit':
        # A horizontal boot cut left the original standing trousers in the
        # torso. They hid the moving thigh and made every step look hinged.
        # Remove the visible ivory trouser surface as well, while preserving
        # the overlying dark/gold tunic panels and cape silhouette.
        rgb=a[:,:,:3].astype(float)
        trouser=(rgb[:,:,0]>100)&(rgb[:,:,1]>90)&(rgb[:,:,0]<rgb[:,:,1]*1.38)&(rgb[:,:,2]>rgb[:,:,1]*.65)
        thighZone=np.minimum(*[bone_distance(x,y,g['hip_'+side],g['knee_'+side]) for side in ['R','L']])<16
        legZone|=trouser&thighZone&(y>=min(g['hip_R'][1],g['hip_L'][1])-5)&(y<max(g['knee_R'][1],g['knee_L'][1])+3)&(a[:,:,3]>0)
    if layer=='BaseBody':
        armDist=np.minimum(*[bone_distance(x,y,g['elbow_'+side],g['hand_'+side]) for side in ['R','L']])
        legDist=np.minimum(*[bone_distance(x,y,g['hip_'+side],g['knee_'+side]) for side in ['R','L']])
        legZone&=armDist>legDist
    # Split by nearest source sole; this is authoring anatomy, not runtime parts.
    dr=(x-g['foot_R'][0])**2+(y-g['foot_R'][1])**2;dl=(x-g['foot_L'][0])**2+(y-g['foot_L'][1])**2
    masks={'R':legZone&(dr<=dl),'L':legZone&(dl<dr)}
    torso=masked(image,~legZone)
    # Remove the crossed foot nodes from the torso's interpolation field.
    bodyNames=['head','neck','waist','shoulder_R','elbow_R','hand_R','shoulder_L','elbow_L','hand_L','hip_R','hip_L']
    originalNames=['head','neck','waist','shoulder_R','elbow_R','hand_R','shoulder_L','elbow_L','hand_L','hip_R','knee_R','foot_R','hip_L','knee_L','foot_L']
    indices=[0,1,2,3]+[4+originalNames.index(n) for n in bodyNames]+list(range(len(source)-4,len(source)))
    torso=warp(torso,[source[i] for i in indices],[target[i] for i in indices]);legs={}
    if layer=='BaseBody':
        posed={name:np.array(target[4+originalNames.index(name)]) for name in originalNames}
        envelope=((x-posed['head'][0])/23)**2+((y-posed['head'][1])/25)**2<=1
        envelope|=poly([posed[n] for n in ['shoulder_R','shoulder_L','hip_L','hip_R']])
        for side in ['R','L']:
            envelope|=bone_distance(x,y,posed['shoulder_'+side],posed['elbow_'+side])<=6
            envelope|=bone_distance(x,y,posed['elbow_'+side],posed['hand_'+side])<=4.5
            envelope|=(x-posed['hand_'+side][0])**2+(y-posed['hand_'+side][1])**2<=5**2
        torso=masked(torso,envelope)
    for side in ['R','L']:
        piece=masked(image,masks[side]);other='L' if side=='R' else 'R'
        if layer=='BaseBody':
            hip=np.array(g['hip_'+side]);knee=np.array(g['knee_'+side]);foot=np.array(g['foot_'+side]);ankle=foot+[0,-12]
            newHip=np.array(target[4+originalNames.index('hip_'+side)]);newKnee=np.array(target[4+originalNames.index('knee_'+side)]);newFoot=np.array(sockets['foot_'+side]);newAnkle=np.array(sockets['ankle_'+side])
            piece=Image.new('RGBA',(320,320))
            for oldA,oldB,newA,newB,r0,r1 in [(hip,knee,newHip,newKnee,4.5,4),(knee,ankle,newKnee,newAnkle,3,2.5),(ankle,foot+[0,-6],newAnkle,newFoot+[0,-6],2.5,3)]:piece.alpha_composite(painted_skin(image,oldA,oldB,newA,newB,r0,r1))
            legs[side]=piece;continue
        if layer=='Outfit':
            # Complete same-direction leg painting restores surfaces occluded
            # by the master cape/other boot. Both legs use one shared pose guide.
            piece=Image.open(SOURCE/'male/leg-templates'/f'{d}.png')
        elif masks[side].sum()<masks[other].sum()*.32:
            # Occluded boot texture is completed from the same direction's
            # symmetric painted boot, without mirroring a direction or design.
            piece=masked(image,masks[other]);shift=np.array(g['foot_'+side])-g['foot_'+other]
            piece=piece.transform((320,320),Image.Transform.AFFINE,(1,0,-shift[0],0,1,-shift[1]),Image.Resampling.BICUBIC)
        foot=np.array(g['foot_'+side]);knee=np.array(g['knee_'+side]);newFoot=np.array(sockets['foot_'+side]);newKnee=np.array(target[4+originalNames.index('knee_'+side)])
        hip=np.array(g['hip_'+side]);newHip=np.array(target[4+originalNames.index('hip_'+side)])
        if layer=='Outfit':
            # The complete component has its own measured anatomical joints;
            # do not pretend its cuff and knee coincide with the master pose.
            component={
                'S':[[160,200],[160,225],[160,247],[160,260]],
                'SW':[[160,203],[158,229],[157,249],[157,260]],
                'W':[[160,207],[158,231],[159,249],[159,260]],
                'NW':[[160,202],[164,228],[166,249],[166,260]],
                'N':[[160,201],[160,228],[160,249],[160,260]],
                'NE':[[160,203],[161,229],[160,249],[160,260]],
                'E':[[160,207],[161,231],[160,249],[160,260]],
                'SE':[[160,200],[160,228],[160,248],[160,260]]
            }
            oldHip,oldKnee,oldAnkle,oldFoot=map(np.array,component[d])
            oldBootCut=float(oldAnkle[1]-1)
            # Registration metadata has always defined the sole at y=264.
            # The previous guessed y=260 produced a four-pixel sink. Distinguish
            # the upper boot paint boundary from the anatomical ankle joint.
            oldFoot=oldFoot.astype(float);oldFoot[1]=264.
            oldAnkle=oldFoot+[0.,-.085*(320/2.65*.70)/math.sqrt(2)]
            visible=np.array(piece)[:,:,3]>8
            connected,n=ndimage.label(visible)
            if n:
                sizes=np.bincount(connected.ravel());sizes[0]=0
                envelope=ndimage.binary_dilation(connected==sizes.argmax(),iterations=2)
                piece=masked(piece,envelope)
        else:oldHip=hip;oldKnee=knee;oldAnkle=foot+[0,-12];oldFoot=foot;oldBootCut=oldAnkle[1]-1
        newAnkle=np.array(sockets['ankle_'+side])
        boot=masked(piece,y>=oldBootCut)
        shin=masked(piece,(y>=oldKnee[1]-4)&(y<oldBootCut+2))
        # Knee armour belongs wholly to the calf painting; splitting its V
        # across two differently rotated patches produced doubled joints.
        thigh=masked(piece,y<oldKnee[1]-4)
        leg=Image.new('RGBA',(320,320))
        if layer=='Outfit':
            # Complete the cloth beneath overlapping tunic panels. A standing
            # component begins at a cuff; it cannot by itself fill the posed
            # crotch/upper-thigh surface exposed when the coat moves.
            posedWaist=np.array(target[4+originalNames.index('waist')])+[0,8]
            leg.alpha_composite(painted_skin(piece,oldHip,oldKnee,posedWaist,newHip,7,8,surface='trouser'))
            leg.alpha_composite(painted_skin(piece,oldHip,oldKnee,newHip,newKnee,8,5,surface='trouser'))
        bootAngle=math.degrees(math.atan2(newAnkle[1]-newFoot[1],newAnkle[0]-newFoot[0]))+90
        leg.alpha_composite(smooth_painted_leg(piece,oldHip,oldKnee,oldAnkle,newHip,newKnee,newAnkle,oldBootCut,bootAngle))
        legs[side]=leg
        if layer=='BaseBody':
            # Underlying bare foot fits inside footwear, rather than using the
            # full width of the master's oversized boot as anatomy.
            fx,fy=newFoot;footZone=y>fy-17
            footEnvelope=((x-fx)/3.5)**2+((y-(fy-10))/5.0)**2<=1
            envelope=(bone_distance(x,y,newHip,newKnee)<=4.5)|(bone_distance(x,y,newKnee,newAnkle)<=2.5)|footEnvelope
            legs[side]=masked(legs[side],envelope&(~footZone|footEnvelope))
    result=Image.new('RGBA',(320,320))
    for side in sorted(['R','L'],key=lambda side:sockets['foot_'+side][1]):result.alpha_composite(legs[side])
    result.alpha_composite(torso);return result

def produce(animation):
    if animation not in ['Idle','Walk','Run']:raise ValueError('Review established gates before adding subsequent motion strategies')
    if animation=='Run':
        walkGate=json.loads((SOURCE/'male/motion-candidates/Walk/candidate-28/visual-quality-report.json').read_text())
        if walkGate['status']!='INTERNAL_PASS':raise ValueError('Painted Walk must pass before Run production')
    count={'Idle':8,'Walk':16,'Run':12}[animation];durations=[{'Idle':225,'Walk':70,'Run':60}[animation]]*count
    p=SOURCE/'male';guides=json.loads((p/'pose-guides.json').read_text())['guides'];history=p/'motion-candidates'/animation;iteration=len(list(history.glob('candidate-*')))+1;output=history/f'candidate-{iteration:02d}';output.mkdir(parents=True,exist_ok=True)
    strips={layer:Image.new('RGBA',(320*count,320*8)) for layer in LAYERS};composites=[];directions={};film=Image.new('RGBA',(320*count,320*8))
    for row,d in enumerate(DIRECTIONS):
        g=guides[d];masters={layer:Image.open(p/'modular-masters'/d/f'{layer}.png') for layer in LAYERS};frames=[]
        for index in range(count):
            src,dst,sockets,angle=pose(animation,index,count,d,g);composite=Image.new('RGBA',(320,320));layers={}
            for layer in LAYERS:
                layers[layer]=rigid_weapon(masters[layer],g['hand_R'],sockets['hand_R'],angle) if layer=='Weapon' else painted_body_motion(masters[layer],src,dst,g,sockets,d,layer) if layer in ['BaseBody','Outfit'] else rigid_weapon(masters[layer],g['head'],sockets['head'],0) if layer=='Hair' else warp(masters[layer],src,dst) if layer not in ['Headgear','BackAccessory'] else masters[layer]
                strips[layer].paste(layers[layer],(320*index,320*row))
            for layer in ORDER:composite.alpha_composite(layers[layer])
            film.paste(composite,(320*index,320*row));frames.append({'frameIndex':index,'sockets':sockets})
        directions[d]={'frames':frames}
    for layer,strip in strips.items():
        target=p/'normalized/parts'/PARTS[layer]/animation;target.mkdir(parents=True,exist_ok=True);strip.save(target/'strip.png')
    film.save(output/'composite-strip.png')
    preview=[]
    for index in range(count):
        bg=Image.new('RGBA',(320*4,320*2),(31,48,60,255));dr=ImageDraw.Draw(bg)
        for row,d in enumerate(DIRECTIONS):
            x=row%4*320;y=row//4*320;bg.alpha_composite(film.crop((index*320,row*320,(index+1)*320,(row+1)*320)),(x,y));dr.text((x+10,y+15),d,fill='white');dr.line((x,y+264,x+320,y+264),fill=(54,74,82))
        preview.append(bg.convert('RGB'))
    for speed,name in [(1,'normal'),(.25,'quarter')]:preview[0].save(output/f'{name}.gif',save_all=True,append_images=preview[1:],duration=[round(v/speed) for v in durations],loop=0)
    record={'candidateId':f'male-{animation.lower()}-{iteration:02d}','dateTime':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'awaiting-visual-gate','method':'shared offline painted pose construction, one source warp per frame; rigid cosmetic sword; no runtime skeleton','sourceReferences':['../../../../masters','../../../modular-masters','../../../pose-guides.json'],'prompt':None,'negativePrompt':None,'purpose':animation+' whole-cycle construction for all eight directions and aligned layers','ownerApproval':'NOT_APPROVED','timingMs':durations}
    if animation=='Walk':
        record['method']='Inspected articulated 3D rig cycle projected into offline painted layers; rigid hair and sword, fixed full canvas; no runtime skeleton'
        record['sharedCycle']='authoring/characters/swordsman-production/rig-walk/candidate-03/shared-cycle.json'
        record['rigGate']='INTERNAL_PASS / NOT_OWNER_APPROVED'
        record['bodyCalibration']={'uniformLegChainScale':.70,'pixelsPerProxyMetre':320/2.65*.70,'cameraElevationDegrees':45,'root':[160,264],'upperBody':'Original painted identity retained; only shared-cycle displacement applied'}
        record['surfaceMethod']='One continuous weighted UV surface per painted leg; rigid soles; offline full-canvas baking'
        record['sampling']='16 frames over the same inspected eight-phase, 1.12-second cycle; no timing copied from RO'
    if animation=='Run':
        record['method']='Original articulated run cycle, shorter support with airborne transfer and stronger recovery; continuous painted UV legs and rigid sword; authoring-only rig'
        record['sharedCycle']='tools/swordsman-run-cycle.py'
        record['motionDifferences']=['42% support interval','15 cm swing clearance','airborne support transfer','loaded compression','forward torso commitment','stronger arm counter-motion']
        record['identity']='Same painted directional masters, leg-chain calibration, canvas, camera and cosmetic parts as Walk'
    (output/'provenance.json').write_text(json.dumps(record,indent=2)+'\n')
    # Pending clips explicitly use temporary Idle poses to exercise the existing complete definition contract.
    definitionPath=p/'definition.json'
    if definitionPath.exists():definition=json.loads(definitionPath.read_text())
    else:
        reference=json.loads((SOURCE/'reference/identity-lock.json').read_text())
        definition={'version':'0.1','characterId':'swordsman-male-candidate','classId':'Swordsman','bodyVariant':'male','directions':DIRECTIONS,'mirroring':'none','tags':['DEV_ONLY','PLACEHOLDER','NOT_FINAL_ART','PRODUCTION_CANDIDATE'],'source':{'status':'DEV_ONLY','reference':'authoring/characters/gait-rig-v50/approved-warrior-seed.png','approvedBy':None,'camera':'Elevated painted Warrior camera, approximately 45 degrees','handedness':'right','normalization':{'sourceFrameWidth':320,'sourceFrameHeight':320,'sourceRootAnchor':[160,264],'scale':1},'designLocks':['identity','silver swept hair','gold cape and bronze armour','anatomical right-hand sword','painted 2D','canonical elevated camera']},'canvas':{'frameWidth':320,'frameHeight':320,'rootAnchorX':160,'rootAnchorY':264,'referenceHeight':176},'slots':{n:n for n in LAYERS},'defaultParts':PARTS,'drawOrder':ORDER,'clips':{},'parts':{id:{'slot':layer,'cosmeticId':id,'frames':{}} for layer,id in PARTS.items()},'atlases':{}}
        for clip in CLIPS:
            definition['clips'][clip]={'loop':clip in ['Idle','Walk','Run','Guard'],'durations':durations,'directions':directions,'tags':['PENDING_PRODUCTION']}
            for layer in LAYERS:
                target=p/'normalized/parts'/PARTS[layer]/clip;target.mkdir(parents=True,exist_ok=True);strips[layer].save(target/'strip.png')
    definition['clips'][animation]={'loop':True,'durations':durations,'directions':directions,'tags':['AWAITING_VISUAL_GATE']}
    if animation=='Walk':definition['clips'][animation]['cycleDistance']=json.loads((SOURCE/'rig-walk/candidate-03/shared-cycle.json').read_text())['cycleDistance']*(320/2.65*.70)/(49.497/(70*(92/76)/176))
    if animation=='Run':
        import importlib.util
        spec=importlib.util.spec_from_file_location('run_distance',ROOT/'tools/swordsman-run-cycle.py');motion=importlib.util.module_from_spec(spec);spec.loader.exec_module(motion)
        definition['clips'][animation]['cycleDistance']=motion.CYCLE_DISTANCE*(320/2.65*.70)/(49.497/(70*(92/76)/176))
    definitionPath.write_text(json.dumps(definition,indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--extract',action='store_true');parser.add_argument('--animation',choices=CLIPS);args=parser.parse_args()
    if args.extract:extract()
    if args.animation:produce(args.animation)
