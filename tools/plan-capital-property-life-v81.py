"""Plan larger pierced upper windows and connected owned-path vegetation.

Read-only: seal the current verified v80 source before any native mutation.
New planting stays on private paving, away from entries, uses and public roads.
"""
import json, hashlib, math, runpy, random
from pathlib import Path
from shapely.geometry import Polygon, Point, MultiPoint, LineString
from shapely.ops import unary_union
from shapely import affinity, constrained_delaunay_triangles

R=Path(__file__).resolve().parents[1]
O=R/'docs/review/wayfarer-capital-v81/property-life';O.mkdir(parents=True,exist_ok=True)
raw=(R/'world/v3/wayfarer-spatial.json').read_bytes()
sha=hashlib.sha256(raw).hexdigest()
assert sha=='b999c59228786b93f4f6be9c5836f24cb38e108c7c1bd60000cab11414236f85'
s=json.loads(raw); del raw
layout=json.loads((R/'docs/review/wayfarer-capital-v80/native-plan.json').read_text())
houses=json.loads((R/'docs/review/wayfarer-capital-v80/unique-neighborhoods/plan.json').read_text())['houses']
helper=runpy.run_path(str(R/'tools/capital-neighborhood-proof-v80.py'))
fp,unlit,metadata=helper['fingerprint'],helper['unlit'],helper['metadata']
def face_prefixes(spec):
    names={'stepped-gables':['main-wing','lower-wing'],'garden-cottage':['low-home'],
           'dormered-gambrel':['trade-home'],'corner-oriel':['corner-home']}[spec['design']]
    return ['capital-v80-'+n+'-'+face+'-' for n in names for face in ('front','back','west','east')]
selected={h['id']:h for h in houses}
baseline={'sourceSHA256':sha,'owners':{},'materials':s['materials'],
          'common':fp({k:v for k,v in s.items() if k not in ('objects','materials','lighting')}),
          'lighting':fp({k:v for k,v in s['lighting'].items() if k!='groundShadow'})}
for o in s['objects']:
    entry={'metadata':fp(metadata(o)),'parts':fp([unlit(a) for a in o['parts']])}
    if o['id'] in selected:
        prefixes=face_prefixes(selected[o['id']]);allowed=[a for a in o['parts'] if any(a['id'].startswith(n) for n in prefixes)]
        assert allowed and all(min(v[2] for v in a['vertices'])>3 for a in allowed)
        entry['removedUpperFaces']=[a['id'] for a in allowed]
        entry['retainedParts']={a['id']:fp(unlit(a)) for a in o['parts'] if a not in allowed}
    baseline['owners'][o['id']]=entry
(O/'baseline.json').write_text(json.dumps(baseline,separators=(',',':'))+'\n')
def region(parts):
    return unary_union([Polygon([a['vertices'][i][:2] for i in f]) for a in parts for f in a['faces']])
green=region(next(o for o in s['objects'] if o['id']=='capital-beta-frontage-groundcover')['parts'])
private=region([a for a in s['terrain']['surfaces'] if a['material']=='houseApronPaving' and all(abs(v[2]-.04)<.0001 for v in a['vertices'])])
roads=unary_union([LineString(a['centerline']).buffer(a['width']/2+.15,cap_style=2,join_style=2) for a in layout['roads']])
keep=[]
for o in s['objects']:
    if o['id'] in ('capital-beta-frontage-groundcover','capital-grass-ingress-v76','capital-painted-garden-blades-v79'):continue
    for a in o['parts']:
        if a['role']=='solid':keep.append(MultiPoint([v[:2] for v in a['vertices']]).convex_hull.buffer(.2))
        if a.get('visible',True) and a['material'] not in ('grass','leaf','flowerRose','vergeGroundcover','vergeGroundcoverShade','capitalGrassBladeLight','capitalGrassBladeShade'):
            low=[v[:2] for v in a['vertices'] if v[2]<1.1]
            if len(low)>=3:keep.append(MultiPoint(low).convex_hull.buffer(.14))
    for w in o.get('walkers',[]):
        if len(w['route'])>1:keep.append(LineString(w['route']+[w['route'][0]]).buffer(.45))
    for a in o.get('services',[]):keep.append(Point(a['position'][:2]).buffer(1.2))
    for a in o.get('portals',[]):keep.append(Point(a['anchor'][:2]).buffer(1.2))
owners={o['id']:o for o in s['objects']}
for lot in layout['lots']:
    door=next(a for a in owners[lot['id']]['parts'] if a['id'].endswith('-door-leaf'))
    q=[sum(v[i] for v in door['vertices'])/len(door['vertices']) for i in (0,1)]
    n=(-math.sin(lot['angle']),math.cos(lot['angle']))
    keep.append(LineString([q,[q[i]+n[i]*4.2 for i in (0,1)]]).buffer(1.1,cap_style=2))
keep += [Polygon(a['polygon']).buffer(.25) for a in layout['courtyards']]+[roads]
allowed=private.difference(unary_union(keep))
focus=[('artisan',[68,168],11),('west',[68,201],9),('merchant',[48,165],11),
       ('willow',[153,200],9),('borough',[176,224],9),('south',[108,222],8)]
rng=random.Random(81081);patches=[];occupied=[]
boundary=green.boundary
lines=[boundary] if boundary.geom_type=='LineString' else list(boundary.geoms)
for label,center,radius in focus:
    candidates=[]
    for line in lines:
        if line.distance(Point(center))>radius:continue
        for i in range(max(1,int(line.length/1.2))):
            t=(i+.5)*1.2
            if t>=line.length:continue
            q=line.interpolate(t)
            if q.distance(Point(center))>radius:continue
            a,b=line.interpolate(max(0,t-.15)),line.interpolate(min(line.length,t+.15))
            angle=math.atan2(b.y-a.y,b.x-a.x)
            candidates.append((q.distance(Point(center)),q,angle))
    placed=0
    for _,q,angle in sorted(candidates,key=lambda a:a[0]):
        if placed>=6:break
        if any(q.distance(a)<1.75 for a in occupied):continue
        # A broad, shallow irregular tongue starts inside real green and reaches
        # at most 90cm into the private walking apron. It is never a road decal.
        shape=affinity.scale(Point(0,0).buffer(1,quad_segs=5),1.05+rng.random()*.32,.64+rng.random()*.20)
        shape=affinity.rotate(shape,math.degrees(angle),origin=(0,0))
        shape=affinity.translate(shape,q.x,q.y)
        clipped=shape.intersection(allowed).difference(green.buffer(-.34))
        polys=[clipped] if clipped.geom_type=='Polygon' else [a for a in getattr(clipped,'geoms',[]) if a.geom_type=='Polygon']
        for poly in polys:
            outside=poly.difference(green)
            if outside.area<.12 or outside.area>2 or not poly.intersection(green).area>.1:continue
            if poly.area<.4:continue
            verts=[];faces=[]
            for tri in constrained_delaunay_triangles(poly).geoms:
                pts=list(tri.exterior.coords)[:-1]
                if not tri.exterior.is_ccw:pts.reverse()
                off=len(verts);verts.extend([[x,y,.051] for x,y in pts]);faces.append([off,off+1,off+2])
            patches.append({'id':f'capital-soft-verge-v81-{len(patches):03}','block':label,
                            'vertices':verts,'faces':faces,'material':'grass','area':poly.area,'newArea':outside.area})
            occupied.append(q);placed+=1
            break
assert 12<=len(patches)<=36,len(patches)
feather=runpy.run_path(str(R/'tools/plan-capital-grass-feather-v76.py'))['feather_plan']({'pieces':patches})
for a in feather['pieces']:
    for v in a['vertices']:v[2]=.051
assert feather['triangles']<3500,feather['triangles']
plan={'baselineCommit':'0cc347f','beforeSourceSHA256':sha,'houses':houses,
      'beforeVisibleTriangles':sum(len(f)-2 for o in s['objects'] for a in o['parts'] if a.get('visible',True) for f in a['faces']),
      'removedUpperFacePrefixes':{h['id']:face_prefixes(h) for h in houses},
      'newOwner':'capital-soft-property-verges-v81','pieces':feather['pieces'],
      'patches':len(patches),'newPlantedArea':sum(a['newArea'] for a in patches),
      'grassTriangles':feather['triangles'],'grassTriangleBudget':3500,
      'newMaterials':['frontageGlazingV81','windowIvoryV81'],'newImageAssets':0,
      'newWindowWidthCap':1.65,'newWindowHeightCap':1.65,'entranceClearWidth':2.2,
      'policy':'Actual pierced upper openings, broad pale window frames and quieter blue glazing; connected small grass tongues on owned private path edges only. Original houses, roof forms, entries, services, terrain and all collision unchanged.'}
(O/'plan.json').write_text(json.dumps(plan,separators=(',',':'))+'\n')
print(json.dumps({k:v for k,v in plan.items() if k not in ('pieces','houses','removedUpperFacePrefixes')},indent=2))
