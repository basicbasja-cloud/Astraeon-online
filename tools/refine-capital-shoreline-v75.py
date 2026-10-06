"""Orient only inward cliff faces and downward native waterline ribbons.

Keep the first corner fixed when reversing a face: its fan diagonal, every
vertex and each vertex's UV remain intact. Rebake the changed shoreline lights.
"""
import bpy,json,runpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('capital_version')==75
center=Vector((*json.loads(scene['capital_plan_json'])['center'],0));counts={};changed=False
for name in ('capital-river-bank','capital-waterline'):
 checked=0;reoriented=0
 for obj in bpy.data.collections[name].objects:
  if obj.type!='MESH':continue
  old=obj.data;faces=[];flipped=False
  for face in old.polygons:
   f=list(face.vertices);vs=[obj.matrix_world@old.vertices[i].co for i in f];normal=(vs[1]-vs[0]).cross(vs[2]-vs[0]);mid=sum(vs,Vector())/len(vs)
   reverse=normal.z<=0 if name=='capital-waterline' else normal.x*(mid.x-center.x)+normal.y*(mid.y-center.y)<=0
   faces.append([f[0],*reversed(f[1:])] if reverse else f);checked+=1;reoriented+=reverse;flipped|=reverse
  if not flipped:continue
  uvs=[{old.loops[i].vertex_index:tuple(old.uv_layers.active.data[i].uv) for i in f.loop_indices} for f in old.polygons]
  mesh=bpy.data.meshes.new(obj.name+'-outward');mesh.from_pydata([tuple(v.co) for v in old.vertices],[],faces)
  for material in old.materials:mesh.materials.append(material)
  mesh.uv_layers.new(name='WorldUV')
  for face,uv in zip(mesh.polygons,uvs):
   for i in face.loop_indices:mesh.uv_layers.active.data[i].uv=uv[mesh.loops[i].vertex_index]
  obj.data=mesh;changed=True
 counts[name]={'checkedFaces':checked,'reorientedFaces':reoriented}
if changed:
 scene['capital_shoreline_normals']=75;scene['capital_shoreline_review_json']=json.dumps(counts)
 bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Native shoreline orientation verified',json.dumps(counts),flush=True)
