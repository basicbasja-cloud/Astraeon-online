"""Fixed, reviewed surface windows for planted boots that overlap higher up.

Tracks two visible contour extrema; NEVER infers anatomical left/right owners.
The band is a material/camera-specific observation contract, not hidden pose AI.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label


def observe(image,window,edge,material='brown'):
    x0,y0,x1,y1=window
    a=np.asarray(image.convert('RGBA'))[y0:y1,x0:x1]
    r,g,b=a[:,:,:3].astype(float).transpose(2,0,1)
    if material=='foreground':
        # Observation filtering only. Stray pixels remain in the raw/final art
        # and fail independent contour/size checks; no alpha is edited here.
        labels,n=label(a[:,:,3]>=128,structure=np.ones((3,3)));sizes=np.bincount(labels.ravel());sizes[0]=0
        mask=np.isin(labels,np.where(sizes>=100)[0])
    elif material=='brown':mask=(a[:,:,3]>=128)&(r>g+8)&(g>b+3)
    else:raise ValueError('Unknown reviewed observation policy')
    y,x=np.where(mask)
    if len(x)<100:return dict(known=False,reason='Insufficient reviewed boot material')
    # Shaft at top may continue outside; the measured side and bottom must not.
    if y.max()==y1-y0-1 or (x.min()==0 if edge=='min' else x.max()==x1-x0-1):
        return dict(known=False,reason='Observed surface exits window')
    result=dict(known=True,xy=[int((x.min() if edge=='min' else x.max())+x0),int(y.max()+y0)],pixels=int(len(x)),window=window,edge=edge)
    if material=='foreground':result.update(mask_policy='alpha128 reviewed foreground contour',min_component_pixels=100)
    return result


def run(images,windows,budget=6,display_scale=1):
    tracks={};checks={}
    for name,w in windows.items():
        rows=[observe(im,w['roi'],w['edge'],w.get('material','brown')) for im in images]
        known=all(r['known'] for r in rows)
        spread=np.ptp([r['xy'] for r in rows],axis=0)*display_scale if known else None
        tracks[name]=dict(observations=rows,range_display_px=spread.tolist() if known else None,known=known)
        checks[name]=bool(known and max(spread)<=budget)
    scope='Reviewed brown boot contour extrema in fixed windows. Screen near/far labels only. Overlap above the band is permitted; mixed materials, a changing visible surface or occlusion require abstention/manual review. Not ankle/toe joint inference, anatomical ownership, contact force or action approval.'
    if any(w.get('material')=='foreground' for w in windows.values()):scope='Reviewed alpha128 boot contour extrema with100pixel connected-component observation filter. Current fixed non-crossing camera/windows exclude prop/cape/neighbor extrema; source/painting pixels are unchanged. Stray pixels still fail independent raw contour/size checks. No anatomical ownership, hidden joint or force/action approval.'
    return dict(checks=checks,surface_checks_pass=all(checks.values()),tracks=tracks,budget_display_px=budget,display_scale=display_scale,scope=scope,production_pass=False)


def main():
    p=argparse.ArgumentParser();p.add_argument('--contract',type=Path,required=True);p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    c=json.loads(a.contract.read_text());imgs=[Image.open(a.root/r['path']).convert('RGBA') for r in c['frames']];r=run(imgs,c['windows'],c['budget_display_px'],c['display_scale'])
    r['input_hashes_pass']=all(hashlib.sha256((a.root/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in c['frames'])
    a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['checks']));return int(not(r['surface_checks_pass'] and r['input_hashes_pass']))


if __name__=='__main__':raise SystemExit(main())
