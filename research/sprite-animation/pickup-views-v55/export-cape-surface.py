"""Read actual evaluated original cape surface; never edit the frozen source blend."""
import bpy,json,math,hashlib
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;blend=P.parent/'pickup-sixteen-v48/source/parent-v45.blend';data=json.loads((P/'source/controlled-retiming-v1.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(blend));sc=bpy.context.scene;sc.camera=bpy.data.objects['S'];sc.render.resolution_x=384;sc.render.resolution_y=512;sc.render.resolution_percentage=100;obj=bpy.data.objects['original_cape'];rows=[]
for row in data['views']['S']['frames']:
 tick=1+39*row['source_phase'];sc.frame_set(math.floor(tick),subframe=tick-math.floor(tick));bpy.context.view_layer.update();ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();vertices=[]
 for v in mesh.vertices:
  w=ev.matrix_world@v.co;q=world_to_camera_view(sc,sc.camera,w);vertices.append({'world':list(w),'xy':[q.x*384,(1-q.y)*512],'depth':q.z})
 rows.append({'index':row['index'],'source_phase':row['source_phase'],'vertices':vertices,'polygons':[list(p.vertices) for p in mesh.polygons]});ev.to_mesh_clear()
(P/'source/cape-surface-S.json').write_text(json.dumps({'parent_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'retiming_sha256':hashlib.sha256((P/'source/controlled-retiming-v1.json').read_bytes()).hexdigest(),'object':'original_cape','view':'S','frames':rows,'scope':'Actual evaluated source3D surface, not recovered painted geometry.'},indent=2)+'\n');print('CAPTURED_ACTUAL_CAPE',len(rows),len(rows[0]['vertices']))
