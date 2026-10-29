"""Overlay guide bone positions on the SW03 bounded repaint proposal."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw
import review_swordsman_walk_pair_landmarks as base

def build(candidate,out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 proof=json.loads((candidate/'receipt.json').read_text())
 if proof.get('status')!='SW03_BOUNDED_MASTER_REPAIR_NOT_APPROVED':raise ValueError('unexpected proposal')
 manifest=json.loads((base.G/'manifest.json').read_text());landmarks=manifest['views']['SW']['frames'][3]['landmarks']
 with Image.open(base.G/'SW'/'003.png') as im:
  im=im.convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);guide=bg.crop((420,520,1116,1216)).resize((887,887),Image.Resampling.LANCZOS).convert('RGB')
 with Image.open(candidate/'source.png') as im:source=im.convert('RGB')
 with Image.open(candidate/'candidate.png') as im:repaired=im.convert('RGB')
 panel=Image.new('RGB',(1065,390),'white');draw=ImageDraw.Draw(panel)
 for k,(label,image) in enumerate((('guide',guide),('prior proposal',source),('new proposal',repaired))):
  panel.paste(base.overlay(image,landmarks).resize((355,355),Image.Resampling.LANCZOS),(k*355,35));draw.text((k*355+4,6),f'{label} frame 03',fill='black')
 out.mkdir(parents=True);panel.save(out/'frame03-comparison.png')
 proof={'status':'SW03_BONE_OVERLAY_NOT_ACCEPTED','candidate_receipt_sha256':hashlib.sha256((candidate/'receipt.json').read_bytes()).hexdigest(),'limitations':['Projected foot bone origin is not a measured painted ankle or sole contact.', 'This is one master pose, not an animation or runtime validation.']}
 (out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.candidate,a.output)))
