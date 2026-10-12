"""Decode actual exposure durations. Measures clock regularity, not acting."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
def audit(path):
 delays=[]
 with Image.open(path) as im:
  for i in range(im.n_frames):
   im.seek(i);im.load();d=im.info.get('duration')
   if d is None or not np.isfinite(d) or d<=0:raise ValueError('Unknown or invalid decoded exposure duration')
   delays.append(float(d))
 mean=float(np.mean(delays))
 return {'schema':'decoded-animation-cadence-v1','file':str(path),'sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),'frame_count':len(delays),'delays_ms':delays,'duration_ms':sum(delays),'mean_ms':mean,'range_ms':[min(delays),max(delays)],'standard_deviation_ms':float(np.std(delays)),'relative_exposure_range':(max(delays)-min(delays))/mean,'uniform_exposures':max(delays)==min(delays),'anatomy_accepted':False,'scope':'Actual file exposure timing only. Nonuniform durations can be intentional; regularity does not establish natural animation or correct contacts.'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--animation',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args();r=audit(a.animation);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2)+'\n');print('CADENCE',r['frame_count'],r['range_ms'],r['duration_ms'])
if __name__=='__main__':main()
