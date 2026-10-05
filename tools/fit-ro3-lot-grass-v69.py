"""Move complete grass groups to the outside of native house-owned apron rims."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('ro3_house_apron_version')==69
assert not scene.get('ro3_lot_grass_fit_version')
aprons=json.loads(scene['ro3_house_apron_review_json'])['aprons'];terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain');vs=[];fs=[]
for o in terrain.objects:
 if o.type!='MESH' or o.get('surface_role')=='water' or not o.get('walkable',True):continue
 off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles();fs.extend(tuple(off+i for i in f.vertices) for f in o.data.loop_triangles)
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True);default_height=json.loads((ROOT/'world/v3/wayfarer-spatial.json').read_text())['terrain']['elevation']
def height(x,y):
 hit=floor.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),150)[0]
 return hit.z if hit else default_height
records=[];moved=0;clumps=0;blades=0
for c in bpy.data.collections:
 patches=[o for o in c.objects if o.get('street_v69_patch')];groups=[]
 for o in patches:
  pts=[o.matrix_world@v.co for v in o.data.vertices];front=[pts[0],pts[1]] if len(pts)==4 else [pts[0],pts[-1]];center=sum(front,Vector())/2;t=front[1]-front[0];t.z=0;t.normalize();n=Vector((t.y,-t.x,0));options=[]
  for p in aprons:
   if p['owner']!=c.name or n.dot(Vector((*p['normal'],0)))<.95:continue
   a,b=Vector((*p['polygon'][3],0)),Vector((*p['polygon'][2],0));u=(center-a).dot(t);length=(b-a).length
   if -.25<=u<=length+.25:options.append(((center-a).dot(n),p))
  shift=Vector()
  if options:
   _,p=min(options,key=lambda p:abs(p[0]));outer=Vector((*p['polygon'][3],0));distance=(outer-center).dot(n)+.045
   shift=n*max(0,min(.85,distance));moved+=shift.length>.01
  groups.append({'id':o.name,'center':center.copy(),'shift':shift.copy(),'oldPoints':pts})
  inv=o.matrix_world.inverted()
  for v,p in zip(o.data.vertices,pts):
   q=p+shift;q.z=height(q.x,q.y)+.017;v.co=inv@q
  records.append({'id':o.name,'owner':c.name,'vertices':[list(o.matrix_world@v.co) for v in o.data.vertices]})
 for o in list(c.objects):
  isclump=bool(o.get('street_v69_clump'));isblade=bool(o.get('street_v69_blade'))
  if not (isclump or isblade):continue
  if isclump:old=Vector(o['street_v69_root_world'])
  else:old=(o.matrix_world@o.data.vertices[0].co+o.matrix_world@o.data.vertices[1].co)/2
  # All parts of a clump share one translation, preserving blade shape.
  group=min(groups,key=lambda g:(old.xy-g['center'].xy).length) if groups else None
  shift=group['shift'] if group else Vector();new=old+shift;new.z=height(new.x,new.y)+(.017 if isclump else .022);delta=new-old;inv=o.matrix_world.inverted()
  for v in o.data.vertices:v.co=inv@(o.matrix_world@v.co+delta)
  if isclump:o['street_v69_root_world']=list(new);clumps+=1
  else:blades+=1
review=json.loads(scene['ro3_street_review_json']);review['patches']=records;scene['ro3_street_review_json']=json.dumps(review)
scene['ro3_lot_grass_fit_version']=69;scene['ro3_lot_grass_fit_review_json']=json.dumps({'foundationStrips':len(records),'movedToOuterLotEdge':moved,'refittedClumps':clumps,'refittedOldBlades':blades,'outsideRimGap':.045})
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Living lot edge:',moved,'strips outside stone rims;',clumps,'complete rooted clumps;',blades,'inherited blades refitted')
