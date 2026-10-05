"""Read-only source contact and clearance for editable house accessory stations."""
import json,sys
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
scene=bpy.context.scene;assert scene.get('ro3_house_life_version')==69
review=json.loads(scene['ro3_house_life_review_json'])
assert len(review['buildings'])==37
terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain');vs=[];fs=[]
for o in terrain.objects:
 if o.type!='MESH' or o.get('surface_role')=='water' or not o.get('walkable',True):continue
 off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles();fs.extend(tuple(off+i for i in f.vertices) for f in o.data.loop_triangles)
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True)
violations=[];vertices=0
for record in review['groundStations']:
 collision=bpy.data.objects[record['collider']];parts=[o for o in bpy.data.collections[record['owner']].objects if o.type=='MESH' and o.get('house_life_v69_station')==collision.get('house_life_v69_station')]
 inv=collision.parent.matrix_world.inverted()
 # Projection into the station's world tangent/normal, independent of house orientation.
 t=Vector((*record['tangent'],0));n=Vector((*record['normal'],0));center=Vector((*record['center'],0))
 for o in parts:
  assert o.parent==collision.parent,o.name
  for v in o.data.vertices:
   p=o.matrix_world@v.co;vertices+=1
   if abs((p-center).dot(t))>.411 or abs((p-center).dot(n))>.341:violations.append({'id':o.name,'outsideCollider':list(p)})
 ground=floor.ray_cast(Vector((*record['center'],100)),Vector((0,0,-1)),150)[0]
 lowest=min((collision.matrix_world@v.co).z for v in collision.data.vertices)
 if ground is None or abs(lowest-ground.z-.012)>.003:violations.append({'id':collision.name,'ground':lowest})
for o in bpy.data.objects:
 if o.type=='MESH' and o.name.startswith('life69-') and '-flowerbox-' in o.name:
  for v in o.data.vertices:
   p=o.matrix_world@v.co;ground=floor.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),150)[0]
   if ground and p.z-ground.z<70*(92/76)/35:violations.append({'id':o.name,'belowBodyClearance':list(p)})
report={'sourcePass':69,'buildings':review['buildings'],'groundStations':len(review['groundStations']),'plannedStations':review['plannedCount'],'checkedStationVertices':vertices,'violations':violations}
path=Path(sys.argv[sys.argv.index('--')+1]);path.write_text(json.dumps(report,indent=2)+'\n')
assert not violations,json.dumps(violations[:12])
print('PASS 37 dressed houses;',len(review['groundStations']),'rooted stations;',vertices,'vertices within native collision')
