"""Omit wear islands that bridge existing tiny paving steps; keep routes and floor unchanged."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;assert not scene.get('ro3_path_wear_trim_version');review=json.loads(scene['ro3_path_wear_review_json']);terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain');vs=[];fs=[]
for o in terrain.objects:
 if o.type!='MESH' or o.get('surface_role')=='water' or not o.get('walkable',True):continue
 off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles();fs.extend(tuple(off+i for i in f.vertices) for f in o.data.loop_triangles)
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def height(p):
 hit=floor.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),150)[0];assert hit is not None;return hit.z
kept=[];skips=[];removed_grass=0
for record in review['patches']:
 o=bpy.data.objects[record['id']];a,b,c,d=[o.matrix_world@v.co for v in o.data.vertices];fail=[]
 for u in range(9):
  for v in range(9):
   p=a+(b-a)*u/8+(d-a)*v/8;error=abs(p.z-height(p)-.021)
   if error>.003:fail.append({'point':list(p),'error':error})
 if not fail:kept.append(record);continue
 skips.append({'id':o.name,'reason':'Existing paving transition cannot support a flat wear island','maximumContactError':max(p['error'] for p in fail)})
 for grass in list(terrain.objects):
  if not grass.get('path_wear_grass_v69'):continue
  root=(grass.matrix_world@grass.data.vertices[0].co+grass.matrix_world@grass.data.vertices[1].co)/2
  if any((root-Vector(p)).length<.0001 for p in record['roots']):bpy.data.objects.remove(grass,do_unlink=True);removed_grass+=1
 bpy.data.objects.remove(o,do_unlink=True)
assert len(kept)>=12,(len(kept),skips)
review['patches']=kept;review['jointGrassClumps']-=removed_grass;review['omittedPavingTransitions']=skips;scene['ro3_path_wear_review_json']=json.dumps(review);scene['ro3_path_wear_trim_version']=69
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('PASS fit wear islands:',len(kept),'retained;',len(skips),'omitted across paving transitions;',removed_grass,'associated tufts removed; floor/casters unchanged')
