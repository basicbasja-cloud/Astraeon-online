"""Normalize reviewed generated limb candidates, preserving all pixels outside masks."""
import json,sys,copy
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.spatial import Delaunay
from scipy.ndimage import map_coordinates
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_attack_anatomy as prior
R=Path(__file__).resolve().parents[1];B=R/'authoring/characters/builds/swordsman-true8dir-v1';O=R/'assets/characters/swordsman-true8dir-v1';O.mkdir(exist_ok=True)
p=json.loads((R/'authoring/characters/appearance/swordsman-basicattack-anatomy/appearance-pack.json').read_text());spec=json.loads((B/'generated-arm-landmarks.json').read_text());j=json.loads((R/'authoring/characters/builds/swordsman-basicattack-anatomy-v1/joint-review.json').read_text());body=Image.open(R/p['atlases']['body-basicattack']['file']).convert('RGBA');head=Image.open(R/p['atlases']['head-basicattack']['file']).convert('RGBA');prior.SCALE=spec['scale'];receipts=[]
for d,chains in spec['directions'].items():
 row=p['bodyContract']['directions'].index(d);sheet=Image.open(B/f'{d}-generated.png').convert('RGBA')
 for i in range(6,16):
  keys=spec['frames'];lo=max(k for k in keys if k<=i);hi=min(k for k in keys if k>=i);blend=0 if lo==hi else (i-lo)/(hi-lo);source=lo if blend<.5 else hi;k=keys.index(source);chain=chains[k]
  raw=sheet.crop((k%3*512,k//3*512,k%3*512+512,k//3*512+512));arr=np.array(raw);arr[:,:,3][arr[:,:,3]>=250]=255;
  # Remove generated identity context before limb-only integration.
  purple=(arr[:,:,2]>arr[:,:,0]*.92)&(arr[:,:,2]>arr[:,:,1]*1.06)&(arr[:,:,3]>0)
  from scipy.ndimage import binary_dilation
  bounds=np.zeros((512,512),dtype=bool);bounds[60:(250 if k<3 else 210),140:330]=True;purple=binary_dilation(purple & bounds,iterations=2);arr[purple]=0;raw=Image.fromarray(arr)
  old=body.crop((i*320,row*320,(i+1)*320,(row+1)*320));ref=p['parts']['swordsman-head']['timelines']['BasicAttack'][d]['frames'][i]['layers']['HeadBase'];x,y,w,h=ref['rect'];mask=Image.new('L',(320,320));mask.paste(head.crop((x,y,x+w,y+h)).getchannel('A'),tuple(ref['trim']['offset']))
  oldchain=j['frames'][d][i]['joints'];ann=dict(generatedJoints=chain,shoulder=oldchain[0],originalJoints=oldchain,width=27,oldWidth=40 if d=='NW' else 30,generatedHeadPolygon=[])
  result,m,pts,shift=prior.replace_arm(old,raw,ann,mask)
  if i not in keys:
   # Explicit in-between deformation from reviewed key art, never an adjacent
   # direction fallback or a wholesale copied body frame.
   original=json.loads((R/'authoring/characters/builds/swordsman-basicattack-anatomy-v1/joint-review.json').read_text())['frames'][d]
   def keypoints(frame):
    ch=np.array(chains[keys.index(frame)],float);return (ch-ch[0])*spec['scale']+np.array(original[frame]['joints'][0])
   target=(1-blend)*keypoints(lo)+blend*keypoints(hi);src=np.array(pts)
   fixed=np.array([[0,0],[160,0],[319,0],[319,160],[319,319],[160,319],[0,319],[0,160]],float)
   dst=np.vstack([target,fixed]);sourcepts=np.vstack([src,fixed]);tri=Delaunay(dst);yy,xx=np.mgrid[0:320,0:320];grid=np.column_stack([xx.ravel(),yy.ravel()]);simplex=tri.find_simplex(grid);trans=tri.transform[simplex];bary=np.einsum('nij,nj->ni',trans[:,:2,:],grid-trans[:,2,:]);bary=np.column_stack([bary,1-bary.sum(axis=1)]);coords=np.einsum('ni,nij->nj',bary,sourcepts[tri.simplices[simplex]])
   sourcearr=np.array(result);warped=np.stack([map_coordinates(sourcearr[:,:,c],[coords[:,1],coords[:,0]],order=1,mode='constant').reshape(320,320) for c in range(4)],axis=-1).astype('uint8');result=Image.fromarray(warped)
   newmask=prior.arm_mask(target.tolist(),27);m=Image.fromarray(np.maximum(np.array(m),np.array(newmask)));pts=target.round(3).tolist()

  # Keep legs, pelvis and lower skirt untouched. Shoulder repair stays in upper body.
  ma=np.array(m);ma[218:]=0;m=Image.fromarray(ma);result=Image.composite(result,old,m)
  body.paste(result,(i*320,row*320));result.save(B/f'{d}-{i:02}-candidate.png');m.save(B/f'{d}-{i:02}-mask.png');j['frames'][d][i].update(joints=pts,reauthored=True,confidence='manually annotated generated limb, scale and shoulder registered')
  receipts.append(dict(direction=d,frame=i,joints=pts,source='generated-arm-landmarks.json',maskPixels=int(np.count_nonzero(ma))))
body.save(O/'body-basicattack.png');(B/'joint-review.json').write_text(json.dumps(j,indent=2));(B/'limb-receipt.json').write_text(json.dumps(receipts,indent=2))
board=Image.new('RGB',(6*320,4*350),'#243644');dr=ImageDraw.Draw(board)
for r,d in enumerate(spec['directions']):
 for c,i in enumerate(spec['frames']):
  im=Image.open(B/f'{d}-{i:02}-candidate.png');board.paste(im,(c*320,r*350+25),im);dr.text((c*320+5,r*350+5),f'{d} {i}',fill='white')
board.save(B/'limb-candidates.png')
