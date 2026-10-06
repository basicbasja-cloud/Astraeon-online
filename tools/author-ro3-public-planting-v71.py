"""Move inherited loose flowers out of public paths onto owned building margins."""
import bpy,json,runpy,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('ro3_curb_boundaries_version')==71 and not scene.get('ro3_public_planting_version')
exporter=runpy.run_path(str(ROOT/'tools/export-world-v3.py'));w=exporter['export'](scene);h=runpy.run_path(str(ROOT/'tools/plan-ro3-density-v68.py'));bound=runpy.run_path(str(ROOT/'tools/ro3-public-boundaries-v71.py'));public=[h['hull'](s['vertices']) for s in bound['public_surfaces'](w)];ss={s['id']:s for s in w['terrain']['surfaces']};review=json.loads(scene['ro3_planting_edge_review_json']);curbs=json.loads(scene['ro3_road_curb_review_json'])['curbBlocks'];boundary=json.loads(scene['ro3_curb_boundaries_review_json']);terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain')
vs=[];fs=[]
for s in ss.values():
 if not s['walkable']:continue
 off=len(vs);vs.extend(s['vertices'])
 for f in s['faces']:
  for j in range(1,len(f)-1):fs.append((off+f[0],off+f[j],off+f[j+1]))
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def ground(p):
 hit=floor.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),150)[0];assert hit is not None;return hit.z
solids=[h['hull'](p['vertices']) for o in w['objects'] for p in o['parts'] if p['role']=='solid'];approaches=[p['position'][:2] for o in w['objects'] for p in o.get('services',[])]+[p['anchor'][:2] for o in w['objects'] for p in o.get('portals',[])];owners=[]
for c in bpy.data.collections:
 core=next((o for o in c.objects if o.type=='MESH' and (o.name.endswith('-ground-core') or o.name.startswith('side-v59-') and o.name.endswith('-lower-walls'))),None)
 if core:owners.append((c.name,core.parent,h['hull']([tuple(core.matrix_world@v.co) for v in core.data.vertices])))
assert len(owners)==37
moves=[r for r in review['orphanGroundFlowerGroups'] if any(h['overlap'](h['hull'](ss[r['grassPatch']]['vertices']),p,-.0001) for p in public)];assert len(moves)==10,len(moves);moving={r['grassPatch'] for r in moves};occupied=[h['hull'](s['vertices']) for s in ss.values() if s['id'].startswith('plantedge69-') and s['id'] not in moving];edges=[]
for rec in curbs:
 if not rec['active']:continue
 s=ss[rec['id']];a,b=Vector(s['vertices'][0]),Vector(s['vertices'][6]);t=b-a;t.z=0;t.normalize();n=Vector(s['vertices'][1])-a;n.z=0;n.normalize();edges.append((rec,(a+b)/2,t,n))
results=[]
for rec in moves:
 old=sum((Vector(v) for v in ss[rec['grassPatch']]['vertices']),Vector())/4;candidates=[]
 for edge,p,t,n in edges:
  center=p+n*(edge['width']+.35+.12);q=[center+t*u*.35+n*v*.35 for u,v in ((-1,-1),(1,-1),(1,1),(-1,1))];poly=[tuple(p[:2]) for p in q]
  if any(not h['inside'](p,w['terrain']['walkablePolygon']) for p in poly):continue
  if any(h['overlap'](poly,p,.06) for p in public+solids+occupied):continue
  if any(h['inside'](p,poly) or min(h['distance'](p,a,b) for a,b in zip(poly,poly[1:]+poly[:1]))<.95 for p in approaches):continue
  eligible=[]
  for name,root,body in owners:
   if h['inside'](center,body):continue
   distance=min(h['distance'](center,a,b) for a,b in zip(body,body[1:]+body[:1]))
   if distance<=3.5:eligible.append((distance,name,root))
  if not eligible:continue
  zs=[ground(q[0]+(q[1]-q[0])*i/4+(q[3]-q[0])*j/4) for i in range(5) for j in range(5)]
  if max(zs)-min(zs)>.025:continue
  dist,name,root=min(eligible,key=lambda p:p[0]);candidates.append(((center.xy-old.xy).length+.15*dist,edge,center,q,poly,name,root))
 assert candidates,('No owned flower margin',rec['group'])
 _,edge,center,q,poly,name,root=min(candidates,key=lambda p:p[0]);delta=Vector((center.x-old.x,center.y-old.y,0))
 for part in rec['parts']:
  o=bpy.data.objects[part];inv=o.matrix_world.inverted()
  for v in o.data.vertices:
   p=o.matrix_world@v.co;new=p+delta;new.z+=ground(new)-ground(p);v.co=inv@new
  matrix=o.matrix_world.copy();o.parent=root;o.matrix_world=matrix;o['planting_owner_v71']=name
 patch=bpy.data.objects[rec['grassPatch']];inv=patch.matrix_world.inverted()
 for v,p in zip(patch.data.vertices,q):p.z=ground(p)+.017;v.co=inv@p
 matrix=patch.matrix_world.copy();patch.parent=root;patch.matrix_world=matrix;patch['planting_owner_v71']=name
 result={'group':rec['group'],'parts':rec['parts'],'grassPatch':rec['grassPatch'],'owner':name,'road':edge['road'],'curb':edge['id'],'offsetXY':list(delta[:2]),'beforeCenter':list(old),'afterCenter':[center.x,center.y,ground(center)],'plantingPolygon':poly};results.append(result);occupied.append(poly);rec.update(owner=name,road=edge['road'],after=result['afterCenter'],floor=ground(center),plantingPolygon=poly,publicBoundaryRefit=71)
scene['ro3_planting_edge_review_json']=json.dumps(review);boundary['plantingMoves']=results;scene['ro3_curb_boundaries_review_json']=json.dumps(boundary);scene['ro3_public_planting_version']=71;bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('PASS owned flower margins',len(results),'groups',json.dumps(results))
