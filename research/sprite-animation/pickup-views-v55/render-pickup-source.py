"""New retimed guide from saved rig. Not final sprite art or external reference."""
import bpy,json,math,hashlib
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;blend=P.parent/'pickup-sixteen-v48/source/parent-v45.blend';bpy.ops.wm.open_mainfile(filepath=str(blend));sc=bpy.context.scene;sc.cycles.samples=4;sc.render.resolution_x=384;sc.render.resolution_y=512;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.render.film_transparent=True;rig=bpy.data.objects['Astraeon_Free_Local']
gem=bpy.data.objects['collectible'];gem.animation_data_clear();gem.hide_render=True
records_by_view={}
def set_phase(t):
 tick=1+39*t;sc.frame_set(math.floor(tick),subframe=tick-math.floor(tick));gem.hide_render=True;bpy.context.view_layer.update()
def y():return 512*(1-world_to_camera_view(sc,sc.camera,rig.matrix_world@rig.pose.bones['head'].head).y)
progress=[0,.02,.08,.18,.34,.55,.78,.95,1,.91,.73,.49,.28,.12,.03,0]
for view in ['S','W','E']:
 sc.camera=bpy.data.objects[view];samples=[]
 for k in range(401):set_phase(k/400);samples.append(y())
 peak=max(range(len(samples)),key=lambda i:samples[i]);neutral=samples[0];amplitude=samples[peak]-neutral;records=[]
 for i,p in enumerate(progress):
  region=range(peak+1) if i<=8 else range(peak,401);j=min(region,key=lambda k:abs(samples[k]-(neutral+amplitude*p)));t=j/400;set_phase(t);out=P/'source'/view/f'{i:02}.png';out.parent.mkdir(parents=True,exist_ok=True);sc.render.filepath=str(out);bpy.ops.render.render(write_still=True);pts={}
  for b in rig.pose.bones:
   pts[b.name]={}
   for edge in ['head','tail']:
    pt=rig.matrix_world@getattr(b,edge);q=world_to_camera_view(sc,sc.camera,pt);pts[b.name][edge]={'world':list(pt),'xy':[q.x*384,(1-q.y)*512]}
  records.append({'index':i,'pose_phase':t,'desired_progress':p,'actual_projected_head_origin_y':y(),'source_bones':pts,'image':str(out.relative_to(P)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
 records_by_view[view]={'neutral_head_origin_y':neutral,'peak_excursion_px':amplitude,'frames':records}
(P/'source/retiming.json').write_text(json.dumps({'parent_blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'phase_selection':'Monotone source head-origin inverse, peak at8; source-only guide, never fitting final art','views':records_by_view,'prop_action_cleared_and_hidden_every_capture':True,'source_is_external':False,'production_pass':False},indent=2)+'\n')
