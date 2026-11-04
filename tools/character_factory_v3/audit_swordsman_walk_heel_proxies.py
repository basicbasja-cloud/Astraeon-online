"""Flag possible painted heel drift using a deliberately provisional color proxy."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/review/swordsman-walk-sw-fourframe-candidate-20261029'
G=ROOT/'authoring/characters/factory-v3/patch-0.0.1/guides/4e519e1eadc69aaf28a2/manifest.json'

def sample(image,guide):
 a=np.asarray(image.convert('RGB'),dtype=int);y,x=np.indices(a.shape[:2]);gx=(guide[0]-420)*887/696;gy=(guide[1]-520)*887/696;r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
 mask=(x>=gx-25)&(x<=gx+5)&(y>=gy)&(y<=gy+80)&(r<190)&(r>g*1.25)&(g>b*1.12)&(r>30)
 yy,xx=np.where(mask)
 if not len(yy):raise ValueError('empty heel color proxy')
 bottom=int(yy.max());near=xx[yy>=bottom-2];return {'guide_foot_origin':[gx,gy],'proxy_xy':[float(near.mean()),bottom],'candidate_pixels':len(yy),'roi':[gx-25,gy,gx+5,gy+80]}

def audit(out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 guide=json.loads(G.read_text())['views']['SW']['frames'];out.mkdir(parents=True);records=[];panels=[];offset0=None
 for i in range(4):
  path=P/'frames'/f'{i:03}.png'
  with Image.open(path) as im:image=im.convert('RGB')
  r=sample(image,guide[i]['landmarks']['foot_l']);offset=r['proxy_xy'][1]-r['guide_foot_origin'][1]
  if offset0 is None:offset0=offset
  r.update({'frame':i,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'vertical_offset_from_guide_px':offset,'offset_change_from_frame00_runtime_px':(offset-offset0)*696/887*240/1536});records.append(r)
  d=ImageDraw.Draw(image);x,y=r['guide_foot_origin'];u,v=r['proxy_xy'];d.ellipse((x-8,y-8,x+8,y+8),outline='#00aeff',width=4);d.ellipse((u-8,v-8,u+8,v+8),outline='#ff00df',width=4);d.rectangle(tuple(r['roi']),outline='#e0a000',width=2)
  crop=image.crop((360,550,650,810)).resize((580,520),Image.Resampling.NEAREST);board=Image.new('RGB',(580,550),'white');board.paste(crop,(0,30));ImageDraw.Draw(board).text((4,5),f'frame {i:02} / foot bone cyan / color proxy magenta',fill='black');board.save(out/f'frame{i:02}.png');panels.append(board)
 panels[0].save(out/'partial-heel-proxy.gif',save_all=True,append_images=panels[1:],duration=220,loop=0,optimize=False)
 result={'status':'PROVISIONAL_COLOR_PROXY_NOT_CONTACT_APPROVAL','frames':records,'guide_sha256':hashlib.sha256(G.read_bytes()).hexdigest(),
         'limitations':['Brown-pixel ROI can select another shoe region, a costume pixel, or a different feature as shape changes.', 'Source foot bone origin is not a ground-contact landmark, and foot pose may rotate.', 'Four poses only; no game velocity, full loop, source/cutout or runtime approval.']}
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(audit(a.output)))
