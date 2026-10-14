"""Fixed-view separated boot surface observations; never anatomical LR labels."""
import numpy as np
from scipy.ndimage import label

def observe(image,band):
    x0,y0,x1,y1=map(int,band)
    if min(x0,y0)<0 or x1>image.shape[1] or y1>image.shape[0]:return dict(known=False,reason='Band outside image')
    mask=image[y0:y1,x0:x1,3]>=128;labels,n=label(mask,structure=np.ones((3,3)))
    components=[]
    for k in range(1,n+1):
        y,x=np.where(labels==k)
        if len(x)<100:continue
        if x.min()==0 or x.max()==x1-x0-1 or y.max()==y1-y0-1:return dict(known=False,reason='Support component clipped by side/bottom of band')
        components.append(dict(surface_xy=[float(x.min()+x0),float(y.max()+y0)],pixels=int(len(x)),centroid_x=float(x.mean()+x0),bbox=[int(x.min()+x0),int(y.min()+y0),int(x.max()+x0),int(y.max()+y0)]))
    if len(components)!=2:return dict(known=False,reason=f'Expected two separated boot components; found{len(components)}. Occluded/merged anatomy remains unknown.')
    components.sort(key=lambda c:c['centroid_x'])
    return dict(known=True,components=components,scope='Screen-left/right visible boot surfaces in one fixed non-crossing view. No anatomical left/right, world-ground contact or hidden joint certification.')

def sequence(raw,rendered,scale,budget=6):
    observations_raw=[observe(a,[90,430,310,500]) for a in raw]
    observations_rendered=[observe(a,[90,420,310,500]) for a in rendered]
    known=all(x['known'] for x in observations_raw+observations_rendered)
    output={}
    if known:
        for k,name in enumerate(['screen_left_boot','screen_right_boot']):
            r=np.array([x['components'][k]['surface_xy'] for x in observations_raw]);p=np.array([x['components'][k]['surface_xy'] for x in observations_rendered]);nr=np.ptp(r,axis=0)*scale;pr=np.ptp(p,axis=0)
            output[name]=dict(raw_surface_xy=r.tolist(),rendered_surface_xy=p.tolist(),raw_range_at_display_scale_px=nr.tolist(),rendered_range_px=pr.tolist(),pass_=bool(max(*nr,*pr)<=budget))
    return dict(observations_known=known,raw=observations_raw,rendered=observations_rendered,support=output,pass_=bool(known and all(x['pass_'] for x in output.values())),scope='Whole connected foreground components avoid neighboring-boot contamination. Explicit 100px component filter and alpha128 visible-surface threshold are not image cleanup. Material/camera-specific reviewed bands; merged/crossing boots abstain.')
