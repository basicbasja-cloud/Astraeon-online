"""Independently verify v82 additions, exact old parts and continuous bank UVs."""
import json,hashlib,runpy,math,argparse
from pathlib import Path
from shapely.geometry import Polygon,Point,LineString,MultiPoint
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v82/grounded-frontages'
ap=argparse.ArgumentParser();ap.add_argument('--pending-light',action='store_true');args=ap.parse_args()
p=json.loads((O/'plan.json').read_text());base=json.loads((O/'baseline.json').read_text())
receipt=json.loads((O/'authoring.json').read_text());city=json.loads((O.parent/'native-plan.json').read_text())
helper=runpy.run_path(str(R/'tools/capital-neighborhood-proof-v80.py'))
fp,unlit,meta=helper['fingerprint'],helper['unlit'],helper['metadata']
raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();sha=hashlib.sha256(raw).hexdigest();s=json.loads(raw);del raw
now={o['id']:o for o in s['objects']};chosen={h['id']:h for h in p['houses']}
assert set(now)-set(base['owners'])=={p['drainOwner']} and not set(base['owners'])-set(now)
retained=0
for name,entry in base['owners'].items():
    o=now[name];assert fp(meta(o))==entry['metadata'],(name,'gameplay changed')
    parts={a['id']:a for a in o['parts']}
    assert set(entry['parts'])<=set(parts),(name,'old part missing')
    for n,digest in entry['parts'].items():
        if name==p['bankOwner']:
            assert fp({k:v for k,v in unlit(parts[n]).items() if k!='uvs'})==entry['opaqueBankPartsExceptUV'][n],n
        else:assert fp(unlit(parts[n]))==digest,(name,n,'old geometry/UV/material changed')
        retained+=1
    if name not in chosen:assert set(parts)==set(entry['parts']),name
    else:assert all(n in entry['parts'] or n.startswith('capital-v82-') for n in parts),name
assert fp({k:v for k,v in s.items() if k not in ('objects','materials','lighting')})==base['common']
assert {k:v for k,v in s['lighting'].items() if k!='groundShadow'}=={k:v for k,v in base['lighting'].items() if k!='groundShadow'}
if not args.pending_light:
    assert s['lighting']['groundShadow']['file']=='assets/wayfarer-ground-shadow-v82-grounded-frontages.png'
    assert s['lighting']['groundShadow']['resolution']==4096
assert set(s['materials'])==set(base['materials'])
for name,value in base['materials'].items():
    if name not in p['bankColors']:assert s['materials'][name]==value,name
    else:
        assert s['materials'][name]['texture']==p['bankTexture']
        assert all(abs(a-b)<.000001 for a,b in zip(s['materials'][name]['color'],p['bankColors'][name]))
for image,digest in base['images'].items():assert hashlib.sha256((R/image).read_bytes()).hexdigest()==digest,image
assert {m['texture']['file'] for m in s['materials'].values() if m.get('texture')}<=set(base['images'])

windows=[]
for name,h in chosen.items():
    ca,sa=math.cos(h['angle']),math.sin(h['angle']);cx,cy=h['center']
    def local(v):return [ca*(v[0]-cx)+sa*(v[1]-cy),-sa*(v[0]-cx)+ca*(v[1]-cy),v[2]-.04]
    glass=[a for a in now[name]['parts'] if a['id'].startswith('capital-v82-') and a['material']=='frontageGlazingV81']
    assert len(glass)==len(h['westWindows'])
    for a in glass:
        vs=[local(v) for v in a['vertices']]
        assert max(v[0] for v in vs)<-h['width']/2-.015,(name,'closed glass buried in retained wall core')
        center=[sum(v[i] for v in vs)/len(vs) for i in (1,2)]
        spec=min(h['westWindows'],key=lambda a:abs(a['y']-center[0]))
        assert abs(center[0]-spec['y'])<.0001 and abs(center[1]-spec['z'])<.0001
        assert abs(max(v[1] for v in vs)-min(v[1] for v in vs)-(spec['width']-.18))<.00015
        assert abs(max(v[2] for v in vs)-min(v[2] for v in vs)-(spec['height']-.18))<.00015
        windows.append({'owner':name,'groundWestClosedGlazingExposed':True,'width':spec['width'],'height':spec['height']})

bank={a['id']:a for a in now[p['bankOwner']]['parts']};bank_corners=0
for station in p['bankStations']:
    a=bank[station['id']]
    for f,uvs in zip(a['faces'],a['uvs']):
        for index,uv in zip(f,uvs):
            expected=[(station['start']+station['length']*(index%2))/p['bankPhysicalRepeat'],a['vertices'][index][2]/p['bankPhysicalRepeat']]
            assert max(abs(x-y) for x,y in zip(uv,expected))<.00004,(a['id'],'bank UV continuity')
            bank_corners+=1
perimeter=sum(a['length'] for a in p['bankStations'])
assert abs(perimeter/p['bankPhysicalRepeat']-round(perimeter/p['bankPhysicalRepeat']))<.000001

region=lambda parts:unary_union([Polygon([a['vertices'][i][:2] for i in f]) for a in parts for f in a['faces']])
private=region([a for a in s['terrain']['surfaces'] if a['material']=='houseApronPaving' and all(abs(v[2]-.04)<.0001 for v in a['vertices'])])
green=region([a for o in s['objects'] for a in o['parts'] if a['material']=='grass' and a.get('visible',True) and max(v[2] for v in a['vertices'])<.1])
roads=unary_union([LineString(a['centerline']).buffer(a['width']/2+.12,cap_style=2,join_style=2) for a in city['roads']])
keep=[roads,green]
for o in s['objects']:
    for a in o['parts']:
        if a['role']=='solid':keep.append(MultiPoint([v[:2] for v in a['vertices']]).convex_hull.buffer(.14))
    for w in o.get('walkers',[]):
        if len(w['route'])>1:keep.append(LineString(w['route']+[w['route'][0]]).buffer(.44))
    for a in o.get('services',[]):keep.append(Point(a['position'][:2]).buffer(1.2))
    for a in o.get('portals',[]):keep.append(Point(a['anchor'][:2]).buffer(1.2))
for l in city['lots']:
    door=next(a for a in now[l['id']]['parts'] if a['id'].endswith('-door-leaf'))
    q=[sum(v[i] for v in door['vertices'])/len(door['vertices']) for i in (0,1)];n=(-math.sin(l['angle']),math.cos(l['angle']))
    keep.append(LineString([q,[q[i]+n[i]*4.2 for i in (0,1)]]).buffer(1.1,cap_style=2))
blocked=unary_union(keep);drainproof=[];drainowner=now[p['drainOwner']]
assert len(drainowner['parts'])==len(p['drains'])*10
for a in p['drains']:
    parts=[q for q in drainowner['parts'] if q['id'].startswith('capital-v82-'+a['id']+'-')]
    assert len(parts)==10 and all(not q['shadow'] and q['role']=='decorative' for q in parts)
    footprint=region(parts)
    assert footprint.difference(private).area<.00001 and footprint.intersection(blocked).area<.00001,a['id']
    assert all(.04<v[2]<.056 for q in parts for v in q['vertices'])
    drainproof.append({'id':a['id'],'actualOwnedPath':True,'greenPublicStreetsDoorsPatrolsClear':True,'noNewCollisionOrElevation':True})
report={'sourceSHA256':sha,'pass':True,'lightingVerified':not args.pending_light,
        'baselineCommit':p['baselineCommit'],'retainedOriginalParts':retained,
        'originalCoreRoofDoorsTerrainNavigationGameplayExact':True,'bankVerticesFacesNormalsAndPhysicalGeometryExact':True,
        'bankContinuousUVCorners':bank_corners,'bankPhysicalRepeat':p['bankPhysicalRepeat'],
        'closedGroundSideWindows':windows,'drains':drainproof,'newImages':0,'newMaterials':0,
        'originalImageBytesAndResolutionExact':True,'netAddedVisibleTriangles':receipt['netAddedVisibleTriangles'],
        'visualAcceptance':'Requires actual source-matched gameplay review'}
(O/('geometry-candidate.json' if args.pending_light else 'declared-delta.json')).write_text(json.dumps(report,indent=2)+'\n')
print('PASS v82 retained',retained,'old parts;',len(windows),'exposed closed side windows;',len(drainproof),'clear drains;',bank_corners,'continuous bank corners')
