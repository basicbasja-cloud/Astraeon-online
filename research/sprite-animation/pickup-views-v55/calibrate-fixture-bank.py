"""One similarity transform from an unused neutral fixture, never active pose fitting."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from scipy import ndimage
from PIL import Image

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def feature(im):
    a=np.asarray(im.convert('RGBA'))[:,:,3]>=128
    labels,n=ndimage.label(a);counts=np.bincount(labels.ravel());counts[0]=0
    if not n or counts.max()<100:raise ValueError('Missing neutral fixture')
    y,x=np.where(labels==counts.argmax());bottom=int(y.max());top=int(y.min())
    # Neutral sole location only; active poses never enter calibration.
    xx=x[y>=bottom-max(1,round((bottom-top+1)*.02))+1]
    return {'height':bottom-top+1,'bottom':bottom,'sole_mid':float((xx.min()+xx.max())/2),'sole_width':int(xx.max()-xx.min()+1),'crown_width':int(x[y<=top+round((bottom-top+1)*.18)].max()-x[y<=top+round((bottom-top+1)*.18)].min()+1)}

def calibrate(raw,neutral,out):
    im=Image.open(raw).convert('RGBA');assert im.width==im.height and im.width%2==0
    cell=im.width//2;fixture=im.crop((cell,cell,2*cell,2*cell));a=feature(fixture);b=feature(Image.open(neutral));s=b['height']/a['height'];tx=b['sole_mid']-s*a['sole_mid'];ty=b['bottom']-s*a['bottom']
    out.mkdir(parents=True,exist_ok=True);rows=[]
    for i in range(4):
        tile=im.crop((i%2*cell,i//2*cell,i%2*cell+cell,i//2*cell+cell))
        tile=tile.transform((512,512),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),Image.Resampling.BICUBIC)
        p=out/f'{i}.png';tile.save(p);rows.append({'path':str(p),'sha256':sha(p)})
    measured=feature(Image.open(out/'3.png'))
    # Independent same-pose shape checks. Endpoint raster uncertainty <=2px.
    checks={k:abs(measured[k]-b[k])<=max(2,.08*b[k]) for k in ['sole_width','crown_width']}
    r={'raw_sha256':sha(raw),'neutral_sha256':sha(neutral),'raw_canvas':list(im.size),'fixture_slot':3,'fixture_source':a,'target':b,'scale':s,'translation':[tx,ty],'all_four_tiles_same_affine':True,'active_pose_measurements_used':False,'normalized_fixture':measured,'shape_checks':checks,'fixture_calibration_pass':all(checks.values()),'frames':rows,'production_pass':False}
    (out/'calibration.json').write_text(json.dumps(r,indent=2)+'\n');return r

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('raw',type=Path);p.add_argument('neutral',type=Path);p.add_argument('out',type=Path);a=p.parse_args();print(json.dumps(calibrate(a.raw,a.neutral,a.out),indent=2))
