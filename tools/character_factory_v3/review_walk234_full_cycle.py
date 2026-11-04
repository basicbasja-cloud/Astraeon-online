"""Compare original and bounded Walk drafts with the guide through all 16 poses."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-sw-baseline-seam-repair-20261104'
REV=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research/swordsman-walk234-bounded-20261104/review-sheet.png'
def build(out):
 if out.exists():raise ValueError('Fresh output required')
 paths=[BASE/'guide-contact.png',BASE/'generated-sheet.png',REV]
 sheets=[Image.open(p).convert('RGB').resize((1536,1536),Image.Resampling.LANCZOS) for p in paths]
 out.mkdir(parents=True);panels=[]
 for i in range(16):
  box=(i%4*384,i//4*384,(i%4+1)*384,(i//4+1)*384)
  panel=Image.new('RGB',(1152,412),'white');d=ImageDraw.Draw(panel)
  for col,(name,sheet) in enumerate(zip(('guide','original draft','bounded draft'),sheets)):
   panel.paste(sheet.crop(box),(col*384,28));d.text((col*384+4,5),f'{name} {i:02}',fill='black')
  panels.append(panel)
 for n,t in [('cycle.gif',85),('cycle-slow.gif',200)]:panels[0].save(out/n,save_all=True,append_images=panels[1:],duration=t,loop=0,optimize=False)
 for seq in ((0,1,2,3),(3,4,5,6),(14,15,0,1)):
  board=Image.new('RGB',(1152,412*len(seq)),'white')
  for j,i in enumerate(seq):board.paste(panels[i],(0,j*412))
  board.save(out/('boundary-'+ '-'.join(map(str,seq))+'.png'))
 (out/'receipt.json').write_text(json.dumps({'status':'FULL_CYCLE_DRAFT_REVIEW_NOT_ACCEPTED','inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'frames':16,'preview_delays_ms':[85,200],'limitations':['Timing is diagnostic, not the gameplay contract.','No registration or per-frame fit is applied.','Visual comparison is not a contact or anatomy pass.']},indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);build(p.parse_args().output)
