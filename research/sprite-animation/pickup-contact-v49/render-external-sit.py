"""Render actual external CC0 KayKit clips at fixed cameras, retaining native clocks.
No Astraeon source/action/character is loaded or used as a motion reference.
"""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;path=P/'references/Rig_Medium_Simulation.glb';bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path));sc=bpy.context.scene;r=next(o for o in sc.objects if o.type=='ARMATURE')
for o in sc.objects:
 if o.animation_data:
  for tr in o.animation_data.nla_tracks:tr.mute=True
sc.render.engine='CYCLES';sc.cycles.samples=4;sc.cycles.use_denoising=False;sc.render.resolution_x=256;sc.render.resolution_y=384;sc.render.resolution_percentage=100;sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.view_settings.view_transform='Standard';sc.render.fps=24
sc.world=bpy.data.worlds.new('ReferenceWorld');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
for loc,energy in [((3,-4,7),500),((-4,3,5),350)]:
 d=bpy.data.lights.new('ref_light','AREA');d.energy=energy;d.size=4;o=bpy.data.objects.new('ref_light',d);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
cams={}
for name,loc in [('N',(0,7,4)),('SW',(-6,-9,5.5))]:
 d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=3.0;o=bpy.data.objects.new('External_'+name,d);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1.0))-o.location).to_track_quat('-Z','Y').to_euler();cams[name]=o
records=[]
for clip,count,views in [('Sit_Floor_Down',16,['N','SW']),('Sit_Floor_Idle',8,['N']),('Sit_Floor_StandUp',16,['N'])]:
 action=bpy.data.actions[clip+'_Rig_Medium'];r.animation_data.action=action;end=float(action.frame_range[1]);duration=end/24
 for i in range(count):
  t=i/(count-1);frame=end*t;sc.frame_set(math.floor(frame),subframe=frame-math.floor(frame));bpy.context.view_layer.update()
  world={b.name:list(r.matrix_world@b.head) for b in r.pose.bones}
  for view in views:
   sc.camera=cams[view];out=P/'references/kaykit-captures'/clip/view;out.mkdir(parents=True,exist_ok=True);f=out/f'{i:02}.png';sc.render.filepath=str(f);bpy.ops.render.render(write_still=True)
   points={}
   for n,p in world.items():
    q=world_to_camera_view(sc,sc.camera,Vector(p));points[n]={'world':p,'xy':[q.x*256,(1-q.y)*384]}
   records.append({'clip':clip,'view':view,'index':i,'source_time_seconds':duration*t,'source_duration_seconds':duration,'scene_frame':frame,'image':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'actual_source_bones':points})
(P/'references/kaykit-sit-captures.json').write_text(json.dumps({'source_file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source':'KayKit Character Animations1.1 / Kay Lousberg / CC0; pinned acquisition in kaykit-retrieval.json','frames':records,'scope':'Actual evaluated external clip and mesh; no hidden painted-joint recovery or game art approval'},indent=2)+'\n');print('EXTERNAL_SOURCE_CAPTURES',len(records))
