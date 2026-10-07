"""Bounded RO3 street-depth candidate against the actual saved capital.

Only placed parklets and the original texture's paving frequency change.
Doors, public road widths, services and all existing resident loops are guards.
"""
import json, hashlib, math, random
from pathlib import Path
import numpy as np
from PIL import Image
from shapely.geometry import Polygon, MultiPoint, Point, LineString
from shapely.ops import unary_union

R=Path(__file__).resolve().parents[1]; O=R/'docs/review/wayfarer-capital-v77/street-depth'
O.mkdir(parents=True,exist_ok=True)
raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();s=json.loads(raw)
assert hashlib.sha256(raw).hexdigest()=='1a4efa50e8cb607bb40d4c15d12d834131b8cd7ca6ed699858ce5826b2afb771'
p=json.loads((R/'docs/review/wayfarer-capital-v76/native-plan.json').read_text())
objects={o['id']:o for o in s['objects']}
def region(parts):
    return unary_union([Polygon([a['vertices'][i][:2] for i in f]) for a in parts for f in a['faces'] if len(f)>=3])
green=region(objects['capital-beta-frontage-groundcover']['parts'])
roads=unary_union([LineString(a['centerline']).buffer(a['width']/2+.35,cap_style=2,join_style=2) for a in p['roads']])
feet=unary_union([MultiPoint([v[:2] for v in a['vertices']]).convex_hull.buffer(.45)
    for o in s['objects'] for a in o['parts'] if a['role']=='solid' and min(v[2] for v in a['vertices'])<1])
entries=[]
for l in p['lots']:
    h=l['angle']+l.get('frontageOffset',0);n=(-math.sin(h),math.cos(h))
    for a in objects[l['id']]['parts']:
        if not a['id'].endswith('-door-leaf'):continue
        q=[sum(v[i] for v in a['vertices'])/len(a['vertices']) for i in (0,1)]
        entries.append(LineString([q,[q[i]+n[i]*4.2 for i in (0,1)]]).buffer(1.1,cap_style=2))
entries+= [Point(a['position'][:2]).buffer(1.5) for o in s['objects'] for a in o.get('services',[])]
entries+= [Point(a['anchor'][:2]).buffer(1.5) for o in s['objects'] for a in o['portals']]
patrols=unary_union([LineString(w['route']+[w['route'][0]]).buffer(.5) for o in s['objects'] for w in o.get('walkers',[]) if len(w['route'])>1])
clear=unary_union([roads,feet,unary_union(entries),patrols,green.buffer(.24)])
floors=[(Polygon([a['vertices'][i][:2] for i in f]),a) for a in s['terrain']['surfaces'] if a.get('walkable') for f in a['faces']]
def support(q):
    hits=[(max(v[2] for v in a['vertices']),a['id'],a['material']) for poly,a in floors if poly.covers(q)]
    return max(hits) if hits else None
occupied=[];parklets=[]
desired=[('plaza-northwest',119.0,130.0),('plaza-northeast',137.0,130.0),
    ('plaza-southwest',119.0,158.0),('plaza-southeast',137.0,158.0),
    ('west-neighborhood-north',74.6,197.0),('west-neighborhood-south',85.4,204.0)]
for name,x,y in desired:
    choices=[Point(x+dx*.3,y+dy*.3) for dx in range(-22,23) for dy in range(-22,23)]
    choices.sort(key=lambda q:q.distance(Point(x,y)))
    for q in choices:
        hit=support(q)
        if not hit or hit[0]>.06 or hit[2] not in ('publicTownStone','houseApronPaving'):continue
        footprint=q.buffer(.55,resolution=8)
        if clear.intersects(footprint) or any(g.distance(q)<4 for g in occupied):continue
        # A seat is paired with each tree. Try four headings, retaining a clear
        # passage around the seat rather than occupying the ceremonial roads.
        for angle in (0,math.pi/2,math.pi,3*math.pi/2):
            c=Point(q.x+math.sin(angle)*1.05,q.y-math.cos(angle)*1.05)
            footprint2=Polygon([(c.x+math.cos(angle)*u-math.sin(angle)*v,c.y+math.sin(angle)*u+math.cos(angle)*v)
                for u,v in [(-1.0,-.36),(1.0,-.36),(1.0,.36),(-1.0,.36)]]).buffer(.2)
            if clear.intersects(footprint2) or not support(c):continue
            parklets.append({'id':name,'position':[q.x,q.y,hit[0]],'floor':hit[1],
                'benchPosition':[c.x,c.y,hit[0]],'benchAngle':angle,'height':5.7+(len(parklets)%3)*.35,
                'treeRotation':len(parklets)*.67,'planterRadius':.52})
            occupied.append(q);break
        else:continue
        break
    else:raise AssertionError(('No clear parklet position',name))

# Retarget only the 400 existing street-joint blades to the enlarged painted
# joints. Root count, curb ownership and tiny blade dimensions are preserved.
old=json.loads((R/'docs/review/wayfarer-capital-v76/property-frontages/grass-ingress-plan.json').read_text())
spec=s['materials']['publicTownStone']['texture'];size=5.76
px=np.asarray(Image.open(R/spec['file']).convert('RGB'));lum=px.mean(axis=2);H,W=lum.shape
private=region([a for a in s['terrain']['surfaces'] if a['material']=='houseApronPaving' and all(abs(v[2]-.04)<.0001 for v in a['vertices'])])
seam=lambda q:float(lum[int((1-(q.y/size)%1)*H)%H,int((q.x/size)%1*W)%W])
blocked=unary_union([feet,unary_union(entries),patrols]+[q.buffer(.8) for q in occupied])
shifts=[];roots=[]
for index,a in enumerate(old['roots']):
    x,y,z=a['position']
    if a['kind']=='lawn':roots.append(a);continue
    q=Point(x,y)
    candidates=[Point(x+dx*.025,y+dy*.025) for dx in range(-16,17) for dy in range(-16,17)]
    candidates.sort(key=lambda t:(seam(t)>103,t.distance(q)))
    for t in candidates:
        if seam(t)>103 or blocked.intersects(t.buffer(.055)):continue
        d=private.distance(t)
        if not .24<=d<=.49 or green.distance(t)>.8:continue
        hit=support(t)
        if not hit or hit[2]!='publicTownStone':continue
        shifts.append({'root':index,'before':a['position'],'after':[t.x,t.y,hit[0]+.012],'paintedJointLuma':seam(t)})
        roots.append({**a,'position':[t.x,t.y,hit[0]+.012],'paintedJointLuma':seam(t),'floor':hit[1]});break
    else:
        # Some narrow patches have no enlarged joint nearby. Keep the blade
        # at the planted edge and record this honestly, rather than on a stone.
        shifts.append({'root':index,'before':a['position'],'after':None})
        roots.append({**a,'remove':True})
assert len(parklets)==6 and len(shifts)==400
report={'beforeSourceSHA256':hashlib.sha256(raw).hexdigest(),'baselineCommit':'4f6b275',
    'publicPaving':{'worldSizeBefore':spec['worldSize'],'worldSizeAfter':size,'stoneScaleFactor':size/spec['worldSize'],
        'detailBefore':spec['paletteDetail'],'detailAfter':.58,'image':spec['file'],
        'originalImageSHA256':hashlib.sha256((R/spec['file']).read_bytes()).hexdigest()},
    'parklets':parklets,'grassRootShifts':shifts,'grassRoots':roots,
    'removedJointTufts':sum(a['after'] is None for a in shifts),'entranceClearWidth':2.2,
    'additionalTextures':0,'triangleBudget':7000,'visualAcceptance':'Pending paired gameplay comparisons'}
(O/'plan.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('grassRootShifts','grassRoots')},indent=2))
