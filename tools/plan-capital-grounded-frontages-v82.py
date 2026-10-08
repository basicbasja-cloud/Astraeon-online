"""Seal v81, then plan occupied side facades and economical royal river detail.

Plans use actual saved geometry and planted/private floor, not guessed street
coordinates. This script does not mutate the native scene or current runtime.
"""
import json,hashlib,math,runpy,argparse
from pathlib import Path
from shapely.geometry import Polygon,Point,LineString,MultiPoint
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v82/grounded-frontages'
ap=argparse.ArgumentParser();ap.add_argument('--baseline-commit',required=True);args=ap.parse_args()
seal=json.loads((R/'docs/review/wayfarer-capital-v81/property-life/verified-source.json').read_text())
assert seal['pass']
raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();sha=hashlib.sha256(raw).hexdigest()
assert sha==seal['sourceSHA256'];s=json.loads(raw);del raw
assert hashlib.sha256((R/'authoring/wayfarer-spatial.blend').read_bytes()).hexdigest()==seal['nativeSHA256']
O.mkdir(parents=True,exist_ok=True)
city=json.loads((R/'docs/review/wayfarer-capital-v81/native-plan.json').read_text())
houses=json.loads((R/'docs/review/wayfarer-capital-v81/property-life/plan.json').read_text())['houses']
helpers=runpy.run_path(str(R/'tools/capital-neighborhood-proof-v80.py'))
fp,meta,unlit=helpers['fingerprint'],helpers['metadata'],helpers['unlit']
baseline={'sourceSHA256':sha,'nativeSHA256':seal['nativeSHA256'],'owners':{},
          'materials':s['materials'],'lighting':s['lighting'],
          'common':fp({k:v for k,v in s.items() if k not in ('objects','materials','lighting')})}
for o in s['objects']:
    entry={'metadata':fp(meta(o)),'parts':{a['id']:fp(unlit(a)) for a in o['parts']}}
    if o['id']=='capital-river-bank':
        entry['opaqueBankPartsExceptUV']={a['id']:fp({k:v for k,v in unlit(a).items() if k!='uvs'}) for a in o['parts']}
    baseline['owners'][o['id']]=entry
original_images={m['texture']['file'] for m in s['materials'].values() if m.get('texture')}
baseline['images']={f:hashlib.sha256((R/f).read_bytes()).hexdigest() for f in original_images}
(O/'baseline.json').write_text(json.dumps(baseline,separators=(',',':'))+'\n')
owners={o['id']:o for o in s['objects']};selections=[];rejected=[]
for h in houses:
    c,sn=math.cos(h['angle']),math.sin(h['angle']);cx,cy=h['center'];w,d=h['width'],h['depth']
    def local(v):return [c*(v[0]-cx)+sn*(v[1]-cy),-sn*(v[0]-cx)+c*(v[1]-cy),v[2]-.04]
    locations=[-d*.23,d*.23] if d>5.2 else [0]
    windows=[]
    for y in locations:
        width=1.38;height=1.38;z=1.84
        # The west ground wall is a closed core. New closed glazing sits ahead
        # of it, with real jambs/reveals/sills. Test against actual other props.
        bounds=[(-w/2-.22,-w/2-.012),(y-width/2-.16,y+width/2+.16),(z-height/2-.15,z+height/2+.15)]
        obstruction=[]
        for a in owners[h['id']]['parts']:
            if not a.get('visible',True) or a['role']=='solid' or a['material'] in ('homeLimewash','merchantLimewash','workshopLimewash','stone','stoneLight'):continue
            vs=[local(v) for v in a['vertices']]
            for f in a['faces']:
                pts=[vs[i] for i in f]
                if all(max(v[i] for v in pts)>lo and min(v[i] for v in pts)<hi for i,(lo,hi) in enumerate(bounds)):
                    obstruction.append(a['id']);break
        if obstruction:rejected.append({'id':h['id'],'y':y,'existingUseObstructions':sorted(set(obstruction))});continue
        windows.append({'y':y,'z':z,'width':width,'height':height})
    if windows:selections.append({**h,'westWindows':windows})
assert len(selections)>=8,(len(selections),rejected)

# Grates collect water along actual private walking edges. They are flat
# cosmetic surfaces, not additional obstacles or floor/elevation replacements.
region=lambda parts:unary_union([Polygon([a['vertices'][i][:2] for i in f]) for a in parts for f in a['faces']])
private=region([a for a in s['terrain']['surfaces'] if a['material']=='houseApronPaving' and all(abs(v[2]-.04)<.0001 for v in a['vertices'])])
green=region([a for o in s['objects'] for a in o['parts'] if a['material']=='grass' and a.get('visible',True) and max(v[2] for v in a['vertices'])<.1])
roads=unary_union([LineString(a['centerline']).buffer(a['width']/2+.12,cap_style=2,join_style=2) for a in city['roads']])
keep=[roads,green.buffer(.08)]
for o in s['objects']:
    for a in o['parts']:
        if a['role']=='solid':keep.append(MultiPoint([v[:2] for v in a['vertices']]).convex_hull.buffer(.15))
        if a.get('visible',True) and a['material'] not in ('grass','capitalGrassBladeLight','capitalGrassBladeShade'):
            low=[v[:2] for v in a['vertices'] if v[2]<.9]
            if len(low)>=3:keep.append(MultiPoint(low).convex_hull.buffer(.08))
    for w in o.get('walkers',[]):
        if len(w['route'])>1:keep.append(LineString(w['route']+[w['route'][0]]).buffer(.45))
    for a in o.get('services',[]):keep.append(Point(a['position'][:2]).buffer(1.2))
    for a in o.get('portals',[]):keep.append(Point(a['anchor'][:2]).buffer(1.2))
for l in city['lots']:
    door=next(a for a in owners[l['id']]['parts'] if a['id'].endswith('-door-leaf'))
    q=[sum(v[i] for v in door['vertices'])/len(door['vertices']) for i in (0,1)]
    n=(-math.sin(l['angle']),math.cos(l['angle']))
    keep.append(LineString([q,[q[i]+n[i]*4.2 for i in (0,1)]]).buffer(1.1,cap_style=2))
blocked=unary_union(keep);allowed=private.buffer(-.05).difference(blocked)
focus=[('artisan',[68,168],11),('west',[68,201],10),('merchant',[48,165],11),
       ('willow',[153,200],11),('borough',[176,224],11),('south',[108,222],10)]
drains=[]
for zone,center,radius in focus:
    candidates=[]
    for ix in range(-int(radius*2),int(radius*2)+1):
        for iy in range(-int(radius*2),int(radius*2)+1):
            q=Point(center[0]+ix*.5,center[1]+iy*.5)
            distance=roads.distance(q)
            if not .35<distance<2.4 or not allowed.covers(q.buffer(.53)):continue
            candidates.append((q.distance(Point(center))+.4*distance,q))
    count=0
    for _,q in sorted(candidates,key=lambda a:a[0]):
        if count>=4:break
        if any(q.distance(Point(a['position'][:2]))<3 for a in drains):continue
        nearest=min(city['roads'],key=lambda a:LineString(a['centerline']).distance(q))
        a,b=nearest['centerline'][0],nearest['centerline'][-1];angle=math.atan2(b[1]-a[1],b[0]-a[0])
        drains.append({'id':f'capital-property-grate-v82-{len(drains):02}','zone':zone,'position':[q.x,q.y,.04],'angle':angle,'width':.86,'depth':.54});count+=1
assert 4<=len(drains)<=24,len(drains)
bank=owners['capital-river-bank']['parts']
assert len(bank)==226 and all(len(a['vertices'])==10 for a in bank)
ordered=sorted(bank,key=lambda a:int(a['id'].rsplit('-',1)[-1]));cursor=0;stations=[]
for a in ordered:
    length=math.dist(a['vertices'][0][:2],a['vertices'][1][:2]);assert 0<length<4.1
    stations.append({'id':a['id'],'start':cursor,'length':length});cursor+=length
repeat=cursor/round(cursor/4)
tex=dict(s['materials']['stoneLight']['texture']);tex.update(worldSize=repeat,paletteNative=True,paletteDetail=.58)
plan={'baselineCommit':args.baseline_commit,'beforeSourceSHA256':sha,'beforeNativeSHA256':seal['nativeSHA256'],
      'houses':selections,'rejectedSideWindows':rejected,'drains':drains,
      'drainOwner':'capital-property-drainage-v82','bankOwner':'capital-river-bank','bankStations':stations,
      'bankPhysicalRepeat':repeat,'bankTexture':tex,
      'bankColors':{'bankStone':[.38,.395,.36],'bankStoneLight':[.405,.42,.383]},
      'beforeVisibleTriangles':sum(len(f)-2 for o in s['objects'] for a in o['parts'] if a.get('visible',True) for f in a['faces']),
      'netTriangleBudget':7000,'newImages':0,'newMaterials':0,'entranceClearWidth':2.2,
      'policy':'Occupied closed west-side glazing and timber posts on selected new houses; real path-edge drainage; continuous full-resolution shared city masonry on original river-bank geometry. Preserve all original parts and gameplay except explicitly declared bank UV/material changes.'}
(O/'plan.json').write_text(json.dumps(plan,separators=(',',':'))+'\n')
print(json.dumps({'houses':len(selections),'closedSideWindows':sum(len(a['westWindows']) for a in selections),'drains':len(drains),'bankFaces':sum(len(a['faces']) for a in bank),'bankPhysicalRepeat':repeat,'newImages':0,'newMaterials':0,'rejected':rejected},indent=2))
