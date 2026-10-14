"""Authored 2D diagnostic deformation, NOT final sprites or a 3D retarget."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import map_coordinates
P=Path(__file__).resolve().parent
im=Image.open(P/'neutral-canonical.png').convert('RGBA')
s=300/(470-81);tx=192-160*s;ty=480-470*s
base=im.transform((384,512),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),Image.Resampling.BICUBIC)
base.save(P/'neutral-guide.png');arr=np.asarray(base).astype(float)/255
arr[:,:,:3]*=arr[:,:,3:4]
source=json.loads((P/'source/source.json').read_text());rest=source['frames'][0]['points']
# Manually authored visible positions. Hips under clothing are authoring guesses,
# not measurements or labels of painted hidden anatomy.
landmarks={'head':[160,81],'chest':[166,178],'pelvis':[166,279],
'left.shoulder':[113,135],'left.elbow':[88,190],'left.wrist':[62,229],
'right.shoulder':[236,138],'right.elbow':[274,195],'right.wrist':[296,241],
'left.hip':[130,283],'left.knee':[136,335],'left.ankle':[145,430],'left.toe':[104,454],
'right.hip':[205,284],'right.knee':[219,335],'right.ankle':[227,411],'right.toe':[207,436]}
atlas=Image.new('RGBA',(1536,1024));records=[];yy,xx=np.mgrid[:512,:384];grid=np.stack([xx,yy],axis=-1).reshape(-1,2)
for i,f in enumerate(source['frames']):
    start=[];end=[]
    for name,p in landmarks.items():
        if name.startswith('right.') and name.endswith(('.shoulder','.elbow','.wrist')):continue
        a=np.array(p)*s+[tx,ty];delta=(np.array(f['points'][name]['xy'])-rest[name]['xy'])*1.65
        if name.endswith(('.ankle','.toe')):delta*=0
        start.append(a);end.append(a+delta)
    # Same neck translation at both collar ends; cloth/cape follows core motion.
    for p,name in [([140,80],'head'),([181,80],'head'),([323,335],'pelvis'),([259,256],'chest'),([238,140],'chest')]:
        a=np.array(p)*s+[tx,ty];delta=(np.array(f['points'][name]['xy'])-rest[name]['xy'])*1.65
        start.append(a);end.append(a+delta)
    # Dense support guides preserve full boot areas. They condition a redraw;
    # they are never copied into or substituted for generated final shoes.
    for y in [434,450,470,490]:
        for x in [100,125,150,175,200,225,250]:start.append(np.array([x,y]));end.append(np.array([x,y]))
    for p in [[0,0],[383,0],[0,511],[383,511]]:start.append(np.array(p));end.append(np.array(p))
    start=np.array(start);end=np.array(end)
    uv=RBFInterpolator(end,start-end,kernel='thin_plate_spline',smoothing=0)(grid)+grid
    channels=[map_coordinates(arr[:,:,k],[uv[:,1],uv[:,0]],order=1,mode='constant',cval=0).reshape(512,384) for k in range(4)]
    out=np.stack(channels,-1);out[:,:,:3]=np.divide(out[:,:,:3],out[:,:,3:4],out=np.zeros_like(out[:,:,:3]),where=out[:,:,3:4]>0)
    result=Image.fromarray(np.uint8(np.clip(out,0,1)*255+.5));atlas.paste(result,(i%4*384,i//4*512))
    records.append(dict(index=i,source_time_seconds=f['source_time_seconds'],guide_neck_xy=end[0].tolist(),authored_control_from=start.tolist(),authored_control_to=end.tolist()))
atlas.save(P/'painted-pose-guide.png')
(P/'guide-authoring.json').write_text(json.dumps(dict(scope='Warped neutral picture for image-generation conditioning ONLY. Not final art, measured hidden anatomy, physics or unchanged 3D retarget. Far arm is omitted from the cloth warp to avoid dragging the occluding cape with an independently moving hidden limb; use the separate source skeleton for its true projected motion.',neutral_static_matrix=[s,0,0,s,tx,ty],source_projected_displacement_multiplier=1.65,manual_authoring_landmarks_native=landmarks,records=records),indent=2)+'\n')
