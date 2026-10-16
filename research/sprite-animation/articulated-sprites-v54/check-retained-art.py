"""SHA-bound pixel retention in manually reviewed head/cape regions. Not anatomy inference."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();out={};regions={'S':[[340,320],[370,350],[375,370],[345,350]],'N':[[232,235],[283,235],[304,360],[212,360]],'NW':[[248,235],[269,235],[332,330],[345,354],[269,378],[251,375]],'NE':[[246,235],[267,235],[258,375],[158,367],[171,343]],'SE':[[185,300],[197,300],[183,342],[157,368],[145,360],[160,330]]}
for v in ['S','SW','W','NW','N','NE','E','SE']:
 source=P.parent/'ro-core-views-v52/stage/idle'/v/'00.png';master=np.array(Image.open(source).convert('RGBA'));head_path=P/'parts'/v/'head.png';head=np.array(Image.open(head_path));end={'W':204,'E':204,'N':198}.get(v,211);mask=master[:end,:,3]>=128;assert np.array_equal(master[:end][mask],head[:end][mask]),v
 row={'source_sha256':sha(source),'head_sha256':sha(head_path),'retained_head_region':[0,0,512,end],'head_solid_pixels_equal':True}
 if v in regions:
  bodypath=P/'parts'/v/'body.png';body=Image.open(bodypath).convert('RGBA');m=Image.new('L',(512,512));ImageDraw.Draw(m).polygon(regions[v],fill=255);mask=(np.array(m)>0)&(master[:,:,3]>=128);current=np.array(body);different=int(np.any(current[mask]!=master[mask],axis=1).sum());assert different==0,(v,different);bad=body.copy();ImageDraw.Draw(bad).rectangle((0,0,512,512),fill=(0,0,0,0));assert np.any(np.array(bad)[mask]!=master[mask]);row['cape']={'body_sha256':sha(bodypath),'reviewed_polygon':regions[v],'reference_solid_pixels':int(mask.sum()),'different_pixels':different,'blank_cape_negative_rejected':True}
  if v=='NW':
   bad=body.copy();ImageDraw.Draw(bad).polygon([[294,218],[309,224],[317,245],[319,279],[321,309],[318,334],[305,340],[299,311],[299,278],[296,249]],fill=(0,0,0,0));n=int(np.any(np.array(bad)[mask]!=master[mask],axis=1).sum());assert n>0;row['cape']['actual_old_far_arm_region_cut_negative_pixels']=n
 out[v]=row
(P/'retained-art-qa.json').write_text(json.dumps({'pass':True,'views':out,'scope':'Exact original head and manually declared retained cape core only. New native W/E/SW cape variants require separate image review; hidden joints and all outside-ROI art are not approved by this check.'},indent=2)+'\n');print({v:r.get('cape',{}).get('reference_solid_pixels','new cape requires manual review') for v,r in out.items()})
