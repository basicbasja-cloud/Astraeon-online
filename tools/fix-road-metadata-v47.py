"""Correct the saved strip vertex order used by road centerline export."""
import bpy,bmesh
from pathlib import Path
assert bpy.context.scene.get('organic_town_version')==47 and bpy.context.scene.get('road_metadata_version')!=47,'One-time repair already applied or wrong source'
count=0
for o in bpy.data.objects:
 if o.name.startswith('organic-v47-plan-') and o.get('road_segment'):
  data=o.data
  a,b=data.vertices[1].co.copy(),data.vertices[3].co.copy()
  data.vertices[1].co=b;data.vertices[3].co=a
  bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
  for face in data.polygons:
   for li in face.loop_indices:
    p=o.matrix_world@data.vertices[data.loops[li].vertex_index].co
    data.uv_layers.active.data[li].uv=(p.x/4,p.y/4)
  count+=1
bpy.context.scene['road_metadata_version']=47
bpy.ops.wm.save_as_mainfile(filepath=str(Path(__file__).resolve().parents[1]/'authoring/wayfarer-spatial.blend'))
print('Corrected saved road centerlines:',count)
