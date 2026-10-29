"""Propose single-frame visible cutouts from the saved SW08 paint study.

White-key and hand-drawn region ownership are provisional. This does not supply
hidden surfaces, a 35-frame action, semantic approval or runtime admission.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_propagation
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-pickup-sw08-single-20261029/generated.png'
# Native 1254x1254 source coordinates; conservative ownership proposals.
HEAD=[(754,666),(773,643),(800,626),(834,626),(863,640),(883,666),(891,690),(885,722),(868,746),(851,762),(828,765),(809,758),(789,749),(770,736),(758,716),(752,691)]
WEAPON=[[(631,982),(805,983),(815,995),(802,1008),(630,1007)],[(596,1017),(608,1034),(670,971),(662,957)]]
ORDER=('BodyCostume','HeadHair','Weapon')

def build(out):
 if out.exists() or out.is_symlink():raise ValueError('Choose a fresh output')
 raw=Image.open(SOURCE).convert('RGB')
 if raw.size!=(1254,1254):raise ValueError('Unexpected source canvas')
 rgb=np.asarray(raw);nearwhite=np.min(rgb,axis=2)>=250;seed=np.zeros(nearwhite.shape,bool);seed[0,:]=nearwhite[0,:];seed[-1,:]=nearwhite[-1,:];seed[:,0]|=nearwhite[:,0];seed[:,-1]|=nearwhite[:,-1]
 background=binary_propagation(seed,mask=nearwhite,structure=np.ones((3,3)))
 rgba=np.dstack((rgb,np.where(background,0,255).astype(np.uint8)));rgba[background]=0
 # Resample the full same-frame master once; no per-layer/per-limb fitting.
 tile=Image.fromarray(rgba,'RGBA').resize((384,384),Image.Resampling.LANCZOS)
 master=Image.new('RGBA',(768,768));master.alpha_composite(tile,(192,257))
 def polygon_mask(polys):
  im=Image.new('1',(1254,1254));draw=ImageDraw.Draw(im)
  for poly in polys:draw.polygon(poly,fill=1)
  tile=im.resize((384,384),Image.Resampling.NEAREST);mask=Image.new('1',(768,768));mask.paste(tile,(192,257));return np.asarray(mask,dtype=bool).copy()
 head=polygon_mask([HEAD]);weapon=polygon_mask(WEAPON)
 # A boot overlaps the blade near its tip. Return visibly brown boot pixels to
 # the body; this color heuristic is only a proposal and needs manual review.
 yy,xx=np.indices(rgb.shape[:2]);rr,gg,bb=[rgb[:,:,i].astype(np.int16) for i in range(3)]
 boot=(xx>700)&(xx<815)&(yy>=982)&(yy<=1008)&((rr-gg)>15)&((gg-bb)>10)&(rr<220)
 boot_tile=Image.fromarray(boot).resize((384,384),Image.Resampling.NEAREST);boot_mask=Image.new('1',(768,768));boot_mask.paste(boot_tile,(192,257));weapon &= ~np.asarray(boot_mask,dtype=bool)
 if np.any(head&weapon):raise ValueError('Proposed regions overlap')
 pixels=np.asarray(master).copy();visible=pixels[:,:,3]>0;labels=np.zeros((768,768),np.uint8);labels[visible]=1;labels[visible&head]=2;labels[visible&weapon]=3
 layers={}
 for label,role in enumerate(ORDER,1):
  a=np.zeros_like(pixels);a[labels==label]=pixels[labels==label];layers[role]=Image.fromarray(a,'RGBA')
 composed=Image.new('RGBA',(768,768))
 for role in ORDER:composed.alpha_composite(layers[role])
 if composed.tobytes()!=master.tobytes():raise ValueError('Visible recomposition changed')
 out.mkdir(parents=True);(out/'layers').mkdir();master.save(out/'master.png');Image.fromarray(labels,'L').save(out/'labels.png')
 for role,im in layers.items():im.save(out/'layers'/f'{role}.png')
 # Same shared crop and scale for all tiles; white/mid-gray/dark show halo defects.
 crop=(250,400,600,700);board=Image.new('RGB',(1050,930),'white');draw=ImageDraw.Draw(board)
 for row,color in enumerate(['white','#808080','#202020']):
  for col,(title,im) in enumerate([('Master',master),('HeadHair',layers['HeadHair']),('Body + Weapon',Image.alpha_composite(layers['BodyCostume'],layers['Weapon']))]):
   bg=Image.new('RGBA',(350,300),color);bg.alpha_composite(im.crop(crop));board.paste(bg.convert('RGB'),(350*col,310*row+30));draw.text((350*col+4,310*row+5),title+' / '+color,fill='black' if row<2 else 'white')
 board.save(out/'edge-review.png')
 proof={'status':'PROVISIONAL_SINGLE_FRAME_LABELS_NOT_APPROVED','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'input_size':[1254,1254],'canvas':[768,768],'shared_tile_resize':[384,384],'tile_offset':[192,257],'background_rule':'8-connected source pixels with all RGB >=250 from image boundary; remaining pixels opaque before resizing','manual_head_polygon_source_px':HEAD,'manual_weapon_polygons_source_px':WEAPON,'boot_color_return_source_pixels':int(boot.sum()),'visible_pixels_by_role':{r:int(np.sum(labels==i))for i,r in enumerate(ORDER,1)},'exact_same_frame_recomposition':True,'source_modified':False,'limitations':['White-key may remove highlights or leave halos; edge colors/alpha require visual correction.','Manual polygons and the boot-color heuristic may include incorrect skin, garment, hand or sword-edge ownership.','Hidden surfaces and hand-weapon occlusion are not authored; replacement is not validated.','The +17px tile registration is a proposal, not a confirmed contact anchor.','Only one frame and view; motion and gameplay unverified.']}
 (out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
