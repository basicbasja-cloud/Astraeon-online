"""Blender: real licensed external mannequin renders + exact bone projections.
Source-projected joint truth is a 3D-render benchmark, not independent annotations
of our painted art. First-frame projection seeds are disclosed; later truth is
not provided to the pixel tracker. No old own rig/attack is loaded.
"""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--source',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
a.out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.fps=30
bpy.ops.import_scene.gltf(filepath=str(a.source));rig=next(o for o in scene.objects if o.type=='ARMATURE')
for t in rig.animation_data.nla_tracks:t.mute=True
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12;scene.cycles.use_denoising=False
scene.render.resolution_x=320;scene.render.resolution_y=320;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.world=bpy.data.worlds.new('StudyWorld');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.65,.65,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
camdata=bpy.data.cameras.new('StudyCamera');camera=bpy.data.objects.new('StudyCamera',camdata);scene.collection.objects.link(camera);scene.camera=camera;camdata.type='ORTHO';camdata.ortho_scale=3.3
camera.location=(5,-8,4.5);camera.rotation_euler=(Vector((0,0,1.0))-camera.location).to_track_quat('-Z','Y').to_euler()
for loc,energy,size in [((3,-4,6),650,4),((-3,1,4),350,3)]:
 data=bpy.data.lights.new('StudyLight','AREA');data.energy=energy;data.shape='DISK';data.size=size;obj=bpy.data.objects.new('StudyLight',data);scene.collection.objects.link(obj);obj.location=loc;obj.rotation_euler=(Vector((0,0,1))-obj.location).to_track_quat('-Z','Y').to_euler()
JOINTMAP={'head':'Head','neck':'neck_01','pelvis':'pelvis'}
for side,suffix in [('right','r'),('left','l')]:
 for joint,bone in [('shoulder','upperarm'),('elbow','lowerarm'),('wrist','hand'),('hip','thigh'),('knee','calf'),('ankle','foot'),('toe','ball_leaf')]:JOINTMAP[side+'.'+joint]=bone+'_'+suffix
source_hash=hashlib.sha256(a.source.read_bytes()).hexdigest();runs=[]
for name in ['Walk_Carry_Loop','Chest_Open','Sword_Regular_A']:
 action=bpy.data.actions.get(name+'_Armature')
 if not action:raise ValueError('Missing exact source action '+name)
 rig.animation_data.action=action;end=float(action.frame_range[-1]);frames=[];truth=[]
 count=16
 for i in range(count):
  frame=end*i/(count-1);scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame));bpy.context.view_layer.update();folder=a.out/name;folder.mkdir(exist_ok=True);file=folder/f'{i:02}.png';scene.render.filepath=str(file);bpy.ops.render.render(write_still=True)
  points={}
  for label,bone in JOINTMAP.items():
   world=rig.matrix_world@rig.pose.bones[bone].head;v=world_to_camera_view(scene,camera,world);points[label]={'xy':[v.x*320,(1-v.y)*320],'world_xyz':list(world),'source_bone':bone,'pixel_visibility':'unverified'}
  duration=end/30/(count-1)*1000;image_hash=hashlib.sha256(file.read_bytes()).hexdigest();frames.append({'index':i,'path':str(file),'sha256':image_hash,'time_ms':i*duration,'duration_ms':duration,'source_time_seconds':frame/30});truth.append({'index':i,'candidate_image_sha256':image_hash,'source_time_seconds':frame/30,'points':points})
 case={'schema':'sprite-image-joint-tracks-v1','canvas':[320,320],'source_sha256':source_hash,'frames':frames,'seeds':[{'frame':0,'joint':label,'xy':point['xy'],'image_sha256':frames[0]['sha256'],'kind':'source_projected_benchmark','uncertainty_px':0,'owner_confirmed':False} for label,point in truth[0]['points'].items()]}
 (folder/'case.json').write_text(json.dumps(case,indent=2)+'\n');(folder/'truth.json').write_text(json.dumps({'source_sha256':source_hash,'frames':truth,'scope':'Actual source bone projection truth, not visible painted-art annotation; held-out later projections are not tracker inputs.'},indent=2)+'\n');runs.append({'clip':name,'frames':count,'duration_seconds':end/30,'source_sha256':source_hash,'case':str(folder/'case.json'),'truth':str(folder/'truth.json')})
(a.out/'render-receipt.json').write_text(json.dumps({'blender':bpy.app.version_string,'source_file':str(a.source),'source_sha256':source_hash,'camera_world_matrix':[list(row) for row in camera.matrix_world],'orthographic_scale':camdata.ortho_scale,'runs':runs,'old_own_attack_or_rig_used':False,'original_art_approved':False},indent=2)+'\n');print('BENCHMARK_RENDERED',len(runs)*16)
