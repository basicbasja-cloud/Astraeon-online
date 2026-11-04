"""Extract a frame-specific generated repair into a bounded master region."""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-sw-baseline-seam-repair-20261104/generated-sheet.png'
PROPOSAL=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-sw03-targeted-20261104/result.png'
POLYGON=[(195,480),(348,480),(389,503),(388,535),(350,566),(325,625),(195,625)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(out):
 if out.exists():raise ValueError('Use fresh output')
 if sha(SOURCE)!='8d711b15c44215a69f69869596c260f2753d1c55cae3ba016bc78dd191a1df44' or sha(PROPOSAL)!='4d7e74145d44a0153cafb83f52bcb127f8ef666168f7124b858bb9b7a0310914':raise ValueError('Inputs changed')
 sheet=Image.open(SOURCE).convert('RGB').resize((1536,1536),Image.Resampling.LANCZOS)
 original=sheet.crop((1152,0,1536,384)).resize((768,768),Image.Resampling.LANCZOS)
 proposal=Image.open(PROPOSAL).convert('RGB').resize((768,768),Image.Resampling.LANCZOS)
 mask=Image.new('L',(768,768));ImageDraw.Draw(mask).polygon(POLYGON,fill=255)
 master=Image.composite(proposal,original,mask)
 protected=sum(a!=b for a,b,m in zip(original.getdata(),master.getdata(),mask.getdata()) if m==0)
 assert protected==0
 # Preserve original pixels at review resolution outside the downsampled mask.
 frame=sheet.crop((1152,0,1536,384));smallmask=mask.resize((384,384),Image.Resampling.NEAREST)
 frame=Image.composite(master.resize((384,384),Image.Resampling.LANCZOS),frame,smallmask)
 revised=sheet.copy();revised.paste(frame,(1152,0))
 out.mkdir(parents=True);master.save(out/'master03.png');mask.save(out/'mask.png');revised.save(out/'review-sheet.png')
 panels=[]
 for i in (2,3,4):
  box=((i%4)*384,(i//4)*384,(i%4+1)*384,(i//4+1)*384)
  p=Image.new('RGB',(768,412),'white');p.paste(sheet.crop(box),(0,28));p.paste(revised.crop(box),(384,28));d=ImageDraw.Draw(p);d.text((4,5),f'original draft {i:02}',fill='black');d.text((388,5),f'bounded revision {i:02}',fill='black');p.save(out/f'frame{i:02}.png');panels.append(p)
 panels[0].save(out/'neighbors-slow.gif',save_all=True,append_images=panels[1:],duration=250,loop=0,optimize=False)
 receipt={'status':'BOUNDED_REPAIR_DRAFT_NOT_ACCEPTED','source_sha256':sha(SOURCE),'proposal_sha256':sha(PROPOSAL),'script_sha256':sha(Path(__file__)),'polygon_768':POLYGON,'protected_pixels_changed_768':protected,'limitations':['Uses actual frame 03 proposal pixels only; no reused limb from another pose.', '768 is a review resize, not newly authored detail.', 'No claim of verified sole contact, whole-cycle stability, cutout or gameplay approval.']}
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);build(p.parse_args().output)
