"""Source-only monotone retiming. Actual saved rig evaluations, no image registration."""
from pathlib import Path
import bpy,json,math,hashlib
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;blend=P.parent/'pickup-sixteen-v48/source/parent-v45.blend';bpy.ops.wm.open_mainfile(filepath=str(blend));sc=bpy.context.scene;sc.render.resolution_x=384;sc.render.resolution_y=512;rig=bpy.data.objects['Astraeon_Free_Local'];gem=bpy.data.objects['collectible'];gem.animation_data_clear();gem.hide_render=True;progress=[0,.03,.11,.23,.38,.55,.72,.89,1,.92,.77,.59,.41,.23,.08,0];views={}
def phase(t):
 tick=1+39*t;sc.frame_set(math.floor(tick),subframe=tick-math.floor(tick));gem.hide_render=True;bpy.context.view_layer.update()
def head_y():return 512*(1-world_to_camera_view(sc,sc.camera,rig.matrix_world@rig.pose.bones['head'].head).y)
for view in ['S','W','E']:
 sc.camera=bpy.data.objects[view];ys=[]
 for k in range(401):phase(k/400);ys.append(head_y())
 peak=max(range(401),key=lambda i:ys[i]);start=ys[0];amp=ys[peak]-start;frames=[]
 for i,p in enumerate(progress):
  region=range(peak+1) if i<=8 else range(peak,401);k=min(region,key=lambda j:abs(ys[j]-(start+amp*p))) if p else 0;phase(k/400);bones={}
  for b in rig.pose.bones:
   bones[b.name]={}
   for edge in ['head','tail']:
    pt=rig.matrix_world@getattr(b,edge);q=world_to_camera_view(sc,sc.camera,pt);bones[b.name][edge]={'world':list(pt),'xy':[q.x*384,(1-q.y)*512]}
  frames.append({'index':i,'desired_progress':p,'source_phase':k/400,'actual_head_origin_y':head_y(),'source_bones':bones})
 stance={}
 for side in ['left','right']:
  for edge in ['head','tail']:stance[side+'.foot.'+edge]=np.ptp(np.array([r['source_bones'][side+'.foot'][edge]['world'] for r in frames]),axis=0).tolist()
 assert max(max(a) for a in stance.values())<1e-5;views[view]={'frames':frames,'source_head_excursion_px':amp,'actual_foot_bone_world_ranges_m':stance}
(P/'source/controlled-retiming-v1.json').write_text(json.dumps({'parent_blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'desired_head_progress':progress,'phase_method':'Inverse actual source head-origin Y on descending/recovery branch,401source samples. No painted-image fitting. Final neutral aliases source0 exactly.','durations_ms':[90]*15+[550],'views':views,'scope':'Actual source bones only, not final painted joint detection or foot surface acceptance'},indent=2)+'\n')
