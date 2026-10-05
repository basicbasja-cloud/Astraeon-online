"""Fit each complete accessory station to the highest actual native floor at its root."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain');vs=[];fs=[]
for o in terrain.objects:
 if o.type!='MESH' or o.get('surface_role')=='water' or not o.get('walkable',True):continue
 off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles();fs.extend(tuple(off+i for i in f.vertices) for f in o.data.loop_triangles)
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True);review=json.loads(scene['ro3_house_life_review_json']);repairs=[]
for record in review['groundStations']:
 collision=bpy.data.objects[record['collider']];ground=floor.ray_cast(Vector((*record['center'],100)),Vector((0,0,-1)),150)[0];assert ground is not None,collision.name
 lowest=min((collision.matrix_world@v.co).z for v in collision.data.vertices);dz=ground.z+.012-lowest
 for o in bpy.data.collections[record['owner']].objects:
  if o.type=='MESH' and o.get('house_life_v69_station')==collision.get('house_life_v69_station'):
   delta=o.matrix_world.inverted().to_3x3()@Vector((0,0,dz))
   for v in o.data.vertices:v.co+=delta
   o['house_life_v69_ground']=ground.z
 record['ground']=ground.z;repairs.append({'id':collision.name,'translationZ':dz,'ground':ground.z})
scene['ro3_house_life_review_json']=json.dumps(review);scene['ro3_goods_floor_fit_review_json']=json.dumps(repairs)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Accessory floor fits',json.dumps(repairs))
