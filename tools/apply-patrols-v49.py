"""Register planned world routes in each editable Blender walker transform."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
routes=json.loads((ROOT/'authoring/patrol-routes-v49.json').read_text())
for o in bpy.data.objects:
 if o.get('kind')=='walker':
  inverse=o.matrix_world.inverted();o['route_json']=json.dumps([list(inverse@Vector((x,y,0))) for x,y in routes[o.name]])
bpy.context.scene['patrol_route_version']=49
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Saved and exported closed source patrol routes')
