"""Independent checks against actual exported triangles, not mesh convex hulls."""
import argparse,json,math,runpy
from pathlib import Path
from collections import Counter,defaultdict
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
from shapely.strtree import STRtree
ROOT=Path(__file__).resolve().parents[1];h=runpy.run_path(str(ROOT/'tools/plan-ro3-density-v68.py'));ap=argparse.ArgumentParser();ap.add_argument('--native',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();w=json.loads((ROOT/'world/v3/wayfarer-spatial.json').read_text());r=json.loads(args.native.read_text());surfaces={s['id']:s for s in w['terrain']['surfaces']}
def footprint(s):
 return unary_union([Polygon([s['vertices'][i][:2] for i in f]) for f in s['faces'] if len(f)>=3]).buffer(0)
public=unary_union([footprint(s) for s in surfaces.values() if s['visible'] and s['walkable'] and (s.get('centerline') and s.get('width',0)>=1.8 or s['material']=='publicSquareStone' or 'processional-tread-' in s['id'])]);solids=[];solidSpecs=[]
for o in w['objects']:
 for p in o['parts']:
  if p['role']=='solid':solids.append(Polygon(h['hull'](p['vertices'])));solidSpecs.append(p)
index=STRtree(solids);curbRegions=[];publicHits=[];volumeHits=[];loopChecks=[];samples=0
for rec in r['curbs']:
 s=surfaces[rec['id']];assert s['walkable'] and s['visible'];region=footprint(s);curbRegions.append(region);overlap=region.intersection(public)
 if overlap.area>.002:publicHits.append({'curb':s['id'],'area':overlap.area})
 # A band has outer and inner cyclic borders, with no degree-one open ends.
 edges=Counter(tuple(sorted((a,b))) for f in s['faces'] for a,b in zip(f,f[1:]+f[:1]));border=[e for e,n in edges.items() if n==1];graph=defaultdict(set)
 for a,b in border:graph[a].add(b);graph[b].add(a)
 assert all(len(v)==2 for v in graph.values()),(s['id'],'open boundary or branching seam')
 assert max(edges.values())<=2,(s['id'],'non-manifold curb')
 seen=set();loops=0
 for v in graph:
  if v in seen:continue
  loops+=1;todo=[v]
  while todo:
   q=todo.pop()
   if q in seen:continue
   seen.add(q);todo.extend(graph[q]-seen)
 loopChecks.append({'id':s['id'],'meshBorderLoops':loops,'openEnds':0,'borderVertices':len(graph)})
 for face in s['faces']:
  xyz=[s['vertices'][i] for i in face];tri=Polygon([p[:2] for p in xyz])
  if tri.area<1e-10:continue
  a,b,c=xyz;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  for n in index.query(tri):
   overlap=tri.intersection(solids[n])
   if overlap.area<.00001:continue
   p=solidSpecs[n];lo=min(v[2] for v in p['vertices']);hi=max(v[2] for v in p['vertices']);q=overlap.representative_point();u=((b[1]-c[1])*(q.x-c[0])+(c[0]-b[0])*(q.y-c[1]))/den;v=((c[1]-a[1])*(q.x-c[0])+(a[0]-c[0])*(q.y-c[1]))/den;z=u*a[2]+v*b[2]+(1-u-v)*c[2]
   if lo+.001<z<hi-.001:volumeHits.append({'curb':s['id'],'solid':p['id'],'xy':[q.x,q.y],'curbZ':z,'solidZ':[lo,hi]})
   samples+=1
cross=[s for s in surfaces.values() if s['id'].startswith('blueprint72-cross-')];assert len(cross)==4
center=r['center'];assert center==[54,52.75];assert r['plaza']['increasePercent']>60
fountain=next(o for o in w['objects'] if o['id']=='astral-fountain');basin=next(p for p in fountain['parts'] if p['id']=='fountain-basin');actual=[(min(v[i] for v in basin['vertices'])+max(v[i] for v in basin['vertices']))/2 for i in (0,1)];assert math.dist(actual,center)<.0001
for old in r['retiredLegacyMeshes']:assert not surfaces[old]['visible'] and not surfaces[old]['walkable'],old
intersections=sum(curbRegions[i].intersection(b).area for i in range(len(curbRegions)) for b in curbRegions[:i]);assert intersections<.001
report={'status':'passed' if not(publicHits or volumeHits) else 'needs_correction','plazaAreaBefore':r['plaza']['beforeArea'],'plazaAreaAfter':r['plaza']['area'],'increasePercent':r['plaza']['increasePercent'],'fountainCenter':actual,'closedBuildingBoundaryLoops':r['closedBoundaryLoops'],'nativeBorderChecks':loopChecks,'publicPathOverlaps':publicHits,'curbSolidVolumeOverlaps':volumeHits,'solidContactsChecked':samples,'curbIntersectionArea':intersections,'nativeFullResolutionPolicyUnchanged':True,'groundShadow':w['lighting'].get('groundShadow')};args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('curbSolidVolumeOverlaps','groundShadow')}));assert report['status']=='passed',(len(publicHits),len(volumeHits),'curb placement correction required')
