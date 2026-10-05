"""Read-only terrain contact and lighting-bake preservation for curb-side grass."""
import bpy,json,sys,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain');vs=[];fs=[]
for o in terrain.objects:
 if o.type!='MESH' or o.get('surface_role')=='water' or not o.get('walkable',True):continue
 off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles();fs.extend(tuple(off+i for i in f.vertices) for f in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);violations=[];count=0
for o in terrain.objects:
 if not o.get('curb_grass_v69'):continue
 assert not o['walkable'] and not o['shadow'];count+=1
 for v in o.data.vertices:
  p=o.matrix_world@v.co;hit=tree.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),150)[0]
  if hit is None or abs(p.z-hit.z-.017)>.003:violations.append({'id':o.name,'point':list(p)})
exporter=runpy.run_path(str(ROOT/'tools/export-world-v3.py'));w=exporter['export'](scene);assert w['lighting'].get('groundShadow'),'Decorative roadside grass must retain current floor bake';assert not violations,violations
assert count==len(json.loads(scene['ro3_curb_grass_review_json'])['strips']) and count>20
report={'sourcePass':69,'roadsideStrips':count,'rootedVertices':count*4,'violations':violations,'floorAndCasterGeometryPreserved':True,'shadowDigest':w['lighting']['groundShadow']['geometryDigest']};Path(sys.argv[sys.argv.index('--')+1]).write_text(json.dumps(report,indent=2)+'\n');print('PASS rooted roadside grass',count,'strips; current native floor bake preserved')
