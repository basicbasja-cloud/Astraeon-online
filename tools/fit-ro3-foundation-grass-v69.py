"""Fit overlapping living grass edges to building bases, leaving entrances clear.

Native decorative grass never changes navigation. Source-owned alpha islands
are wider along the wall and irregular outwards, rather than scattered dots.
Only non-casting plant meshes change; existing lighting geometry stays valid.
"""
import bpy,json,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('ro3_street_version')==69
assert not scene.get('ro3_verge_fit_version')
terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain');vs=[];fs=[]
for o in terrain.objects:
 if o.type!='MESH' or o.get('surface_role')=='water' or not o.get('walkable',True):continue
 off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles();fs.extend(tuple(off+i for i in f.vertices) for f in o.data.loop_triangles)
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def rooted(point):
 hit=floor.ray_cast(Vector((point.x,point.y,100)),Vector((0,0,-1)),150)[0]
 if hit is None:return None
 return Vector((point.x,point.y,hit.z+.017))
records=[];removed=[];widened=0
for c in bpy.data.collections:
 doors=[o for o in c.objects if o.type=='MESH' and o.name.startswith('ro3-v68-') and o.name.endswith('-door-leaf')]
 for o in list(c.objects):
  if not o.get('street_v69_patch'):continue
  assert not o.get('shadow')
  root=o.parent;inv=root.matrix_world.inverted();old=[v.co.copy() for v in o.data.vertices];t=(old[-1]-old[0]).normalized();t.z=0;t.normalize();n=Vector((t.y,-t.x,0));center=(old[0]+old[-1])/2
  new=[center+t*((p-center).dot(t)*1.55)+n*((p-center).dot(n)*1.15) for p in old]
  # Keep a generous visible bare threshold corridor, including off-centre doors.
  def crosses_door(points):
   for door in doors:
    pp=[inv@door.matrix_world@v.co for v in door.data.vertices];dc=sum(pp,Vector())/len(pp)
    if abs((dc-center).dot(n))>.40:continue
    du=[p.dot(t) for p in pp];u=[p.dot(t) for p in points]
    if min(u)<max(du)+.25 and max(u)>min(du)-.25:return True
   return False
  if crosses_door(new):
   if crosses_door(old):
    removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True);continue
   new=old
  world=[rooted(root.matrix_world@p) for p in new]
  if any(p is None for p in world) or max(p.z for p in world)-min(p.z for p in world)>.13:
   world=[rooted(root.matrix_world@p) for p in old]
  else:widened+=new!=old
  for v,p in zip(o.data.vertices,world):v.co=inv@p
  pts=[v.co for v in o.data.vertices];us=[p.dot(t) for p in pts];vs=[p.dot(n) for p in pts]
  for f in o.data.polygons:
   for li in f.loop_indices:
    p=o.data.vertices[o.data.loops[li].vertex_index].co;o.data.uv_layers.active.data[li].uv=((p.dot(t)-min(us))/(max(us)-min(us)),(p.dot(n)-min(vs))/(max(vs)-min(vs)))
  records.append({'id':o.name,'owner':c.name,'vertices':[list(p) for p in world]})
 # Remove orphan tufts in the preserved doorway corridor too.
 for o in list(c.objects):
  if not o.get('street_v69_blade'):continue
  p=o.matrix_world@o.data.vertices[0].co
  for door in doors:
   pp=[door.matrix_world@v.co for v in door.data.vertices];dc=sum(pp,Vector())/len(pp)
   if abs(p.x-dc.x)<.95 and abs(p.y-dc.y)<.95:bpy.data.objects.remove(o,do_unlink=True);break
review=json.loads(scene['ro3_street_review_json']);review['patches']=records
scene['ro3_street_review_json']=json.dumps(review)
scene['ro3_verge_fit_version']=69;scene['ro3_verge_fit_review_json']=json.dumps({'remainingPatches':len(records),'widened':widened,'doorwayOmissions':removed,'tangentScale':1.55,'outwardScale':1.15,'shadowCastersChanged':False})
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Fitted living foundation grass:',len(records),'patches;',widened,'widened;',len(removed),'doorway omissions')
