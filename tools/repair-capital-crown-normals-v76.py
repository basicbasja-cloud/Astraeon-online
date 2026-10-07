"""Correct new bough face winding while retaining each physical UV corner."""
import bpy, bmesh, json, runpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v76/property-frontages'
s=bpy.context.scene;assert s.get('capital_natural_landscape') and not s.get('capital_crown_upward_normals')
meshes=faces=0
for obj in bpy.data.objects:
    if not obj.get('landscape_v76'):continue
    before=[sorted((tuple(obj.data.vertices[obj.data.loops[i].vertex_index].co),tuple(obj.data.uv_layers.active.data[i].uv)) for i in f.loop_indices) for f in obj.data.polygons]
    bm=bmesh.new();bm.from_mesh(obj.data);down=[f for f in bm.faces if f.normal.z<0]
    faces+=len(down);bmesh.ops.reverse_faces(bm,faces=down);bm.to_mesh(obj.data);bm.free();obj.data.update()
    assert all(f.normal.z>0 for f in obj.data.polygons),obj.name
    after=[sorted((tuple(obj.data.vertices[obj.data.loops[i].vertex_index].co),tuple(obj.data.uv_layers.active.data[i].uv)) for i in f.loop_indices) for f in obj.data.polygons]
    assert before==after,(obj.name,'physical UV corners changed')
    meshes+=1
assert meshes==234 and faces==28080,(meshes,faces)
report=json.loads((O/'landscape-authoring.json').read_text());report['crownNormals']={'meshes':meshes,'upwardFaces':faces,'physicalVerticesAndUVsPreserved':True}
(O/'landscape-authoring.json').write_text(json.dumps(report,indent=2)+'\n');s['capital_crown_upward_normals']=1
bpy.ops.wm.save_as_mainfile(filepath=str(R/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(R/'tools/export-world-v3.py'),run_name='__main__')
print('Upward crown boughs:',meshes,'meshes;',faces,'faces; physical UVs retained',flush=True)
