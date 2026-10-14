"""New source-driven INTERNAL cutout rig, baked into body_outfit + full head.
Not a per-frame repair of whole-strip pixels. Widths calibrated once at rest;
longitudinal foreshortening comes from the source-camera joint vector.
"""
from pathlib import Path
import json,hashlib,math
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;ROOT=P.parents[2];OUT=P/'rig-render-6';OUT.mkdir(exist_ok=True)
source=json.loads((P/'source/source.json').read_text());display=json.loads((P/'guide-receipt.json').read_text())['bank_matrix']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def xy(i,k):
 x,y=source['frames'][i]['points'][k]['xy']['rear'];return np.array([display[0]*x+display[4],display[3]*y+display[5]])
# Reviewed attachment coordinates inside native asset crops. These are authored
# rig coordinates, NOT an image joint-detector's observations.
D={
 'torso':dict(pivot=[153,70],end=[154,260],chain=['neck','pelvis']),
 'cape':dict(pivot=[112,68],scale=.55,attach='neck'),
 'head':dict(pivot=[193,290],end=(np.array([193,290])+(xy(0,'head')-xy(0,'neck'))/.44).tolist(),width=.44,chain=['neck','head']),
 'left.upperarm':dict(pivot=[455,265],end=[410,715],chain=['left.shoulder','left.elbow'],width=.12,file='left-upperarm-repaired.png'),
 'left.forearm':dict(pivot=[173,49],end=[143,209],chain=['left.elbow','left.wrist'],width=.33),
 'left.hand':dict(pivot=[153,85],end=[135,154],chain=['left.wrist','left.palm'],width=.18),
 'right.upperarm':dict(pivot=[445,270],end=[510,700],chain=['right.shoulder','right.elbow'],width=.12,file='right-upperarm-repaired.png'),
 'right.forearm':dict(pivot=[138,41],end=[174,205],chain=['right.elbow','right.wrist'],width=.33),
 'right.hand':dict(pivot=[174,125],end=[155,175],chain=['right.wrist','right.palm'],width=.18),
 'left.thigh':dict(pivot=[172,53],end=[157,235],chain=['left.hip','left.knee'],width=.32),
 'left.shin':dict(pivot=[140,52],end=[145,255],chain=['left.knee','left.ankle'],width=.42),
 'left.foot':dict(pivot=[159,176],scale=.30,attach='left.ankle'),
 'right.thigh':dict(pivot=[155,55],end=[180,230],chain=['right.hip','right.knee'],width=.32),
 'right.shin':dict(pivot=[175,54],end=[149,254],chain=['right.knee','right.ankle'],width=.42),
 'right.foot':dict(pivot=[760,581],scale=.08,attach='right.ankle',file='right-boot-repair-raw.png'),
 'collar':dict(pivot=[130,136],scale=.28,attach='neck')}
textures={name:Image.open(P/(d.get('file') or 'parts/'+name+'.png')).convert('RGBA') for name,d in D.items()}
for name,d in D.items():
 d['file']=d.get('file') or 'parts/'+name+'.png';d['sha256']=sha(P/d['file'])
 if 'chain' in d and 'width' not in d:
  d['width']=float(np.linalg.norm(xy(0,d['chain'][1])-xy(0,d['chain'][0]))/np.linalg.norm(np.array(d['end'])-d['pivot']))

def matrix(i,name):
 d=D[name];p=np.array(d['pivot'],float)
 if 'chain' in d:
  a,b=[xy(i,k) for k in d['chain']];delta=np.array(d['end'])-p;l=np.linalg.norm(delta);u=delta/l;v=np.array([-u[1],u[0]]);w=b-a;length=np.linalg.norm(w);t=w/length;n=np.array([-t[1],t[0]]);m=np.outer(t,u)*(length/l)+np.outer(n,v)*d['width'];trans=a-m@p
 else:
  a=xy(i,d['attach']);angle=0
  if name in ['cape','head','collar']:
   rest=xy(0,'neck')-xy(0,'pelvis');cur=xy(i,'neck')-xy(i,'pelvis');angle=math.atan2(cur[1],cur[0])-math.atan2(rest[1],rest[0])
   if name=='head':angle*=.60
  c,s=math.cos(angle),math.sin(angle);m=d['scale']*np.array([[c,-s],[s,c]]);trans=a-m@p
 return np.array([[*m[0],trans[0]],[*m[1],trans[1]],[0,0,1.]])
rest=Image.open(P/'rig-render-3/full/00.png').convert('RGBA');a=np.array(rest.getchannel('A'));yy,xx=np.where(a>=128);global_scale=398/(int(yy.max())-int(yy.min()));global_matrix=np.array([[global_scale,0,192-global_scale*192],[0,global_scale,82-global_scale*int(yy.min())],[0,0,1.]])

# Final rest-only correction after changing authored shoe scale: neutral5H400/481floor.
calibration=Image.open(P/'rig-render-5/full/00.png').convert('RGBA');ca=np.array(calibration.getchannel('A'));cy,cx=np.where(ca>=128);rs=398/(int(cy.max())-int(cy.min()));residual=np.array([[rs,0,192-rs*192],[0,rs,82-rs*int(cy.min())],[0,0,1.]])
global_matrix=residual@global_matrix

def draw(im,M):
 inv=np.linalg.inv(M);return im.convert('RGBa').transform((384,512),Image.Transform.AFFINE,tuple(inv[:2].flatten()),Image.Resampling.BICUBIC).convert('RGBA')
# Art kit was produced in one native image job; far boot separately repaired.
# Keep complete coverage: thigh behind torso hem, shin receivers into shoe cuff.
order=['right.foot','right.thigh','right.shin','right.upperarm','right.forearm','right.hand','left.foot','left.thigh','left.shin','torso','cape','head','left.upperarm','left.forearm','left.hand']
frames=[]
for i in range(8):
 full=Image.new('RGBA',(384,512));body=Image.new('RGBA',full.size);head=Image.new('RGBA',full.size);front=Image.new('RGBA',full.size);records=[]
 for name in order:
  mat=global_matrix@matrix(i,name);layer=draw(textures[name],mat);full.alpha_composite(layer)
  (head if name=='head' else front if order.index(name)>order.index('head') else body).alpha_composite(layer)
  partfolder=OUT/'isolated'/name;partfolder.mkdir(parents=True,exist_ok=True);layer.save(partfolder/f'{i:02}.png')
  records.append(dict(name=name,matrix=mat[:2].tolist(),asset=D[name]['file'],asset_sha256=D[name]['sha256'],width_scale=D[name].get('width',D[name].get('scale'))))
 full=body.copy();full.alpha_composite(head);full.alpha_composite(front) # canonical runtime pass composition
 for name,im in [('full',full),('body_outfit_back',body),('head',head),('body_outfit_front',front)]:
  folder=OUT/name;folder.mkdir(exist_ok=True);im.save(folder/f'{i:02}.png')
 frames.append(dict(index=i,source_points={k:(global_matrix@np.array([*xy(i,k),1]))[:2].tolist() for k in source['frames'][i]['points']},parts=records))
# Same approved clocks, no interpolation or new invented holds.
for name,ds in [('source',[190,180,190,180,190,180,190,600]),('game',[100]*7+[600])]:
 ims=[]
 for i in range(8):
  bg=Image.new('RGBA',(384,512),(45,55,65,255));bg.alpha_composite(Image.open(OUT/f'full/{i:02}.png'));ims.append(bg.convert('RGB'))
 ims[0].save(OUT/f'review-{name}.gif',save_all=True,append_images=ims[1:],duration=ds,loop=0,disposal=2)
sheet=Image.new('RGBA',(1536,1024),(45,55,65,255))
for i in range(8):sheet.alpha_composite(Image.open(OUT/f'full/{i:02}.png'),(i%4*384,i//4*512))
sheet.convert('RGB').save(OUT/'review-sheet.png')
(OUT/'bindings.json').write_text(json.dumps(dict(source_sha256=sha(P/'source/source.json'),display_matrix=display,whole_bank_rest_matrix=global_matrix.tolist(),calibration_image_sha256=sha(P/'rig-render-5/full/00.png'),calibration_scope='One composed whole-bank rest-only matrix after source-rig authoring; no per-frame fits. Canonical full uses actual three runtime passes.',assets=D,draw_order=order,frames=frames,scope='Internal16part2Dskinning: fixed rest transverse widths, source-vector axial foreshortening, fixed foot transforms. This is not whole-frame fitting, 3D skinning or automatic anatomical recovery. Two logical slots; body_outfit has back/front draw passes around head. Exact pixel recomposition is required.',production_pass=False),indent=2)+'\n')
print('Painted source-driven rig exported')
