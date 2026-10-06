"""Plan curb intervals outside the complete native public path footprints.

Works on exported native coordinates; no external geometry dependencies.
"""
import math

def public_surfaces(world):
    return [s for s in world['terrain']['surfaces'] if s.get('visible',True) and s['walkable'] and (
        (s.get('centerline') and s.get('width',0)>=1.8) or s['material']=='publicSquareStone' or
        (s['role']=='forecourt' and ('stair' in s['id'] or 'processional' in s['id'] or 'landing' in s['id'] or s['id'] in ('civic-terrace','terrace-v49-upper-civic-floor'))))]

def clip_halfplane(poly,value,greater):
    if not poly:return []
    result=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        aa=a[1]>=value if greater else a[1]<=value
        bb=b[1]>=value if greater else b[1]<=value
        if aa:result.append(a)
        if aa!=bb:
            t=(value-a[1])/(b[1]-a[1]);result.append((a[0]+t*(b[0]-a[0]),value))
    return result

def outside_intervals(a,b,normal,width,polygons,clearance=.008):
    length=math.dist(a[:2],b[:2]);t=((b[0]-a[0])/length,(b[1]-a[1])/length);blocked=[]
    for poly in polygons:
        points=[((p[0]-a[0])*t[0]+(p[1]-a[1])*t[1],(p[0]-a[0])*normal[0]+(p[1]-a[1])*normal[1]) for p in poly]
        points=clip_halfplane(clip_halfplane(points,-clearance,True),width+clearance,False)
        if not points:continue
        lo=max(0,min(p[0] for p in points)-clearance);hi=min(length,max(p[0] for p in points)+clearance)
        if hi>lo:blocked.append((lo,hi))
    merged=[]
    for lo,hi in sorted(blocked):
        if merged and lo<=merged[-1][1]:merged[-1]=(merged[-1][0],max(merged[-1][1],hi))
        else:merged.append((lo,hi))
    result=[];start=0
    for lo,hi in merged:
        if lo>start:result.append((start,lo))
        start=max(start,hi)
    if start<length:result.append((start,length))
    return result
