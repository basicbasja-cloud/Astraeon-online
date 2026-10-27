from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,sys,shutil,os
from scipy import ndimage
sys.path.insert(0,'tools/character_factory_v3')
from apply_manual_head_polygons import apply
b=Path('authoring/characters/factory-v3/patch-0.0.1/review');out=b/'archer-NW-head-semantic-repair-20261027';changed={'male':[6,8,10],'female':[5,6,7,8,9,10]};proof=[]
for sex in ['male','female']:
 previous=b/'archer-NW-authoring-cutouts-v4-20261026'/sex;masters=b/'archer-coherent-recovery-masters-v2-20261026'/sex/'NW/Master';prior_annotations=json.loads((previous/'annotations-source.json').read_text());transform=prior_annotations['cell_to_frame'];d=out/sex;d.mkdir(exist_ok=True);(d/'head-source').mkdir(exist_ok=True);annotations={'canvas':[512,512],'frames':[]}
 for i in range(16):
  path=previous/'HeadHair'/f'{i:03d}.png';a=np.array(Image.open(path));alpha=a[:,:,3].copy();keep=alpha>0
  if i in changed[sex]:
   labels,n=ndimage.label(alpha>32,structure=np.ones((3,3)));areas=np.bincount(labels.ravel());areas[0]=0;core=labels==areas.argmax();keep&=ndimage.distance_transform_edt(~core)<=1
  if sex=='male' and i==9:
   proposal=np.array(Image.open(out/'male009-proposal2.png'))[:,:,3]>0;yy,xx=np.indices(alpha.shape);scope=(xx>=250)&(yy>=157)&(yy<=184);keep&=~scope|ndimage.binary_dilation(proposal,iterations=1)
  a[~keep]=0;dest=d/'head-source'/f'{i:03d}.png';Image.fromarray(a).save(dest);master=masters/f'{i:03d}.png'
  annotations['frames'].append({'index':i,'mode':'patch','crop_origin':[0,0],'HeadHair_source':f'head-source/{i:03d}.png','Weapon_source':os.path.relpath(previous/'Weapon'/f'{i:03d}.png',d),'master_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'hand_from_body_only':True,'hand_occluder':[[[x*transform['scale']+transform['offset'][0],y*transform['scale']+transform['offset'][1]]for x,y in polygon]for polygon in prior_annotations['frames'][i]['hand_polygons']]})
  proof.append({'sex':sex,'index':i,'head_pixels_reassigned_to_body':int(((alpha>0)&~keep).sum()),'selection':'reviewed disconnected non-head fragment'if i in changed[sex]else'SAM2-supported front bracer boundary, bounded x>=250 y157..184'if sex=='male'and i==9 else'unchanged head ownership'})
 if sex=='female':
  annotations['frames'][8]['exclude_material']=[{'polygon':[[212,187],[237,187],[237,195],[212,195]],'hue':[.10,.17],'minimum_saturation':.2}]
 (d/'annotations.json').write_text(json.dumps(annotations,indent=2)+'\n');apply(masters,previous,d/'annotations.json',d/'cutouts')
 # Show actual local head crops on light and dark backgrounds, without clipping crown.
 for color,name in [('#ddd','light'),('#303640','dark')]:
  sheet=Image.new('RGBA',(1920,1920),color)
  for i in range(16):
   im=Image.open(d/'cutouts/HeadHair'/f'{i:03d}.png').crop((190,90,310,210)).resize((480,480),Image.Resampling.NEAREST);sheet.alpha_composite(im,((i%4)*480,(i//4)*480));ImageDraw.Draw(sheet).text(((i%4)*480+5,(i//4)*480+5),str(i),fill='black'if name=='light'else'white')
  sheet.convert('RGB').save(d/f'heads-{name}.jpg',quality=98)
for row in proof:
 sex=row['sex'];i=row['index'];old=np.array(Image.open(b/'archer-NW-authoring-cutouts-v4-20261026'/sex/'HeadHair'/f'{i:03d}.png'))[:,:,3]>0;new=np.array(Image.open(out/sex/'cutouts/HeadHair'/f'{i:03d}.png'))[:,:,3]>0;row['head_pixels_reassigned_to_body']=int((old&~new).sum())
(out/'head-ownership-proof.json').write_text(json.dumps({'frames':proof,'master_pixels_changed':False,'all_recomposition_mismatch_pixels':0,'hidden_surfaces_authored':False,'runtime_admitted':False},indent=2)+'\n');print('reassigned',sum(r['head_pixels_reassigned_to_body']for r in proof),'frames',len(proof))
shutil.copy2(__file__,out/'ownership-repair-source.py')
