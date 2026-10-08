"""Verify the sealed v80 delta, real window apertures and connected grass."""
import json,hashlib,math,runpy,argparse
from pathlib import Path
from shapely.geometry import Polygon,Point,LineString,MultiPoint,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v81/property-life'
ap=argparse.ArgumentParser();ap.add_argument('--pending-light',action='store_true');args=ap.parse_args()
p=json.loads((O/'plan.json').read_text());base=json.loads((O/'baseline.json').read_text())
receipt=json.loads((O/'authoring.json').read_text());layout=json.loads((O.parent/'native-plan.json').read_text())
helper=runpy.run_path(str(R/'tools/capital-neighborhood-proof-v80.py'))
fp,unlit,metadata=helper['fingerprint'],helper['unlit'],helper['metadata']
raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();s=json.loads(raw)
sha=hashlib.sha256(raw).hexdigest();del raw
now={o['id']:o for o in s['objects']};selected={h['id']:h for h in p['houses']}
assert set(now)-set(base['owners'])=={p['newOwner']} and not set(base['owners'])-set(now)
retained=0
for name,b in base['owners'].items():
    o=now[name];assert fp(metadata(o))==b['metadata'],(name,'owner gameplay changed')
    if name not in selected:assert fp([unlit(a) for a in o['parts']])==b['parts'],(name,'undeclared geometry change')
    else:
        parts={a['id']:a for a in o['parts']}
        assert not set(b['removedUpperFaces'])&set(parts),(name,'old wall faces remain')
        for n,digest in b['retainedParts'].items():assert fp(unlit(parts[n]))==digest,(name,n,'old roof/ground/use/solid changed')
        assert all(n in b['retainedParts'] or n.startswith('capital-v81-') for n in parts)
        retained+=len(b['retainedParts'])
assert set(s['materials'])-set(base['materials'])==set(p['newMaterials'])
assert all(s['materials'][k]==v for k,v in base['materials'].items())
assert fp({k:v for k,v in s.items() if k not in ('objects','materials','lighting')})==base['common']
assert fp({k:v for k,v in s['lighting'].items() if k!='groundShadow'})==base['lighting']
if not args.pending_light:
    assert s['lighting']['groundShadow']['resolution']==4096
    assert s['lighting']['groundShadow']['file']=='assets/wayfarer-ground-shadow-v81-property-life.png'
original_images={m['texture']['file'] for m in base['materials'].values() if m.get('texture')}
assert {m['texture']['file'] for m in s['materials'].values() if m.get('texture')}==original_images

windows=[]
for h in p['houses']:
    c,sn=math.cos(h['angle']),math.sin(h['angle']);cx,cy=h['center']
    def local(v):return [c*(v[0]-cx)+sn*(v[1]-cy),-sn*(v[0]-cx)+c*(v[1]-cy),v[2]-.04]
    specs=next(a for a in receipt['houses'] if a['id']==h['id'])['faces']
    for spec in specs:
        prefix='capital-v81-'+spec['wing']+'-'+spec['face']+'-'
        parts=[a for a in now[h['id']]['parts'] if a['id'].startswith(prefix)]
        glass=[a for a in parts if a['material']=='frontageGlazingV81']
        assert len(glass)==spec['bays'],(h['id'],prefix,'missing glazing')
        angle={'front':0,'back':math.pi,'west':math.pi/2,'east':-math.pi/2}[spec['face']]
        ca,sa=math.cos(angle),math.sin(angle)
        def plane(v):
            q=local(v);return [ca*q[0]+sa*q[1],q[2]]
        walls=[MultiPoint([plane(v) for v in a['vertices']]).convex_hull for a in parts if a['material'] in ('homeLimewash','merchantLimewash','workshopLimewash')]
        wall=unary_union(walls)
        for a in glass:
            vs=[plane(v) for v in a['vertices']];aperture=MultiPoint(vs).convex_hull
            width=aperture.bounds[2]-aperture.bounds[0];height=aperture.bounds[3]-aperture.bounds[1]
            assert abs(width-(spec['windowWidth']-.18))<.00015,(a['id'],'glass width')
            assert abs(height-(spec['windowHeight']-.18))<.00015,(a['id'],'glass height')
            assert aperture.intersection(wall).area<.00001,(a['id'],'glass covered by wall')
            windows.append({'owner':h['id'],'face':spec['wing']+'-'+spec['face'],'openingWidth':spec['windowWidth'],'openingHeight':spec['windowHeight'],'actualWallOpeningClear':True})

region=lambda parts:unary_union([Polygon([a['vertices'][i][:2] for i in f]) for a in parts for f in a['faces']])
green=region(now['capital-beta-frontage-groundcover']['parts'])
private=region([a for a in s['terrain']['surfaces'] if a['material']=='houseApronPaving' and all(abs(v[2]-.04)<.0001 for v in a['vertices'])])
roads=unary_union([LineString(a['centerline']).buffer(a['width']/2+.12,cap_style=2,join_style=2) for a in layout['roads']])
keep=[roads]
for o in now.values():
    for a in o['parts']:
        if a['role']=='solid':keep.append(MultiPoint([v[:2] for v in a['vertices']]).convex_hull.buffer(.18))
    for w in o.get('walkers',[]):
        if len(w['route'])>1:keep.append(LineString(w['route']+[w['route'][0]]).buffer(.44))
    for a in o.get('services',[]):keep.append(Point(a['position'][:2]).buffer(1.2))
    for a in o.get('portals',[]):keep.append(Point(a['anchor'][:2]).buffer(1.2))
for l in layout['lots']:
    door=next(a for a in now[l['id']]['parts'] if a['id'].endswith('-door-leaf'))
    dc=[sum(v[i] for v in door['vertices'])/len(door['vertices']) for i in (0,1)]
    n=(-math.sin(l['angle']),math.cos(l['angle']))
    keep.append(LineString([dc,[dc[i]+n[i]*4.2 for i in (0,1)]]).buffer(1.1,cap_style=2))
blocked=unary_union(keep);patchproof=[]
parts={a['id']:a for a in now[p['newOwner']]['parts']};assert len(parts)==p['patches']
for spec in p['pieces']:
    a=parts[spec['id']];q=region([a]);expected=region([spec])
    assert q.symmetric_difference(expected).area<.0001
    assert q.difference(private).area<.0001 and q.intersection(blocked).area<.0001,a['id']
    assert q.intersection(green).area>.09 and q.difference(green).area>.1,a['id']
    assert all(abs(v[2]-.051)<.000001 for v in a['vertices'])
    assert len(a['vertexOpacity'])==len(a['vertices']) and min(a['vertexOpacity'])<.001 and max(a['vertexOpacity'])>.99
    patchproof.append({'id':a['id'],'connectedToExistingGreen':True,'onOwnedPrivatePath':True,'doorsPublicStreetsPatrolsClear':True,'addedPlantedArea':q.difference(green).area})
report={'sourceSHA256':sha,'pass':True,'lightingVerified':not args.pending_light,
        'baselineCommit':p['baselineCommit'],'originalOwnersExactOutsideDeclaredUpperWallFaces':True,
        'retainedPartsInSelectedHouses':retained,'originalRoofFormsGroundUsesDoorsSolidsTerrainNavigationGameplayExact':True,
        'originalMaterialDefinitionsAndImageAssetsExact':True,'newImageAssets':0,
        'actualPiercedWindowOpenings':windows,'connectedPropertyPatches':patchproof,
        'newPlantedArea':sum(a['addedPlantedArea'] for a in patchproof),'netAddedVisibleTriangles':receipt['netAddedVisibleTriangles'],
        'visualAcceptance':'Requires normal paired gameplay review'}
(O/('geometry-candidate.json' if args.pending_light else 'declared-delta.json')).write_text(json.dumps(report,indent=2)+'\n')
print('PASS v81 preservation:',len(windows),'pierced windows,',len(patchproof),'connected owned green patches; lighting',not args.pending_light)
