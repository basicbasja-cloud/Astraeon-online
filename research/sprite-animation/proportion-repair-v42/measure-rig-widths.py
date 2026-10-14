"""Observe actual isolated rendered material sections, not matrix width claims."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--render',default='rig-render-6');args=ap.parse_args()
P=Path(__file__).resolve().parent;R=P/args.render;b=json.loads((R/'bindings.json').read_text());results={}
for name in ['left.upperarm','right.upperarm','left.forearm','right.forearm','left.shin','right.shin','left.hand','right.hand']:
 d=b['assets'][name];p=np.array(d['pivot']);end=np.array(d['end']);u=(end-p)/np.linalg.norm(end-p);v=np.array([-u[1],u[0]]);rows=[]
 for i in range(8):
  f=b['frames'][i];rec=next(q for q in f['parts'] if q['name']==name);M=np.array(rec['matrix']);fraction=.9 if name.endswith('.hand') else .5;q=M@np.array([*(p+(end-p)*fraction),1]);axis=np.array(f['source_points'][d['chain'][1]])-f['source_points'][d['chain'][0]];n=np.array([-axis[1],axis[0]])/np.linalg.norm(axis);t=np.arange(-60,60.01,.25);coords=q[None,:]+t[:,None]*n[None,:];a=np.array(Image.open(R/f'isolated/{name}/{i:02}.png').convert('RGBA').getchannel('A'));xs=np.rint(coords[:,0]).astype(int);ys=np.rint(coords[:,1]).astype(int);valid=(xs>=0)&(ys>=0)&(xs<384)&(ys<512);hit=np.zeros(len(t),bool);hit[valid]=a[ys[valid],xs[valid]]>=128;idx=np.flatnonzero(hit)
  # Actual foreground extent at the same authored surface section. Not hidden
  # joint detection or automatic labeling of a merged full-character image.
  row=dict(index=i,visible_width_px=float(t[idx[-1]]-t[idx[0]]+.25) if len(idx) else None,center=q.tolist(),normal=n.tolist(),image_sha256=hashlib.sha256((R/f'isolated/{name}/{i:02}.png').read_bytes()).hexdigest());rows.append(row)
 results[name]=dict(observations=rows,range_px=[min(r['visible_width_px'] for r in rows),max(r['visible_width_px'] for r in rows)])
(R/'width-qa.json').write_text(json.dumps(dict(parts=results,scope='Alpha128 quarter-pixel nearest-sampled cross-section of actual rendered isolated authored parts at constant asset centerline fraction. Authored surface correspondence, not automatic anatomy/volume detection or full-image visibility proof.',production_pass=False),indent=2)+'\n');print({k:v['range_px'] for k,v in results.items()})
