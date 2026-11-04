"""Rebuild 2x2 fixed-grid guide batches from the retained 16-pose sheet."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-male-walk-sw-fixed-crop-20261029/guide-contact.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 with Image.open(SOURCE) as im:
  if im.width!=im.height:raise ValueError('expected square fixed-grid source')
  sheet=im.convert('RGB').resize((1536,1536))
 out.mkdir(parents=True);files=[]
 for b in range(4):
  board=Image.new('RGB',(768,768),'white')
  for j in range(4):
   i=b*4+j;x=i%4*384;y=i//4*384;board.paste(sheet.crop((x,y,x+384,y+384)),(j%2*384,j//2*384))
  p=out/f'walk-guide-batch-{b}-20261104.png';board.save(p);files.append({'name':p.name,'sha256':sha(p)})
 (out/'receipt.json').write_text(json.dumps({'status':'GUIDES_NOT_PAINTED_OR_APPROVED','source_sha256':sha(SOURCE),'script_sha256':sha(Path(__file__)),'outputs':files},indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);build(p.parse_args().output)
