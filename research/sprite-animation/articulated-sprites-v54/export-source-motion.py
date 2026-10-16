"""Actual saved source endpoints, including hidden source joints; not painted joint recovery."""
from pathlib import Path
import bpy,json,hashlib
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;parent=P.parent/'pickup-sixteen-v48/source/parent-v45.blend';walk=P/'source/walk-natural.blend'
def joints(scene,rig,camera):
 return {b.name:{edge:{'world':list(rig.matrix_world@getattr(b,edge)),'xy':list((lambda q:(q.x*384,(1-q.y)*512))(world_to_camera_view(scene,camera,rig.matrix_world@getattr(b,edge))))} for edge in ['head','tail']} for b in rig.pose.bones}
bpy.ops.wm.open_mainfile(filepath=str(parent));sc=bpy.context.scene;sc.frame_set(1);rig=bpy.data.objects['Astraeon_Free_Local'];rest={v:joints(sc,rig,bpy.data.objects[v]) for v in ['S','SW','W','NW','N','NE','E','SE']}
bpy.ops.wm.open_mainfile(filepath=str(walk));sc=bpy.context.scene;rig=bpy.data.objects['Astraeon_Free_Local'];out={v:[] for v in rest}
for i in range(257):
 tick=1+(sc.frame_end-1)*i/256;sc.frame_set(int(tick),subframe=tick%1);bpy.context.view_layer.update()
 for v in rest:out[v].append({'phase':i/256,'joints':joints(sc,rig,bpy.data.objects[v])})
(P/'source/source-walk-endpoints.json').write_text(json.dumps({'rest_parent_sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),'walk_blend_sha256':hashlib.sha256(walk.read_bytes()).hexdigest(),'motion_profile':json.loads((P/'source/walk-natural-source-review.json').read_text())['design'],'rest':rest,'walk':out,'scope':'Actual source endpoints only, not automatic painted anatomy/retarget correctness'},separators=(',',':'))+'\n');print('SOURCE_ENDPOINTS',8,257,flush=True)
