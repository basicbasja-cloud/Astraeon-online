"""Propose bounded white-matte edge repair on a single keyed Swordsman frame.

This intentionally limits changes to near-white pixels beside connected white.
It is not a semantically approved matte, motion or production asset.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_propagation,distance_transform_edt
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-pickup-sw08-single-20261029/generated.png'
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/review/swordsman-pickup-sw08-visible-cutout-v2-20261029'
ORDER=('BodyCostume','HeadHair','Weapon')
# Reviewed background points in enclosed gaps; sword highlights are excluded.
HOLE_SEEDS=((667,931),(505,905),(600,969),(592,981))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('Choose fresh output')
 rgb=np.array(Image.open(SOURCE).convert('RGB'))
 if rgb.shape!=(1254,1254,3):raise ValueError('Unexpected source canvas')
 minimum=rgb.min(axis=2);nearwhite=minimum>=250;seed=np.zeros(nearwhite.shape,bool);seed[0]=nearwhite[0];seed[-1]=nearwhite[-1];seed[:,0]|=nearwhite[:,0];seed[:,-1]|=nearwhite[:,-1]
 for x,y in HOLE_SEEDS:
  if not nearwhite[y,x]:raise ValueError('Expected white gap seed changed')
  seed[y,x]=True
 background=binary_propagation(seed,mask=nearwhite,structure=np.ones((3,3)));inside=~background;distance=distance_transform_edt(inside)
 stable=inside&(distance>=4)&(minimum<220)
 if not stable.any():raise ValueError('No stable foreground for edge estimation')
 index=distance_transform_edt(~stable,return_distances=False,return_indices=True);reference=rgb[index[0],index[1]].astype(np.float64)
 edge=inside&(distance<=3)&(minimum>=235);color=rgb.astype(np.float64);num=(255-color).max(axis=2);den=(255-reference).max(axis=2);alpha=np.ones(minimum.shape,dtype=np.float64);alpha[background]=0
 alpha[edge]=np.clip(num[edge]/np.maximum(den[edge],1),1/255,1)
 recovered=color.copy();a=alpha[edge,None];recovered[edge]=np.clip((color[edge]-255*(1-a))/a,0,255)
 rgba=np.dstack((np.rint(recovered).astype(np.uint8),np.rint(alpha*255).astype(np.uint8)));rgba[background]=0
 recomposite=np.rint(rgba[:,:,:3]*(rgba[:,:,3:4]/255.)+255*(1-rgba[:,:,3:4]/255.)).astype(np.uint8);delta=np.abs(recomposite.astype(np.int16)-rgb.astype(np.int16))
 tile=Image.fromarray(rgba,'RGBA').resize((384,384),Image.Resampling.LANCZOS);master=Image.new('RGBA',(768,768));master.alpha_composite(tile,(192,257));pixels=np.asarray(master);labels=np.array(Image.open(BASE/'labels.png'))
 unowned=(pixels[:,:,3]>0)&(labels==0)
 if unowned.any():
  distance,nearest=distance_transform_edt(labels==0,return_indices=True)
  if np.any(distance[unowned]>3):raise ValueError('Matte introduced distant unowned pixels')
  labels[unowned]=labels[nearest[0][unowned],nearest[1][unowned]]
 labels[pixels[:,:,3]==0]=0;layers={}
 for i,role in enumerate(ORDER,1):
  arr=np.zeros_like(pixels);arr[labels==i]=pixels[labels==i];layers[role]=Image.fromarray(arr,'RGBA')
 combined=Image.new('RGBA',(768,768))
 for role in ORDER:combined.alpha_composite(layers[role])
 if combined.tobytes()!=master.tobytes():raise ValueError('Same-frame composition changed')
 out.mkdir(parents=True);(out/'layers').mkdir();master.save(out/'master.png');Image.fromarray(labels,'L').save(out/'labels.png')
 for role,im in layers.items():im.save(out/'layers'/f'{role}.png')
 original=Image.open(BASE/'master.png').convert('RGBA');crop=(310,440,500,610);board=Image.new('RGB',(760,720),'#202020');draw=ImageDraw.Draw(board)
 for row,color in enumerate(['#808080','#202020']):
  for col,(title,im) in enumerate([('old keyed matte',original),('bounded edge proposal',master)]):
   bg=Image.new('RGBA',(190,170),color);bg.alpha_composite(im.crop(crop));board.paste(bg.convert('RGB').resize((380,340),Image.Resampling.NEAREST),(col*380,row*360+20));draw.text((col*380+3,row*360+3),title+' / '+color,fill='white' if row else 'black')
 board.save(out/'matte-comparison.png');proof={'status':'BOUNDED_UNMATTE_DRAFT_NOT_APPROVED','source_sha256':sha(SOURCE),'old_keyed_master_sha256':sha(BASE/'master.png'),'reviewed_white_gap_seeds_source_px':HOLE_SEEDS,'changed_source_edge_pixels':int(edge.sum()),'newly_assigned_resample_pixels':int(unowned.sum()),'white_recomposite_max_channel_difference':int(delta.max()),'white_recomposite_changed_pixels':int(np.any(delta!=0,axis=2).sum()),'keyed_master_exact_recomposition':True,'source_modified':False,'runtime_admitted':False,'limitations':['Only near-white edge pixels and explicitly seeded gaps were estimated; white foreground may be misclassified and other enclosed gaps may remain.','New resampling pixels inherit the nearest previous label and may belong to a different slot.','White recomposition cannot establish correct alpha on dark scenes.','Existing head/collar and sword/boot ownership is provisional.','One frame only; hidden surfaces, variants and temporal behavior are absent.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
