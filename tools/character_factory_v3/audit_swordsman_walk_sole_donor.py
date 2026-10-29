"""Review an unapproved boot repaint against projected source skin points."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-sw-sole-repair-20261029'
PROJECTION=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research/swordsman-walk-feet-projection-20261029/receipt.json'

def nearest_brown(image,point):
 a=np.asarray(image.convert('RGB'),dtype=int);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];y,x=np.where((r<190)&(r>g*1.25)&(g>b*1.12)&(r>30));keep=(abs(x-point[0])<80)&(abs(y-point[1])<100);x=x[keep];y=y[keep]
 if not len(x):raise ValueError('empty brown proxy search')
 distances=np.hypot(x-point[0],y-point[1]);i=int(distances.argmin());return [int(x[i]),int(y[i])],float(distances[i])

def build(out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 projection=json.loads(PROJECTION.read_text());images=[]
 for name in ('source.png','donor.png'):
  with Image.open(P/name) as im:
   if im.size!=(1774,887):raise ValueError('unexpected sheet')
   images.append(im.convert('RGB'))
 out.mkdir(parents=True);records=[];panels=[]
 for j,i in enumerate((2,3)):
  source_xy=projection['frames'][i]['feet']['r']['source_guide_xy'];point=[(source_xy[0]-420)*887/696,(source_xy[1]-520)*887/696];board=Image.new('RGB',(768,420),'white');draw=ImageDraw.Draw(board)
  for k,(label,sheet) in enumerate(zip(('before','donor'),images)):
   im=sheet.crop((j*887,0,(j+1)*887,887));near,distance=nearest_brown(im,point);d=ImageDraw.Draw(im);x,y=point;d.ellipse((x-10,y-10,x+10,y+10),outline='#ff8200',width=5);x,y=near;d.ellipse((x-8,y-8,x+8,y+8),outline='#00aaff',width=4);board.paste(im.resize((384,384),Image.Resampling.LANCZOS),(k*384,36));draw.text((k*384+4,6),f'{label} frame {i:02}',fill='black')
   records.append({'frame':i,'image':label,'source_skin_point_tile':point,'nearest_brown_pixel':near,'distance_tile_px':distance,'distance_runtime_px':distance*696/887*240/1536})
  board.save(out/f'frame{i:02}.png');panels.append(board)
 panels[0].save(out/'two-frame-review.gif',save_all=True,append_images=panels[1:],duration=500,loop=0,optimize=False)
 result={'status':'DONOR_NOT_APPROVED','projection_sha256':hashlib.sha256(PROJECTION.read_bytes()).hexdigest(),'input_sha256':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ('source.png','donor.png')},'records':records,
         'limitations':['Closest brown pixel is a coarse color proxy, not an anatomical sole or contact.', 'Projected lowest skin vertex can change and may be occluded or differ from painted footwear.', 'No continuous motion, grounded contact, cutouts, variants, gameplay or production acceptance.']}
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
