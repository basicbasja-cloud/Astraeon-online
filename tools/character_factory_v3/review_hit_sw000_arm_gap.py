"""Inspect alpha loss against guide and a generated underpaint, not acceptance."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'authoring/characters/factory-v3/patch-0.0.1';C=P/'painted-candidates/swordsman-hit-sw000-arm-gap-20261102';A=P/'research/swordsman-hit-sw000-transparent-mask-patch-20261102';S=P/'painted-candidates/swordsman-hit-sw000-transparent-20261102'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('fresh output required')
 mask=np.asarray(Image.open(A/'removed-opaque-mask.png').convert('L'))>0;donor=Image.open(C/'raw.png').convert('RGBA')
 if donor.size!=(1254,1254):raise ValueError('unexpected donor')
 donor=np.asarray(donor.resize((125,125),Image.Resampling.LANCZOS));alpha=np.zeros((768,768),np.uint8);alpha[355:480,330:455]=donor[:,:,3];out.mkdir(parents=True);board=Image.new('RGB',(1200,600),'#777');d=ImageDraw.Draw(board)
 for i,(name,path) in enumerate((('source',S/'draft.png'),('guide',S/'source-guide.png'))):
  im=Image.open(path).convert('RGBA');bg=Image.new('RGBA',im.size,'#777');bg.alpha_composite(im);overlay=np.zeros((768,768,4),np.uint8);overlay[mask]=[255,0,255,200];bg.alpha_composite(Image.fromarray(overlay));board.paste(bg.crop((390,370,440,420)).resize((600,600),Image.Resampling.NEAREST).convert('RGB'),(600*i,0));d.text((600*i+3,3),name+' / removed alpha pixels',fill='white')
 board.save(out/'overlap.png');proof={'status':'POSSIBLE_FOREARM_GAP_NOT_APPROVED','source_sha256':sha(S/'draft.png'),'guide_sha256':sha(S/'source-guide.png'),'mask_sha256':sha(A/'removed-opaque-mask.png'),'donor_sha256':sha(C/'raw.png'),'script_sha256':sha(Path(__file__)),'removed_count':int(mask.sum()),'donor_opaque_count':int((mask&(alpha>=240)).sum()),'donor_transparent_count':int((mask&(alpha<10)).sum()),'limitations':['Projection overlap suggests risk but is not a verified painted-forearm correspondence.', 'The donor retains transparency at most affected locations; it was not composited or accepted.', 'A whole-master arm/guide and contact review remains required.']};(out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);print(json.dumps(build(p.parse_args().output)))
