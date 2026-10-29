"""Bound a crop-generated rear-boot repaint inside the SW03 full master."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from audit_swordsman_walk_sole_donor import nearest_brown
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'authoring/characters/factory-v3/patch-0.0.1/review/swordsman-walk-sw-fourframe-candidate-20261029/frames/003.png'
P=ROOT/'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-walk-sw03-sole-crop-20261029'
PROJECTION=ROOT/'authoring/characters/factory-v3/patch-0.0.1/research/swordsman-walk-feet-projection-20261029/receipt.json'

def build(out):
 if out.exists() or out.is_symlink():raise ValueError('choose fresh output')
 with Image.open(SOURCE) as im:source=im.convert('RGB')
 if source.size!=(887,887):raise ValueError('unexpected source geometry')
 path=P/'donor.png'
 with Image.open(path) as im:
  if im.size!=(1254,1254):raise ValueError('unexpected donor crop')
  crop=im.convert('RGB').resize((360,360),Image.Resampling.LANCZOS)
 canvas=Image.new('RGB',source.size,'white');canvas.paste(crop,(130,420));mask=Image.new('L',source.size);ImageDraw.Draw(mask).rounded_rectangle((180,460,465,730),radius=16,fill=255);mask=mask.filter(ImageFilter.GaussianBlur(5));result=Image.composite(canvas,source,mask)
 aa=np.asarray(source);bb=np.asarray(result);m=np.asarray(mask);changed=np.any(aa!=bb,axis=2);outside=int((changed&(m==0)).sum())
 if outside:raise ValueError('outside-mask changes')
 projected=json.loads(PROJECTION.read_text())['frames'][3]['feet']['r']['source_guide_xy'];point=[(projected[0]-420)*887/696,(projected[1]-520)*887/696]
 out.mkdir(parents=True);source.save(out/'source.png');result.save(out/'candidate.png');mask.save(out/'mask.png');records=[];panels=[]
 for label,image in (('source',source),('proposal',result)):
  nearest,distance=nearest_brown(image,point);records.append({'label':label,'nearest_brown_pixel':nearest,'brown_proxy_distance_runtime_px':distance*696/887*240/1536})
  image=image.copy();d=ImageDraw.Draw(image);x,y=point;d.ellipse((x-10,y-10,x+10,y+10),outline='#ff8200',width=5);x,y=nearest;d.ellipse((x-8,y-8,x+8,y+8),outline='#00aaff',width=4);panel=Image.new('RGB',(444,474),'white');panel.paste(image.resize((444,444),Image.Resampling.LANCZOS),(0,30));ImageDraw.Draw(panel).text((5,5),f'{label} / frame 03 only',fill='black');panels.append(panel)
 panels[0].save(out/'still-comparison.gif',save_all=True,append_images=panels[1:],duration=1000,loop=0,optimize=False)
 proof={'status':'BOUNDED_SW03_REPAINT_PROPOSAL_NOT_APPROVED','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'donor_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'projection_sha256':hashlib.sha256(PROJECTION.read_bytes()).hexdigest(),'source_guide_point_tile':point,'mask_rectangle':[180,460,465,730],'donor_crop_source_rect':[130,420,490,780],'changed_pixels':int(changed.sum()),'outside_mask_changed_pixels':outside,'records':records,
        'limitations':['Brown pixel is a color proxy; selected source skin vertex is not a verified painted sole.', 'Mask may alter knee/costume and create seams; other frames and full sequence remain unapproved.', 'No alpha, semantic parts, variants or runtime admission.']}
 (out/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');return proof
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output)))
