"""Broaden living lot edges to a readable RO3-like verge at native gameplay scale."""
import bpy,json,runpy,random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
terrain=next(c for c in bpy.data.collections if c.get('family')=='terrain');vs=[];fs=[]
for o in terrain.objects:
 if o.type!='MESH' or o.get('surface_role')=='water' or not o.get('walkable',True):continue
 off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles();fs.extend(tuple(off+i for i in f.vertices) for f in o.data.loop_triangles)
floor=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def grounded(p):
 hit=floor.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),150)[0]
 return Vector((p.x,p.y,hit.z+.017)) if hit else None
spec=json.loads((ROOT/'authoring/materials/wayfarer-street-v69.json').read_text())['materials']['groundcover']['texture']
for name,color in [('vergeGroundcover',(.25,.38,.09,1)),('vergeGroundcoverShade',(.21,.32,.065,1))]:
 m=bpy.data.materials[name];m['texture_json']=json.dumps(spec);m.diffuse_color=color
r=random.Random(6945);records=[];widened=[]
for c in sorted(bpy.data.collections,key=lambda c:c.name):
 for o in sorted(c.objects,key=lambda o:o.name):
  if not o.get('street_v69_patch'):continue
  pts=[o.matrix_world@v.co for v in o.data.vertices]
  if len(pts)==4:
   t=pts[1]-pts[0];t.z=0;t.normalize();n=Vector((t.y,-t.x,0));depth=(pts[3]-pts[0]).dot(n);target=max(depth,r.uniform(.58,.82))
   for width in [target,target*.8,target*.6,depth]:
    q=[grounded(pts[0]),grounded(pts[1]),grounded(pts[1]+n*width),grounded(pts[0]+n*width)]
    if all(p is not None for p in q) and max(p.z for p in q)-min(p.z for p in q)<=.13:
     inv=o.matrix_world.inverted()
     for v,p in zip(o.data.vertices,q):v.co=inv@p
     if width>depth+.02:widened.append({'id':o.name,'before':depth,'after':width})
     break
  records.append({'id':o.name,'owner':c.name,'vertices':[list(o.matrix_world@v.co) for v in o.data.vertices]})
review=json.loads(scene['ro3_street_review_json']);review['patches']=records;scene['ro3_street_review_json']=json.dumps(review)
scene['ro3_full_grass_review_json']=json.dumps({'broadened':widened,'reason':'Thin first native trial failed reference readability','shadowCastersChanged':False,'floorChanged':False})
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Readable full verges:',len(widened),'strips broadened; native ground/lighting unchanged')
