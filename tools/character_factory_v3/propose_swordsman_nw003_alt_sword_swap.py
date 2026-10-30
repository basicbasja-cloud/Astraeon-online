"""Single-frame alternate blade swap study; not a production cutout."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from scipy.ndimage import label
import propose_swordsman_nw008_blade_ownership as base
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-nw003-sword-variant-20261030/raw.png'
MASK=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research/swordsman-nw003-alt-sword-sam-20261030/mask-1.png'
POMMEL=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research/swordsman-nw003-alt-pommel-sam-20261030/mask-0.png'
UNDER=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research/swordsman-nw003-hilt-edge-20261030/underpaint-no-blade.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 with Image.open(RAW) as im:raw=im.convert('RGB')
 with Image.open(MASK) as im:m=np.asarray(im.convert('L'))>0
 if raw.size!=(1254,1254) or m.shape!=(1254,1254):raise ValueError('unexpected dimensions')
 labels,n=label(m,np.ones((3,3)));sizes=np.bincount(labels.ravel());sizes[0]=0;clean=labels==sizes.argmax();removed=int(m.sum()-clean.sum())
 with Image.open(POMMEL) as im:pommel=np.asarray(im.convert('L'))>0
 if pommel.shape!=m.shape:raise ValueError('unexpected pommel dimensions')
 plabels,pn=label(pommel,np.ones((3,3)));psizes=np.bincount(plabels.ravel());psizes[0]=0;part=plabels==psizes.argmax();removed+=int(pommel.sum()-part.sum());clean |= part
 # This is a review-only binary extraction; no claim of correct edge matting.
 alpha=Image.fromarray((clean*255).astype('uint8'),'L').filter(ImageFilter.GaussianBlur(.6));weapon=Image.new('RGBA',(512,512));local=Image.merge('RGBA',(*raw.split(),alpha)).resize((170,170),Image.Resampling.LANCZOS);weapon.paste(local,(180,130))
 with Image.open(base.SOURCE/'Master/003.png') as im:original=im.convert('RGBA')
 with Image.open(UNDER) as im:under=im.convert('RGBA')
 # Small same-frame glove occluder, explicitly provisional at guard boundary.
 stencil=Image.new('L',(512,512));ImageDraw.Draw(stencil).polygon([(199,245),(202,238),(209,233),(217,233),(220,239),(219,248),(214,253),(205,254)],fill=255)
 hand=Image.new('RGBA',(512,512));hand.paste(original,(0,0),stencil)
 merged=under.copy();merged.alpha_composite(weapon);merged.alpha_composite(hand)
 diff=np.any(np.asarray(merged)!=np.asarray(under),axis=2);union=(np.asarray(weapon)[:,:,3]>0)|(np.asarray(hand)[:,:,3]>0)
 if np.any(diff & ~union):raise ValueError('changed outside proposed swap union')
 out.mkdir(parents=True);weapon.save(out/'alternate-weapon.png');hand.save(out/'hand-occluder.png');merged.save(out/'alternate-composite.png');stencil.save(out/'hand-mask.png')
 board=Image.new('RGB',(1200,800));draw=ImageDraw.Draw(board)
 for row,im in enumerate((original,merged)):
  for col,color in enumerate(('white','#777777','#222222')):
   bg=Image.new('RGBA',(512,512),color);bg.alpha_composite(im);board.paste(bg.crop((180,130,350,300)).resize((400,400),Image.Resampling.LANCZOS).convert('RGB'),(400*col,400*row));draw.text((400*col+2,400*row+2),'original' if row==0 else 'alternate sword draft',fill='red')
 board.save(out/'comparison.png');proof={'status':'ALTERNATE_SWORD_SINGLE_FRAME_NOT_APPROVED','raw_sha256':sha(RAW),'mask_sha256':sha(MASK),'pommel_mask_sha256':sha(POMMEL),'underpaint_sha256':sha(UNDER),'source_sha256':sha(base.SOURCE/'Master/003.png'),'script_sha256':sha(Path(__file__)),'removed_disconnected_mask_pixels':removed,'changed_outside_swap_union':0,'limitations':['SAM mask has garment/arm pixels attached and binary edges; the hand polygon is approximate.', 'Underpaint includes ambiguous guard and white-matte artifacts; 2D source registration is unverified.', 'One frame only; no other direction, full sequence, complete variant package or runtime.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
