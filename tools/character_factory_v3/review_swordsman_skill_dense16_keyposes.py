"""Fixed-grid comparison of sixteen sparse source and painted skill poses."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
S=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-skill-sw-dense16-keyposes-20261103'
INDICES=[0,4,7,11,15,18,22,26,29,33,37,40,44,48,51,55]
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('fresh output required')
 sheets=[Image.open(S/n).convert('RGB').resize((1536,1536),Image.Resampling.LANCZOS) for n in ('guide.png','generated.png')]
 out.mkdir(parents=True);frames=[]
 for i,n in enumerate(INDICES):
  b=Image.new('RGB',(768,416),'white');d=ImageDraw.Draw(b)
  for j,s in enumerate(sheets):
   tile=s.crop(((i%4)*384,(i//4)*384,(i%4+1)*384,(i//4+1)*384));b.paste(tile,(j*384,32));d.text((j*384+5,6),f'{"guide" if j==0 else "paint draft"} source pose {n:02}',fill='black')
  frames.append(b)
 frames[0].save(out/'keyposes.gif',save_all=True,append_images=frames[1:],duration=220,loop=0,optimize=False)
 for i in (2,6,7,15):frames[i].save(out/f'pose-{INDICES[i]:02}.png')
 digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 (out/'receipt.json').write_text(json.dumps({'status':'SPARSE_KEYPOSE_DRAFT_NOT_ANIMATION','source_pose_indices':INDICES,'inputs':{n:digest(S/n) for n in ('guide.png','generated.png')},'script_sha256':digest(Path(__file__)),'limitations':['Sparse samples only, not 56 frames or gameplay timing.','Character, grip, scale, occlusion and foot contacts unapproved.','Cutouts, FX, other views, runtime and variant work absent.']},indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);build(p.parse_args().output)
