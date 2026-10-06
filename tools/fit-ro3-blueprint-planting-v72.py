"""Tie inherited flower groups and foundation grass to the revised native parcels."""
import bpy,json,runpy,math
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;assert scene.get('ro3_blueprint_version')==72 and not scene.get('ro3_blueprint_planting_version')
h=runpy.run_path(str(ROOT/'tools/plan-ro3-density-v68.py'));ex=runpy.run_path(str(ROOT/'tools/export-world-v3.py'));w=ex['export'](scene);record=json.loads(scene['ro3_blueprint_review_json']);review=json.loads(scene['ro3_planting_edge_review_json']);vs=[];fs=[]
for s in [w['terrain'],*[s for s in w['terrain']['surfaces'] if s['walkable']]]:
 off=len(vs);vs.extend(s['vertices'])
 for f in s['faces']:
  for j in range(1,len(f)-1):fs.append(tuple(off+f[k] for k in (0,j,j+1)))
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def ground(p):
 hit=floor.ray_cast(Vector((p[0],p[1],100)),Vector((0,0,-1)),150)[0];assert hit is not None,p;return hit.z
solids=[h['hull'](p['vertices']) for o in w['objects'] for p in o['parts'] if p['role']=='solid'];entries=[p['position'][:2] for o in w['objects'] for p in o.get('services',[])]+[p['approach'][:2] for o in w['objects'] for p in o.get('portals',[])];bodies=[]
for o in w['objects']:
 p=next((p for p in o['parts'] if p['id'].endswith('-ground-core') or p['id'].startswith('side-v59-') and p['id'].endswith('-lower-walls')),None)
 if p:bodies.append((o['id'],h['hull'](p['vertices'])))
def inside(p,z):return any(h['inside'](p,a['outer']) and not any(h['inside'](p,r) for r in a['holes']) for a in z['outline'])
edges=[]
for z in record['zones']:
 for a in z['outline']:
  for ring in [a['outer'],*a['holes']]:
   for a,b in zip(ring,ring[1:]+ring[:1]):
    length=math.dist(a,b)
    if length<.9:continue
    t=Vector(((b[0]-a[0])/length,(b[1]-a[1])/length,0));n=Vector((-t.y,t.x,0));mid=Vector(((a[0]+b[0])/2,(a[1]+b[1])/2,0))
    if not inside((mid+n*.6)[:2],z):n=-n
    edges.append((z,a,b,mid,t,n,length))
occupied=[];results=[]
for rec in sorted(review['beds']+review['orphanGroundFlowerGroups'],key=lambda r:len(r['parts']),reverse=True):
 patch=bpy.data.objects[rec['grassPatch']];points=[patch.matrix_world@v.co for v in patch.data.vertices];old=sum(points,Vector())/len(points);length=(points[1]-points[0]).length;width=(points[3]-points[0]).length;candidates=[]
 for z,a,b,mid,t,n,span in edges:
  if span<length+.12:continue
  center=mid+n*(.43+width/2);q=[center+t*u*length/2+n*v*width/2 for u,v in ((-1,-1),(1,-1),(1,1),(-1,1))];poly=[tuple(p[:2]) for p in q]
  if not all(inside(p,z) for p in poly):continue
  if any(h['overlap'](poly,p,.08) for p in solids+occupied):continue
  if any(h['inside'](p,poly) or min(h['distance'](p,a,b) for a,b in zip(poly,poly[1:]+poly[:1]))<.95 for p in entries):continue
  owners=[(min(h['distance'](center,a,b) for a,b in zip(body,body[1:]+body[:1])),name) for name,body in bodies if not h['inside'](center,body)]
  distance,owner=min(owners)
  if distance>3.5:continue
  zs=[ground((q[0]+(q[1]-q[0])*i/4+(q[3]-q[0])*j/4)[:2]) for i in range(5) for j in range(5)]
  if max(zs)-min(zs)>.025:continue
  candidates.append(((center.xy-old.xy).length+.15*distance,center,q,poly,owner,z['id'],t))
 assert candidates,('No closed-zone flower margin',rec['group'])
 _,center,q,poly,owner,zone,t=min(candidates,key=lambda a:a[0]);oldZ=min(p.z for p in points)-.017;z=ground(center);oldT=(points[1]-points[0]).normalized();angle=math.atan2(t.y,t.x)-math.atan2(oldT.y,oldT.x);transform=Matrix.Translation(Vector((center.x,center.y,z)))@Matrix.Rotation(angle,4,'Z')@Matrix.Translation(Vector((-old.x,-old.y,-oldZ)));root=bpy.data.objects[owner+'-placement']
 for name in rec['parts']:
  o=bpy.data.objects[name];m=transform@o.matrix_world;o.parent=root;o.matrix_world=m;o['planting_owner_v72']=owner
 inv=patch.matrix_world.inverted()
 for v,p in zip(patch.data.vertices,q):p.z=ground(p)+.017;v.co=inv@p
 m=patch.matrix_world.copy();patch.parent=root;patch.matrix_world=m
 occupied.append(poly);rec.update(owner=owner,zone=zone,after=[center.x,center.y,z],floor=z,plantingPolygon=poly,publicBoundaryRefit=72)
 results.append({'group':rec['group'],'grassPatch':rec['grassPatch'],'parts':rec['parts'],'owner':owner,'zone':zone,'beforeCenter':list(old),'afterCenter':[center.x,center.y,z],'rotation':angle})
# Whole house moves already moved child grass meshes; update their world root
# metadata before the floor-contact fitter applies only the new grade difference.
for name,d in record['houseMoves'].items():
 for o in bpy.data.collections[name].objects:
  if o.get('street_v69_clump'):o['street_v69_root_world']=[o['street_v69_root_world'][i]+d[i] for i in range(3)]
scene['ro3_planting_edge_review_json']=json.dumps(review);record['flowerMoves']=results;scene['ro3_blueprint_review_json']=json.dumps(record)
fit=runpy.run_path(str(ROOT/'tools/fit-ro3-grass-contact-v70.py'))['fit'](scene);fit['reason']='Closed district curbs and translated house parcels: native vegetation follows actual revised floor heights';scene['ro3_grass_contact_v70_json']=json.dumps(fit)
scene['ro3_blueprint_planting_version']=72;bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('PASS closed-zone flower ownership',len(results),'groups; foundation grass contact fitted')
