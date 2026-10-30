"""Bounded blade and preliminary hilt underpaint for NW003."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import propose_swordsman_nw008_blade_ownership as base
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-nw003-underpaint-20261030/raw.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 masterpath=base.SOURCE/'Master/003.png'
 with Image.open(masterpath) as im:master=im.convert('RGBA')
 with Image.open(RAW) as im:donor=im.convert('RGB').resize((170,170),Image.Resampling.LANCZOS)
 rgb=np.asarray(donor).astype(float);minimum=np.min(rgb,axis=2);alpha=np.where(minimum<220,255,np.clip((255-minimum)*255/35,0,255));color=np.clip((rgb-(255-alpha[:,:,None]))*255/np.maximum(alpha,1)[:,:,None],0,255);patch=np.dstack((np.rint(color).astype('uint8'),np.rint(alpha).astype('uint8')));patch[alpha<3]=0
 mask=Image.new('L',(512,512));drawmask=ImageDraw.Draw(mask);drawmask.polygon([(225,234),(303,180),(306,179),(308,180),(306,185),(231,240)],fill=255);drawmask.polygon([(216,228),(221,229),(228,235),(228,240),(225,243),(224,250),(220,250),(217,245),(215,242)],fill=255);drawmask.polygon([(195,253),(201,251),(205,253),(204,258),(198,260),(194,257)],fill=255);selected=np.asarray(mask)>0
 original=np.asarray(master);under=original.copy();canvas=np.zeros_like(original);canvas[130:300,180:350]=patch;under[selected]=canvas[selected]
 # A nonopaque original silhouette pixel has no known underlay; retain transparent background to avoid double alpha.
 under[selected & (original[:,:,3]<255)]=0
 blade=np.zeros_like(original);blade[selected]=original[selected]
 if np.any(under[~selected]!=original[~selected]):raise ValueError('changed outside mask')
 restored=Image.fromarray(under);restored.alpha_composite(Image.fromarray(blade));different=np.any(original!=np.asarray(restored),axis=2)
 if different.any():raise ValueError('RGBA reconstruction differs')
 out.mkdir(parents=True);Image.fromarray(under).save(out/'underpaint-no-blade.png');Image.fromarray(blade).save(out/'blade.png');mask.save(out/'blade-mask.png');restored.save(out/'recomposed.png')
 board=Image.new('RGB',(1200,800));draw=ImageDraw.Draw(board)
 for row,im in enumerate((master,Image.fromarray(under))):
  for col,color in enumerate(('white','#777777','#222222')):
   bg=Image.new('RGBA',(512,512),color);bg.alpha_composite(im);board.paste(bg.crop((180,130,350,300)).resize((400,400),Image.Resampling.LANCZOS).convert('RGB'),(400*col,400*row));draw.text((400*col+3,400*row+3),'preserved master' if row==0 else 'provisional underpaint, weapon hidden',fill='red')
 board.save(out/'comparison.png')
 receipt={'status':'EXACT_BLADE_AND_HILT_STUDY_NOT_APPROVED','master_sha256':sha(masterpath),'donor_sha256':sha(RAW),'script_sha256':sha(Path(__file__)),'mask_pixels':int(selected.sum()),'rgba_difference_pixels':int(different.sum()),'outside_mask_exact':True,'limitations':['Blade and hilt outlines contain garment/skin or glove edge pixels and are not clean semantic weapon cutouts.', 'Hilt polygon is approximate; gripping hand and pommel boundaries require detailed correction.', 'The donor and heuristic alpha need visual edge and anatomy review on all backgrounds.', 'This is one master, not BodyCostume/HeadHair/Weapon slots, animation, gameplay or a complete action.']}
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
