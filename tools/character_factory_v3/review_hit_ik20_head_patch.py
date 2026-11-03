"""Review a bounded 20-frame head edit; GIF is not gameplay timing."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw
import propose_hit_ik20_head_patch as patch
GUIDE=patch.P/'swordsman-hit-sw-floor-ik20-20261103/guide.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(candidate,out):
 if out.exists() or out.is_symlink():raise ValueError('fresh output required')
 inputs=[GUIDE,patch.SRC,candidate/'paint.png'];sheets=[]
 for p in inputs:
  with Image.open(p) as im:sheets.append(im.convert('RGB').resize((1600,1280),Image.Resampling.LANCZOS))
 out.mkdir(parents=True);frames=[]
 for i in range(20):
  x=i%5*320;y=i//5*320;b=Image.new('RGB',(960,344),'white');d=ImageDraw.Draw(b)
  for j,s in enumerate(sheets):b.paste(s.crop((x,y,x+320,y+320)),(j*320,24));d.text((j*320+4,4),f'{("guide","before","bounded draft")[j]} {i:02}',fill='black')
  frames.append(b)
 for n,ms in [('normal.gif',100),('slow.gif',220)]:frames[0].save(out/n,save_all=True,append_images=frames[1:],duration=[ms]*19+[ms*5],loop=0,optimize=False)
 for i in (4,5,6,7):frames[i].save(out/f'frame{i:02}.png')
 (out/'receipt.json').write_text(json.dumps({'status':'REVIEW_NOT_ACCEPTED','inputs':{str(p):sha(p) for p in inputs},'script_sha256':sha(Path(__file__)),'limitations':['The GIF repeats a one-shot and uses illustrative timing.','Boxes may cut hair or collar; head pose and sequence still need anatomical acceptance.','Only SW view; cutout, variants and gameplay not evaluated.']},indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();build(a.candidate,a.output)
