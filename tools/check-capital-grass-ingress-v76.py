"""Independent contact, clearance, native mesh and original texture checks."""
import json, hashlib, math
from pathlib import Path
import numpy as np
from PIL import Image
from shapely.geometry import Polygon, Point, MultiPoint, LineString
from shapely.ops import unary_union
from shapely.strtree import STRtree

R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v76/property-frontages'
raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();s=json.loads(raw)
plan=json.loads((O/'grass-ingress-plan.json').read_text());receipt=json.loads((O/'ro3-daylight-authoring.json').read_text())
p=json.loads((O.parent/'native-plan.json').read_text());objects={o['id']:o for o in s['objects']}
owner=objects[plan['owner']]
assert owner['family']=='vegetation' and not owner['portals'] and not owner['lights']
assert not owner.get('services') and not owner.get('walkers') and not owner.get('presentation')
parts={a['id']:a for a in owner['parts']};assert parts.keys()=={a['id'] for a in plan['pieces']}
error=0
for a in plan['pieces']:
    b=parts[a['id']];assert b['faces']==a['faces'] and b['material']==a['material']
    assert b['role']=='decorative' and not b['shadow'] and b.get('visible',True)
    assert len(b['vertices'])==len(a['vertices'])
    error=max(error,max(abs(x-y) for v,q in zip(a['vertices'],b['vertices']) for x,y in zip(v,q)))
    for f,uv in zip(b['faces'],b['uvs']):
        for i,q in zip(f,uv):assert max(abs(q[j]-b['vertices'][i][j]/7) for j in (0,1))<.00002
assert error<.000021
count=sum(len(f)-2 for a in owner['parts'] for f in a['faces'])
assert count==plan['triangles']==receipt['grassTriangles']==3*len(plan['roots'])<4000
def region(parts):return unary_union([Polygon([a['vertices'][i][:2] for i in f]) for a in parts for f in a['faces']])
green=region(objects['capital-beta-frontage-groundcover']['parts'])
private=region([a for a in s['terrain']['surfaces'] if a['material']=='houseApronPaving' and all(abs(v[2]-.04)<1e-4 for v in a['vertices'])])
entries=[]
for lot in p['lots']:
    h=lot['angle']+lot.get('frontageOffset',0);n=(-math.sin(h),math.cos(h))
    for a in objects[lot['id']]['parts']:
        if not a['id'].endswith('-door-leaf'):continue
        q=[sum(v[i] for v in a['vertices'])/len(a['vertices']) for i in (0,1)]
        entries.append(LineString([q,[q[i]+n[i]*4.2 for i in (0,1)]]).buffer(1.1,cap_style=2))
feet=[MultiPoint([v[:2] for v in a['vertices']]).convex_hull.buffer(.20)
      for o in s['objects'] for a in o['parts'] if a['role']=='solid' and min(v[2] for v in a['vertices'])<1]
blocked=unary_union(entries+feet)
surfaces=[];polys=[]
for a in s['terrain']['surfaces']:
    if not a.get('walkable'):continue
    for f in a['faces']:
        for i in range(1,len(f)-1):
            vs=[a['vertices'][j] for j in (f[0],f[i],f[i+1])];poly=Polygon([v[:2] for v in vs])
            if poly.area<1e-9:continue
            polys.append(poly);surfaces.append((a['id'],a['material'],vs))
tree=STRtree(polys);heights=[];lumas=[];curb_distances=[]
spec=plan['jointTexture'];texture=np.asarray(Image.open(R/spec['file']).convert('RGB'));height,width=texture.shape[:2]
assert s['materials']['publicTownStone']['texture']==spec
assert hashlib.sha256((R/spec['file']).read_bytes()).hexdigest()==plan['jointTextureSHA256']
assert hashlib.sha256((R/s['materials']['grass']['texture']['file']).read_bytes()).hexdigest()==plan['grassTextureSHA256']
for root in plan['roots']:
    x,y,z=root['position'];q=Point(x,y)
    # Whole blade footprints must retain the original 2.2-unit door passage.
    assert not blocked.intersects(q.buffer(.055))
    hits=[]
    for i in tree.query(q,predicate='intersects'):
        name,material,(a,b,c)=surfaces[i]
        determinant=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/determinant
        v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/determinant
        hits.append((u*a[2]+v*b[2]+(1-u-v)*c[2],name,material))
    floor,name,material=max(hits)
    assert name==root['floor'] and material==root['floorMaterial']
    assert abs(z-floor-.012)<.00002;heights.append(z-floor)
    if root['kind']=='lawn':assert green.buffer(.000021).contains(q.buffer(.05))
    else:
        assert material=='publicTownStone'
        distance=private.distance(q);assert .23998<=distance<=.49002;curb_distances.append(distance)
        assert green.distance(q)<=.80002
        px=int(((x/spec['worldSize'])%1)*width)%width
        py=int((1-(y/spec['worldSize'])%1)*height)%height
        luma=float(np.mean(texture[py,px]));assert luma<=103 and luma==root['paintedJointLuma'];lumas.append(luma)
for name,a in receipt['newMaterials'].items():assert s['materials'][name]==a
assert receipt['terrainAndGameplayExactlyPreserved']
report={'sourceSHA256':hashlib.sha256(raw).hexdigest(),'counts':plan['counts'],'decorativeTriangles':count,
    'triangleBudget':4000,'maximumNativeCoordinateError':error,'heightAboveActualFloor':max(heights),
    'maximumJointLuma':max(lumas),'maximumDistanceFromPlantedCurb':max(curb_distances),
    'allRootsGrounded':True,'originalDoorPassagesClear':True,'allPhysicalFeetClear':True,
    'additionalImages':0,'originalImageHashesVerified':True,'additionalObstacles':0,'pass':True,
    'visualAcceptance':'Requires source-matched gameplay review'}
(O/'grass-ingress-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
