"""Overlay fixed source rig landmarks on unapproved original/registered walk frames."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-sw-adjacent-pairs-20261029'
G=ROOT/'authoring/characters/factory-v3/patch-0.0.1/guides/4e519e1eadc69aaf28a2'
COLORS={'head':(243,24,228),'hand_r':(255,60,30),'foot_r':(255,194,0),'foot_l':(0,170,255)}

def overlay(image,landmarks):
 draw=ImageDraw.Draw(image)
 for name,color in COLORS.items():
  x=(landmarks[name][0]-420)*887/696;y=(landmarks[name][1]-520)*887/696;r=8
  draw.ellipse((x-r,y-r,x+r,y+r),outline=color,width=4)
 return image

def make(registered,out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 receipt=json.loads((registered/'receipt.json').read_text());manifest=json.loads((G/'manifest.json').read_text());out.mkdir(parents=True);panels=[]
 for i in range(4):
  with Image.open(G/'SW'/f'{i:03}.png') as im:
   im=im.convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);guide=bg.crop((420,520,1116,1216)).resize((887,887),Image.Resampling.LANCZOS).convert('RGB')
  pair=P/('paint-00-01.png' if i<2 else 'paint-02-03.png')
  with Image.open(pair) as im:original=im.convert('RGB').crop(((i%2)*887,0,(i%2+1)*887,887))
  with Image.open(registered/'frames'/f'{i:03}.png') as im:candidate=im.convert('RGB')
  board=Image.new('RGB',(1065,390),'white');d=ImageDraw.Draw(board)
  for k,(label,im) in enumerate((('guide',guide),('original',original),('full-frame proposal',candidate))):
   board.paste(overlay(im,manifest['views']['SW']['frames'][i]['landmarks']).resize((355,355),Image.Resampling.LANCZOS),(k*355,35));d.text((k*355+4,6),f'{label} {i:02}',fill='black')
  panels.append(board);board.save(out/f'frame{i:02}.png')
 panels[0].save(out/'partial-landmark-review.gif',save_all=True,append_images=panels[1:],duration=180,loop=0,optimize=False)
 result={'status':'SOURCE_BONE_OVERLAY_NOT_ACCEPTANCE','colors':{k:list(v) for k,v in COLORS.items()},'registration_receipt_sha256':hashlib.sha256((registered/'receipt.json').read_bytes()).hexdigest(),'limitations':['Bone head points are not ground-contact soles, hand grips, or painted landmarks.', 'Overlay makes misalignment visible but is not a quantitative acceptance test.', 'Four frames only, repeated GIF is not a walk loop.']}
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--registered',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(make(a.registered,a.output)))
