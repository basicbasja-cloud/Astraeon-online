"""Bound two crop-generated leg repaints inside the same SW02 master."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from audit_swordsman_walk_sole_donor import nearest_brown
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/review/swordsman-walk-sw-fourframe-candidate-20261029/frames/002.png'
P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-sw02-sole-crop-20261029'
PROJECTION=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research/swordsman-walk-feet-projection-20261029/receipt.json'

def build(out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 with Image.open(SOURCE) as im:source=im.convert('RGB')
 if source.size!=(887,887):raise ValueError('unexpected source geometry')
 projected=json.loads(PROJECTION.read_text())['frames'][2]['feet']['r']['source_guide_xy'];point=[(projected[0]-420)*887/696,(projected[1]-520)*887/696]
 mask=Image.new('L',source.size);ImageDraw.Draw(mask).rounded_rectangle((180,470,465,750),radius=16,fill=255);mask=mask.filter(ImageFilter.GaussianBlur(5))
 out.mkdir(parents=True);source.save(out/'source.png');mask.save(out/'mask.png');rows=[];panels=[]
 for label in ('source','v1','v2'):
  if label=='source':result=source;digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
  else:
   p=P/f'donor-{label}.png';digest=hashlib.sha256(p.read_bytes()).hexdigest()
   with Image.open(p) as im:
    if im.size!=(1254,1254):raise ValueError('unexpected donor crop')
    crop=im.convert('RGB').resize((360,360),Image.Resampling.LANCZOS)
   canvas=Image.new('RGB',source.size,'white');canvas.paste(crop,(130,430));result=Image.composite(canvas,source,mask);result.save(out/f'{label}.png')
  a=np.asarray(source);b=np.asarray(result);m=np.asarray(mask);changed=np.any(a!=b,axis=2);outside=int((changed&(m==0)).sum())
  if outside:raise ValueError('outside-mask changes')
  nearest,distance=nearest_brown(result,point);rows.append({'label':label,'input_sha256':digest,'changed_pixels':int(changed.sum()),'outside_mask_changed_pixels':outside,'nearest_brown_pixel':nearest,'brown_proxy_distance_runtime_px':distance*696/887*240/1536})
  image=result.copy();d=ImageDraw.Draw(image);x,y=point;d.ellipse((x-10,y-10,x+10,y+10),outline='#ff8200',width=5);x,y=nearest;d.ellipse((x-8,y-8,x+8,y+8),outline='#00aaff',width=4);image=image.resize((444,444),Image.Resampling.LANCZOS);panel=Image.new('RGB',(444,474),'white');panel.paste(image,(0,30));ImageDraw.Draw(panel).text((5,5),f'{label} / frame 02 only',fill='black');panels.append(panel)
 panels[0].save(out/'still-comparison.gif',save_all=True,append_images=panels[1:],duration=1000,loop=0,optimize=False)
 proof={'status':'BOUNDED_SW02_REPAINT_PROPOSALS_NOT_APPROVED','projection_sha256':hashlib.sha256(PROJECTION.read_bytes()).hexdigest(),'source_guide_point_tile':point,'mask_rectangle':[180,470,465,750],'donor_crop_source_rect':[130,430,490,790],'records':rows,
        'limitations':['Nearest brown pixel is a color proxy; source skin vertex is not an identified painted sole.', 'Mask can affect knee/costume and create seams; no whole-sequence contact or anatomy acceptance.', 'No alpha, part cutouts, other directions, variant or runtime admission.']}
 (out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
