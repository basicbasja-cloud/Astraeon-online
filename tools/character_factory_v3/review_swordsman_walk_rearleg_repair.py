"""Review 2-frame master leg repair with guide bone overlays."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw
import review_swordsman_walk_pair_landmarks as base

def make(candidate,out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 proof=json.loads((candidate/'receipt.json').read_text());manifest=json.loads((base.G/'manifest.json').read_text())
 if proof.get('status')!='TWO_FRAME_BOUNDED_MASTER_REPAIR_NOT_APPROVED':raise ValueError('unexpected candidate')
 with Image.open(candidate/'source.png') as im:source=im.convert('RGB')
 with Image.open(candidate/'candidate.png') as im:repaired=im.convert('RGB')
 out.mkdir(parents=True);panels=[]
 for n,i in enumerate((2,3)):
  with Image.open(base.G/'SW'/f'{i:03}.png') as im:
   im=im.convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);guide=bg.crop((420,520,1116,1216)).resize((887,887),Image.Resampling.LANCZOS).convert('RGB')
  images=[guide,source.crop((n*887,0,(n+1)*887,887)),repaired.crop((n*887,0,(n+1)*887,887))];panel=Image.new('RGB',(1065,390),'white');d=ImageDraw.Draw(panel)
  for k,(label,image) in enumerate(zip(('guide','original','bounded proposal'),images)):
   panel.paste(base.overlay(image,manifest['views']['SW']['frames'][i]['landmarks']).resize((355,355),Image.Resampling.LANCZOS),(k*355,35));d.text((k*355+4,6),f'{label} {i:02}',fill='black')
  panels.append(panel);panel.save(out/f'frame{i:02}.png')
 panels[0].save(out/'two-frame-review.gif',save_all=True,append_images=panels[1:],duration=400,loop=0,optimize=False)
 result={'status':'TWO_FRAME_BONE_OVERLAY_REVIEW_NOT_ACCEPTED','candidate_receipt_sha256':hashlib.sha256((candidate/'receipt.json').read_bytes()).hexdigest(),'limitations':['Bone origins are not confirmed painted joints or sole contacts.', 'Mask seams, frame-to-frame anatomy, other frames, other views and runtime remain unverified.', 'Repeating two-frame review is not a complete walk.']}
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(make(a.candidate,a.output)))
