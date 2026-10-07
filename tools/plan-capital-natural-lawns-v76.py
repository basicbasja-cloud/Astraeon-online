"""Shape owned lawns around usable entries, never across public paving."""
import json, math, hashlib
from pathlib import Path
from shapely.geometry import Polygon, MultiPoint, LineString, Point
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
R=Path(__file__).resolve().parents[1]; O=R/'docs/review/wayfarer-capital-v76/property-frontages'
raw=(R/'world/v3/wayfarer-spatial.json').read_bytes(); s=json.loads(raw)
p=json.loads((O.parent/'native-plan.json').read_text()); objects={o['id']:o for o in s['objects']}
def region(parts):
    return unary_union([Polygon([a['vertices'][i][:2] for i in f]) for a in parts for f in a['faces']])
private=region([a for a in s['terrain']['surfaces'] if a['material']=='houseApronPaving' and all(abs(v[2]-.04)<1e-4 for v in a['vertices'])])
roads=unary_union([LineString(a['centerline']).buffer(a['width']/2+.12,cap_style=2,join_style=2) for a in p['roads']])
solids=[]; props=[]; entries=[]
for o in s['objects']:
    if o['id']=='capital-beta-frontage-groundcover':continue
    for a in o['parts']:
        if a['role']=='solid' and min(v[2] for v in a['vertices'])<1:
            solids.append(MultiPoint([v[:2] for v in a['vertices']]).convex_hull.buffer(.20))
        if a.get('visible',True) and a['material'] not in ('grass','leaf','flowerRose','vergeGroundcover','vergeGroundcoverShade'):
            low=[v[:2] for v in a['vertices'] if v[2]<1.05]
            if len(low)>=3:props.append(MultiPoint(low).convex_hull.buffer(.12))
for lot in p['lots']:
    angle=lot['angle']+lot.get('frontageOffset',0); normal=(-math.sin(angle),math.cos(angle))
    for a in objects[lot['id']]['parts']:
        if not a['id'].endswith('-door-leaf'):continue
        center=[sum(v[i] for v in a['vertices'])/len(a['vertices']) for i in (0,1)]
        entries.append(LineString([center,[center[i]+normal[i]*4.2 for i in (0,1)]]).buffer(1.1,cap_style=2))
keepout=unary_union(solids+props+entries+[Polygon(c['polygon']).buffer(.3) for c in p.get('courtyards',[])]+[roads])
pieces=[]; widths=[]
for index,b in enumerate(p['ownedBlocks']):
    block=Polygon(b['outer'],b['holes']); center=block.centroid
    if not (45<center.x<211 and 80<center.y<244):continue
    # The curb-facing edge follows the royal block. The inward edge expands
    # into planted pockets with slow, continuous variation, rather than tiles.
    rings=[block.exterior]+list(block.interiors); lobes=[]
    for ring in rings:
        count=math.ceil(ring.length/1.0)
        for j in range(count):
            distance=j*ring.length/count
            width=1.35+.40*math.sin(distance*.23+index*.81)+.22*math.sin(distance*.57+index*1.31)
            widths.append(width); lobes.append(Point(ring.interpolate(distance)).buffer(width,quad_segs=6))
    lawn=unary_union(lobes).intersection(block.buffer(-.18,join_style=2)).intersection(private).difference(keepout)
    lawn=lawn.simplify(.075,preserve_topology=True).intersection(private).difference(keepout)
    for q in ([lawn] if lawn.geom_type=='Polygon' else getattr(lawn,'geoms',[])):
        if q.geom_type!='Polygon' or q.area<.8:continue
        triangles=list(constrained_delaunay_triangles(q).geoms)
        assert all(q.covers(t) for t in triangles)
        vertices=[]; faces=[]
        for t in triangles:
            points=list(t.exterior.coords)[:-1]
            if not t.exterior.is_ccw:points.reverse()
            base=len(vertices); vertices.extend([[x,y,.047] for x,y in points]); faces.append([base,base+1,base+2])
        pieces.append({'id':f'natural-block-lawn-{index:02}-{len(pieces):03}','block':index,'vertices':vertices,'faces':faces,'material':'grass','area':q.area})
old=objects['capital-beta-frontage-groundcover']; old_area=region(old['parts']).area
area=sum(q['area'] for q in pieces); tris=sum(len(q['faces']) for q in pieces)
assert old_area*1.1<area<old_area*2.1,(old_area,area)
assert tris<12500,tris
report={'beforeSourceSHA256':hashlib.sha256(raw).hexdigest(),'strategy':'Curb-aligned outer edges, curved inward planted pockets; paved entrance and work bays',
        'oldArea':old_area,'area':area,'widthRange':[min(widths),max(widths)],'entranceClearWidth':2.2,'triangles':tris,'pieces':pieces,
        'roadsPreserved':True,'privateFloorsPreserved':True,'newTextures':0,'newCollisionObstacles':0}
(O/'natural-lawns-plan.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='pieces'},indent=2))
