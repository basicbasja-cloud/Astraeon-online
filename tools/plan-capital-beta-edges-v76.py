"""Derive planted frontage bands from actual owned paving and clear entrances."""
import json,hashlib,math,runpy
from pathlib import Path
from shapely.geometry import Polygon,MultiPoint,LineString
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v76'
raw=(R/'world/v3/wayfarer-spatial.json').read_bytes();s=json.loads(raw)
p=json.loads((O/'native-plan.json').read_text());assert not p.get('betaReferenceRefinement')
objects={o['id']:o for o in s['objects']}
def region(arr):
    return unary_union([Polygon([a['vertices'][i][:2] for i in f]) for a in arr for f in a['faces']])
private=region([a for a in s['terrain']['surfaces'] if a['material']=='houseApronPaving' and all(abs(v[2]-.04)<1e-4 for v in a['vertices'])])
roads=unary_union([LineString(a['centerline']).buffer(a['width']/2+.12,cap_style=2,join_style=2) for a in p['roads']])
solids=[];props=[];entries=[]
for o in s['objects']:
    for part in o['parts']:
        vs=part['vertices']
        if part['role']=='solid' and min(v[2] for v in vs)<1:
            solids.append(MultiPoint([v[:2] for v in vs]).convex_hull.buffer(.18))
        if part.get('visible',True) and part['material'] not in ('grass','leaf','flowerRose','vergeGroundcover','vergeGroundcoverShade'):
            low=[v[:2] for v in vs if v[2]<.85]
            if len(low)>=3:props.append(MultiPoint(low).convex_hull.buffer(.08))
for l in p['lots']:
    angle=l['angle']+l.get('frontageOffset',0);normal=(-math.sin(angle),math.cos(angle))
    doors=[a for a in objects[l['id']]['parts'] if 'door' in a['id'] and 'leaf' in a['id']]
    for a in doors:
        center=[sum(v[i] for v in a['vertices'])/len(a['vertices']) for i in (0,1)]
        entries.append(LineString([center,[center[i]+normal[i]*3.8 for i in (0,1)]]).buffer(1.0,cap_style=2))
courts=[Polygon(c['polygon']).buffer(.25) for c in p.get('courtyards',[])]
keepout=unary_union(solids+props+entries+courts+[roads])
pieces=[]
for index,b in enumerate(p['ownedBlocks']):
    block=Polygon(b['outer'],b['holes']);center=block.centroid
    if not (45<center.x<211 and 80<center.y<244):continue
    # A continuous band belongs to the shared block, with gaps only for real
    # entrances/obstacles. No individual grass pads are scattered in roads.
    band=block.buffer(-.18,join_style=2).difference(block.buffer(-.95,join_style=2))
    available=band.intersection(private).difference(keepout)
    for q in ([available] if available.geom_type=='Polygon' else getattr(available,'geoms',[])):
        if q.geom_type!='Polygon' or q.area<.65:continue
        assert private.buffer(1e-6).covers(q) and q.intersection(keepout).area<1e-6
        triangles=list(constrained_delaunay_triangles(q).geoms)
        assert all(q.covers(t) for t in triangles)
        assert abs(sum(t.area for t in triangles)-q.area)<1e-5
        vertices=[];faces=[]
        for t in triangles:
            points=list(t.exterior.coords)[:-1]
            if not t.exterior.is_ccw:points.reverse()
            base=len(vertices);vertices.extend([[x,y,.047] for x,y in points]);faces.append([base,base+1,base+2])
        pieces.append({'id':f'beta-block-groundcover-{index:02}-{len(pieces):03}','block':index,'vertices':vertices,'faces':faces,'material':'grass','area':q.area})
assert len(pieces)>=12,('Insufficient usable frontage bands',len(pieces))
refinement={'beforeSourceSHA256':hashlib.sha256(raw).hexdigest(),'publicStoneWorldSize':3.2,'privateStoneWorldSize':8,'basis':'RO3 beta00:35,02:00,02:10,03:05 and03:20; direct same-size Wayfarer street comparison','plantingStrategy':'Continuous planted strips within existing owned block edges, cut clear of entrances, courts, props and roads','pieces':pieces,'plantedArea':sum(q['area'] for q in pieces),'entranceClearWidth':2.0,'geometryAndNavigationUnchanged':True,'existingGroundShadowReceiversRetained':True}
refinement['preservedSourceDigest']=runpy.run_path(str(R/'tools/capital-beta-edge-integrity-v76.py'))['preserved_digest'](s)
(O/'beta-edge-plan.json').write_text(json.dumps(refinement,indent=2)+'\n')
print(json.dumps({k:v for k,v in refinement.items() if k!='pieces'},indent=2));print('Frontage strips',len(pieces),'triangles',sum(len(q['faces']) for q in pieces))
