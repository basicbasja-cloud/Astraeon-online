"""Save reviewed route repairs in native walker anchors, preserving actor art/pace."""
import bpy,json,runpy,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;plan=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());record=json.loads(scene['ro3_blueprint_review_json'])
for name,points in plan['repairs'].items():
 o=bpy.data.objects[name];inv=o.matrix_world.inverted();o['route_json']=json.dumps([list(inv@Vector((x,y,0))) for x,y in points])
record['patrolRepairs']=plan['checks'];scene['ro3_blueprint_review_json']=json.dumps(record);scene['ro3_blueprint_patrols_version']=72;bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('PASS native patrol route repairs',len(plan['repairs']))
