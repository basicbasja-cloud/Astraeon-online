"""Combine preserved four-frame master proposals and review against source guide."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import propose_swordsman_walk_pair_registration as reg
import review_swordsman_walk_pair_landmarks as review
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1'
REG=BASE/'review/swordsman-walk-sw-pair-registration-20261029/receipt.json'
PAIR=BASE/'review/swordsman-walk-sw-rearleg-repair-20261029/candidate.png'
LAST=BASE/'review/swordsman-walk-sw03-rearleg-repair-20261029/candidate.png'

def make(out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 registration=json.loads(REG.read_text());manifest=json.loads((review.G/'manifest.json').read_text());sources=[];originals=[]
 with Image.open(reg.P/'paint-00-01.png') as im:
  im=im.convert('RGB');sources.extend(im.crop((i*887,0,(i+1)*887,887)) for i in range(2))
 with Image.open(PAIR) as im:sources.append(im.convert('RGB').crop((0,0,887,887)))
 with Image.open(LAST) as im:sources.append(im.convert('RGB'))
 for i in range(4):
  p=reg.P/('paint-00-01.png' if i<2 else 'paint-02-03.png')
  with Image.open(p) as im:originals.append(im.convert('RGB').crop(((i%2)*887,0,(i%2+1)*887,887)))
 if any(np.any(np.asarray(sources[i])[:400]!=np.asarray(originals[i])[:400]) for i in range(4)):raise ValueError('head source changed since proxy registration')
 out.mkdir(parents=True);(out/'frames').mkdir();panels=[];records=[]
 for i in range(4):
  delta=registration['frames'][i]['translation_source_tile_px'];image=reg.translate(sources[i],delta);image.save(out/'frames'/f'{i:03}.png')
  with Image.open(review.G/'SW'/f'{i:03}.png') as im:
   im=im.convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);guide=bg.crop((420,520,1116,1216)).resize((887,887),Image.Resampling.LANCZOS).convert('RGB')
  board=Image.new('RGB',(710,390),'white');draw=ImageDraw.Draw(board)
  for k,(label,im) in enumerate((('guide',guide),('full-body candidate',image))):
   board.paste(review.overlay(im,manifest['views']['SW']['frames'][i]['landmarks']).resize((355,355),Image.Resampling.LANCZOS),(k*355,35));draw.text((k*355+4,6),f'{label} {i:02} / partial',fill='black')
  panels.append(board);board.save(out/f'frame{i:02}.png');records.append({'frame':i,'translation_source_tile_px':delta,'image_sha256':hashlib.sha256((out/'frames'/f'{i:03}.png').read_bytes()).hexdigest()})
 panels[0].save(out/'partial-four-frames.gif',save_all=True,append_images=panels[1:],duration=160,loop=0,optimize=False)
 result={'status':'FOUR_FRAME_CANDIDATE_NOT_APPROVED','frames':records,'inputs_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (REG,PAIR,LAST)},
         'limitations':['Head registration is driven by an unverified hair centroid; near-zero proxy residual is by construction.', 'Foot markers are bone origins, not measured painted ankles or sole contacts.', 'Only four frames of one direction; repeated GIF is not a complete walk.', 'Alpha extraction, cutouts, variants, game timing and runtime remain unapproved.']}
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(make(a.output)))
