"""Produce a fixed-crop identity reference from protected Swordsman master."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/'authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/basic-attack-simple/SW/Master/000.png';CROP=(110,135,380,405)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('fresh output required')
 with Image.open(SRC) as im:
  if im.size!=(512,512):raise ValueError('unexpected source canvas')
  img=im.convert('RGBA');box=img.getchannel('A').getbbox()
  if box is None or box[0]<CROP[0] or box[1]<CROP[1] or box[2]>CROP[2] or box[3]>CROP[3]:raise ValueError('reference crop clips baseline')
  bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(img);ref=bg.crop(CROP).resize((512,512),Image.Resampling.LANCZOS).convert('RGB')
 out.mkdir(parents=True);ref.save(out/'reference.png');(out/'receipt.json').write_text(json.dumps({'status':'IDENTITY_REFERENCE_NOT_WALK_MASTER','source_sha256':sha(SRC),'crop':CROP,'reference_sha256':sha(out/'reference.png'),'script_sha256':sha(Path(__file__)),'limitations':['This identity image uses BasicAttack pose 00 and is not a Walk pose or finished animation.']},indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);build(p.parse_args().output)
