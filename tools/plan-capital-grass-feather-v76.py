"""Tessellate native lawns into solid interiors and translucent planted edges."""
import json, hashlib, math
from pathlib import Path
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v76/property-frontages'
def feather_plan(plan):
    assert not plan.get('nativeEdgeOpacity'), 'Already feathered'
    pieces=[]; old_triangles=sum(len(a['faces']) for a in plan['pieces'])
    for a in plan['pieces']:
        q=unary_union([Polygon([a['vertices'][i][:2] for i in f]) for f in a['faces']])
        width=.28
        core=q.buffer(-width,quad_segs=2,join_style=2)
        while core.is_empty and width>.035:
            width/=2;core=q.buffer(-width,quad_segs=2,join_style=2)
        vertices=[];faces=[];opacity=[];index={}
        for zone in (core,q.difference(core)):
            for t in constrained_delaunay_triangles(zone).geoms:
                pts=list(t.exterior.coords)[:-1]
                if not t.exterior.is_ccw:pts.reverse()
                face=[]
                for x,y in pts:
                    key=(round(x,5),round(y,5))
                    if key not in index:
                        index[key]=len(vertices);vertices.append([*key,.047])
                        opacity.append(round(min(1,max(0,q.boundary.distance(Point(x,y))/width)),5))
                    face.append(index[key])
                faces.append(face)
        assert faces and max(opacity)>.99 and min(opacity)<.001,a['id']
        area=sum(Polygon([vertices[i][:2] for i in f]).area for f in faces)
        assert abs(area-q.area)<.001,(a['id'],area,q.area)
        pieces.append({**a,'vertices':vertices,'faces':faces,'vertexOpacity':opacity,'featherWidth':width})
    triangles=sum(len(a['faces']) for a in pieces)
    added=triangles-old_triangles
    assert 0<added<20000,(triangles,added)
    report={**plan,'pieces':pieces,'triangles':triangles,'nativeEdgeOpacity':True,
            'edgeBlending':{'width':.28,'oldTriangles':old_triangles,'addedTriangles':added,'triangleBudget':20000,
                           'newTextures':0,'newPhysicalObstacles':0,'underlyingStoneVisible':True}}
    return report

if __name__=='__main__':
    report=feather_plan(json.loads((O/'natural-lawns-plan.json').read_text()))
    (O/'grass-feather-plan.json').write_text(json.dumps(report,separators=(',',':'))+'\n')
    print(json.dumps(report['edgeBlending'],indent=2))
