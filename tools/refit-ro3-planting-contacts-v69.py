"""Fit decorative planting vertex roots onto actual subtly sloped native paving."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;assert scene.get('ro3_planting_edge_version')==69 and not scene.get('ro3_planting_ground_refit_version');review=json.loads(scene['ro3_planting_edge_review_json']);terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain');vs=[];fs=[]
for o in terrain.objects:
 if o.type!='MESH' or o.get('surface_role')=='water' or not o.get('walkable',True):continue
 off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles();fs.extend(tuple(off+i for i in f.vertices) for f in o.data.loop_triangles)
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def ground(p):
 hit=floor.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),150)[0];assert hit is not None;return hit.z
count=0;maximum=0
for record in review['beds']+review['orphanGroundFlowerGroups']:
 for name in record['parts']:
  o=bpy.data.objects[name];inv=o.matrix_world.inverted()
  for v in o.data.vertices:
   p=o.matrix_world@v.co;dz=ground(p)-record['floor'];maximum=max(maximum,abs(dz));p.z+=dz;v.co=inv@p;count+=1
 o=bpy.data.objects[record['grassPatch']];inv=o.matrix_world.inverted()
 for v in o.data.vertices:
  p=o.matrix_world@v.co;p.z=ground(p)+.017;v.co=inv@p;count+=1
assert maximum<.05,maximum
review['groundRefit']={'vertices':count,'maximumCorrection':maximum,'method':'Actual native floor height at each planted vertex; plant height above its local floor preserved'};scene['ro3_planting_edge_review_json']=json.dumps(review);scene['ro3_planting_ground_refit_version']=69
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('PASS planting slope contact:',count,'vertices; maximum height correction',maximum)
