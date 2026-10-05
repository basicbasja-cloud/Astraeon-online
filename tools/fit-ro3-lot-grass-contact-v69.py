"""Resolve lot-edge grass strips against actual terrain, including nearby steps."""
import bpy,json,runpy,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain');vs=[];fs=[]
for o in terrain.objects:
 if o.type!='MESH' or o.get('surface_role')=='water' or not o.get('walkable',True):continue
 off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles();fs.extend(tuple(off+i for i in f.vertices) for f in o.data.loop_triangles)
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def contact(p):
 hit=floor.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),150)[0]
 return Vector((p.x,p.y,hit.z+.017)) if hit else None
repairs=[];records=[]
for c in bpy.data.collections:
 patches=[o for o in c.objects if o.get('street_v69_patch')]
 centers={o.name:sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices) for o in patches}
 shifts={}
 for o in patches:
  pts=[o.matrix_world@v.co for v in o.data.vertices]
  def fitted(delta):
   q=[contact(p+delta) for p in pts]
   return q if all(p is not None for p in q) and max(p.z for p in q)-min(p.z for p in q)<=.13 else None
  shift=Vector();q=fitted(shift)
  if q is None:
   candidates=sorted((Vector((x*.05,y*.05,0)) for x in range(-16,17) for y in range(-16,17)),key=lambda d:d.length_squared)
   for delta in candidates:
    q=fitted(delta)
    if q is not None:shift=delta;break
   assert q is not None,o.name
   shifts[o.name]=shift;repairs.append({'id':o.name,'translation':list(shift)})
  inv=o.matrix_world.inverted()
  for v,p in zip(o.data.vertices,q):v.co=inv@p
  records.append({'id':o.name,'owner':c.name,'vertices':[list(o.matrix_world@v.co) for v in o.data.vertices]})
 for o in c.objects:
  clump=bool(o.get('street_v69_clump'));blade=bool(o.get('street_v69_blade'))
  if not (clump or blade) or not centers:continue
  old=Vector(o['street_v69_root_world']) if clump else (o.matrix_world@o.data.vertices[0].co+o.matrix_world@o.data.vertices[1].co)/2
  owner=min(centers,key=lambda k:(old.xy-centers[k].xy).length_squared)
  new=contact(old+shifts.get(owner,Vector()));assert new is not None,o.name
  if blade:new.z+=.005
  inv=o.matrix_world.inverted();delta=new-old
  for v in o.data.vertices:v.co=inv@(o.matrix_world@v.co+delta)
  if clump:o['street_v69_root_world']=list(new)
review=json.loads(scene['ro3_street_review_json']);review['patches']=records;scene['ro3_street_review_json']=json.dumps(review)
scene['ro3_lot_grass_contact_review_json']=json.dumps({'stepAndGroundRepairs':repairs,'actualTerrainContact':True})
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Lot grass contact repairs',json.dumps(repairs))
