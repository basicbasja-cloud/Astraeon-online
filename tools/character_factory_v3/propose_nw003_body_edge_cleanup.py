"""Conservative, bounded bright edge cleanup proposal for one full-master frame."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research';SLOTS=P/'swordsman-nw003-three-slots-20261102';ALT=P/'swordsman-nw003-alt-head-swap-20261102/alternate-head.png';SOURCE=ROOT/'authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/basic-attack-simple/NW/Master/003.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('fresh output required')
 body=np.array(Image.open(SLOTS/'BodyCostume.png').convert('RGBA'));head=Image.open(SLOTS/'HeadHair.png').convert('RGBA');alt=Image.open(ALT).convert('RGBA');weapon=Image.open(SLOTS/'Weapon.png').convert('RGBA');master=np.asarray(Image.open(SOURCE).convert('RGBA'));yy,xx=np.indices(body.shape[:2]);mask=(body[:,:,3]>0)&(np.min(body[:,:,:3],axis=2)>230)&binary_dilation(body[:,:,3]==0,iterations=1)&(xx>=215)&(xx<285)&(yy>=150)&(yy<220);candidate=body.copy();candidate[mask]=0
 if np.any(candidate[~mask]!=body[~mask]):raise ValueError('changed outside bounded mask')
 def assemble(b,h):
  out=Image.fromarray(b);out.alpha_composite(h);out.alpha_composite(weapon);return out
 before=assemble(body,alt);after=assemble(candidate,alt);corrected=assemble(candidate,head);delta=np.any(np.asarray(corrected)!=master,axis=2)
 out.mkdir(parents=True);Image.fromarray(candidate).save(out/'BodyCostume.png');Image.fromarray((mask*255).astype('uint8')).save(out/'edge-mask.png');corrected.save(out/'corrected-master.png');after.save(out/'alternate-composite.png')
 board=Image.new('RGB',(1200,800));d=ImageDraw.Draw(board)
 for row,img in enumerate((before,after)):
  for col,c in enumerate(('white','#777','#222')):
   bg=Image.new('RGBA',(512,512),c);bg.alpha_composite(img);board.paste(bg.crop((215,155,285,225)).resize((400,400),Image.Resampling.NEAREST).convert('RGB'),(col*400,row*400));d.text((col*400+3,row*400+3),'before' if row==0 else 'edge proposal',fill='red')
 board.save(out/'comparison.png');proof={'status':'BOUNDED_BODY_EDGE_CLEANUP_NOT_APPROVED','body_sha256':sha(SLOTS/'BodyCostume.png'),'head_sha256':sha(SLOTS/'HeadHair.png'),'alternate_head_sha256':sha(ALT),'weapon_sha256':sha(SLOTS/'Weapon.png'),'source_sha256':sha(SOURCE),'script_sha256':sha(Path(__file__)),'selected_body_pixels':int(mask.sum()),'original_master_rgba_difference':int(delta.sum()),'outside_mask_exact':True,'limitations':['Bright threshold may erase a legitimate garment highlight or create hard edges; inspect at native scale.', 'It corrects only a bounded body region and cannot remove preexisting bright fringe elsewhere.', 'Head fit, neck underpainting, weapon semantics, animation and gameplay remain unapproved.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
