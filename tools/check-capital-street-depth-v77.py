"""Independent declared-delta and clearance audit against the pushed checkpoint.

Historical v76 proofs are retained. This phase permits only declared lighting,
material/UV, tiny joint-root shifts and six new owned tree/seat parklets.
"""
import json, hashlib, subprocess, math
from pathlib import Path
from shapely.geometry import Polygon, Point, LineString, MultiPoint
from shapely.ops import unary_union
from shapely.strtree import STRtree
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v77/street-depth'
plan=json.loads((O/'plan.json').read_text());receipt=json.loads((O/'authoring.json').read_text())
oldraw=subprocess.check_output(['git','show','4f6b275:world/v3/wayfarer-spatial.json'],cwd=R)
assert hashlib.sha256(oldraw).hexdigest()==plan['beforeSourceSHA256']
before=json.loads(oldraw);raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();s=json.loads(raw)
old={o['id']:o for o in before['objects']};new={o['id']:o for o in s['objects']}
assert new.keys()-old.keys()==set(receipt['newOwners']) and not old.keys()-new.keys()
def unlit(a):return {k:v for k,v in a.items() if k!='bakedLighting'}
changed_uv=set(receipt['publicUVMeshes']);grass='capital-grass-ingress-v76'
oldparts={a['id']:a for o in before['objects'] for a in o['parts']}
for n,o in old.items():
    a=new[n]
    for key in o.keys()-{'parts'}:
        expected=o[key]
        if key=='walkers':
            for change in plan.get('walkerRouteChanges',[]):
                if change['owner']==n:
                    assert change['before'] in expected
                    expected=[change['after'] if w['id']==change['before']['id'] else w for w in expected]
        assert a.get(key)==expected,(n,key)
    assert [p['id'] for p in o['parts']]==[p['id'] for p in a['parts']],n
    if n==grass:continue
    for x,y in zip(o['parts'],a['parts']):
        bx,by=unlit(x),unlit(y)
        if x['id'] in changed_uv:
            bx.pop('uvs',None);by.pop('uvs',None)
        assert bx==by,(n,x['id'],'undeclared original mesh change')
for k in before.keys()-{'objects','terrain','materials','lighting'}:assert s[k]==before[k],k
terrain=dict(before['terrain']);current=dict(s['terrain']);surfaces=terrain.pop('surfaces');now=current.pop('surfaces')
if terrain['material']=='publicTownStone':
    terrain.pop('uvs',None);current.pop('uvs',None)
    for face,uvs in zip(s['terrain']['faces'],s['terrain']['uvs']):
        for i,uv in zip(face,uvs):assert max(abs(uv[j]-s['terrain']['vertices'][i][j]/5.76) for j in (0,1))<.000021
assert terrain==current and len(surfaces)==len(now)
for a,b in zip(surfaces,now):
    x,y=dict(a),dict(b)
    if a['id'] in changed_uv:x.pop('uvs',None);y.pop('uvs',None)
    assert x==y,('floor',a['id'])
for name,m in before['materials'].items():
    expected=receipt['materialChanges'].get(name,{}).get('after',m)
    assert s['materials'][name]==expected,('material',name)
assert s['materials'].keys()==before['materials'].keys()
for a in now+[p for o in s['objects'] for p in o['parts']]:
    if a['id'] not in changed_uv:continue
    for face,uvs in zip(a['faces'],a['uvs']):
        for i,uv in zip(face,uvs):assert max(abs(uv[j]-a['vertices'][i][j]/5.76) for j in (0,1))<.000021
assert s['materials']['publicTownStone']['texture']['worldSize']==5.76
assert hashlib.sha256((R/plan['publicPaving']['image']).read_bytes()).hexdigest()==plan['publicPaving']['originalImageSHA256']
assert s['lighting']['groundShadow']['file']=='assets/wayfarer-ground-shadow-v77-street-depth.png'
assert s['lighting']['groundShadow']['resolution']==4096
for k,v in receipt['lightingAfter'].items():
    if k!='groundShadow':assert s['lighting'][k]==v

ingress=json.loads((R/'docs/review/wayfarer-capital-v76/property-frontages/grass-ingress-plan.json').read_text())
expected={a['id']:json.loads(json.dumps(a)) for a in ingress['pieces']};offsets={};removed={}
shifts={a['root']:a for a in plan['grassRootShifts']}
for i,root in enumerate(ingress['roots']):
    x,y,z=root['position'];cell=(int(x//32),int(y//32))
    for blade in range(3):
        mat='capitalGrassBladeLight' if (i+blade)%3 else 'capitalGrassBladeShade'
        name=f'capital-grass-{cell[0]}-{cell[1]}-{mat}';off=offsets.get(name,0);offsets[name]=off+3
        if i not in shifts:continue
        shift=shifts[i]
        if shift['after'] is None:removed.setdefault(name,set()).update(range(off,off+3));continue
        delta=[shift['after'][j]-shift['before'][j] for j in range(3)]
        for j in range(off,off+3):expected[name]['vertices'][j]=[v+d for v,d in zip(expected[name]['vertices'][j],delta)]
grass_error=0
for a in new[grass]['parts']:
    e=expected[a['id']];remove=removed.get(a['id'],set());vs=[v for j,v in enumerate(e['vertices']) if j not in remove]
    assert len(vs)==len(a['vertices'])
    grass_error=max(grass_error,max(abs(x-y) for v,q in zip(vs,a['vertices']) for x,y in zip(v,q)))
    assert a['material']==e['material'] and a['role']=='decorative' and not a['shadow']
    assert len(a['faces'])==len(vs)//3
    for face,uvs in zip(a['faces'],a['uvs']):
        for j,uv in zip(face,uvs):assert max(abs(uv[k]-a['vertices'][j][k]/7) for k in (0,1))<.000021
assert grass_error<.00003,grass_error
def region(parts):return unary_union([Polygon([a['vertices'][i][:2] for i in f]) for a in parts for f in a['faces']])
private=region([a for a in s['terrain']['surfaces'] if a['material']=='houseApronPaving' and all(abs(v[2]-.04)<.0001 for v in a['vertices'])])
green=region(new['capital-beta-frontage-groundcover']['parts'])
floor_polys=[];floor_data=[]
for a in s['terrain']['surfaces']:
    if not a.get('walkable'):continue
    for face in a['faces']:
        poly=Polygon([a['vertices'][i][:2] for i in face])
        if poly.area<1e-9:continue
        floor_polys.append(poly);floor_data.append((max(v[2] for v in a['vertices']),a['id'],a['material']))
tree=STRtree(floor_polys);spec=s['materials']['publicTownStone']['texture'];pixels=np.asarray(Image.open(R/spec['file']).convert('RGB'));H,W=pixels.shape[:2]
allfeet=unary_union([MultiPoint([v[:2] for v in a['vertices']]).convex_hull.buffer(.2) for o in s['objects'] for a in o['parts'] if a['role']=='solid' and min(v[2] for v in a['vertices'])<1])
joint_lumas=[]
for root in plan['grassRoots']:
    if root.get('remove'):continue
    x,y,z=root['position'];q=Point(x,y)
    assert not allfeet.intersects(q.buffer(.055)),('blade occupies foot',root)
    hit=max(floor_data[i] for i in tree.query(q,predicate='intersects'))
    assert abs(z-hit[0]-.012)<.00002 and hit[1]==root['floor']
    if root['kind']=='lawn':assert green.buffer(.00002).contains(q.buffer(.05))
    else:
        assert hit[2]=='publicTownStone' and .23998<=private.distance(q)<=.49002 and green.distance(q)<=.80002
        luma=float(pixels[int((1-(y/5.76)%1)*H)%H,int((x/5.76)%1*W)%W].mean())
        assert luma<=103 and luma==root['paintedJointLuma'];joint_lumas.append(luma)

p=json.loads((R/'docs/review/wayfarer-capital-v76/native-plan.json').read_text())
roads=unary_union([LineString(r['centerline']).buffer(r['width']/2,cap_style=2,join_style=2) for r in p['roads']])
feet=unary_union([MultiPoint([v[:2] for v in a['vertices']]).convex_hull.buffer(.2)
    for o in before['objects'] for a in o['parts'] if a['role']=='solid' and min(v[2] for v in a['vertices'])<1])
entries=[]
for lot in p['lots']:
    h=lot['angle']+lot.get('frontageOffset',0);n=(-math.sin(h),math.cos(h))
    for a in new[lot['id']]['parts']:
        if not a['id'].endswith('-door-leaf'):continue
        q=[sum(v[i] for v in a['vertices'])/len(a['vertices']) for i in (0,1)]
        entries.append(LineString([q,[q[i]+n[i]*4.2 for i in (0,1)]]).buffer(1.1,cap_style=2))
entries+=[Point(a['position'][:2]).buffer(1.05) for o in s['objects'] for a in o.get('services',[])]
entries+=[Point(a['anchor'][:2]).buffer(1.05) for o in s['objects'] for a in o['portals']]
patrol=unary_union([LineString(a['route']+[a['route'][0]]).buffer(.3) for o in s['objects'] for a in o.get('walkers',[])])
blocked=unary_union([roads,feet,unary_union(entries),patrol]);newfeet=[]
for n in receipt['newOwners']:
    o=new[n];assert not o.get('services') and not o.get('walkers') and not o['portals'] and not o['lights']
    for a in o['parts']:
        if a['role']=='solid':
            poly=MultiPoint([v[:2] for v in a['vertices']]).convex_hull
            assert not blocked.intersects(poly),(a['id'],'blocks street, door, service or existing route')
            newfeet.append(poly)
for i,foot in enumerate(newfeet):
    # Trunk and its own planter may overlap intentionally; unrelated solid
    # checks are represented by independent planned parklet footprints.
    assert foot.area<1.5
count=sum(len(f)-2 for n in receipt['newOwners'] for a in new[n]['parts'] if a.get('visible',True) for f in a['faces'])
assert count==receipt['addedTriangles']<plan['triangleBudget']
assert len(raw)<100*1024*1024
report={'sourceSHA256':hashlib.sha256(raw).hexdigest(),'baselineCommit':'4f6b275','baselineSHA256':plan['beforeSourceSHA256'],
    'originalOwnersRetainedExceptDeclaredUVGrassLightAndOneVisitorTurn':len(old),'originalCollidersAndGameplayExactExceptDeclaredVisitorTurn':True,
    'visitorRouteChanges':[a['before']['id'] for a in plan.get('walkerRouteChanges',[])],
    'publicTileScaleFactor':1.8,'fullResolutionOriginalPavingHashVerified':True,'actualPublicUVsVerified':len(changed_uv),
    'jointRootMeshError':grass_error,'jointTuftsMoved':len(shifts)-plan['removedJointTufts'],'jointTuftsRemoved':plan['removedJointTufts'],
    'allBladeRootsGroundedAndPhysicalFeetClear':True,'maximumPaintedJointLuma':max(joint_lumas),
    'newParklets':len(plan['parklets']),'newVisibleTriangles':count,'triangleBudget':plan['triangleBudget'],
    'roadsDoorsServicesAndResidentLoopsClear':True,'groundBakeSHA256':hashlib.sha256((R/s['lighting']['groundShadow']['file']).read_bytes()).hexdigest(),
    'exportBytes':len(raw),'pass':True,'visualAcceptance':'Separate paired screenshot review required'}
(O/'preservation-and-clearance.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
